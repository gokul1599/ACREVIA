"""
ACREVIA - Agricultural Data Exchange Schemas.
Stage 14: Data Export, Data Import, Conflict Tracking, Cryptographic Manifests, and Mapping Profiles.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DataExportRequest(BaseModel):
    farm_id: Optional[str] = None
    categories: List[str] = Field(
        default=["ALL"],
        description="Categories: ALL, FARM_PROFILE, SOIL_HEALTH, WATER_RESOURCES, OBSERVATIONS, DIAGNOSTICS, HARVEST_YIELD, FINANCIAL_LEDGER"
    )
    format: str = Field("JSON", description="JSON, CSV, GEOJSON, ARCHIVE")
    redact_pii: bool = Field(True, description="Anonymize farmer personal identifying information")
    redact_gps: bool = Field(True, description="Mask exact coordinates to district/mandal centroids")


class DataImportRequest(BaseModel):
    farm_id: Optional[str] = None
    format: str = Field("JSON", description="JSON, CSV, GEOJSON")
    target_category: str = Field("SOIL_TESTS", description="SOIL_TESTS, OBSERVATIONS, MARKET_PRICES, HARVEST_RECORDS")
    data_payload: str = Field(..., description="Stringified JSON array or CSV text data")
    mapping_profile_id: Optional[str] = None
    preserve_conflicts: bool = Field(True, description="Never overwrite existing data; mark conflicts for audit")


class DataExchangeJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    user_id: str
    farm_id: Optional[str] = None
    job_type: str
    format: str
    categories_json: str
    status: str
    records_processed: int
    records_failed: int
    conflicts_detected: int
    manifest_json: str
    checksum_sha256: Optional[str] = None
    error_message: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime


class DataMappingProfileCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    source_format: str = Field(..., description="CUSTOM_CSV, AGMIST_EXPORT, SOIL_HEALTH_CARD_CSV, IOT_JSON")
    target_entity: str = Field(..., description="SOIL_SAMPLE, PLOT_OBSERVATION, HARVEST_RECORD, MARKET_PRICE")
    mapping_rules: Dict[str, str] = Field(..., description="Dictionary mapping source field names to canonical field names")


class DataMappingProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    user_id: str
    name: str
    source_format: str
    target_entity: str
    mapping_rules_json: str
    created_at: datetime
