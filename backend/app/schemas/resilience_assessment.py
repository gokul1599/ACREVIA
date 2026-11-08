"""
ACREVIA - Agricultural Resilience Engine Pydantic Schemas.
Pillar F: Multi-dimensional farm resilience evaluations, evidence quality audits, and adaptation simulations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ResilienceAssessRequest(BaseModel):
    plot_id: str


class ResilienceScenarioSimulationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    assessment_id: str
    package_name: str
    simulated_overall_score: float
    projected_water_saving_percent: float
    cost_delta_inr: float
    yield_risk_reduction_percent: float
    simulated_at: datetime


class ResilienceAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    plot_id: str
    overall_resilience_score: float
    soil_score: float
    water_score: float
    climate_score: float
    nutrient_score: float
    practice_score: float
    evidence_quality_score: float
    confidence_category: str
    top_vulnerabilities_json: str
    adaptation_recommendations_json: str
    evaluated_at: datetime
    simulations: List[ResilienceScenarioSimulationResponse] = Field(default_factory=list)


class ResilienceSimulationRequest(BaseModel):
    plot_id: str
    package_name: str = "REGENERATIVE_INTEGRATED_PACKAGE"
