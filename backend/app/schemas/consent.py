"""
ACREVIA - Consent & Audit Governance Schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ConsentCreateRequest(BaseModel):
    consent_type: str = Field(..., pattern="^(CORE_SERVICE|EXPERT_REVIEW|RESEARCH_PARTICIPATION|MODEL_TRAINING)$")
    is_granted: bool = True
    policy_version: str = Field(default="1.0.0")


class ConsentResponse(BaseModel):
    id: str
    user_id: str
    consent_type: str
    is_granted: bool
    policy_version: str
    granted_at: datetime
    revoked_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    farm_id: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime
    metadata_json: Optional[str] = None

    model_config = {"from_attributes": True}
