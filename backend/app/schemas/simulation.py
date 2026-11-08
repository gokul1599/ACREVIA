"""
ACREVIA - Agricultural Scenario Simulation Pydantic Schemas.
Pillar B: Scenario definition, execution request, and counterfactual result contracts.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SimulationScenarioCreate(BaseModel):
    plot_id: str
    crop_season_id: Optional[str] = None
    scenario_name: str
    scenario_type: str = "IRRIGATION_WATER_BALANCE"  # IRRIGATION_WATER_BALANCE, THERMAL_GDD_STAGE, WATERLOGGING_STRESS
    baseline_snapshot_id: Optional[str] = None
    input_parameters: Dict[str, Any] = Field(default_factory=dict)
    farmer_assumptions: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)


class SimulationResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    scenario_id: str
    model_name: str
    model_version: str
    outputs: Dict[str, Any] = Field(default_factory=dict, validation_alias="outputs_json")
    uncertainty_metadata: Dict[str, Any] = Field(default_factory=dict, validation_alias="uncertainty_metadata_json")
    evidence_sources: List[Any] = Field(default_factory=list, validation_alias="evidence_sources_json")
    execution_duration_ms: float
    completed_at: datetime


class SimulationScenarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    plot_id: str
    crop_season_id: Optional[str] = None
    creator_id: str
    scenario_type: str
    scenario_name: str
    status: str
    baseline_snapshot_id: Optional[str] = None
    input_parameters: Dict[str, Any] = Field(default_factory=dict, validation_alias="input_parameters_json")
    farmer_assumptions: Dict[str, Any] = Field(default_factory=dict, validation_alias="farmer_assumptions_json")
    constraints: Dict[str, Any] = Field(default_factory=dict, validation_alias="constraints_json")
    result: Optional[SimulationResultResponse] = None
    created_at: datetime


class ScenarioCompareRequest(BaseModel):
    scenario_ids: List[str]


class ScenarioComparisonItem(BaseModel):
    scenario_id: str
    scenario_name: str
    scenario_type: str
    key_metrics: Dict[str, Any]
    uncertainty_bounds: Dict[str, Any]


class ScenarioComparisonResponse(BaseModel):
    scenarios: List[ScenarioComparisonItem]
    comparison_summary: Dict[str, Any]
    trade_off_recommendation: Optional[str] = None
