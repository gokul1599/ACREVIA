"""
KisanVision - Edge Architecture Benchmark Suite.
Compares MobileNetV3-Small, MobileNetV3-Large, ResNet-18, and EfficientNet-B0
across parameters, disk footprint, ONNX INT8 compression, and CPU latency percentiles.
"""

import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import torch
import onnxruntime as ort

from ml.models.classifier import KisanVisionClassifier
from ml.models.export_onnx import ONNXModelExporter

logger = logging.getLogger("kisanvision.benchmark")


class ArchitectureBenchmarkRunner:
    """
    Automated benchmark runner for agricultural edge vision models.
    """
    def __init__(
        self,
        output_dir: str = "ml/exports/benchmarks",
        warmup_runs: int = 5,
        timed_runs: int = 50,
        num_classes: int = 10
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.warmup_runs = warmup_runs
        self.timed_runs = timed_runs
        self.num_classes = num_classes
        self.exporter = ONNXModelExporter(export_dir=str(self.output_dir / "models"))

    def benchmark_architecture(
        self,
        architecture: str,
        input_shape: tuple = (1, 3, 224, 224)
    ) -> Dict[str, Any]:
        """
        Runs comprehensive benchmark on a single architecture.
        """
        logger.info(f"Initiating benchmark for architecture: {architecture}")
        
        # 1. Instantiate PyTorch Classifier
        model = KisanVisionClassifier(
            architecture=architecture,
            num_classes=self.num_classes,
            pretrained=False
        )
        model.eval()
        param_counts = model.get_parameter_counts()

        # 2. Export FP32 and Quantize to INT8 ONNX
        class_names = [f"class_{i}" for i in range(self.num_classes)]
        export_result = self.exporter.export_and_quantize(
            model=model,
            model_name=f"benchmark_{architecture}",
            class_names=class_names,
            crop_type="benchmark"
        )

        fp32_onnx_path = export_result["fp32_path"]
        int8_onnx_path = export_result["int8_path"]

        # 3. Benchmark PyTorch CPU Latency
        dummy_tensor = torch.randn(*input_shape)
        with torch.no_grad():
            for _ in range(self.warmup_runs):
                _ = model(dummy_tensor)

            pt_latencies = []
            for _ in range(self.timed_runs):
                t0 = time.perf_counter()
                _ = model(dummy_tensor)
                pt_latencies.append((time.perf_counter() - t0) * 1000.0)

        # 4. Benchmark ONNX FP32 CPU Latency
        session_fp32 = ort.InferenceSession(fp32_onnx_path, providers=["CPUExecutionProvider"])
        input_name_fp32 = session_fp32.get_inputs()[0].name
        output_name_fp32 = session_fp32.get_outputs()[0].name
        dummy_np = dummy_tensor.numpy()

        for _ in range(self.warmup_runs):
            _ = session_fp32.run([output_name_fp32], {input_name_fp32: dummy_np})

        ort_fp32_latencies = []
        for _ in range(self.timed_runs):
            t0 = time.perf_counter()
            _ = session_fp32.run([output_name_fp32], {input_name_fp32: dummy_np})
            ort_fp32_latencies.append((time.perf_counter() - t0) * 1000.0)

        # 5. Benchmark ONNX INT8 CPU Latency
        session_int8 = ort.InferenceSession(int8_onnx_path, providers=["CPUExecutionProvider"])
        input_name_int8 = session_int8.get_inputs()[0].name
        output_name_int8 = session_int8.get_outputs()[0].name

        for _ in range(self.warmup_runs):
            _ = session_int8.run([output_name_int8], {input_name_int8: dummy_np})

        ort_int8_latencies = []
        for _ in range(self.timed_runs):
            t0 = time.perf_counter()
            _ = session_int8.run([output_name_int8], {input_name_int8: dummy_np})
            ort_int8_latencies.append((time.perf_counter() - t0) * 1000.0)

        def calc_stats(lat_list: List[float]) -> Dict[str, float]:
            arr = np.array(lat_list)
            return {
                "mean_ms": round(float(np.mean(arr)), 2),
                "median_ms": round(float(np.median(arr)), 2),
                "p95_ms": round(float(np.percentile(arr, 95)), 2),
                "p99_ms": round(float(np.percentile(arr, 99)), 2),
                "fps": round(float(1000.0 / np.mean(arr)), 1)
            }

        fp32_size_mb = Path(fp32_onnx_path).stat().st_size / (1024 * 1024)
        int8_size_mb = Path(int8_onnx_path).stat().st_size / (1024 * 1024)

        return {
            "architecture": architecture,
            "parameters": param_counts,
            "file_size": {
                "fp32_onnx_mb": round(fp32_size_mb, 2),
                "int8_onnx_mb": round(int8_size_mb, 2),
                "compression_ratio": round(fp32_size_mb / max(int8_size_mb, 0.01), 2)
            },
            "latency": {
                "pytorch_cpu": calc_stats(pt_latencies),
                "onnx_fp32_cpu": calc_stats(ort_fp32_latencies),
                "onnx_int8_cpu": calc_stats(ort_int8_latencies)
            },
            "parity_vs_pytorch": export_result["int8_parity"],
            "edge_compliant": bool(calc_stats(ort_int8_latencies)["p95_ms"] < 200.0 and int8_size_mb < 15.0)
        }

    def run_suite(
        self,
        architectures: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Runs the benchmark suite across candidate architectures and generates summary.
        """
        archs = architectures or ["mobilenet_v3_small", "mobilenet_v3_large", "resnet18", "efficientnet_b0"]
        results = {}

        for arch in archs:
            results[arch] = self.benchmark_architecture(arch)

        # Generate markdown table summary
        markdown_table = self.generate_markdown_summary(results)

        suite_summary = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "host_environment": {
                "device": "AMD Ryzen 5 5500U CPU",
                "execution_provider": "CPUExecutionProvider",
                "timed_iterations": self.timed_runs,
                "warmup_iterations": self.warmup_runs
            },
            "benchmarks": results,
            "markdown_summary": markdown_table
        }

        summary_file = self.output_dir / "benchmark_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(suite_summary, f, indent=2)

        md_file = self.output_dir / "BENCHMARK_SUMMARY.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(markdown_table)

        logger.info(f"Benchmark suite completed. Results saved to {summary_file}")
        return suite_summary

    @staticmethod
    def generate_markdown_summary(results: Dict[str, Any]) -> str:
        """Formats benchmark results as a GitHub Flavored Markdown table."""
        lines = [
            "# KisanVision Edge Vision Architecture Benchmark Summary",
            "",
            "| Architecture | Total Params | FP32 Size | INT8 Size | Compression | INT8 p50 (ms) | INT8 p95 (ms) | INT8 FPS | Edge Compliant (<200ms, <15MB) |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
        ]

        for arch, data in results.items():
            params = f"{data['parameters']['total_parameters']:,}"
            fp32_mb = f"{data['file_size']['fp32_onnx_mb']} MB"
            int8_mb = f"{data['file_size']['int8_onnx_mb']} MB"
            comp = f"{data['file_size']['compression_ratio']}x"
            p50 = f"{data['latency']['onnx_int8_cpu']['median_ms']} ms"
            p95 = f"{data['latency']['onnx_int8_cpu']['p95_ms']} ms"
            fps = f"{data['latency']['onnx_int8_cpu']['fps']}"
            compliant = "PASSED" if data["edge_compliant"] else "EXCEEDS_BUDGET"

            lines.append(f"| `{arch}` | {params} | {fp32_mb} | {int8_mb} | {comp} | {p50} | {p95} | {fps} | **{compliant}** |")

        lines.append("")
        return "\n".join(lines)
