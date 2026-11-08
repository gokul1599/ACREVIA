"""
ACREVIA - Produce Traceability Service.
Pillar E: Quantity-conserving lot movements, audit histories, and privacy-preserving public QR verification.
"""

from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.farm import Farm
from backend.app.models.crop import Crop
from backend.app.models.produce_traceability import ProduceLot, LotMovement
from backend.app.models.post_harvest import QualityMeasurement
from backend.app.schemas.produce_traceability import (
    LotMovementCreate,
    ProduceLotResponse,
    ProduceLotDetailResponse,
    ProduceLotPublicResponse,
    QualitySummaryItem,
)


class TraceabilityService:
    @staticmethod
    def get_produce_lot(db: Session, lot_id: str) -> ProduceLot:
        lot = db.get(ProduceLot, lot_id)
        if not lot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ProduceLot '{lot_id}' not found.",
            )
        return lot

    @staticmethod
    def record_lot_movement(db: Session, lot_id: str, data: LotMovementCreate) -> LotMovement:
        lot = db.get(ProduceLot, lot_id)
        if not lot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ProduceLot '{lot_id}' not found.",
            )

        if data.quantity_transferred <= Decimal("0.00"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transferred quantity must be strictly greater than zero.",
            )

        # For movements that reduce remaining quantity (TRANSFER, SALE, SPLIT, DISCARD)
        reducing_movements = {"TRANSFER", "SALE", "SPLIT", "DISCARD"}
        if data.movement_type.upper() in reducing_movements:
            if data.quantity_transferred > lot.remaining_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Cannot transfer {data.quantity_transferred} {lot.unit}. "
                        f"Only {lot.remaining_quantity} {lot.unit} remains in this lot."
                    ),
                )
            lot.remaining_quantity -= data.quantity_transferred
            if lot.remaining_quantity == Decimal("0.00"):
                lot.current_status = "COMPLETELY_SOLD" if data.movement_type.upper() == "SALE" else "DISPATCHED"
            else:
                lot.current_status = "PARTIALLY_SOLD" if data.movement_type.upper() == "SALE" else lot.current_status

        movement = LotMovement(
            lot_id=lot.id,
            movement_type=data.movement_type.upper(),
            source_location=data.source_location,
            destination_location=data.destination_location,
            quantity_transferred=data.quantity_transferred,
            unit=data.unit.upper(),
            actor_name=data.actor_name,
            notes=data.notes,
        )
        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement

    @staticmethod
    def get_public_lot_verification(db: Session, qr_token: str) -> ProduceLotPublicResponse:
        lot = db.scalar(select(ProduceLot).where(ProduceLot.qr_token == qr_token))
        if not lot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid or unverified produce QR token.",
            )

        farm = db.get(Farm, lot.farm_id)
        crop = db.get(Crop, lot.crop_id)

        crop_display = crop.name_en if crop else lot.crop_id.capitalize()
        if crop and crop.name_te:
            crop_display = f"{crop.name_en} ({crop.name_te})"

        measurements = list(db.scalars(select(QualityMeasurement).where(QualityMeasurement.lot_id == lot.id)).all())
        quality_items: List[QualitySummaryItem] = []
        moisture_val: Optional[Decimal] = None

        for m in measurements:
            quality_items.append(
                QualitySummaryItem(
                    parameter_name=m.parameter_name,
                    measured_value=m.measured_value,
                    unit=m.unit,
                    method=m.measurement_method,
                )
            )
            if m.parameter_name == "MOISTURE_PCT":
                moisture_val = m.measured_value

        # Derive overall grade based on verified standards
        overall_grade = "Grade A Standard"
        if moisture_val is not None:
            if lot.crop_id == "rice" and moisture_val <= Decimal("17.00"):
                overall_grade = "Grade A Premium (Optimum Moisture)"
            elif lot.crop_id == "cotton" and moisture_val <= Decimal("9.00"):
                overall_grade = "Grade A Premium Long-Staple"
            elif lot.crop_id == "chilli" and moisture_val <= Decimal("11.00"):
                overall_grade = "Export Grade Teja (Optimum Dryness)"
            elif moisture_val > Decimal("18.00"):
                overall_grade = "Fair Average Quality (High Moisture)"

        return ProduceLotPublicResponse(
            lot_code=lot.lot_code,
            crop_name=crop_display,
            variety=lot.variety_name or "Regional Certified Variety",
            harvest_date=lot.harvest_date,
            district=farm.district if farm else "Telangana Region",
            state=farm.state if farm else "Telangana",
            origin_verification="VERIFIED_ACREVIA_FARM",
            quality_parameters=quality_items,
            overall_grade=overall_grade,
            traceability_status=f"Active Origin Provenance ({lot.current_status})",
            public_notice="Farmer identity and exact plot coordinates are protected under ACREVIA Data Governance.",
        )
