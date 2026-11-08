"""
ACREVIA - Developer Portal, API Applications & Scoped Credential Service.
Stage 14: Client ID generation, SHA-256 secret hashing, scope enforcement, and rate limit tracking.
"""

from datetime import datetime, timedelta, timezone
import hashlib
import json
import secrets
from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.interoperability import ApiApplication, ApiCredential


class DeveloperService:
    """
    Manages developer applications, API keys, cryptographic secret hashing,
    and credential verification for third-party integrations.
    """

    @classmethod
    def create_application(
        cls,
        db: Session,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        partner_id: Optional[str] = None,
        is_sandbox: bool = False,
        redirect_uris: Optional[List[str]] = None,
    ) -> ApiApplication:
        app = ApiApplication(
            user_id=user_id,
            partner_id=partner_id,
            name=name,
            description=description,
            is_sandbox=is_sandbox,
            is_active=True,
            redirect_uris_json=json.dumps(redirect_uris or []),
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        return app

    @classmethod
    def list_applications(cls, db: Session, user_id: str) -> List[ApiApplication]:
        return db.scalars(select(ApiApplication).where(ApiApplication.user_id == user_id)).all()

    @classmethod
    def get_application(cls, db: Session, app_id: str, user_id: str) -> Optional[ApiApplication]:
        app = db.get(ApiApplication, app_id)
        if app and app.user_id == user_id:
            return app
        return None

    @classmethod
    def create_credential(
        cls,
        db: Session,
        application_id: str,
        user_id: str,
        scopes: List[str],
        rate_limit_per_minute: int = 60,
        expires_in_days: int = 365,
    ) -> Tuple[ApiCredential, str]:
        app = db.get(ApiApplication, application_id)
        if not app:
            raise ValueError(f"Application '{application_id}' not found")
        if app.user_id != user_id:
            raise PermissionError("Access denied: You do not own this application")

        prefix = "ak_sand_" if app.is_sandbox else "ak_live_"
        client_id = f"{prefix}{secrets.token_hex(16)}"

        secret_prefix_str = "sec_snd_" if app.is_sandbox else "sec_liv_"
        raw_secret_body = secrets.token_urlsafe(32)
        plaintext_secret = f"{secret_prefix_str}{raw_secret_body}"

        # SHA-256 hash for secure storage
        hashed_secret = hashlib.sha256(plaintext_secret.encode("utf-8")).hexdigest()
        secret_hint = plaintext_secret[:12] + "..."

        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        cred = ApiCredential(
            application_id=application_id,
            client_id=client_id,
            hashed_secret=hashed_secret,
            secret_prefix=secret_hint,
            scopes_json=json.dumps(scopes),
            rate_limit_per_minute=rate_limit_per_minute,
            is_active=True,
            expires_at=expires_at,
        )
        db.add(cred)
        db.commit()
        db.refresh(cred)

        return cred, plaintext_secret

    @classmethod
    def verify_credential(
        cls,
        db: Session,
        client_id: str,
        client_secret: str,
        required_scope: Optional[str] = None,
    ) -> Tuple[bool, Optional[ApiCredential], Optional[str]]:
        cred = db.scalars(select(ApiCredential).where(ApiCredential.client_id == client_id)).first()
        if not cred:
            return False, None, "Invalid client_id"

        if not cred.is_active:
            return False, None, "Credential is inactive or revoked"

        if cred.expires_at:
            now = datetime.now(timezone.utc)
            expires_at = cred.expires_at if cred.expires_at.tzinfo else cred.expires_at.replace(tzinfo=timezone.utc)
            if expires_at < now:
                return False, None, "Credential has expired"

        # Verify hashed secret
        incoming_hash = hashlib.sha256(client_secret.encode("utf-8")).hexdigest()
        if incoming_hash != cred.hashed_secret:
            return False, None, "Invalid client_secret"

        # Check permission scope
        if required_scope:
            scopes = json.loads(cred.scopes_json)
            if "*" not in scopes and required_scope not in scopes:
                return False, None, f"Insufficient scope: requires '{required_scope}'"

        # Update last used
        cred.last_used_at = datetime.now(timezone.utc)
        db.commit()

        return True, cred, None

    @classmethod
    def revoke_credential(cls, db: Session, credential_id: str, user_id: str) -> ApiCredential:
        cred = db.get(ApiCredential, credential_id)
        if not cred:
            raise ValueError(f"Credential '{credential_id}' not found")
        if cred.application.user_id != user_id:
            raise PermissionError("Access denied: You do not own this credential")

        cred.is_active = False
        db.commit()
        db.refresh(cred)
        return cred
