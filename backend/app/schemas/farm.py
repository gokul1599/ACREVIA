"""
ACREVIA - Farm, Membership & Plot Schemas.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class FarmCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    district: str = Field(..., min_length=2, max_length=50)  # Telangana district
    mandal: str = Field(..., min_length=2, max_length=50)
    village: str = Field(..., min_length=2, max_length=50)
    total_acreage: float = Field(default=1.0, ge=0.1, le=10000.0)


class FarmUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    district: Optional[str] = None
    mandal: Optional[str] = None
    village: Optional[str] = None
    total_acreage: Optional[float] = Field(None, ge=0.1)


class FarmResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    state: str
    district: str
    mandal: str
    village: str
    total_acreage: float
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FarmMembershipCreateRequest(BaseModel):
    user_id: str
    role_in_farm: str = Field(default="WORKER", pattern="^(OWNER|MANAGER|WORKER|AGRONOMIST_ADVISOR)$")


class FarmMembershipResponse(BaseModel):
    id: str
    farm_id: str
    user_id: str
    role_in_farm: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PlotCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    soil_type: str = Field(default="BLACK_COTTON", pattern="^(BLACK_COTTON|RED_CHALKA|ALLUVIAL|LOAMY)$")
    irrigation_source: str = Field(default="BOREWELL", pattern="^(BOREWELL|CANAL|RAINFED|DRIP|WELL)$")
    acreage: float = Field(default=1.0, ge=0.01, le=5000.0)
    boundary_geojson: Optional[str] = None


class PlotUpdateRequest(BaseModel):
    name: Optional[str] = None
    soil_type: Optional[str] = None
    irrigation_source: Optional[str] = None
    acreage: Optional[float] = Field(None, ge=0.01)
    boundary_geojson: Optional[str] = None


class PlotResponse(BaseModel):
    id: str
    farm_id: str
    name: str
    soil_type: str
    irrigation_source: str
    acreage: float
    boundary_geojson: Optional[str] = None
    is_archived: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PlantCreateRequest(BaseModel):
    tag_code: str = Field(..., min_length=1, max_length=50)
    crop_id: str = Field(..., pattern="^(cotton|rice|chilli)$")
    notes: Optional[str] = None


class PlantResponse(BaseModel):
    id: str
    plot_id: str
    tag_code: str
    crop_id: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
