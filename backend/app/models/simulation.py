"""
ACREVIA - Agricultural Scenario Simulation Models (Pillar B: ACREVIA Simulate).
Stores counterfactual scenario definitions and simulated agronomic projections.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class SimulationScenario(Base, TimestampMixin):
    __tablename__ = "simulation_scenarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    crop_season_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="SET NULL"), nullable=True, index=True)
    creator_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)

    scenario_type: Mapped[str] = mapped_column(String(50), nullable=False)  # IRRIGATION_WATER_BALANCE, THERMAL_GDD_STAGE, WATERLOGGING_STRESS
    scenario_name: Mapped[str] = mapped_column(String(150), nullable=False)
    baseline_snapshot_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("twin_snapshots.id", ondelete="SET NULL"), nullable=True)

    input_parameters_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    farmer_assumptions_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    constraints_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)  # PENDING, RUNNING, COMPLETED, FAILED

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot")
    creator: Mapped["User"] = relationship("User")
    result: Mapped[Optional["SimulationResult"]] = relationship("SimulationResult", back_populates="scenario", uselist=False, cascade="all, delete-orphan")


class SimulationResult(Base, TimestampMixin):
    __tablename__ = "simulation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_id: Mapped[str] = mapped_column(String(36), ForeignKey("simulation_scenarios.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)

    model_name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. FAO-56_DUAL_KC, GDD_THERMAL_MODEL
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. v1.4
    outputs_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    uncertainty_metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    evidence_sources_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    execution_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    scenario: Mapped["SimulationScenario"] = relationship("SimulationScenario", back_populates="result")
