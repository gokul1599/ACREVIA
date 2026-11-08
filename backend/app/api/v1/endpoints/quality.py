"""
ACREVIA - Post-Harvest Quality & Storage API Endpoints.
Pillar D: Moisture provenance, quality assays, and storage lot assignments.
"""

from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.post_harvest import (
    QualityMeasurementCreate,
    QualityMeasurementResponse,
    StorageLocationCreate,
    StorageLocationResponse,
    StorageLotCreate,
    StorageLotResponse,
)
from backend.app.security.dependencies import get_current_user, verify_farm_access
from backend.app.services.quality_service import QualityService

router = APIRouter(prefix="/quality", tags=["Post-Harvest Quality & Storage"])


@router.post("/measurements", response_model=QualityMeasurementResponse, status_code=status.HTTP_201_CREATED)
def record_quality_measurement(
    data: QualityMeasurementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return QualityService.record_quality_measurement(db, data)


@router.get("/measurements/{lot_id}", response_model=List[QualityMeasurementResponse], status_code=status.HTTP_200_OK)
def get_lot_quality_measurements(
    lot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return QualityService.get_measurements_for_lot(db, lot_id=lot_id)


@router.post("/storage/locations", response_model=StorageLocationResponse, status_code=status.HTTP_201_CREATED)
def create_storage_location(
    data: StorageLocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verify_farm_access(farm_id=data.farm_id, user=current_user, db=db)
    return QualityService.create_storage_location(db, data)


@router.post("/storage/lots", response_model=StorageLotResponse, status_code=status.HTTP_201_CREATED)
def assign_to_storage(
    data: StorageLotCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return QualityService.assign_to_storage(db, data)
