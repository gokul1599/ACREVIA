"""
ACREVIA Backend - Farms, Plots, Plants & Crop Seasons Test Suite.
"""

from fastapi.testclient import TestClient


def test_create_farm(client: TestClient, farmer_token):
    headers = {"Authorization": f"Bearer {farmer_token}"}
    payload = {
        "name": "Nalgonda Chilli Farm",
        "district": "Nalgonda",
        "mandal": "Miryalaguda",
        "village": "Alagadapa",
        "total_acreage": 4.5
    }
    resp = client.post("/api/v1/farms/", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Nalgonda Chilli Farm"
    assert data["district"] == "Nalgonda"
    assert data["total_acreage"] == 4.5


def test_list_farms(client: TestClient, sample_farm, farmer_token):
    headers = {"Authorization": f"Bearer {farmer_token}"}
    resp = client.get("/api/v1/farms/", headers=headers)
    assert resp.status_code == 200
    farms = resp.json()
    assert len(farms) >= 1
    assert any(f["id"] == sample_farm.id for f in farms)


def test_update_farm(client: TestClient, sample_farm, farmer_token):
    headers = {"Authorization": f"Bearer {farmer_token}"}
    payload = {
        "name": "Updated Warangal Cotton Farm",
        "total_acreage": 5.0
    }
    resp = client.put(f"/api/v1/farms/{sample_farm.id}", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Updated Warangal Cotton Farm"
    assert data["total_acreage"] == 5.0


def test_create_plot(client: TestClient, sample_farm, farmer_token):
    headers = {"Authorization": f"Bearer {farmer_token}"}
    payload = {
        "name": "South Plot - Chilli",
        "soil_type": "RED_CHALKA",
        "irrigation_source": "DRIP",
        "acreage": 1.5
    }
    resp = client.post(f"/api/v1/farms/{sample_farm.id}/plots", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "South Plot - Chilli"
    assert data["soil_type"] == "RED_CHALKA"


def test_list_plots(client: TestClient, sample_farm, sample_plot, farmer_token):
    headers = {"Authorization": f"Bearer {farmer_token}"}
    resp = client.get(f"/api/v1/farms/{sample_farm.id}/plots", headers=headers)
    assert resp.status_code == 200
    plots = resp.json()
    assert len(plots) >= 1
    assert any(p["id"] == sample_plot.id for p in plots)


def test_create_and_list_plant(client: TestClient, sample_plot, farmer_token):
    headers = {"Authorization": f"Bearer {farmer_token}"}
    payload = {
        "tag_code": "COT-PLT-001",
        "crop_id": "cotton",
        "notes": "Healthy vegetative specimen"
    }
    create_resp = client.post(f"/api/v1/plots/{sample_plot.id}/plants", json=payload, headers=headers)
    assert create_resp.status_code == 201
    assert create_resp.json()["tag_code"] == "COT-PLT-001"

    list_resp = client.get(f"/api/v1/plots/{sample_plot.id}/plants", headers=headers)
    assert list_resp.status_code == 200
    plants = list_resp.json()
    assert any(p["tag_code"] == "COT-PLT-001" for p in plants)


def test_create_season_and_stage_event(client: TestClient, sample_plot, farmer_token):
    headers = {"Authorization": f"Bearer {farmer_token}"}
    season_payload = {
        "plot_id": sample_plot.id,
        "crop_id": "cotton",
        "season_type": "KHARIF",
        "sowing_date": "2026-06-20",
        "current_stage": "SOWING"
    }
    season_resp = client.post(f"/api/v1/plots/{sample_plot.id}/seasons", json=season_payload, headers=headers)
    assert season_resp.status_code == 201
    season_data = season_resp.json()
    season_id = season_data["id"]

    event_payload = {
        "stage_name": "FLOWERING",
        "event_date": "2026-08-15",
        "notes": "First flush of flowering observed across plot"
    }
    event_resp = client.post(f"/api/v1/seasons/{season_id}/stage-events", json=event_payload, headers=headers)
    assert event_resp.status_code == 201
    assert event_resp.json()["stage_name"] == "FLOWERING"
