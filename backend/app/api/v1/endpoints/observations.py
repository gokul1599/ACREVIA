"""
ACREVIA - Agricultural Observations & Foliar Image Upload Endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.observation import (
    ObservationCreateRequest,
    ObservationResponse,
    ObservationMediaResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.observation_service import ObservationService

router = APIRouter(prefix="/observations", tags=["Observations & Media"])


@router.post("/", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED)
def create_observation(
    data: ObservationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates an agricultural field observation.
    """
    return ObservationService.create_observation(data=data, current_user=current_user, db=db)


@router.get("/", response_model=List[ObservationResponse])
def list_observations(
    farm_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists historical observations for a specific farm. Enforces tenant boundary.
    """
    return ObservationService.list_farm_observations(
        farm_id=farm_id,
        current_user=current_user,
        db=db,
        limit=limit,
        offset=offset
    )


@router.get("/{observation_id}", response_model=ObservationResponse)
def get_observation(
    observation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves full details of a specific field observation, including attached foliar media.
    """
    return ObservationService.get_observation(
        observation_id=observation_id,
        current_user=current_user,
        db=db
    )


@router.post("/{observation_id}/media", response_model=ObservationMediaResponse, status_code=status.HTTP_201_CREATED)
async def upload_observation_media(
    observation_id: str,
    file: UploadFile = File(...),
    is_primary: bool = Form(default=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Uploads a foliar photograph to an observation.
    Runs automated image quality checks and stores file in private object storage.
    """
    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    mime_type = file.content_type or "image/jpeg"
    return ObservationService.add_media_to_observation(
        observation_id=observation_id,
        file_bytes=content,
        filename=file.filename or "foliar.jpg",
        mime_type=mime_type,
        current_user=current_user,
        db=db,
        is_primary=is_primary
    )


@router.get("/{observation_id}/media/{media_id}/file")
def get_media_file(
    observation_id: str,
    media_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Streams private foliar photograph securely. Requires farm access authorization.
    """
    content, mime_type = ObservationService.get_media_bytes(
        media_id=media_id,
        current_user=current_user,
        db=db
    )
    return Response(content=content, media_type=mime_type)
