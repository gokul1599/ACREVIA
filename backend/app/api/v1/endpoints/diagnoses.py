"""
ACREVIA - AI Pathology Diagnosis & Differential Inference Endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.diagnosis import DiagnosisCreateRequest, DiagnosisResponse
from backend.app.security.dependencies import get_current_user
from backend.app.services.diagnosis_service import DiagnosisService

router = APIRouter(prefix="/diagnoses", tags=["AI Diagnoses"])


@router.post("/", response_model=DiagnosisResponse, status_code=status.HTTP_201_CREATED)
async def request_diagnosis(
    data: DiagnosisCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits a foliar observation to the Stage 3 ML inference microservice.
    Calculates temperature-scaled calibrated probabilities, entropy, and differential rankings.
    """
    return await DiagnosisService.process_diagnosis(
        data=data,
        current_user=current_user,
        db=db
    )


@router.get("/{diagnosis_id}", response_model=DiagnosisResponse)
def get_diagnosis(
    diagnosis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves complete diagnosis results, calibrated candidates, and agronomist reviews.
    """
    return DiagnosisService.get_diagnosis(
        diagnosis_id=diagnosis_id,
        current_user=current_user,
        db=db
    )
