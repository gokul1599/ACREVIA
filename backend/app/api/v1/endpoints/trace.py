"""
ACREVIA - Produce Traceability API Endpoints.
Pillar E: Internal lot lifecycle, movement balance, and privacy-preserving public QR verification.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.produce_traceability import (
    LotMovementCreate,
    LotMovementResponse,
    ProduceLotResponse,
    ProduceLotDetailResponse,
    ProduceLotPublicResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.traceability_service import TraceabilityService

router = APIRouter(prefix="/trace", tags=["Produce Traceability"])


@router.get("/lots/{lot_id}", response_model=ProduceLotDetailResponse, status_code=status.HTTP_200_OK)
def get_lot_detail(
    lot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Authenticated internal view with full movement history and internal identifiers.
    """
    lot = TraceabilityService.get_produce_lot(db, lot_id=lot_id)
    return lot


@router.post("/lots/{lot_id}/movements", response_model=LotMovementResponse, status_code=status.HTTP_201_CREATED)
def record_movement(
    lot_id: str,
    data: LotMovementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TraceabilityService.record_lot_movement(db, lot_id=lot_id, data=data)


@router.get("/public/{qr_token}", response_model=ProduceLotPublicResponse, status_code=status.HTTP_200_OK)
def verify_public_qr_code(
    qr_token: str,
    db: Session = Depends(get_db),
):
    """
    Open public verification endpoint accessed by scanning the lot QR code.
    Strictly redacts farmer PII, telephone numbers, and exact farm GPS coordinates.
    """
    return TraceabilityService.get_public_lot_verification(db, qr_token=qr_token)
