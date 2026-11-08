"""
ACREVIA Backend - System Health, Weather & Consent Governance Test Suite.
"""

from fastapi.testclient import TestClient


def test_health_and_ready(client: TestClient):
    h_resp = client.get("/health")
    assert h_resp.status_code == 200
    assert h_resp.json()["status"] == "HEALTHY"

    r_resp = client.get("/ready")
    assert r_resp.status_code == 200
    assert r_resp.json()["status"] == "READY"


def test_system_info(client: TestClient):
    resp = client.get("/api/v1/system/info")
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_name"] == "ACREVIA"
    assert "Telangana" in data["target_geography"]
    assert "cotton" in data["supported_crops"]
    assert "rice" in data["supported_crops"]
    assert "chilli" in data["supported_crops"]
    assert "te" in data["supported_languages"]


def test_system_integrations(client: TestClient):
    resp = client.get("/api/v1/system/integrations")
    assert resp.status_code == 200
    data = resp.json()
    assert "storage" in data
    assert "ml_inference_microservice" in data
    assert "weather_provider" in data


def test_farm_weather(client: TestClient, sample_farm, farmer_token):
    headers = {"Authorization": f"Bearer {farmer_token}"}
    resp = client.get(f"/api/v1/farms/{sample_farm.id}/weather", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["farm_id"] == sample_farm.id
    assert "temperature" in data
    assert "humidity" in data
    assert "advisory" in data


def test_consent_workflow(client: TestClient, farmer_token):
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Grant consent
    grant_payload = {
        "consent_type": "CORE_SERVICE",
        "is_granted": True,
        "policy_version": "1.0.0"
    }
    grant_resp = client.post("/api/v1/consent/", json=grant_payload, headers=headers)
    assert grant_resp.status_code == 201
    assert grant_resp.json()["is_granted"] is True

    # 2. Retrieve consent records
    list_resp = client.get("/api/v1/consent/", headers=headers)
    assert list_resp.status_code == 200
    consents = list_resp.json()
    assert any(c["consent_type"] == "CORE_SERVICE" and c["is_granted"] is True for c in consents)
