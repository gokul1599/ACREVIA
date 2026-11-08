"""
KisanVision - Image Quality Validator Orchestrator.
Combines dimension, blur, and exposure metrics into an auditable quality state.
"""

from typing import Dict, Any, List
from PIL import Image
from datetime import datetime, timezone

from ml.datasets.manifests.manifest_schema import ImageQualityStatus
from ml.datasets.quality.blur_detector import BlurDetector
from ml.datasets.quality.exposure_analyzer import ExposureAnalyzer


class QualityValidationResult:
    def __init__(
        self,
        overall_status: ImageQualityStatus,
        is_admissible_for_training: bool,
        is_admissible_for_inference: bool,
        reason_codes: List[str],
        metrics: Dict[str, Any],
        validator_version: str = "1.0.0"
    ):
        self.overall_status = overall_status
        self.is_admissible_for_training = is_admissible_for_training
        self.is_admissible_for_inference = is_admissible_for_inference
        self.reason_codes = reason_codes
        self.metrics = metrics
        self.validator_version = validator_version
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status.value,
            "is_admissible_for_training": self.is_admissible_for_training,
            "is_admissible_for_inference": self.is_admissible_for_inference,
            "reason_codes": self.reason_codes,
            "metrics": self.metrics,
            "validator_version": self.validator_version,
            "timestamp": self.timestamp
        }


class ImageQualityValidator:
    """
    Exhaustive quality gate for photographic ingestion.
    Enforces scientific standards before allowing samples into training or inference.
    """
    def __init__(
        self,
        min_width: int = 64,
        min_height: int = 64,
        min_aspect_ratio: float = 0.25,
        max_aspect_ratio: float = 4.0,
        blur_detector: BlurDetector = None,
        exposure_analyzer: ExposureAnalyzer = None
    ):
        self.min_width = min_width
        self.min_height = min_height
        self.min_aspect_ratio = min_aspect_ratio
        self.max_aspect_ratio = max_aspect_ratio
        self.blur_detector = blur_detector or BlurDetector()
        self.exposure_analyzer = exposure_analyzer or ExposureAnalyzer()

    def validate(self, image: Image.Image) -> QualityValidationResult:
        reason_codes: List[str] = []
        metrics: Dict[str, Any] = {}
        
        # 1. Dimension & Aspect Ratio Checks
        width, height = image.size
        aspect_ratio = width / max(height, 1)
        metrics["dimensions"] = {"width": width, "height": height, "aspect_ratio": round(aspect_ratio, 3)}
        
        if width < self.min_width or height < self.min_height:
            reason_codes.append("IMAGE_DIMENSIONS_TOO_SMALL")
            
        if aspect_ratio < self.min_aspect_ratio or aspect_ratio > self.max_aspect_ratio:
            reason_codes.append("UNUSABLE_EXTREME_ASPECT_RATIO")

        # 2. Blur / Sharpness Evaluation
        blur_eval = self.blur_detector.evaluate(image)
        metrics["blur"] = blur_eval
        if not blur_eval["is_acceptable"]:
            reason_codes.append("SEVERE_BLUR_OUT_OF_FOCUS")
        elif blur_eval["status"] == "MILD_BLUR":
            reason_codes.append("MILD_BLUR_NOTICE")

        # 3. Exposure & Contrast Evaluation
        exposure_eval = self.exposure_analyzer.evaluate(image)
        metrics["exposure"] = exposure_eval
        if not exposure_eval["is_acceptable"]:
            reason_codes.extend(exposure_eval["reason_codes"])

        # 4. State Determination
        # Hard fatal errors -> QUARANTINED
        fatal_errors = {"IMAGE_DIMENSIONS_TOO_SMALL", "UNUSABLE_EXTREME_ASPECT_RATIO"}
        if any(r in fatal_errors for r in reason_codes):
            overall_status = ImageQualityStatus.QUARANTINED
            is_train = False
            is_infer = False
        # Diagnostic blockers -> RETAKE_OR_REVIEW
        elif "SEVERE_BLUR_OUT_OF_FOCUS" in reason_codes or "UNDEREXPOSED_TOO_DARK" in reason_codes or "OVEREXPOSED_TOO_BRIGHT" in reason_codes:
            overall_status = ImageQualityStatus.RETAKE_OR_REVIEW
            is_train = False
            is_infer = False
        # Minor notices -> ACCEPTED_WITH_LIMITATIONS
        elif "MILD_BLUR_NOTICE" in reason_codes or exposure_eval["status"] == "SUBOPTIMAL_EXPOSURE":
            overall_status = ImageQualityStatus.ACCEPTED_WITH_LIMITATIONS
            is_train = True
            is_infer = True
        else:
            overall_status = ImageQualityStatus.ACCEPTED
            is_train = True
            is_infer = True

        return QualityValidationResult(
            overall_status=overall_status,
            is_admissible_for_training=is_train,
            is_admissible_for_inference=is_infer,
            reason_codes=reason_codes,
            metrics=metrics
        )
