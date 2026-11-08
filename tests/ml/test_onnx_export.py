"""
Tests for ONNX Export, INT8 Dynamic Quantization, and Numerical Parity.
"""

import pytest
import torch
from pathlib import Path
from ml.models.classifier import KisanVisionClassifier
from ml.models.export_onnx import ONNXModelExporter


@pytest.fixture
def test_export_dir(tmp_path):
    return tmp_path / "onnx_exports"


def test_fp32_export_and_validation(test_export_dir):
    exporter = ONNXModelExporter(export_dir=str(test_export_dir))
    model = KisanVisionClassifier(architecture="mobilenet_v3_small", num_classes=5, pretrained=False)

    fp32_path = exporter.export_fp32(model, "test_mobilenet")
    assert fp32_path.exists()
    assert fp32_path.suffix == ".onnx"

    # Parity check
    parity = exporter.verify_parity(model, fp32_path, test_samples=3)
    assert parity["verification_passed"] is True
    assert parity["max_absolute_difference"] < 1e-4
    assert parity["top1_agreement_rate"] == 1.0


def test_int8_quantization_and_size_budget(test_export_dir):
    exporter = ONNXModelExporter(export_dir=str(test_export_dir))
    model = KisanVisionClassifier(architecture="mobilenet_v3_small", num_classes=5, pretrained=False)

    fp32_path = exporter.export_fp32(model, "test_mobilenet_q")
    int8_path = exporter.quantize_int8(fp32_path)

    assert int8_path.exists()
    assert int8_path.stat().st_size > 0

    # Size check: must be well below 15MB edge budget (MobileNetV3-Small INT8 is typically < 5MB)
    size_mb = int8_path.stat().st_size / (1024 * 1024)
    assert size_mb < 15.0

    # Quantization parity: Cosine similarity should remain high (>= 0.98)
    q_parity = exporter.verify_parity(model, int8_path, test_samples=5)
    assert q_parity["mean_cosine_similarity"] >= 0.98
    assert q_parity["verification_passed"] is True


def test_export_and_quantize_manifest(test_export_dir):
    exporter = ONNXModelExporter(export_dir=str(test_export_dir))
    model = KisanVisionClassifier(architecture="mobilenet_v3_small", num_classes=3, pretrained=False)
    classes = ["cotton_healthy", "cotton_bacterial_blight", "cotton_bollworm"]

    result = exporter.export_and_quantize(
        model=model,
        model_name="cotton_test",
        class_names=classes,
        crop_type="cotton"
    )

    manifest_path = Path(result["manifest_path"])
    assert manifest_path.exists()
    assert result["manifest"]["crop_type"] == "cotton"
    assert result["manifest"]["num_classes"] == 3
    assert result["manifest"]["compression_ratio"] >= 1.0
