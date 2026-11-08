"""
ACREVIA - Data Governance, Consent & Audit Log Models.
Ensures full DPDPA 2023 compliance, farmer consent tracking, and immutable audit trails.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    consent_type: Mapped[str] = mapped_column(String(50), nullable=False)  # CORE_SERVICE, EXPERT_REVIEW, RESEARCH_PARTICIPATION, MODEL_TRAINING
    is_granted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    policy_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="consents")

    __table_args__ = (
        Index("ix_consent_user_type", "user_id", "consent_type"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    farm_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # CREATE, READ, UPDATE, DELETE, INFERENCE_REQUEST, LOGIN
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)  # FARM, PLOT, OBSERVATION, DIAGNOSIS, USER
    resource_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
    metadata_json: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
