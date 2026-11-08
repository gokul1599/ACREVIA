"""
ACREVIA Backend - AI Diagnoses & Expert Reviews Test Suite.
"""

from fastapi.testclient import TestClient


def test_diagnosis_workflow(
    client: TestClient,
    sample_farm,
    farmer_token,
    sample_image_bytes
):
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Create observation & media
    obs_id = client.post("/api/v1/observations/", json={"farm_id": sample_farm.id}, headers=headers).json()["id"]
    media_id = client.post(
        f"/api/v1/observations/{obs_id}/media",
        files={"file": ("foliar.jpg", sample_image_bytes, "image/jpeg")},
        headers=headers
    ).json()["id"]

    # 2. Request AI diagnosis
    diag_payload = {
        "observation_id": obs_id,
        "media_id": media_id,
        "crop_type": "cotton",
        "language": "te"
    }
    diag_resp = client.post("/api/v1/diagnoses/", json=diag_payload, headers=headers)
    assert diag_resp.status_code == 201
    diag_data = diag_resp.json()
    assert diag_data["observation_id"] == obs_id
    assert diag_data["status"] in ["COMPLETED", "NEEDS_REVIEW"]
    assert diag_data["prediction"] is not None
    assert len(diag_data["prediction"]["candidates"]) >= 1
    assert "cibrc_advisory" in diag_data["prediction"]

    # 3. Retrieve diagnosis by ID
    diag_id = diag_data["id"]
    get_resp = client.get(f"/api/v1/diagnoses/{diag_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == diag_id


def test_expert_review_workflow(
    client: TestClient,
    sample_farm,
    farmer_token,
    expert_token,
    sample_image_bytes
):
    headers_farmer = {"Authorization": f"Bearer {farmer_token}"}
    headers_expert = {"Authorization": f"Bearer {expert_token}"}

    # 1. Create diagnosis request
    obs_id = client.post("/api/v1/observations/", json={"farm_id": sample_farm.id}, headers=headers_farmer).json()["id"]
    client.post(
        f"/api/v1/observations/{obs_id}/media",
        files={"file": ("foliar.jpg", sample_image_bytes, "image/jpeg")},
        headers=headers_farmer
    )
    diag_id = client.post(
        "/api/v1/diagnoses/",
        json={"observation_id": obs_id, "crop_type": "cotton", "language": "te"},
        headers=headers_farmer
    ).json()["id"]

    # 2. Expert reviews and validates diagnosis
    review_payload = {
        "status": "CONFIRMED",
        "verified_class_id": "cotton_cercospora_leaf_spot",
        "expert_notes": "Clinical leaf spot morphology matches Cercospora gossypina. Recommend field drainage."
    }
    review_resp = client.post(f"/api/v1/diagnoses/{diag_id}/expert-review", json=review_payload, headers=headers_expert)
    assert review_resp.status_code == 201
    review_data = review_resp.json()
    assert review_data["status"] == "CONFIRMED"
    assert review_data["verified_class_id"] == "cotton_cercospora_leaf_spot"


def test_farmer_cannot_submit_expert_review(
    client: TestClient,
    sample_farm,
    farmer_token,
    sample_image_bytes
):
    headers_farmer = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Create diagnosis request
    obs_id = client.post("/api/v1/observations/", json={"farm_id": sample_farm.id}, headers=headers_farmer).json()["id"]
    client.post(
        f"/api/v1/observations/{obs_id}/media",
        files={"file": ("foliar.jpg", sample_image_bytes, "image/jpeg")},
        headers=headers_farmer
    )
    diag_id = client.post(
        "/api/v1/diagnoses/",
        json={"observation_id": obs_id, "crop_type": "cotton"},
        headers=headers_farmer
    ).json()["id"]

    # 2. Regular farmer attempts to submit expert review -> HTTP 403 Forbidden
    review_payload = {
        "status": "CONFIRMED",
        "verified_class_id": "cotton_healthy"
    }
    unauthorized_resp = client.post(
        f"/api/v1/diagnoses/{diag_id}/expert-review",
        json=review_payload,
        headers=headers_farmer
    )
    assert unauthorized_resp.status_code == 403
