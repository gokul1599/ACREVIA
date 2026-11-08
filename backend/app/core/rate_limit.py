"""
ACREVIA - Application Rate Limiting & Throttling.
Thread-safe sliding-window in-memory rate limiter for brute-force mitigation and API defense.
"""

import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List, Optional
from fastapi import Request

from backend.app.core.exceptions import RateLimitExceededException
from backend.app.core.logging import logger


class InMemoryRateLimiter:
    """
    Sliding window in-memory rate limiter.
    Tracks timestamps per key (e.g., client IP or user ID).
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._storage: Dict[str, List[float]] = defaultdict(list)
        self._last_cleanup = time.time()

    def _cleanup_old_entries(self, max_age_seconds: float = 300.0) -> None:
        now = time.time()
        if now - self._last_cleanup > 60.0:  # Run cleanup at most once per minute
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
        max_requests: int = 60,
        window_seconds: int = 60
    ) -> bool:
        """
        Returns True if request is allowed, False if exceeded.
        """
        now = time.time()
        window_start = now - window_seconds

        with self._lock:
            self._cleanup_old_entries(window_seconds * 2)
            timestamps = self._storage[key]
            # Prune timestamps outside current window
            valid_timestamps = [t for t in timestamps if t > window_start]
            if len(valid_timestamps) >= max_requests:
                self._storage[key] = valid_timestamps
                return False
            valid_timestamps.append(now)
            self._storage[key] = valid_timestamps
            return True


# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()


def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """
    FastAPI dependency factory for endpoint-specific rate limiting.
    Extracts client IP address or Authorization header.
    """
    async def dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        auth_header = request.headers.get("Authorization", "")
        # Use auth header hash if present, otherwise client IP
        key = f"{request.url.path}:{auth_header[:30] if auth_header else client_ip}"

        allowed = rate_limiter.check_rate_limit(
            key=key,
            max_requests=max_requests,
            window_seconds=window_seconds
        )
        if not allowed:
            logger.warning(f"Rate limit exceeded for key {key} ({max_requests} req / {window_seconds}s)")
            raise RateLimitExceededException(
                message=f"Rate limit exceeded: maximum {max_requests} requests per {window_seconds} seconds.",
                retry_after=window_seconds
            )

    return dependency
