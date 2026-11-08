"""
Tests for Field Robustness & Agricultural Perturbation Harness.
"""

from PIL import Image
import numpy as np
import torch
import torch.nn as nn
from ml.evaluation.robustness import FieldRobustnessHarness


def test_robustness_perturbations():
    harness = FieldRobustnessHarness()
    raw_img = Image.new("RGB", (100, 100), (50, 150, 40))

    for pert in harness.perturbation_types:
        perturbed = harness.perturb_image(raw_img, pert, severity=1.0)
        assert isinstance(perturbed, Image.Image)
        assert perturbed.size == raw_img.size


def test_robustness_evaluation_runner():
    harness = FieldRobustnessHarness()
    
    # Simple dummy model
    class DummyModel(nn.Module):
        def forward(self, x):
            # Returns fixed logits favoring class 0
            return torch.tensor([[10.0, 1.0]])

    model = DummyModel()
    test_imgs = [Image.new("RGB", (64, 64), (50, 150, 40)) for _ in range(4)]
    labels = [0, 0, 0, 0]

    def dummy_preprocess(img):
        return torch.randn(1, 3, 64, 64)

    report = harness.evaluate_model_robustness(
        model=model,
        test_images=test_imgs,
        true_labels=labels,
        preprocess_fn=dummy_preprocess
    )

    assert "clean_accuracy" in report
    assert report["clean_accuracy"] == 1.0
    assert "perturbations" in report
    assert len(report["perturbations"]) == len(harness.perturbation_types)
