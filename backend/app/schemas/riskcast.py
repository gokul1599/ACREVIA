"""
ACREVIA - RiskCast Pydantic Schemas.
Data contracts for agrometeorology, rule catalogues, plot risk evaluations, and alerts.
"""

from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class WeatherDataSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    farm_id: str
    district: str
    is_forecast: bool
    observation_time: datetime
    forecast_target_time: Optional[datetime] = None
    temperature_celsius: float
    relative_humidity: float
    precipitation_mm: float
    wind_speed_kmh: float
    leaf_wetness_hours: float
    source_provider: str
    created_at: datetime


class RiskRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    rule_code: str
    crop: str
    target_threat: str
    applicable_growth_stages: str
    min_temp: Optional[float] = None
    max_temp: Optional[float] = None
    min_humidity: Optional[float] = None
    min_leaf_wetness_hours: Optional[float] = None
    min_consecutive_wet_days: Optional[int] = None
    severity_level: str
    advisory_en: str
    advisory_te: str
    advisory_hi: str
    evidence_citations: List[str] = Field(default_factory=list)
    version: str
    is_active: bool


class TriggeredRuleDetail(BaseModel):
    rule_code: str
    target_threat: str
    severity_level: str
    advisory_en: str
    advisory_te: str
    advisory_hi: str
    citations: List[str] = Field(default_factory=list)


class RiskAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    plot_id: str
    farm_id: str
    crop_season_id: Optional[str] = None
    evaluation_timestamp: datetime
    overall_risk_level: str
    weather_data_id: Optional[str] = None
    weather_summary: Optional[dict] = None
    rules_triggered: List[TriggeredRuleDetail] = Field(default_factory=list)
    advisory_en: str
    advisory_te: str
    advisory_hi: str
    limitations_notice: str


class RiskAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    farm_id: str
    plot_id: str
    risk_assessment_id: str
    alert_level: str
    title: str
    message_en: str
    message_te: str
    message_hi: str
    recommended_actions: List[str] = Field(default_factory=list)
    is_acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    is_dismissed: bool
    dismissed_at: Optional[datetime] = None
    created_at: datetime


class PlotRiskSummary(BaseModel):
    plot_id: str
    plot_name: str
    crop_id: Optional[str] = None
    growth_stage: Optional[str] = None
    current_risk_level: str
    top_threat: Optional[str] = None
    advisory: str
    active_alerts_count: int = 0


class FarmRiskOverviewResponse(BaseModel):
    farm_id: str
    district: str
    current_weather: Optional[dict] = None
    plots_risk_summary: List[PlotRiskSummary] = Field(default_factory=list)
    active_alerts: List[RiskAlertResponse] = Field(default_factory=list)
