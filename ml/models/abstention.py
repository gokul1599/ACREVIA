"""
KisanVision - Uncertainty & Abstention Engine.
Formalizes the 8 explicit agricultural decision states to ensure the AI system
knows when to diagnose, when to request follow-up observations, and when to abstain.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
import numpy as np


class AgriculturalDecisionState(str, Enum):
    """
    Standardized diagnostic decision states mandated by KisanVision AI Governance.
    """
    SUPPORTED_PREDICTION = "SUPPORTED_PREDICTION"
    NEEDS_MORE_INFORMATION = "NEEDS_MORE_INFORMATION"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    IMAGE_QUALITY_INSUFFICIENT = "IMAGE_QUALITY_INSUFFICIENT"
    UNSUPPORTED_CROP = "UNSUPPORTED_CROP"
    OUT_OF_DISTRIBUTION = "OUT_OF_DISTRIBUTION"
    EXPERT_REVIEW_REQUIRED = "EXPERT_REVIEW_REQUIRED"
    PROCESSING_FAILED = "PROCESSING_FAILED"


class AbstentionEngine:
    """
    Evaluates inputs, quality metrics, and probability distributions to determine
    the definitive agricultural decision state.
    """
    def __init__(
        self,
        high_confidence_threshold: float = 0.85,
        minimum_usable_confidence: float = 0.50,
        maximum_normalized_entropy: float = 0.65,
        minimum_prediction_margin: float = 0.15
    ):
        self.high_confidence_threshold = high_confidence_threshold
        self.minimum_usable_confidence = minimum_usable_confidence
        self.maximum_normalized_entropy = maximum_normalized_entropy
        self.minimum_prediction_margin = minimum_prediction_margin

    def evaluate_decision_state(
        self,
        is_quality_acceptable: bool,
        is_supported_crop: bool,
        is_foliar_verified: bool,
        probabilities: Optional[np.ndarray] = None,
        class_names: Optional[List[str]] = None,
        crop_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determines the diagnostic decision state following strict agricultural hierarchy.
        """
        # Gate 1: Image Quality Inspection
        if not is_quality_acceptable:
            return {
                "decision_state": AgriculturalDecisionState.IMAGE_QUALITY_INSUFFICIENT,
                "can_diagnose": False,
                "expert_review_required": False,
                "reason": "Image quality is blurred, severely underexposed, or overexposed.",
                "action_guidance": "Retake photo holding camera 15-20cm from the leaf in natural diffused light."
            }

        # Gate 2: Supported Crop Inspection
        if not is_supported_crop:
            return {
                "decision_state": AgriculturalDecisionState.UNSUPPORTED_CROP,
                "can_diagnose": False,
                "expert_review_required": False,
                "reason": f"Crop '{crop_name}' is not in the supported diagnostic scope (Cotton, Rice, Chilli).",
                "action_guidance": "Please select a supported Telangana crop or submit sample for agronomist expansion."
            }

        # Gate 3: Foliar Botanical Inspection (Tier 1 OOD)
        if not is_foliar_verified:
            return {
                "decision_state": AgriculturalDecisionState.OUT_OF_DISTRIBUTION,
                "can_diagnose": False,
                "expert_review_required": False,
                "reason": "Photograph does not contain characteristic agricultural foliar vegetation.",
                "action_guidance": "Please frame only the affected plant leaf or crop canopy."
            }

        # Gate 4: Probability Distribution Inspection (Tier 2 OOD / Uncertainty)
        if probabilities is None or len(probabilities) == 0:
            return {
                "decision_state": AgriculturalDecisionState.PROCESSING_FAILED,
                "can_diagnose": False,
                "expert_review_required": True,
                "reason": "Inference computation did not produce valid probabilities.",
                "action_guidance": "System internal error. Please retry submission."
            }

        probs = np.array(probabilities, dtype=np.float64)
        num_classes = len(probs)
        sorted_indices = np.argsort(probs)[::-1]
        
        top1_idx = int(sorted_indices[0])
        top1_conf = float(probs[top1_idx])
        top2_conf = float(probs[sorted_indices[1]]) if num_classes > 1 else 0.0
        margin = float(top1_conf - top2_conf)

        eps = 1e-12
        entropy = -float(np.sum(probs * np.log2(probs + eps)))
        max_entropy = float(np.log2(num_classes)) if num_classes > 1 else 1.0
        normalized_entropy = float(entropy / max_entropy)

        cnames = class_names or [f"class_{i}" for i in range(num_classes)]
        top1_name = cnames[top1_idx]

        # Case A: Very low confidence -> Needs More Information
        if top1_conf < self.minimum_usable_confidence:
            return {
                "decision_state": AgriculturalDecisionState.NEEDS_MORE_INFORMATION,
                "can_diagnose": False,
                "expert_review_required": True,
                "top_candidate": top1_name,
                "confidence": round(top1_conf, 4),
                "normalized_entropy": round(normalized_entropy, 4),
                "margin": round(margin, 4),
                "reason": f"Top confidence ({round(top1_conf, 2)}) is below minimal diagnostic threshold ({self.minimum_usable_confidence}).",
                "action_guidance": "Symptoms are ambiguous. Provide additional context (growth stage, irrigation) and route to expert."
            }

        # Case B: High Entropy or Narrow Margin -> Expert Review Required
        if normalized_entropy > self.maximum_normalized_entropy or (margin < self.minimum_prediction_margin and num_classes > 1):
            return {
                "decision_state": AgriculturalDecisionState.EXPERT_REVIEW_REQUIRED,
                "can_diagnose": False,
                "expert_review_required": True,
                "top_candidate": top1_name,
                "confidence": round(top1_conf, 4),
                "normalized_entropy": round(normalized_entropy, 4),
                "margin": round(margin, 4),
                "reason": f"Diagnostic conflict between top candidates (Margin: {round(margin, 3)}, Entropy: {round(normalized_entropy, 3)}).",
                "action_guidance": "Differential diagnosis required. Case dispatched to Krishi Vigyan Kendra agronomist."
            }

        # Case C: Moderate confidence -> Low Confidence
        if top1_conf < self.high_confidence_threshold:
            return {
                "decision_state": AgriculturalDecisionState.LOW_CONFIDENCE,
                "can_diagnose": True,
                "expert_review_required": True,
                "top_candidate": top1_name,
                "confidence": round(top1_conf, 4),
                "normalized_entropy": round(normalized_entropy, 4),
                "margin": round(margin, 4),
                "reason": f"Confidence ({round(top1_conf, 2)}) is acceptable but below definitive threshold ({self.high_confidence_threshold}).",
                "action_guidance": "Preliminary diagnosis provided. Monitor crop closely and verify before chemical application."
            }

        # Case D: High confidence, low entropy, clear margin -> Supported Prediction
        return {
            "decision_state": AgriculturalDecisionState.SUPPORTED_PREDICTION,
            "can_diagnose": True,
            "expert_review_required": False,
            "top_candidate": top1_name,
            "confidence": round(top1_conf, 4),
            "normalized_entropy": round(normalized_entropy, 4),
            "margin": round(margin, 4),
            "reason": "High-confidence verified prediction with low symptom entropy.",
            "action_guidance": "Proceed with recommended CIBRC agronomic interventions."
        }
