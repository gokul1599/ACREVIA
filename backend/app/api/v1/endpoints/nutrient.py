"""
ACREVIA - Nutrient Intelligence & Governance API Endpoints (Pillar D).
Generates soil-test-driven N-P-K & micronutrient prescriptions according to PJTSAU standards,
enforces strict upper-bound safety guards, and manages expert agronomist escalations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.nutrient_intelligence import (
    NutrientPrescribeRequest,
    NutrientAssessmentResponse,
    NutrientExpertReviewRequest,
    NutrientExpertReviewResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.nutrient_service import NutrientService

router = APIRouter(prefix="/nutrient", tags=["ACREVIA Nutrient Intelligence"])


@router.post("/prescribe", response_model=NutrientAssessmentResponse, status_code=status.HTTP_200_OK)
def prescribe_nutrients(
    request: NutrientPrescribeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return NutrientService.prescribe_nutrients(db=db, request=request)


@router.get("/assessment/{assessment_id}", response_model=NutrientAssessmentResponse, status_code=status.HTTP_200_OK)
def get_nutrient_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return NutrientService.get_assessment(db=db, assessment_id=assessment_id)


@router.post("/expert-review", response_model=NutrientExpertReviewResponse, status_code=status.HTTP_200_OK)
def submit_expert_review(
    request: NutrientExpertReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return NutrientService.submit_expert_review(db=db, expert_user_id=current_user.id, request=request)
