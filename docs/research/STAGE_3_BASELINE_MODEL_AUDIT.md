# KISANVISION — STAGE 3 BASELINE MODEL AUDIT

**Document Version:** 1.0.0  
**Audit Date:** November 7, 2026  
**Auditor:** Principal Computer Vision Research Scientist & MLOps Architect  
**Current Stage:** Stage 3 Entry Gate Assessment  

---

## 1. Stage 3 Entry Gate Classification

Before undertaking advanced ML engineering, the current project state is rigorously evaluated against the Stage 3 Entry Gate criteria:

| Gate Category | Description | Status |
| :--- | :--- | :---: |
| **A. Valid dataset and baseline model available** | Datasets downloaded on disk, trained weights converged on field data. | ❌ NOT MET |
| **B. Dataset available, baseline training incomplete** | Raw images staged in `data/raw/`, partial training runs executed. | ❌ NOT MET |
| **C. Software pipeline available, real dataset unavailable** | Ingestion, quality filtering, deduplication, splitting, PyTorch training, ONNX quantization, and evaluation pipelines fully implemented and tested via synthetic fixtures, but external raw datasets are not yet downloaded on local disk. | **✅ CURRENT STATE** |
| **D. Critical data, licensing or technical blockers remain** | Technical stack incompatible or severe licensing impediment. | ❌ CLEARED (CPython 3.11 pinned, non-commercial licenses quarantined) |

### Formal Entry Gate Declaration:
> **CLASSIFICATION: STATE C (Software Pipeline Available, Real Dataset Unavailable)**  
> In strict accordance with research integrity rules:
> 1. All architectural comparisons, uncertainty mechanisms, probability calibration tools, Out-of-Distribution filters, Grad-CAM utilities, and inference services will be developed and tested with verifiable synthetic fixtures and unit tests.
> 2. No fabricated accuracy, precision, or recall numbers will be reported.
> 3. Real training and validation benchmarks are formally classified as **`BLOCKED_PENDING_DATASET_ACQUISITION`**.

---

## 2. Comprehensive Audit of Stage 2 Experiments & Artifacts

### 2.1 Datasets and Version Registry
- **Target Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*).
- **Dataset Registry Status:**
  - `PlantVillage (CrowdAI v1.0)`: Planned ingestion for Rice & Chilli lab baselines. License: CC BY-SA 4.0.
  - `PlantDoc (IIT Delhi v1.0)`: Planned ingestion for in-field foliar validation. License: MIT.
  - `Mendeley Cotton Disease Dataset (v1.0)`: Planned ingestion for Cotton foliar baselines. License: CC BY 4.0.
  - `PJTSAU Telangana Field Pilot (v0.1)`: Target gold-standard research dataset. Status: Pending field collection.
- **Disk Storage Audit:**
  - `data/raw/`: Initialized, 0 raw images on disk.
  - `data/processed/`: Initialized, 0 processed manifests.
  - `data/splits/`: Initialized, verified with group-stratified split test fixtures.

### 2.2 Agricultural Taxonomy Audit
- **Schema File:** `ml/configs/taxonomy/taxonomy_schema.yaml` (v1.0.0)
- **Target Taxonomies:**
  - `cotton_taxonomy.yaml`: 10 classes (1 Healthy, 6 Diseases, 2 Pests, 1 Deficiency).
  - `rice_taxonomy.yaml`: 10 classes (1 Healthy, 6 Diseases, 2 Pests, 1 Deficiency).
  - `chilli_taxonomy.yaml`: 8 classes (1 Healthy, 5 Diseases, 1 Pest, 1 Deficiency).
- **Total Diagnostic Scope:** 28 distinct agricultural classes.
- **Multi-Lingual Compliance:** 100% of classes contain verified names in English, Telugu (తెలుగు), and Hindi (हिन्दी) citing PJTSAU and ICAR authorities.

### 2.3 Model Architecture & Training Engine Audit
- **Module:** `ml/models/classifier.py` ([`KisanVisionClassifier`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/models/classifier.py#L15))
- **Backbone Factory:** `ml/models/backbones.py` ([`build_backbone`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/models/backbones.py#L12))
  - Supported: `mobilenet_v3_small`, `mobilenet_v3_large`, `resnet18`, `resnet50`, `efficientnet_b0`.
- **Classification Head:** Linear(in_features, 256) -> BatchNorm1d -> ReLU -> Dropout(0.1) -> Linear(256, num_classes).
- **Temperature Parameter:** `nn.Parameter(torch.tensor(temperature), requires_grad=False)`.
- **Training Engine:** `ml/training/trainer.py` ([`KisanVisionTrainer`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/training/trainer.py#L22))
  - AdamW optimizer, CrossEntropyLoss with class weights, ReduceLROnPlateau, Early Stopping (patience=5), Checkpoint saving.

### 2.4 Preprocessing & Leakage Prevention Audit
- **Transforms:** `ml/datasets/transforms/pipeline.py` ([`KisanVisionTransforms`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/datasets/transforms/pipeline.py#L16))
  - Input resolution: $224 \times 224 \times 3$.
  - Normalization: ImageNet mean `[0.485, 0.456, 0.406]`, std `[0.229, 0.224, 0.225]`.
- **Group Leakage Prevention:** `ml/datasets/splitting/group_splitter.py` ([`GroupStratifiedSplitter`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/datasets/splitting/group_splitter.py#L17))
  - Enforces 0% overlap of `farm_id` across train (70%), validation (15%), and test (15%).
- **Deduplication Audit:** `ml/datasets/deduplication/`
  - Exact duplicates blocked via SHA-256 hash.
  - Near-duplicates blocked via 64-bit difference hash ($dHash$) with Hamming distance threshold $D_H \le 4$.

### 2.5 Compute Environment Audit
- **OS:** Windows 11 Home (Build 26100).
- **CPU:** AMD Ryzen 5 5500U with Radeon Graphics (6 Cores, 12 Threads @ 2.10 GHz).
- **RAM:** 5.86 GB total (~1.0 GB available during normal execution).
- **GPU:** Integrated AMD Radeon Graphics (2 GB shared VRAM). No discrete NVIDIA CUDA acceleration.
- **Python Runtime:** CPython 3.11.16 isolated in `.venv` via Astral `uv`.

---

## 3. Checkpoint Provenance & Reproducibility Verification

1. **Checkpoint Integrity:**
   - Synthetic smoke test checkpoints verified at `ml/models/` and `ml/exports/`.
   - All state dicts load cleanly without key mismatches or missing weights.
2. **Model Graph & Export Verification:**
   - FP32 ONNX export and Dynamic INT8 quantization verified via `ml/models/export_onnx.py`.
   - Cosine similarity between PyTorch and INT8 ONNX verified at $\ge 0.985$.
3. **Known Weaknesses Documented:**
   - **Absence of Real Field Training:** While algorithms are verified, models have not yet learned real foliar biological features from actual field images.
   - **No Discrete GPU:** Cloud execution (Google Colab / Kaggle / Hugging Face Jobs) is required for full multi-epoch backbone pretraining before exporting INT8 weights to local CPU.

---

## 4. Audit Sign-Off

The Stage 2 engineering artifacts have been inspected and confirmed to be structurally sound, leakage-resistant, and strictly compliant with scientific honesty guidelines.

Proceed to **Task B (Advanced Model Architecture Benchmarking)** and **Task C (Multi-Crop Intelligence Architecture)**.
