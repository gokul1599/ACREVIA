"""
ACREVIA - Satellite Intelligence REST API (Pillar B: Acrevia Earth).
Provides optical vegetation indices (NDVI, EVI, NDMI), vigor trend trajectories,
and strictly enforces non-diagnostic evidence disclaimers.
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.satellite import SATELLITE_EVIDENCE_DISCLAIMER
from backend.app.schemas.satellite import (
    SatelliteTimeSeriesResponse,
    SatelliteLatestResponse,
    SatelliteObservationItem
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.satellite_service import SatelliteService

router = APIRouter(prefix="/satellite", tags=["Acrevia Earth"])


class SatelliteObservationCreate(BaseModel):
    observation_date: datetime
    mean_ndvi: float = Field(..., ge=-1.0, le=1.0)
    min_ndvi: float = Field(..., ge=-1.0, le=1.0)
    max_ndvi: float = Field(..., ge=-1.0, le=1.0)
    std_ndvi: float = Field(0.02, ge=0.0)
    mean_evi: Optional[float] = None
    mean_ndmi: Optional[float] = None
    cloud_masked_pixel_ratio: float = Field(0.0, ge=0.0, le=1.0)


@router.get("/plots/{plot_id}/time-series", response_model=SatelliteTimeSeriesResponse)
def get_plot_time_series(
    plot_id: str,
    days: int = Query(60, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves satellite observation history and 30-day vigor trajectory.
    Always includes mandatory non-disease disclaimer.
    """
    data = SatelliteService.get_time_series(db=db, plot_id=plot_id, days=days)
    return SatelliteTimeSeriesResponse(
        plot_id=data["plot_id"],
        trend_summary=data["trend_summary"],
        observations_count=data["observations_count"],
        evidence_disclaimer=data["evidence_disclaimer"],
        time_series=[SatelliteObservationItem.model_validate(o) for o in data["time_series"]]
    )


@router.get("/plots/{plot_id}/latest", response_model=SatelliteLatestResponse)
def get_latest_observation(
    plot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves the most recent clear-sky satellite observation for a plot."""
    obs = SatelliteService.get_latest_observation(db=db, plot_id=plot_id)
    return SatelliteLatestResponse(
        plot_id=plot_id,
        observation=SatelliteObservationItem.model_validate(obs) if obs else None,
        evidence_disclaimer=SATELLITE_EVIDENCE_DISCLAIMER
    )


@router.post("/plots/{plot_id}/observations", response_model=SatelliteObservationItem, status_code=status.HTTP_201_CREATED)
def record_satellite_observation(
    plot_id: str,
    payload: SatelliteObservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ingests or mocks a satellite observation for a plot."""
    obs = SatelliteService.record_observation(
        db=db,
        plot_id=plot_id,
        observation_date=payload.observation_date,
        mean_ndvi=payload.mean_ndvi,
        min_ndvi=payload.min_ndvi,
        max_ndvi=payload.max_ndvi,
        std_ndvi=payload.std_ndvi,
        mean_evi=payload.mean_evi,
        mean_ndmi=payload.mean_ndmi,
        cloud_masked_pixel_ratio=payload.cloud_masked_pixel_ratio
    )
    return SatelliteObservationItem.model_validate(obs)
