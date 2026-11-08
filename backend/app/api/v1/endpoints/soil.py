"""
ACREVIA - Soil Health Intelligence API Endpoints (Pillar A).
Manages soil profiles, sampling events, accredited laboratory results, and longitudinal plot history.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.soil_health import (
    SoilProfileCreate,
    SoilProfileResponse,
    SoilSampleCreate,
    SoilSampleResponse,
    SoilTestResultCreate,
    SoilTestResultResponse,
    SoilPlotHistoryResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.soil_service import SoilService

router = APIRouter(prefix="/soil", tags=["ACREVIA Soil Health"])


@router.post("/profiles", response_model=SoilProfileResponse, status_code=status.HTTP_201_CREATED)
def create_soil_profile(
    data: SoilProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SoilService.create_profile(db=db, data=data)


@router.post("/samples", response_model=SoilSampleResponse, status_code=status.HTTP_201_CREATED)
def create_soil_sample(
    data: SoilSampleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SoilService.create_sample(db=db, user_id=current_user.id, data=data)


@router.post("/lab-results", response_model=SoilTestResultResponse, status_code=status.HTTP_201_CREATED)
def ingest_lab_result(
    data: SoilTestResultCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SoilService.ingest_lab_result(db=db, data=data)


@router.get("/plot/{plot_id}/history", response_model=SoilPlotHistoryResponse, status_code=status.HTTP_200_OK)
def get_plot_soil_history(
    plot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SoilService.get_plot_history(db=db, plot_id=plot_id)
