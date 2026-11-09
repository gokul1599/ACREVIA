"""
ACREVIA - FastAPI Security Dependencies.
Enforces JWT authentication, role-based access control, and tenant farm ownership.
"""

from typing import List, Optional, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.security import decode_access_token
from backend.app.core.exceptions import AuthenticationException, AuthorizationException
from backend.app.database.session import get_db
from backend.app.database.rls import set_tenant_context
from backend.app.models.user import User
from backend.app.models.farm import Farm, FarmMembership
from backend.app.security.permissions import SystemRole, FarmRole

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False
)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Validates JWT bearer token and retrieves active User record from database.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Invalid token payload: missing subject.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or does not exist.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Set user context in database session for RLS / audit isolation
    user_roles = [r.id for r in user.roles]
    is_admin = SystemRole.ADMIN.value in user_roles
    set_tenant_context(db, tenant_id=None, user_id=user.id, is_admin=is_admin)

    return user


def require_roles(*allowed_roles: str) -> Callable:
    """
    Dependency factory verifying that the authenticated user possesses at least
    one of the specified system roles (or is an ADMIN).
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_roles = [r.id for r in current_user.roles]
        if SystemRole.ADMIN.value in user_roles:
            return current_user  # Superuser bypass

        for role in allowed_roles:
            if role in user_roles:
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Operation requires one of the following roles: {allowed_roles}"
        )

    return role_checker


def verify_farm_access(
    farm_id: str,
    user: User,
    db: Session,
    allowed_farm_roles: Optional[List[str]] = None
) -> Farm:
    """
    Validates whether the user is authorized to read/modify the specified farm.
    Blocks cross-farm unauthorized access attempts.
    """
    user_roles = [r.id for r in user.roles]
    farm = db.get(Farm, farm_id)
    if not farm or farm.is_archived:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with identifier '{farm_id}' was not found."
        )

    # 1. Superuser override
    if SystemRole.ADMIN.value in user_roles:
        set_tenant_context(db, tenant_id=farm_id, user_id=user.id, is_admin=True)
        return farm

    # 2. Primary Farm Owner
    if farm.owner_id == user.id:
        set_tenant_context(db, tenant_id=farm_id, user_id=user.id, is_admin=False)
        return farm

    # 3. Active Farm Membership
    membership = (
        db.query(FarmMembership)
        .filter(
            FarmMembership.farm_id == farm_id,
            FarmMembership.user_id == user.id
        )
        .first()
    )

    if membership:
        if allowed_farm_roles:
            if membership.role_in_farm in allowed_farm_roles:
                set_tenant_context(db, tenant_id=farm_id, user_id=user.id, is_admin=False)
                return farm
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action requires one of farm roles: {allowed_farm_roles}, but user has '{membership.role_in_farm}'."
            )
        set_tenant_context(db, tenant_id=farm_id, user_id=user.id, is_admin=False)
        return farm

    # 4. Cross-Farm Access Denied
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access to requested farm is forbidden: you are not an owner or member."
    )
