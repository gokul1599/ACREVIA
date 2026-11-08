# STAGE 02 — TEST & QUALITY ASSURANCE REPORT
## Automated Test Execution, Regression Outcomes & Stage 03 Compatibility Verification

**Stage:** 02 — Agricultural Dataset Engineering & Taxonomy Validation  
**Execution Timestamp:** 2026-11-08T15:40:00+05:30  
**Test Harness:** Pytest 9.2.0 (CPython 3.11.16)  
**Total Tests Executed:** 11 Stage-Specific Tests (and 49 Full ML Suite Tests)  
**Pass Rate:** **100% Green (Zero Failures, Zero Skips)**  

---

### 1. Stage 02 Unit & Pipeline Integration Test Results

```powershell
python -m pytest tests/ml/test_taxonomy.py tests/ml/test_image_quality.py tests/ml/test_ingestion_manifest.py tests/ml/test_deduplication_leakage.py -v
```

| Test File | Test Name | Assertion Focus | Execution Time | Result |
|---|---|---|---|---|
| `test_taxonomy.py` | `test_taxonomy_loading_and_classes` | Verifies existence and loading of all Cotton, Rice, Chilli, and Background classes from YAML | 0.08s | **PASSED** |
| `test_taxonomy.py` | `test_taxonomy_normalization_mapping` | Tests mapping of public labels and fallback to `UNKNOWN_CONDITION` | 0.01s | **PASSED** |
| `test_image_quality.py` | `test_blur_detector` | Evaluates Laplacian variance on sharp vs blurred images ($Var < 100$) | 0.42s | **PASSED** |
| `test_image_quality.py` | `test_exposure_analyzer` | Tests detection of underexposure ($< 35$), overexposure ($> 225$), and clipping | 0.04s | **PASSED** |
| `test_image_quality.py` | `test_quality_validator_quarantine` | Tests end-to-end quality validation orchestration and quarantine rejection | 0.05s | **PASSED** |
| `test_ingestion_manifest.py`| `test_image_reader_valid` | Validates PIL decoding, format checks, and EXIF stripping on valid images | 0.12s | **PASSED** |
| `test_ingestion_manifest.py`| `test_image_reader_corrupt` | Verifies safe rejection (HTTP 422) on corrupted or non-image payloads | 0.02s | **PASSED** |
| `test_ingestion_manifest.py`| `test_manifest_generator` | Validates creation of `UnifiedSampleManifest` with SHA-256 and dHash | 0.08s | **PASSED** |
| `test_deduplication_leakage.py`| `test_exact_duplicate_checker` | Verifies byte-for-byte duplicate detection regardless of filename | 0.02s | **PASSED** |
| `test_deduplication_leakage.py`| `test_near_duplicate_checker` | Tests 64-bit dHash Hamming distance calculation ($\text{dist} \le 4$) | 0.04s | **PASSED** |
| `test_deduplication_leakage.py`| `test_group_splitter_and_leakage_detection` | Tests `GroupSplitter` farm-disjoint partitioning and audits with `DataLeakageDetector` | 0.18s | **PASSED** |

---

### 2. Full ML Suite Regression Check (49 Tests)

All 49 tests across the broader machine learning directory were executed to ensure Stage 02 changes introduce zero regressions into Stage 03 vision heads or inference services:

* `tests/ml/test_abstention.py` (7 tests) $\to$ **7 Passed**
* `tests/ml/test_benchmark.py` (2 tests) $\to$ **2 Passed**
* `tests/ml/test_deduplication_leakage.py` (3 tests) $\to$ **3 Passed**
* `tests/ml/test_evaluation_metrics.py` (1 test) $\to$ **1 Passed**
* `tests/ml/test_gradcam.py` (2 tests) $\to$ **2 Passed**
* `tests/ml/test_image_quality.py` (3 tests) $\to$ **3 Passed**
* `tests/ml/test_ingestion_manifest.py` (3 tests) $\to$ **3 Passed**
* `tests/ml/test_losses.py` (4 tests) $\to$ **4 Passed**
* `tests/ml/test_models.py` (3 tests) $\to$ **3 Passed**
* `tests/ml/test_multi_crop.py` (5 tests) $\to$ **5 Passed**
* `tests/ml/test_onnx_export.py` (3 tests) $\to$ **3 Passed**
* `tests/ml/test_ood_calibration.py` (6 tests) $\to$ **6 Passed**
* `tests/ml/test_robustness.py` (2 tests) $\to$ **2 Passed**
* `tests/ml/test_taxonomy.py` (2 tests) $\to$ **2 Passed**
* `tests/ml/test_training_smoke.py` (1 test) $\to$ **1 Passed**
* `tests/ml/test_transforms.py` (2 tests) $\to$ **2 Passed**
* **Total:** **49 Passed in 38.22 seconds**.

---

### 3. Stage 03 Downstream Compatibility Verification

* **Output Dimensions:** Verified that classification heads remain Cotton: 10, Rice: 10, Chilli: 8 (Total: 28 classes).
* **Input Tensor Shape:** Standardized at `(3, 224, 224)` with ImageNet mean `[0.485, 0.456, 0.406]` and std `[0.229, 0.224, 0.225]`.
* **Zero Softmax Leakage:** Independent classification heads prevent probability spillover between crops.
