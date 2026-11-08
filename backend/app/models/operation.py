"""
ACREVIA - Agricultural Operations, Weather & Risk Models.
"""

import uuid
from datetime import date, datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class FarmOperation(Base, TimestampMixin):
    __tablename__ = "farm_operations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # SOWING, IRRIGATION, FERTILIZATION, SPRAYING, WEEDING, HARVEST
    execution_date: Mapped[date] = mapped_column(Date, nullable=False)
    details_json: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)


class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, nullable=False)
    precipitation: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    wind_speed: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="Open-Meteo", nullable=False)


class RiskAssessment(Base, TimestampMixin):
    __tablename__ = "risk_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    crop_season_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="SET NULL"), nullable=True)
    assessment_date: Mapped[date] = mapped_column(Date, nullable=False)
    pest_risk_level: Mapped[str] = mapped_column(String(20), default="LOW", nullable=False)  # LOW, MODERATE, HIGH, CRITICAL
    weather_risk_level: Mapped[str] = mapped_column(String(20), default="LOW", nullable=False)
    advisory: Mapped[str] = mapped_column(String(1000), nullable=False)
