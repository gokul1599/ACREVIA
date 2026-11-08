"""
ACREVIA - Agricultural Knowledge Contribution Models (ACREVIA Commons).
Pillar B: Governed knowledge submissions, expert reviews, translation versions, and KrishiBrain RAG handoff.
"""

from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class KnowledgeContribution(Base, TimestampMixin):
    __tablename__ = "knowledge_contributions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contributor_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    contribution_type: Mapped[str] = mapped_column(String(50), nullable=False)  # EXPLANATION, TERMINOLOGY, OBSERVATION, EXPERT_ARTICLE, ADVISORY, TRANSLATION_CORRECTION
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    original_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    crop_id: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)  # cotton, rice, chilli
    geographic_scope: Mapped[str] = mapped_column(String(100), default="Telangana", nullable=False)
    growth_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    evidence_references_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    usage_permission: Mapped[str] = mapped_column(String(50), default="CC_BY_SA_4_0", nullable=False)

    status: Mapped[str] = mapped_column(String(50), default="SUBMITTED", nullable=False)  # DRAFT, SUBMITTED, MODERATION_PENDING, AGRICULTURAL_REVIEW, LANGUAGE_REVIEW, APPROVED, REJECTED, PUBLISHED, ARCHIVED
    assigned_expert_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    approved_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    krishi_brain_ingested: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    krishi_brain_doc_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Relationships
    reviews: Mapped[List["ContributionReview"]] = relationship("ContributionReview", back_populates="contribution", cascade="all, delete-orphan")
    translations: Mapped[List["TranslationVersion"]] = relationship("TranslationVersion", back_populates="contribution", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_contrib_status_crop", "status", "crop_id"),
    )


class ContributionReview(Base):
    __tablename__ = "contribution_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contribution_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_contributions.id", ondelete="CASCADE"), index=True, nullable=False)
    reviewer_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    reviewer_role: Mapped[str] = mapped_column(String(50), nullable=False)  # EXPERT_AGRONOMIST, LANGUAGE_SPECIALIST, MODERATOR
    decision: Mapped[str] = mapped_column(String(30), nullable=False)  # APPROVE, REJECT, REQUEST_REVISION
    comments: Mapped[str] = mapped_column(Text, nullable=False)
    scientific_rating: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    safety_assessment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    contribution: Mapped["KnowledgeContribution"] = relationship("KnowledgeContribution", back_populates="reviews")


class TranslationVersion(Base):
    __tablename__ = "translation_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contribution_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_contributions.id", ondelete="CASCADE"), index=True, nullable=False)

    target_language: Mapped[str] = mapped_column(String(10), nullable=False)  # te, en, hi
    translated_title: Mapped[str] = mapped_column(String(200), nullable=False)
    translated_content: Mapped[str] = mapped_column(Text, nullable=False)
    is_native_reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reviewer_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    contribution: Mapped["KnowledgeContribution"] = relationship("KnowledgeContribution", back_populates="translations")
