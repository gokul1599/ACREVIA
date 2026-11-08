"""
ACREVIA - Agricultural Integration Partner Registry Endpoints.
Stage 14: Governed partner onboarding, institutional verification, and connector registration.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.interoperability import (
    PartnerRegisterRequest,
    PartnerVerifyRequest,
    PartnerResponse,
    PartnerIntegrationCreate,
    PartnerIntegrationResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.partner_service import PartnerService

router = APIRouter(prefix="/partners", tags=["ACREVIA Partners"])


@router.post("/register", response_model=PartnerResponse, status_code=status.HTTP_201_CREATED)
def register_partner(
    request: PartnerRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submits an institutional partner application for verification.
    """
    partner = PartnerService.register_partner(
        db=db,
        name=request.name,
        partner_type=request.partner_type,
        contact_email=request.contact_email,
        description=request.description,
        website=request.website,
        contact_phone=request.contact_phone,
        legal_entity_number=request.legal_entity_number,
    )
    return partner


@router.get("", response_model=List[PartnerResponse], status_code=status.HTTP_200_OK)
def list_partners(
    verification_status: Optional[str] = Query(None, alias="status"),
    partner_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lists registered integration partners filtered by status or category.
    """
    return PartnerService.list_partners(db=db, status=verification_status, partner_type=partner_type)


@router.get("/{partner_id}", response_model=PartnerResponse, status_code=status.HTTP_200_OK)
def get_partner(
    partner_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    partner = PartnerService.get_partner(db=db, partner_id=partner_id)
    if not partner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    return partner


@router.post("/{partner_id}/verify", response_model=PartnerResponse, status_code=status.HTTP_200_OK)
def verify_partner(
    partner_id: str,
    request: PartnerVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Administrative review gate to transition partner verification status.
    """
    try:
        partner = PartnerService.verify_partner(
            db=db,
            partner_id=partner_id,
            verification_status=request.verification_status,
            verifier_user_id=current_user.id,
            notes=request.verification_notes,
        )
        return partner
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{partner_id}/integrations", response_model=PartnerIntegrationResponse, status_code=status.HTTP_201_CREATED)
def add_partner_integration(
    partner_id: str,
    request: PartnerIntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Registers a standardized connector capability for a verified partner.
    """
    try:
        integration = PartnerService.add_integration(
            db=db,
            partner_id=partner_id,
            connector_type=request.connector_type,
            display_name=request.display_name,
            capabilities=request.capabilities,
            adapter_config=request.adapter_config,
        )
        return integration
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{partner_id}/integrations", response_model=List[PartnerIntegrationResponse], status_code=status.HTTP_200_OK)
def list_partner_integrations(
    partner_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return PartnerService.list_partner_integrations(db=db, partner_id=partner_id)
