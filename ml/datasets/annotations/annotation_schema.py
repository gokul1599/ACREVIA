"""
KisanVision - Annotation & Expert Review Data Schemas.
Enforces multi-tier provenance, auditability, and double-blind agronomist reviews.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timezone


class DiagnosticCertainty(str, Enum):
    CERTAIN = "CERTAIN"
    PROBABLE = "PROBABLE"
    INCONCLUSIVE = "INCONCLUSIVE"


class ReviewAction(str, Enum):
    CONFIRMED = "CONFIRMED"
    OVERRIDDEN = "OVERRIDDEN"
    DISPUTED = "DISPUTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    REJECTED_QUALITY = "REJECTED_QUALITY"


class LabelRevisionEntry(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    previous_label: Optional[str] = None
    new_label: str
    changed_by_role: str  # "SOURCE_IMPORT", "EXPERT_REVIEWER", "SENIOR_PANEL"
    reason: str


class ExpertReviewRecord(BaseModel):
    review_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sample_id: str = Field(..., description="Foreign key to sample manifest")
    expert_id_hash: str = Field(..., description="Anonymized ID of university reviewer")
    candidate_class: str = Field(..., description="Proposed label prior to review")
    confirmed_class: str = Field(..., description="Verified canonical class")
    action_taken: ReviewAction
    certainty: DiagnosticCertainty
    evidence_notes: str = Field(..., description="Botanical and pathological diagnostic rationale")
    microscope_verified: bool = Field(default=False)
    reviewed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ComprehensiveAnnotation(BaseModel):
    sample_id: str
    crop: str
    crop_stage: Optional[str] = None
    farmer_reported_observation: Optional[str] = None
    source_dataset_label: str
    ai_predicted_label: Optional[str] = None
    ai_confidence: Optional[float] = None
    expert_confirmed_label: Optional[str] = None
    final_approved_training_label: Optional[str] = None
    is_approved_for_training: bool = False
    reviews: List[ExpertReviewRecord] = Field(default_factory=list)
    revision_history: List[LabelRevisionEntry] = Field(default_factory=list)
