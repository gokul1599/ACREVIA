"""
Unit & Integration Tests for ACREVIA Distributed Rate Limiting.
Stage 08 Remediation (TASK-S08-02).
"""

import time
import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI, Depends, Request
from fastapi.testclient import TestClient

from backend.app.core.rate_limit import (
    InMemoryRateLimiterBackend,
    RedisRateLimiterBackend,
    DistributedRateLimiter,
    RateLimitPolicy,
    rate_limit,
)
from backend.app.core.exceptions import RateLimitExceededException


def test_in_memory_backend_normal_and_exhaustion():
    backend = InMemoryRateLimiterBackend()
    key = "test:farmer:general:1"

    # Allow 3 requests in 10s
    res1 = backend.check_rate_limit(key, max_requests=3, window_seconds=10)
    assert res1.allowed is True
    assert res1.remaining == 2

    res2 = backend.check_rate_limit(key, max_requests=3, window_seconds=10)
    assert res2.allowed is True
    assert res2.remaining == 1

    res3 = backend.check_rate_limit(key, max_requests=3, window_seconds=10)
    assert res3.allowed is True
    assert res3.remaining == 0

    # 4th request must be rejected
    res4 = backend.check_rate_limit(key, max_requests=3, window_seconds=10)
    assert res4.allowed is False
    assert res4.remaining == 0
    assert res4.retry_after > 0


def test_key_building_tenant_and_user_isolation():
    limiter = DistributedRateLimiter()

    req_farmer_a = MagicMock(spec=Request)
    req_farmer_a.state.tenant_id = "tenant-warangal"
    req_farmer_a.state.user_id = "farmer-01"
    req_farmer_a.headers = {}
    req_farmer_a.client.host = "10.0.0.1"

    req_farmer_b = MagicMock(spec=Request)
    req_farmer_b.state.tenant_id = "tenant-nalgonda"
    req_farmer_b.state.user_id = "farmer-02"
    req_farmer_b.headers = {}
    req_farmer_b.client.host = "10.0.0.2"

    key_a = limiter.build_key(req_farmer_a, "crop_vision")
    key_b = limiter.build_key(req_farmer_b, "crop_vision")

    assert key_a != key_b
    assert "tenant-warangal" in key_a
    assert "tenant-nalgonda" in key_b
    assert "u_farmer-01" in key_a
    assert "u_farmer-02" in key_b


def test_multi_instance_shared_state_simulation():
    """
    Simulates two independent worker replicas (Worker Node 1 and Worker Node 2)
    sharing the same underlying state backend (e.g. shared Redis or state proxy).
    """
    # Shared backend simulation
    shared_backend = InMemoryRateLimiterBackend()

    # Replicas with the same shared backend
    replica_1 = DistributedRateLimiter()
    replica_1.set_backend(shared_backend)

    replica_2 = DistributedRateLimiter()
    replica_2.set_backend(shared_backend)

    shared_key = "rl:acrevia:warangal:crop_vision:u_farmer_101"

    # Replica 1 consumes 2 of 3 requests
    r1 = replica_1.backend.check_rate_limit(shared_key, max_requests=3, window_seconds=30)
    assert r1.allowed is True
    assert r1.remaining == 2

    r2 = replica_1.backend.check_rate_limit(shared_key, max_requests=3, window_seconds=30)
    assert r2.allowed is True
    assert r2.remaining == 1

    # Replica 2 makes a request - must see the remaining quota decremented to 0
    r3 = replica_2.backend.check_rate_limit(shared_key, max_requests=3, window_seconds=30)
    assert r3.allowed is True
    assert r3.remaining == 0

    # Replica 2 makes 4th request - must be rejected by shared quota
    r4 = replica_2.backend.check_rate_limit(shared_key, max_requests=3, window_seconds=30)
    assert r4.allowed is False

    # Replica 1 also sees the rejection
    r5 = replica_1.backend.check_rate_limit(shared_key, max_requests=3, window_seconds=30)
    assert r5.allowed is False


def test_fail_closed_mode_on_unreachable_redis():
    """Verifies that fail_closed blocks requests when Redis is unreachable for critical routes."""
    backend = RedisRateLimiterBackend("redis://nonexistent-host-99999.test:6379", connection_timeout_seconds=0.1)

    result = backend.check_rate_limit("auth:login:u1", max_requests=5, window_seconds=60, fail_mode="fail_closed")
    assert result.allowed is False
    assert result.retry_after == 60
    assert result.service_unavailable is True


def test_fail_open_mode_on_unreachable_redis():
    """Verifies that fail_open degrades gracefully to local in-memory limiting."""
    backend = RedisRateLimiterBackend("redis://nonexistent-host-99999.test:6379", connection_timeout_seconds=0.1)

    result = backend.check_rate_limit("public:general:ip1", max_requests=10, window_seconds=60, fail_mode="fail_open")
    assert result.allowed is True
    assert result.remaining == 9
    assert result.service_unavailable is False


def test_fail_closed_redis_timeout_handling():
    """Verifies that Redis timeout in pipeline triggers fail_closed with service_unavailable=True."""
    backend = RedisRateLimiterBackend("redis://localhost:6379")
    mock_client = MagicMock()
    mock_client.pipeline.side_effect = TimeoutError("Redis socket timeout")
    backend._client = mock_client

    result = backend.check_rate_limit("auth:login:u2", max_requests=5, window_seconds=60, fail_mode="fail_closed")
    assert result.allowed is False
    assert result.service_unavailable is True
    assert result.retry_after == 60


def test_fail_closed_redis_auth_failure_handling():
    """Verifies that Redis authentication failure triggers fail_closed with service_unavailable=True."""
    backend = RedisRateLimiterBackend("redis://localhost:6379")
    mock_client = MagicMock()
    mock_client.pipeline.side_effect = Exception("WRONGPASS invalid username-password pair")
    backend._client = mock_client

    result = backend.check_rate_limit("auth:login:u3", max_requests=5, window_seconds=60, fail_mode="fail_closed")
    assert result.allowed is False
    assert result.service_unavailable is True
    assert result.retry_after == 60


def test_fail_closed_redis_tls_failure_handling():
    """Verifies that Redis TLS/SSL failure triggers fail_closed with service_unavailable=True."""
    import ssl
    backend = RedisRateLimiterBackend("rediss://localhost:6379")
    mock_client = MagicMock()
    mock_client.pipeline.side_effect = ssl.SSLError("SSL handshake failed")
    backend._client = mock_client

    result = backend.check_rate_limit("auth:login:u4", max_requests=5, window_seconds=60, fail_mode="fail_closed")
    assert result.allowed is False
    assert result.service_unavailable is True
    assert result.retry_after == 60


def test_redis_recovery_after_outage():
    """Verifies that once an outage clears, subsequent calls succeed."""
    backend = RedisRateLimiterBackend("redis://localhost:6379")
    # First: simulate outage
    backend._client = None
    with patch.object(backend, "_get_client", return_value=None):
        res1 = backend.check_rate_limit("auth:login:u5", max_requests=5, window_seconds=60, fail_mode="fail_closed")
        assert res1.allowed is False
        assert res1.service_unavailable is True

    # Second: simulate recovery
    mock_healthy_client = MagicMock()
    mock_pipe = MagicMock()
    mock_pipe.execute.return_value = [True, 0, True, True]
    mock_healthy_client.pipeline.return_value = mock_pipe

    with patch.object(backend, "_get_client", return_value=mock_healthy_client):
        res2 = backend.check_rate_limit("auth:login:u5", max_requests=5, window_seconds=60, fail_mode="fail_closed")
        assert res2.allowed is True
        assert res2.service_unavailable is False
        assert res2.remaining == 4


def test_fail_closed_http_503_and_no_secret_leakage():
    """Verifies that fail_closed returns HTTP 503 without leaking credentials or stack traces."""
    from backend.app.core.exceptions import ServiceUnavailableException
    test_app = FastAPI()

    @test_app.exception_handler(ServiceUnavailableException)
    async def service_unavailable_handler(request: Request, exc: ServiceUnavailableException):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={"detail": exc.message, "error_type": "ServiceUnavailableException"},
            headers={"Retry-After": "60"},
        )

    # Broken Redis backend with credentials in URL
    unreachable_backend = RedisRateLimiterBackend(
        "rediss://default:supersecretpassword123@fake-cluster.upstash.io:6379",
        connection_timeout_seconds=0.05
    )
    unreachable_backend._client = None
    with patch.object(unreachable_backend, "_get_client", return_value=None):
        from backend.app.core.rate_limit import rate_limiter
        old_backend = rate_limiter.backend
        try:
            rate_limiter.set_backend(unreachable_backend)

            @test_app.post("/auth/sensitive-login", dependencies=[Depends(rate_limit(max_requests=5, window_seconds=60, endpoint_group="auth_login", fail_mode="fail_closed"))])
            def sensitive_login():
                return {"token": "should_never_reach_here"}

            client = TestClient(test_app)
            resp = client.post("/auth/sensitive-login")

            assert resp.status_code == 503
            assert "Retry-After" in resp.headers
            resp_text = resp.text
            # Absolute secret protection verification:
            assert "supersecretpassword123" not in resp_text
            assert "fake-cluster.upstash.io" not in resp_text
            assert "rediss://" not in resp_text
            assert "RateLimiter" in resp_text or "unavailable" in resp_text.lower()
        finally:
            rate_limiter.set_backend(old_backend)


def test_health_endpoint_remains_accessible_during_redis_outage(client: TestClient):
    """Verifies that infrastructure health checks (/health) do not fail when Redis rate limiter is down."""
    from backend.app.core.rate_limit import rate_limiter
    old_backend = rate_limiter.backend
    try:
        broken_backend = RedisRateLimiterBackend("redis://broken:6379")
        broken_backend._client = None
        with patch.object(broken_backend, "_get_client", return_value=None):
            rate_limiter.set_backend(broken_backend)
            resp = client.get("/health")
            assert resp.status_code == 200
            assert resp.json()["status"] == "HEALTHY"
    finally:
        rate_limiter.set_backend(old_backend)


def test_rate_limit_fastapi_dependency():
    """Tests rate limit HTTP behavior and headers in a live FastAPI app."""
    test_app = FastAPI()

    @test_app.exception_handler(RateLimitExceededException)
    async def rate_limit_handler(request: Request, exc: RateLimitExceededException):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=429,
            content={"detail": exc.message, "retry_after": exc.retry_after},
            headers={"Retry-After": str(exc.retry_after)},
        )

    # Clean backend
    test_limiter = InMemoryRateLimiterBackend()
    from backend.app.core.rate_limit import rate_limiter
    rate_limiter.set_backend(test_limiter)

    @test_app.get("/test-limited", dependencies=[Depends(rate_limit(max_requests=2, window_seconds=10, endpoint_group="test_api"))])
    def limited_endpoint():
        return {"status": "ok"}

    client = TestClient(test_app)

    # Req 1: OK
    resp1 = client.get("/test-limited")
    assert resp1.status_code == 200
    assert resp1.headers["X-RateLimit-Limit"] == "2"
    assert resp1.headers["X-RateLimit-Remaining"] == "1"

    # Req 2: OK
    resp2 = client.get("/test-limited")
    assert resp2.status_code == 200
    assert resp2.headers["X-RateLimit-Remaining"] == "0"

    # Req 3: 429 Too Many Requests
    resp3 = client.get("/test-limited")
    assert resp3.status_code == 429
    assert "Retry-After" in resp3.headers
    assert "Rate limit exceeded" in resp3.json()["detail"]
