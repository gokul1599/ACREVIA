"""
ACREVIA - KrishiBrain Knowledge Chunk Models.
Stores structure-aware text chunks preserving heading hierarchy and physical page citations.
"""

import uuid
from typing import List, Optional
from sqlalchemy import String, Integer, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class KnowledgeChunk(Base, TimestampMixin):
    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_document_versions.id", ondelete="CASCADE"), index=True, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_section: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    heading_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # e.g., Cotton > Pest Management > Pink Bollworm
    content: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    crop_scope: Mapped[str] = mapped_column(String(50), default="cotton", nullable=False)
    region_scope: Mapped[str] = mapped_column(String(50), default="Telangana", nullable=False)
    growth_stage_scope: Mapped[str] = mapped_column(String(50), default="ALL", nullable=False)
    page_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    page_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    approval_status: Mapped[str] = mapped_column(String(50), default="APPROVED", nullable=False)

    # Relationships
    document_version: Mapped["KnowledgeDocumentVersion"] = relationship("KnowledgeDocumentVersion", back_populates="chunks")
    embeddings: Mapped[List["KnowledgeEmbedding"]] = relationship("KnowledgeEmbedding", back_populates="chunk", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_knowledge_chunks_crop_lang", "crop_scope", "language"),
        Index("ix_knowledge_chunks_approval", "approval_status"),
    )
