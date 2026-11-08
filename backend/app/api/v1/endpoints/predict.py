"""
ACREVIA - Predictive Agriculture & Yield Feasibility REST API (Pillar E: Acrevia Predict).
Manages ground-truth harvest measurements and enforces strict governed withholding
policies when sample sizes are below statistical confidence thresholds.
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.yield_prediction import (
    HarvestMeasurementCreate,
    HarvestMeasurementResponse,
    YieldForecastResponse
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.predict_service import PredictService

router = APIRouter(prefix="/predict", tags=["Acrevia Predict"])


@router.post("/plots/{plot_id}/harvests", response_model=HarvestMeasurementResponse, status_code=status.HTTP_201_CREATED)
def record_harvest_measurement(
    plot_id: str,
    payload: HarvestMeasurementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Records ground-truth harvest measurement with provenance classification."""
    harvest = PredictService.record_harvest(
        db=db,
        plot_id=plot_id,
        season_id=payload.season_id,
        harvest_date=payload.harvest_date,
        yield_quintals_per_acre=payload.yield_quintals_per_acre,
        total_harvest_kg=payload.total_harvest_kg,
        provenance_tier=payload.provenance_tier,
        verification_document_url=payload.verification_document_url,
        notes=payload.notes
    )
    return harvest


@router.get("/plots/{plot_id}/forecast", response_model=YieldForecastResponse)
def get_yield_forecast_feasibility(
    plot_id: str,
    threshold: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Evaluates yield forecasting feasibility for a plot.
    If historical verified harvest records fall below threshold,
    forecast is strictly withheld with a transparent scientific explanation.
    """
    result = PredictService.evaluate_yield_forecast_feasibility(
        db=db,
        plot_id=plot_id,
        threshold=threshold
    )
    return YieldForecastResponse(**result)
