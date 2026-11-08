"""
KisanVision Inference Service - Response Contracts.
Strictly adheres to the agricultural differential diagnosis output specifications.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CandidatePrediction(BaseModel):
    rank: int = Field(..., ge=1)
    class_id: str
    display_name_en: str
    display_name_te: str
    display_name_hi: str
    pathogen_or_cause: Optional[str] = None
    calibrated_probability: float = Field(..., ge=0.0, le=1.0)
    raw_score: Optional[float] = None


class InferencePredictionResponse(BaseModel):
    """
    Mandatory API response contract for KisanVision ML inference engine.
    """
    request_id: str
    timestamp: str
    status: str = Field(..., description="One of the 8 standardized agricultural decision states")
    crop: str
    predictions: List[CandidatePrediction] = []
    model_score: Optional[float] = Field(default=None, description="Top-1 raw model score")
    calibrated_probability: Optional[float] = Field(default=None, description="Top-1 temperature-calibrated probability")
    uncertainty_status: str
    normalized_entropy: Optional[float] = None
    prediction_margin: Optional[float] = None
    image_quality: Dict[str, Any]
    ood_status: Dict[str, Any]
    model_version: str
    taxonomy_version: str
    preprocessing_version: str
    limitations: List[str] = []
    next_steps: List[str] = []
    safety_guideline: str


class ModelInfoResponse(BaseModel):
    """
    Model information schema.
    """
    model_identifier: str
    model_version: str
    architecture: str
    supported_crops: List[str]
    supported_task: str
    taxonomy_version: str
    preprocessing_version: str
    artifact_status: str
    quantization: str
    inference_provider: str
    device: str
    active_models: Dict[str, Any]
