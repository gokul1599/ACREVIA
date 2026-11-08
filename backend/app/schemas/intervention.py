"""
ACREVIA - Agricultural Intervention & Outcome Tracking Schemas.
Data contracts for farm action logging, follow-up evaluations, and timeline comparisons.
"""

from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class InterventionCreateRequest(BaseModel):
    plot_id: str
    category: str = Field(..., pattern="^(BIOLOGICAL|CHEMICAL|CULTURAL|IRRIGATION|FERTILIZER)$")
    trade_name: str = Field(..., min_length=2, max_length=150)
    active_ingredient: Optional[str] = Field(None, max_length=150)
    dosage: float = Field(..., gt=0)
    unit: str = Field("ml/acre", max_length=30)
    application_method: str = Field(..., min_length=2, max_length=100)
    application_date: date
    target_condition: Optional[str] = Field(None, max_length=100)
    phi_days: int = Field(0, ge=0)
    rei_hours: int = Field(24, ge=0)
    notes: Optional[str] = None


class OutcomeObservationCreateRequest(BaseModel):
    follow_up_observation_id: str
    evaluation_date: date
    observed_status: str = Field(..., pattern="^(IMPROVING|STABLE|WORSENING|INCONCLUSIVE)$")
    visual_change_notes: str = Field(..., min_length=5)
    confounding_factors: Optional[str] = None
    farmer_assessment: Optional[str] = None


class OutcomeObservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    intervention_id: str
    follow_up_observation_id: str
    evaluation_date: date
    observed_status: str
    visual_change_notes: str
    confounding_factors: str
    farmer_assessment: Optional[str] = None
    days_post_intervention: int
    created_at: datetime


class InterventionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    plot_id: str
    farm_id: str
    farmer_id: str
    category: str
    trade_name: str
    active_ingredient: Optional[str] = None
    dosage: float
    unit: str
    application_method: str
    application_date: date
    target_condition: Optional[str] = None
    phi_days: int
    rei_hours: int
    notes: Optional[str] = None
    created_at: datetime
    outcomes: List[OutcomeObservationResponse] = Field(default_factory=list)


class InterventionTimelineResponse(BaseModel):
    intervention: InterventionResponse
    outcomes: List[OutcomeObservationResponse] = Field(default_factory=list)
    initial_observation_media: List[dict] = Field(default_factory=list)
    latest_observation_media: List[dict] = Field(default_factory=list)
    confounding_variables_notice: str = (
        "Open-field biological systems are subject to ambient temperature fluctuations, rainfall washout, "
        "and untracked surrounding pest reservoirs. Observed visual changes reflect field progression, not proven single-cause cure."
    )
