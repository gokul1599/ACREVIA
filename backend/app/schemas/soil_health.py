"""
ACREVIA - Soil Health Intelligence Pydantic Schemas.
Pillar A: Soil pedon profiles, field soil samples, accredited lab test results, and longitudinal history.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SoilProfileCreate(BaseModel):
    plot_id: str
    soil_order: str = "VERTISOL"
    soil_series_name: Optional[str] = None
    drainage_class: str = "MODERATELY_WELL_DRAINED"
    bulk_density_g_cm3: Optional[float] = 1.35
    effective_soil_depth_cm: Optional[float] = 90.0
    texture_class: str = "CLAY_LOAM"


class SoilProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    plot_id: str
    soil_order: str
    soil_series_name: Optional[str] = None
    drainage_class: str
    bulk_density_g_cm3: Optional[float] = None
    effective_soil_depth_cm: Optional[float] = None
    texture_class: str
    created_at: datetime


class SoilSampleCreate(BaseModel):
    plot_id: str
    profile_id: Optional[str] = None
    sample_code: str
    sampling_date: Optional[datetime] = None
    sampling_depth_min_cm: float = 0.0
    sampling_depth_max_cm: float = 15.0
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    composite_cores_count: int = 5


class SoilSampleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    plot_id: str
    profile_id: Optional[str] = None
    sampled_by_user_id: str
    sample_code: str
    sampling_date: datetime
    sampling_depth_min_cm: float
    sampling_depth_max_cm: float
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    composite_cores_count: int
    spatial_coverage_warning: Optional[str] = None
    status: str
    created_at: datetime


class SoilTestResultCreate(BaseModel):
    soil_sample_id: str
    laboratory_name: str
    accreditation_number: str
    ph: float
    electrical_conductivity_ec: float
    organic_carbon_percent: float
    available_nitrogen_kg_ha: float
    available_phosphorus_kg_ha: float
    available_potassium_kg_ha: float
    available_sulphur_ppm: Optional[float] = 12.0
    available_zinc_ppm: Optional[float] = 0.75
    available_iron_ppm: Optional[float] = 5.50
    available_boron_ppm: Optional[float] = 0.60
    provenance: Optional[Dict[str, Any]] = None


class SoilTestResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    soil_sample_id: str
    laboratory_name: str
    accreditation_number: str
    ph: float
    electrical_conductivity_ec: float
    organic_carbon_percent: float
    available_nitrogen_kg_ha: float
    available_phosphorus_kg_ha: float
    available_potassium_kg_ha: float
    available_sulphur_ppm: Optional[float] = None
    available_zinc_ppm: Optional[float] = None
    available_iron_ppm: Optional[float] = None
    available_boron_ppm: Optional[float] = None
    provenance_json: str
    verified_at: datetime
    created_at: datetime


class SoilPlotHistoryResponse(BaseModel):
    plot_id: str
    samples_count: int
    results: List[SoilTestResultResponse]
    soc_trend_percent: float = 0.0
    latest_ph: Optional[float] = None
    latest_nitrogen_status: str = "UNKNOWN"
