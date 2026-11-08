"""
ACREVIA - Crop, Variety & Season Schemas.
"""

from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field


class CropResponse(BaseModel):
    id: str
    name_en: str
    name_te: str
    name_hi: str
    scientific_name: str

    model_config = {"from_attributes": True}


class CropVarietyResponse(BaseModel):
    id: str
    crop_id: str
    name: str
    duration_days: int
    resistance_traits: Optional[str] = None

    model_config = {"from_attributes": True}


class CropSeasonCreateRequest(BaseModel):
    plot_id: str
    crop_id: str = Field(..., pattern="^(cotton|rice|chilli)$")
    variety_id: Optional[str] = None
    season_type: str = Field(default="KHARIF", pattern="^(KHARIF|RABI|SUMMER)$")
    sowing_date: date
    current_stage: str = Field(default="SOWING")


class CropSeasonResponse(BaseModel):
    id: str
    plot_id: str
    crop_id: str
    variety_id: Optional[str] = None
    season_type: str
    sowing_date: date
    current_stage: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CropStageEventCreateRequest(BaseModel):
    stage_name: str = Field(..., min_length=2, max_length=50)
    event_date: date
    notes: Optional[str] = None


class CropStageEventResponse(BaseModel):
    id: str
    crop_season_id: str
    stage_name: str
    event_date: date
    notes: Optional[str] = None

    model_config = {"from_attributes": True}
