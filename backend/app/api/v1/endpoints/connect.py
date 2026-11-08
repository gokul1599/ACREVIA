"""
ACREVIA - Agricultural Collaboration & Community Endpoints (ACREVIA Connect).
Pillar A: Community spaces, posts, comments with expert reply badge, helpful voting, and moderation reporting.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.community import (
    CommunityResponse,
    CommunityMembershipResponse,
    CommunityPostCreate,
    CommunityPostResponse,
    CommunityCommentCreate,
    CommunityCommentResponse,
    CommunityReportCreate,
    CommunityReportResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.connect_service import ConnectService

router = APIRouter(prefix="/connect", tags=["ACREVIA Connect"])


@router.get("/communities", response_model=List[CommunityResponse], status_code=status.HTTP_200_OK)
def list_communities(
    category: Optional[str] = Query(None),
    crop_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ConnectService.seed_default_communities(db)
    return ConnectService.list_communities(db, category=category, crop_id=crop_id)


@router.post("/communities/{community_id}/join", response_model=CommunityMembershipResponse, status_code=status.HTTP_200_OK)
def join_community(
    community_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ConnectService.join_community(db, community_id=community_id, user_id=current_user.id)


@router.post("/communities/{community_id}/posts", response_model=CommunityPostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    community_id: str,
    data: CommunityPostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ConnectService.create_post(db, community_id=community_id, user_id=current_user.id, data=data)


@router.get("/communities/{community_id}/posts", response_model=List[CommunityPostResponse], status_code=status.HTTP_200_OK)
def list_community_posts(
    community_id: str,
    post_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ConnectService.list_posts(db, community_id=community_id, post_type=post_type, limit=limit, offset=offset)


@router.post("/posts/{post_id}/comments", response_model=CommunityCommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    post_id: str,
    data: CommunityCommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ConnectService.add_comment(db, post_id=post_id, user=current_user, data=data)


@router.post("/posts/{post_id}/helpful", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def vote_helpful(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = ConnectService.vote_helpful(db, post_id=post_id, user_id=current_user.id)
    return {
        "post_id": post_id,
        "helpful_count": post.helpful_count,
        "message": "Vote recorded. Note: Community appreciation does not constitute scientific agronomic validation.",
    }


@router.post("/report", response_model=CommunityReportResponse, status_code=status.HTTP_201_CREATED)
def report_content(
    data: CommunityReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ConnectService.report_content(db, user_id=current_user.id, data=data)
