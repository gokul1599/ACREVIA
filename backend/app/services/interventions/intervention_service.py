"""
ACREVIA - Intervention Intelligence & Outcome Tracking Service.
Manages farmer action records, follow-up outcome evaluations, and timeline comparisons.
"""

from datetime import date
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from backend.app.core.exceptions import NotFoundException, ValidationException
from backend.app.models.farm import Plot
from backend.app.models.user import User
from backend.app.models.observation import Observation
from backend.app.models.intervention import InterventionRecord, OutcomeObservation
from backend.app.schemas.intervention import (
    InterventionCreateRequest,
    OutcomeObservationCreateRequest
)
from backend.app.security.dependencies import verify_farm_access


class InterventionService:
    @classmethod
    def create_intervention(
        cls,
        data: InterventionCreateRequest,
        current_user: User,
        db: Session
    ) -> InterventionRecord:
        """
        Logs a farmer field intervention for a plot.
        """
        plot = db.get(Plot, data.plot_id)
        if not plot:
            raise NotFoundException(f"Plot '{data.plot_id}' not found.")

        # Verify access
        farm = verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)

        record = InterventionRecord(
            plot_id=plot.id,
            farm_id=farm.id,
            farmer_id=current_user.id,
            category=data.category,
            trade_name=data.trade_name,
            active_ingredient=data.active_ingredient,
            dosage=data.dosage,
            unit=data.unit,
            application_method=data.application_method,
            application_date=data.application_date,
            target_condition=data.target_condition,
            phi_days=data.phi_days,
            rei_hours=data.rei_hours,
            notes=data.notes
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @classmethod
    def list_plot_interventions(
        cls,
        plot_id: str,
        current_user: User,
        db: Session
    ) -> List[InterventionRecord]:
        plot = db.get(Plot, plot_id)
        if not plot:
            raise NotFoundException(f"Plot '{plot_id}' not found.")
        verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)

        stmt = (
            select(InterventionRecord)
            .filter_by(plot_id=plot.id)
            .order_by(desc(InterventionRecord.application_date))
        )
        return db.scalars(stmt).all()

    @classmethod
    def get_intervention(
        cls,
        intervention_id: str,
        current_user: User,
        db: Session
    ) -> InterventionRecord:
        record = db.get(InterventionRecord, intervention_id)
        if not record:
            raise NotFoundException(f"Intervention '{intervention_id}' not found.")
        verify_farm_access(farm_id=record.farm_id, user=current_user, db=db)
        return record

    @classmethod
    def record_outcome(
        cls,
        intervention_id: str,
        data: OutcomeObservationCreateRequest,
        current_user: User,
        db: Session
    ) -> OutcomeObservation:
        """
        Links a follow-up CropPulse observation to assess post-intervention recovery.
        """
        record = db.get(InterventionRecord, intervention_id)
        if not record:
            raise NotFoundException(f"Intervention '{intervention_id}' not found.")
        verify_farm_access(farm_id=record.farm_id, user=current_user, db=db)

        obs = db.get(Observation, data.follow_up_observation_id)
        if not obs:
            raise NotFoundException(f"Follow-up observation '{data.follow_up_observation_id}' not found.")

        # Compute elapsed days
        days_post = (data.evaluation_date - record.application_date).days
        if days_post < 0:
            raise ValidationException("Evaluation date cannot precede the intervention application date.")

        confounding = data.confounding_factors or (
            "Open-field micro-climate variation, moisture distribution, and natural predator activity. "
            "Visual improvement reflects systemic progression, not exclusive product causality."
        )

        outcome = OutcomeObservation(
            intervention_id=record.id,
            follow_up_observation_id=obs.id,
            evaluation_date=data.evaluation_date,
            observed_status=data.observed_status,
            visual_change_notes=data.visual_change_notes,
            confounding_factors=confounding,
            farmer_assessment=data.farmer_assessment,
            days_post_intervention=days_post
        )
        db.add(outcome)
        db.commit()
        db.refresh(outcome)
        return outcome

    @classmethod
    def get_timeline(
        cls,
        intervention_id: str,
        current_user: User,
        db: Session
    ) -> Dict[str, Any]:
        """
        Compiles comparative before-and-after imagery and observational notes.
        """
        record = db.get(InterventionRecord, intervention_id)
        if not record:
            raise NotFoundException(f"Intervention '{intervention_id}' not found.")
        verify_farm_access(farm_id=record.farm_id, user=current_user, db=db)

        # Find closest prior observation on this plot
        prior_obs = db.scalars(
            select(Observation)
            .filter(Observation.plot_id == record.plot_id)
            .order_by(desc(Observation.created_at))
            .limit(1)
        ).first()

        prior_media = []
        if prior_obs and prior_obs.media:
            for m in prior_obs.media:
                prior_media.append({
                    "id": m.id,
                    "mime_type": m.mime_type,
                    "url": f"/api/v1/observations/{prior_obs.id}/media/{m.id}/stream"
                })

        # Latest outcome observation media
        latest_media = []
        if record.outcomes:
            latest_outcome = record.outcomes[-1]
            follow_obs = latest_outcome.follow_up_observation
            if follow_obs and follow_obs.media:
                for m in follow_obs.media:
                    latest_media.append({
                        "id": m.id,
                        "mime_type": m.mime_type,
                        "url": f"/api/v1/observations/{follow_obs.id}/media/{m.id}/stream"
                    })

        return {
            "intervention": record,
            "outcomes": record.outcomes,
            "initial_observation_media": prior_media,
            "latest_observation_media": latest_media,
            "confounding_variables_notice": (
                "Open-field biological systems are subject to ambient temperature fluctuations, rainfall washout, "
                "and untracked surrounding pest reservoirs. Observed visual changes reflect field progression, not proven single-cause cure."
            )
        }
