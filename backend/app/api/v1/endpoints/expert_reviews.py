"""
ACREVIA - Agricultural Expert Review & Clinical Validation Endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.diagnosis import ExpertReviewCreateRequest, ExpertReviewResponse
from backend.app.security.dependencies import get_current_user, require_roles
from backend.app.security.permissions import SystemRole
from backend.app.services.diagnosis_service import DiagnosisService

router = APIRouter(prefix="/diagnoses", tags=["Expert Agronomist Reviews"])


@router.post(
    "/{diagnosis_id}/expert-review",
    response_model=ExpertReviewResponse,
    status_code=status.HTTP_201_CREATED
)
def submit_expert_review(
    diagnosis_id: str,
    data: ExpertReviewCreateRequest,
    current_user: User = Depends(require_roles(SystemRole.AGRICULTURAL_EXPERT.value)),
    db: Session = Depends(get_db)
):
    """
    Submits a certified human agricultural expert validation (CONFIRMED or OVERRIDDEN).
    Restricted to AGRICULTURAL_EXPERT and ADMIN roles.
    """
    return DiagnosisService.submit_expert_review(
        diagnosis_id=diagnosis_id,
        data=data,
        current_user=current_user,
        db=db
    )
