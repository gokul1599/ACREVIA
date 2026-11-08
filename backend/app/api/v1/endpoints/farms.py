"""
ACREVIA - Farm Management & Multi-Tenant Boundaries Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.farm import (
    FarmCreateRequest,
    FarmUpdateRequest,
    FarmResponse,
    FarmMembershipCreateRequest,
    FarmMembershipResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.farm_service import FarmService

router = APIRouter(prefix="/farms", tags=["Farms"])


@router.post("/", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
def create_farm(
    data: FarmCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new agricultural farm holding and assigns the creator as OWNER.
    """
    return FarmService.create_farm(user=current_user, data=data, db=db)


@router.get("/", response_model=List[FarmResponse])
def list_farms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists all farms owned by or shared with the authenticated user.
    """
    return FarmService.get_user_farms(user=current_user, db=db)


@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves farm holding details. Rejects cross-tenant access.
    """
    return FarmService.get_farm(farm_id=farm_id, user=current_user, db=db)


@router.put("/{farm_id}", response_model=FarmResponse)
def update_farm(
    farm_id: str,
    data: FarmUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates farm parameters. Requires OWNER or MANAGER permission.
    """
    return FarmService.update_farm(farm_id=farm_id, data=data, user=current_user, db=db)


@router.post("/{farm_id}/memberships", response_model=FarmMembershipResponse, status_code=status.HTTP_201_CREATED)
def add_farm_membership(
    farm_id: str,
    data: FarmMembershipCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Adds a worker or agronomist collaborator to a farm.
    """
    return FarmService.add_farm_membership(
        farm_id=farm_id,
        data=data,
        current_user=current_user,
        db=db
    )


@router.get("/{farm_id}/memberships", response_model=List[FarmMembershipResponse])
def list_farm_memberships(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists collaborators and permissions for a farm holding.
    """
    return FarmService.list_farm_memberships(
        farm_id=farm_id,
        current_user=current_user,
        db=db
    )
