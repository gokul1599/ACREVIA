"""
ACREVIA - Harvest Operations API Endpoints.
Pillar C: Harvest plans, picking session tracking, loss accounting, and lot generation.
"""

from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.farm import Plot
from backend.app.schemas.harvest_operations import (
    HarvestPlanCreate,
    HarvestPlanResponse,
    HarvestSessionCreate,
    HarvestSessionResponse,
)
from backend.app.security.dependencies import get_current_user, verify_farm_access
from backend.app.services.harvest_service import HarvestService

router = APIRouter(prefix="/harvest", tags=["Harvest Operations"])


@router.post("/plans", response_model=HarvestPlanResponse, status_code=status.HTTP_201_CREATED)
def create_harvest_plan(
    data: HarvestPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plot = db.get(Plot, data.plot_id)
    if plot:
        verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)
    return HarvestService.create_harvest_plan(db, data)


@router.get("/plans", response_model=List[HarvestPlanResponse], status_code=status.HTTP_200_OK)
def list_harvest_plans(
    crop_season_id: str = Query(..., description="Crop season ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return HarvestService.get_harvest_plans(db, crop_season_id=crop_season_id)


@router.post("/sessions", response_model=HarvestSessionResponse, status_code=status.HTTP_201_CREATED)
def record_harvest_session(
    data: HarvestSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plot = db.get(Plot, data.plot_id)
    if plot:
        verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)
    data.recorded_by_user_id = current_user.id
    return HarvestService.create_harvest_session(db, data)


@router.get("/sessions", response_model=List[HarvestSessionResponse], status_code=status.HTTP_200_OK)
def list_harvest_sessions(
    crop_season_id: str = Query(..., description="Crop season ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = HarvestService.get_harvest_sessions(db, crop_season_id=crop_season_id)
    responses = []
    for s in sessions:
        responses.append(
            HarvestSessionResponse(
                id=s.id,
                plot_id=s.plot_id,
                crop_season_id=s.crop_season_id,
                harvest_plan_id=s.harvest_plan_id,
                picking_number=s.picking_number,
                harvest_date=s.harvest_date,
                harvested_quantity=s.harvested_quantity,
                unit=s.unit,
                quantity_type=s.quantity_type,
                loss_quantity=s.loss_quantity,
                notes=s.notes,
                recorded_by_user_id=s.recorded_by_user_id,
                created_at=s.created_at,
            )
        )
    return responses
