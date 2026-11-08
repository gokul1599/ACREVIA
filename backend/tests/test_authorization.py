"""
ACREVIA Backend - Multi-Tenant Authorization & Farm Boundary Test Suite.
Verifies that cross-tenant access attempts are strictly rejected with HTTP 403 Forbidden.
"""

from fastapi.testclient import TestClient


def test_owner_can_access_own_farm(client: TestClient, sample_farm, farmer_token):
    headers = {"Authorization": f"Bearer {farmer_token}"}
    resp = client.get(f"/api/v1/farms/{sample_farm.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == sample_farm.id


def test_cross_farm_read_blocked(client: TestClient, sample_farm, second_farmer_token):
    """
    SECURITY TEST: Farmer B attempts to access Farmer A's farm.
    Must return HTTP 403 Forbidden.
    """
    headers = {"Authorization": f"Bearer {second_farmer_token}"}
    resp = client.get(f"/api/v1/farms/{sample_farm.id}", headers=headers)
    assert resp.status_code == 403
    assert "forbidden" in resp.json()["detail"].lower()


def test_cross_farm_plot_creation_blocked(client: TestClient, sample_farm, second_farmer_token):
    """
    SECURITY TEST: Farmer B attempts to create a plot in Farmer A's farm.
    Must return HTTP 403 Forbidden.
    """
    headers = {"Authorization": f"Bearer {second_farmer_token}"}
    payload = {
        "name": "Unauthorized Plot",
        "soil_type": "BLACK_COTTON",
        "irrigation_source": "BOREWELL",
        "acreage": 1.0
    }
    resp = client.post(f"/api/v1/farms/{sample_farm.id}/plots", json=payload, headers=headers)
    assert resp.status_code == 403


def test_cross_farm_observation_blocked(client: TestClient, sample_farm, second_farmer_token):
    """
    SECURITY TEST: Farmer B attempts to create an observation in Farmer A's farm.
    Must return HTTP 403 Forbidden.
    """
    headers = {"Authorization": f"Bearer {second_farmer_token}"}
    payload = {
        "farm_id": sample_farm.id,
        "notes": "Attempting cross-farm observation injection"
    }
    resp = client.post("/api/v1/observations/", json=payload, headers=headers)
    assert resp.status_code == 403


def test_cross_farm_observation_listing_blocked(client: TestClient, sample_farm, second_farmer_token):
    """
    SECURITY TEST: Farmer B attempts to list observations of Farmer A's farm.
    Must return HTTP 403 Forbidden.
    """
    headers = {"Authorization": f"Bearer {second_farmer_token}"}
    resp = client.get(f"/api/v1/observations/?farm_id={sample_farm.id}", headers=headers)
    assert resp.status_code == 403


def test_admin_can_access_any_farm(client: TestClient, sample_farm, admin_token):
    """
    Platform administrator possesses superuser bypass to review any farm holding.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get(f"/api/v1/farms/{sample_farm.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == sample_farm.id


def test_membership_grants_access(client: TestClient, sample_farm, farmer_token, second_farmer_user, second_farmer_token):
    """
    When Farmer A invites Farmer B as a collaborator, Farmer B can now access the farm.
    """
    # 1. Farmer A adds Farmer B as WORKER
    headers_a = {"Authorization": f"Bearer {farmer_token}"}
    add_payload = {
        "user_id": second_farmer_user.id,
        "role_in_farm": "WORKER"
    }
    add_resp = client.post(f"/api/v1/farms/{sample_farm.id}/memberships", json=add_payload, headers=headers_a)
    assert add_resp.status_code == 201

    # 2. Farmer B can now access the farm
    headers_b = {"Authorization": f"Bearer {second_farmer_token}"}
    read_resp = client.get(f"/api/v1/farms/{sample_farm.id}", headers=headers_b)
    assert read_resp.status_code == 200
    assert read_resp.json()["id"] == sample_farm.id
