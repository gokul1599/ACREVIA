"""
ACREVIA - ExpertConnect Pydantic Schemas.
Data contracts for expert onboarding, verification, case review dossiers, and assessments.
"""

from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ExpertApplicationRequest(BaseModel):
    registration_number: Optional[str] = None
    highest_degree: str = Field(..., min_length=2, max_length=100)
    institution: str = Field(..., min_length=2, max_length=150)
    specializations: List[str] = Field(default_factory=lambda: ["COTTON", "RICE", "CHILLI"])
    districts_covered: List[str] = Field(default_factory=lambda: ["Warangal", "Khammam", "Karimnagar"])


class ExpertProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    full_name: str
    email: Optional[str] = None
    phone: str
    registration_number: Optional[str] = None
    highest_degree: str
    institution: str
    specializations: List[str] = Field(default_factory=list)
    districts_covered: List[str] = Field(default_factory=list)
    verification_status: str
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None


class AdminVerifyExpertRequest(BaseModel):
    decision: str = Field(..., pattern="^(APPROVED|REJECTED|SUSPENDED)$")
    rejection_reason: Optional[str] = None


class ExpertCaseItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    observation_id: str
    farm_id: str
    farm_name: str
    district: str
    plot_id: Optional[str] = None
    crop_id: str
    priority: str
    status: str
    assigned_expert_id: Optional[str] = None
    assigned_expert_name: Optional[str] = None
    created_at: datetime


class ExpertCaseDossierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: str
    observation_id: str
    farm_id: str
    farm_name: str
    district: str
    plot_id: Optional[str] = None
    plot_name: Optional[str] = None
    crop_id: str
    growth_stage: Optional[str] = None
    priority: str
    status: str
    assigned_expert_id: Optional[str] = None
    assigned_expert_name: Optional[str] = None
    
    # Evidence Dossier
    farmer_notes: Optional[str] = None
    symptom_tags: Optional[str] = None
    foliar_media: List[dict] = Field(default_factory=list)
    ai_prediction: Optional[dict] = None
    krishi_brain_citations: List[dict] = Field(default_factory=list)
    weather_context: Optional[dict] = None
    
    assessment: Optional[Any] = None
    created_at: datetime


class ExpertAssessmentCreateRequest(BaseModel):
    confirmed_crop: str = Field(..., min_length=2, max_length=50)
    primary_condition: str = Field(..., min_length=2, max_length=100)
    differential_diagnoses: List[str] = Field(default_factory=list)
    confidence_rating: int = Field(..., ge=1, le=5)
    urgency_level: str = Field("ROUTINE", pattern="^(LOW|ROUTINE|HIGH|EMERGENCY)$")
    management_plan: str = Field(..., min_length=10)
    ipm_strategy: str = Field(..., min_length=10)
    cibrc_advisories: str = Field(..., min_length=10)


class ExpertAssessmentRevisionRequest(BaseModel):
    confirmed_crop: str = Field(..., min_length=2, max_length=50)
    primary_condition: str = Field(..., min_length=2, max_length=100)
    differential_diagnoses: List[str] = Field(default_factory=list)
    confidence_rating: int = Field(..., ge=1, le=5)
    urgency_level: str = Field("ROUTINE", pattern="^(LOW|ROUTINE|HIGH|EMERGENCY)$")
    management_plan: str = Field(..., min_length=10)
    ipm_strategy: str = Field(..., min_length=10)
    cibrc_advisories: str = Field(..., min_length=10)
    revision_reason: str = Field(..., min_length=5)


class ExpertAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    expert_id: str
    expert_name: str
    expert_degree: str
    expert_institution: str
    confirmed_crop: str
    primary_condition: str
    differential_diagnoses: List[str] = Field(default_factory=list)
    confidence_rating: int
    urgency_level: str
    management_plan: str
    ipm_strategy: str
    cibrc_advisories: str
    revision_count: int
    created_at: datetime
    updated_at: datetime


class ExpertAssessmentRevisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    assessment_id: str
    revision_number: int
    previous_assessment: dict
    revision_reason: str
    revised_by_user_id: str
    revised_by_name: str
    revised_at: datetime
