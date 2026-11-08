"""
KisanVision API - Vision Schemas.
Pydantic contracts for crop foliar diagnosis, image quality assessment,
differential diagnoses, and agricultural safety advisories.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DifferentialCandidate(BaseModel):
    """Candidate diagnosis in differential analysis with multi-lingual support."""
    rank: int = Field(..., ge=1, le=5)
    class_id: str
    display_name_en: str
    display_name_te: str
    display_name_hi: str
    pathogen_or_cause: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)


class ImageQualityAssessment(BaseModel):
    """Technical quality evaluation of the uploaded foliar image."""
    status: str = Field(..., description="ACCEPTED, RETAKE_OR_REVIEW, or QUARANTINED")
    is_acceptable: bool
    sharpness_score: float
    exposure_status: str
    corrective_guidance: List[str] = []


class FoliarVegetationAssessment(BaseModel):
    """Tier 1 OOD check validating presence of natural plant foliar tissue."""
    is_foliar: bool
    foliar_pixel_ratio: float
    contrast_std: float
    validation_reason: str


class VisionDiagnosisResponse(BaseModel):
    """Comprehensive diagnostic response payload for smallholder farmers and agronomists."""
    request_id: str
    timestamp: str
    crop_type: str
    status: str = Field(..., description="CONFIRMED_DIAGNOSIS, UNCERTAIN_AMBIGUOUS, LOW_CONFIDENCE, QUALITY_REJECTED, OOD_NON_PLANT")
    triage_level: str = Field(..., description="IMMEDIATE_ACTION, MONITOR, EXPERT_REVIEW_RECOMMENDED, RETAKE_IMAGE")
    primary_diagnosis: Optional[DifferentialCandidate] = None
    differential_candidates: List[DifferentialCandidate] = []
    normalized_entropy: Optional[float] = None
    prediction_margin: Optional[float] = None
    image_quality: ImageQualityAssessment
    foliar_assessment: Optional[FoliarVegetationAssessment] = None
    safety_guideline: str
    expert_review_recommended: bool = False
    message: str


class ModelInfoResponse(BaseModel):
    """Metadata regarding active vision inference backbones and quantization status."""
    crop_type: str
    architecture: str
    num_classes: int
    quantization: str
    engine_provider: str
    model_size_mb: float
    inference_device: str
    status: str
