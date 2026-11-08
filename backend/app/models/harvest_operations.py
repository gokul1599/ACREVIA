"""
ACREVIA - Harvest Planning & Operations Models.
Supports multi-picking management, loss accounting, and harvest session recording.
"""

from datetime import date
from decimal import Decimal
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Numeric, Date, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class HarvestPlan(Base, TimestampMixin):
    __tablename__ = "harvest_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    crop_season_id: Mapped[str] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="CASCADE"), index=True, nullable=False)

    planned_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    planned_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    estimated_quantity_quintals: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    harvest_method: Mapped[str] = mapped_column(String(50), default="MANUAL", nullable=False)  # MANUAL, MECHANICAL, COMBINED
    status: Mapped[str] = mapped_column(String(30), default="PLANNED", nullable=False)  # PLANNED, IN_PROGRESS, COMPLETED, CANCELLED

    # Relationships
    sessions: Mapped[List["HarvestSession"]] = relationship("HarvestSession", back_populates="plan", cascade="all, delete-orphan")


class HarvestSession(Base, TimestampMixin):
    __tablename__ = "harvest_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    crop_season_id: Mapped[str] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="CASCADE"), index=True, nullable=False)
    harvest_plan_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("harvest_plans.id", ondelete="SET NULL"), index=True, nullable=True)

    picking_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1st picking, 2nd picking, etc.
    harvest_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    harvested_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="QUINTAL", nullable=False)
    quantity_type: Mapped[str] = mapped_column(String(30), default="MEASURED", nullable=False)  # MEASURED, ESTIMATED_QUANTITY
    loss_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recorded_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Relationships
    plan: Mapped[Optional["HarvestPlan"]] = relationship("HarvestPlan", back_populates="sessions")

    __table_args__ = (
        Index("ix_harvest_session_season_picking", "crop_season_id", "picking_number"),
    )
