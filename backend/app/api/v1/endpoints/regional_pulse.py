"""
ACREVIA - Regional Pulse & Intelligence Endpoints (ACREVIA Regional Pulse).
Pillar F: Privacy-preserving regional signal aggregation, evidence verification, and outbreak claim suppression.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.regional_pulse import (
    RegionalSignalCreate,
    RegionalSignalResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.regional_pulse_service import RegionalPulseService

router = APIRouter(prefix="/regional-pulse", tags=["ACREVIA Regional Pulse"])


@router.post("/signals", response_model=RegionalSignalResponse, status_code=status.HTTP_201_CREATED)
def aggregate_signal(
    data: RegionalSignalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    evidences = getattr(data, "evidences", None)
    return RegionalPulseService.aggregate_regional_signal(db, data=data, evidences=evidences)


@router.get("/signals", response_model=List[RegionalSignalResponse], status_code=status.HTTP_200_OK)
def list_signals(
    district: Optional[str] = Query(None),
    crop_id: Optional[str] = Query(None),
    confidence_tier: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    signals = RegionalPulseService.query_signals(
        db, district=district, crop_id=crop_id, confidence_tier=confidence_tier, limit=limit, offset=offset
    )
    user_roles = [r.id for r in current_user.roles]
    is_privileged = any(r in ("ADMIN", "AGRICULTURAL_EXPERT", "RESEARCHER") for r in user_roles)

    results = []
    for sig in signals:
        # Pre-read dynamic provenance revalidation: closes the stale-publication window
        is_valid = RegionalPulseService.revalidate_signal_provenance(db, sig.id)
        if not is_valid and not is_privileged:
            continue
        if sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE" and not is_privileged:
            continue

        sig_data = RegionalSignalResponse.model_validate(sig)
        if not is_privileged:
            sig_data.evidences = []
        results.append(sig_data)
    return results


@router.get("/signals/{signal_id}", response_model=RegionalSignalResponse, status_code=status.HTTP_200_OK)
def get_signal(
    signal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sig = RegionalPulseService.get_signal(db, signal_id=signal_id)
    if not sig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regional signal not found",
        )

    # Pre-read dynamic provenance revalidation: closes the stale-publication window
    is_valid = RegionalPulseService.revalidate_signal_provenance(db, sig.id)
    user_roles = [r.id for r in current_user.roles]
    is_privileged = any(r in ("ADMIN", "AGRICULTURAL_EXPERT", "RESEARCHER") for r in user_roles)

    if (not is_valid or sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE") and not is_privileged:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regional signal not found or suppressed due to insufficient provenance",
        )

    sig_data = RegionalSignalResponse.model_validate(sig)
    if not is_privileged:
        sig_data.evidences = []
    return sig_data
