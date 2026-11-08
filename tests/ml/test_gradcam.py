"""
Tests for Grad-CAM Explainability & Saliency Inspection.
"""

import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from ml.evaluation.gradcam import GradCAMExplainer


def test_gradcam_computation():
    # Simple CNN with Conv2d and Linear head
    class SimpleConvNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv = nn.Conv2d(3, 16, kernel_size=3, padding=1)
            self.relu = nn.ReLU()
            self.pool = nn.AdaptiveAvgPool2d((1, 1))
            self.fc = nn.Linear(16, 2)

        def forward(self, x):
            x = self.relu(self.conv(x))
            x = self.pool(x)
            x = torch.flatten(x, 1)
            return self.fc(x)

    model = SimpleConvNet()
    explainer = GradCAMExplainer(model=model, target_layer=model.conv)

    dummy_input = torch.randn(1, 3, 32, 32, requires_grad=True)
    cam = explainer.generate_cam(dummy_input, target_class_idx=0)

    assert isinstance(cam, np.ndarray)
    assert cam.shape == (32, 32)
    assert np.all(cam >= 0.0)
    assert np.max(cam) <= 1.0


def test_gradcam_overlay():
    pil_img = Image.new("RGB", (64, 64), (40, 160, 50))
    heatmap = np.random.uniform(0.0, 1.0, (16, 16))

    blended = GradCAMExplainer.overlay_heatmap(pil_img, heatmap, alpha=0.4)
    assert isinstance(blended, Image.Image)
    assert blended.size == (64, 64)
