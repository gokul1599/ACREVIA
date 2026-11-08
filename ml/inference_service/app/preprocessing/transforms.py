"""
KisanVision Inference Service - Zero-Torch Image Preprocessor.
Pure NumPy and Pillow normalization pipeline for lightweight CPU execution.
"""

from typing import Tuple
import numpy as np
from PIL import Image


class InferencePreprocessor:
    """
    Standardized inference image normalization pipeline.
    """
    @staticmethod
    def preprocess(
        image: Image.Image,
        target_size: Tuple[int, int] = (224, 224)
    ) -> np.ndarray:
        """
        Transforms raw PIL image into normalized float32 tensor of shape (1, 3, H, W).
        """
        # Ensure RGB format
        rgb_img = image.convert("RGB")
        resized_img = rgb_img.resize(target_size, Image.Resampling.BILINEAR)

        # Scale pixel values to [0, 1]
        arr = np.asarray(resized_img, dtype=np.float32) / 255.0

        # ImageNet channel-wise mean and standard deviation
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        normalized = (arr - mean) / std

        # Transpose from (H, W, C) to (C, H, W) and expand batch dimension
        transposed = np.transpose(normalized, (2, 0, 1))
        batch_tensor = np.expand_dims(transposed, axis=0)
        return batch_tensor
