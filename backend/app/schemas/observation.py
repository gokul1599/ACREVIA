"""
ACREVIA - Observation & Foliar Media Schemas.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ObservationCreateRequest(BaseModel):
    farm_id: str
    plot_id: Optional[str] = None
    crop_season_id: Optional[str] = None
    notes: Optional[str] = None
    symptom_tags: Optional[str] = None


class ObservationMediaResponse(BaseModel):
    id: str
    observation_id: str
    storage_path: str
    file_size_bytes: int
    mime_type: str
    sha256_hash: str
    is_primary: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ObservationResponse(BaseModel):
    id: str
    farm_id: str
    plot_id: Optional[str] = None
    crop_season_id: Optional[str] = None
    observer_id: str
    notes: Optional[str] = None
    symptom_tags: Optional[str] = None
    created_at: datetime
    media: List[ObservationMediaResponse] = []

    model_config = {"from_attributes": True}
