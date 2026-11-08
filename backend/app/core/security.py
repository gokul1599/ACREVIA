"""
ACREVIA - Cryptographic Security & Identity.
Handles bcrypt password hashing and PyJWT token generation and verification.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import bcrypt
import jwt

from backend.app.core.config import settings


def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt with automatic salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(
    subject: str,
    roles: list,
    extra_claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generates an HMAC-SHA256 signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "roles": roles,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": "acrevia-auth-service"
    }
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT token. Raises PyJWT exceptions on expiration/invalid signature."""
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        issuer="acrevia-auth-service"
    )
    return payload
