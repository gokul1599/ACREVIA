"""
ACREVIA - Farmer Collectives & FPO Pydantic Schemas.
Pillar C: Organization registration, verification, membership roles, and privacy-preserving aggregate analytics.
"""

from datetime import date, datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class AgriculturalOrganizationCreate(BaseModel):
    name: str
    org_type: str = "FPO"  # FPO, COOPERATIVE, FARMER_GROUP, TRAINING_GROUP, RESEARCH_PARTICIPANT_GROUP
    registration_number: Optional[str] = None
    state: str = "Telangana"
    district: str
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class AgriculturalOrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str
    org_type: str
    registration_number: Optional[str] = None
    state: str
    district: str
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    verification_status: str
    created_at: datetime


class OrganizationMembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    organization_id: str
    user_id: str
    org_role: str
    is_active: bool
    joined_at: datetime


class CollectiveActivityCreate(BaseModel):
    activity_type: str = "SHARED_CALENDAR"  # SHARED_CALENDAR, TRAINING_SESSION, GROUP_ANNOUNCEMENT, COLLECTIVE_OBSERVATION, RESOURCE_COORDINATION
    title: str
    description: str
    target_date: date


class CollectiveActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    organization_id: str
    created_by_user_id: Optional[str] = None
    activity_type: str
    title: str
    description: str
    target_date: date
    status: str
    created_at: datetime


class CollectiveAggregateAnalytics(BaseModel):
    organization_id: str
    total_member_farms: int
    aggregated_acreage: float
    crop_distribution: Dict[str, float]
    privacy_cohort_status: str  # VALID_COHORT_GE_5 or SUPPRESSED_INSUFFICIENT_COHORT
    notes: str
