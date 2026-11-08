"""
ACREVIA Backend - Agricultural Observations & Media Stream Test Suite.
"""

from fastapi.testclient import TestClient


def test_create_observation(client: TestClient, sample_farm, sample_plot, sample_season, farmer_token):
    headers = {"Authorization": f"Bearer {farmer_token}"}
    payload = {
        "farm_id": sample_farm.id,
        "plot_id": sample_plot.id,
        "crop_season_id": sample_season.id,
        "notes": "Red spots observed on lower canopy leaves",
        "symptom_tags": "leaf_spot,chlorosis"
    }
    resp = client.post("/api/v1/observations/", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["farm_id"] == sample_farm.id
    assert data["notes"] == "Red spots observed on lower canopy leaves"


def test_upload_media_and_quality_check(
    client: TestClient,
    sample_farm,
    farmer_token,
    sample_image_bytes
):
    headers = {"Authorization": f"Bearer {farmer_token}"}
    # 1. Create observation
    obs_resp = client.post("/api/v1/observations/", json={"farm_id": sample_farm.id}, headers=headers)
    assert obs_resp.status_code == 201
    obs_id = obs_resp.json()["id"]

    # 2. Upload foliar media
    files = {
        "file": ("leaf.jpg", sample_image_bytes, "image/jpeg")
    }
    media_resp = client.post(
        f"/api/v1/observations/{obs_id}/media",
        files=files,
        data={"is_primary": "true"},
        headers=headers
    )
    assert media_resp.status_code == 201
    media_data = media_resp.json()
    assert media_data["observation_id"] == obs_id
    assert media_data["mime_type"] == "image/jpeg"
    assert len(media_data["sha256_hash"]) == 64
    assert media_data["file_size_bytes"] == len(sample_image_bytes)


def test_get_media_stream_authorized_and_cross_tenant(
    client: TestClient,
    sample_farm,
    farmer_token,
    second_farmer_token,
    sample_image_bytes
):
    headers_a = {"Authorization": f"Bearer {farmer_token}"}
    headers_b = {"Authorization": f"Bearer {second_farmer_token}"}

    # 1. Create observation and upload media
    obs_id = client.post("/api/v1/observations/", json={"farm_id": sample_farm.id}, headers=headers_a).json()["id"]
    media_id = client.post(
        f"/api/v1/observations/{obs_id}/media",
        files={"file": ("leaf.jpg", sample_image_bytes, "image/jpeg")},
        headers=headers_a
    ).json()["id"]

    # 2. Farmer A (owner) can stream the image
    stream_resp = client.get(f"/api/v1/observations/{obs_id}/media/{media_id}/file", headers=headers_a)
    assert stream_resp.status_code == 200
    assert stream_resp.content == sample_image_bytes

    # 3. Farmer B (unauthorized) receives 403 Forbidden
    cross_resp = client.get(f"/api/v1/observations/{obs_id}/media/{media_id}/file", headers=headers_b)
    assert cross_resp.status_code == 403
