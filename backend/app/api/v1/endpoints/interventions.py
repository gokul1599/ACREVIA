"""
ACREVIA - Agricultural Intervention & Outcome Tracking Endpoints.
Enables farmers to log inputs, link follow-up CropPulse observations, and compare timelines.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.intervention import (
    InterventionCreateRequest,
    InterventionResponse,
    OutcomeObservationCreateRequest,
    OutcomeObservationResponse,
    InterventionTimelineResponse
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.interventions.intervention_service import InterventionService

router = APIRouter(prefix="/interventions", tags=["Intervention Intelligence & Outcome Tracking"])


@router.post("/", response_model=InterventionResponse, status_code=status.HTTP_201_CREATED)
def record_intervention(
    data: InterventionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logs an intervention (biological, chemical, cultural, irrigation, or fertilizer) on a plot.
    """
    return InterventionService.create_intervention(data=data, current_user=current_user, db=db)


@router.get("/plots/{plot_id}", response_model=List[InterventionResponse])
def list_plot_interventions(
    plot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists all recorded interventions and linked outcomes for a given plot.
    """
    return InterventionService.list_plot_interventions(plot_id=plot_id, current_user=current_user, db=db)


@router.get("/{intervention_id}", response_model=InterventionResponse)
def get_intervention(
    intervention_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves details of an intervention record.
    """
    return InterventionService.get_intervention(intervention_id=intervention_id, current_user=current_user, db=db)


@router.post("/{intervention_id}/outcomes", response_model=OutcomeObservationResponse, status_code=status.HTTP_201_CREATED)
def record_outcome_observation(
    intervention_id: str,
    data: OutcomeObservationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Links a subsequent CropPulse observation to assess visual and field progression post-intervention.
    """
    return InterventionService.record_outcome(
        intervention_id=intervention_id,
        data=data,
        current_user=current_user,
        db=db
    )


@router.get("/{intervention_id}/timeline", response_model=InterventionTimelineResponse)
def get_intervention_timeline(
    intervention_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves comparative before-and-after timeline, imagery, and confounding variable notice.
    """
    return InterventionService.get_timeline(
        intervention_id=intervention_id,
        current_user=current_user,
        db=db
    )
