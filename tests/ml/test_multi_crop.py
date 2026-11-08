"""
Tests for Multi-Crop Hierarchical Vision Architecture.
"""

import pytest
import torch
from ml.models.multi_crop import MultiCropKisanVisionClassifier


def test_multicrop_classifier_initialization():
    model = MultiCropKisanVisionClassifier(
        architecture="mobilenet_v3_small",
        crop_class_counts={"cotton": 10, "rice": 10, "chilli": 8},
        pretrained=False
    )
    assert len(model.heads) == 3
    assert "cotton" in model.heads
    assert "rice" in model.heads
    assert "chilli" in model.heads
    assert model.crop_gate_head is not None


def test_multicrop_forward_with_crop_context():
    model = MultiCropKisanVisionClassifier(
        architecture="mobilenet_v3_small",
        crop_class_counts={"cotton": 10, "rice": 10, "chilli": 8},
        pretrained=False
    )
    model.eval()
    dummy_input = torch.randn(2, 3, 224, 224)

    # Test Cotton Head
    cotton_logits = model(dummy_input, crop_type="cotton")
    assert cotton_logits.shape == (2, 10)

    # Test Rice Head
    rice_logits = model(dummy_input, crop_type="rice")
    assert rice_logits.shape == (2, 10)

    # Test Chilli Head
    chilli_logits = model(dummy_input, crop_type="chilli")
    assert chilli_logits.shape == (2, 8)


def test_multicrop_forward_autonomous_mode():
    model = MultiCropKisanVisionClassifier(
        architecture="mobilenet_v3_small",
        crop_class_counts={"cotton": 10, "rice": 10, "chilli": 8},
        pretrained=False
    )
    model.eval()
    dummy_input = torch.randn(2, 3, 224, 224)

    outputs = model(dummy_input, crop_type=None)
    assert "crop_gate_logits" in outputs
    assert outputs["crop_gate_logits"].shape == (2, 4)  # 3 crops + 1 unknown
    assert "cotton" in outputs
    assert "rice" in outputs
    assert "chilli" in outputs


def test_multicrop_calibrated_uncertainty():
    model = MultiCropKisanVisionClassifier(
        architecture="mobilenet_v3_small",
        crop_class_counts={"cotton": 10, "rice": 10, "chilli": 8},
        pretrained=False
    )
    model.eval()
    dummy_input = torch.randn(1, 3, 224, 224)

    probs, conf, norm_entropy = model.predict_calibrated(dummy_input, crop_type="cotton")
    assert probs.shape == (1, 10)
    assert torch.allclose(torch.sum(probs, dim=-1), torch.tensor([1.0]), atol=1e-4)
    assert 0.0 <= float(conf.item()) <= 1.0
    assert 0.0 <= float(norm_entropy.item()) <= 1.0


def test_multicrop_parameter_breakdown():
    model = MultiCropKisanVisionClassifier(
        architecture="mobilenet_v3_small",
        crop_class_counts={"cotton": 10, "rice": 10, "chilli": 8},
        pretrained=False
    )
    breakdown = model.get_parameter_breakdown()
    assert breakdown["shared_backbone_parameters"] > 0
    assert breakdown["crop_gate_parameters"] > 0
    assert "cotton" in breakdown["crop_head_parameters"]
    assert breakdown["total_parameters"] > breakdown["shared_backbone_parameters"]
