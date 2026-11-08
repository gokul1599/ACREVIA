"""
ACREVIA - Agricultural Resource Optimization API Endpoints (Pillar C: ACREVIA Optimize).
Provides constrained resource allocation solving and transparent infeasibility reporting.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.optimization import OptimizationProblem, OptimizationResult
from backend.app.schemas.optimization import (
    OptimizationProblemCreate,
    OptimizationProblemResponse,
    OptimizationResultResponse,
)
from backend.app.security.dependencies import get_current_user, verify_farm_access
from backend.app.services.optimization_service import OptimizationService

router = APIRouter(prefix="/optimization", tags=["Optimization"])


@router.post("/problems", response_model=OptimizationProblemResponse, status_code=status.HTTP_201_CREATED)
def solve_optimization_problem(
    data: OptimizationProblemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submits a constrained agricultural resource optimization problem and computes solution.
    """
    verify_farm_access(farm_id=data.farm_id, user=current_user, db=db)
    return OptimizationService.solve_problem(user=current_user, data=data, db=db)


@router.get("/problems/{id}", response_model=OptimizationProblemResponse)
def get_optimization_problem(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves the definition and status of an optimization problem.
    """
    problem = db.get(OptimizationProblem, id)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OptimizationProblem '{id}' not found.",
        )
    verify_farm_access(farm_id=problem.farm_id, user=current_user, db=db)

    result_resp = None
    if problem.result:
        res = problem.result
        result_resp = OptimizationResultResponse(
            id=res.id,
            problem_id=res.problem_id,
            feasibility_status=res.feasibility_status,
            selected_solution_json=res.selected_solution_json,
            alternative_solutions_json=res.alternative_solutions_json,
            conflicting_constraints_json=res.conflicting_constraints_json,
            trade_off_analysis_json=res.trade_off_analysis_json,
            solver_name=res.solver_name,
            solved_at=res.solved_at,
        )

    return OptimizationProblemResponse(
        id=problem.id,
        farm_id=problem.farm_id,
        plot_id=problem.plot_id,
        problem_type=problem.problem_type,
        objective_type=problem.objective_type,
        status=problem.status,
        decision_variables_json=problem.decision_variables_json,
        hard_constraints_json=problem.hard_constraints_json,
        soft_constraints_json=problem.soft_constraints_json,
        result=result_resp,
        created_at=problem.created_at,
    )


@router.get("/problems/{id}/results", response_model=OptimizationResultResponse)
def get_optimization_result(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves the computed solution or infeasibility diagnosis for an optimization problem.
    """
    problem = db.get(OptimizationProblem, id)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OptimizationProblem '{id}' not found.",
        )
    verify_farm_access(farm_id=problem.farm_id, user=current_user, db=db)

    if not problem.result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result not yet available for problem '{id}'.",
        )

    res = problem.result
    return OptimizationResultResponse(
        id=res.id,
        problem_id=res.problem_id,
        feasibility_status=res.feasibility_status,
        selected_solution_json=res.selected_solution_json,
        alternative_solutions_json=res.alternative_solutions_json,
        conflicting_constraints_json=res.conflicting_constraints_json,
        trade_off_analysis_json=res.trade_off_analysis_json,
        solver_name=res.solver_name,
        solved_at=res.solved_at,
    )
