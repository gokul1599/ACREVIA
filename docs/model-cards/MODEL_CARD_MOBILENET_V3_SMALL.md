# MODEL CARD — KISANVISION MOBILENETV3-SMALL (INT8 EDGE CANDIDATE)

**Model Identifier:** `kisanvision_multicrop_mobilenet_v3_small`  
**Model Version:** 1.0.0  
**Release Date:** November 7, 2026  
**License:** Apache 2.0 (Code) / CC BY-NC 4.0 (Research Artifact)  
**Primary Intended Use:** Mobile Edge & PWA Client-Side Foliar Crop Disease Triage  
**Target Hardware:** Commodity Android Smartphones & Low-Resource CPUs (<200ms latency)  
**Approval Status:** `APPROVED_FOR_INTERNAL_TESTING`  

---

## 1. Model Details

- **Developer:** KisanVision AI Research Team (Antigravity Environment)
- **Model Architecture:** MobileNetV3-Small with Hard-Swish activations and Squeeze-and-Excitation attention blocks.
- **Backbone Feature Dimension:** 576
- **Precision:** INT8 Post-Training Dynamic Quantization (`ort.quantization.QuantType.QInt8`)
- **Model File Size:** 3.69 MB (INT8 ONNX) / 4.10 MB (FP32 ONNX)
- **Input Dimensions:** $1 \times 3 \times 224 \times 224$ (RGB)
- **Preprocessing:** Bilinear resize to $224 \times 224$; ImageNet normalization ($\mu = [0.485, 0.456, 0.406], \sigma = [0.229, 0.224, 0.225]$).

---

## 2. Intended Use & Target Scope

- **Supported Crops:**
  1. Cotton (*Gossypium hirsutum*): 10 Classes
  2. Rice (*Oryza sativa*): 10 Classes
  3. Chilli (*Capsicum annuum*): 8 Classes
- **Total Diagnostic Classes:** 28 Agricultural Conditions (PJTSAU Taxonomy v1.0.0).
- **Out-of-Scope Uses:**
  - Diagnosing non-foliar symptoms (root rot, vascular wilt without foliar expression).
  - Diagnosing unsupported crops (e.g. Maize, Sugarcane, Mango).
  - Unilateral autonomous chemical prescription without agronomist or CIBRC verification.

---

## 3. Empirical Performance & Hardware Benchmarks

Evaluated on host **AMD Ryzen 5 5500U CPU** (Single Core, Batch Size 1):

| Metric | Measured Value | Edge Budget Requirement |
| :--- | :---: | :---: |
| **Median Latency (p50)** | **3.02 ms** | $< 200.0\text{ ms}$ (**PASSED — 66x faster**) |
| **95th Percentile Latency (p95)** | **4.80 ms** | $< 200.0\text{ ms}$ (**PASSED**) |
| **99th Percentile Latency (p99)** | **6.10 ms** | $< 200.0\text{ ms}$ (**PASSED**) |
| **Throughput** | **307.0 FPS** | $> 10.0\text{ FPS}$ (**PASSED**) |
| **Disk Footprint (INT8)** | **3.69 MB** | $< 15.0\text{ MB}$ (**PASSED — 4x smaller**) |
| **Cosine Similarity vs FP32** | **0.985** | $\ge 0.980$ (**PASSED**) |

---

## 4. Ethical, Social & Agricultural Considerations

1. **Uncertainty & Abstention Invariant:**
   The model is strictly coupled with the `AbstentionEngine`. If confidence $< 0.85$ or normalized entropy $> 0.65$, it declares `LOW_CONFIDENCE` or `EXPERT_REVIEW_REQUIRED` and refuses unilateral diagnosis.
2. **CIBRC Advisory Mandatory:**
   No output is presented to a farmer without the CIBRC compliance warning requiring official label verification.
3. **No Phantom Accuracy Claims:**
   While the software architecture is fully verified, real-world accuracy on Telangana soil remains marked as `BLOCKED_PENDING_DATASET_ACQUISITION`.
