"""
ACREVIA - Expert Review Case Model.
Tracks the clinical diagnostic consultation lifecycle between farmers, AI inference, and agronomists.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class ExpertReviewCase(Base, TimestampMixin):
    __tablename__ = "expert_review_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    diagnosis_request_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("diagnosis_requests.id", ondelete="CASCADE"), nullable=True, index=True)
    observation_id: Mapped[str] = mapped_column(String(36), ForeignKey("observations.id", ondelete="CASCADE"), index=True, nullable=False)
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    plot_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("plots.id", ondelete="SET NULL"), nullable=True)
    
    crop_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # COTTON, RICE, CHILLI
    priority: Mapped[str] = mapped_column(String(20), default="ROUTINE", index=True, nullable=False)  # ROUTINE, URGENT
    status: Mapped[str] = mapped_column(String(50), default="QUEUED", index=True, nullable=False)    # QUEUED, ASSIGNED, IN_REVIEW, COMPLETED, ESCALATED
    
    assigned_expert_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    observation: Mapped["Observation"] = relationship("Observation")
    farm: Mapped["Farm"] = relationship("Farm")
    plot: Mapped[Optional["Plot"]] = relationship("Plot")
    assigned_expert: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_expert_id])
    assessment: Mapped[Optional["ExpertAssessment"]] = relationship("ExpertAssessment", back_populates="case", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_expert_cases_queue", "crop_id", "status", "priority"),
    )
