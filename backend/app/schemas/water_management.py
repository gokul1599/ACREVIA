"""
ACREVIA - Precision Water Management Pydantic Schemas.
Pillar B: Water sources, irrigation events, soil moisture observations, water balances, and scenario comparisons.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class WaterSourceCreate(BaseModel):
    farm_id: str
    source_type: str  # BOREWELL, OPEN_WELL, CANAL_OUTLET, FARM_POND, TANKER
    source_name: str
    depth_meters: Optional[float] = None
    static_water_level_m: Optional[float] = None
    discharge_capacity_lps: Optional[float] = None
    salinity_ec_dsm: Optional[float] = 0.75
    ph: Optional[float] = 7.2
    sar: Optional[float] = 2.0
    seasonal_availability: Optional[Dict[str, bool]] = None


class WaterSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    farm_id: str
    source_type: str
    source_name: str
    depth_meters: Optional[float] = None
    static_water_level_m: Optional[float] = None
    discharge_capacity_lps: Optional[float] = None
    salinity_ec_dsm: Optional[float] = None
    ph: Optional[float] = None
    sar: Optional[float] = None
    seasonal_availability_json: str
    created_at: datetime


class IrrigationEventCreate(BaseModel):
    plot_id: str
    water_source_id: Optional[str] = None
    event_date: Optional[datetime] = None
    irrigation_method: str = "DRIP"  # DRIP, SPRINKLER, FLOOD, ALTERNATE_FURROW
    duration_hours: float
    flow_meter_start_m3: Optional[float] = None
    flow_meter_end_m3: Optional[float] = None
    soil_moisture_before: Optional[float] = None
    soil_moisture_after: Optional[float] = None


class IrrigationEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    plot_id: str
    water_source_id: Optional[str] = None
    event_date: datetime
    irrigation_method: str
    duration_hours: float
    calculated_volume_m3: float
    equivalent_depth_mm: float
    soil_moisture_before: Optional[float] = None
    soil_moisture_after: Optional[float] = None
    created_at: datetime


class SoilMoistureObservationCreate(BaseModel):
    plot_id: str
    sensor_id: str
    depth_cm: int  # 15, 30, 60
    volumetric_water_content: float
    matric_potential_kpa: Optional[float] = None
    moisture_status: str = "FIELD_CAPACITY"


class SoilMoistureObservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    plot_id: str
    sensor_id: str
    depth_cm: int
    volumetric_water_content: float
    matric_potential_kpa: Optional[float] = None
    moisture_status: str
    observed_at: datetime


class WaterBalanceSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    plot_id: str
    snapshot_date: datetime
    effective_precipitation_mm: float
    irrigation_applied_mm: float
    crop_evapotranspiration_mm: float
    deep_percolation_mm: float
    runoff_mm: float
    storage_change_mm: float
    accounting_status: str
    management_allowed_depletion_percent: float
    current_depletion_percent: float


class WaterScenarioComparisonRequest(BaseModel):
    plot_id: str
    baseline_method: str = "FLOOD"
    proposed_method: str = "DRIP"
    crop_name: str = "Cotton"
    crop_season_days: int = 150


class WaterScenarioOption(BaseModel):
    method: str
    total_water_m3: float
    water_saving_percent: float
    projected_yield_kg_per_acre: float
    energy_cost_inr: float


class WaterScenarioComparisonResponse(BaseModel):
    plot_id: str
    crop_name: str
    scenarios: List[WaterScenarioOption]
    recommended_strategy: str
