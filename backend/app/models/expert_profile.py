"""
ACREVIA - Agricultural Expert Profile & Verification Model.
Enforces credential verification before granting agronomist advisory rights.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class ExpertProfile(Base, TimestampMixin):
    __tablename__ = "expert_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    registration_number: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    highest_degree: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., M.Sc. Agronomy, Ph.D. Plant Pathology
    institution: Mapped[str] = mapped_column(String(150), nullable=False)     # e.g., PJTSAU, ICAR-CRIDA, KVK
    specializations_json: Mapped[str] = mapped_column(String(500), default='["COTTON","RICE","CHILLI"]', nullable=False)
    districts_covered_json: Mapped[str] = mapped_column(String(500), default='["Warangal","Khammam"]', nullable=False)
    
    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="APPLICATION_SUBMITTED",
        index=True,
        nullable=False
    )  # APPLICATION_SUBMITTED, UNDER_REVIEW, APPROVED, SUSPENDED, REVOKED
    
    verified_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    verifier: Mapped[Optional["User"]] = relationship("User", foreign_keys=[verified_by_user_id])
