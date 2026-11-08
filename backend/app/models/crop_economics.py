"""
ACREVIA - Crop Season Economics Models.
Summarizes cultivation costs, gross revenues, unit costs, and net margins per crop season.
"""

from datetime import datetime, timezone
from decimal import Decimal
import uuid
from sqlalchemy import String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import Base


class CropSeasonEconomics(Base):
    __tablename__ = "crop_season_economics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    crop_season_id: Mapped[str] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)

    total_expenses: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    gross_revenue: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    net_realization: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    total_harvest_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_sold_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="QUINTAL", nullable=False)

    cost_per_unit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    net_margin_per_unit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    data_completeness_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
