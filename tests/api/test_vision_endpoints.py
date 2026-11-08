"""
Automated Integration Tests for KisanVision API Endpoints.
Verifies health probes, model listing, image quality gating, OOD detection,
and foliar disease diagnosis responses.
"""

import io
import pytest
import numpy as np
from PIL import Image, ImageFilter
from fastapi.testclient import TestClient

from apps.api.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture
def valid_leaf_image_bytes():
    """Generates a synthetic clear foliar leaf image with sharp textures."""
    np_img = np.zeros((300, 300, 3), dtype=np.uint8)
    np_img[:, :, 0] = 50   # Red
    np_img[:, :, 1] = 160  # Green
    np_img[:, :, 2] = 40   # Blue
    
    # Add high-frequency edge texture for high Laplacian sharpness
    pattern = (np.arange(300)[:, None] % 20 > 10).astype(np.uint8) * 60
    np_img[:, :, 1] = np.clip(np_img[:, :, 1] + pattern, 0, 255)
    
    buf = io.BytesIO()
    Image.fromarray(np_img).save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def blurry_leaf_image_bytes():
    """Generates a severely blurry leaf image to trigger quality filter rejection."""
    np_img = np.zeros((300, 300, 3), dtype=np.uint8)
    np_img[:, :, 0] = 50
    np_img[:, :, 1] = 160
    np_img[:, :, 2] = 40
    
    pil_img = Image.fromarray(np_img).filter(ImageFilter.GaussianBlur(radius=15))
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def non_plant_image_bytes():
    """Generates a sharp non-plant checkered image to trigger Tier 1 OOD rejection."""
    np_img = np.zeros((300, 300, 3), dtype=np.uint8)
    checker = ((np.arange(300)[:, None] // 20 + np.arange(300)[None, :] // 20) % 2 == 0)
    np_img[checker] = [240, 240, 240]  # White
    np_img[~checker] = [20, 40, 220]   # Blue
    
    buf = io.BytesIO()
    Image.fromarray(np_img).save(buf, format="JPEG")
    return buf.getvalue()


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OPERATIONAL"
    assert "KisanVision" in data["platform"]


def test_health_probe(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "cotton" in data["supported_crops"]
    assert data["uptime_seconds"] >= 0


def test_list_vision_models(client):
    response = client.get("/api/v1/vision/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # cotton, rice, chilli
    
    crops = [m["crop_type"] for m in data]
    assert "cotton" in crops
    assert "rice" in crops
    assert "chilli" in crops
    assert all(m["quantization"] == "INT8_DYNAMIC" for m in data)


def test_predict_valid_leaf(client, valid_leaf_image_bytes):
    response = client.post(
        "/api/v1/vision/predict",
        data={"crop_type": "cotton", "language": "te"},
        files={"image": ("test_leaf.jpg", valid_leaf_image_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["crop_type"] == "cotton"
    assert "request_id" in data
    assert data["image_quality"]["is_acceptable"] is True
    assert data["foliar_assessment"]["is_foliar"] is True
    assert "differential_candidates" in data
    assert len(data["differential_candidates"]) > 0
    assert "CIBRC" in data["safety_guideline"]


def test_predict_blurry_image_rejection(client, blurry_leaf_image_bytes):
    response = client.post(
        "/api/v1/vision/predict",
        data={"crop_type": "rice"},
        files={"image": ("blurry.jpg", blurry_leaf_image_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Blurry image must be rejected at image quality gate
    assert data["status"] == "QUALITY_REJECTED"
    assert data["triage_level"] == "RETAKE_IMAGE"
    assert data["image_quality"]["is_acceptable"] is False
    assert len(data["image_quality"]["corrective_guidance"]) > 0


def test_predict_non_plant_ood_rejection(client, non_plant_image_bytes):
    response = client.post(
        "/api/v1/vision/predict",
        data={"crop_type": "chilli"},
        files={"image": ("metal_sheet.jpg", non_plant_image_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Non-plant image must be rejected at Tier 1 OOD gate
    assert data["status"] == "OOD_NON_PLANT"
    assert data["triage_level"] == "RETAKE_IMAGE"
    assert data["foliar_assessment"]["is_foliar"] is False


def test_predict_unsupported_crop(client, valid_leaf_image_bytes):
    response = client.post(
        "/api/v1/vision/predict",
        data={"crop_type": "mango"},
        files={"image": ("leaf.jpg", valid_leaf_image_bytes, "image/jpeg")}
    )
    assert response.status_code == 400
    assert "Unsupported crop" in response.json()["detail"]


def test_predict_empty_image(client):
    response = client.post(
        "/api/v1/vision/predict",
        data={"crop_type": "cotton"},
        files={"image": ("empty.jpg", b"", "image/jpeg")}
    )
    assert response.status_code == 400
    assert "Uploaded file is empty" in response.json()["detail"]


def test_predict_corrupt_image(client):
    response = client.post(
        "/api/v1/vision/predict",
        data={"crop_type": "cotton"},
        files={"image": ("corrupt.jpg", b"NOT_AN_IMAGE_RANDOM_GARBAGE", "image/jpeg")}
    )
    assert response.status_code == 400
    assert "Corrupt or unreadable" in response.json()["detail"]
