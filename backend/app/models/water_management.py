"""
ACREVIA - Precision Water Management Models (Pillar B).
Captures farm water sources, irrigation event logs, soil moisture sensor telemetry, and hydrological water balances.
"""

from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class WaterSource(Base, TimestampMixin):
    """Farm water infrastructure asset inventory."""
    __tablename__ = "water_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # BOREWELL, OPEN_WELL, CANAL_OUTLET, FARM_POND, TANKER
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    depth_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    static_water_level_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    discharge_capacity_lps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salinity_ec_dsm: Mapped[Optional[float]] = mapped_column(Float, default=0.75, nullable=True)
    ph: Mapped[Optional[float]] = mapped_column(Float, default=7.2, nullable=True)
    sar: Mapped[Optional[float]] = mapped_column(Float, default=2.0, nullable=True)
    seasonal_availability_json: Mapped[str] = mapped_column(Text, default='{"kharif": true, "rabi": true, "summer": false}', nullable=False)

    # Relationships
    irrigation_events: Mapped[List["IrrigationEvent"]] = relationship("IrrigationEvent", back_populates="water_source")


class IrrigationEvent(Base, TimestampMixin):
    """Verifiable irrigation journaling with metering and sensor correlation."""
    __tablename__ = "irrigation_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    water_source_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("water_sources.id", ondelete="SET NULL"), nullable=True)
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    irrigation_method: Mapped[str] = mapped_column(String(50), default="DRIP", nullable=False)  # DRIP, SPRINKLER, FLOOD, ALTERNATE_FURROW
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    flow_meter_start_m3: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    flow_meter_end_m3: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    calculated_volume_m3: Mapped[float] = mapped_column(Float, nullable=False)
    equivalent_depth_mm: Mapped[float] = mapped_column(Float, nullable=False)
    soil_moisture_before: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    soil_moisture_after: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationship
    water_source: Mapped[Optional["WaterSource"]] = relationship("WaterSource", back_populates="irrigation_events")


class SoilMoistureObservation(Base, TimestampMixin):
    """Multi-depth in-situ soil moisture sensor telemetry."""
    __tablename__ = "soil_moisture_observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    sensor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    depth_cm: Mapped[int] = mapped_column(Integer, nullable=False)  # 15, 30, 60
    volumetric_water_content: Mapped[float] = mapped_column(Float, nullable=False)  # % or m3/m3
    matric_potential_kpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    moisture_status: Mapped[str] = mapped_column(String(50), default="FIELD_CAPACITY", nullable=False)  # SATURATED, FIELD_CAPACITY, DEPLETED, WILTING
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class WaterBalanceSnapshot(Base, TimestampMixin):
    """Root-zone daily hydrological water balance accounting record."""
    __tablename__ = "water_balance_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    snapshot_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    effective_precipitation_mm: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    irrigation_applied_mm: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    crop_evapotranspiration_mm: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    deep_percolation_mm: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    runoff_mm: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    storage_change_mm: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    accounting_status: Mapped[str] = mapped_column(String(50), default="PARTIALLY_ESTIMATED", nullable=False)  # COMPLETED_WITH_VALIDATED_INPUTS, PARTIALLY_ESTIMATED, INSUFFICIENT_DATA
    management_allowed_depletion_percent: Mapped[float] = mapped_column(Float, default=45.0, nullable=False)
    current_depletion_percent: Mapped[float] = mapped_column(Float, default=20.0, nullable=False)
