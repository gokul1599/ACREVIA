"""
ACREVIA - Harvest Planning & Operations Pydantic Schemas.
Pillar C: Harvest plans, picking session tracking, and loss records.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class HarvestPlanCreate(BaseModel):
    plot_id: str
    crop_season_id: str
    planned_start_date: date
    planned_end_date: date
    estimated_quantity_quintals: Decimal
    harvest_method: str = "MANUAL"  # MANUAL, MECHANICAL, COMBINED


class HarvestPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    plot_id: str
    crop_season_id: str
    planned_start_date: date
    planned_end_date: date
    estimated_quantity_quintals: Decimal
    harvest_method: str
    status: str
    created_at: datetime


class HarvestSessionCreate(BaseModel):
    plot_id: str
    crop_season_id: str
    harvest_plan_id: Optional[str] = None
    picking_number: int = 1
    harvest_date: date
    harvested_quantity: Decimal
    unit: str = "QUINTAL"  # QUINTAL, KG, BAGS
    quantity_type: str = "MEASURED"  # MEASURED, ESTIMATED_QUANTITY
    loss_quantity: Decimal = Decimal("0.00")
    notes: Optional[str] = None
    recorded_by_user_id: Optional[str] = None


class HarvestSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    plot_id: str
    crop_season_id: str
    harvest_plan_id: Optional[str] = None
    picking_number: int
    harvest_date: date
    harvested_quantity: Decimal
    unit: str
    quantity_type: str
    loss_quantity: Decimal
    notes: Optional[str] = None
    recorded_by_user_id: Optional[str] = None
    created_at: datetime
    # Attached produce lot information minted from this session
    produce_lot_id: Optional[str] = None
    lot_code: Optional[str] = None
