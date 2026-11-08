"""
ACREVIA - Agricultural Resilience Engine Models (Pillar F).
Captures multi-dimensional farm resilience evaluations, evidence completeness tracking, and adaptation simulations.
"""

from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class ResilienceAssessment(Base, TimestampMixin):
    """Holistic multi-dimensional farm resilience evaluation and evidence quality audit."""
    __tablename__ = "resilience_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # 5-Dimensional Resilience Scores (0.0 - 100.0)
    overall_resilience_score: Mapped[float] = mapped_column(Float, nullable=False)
    soil_score: Mapped[float] = mapped_column(Float, nullable=False)
    water_score: Mapped[float] = mapped_column(Float, nullable=False)
    climate_score: Mapped[float] = mapped_column(Float, nullable=False)
    nutrient_score: Mapped[float] = mapped_column(Float, nullable=False)
    practice_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Evidence Quality & Confidence Propagation (0.0 - 1.0)
    evidence_quality_score: Mapped[float] = mapped_column(Float, default=0.80, nullable=False)
    confidence_category: Mapped[str] = mapped_column(String(50), default="HIGH_CONFIDENCE_EMPIRICAL", nullable=False)  # HIGH_CONFIDENCE_EMPIRICAL, MODERATE_CONFIDENCE_HYBRID, LOW_CONFIDENCE_INSUFFICIENT_DATA

    # Insights & Recommendations
    top_vulnerabilities_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    adaptation_recommendations_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    simulations: Mapped[List["ResilienceScenarioSimulation"]] = relationship("ResilienceScenarioSimulation", back_populates="assessment", cascade="all, delete-orphan")


class ResilienceScenarioSimulation(Base, TimestampMixin):
    """Simulated outcome of adopting a climate-resilient adaptation package."""
    __tablename__ = "resilience_scenario_simulations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(String(36), ForeignKey("resilience_assessments.id", ondelete="CASCADE"), index=True, nullable=False)
    package_name: Mapped[str] = mapped_column(String(100), nullable=False)
    simulated_overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    projected_water_saving_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    cost_delta_inr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    yield_risk_reduction_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    simulated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    assessment: Mapped["ResilienceAssessment"] = relationship("ResilienceAssessment", back_populates="simulations")
