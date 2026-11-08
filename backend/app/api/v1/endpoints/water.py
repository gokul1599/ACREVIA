"""
ACREVIA - Precision Water Management API Endpoints (Pillar B).
Manages farm water sources, metered irrigation events, soil moisture observations, water balances, and scenario comparisons.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.water_management import (
    WaterSourceCreate,
    WaterSourceResponse,
    IrrigationEventCreate,
    IrrigationEventResponse,
    SoilMoistureObservationCreate,
    SoilMoistureObservationResponse,
    WaterBalanceSnapshotResponse,
    WaterScenarioComparisonRequest,
    WaterScenarioComparisonResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.water_service import WaterService

router = APIRouter(prefix="/water", tags=["ACREVIA Precision Water"])


@router.post("/sources", response_model=WaterSourceResponse, status_code=status.HTTP_201_CREATED)
def create_water_source(
    data: WaterSourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return WaterService.create_water_source(db=db, data=data)


@router.get("/sources", response_model=List[WaterSourceResponse], status_code=status.HTTP_200_OK)
def list_water_sources(
    farm_id: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return WaterService.get_water_sources(db=db, farm_id=farm_id)


@router.post("/irrigation-events", response_model=IrrigationEventResponse, status_code=status.HTTP_201_CREATED)
def record_irrigation_event(
    data: IrrigationEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return WaterService.record_irrigation_event(db=db, data=data)


@router.post("/telemetry", response_model=SoilMoistureObservationResponse, status_code=status.HTTP_201_CREATED)
def record_soil_moisture_telemetry(
    data: SoilMoistureObservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return WaterService.record_soil_moisture(db=db, data=data)


@router.get("/plot/{plot_id}/balance", response_model=WaterBalanceSnapshotResponse, status_code=status.HTTP_200_OK)
def get_plot_water_balance(
    plot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return WaterService.get_plot_water_balance(db=db, plot_id=plot_id)


@router.post("/scenarios/compare", response_model=WaterScenarioComparisonResponse, status_code=status.HTTP_200_OK)
def compare_irrigation_scenarios(
    request: WaterScenarioComparisonRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return WaterService.compare_irrigation_scenarios(db=db, request=request)
