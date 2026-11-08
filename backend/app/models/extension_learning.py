"""
ACREVIA - Agricultural Extension & Learning Models.
Pillar E: Educational guides, university advisories, interactive training events, and farmer feedback.
"""

from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class LearningResource(Base, TimestampMixin):
    __tablename__ = "learning_resources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content_body: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)  # CROP_GUIDE, EDUCATIONAL_ARTICLE, GOVERNMENT_ADVISORY, RESEARCH_SUMMARY, FAQ
    creator_org_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agricultural_organizations.id", ondelete="SET NULL"), nullable=True)
    creator_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    crop_id: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)  # cotton, rice, chilli
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    review_status: Mapped[str] = mapped_column(String(30), default="PUBLISHED", nullable=False)  # DRAFT, IN_REVIEW, VERIFIED_OFFICIAL, PUBLISHED
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    feedback: Mapped[List["LearningFeedback"]] = relationship("LearningFeedback", back_populates="resource", cascade="all, delete-orphan")


class TrainingEvent(Base, TimestampMixin):
    __tablename__ = "training_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organizer_org_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agricultural_organizations.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # WORKSHOP, FIELD_DEMONSTRATION, WEBINAR, EXPERT_QA
    target_crop_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    meeting_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    max_capacity: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="SCHEDULED", nullable=False)  # SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED

    # Relationships
    registrations: Mapped[List["EventRegistration"]] = relationship("EventRegistration", back_populates="event", cascade="all, delete-orphan")


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("training_events.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    attendance_status: Mapped[str] = mapped_column(String(30), default="REGISTERED", nullable=False)  # REGISTERED, ATTENDED, CANCELLED
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    event: Mapped["TrainingEvent"] = relationship("TrainingEvent", back_populates="registrations")

    __table_args__ = (
        Index("ix_event_reg_unique", "event_id", "user_id", unique=True),
    )


class LearningFeedback(Base):
    __tablename__ = "learning_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resource_id: Mapped[str] = mapped_column(String(36), ForeignKey("learning_resources.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    feedback_type: Mapped[str] = mapped_column(String(50), nullable=False)  # HELPFUL, NOT_HELPFUL, DIFFICULT_TO_UNDERSTAND, OUTDATED, INCORRECT_TRANSLATION
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    resource: Mapped["LearningResource"] = relationship("LearningResource", back_populates="feedback")
