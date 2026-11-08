"""
ACREVIA - Farmer Collectives & FPO Models (ACREVIA Collectives).
Pillar C: Organization profiles, verification, membership roles, and collective activities.
"""

from datetime import date, datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class AgriculturalOrganization(Base, TimestampMixin):
    __tablename__ = "agricultural_organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    org_type: Mapped[str] = mapped_column(String(50), nullable=False)  # FPO, COOPERATIVE, FARMER_GROUP, TRAINING_GROUP, RESEARCH_PARTICIPANT_GROUP
    registration_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), default="Telangana", nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    verification_status: Mapped[str] = mapped_column(String(50), default="APPLICATION_SUBMITTED", nullable=False)  # APPLICATION_SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, SUSPENDED
    verified_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Relationships
    memberships: Mapped[List["OrganizationMembership"]] = relationship("OrganizationMembership", back_populates="organization", cascade="all, delete-orphan")
    activities: Mapped[List["CollectiveActivity"]] = relationship("CollectiveActivity", back_populates="organization", cascade="all, delete-orphan")


class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("agricultural_organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    org_role: Mapped[str] = mapped_column(String(50), default="MEMBER", nullable=False)  # ORGANIZATION_ADMIN, GROUP_COORDINATOR, MEMBER, ADVISOR, OBSERVER
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    organization: Mapped["AgriculturalOrganization"] = relationship("AgriculturalOrganization", back_populates="memberships")

    __table_args__ = (
        Index("ix_org_member_unique", "organization_id", "user_id", unique=True),
    )


class CollectiveActivity(Base, TimestampMixin):
    __tablename__ = "collective_activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("agricultural_organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    created_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # SHARED_CALENDAR, TRAINING_SESSION, GROUP_ANNOUNCEMENT, COLLECTIVE_OBSERVATION, RESOURCE_COORDINATION
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PLANNED", nullable=False)  # PLANNED, IN_PROGRESS, COMPLETED, CANCELLED

    # Relationships
    organization: Mapped["AgriculturalOrganization"] = relationship("AgriculturalOrganization", back_populates="activities")
