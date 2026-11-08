"""
ACREVIA - KrishiBrain Knowledge Feedback Models.
Tracks farmer and agronomist feedback regarding citation accuracy and retrieval relevance.
"""

import uuid
from typing import Optional
from sqlalchemy import String, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import Base, TimestampMixin


class KnowledgeFeedback(Base, TimestampMixin):
    __tablename__ = "knowledge_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    issue_category: Mapped[str] = mapped_column(String(50), nullable=False)  # INCORRECT_ANSWER, MISSING_CITATION, INCORRECT_CITATION, OUTDATED_SOURCE, WRONG_CROP, LANGUAGE_QUALITY, UNSAFE_RECOMMENDATION
    user_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewer_status: Mapped[str] = mapped_column(String(50), default="SUBMITTED", nullable=False)  # SUBMITTED, INVESTIGATING, RESOLVED, DISMISSED
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_knowledge_feedback_status", "reviewer_status"),
    )
