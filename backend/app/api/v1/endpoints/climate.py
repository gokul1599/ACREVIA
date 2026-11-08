"""
ACREVIA - Climate Resilience API Endpoints (Pillar C).
Provides 30-year climatological baselines, hazard exposure assessments, and adaptation scenarios.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.climate_resilience import (
    ClimateBaselineResponse,
    ClimateExposureAssessmentRequest,
    ClimateExposureAssessmentResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.climate_service import ClimateService

router = APIRouter(prefix="/climate", tags=["ACREVIA Climate Resilience"])


@router.get("/baselines/{district_code}", response_model=List[ClimateBaselineResponse], status_code=status.HTTP_200_OK)
def get_climate_baselines(
    district_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ClimateService.get_district_baselines(db=db, district_code=district_code)


@router.post("/assess-exposure", response_model=ClimateExposureAssessmentResponse, status_code=status.HTTP_200_OK)
def assess_climate_exposure(
    request: ClimateExposureAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = ClimateService.assess_exposure(db=db, request=request)
    return assessment
