"""
KisanVision - Multi-Crop Hierarchical Vision Architecture.
Shared foliar feature backbone with isolated crop-specific classification heads
and an auxiliary crop identification gate to prevent cross-crop diagnostic contamination.
"""

import math
from typing import Dict, Any, Optional, Tuple, List, Union
import torch
import torch.nn as nn
import torch.nn.functional as F

from ml.models.backbones import build_backbone


class MultiCropKisanVisionClassifier(nn.Module):
    """
    Hierarchical multi-crop vision model with shared representation learning
    and isolated classification heads for Cotton, Rice, and Chilli.
    """
    def __init__(
        self,
        architecture: str = "mobilenet_v3_small",
        crop_class_counts: Optional[Dict[str, int]] = None,
        pretrained: bool = False,
        dropout_rate: float = 0.2,
        temperatures: Optional[Dict[str, float]] = None
    ):
        super().__init__()
        self.architecture = architecture
        self.crop_class_counts = crop_class_counts or {
            "cotton": 10,
            "rice": 10,
            "chilli": 8
        }
        self.crops = list(self.crop_class_counts.keys())
        
        # 1. Shared Feature Backbone
        self.backbone, self.in_features = build_backbone(
            architecture=architecture,
            pretrained=pretrained
        )

        # 2. Auxiliary Crop Identification Gate (cotton, rice, chilli, unsupported/other)
        self.crop_gate_head = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(self.in_features, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, len(self.crops) + 1)  # +1 for unknown/unsupported
        )

        # 3. Isolated Crop-Specific Pathology Heads
        self.heads = nn.ModuleDict()
        for crop, count in self.crop_class_counts.items():
            self.heads[crop] = nn.Sequential(
                nn.Dropout(p=dropout_rate),
                nn.Linear(self.in_features, 256),
                nn.BatchNorm1d(256),
                nn.ReLU(inplace=True),
                nn.Dropout(p=dropout_rate / 2.0),
                nn.Linear(256, count)
            )

        # 4. Per-crop temperature parameters
        temps = temperatures or {c: 1.0 for c in self.crops}
        self.temperatures = nn.ParameterDict({
            crop: nn.Parameter(torch.tensor(temps.get(crop, 1.0)), requires_grad=False)
            for crop in self.crops
        })

    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Passes image through shared CNN backbone."""
        return self.backbone(x)

    def identify_crop(self, features: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Runs auxiliary crop gating head.
        Returns (predicted_crop_idx, crop_confidence).
        """
        gate_logits = self.crop_gate_head(features)
        crop_probs = F.softmax(gate_logits, dim=-1)
        conf, pred_idx = torch.max(crop_probs, dim=-1)
        return pred_idx, conf

    def forward(
        self,
        x: torch.Tensor,
        crop_type: Optional[str] = None
    ) -> Union[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Forward pass.
        If crop_type is specified: returns logits strictly for that crop's head (B, num_classes).
        If crop_type is None: returns dictionary containing 'crop_gate_logits' and all crop head logits.
        """
        features = self.extract_features(x)

        if crop_type is not None:
            crop_key = crop_type.lower().strip()
            if crop_key not in self.heads:
                raise ValueError(f"Crop '{crop_type}' not recognized. Supported: {self.crops}")
            return self.heads[crop_key](features)

        # Autonomous mode: evaluate all heads and crop gate
        gate_logits = self.crop_gate_head(features)
        head_logits = {crop: head(features) for crop, head in self.heads.items()}
        return {
            "crop_gate_logits": gate_logits,
            **head_logits
        }

    def predict_calibrated(
        self,
        x: torch.Tensor,
        crop_type: str
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Computes calibrated softmax probabilities, top confidence, and normalized entropy
        for a specified crop context.
        """
        crop_key = crop_type.lower().strip()
        logits = self.forward(x, crop_type=crop_key)
        temp = torch.clamp(self.temperatures[crop_key], min=0.1)
        scaled_logits = logits / temp
        probs = F.softmax(scaled_logits, dim=-1)

        # Top confidence
        top_conf, _ = torch.max(probs, dim=-1)

        # Normalized Shannon entropy
        eps = 1e-8
        entropy = -torch.sum(probs * torch.log(probs + eps), dim=-1)
        num_classes = self.crop_class_counts[crop_key]
        max_entropy = math.log(num_classes) if num_classes > 1 else 1.0
        norm_entropy = entropy / max_entropy

        return probs, top_conf, norm_entropy

    def get_parameter_breakdown(self) -> Dict[str, Any]:
        """Returns parameter count breakdown across shared backbone and crop heads."""
        backbone_params = sum(p.numel() for p in self.backbone.parameters())
        gate_params = sum(p.numel() for p in self.crop_gate_head.parameters())
        heads_params = {
            crop: sum(p.numel() for p in head.parameters())
            for crop, head in self.heads.items()
        }
        total = backbone_params + gate_params + sum(heads_params.values())

        return {
            "shared_backbone_parameters": backbone_params,
            "crop_gate_parameters": gate_params,
            "crop_head_parameters": heads_params,
            "total_parameters": total
        }
