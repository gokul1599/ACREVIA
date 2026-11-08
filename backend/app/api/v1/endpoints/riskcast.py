"""
ACREVIA - RiskCast API Endpoints.
Provides agrometeorological risk intelligence, plot evaluations, and idempotent alerts.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
import json

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.riskcast import (
    FarmRiskOverviewResponse,
    RiskAssessmentResponse,
    RiskAlertResponse,
    RiskRuleResponse,
    TriggeredRuleDetail
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.riskcast.risk_service import RiskCastService

router = APIRouter(prefix="/riskcast", tags=["RiskCast - Climate & Crop Risk Intelligence"])


@router.get("/farms/{farm_id}/overview", response_model=FarmRiskOverviewResponse)
async def get_farm_risk_overview(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves real-time weather observations, per-plot agro-climatic risk status, and active alerts.
    """
    return await RiskCastService.get_farm_overview(farm_id=farm_id, current_user=current_user, db=db)


@router.post("/evaluate/{plot_id}", response_model=RiskAssessmentResponse, status_code=status.HTTP_201_CREATED)
async def evaluate_plot_risk(
    plot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Triggers an on-demand agrometeorological risk assessment for a specific plot and active crop season.
    """
    assessment = await RiskCastService.evaluate_plot(plot_id=plot_id, current_user=current_user, db=db)

    # Format triggered rules
    triggered_rules = []
    if assessment.rules_triggered_json:
        try:
            raw_rules = json.loads(assessment.rules_triggered_json)
            for r in raw_rules:
                triggered_rules.append(TriggeredRuleDetail(
                    rule_code=r["rule_code"],
                    target_threat=r["target_threat"],
                    severity_level=r["severity_level"],
                    advisory_en=r["advisory_en"],
                    advisory_te=r["advisory_te"],
                    advisory_hi=r["advisory_hi"],
                    citations=r.get("citations", [])
                ))
        except Exception:
            pass

    weather_summary = None
    if assessment.weather:
        weather_summary = {
            "temperature_celsius": assessment.weather.temperature_celsius,
            "relative_humidity": assessment.weather.relative_humidity,
            "precipitation_mm": assessment.weather.precipitation_mm,
            "leaf_wetness_hours": assessment.weather.leaf_wetness_hours,
            "source_provider": assessment.weather.source_provider
        }

    return RiskAssessmentResponse(
        id=assessment.id,
        plot_id=assessment.plot_id,
        farm_id=assessment.farm_id,
        crop_season_id=assessment.crop_season_id,
        evaluation_timestamp=assessment.evaluation_timestamp,
        overall_risk_level=assessment.overall_risk_level,
        weather_data_id=assessment.weather_data_id,
        weather_summary=weather_summary,
        rules_triggered=triggered_rules,
        advisory_en=assessment.advisory_en,
        advisory_te=assessment.advisory_te,
        advisory_hi=assessment.advisory_hi,
        limitations_notice=assessment.limitations_notice
    )


@router.get("/alerts", response_model=List[RiskAlertResponse])
def list_alerts(
    farm_id: str = Query(..., description="ID of the farm to retrieve alerts for"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists active and acknowledged risk alerts for a farm holding.
    """
    alerts = RiskCastService.list_farm_alerts(farm_id=farm_id, current_user=current_user, db=db)
    results = []
    for a in alerts:
        actions = []
        try:
            actions = json.loads(a.recommended_actions_json)
        except Exception:
            pass
        results.append(RiskAlertResponse(
            id=a.id,
            farm_id=a.farm_id,
            plot_id=a.plot_id,
            risk_assessment_id=a.risk_assessment_id,
            alert_level=a.alert_level,
            title=a.title,
            message_en=a.message_en,
            message_te=a.message_te,
            message_hi=a.message_hi,
            recommended_actions=actions,
            is_acknowledged=a.is_acknowledged,
            acknowledged_at=a.acknowledged_at,
            is_dismissed=a.is_dismissed,
            dismissed_at=a.dismissed_at,
            created_at=a.created_at
        ))
    return results


@router.post("/alerts/{alert_id}/acknowledge", response_model=RiskAlertResponse)
def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Acknowledges an active agro-climatic alert.
    """
    a = RiskCastService.acknowledge_alert(alert_id=alert_id, current_user=current_user, db=db)
    actions = []
    try:
        actions = json.loads(a.recommended_actions_json)
    except Exception:
        pass
    return RiskAlertResponse(
        id=a.id,
        farm_id=a.farm_id,
        plot_id=a.plot_id,
        risk_assessment_id=a.risk_assessment_id,
        alert_level=a.alert_level,
        title=a.title,
        message_en=a.message_en,
        message_te=a.message_te,
        message_hi=a.message_hi,
        recommended_actions=actions,
        is_acknowledged=a.is_acknowledged,
        acknowledged_at=a.acknowledged_at,
        is_dismissed=a.is_dismissed,
        dismissed_at=a.dismissed_at,
        created_at=a.created_at
    )


@router.post("/alerts/{alert_id}/dismiss", response_model=RiskAlertResponse)
def dismiss_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dismisses an alert from the active notification drawer.
    """
    a = RiskCastService.dismiss_alert(alert_id=alert_id, current_user=current_user, db=db)
    actions = []
    try:
        actions = json.loads(a.recommended_actions_json)
    except Exception:
        pass
    return RiskAlertResponse(
        id=a.id,
        farm_id=a.farm_id,
        plot_id=a.plot_id,
        risk_assessment_id=a.risk_assessment_id,
        alert_level=a.alert_level,
        title=a.title,
        message_en=a.message_en,
        message_te=a.message_te,
        message_hi=a.message_hi,
        recommended_actions=actions,
        is_acknowledged=a.is_acknowledged,
        acknowledged_at=a.acknowledged_at,
        is_dismissed=a.is_dismissed,
        dismissed_at=a.dismissed_at,
        created_at=a.created_at
    )


@router.get("/rules", response_model=List[RiskRuleResponse])
def list_risk_rules(
    crop: Optional[str] = Query(None, description="Optional crop filter: cotton, rice, chilli"),
    db: Session = Depends(get_db)
):
    """
    Returns the catalogue of evidence-grounded PJTSAU/ICAR agronomic risk rules.
    """
    rules = RiskCastService.list_rules(crop=crop, db=db)
    results = []
    for r in rules:
        citations = []
        try:
            citations = json.loads(r.evidence_citations_json)
        except Exception:
            pass
        results.append(RiskRuleResponse(
            id=r.id,
            rule_code=r.rule_code,
            crop=r.crop,
            target_threat=r.target_threat,
            applicable_growth_stages=r.applicable_growth_stages,
            min_temp=r.min_temp,
            max_temp=r.max_temp,
            min_humidity=r.min_humidity,
            min_leaf_wetness_hours=r.min_leaf_wetness_hours,
            min_consecutive_wet_days=r.min_consecutive_wet_days,
            severity_level=r.severity_level,
            advisory_en=r.advisory_en,
            advisory_te=r.advisory_te,
            advisory_hi=r.advisory_hi,
            evidence_citations=citations,
            version=r.version,
            is_active=r.is_active
        ))
    return results
