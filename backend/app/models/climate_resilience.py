"""
ACREVIA - Climate Resilience Models (Pillar C).
Captures 30-year climatological baselines, agricultural hazard evaluations, and adaptation scenarios.
"""

from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class ClimateBaseline(Base, TimestampMixin):
    """District 30-year climatological normal baseline (IMD/ERA5 1991-2020)."""
    __tablename__ = "climate_baselines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    district_code: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # e.g., TL_WARANGAL, TL_KHAMMAM
    month: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 - 12
    normal_rainfall_mm: Mapped[float] = mapped_column(Float, nullable=False)
    normal_tmax_celsius: Mapped[float] = mapped_column(Float, nullable=False)
    normal_tmin_celsius: Mapped[float] = mapped_column(Float, nullable=False)
    extreme_heat_days_p90: Mapped[float] = mapped_column(Float, default=2.0, nullable=False)
    dry_spell_frequency: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    heavy_rain_days_count: Mapped[float] = mapped_column(Float, default=1.5, nullable=False)
    baseline_period: Mapped[str] = mapped_column(String(20), default="1991-2020", nullable=False)


class ClimateExposureAssessment(Base, TimestampMixin):
    """Plot-level agro-climatic hazard exposure and vulnerability evaluation."""
    __tablename__ = "climate_exposure_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    crop_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("crops.id", ondelete="SET NULL"), nullable=True)
    hazard_type: Mapped[str] = mapped_column(String(50), nullable=False)  # HEAT_STRESS, DRY_SPELL, EXTREME_RAINFALL, WATERLOGGING, HIGH_WIND
    severity_level: Mapped[str] = mapped_column(String(30), default="MODERATE", nullable=False)  # LOW, MODERATE, HIGH, CRITICAL
    crop_stage: Mapped[str] = mapped_column(String(100), nullable=False)
    vulnerability_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 - 1.0
    forecast_tmax: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    forecast_rainfall_next_7_days: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    consecutive_rainless_days: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)
    recommended_adaptation: Mapped[str] = mapped_column(Text, nullable=False)
    institutional_citation: Mapped[str] = mapped_column(String(200), default="PJTSAU / ICAR-CRIDA", nullable=False)
    assessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    scenarios: Mapped[List["ClimateAdaptationScenario"]] = relationship("ClimateAdaptationScenario", back_populates="assessment", cascade="all, delete-orphan")


class ClimateAdaptationScenario(Base, TimestampMixin):
    """Simulated adaptation interventions mitigating climate hazards."""
    __tablename__ = "climate_adaptation_scenarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(String(36), ForeignKey("climate_exposure_assessments.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    projected_loss_reduction_percent: Mapped[float] = mapped_column(Float, nullable=False)
    cost_delta_inr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    intervention_actions_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)

    # Relationship
    assessment: Mapped["ClimateExposureAssessment"] = relationship("ClimateExposureAssessment", back_populates="scenarios")
