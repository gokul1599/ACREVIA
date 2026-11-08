"""
ACREVIA - Agricultural Market Intelligence Pydantic Schemas.
Pillar B: Mandi locations, normalized observations, and comparative net realization.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class MarketLocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    market_code: str
    market_name: str
    district: str
    state: str
    latitude: Decimal
    longitude: Decimal
    is_active: bool


class MarketCommodityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    commodity_name: str
    canonical_crop_id: str
    variety_name: Optional[str] = None
    grade: Optional[str] = None


class MarketPriceObservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    market_id: str
    commodity_id: str
    min_price: Decimal
    max_price: Decimal
    modal_price: Decimal
    price_unit: str
    arrival_quantity_quintals: Decimal
    observation_date: date
    source_provider: str
    retrieved_at: datetime
    market: Optional[MarketLocationResponse] = None
    commodity: Optional[MarketCommodityResponse] = None


class MarketComparisonItem(BaseModel):
    market_id: str
    market_name: str
    district: str
    distance_km: float
    modal_price_per_quintal: Decimal
    min_price_per_quintal: Decimal
    max_price_per_quintal: Decimal
    gross_value: Decimal
    estimated_transport_cost: Decimal
    estimated_mandi_cess: Decimal
    estimated_handling_charges: Decimal
    estimated_net_realization: Decimal
    effective_rate_per_quintal: Decimal
    observation_date: date
    disclaimer: str = "Actual market realizations depend on on-site lot inspection, moisture testing, and buyer bidding."


class MarketCompareResponse(BaseModel):
    canonical_crop_id: str
    quantity_quintals: Decimal
    plot_id: Optional[str] = None
    comparisons: List[MarketComparisonItem]
