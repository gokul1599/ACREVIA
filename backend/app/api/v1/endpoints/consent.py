"""
ACREVIA - Data Governance & Consent Endpoints.
Compliant with DPDP Act, India.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.consent import ConsentCreateRequest, ConsentResponse
from backend.app.security.dependencies import get_current_user
from backend.app.services.consent_service import ConsentService

router = APIRouter(prefix="/consent", tags=["Data Governance & Consent"])


@router.post("/", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED)
def record_consent(
    data: ConsentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Records or revokes explicit farmer consent for specific data processing categories.
    """
    return ConsentService.record_consent(user=current_user, data=data, db=db)


@router.get("/", response_model=List[ConsentResponse])
def get_consents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the list of active and historical consent declarations for the authenticated user.
    """
    return ConsentService.get_user_consents(user=current_user, db=db)
