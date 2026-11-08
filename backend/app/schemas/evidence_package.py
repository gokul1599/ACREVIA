"""
ACREVIA - Crop Loss Evidence Package Pydantic Schemas.
Generates cryptographically sealed evidence bundles for insurance and disaster relief.
"""

from datetime import date, datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class CropLossEvidencePackageCreate(BaseModel):
    farm_id: str
    plot_id: str
    crop_season_id: str
    incident_date: date
    incident_type: str  # EXCESS_RAINFALL, CYCLONE_WIND, HAILSTORM, EXTREME_DROUGHT, PEST_OUTBREAK
    notes: Optional[str] = None


class CropLossEvidencePackageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    farm_id: str
    plot_id: str
    crop_season_id: str
    incident_date: date
    incident_type: str
    package_payload: Dict[str, Any] = Field(default_factory=dict, validation_alias="package_payload_json")
    package_hash: str
    generated_at: datetime
