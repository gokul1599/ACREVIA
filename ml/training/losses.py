"""
KisanVision - Advanced Training Loss Functions.
Implements Focal Loss, Label Smoothing Cross-Entropy, and Class-Balanced Loss
to combat extreme agricultural class imbalance and calibrate diagnostic predictions.
"""

from typing import Optional, List, Union
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class FocalLoss(nn.Module):
    """
    Multi-class Focal Loss (Lin et al., 2017).
    Down-weights easy examples and focuses training on hard misclassified foliar symptoms.
    FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)
    """
    def __init__(
        self,
        gamma: float = 2.0,
        alpha: Optional[Union[float, List[float], torch.Tensor]] = None,
        reduction: str = "mean"
    ):
        super().__init__()
        self.gamma = gamma
        self.reduction = reduction

        if alpha is not None:
            if isinstance(alpha, (float, int)):
                self.alpha = torch.tensor([alpha])
            elif isinstance(alpha, (list, np.ndarray)):
                self.alpha = torch.tensor(alpha, dtype=torch.float32)
            elif isinstance(alpha, torch.Tensor):
                self.alpha = alpha.clone().detach().float()
            else:
                self.alpha = None
        else:
            self.alpha = None

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Args:
            logits: Predicted raw logits of shape (N, C).
            targets: Ground truth class indices of shape (N,).
        """
        # Cross entropy loss without reduction: -log(p_t)
        ce_loss = F.cross_entropy(logits, targets, reduction="none")
        p_t = torch.exp(-ce_loss)

        # Modulating factor: (1 - p_t)^gamma
        modulating_factor = (1.0 - p_t) ** self.gamma
        focal_loss = modulating_factor * ce_loss

        # Alpha weighting
        if self.alpha is not None:
            if self.alpha.device != logits.device:
                self.alpha = self.alpha.to(logits.device)
            if self.alpha.numel() == logits.size(1):
                alpha_t = self.alpha[targets]
                focal_loss = alpha_t * focal_loss
            elif self.alpha.numel() == 1:
                focal_loss = self.alpha * focal_loss

        if self.reduction == "mean":
            return focal_loss.mean()
        elif self.reduction == "sum":
            return focal_loss.sum()
        else:
            return focal_loss


class LabelSmoothingCrossEntropy(nn.Module):
    """
    Cross Entropy Loss with Label Smoothing.
    Prevents overconfidence in network logits, aiding post-hoc temperature calibration.
    """
    def __init__(self, smoothing: float = 0.1, reduction: str = "mean"):
        super().__init__()
        if not 0.0 <= smoothing < 1.0:
            raise ValueError(f"Smoothing must be in [0, 1), got {smoothing}")
        self.smoothing = smoothing
        self.reduction = reduction

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        num_classes = logits.size(-1)
        log_preds = F.log_softmax(logits, dim=-1)

        if self.reduction == "mean":
            loss = F.cross_entropy(logits, targets, label_smoothing=self.smoothing, reduction="mean")
        elif self.reduction == "sum":
            loss = F.cross_entropy(logits, targets, label_smoothing=self.smoothing, reduction="sum")
        else:
            loss = F.cross_entropy(logits, targets, label_smoothing=self.smoothing, reduction="none")

        return loss


class ClassBalancedLoss(nn.Module):
    """
    Class-Balanced Loss (Cui et al., CVPR 2019).
    Reweights loss by effective number of samples: (1 - beta) / (1 - beta^n_c).
    """
    def __init__(
        self,
        samples_per_class: List[int],
        beta: float = 0.9999,
        gamma: float = 2.0,
        loss_type: str = "focal"
    ):
        super().__init__()
        self.beta = beta
        self.gamma = gamma
        self.loss_type = loss_type

        # Compute effective sample weights
        effective_num = 1.0 - np.power(beta, samples_per_class)
        weights = (1.0 - beta) / np.array(effective_num)
        weights = weights / np.sum(weights) * len(samples_per_class)
        self.weights = torch.tensor(weights, dtype=torch.float32)

        if loss_type == "focal":
            self.loss_fn = FocalLoss(gamma=gamma, alpha=self.weights)
        else:
            self.loss_fn = nn.CrossEntropyLoss(weight=self.weights)

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        if self.weights.device != logits.device:
            self.weights = self.weights.to(logits.device)
            if hasattr(self.loss_fn, "alpha") and self.loss_fn.alpha is not None:
                self.loss_fn.alpha = self.loss_fn.alpha.to(logits.device)
            elif hasattr(self.loss_fn, "weight") and self.loss_fn.weight is not None:
                self.loss_fn.weight = self.loss_fn.weight.to(logits.device)

        return self.loss_fn(logits, targets)
