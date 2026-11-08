# ACREVIA — DATASET REPRODUCIBILITY & TRAINING IMMUTABILITY REPORT
## SCIENTIFIC REPRODUCIBILITY, MANIFEST LOCKING & VERSION CONTROL (TASK-S02-01)
**Document:** `DATASET_REPRODUCIBILITY_REPORT.md`  
**Classification:** Scientific Methodology & Compliance  
**Date:** 2026-11-08  
**Component:** `ml/data/archival_manager.py`  
**Status:** `COMPLETE_VERIFIED`  

---

## 1. THE PROBLEM OF TRAINING DATA DRIFT

In standard machine learning workflows, training datasets frequently suffer from "silent drift": images are added, cleaned, or deleted without version locking. Consequently, an evaluation score reported in a research paper or milestone report cannot be mathematically reproduced months later because the underlying data corpus has changed.

---

## 2. ACREVIA IMMUTABILITY CONTROLS
To ensure absolute scientific reproducibility:
1. **Manifest-Locked Training:** Training configurations (`ml/configs/experiments/multicrop_mobilenet.yaml`) reference exact dataset releases via `dataset_version: v1.0.0` and `manifest_sha256`.
2. **Deterministic Splitting:** Group splitting algorithms (`ml/datasets/splitting/group_splitter.py`) hash farm and farmer identifiers with a fixed seed (`seed=42`), guaranteeing that images from the same farmer or field never leak across training, validation, and holdout test partitions.
3. **Perceptual Hash Pinning:** Every image retains an immutable perceptual hash (`pHash`), ensuring near-duplicate images captured within seconds of each other in the same row of cotton or rice are eliminated during ingestion.

---

## 3. STAGE 02 REMEDIATION SIGN-OFF
With the implementation and test verification of:
- `ml/data/archival_manager.py`
- `scripts/sync_training_corpus.py`
- `tests/ml/test_dataset_archival.py`
- Full inventory and reproducibility specifications

The archival architecture, tooling, and integrity verifiers are **100% complete and verified**. Actual large-scale cloud S3 corpus upload is gated under human authorization (`GATED_STORAGE_TRANSFER`) to avoid incurring unauthorized cloud billing without live credentials.

**Final Stage 02 Engineering Status:** **`COMPLETE_VERIFIED`**
