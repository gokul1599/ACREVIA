"""
ACREVIA - Authentication & Identity Endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
)
from backend.app.services.auth_service import AuthService
from backend.app.security.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Registers a new user account with secure password hashing.
    """
    return AuthService.register_user(db=db, req=data)


@router.post("/login", response_model=TokenResponse)
def login(
    data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticates user credentials and returns JWT bearer tokens.
    """
    return AuthService.authenticate_user(db=db, req=data)


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Returns the profile and role assignments of the currently authenticated user.
    """
    return current_user
