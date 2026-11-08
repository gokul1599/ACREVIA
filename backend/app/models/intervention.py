"""
ACREVIA - Agricultural Intervention & Outcome Tracking Models.
Records field actions and links follow-up CropPulse observations to evaluate changes.
"""

import uuid
from datetime import date, datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Float, Integer, Date, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class InterventionRecord(Base, TimestampMixin):
    __tablename__ = "intervention_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    farmer_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # BIOLOGICAL, CHEMICAL, CULTURAL, IRRIGATION, FERTILIZER
    trade_name: Mapped[str] = mapped_column(String(150), nullable=False)
    active_ingredient: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    
    dosage: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(30), default="ml/acre", nullable=False)
    application_method: Mapped[str] = mapped_column(String(100), nullable=False)  # FOLIAR_SPRAY, SOIL_DRENCH, SEED_TREATMENT, TRAP
    application_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    
    target_condition: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phi_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Pre-harvest interval (days)
    rei_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)  # Re-entry interval (hours)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot")
    farm: Mapped["Farm"] = relationship("Farm")
    farmer: Mapped["User"] = relationship("User")
    outcomes: Mapped[List["OutcomeObservation"]] = relationship(
        "OutcomeObservation",
        back_populates="intervention",
        cascade="all, delete-orphan",
        order_by="OutcomeObservation.evaluation_date"
    )

    __table_args__ = (
        Index("ix_interventions_plot_date", "plot_id", "application_date"),
    )


class OutcomeObservation(Base, TimestampMixin):
    __tablename__ = "outcome_observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    intervention_id: Mapped[str] = mapped_column(String(36), ForeignKey("intervention_records.id", ondelete="CASCADE"), index=True, nullable=False)
    follow_up_observation_id: Mapped[str] = mapped_column(String(36), ForeignKey("observations.id", ondelete="CASCADE"), index=True, nullable=False)
    
    evaluation_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    observed_status: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # IMPROVING, STABLE, WORSENING, INCONCLUSIVE
    
    visual_change_notes: Mapped[str] = mapped_column(Text, nullable=False)
    confounding_factors: Mapped[str] = mapped_column(
        Text,
        default="Open-field conditions subject to temperature, rainfall wash-off, and untracked pest reservoirs. Correlation does not imply direct causation.",
        nullable=False
    )
    farmer_assessment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    days_post_intervention: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    intervention: Mapped["InterventionRecord"] = relationship("InterventionRecord", back_populates="outcomes")
    follow_up_observation: Mapped["Observation"] = relationship("Observation")
