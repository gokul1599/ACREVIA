"""
KisanVision - Foliar Disease Classifier Architecture.
Modular PyTorch model with temperature-scaled uncertainty calibration and dropout regularization.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, Tuple

from ml.models.backbones import build_backbone


class KisanVisionClassifier(nn.Module):
    """
    Extensible computer vision model for crop disease classification.
    """
    def __init__(
        self,
        architecture: str = "mobilenet_v3_large",
        num_classes: int = 10,
        pretrained: bool = False,
        dropout_rate: float = 0.2,
        temperature: float = 1.0
    ):
        super().__init__()
        self.architecture = architecture
        self.num_classes = num_classes
        self.temperature = nn.Parameter(torch.tensor(temperature), requires_grad=False)
        
        self.backbone, in_features = build_backbone(
            architecture=architecture,
            pretrained=pretrained
        )
        
        self.head = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(in_features, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate / 2.0),
            nn.Linear(256, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Standard forward pass returning raw logits."""
        features = self.backbone(x)
        logits = self.head(features)
        return logits

    def predict_proba(self, x: torch.Tensor) -> torch.Tensor:
        """Returns calibrated softmax probabilities scaled by temperature."""
        logits = self.forward(x)
        scaled_logits = logits / torch.clamp(self.temperature, min=0.1)
        return F.softmax(scaled_logits, dim=-1)

    def compute_uncertainty(self, logits: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Computes (top_confidence, normalized_entropy).
        High entropy indicates high model uncertainty.
        """
        probs = F.softmax(logits, dim=-1)
        top_conf, _ = torch.max(probs, dim=-1)
        
        # Shannon Entropy: -sum(p * log(p))
        eps = 1e-8
        entropy = -torch.sum(probs * torch.log(probs + eps), dim=-1)
        max_entropy = math.log(self.num_classes) if self.num_classes > 1 else 1.0
        normalized_entropy = entropy / max_entropy
        
        return top_conf, normalized_entropy

    def get_parameter_counts(self) -> Dict[str, int]:
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "frozen_parameters": total_params - trainable_params
        }
