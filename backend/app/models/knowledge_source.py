"""
ACREVIA - KrishiBrain Knowledge Source Models.
Tracks approved agricultural institutions, publishers, and governance approvals.
"""

import uuid
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class KnowledgeSource(Base, TimestampMixin):
    __tablename__ = "knowledge_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    publisher_name: Mapped[str] = mapped_column(String(150), nullable=False)
    publisher_type: Mapped[str] = mapped_column(String(50), default="RESEARCH_COUNCIL", nullable=False)  # UNIVERSITY, GOVERNMENT_DEPT, RESEARCH_COUNCIL, KVK
    official_domain: Mapped[str] = mapped_column(String(100), nullable=False)
    authority_level: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    licensing_status: Mapped[str] = mapped_column(String(50), default="GOVERNMENT_OPEN_ACCESS", nullable=False)
    approval_status: Mapped[str] = mapped_column(String(50), default="PENDING_REVIEW", nullable=False)  # PENDING_REVIEW, APPROVED, REJECTED, SUSPENDED, EXPIRED
    reviewer_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    documents: Mapped[List["KnowledgeDocument"]] = relationship("KnowledgeDocument", back_populates="source", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_knowledge_sources_approval", "approval_status"),
        Index("ix_knowledge_sources_publisher", "publisher_name"),
    )
