"""
KisanVision - Field Robustness & Perturbation Evaluation Harness.
Systematically tests vision models against simulated Telangana field conditions:
intense tropical solar glare, deep canopy shadows, camera blur, JPEG compression, and noise.
"""

from typing import Dict, Any, List, Tuple
import io
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import torch
import torch.nn.functional as F


class FieldRobustnessHarness:
    """
    Applies calibrated agricultural perturbations to evaluate model degradation.
    """
    def __init__(self):
        self.perturbation_types = [
            "direct_solar_glare",
            "canopy_shadow",
            "camera_blur",
            "jpeg_compression",
            "sensor_noise",
            "leaf_rotation"
        ]

    @staticmethod
    def apply_solar_glare(image: Image.Image, factor: float = 1.5) -> Image.Image:
        """Simulates intense direct mid-day tropical sun glare."""
        enhancer = ImageEnhance.Brightness(image)
        bright = enhancer.enhance(factor)
        contrast = ImageEnhance.Contrast(bright)
        return contrast.enhance(1.2)

    @staticmethod
    def apply_canopy_shadow(image: Image.Image, factor: float = 0.5) -> Image.Image:
        """Simulates deep canopy shadow and dense foliage occlusion."""
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

    @staticmethod
    def apply_camera_blur(image: Image.Image, radius: float = 2.5) -> Image.Image:
        """Simulates camera shake or hand movement common in field photography."""
        return image.filter(ImageFilter.GaussianBlur(radius=radius))

    @staticmethod
    def apply_jpeg_compression(image: Image.Image, quality: int = 25) -> Image.Image:
        """Simulates WhatsApp / low-bandwidth mobile network compression."""
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=quality)
        buf.seek(0)
        return Image.open(buf)

    @staticmethod
    def apply_sensor_noise(image: Image.Image, sigma: float = 20.0) -> Image.Image:
        """Simulates low-cost CMOS sensor electronic noise in low-light conditions."""
        arr = np.asarray(image, dtype=np.float32)
        noise = np.random.normal(0, sigma, arr.shape)
        noisy_arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy_arr)

    @staticmethod
    def apply_leaf_rotation(image: Image.Image, angle: float = 90.0) -> Image.Image:
        """Rotates leaf orientation arbitrarily."""
        return image.rotate(angle, expand=False)

    def perturb_image(self, image: Image.Image, perturbation: str, severity: float = 1.0) -> Image.Image:
        """Applies a named perturbation with scaled severity."""
        if perturbation == "direct_solar_glare":
            return self.apply_solar_glare(image, factor=1.0 + 0.5 * severity)
        elif perturbation == "canopy_shadow":
            return self.apply_canopy_shadow(image, factor=max(0.2, 1.0 - 0.5 * severity))
        elif perturbation == "camera_blur":
            return self.apply_camera_blur(image, radius=1.0 * severity)
        elif perturbation == "jpeg_compression":
            q = max(10, int(85 - 50 * severity))
            return self.apply_jpeg_compression(image, quality=q)
        elif perturbation == "sensor_noise":
            return self.apply_sensor_noise(image, sigma=15.0 * severity)
        elif perturbation == "leaf_rotation":
            return self.apply_leaf_rotation(image, angle=45.0 * severity)
        else:
            raise ValueError(f"Unknown perturbation: {perturbation}")

    def evaluate_model_robustness(
        self,
        model,
        test_images: List[Image.Image],
        true_labels: List[int],
        preprocess_fn,
        device: str = "cpu"
    ) -> Dict[str, Any]:
        """
        Tests model performance across clean vs perturbed samples.
        """
        model.eval()
        results = {"clean_accuracy": 0.0, "perturbations": {}}

        # 1. Clean Baseline
        clean_correct = 0
        total = len(test_images)
        for img, lbl in zip(test_images, true_labels):
            tensor = preprocess_fn(img).to(device)
            with torch.no_grad():
                logits = model(tensor)
                pred = int(torch.argmax(logits, dim=-1).item())
                if pred == lbl:
                    clean_correct += 1

        clean_acc = clean_correct / total if total > 0 else 0.0
        results["clean_accuracy"] = round(clean_acc, 4)

        # 2. Perturbed Evaluations
        for pert in self.perturbation_types:
            pert_correct = 0
            for img, lbl in zip(test_images, true_labels):
                perturbed_img = self.perturb_image(img, pert, severity=1.0)
                tensor = preprocess_fn(perturbed_img).to(device)
                with torch.no_grad():
                    logits = model(tensor)
                    pred = int(torch.argmax(logits, dim=-1).item())
                    if pred == lbl:
                        pert_correct += 1

            pert_acc = pert_correct / total if total > 0 else 0.0
            acc_drop = clean_acc - pert_acc
            results["perturbations"][pert] = {
                "accuracy": round(pert_acc, 4),
                "accuracy_drop": round(acc_drop, 4),
                "relative_retention": round(pert_acc / max(clean_acc, 1e-4), 4)
            }

        return results
