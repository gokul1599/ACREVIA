"""
ACREVIA - Authentication & User Schemas.
"""

from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator


class UserRegisterRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$", description="E.164 phone number, e.g. +919876543210 or 9876543210")
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    email: Optional[EmailStr] = None
    language_preference: str = Field(default="te", pattern="^(te|en|hi)$")
    role: str = Field(default="FARMER", pattern="^(FARMER|AGRICULTURAL_EXPERT|RESEARCHER)$")


class UserLoginRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=1)


class UserSummaryResponse(BaseModel):
    id: str
    phone: str
    email: Optional[str] = None
    full_name: str
    language_preference: str
    is_active: bool
    is_verified: bool
    roles: List[str] = []

    @field_validator("roles", mode="before")
    @classmethod
    def extract_role_ids(cls, v: Any) -> List[str]:
        if isinstance(v, list):
            return [getattr(item, "id", str(item)) for item in v]
        return v

    model_config = {"from_attributes": True}


UserResponse = UserSummaryResponse


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: UserSummaryResponse
