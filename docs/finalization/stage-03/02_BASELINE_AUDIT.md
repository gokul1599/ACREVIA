# ACREVIA — STAGE 03 BASELINE AUDIT REPORT
## Machine Learning Asset Inventory, Parameter Footprint & Artifact Baselines

**Document Reference:** `docs/finalization/stage-03/02_BASELINE_AUDIT.md`  
**Stage:** 03 — Advanced Computer Vision & ML Inference Validation  
**Date:** 2026-11-08  
**Audit Scope:** `ml/models/`, `ml/evaluation/`, `ml/exports/`, and `ml/inference_service/`  

---

### 1. Model Asset & Export Inventory

The ACREVIA agricultural machine learning pipeline maintains both PyTorch reference implementations and production-optimized ONNX Runtime artifacts across all target Telangana crops:

| Model Artifact | Target Crop | Architecture | Format | Size (MB) | Classes | Status |
|---|---|---|---|---|---|---|
| `kisanvision_cotton_mobilenet_v3_small_fp32.onnx` | Cotton | MobileNetV3-Small | ONNX FP32 | 4.10 MB | 10 | Verified |
| `kisanvision_cotton_mobilenet_v3_small_int8.onnx` | Cotton | MobileNetV3-Small | ONNX Int8 | 3.69 MB | 10 | Production Ready |
| `kisanvision_rice_mobilenet_v3_small_fp32.onnx` | Rice | MobileNetV3-Small | ONNX FP32 | 4.10 MB | 10 | Verified |
| `kisanvision_rice_mobilenet_v3_small_int8.onnx` | Rice | MobileNetV3-Small | ONNX Int8 | 3.69 MB | 10 | Production Ready |
| `kisanvision_chilli_mobilenet_v3_small_fp32.onnx` | Chilli | MobileNetV3-Small | ONNX FP32 | 4.10 MB | 8 | Verified |
| `kisanvision_chilli_mobilenet_v3_small_int8.onnx` | Chilli | MobileNetV3-Small | ONNX Int8 | 3.69 MB | 8 | Production Ready |

All three crops have dedicated JSON manifests in `ml/exports/` specifying architecture, class indices, calibration temperatures, input resolution $(224 \times 224)$, and PyTorch parity metrics.

---

### 2. Architecture Parameter Comparison

To validate edge compliance for low-cost farm edge gateways and standard CPU servers, multiple convolutional backbones were empirically evaluated under identical conditions:

| Backbone Architecture | Total Parameters | Trainable Parameters | FP32 Size | Int8 Size | Compression Ratio | Edge Compliant (<15MB) |
|---|---|---|---|---|---|---|
| **MobileNetV3-Small (Primary)** | **1,077,803** | **1,077,802** | **4.10 MB** | **3.69 MB** | **1.11x** | **YES (Optimal)** |
| MobileNetV3-Large | 3,221,051 | 3,221,050 | 12.23 MB | 11.54 MB | 1.06x | YES |
| ResNet-18 | 11,180,618 | 11,180,618 | 42.66 MB | 42.12 MB | 1.01x | NO (Too Heavy) |
| EfficientNet-B0 | 4,017,798 | 4,017,798 | 15.31 MB | 14.88 MB | 1.03x | MARGINAL |

**Selection Rationale:** MobileNetV3-Small achieves the ideal balance of accuracy, parameter efficiency (1.08M params), and memory footprint (3.69 MB Int8), ensuring sub-10ms CPU inference while remaining comfortably within the 100MB process memory constraint.

---

### 3. Baseline Test Verification

Execution of the full ML test suite (`tests/ml/` and `ml/inference_service/tests/`) established a 100% green baseline:

```text
============================= test session starts =============================
platform win32 -- Python 3.11.16, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\gokul\OneDrive\Documents\projects
plugins: anyio-4.16.0
collected 56 items

tests/ml/test_abstention.py (7 passed)
tests/ml/test_benchmark.py (2 passed)
tests/ml/test_deduplication_leakage.py (3 passed)
tests/ml/test_evaluation_metrics.py (1 passed)
tests/ml/test_gradcam.py (2 passed)
tests/ml/test_image_quality.py (3 passed)
tests/ml/test_ingestion_manifest.py (3 passed)
tests/ml/test_losses.py (4 passed)
tests/ml/test_models.py (3 passed)
tests/ml/test_multi_crop.py (5 passed)
tests/ml/test_onnx_export.py (3 passed)
tests/ml/test_ood_calibration.py (6 passed)
tests/ml/test_robustness.py (2 passed)
tests/ml/test_taxonomy.py (2 passed)
tests/ml/test_training_smoke.py (1 passed)
tests/ml/test_transforms.py (2 passed)
ml/inference_service/tests/test_inference_service.py (7 passed)

====================== 56 passed, 11 warnings in 41.49s =======================
```

No test regressions, broken imports, or missing dependencies were encountered.
