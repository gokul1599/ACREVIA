"""
ACREVIA - Authentication & Identity Service.
Handles user registration, credential verification, and JWT issuance.
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.core.config import settings
from backend.app.core.exceptions import ConflictException, AuthenticationException
from backend.app.models.user import User, Role
from backend.app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserSummaryResponse
from backend.app.services.audit_service import audit_service


class AuthService:
    @staticmethod
    def register_user(db: Session, req: UserRegisterRequest) -> UserSummaryResponse:
        """Registers a new user and assigns requested system role."""
        # 1. Duplicate phone check
        existing_phone = db.query(User).filter(User.phone == req.phone).first()
        if existing_phone:
            raise ConflictException(f"User with phone number '{req.phone}' already exists.")

        # 2. Duplicate email check if provided
        if req.email:
            existing_email = db.query(User).filter(User.email == req.email).first()
            if existing_email:
                raise ConflictException(f"User with email '{req.email}' already exists.")

        # 3. Create User
        hashed_pw = hash_password(req.password)
        user = User(
            phone=req.phone,
            email=req.email,
            hashed_password=hashed_pw,
            full_name=req.full_name,
            language_preference=req.language_preference,
            is_active=True,
            is_verified=False
        )

        # 4. Attach Role
        role_record = db.get(Role, req.role)
        if not role_record:
            role_record = Role(id=req.role, description=f"{req.role} system role")
            db.add(role_record)
        user.roles.append(role_record)

        db.add(user)
        db.commit()
        db.refresh(user)

        audit_service.record_activity(
            db=db,
            action="USER_REGISTRATION",
            resource_type="USER",
            resource_id=user.id,
            user_id=user.id,
            metadata={"phone": req.phone, "role": req.role}
        )

        return UserSummaryResponse(
            id=user.id,
            phone=user.phone,
            email=user.email,
            full_name=user.full_name,
            language_preference=user.language_preference,
            is_active=user.is_active,
            is_verified=user.is_verified,
            roles=[r.id for r in user.roles]
        )

    @staticmethod
    def authenticate_user(db: Session, req: UserLoginRequest) -> TokenResponse:
        """Authenticates user and returns JWT access token."""
        if not req.phone and not req.email:
            raise AuthenticationException("Either phone or email must be provided for login.")

        query = db.query(User)
        if req.phone:
            user = query.filter(User.phone == req.phone).first()
        else:
            user = query.filter(User.email == req.email).first()

        if not user or not verify_password(req.password, user.hashed_password):
            raise AuthenticationException("Invalid phone/email or password.")

        if not user.is_active:
            raise AuthenticationException("Account has been deactivated. Please contact support.")

        roles = [r.id for r in user.roles]
        access_token = create_access_token(
            subject=user.id,
            roles=roles,
            extra_claims={"phone": user.phone, "name": user.full_name}
        )

        audit_service.record_activity(
            db=db,
            action="USER_LOGIN",
            resource_type="USER",
            resource_id=user.id,
            user_id=user.id,
            metadata={"login_identifier": req.phone or req.email}
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserSummaryResponse(
                id=user.id,
                phone=user.phone,
                email=user.email,
                full_name=user.full_name,
                language_preference=user.language_preference,
                is_active=user.is_active,
                is_verified=user.is_verified,
                roles=roles
            )
        )


auth_service = AuthService()
