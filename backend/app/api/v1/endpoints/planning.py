"""
ACREVIA - Crop Planning & Operations API Endpoints (Pillar D: ACREVIA Plan).
Provides access to PJTSAU crop calendars, scheduled operations tasks, and weather conflict mitigation.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.farm import Plot
from backend.app.models.crop_planning import CropCalendarDefinition, CropTask
from backend.app.schemas.crop_planning import (
    CropCalendarDefinitionResponse,
    CropTaskCreate,
    CropTaskUpdate,
    CropTaskCompleteRequest,
    CropTaskResponse,
)
from backend.app.security.dependencies import get_current_user, verify_farm_access
from backend.app.services.crop_planning_service import CropPlanningService

router = APIRouter(prefix="/planning", tags=["Crop Planning"])


@router.get("/calendars", response_model=List[CropCalendarDefinitionResponse])
def list_crop_calendars(
    crop_name: Optional[str] = Query(None, description="e.g. COTTON, RICE, CHILLI"),
    zone: Optional[str] = Query(None, description="e.g. TELANGANA_NORTH_EASTERN"),
    db: Session = Depends(get_db),
):
    """
    Lists PJTSAU package of practice crop calendar definitions.
    """
    calendars = CropPlanningService.list_calendars(crop_name=crop_name, zone=zone, db=db)
    return [
        CropCalendarDefinitionResponse(
            id=c.id,
            crop_id=c.crop_id,
            variety_id=c.variety_id,
            agro_climatic_zone=c.agro_climatic_zone,
            growth_stage=c.growth_stage,
            typical_duration_days=c.typical_duration_days,
            recommended_tasks_json=c.recommended_tasks_json,
            source_citation=c.source_citation,
            version=c.version,
        )
        for c in calendars
    ]


@router.post("/tasks", response_model=CropTaskResponse, status_code=status.HTTP_201_CREATED)
def create_crop_task(
    data: CropTaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates an agricultural operation task with automated weather conflict detection.
    """
    plot = db.get(Plot, data.plot_id)
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plot '{data.plot_id}' not found.",
        )
    verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)
    task = CropPlanningService.create_task(user=current_user, data=data, db=db)
    return CropTaskResponse(
        id=task.id,
        crop_season_id=task.crop_season_id,
        plot_id=task.plot_id,
        calendar_def_id=task.calendar_def_id,
        task_name=task.task_name,
        task_category=task.task_category,
        due_date=task.due_date,
        completed_date=task.completed_date,
        status=task.status,
        weather_conflict_flag=task.weather_conflict_flag,
        conflict_reason=task.conflict_reason,
        execution_details_json=task.execution_details_json,
        notes=task.notes,
        created_at=task.created_at,
    )


@router.get("/tasks", response_model=List[CropTaskResponse])
def list_crop_tasks(
    plot_id: Optional[str] = Query(None),
    crop_season_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lists scheduled crop tasks for a plot or crop season.
    """
    query = db.query(CropTask)
    if plot_id:
        plot = db.get(Plot, plot_id)
        if plot:
            verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)
        query = query.filter(CropTask.plot_id == plot_id)
    if crop_season_id:
        query = query.filter(CropTask.crop_season_id == crop_season_id)

    tasks = query.order_by(CropTask.due_date).all()
    return [
        CropTaskResponse(
            id=t.id,
            crop_season_id=t.crop_season_id,
            plot_id=t.plot_id,
            calendar_def_id=t.calendar_def_id,
            task_name=t.task_name,
            task_category=t.task_category,
            due_date=t.due_date,
            completed_date=t.completed_date,
            status=t.status,
            weather_conflict_flag=t.weather_conflict_flag,
            conflict_reason=t.conflict_reason,
            execution_details_json=t.execution_details_json,
            notes=t.notes,
            created_at=t.created_at,
        )
        for t in tasks
    ]


@router.patch("/tasks/{id}", response_model=CropTaskResponse)
def update_crop_task(
    id: str,
    data: CropTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates schedule or status of a planned crop task.
    """
    task = db.get(CropTask, id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CropTask '{id}' not found.",
        )
    plot = db.get(Plot, task.plot_id)
    if plot:
        verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)

    if data.due_date is not None:
        task.due_date = data.due_date
    if data.status is not None:
        task.status = data.status
    if data.notes is not None:
        task.notes = data.notes

    db.commit()
    db.refresh(task)

    return CropTaskResponse(
        id=task.id,
        crop_season_id=task.crop_season_id,
        plot_id=task.plot_id,
        calendar_def_id=task.calendar_def_id,
        task_name=task.task_name,
        task_category=task.task_category,
        due_date=task.due_date,
        completed_date=task.completed_date,
        status=task.status,
        weather_conflict_flag=task.weather_conflict_flag,
        conflict_reason=task.conflict_reason,
        execution_details_json=task.execution_details_json,
        notes=task.notes,
        created_at=task.created_at,
    )


@router.post("/tasks/{id}/complete", response_model=CropTaskResponse)
def complete_crop_task(
    id: str,
    data: CropTaskCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Marks a crop task as COMPLETED and records operational labor/materials used.
    """
    task = db.get(CropTask, id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CropTask '{id}' not found.",
        )
    plot = db.get(Plot, task.plot_id)
    if plot:
        verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)

    task = CropPlanningService.complete_task(task_id=id, data=data, user=current_user, db=db)
    return CropTaskResponse(
        id=task.id,
        crop_season_id=task.crop_season_id,
        plot_id=task.plot_id,
        calendar_def_id=task.calendar_def_id,
        task_name=task.task_name,
        task_category=task.task_category,
        due_date=task.due_date,
        completed_date=task.completed_date,
        status=task.status,
        weather_conflict_flag=task.weather_conflict_flag,
        conflict_reason=task.conflict_reason,
        execution_details_json=task.execution_details_json,
        notes=task.notes,
        created_at=task.created_at,
    )
