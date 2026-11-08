"""
ACREVIA - Agricultural Collaboration & Community Models.
Pillar A: Moderated community spaces, structured post types, comments, and safety reporting.
"""

from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class Community(Base, TimestampMixin):
    __tablename__ = "communities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="CROP", nullable=False)  # CROP, TOPIC, GEOGRAPHY, PRACTICE
    crop_id: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)  # cotton, rice, chilli
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_moderated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    memberships: Mapped[List["CommunityMembership"]] = relationship("CommunityMembership", back_populates="community", cascade="all, delete-orphan")
    posts: Mapped[List["CommunityPost"]] = relationship("CommunityPost", back_populates="community", cascade="all, delete-orphan")


class CommunityMembership(Base):
    __tablename__ = "community_memberships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    community_id: Mapped[str] = mapped_column(String(36), ForeignKey("communities.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="MEMBER", nullable=False)  # MEMBER, MODERATOR, EXPERT_ADVISOR
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    community: Mapped["Community"] = relationship("Community", back_populates="memberships")

    __table_args__ = (
        Index("ix_comm_membership_unique", "community_id", "user_id", unique=True),
    )


class CommunityPost(Base, TimestampMixin):
    __tablename__ = "community_posts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    community_id: Mapped[str] = mapped_column(String(36), ForeignKey("communities.id", ondelete="CASCADE"), index=True, nullable=False)
    author_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    post_type: Mapped[str] = mapped_column(String(50), nullable=False)  # QUESTION, FIELD_EXPERIENCE, OBSERVATION, KNOWLEDGE_CONTRIBUTION, EDUCATIONAL_RESOURCE, EVENT_ANNOUNCEMENT, EXPERT_RESPONSE
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    crop_id: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    growth_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    visibility: Mapped[str] = mapped_column(String(30), default="COMMUNITY_PUBLIC", nullable=False)  # COMMUNITY_PUBLIC, RESTRICTED_MEMBERS, EXPERT_ONLY
    moderation_status: Mapped[str] = mapped_column(String(30), default="APPROVED", nullable=False)  # PENDING, APPROVED, FLAGGED, REMOVED
    is_expert_reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    helpful_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    community: Mapped["Community"] = relationship("Community", back_populates="posts")
    comments: Mapped[List["CommunityComment"]] = relationship("CommunityComment", back_populates="post", cascade="all, delete-orphan")
    reports: Mapped[List["CommunityReport"]] = relationship("CommunityReport", back_populates="post", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_community_posts_comm_created", "community_id", "created_at"),
    )


class CommunityComment(Base):
    __tablename__ = "community_comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id: Mapped[str] = mapped_column(String(36), ForeignKey("community_posts.id", ondelete="CASCADE"), index=True, nullable=False)
    author_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_expert_reply: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_helpful: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    moderation_status: Mapped[str] = mapped_column(String(30), default="APPROVED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    post: Mapped["CommunityPost"] = relationship("CommunityPost", back_populates="comments")


class CommunityReport(Base):
    __tablename__ = "community_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=True, index=True)
    comment_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("community_comments.id", ondelete="CASCADE"), nullable=True, index=True)
    reported_by_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    reason_category: Mapped[str] = mapped_column(String(50), nullable=False)  # SPAM, MISINFORMATION, DANGEROUS_ADVICE, HARASSMENT, COMMERCIAL_SOLICITATION
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)  # PENDING, RESOLVED, DISMISSED
    reviewed_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    post: Mapped[Optional["CommunityPost"]] = relationship("CommunityPost", back_populates="reports")
