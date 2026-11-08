"""
ACREVIA - Farmer Consent & Data Sharing Grants Endpoints.
Stage 14: Granular consent grants, purpose restrictions, privacy redaction, and instant revocation.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.interoperability import (
    DataSharingGrantCreate,
    DataSharingGrantRevoke,
    DataSharingGrantResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.partner_service import PartnerService

router = APIRouter(prefix="/consent/grants", tags=["ACREVIA Consent Grants"])


@router.post("", response_model=DataSharingGrantResponse, status_code=status.HTTP_201_CREATED)
def grant_data_sharing(
    request: DataSharingGrantCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Grants explicit consent to share categorized farm data with an approved partner.
    """
    try:
        grant = PartnerService.grant_consent(
            db=db,
            user_id=current_user.id,
            partner_id=request.partner_id,
            purpose=request.purpose,
            farm_id=request.farm_id,
            plot_id=request.plot_id,
            data_categories=request.data_categories,
            anonymize_pii=request.anonymize_pii,
            redact_exact_gps=request.redact_exact_gps,
            expires_in_days=request.expires_in_days or 90,
        )
        return grant
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=List[DataSharingGrantResponse], status_code=status.HTTP_200_OK)
def list_farmer_grants(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lists all active and historical data-sharing grants authorized by the farmer.
    """
    return PartnerService.list_farmer_grants(db=db, user_id=current_user.id)


@router.post("/{grant_id}/revoke", response_model=DataSharingGrantResponse, status_code=status.HTTP_200_OK)
def revoke_data_sharing(
    grant_id: str,
    request: DataSharingGrantRevoke,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Immediately revokes data-sharing authorization for a partner.
    """
    try:
        grant = PartnerService.revoke_consent(
            db=db,
            grant_id=grant_id,
            user_id=current_user.id,
            reason=request.reason,
        )
        return grant
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
