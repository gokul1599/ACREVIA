"""
ACREVIA - Post-Harvest Quality & Storage Models.
Manages produce quality assays, moisture provenance, storage facilities, and storage lot assignments.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Numeric, Date, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base


class ProduceQualityProfile(Base):
    __tablename__ = "produce_quality_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    crop_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # cotton, rice, chilli
    standard_name: Mapped[str] = mapped_column(String(100), default="AGMARK_TELANGANA", nullable=False)
    grade_definitions_json: Mapped[str] = mapped_column(Text, nullable=False)


class QualityMeasurement(Base):
    __tablename__ = "quality_measurements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("harvest_sessions.id", ondelete="SET NULL"), index=True, nullable=True)
    lot_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("produce_lots.id", ondelete="CASCADE"), index=True, nullable=True)

    parameter_name: Mapped[str] = mapped_column(String(50), nullable=False)  # MOISTURE_PCT, STAPLE_LENGTH_MM, MICRONAIRE, ASTA_COLOR, FOREIGN_MATTER_PCT, BROKEN_GRAIN_PCT
    measured_value: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)  # %, mm, ASTA, SHU
    measurement_method: Mapped[str] = mapped_column(String(50), default="MEASURED_DIGITAL_SENSOR", nullable=False)  # MEASURED_DIGITAL_SENSOR, VERIFIED_LAB_ASSAY, FARMER_VISUAL_ESTIMATE
    instrument_details: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_quality_lot_param", "lot_id", "parameter_name"),
    )


class StorageLocation(Base):
    __tablename__ = "storage_locations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_type: Mapped[str] = mapped_column(String(50), nullable=False)  # ON_FARM_SHED, HERMETIC_BAGS, COMMERCIAL_COLD_STORAGE, CWC_TSWC_WAREHOUSE
    capacity_quintals: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    is_temperature_controlled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    storage_lots: Mapped[List["StorageLot"]] = relationship("StorageLot", back_populates="location", cascade="all, delete-orphan")


class StorageLot(Base):
    __tablename__ = "storage_lots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lot_id: Mapped[str] = mapped_column(String(36), ForeignKey("produce_lots.id", ondelete="CASCADE"), index=True, nullable=False)
    storage_location_id: Mapped[str] = mapped_column(String(36), ForeignKey("storage_locations.id", ondelete="CASCADE"), index=True, nullable=False)

    quantity_stored: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="QUINTAL", nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    exit_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    current_status: Mapped[str] = mapped_column(String(30), default="STORED", nullable=False)  # STORED, DISPATCHED, LOSS_DISCARDED

    # Relationships
    location: Mapped["StorageLocation"] = relationship("StorageLocation", back_populates="storage_lots")
