"""
KisanVision - Learning Rate Schedulers.
Implements warmup and adaptive decay schedules for stable CNN fine-tuning.
"""

from typing import Dict, Any, Optional
import math
import torch
from torch.optim import Optimizer
from torch.optim.lr_scheduler import (
    CosineAnnealingLR,
    CosineAnnealingWarmRestarts,
    ReduceLROnPlateau,
    StepLR,
    LambdaLR
)


def build_warmup_cosine_scheduler(
    optimizer: Optimizer,
    warmup_epochs: int,
    total_epochs: int,
    min_lr_ratio: float = 0.01
) -> LambdaLR:
    """
    Constructs a linear warmup followed by cosine annealing learning rate scheduler.
    """
    def lr_lambda(current_epoch: int) -> float:
        if current_epoch < warmup_epochs:
            # Linear warmup
            return float(current_epoch + 1) / float(max(1, warmup_epochs))
        # Cosine decay
        progress = float(current_epoch - warmup_epochs) / float(max(1, total_epochs - warmup_epochs))
        cosine_decay = 0.5 * (1.0 + math.cos(math.pi * progress))
        return min_lr_ratio + (1.0 - min_lr_ratio) * cosine_decay

    return LambdaLR(optimizer, lr_lambda=lr_lambda)


def build_scheduler(
    optimizer: Optimizer,
    scheduler_name: str = "CosineAnnealingLR",
    epochs: int = 40,
    warmup_epochs: int = 3,
    **kwargs
):
    """
    Factory constructing the appropriate PyTorch learning rate scheduler.
    """
    name = scheduler_name.lower().strip()

    if name in ["cosine", "cosineannealinglr"]:
        return CosineAnnealingLR(optimizer, T_max=epochs, eta_min=kwargs.get("min_lr", 1e-6))
    elif name == "warmup_cosine":
        return build_warmup_cosine_scheduler(optimizer, warmup_epochs=warmup_epochs, total_epochs=epochs)
    elif name in ["plateau", "reducelronplateau"]:
        return ReduceLROnPlateau(
            optimizer,
            mode=kwargs.get("mode", "min"),
            factor=kwargs.get("factor", 0.5),
            patience=kwargs.get("patience", 3),
            min_lr=kwargs.get("min_lr", 1e-6)
        )
    elif name == "step":
        return StepLR(optimizer, step_size=kwargs.get("step_size", 10), gamma=kwargs.get("gamma", 0.1))
    else:
        raise ValueError(f"Unsupported scheduler '{scheduler_name}'. Choose from: ['cosine', 'warmup_cosine', 'plateau', 'step']")
