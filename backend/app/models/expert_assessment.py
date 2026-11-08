"""
ACREVIA - Expert Assessment & Immutable Revision History Models.
Provides structured human agronomist reports with complete audit trail.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class ExpertAssessment(Base, TimestampMixin):
    __tablename__ = "expert_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("expert_review_cases.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    expert_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    
    confirmed_crop: Mapped[str] = mapped_column(String(50), nullable=False)
    primary_condition: Mapped[str] = mapped_column(String(100), nullable=False)
    differential_diagnoses_json: Mapped[Optional[str]] = mapped_column(Text, default="[]", nullable=True)
    
    confidence_rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 5 scale
    urgency_level: Mapped[str] = mapped_column(String(20), default="ROUTINE", nullable=False)  # LOW, ROUTINE, HIGH, EMERGENCY
    
    management_plan: Mapped[str] = mapped_column(Text, nullable=False)
    ipm_strategy: Mapped[str] = mapped_column(Text, nullable=False)
    cibrc_advisories: Mapped[str] = mapped_column(Text, nullable=False)
    
    revision_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    case: Mapped["ExpertReviewCase"] = relationship("ExpertReviewCase", back_populates="assessment")
    expert: Mapped["User"] = relationship("User", foreign_keys=[expert_id])
    revisions: Mapped[List["ExpertAssessmentRevision"]] = relationship(
        "ExpertAssessmentRevision",
        back_populates="assessment",
        cascade="all, delete-orphan",
        order_by="ExpertAssessmentRevision.revision_number"
    )


class ExpertAssessmentRevision(Base):
    __tablename__ = "expert_assessment_revisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id: Mapped[str] = mapped_column(String(36), ForeignKey("expert_assessments.id", ondelete="CASCADE"), index=True, nullable=False)
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    previous_assessment_json: Mapped[str] = mapped_column(Text, nullable=False)
    revision_reason: Mapped[str] = mapped_column(Text, nullable=False)
    
    revised_by_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    revised_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    assessment: Mapped["ExpertAssessment"] = relationship("ExpertAssessment", back_populates="revisions")
    revised_by: Mapped["User"] = relationship("User", foreign_keys=[revised_by_user_id])

    __table_args__ = (
        Index("ix_revisions_assessment_num", "assessment_id", "revision_number", unique=True),
    )
