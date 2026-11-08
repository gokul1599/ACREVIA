# ACREVIA — DATASET ARCHIVAL VERIFICATION REPORT
## INTEGRITY AUDITING, CHECKSUM VERIFICATION & TAMPER DETECTION (TASK-S02-01)
**Document:** `ARCHIVAL_VERIFICATION_REPORT.md`  
**Classification:** Verification Evidence  
**Date:** 2026-11-08  
**Component:** `tests/ml/test_dataset_archival.py`  
**Status:** `COMPLETE_VERIFIED`  

---

## 1. EMPIRICAL TEST EXECUTION RESULTS

The complete dataset archival verification suite in `tests/ml/test_dataset_archival.py` was executed independently against the active CPython 3.11 environment.

- **Command:** `.venv\Scripts\python.exe -m pytest tests/ml/test_dataset_archival.py -v`
- **Result:** **6 Passed**, 0 Failed, 0 Errors
- **Execution Time:** $0.32\text{ seconds}$

| Test Identifier | Verified Functionality | Result | Notes |
|---|---|:---:|---|
| `test_inventory_dataset_discovery` | Recursive scanning, extension filtering, class and crop inference | `PASSED` | Discovers images and ignores `.txt` non-image artifacts |
| `test_create_manifest_deterministic` | Deterministic SHA-256 calculation over dataset items | `PASSED` | Identical inputs produce bit-for-bit identical hashes |
| `test_archive_dataset_dry_run` | Non-destructive dry-run planning output | `PASSED` | Calculates expected file count and byte totals without disk writes |
| `test_archive_dataset_execution_and_verification` | Hermetic copy to storage adapter and subsequent full SHA-256 audit | `PASSED` | Verifies 100% of files match manifest hashes |
| `test_archive_tamper_and_missing_detection` | Malicious byte tampering and missing file detection | `PASSED` | Reliably catches corrupted byte content and deleted keys |
| `test_path_traversal_protection` | Security enforcement against directory traversal (`../`) | `PASSED` | Rejects malicious traversal attempts with `ValueError` |

---

## 2. DRY-RUN CLI EXECUTION EVIDENCE
Executing the dry-run CLI tool against existing storage:
- **Command:** `python scripts/sync_training_corpus.py --dry-run --source-dir data/storage`
- **Output:** Discovered 4 eligible images (6,612 bytes), generated SHA-256 manifest `f824d06c78c4fa8d...`, confirmed target destination `datasets/acrevia/acrevia-pathology-28/v1.0.0/manifests/archival_manifest.json`.
- **Finding:** Zero source files were moved or deleted.
