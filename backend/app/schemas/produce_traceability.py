"""
ACREVIA - Produce Traceability Pydantic Schemas.
Pillar E: Internal lot lifecycle, movement balance, and public QR verification.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict


class LotMovementCreate(BaseModel):
    movement_type: str = "STORAGE_ENTRY"  # HARVEST_IN, STORAGE_ENTRY, TRANSFER, SALE, SPLIT, DISCARD
    source_location: str
    destination_location: str
    quantity_transferred: Decimal
    unit: str = "QUINTAL"
    actor_name: str
    notes: Optional[str] = None


class LotMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    lot_id: str
    movement_type: str
    source_location: str
    destination_location: str
    quantity_transferred: Decimal
    unit: str
    actor_name: str
    movement_timestamp: datetime
    notes: Optional[str] = None


class ProduceLotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    lot_code: str
    qr_token: str
    farm_id: str
    plot_id: str
    crop_season_id: str
    harvest_session_id: Optional[str] = None
    crop_id: str
    variety_name: Optional[str] = None
    harvest_date: date
    initial_quantity: Decimal
    remaining_quantity: Decimal
    unit: str
    current_status: str
    created_at: datetime


class ProduceLotDetailResponse(ProduceLotResponse):
    movements: List[LotMovementResponse] = []


class QualitySummaryItem(BaseModel):
    parameter_name: str
    measured_value: Decimal
    unit: str
    method: str


class ProduceLotPublicResponse(BaseModel):
    """
    Publicly visible provenance data returned when scanning a produce QR code.
    Strictly redacts farmer PII, phone numbers, exact plot GPS coordinates, and private receipts.
    """
    lot_code: str
    crop_name: str
    variety: Optional[str] = None
    harvest_date: date
    district: str
    state: str
    origin_verification: str  # VERIFIED_ACREVIA_FARM
    quality_parameters: List[QualitySummaryItem] = []
    overall_grade: str
    traceability_status: str
    public_notice: str = "Farmer identity and exact plot coordinates are protected under ACREVIA Data Governance."
