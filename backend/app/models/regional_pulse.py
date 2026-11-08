"""
ACREVIA - Regional Pulse & Intelligence Models.
Pillar F: Privacy-preserving regional agricultural signal aggregation, evidence verification, and outbreak claim suppression.
"""

from datetime import date, datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Integer, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class RegionalSignal(Base, TimestampMixin):
    __tablename__ = "regional_signals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    district: Mapped[str] = mapped_column(String(100), index=True, nullable=False)  # Warangal, Khammam, Suryapet, Karimnagar, Adilabad
    state: Mapped[str] = mapped_column(String(100), default="Telangana", nullable=False)
    crop_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # cotton, rice, chilli

    signal_category: Mapped[str] = mapped_column(String(50), nullable=False)  # OBSERVATION_SURGE, WEATHER_EXPOSURE, PEST_INQUIRIES, ADVISORY_ALERT, SATELLITE_VEGETATION_CHANGE
    signal_title: Mapped[str] = mapped_column(String(200), nullable=False)
    signal_summary: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_tier: Mapped[str] = mapped_column(String(50), nullable=False)  # FARMER_REPORT, MULTIPLE_INDEPENDENT, AI_ASSISTED, EXPERT_REVIEWED, OFFICIAL_ADVISORY
    source_observation_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    distinct_farms_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_outbreak_claim_suppressed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    validation_status: Mapped[str] = mapped_column(String(50), default="UNVALIDATED_OBSERVATION", nullable=False)  # UNVALIDATED_OBSERVATION, EXPERT_CONFIRMED, OFFICIAL_ALERT
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)
    observed_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    observed_end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    evidences: Mapped[List["RegionalSignalEvidence"]] = relationship("RegionalSignalEvidence", back_populates="signal", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_reg_signal_dist_crop", "district", "crop_id"),
    )


class RegionalSignalEvidence(Base):
    __tablename__ = "regional_signal_evidences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    signal_id: Mapped[str] = mapped_column(String(36), ForeignKey("regional_signals.id", ondelete="CASCADE"), index=True, nullable=False)

    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False)  # OBSERVATION_REF, RISKCAST_ALERT, EXPERT_CASE_REF, SATELLITE_INDEX
    evidence_reference_id: Mapped[str] = mapped_column(String(100), nullable=False)
    evidence_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    signal: Mapped["RegionalSignal"] = relationship("RegionalSignal", back_populates="evidences")
