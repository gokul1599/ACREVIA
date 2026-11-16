"""
ACREVIA - Regional Pulse & Intelligence Pydantic Schemas.
Pillar F: Privacy-preserving regional signal aggregation, evidence links, and outbreak suppression.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, model_validator


class RegionalSignalEvidenceItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    evidence_type: str
    evidence_reference_id: str
    evidence_notes: Optional[str] = None
    added_at: datetime


class RegionalSignalEvidenceCreateItem(BaseModel):
    evidence_type: str = "OBSERVATION_REF"
    evidence_reference_id: str = Field(..., max_length=100)
    evidence_notes: Optional[str] = None


class RegionalSignalCreate(BaseModel):
    district: str
    state: str = "Telangana"
    crop_id: str
    signal_category: str = "OBSERVATION_SURGE"  # OBSERVATION_SURGE, WEATHER_EXPOSURE, PEST_INQUIRIES, ADVISORY_ALERT, SATELLITE_VEGETATION_CHANGE
    signal_title: str = Field(..., max_length=200)
    signal_summary: str
    confidence_tier: str = "FARMER_REPORT"  # FARMER_REPORT, MULTIPLE_INDEPENDENT, AI_ASSISTED, EXPERT_REVIEWED, OFFICIAL_ADVISORY
    source_observation_count: int = Field(1, ge=0)
    distinct_farms_count: int = Field(1, ge=0)
    validation_status: str = "UNVALIDATED_OBSERVATION"  # UNVALIDATED_OBSERVATION, EXPERT_CONFIRMED, OFFICIAL_ALERT
    recommended_action: str
    observed_start_date: date
    observed_end_date: date
    evidences: Optional[List[Union[RegionalSignalEvidenceCreateItem, Dict[str, Any]]]] = None

    @model_validator(mode="after")
    def validate_date_ordering(self) -> "RegionalSignalCreate":
        if self.observed_start_date > self.observed_end_date:
            raise ValueError(
                f"observed_start_date ({self.observed_start_date}) must be before or equal to "
                f"observed_end_date ({self.observed_end_date})"
            )
        return self


class RegionalSignalRecoverRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=500, description="Justification or evidence notes for signal recovery")


class RegionalSignalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    district: str
    state: str
    crop_id: str
    signal_category: str
    signal_title: str
    signal_summary: str
    confidence_tier: str
    source_observation_count: int
    distinct_farms_count: int
    is_outbreak_claim_suppressed: bool
    validation_status: str
    recommended_action: str
    observed_start_date: date
    observed_end_date: date
    created_at: datetime
    evidences: List[RegionalSignalEvidenceItem] = Field(default_factory=list)
