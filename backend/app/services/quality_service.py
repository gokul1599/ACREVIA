"""
ACREVIA - Post-Harvest Quality & Storage Service.
Pillar D: Moisture provenance, quality assay validation, and storage lot allocation.
"""

from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.farm import Farm
from backend.app.models.produce_traceability import ProduceLot, LotMovement
from backend.app.models.post_harvest import (
    ProduceQualityProfile,
    QualityMeasurement,
    StorageLocation,
    StorageLot,
)
from backend.app.schemas.post_harvest import (
    QualityMeasurementCreate,
    StorageLocationCreate,
    StorageLotCreate,
)


class QualityService:
    @staticmethod
    def record_quality_measurement(db: Session, data: QualityMeasurementCreate) -> QualityMeasurement:
        if not data.lot_id and not data.session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either lot_id or session_id must be provided for quality measurement.",
            )

        if data.lot_id:
            lot = db.get(ProduceLot, data.lot_id)
            if not lot:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ProduceLot '{data.lot_id}' not found.",
                )

        if data.measured_value < Decimal("0.00"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quality measurement value cannot be negative.",
            )

        # Moisture percentage bound check
        if data.parameter_name.upper() == "MOISTURE_PCT" and data.measured_value > Decimal("100.00"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Moisture percentage cannot exceed 100%.",
            )

        measurement = QualityMeasurement(
            session_id=data.session_id,
            lot_id=data.lot_id,
            parameter_name=data.parameter_name.upper(),
            measured_value=data.measured_value,
            unit=data.unit,
            measurement_method=data.measurement_method.upper(),
            instrument_details=data.instrument_details,
        )
        db.add(measurement)
        db.commit()
        db.refresh(measurement)
        return measurement

    @staticmethod
    def get_measurements_for_lot(db: Session, lot_id: str) -> List[QualityMeasurement]:
        query = select(QualityMeasurement).where(QualityMeasurement.lot_id == lot_id).order_by(QualityMeasurement.measured_at.asc())
        return list(db.scalars(query).all())

    @staticmethod
    def create_storage_location(db: Session, data: StorageLocationCreate) -> StorageLocation:
        farm = db.get(Farm, data.farm_id)
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm '{data.farm_id}' not found.",
            )

        if data.capacity_quintals <= Decimal("0.00"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Storage capacity must be greater than zero.",
            )

        location = StorageLocation(
            farm_id=data.farm_id,
            name=data.name,
            storage_type=data.storage_type.upper(),
            capacity_quintals=data.capacity_quintals,
            district=data.district,
            is_temperature_controlled=data.is_temperature_controlled,
        )
        db.add(location)
        db.commit()
        db.refresh(location)
        return location

    @staticmethod
    def assign_to_storage(db: Session, data: StorageLotCreate) -> StorageLot:
        lot = db.get(ProduceLot, data.lot_id)
        if not lot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ProduceLot '{data.lot_id}' not found.",
            )

        storage_loc = db.get(StorageLocation, data.storage_location_id)
        if not storage_loc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"StorageLocation '{data.storage_location_id}' not found.",
            )

        if data.quantity_stored <= Decimal("0.00"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stored quantity must be greater than zero.",
            )

        if data.quantity_stored > lot.remaining_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot store {data.quantity_stored} quintals. Only {lot.remaining_quantity} quintals remain in lot.",
            )

        storage_lot = StorageLot(
            lot_id=data.lot_id,
            storage_location_id=data.storage_location_id,
            quantity_stored=data.quantity_stored,
            unit=data.unit.upper(),
            entry_date=data.entry_date,
            current_status="STORED",
        )
        db.add(storage_lot)

        # Log lot movement
        movement = LotMovement(
            lot_id=lot.id,
            movement_type="STORAGE_ENTRY",
            source_location="Farm Yard / Aggregation Area",
            destination_location=f"{storage_loc.name} ({storage_loc.storage_type})",
            quantity_transferred=data.quantity_stored,
            unit=data.unit.upper(),
            actor_name="ACREVIA Storage Logistics",
            notes=f"Produce stored under condition: {'Temperature Controlled' if storage_loc.is_temperature_controlled else 'Ambient Storage'}",
        )
        db.add(movement)

        lot.current_status = "STORED"
        db.commit()
        db.refresh(storage_lot)
        return storage_lot
