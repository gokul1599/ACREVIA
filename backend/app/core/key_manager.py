"""
ACREVIA - Resilient Multi-Provider API Key Manager & Dynamic Key Selector.
Intelligently selects the best, healthiest, and least-loaded API key for upstream integrations
(GroqCloud, data.gov.in, Neon, Hugging Face).
Features:
- Multi-key rotation and round-robin quota balancing.
- Automatic rate-limit (HTTP 429) backoff and temporary key suspension.
- Authentication failure (HTTP 401/403) isolation without crashing active pipelines.
- Zero secret leakage in logs and monitoring payloads.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import time
import os

from backend.app.core.logging import logger


def mask_key(key: Optional[str]) -> str:
    """Masks secret API key for secure logging and telemetry."""
    if not key or not key.strip():
        return "[UNCONFIGURED]"
    clean = key.strip()
    if len(clean) <= 8:
        return f"{clean[:2]}***{clean[-2:]}"
    return f"{clean[:4]}***{clean[-4:]}"


@dataclass
class KeyHealth:
    key: str
    is_active: bool = True
    consecutive_failures: int = 0
    total_successes: int = 0
    cooldown_until: float = 0.0
    cooldown_reason: Optional[str] = None
    last_used: float = 0.0


class ApiKeyPool:
    """
    Manages a pool of API keys for a specific upstream provider.
    Picks the best available key based on health, rate-limit cooldown, and usage balancing.
    """
    def __init__(
        self,
        provider_name: str,
        raw_keys: Optional[str] = None,
        default_rate_limit_cooldown: float = 60.0
    ):
        self.provider_name = provider_name
        self.default_rate_limit_cooldown = default_rate_limit_cooldown
        self._keys: List[KeyHealth] = []
        self._index: int = 0

        if raw_keys:
            self.load_keys(raw_keys)

    def load_keys(self, raw: str) -> None:
        """Parses comma- or semicolon-delimited keys into the pool."""
        self._keys.clear()
        tokens = [k.strip() for k in raw.replace(";", ",").split(",") if k.strip()]
        for k in tokens:
            self._keys.append(KeyHealth(key=k))

    def add_key(self, key: str) -> None:
        """Adds a single key to the pool if not already registered."""
        k = key.strip()
        if k and not any(kh.key == k for kh in self._keys):
            self._keys.append(KeyHealth(key=k))

    @property
    def total_keys(self) -> int:
        return len(self._keys)

    @property
    def active_keys_count(self) -> int:
        now = time.time()
        return sum(1 for kh in self._keys if kh.is_active and now >= kh.cooldown_until)

    def get_best_key(self) -> Optional[str]:
        """
        Picks the best available API key:
        1. Must be active and not in rate-limit cooldown.
        2. Sorted by lowest consecutive failures and least recently used (for fair rotation).
        3. If all keys are in cooldown, falls back to the key whose cooldown expires earliest.
        """
        if not self._keys:
            return None

        now = time.time()
        # Find candidates not in cooldown
        ready_keys = [
            kh for kh in self._keys
            if kh.is_active and now >= kh.cooldown_until
        ]

        if ready_keys:
            # Pick least-failed, least-recently-used key
            ready_keys.sort(key=lambda kh: (kh.consecutive_failures, kh.last_used))
            chosen = ready_keys[0]
            chosen.last_used = now
            return chosen.key

        # If all keys are throttled, find the active key with the earliest cooldown expiry
        active_throttled = [kh for kh in self._keys if kh.is_active]
        if active_throttled:
            active_throttled.sort(key=lambda kh: kh.cooldown_until)
            best_throttled = active_throttled[0]
            wait_time = max(0.0, best_throttled.cooldown_until - now)
            logger.warning(
                f"[{self.provider_name}] All API keys are in cooldown. Best key {mask_key(best_throttled.key)} "
                f"ready in {wait_time:.1f}s."
            )
            best_throttled.last_used = now
            return best_throttled.key

        # All keys revoked or disabled
        logger.error(f"[{self.provider_name}] All registered API keys have been disabled or revoked.")
        return None

    def record_success(self, key: str) -> None:
        """Records successful response using the given key."""
        for kh in self._keys:
            if kh.key == key:
                kh.consecutive_failures = 0
                kh.cooldown_until = 0.0
                kh.cooldown_reason = None
                kh.total_successes += 1
                return

    def record_rate_limit(self, key: str, cooldown_seconds: Optional[float] = None) -> None:
        """Suspends key temporarily after receiving HTTP 429 Too Many Requests."""
        cd = cooldown_seconds or self.default_rate_limit_cooldown
        now = time.time()
        for kh in self._keys:
            if kh.key == key:
                kh.consecutive_failures += 1
                kh.cooldown_until = now + cd
                kh.cooldown_reason = "HTTP_429_RATE_LIMITED"
                logger.warning(
                    f"[{self.provider_name}] API key {mask_key(key)} rate-limited (HTTP 429). "
                    f"Suspended for {cd:.0f}s."
                )
                return

    def record_auth_failure(self, key: str) -> None:
        """Disables or flags key after receiving HTTP 401 Unauthorized or 403 Forbidden."""
        for kh in self._keys:
            if kh.key == key:
                kh.is_active = False
                kh.consecutive_failures += 10
                kh.cooldown_reason = "HTTP_401_403_AUTH_FAILED"
                logger.error(
                    f"[{self.provider_name}] API key {mask_key(key)} authentication failed (401/403). Disabled."
                )
                return

    def get_pool_status(self) -> Dict[str, Any]:
        """Returns non-sensitive health metadata for telemetry and diagnostics."""
        now = time.time()
        keys_summary = []
        for kh in self._keys:
            in_cooldown = now < kh.cooldown_until
            keys_summary.append({
                "key_preview": mask_key(kh.key),
                "is_active": kh.is_active,
                "in_cooldown": in_cooldown,
                "remaining_cooldown_seconds": max(0.0, round(kh.cooldown_until - now, 1)) if in_cooldown else 0.0,
                "cooldown_reason": kh.cooldown_reason,
                "total_successes": kh.total_successes,
                "consecutive_failures": kh.consecutive_failures,
            })

        return {
            "provider": self.provider_name,
            "total_keys": len(self._keys),
            "healthy_ready_keys": self.active_keys_count,
            "keys": keys_summary
        }


class ApiKeyManager:
    """
    Global Registry managing dynamic API key pools across all ACREVIA integrations.
    """
    _pools: Dict[str, ApiKeyPool] = {}

    @classmethod
    def get_pool(
        cls,
        provider: str,
        raw_keys: Optional[str] = None,
        default_raw_keys: Optional[str] = None
    ) -> ApiKeyPool:
        provider_key = provider.lower().strip()
        keys_to_load = raw_keys or default_raw_keys
        if provider_key not in cls._pools:
            cls._pools[provider_key] = ApiKeyPool(provider_key, raw_keys=keys_to_load)
        elif keys_to_load and cls._pools[provider_key].total_keys == 0:
            cls._pools[provider_key].load_keys(keys_to_load)
        return cls._pools[provider_key]

    @classmethod
    def pick_best_key(cls, provider: str, default_raw_keys: Optional[str] = None) -> Optional[str]:
        """Selects the best available API key for the specified provider."""
        pool = cls.get_pool(provider, default_raw_keys)
        return pool.get_best_key()

    @classmethod
    def record_success(cls, provider: str, key: str) -> None:
        pool = cls.get_pool(provider)
        pool.record_success(key)

    @classmethod
    def record_rate_limit(cls, provider: str, key: str, cooldown_seconds: Optional[float] = None) -> None:
        pool = cls.get_pool(provider)
        pool.record_rate_limit(key, cooldown_seconds)

    @classmethod
    def record_auth_failure(cls, provider: str, key: str) -> None:
        pool = cls.get_pool(provider)
        pool.record_auth_failure(key)

    @classmethod
    def get_all_pool_statuses(cls) -> Dict[str, Any]:
        """Provides holistic health status of all registered API key pools."""
        return {p: pool.get_pool_status() for p, pool in cls._pools.items()}


# Initialize default pools from environment/settings
def init_key_manager_pools():
    from backend.app.core.config import settings

    if settings.GROQ_API_KEY:
        ApiKeyManager.get_pool("groq", settings.GROQ_API_KEY)
    if settings.DATA_GOV_IN_API_KEY:
        ApiKeyManager.get_pool("data_gov_in", settings.DATA_GOV_IN_API_KEY)
    if settings.HF_TOKEN:
        ApiKeyManager.get_pool("huggingface", settings.HF_TOKEN)


init_key_manager_pools()
