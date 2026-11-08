"""
ACREVIA - Sustainable Agriculture Pydantic Schemas.
Pillar E: Sustainable practices, farm practice logs, empirical SOC tracking, research GHG balances, and scorecards.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AgriculturalPracticeDefinitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    code: str
    category: str
    title_en: str
    title_te: str
    title_hi: str
    description_en: str
    specification_json: str


class FarmPracticeRecordCreate(BaseModel):
    plot_id: str
    practice_code: str
    implementation_date: Optional[datetime] = None
    area_covered_acres: float
    verification_method: str = "FARMER_LOG"


class FarmPracticeRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    plot_id: str
    practice_code: str
    implementation_date: datetime
    area_covered_acres: float
    verification_method: str
    status: str
    created_at: datetime


class SoilCarbonMeasurementCreate(BaseModel):
    plot_id: str
    sample_date: Optional[datetime] = None
    depth_cm: float = 15.0
    soc_percent: float
    bulk_density: Optional[float] = 1.35
    method: str = "WALKLEY_BLACK"
    lab_accreditation: str = "NABL"


class SoilCarbonMeasurementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    plot_id: str
    sample_date: datetime
    depth_cm: float
    soc_percent: float
    bulk_density: Optional[float] = None
    method: str
    lab_accreditation: str
    created_at: datetime


class EnvironmentalAccountingEstimateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    plot_id: str
    season: str
    year: int
    fertilizer_n2o_kg_co2e: float
    paddy_ch4_kg_co2e: float
    fuel_combustion_kg_co2e: float
    total_emissions_kg_co2e: float
    emission_intensity_kg_co2e_per_kg: Optional[float] = None
    is_certified: bool
    scientific_disclaimer: str


class SeasonalSustainabilityScorecardResponse(BaseModel):
    plot_id: str
    season: str
    year: int
    sustainability_index: float  # 0.0 - 100.0
    soil_cover_score: float
    water_efficiency_score: float
    nutrient_balance_score: float
    ipm_adoption_score: float
    biodiversity_score: float
    verified_practices: List[str]
    disclaimer: str
