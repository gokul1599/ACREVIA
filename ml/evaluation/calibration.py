"""
KisanVision - Model Calibration & Uncertainty Evaluation.
Implements Expected Calibration Error (ECE), Maximum Calibration Error (MCE),
and post-hoc Temperature Scaling to prevent overconfident diagnostic errors.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F


class CalibrationEvaluator:
    """
    Evaluates probability calibration using binned confidence reliability metrics.
    """
    @staticmethod
    def compute_ece(
        probabilities: np.ndarray,
        labels: np.ndarray,
        num_bins: int = 10
    ) -> Dict[str, Any]:
        """
        Computes Expected Calibration Error (ECE) and Maximum Calibration Error (MCE).
        
        Args:
            probabilities: Array of shape (N, C) containing predicted class probabilities.
            labels: Array of shape (N,) containing true integer class indices.
            num_bins: Number of equal-width confidence bins (default: 10).
            
        Returns:
            Dictionary containing ECE, MCE, and per-bin reliability statistics.
        """
        confidences = np.max(probabilities, axis=1)
        predictions = np.argmax(probabilities, axis=1)
        accuracies = (predictions == labels).astype(float)

        bin_boundaries = np.linspace(0.0, 1.0, num_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]

        ece = 0.0
        mce = 0.0
        bin_stats = []

        total_samples = len(labels)

        for lower, upper in zip(bin_lowers, bin_uppers):
            # Samples within [lower, upper)
            in_bin = (confidences > lower) & (confidences <= upper)
            prop_in_bin = np.mean(in_bin)

            if prop_in_bin > 0:
                bin_acc = float(np.mean(accuracies[in_bin]))
                bin_conf = float(np.mean(confidences[in_bin]))
                gap = abs(bin_acc - bin_conf)
                
                ece += float(gap * prop_in_bin)
                mce = max(mce, gap)

                bin_stats.append({
                    "lower_bound": round(float(lower), 2),
                    "upper_bound": round(float(upper), 2),
                    "sample_count": int(np.sum(in_bin)),
                    "bin_accuracy": round(bin_acc, 4),
                    "bin_confidence": round(bin_conf, 4),
                    "calibration_gap": round(float(gap), 4)
                })
            else:
                bin_stats.append({
                    "lower_bound": round(float(lower), 2),
                    "upper_bound": round(float(upper), 2),
                    "sample_count": 0,
                    "bin_accuracy": 0.0,
                    "bin_confidence": 0.0,
                    "calibration_gap": 0.0
                })

        return {
            "expected_calibration_error": round(float(ece), 4),
            "max_calibration_error": round(float(mce), 4),
            "num_bins": num_bins,
            "bins": bin_stats
        }


class TemperatureScaler:
    """
    Fits a single scalar temperature T > 0 on validation logits using NLL loss.
    """
    def __init__(self, initial_temperature: float = 1.0):
        self.temperature = nn.Parameter(torch.tensor(initial_temperature), requires_grad=True)

    def fit(
        self,
        validation_logits: torch.Tensor,
        validation_labels: torch.Tensor,
        max_iter: int = 100,
        lr: float = 0.01
    ) -> float:
        """
        Optimizes temperature T to minimize cross-entropy loss on validation data.
        """
        optimizer = optim.LBFGS([self.temperature], lr=lr, max_iter=max_iter)
        criterion = nn.CrossEntropyLoss()

        def eval_loss():
            optimizer.zero_grad()
            # Ensure temperature stays strictly positive
            clamped_temp = torch.clamp(self.temperature, min=0.1, max=10.0)
            loss = criterion(validation_logits / clamped_temp, validation_labels)
            loss.backward()
            return loss

        optimizer.step(eval_loss)
        final_temp = float(torch.clamp(self.temperature, min=0.1, max=10.0).detach().item())
        return round(final_temp, 4)

    def calibrate(self, logits: np.ndarray, temperature: float) -> np.ndarray:
        """Applies temperature to raw logits and returns softmax probabilities."""
        t = max(temperature, 0.1)
        scaled = logits / t
        # Numerically stable softmax
        exp_scaled = np.exp(scaled - np.max(scaled, axis=-1, keepdims=True))
        return exp_scaled / np.sum(exp_scaled, axis=-1, keepdims=True)
