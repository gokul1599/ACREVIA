"""
ACREVIA - Agricultural Research Hub API Endpoints (ACREVIA Research Hub).
Pillar D: Research projects, consent management, dataset splits, annotation tasks, and records.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.research_hub import (
    ResearchProjectCreate,
    ResearchProjectResponse,
    ResearchConsentCreate,
    ResearchConsentResponse,
    DatasetContributionCreate,
    DatasetContributionResponse,
    AnnotationTaskCreate,
    AnnotationTaskResponse,
    AnnotationRecordCreate,
    AnnotationRecordResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.research_service import ResearchService

router = APIRouter(prefix="/research", tags=["ACREVIA Research Hub"])


@router.post("/projects", response_model=ResearchProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ResearchProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ResearchService.create_project(db, lead_researcher_id=current_user.id, data=data)


@router.get("/projects", response_model=List[ResearchProjectResponse], status_code=status.HTTP_200_OK)
def list_projects(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ResearchService.list_projects(db, status_filter=status_filter, limit=limit, offset=offset)


@router.get("/projects/{project_id}", response_model=ResearchProjectResponse, status_code=status.HTTP_200_OK)
def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = ResearchService.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research project not found",
        )
    return project


@router.post("/projects/{project_id}/consent", response_model=ResearchConsentResponse, status_code=status.HTTP_201_CREATED)
def grant_research_consent(
    project_id: str,
    data: ResearchConsentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ResearchService.grant_research_consent(
        db, farmer_user_id=current_user.id, project_id=project_id, data=data
    )


@router.post("/consents/{consent_id}/revoke", response_model=ResearchConsentResponse, status_code=status.HTTP_200_OK)
def revoke_research_consent(
    consent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ResearchService.revoke_research_consent(
        db, consent_id=consent_id, farmer_user=current_user
    )


@router.post("/datasets", response_model=DatasetContributionResponse, status_code=status.HTTP_201_CREATED)
def contribute_dataset(
    data: DatasetContributionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ResearchService.contribute_dataset(db, contributor_id=current_user.id, data=data)


@router.post("/annotation-tasks", response_model=AnnotationTaskResponse, status_code=status.HTTP_201_CREATED)
def create_annotation_task(
    data: AnnotationTaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ResearchService.create_annotation_task(db, data=data)


@router.post("/annotation-tasks/{task_id}/records", response_model=AnnotationRecordResponse, status_code=status.HTTP_201_CREATED)
def submit_annotation_record(
    task_id: str,
    data: AnnotationRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ResearchService.submit_annotation_record(
        db, task_id=task_id, annotator_id=current_user.id, data=data
    )
