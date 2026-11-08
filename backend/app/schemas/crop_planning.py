"""
ACREVIA - Crop Planning & Operations Pydantic Schemas.
Pillar D: Crop calendars, agricultural tasks, and weather conflict alerts.
"""

from datetime import datetime, date
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CropCalendarDefinitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    crop_id: str
    variety_id: Optional[str] = None
    agro_climatic_zone: str
    growth_stage: str
    typical_duration_days: int
    recommended_tasks: List[Any] = Field(default_factory=list, validation_alias="recommended_tasks_json")
    source_citation: str
    version: str


class CropTaskCreate(BaseModel):
    crop_season_id: str
    plot_id: str
    calendar_def_id: Optional[str] = None
    task_name: str
    task_category: str = "PLANT_PROTECTION"  # LAND_PREP, SOWING, IRRIGATION, FERTILIZATION, PLANT_PROTECTION, HARVEST
    due_date: date
    notes: Optional[str] = None


class CropTaskUpdate(BaseModel):
    due_date: Optional[date] = None
    status: Optional[str] = None  # PLANNED, DUE, IN_PROGRESS, COMPLETED, SKIPPED, RESCHEDULED, CANCELLED
    notes: Optional[str] = None


class CropTaskCompleteRequest(BaseModel):
    actual_date: Optional[date] = None
    labor_hours: Optional[float] = None
    materials_used: List[Dict[str, Any]] = Field(default_factory=list)
    observations: Optional[str] = None


class CropTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    crop_season_id: str
    plot_id: str
    calendar_def_id: Optional[str] = None
    task_name: str
    task_category: str
    due_date: date
    completed_date: Optional[date] = None
    status: str
    weather_conflict_flag: bool
    conflict_reason: Optional[str] = None
    execution_details: Dict[str, Any] = Field(default_factory=dict, validation_alias="execution_details_json")
    notes: Optional[str] = None
    created_at: datetime
