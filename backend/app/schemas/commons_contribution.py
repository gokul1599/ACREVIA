"""
ACREVIA - Agricultural Knowledge Contribution Pydantic Schemas.
Pillar B: Governed knowledge submissions, expert review transitions, and translations.
"""

import json
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class KnowledgeContributionCreate(BaseModel):
    contribution_type: str = "EXPLANATION"  # EXPLANATION, TERMINOLOGY, OBSERVATION, EXPERT_ARTICLE, ADVISORY, TRANSLATION_CORRECTION
    title: str
    description: str
    original_language: str = "en"
    crop_id: Optional[str] = None
    geographic_scope: str = "Telangana"
    growth_stage: Optional[str] = None
    evidence_references: List[str] = Field(default_factory=list)
    usage_permission: str = "CC_BY_SA_4_0"


class ContributionReviewCreate(BaseModel):
    decision: str = "APPROVE"  # APPROVE, REJECT, REQUEST_REVISION
    comments: str
    scientific_rating: int = 5
    safety_assessment: Optional[str] = None


class ContributionReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    contribution_id: str
    reviewer_id: str
    reviewer_role: str
    decision: str
    comments: str
    scientific_rating: int
    safety_assessment: Optional[str] = None
    reviewed_at: datetime


class TranslationVersionCreate(BaseModel):
    target_language: str  # te, en, hi
    translated_title: str
    translated_content: str


class TranslationVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    contribution_id: str
    target_language: str
    translated_title: str
    translated_content: str
    is_native_reviewed: bool
    reviewer_id: Optional[str] = None
    created_at: datetime


class KnowledgeContributionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    contributor_id: str
    contribution_type: str
    title: str
    description: str
    original_language: str
    crop_id: Optional[str] = None
    geographic_scope: str
    growth_stage: Optional[str] = None
    evidence_references: List[str] = Field(default_factory=list, validation_alias="evidence_references_json")
    usage_permission: str

    @field_validator("evidence_references", mode="before")
    @classmethod
    def parse_evidence_references(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        if isinstance(v, list):
            return v
        return []
    status: str
    assigned_expert_id: Optional[str] = None
    approved_by_user_id: Optional[str] = None
    krishi_brain_ingested: bool
    krishi_brain_doc_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    reviews: List[ContributionReviewResponse] = Field(default_factory=list)
    translations: List[TranslationVersionResponse] = Field(default_factory=list)
