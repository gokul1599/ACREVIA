"""
ACREVIA - Satellite Intelligence & Remote Sensing Schemas.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from backend.app.models.satellite import SATELLITE_EVIDENCE_DISCLAIMER


class SatelliteObservationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    observation_date: datetime
    mean_ndvi: float
    min_ndvi: float
    max_ndvi: float
    std_ndvi: float
    mean_evi: float
    mean_ndmi: float
    cloud_masked_pixel_ratio: float
    trend_classification: str


class SatelliteTimeSeriesResponse(BaseModel):
    plot_id: str
    trend_summary: str
    observations_count: int
    evidence_disclaimer: str = SATELLITE_EVIDENCE_DISCLAIMER
    time_series: List[SatelliteObservationItem]


class SatelliteLatestResponse(BaseModel):
    plot_id: str
    observation: Optional[SatelliteObservationItem] = None
    evidence_disclaimer: str = SATELLITE_EVIDENCE_DISCLAIMER
