"""
ACREVIA - Post-Harvest Quality & Storage Pydantic Schemas.
Pillar D: Moisture provenance, quality assay recording, and storage lot assignments.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class QualityMeasurementCreate(BaseModel):
    session_id: Optional[str] = None
    lot_id: Optional[str] = None
    parameter_name: str  # MOISTURE_PCT, STAPLE_LENGTH_MM, MICRONAIRE, ASTA_COLOR, FOREIGN_MATTER_PCT, BROKEN_GRAIN_PCT
    measured_value: Decimal
    unit: str  # %, mm, ASTA, SHU
    measurement_method: str = "MEASURED_DIGITAL_SENSOR"  # MEASURED_DIGITAL_SENSOR, VERIFIED_LAB_ASSAY, FARMER_VISUAL_ESTIMATE
    instrument_details: Optional[str] = None


class QualityMeasurementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    session_id: Optional[str] = None
    lot_id: Optional[str] = None
    parameter_name: str
    measured_value: Decimal
    unit: str
    measurement_method: str
    instrument_details: Optional[str] = None
    measured_at: datetime


class StorageLocationCreate(BaseModel):
    farm_id: str
    name: str
    storage_type: str = "COMMERCIAL_COLD_STORAGE"  # ON_FARM_SHED, HERMETIC_BAGS, COMMERCIAL_COLD_STORAGE, CWC_TSWC_WAREHOUSE
    capacity_quintals: Decimal
    district: str
    is_temperature_controlled: bool = False


class StorageLocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    farm_id: str
    name: str
    storage_type: str
    capacity_quintals: Decimal
    district: str
    is_temperature_controlled: bool


class StorageLotCreate(BaseModel):
    lot_id: str
    storage_location_id: str
    quantity_stored: Decimal
    unit: str = "QUINTAL"
    entry_date: date


class StorageLotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    lot_id: str
    storage_location_id: str
    quantity_stored: Decimal
    unit: str
    entry_date: date
    exit_date: Optional[date] = None
    current_status: str
