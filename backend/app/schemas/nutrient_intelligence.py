"""
ACREVIA - Nutrient Intelligence & Governance Pydantic Schemas.
Pillar D: Soil-test-driven N-P-K & micronutrient prescriptions, split schedules, and agronomist escalations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class NutrientPrescribeRequest(BaseModel):
    soil_test_result_id: str
    crop_id: str
    yield_target_quintals_per_acre: Optional[float] = 12.0
    override_n_kg_ha: Optional[float] = None  # Tested against safeguards


class SplitScheduleItem(BaseModel):
    stage: str
    n_kg: float
    p2o5_kg: float
    k2o_kg: float
    timing: str


class NutrientAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    soil_test_result_id: str
    crop_id: str
    crop_name: Optional[str] = "Crop"
    nitrogen_status: str
    phosphorus_status: str
    potassium_status: str
    zinc_status: str
    boron_status: str
    recommended_n_kg_ha: float
    recommended_p2o5_kg_ha: float
    recommended_k2o_kg_ha: float
    split_application_schedule_json: str
    micronutrient_recommendations_json: str
    safeguard_checks_passed: bool
    institutional_citation: str
    created_at: datetime


class NutrientExpertReviewRequest(BaseModel):
    nutrient_assessment_id: str
    review_status: str = "APPROVED"  # APPROVED, MODIFIED, REJECTED
    agronomist_notes: str
    revised_prescription: Optional[Dict[str, Any]] = None


class NutrientExpertReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    nutrient_assessment_id: str
    expert_user_id: str
    review_status: str
    agronomist_notes: str
    revised_prescription_json: Optional[str] = None
    reviewed_at: datetime
