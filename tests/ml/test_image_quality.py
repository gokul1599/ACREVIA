"""
Tests for Image Quality Validation (Blur, Exposure, Dimensions).
"""

import numpy as np
from PIL import Image
from ml.datasets.quality.blur_detector import BlurDetector
from ml.datasets.quality.exposure_analyzer import ExposureAnalyzer
from ml.datasets.quality.quality_validator import ImageQualityValidator
from ml.datasets.manifests.manifest_schema import ImageQualityStatus


def test_blur_detector():
    detector = BlurDetector(blur_threshold=100.0)
    
    # 1. Perfectly flat image has 0 variance (blurry / featureless)
    flat_img = Image.new("RGB", (200, 200), color=(100, 100, 100))
    flat_eval = detector.evaluate(flat_img)
    assert flat_eval["score"] == 0.0
    assert flat_eval["is_acceptable"] is False
    assert flat_eval["status"] == "BLURRY"
    
    # 2. High-contrast checkerboard image has high Laplacian variance (sharp)
    arr = np.zeros((200, 200, 3), dtype=np.uint8)
    arr[::4, ::4] = 255
    arr[1::4, 1::4] = 255
    sharp_img = Image.fromarray(arr)
    sharp_eval = detector.evaluate(sharp_img)
    assert sharp_eval["score"] > 250.0
    assert sharp_eval["is_acceptable"] is True
    assert sharp_eval["status"] == "SHARP"


def test_exposure_analyzer():
    analyzer = ExposureAnalyzer()
    
    # Pure black image -> Underexposed
    black_img = Image.new("RGB", (100, 100), color=(0, 0, 0))
    black_eval = analyzer.evaluate(black_img)
    assert black_eval["is_acceptable"] is False
    assert "UNDEREXPOSED_TOO_DARK" in black_eval["reason_codes"]
    
    # Pure white image -> Overexposed
    white_img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    white_eval = analyzer.evaluate(white_img)
    assert white_eval["is_acceptable"] is False
    assert "OVEREXPOSED_TOO_BRIGHT" in white_eval["reason_codes"]


def test_quality_validator_quarantine():
    validator = ImageQualityValidator(min_width=64, min_height=64)
    
    # Tiny 16x16 image -> QUARANTINED
    tiny_img = Image.new("RGB", (16, 16), color=(50, 150, 50))
    result = validator.validate(tiny_img)
    assert result.overall_status == ImageQualityStatus.QUARANTINED
    assert result.is_admissible_for_training is False
    assert "IMAGE_DIMENSIONS_TOO_SMALL" in result.reason_codes
