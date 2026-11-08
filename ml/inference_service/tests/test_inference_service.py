"""
Tests for KisanVision Dedicated ML Inference Service.
Verifies health, model inventory, input validation, quality rejection,
OOD detection, and structured differential diagnosis responses.
"""

import io
import pytest
import numpy as np
from PIL import Image, ImageFilter
from fastapi.testclient import TestClient

from ml.inference_service.app.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture
def valid_leaf_image_bytes():
    """Generates a synthetic clear leaf image with sharp textures."""
    np_img = np.zeros((300, 300, 3), dtype=np.uint8)
    np_img[:, :, 0] = 50   # Red
    np_img[:, :, 1] = 160  # Green
    np_img[:, :, 2] = 40   # Blue
    
    pattern = (np.arange(300)[:, None] % 20 > 10).astype(np.uint8) * 60
    np_img[:, :, 1] = np.clip(np_img[:, :, 1] + pattern, 0, 255)
    
    buf = io.BytesIO()
    Image.fromarray(np_img).save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def blurry_leaf_image_bytes():
    """Generates a blurry leaf image."""
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
    """Generates a textured non-plant image (blue & white checkerboard)."""
    np_img = np.zeros((300, 300, 3), dtype=np.uint8)
    checker = ((np.arange(300)[:, None] // 20 + np.arange(300)[None, :] // 20) % 2 == 0)
    np_img[checker] = [240, 240, 240]
    np_img[~checker] = [20, 40, 220]
    
    buf = io.BytesIO()
    Image.fromarray(np_img).save(buf, format="JPEG")
    return buf.getvalue()


def test_service_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "cotton" in data["supported_crops"]


def test_service_model_info(client):
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["architecture"] == "mobilenet_v3_small"
    assert data["quantization"] == "INT8_DYNAMIC"
    assert "cotton" in data["active_models"]
    assert "rice" in data["active_models"]
    assert "chilli" in data["active_models"]


def test_service_predict_valid_leaf(client, valid_leaf_image_bytes):
    response = client.post(
        "/api/v1/predict",
        data={"crop_type": "cotton", "language": "te"},
        files={"image": ("cotton_leaf.jpg", valid_leaf_image_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["crop"] == "cotton"
    assert "request_id" in data
    assert data["image_quality"]["is_acceptable"] is True
    assert data["ood_status"]["is_foliar_verified"] is True
    assert len(data["predictions"]) > 0
    assert "CIBRC" in data["safety_guideline"]


def test_service_predict_blurry_rejection(client, blurry_leaf_image_bytes):
    response = client.post(
        "/api/v1/predict",
        data={"crop_type": "rice"},
        files={"image": ("blurry.jpg", blurry_leaf_image_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "IMAGE_QUALITY_INSUFFICIENT"
    assert data["image_quality"]["is_acceptable"] is False


def test_service_predict_non_plant_ood_rejection(client, non_plant_image_bytes):
    response = client.post(
        "/api/v1/predict",
        data={"crop_type": "chilli"},
        files={"image": ("checker.jpg", non_plant_image_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OUT_OF_DISTRIBUTION"
    assert data["ood_status"]["is_foliar_verified"] is False


def test_service_predict_unsupported_crop(client, valid_leaf_image_bytes):
    response = client.post(
        "/api/v1/predict",
        data={"crop_type": "apple"},
        files={"image": ("leaf.jpg", valid_leaf_image_bytes, "image/jpeg")}
    )
    assert response.status_code == 400
    assert "Unsupported crop" in response.json()["detail"]


def test_service_predict_corrupt_file(client):
    response = client.post(
        "/api/v1/predict",
        data={"crop_type": "cotton"},
        files={"image": ("bad.jpg", b"MALFORMED_DATA", "image/jpeg")}
    )
    # Rejection caught by ImageIngestionValidator
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PROCESSING_FAILED"
    assert "Unsupported or disguised" in data["image_quality"]["error"]
