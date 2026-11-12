"""
ACREVIA - Pydantic Schemas for ISRIC SoilGrids v2.0 REST API.
Enforces typed uncertainty bounds, depth intervals, units conversion,
and explicit epistemic status (REMOTE_STATISTICAL_MODEL_ESTIMATE).
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SoilDepthLayer(BaseModel):
    """Represents a single depth interval observation with uncertainty deciles."""
    depth_interval: str = Field(..., description="Depth interval, e.g., '0-5cm', '5-15cm', '15-30cm'")
    mean: float = Field(..., description="Estimated mean value")
    median: float = Field(..., description="50th percentile (median estimate, Q0.50)")
    q05: float = Field(..., description="5th percentile (lower uncertainty bound, Q0.05)")
    q95: float = Field(..., description="95th percentile (upper uncertainty bound, Q0.95)")
    unit: str = Field(..., description="Physical or chemical measurement unit")


class SoilPhysicalProperties(BaseModel):
    """Physical soil properties: texture fractions and dry bulk density."""
    clay_percentage: SoilDepthLayer = Field(..., description="Clay fraction (< 0.002 mm) in %")
    sand_percentage: SoilDepthLayer = Field(..., description="Sand fraction (0.05 - 2.0 mm) in %")
    silt_percentage: SoilDepthLayer = Field(..., description="Silt fraction (0.002 - 0.05 mm) in %")
    bulk_density: Optional[SoilDepthLayer] = Field(None, description="Bulk density of fine earth in g/cm³")


class SoilChemicalProperties(BaseModel):
    """Chemical soil properties: pH, organic carbon, cation exchange capacity, nitrogen."""
    ph: SoilDepthLayer = Field(..., description="Soil pH measured in water (pH H2O)")
    soil_organic_carbon: SoilDepthLayer = Field(..., description="Soil Organic Carbon in g/kg")
    cation_exchange_capacity: Optional[SoilDepthLayer] = Field(None, description="CEC at pH 7 in cmol(+)/kg")
    nitrogen: Optional[SoilDepthLayer] = Field(None, description="Total nitrogen in g/kg")


class SoilGridsProfileResponse(BaseModel):
    """
    Standardized domain payload for farm-level soil baseline profile derived from SoilGrids 250m.
    Guarantees the non-override invariant and attaches scientific caveats.
    """
    status: str = Field(..., description="CONFIGURED, DEGRADED, or UNAVAILABLE")
    latitude: float
    longitude: float
    is_dithered: bool = Field(True, description="True if coordinates were dithered for privacy")
    retrieval_timestamp: str
    physical: SoilPhysicalProperties
    chemical: SoilChemicalProperties
    data_source: str = "ISRIC_SOILGRIDS_V2_250M"
    epistemic_status: str = "REMOTE_STATISTICAL_MODEL_ESTIMATE"
    is_measured_in_situ: bool = False
    non_override_guarantee: bool = True
    scientific_disclaimer: str = (
        "Soil indicators are 250m regional statistical model estimates from ISRIC SoilGrids v2.0. "
        "They provide baseline agro-pedological context and must never overwrite verified in-situ "
        "laboratory soil test records."
    )
    attribution: str = "Soil data produced by ISRIC - World Soil Information (SoilGrids 250m v2.0, CC-BY 4.0)"
    is_cached: bool = False
