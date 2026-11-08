"""
ACREVIA - Agricultural Extension & Learning Endpoints (ACREVIA Extension).
Pillar E: Educational guides, university advisories, interactive training events, and farmer feedback.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.extension_learning import (
    LearningResourceCreate,
    LearningResourceResponse,
    LearningFeedbackCreate,
    LearningFeedbackResponse,
    TrainingEventCreate,
    TrainingEventResponse,
    EventRegistrationResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.extension_service import ExtensionService

router = APIRouter(prefix="/extension", tags=["ACREVIA Extension"])


@router.post("/resources", response_model=LearningResourceResponse, status_code=status.HTTP_201_CREATED)
def publish_learning_resource(
    data: LearningResourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ExtensionService.publish_learning_resource(db, creator_user_id=current_user.id, data=data)


@router.get("/resources", response_model=List[LearningResourceResponse], status_code=status.HTTP_200_OK)
def list_learning_resources(
    crop_id: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ExtensionService.list_learning_resources(
        db, crop_id=crop_id, language=language, resource_type=resource_type, limit=limit, offset=offset
    )


@router.get("/resources/{resource_id}", response_model=LearningResourceResponse, status_code=status.HTTP_200_OK)
def get_learning_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resource = ExtensionService.get_learning_resource(db, resource_id=resource_id, increment_views=True)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning resource not found",
        )
    return resource


@router.post("/resources/{resource_id}/feedback", response_model=LearningFeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    resource_id: str,
    data: LearningFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ExtensionService.submit_feedback(db, resource_id=resource_id, user_id=current_user.id, data=data)


@router.post("/events", response_model=TrainingEventResponse, status_code=status.HTTP_201_CREATED)
def create_training_event(
    data: TrainingEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ExtensionService.create_training_event(db, data=data)


@router.get("/events", response_model=List[TrainingEventResponse], status_code=status.HTTP_200_OK)
def list_training_events(
    district: Optional[str] = Query(None),
    target_crop_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ExtensionService.list_training_events(
        db, district=district, target_crop_id=target_crop_id, status_filter=status_filter, limit=limit, offset=offset
    )


@router.post("/events/{event_id}/register", response_model=EventRegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_for_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ExtensionService.register_for_event(db, event_id=event_id, user_id=current_user.id)
