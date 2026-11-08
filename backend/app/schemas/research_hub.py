"""
ACREVIA - Agricultural Research Hub Pydantic Schemas.
Pillar D: Research projects, consent management, dataset splits, annotation tasks, and records.
"""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResearchProjectCreate(BaseModel):
    title: str
    institution_name: str
    research_objectives: str
    supported_crops: List[str] = Field(default=["cotton", "rice", "chilli"])
    geographic_scope: str = "Telangana"


class ResearchProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    title: str
    lead_researcher_id: str
    institution_name: str
    research_objectives: str
    supported_crops: List[str] = Field(default_factory=list, validation_alias="supported_crops_json")
    geographic_scope: str

    @field_validator("supported_crops", mode="before")
    @classmethod
    def parse_supported_crops(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        if isinstance(v, list):
            return v
        return []
    project_status: str
    created_at: datetime
    tasks: List[AnnotationTaskResponse] = Field(default_factory=list)


class ResearchConsentCreate(BaseModel):
    consent_scope: str = "ANNOTATED_IMAGES"  # OBSERVATIONS_ONLY, ANNOTATED_IMAGES, SENSOR_DATA, HARVEST_METRICS, FULL_RESEARCH
    consent_version: str = "1.0"


class ResearchConsentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    project_id: str
    farmer_id: str
    consent_scope: str
    is_active: bool
    consent_version: str
    granted_at: datetime
    revoked_at: Optional[datetime] = None


class DatasetContributionCreate(BaseModel):
    project_id: str
    dataset_name: str
    crop_id: str
    sample_count: int = 0
    data_type: str = "CROP_IMAGES"  # CROP_IMAGES, OBSERVATIONS, SENSOR_TELEMETRY
    split_type: str = "TRAIN"  # TRAIN, VALIDATION, TEST
    storage_uri: str
    license: str = "CC_BY_4_0"


class DatasetContributionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    project_id: str
    contributor_id: str
    dataset_name: str
    crop_id: str
    sample_count: int
    data_type: str
    split_type: str
    storage_uri: str
    license: str
    status: str
    created_at: datetime


class AnnotationTaskCreate(BaseModel):
    project_id: str
    assigned_expert_id: Optional[str] = None
    task_type: str = "CROP_CLASSIFICATION"  # CROP_CLASSIFICATION, SYMPTOM_ANNOTATION, IMAGE_QUALITY, GROWTH_STAGE
    entity_reference_id: str


class AnnotationRecordCreate(BaseModel):
    label_taxonomy_version: str = "ACREVIA_TAXONOMY_V1"
    label_assigned: str
    confidence_score: Decimal = Decimal("1.0000")
    notes: Optional[str] = None


class AnnotationRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    task_id: str
    annotator_id: str
    label_taxonomy_version: str
    label_assigned: str
    confidence_score: Decimal
    disagreement_flag: bool
    notes: Optional[str] = None
    submitted_at: datetime


class AnnotationTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    project_id: str
    assigned_expert_id: Optional[str] = None
    task_type: str
    entity_reference_id: str
    status: str
    created_at: datetime
    records: List[AnnotationRecordResponse] = Field(default_factory=list)
