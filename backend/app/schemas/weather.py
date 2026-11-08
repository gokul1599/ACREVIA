"""
ACREVIA - Weather & Risk Assessment Schemas.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class WeatherObservationResponse(BaseModel):
    id: str
    farm_id: str
    timestamp: datetime
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
    source: str

    model_config = {"from_attributes": True}


class RiskAssessmentResponse(BaseModel):
    id: str
    farm_id: str
    crop_season_id: Optional[str] = None
    assessment_date: date
    pest_risk_level: str
    weather_risk_level: str
    advisory: str

    model_config = {"from_attributes": True}


class FarmWeatherReportResponse(BaseModel):
    farm_id: str
    district: str
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
    source: str
    pest_risk_level: str
    weather_risk_level: str
    advisory: str
