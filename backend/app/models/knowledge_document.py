"""
ACREVIA - KrishiBrain Knowledge Document & Version Models.
Maintains immutable versioning for agricultural monographs and advisories.
"""

import uuid
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy import String, Integer, Date, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class KnowledgeDocument(Base, TimestampMixin):
    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_sources.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    document_type: Mapped[str] = mapped_column(String(20), default="PDF", nullable=False)  # PDF, DOCX, HTML, TEXT, MARKDOWN
    primary_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)  # te, en, hi
    crop_scope: Mapped[str] = mapped_column(String(50), default="cotton", nullable=False)  # cotton, rice, chilli, all
    region_scope: Mapped[str] = mapped_column(String(50), default="Telangana", nullable=False)
    topic_scope: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # IPM, NUTRIENT, WEED, IRRIGATION
    current_version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING_REVIEW", nullable=False)

    # Relationships
    source: Mapped["KnowledgeSource"] = relationship("KnowledgeSource", back_populates="documents")
    versions: Mapped[List["KnowledgeDocumentVersion"]] = relationship("KnowledgeDocumentVersion", back_populates="document", cascade="all, delete-orphan", foreign_keys="KnowledgeDocumentVersion.document_id")

    __table_args__ = (
        Index("ix_knowledge_docs_crop_status", "crop_scope", "status"),
        Index("ix_knowledge_docs_language", "primary_language"),
    )


class KnowledgeDocumentVersion(Base, TimestampMixin):
    __tablename__ = "knowledge_document_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_documents.id", ondelete="CASCADE"), index=True, nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # SHA-256
    original_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    publication_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    extraction_status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)  # PENDING, EXTRACTED, FAILED
    review_status: Mapped[str] = mapped_column(String(50), default="PENDING_REVIEW", nullable=False)
    supersedes_version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Relationships
    document: Mapped["KnowledgeDocument"] = relationship("KnowledgeDocument", back_populates="versions", foreign_keys=[document_id])
    chunks: Mapped[List["KnowledgeChunk"]] = relationship("KnowledgeChunk", back_populates="document_version", cascade="all, delete-orphan")
