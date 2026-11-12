"""
ACREVIA - Pydantic Schemas for NASA POWER Agroclimatology API.
Captures all-sky surface solar radiation, precipitation, temperature,
and climatological baseline indices for agricultural water resilience modeling.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class NASAPowerDailyPoint(BaseModel):
    """Daily agroclimatological indicators for a single observation date."""
    date: str = Field(..., description="Observation date (YYYY-MM-DD or YYYYMMDD)")
    solar_radiation_allsky_sw: float = Field(..., description="All Sky Surface SW Downward Irradiance (MJ/m²/day)")
    temperature_2m: float = Field(..., description="Mean Temperature at 2 Meters (°C)")
    relative_humidity_2m: float = Field(..., description="Relative Humidity at 2 Meters (%)")
    precipitation_corrected: float = Field(..., description="Precipitation Corrected (mm/day)")


class NASAPowerClimatologyBaseline(BaseModel):
    """
    Standardized payload for multi-day or climatological baseline data from NASA POWER.
    Guarantees non-override status and attaches scientific attribution.
    """
    status: str = Field(..., description="CONFIGURED, DEGRADED, or UNAVAILABLE")
    latitude: float
    longitude: float
    is_dithered: bool = Field(True, description="True if coordinates were dithered for privacy")
    retrieval_timestamp: str
    solar_radiation_mean_daily: float = Field(..., description="Mean daily solar radiation in MJ/m²/day")
    precipitation_total_period: float = Field(..., description="Total precipitation over queried period in mm")
    temperature_mean_period: float = Field(..., description="Mean temperature over queried period in °C")
    records: List[NASAPowerDailyPoint] = Field(default_factory=list)
    data_source: str = "NASA_POWER_AGROCLIMATOLOGY"
    epistemic_status: str = "CLIMATOLOGICAL_REMOTE_ESTIMATE"
    is_measured_in_situ: bool = False
    non_override_guarantee: bool = True
    scientific_disclaimer: str = (
        "Agroclimatology indicators are 0.5° × 0.5° regional estimates from NASA POWER. "
        "Intended for long-term water budgeting, solar potential, and drought risk profiling."
    )
    attribution: str = "Data obtained from NASA Langley Research Center POWER Project (Agroclimatology Community)"
    is_cached: bool = False
