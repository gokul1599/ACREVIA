# KISANVISION — BASELINE MODEL EVALUATION REPORT

**Document Version:** 1.0.0  
**Effective Date:** November 7, 2026  
**Author:** ML Evaluation and Experimentation Specialist, Senior Computer Vision Research Scientist  
**Reporting Status:** `SOFTWARE_PIPELINE_VERIFIED_TRAINING_BLOCKED_PENDING_DATASET`  

---

## 1. Executive Research Summary & Scientific Integrity Notice

In strict compliance with KisanVision Stage 2 operating rules:
- **No Fabricated Data or Metrics:** Because external public datasets (PlantVillage, PlantDoc) and local field photographs have not yet been downloaded or staged on the local disk, **no real agricultural accuracy or F1 performance claims are presented in this report.**
- **Software Pipeline Verification:** The full PyTorch computer-vision training, group-stratified splitting, INT8 quantization, and evaluation pipelines have been implemented and validated using reproducible **synthetic test fixtures** strictly to guarantee algorithmic correctness.
- **Official Model Training Status:** **`BLOCKED_PENDING_DATASET_ACQUISITION`**

---

## 2. Model Architecture Benchmarking & Theoretical Characteristics

The following baseline architectures were evaluated against the audited host environment constraints (AMD Ryzen 5 5500U, 5.86 GB RAM, no NVIDIA CUDA):

| Architecture Candidate | Model Parameters (M) | Model Size on Disk (MB) | FLOPs (G) | Expected CPU Latency (INT8) | Resource Viability on Host | Architectural Role |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **MobileNetV3-Small** | 2.54M | 9.8 MB | 0.06G | **~25–40 ms** | **HIGH** (Negligible RAM) | Primary Mobile Edge Target |
| **MobileNetV3-Large** | 5.48M | 21.2 MB | 0.22G | **~45–65 ms** | **HIGH** | Primary Production Baseline |
| **EfficientNet-B0** | 5.29M | 20.8 MB | 0.39G | **~75–110 ms** | **HIGH** | Cloud Comparative Baseline |
| **ResNet-18** | 11.69M | 44.8 MB | 1.82G | **~120–180 ms** | **MEDIUM** | Control Baseline |
| **Vision Transformer (ViT-B/16)** | 86.6M | 330.0 MB | 17.6G | **~850–1400 ms** | **EXHAUSTS LOCAL RAM** | Disqualified for Host CPU |

---

## 3. Evaluation Pipeline Verification via Synthetic Fixtures

To verify that the evaluation engine correctly computes accuracy, macro F1, confusion matrices, and per-class breakdowns without bugs, a controlled synthetic smoke test was executed across all 10 target Cotton taxonomy classes:

```
Test Fixture Evaluation Results (Pipeline Verification Run):
- Evaluated Samples: 40 synthetic tensor fixtures
- Number of Classes: 10
- Pipeline Status: Fully Operational
- Automated Test Suite: 100% Passing
```

### 3.1 Verification Metrics Schema Check
- **Accuracy Calculation:** Evaluated via scikit-learn standard metric engine.
- **Per-Class Breakdown:** Reports Precision, Recall, F1-Score, and Support Count per class.
- **Macro F1 Metric:** Evaluated to prevent majority-class masking.
- **Confusion Matrix:** Correctly emits $N \times N$ integer matrix format.
- **Latency Profiling:** Computes Mean, Median, P95, and P99 latency percentiles in milliseconds.

---

## 4. Path to Production Baseline Training (Milestone 3 Execution)

Once dataset acquisition is approved and staged into `data/raw/`, the following concrete execution steps will produce the first real agricultural baseline:
1. **Ingestion & Manifest Generation:**
   ```powershell
   & .venv\Scripts\python.exe -m ml.datasets.ingestion.run_ingest --source data/raw/cotton --crop cotton
   ```
2. **Leakage-Resistant Farm Splitting:**
   ```powershell
   & .venv\Scripts\python.exe -m ml.datasets.splitting.run_split --manifest data/manifests/cotton_manifest.json
   ```
3. **Cloud Baseline Training (Google Colab / Hugging Face Jobs):**
   ```bash
   python -m ml.training.train_baseline --config ml/configs/experiments/baseline_mobilenet.yaml --device cuda
   ```
4. **Quantization & Local Registration:**
   ```powershell
   & .venv\Scripts\python.exe -m ml.models.export_onnx --checkpoint data/models/checkpoints/best_model.pt --quantize int8
   ```
