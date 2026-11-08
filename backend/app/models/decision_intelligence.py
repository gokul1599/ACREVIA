"""
ACREVIA - Agricultural Decision Intelligence Models (Pillar E: ACREVIA Decision).
Stores unified decision evaluations, grounded multilingual explanations, and farmer feedback.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class DecisionRecord(Base, TimestampMixin):
    __tablename__ = "decision_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    farmer_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)

    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    decision_category: Mapped[str] = mapped_column(String(50), nullable=False)  # IRRIGATION_SCHEDULING, PEST_MANAGEMENT, FERTILIZER_APPLICATION, HARVEST_WINDOW
    recommendation_state: Mapped[str] = mapped_column(String(50), nullable=False)  # INFORMATIONAL, EVIDENCE_SUPPORTED, SCENARIO_RESULT, REQUIRES_MORE_INFORMATION, REQUIRES_EXPERT_REVIEW, INSUFFICIENT_EVIDENCE, NOT_SUPPORTED

    evidence_sources_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    grounded_explanation_en: Mapped[str] = mapped_column(Text, nullable=False)
    grounded_explanation_te: Mapped[str] = mapped_column(Text, nullable=False)
    grounded_explanation_hi: Mapped[str] = mapped_column(Text, nullable=False)
    uncertainty_disclosures_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    expert_escalation_case_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("expert_review_cases.id", ondelete="SET NULL"), nullable=True)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot")
    farmer: Mapped["User"] = relationship("User")
    feedback: Mapped[List["DecisionFeedback"]] = relationship("DecisionFeedback", back_populates="decision", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_decision_records_plot_eval", "plot_id", "evaluated_at"),
    )


class DecisionFeedback(Base, TimestampMixin):
    __tablename__ = "decision_feedbacks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    decision_id: Mapped[str] = mapped_column(String(36), ForeignKey("decision_records.id", ondelete="CASCADE"), index=True, nullable=False)

    farmer_action_taken: Mapped[str] = mapped_column(String(50), nullable=False)  # ADOPTED, PARTIALLY_ADOPTED, REJECTED, INAPPLICABLE
    farmer_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1 to 5
    feedback_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    observed_outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    decision: Mapped["DecisionRecord"] = relationship("DecisionRecord", back_populates="feedback")
