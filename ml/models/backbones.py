"""
KisanVision - Vision Model Backbones.
Provides standardized feature extractors adapted for resource-constrained edge and cloud execution.
"""

import torch
import torch.nn as nn
from torchvision import models
from typing import Tuple


def build_backbone(
    architecture: str = "mobilenet_v3_large",
    pretrained: bool = False
) -> Tuple[nn.Module, int]:
    """
    Constructs a vision backbone and returns (feature_extractor, embedding_dim).
    """
    arch = architecture.lower()
    
    if arch == "mobilenet_v3_large":
        weights = models.MobileNet_V3_Large_Weights.DEFAULT if pretrained else None
        base_model = models.mobilenet_v3_large(weights=weights)
        in_features = base_model.classifier[0].in_features
        base_model.classifier = nn.Identity()
        return base_model, in_features

    elif arch == "mobilenet_v3_small":
        weights = models.MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
        base_model = models.mobilenet_v3_small(weights=weights)
        in_features = base_model.classifier[0].in_features
        base_model.classifier = nn.Identity()
        return base_model, in_features

    elif arch == "resnet18":
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        base_model = models.resnet18(weights=weights)
        in_features = base_model.fc.in_features
        base_model.fc = nn.Identity()
        return base_model, in_features

    elif arch == "resnet50":
        weights = models.ResNet50_Weights.DEFAULT if pretrained else None
        base_model = models.resnet50(weights=weights)
        in_features = base_model.fc.in_features
        base_model.fc = nn.Identity()
        return base_model, in_features

    elif arch == "efficientnet_b0":
        weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        base_model = models.efficientnet_b0(weights=weights)
        in_features = base_model.classifier[1].in_features
        base_model.classifier = nn.Identity()
        return base_model, in_features

    else:
        raise ValueError(f"Unsupported architecture: '{architecture}'. Choose from: "
                         "['mobilenet_v3_large', 'mobilenet_v3_small', 'resnet18', 'resnet50', 'efficientnet_b0']")
