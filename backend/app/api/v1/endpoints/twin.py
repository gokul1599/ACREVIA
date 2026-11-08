"""
ACREVIA - Digital Twin API Endpoints (Pillar A: ACREVIA Twin).
Provides access to farm digital twin state, completeness vectors, and snapshots.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.digital_twin import TwinSnapshot, TwinStateRecord
from backend.app.schemas.digital_twin import (
    FarmTwinResponse,
    TwinSnapshotSummaryResponse,
    TwinSnapshotDetailResponse,
    TwinStateRecordResponse,
    DataCompletenessResponse,
    TwinReconcileResponse,
)
from backend.app.security.dependencies import get_current_user, verify_farm_access
from backend.app.services.twin_service import TwinService

router = APIRouter(prefix="/twin", tags=["Digital Twin"])


@router.get("/farms/{farm_id}", response_model=FarmTwinResponse)
def get_farm_twin(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves the current synchronized digital twin state for a farm holding.
    """
    farm = verify_farm_access(farm_id=farm_id, user=current_user, db=db)
    return TwinService.get_twin_summary(farm=farm, db=db)


@router.get("/farms/{farm_id}/completeness", response_model=DataCompletenessResponse)
def get_twin_completeness(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns the multidimensional data completeness vector for a farm digital twin.
    """
    farm = verify_farm_access(farm_id=farm_id, user=current_user, db=db)
    return TwinService.calculate_completeness(farm=farm, db=db)


@router.post("/farms/{farm_id}/reconcile", response_model=TwinReconcileResponse)
def reconcile_farm_twin(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Triggers explicit state reconciliation, producing a fresh immutable twin snapshot.
    """
    farm = verify_farm_access(farm_id=farm_id, user=current_user, db=db)
    return TwinService.reconcile_twin(farm=farm, db=db)


@router.get("/farms/{farm_id}/snapshots", response_model=List[TwinSnapshotSummaryResponse])
def list_farm_snapshots(
    farm_id: str,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lists historical immutable state snapshots for the specified farm.
    """
    farm = verify_farm_access(farm_id=farm_id, user=current_user, db=db)
    snapshots = (
        db.query(TwinSnapshot)
        .filter(TwinSnapshot.farm_id == farm.id)
        .order_by(desc(TwinSnapshot.snapshot_version))
        .limit(limit)
        .all()
    )

    return [
        TwinSnapshotSummaryResponse(
            id=s.id,
            twin_id=s.twin_id,
            farm_id=s.farm_id,
            plot_id=s.plot_id,
            crop_season_id=s.crop_season_id,
            snapshot_version=s.snapshot_version,
            data_completeness_pct=s.data_completeness_pct,
            payload_hash=s.payload_hash,
            generated_at=s.generated_at,
            source_manifest_json=s.source_manifest_json,
        )
        for s in snapshots
    ]


@router.get("/snapshots/{snapshot_id}", response_model=TwinSnapshotDetailResponse)
def get_snapshot_detail(
    snapshot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves full detail and individual state records for a specific twin snapshot.
    """
    snapshot = db.get(TwinSnapshot, snapshot_id)
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TwinSnapshot '{snapshot_id}' not found.",
        )

    # Check tenancy
    verify_farm_access(farm_id=snapshot.farm_id, user=current_user, db=db)

    records = (
        db.query(TwinStateRecord)
        .filter(TwinStateRecord.snapshot_id == snapshot.id)
        .all()
    )

    rec_responses = [
        TwinStateRecordResponse(
            id=r.id,
            snapshot_id=r.snapshot_id,
            entity_type=r.entity_type,
            entity_id=r.entity_id,
            property_name=r.property_name,
            property_value_json=r.property_value_json,
            unit=r.unit,
            provenance_type=r.provenance_type,
            source_reference=r.source_reference,
            observed_at=r.observed_at,
            quality_status=r.quality_status,
        )
        for r in records
    ]

    return TwinSnapshotDetailResponse(
        id=snapshot.id,
        twin_id=snapshot.twin_id,
        farm_id=snapshot.farm_id,
        plot_id=snapshot.plot_id,
        crop_season_id=snapshot.crop_season_id,
        snapshot_version=snapshot.snapshot_version,
        data_completeness_pct=snapshot.data_completeness_pct,
        payload_hash=snapshot.payload_hash,
        generated_at=snapshot.generated_at,
        source_manifest_json=snapshot.source_manifest_json,
        state_payload_json=snapshot.state_payload_json,
        records=rec_responses,
    )
