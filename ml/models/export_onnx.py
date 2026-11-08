"""
KisanVision - ONNX Model Exporter and Quantization Engine.
Exports PyTorch foliar classifiers to ONNX format and applies post-training
dynamic INT8 quantization for sub-200ms CPU inference.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import numpy as np
import torch
import onnx
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, QuantType

from ml.models.classifier import KisanVisionClassifier

logger = logging.getLogger("kisanvision.onnx_exporter")


class ONNXModelExporter:
    """
    Handles FP32 ONNX export, graph verification, and dynamic INT8 quantization.
    """
    def __init__(self, export_dir: str = "ml/exports"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_fp32(
        self,
        model: KisanVisionClassifier,
        model_name: str,
        input_shape: Tuple[int, int, int, int] = (1, 3, 224, 224),
        opset_version: int = 17
    ) -> Path:
        """
        Exports PyTorch classifier to FP32 ONNX format with dynamic batch axis.
        """
        model.eval()
        output_path = self.export_dir / f"{model_name}_fp32.onnx"
        dummy_input = torch.randn(*input_shape, requires_grad=False)

        # Dynamic batch dimension for flexible inference batching
        dynamic_axes = {
            "input": {0: "batch_size"},
            "logits": {0: "batch_size"}
        }

        logger.info(f"Exporting PyTorch model to FP32 ONNX: {output_path}")
        torch.onnx.export(
            model,
            dummy_input,
            str(output_path),
            export_params=True,
            opset_version=opset_version,
            do_constant_folding=True,
            input_names=["input"],
            output_names=["logits"],
            dynamic_axes=dynamic_axes,
            dynamo=False
        )

        # Validate ONNX model graph structure
        onnx_model = onnx.load(str(output_path))
        onnx.checker.check_model(onnx_model)
        logger.info(f"Successfully verified FP32 ONNX model graph: {output_path}")

        return output_path

    def quantize_int8(
        self,
        fp32_onnx_path: Path,
        quantized_name: Optional[str] = None
    ) -> Path:
        """
        Applies dynamic INT8 post-training quantization to reduce model footprint
        and optimize CPU instruction execution.
        """
        if not fp32_onnx_path.exists():
            raise FileNotFoundError(f"Source FP32 ONNX model not found: {fp32_onnx_path}")

        base_name = fp32_onnx_path.stem.replace("_fp32", "")
        q_name = quantized_name or f"{base_name}_int8.onnx"
        output_path = self.export_dir / q_name

        logger.info(f"Quantizing ONNX model to INT8: {output_path}")
        quantize_dynamic(
            model_input=str(fp32_onnx_path),
            model_output=str(output_path),
            weight_type=QuantType.QInt8,
            op_types_to_quantize=["MatMul", "Gemm"]
        )

        # Validate quantized ONNX model
        q_model = onnx.load(str(output_path))
        onnx.checker.check_model(q_model)
        logger.info(f"Successfully verified INT8 ONNX model: {output_path}")

        return output_path

    def verify_parity(
        self,
        pytorch_model: KisanVisionClassifier,
        onnx_path: Path,
        test_samples: int = 5,
        tolerance: float = 1e-4
    ) -> Dict[str, Any]:
        """
        Compares PyTorch forward pass outputs with ONNX Runtime session outputs.
        """
        pytorch_model.eval()
        session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name

        max_diff = 0.0
        cosine_similarities = []
        top1_matches = 0

        for _ in range(test_samples):
            dummy_input = torch.randn(1, 3, 224, 224)
            
            with torch.no_grad():
                pt_logits = pytorch_model(dummy_input).numpy()

            ort_inputs = {input_name: dummy_input.numpy()}
            ort_logits = session.run([output_name], ort_inputs)[0]

            # Parity metrics
            diff = np.max(np.abs(pt_logits - ort_logits))
            if diff > max_diff:
                max_diff = float(diff)

            # Cosine similarity
            dot = np.dot(pt_logits.flatten(), ort_logits.flatten())
            norm_pt = np.linalg.norm(pt_logits)
            norm_ort = np.linalg.norm(ort_logits)
            cos_sim = float(dot / (norm_pt * norm_ort + 1e-8))
            cosine_similarities.append(cos_sim)

            # Top-1 class agreement
            if np.argmax(pt_logits) == np.argmax(ort_logits):
                top1_matches += 1

        is_fp32 = "fp32" in onnx_path.name
        passed = (max_diff <= tolerance) if is_fp32 else (np.mean(cosine_similarities) >= 0.98)

        file_size_mb = onnx_path.stat().st_size / (1024 * 1024)

        return {
            "onnx_path": str(onnx_path),
            "file_size_mb": round(file_size_mb, 2),
            "max_absolute_difference": float(max_diff),
            "mean_cosine_similarity": round(float(np.mean(cosine_similarities)), 5),
            "top1_agreement_rate": round(float(top1_matches / test_samples), 4),
            "verification_passed": bool(passed)
        }

    def export_and_quantize(
        self,
        model: KisanVisionClassifier,
        model_name: str,
        class_names: List[str],
        crop_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end export: FP32 export -> INT8 quantization -> Parity check -> Manifest emission.
        """
        # 1. FP32 Export
        fp32_path = self.export_fp32(model, model_name)
        fp32_parity = self.verify_parity(model, fp32_path)

        # 2. INT8 Quantization
        int8_path = self.quantize_int8(fp32_path)
        int8_parity = self.verify_parity(model, int8_path)

        # 3. Model Manifest
        manifest = {
            "model_name": model_name,
            "architecture": model.architecture,
            "crop_type": crop_type,
            "num_classes": len(class_names),
            "class_names": class_names,
            "temperature": float(model.temperature.item()),
            "input_resolution": [224, 224],
            "fp32_model": {
                "path": str(fp32_path.name),
                "size_mb": fp32_parity["file_size_mb"],
                "max_diff_vs_pytorch": fp32_parity["max_absolute_difference"]
            },
            "int8_model": {
                "path": str(int8_path.name),
                "size_mb": int8_parity["file_size_mb"],
                "cosine_sim_vs_pytorch": int8_parity["mean_cosine_similarity"],
                "top1_agreement": int8_parity["top1_agreement_rate"]
            },
            "compression_ratio": round(fp32_parity["file_size_mb"] / max(int8_parity["file_size_mb"], 0.01), 2),
            "extra_metadata": metadata or {}
        }

        manifest_path = self.export_dir / f"{model_name}_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Export manifest saved to {manifest_path}")

        return {
            "fp32_path": str(fp32_path),
            "int8_path": str(int8_path),
            "manifest_path": str(manifest_path),
            "fp32_parity": fp32_parity,
            "int8_parity": int8_parity,
            "manifest": manifest
        }
