"""
ACREVIA - Agricultural Market Intelligence API Endpoints.
Pillar B: Multi-mandi prices, commodity normalization, and distance-adjusted comparative net realization.
"""

from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.market_intelligence import (
    MarketPriceObservationResponse,
    MarketCompareResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.market_service import MarketService

router = APIRouter(prefix="/market", tags=["Market Intelligence"])


@router.get("/prices", response_model=List[MarketPriceObservationResponse], status_code=status.HTTP_200_OK)
def get_prices(
    crop_id: Optional[str] = Query(None, description="Canonical crop ID (cotton, rice, chilli)"),
    district: Optional[str] = Query(None, description="District filter (Warangal, Khammam, Suryapet, etc.)"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Publicly queryable endpoint providing latest verified mandi price observations.
    """
    return MarketService.get_market_prices(db, canonical_crop_id=crop_id, district=district, limit=limit)


@router.get("/compare", response_model=MarketCompareResponse, status_code=status.HTTP_200_OK)
def compare_market_realizations(
    crop_id: str = Query(..., description="Canonical crop ID (cotton, rice, chilli)"),
    quantity_quintals: Decimal = Query(..., gt=0, description="Quantity for sale in quintals"),
    plot_id: Optional[str] = Query(None, description="Plot ID for origin distance calculations"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Calculates estimated net realization across candidate mandis after deducting transport, cess, and handling fees.
    """
    return MarketService.compare_market_realizations(
        db,
        canonical_crop_id=crop_id,
        quantity_quintals=quantity_quintals,
        plot_id=plot_id,
    )
