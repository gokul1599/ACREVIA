"""
KisanVision - Unified Dataset Manifest Schema.
Standardized Pydantic data model for image provenance, metadata, and quality tracking.
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
import uuid


class ImageQualityStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    ACCEPTED_WITH_LIMITATIONS = "ACCEPTED_WITH_LIMITATIONS"
    RETAKE_OR_REVIEW = "RETAKE_OR_REVIEW"
    QUARANTINED = "QUARANTINED"


class AnnotationStatus(str, Enum):
    SOURCE_PROVIDED = "SOURCE_PROVIDED"
    EXPERT_CONFIRMED = "EXPERT_CONFIRMED"
    DISPUTED = "DISPUTED"
    UNKNOWN = "UNKNOWN"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class CollectionContext(str, Enum):
    CONTROLLED_LAB = "CONTROLLED_LAB"
    SHADE_HOUSE = "SHADE_HOUSE"
    OPEN_FIELD = "OPEN_FIELD"
    UNKNOWN = "UNKNOWN"


class ConsentStatus(str, Enum):
    RESEARCH_CONSENT_GRANTED = "RESEARCH_CONSENT_GRANTED"
    DIAGNOSTIC_ONLY = "DIAGNOSTIC_ONLY"
    PUBLIC_OPEN_ACCESS = "PUBLIC_OPEN_ACCESS"
    REVOKED = "REVOKED"


class UnifiedSampleManifest(BaseModel):
    """
    Core manifest record representing a single photographic sample in KisanVision.
    Preserves provenance, legal license, and agronomic metadata without exposing PII.
    """
    sample_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique sample UUID")
    dataset_id: str = Field(..., description="ID of source dataset (e.g., 'ds_plantvillage_v1')")
    source_name: str = Field(..., description="Entity or provider of the image")
    source_url: str = Field(..., description="URL or internal URI of original source")
    license_identifier: str = Field(..., description="SPDX License identifier (e.g., 'CC-BY-4.0', 'MIT')")
    image_path: str = Field(..., description="Relative storage path to the raw image file")
    original_filename: str = Field(..., description="Original filename upon ingestion")
    image_hash: str = Field(..., description="SHA-256 cryptographic digest of raw bytes")
    phash: Optional[str] = Field(None, description="Perceptual hash string for deduplication")
    crop: str = Field(..., description="Target crop: 'cotton', 'rice', 'chilli'")
    variety: Optional[str] = Field(None, description="Cultivar or hybrid name if known")
    original_label: str = Field(..., description="Verbatim raw label from source dataset")
    normalized_label: str = Field(..., description="Standardized KisanVision class ID")
    taxonomy_version: str = Field(default="1.0.0", description="Version of taxonomy applied")
    annotation_status: AnnotationStatus = Field(default=AnnotationStatus.SOURCE_PROVIDED)
    image_quality_status: ImageQualityStatus = Field(default=ImageQualityStatus.ACCEPTED)
    collection_context: CollectionContext = Field(default=CollectionContext.OPEN_FIELD)
    capture_date: Optional[str] = Field(None, description="ISO-8601 capture timestamp")
    plant_id: Optional[str] = Field(None, description="Unique identifier for the physical plant")
    farm_group_id: str = Field(..., description="Grouping key for leakage-free splitting")
    consent_status: ConsentStatus = Field(default=ConsentStatus.PUBLIC_OPEN_ACCESS)
    dataset_version: str = Field(default="v0.1.0-alpha", description="Dataset release version")
    quality_metrics: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Blur, exposure, and dimension stats")

    model_config = ConfigDict(use_enum_values=True, extra="allow")
