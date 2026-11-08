"""
ACREVIA - Agricultural Scenario Simulation API Endpoints (Pillar B: ACREVIA Simulate).
Provides counterfactual scenario execution and comparison.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.farm import Plot
from backend.app.models.simulation import SimulationScenario, SimulationResult
from backend.app.schemas.simulation import (
    SimulationScenarioCreate,
    SimulationScenarioResponse,
    SimulationResultResponse,
    ScenarioCompareRequest,
    ScenarioComparisonResponse,
)
from backend.app.security.dependencies import get_current_user, verify_farm_access
from backend.app.services.simulation_service import SimulationService

router = APIRouter(prefix="/simulations", tags=["Simulation"])


@router.post("/", response_model=SimulationScenarioResponse, status_code=status.HTTP_201_CREATED)
def create_and_run_simulation(
    data: SimulationScenarioCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submits and computes a counterfactual agricultural simulation scenario.
    """
    plot = db.get(Plot, data.plot_id)
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plot '{data.plot_id}' not found.",
        )
    verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)
    return SimulationService.run_simulation(user=current_user, data=data, db=db)


@router.get("/{id}", response_model=SimulationScenarioResponse)
def get_simulation_scenario(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves the status and metadata of a specific simulation scenario.
    """
    scenario = db.get(SimulationScenario, id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SimulationScenario '{id}' not found.",
        )
    plot = db.get(Plot, scenario.plot_id)
    if plot:
        verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)

    result_resp = None
    if scenario.result:
        res = scenario.result
        result_resp = SimulationResultResponse(
            id=res.id,
            scenario_id=res.scenario_id,
            model_name=res.model_name,
            model_version=res.model_version,
            outputs_json=res.outputs_json,
            uncertainty_metadata_json=res.uncertainty_metadata_json,
            evidence_sources_json=res.evidence_sources_json,
            execution_duration_ms=res.execution_duration_ms,
            completed_at=res.completed_at,
        )

    return SimulationScenarioResponse(
        id=scenario.id,
        plot_id=scenario.plot_id,
        crop_season_id=scenario.crop_season_id,
        creator_id=scenario.creator_id,
        scenario_type=scenario.scenario_type,
        scenario_name=scenario.scenario_name,
        status=scenario.status,
        baseline_snapshot_id=scenario.baseline_snapshot_id,
        input_parameters_json=scenario.input_parameters_json,
        farmer_assumptions_json=scenario.farmer_assumptions_json,
        constraints_json=scenario.constraints_json,
        result=result_resp,
        created_at=scenario.created_at,
    )


@router.get("/{id}/results", response_model=SimulationResultResponse)
def get_simulation_results(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves the computed outputs and uncertainty metadata of a simulation scenario.
    """
    scenario = db.get(SimulationScenario, id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SimulationScenario '{id}' not found.",
        )
    plot = db.get(Plot, scenario.plot_id)
    if plot:
        verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)

    if not scenario.result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result not yet available for scenario '{id}'.",
        )

    res = scenario.result
    return SimulationResultResponse(
        id=res.id,
        scenario_id=res.scenario_id,
        model_name=res.model_name,
        model_version=res.model_version,
        outputs_json=res.outputs_json,
        uncertainty_metadata_json=res.uncertainty_metadata_json,
        evidence_sources_json=res.evidence_sources_json,
        execution_duration_ms=res.execution_duration_ms,
        completed_at=res.completed_at,
    )


@router.post("/compare", response_model=ScenarioComparisonResponse)
def compare_scenarios(
    data: ScenarioCompareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Evaluates side-by-side trade-offs between two or more simulation runs.
    """
    return SimulationService.compare_scenarios(user=current_user, data=data, db=db)
