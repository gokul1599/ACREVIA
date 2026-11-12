"""
ACREVIA - RiskCast Risk Management Service.
Handles plot evaluations, idempotent alert generation, acknowledgment lifecycle, and farm overviews.
"""

import hashlib
import json
from datetime import datetime, timezone, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc

from backend.app.core.exceptions import NotFoundException, AuthorizationException
from backend.app.models.farm import Farm, Plot
from backend.app.models.crop import CropSeason
from backend.app.models.weather_data import WeatherData
from backend.app.models.risk_assessment import RiskAssessmentRecord
from backend.app.models.risk_alert import RiskAlert
from backend.app.models.risk_rule import RiskRule
from backend.app.models.user import User
from backend.app.security.dependencies import verify_farm_access
from backend.app.services.riskcast.weather_service import WeatherService
from backend.app.services.riskcast.rule_engine import RuleEvaluationEngine


class RiskCastService:
    @classmethod
    async def evaluate_plot(
        cls,
        plot_id: str,
        current_user: Optional[User] = None,
        db: Session = None,
        actor_identity: str = "user"
    ) -> RiskAssessmentRecord:
        """
        Runs complete agrometeorological risk evaluation for a plot.
        Generates RiskAssessmentRecord and idempotent RiskAlert if severity is HIGH or MODERATE.
        Supports both user-initiated API flows (with verify_farm_access) and system worker
        flows (scoped to tenant context without farmer impersonation).
        """
        plot = db.get(Plot, plot_id)
        if not plot:
            raise NotFoundException(f"Plot '{plot_id}' not found.")

        # Verify access: user flow vs. background worker flow
        if current_user:
            farm = verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)
        else:
            # System worker flow: verify plot matches current tenant context without user impersonation
            ctx = db.info.get("tenant_context", {})
            tenant_id = ctx.get("tenant_id")
            if tenant_id and str(plot.farm_id) != str(tenant_id):
                raise PermissionError(f"Cross-tenant evaluation blocked: plot {plot_id} does not belong to tenant {tenant_id}")
            farm = db.get(Farm, plot.farm_id)
            if not farm or farm.is_archived:
                raise NotFoundException(f"Farm '{plot.farm_id}' not found or archived.")

        # Retrieve active crop season and stage
        stmt = (
            select(CropSeason)
            .filter_by(plot_id=plot.id, status="ACTIVE")
            .order_by(desc(CropSeason.created_at))
            .limit(1)
        )
        season = db.scalars(stmt).first()
        crop_name = season.crop_id if season else "cotton"
        growth_stage = season.current_stage if season else "VEGETATIVE"

        # Obtain or fetch weather
        weather = WeatherService.get_latest_weather(farm_id=farm.id, db=db)
        if not weather:
            weather = await WeatherService.fetch_and_persist_weather(farm=farm, db=db)

        # Run rule engine
        overall_severity, triggered_rules, advisories = RuleEvaluationEngine.evaluate_rules(
            crop=crop_name,
            growth_stage=growth_stage,
            weather=weather,
            db=db
        )

        assessment = RiskAssessmentRecord(
            plot_id=plot.id,
            farm_id=farm.id,
            crop_season_id=season.id if season else None,
            evaluation_timestamp=datetime.now(timezone.utc),
            overall_risk_level=overall_severity,
            weather_data_id=weather.id,
            rules_triggered_json=json.dumps(triggered_rules),
            advisory_en=advisories["en"],
            advisory_te=advisories["te"],
            advisory_hi=advisories["hi"],
            limitations_notice="High environmental risk denotes favorable climatic conditions for pathogen proliferation, NOT confirmed disease outbreak. Physical scouting required."
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        # Deduplicated Alert Creation if HIGH or MODERATE
        if overall_severity in ("HIGH", "MODERATE") and triggered_rules:
            top_threat = triggered_rules[0]["target_threat"]
            today_str = date.today().isoformat()
            dedup_raw = f"{farm.id}:{plot.id}:{top_threat}:{today_str}:{overall_severity}"
            dedup_key = hashlib.sha256(dedup_raw.encode()).hexdigest()

            # Check if active alert already exists with this key
            existing_alert = db.scalars(
                select(RiskAlert).filter_by(deduplication_key=dedup_key)
            ).first()

            if not existing_alert:
                actions = [
                    f"Scout lower leaf canopy in Plot '{plot.name}' for early symptoms of {top_threat}.",
                    "Ensure adequate drainage and avoid water stagnation around root zones.",
                    "Consult KrishiBrain knowledge recommendations or request Expert review before applying chemical sprays."
                ]
                alert = RiskAlert(
                    farm_id=farm.id,
                    plot_id=plot.id,
                    risk_assessment_id=assessment.id,
                    alert_level=overall_severity,
                    title=f"Climate Risk: {top_threat} ({overall_severity})",
                    message_en=advisories["en"],
                    message_te=advisories["te"],
                    message_hi=advisories["hi"],
                    recommended_actions_json=json.dumps(actions),
                    deduplication_key=dedup_key
                )
                db.add(alert)
                db.commit()

        return assessment

    @classmethod
    async def get_farm_overview(cls, farm_id: str, current_user: User, db: Session) -> Dict[str, Any]:
        """
        Retrieves agrometeorological overview, per-plot risk status, and active alerts for a farm.
        """
        farm = verify_farm_access(farm_id=farm_id, user=current_user, db=db)

        # Get latest weather or fetch
        weather = WeatherService.get_latest_weather(farm_id=farm.id, db=db)
        if not weather:
            weather = await WeatherService.fetch_and_persist_weather(farm=farm, db=db)

        # Summarize plots
        plot_summaries = []
        for plot in farm.plots:
            if plot.is_archived:
                continue

            # Latest assessment for plot
            stmt = (
                select(RiskAssessmentRecord)
                .filter_by(plot_id=plot.id)
                .order_by(desc(RiskAssessmentRecord.evaluation_timestamp))
                .limit(1)
            )
            latest_eval = db.scalars(stmt).first()

            # Active season
            season_stmt = (
                select(CropSeason)
                .filter_by(plot_id=plot.id, status="ACTIVE")
                .order_by(desc(CropSeason.created_at))
                .limit(1)
            )
            season = db.scalars(season_stmt).first()

            # Active alerts count
            alerts_count = db.query(RiskAlert).filter(
                and_(
                    RiskAlert.plot_id == plot.id,
                    RiskAlert.is_acknowledged == False,
                    RiskAlert.is_dismissed == False
                )
            ).count()

            current_risk = latest_eval.overall_risk_level if latest_eval else "LOW"
            advisory = latest_eval.advisory_en if latest_eval else "Conditions stable. Routine monitoring advised."

            top_threat = None
            if latest_eval and latest_eval.rules_triggered_json:
                try:
                    rules = json.loads(latest_eval.rules_triggered_json)
                    if rules:
                        top_threat = rules[0].get("target_threat")
                except Exception:
                    pass

            plot_summaries.append({
                "plot_id": plot.id,
                "plot_name": plot.name,
                "crop_id": season.crop_id if season else None,
                "growth_stage": season.current_stage if season else "VEGETATIVE",
                "current_risk_level": current_risk,
                "top_threat": top_threat,
                "advisory": advisory,
                "active_alerts_count": alerts_count
            })

        # Fetch active alerts for farm
        active_alerts = db.scalars(
            select(RiskAlert)
            .filter_by(farm_id=farm.id, is_dismissed=False)
            .order_by(desc(RiskAlert.created_at))
            .limit(10)
        ).all()

        alerts_formatted = []
        for a in active_alerts:
            actions = []
            try:
                actions = json.loads(a.recommended_actions_json)
            except Exception:
                actions = []

            alerts_formatted.append({
                "id": a.id,
                "farm_id": a.farm_id,
                "plot_id": a.plot_id,
                "risk_assessment_id": a.risk_assessment_id,
                "alert_level": a.alert_level,
                "title": a.title,
                "message_en": a.message_en,
                "message_te": a.message_te,
                "message_hi": a.message_hi,
                "recommended_actions": actions,
                "is_acknowledged": a.is_acknowledged,
                "acknowledged_at": a.acknowledged_at,
                "is_dismissed": a.is_dismissed,
                "dismissed_at": a.dismissed_at,
                "created_at": a.created_at
            })

        weather_summary = {
            "temperature_celsius": weather.temperature_celsius,
            "relative_humidity": weather.relative_humidity,
            "precipitation_mm": weather.precipitation_mm,
            "wind_speed_kmh": weather.wind_speed_kmh,
            "leaf_wetness_hours": weather.leaf_wetness_hours,
            "source_provider": weather.source_provider,
            "observation_time": weather.observation_time.isoformat()
        } if weather else None

        return {
            "farm_id": farm.id,
            "district": farm.district,
            "current_weather": weather_summary,
            "plots_risk_summary": plot_summaries,
            "active_alerts": alerts_formatted
        }

    @classmethod
    def list_farm_alerts(cls, farm_id: str, current_user: User, db: Session) -> List[RiskAlert]:
        """Lists active and acknowledged alerts for a farm."""
        verify_farm_access(farm_id=farm_id, user=current_user, db=db)
        stmt = (
            select(RiskAlert)
            .filter_by(farm_id=farm_id, is_dismissed=False)
            .order_by(desc(RiskAlert.created_at))
        )
        return db.scalars(stmt).all()

    @classmethod
    def acknowledge_alert(cls, alert_id: str, current_user: User, db: Session) -> RiskAlert:
        """Marks alert as acknowledged by the farmer."""
        alert = db.get(RiskAlert, alert_id)
        if not alert:
            raise NotFoundException(f"Alert '{alert_id}' not found.")
        verify_farm_access(farm_id=alert.farm_id, user=current_user, db=db)

        alert.is_acknowledged = True
        alert.acknowledged_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(alert)
        return alert

    @classmethod
    def dismiss_alert(cls, alert_id: str, current_user: User, db: Session) -> RiskAlert:
        """Dismisses an alert from active view."""
        alert = db.get(RiskAlert, alert_id)
        if not alert:
            raise NotFoundException(f"Alert '{alert_id}' not found.")
        verify_farm_access(farm_id=alert.farm_id, user=current_user, db=db)

        alert.is_dismissed = True
        alert.dismissed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(alert)
        return alert

    @classmethod
    def list_rules(cls, crop: Optional[str], db: Session) -> List[RiskRule]:
        """Lists active risk rules, optionally filtered by crop."""
        stmt = select(RiskRule).filter_by(is_active=True)
        if crop:
            stmt = stmt.filter(RiskRule.crop == crop.lower().strip())
        return db.scalars(stmt).all()
