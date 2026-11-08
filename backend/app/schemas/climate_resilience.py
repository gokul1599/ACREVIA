"""
ACREVIA - Climate Resilience Pydantic Schemas.
Pillar C: 30-year climatological baselines, hazard exposure assessments, and adaptation scenarios.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ClimateBaselineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    district_code: str
    month: int
    normal_rainfall_mm: float
    normal_tmax_celsius: float
    normal_tmin_celsius: float
    extreme_heat_days_p90: float
    dry_spell_frequency: float
    heavy_rain_days_count: float
    baseline_period: str


class ClimateExposureAssessmentRequest(BaseModel):
    plot_id: str
    crop_id: Optional[str] = None
    crop_stage: str = "FLOWERING_BOLL_FORMATION"
    forecast_tmax: Optional[float] = 38.0
    forecast_rainfall_next_7_days: Optional[float] = 0.0
    consecutive_rainless_days: Optional[int] = 14


class ClimateAdaptationScenarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    assessment_id: str
    title: str
    description: str
    projected_loss_reduction_percent: float
    cost_delta_inr: float
    intervention_actions_json: str


class ClimateExposureAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    plot_id: str
    crop_id: Optional[str] = None
    hazard_type: str
    severity_level: str
    crop_stage: str
    vulnerability_score: float
    forecast_tmax: Optional[float] = None
    forecast_rainfall_next_7_days: Optional[float] = None
    consecutive_rainless_days: Optional[int] = None
    recommended_adaptation: str
    institutional_citation: str
    assessed_at: datetime
    scenarios: List[ClimateAdaptationScenarioResponse] = Field(default_factory=list)
