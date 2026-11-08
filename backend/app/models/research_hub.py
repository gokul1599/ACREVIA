"""
ACREVIA - Agricultural Research Hub & Governance Models.
Pillar D: Research projects, purpose-specific consent, dataset splits, annotation tasks, and disagreement tracking.
"""

from datetime import datetime, timezone
from decimal import Decimal
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Integer, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class ResearchProject(Base, TimestampMixin):
    __tablename__ = "research_projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    lead_researcher_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    institution_name: Mapped[str] = mapped_column(String(150), nullable=False)
    research_objectives: Mapped[str] = mapped_column(Text, nullable=False)
    supported_crops_json: Mapped[str] = mapped_column(Text, default='["cotton", "rice", "chilli"]', nullable=False)
    geographic_scope: Mapped[str] = mapped_column(String(100), default="Telangana", nullable=False)
    project_status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)  # ACTIVE, COMPLETED, PAUSED
    publication_references_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)

    # Relationships
    consents: Mapped[List["ResearchConsent"]] = relationship("ResearchConsent", back_populates="project", cascade="all, delete-orphan")
    datasets: Mapped[List["DatasetContribution"]] = relationship("DatasetContribution", back_populates="project", cascade="all, delete-orphan")
    tasks: Mapped[List["AnnotationTask"]] = relationship("AnnotationTask", back_populates="project", cascade="all, delete-orphan")


class ResearchConsent(Base):
    __tablename__ = "research_consents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), index=True, nullable=False)
    farmer_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    consent_scope: Mapped[str] = mapped_column(String(50), nullable=False)  # OBSERVATIONS_ONLY, ANNOTATED_IMAGES, SENSOR_DATA, HARVEST_METRICS, FULL_RESEARCH
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    consent_version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    project: Mapped["ResearchProject"] = relationship("ResearchProject", back_populates="consents")

    __table_args__ = (
        Index("ix_res_consent_farmer_proj", "farmer_id", "project_id"),
    )


class DatasetContribution(Base, TimestampMixin):
    __tablename__ = "dataset_contributions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), index=True, nullable=False)
    contributor_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    dataset_name: Mapped[str] = mapped_column(String(150), nullable=False)
    crop_id: Mapped[str] = mapped_column(String(50), nullable=False)  # cotton, rice, chilli
    sample_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    data_type: Mapped[str] = mapped_column(String(50), nullable=False)  # CROP_IMAGES, OBSERVATIONS, SENSOR_TELEMETRY
    split_type: Mapped[str] = mapped_column(String(20), default="TRAIN", nullable=False)  # TRAIN, VALIDATION, TEST
    storage_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    license: Mapped[str] = mapped_column(String(50), default="CC_BY_4_0", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="SUBMITTED", nullable=False)  # SUBMITTED, VALIDATED, PUBLISHED

    # Relationships
    project: Mapped["ResearchProject"] = relationship("ResearchProject", back_populates="datasets")


class AnnotationTask(Base):
    __tablename__ = "annotation_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), index=True, nullable=False)
    assigned_expert_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    task_type: Mapped[str] = mapped_column(String(50), nullable=False)  # CROP_CLASSIFICATION, SYMPTOM_ANNOTATION, IMAGE_QUALITY, GROWTH_STAGE
    entity_reference_id: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)  # PENDING, COMPLETED, DISPUTED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    project: Mapped["ResearchProject"] = relationship("ResearchProject", back_populates="tasks")
    records: Mapped[List["AnnotationRecord"]] = relationship("AnnotationRecord", back_populates="task", cascade="all, delete-orphan")


class AnnotationRecord(Base):
    __tablename__ = "annotation_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("annotation_tasks.id", ondelete="CASCADE"), index=True, nullable=False)
    annotator_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    label_taxonomy_version: Mapped[str] = mapped_column(String(50), default="ACREVIA_TAXONOMY_V1", nullable=False)
    label_assigned: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("1.0000"), nullable=False)
    disagreement_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    task: Mapped["AnnotationTask"] = relationship("AnnotationTask", back_populates="records")
