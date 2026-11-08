"""
ACREVIA - Agricultural Knowledge Graph Models.
Stores typed domain entities, causal & agronomic relationships,
and evidence provenance for hybrid graph traversal with KrishiBrain.
"""

import uuid
from typing import Optional, List
from sqlalchemy import String, Float, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class KnowledgeEntity(Base, TimestampMixin):
    __tablename__ = "knowledge_entities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # CROP, DISEASE, PEST, WEATHER_CONDITION, SOIL_TYPE, AGRONOMIC_PRACTICE, SYMPTOM
    
    canonical_name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    local_name_te: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    local_name_hi: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    scientific_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    
    properties_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)

    # Relationships
    outbound_relationships: Mapped[List["KnowledgeRelationship"]] = relationship(
        "KnowledgeRelationship",
        foreign_keys="KnowledgeRelationship.source_entity_id",
        back_populates="source_entity",
        cascade="all, delete-orphan"
    )
    inbound_relationships: Mapped[List["KnowledgeRelationship"]] = relationship(
        "KnowledgeRelationship",
        foreign_keys="KnowledgeRelationship.target_entity_id",
        back_populates="target_entity",
        cascade="all, delete-orphan"
    )


class KnowledgeRelationship(Base, TimestampMixin):
    __tablename__ = "knowledge_relationships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_entities.id", ondelete="CASCADE"), index=True, nullable=False)
    target_entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_entities.id", ondelete="CASCADE"), index=True, nullable=False)
    
    relationship_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # AFFECTS_CROP, FAVORED_BY_CONDITION, INDICATED_BY_SYMPTOM, SUPPRESSED_BY_PRACTICE, REQUIRES_SOIL
    confidence_weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    evidence_source: Mapped[str] = mapped_column(String(200), default="PJTSAU POP / ICAR Advisory", nullable=False)
    
    properties_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)

    # Relationships
    source_entity: Mapped["KnowledgeEntity"] = relationship("KnowledgeEntity", foreign_keys=[source_entity_id], back_populates="outbound_relationships")
    target_entity: Mapped["KnowledgeEntity"] = relationship("KnowledgeEntity", foreign_keys=[target_entity_id], back_populates="inbound_relationships")

    __table_args__ = (
        Index("ix_kg_rel_source_type", "source_entity_id", "relationship_type"),
        Index("ix_kg_rel_target_type", "target_entity_id", "relationship_type"),
    )
