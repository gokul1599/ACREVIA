"""
ACREVIA - Agricultural Knowledge Contribution Endpoints (ACREVIA Commons).
Pillar B: Governed knowledge contributions, expert reviews, translations, and KrishiBrain RAG handoff.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.commons_contribution import (
    KnowledgeContributionCreate,
    KnowledgeContributionResponse,
    ContributionReviewCreate,
    ContributionReviewResponse,
    TranslationVersionCreate,
    TranslationVersionResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.commons_service import CommonsService

router = APIRouter(prefix="/commons", tags=["ACREVIA Commons"])


@router.post("/contributions", response_model=KnowledgeContributionResponse, status_code=status.HTTP_201_CREATED)
def submit_contribution(
    data: KnowledgeContributionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CommonsService.submit_contribution(db, user_id=current_user.id, data=data)


@router.get("/contributions", response_model=List[KnowledgeContributionResponse], status_code=status.HTTP_200_OK)
def list_contributions(
    status_filter: Optional[str] = Query(None, alias="status"),
    crop_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CommonsService.list_contributions(
        db, status_filter=status_filter, crop_id=crop_id, limit=limit, offset=offset
    )


@router.get("/contributions/{contribution_id}", response_model=KnowledgeContributionResponse, status_code=status.HTTP_200_OK)
def get_contribution(
    contribution_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contribution = CommonsService.get_contribution(db, contribution_id=contribution_id)
    if not contribution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge contribution not found",
        )
    return contribution


@router.post("/contributions/{contribution_id}/review", response_model=ContributionReviewResponse, status_code=status.HTTP_201_CREATED)
def review_contribution(
    contribution_id: str,
    data: ContributionReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CommonsService.review_contribution(
        db, contribution_id=contribution_id, expert_user=current_user, data=data
    )


@router.post("/contributions/{contribution_id}/translations", response_model=TranslationVersionResponse, status_code=status.HTTP_201_CREATED)
def create_translation(
    contribution_id: str,
    data: TranslationVersionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CommonsService.create_translation(
        db, contribution_id=contribution_id, user_id=current_user.id, data=data
    )


@router.post("/contributions/{contribution_id}/handoff-krishibrain", response_model=KnowledgeContributionResponse, status_code=status.HTTP_200_OK)
def handoff_to_krishi_brain(
    contribution_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CommonsService.handoff_to_krishi_brain(
        db, contribution_id=contribution_id, admin_or_expert_user=current_user
    )
