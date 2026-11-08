"""
ACREVIA - Weather Data Model.
Supports both ground observations and multi-day meteorological forecasts.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base


class WeatherData(Base):
    __tablename__ = "weather_data"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    district: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    is_forecast: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    
    observation_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    forecast_target_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    
    temperature_celsius: Mapped[float] = mapped_column(Float, nullable=False)
    relative_humidity: Mapped[float] = mapped_column(Float, nullable=False)
    precipitation_mm: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    wind_speed_kmh: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    leaf_wetness_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    source_provider: Mapped[str] = mapped_column(String(50), default="Open-Meteo", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm")

    __table_args__ = (
        Index("ix_weather_farm_obs_time", "farm_id", "observation_time"),
    )
