"""
ACREVIA - Crop, Variety & Season Models.
"""

import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy import String, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class Crop(Base):
    __tablename__ = "crops"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # cotton, rice, chilli
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_te: Mapped[str] = mapped_column(String(100), nullable=False)
    name_hi: Mapped[str] = mapped_column(String(100), nullable=False)
    scientific_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    varieties: Mapped[List["CropVariety"]] = relationship("CropVariety", back_populates="crop", cascade="all, delete-orphan")
    seasons: Mapped[List["CropSeason"]] = relationship("CropSeason", back_populates="crop")


class CropVariety(Base):
    __tablename__ = "crop_varieties"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    crop_id: Mapped[str] = mapped_column(String(50), ForeignKey("crops.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, default=150, nullable=False)
    resistance_traits: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    crop: Mapped["Crop"] = relationship("Crop", back_populates="varieties")
    seasons: Mapped[List["CropSeason"]] = relationship("CropSeason", back_populates="variety")


class CropSeason(Base, TimestampMixin):
    __tablename__ = "crop_seasons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    crop_id: Mapped[str] = mapped_column(String(50), ForeignKey("crops.id", ondelete="RESTRICT"), index=True, nullable=False)
    variety_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("crop_varieties.id", ondelete="SET NULL"), nullable=True)
    season_type: Mapped[str] = mapped_column(String(20), default="KHARIF", nullable=False)  # KHARIF, RABI, SUMMER
    sowing_date: Mapped[date] = mapped_column(Date, nullable=False)
    current_stage: Mapped[str] = mapped_column(String(50), default="VEGETATIVE", nullable=False)  # SOWING, VEGETATIVE, FLOWERING, BOLL_FORMATION, MATURITY
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, HARVESTED, ABANDONED

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot", back_populates="seasons")
    crop: Mapped["Crop"] = relationship("Crop", back_populates="seasons")
    variety: Mapped[Optional["CropVariety"]] = relationship("CropVariety", back_populates="seasons")
    stage_events: Mapped[List["CropStageEvent"]] = relationship("CropStageEvent", back_populates="season", cascade="all, delete-orphan")
    observations: Mapped[List["Observation"]] = relationship("Observation", back_populates="season", cascade="all, delete-orphan")


class CropStageEvent(Base):
    __tablename__ = "crop_stage_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    crop_season_id: Mapped[str] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="CASCADE"), index=True, nullable=False)
    stage_name: Mapped[str] = mapped_column(String(50), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    season: Mapped["CropSeason"] = relationship("CropSeason", back_populates="stage_events")
