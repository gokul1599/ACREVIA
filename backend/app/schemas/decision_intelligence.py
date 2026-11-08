"""
ACREVIA - Agricultural Decision Intelligence Pydantic Schemas.
Pillar E: Grounded multilingual recommendations, evidence references, and farmer feedback.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DecisionAnalyzeRequest(BaseModel):
    plot_id: str
    query_text: str
    decision_category: str = "IRRIGATION_SCHEDULING"  # IRRIGATION_SCHEDULING, PEST_MANAGEMENT, FERTILIZER_APPLICATION, HARVEST_WINDOW


class EvidenceSourceItem(BaseModel):
    source_title: str
    chapter: Optional[str] = None
    chunk_id: Optional[str] = None
    citation: Optional[str] = None


class DecisionRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    plot_id: str
    query_text: str
    decision_category: str
    recommendation_state: str  # INFORMATIONAL, EVIDENCE_SUPPORTED, SCENARIO_RESULT, REQUIRES_MORE_INFORMATION, REQUIRES_EXPERT_REVIEW, INSUFFICIENT_EVIDENCE, NOT_SUPPORTED
    grounded_explanation_en: str
    grounded_explanation_te: str
    grounded_explanation_hi: str
    evidence_sources: List[EvidenceSourceItem] = Field(default_factory=list, validation_alias="evidence_sources_json")
    uncertainty_disclosures: List[str] = Field(default_factory=list, validation_alias="uncertainty_disclosures_json")
    expert_escalation_case_id: Optional[str] = None
    evaluated_at: datetime


class DecisionFeedbackCreate(BaseModel):
    farmer_action_taken: str  # ADOPTED, PARTIALLY_ADOPTED, REJECTED, INAPPLICABLE
    farmer_rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_notes: Optional[str] = None
    observed_outcome: Optional[str] = None


class DecisionFeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    decision_id: str
    farmer_action_taken: str
    farmer_rating: Optional[int] = None
    feedback_notes: Optional[str] = None
    observed_outcome: Optional[str] = None
    recorded_at: datetime
