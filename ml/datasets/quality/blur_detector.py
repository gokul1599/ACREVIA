"""
KisanVision - Blur & Sharpness Detector.
Evaluates foliar focus quality using Laplacian variance and edge energy metrics.
"""

import numpy as np
from PIL import Image
from scipy.ndimage import laplace


class BlurDetector:
    """
    Computes image sharpness using Laplacian operator variance.
    Low variance indicates an out-of-focus or motion-blurred image.
    """
    def __init__(self, blur_threshold: float = 100.0, mild_blur_threshold: float = 250.0):
        self.blur_threshold = blur_threshold
        self.mild_blur_threshold = mild_blur_threshold

    def compute_laplacian_variance(self, image: Image.Image) -> float:
        """
        Converts image to greyscale and computes the variance of the Laplacian.
        """
        grey_img = image.convert("L")
        # Resize large images to standard benchmark dimension to ensure consistent scale
        if max(grey_img.size) > 1024:
            grey_img.thumbnail((1024, 1024), Image.Resampling.BILINEAR)
            
        img_array = np.array(grey_img, dtype=np.float32)
        laplacian = laplace(img_array)
        variance = float(np.var(laplacian))
        return round(variance, 2)

    def evaluate(self, image: Image.Image) -> dict:
        variance = self.compute_laplacian_variance(image)
        
        if variance < self.blur_threshold:
            status = "BLURRY"
            is_acceptable = False
            recommendation = "Severe blur detected. Keep the smartphone steady and tap to focus on the leaf."
        elif variance < self.mild_blur_threshold:
            status = "MILD_BLUR"
            is_acceptable = True
            recommendation = "Slight softness detected, but usable with limitations."
        else:
            status = "SHARP"
            is_acceptable = True
            recommendation = "Optimal sharpness for diagnostic inference."

        return {
            "metric": "laplacian_variance",
            "score": variance,
            "status": status,
            "is_acceptable": is_acceptable,
            "recommendation": recommendation
        }
