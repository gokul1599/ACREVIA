"""
ACREVIA Backend - Authentication & User Registration Test Suite.
"""

from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    payload = {
        "phone": "+919777888999",
        "full_name": "Kavitha Devi",
        "password": "SecurePassword123!",
        "email": "kavitha@example.com",
        "language_preference": "te",
        "role": "FARMER"
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["phone"] == "+919777888999"
    assert data["full_name"] == "Kavitha Devi"
    assert "FARMER" in data["roles"]
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_phone(client: TestClient, farmer_user):
    payload = {
        "phone": farmer_user.phone,
        "full_name": "Duplicate Farmer",
        "password": "AnotherPassword123!",
        "language_preference": "te",
        "role": "FARMER"
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409


def test_login_success(client: TestClient, farmer_user):
    payload = {
        "phone": farmer_user.phone,
        "password": "Acrevia@2026"
    }
    resp = client.post("/api/v1/auth/login", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["id"] == farmer_user.id
    assert "FARMER" in data["user"]["roles"]


def test_login_invalid_password(client: TestClient, farmer_user):
    payload = {
        "phone": farmer_user.phone,
        "password": "WrongPassword!"
    }
    resp = client.post("/api/v1/auth/login", json=payload)
    assert resp.status_code == 401


def test_get_current_user_me(client: TestClient, farmer_token, farmer_user):
    headers = {"Authorization": f"Bearer {farmer_token}"}
    resp = client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == farmer_user.id
    assert data["phone"] == farmer_user.phone


def test_get_me_unauthorized(client: TestClient):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_auth_login_fail_closed_when_redis_unreachable(client: TestClient, farmer_user):
    """Verifies that /auth/login returns HTTP 503 when Redis rate limiter is down."""
    from unittest.mock import patch
    from backend.app.core.rate_limit import RedisRateLimiterBackend, rate_limiter
    old_backend = rate_limiter.backend
    try:
        broken_backend = RedisRateLimiterBackend("redis://fake-redis-host:6379", connection_timeout_seconds=0.01)
        with patch.object(broken_backend, "_get_client", return_value=None):
            rate_limiter.set_backend(broken_backend)
            payload = {"phone": farmer_user.phone, "password": "Acrevia@2026"}
            resp = client.post("/api/v1/auth/login", json=payload)
            assert resp.status_code == 503
            assert "Retry-After" in resp.headers
            assert "RateLimiter" in resp.json()["detail"] or "unavailable" in resp.json()["detail"].lower()
    finally:
        rate_limiter.set_backend(old_backend)


def test_auth_register_fail_closed_when_redis_unreachable(client: TestClient):
    """Verifies that /auth/register returns HTTP 503 when Redis rate limiter is down."""
    from unittest.mock import patch
    from backend.app.core.rate_limit import RedisRateLimiterBackend, rate_limiter
    old_backend = rate_limiter.backend
    try:
        broken_backend = RedisRateLimiterBackend("redis://fake-redis-host:6379", connection_timeout_seconds=0.01)
        with patch.object(broken_backend, "_get_client", return_value=None):
            rate_limiter.set_backend(broken_backend)
            payload = {
                "phone": "+919888877777",
                "full_name": "Test FailClosed",
                "password": "Password123!",
                "language_preference": "te",
                "role": "FARMER"
            }
            resp = client.post("/api/v1/auth/register", json=payload)
            assert resp.status_code == 503
            assert "Retry-After" in resp.headers
            assert "RateLimiter" in resp.json()["detail"] or "unavailable" in resp.json()["detail"].lower()
    finally:
        rate_limiter.set_backend(old_backend)


def test_auth_login_quota_exceeded_returns_http_429(client: TestClient, farmer_user):
    """
    Verifies that exceeding the 5 requests/min rate limit quota on /auth/login
    returns HTTP 429 Too Many Requests (distinguished from HTTP 503 dependency failure).
    """
    from backend.app.core.rate_limit import InMemoryRateLimiterBackend, rate_limiter
    old_backend = rate_limiter.backend
    test_limiter = InMemoryRateLimiterBackend()
    try:
        rate_limiter.set_backend(test_limiter)
        payload = {"phone": farmer_user.phone, "password": "WrongPassword!"}

        # First 5 attempts: return 401 Unauthorized (credentials invalid, but allowed by rate limiter)
        for _ in range(5):
            resp = client.post("/api/v1/auth/login", json=payload)
            assert resp.status_code == 401

        # 6th attempt: quota exceeded, must return HTTP 429 Too Many Requests
        resp_blocked = client.post("/api/v1/auth/login", json=payload)
        assert resp_blocked.status_code == 429
        assert "Retry-After" in resp_blocked.headers
        assert "Rate limit exceeded" in resp_blocked.json()["detail"]
    finally:
        rate_limiter.set_backend(old_backend)


def test_auth_routes_registry_verification(client: TestClient):
    """
    Verifies that POST /api/v1/auth/login is explicitly registered in FastAPI's
    master OpenAPI schema and route table with expected HTTP POST method.
    """
    from backend.app.main import app
    openapi = app.openapi()
    paths = openapi.get("paths", {})
    assert "/api/v1/auth/login" in paths
    assert "post" in paths["/api/v1/auth/login"]
    assert "/api/v1/auth/register" in paths
    assert "post" in paths["/api/v1/auth/register"]
    assert "/api/v1/auth/me" in paths
    assert "get" in paths["/api/v1/auth/me"]


def test_auth_login_method_not_allowed(client: TestClient):
    """
    Verifies that attempting GET on /api/v1/auth/login returns HTTP 405 Method Not Allowed,
    confirming the endpoint only accepts POST credentials.
    """
    resp = client.get("/api/v1/auth/login")
    assert resp.status_code == 405


def test_auth_login_not_found_on_duplicate_prefix(client: TestClient):
    """
    Verifies that requesting a malformed path such as /api/v1/api/v1/auth/login returns
    HTTP 404 with structured JSON, demonstrating how misconfigured base URLs produce 404s.
    """
    resp = client.post("/api/v1/api/v1/auth/login", json={"phone": "+919000000000", "password": "pass"})
    assert resp.status_code == 404
    data = resp.json()
    assert data.get("detail") == "Not Found"


def test_auth_synthetic_farmer_login_lifecycle(client: TestClient):
    """
    Executes a complete synthetic authentication lifecycle:
    1. Register synthetic farmer
    2. Attempt login with invalid password (verify 401 with structured detail)
    3. Attempt login with valid password (verify 200, JWT token, user payload)
    4. Access /auth/me with bearer token (verify 200)
    """
    phone = "+919999111222"
    password = "CorrectHorseBattery99!"

    # 1. Register synthetic user
    reg_resp = client.post("/api/v1/auth/register", json={
        "phone": phone,
        "full_name": "Synthetic Test Farmer",
        "password": password,
        "language_preference": "te",
        "role": "FARMER"
    })
    assert reg_resp.status_code == 201

    # 2. Login with wrong password
    bad_login = client.post("/api/v1/auth/login", json={
        "phone": phone,
        "password": "WrongPassword99!"
    })
    assert bad_login.status_code == 401
    assert "Invalid phone/email or password." in bad_login.json()["detail"]

    # 3. Login with correct password
    good_login = client.post("/api/v1/auth/login", json={
        "phone": phone,
        "password": password
    })
    assert good_login.status_code == 200
    token_data = good_login.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["user"]["phone"] == phone
    assert token_data["user"]["full_name"] == "Synthetic Test Farmer"
    assert "FARMER" in token_data["user"]["roles"]

    # 4. Verify token access on /auth/me
    token = token_data["access_token"]
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["id"] == token_data["user"]["id"]


