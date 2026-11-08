"""
ACREVIA - Harvest Planning & Operations Service.
Pillar C: Harvest plans, multi-picking management, loss tracking, and produce lot minting.
"""

from datetime import datetime, timezone
from decimal import Decimal
import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.farm import Plot
from backend.app.models.crop import CropSeason
from backend.app.models.harvest_operations import HarvestPlan, HarvestSession
from backend.app.models.produce_traceability import ProduceLot, LotMovement
from backend.app.schemas.harvest_operations import (
    HarvestPlanCreate,
    HarvestSessionCreate,
    HarvestSessionResponse,
)


class HarvestService:
    @staticmethod
    def create_harvest_plan(db: Session, data: HarvestPlanCreate) -> HarvestPlan:
        plot = db.get(Plot, data.plot_id)
        if not plot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot '{data.plot_id}' not found.",
            )

        season = db.get(CropSeason, data.crop_season_id)
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CropSeason '{data.crop_season_id}' not found.",
            )

        if data.planned_end_date < data.planned_start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Planned end date cannot be earlier than planned start date.",
            )

        if data.estimated_quantity_quintals <= Decimal("0.00"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estimated quantity must be greater than zero quintals.",
            )

        plan = HarvestPlan(
            plot_id=data.plot_id,
            crop_season_id=data.crop_season_id,
            planned_start_date=data.planned_start_date,
            planned_end_date=data.planned_end_date,
            estimated_quantity_quintals=data.estimated_quantity_quintals,
            harvest_method=data.harvest_method.upper(),
            status="PLANNED",
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan

    @staticmethod
    def create_harvest_session(db: Session, data: HarvestSessionCreate) -> HarvestSessionResponse:
        plot = db.get(Plot, data.plot_id)
        if not plot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot '{data.plot_id}' not found.",
            )

        season = db.get(CropSeason, data.crop_season_id)
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CropSeason '{data.crop_season_id}' not found.",
            )

        if data.harvested_quantity <= Decimal("0.00"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Harvested quantity must be strictly greater than zero.",
            )

        if data.loss_quantity < Decimal("0.00"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Loss quantity cannot be negative.",
            )

        session = HarvestSession(
            plot_id=data.plot_id,
            crop_season_id=data.crop_season_id,
            harvest_plan_id=data.harvest_plan_id,
            picking_number=data.picking_number,
            harvest_date=data.harvest_date,
            harvested_quantity=data.harvested_quantity,
            unit=data.unit.upper(),
            quantity_type=data.quantity_type.upper(),
            loss_quantity=data.loss_quantity,
            notes=data.notes,
            recorded_by_user_id=data.recorded_by_user_id,
        )
        db.add(session)
        db.flush()  # Obtain session.id

        # Mint linked ProduceLot
        crop_name = season.crop.name_en if season.crop else season.crop_id
        crop_code = season.crop_id.upper()[:3] if season.crop_id else "CRP"
        unique_suffix = uuid.uuid4().hex[:6].upper()
        lot_code = f"ACR-{crop_code}-{data.harvest_date.strftime('%Y%m%d')}-{unique_suffix}"
        qr_token = str(uuid.uuid4())

        produce_lot = ProduceLot(
            lot_code=lot_code,
            qr_token=qr_token,
            farm_id=plot.farm_id,
            plot_id=plot.id,
            crop_season_id=season.id,
            harvest_session_id=session.id,
            crop_id=season.crop_id,
            variety_name=season.variety.name if season.variety else None,
            harvest_date=data.harvest_date,
            initial_quantity=data.harvested_quantity,
            remaining_quantity=data.harvested_quantity,
            unit=data.unit.upper(),
            current_status="ACTIVE",
        )
        db.add(produce_lot)
        db.flush()

        # Record initial LotMovement (HARVEST_IN)
        movement = LotMovement(
            lot_id=produce_lot.id,
            movement_type="HARVEST_IN",
            source_location=f"Plot {plot.name} ({plot.id[:8]})",
            destination_location="Farm Yard / Aggregation Area",
            quantity_transferred=data.harvested_quantity,
            unit=data.unit.upper(),
            actor_name="ACREVIA Harvest Engine",
            notes=f"Harvest session #{data.picking_number} recorded",
        )
        db.add(movement)
        db.commit()
        db.refresh(session)

        return HarvestSessionResponse(
            id=session.id,
            plot_id=session.plot_id,
            crop_season_id=session.crop_season_id,
            harvest_plan_id=session.harvest_plan_id,
            picking_number=session.picking_number,
            harvest_date=session.harvest_date,
            harvested_quantity=session.harvested_quantity,
            unit=session.unit,
            quantity_type=session.quantity_type,
            loss_quantity=session.loss_quantity,
            notes=session.notes,
            recorded_by_user_id=session.recorded_by_user_id,
            created_at=session.created_at,
            produce_lot_id=produce_lot.id,
            lot_code=produce_lot.lot_code,
        )

    @staticmethod
    def get_harvest_sessions(db: Session, crop_season_id: str) -> List[HarvestSession]:
        query = select(HarvestSession).where(HarvestSession.crop_season_id == crop_season_id).order_by(HarvestSession.picking_number.asc())
        return list(db.scalars(query).all())

    @staticmethod
    def get_harvest_plans(db: Session, crop_season_id: str) -> List[HarvestPlan]:
        query = select(HarvestPlan).where(HarvestPlan.crop_season_id == crop_season_id).order_by(HarvestPlan.planned_start_date.asc())
        return list(db.scalars(query).all())
