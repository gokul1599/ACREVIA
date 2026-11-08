"""
ACREVIA - Sustainable Agriculture API Endpoints (Pillar E).
Manages practice taxonomies, farm practice records, empirical SOC tracking,
research-grade GHG accounting, and seasonal sustainability scorecards.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.sustainability import (
    AgriculturalPracticeDefinitionResponse,
    FarmPracticeRecordCreate,
    FarmPracticeRecordResponse,
    SoilCarbonMeasurementCreate,
    SoilCarbonMeasurementResponse,
    EnvironmentalAccountingEstimateResponse,
    SeasonalSustainabilityScorecardResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.sustain_service import SustainService

router = APIRouter(prefix="/sustain", tags=["ACREVIA Sustainable Agriculture"])


@router.get("/practices", response_model=List[AgriculturalPracticeDefinitionResponse], status_code=status.HTTP_200_OK)
def list_sustainable_practices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SustainService.get_practices(db=db)


@router.post("/records", response_model=FarmPracticeRecordResponse, status_code=status.HTTP_201_CREATED)
def record_farm_practice(
    data: FarmPracticeRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SustainService.record_practice(db=db, data=data)


@router.post("/carbon-measurement", response_model=SoilCarbonMeasurementResponse, status_code=status.HTTP_201_CREATED)
def record_soil_carbon_measurement(
    data: SoilCarbonMeasurementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SustainService.record_carbon_measurement(db=db, data=data)


@router.get("/plot/{plot_id}/emissions", response_model=EnvironmentalAccountingEstimateResponse, status_code=status.HTTP_200_OK)
def get_plot_emissions_estimate(
    plot_id: str,
    season: str = Query("Kharif"),
    year: int = Query(2026),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SustainService.get_emissions_estimate(db=db, plot_id=plot_id, season=season, year=year)


@router.get("/plot/{plot_id}/scorecard", response_model=SeasonalSustainabilityScorecardResponse, status_code=status.HTTP_200_OK)
def get_plot_sustainability_scorecard(
    plot_id: str,
    season: str = Query("Kharif"),
    year: int = Query(2026),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SustainService.get_scorecard(db=db, plot_id=plot_id, season=season, year=year)
