"""
ACREVIA - Multi-Source Evidence Fusion Pydantic Schemas.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict


class MultilingualText(BaseModel):
    en: str
    te: str
    hi: str


class FusionContradiction(BaseModel):
    conflict_type: str
    description: str
    resolution: str


class FusionExplanationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    plot_id: str
    evaluation_timestamp: datetime
    overall_vigor_status: str
    primary_stress_driver: str
    evidence_sources: Dict[str, Any]
    contradictions_detected: List[FusionContradiction]
    farmer_explanation: MultilingualText
    epistemic_qualifications: Dict[str, Any]
