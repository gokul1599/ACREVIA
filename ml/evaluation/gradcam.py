"""
KisanVision - Explainability & Grad-CAM Visual Inspection Engine.
Computes gradient-weighted class activation mapping (Grad-CAM) to visualize
which foliar regions influenced convolutional network predictions.
"""

from typing import Tuple, Optional, Dict, Any
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F


class GradCAMExplainer:
    """
    Grad-CAM implementation for PyTorch convolutional backbones.
    """
    def __init__(self, model: nn.Module, target_layer: nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.gradients: Optional[torch.Tensor] = None
        self.activations: Optional[torch.Tensor] = None
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0].detach()

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate_cam(
        self,
        input_tensor: torch.Tensor,
        target_class_idx: Optional[int] = None
    ) -> np.ndarray:
        """
        Computes Grad-CAM heatmap for the specified class index.
        """
        self.model.eval()
        self.model.zero_grad()

        # Forward pass
        logits = self.model(input_tensor)
        if target_class_idx is None:
            target_class_idx = int(torch.argmax(logits, dim=-1).item())

        score = logits[0, target_class_idx]
        score.backward(retain_graph=True)

        if self.gradients is None or self.activations is None:
            raise RuntimeError("Gradients or activations were not captured by hooks.")

        # Global average pooling of gradients: alpha_k = (1/Z) * sum(grad)
        pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])

        # Weighted combination of activation maps: sum(alpha_k * A^k)
        for i in range(self.activations.size(1)):
            self.activations[:, i, :, :] *= pooled_gradients[i]

        heatmap = torch.mean(self.activations, dim=1).squeeze().cpu()
        heatmap = F.relu(heatmap)  # Keep only positive influence

        # Normalize heatmap to [0, 1]
        max_val = torch.max(heatmap)
        if max_val > 0:
            heatmap = heatmap / max_val

        return heatmap.numpy()

    @staticmethod
    def overlay_heatmap(
        pil_image: Image.Image,
        heatmap: np.ndarray,
        alpha: float = 0.4
    ) -> Image.Image:
        """
        Resizes heatmap to original image dimensions and creates visual overlay.
        """
        # Resize heatmap using PIL bilinear interpolation
        heat_img = Image.fromarray((heatmap * 255).astype(np.uint8)).resize(
            pil_image.size, Image.Resampling.BILINEAR
        )
        heat_np = np.asarray(heat_img, dtype=np.float32) / 255.0

        # Create false-color RGB overlay (Red = High attention, Blue = Low attention)
        color_map = np.zeros((*pil_image.size[::-1], 3), dtype=np.uint8)
        color_map[:, :, 0] = (heat_np * 255).astype(np.uint8)  # Red channel
        color_map[:, :, 1] = ((1.0 - np.abs(heat_np - 0.5) * 2.0) * 150).astype(np.uint8)  # Green
        color_map[:, :, 2] = ((1.0 - heat_np) * 200).astype(np.uint8)  # Blue

        color_img = Image.fromarray(color_map)
        blended = Image.blend(pil_image.convert("RGB"), color_img, alpha=alpha)
        return blended
