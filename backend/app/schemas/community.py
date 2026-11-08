"""
ACREVIA - Agricultural Collaboration & Community Pydantic Schemas.
Pillar A: Community spaces, posts, comments, helpful votes, and moderation reports.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CommunityCreate(BaseModel):
    name: str
    slug: str
    description: str
    category: str = "CROP"  # CROP, TOPIC, GEOGRAPHY, PRACTICE
    crop_id: Optional[str] = None
    district: Optional[str] = None


class CommunityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str
    slug: str
    description: str
    category: str
    crop_id: Optional[str] = None
    district: Optional[str] = None
    is_moderated: bool
    created_at: datetime


class CommunityMembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    community_id: str
    user_id: str
    role: str
    joined_at: datetime


class CommunityPostCreate(BaseModel):
    post_type: str = "QUESTION"  # QUESTION, FIELD_EXPERIENCE, OBSERVATION, KNOWLEDGE_CONTRIBUTION, EDUCATIONAL_RESOURCE, EVENT_ANNOUNCEMENT, EXPERT_RESPONSE
    title: str
    content: str
    language: str = "en"
    crop_id: Optional[str] = None
    growth_stage: Optional[str] = None
    visibility: str = "COMMUNITY_PUBLIC"


class CommunityCommentCreate(BaseModel):
    content: str


class CommunityCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    post_id: str
    author_id: str
    content: str
    is_expert_reply: bool
    is_helpful: bool
    moderation_status: str
    created_at: datetime


class CommunityPostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    community_id: str
    author_id: str
    post_type: str
    title: str
    content: str
    language: str
    crop_id: Optional[str] = None
    growth_stage: Optional[str] = None
    visibility: str
    moderation_status: str
    is_expert_reviewed: bool
    helpful_count: int
    created_at: datetime
    updated_at: datetime
    comments: List[CommunityCommentResponse] = Field(default_factory=list)


class CommunityReportCreate(BaseModel):
    post_id: Optional[str] = None
    comment_id: Optional[str] = None
    reason_category: str = "MISINFORMATION"  # SPAM, MISINFORMATION, DANGEROUS_ADVICE, HARASSMENT, COMMERCIAL_SOLICITATION
    details: Optional[str] = None


class CommunityReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    post_id: Optional[str] = None
    comment_id: Optional[str] = None
    reported_by_user_id: str
    reason_category: str
    details: Optional[str] = None
    status: str
    created_at: datetime
