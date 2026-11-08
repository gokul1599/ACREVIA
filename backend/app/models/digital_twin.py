"""
ACREVIA - Farm Digital Twin Models (Pillar A: ACREVIA Twin).
Hierarchical digital representation of farm, plot, and crop season states
with strict 8-tier provenance tracking and immutable snapshot records.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, JSON, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class FarmTwin(Base, TimestampMixin):
    __tablename__ = "farm_twins"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    twin_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    state_status: Mapped[str] = mapped_column(String(50), default="SYNCHRONIZED", nullable=False)  # SYNCHRONIZED, STALE, RECONCILING, ERROR
    last_synchronized_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completeness_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm")
    snapshots: Mapped[List["TwinSnapshot"]] = relationship("TwinSnapshot", back_populates="twin", cascade="all, delete-orphan")
    sync_events: Mapped[List["TwinSynchronizationEvent"]] = relationship("TwinSynchronizationEvent", back_populates="twin", cascade="all, delete-orphan")


class TwinSnapshot(Base, TimestampMixin):
    __tablename__ = "twin_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    twin_id: Mapped[str] = mapped_column(String(36), ForeignKey("farm_twins.id", ondelete="CASCADE"), index=True, nullable=False)
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    plot_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("plots.id", ondelete="SET NULL"), nullable=True, index=True)
    crop_season_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="SET NULL"), nullable=True, index=True)

    snapshot_version: Mapped[int] = mapped_column(Integer, nullable=False)
    state_payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    source_manifest_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    data_completeness_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    twin: Mapped["FarmTwin"] = relationship("FarmTwin", back_populates="snapshots")
    state_records: Mapped[List["TwinStateRecord"]] = relationship("TwinStateRecord", back_populates="snapshot", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_twin_snapshots_farm_ver", "farm_id", "snapshot_version"),
    )


class TwinStateRecord(Base, TimestampMixin):
    __tablename__ = "twin_state_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    snapshot_id: Mapped[str] = mapped_column(String(36), ForeignKey("twin_snapshots.id", ondelete="CASCADE"), index=True, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # PLOT, SOIL, CROP, SENSOR, WEATHER, OPERATION
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    property_name: Mapped[str] = mapped_column(String(100), nullable=False)
    property_value_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    provenance_type: Mapped[str] = mapped_column(String(50), nullable=False)  # MEASURED, FARMER_REPORTED, EXPERT_REVIEWED, AI_ESTIMATED, PROVIDER_OBSERVATION, SIMULATED, INFERRED, UNKNOWN
    source_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    quality_status: Mapped[str] = mapped_column(String(30), default="VERIFIED", nullable=False)

    snapshot: Mapped["TwinSnapshot"] = relationship("TwinSnapshot", back_populates="state_records")

    __table_args__ = (
        Index("ix_twin_state_prop_lookup", "snapshot_id", "property_name"),
    )


class TwinSynchronizationEvent(Base, TimestampMixin):
    __tablename__ = "twin_synchronization_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    twin_id: Mapped[str] = mapped_column(String(36), ForeignKey("farm_twins.id", ondelete="CASCADE"), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    twin: Mapped["FarmTwin"] = relationship("FarmTwin", back_populates="sync_events")
