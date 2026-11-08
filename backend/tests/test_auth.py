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
