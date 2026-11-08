"""
ACREVIA - KrishiBrain Vector Embedding Models.
Stores dense vector representations in Neon pgvector with profile tracking.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from backend.app.database.base import Base


class KnowledgeEmbedding(Base):
    __tablename__ = "knowledge_embeddings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chunk_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_chunks.id", ondelete="CASCADE"), index=True, nullable=False)
    embedding_profile_id: Mapped[str] = mapped_column(String(100), default="text-embedding-3-small", nullable=False)
    embedding = mapped_column(Vector(1536), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, default=1536, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    chunk: Mapped["KnowledgeChunk"] = relationship("KnowledgeChunk", back_populates="embeddings")

    __table_args__ = (
        Index("ix_embeddings_profile", "embedding_profile_id"),
    )
