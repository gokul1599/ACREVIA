# MODEL CARD — KISANVISION MOBILENETV3-LARGE (SERVER BASELINE)

**Model Identifier:** `kisanvision_multicrop_mobilenet_v3_large`  
**Model Version:** 1.0.0  
**Release Date:** November 7, 2026  
**License:** Apache 2.0 (Code) / CC BY-NC 4.0 (Research Artifact)  
**Primary Intended Use:** High-Capacity Multi-Crop Backend Inference Server  
**Target Hardware:** Cloud / VPS Multi-Core CPU / Edge Gateways  
**Approval Status:** `APPROVED_FOR_INTERNAL_TESTING`  

---

## 1. Model Details

- **Developer:** KisanVision AI Research Team
- **Model Architecture:** MobileNetV3-Large with Squeeze-and-Excitation blocks and Hard-Swish non-linearities.
- **Parameters:** 3,221,051 (3.22M)
- **Backbone Feature Dimension:** 960
- **Precision:** INT8 Dynamic Quantization
- **Model File Size:** 11.54 MB (INT8 ONNX) / 12.23 MB (FP32 ONNX)
- **Input Dimensions:** $1 \times 3 \times 224 \times 224$ (RGB)

---

## 2. Empirical Performance & Benchmarks

Evaluated on host **AMD Ryzen 5 5500U CPU**:

| Metric | Measured Value | Server Budget Requirement |
| :--- | :---: | :---: |
| **Median Latency (p50)** | **5.95 ms** | $< 200.0\text{ ms}$ (**PASSED**) |
| **95th Percentile Latency (p95)** | **6.29 ms** | $< 200.0\text{ ms}$ (**PASSED**) |
| **Throughput** | **169.2 FPS** | $> 20.0\text{ FPS}$ (**PASSED**) |
| **Disk Footprint (INT8)** | **11.54 MB** | $< 15.0\text{ MB}$ (**PASSED**) |
| **Cosine Similarity vs FP32** | **0.988** | $\ge 0.980$ (**PASSED**) |

---

## 3. Deployment Guidance

- Recommended as the primary backend server inference engine when serving requests over mobile API gateways (`/api/v1/predict`).
- Provides enhanced representational capacity over MobileNetV3-Small for distinguishing visually similar foliar symptoms (e.g. Cotton Bacterial Blight vs Alternaria Spot).
