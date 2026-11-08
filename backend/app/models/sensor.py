"""
ACREVIA - IoT & Sensor Ecosystem Models (Pillar C: Acrevia Sense).
Stores field device registry, authentication credentials, high-frequency telemetry,
and calibration verification records.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class SensorDevice(Base, TimestampMixin):
    __tablename__ = "sensor_devices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    plot_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("plots.id", ondelete="SET NULL"), index=True, nullable=True)
    
    device_serial_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    device_category: Mapped[str] = mapped_column(String(50), nullable=False)  # SOIL_PROBE, WEATHER_STATION, LEAF_WETNESS, NPK_PROBE
    auth_token_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    
    firmware_version: Mapped[Optional[str]] = mapped_column(String(50), default="1.0.0", nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)  # ACTIVE, INACTIVE, DECOMMISSIONED, ERROR
    last_heartbeat_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    properties_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm")
    plot: Mapped[Optional["Plot"]] = relationship("Plot")
    measurements: Mapped[List["SensorMeasurement"]] = relationship("SensorMeasurement", back_populates="device", cascade="all, delete-orphan")
    calibrations: Mapped[List["SensorCalibration"]] = relationship("SensorCalibration", back_populates="device", cascade="all, delete-orphan")


class SensorMeasurement(Base, TimestampMixin):
    __tablename__ = "sensor_measurements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id: Mapped[str] = mapped_column(String(36), ForeignKey("sensor_devices.id", ondelete="CASCADE"), index=True, nullable=False)
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    
    soil_moisture_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    soil_temperature_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ambient_temperature_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    relative_humidity_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    leaf_wetness_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    solar_radiation_w_m2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    battery_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    signal_rssi: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    data_quality_flag: Mapped[str] = mapped_column(String(50), default="VALID", nullable=False)  # VALID, SUSPECT_STUCK, SUSPECT_SPIKE, UNCALIBRATED, OUT_OF_BOUNDS
    quality_notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    device: Mapped["SensorDevice"] = relationship("SensorDevice", back_populates="measurements")
    plot: Mapped["Plot"] = relationship("Plot")

    __table_args__ = (
        Index("ix_sensor_measurements_plot_ts", "plot_id", "timestamp"),
        Index("ix_sensor_measurements_device_ts", "device_id", "timestamp"),
    )


class SensorCalibration(Base, TimestampMixin):
    __tablename__ = "sensor_calibrations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id: Mapped[str] = mapped_column(String(36), ForeignKey("sensor_devices.id", ondelete="CASCADE"), index=True, nullable=False)
    
    calibrated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    calibrated_by: Mapped[str] = mapped_column(String(100), nullable=False)
    
    calibration_coefficients_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    device: Mapped["SensorDevice"] = relationship("SensorDevice", back_populates="calibrations")
