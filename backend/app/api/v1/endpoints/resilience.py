"""
ACREVIA - Agricultural Resilience Engine API Endpoints (Pillar F).
Evaluates multi-dimensional farm resilience, computes evidence quality scores,
identifies priority vulnerabilities, and simulates climate-resilient adaptation packages.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.resilience_assessment import (
    ResilienceAssessRequest,
    ResilienceAssessmentResponse,
    ResilienceSimulationRequest,
    ResilienceScenarioSimulationResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.resilience_service import ResilienceService

router = APIRouter(prefix="/resilience", tags=["ACREVIA Agricultural Resilience"])


@router.post("/assess", response_model=ResilienceAssessmentResponse, status_code=status.HTTP_200_OK)
def assess_plot_resilience(
    request: ResilienceAssessRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ResilienceService.assess_plot_resilience(db=db, plot_id=request.plot_id)


@router.get("/plot/{plot_id}/latest", response_model=ResilienceAssessmentResponse, status_code=status.HTTP_200_OK)
def get_latest_resilience_assessment(
    plot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ResilienceService.get_latest_assessment(db=db, plot_id=plot_id)


@router.post("/simulate-adaptation", response_model=ResilienceScenarioSimulationResponse, status_code=status.HTTP_200_OK)
def simulate_adaptation_package(
    request: ResilienceSimulationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ResilienceService.simulate_adaptation_package(
        db=db,
        plot_id=request.plot_id,
        package_name=request.package_name,
    )
