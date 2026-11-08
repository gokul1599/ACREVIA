"""
ACREVIA - Yield Feasibility & Prediction Pydantic Schemas.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class HarvestMeasurementCreate(BaseModel):
    season_id: str
    harvest_date: datetime
    yield_quintals_per_acre: float = Field(..., gt=0.0, le=100.0)
    total_harvest_kg: float = Field(..., gt=0.0)
    provenance_tier: Literal["TIER_1_VERIFIED_WEIGHBRIDGE", "TIER_2_CCE_CUT", "TIER_3_FARMER_REPORT"] = "TIER_3_FARMER_REPORT"
    verification_document_url: Optional[str] = None
    notes: Optional[str] = None


class HarvestMeasurementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    plot_id: str
    season_id: str
    harvest_date: datetime
    yield_quintals_per_acre: float
    total_harvest_kg: float
    provenance_tier: str
    verification_document_url: Optional[str] = None


class YieldForecastResponse(BaseModel):
    plot_id: str
    crop_name: str
    forecast_status: Literal["WITHHELD_INSUFFICIENT_DATA", "READY_FOR_PILOT", "RESEARCH_ONLY"]
    is_forecast_available: bool
    sample_count_available: int
    minimum_sample_threshold_required: int = 50
    withholding_reason: Optional[str] = None
    predicted_yield_min: Optional[float] = None
    predicted_yield_max: Optional[float] = None
    confidence_score: Optional[float] = None
    scientific_disclaimer: str = (
        "Smallholder crop yield is subject to multi-factorial micro-climatic and management variance. "
        "Forecasts are strictly withheld when sample sizes are inadequate to prevent misleading estimates."
    )
