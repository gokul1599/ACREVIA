"""
ACREVIA - Crop Season Economics Pydantic Schemas.
Pillar F: Cost of cultivation, gross revenue, net margins, and data completeness scoring.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class ExpenseCategoryBreakdown(BaseModel):
    category: str
    total_amount: Decimal
    percentage_of_total: Decimal


class CropSeasonEconomicsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    crop_season_id: str
    total_expenses: Decimal
    gross_revenue: Decimal
    net_realization: Decimal
    total_harvest_quantity: Decimal
    total_sold_quantity: Decimal
    unit: str
    cost_per_unit: Decimal
    net_margin_per_unit: Decimal
    data_completeness_pct: Decimal
    calculated_at: datetime


class EconomicsSummaryResponse(BaseModel):
    crop_season_id: str
    crop_name: str
    total_expenses: Decimal
    gross_revenue: Decimal
    net_realization: Decimal
    total_harvest_quantity: Decimal
    total_sold_quantity: Decimal
    unit: str
    cost_per_unit: Decimal
    net_margin_per_unit: Decimal
    data_completeness_pct: Decimal
    completeness_badge: str  # COMPLETE, PARTIAL_DATA, MINIMAL_DATA
    category_breakdown: List[ExpenseCategoryBreakdown]
    missing_categories: List[str]
    economic_disclaimers: List[str]
