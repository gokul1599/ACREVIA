"""
ACREVIA - Agricultural Resource Optimization Pydantic Schemas.
Pillar C: Constrained resource formulation, decision variables, and solver responses.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class OptimizationProblemCreate(BaseModel):
    farm_id: str
    plot_id: Optional[str] = None
    problem_type: str = "WATER_ALLOCATION"  # WATER_ALLOCATION, INPUT_BUDGET_ALLOCATION
    objective_type: str = "MAXIMIZE_WATER_PRODUCTIVITY"  # MAXIMIZE_WATER_PRODUCTIVITY, MINIMIZE_STRESS, MINIMIZE_COST
    decision_variables: Dict[str, Any] = Field(default_factory=dict)
    hard_constraints: Dict[str, Any] = Field(default_factory=dict)
    soft_constraints: Dict[str, Any] = Field(default_factory=dict)


class OptimizationResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    problem_id: str
    feasibility_status: str  # FEASIBLE, INFEASIBLE
    selected_solution: Dict[str, Any] = Field(default_factory=dict, validation_alias="selected_solution_json")
    alternative_solutions: List[Any] = Field(default_factory=list, validation_alias="alternative_solutions_json")
    conflicting_constraints: List[Any] = Field(default_factory=list, validation_alias="conflicting_constraints_json")
    trade_off_analysis: Dict[str, Any] = Field(default_factory=dict, validation_alias="trade_off_analysis_json")
    solver_name: str
    solved_at: datetime


class OptimizationProblemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    farm_id: str
    plot_id: Optional[str] = None
    problem_type: str
    objective_type: str
    status: str
    decision_variables: Dict[str, Any] = Field(default_factory=dict, validation_alias="decision_variables_json")
    hard_constraints: Dict[str, Any] = Field(default_factory=dict, validation_alias="hard_constraints_json")
    soft_constraints: Dict[str, Any] = Field(default_factory=dict, validation_alias="soft_constraints_json")
    result: Optional[OptimizationResultResponse] = None
    created_at: datetime
