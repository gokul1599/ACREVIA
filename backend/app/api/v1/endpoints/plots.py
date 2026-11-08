"""
ACREVIA - Plot & Plant Management Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.farm import (
    PlotCreateRequest,
    PlotResponse,
    PlantCreateRequest,
    PlantResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.farm_service import FarmService

router = APIRouter(tags=["Plots & Plants"])


@router.post("/farms/{farm_id}/plots", response_model=PlotResponse, status_code=status.HTTP_201_CREATED)
def create_plot(
    farm_id: str,
    data: PlotCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new cultivation plot within a farm.
    """
    return FarmService.create_plot(farm_id=farm_id, data=data, current_user=current_user, db=db)


@router.get("/farms/{farm_id}/plots", response_model=List[PlotResponse])
def list_plots(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists all plots belonging to a specific farm holding.
    """
    return FarmService.list_plots(farm_id=farm_id, current_user=current_user, db=db)


@router.get("/plots/{plot_id}", response_model=PlotResponse)
def get_plot(
    plot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves plot details.
    """
    return FarmService.get_plot(plot_id=plot_id, current_user=current_user, db=db)


@router.post("/plots/{plot_id}/plants", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
def create_plant(
    plot_id: str,
    data: PlantCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tags a specific plant or quadrant within a cultivation plot.
    """
    return FarmService.create_plant(plot_id=plot_id, data=data, current_user=current_user, db=db)


@router.get("/plots/{plot_id}/plants", response_model=List[PlantResponse])
def list_plants(
    plot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists tagged plants within a cultivation plot.
    """
    return FarmService.list_plants(plot_id=plot_id, current_user=current_user, db=db)
