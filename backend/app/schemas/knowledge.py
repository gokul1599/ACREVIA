"""
ACREVIA - KrishiBrain Knowledge, RAG & Citation Schemas.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Knowledge Source Schemas
# -----------------------------------------------------------------------------
class KnowledgeSourceCreateRequest(BaseModel):
    publisher_name: str = Field(..., min_length=2, max_length=150)
    publisher_type: str = Field(default="RESEARCH_COUNCIL", pattern="^(UNIVERSITY|GOVERNMENT_DEPT|RESEARCH_COUNCIL|KVK)$")
    official_domain: str = Field(..., min_length=3, max_length=100)
    authority_level: float = Field(default=1.0, ge=0.1, le=1.0)
    licensing_status: str = Field(default="GOVERNMENT_OPEN_ACCESS")


class KnowledgeSourceUpdateRequest(BaseModel):
    approval_status: Optional[str] = Field(None, pattern="^(PENDING_REVIEW|APPROVED|REJECTED|SUSPENDED|EXPIRED)$")
    authority_level: Optional[float] = Field(None, ge=0.1, le=1.0)
    licensing_status: Optional[str] = None


class KnowledgeSourceResponse(BaseModel):
    id: str
    publisher_name: str
    publisher_type: str
    official_domain: str
    authority_level: float
    licensing_status: str
    approval_status: str
    approved_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# -----------------------------------------------------------------------------
# Knowledge Document Schemas
# -----------------------------------------------------------------------------
class KnowledgeDocumentCreateRequest(BaseModel):
    source_id: str
    title: str = Field(..., min_length=3, max_length=255)
    canonical_url: Optional[str] = None
    document_type: str = Field(default="PDF", pattern="^(PDF|DOCX|HTML|TEXT|MARKDOWN)$")
    primary_language: str = Field(default="en", pattern="^(te|en|hi)$")
    crop_scope: str = Field(default="cotton", pattern="^(cotton|rice|chilli|all)$")
    region_scope: str = Field(default="Telangana")
    topic_scope: Optional[str] = None


class KnowledgeDocumentResponse(BaseModel):
    id: str
    source_id: str
    title: str
    canonical_url: Optional[str] = None
    document_type: str
    primary_language: str
    crop_scope: str
    region_scope: str
    topic_scope: Optional[str] = None
    current_version_id: Optional[str] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# -----------------------------------------------------------------------------
# Ingestion Job Schemas
# -----------------------------------------------------------------------------
class IngestionJobResponse(BaseModel):
    id: str
    document_id: str
    document_version_id: Optional[str] = None
    status: str
    stage: str
    progress_pct: int
    error_message: Optional[str] = None
    attempt_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


# -----------------------------------------------------------------------------
# Citation & Query Schemas
# -----------------------------------------------------------------------------
class CitationResponse(BaseModel):
    source_title: str
    publisher: str
    canonical_url: Optional[str] = None
    document_version: int = 1
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    heading_path: Optional[str] = None
    content_snippet: str
    relevance_score: float


class KnowledgeQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    language: str = Field(default="en", pattern="^(te|en|hi)$")
    crop: Optional[str] = Field(None, pattern="^(cotton|rice|chilli)$")
    growth_stage: Optional[str] = None
    region: Optional[str] = None
    farm_id: Optional[str] = None
    include_citations: bool = True


class KnowledgeQueryResponse(BaseModel):
    query_id: str
    answer_status: str = Field(..., pattern="^(ANSWERED|PARTIALLY_ANSWERED|INSUFFICIENT_EVIDENCE|CONFLICTING_EVIDENCE|REQUIRES_EXPERT_REVIEW)$")
    language: str
    answer: str
    evidence_strength: str = Field(..., pattern="^(STRONG|MODERATE|WEAK|INSUFFICIENT)$")
    citations: List[CitationResponse] = []
    limitations: List[str] = []
    follow_up_questions: List[str] = []
    requires_expert_review: bool = False
    execution_time_ms: float = 0.0


# -----------------------------------------------------------------------------
# Knowledge Feedback Schemas
# -----------------------------------------------------------------------------
class KnowledgeFeedbackCreateRequest(BaseModel):
    query_id: str
    issue_category: str = Field(..., pattern="^(INCORRECT_ANSWER|MISSING_CITATION|INCORRECT_CITATION|OUTDATED_SOURCE|WRONG_CROP|LANGUAGE_QUALITY|UNSAFE_RECOMMENDATION)$")
    user_comments: Optional[str] = None


class KnowledgeFeedbackResponse(BaseModel):
    id: str
    query_id: str
    user_id: Optional[str] = None
    issue_category: str
    user_comments: Optional[str] = None
    reviewer_status: str
    created_at: datetime

    model_config = {"from_attributes": True}
