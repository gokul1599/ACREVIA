"""
ACREVIA - AI Diagnosis & Expert Review Schemas.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DiagnosisCreateRequest(BaseModel):
    observation_id: str
    media_id: Optional[str] = None
    crop_type: str = Field(..., pattern="^(cotton|rice|chilli)$")
    language: str = Field(default="en", pattern="^(te|en|hi)$")


class PredictionCandidateResponse(BaseModel):
    rank: int
    class_id: str
    display_name_en: str
    display_name_te: str
    display_name_hi: str
    pathogen_or_cause: Optional[str] = None
    calibrated_prob: float

    model_config = {"from_attributes": True}


class PredictionResponse(BaseModel):
    id: str
    model_version: str
    decision_state: str
    top_confidence: float
    normalized_entropy: Optional[float] = None
    prediction_margin: Optional[float] = None
    cibrc_advisory: str
    candidates: List[PredictionCandidateResponse] = []

    model_config = {"from_attributes": True}


class ExpertReviewCreateRequest(BaseModel):
    status: str = Field(..., pattern="^(CONFIRMED|OVERRIDDEN)$")
    verified_class_id: str
    expert_notes: Optional[str] = None


class ExpertReviewResponse(BaseModel):
    id: str
    diagnosis_request_id: str
    expert_id: str
    status: str
    verified_class_id: Optional[str] = None
    expert_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DiagnosisResponse(BaseModel):
    id: str
    observation_id: str
    media_id: Optional[str] = None
    status: str
    requested_at: datetime
    completed_at: Optional[datetime] = None
    prediction: Optional[PredictionResponse] = None
    expert_review: Optional[ExpertReviewResponse] = None

    model_config = {"from_attributes": True}
