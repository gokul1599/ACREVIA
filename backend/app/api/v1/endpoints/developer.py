"""
ACREVIA - Developer Portal & Scoped API Credentials Endpoints.
Stage 14: API applications, SHA-256 hashed keys, scope enforcement, and sandbox isolation.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.interoperability import (
    ApiApplicationCreate,
    ApiApplicationResponse,
    ApiCredentialCreate,
    ApiCredentialCreatedResponse,
    ApiCredentialResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.developer_service import DeveloperService

router = APIRouter(prefix="/developer", tags=["ACREVIA Developer"])


@router.post("/applications", response_model=ApiApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    request: ApiApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Registers a third-party or sandbox API application.
    """
    app = DeveloperService.create_application(
        db=db,
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        partner_id=request.partner_id,
        is_sandbox=request.is_sandbox,
        redirect_uris=request.redirect_uris,
    )
    return app


@router.get("/applications", response_model=List[ApiApplicationResponse], status_code=status.HTTP_200_OK)
def list_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return DeveloperService.list_applications(db=db, user_id=current_user.id)


@router.get("/applications/{app_id}", response_model=ApiApplicationResponse, status_code=status.HTTP_200_OK)
def get_application(
    app_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app = DeveloperService.get_application(db=db, app_id=app_id, user_id=current_user.id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return app


@router.post("/applications/{app_id}/credentials", response_model=ApiCredentialCreatedResponse, status_code=status.HTTP_201_CREATED)
def generate_api_credential(
    app_id: str,
    request: ApiCredentialCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generates scoped client credentials with client_id and plaintext client_secret.
    NOTE: The client_secret is returned ONLY ONCE in this response.
    """
    try:
        cred, plaintext_secret = DeveloperService.create_credential(
            db=db,
            application_id=app_id,
            user_id=current_user.id,
            scopes=request.scopes,
            rate_limit_per_minute=request.rate_limit_per_minute,
            expires_in_days=request.expires_in_days or 365,
        )
        return ApiCredentialCreatedResponse(
            id=cred.id,
            application_id=cred.application_id,
            client_id=cred.client_id,
            secret_prefix=cred.secret_prefix,
            scopes_json=cred.scopes_json,
            rate_limit_per_minute=cred.rate_limit_per_minute,
            is_active=cred.is_active,
            expires_at=cred.expires_at,
            last_used_at=cred.last_used_at,
            created_at=cred.created_at,
            client_secret=plaintext_secret,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/credentials/{cred_id}", response_model=ApiCredentialResponse, status_code=status.HTTP_200_OK)
def revoke_api_credential(
    cred_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Immediately revokes an active API credential.
    """
    try:
        cred = DeveloperService.revoke_credential(db=db, credential_id=cred_id, user_id=current_user.id)
        return cred
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
