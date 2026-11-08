"""
KisanVision Inference Service - Request Schemas.
"""

from typing import Optional
from pydantic import BaseModel, Field


class DiagnosticContext(BaseModel):
    crop_type: str = Field(..., description="Target crop: cotton, rice, or chilli")
    language: str = Field(default="en", description="Response language: te, en, or hi")
    farm_id: Optional[str] = Field(default=None, description="Optional tenant farm ID")
    plot_id: Optional[str] = Field(default=None, description="Optional crop plot ID")
