"""
ACREVIA - Farmer Collectives & FPO API Endpoints (ACREVIA Collectives).
Pillar C: FPO registration, verification, membership roles, shared activities,
and privacy-preserving aggregate metrics.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.collective import (
    AgriculturalOrganizationCreate,
    AgriculturalOrganizationResponse,
    OrganizationMembershipResponse,
    CollectiveActivityCreate,
    CollectiveActivityResponse,
    CollectiveAggregateAnalytics,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.collectives_service import CollectivesService

router = APIRouter(prefix="/collectives", tags=["ACREVIA Collectives"])


@router.post("/organizations", response_model=AgriculturalOrganizationResponse, status_code=status.HTTP_201_CREATED)
def register_organization(
    data: AgriculturalOrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CollectivesService.register_organization(db, creator_user_id=current_user.id, data=data)


@router.get("/organizations", response_model=List[AgriculturalOrganizationResponse], status_code=status.HTTP_200_OK)
def list_organizations(
    district: Optional[str] = Query(None),
    org_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CollectivesService.list_organizations(db, district=district, org_type=org_type, limit=limit, offset=offset)


@router.get("/organizations/{org_id}", response_model=AgriculturalOrganizationResponse, status_code=status.HTTP_200_OK)
def get_organization(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org = CollectivesService.get_organization(db, org_id=org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agricultural organization not found",
        )
    return org


@router.post("/organizations/{org_id}/verify", response_model=AgriculturalOrganizationResponse, status_code=status.HTTP_200_OK)
def verify_organization(
    org_id: str,
    approve: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CollectivesService.verify_organization(db, org_id=org_id, admin_user=current_user, approve=approve)


@router.post("/organizations/{org_id}/join", response_model=OrganizationMembershipResponse, status_code=status.HTTP_200_OK)
def join_organization(
    org_id: str,
    role: str = Query("MEMBER"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CollectivesService.join_organization(db, org_id=org_id, user_id=current_user.id, org_role=role)


@router.post("/organizations/{org_id}/activities", response_model=CollectiveActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    org_id: str,
    data: CollectiveActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CollectivesService.create_activity(db, org_id=org_id, user_id=current_user.id, data=data)


@router.get("/organizations/{org_id}/activities", response_model=List[CollectiveActivityResponse], status_code=status.HTTP_200_OK)
def list_activities(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CollectivesService.list_activities(db, org_id=org_id, user_id=current_user.id)


@router.get("/organizations/{org_id}/analytics", response_model=CollectiveAggregateAnalytics, status_code=status.HTTP_200_OK)
def get_collective_analytics(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CollectivesService.get_collective_analytics(db, org_id=org_id, user_id=current_user.id)
