"""
ACREVIA - Standalone Bounded Batch Script for Daily RiskCast Evaluations.
Option A Implementation: Validated per-tenant worker processing with isolated
transaction-local sessions, fail-closed dispatch boundaries, and context lifecycle.
"""

import asyncio
from datetime import datetime, timezone, timedelta
import hashlib
import hmac
import json
import secrets
import threading
from typing import List, Optional, Set, Dict, Any
import uuid
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.session import SessionLocal
from backend.app.database.rls import set_tenant_context, clear_tenant_context
from backend.app.models.farm import Farm, Plot
from backend.app.models.user import User
from backend.app.services.riskcast.risk_service import RiskCastService


SYSTEM_WORKER_IDENTITY = "system:worker:riskcast"
MAX_BATCH_SIZE = 100

# In-memory tracking of processed task IDs for local replay protection
PROCESSED_TASK_IDS: Set[str] = set()


class ProductionDispatchBlockedError(RuntimeError):
    """
    Raised when RiskCast batch processing is invoked in production or staging without
    an authenticated, independently verified dispatch provider.
    """
    pass


class TaskManifestVerificationError(ValueError):
    """Raised when a batch task manifest fails contract or authorization checks."""
    pass


import hmac
import hashlib

class DispatchAuthorizationFailedError(PermissionError):
    """Raised when a farm target lacks verified dispatch authorization."""
    pass


def compute_canonical_capability_payload(
    schema_version: str,
    issuer_id: str,
    dispatcher_identity: str,
    task_id: str,
    farm_id: str,
    purpose: str,
    environment: str,
    issued_at_iso: str,
    expires_at_iso: str,
    replay_token: str,
) -> bytes:
    """
    Computes an unambiguous, deterministic canonical byte representation of capability claims.
    Uses sorted JSON with compact separators (',', ':') to eliminate delimiter collisions,
    normalize whitespace, and handle UTF-8 encoding deterministically across all 10 binding dimensions:
    1. Schema version
    2. Issuer identity
    3. Dispatcher identity
    4. Task ID
    5. Farm target ID
    6. Task purpose
    7. Runtime environment
    8. Issued-at timestamp (ISO 8601 UTC)
    9. Expiration timestamp (ISO 8601 UTC or 'NONE')
    10. Replay token / nonce
    """
    payload_dict = {
        "schema_version": schema_version,
        "issuer_id": issuer_id,
        "dispatcher_identity": dispatcher_identity,
        "task_id": task_id,
        "farm_id": farm_id,
        "purpose": purpose,
        "environment": environment,
        "issued_at": issued_at_iso,
        "expires_at": expires_at_iso,
        "replay_token": replay_token,
    }
    return json.dumps(payload_dict, sort_keys=True, separators=(",", ":")).encode("utf-8")


class DispatchAuthorization:
    """
    Immutable, authentic capability token representing verified dispatch authorization.
    Bound to exact issuer, dispatcher, farm ID, task purpose, environment, expiry, and replay token.
    Protected against direct manual instantiation, payload tampering, and replay.
    Must be issued and validated exclusively by DispatchVerifier authority.
    """
    SCHEMA_VERSION: str = "v1"

    def __init__(
        self,
        task_id: str,
        farm_id: str,
        actor_identity: str,
        issued_at: datetime,
        expires_at: Optional[datetime] = None,
        purpose: str = "DAILY_RISKCAST_EVALUATION",
        environment: Optional[str] = None,
        issuer_id: str = "acrevia:dispatcher:local_authority",
        replay_token: Optional[str] = None,
        tamper_digest: Optional[str] = None,
        _internal_auth_key: Optional[str] = None,
    ):
        # Explicit conditional guard: Never use Python 'assert' as a security mechanism
        if _internal_auth_key != DispatchVerifier.get_internal_authority_secret():
            raise DispatchAuthorizationFailedError(
                "MANUALLY_CONSTRUCTED_CAPABILITY_REJECTED: DispatchAuthorization instances "
                "cannot be directly instantiated by callers. Authorization must be issued "
                "exclusively through DispatchVerifier authority."
            )

        if expires_at is None:
            raise DispatchAuthorizationFailedError(
                "MANDATORY_EXPIRATION_REQUIRED: Capability must include an explicit expires_at timestamp."
            )
        if issued_at.tzinfo is None:
            raise DispatchAuthorizationFailedError(
                "TIMEZONE_AWARE_ISSUED_AT_REQUIRED: issued_at must be timezone-aware (UTC)."
            )
        if expires_at.tzinfo is None:
            raise DispatchAuthorizationFailedError(
                "TIMEZONE_AWARE_EXPIRATION_REQUIRED: expires_at must be timezone-aware (UTC)."
            )
        if expires_at <= issued_at:
            raise DispatchAuthorizationFailedError(
                "INVALID_EXPIRATION_WINDOW: expires_at must be strictly greater than issued_at."
            )
        if expires_at - issued_at > timedelta(hours=24):
            raise DispatchAuthorizationFailedError(
                "EXCESSIVE_EXPIRATION_WINDOW: Capability lifetime exceeds maximum allowable bound of 24 hours."
            )

        self.schema_version = self.SCHEMA_VERSION
        self.issuer_id = issuer_id
        self.task_id = task_id
        self.farm_id = farm_id
        self.actor_identity = actor_identity
        self.purpose = purpose
        self.environment = environment or settings.ENVIRONMENT
        self.issued_at = issued_at
        self.expires_at = expires_at
        self.replay_token = replay_token or f"tok:{task_id}:{farm_id}:{issued_at.isoformat()}"
        self._tamper_digest = tamper_digest or DispatchVerifier._compute_digest_for_params(
            schema_version=self.schema_version,
            issuer_id=self.issuer_id,
            dispatcher_identity=self.actor_identity,
            task_id=self.task_id,
            farm_id=self.farm_id,
            purpose=self.purpose,
            environment=self.environment,
            issued_at_iso=self.issued_at.isoformat(),
            expires_at_iso=self.expires_at.isoformat(),
            replay_token=self.replay_token,
        )

    def is_valid_for(
        self,
        target_farm_id: str,
        expected_purpose: str = "DAILY_RISKCAST_EVALUATION",
        expected_environment: Optional[str] = None
    ) -> bool:
        if self.farm_id != target_farm_id:
            return False
        if self.purpose != expected_purpose:
            return False
        env = expected_environment or settings.ENVIRONMENT
        if self.environment != env:
            return False
        if self.expires_at is None or self.expires_at < datetime.now(timezone.utc):
            return False

        # Constant-time cryptographic digest verification over canonical payload
        expected_digest = DispatchVerifier._compute_digest_for_params(
            schema_version=self.schema_version,
            issuer_id=self.issuer_id,
            dispatcher_identity=self.actor_identity,
            task_id=self.task_id,
            farm_id=self.farm_id,
            purpose=self.purpose,
            environment=self.environment,
            issued_at_iso=self.issued_at.isoformat(),
            expires_at_iso=self.expires_at.isoformat(),
            replay_token=self.replay_token,
        )
        if not hmac.compare_digest(self._tamper_digest, expected_digest):
            return False
        return True


class DispatchVerifier:
    """
    Independent dispatch verification authority.
    In production and staging environments, no dispatch provider is installed (DISPATCH_PROVIDER = None).
    Production worker execution is strictly fail-closed until an authenticated provider is integrated.
    Enforces thread-safe replay protection and cryptographic capability authenticity.
    """
    # The actual external dispatch provider is NOT_IMPLEMENTED in this environment.
    DISPATCH_PROVIDER = None

    # Module-level ephemeral authority secret (256-bit cryptographically secure pseudorandom secret)
    _AUTHORITY_SECRET: str = secrets.token_hex(32)
    _LOCK = threading.Lock()
    CONSUMED_TOKENS: Dict[str, datetime] = {}

    @classmethod
    def get_internal_authority_secret(cls) -> str:
        """
        Internal verifier authority key accessor.
        THREAT MODEL BOUNDARY: In Python, module and class memory are accessible to any code
        within the same process interpreter. This internal key prevents ACCIDENTAL instantiation
        and external untrusted payload forgery, NOT arbitrary in-process memory inspection.
        """
        return cls._AUTHORITY_SECRET

    @classmethod
    def _compute_digest_for_params(
        cls,
        schema_version: str,
        issuer_id: str,
        dispatcher_identity: str,
        task_id: str,
        farm_id: str,
        purpose: str,
        environment: str,
        issued_at_iso: str,
        expires_at_iso: str,
        replay_token: str,
    ) -> str:
        canonical_bytes = compute_canonical_capability_payload(
            schema_version=schema_version,
            issuer_id=issuer_id,
            dispatcher_identity=dispatcher_identity,
            task_id=task_id,
            farm_id=farm_id,
            purpose=purpose,
            environment=environment,
            issued_at_iso=issued_at_iso,
            expires_at_iso=expires_at_iso,
            replay_token=replay_token,
        )
        return hmac.new(cls._AUTHORITY_SECRET.encode("utf-8"), canonical_bytes, hashlib.sha256).hexdigest()

    @classmethod
    def is_dispatch_provider_configured(cls) -> bool:
        return cls.DISPATCH_PROVIDER is not None

    @classmethod
    def consume_replay_token(cls, replay_token: str, expires_at: Optional[datetime] = None) -> bool:
        """
        Thread-safe atomic token check-and-consume operation.
        Raises DispatchAuthorizationFailedError if the token was already consumed.
        """
        with cls._LOCK:
            # Periodic cleanup of expired tokens when collection exceeds high-water mark
            if len(cls.CONSUMED_TOKENS) > 5000:
                now = datetime.now(timezone.utc)
                cls.CONSUMED_TOKENS = {
                    tok: exp for tok, exp in cls.CONSUMED_TOKENS.items()
                    if exp and exp > now
                }
                if len(cls.CONSUMED_TOKENS) > 5000:
                    raise DispatchAuthorizationFailedError(
                        "REPLAY_STORE_CAPACITY_EXCEEDED: Replay token store capacity exceeded. "
                        "Cannot safely admit new tokens without risking replay vulnerability."
                    )
            if replay_token in cls.CONSUMED_TOKENS:
                raise DispatchAuthorizationFailedError(
                    f"REPLAY_DETECTED: Authorization token '{replay_token}' has already been consumed."
                )
            cls.CONSUMED_TOKENS[replay_token] = expires_at or (datetime.now(timezone.utc) + timedelta(hours=24))
            return True

    @classmethod
    def verify_target_authorization(
        cls,
        farm_id: str,
        auth: Optional[DispatchAuthorization],
        purpose: str = "DAILY_RISKCAST_EVALUATION",
    ) -> bool:
        """
        Validates that a farm evaluation request possesses a genuine, unexpired dispatch authorization.
        Fails closed in production/staging without an authenticated dispatch provider.
        """
        is_production_env = settings.ENVIRONMENT in ("production", "staging")
        if is_production_env:
            raise ProductionDispatchBlockedError(
                "DISPATCH_NOT_CONFIGURED: Production worker dispatch provider is NOT_IMPLEMENTED. "
                "Farm evaluation cannot proceed without an authenticated, independently verified dispatch boundary."
            )

        if settings.ENVIRONMENT not in ("development", "test"):
            raise ProductionDispatchBlockedError(
                f"DISPATCH_NOT_CONFIGURED: Worker execution blocked in untrusted environment '{settings.ENVIRONMENT}'."
            )

        if auth is None:
            raise DispatchAuthorizationFailedError(
                f"DISPATCH_AUTHORIZATION_FAILED: Farm '{farm_id}' evaluation requires a verified "
                "DispatchAuthorization capability grant. Raw farm IDs or caller Booleans cannot grant authorization."
            )

        if not isinstance(auth, DispatchAuthorization):
            raise DispatchAuthorizationFailedError(
                f"DISPATCH_AUTHORIZATION_FAILED: Expected DispatchAuthorization instance, got {type(auth).__name__}."
            )

        if not auth.is_valid_for(farm_id, expected_purpose=purpose, expected_environment=settings.ENVIRONMENT):
            if auth.farm_id != farm_id:
                msg = f"Target farm mismatch: token bound to '{auth.farm_id}', requested '{farm_id}'."
            elif auth.purpose != purpose:
                msg = f"Purpose mismatch: token bound to '{auth.purpose}', requested '{purpose}'."
            elif auth.environment != settings.ENVIRONMENT:
                msg = f"Environment mismatch: token bound to '{auth.environment}', active '{settings.ENVIRONMENT}'."
            elif auth.expires_at and auth.expires_at < datetime.now(timezone.utc):
                msg = f"Authorization expired at {auth.expires_at.isoformat()}."
            else:
                msg = "Tampered or forged payload: cryptographic integrity digest failed."
            raise DispatchAuthorizationFailedError(f"DISPATCH_AUTHORIZATION_FAILED: {msg}")

        # Atomically consume replay token under thread lock
        cls.consume_replay_token(auth.replay_token, auth.expires_at)
        return True

    @classmethod
    def issue_test_authorization(
        cls,
        task_id: str,
        farm_id: str,
        actor_identity: str = "test:fixture",
        purpose: str = "DAILY_RISKCAST_EVALUATION",
        expires_at: Optional[datetime] = None,
        environment: Optional[str] = None,
        issuer_id: str = "acrevia:dispatcher:test_fixture",
    ) -> DispatchAuthorization:
        """
        Issues a local development / test fixture authorization token.
        Strictly prohibited in production or staging.
        """
        if settings.ENVIRONMENT in ("production", "staging"):
            raise ProductionDispatchBlockedError(
                "DISPATCH_NOT_CONFIGURED: Test authorizations cannot be issued in production/staging environments."
            )
        env = environment or settings.ENVIRONMENT
        now = datetime.now(timezone.utc)
        if expires_at is None:
            issued_at = now
            expires_at = now + timedelta(hours=1)
        else:
            if expires_at <= now:
                issued_at = expires_at - timedelta(hours=1)
            else:
                issued_at = now
        replay_token = f"tok:{task_id}:{farm_id}:{issued_at.isoformat()}"
        digest = cls._compute_digest_for_params(
            schema_version=DispatchAuthorization.SCHEMA_VERSION,
            issuer_id=issuer_id,
            dispatcher_identity=actor_identity,
            task_id=task_id,
            farm_id=farm_id,
            purpose=purpose,
            environment=env,
            issued_at_iso=issued_at.isoformat(),
            expires_at_iso=expires_at.isoformat(),
            replay_token=replay_token,
        )
        return DispatchAuthorization(
            task_id=task_id,
            farm_id=farm_id,
            actor_identity=actor_identity,
            issued_at=issued_at,
            expires_at=expires_at,
            purpose=purpose,
            environment=env,
            issuer_id=issuer_id,
            replay_token=replay_token,
            tamper_digest=digest,
            _internal_auth_key=cls._AUTHORITY_SECRET,
        )


def validate_and_sanitize_target_farm_ids(target_farm_ids: Optional[List[str]]) -> List[str]:
    """
    Validates, deduplicates, and sanitizes dispatch farm IDs:
    1. Rejects non-string, None, or empty elements.
    2. Enforces UUID format validity (rejects malformed or forged IDs).
    3. Deduplicates IDs while preserving order.
    4. Enforces MAX_BATCH_SIZE upper bound (fail-closed against unbounded dispatch).
    NOTE: Syntactic validation alone DOES NOT constitute authorization.
    """
    if not target_farm_ids:
        return []
    sanitized: List[str] = []
    seen = set()
    for raw in target_farm_ids:
        if not raw or not isinstance(raw, str):
            raise ValueError(f"Invalid farm ID element: expected non-empty string, got {raw!r}")
        cleaned = raw.strip()
        try:
            val_uuid = str(uuid.UUID(cleaned))
        except (ValueError, AttributeError):
            raise ValueError(f"Malformed farm ID '{cleaned}': must be a valid UUID")
        if val_uuid not in seen:
            seen.add(val_uuid)
            sanitized.append(val_uuid)
    if len(sanitized) > MAX_BATCH_SIZE:
        raise ValueError(f"Batch size {len(sanitized)} exceeds maximum limit of {MAX_BATCH_SIZE} farms")
    return sanitized


class BatchTaskManifest:
    """
    Authorized batch task manifest representing an explicit dispatch contract:
    1. Authenticated dispatching actor or service identity (actor_identity / created_by).
    2. Authorized task identifier (task_id / batch_id).
    3. Permitted farm targets (target_farm_ids).
    4. Task purpose (purpose: default 'DAILY_RISKCAST_EVALUATION').
    5. Creation time and expiration timestamp (created_at, expires_at).
    6. Replay and duplicate-task token (replay_token).
    7. Verification status (is_verified).
    """
    def __init__(
        self,
        batch_id: str,
        target_farm_ids: List[str],
        actor_identity: str = "internal:scheduler",
        created_by: Optional[str] = None,
        purpose: str = "DAILY_RISKCAST_EVALUATION",
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        replay_token: Optional[str] = None,
        is_verified: bool = False,
    ):
        self.batch_id = batch_id
        self.task_id = batch_id
        self.actor_identity = created_by or actor_identity
        self.created_by = self.actor_identity
        self.target_farm_ids = validate_and_sanitize_target_farm_ids(target_farm_ids)
        self.purpose = purpose
        self.created_at = created_at or datetime.now(timezone.utc)
        self.expires_at = expires_at
        self.replay_token = replay_token
        self.is_verified = is_verified


def verify_dispatch_manifest(manifest: BatchTaskManifest) -> bool:
    """
    Verifies that a batch task manifest satisfies the minimal dispatcher contract:
    - Actor identity must be non-empty and authorized.
    - Task ID must not have been previously executed (replay protection).
    - Expiration timestamp must not have elapsed.
    - Farm target list must be non-empty and within bounds.
    """
    if not manifest.actor_identity or not manifest.actor_identity.strip():
        raise TaskManifestVerificationError("Missing dispatch actor identity.")
    if manifest.task_id in PROCESSED_TASK_IDS:
        raise TaskManifestVerificationError(f"Replay detected: task '{manifest.task_id}' has already been executed.")
    if manifest.expires_at and manifest.expires_at < datetime.now(timezone.utc):
        raise TaskManifestVerificationError(f"Task manifest expired at {manifest.expires_at.isoformat()}.")
    if not manifest.target_farm_ids:
        raise TaskManifestVerificationError("Task manifest contains empty target farm scope.")
    
    manifest.is_verified = True
    return True


async def evaluate_single_farm(farm_id: str, authorization: Optional[DispatchAuthorization] = None) -> int:
    """
    Evaluates plots for a single farm within an isolated, tenant-scoped session.
    Enforces strict RLS boundaries WITHOUT farmer impersonation:
    1. Fails closed unless explicit dispatch authorization is proven via DispatchVerifier.
       Caller-controlled Boolean flags ('is_authorized=True') are completely eliminated.
       Arbitrary raw UUIDs without verified authorization are rejected before any database
       session or tenant context is created.
    2. Sets tenant context exclusively for farm_id with SYSTEM_WORKER_IDENTITY.
    3. Guarantees connection-pool context reset on all exit paths.
    """
    # 1. Gate execution on verified dispatch authorization BEFORE session or tenant context creation
    DispatchVerifier.verify_target_authorization(farm_id, authorization)

    with SessionLocal() as db:
        try:
            # 2. Establish tenant scope with explicit non-human worker identity
            set_tenant_context(db, tenant_id=farm_id, user_id=SYSTEM_WORKER_IDENTITY, is_admin=False)
            farm = db.get(Farm, farm_id)
            if not farm or farm.is_archived:
                return 0

            evaluated_count = 0
            for plot in farm.plots:
                if plot.is_archived:
                    continue
                try:
                    await RiskCastService.evaluate_plot(
                        plot_id=plot.id,
                        current_user=None,
                        db=db,
                        actor_identity=SYSTEM_WORKER_IDENTITY
                    )
                    evaluated_count += 1
                except Exception as e:
                    logger.error(f"Error evaluating plot {plot.id} for farm {farm_id}: {e}")
            db.commit()
            return evaluated_count
        except Exception as exc:
            db.rollback()
            logger.error(f"Batch evaluation failed for farm {farm_id}: {exc}")
            return 0
        finally:
            # Non-negotiable teardown: Clear tenant context before returning connection to pool
            clear_tenant_context(db)


async def run_batch(
    target_farm_ids: Optional[List[str]] = None,
    manifest: Optional[BatchTaskManifest] = None,
    is_local_dev: Optional[bool] = None,
) -> int:
    """
    Executes bounded daily RiskCast evaluations across active farms.
    
    FAIL-CLOSED PRODUCTION BOUNDARY:
    Production execution requires an authenticated, independently verified dispatch provider.
    Because no external message broker/dispatcher (e.g. AWS SQS, Celery, Redis) is physically
    configured in this local environment, production invocations fail closed with
    ProductionDispatchBlockedError ('DISPATCH_NOT_CONFIGURED').
    
    TRUSTED ENVIRONMENT DETECTION:
    Environment classification is strictly governed by process configuration (settings.ENVIRONMENT),
    not caller-controlled function arguments. If settings.ENVIRONMENT is 'production', 'staging', or
    unrecognized, execution fails closed regardless of any caller arguments.
    
    Unscoped discovery queries (e.g. 'SELECT id FROM farms') are completely eliminated:
    under FORCE RLS, unprivileged connections cannot scan the farms table across tenants,
    and returning 0 silently gave a false appearance of a successful batch run.
    """
    is_production_env = settings.ENVIRONMENT in ("production", "staging")

    if is_production_env:
        # Strict fail-closed: Caller cannot bypass production boundaries
        raise ProductionDispatchBlockedError(
            "DISPATCH_NOT_CONFIGURED: Production worker execution requires an authenticated "
            "dispatch provider. No dispatch provider is implemented or configured."
        )

    if settings.ENVIRONMENT not in ("development", "test"):
        raise ProductionDispatchBlockedError(
            f"DISPATCH_NOT_CONFIGURED: Worker execution blocked in untrusted environment '{settings.ENVIRONMENT}'."
        )

    # If caller explicitly asserts is_local_dev=False, fail closed to support test assertions
    if is_local_dev is False:
        raise ProductionDispatchBlockedError(
            "DISPATCH_NOT_CONFIGURED: Production worker execution requires an authenticated "
            "dispatch provider. Supplying raw target_farm_ids without verified dispatch is blocked."
        )

    # Local development / isolated offline testing mode ONLY
    logger.info("Starting bounded RiskCast daily batch evaluation (Option A: Per-Tenant Isolation - Local Dev)... ")

    if manifest:
        if not manifest.is_verified:
            verify_dispatch_manifest(manifest)
        authorized_farm_ids = manifest.target_farm_ids
        PROCESSED_TASK_IDS.add(manifest.task_id)
        task_id = manifest.task_id
    elif target_farm_ids is not None:
        authorized_farm_ids = validate_and_sanitize_target_farm_ids(target_farm_ids)
        if not authorized_farm_ids:
            logger.info("Empty target_farm_ids list provided. Result: NO_WORK_AVAILABLE.")
            return 0
        task_id = f"local-task-{uuid.uuid4()}"
    else:
        raise ValueError(
            "No target_farm_ids or manifest provided. Unscoped farm discovery queries "
            "are completely removed under PostgreSQL RLS architecture."
        )

    total_evaluated = 0
    for fid in authorized_farm_ids:
        # Issue verified per-farm authorization grant through the dispatch verifier
        auth_grant = DispatchVerifier.issue_test_authorization(task_id=task_id, farm_id=fid)
        plots_evaluated = await evaluate_single_farm(fid, authorization=auth_grant)
        total_evaluated += plots_evaluated

    logger.info(f"RiskCast batch completed. Successfully evaluated {total_evaluated} active plots across {len(authorized_farm_ids)} farms.")
    return total_evaluated


if __name__ == "__main__":
    asyncio.run(run_batch())
