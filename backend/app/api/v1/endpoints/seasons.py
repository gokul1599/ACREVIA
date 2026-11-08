"""
ACREVIA - Crop Seasons & Phenological Tracking Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.crop import (
    CropSeasonCreateRequest,
    CropSeasonResponse,
    CropStageEventCreateRequest,
    CropStageEventResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.farm_service import FarmService

router = APIRouter(tags=["Crop Seasons"])


@router.post("/plots/{plot_id}/seasons", response_model=CropSeasonResponse, status_code=status.HTTP_201_CREATED)
def create_crop_season(
    plot_id: str,
    data: CropSeasonCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiates a new cultivation cycle (Kharif, Rabi, Summer) on a plot.
    """
    # Ensure plot_id matches data
    data.plot_id = plot_id
    return FarmService.create_season(data=data, current_user=current_user, db=db)


@router.get("/plots/{plot_id}/seasons", response_model=List[CropSeasonResponse])
def list_crop_seasons(
    plot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists historical and active crop cycles on a cultivation plot.
    """
    return FarmService.list_seasons(plot_id=plot_id, current_user=current_user, db=db)


@router.post("/seasons/{season_id}/stage-events", response_model=CropStageEventResponse, status_code=status.HTTP_201_CREATED)
def record_stage_event(
    season_id: str,
    data: CropStageEventCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Records a phenological milestone transition (e.g., VEGETATIVE, FLOWERING, BOLL_FORMATION).
    """
    return FarmService.add_stage_event(
        season_id=season_id,
        data=data,
        current_user=current_user,
        db=db
    )
