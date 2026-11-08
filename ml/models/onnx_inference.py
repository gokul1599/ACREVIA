"""
KisanVision - Production ONNX Inference Engine.
Provides lightweight, pure NumPy/Pillow preprocessed CPU inference for
quantized INT8 agricultural vision models.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np
from PIL import Image
import onnxruntime as ort

from ml.models.ood_detector import FoliarImageDetector, ModelUncertaintyAuditor

logger = logging.getLogger("kisanvision.onnx_engine")


class ONNXInferenceEngine:
    """
    High-performance CPU inference session manager for quantized ONNX vision models.
    """
    def __init__(
        self,
        model_path: Union[str, Path],
        manifest_path: Optional[Union[str, Path]] = None,
        crop_type: Optional[str] = None
    ):
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"ONNX model file does not exist: {self.model_path}")

        # Configure optimized CPU execution provider
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = min(4, os.cpu_count() or 2)
        opts.inter_op_num_threads = 1
        opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        self.session = ort.InferenceSession(
            str(self.model_path),
            sess_options=opts,
            providers=["CPUExecutionProvider"]
        )

        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

        # Load manifest if available
        self.manifest = {}
        if manifest_path and Path(manifest_path).exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                self.manifest = json.load(f)

        self.crop_type = crop_type or self.manifest.get("crop_type", "unknown")
        self.class_names = self.manifest.get("class_names", [])
        self.temperature = float(self.manifest.get("temperature", 1.0))

        # Defense systems
        self.foliar_detector = FoliarImageDetector()
        self.uncertainty_auditor = ModelUncertaintyAuditor()

    @staticmethod
    def preprocess_image(
        pil_image: Image.Image,
        target_size: Tuple[int, int] = (224, 224)
    ) -> np.ndarray:
        """
        Pure NumPy & Pillow ImageNet preprocessing pipeline (Zero-Torch inference).
        1. RGB conversion.
        2. Bilinear resize to target_size.
        3. Normalization: (x / 255.0 - mean) / std.
        4. Transpose to (1, 3, H, W) float32 array.
        """
        img = pil_image.convert("RGB")
        img_resized = img.resize(target_size, Image.Resampling.BILINEAR)

        # Convert to float array [0, 1]
        arr = np.asarray(img_resized, dtype=np.float32) / 255.0

        # Standard ImageNet Mean and Standard Deviation
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        arr = (arr - mean) / std

        # Transpose from (H, W, C) to (C, H, W) and add batch dimension
        arr_transposed = np.transpose(arr, (2, 0, 1))
        input_tensor = np.expand_dims(arr_transposed, axis=0)
        return input_tensor

    def predict(
        self,
        pil_image: Image.Image,
        class_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Executes full inference lifecycle:
        1. Foliar content verification (Tier 1 OOD check).
        2. Preprocessing.
        3. ONNX session execution.
        4. Temperature scaling & softmax.
        5. Uncertainty & differential diagnosis (Tier 2 OOD check).
        """
        active_class_names = class_names or self.class_names
        
        # 1. Tier 1 Foliar Check
        foliar_report = self.foliar_detector.analyze_foliar_content(pil_image)
        if not foliar_report["is_foliar"]:
            return {
                "success": False,
                "status": "OOD_NON_PLANT",
                "diagnosis": None,
                "foliar_validation": foliar_report,
                "message": "Image does not appear to contain foliar crop material. Please capture a clear leaf photo."
            }

        # 2. Preprocess
        input_tensor = self.preprocess_image(pil_image)

        # 3. ONNX Inference
        ort_inputs = {self.input_name: input_tensor}
        raw_logits = self.session.run([self.output_name], ort_inputs)[0][0]

        # 4. Temperature Scaling & Softmax
        scaled_logits = raw_logits / max(self.temperature, 0.1)
        exp_logits = np.exp(scaled_logits - np.max(scaled_logits))
        probabilities = exp_logits / np.sum(exp_logits)

        # 5. Tier 2 Uncertainty & Differential Diagnosis
        if not active_class_names:
            active_class_names = [f"class_{i}" for i in range(len(probabilities))]

        uncertainty_report = self.uncertainty_auditor.evaluate_uncertainty(
            probabilities=probabilities,
            class_names=active_class_names
        )

        return {
            "success": True,
            "status": uncertainty_report["status"],
            "action": uncertainty_report["action"],
            "crop_type": self.crop_type,
            "diagnosis": {
                "predicted_class": uncertainty_report["top1_class"],
                "confidence": uncertainty_report["top1_confidence"],
                "normalized_entropy": uncertainty_report["normalized_entropy"],
                "prediction_margin": uncertainty_report["prediction_margin"]
            },
            "differential_candidates": uncertainty_report["differential_candidates"],
            "uncertainty_reasons": uncertainty_report["reasons"],
            "foliar_validation": foliar_report
        }
