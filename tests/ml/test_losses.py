"""
Tests for Advanced Loss Functions (Focal Loss, Label Smoothing, Class-Balanced Loss).
"""

import torch
import torch.nn.functional as F
from ml.training.losses import FocalLoss, LabelSmoothingCrossEntropy, ClassBalancedLoss


def test_focal_loss_forward():
    loss_fn = FocalLoss(gamma=2.0, alpha=None)
    logits = torch.tensor([[2.0, 0.5, 0.1], [0.2, 1.8, 0.5]], requires_grad=True)
    targets = torch.tensor([0, 1])

    loss = loss_fn(logits, targets)
    assert loss.dim() == 0  # scalar
    assert loss.item() > 0.0

    # Verify backward pass works
    loss.backward()
    assert logits.grad is not None


def test_focal_loss_downweights_easy_examples():
    loss_fn = FocalLoss(gamma=2.0)
    
    # Moderately easy sample: p_t ≈ 0.98
    easy_logits = torch.tensor([[3.0, -1.0]])
    target = torch.tensor([0])
    easy_loss = loss_fn(easy_logits, target).item()
    ce_easy = F.cross_entropy(easy_logits, target).item()

    # Focal loss should heavily suppress the loss on this easy sample compared to standard CE
    assert easy_loss > 0.0
    assert easy_loss < ce_easy * 0.01


def test_label_smoothing_cross_entropy():
    loss_fn = LabelSmoothingCrossEntropy(smoothing=0.1)
    logits = torch.tensor([[3.0, 0.2, 0.1]], requires_grad=True)
    targets = torch.tensor([0])

    loss = loss_fn(logits, targets)
    assert loss.item() > 0.0
    
    loss.backward()
    assert logits.grad is not None


def test_class_balanced_loss():
    samples_per_class = [1000, 100, 20]  # Severe imbalance
    loss_fn = ClassBalancedLoss(samples_per_class=samples_per_class, beta=0.999, loss_type="focal")

    logits = torch.tensor([[1.0, 2.0, 0.5], [0.1, 0.2, 3.0]], requires_grad=True)
    targets = torch.tensor([1, 2])

    loss = loss_fn(logits, targets)
    assert loss.item() > 0.0
    
    loss.backward()
    assert logits.grad is not None
