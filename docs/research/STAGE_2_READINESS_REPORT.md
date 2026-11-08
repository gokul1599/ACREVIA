# KISANVISION — STAGE 2 ENVIRONMENT & DATASET READINESS REPORT

**Document Version:** 1.0.0  
**Audit Date:** November 7, 2026  
**Auditor Roles:** Principal ML Engineer, Senior Computer Vision Research Scientist, MLOps Engineer  
**Scope:** Stage 2 Pre-Execution Verification of Hardware, Python ML Runtime, Datasets, and Licensing  

---

## 1. Environment & Hardware Audit Results

A programmatic audit of the host environment was performed prior to executing Stage 2 dataset and ML operations:

| Component | Detected Specification | ML Readiness Assessment | Notes & Operational Constraints |
| :--- | :--- | :--- | :--- |
| **Operating System** | Windows 11 Home Single Language (Build 64-bit) | **READY** | Compatible with Python asyncio and PyTorch CPU wheels |
| **CPU** | AMD Ryzen 5 5500U with Radeon Graphics (6 Cores / 12 Threads, 2.1 GHz) | **READY** | Highly capable for multi-threaded CPU inference and data preprocessing |
| **RAM** | 5.86 GB Total (~1.0 GB Free under baseline load) | **CONSTRAINED** | Memory budget strictly limits batch sizes ($\le 16$) and prevents local training of heavy ViT backbones |
| **GPU / Acceleration** | AMD Radeon Graphics (Integrated, 2 GB shared VRAM) | **NO CUDA ACCELERATION** | NVIDIA CUDA runtime is **NOT AVAILABLE**. PyTorch operates in CPU mode. |
| **Available Storage** | C: Drive: 150.21 GB Used / **325.48 GB Free** | **EXCELLENT** | Sufficient storage for raw/processed datasets, checkpoints, and artifacts |
| **System Python** | Python 3.14.7 | **INCOMPATIBLE** | Lacks C-extension wheel support for PyTorch 2.x and OpenCV |
| **Managed Runtime** | **CPython 3.11.16** via Astral `uv` (`.venv\Scripts\python.exe`) | **FULLY OPERATIONAL** | Pinned CPython 3.11 runtime verified with PyTorch 2.15 CPU, torchvision, numpy, pandas, scikit-learn |
| **Git Status** | Working directory clean; isolated within `projects/` boundary | **READY** | `.gitignore` rules implemented to prevent committing large datasets and weights |

---

## 2. Dataset Readiness & Acquisition Status

| Dataset Source | Target Crops Covered | Verified Download Status | Licensing & Usage Terms | Known Limitations |
| :--- | :--- | :--- | :--- | :--- |
| **PlantVillage** | Pepper (Chilli), Cotton (Limited), Rice (None) | **NOT YET DOWNLOADED** (Clean slate) | CC-BY 4.0 | Lab-photographed leaves on plain grey backgrounds. High domain shift; inadequate for raw field deployment. |
| **PlantDoc** | Rice, Pepper, Cotton (Subset) | **NOT YET DOWNLOADED** (Clean slate) | MIT License | In-field imagery with background clutter; modest sample size (~2,598 images total across 13 species). |
| **Mendeley Cotton / Rice Sets** | Cotton & Rice diseases | **NOT YET DOWNLOADED** (Clean slate) | CC-BY 4.0 | Skewed class distributions; requires manual deduplication and label alignment. |
| **Local Telangana Field Photos** | Cotton, Rice, Chilli (including *Thrips parvispinus*) | **NOT AVAILABLE** (Pending Field Collection) | Proprietary with DPDPA Consent | Ground-truth localized imagery to be acquired in partnership with regional extension officers. |

---

## 3. Training Feasibility & Mode Determination

### 3.1 Feasibility Analysis
1. **Local Host Execution:** Local CPU compute (AMD Ryzen 5500U) is optimal for data ingestion pipelines, quality validation, perceptual hash deduplication, synthetic fixture smoke tests, and ONNX INT8 CPU inference.
2. **Heavy Backbone Training:** Training deep vision models (e.g., EfficientNet-B0 or ResNet-50) on 50,000+ high-resolution images locally on CPU with 5.86 GB RAM is mathematically and temporally prohibitive (estimated 48+ hours per epoch with high OOM paging risk). Heavy training is designated for cloud GPU environments (Google Colab T4 / Hugging Face Jobs / Kaggle).

### 3.2 Recommended Stage 2 Execution Mode

**DETERMINED MODE:** **`CPU_ONLY` & `CLOUD_TRAINING_REQUIRED` (with `DATASET_BLOCKED` for full external training; `READY_FOR_BASELINE` on synthetic/smoke test fixtures)**

- The entire data engineering, quality filtering, deduplication, group splitting, and model framework will be implemented and tested using **CPU-compatible PyTorch 2.15** on CPython 3.11.
- In strict adherence to Stage 2 operating rules, because raw commercial/public datasets are not yet downloaded into local storage, the pipeline will be verified using **reproducible synthetic test fixtures**.
- Full-scale training on external multi-gigabyte datasets will be marked as `DATASET_BLOCKED_PENDING_ACQUISITION`.
