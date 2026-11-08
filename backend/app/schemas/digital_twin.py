"""
ACREVIA - Farm Digital Twin Pydantic Schemas.
Pillar A: Digital Twin state representation, provenance records, and completeness metrics.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TwinStateRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    snapshot_id: str
    entity_type: str
    entity_id: str
    property_name: str
    property_value_json: Dict[str, Any]
    unit: Optional[str] = None
    provenance_type: str
    source_reference: Optional[str] = None
    observed_at: datetime
    quality_status: str


class TwinSnapshotSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    twin_id: str
    farm_id: str
    plot_id: Optional[str] = None
    crop_season_id: Optional[str] = None
    snapshot_version: int
    data_completeness_pct: float
    payload_hash: str
    generated_at: datetime
    source_manifest: Dict[str, Any] = Field(default_factory=dict, validation_alias="source_manifest_json")


class TwinSnapshotDetailResponse(TwinSnapshotSummaryResponse):
    state_payload: Dict[str, Any] = Field(default_factory=dict, validation_alias="state_payload_json")
    records: List[TwinStateRecordResponse] = Field(default_factory=list)


class DataCompletenessResponse(BaseModel):
    farm_id: str
    overall_score: float
    dimensions: Dict[str, float]
    missing_critical_fields: List[str]
    recommendations: List[str]


class FarmTwinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    farm_id: str
    twin_version: int
    state_status: str
    last_synchronized_at: datetime
    completeness_score: float
    latest_snapshot: Optional[TwinSnapshotSummaryResponse] = None
    active_plots_count: int = 0


class TwinReconcileResponse(BaseModel):
    twin_id: str
    farm_id: str
    reconciled_events_count: int
    previous_version: int
    current_version: int
    status: str
    timestamp: datetime
