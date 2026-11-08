"""
ACREVIA - Agricultural Extension & Learning Pydantic Schemas.
Pillar E: Educational guides, university advisories, interactive training events, and feedback.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class LearningResourceCreate(BaseModel):
    title: str
    content_body: str
    resource_type: str = "CROP_GUIDE"  # CROP_GUIDE, EDUCATIONAL_ARTICLE, GOVERNMENT_ADVISORY, RESEARCH_SUMMARY, FAQ
    creator_org_id: Optional[str] = None
    crop_id: Optional[str] = None
    language: str = "en"


class LearningFeedbackCreate(BaseModel):
    feedback_type: str = "HELPFUL"  # HELPFUL, NOT_HELPFUL, DIFFICULT_TO_UNDERSTAND, OUTDATED, INCORRECT_TRANSLATION
    comments: Optional[str] = None


class LearningFeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    resource_id: str
    user_id: str
    feedback_type: str
    comments: Optional[str] = None
    created_at: datetime


class LearningResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    title: str
    content_body: str
    resource_type: str
    creator_org_id: Optional[str] = None
    creator_user_id: str
    crop_id: Optional[str] = None
    language: str
    review_status: str
    view_count: int
    created_at: datetime


class TrainingEventCreate(BaseModel):
    organizer_org_id: Optional[str] = None
    title: str
    description: str
    event_type: str = "WORKSHOP"  # WORKSHOP, FIELD_DEMONSTRATION, WEBINAR, EXPERT_QA
    target_crop_id: Optional[str] = None
    district: str
    scheduled_start: datetime
    scheduled_end: datetime
    is_online: bool = False
    meeting_link: Optional[str] = None
    max_capacity: int = 100


class EventRegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    event_id: str
    user_id: str
    attendance_status: str
    registered_at: datetime


class TrainingEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    organizer_org_id: Optional[str] = None
    title: str
    description: str
    event_type: str
    target_crop_id: Optional[str] = None
    district: str
    scheduled_start: datetime
    scheduled_end: datetime
    is_online: bool
    meeting_link: Optional[str] = None
    max_capacity: int
    status: str
    created_at: datetime
