"""
ACREVIA - Unit & Offline Integration Tests for Dynamic API Key Manager.
Verifies multi-key parsing, intelligent key selection, rate-limit cooldown,
auth failure isolation, secret masking, and load-balancing rotation.
"""

import time
import pytest

from backend.app.core.key_manager import (
    ApiKeyPool,
    ApiKeyManager,
    mask_key,
)


def test_mask_key_security():
    """Verifies that API keys are strictly masked and never printed raw."""
    assert mask_key(None) == "[UNCONFIGURED]"
    assert mask_key("") == "[UNCONFIGURED]"
    assert mask_key("short12") == "sh***12"
    masked = mask_key("gsk_test_groq_key_99998888")
    assert masked.startswith("gsk_")
    assert masked.endswith("8888")
    assert "test_groq" not in masked


def test_api_key_pool_single_key_lifecycle():
    """Verifies standard lifecycle of a single configured key."""
    pool = ApiKeyPool("groq", raw_keys="gsk_primary_key_1111")
    assert pool.total_keys == 1
    assert pool.active_keys_count == 1

    key = pool.get_best_key()
    assert key == "gsk_primary_key_1111"

    pool.record_success(key)
    status = pool.get_pool_status()
    assert status["healthy_ready_keys"] == 1
    assert status["keys"][0]["total_successes"] == 1


def test_api_key_pool_multi_key_rotation_and_rate_limiting():
    """Verifies that rate-limited keys are suspended and the pool fails over to the next best key."""
    raw_keys = "key_alpha_1111, key_beta_2222; key_gamma_3333"
    pool = ApiKeyPool("data_gov_in", raw_keys=raw_keys, default_rate_limit_cooldown=0.5)
    assert pool.total_keys == 3
    assert pool.active_keys_count == 3

    # Pick best key 1
    k1 = pool.get_best_key()
    assert k1 == "key_alpha_1111"

    # Simulate rate-limit on key 1 (HTTP 429)
    pool.record_rate_limit(k1, cooldown_seconds=0.5)
    assert pool.active_keys_count == 2

    # Best key must now be key 2 (key 1 is in cooldown)
    k2 = pool.get_best_key()
    assert k2 == "key_beta_2222"
    assert k2 != k1

    # Simulate rate-limit on key 2
    pool.record_rate_limit(k2, cooldown_seconds=0.5)
    assert pool.active_keys_count == 1

    # Best key must now be key 3
    k3 = pool.get_best_key()
    assert k3 == "key_gamma_3333"

    # Simulate auth failure on key 3 (e.g. invalid or revoked key)
    pool.record_auth_failure(k3)
    assert pool.active_keys_count == 0

    # Wait for key 1 and key 2 cooldown to expire
    time.sleep(0.6)
    assert pool.active_keys_count == 2

    # Key 1 or Key 2 should be picked, key 3 remains disabled
    k_recovered = pool.get_best_key()
    assert k_recovered in ["key_alpha_1111", "key_beta_2222"]
    assert k_recovered != "key_gamma_3333"


def test_api_key_manager_global_selection():
    """Verifies ApiKeyManager registers pools and picks best keys globally."""
    ApiKeyManager.get_pool("custom_service", raw_keys="svc_key_a,svc_key_b")

    best_key = ApiKeyManager.pick_best_key("custom_service")
    assert best_key in ["svc_key_a", "svc_key_b"]

    ApiKeyManager.record_rate_limit("custom_service", best_key, cooldown_seconds=10.0)
    second_best = ApiKeyManager.pick_best_key("custom_service")
    assert second_best != best_key

    statuses = ApiKeyManager.get_all_pool_statuses()
    assert "custom_service" in statuses
    assert statuses["custom_service"]["total_keys"] == 2
