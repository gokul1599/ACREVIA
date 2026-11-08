"""
ACREVIA - Distributed Rate Limiting & Denial-of-Service Defense.
Stage 08 Remediation (TASK-S08-02).

Implements atomic Redis-backed sliding-window rate limiting for multi-replica deployments
with seamless, thread-safe in-memory fallback, tenant-scoped namespacing, and fail-safe policies.
"""

import os
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from threading import Lock
from typing import Dict, List, Optional, Tuple, NamedTuple
from fastapi import Request, Response

from backend.app.core.config import settings
from backend.app.core.exceptions import RateLimitExceededException
from backend.app.core.logging import logger


class RateLimitResult(NamedTuple):
    allowed: bool
    limit: int
    remaining: int
    reset_epoch: int
    retry_after: int


class RateLimitPolicy:
    """Pre-registered endpoint policy quotas."""
    AUTH_LOGIN = (5, 60)              # 5 requests per minute
    PASSWORD_RESET = (3, 300)         # 3 requests per 5 minutes
    AI_INFERENCE = (15, 60)           # 15 requests per minute (CropVision, Grad-CAM)
    RAG_QUERY = (20, 60)              # 20 requests per minute (KrishiBrain)
    FILE_UPLOAD = (10, 60)            # 10 uploads per minute
    EXPERT_CONNECT = (30, 60)         # 30 requests per minute
    DEFAULT_AUTHENTICATED = (120, 60) # 120 requests per minute
    PUBLIC_GENERAL = (60, 60)         # 60 requests per minute


class RateLimiterBackend(ABC):
    """Abstract interface for rate limiting storage."""

    @abstractmethod
    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
        fail_mode: str = "fail_open",
    ) -> RateLimitResult:
        pass

    @abstractmethod
    def reset(self, key_prefix: str = "") -> None:
        pass


class InMemoryRateLimiterBackend(RateLimiterBackend):
    """
    Thread-safe in-memory sliding window rate limiter.
    Used for local development, testing, and isolated staging environments.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._storage: Dict[str, List[float]] = defaultdict(list)
        self._last_cleanup = time.time()

    def _cleanup_old_entries(self, max_age_seconds: float = 300.0) -> None:
        now = time.time()
        if now - self._last_cleanup > 60.0:
            threshold = now - max_age_seconds
            keys_to_remove = []
            for key, timestamps in self._storage.items():
                self._storage[key] = [t for t in timestamps if t > threshold]
                if not self._storage[key]:
                    keys_to_remove.append(key)
            for k in keys_to_remove:
                del self._storage[k]
            self._last_cleanup = now

    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
        fail_mode: str = "fail_open",
    ) -> RateLimitResult:
        now = time.time()
        window_start = now - window_seconds
        reset_epoch = int(now + window_seconds)

        with self._lock:
            self._cleanup_old_entries(window_seconds * 2)
            timestamps = self._storage[key]
            valid_timestamps = [t for t in timestamps if t > window_start]

            if len(valid_timestamps) >= max_requests:
                self._storage[key] = valid_timestamps
                oldest = valid_timestamps[0]
                retry_after = max(1, int(oldest + window_seconds - now))
                return RateLimitResult(
                    allowed=False,
                    limit=max_requests,
                    remaining=0,
                    reset_epoch=int(oldest + window_seconds),
                    retry_after=retry_after,
                )

            valid_timestamps.append(now)
            self._storage[key] = valid_timestamps
            remaining = max(0, max_requests - len(valid_timestamps))
            return RateLimitResult(
                allowed=True,
                limit=max_requests,
                remaining=remaining,
                reset_epoch=reset_epoch,
                retry_after=0,
            )

    def reset(self, key_prefix: str = "") -> None:
        with self._lock:
            if not key_prefix:
                self._storage.clear()
            else:
                to_del = [k for k in self._storage if k.startswith(key_prefix)]
                for k in to_del:
                    del self._storage[k]


class RedisRateLimiterBackend(RateLimiterBackend):
    """
    Distributed Redis-backed sliding window rate limiter.
    Uses atomic Redis pipelines with sorted sets (ZADD, ZREMRANGEBYSCORE, ZCARD, EXPIRE).
    Guarantees shared counter consistency across multi-replica FastAPI worker nodes.
    """

    def __init__(self, redis_url: str, connection_timeout_seconds: float = 2.5) -> None:
        if redis_url and redis_url.startswith("redis://") and "upstash.io" in redis_url:
            # Upstash endpoints require SSL/TLS transport (rediss:// scheme)
            redis_url = "rediss://" + redis_url[len("redis://"):]
        self.redis_url = redis_url
        self.timeout = connection_timeout_seconds
        self._client = None
        self._fallback = InMemoryRateLimiterBackend()

    def _get_client(self):
        if self._client is None:
            try:
                import redis
                self._client = redis.Redis.from_url(
                    self.redis_url,
                    socket_connect_timeout=self.timeout,
                    socket_timeout=self.timeout,
                    decode_responses=True,
                )
            except Exception as e:
                logger.error(f"Failed to connect to Redis for distributed rate limiting: {e}")
                self._client = None
        return self._client

    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
        fail_mode: str = "fail_open",
    ) -> RateLimitResult:
        client = self._get_client()

        if client is None:
            # Redis is unreachable
            if fail_mode == "fail_closed":
                logger.error(f"Redis rate limiter down; fail_closed blocking request for {key}")
                return RateLimitResult(
                    allowed=False,
                    limit=max_requests,
                    remaining=0,
                    reset_epoch=int(time.time() + window_seconds),
                    retry_after=window_seconds,
                )
            else:
                logger.warning(f"Redis rate limiter down; falling back to in-memory limiter for {key}")
                return self._fallback.check_rate_limit(key, max_requests, window_seconds, fail_mode)

        now = time.time()
        window_start = now - window_seconds
        reset_epoch = int(now + window_seconds)

        try:
            # Atomic sliding-window pipeline
            pipe = client.pipeline()
            pipe.zremrangebyscore(key, "-inf", window_start)
            pipe.zcard(key)
            pipe.zadd(key, {f"{now}:{time.time_ns()}": now})
            pipe.expire(key, window_seconds + 5)
            results = pipe.execute()

            current_count = results[1]  # count before this addition

            if current_count >= max_requests:
                # Remove the timestamp we just tentatively added
                client.zremrangebyscore(key, now, now)
                retry_after = window_seconds
                return RateLimitResult(
                    allowed=False,
                    limit=max_requests,
                    remaining=0,
                    reset_epoch=reset_epoch,
                    retry_after=retry_after,
                )

            remaining = max(0, max_requests - current_count - 1)
            return RateLimitResult(
                allowed=True,
                limit=max_requests,
                remaining=remaining,
                reset_epoch=reset_epoch,
                retry_after=0,
            )
        except Exception as err:
            logger.error(f"Redis rate limiter communication error: {err}")
            if fail_mode == "fail_closed":
                return RateLimitResult(
                    allowed=False,
                    limit=max_requests,
                    remaining=0,
                    reset_epoch=reset_epoch,
                    retry_after=window_seconds,
                )
            return self._fallback.check_rate_limit(key, max_requests, window_seconds, fail_mode)

    def reset(self, key_prefix: str = "") -> None:
        client = self._get_client()
        if client:
            try:
                keys = client.keys(f"{key_prefix}*")
                if keys:
                    client.delete(*keys)
            except Exception as e:
                logger.warning(f"Failed to reset Redis keys with prefix {key_prefix}: {e}")
        self._fallback.reset(key_prefix)


class DistributedRateLimiter:
    """Master Rate Limiter managing backend selection and key generation."""

    def __init__(self) -> None:
        self.namespace = settings.RATE_LIMIT_NAMESPACE
        if settings.REDIS_URL:
            logger.info("Initializing distributed Redis rate limiting backend...")
            self.backend: RateLimiterBackend = RedisRateLimiterBackend(settings.REDIS_URL)
        else:
            logger.info("Initializing in-memory rate limiting backend (single-process)...")
            self.backend = InMemoryRateLimiterBackend()

    def set_backend(self, backend: RateLimiterBackend) -> None:
        """Allows hot-swapping backend for multi-instance simulation tests."""
        self.backend = backend

    def build_key(self, request: Request, endpoint_group: str) -> str:
        """
        Derives a safe, tenant-scoped, user-scoped rate limit key.
        Pertains to OWASP and DPDP privacy guidelines: avoids raw PII in keys.
        """
        tenant_id = getattr(request.state, "tenant_id", "default_tenant") if hasattr(request, "state") else "default"
        user_id = getattr(request.state, "user_id", None) if hasattr(request, "state") else None

        auth_header = request.headers.get("Authorization", "")
        if not user_id and auth_header.startswith("Bearer "):
            # Deterministic token hash fragment
            import hashlib
            user_id = hashlib.sha256(auth_header.encode()).hexdigest()[:12]

        client_ip = request.client.host if request.client else "unknown"

        identifier = f"u_{user_id}" if user_id else f"ip_{client_ip}"
        return f"rl:{self.namespace}:{tenant_id}:{endpoint_group}:{identifier}"


# Global Master Rate Limiter
rate_limiter = DistributedRateLimiter()


def rate_limit(
    max_requests: int = 60,
    window_seconds: int = 60,
    endpoint_group: str = "general",
    fail_mode: Optional[str] = None,
):
    """
    FastAPI dependency factory for endpoint-specific rate limiting.
    Injects standard RFC 6585 rate limiting headers and raises 429 when exhausted.
    """
    effective_fail_mode = fail_mode or settings.RATE_LIMIT_FAIL_MODE

    async def dependency(request: Request, response: Response) -> None:
        if not settings.RATE_LIMIT_ENABLED:
            return

        key = rate_limiter.build_key(request, endpoint_group)
        result = rate_limiter.backend.check_rate_limit(
            key=key,
            max_requests=max_requests,
            window_seconds=window_seconds,
            fail_mode=effective_fail_mode,
        )

        # Inject standard rate limit headers
        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)
        response.headers["X-RateLimit-Reset"] = str(result.reset_epoch)

        if not result.allowed:
            response.headers["Retry-After"] = str(result.retry_after)
            logger.warning(
                f"Rate limit exceeded: key_prefix={key[:30]} limit={max_requests}/{window_seconds}s "
                f"retry_after={result.retry_after}s"
            )
            raise RateLimitExceededException(
                message=f"Rate limit exceeded: maximum {max_requests} requests per {window_seconds} seconds.",
                retry_after=result.retry_after,
            )

    return dependency
