"""
Tests for KisanVision Model Architecture & Calibrated Uncertainty.
"""

import torch
from ml.models.classifier import KisanVisionClassifier


def test_mobilenet_forward_and_output_shape():
    batch_size = 4
    num_classes = 8
    model = KisanVisionClassifier(
        architecture="mobilenet_v3_small",
        num_classes=num_classes,
        pretrained=False
    )
    
    # Synthetic batch of images [B, C, H, W]
    dummy_input = torch.randn(batch_size, 3, 224, 224)
    logits = model(dummy_input)
    
    assert logits.shape == (batch_size, num_classes)


def test_calibrated_uncertainty_and_probabilities():
    model = KisanVisionClassifier(
        architecture="mobilenet_v3_small",
        num_classes=5,
        pretrained=False
    )
    
    dummy_input = torch.randn(2, 3, 224, 224)
    probs = model.predict_proba(dummy_input)
    
    # Probabilities must sum to 1.0 along class dimension
    assert torch.allclose(torch.sum(probs, dim=-1), torch.ones(2), atol=1e-5)
    
    logits = model(dummy_input)
    top_conf, norm_entropy = model.compute_uncertainty(logits)
    
    assert top_conf.shape == (2,)
    assert norm_entropy.shape == (2,)
    # Normalized entropy is bounded in [0, 1]
    assert (norm_entropy >= 0.0).all() and (norm_entropy <= 1.01).all()


def test_parameter_counts():
    model = KisanVisionClassifier(architecture="mobilenet_v3_small", num_classes=10)
    counts = model.get_parameter_counts()
    assert counts["total_parameters"] > 1_000_000
    assert counts["trainable_parameters"] + counts["frozen_parameters"] == counts["total_parameters"]
    assert counts["frozen_parameters"] == 1  # 1 non-trainable temperature parameter
