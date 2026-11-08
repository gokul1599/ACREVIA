"""
ACREVIA - Agricultural Market Intelligence Models.
Covers mandi locations, commodity standardizations, and daily price observations.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
import uuid
from typing import List, Optional
from sqlalchemy import String, Numeric, Date, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base


class MarketLocation(Base):
    __tablename__ = "market_locations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    market_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    market_name: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)  # Warangal, Khammam, Suryapet, Karimnagar, etc.
    state: Mapped[str] = mapped_column(String(100), default="Telangana", nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    observations: Mapped[List["MarketPriceObservation"]] = relationship("MarketPriceObservation", back_populates="market", cascade="all, delete-orphan")


class MarketCommodity(Base):
    __tablename__ = "market_commodities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    commodity_name: Mapped[str] = mapped_column(String(100), nullable=False)
    canonical_crop_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # cotton, rice, chilli
    variety_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    observations: Mapped[List["MarketPriceObservation"]] = relationship("MarketPriceObservation", back_populates="commodity", cascade="all, delete-orphan")


class MarketPriceObservation(Base):
    __tablename__ = "market_price_observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    market_id: Mapped[str] = mapped_column(String(36), ForeignKey("market_locations.id", ondelete="CASCADE"), index=True, nullable=False)
    commodity_id: Mapped[str] = mapped_column(String(36), ForeignKey("market_commodities.id", ondelete="CASCADE"), index=True, nullable=False)

    min_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    max_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    modal_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    price_unit: Mapped[str] = mapped_column(String(30), default="INR_PER_QUINTAL", nullable=False)
    arrival_quantity_quintals: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    observation_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    source_provider: Mapped[str] = mapped_column(String(50), default="AGMARKNET", nullable=False)  # AGMARKNET, ENAM, TS_MARKETING
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    market: Mapped["MarketLocation"] = relationship("MarketLocation", back_populates="observations")
    commodity: Mapped["MarketCommodity"] = relationship("MarketCommodity", back_populates="observations")

    __table_args__ = (
        Index("ix_market_obs_comm_date", "commodity_id", "observation_date"),
        Index("ix_market_obs_market_date", "market_id", "observation_date"),
    )
