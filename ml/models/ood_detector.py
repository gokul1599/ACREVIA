"""
KisanVision - Out-of-Distribution (OOD) & Foliar Verification Engine.
Two-tier defense system:
Tier 1: Chromatic and foliar vegetation validation (rejects non-plant imagery).
Tier 2: Prediction entropy and margin uncertainty analysis (identifies ambiguous foliar pathologies).
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np
from PIL import Image


class FoliarImageDetector:
    """
    Tier 1 Defense: Validates whether an incoming image contains foliar/agricultural
    plant material based on vegetation color indices and textural distribution.
    """
    def __init__(
        self,
        min_foliar_ratio: float = 0.08,
        min_contrast_std: float = 5.0
    ):
        self.min_foliar_ratio = min_foliar_ratio
        self.min_contrast_std = min_contrast_std

    def analyze_foliar_content(self, pil_image: Image.Image) -> Dict[str, Any]:
        """
        Computes Excess Green Index (ExG) and foliar spectrum ratios on RGB image.
        ExG = 2*G - R - B.
        Also accommodates chlorotic, necrotic, and diseased leaves (yellows/browns).
        """
        rgb_image = pil_image.convert("RGB")
        img_np = np.asarray(rgb_image, dtype=np.float32)

        r = img_np[:, :, 0]
        g = img_np[:, :, 1]
        b = img_np[:, :, 2]

        # 1. Excess Green (ExG) vegetation index
        exg = 2.0 * g - r - b
        green_mask = (exg > 10.0) & (g > 30.0)

        # 2. Chlorotic / Yellowing foliage mask (R and G high, B significantly lower)
        yellow_mask = (r > 70.0) & (g > 70.0) & (b < 100.0) & (np.abs(r - g) < 50.0)

        # 3. Necrotic / Brown lesion mask (R > G > B, earthy hue typical of leaf blights)
        brown_mask = (r > 60.0) & (g > 35.0) & (b > 15.0) & (r > g) & (g > b) & ((r - b) > 20.0)

        # Combined foliar mask
        foliar_mask = green_mask | yellow_mask | brown_mask
        foliar_pixel_ratio = float(np.mean(foliar_mask))

        # Overall image grayscale standard deviation (texture check)
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        contrast_std = float(np.std(gray))

        is_foliar = bool(
            (foliar_pixel_ratio >= self.min_foliar_ratio) and
            (contrast_std >= self.min_contrast_std)
        )

        reason = "VERIFIED_FOLIAR_CANOPY"
        if foliar_pixel_ratio < self.min_foliar_ratio:
            reason = "INSUFFICIENT_FOLIAR_TISSUE"
        elif contrast_std < self.min_contrast_std:
            reason = "LACKS_NATURAL_LEAF_TEXTURE"

        return {
            "is_foliar": is_foliar,
            "foliar_pixel_ratio": round(foliar_pixel_ratio, 4),
            "contrast_std": round(contrast_std, 2),
            "reason": reason
        }


class ModelUncertaintyAuditor:
    """
    Tier 2 Defense: Analyzes calibrated softmax posteriors to identify
    out-of-distribution inputs, ambiguous diagnoses, and margin conflicts.
    """
    def __init__(
        self,
        min_confidence_threshold: float = 0.85,
        max_normalized_entropy: float = 0.65,
        min_prediction_margin: float = 0.15
    ):
        self.min_confidence_threshold = min_confidence_threshold
        self.max_normalized_entropy = max_normalized_entropy
        self.min_prediction_margin = min_prediction_margin

    def evaluate_uncertainty(
        self,
        probabilities: np.ndarray,
        class_names: list
    ) -> Dict[str, Any]:
        """
        Evaluates probabilities for a single sample (1D array of shape [C]).
        """
        probs = np.array(probabilities, dtype=np.float64)
        num_classes = len(probs)
        
        # Sort descending
        sorted_indices = np.argsort(probs)[::-1]
        top1_idx = int(sorted_indices[0])
        top1_conf = float(probs[top1_idx])
        
        top2_conf = float(probs[sorted_indices[1]]) if num_classes > 1 else 0.0
        margin = float(top1_conf - top2_conf)

        # Normalized Shannon entropy
        eps = 1e-12
        entropy = -float(np.sum(probs * np.log2(probs + eps)))
        max_entropy = float(np.log2(num_classes)) if num_classes > 1 else 1.0
        normalized_entropy = float(entropy / max_entropy)

        # Decision status
        status = "IN_DISTRIBUTION"
        action = "DIRECT_DIAGNOSIS"
        reasons = []

        if top1_conf < self.min_confidence_threshold:
            status = "LOW_CONFIDENCE"
            action = "EXPERT_REVIEW_RECOMMENDED"
            reasons.append(f"Top confidence ({round(top1_conf, 3)}) below {self.min_confidence_threshold} threshold")

        if normalized_entropy > self.max_normalized_entropy:
            status = "UNCERTAIN_AMBIGUOUS"
            action = "EXPERT_REVIEW_RECOMMENDED"
            reasons.append(f"High posterior entropy ({round(normalized_entropy, 3)}) indicates ambiguous symptom pattern")

        if margin < self.min_prediction_margin and num_classes > 1:
            status = "UNCERTAIN_AMBIGUOUS"
            action = "DIFFERENTIAL_DIAGNOSIS_REQUIRED"
            reasons.append(f"Narrow margin ({round(margin, 3)}) between {class_names[top1_idx]} and {class_names[int(sorted_indices[1])]}")

        # Top-3 Differential Candidates
        top_candidates = []
        for rank in range(min(3, num_classes)):
            idx = int(sorted_indices[rank])
            top_candidates.append({
                "rank": rank + 1,
                "class_name": class_names[idx],
                "class_index": idx,
                "confidence": round(float(probs[idx]), 4)
            })

        return {
            "status": status,
            "action": action,
            "top1_confidence": round(top1_conf, 4),
            "top1_class": class_names[top1_idx],
            "prediction_margin": round(margin, 4),
            "normalized_entropy": round(normalized_entropy, 4),
            "reasons": reasons,
            "differential_candidates": top_candidates
        }
