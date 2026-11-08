"""
KisanVision - Exposure & Illumination Analyzer.
Detects severe overexposure, deep shadows, and contrast deficits on agricultural foliage.
"""

import numpy as np
from PIL import Image


class ExposureAnalyzer:
    """
    Evaluates brightness, contrast, and extreme pixel clipping.
    """
    def __init__(
        self,
        min_mean_brightness: float = 35.0,
        max_mean_brightness: float = 225.0,
        min_contrast_std: float = 20.0,
        max_clipping_ratio: float = 0.25
    ):
        self.min_mean_brightness = min_mean_brightness
        self.max_mean_brightness = max_mean_brightness
        self.min_contrast_std = min_contrast_std
        self.max_clipping_ratio = max_clipping_ratio

    def evaluate(self, image: Image.Image) -> dict:
        grey = image.convert("L")
        arr = np.array(grey, dtype=np.float32)
        
        mean_val = float(np.mean(arr))
        std_val = float(np.std(arr))
        total_pixels = arr.size
        
        underexposed_ratio = float(np.sum(arr < 15) / total_pixels)
        overexposed_ratio = float(np.sum(arr > 240) / total_pixels)
        
        reasons = []
        is_acceptable = True
        
        if mean_val < self.min_mean_brightness or underexposed_ratio > self.max_clipping_ratio:
            reasons.append("UNDEREXPOSED_TOO_DARK")
            is_acceptable = False
            
        if mean_val > self.max_mean_brightness or overexposed_ratio > self.max_clipping_ratio:
            reasons.append("OVEREXPOSED_TOO_BRIGHT")
            is_acceptable = False
            
        if std_val < self.min_contrast_std:
            reasons.append("LOW_CONTRAST_WASHED_OUT")
            is_acceptable = False
            
        status = "OPTIMAL_EXPOSURE"
        if not is_acceptable:
            status = "POOR_EXPOSURE"
        elif underexposed_ratio > 0.10 or overexposed_ratio > 0.10:
            status = "SUBOPTIMAL_EXPOSURE"

        return {
            "status": status,
            "is_acceptable": is_acceptable,
            "mean_brightness": round(mean_val, 2),
            "contrast_std": round(std_val, 2),
            "underexposed_ratio": round(underexposed_ratio, 3),
            "overexposed_ratio": round(overexposed_ratio, 3),
            "reason_codes": reasons
        }
