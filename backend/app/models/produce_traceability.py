"""
ACREVIA - Produce Traceability Models.
Provides immutable lot registration, unique QR tokens, and quantity-conserving lot movements.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Numeric, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class ProduceLot(Base, TimestampMixin):
    __tablename__ = "produce_lots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lot_code: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    qr_token: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    crop_season_id: Mapped[str] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="CASCADE"), index=True, nullable=False)
    harvest_session_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("harvest_sessions.id", ondelete="SET NULL"), index=True, nullable=True)

    crop_id: Mapped[str] = mapped_column(String(50), nullable=False)  # cotton, rice, chilli
    variety_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    harvest_date: Mapped[date] = mapped_column(Date, nullable=False)
    initial_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    remaining_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="QUINTAL", nullable=False)
    current_status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)  # ACTIVE, STORED, PARTIALLY_SOLD, COMPLETELY_SOLD, EXPIRED

    # Relationships
    movements: Mapped[List["LotMovement"]] = relationship("LotMovement", back_populates="lot", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_produce_lots_farm_crop", "farm_id", "crop_id"),
    )


class LotMovement(Base):
    __tablename__ = "lot_movements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lot_id: Mapped[str] = mapped_column(String(36), ForeignKey("produce_lots.id", ondelete="CASCADE"), index=True, nullable=False)

    movement_type: Mapped[str] = mapped_column(String(30), nullable=False)  # HARVEST_IN, STORAGE_ENTRY, TRANSFER, SALE, SPLIT, DISCARD
    source_location: Mapped[str] = mapped_column(String(100), nullable=False)
    destination_location: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity_transferred: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="QUINTAL", nullable=False)
    actor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    movement_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    lot: Mapped["ProduceLot"] = relationship("ProduceLot", back_populates="movements")

    __table_args__ = (
        Index("ix_lot_movements_lot_time", "lot_id", "movement_timestamp"),
    )
