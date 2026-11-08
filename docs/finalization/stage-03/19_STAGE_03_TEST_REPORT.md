# ACREVIA — STAGE 03 TEST SUITE REPORT
## Complete Execution Log, Pass Rates & Regression Coverage

**Document Reference:** `docs/finalization/stage-03/19_STAGE_03_TEST_REPORT.md`  
**Stage:** 03 — Advanced Computer Vision & ML Inference Validation  
**Execution Timestamp:** 2026-11-08T15:57:59+05:30  
**Test Runner:** `pytest 9.2.0` on Python `3.11.16` (win32)  

---

### 1. Test Execution Summary

| Test Suite Category | Test Files | Total Tests | Passed | Failed | Duration | Status |
|---|---|---|---|---|---|---|
| **Abstention & Decision States** | `tests/ml/test_abstention.py` | 7 | 7 | 0 | 1.82s | **PASS** |
| **Inference Benchmark Smoke** | `tests/ml/test_benchmark.py` | 2 | 2 | 0 | 4.15s | **PASS** |
| **Deduplication & Leakage** | `tests/ml/test_deduplication_leakage.py` | 3 | 3 | 0 | 1.10s | **PASS** |
| **Evaluation Metrics** | `tests/ml/test_evaluation_metrics.py` | 1 | 1 | 0 | 0.45s | **PASS** |
| **Grad-CAM Explainability** | `tests/ml/test_gradcam.py` | 2 | 2 | 0 | 2.30s | **PASS** |
| **Image Quality & Blur** | `tests/ml/test_image_quality.py` | 3 | 3 | 0 | 0.95s | **PASS** |
| **Ingestion & Manifests** | `tests/ml/test_ingestion_manifest.py` | 3 | 3 | 0 | 0.88s | **PASS** |
| **Loss Formulations** | `tests/ml/test_losses.py` | 4 | 4 | 0 | 1.05s | **PASS** |
| **Single-Crop Backbones** | `tests/ml/test_models.py` | 3 | 3 | 0 | 2.12s | **PASS** |
| **Multi-Crop Architecture** | `tests/ml/test_multi_crop.py` | 5 | 5 | 0 | 3.40s | **PASS** |
| **ONNX Export & Int8 Quant** | `tests/ml/test_onnx_export.py` | 3 | 3 | 0 | 6.85s | **PASS** |
| **OOD & ECE Calibration** | `tests/ml/test_ood_calibration.py` | 6 | 6 | 0 | 2.90s | **PASS** |
| **Domain Robustness** | `tests/ml/test_robustness.py` | 2 | 2 | 0 | 3.10s | **PASS** |
| **Taxonomy Validation** | `tests/ml/test_taxonomy.py` | 2 | 2 | 0 | 0.50s | **PASS** |
| **Training Smoke Pipeline** | `tests/ml/test_training_smoke.py` | 1 | 1 | 0 | 4.80s | **PASS** |
| **Input Transforms Parity** | `tests/ml/test_transforms.py` | 2 | 2 | 0 | 0.62s | **PASS** |
| **ML Inference Microservice**| `ml/inference_service/tests/test_inference_service.py` | 7 | 7 | 0 | 4.40s | **PASS** |
| **TOTAL** | **17 Suites** | **56** | **56** | **0** | **41.49s** | **100% PASS** |

---

### 2. Comprehensive Test Item Inventory

```text
tests/ml/test_abstention.py::test_abstention_image_quality_insufficient PASSED           [  1%]
tests/ml/test_abstention.py::test_abstention_unsupported_crop PASSED                   [  3%]
tests/ml/test_abstention.py::test_abstention_out_of_distribution_non_plant PASSED     [  5%]
tests/ml/test_abstention.py::test_abstention_needs_more_information PASSED             [  7%]
tests/ml/test_abstention.py::test_abstention_expert_review_required_due_to_narrow_margin PASSED [  8%]
tests/ml/test_abstention.py::test_abstention_low_confidence PASSED                     [ 10%]
tests/ml/test_abstention.py::test_abstention_supported_prediction PASSED               [ 12%]
tests/ml/test_benchmark.py::test_benchmark_runner_smoke PASSED                         [ 14%]
tests/ml/test_benchmark.py::test_benchmark_suite_markdown_summary PASSED               [ 16%]
tests/ml/test_deduplication_leakage.py::test_exact_duplicate_checker PASSED            [ 17%]
tests/ml/test_deduplication_leakage.py::test_near_duplicate_checker PASSED             [ 19%]
tests/ml/test_deduplication_leakage.py::test_group_splitter_and_leakage_detection PASSED [ 21%]
tests/ml/test_evaluation_metrics.py::test_metrics_calculation PASSED                   [ 23%]
tests/ml/test_gradcam.py::test_gradcam_computation PASSED                              [ 25%]
tests/ml/test_gradcam.py::test_gradcam_overlay PASSED                                  [ 26%]
tests/ml/test_image_quality.py::test_blur_detector PASSED                              [ 28%]
tests/ml/test_image_quality.py::test_exposure_analyzer PASSED                          [ 30%]
tests/ml/test_image_quality.py::test_quality_validator_quarantine PASSED               [ 32%]
tests/ml/test_ingestion_manifest.py::test_image_reader_valid PASSED                    [ 33%]
tests/ml/test_ingestion_manifest.py::test_image_reader_corrupt PASSED                  [ 35%]
tests/ml/test_ingestion_manifest.py::test_manifest_generator PASSED                    [ 37%]
tests/ml/test_losses.py::test_focal_loss_forward PASSED                                [ 39%]
tests/ml/test_losses.py::test_focal_loss_downweights_easy_examples PASSED               [ 41%]
tests/ml/test_losses.py::test_label_smoothing_cross_entropy PASSED                     [ 42%]
tests/ml/test_losses.py::test_class_balanced_loss PASSED                               [ 44%]
tests/ml/test_models.py::test_mobilenet_forward_and_output_shape PASSED                [ 46%]
tests/ml/test_models.py::test_calibrated_uncertainty_and_probabilities PASSED          [ 48%]
tests/ml/test_models.py::test_parameter_counts PASSED                                  [ 50%]
tests/ml/test_multi_crop.py::test_multicrop_classifier_initialization PASSED           [ 51%]
tests/ml/test_multi_crop.py::test_multicrop_forward_with_crop_context PASSED           [ 53%]
tests/ml/test_multi_crop.py::test_multicrop_forward_autonomous_mode PASSED             [ 55%]
tests/ml/test_multi_crop.py::test_multicrop_calibrated_uncertainty PASSED              [ 57%]
tests/ml/test_multi_crop.py::test_multicrop_parameter_breakdown PASSED                 [ 58%]
tests/ml/test_onnx_export.py::test_fp32_export_and_validation PASSED                   [ 60%]
tests/ml/test_onnx_export.py::test_int8_quantization_and_size_budget PASSED           [ 62%]
tests/ml/test_onnx_export.py::test_export_and_quantize_manifest PASSED                 [ 64%]
tests/ml/test_ood_calibration.py::test_ece_perfect_calibration PASSED                  [ 66%]
tests/ml/test_ood_calibration.py::test_ece_uncalibrated_case PASSED                    [ 67%]
tests/ml/test_ood_calibration.py::test_temperature_scaler PASSED                       [ 69%]
tests/ml/test_ood_calibration.py::test_foliar_detector_natural_leaf PASSED             [ 71%]
tests/ml/test_ood_calibration.py::test_foliar_detector_non_plant_rejection PASSED     [ 73%]
tests/ml/test_ood_calibration.py::test_model_uncertainty_auditor PASSED                [ 75%]
tests/ml/test_robustness.py::test_robustness_perturbations PASSED                      [ 76%]
tests/ml/test_robustness.py::test_robustness_evaluation_runner PASSED                  [ 78%]
tests/ml/test_taxonomy.py::test_taxonomy_loading_and_classes PASSED                    [ 80%]
tests/ml/test_taxonomy.py::test_taxonomy_normalization_mapping PASSED                  [ 82%]
tests/ml/test_training_smoke.py::test_training_smoke_and_checkpoint PASSED             [ 83%]
tests/ml/test_transforms.py::test_transforms_output_shape_and_type PASSED             [ 85%]
tests/ml/test_transforms.py::test_validation_inference_consistency PASSED             [ 87%]
ml/inference_service/tests/test_inference_service.py::test_service_health PASSED       [ 89%]
ml/inference_service/tests/test_inference_service.py::test_service_model_info PASSED   [ 91%]
ml/inference_service/tests/test_inference_service.py::test_service_predict_valid_leaf PASSED [ 92%]
ml/inference_service/tests/test_inference_service.py::test_service_predict_blurry_rejection PASSED [ 94%]
ml/inference_service/tests/test_inference_service.py::test_service_predict_non_plant_ood_rejection PASSED [ 96%]
ml/inference_service/tests/test_inference_service.py::test_service_predict_unsupported_crop PASSED [ 98%]
ml/inference_service/tests/test_inference_service.py::test_service_predict_corrupt_file PASSED [100%]
```

---

### 3. Key Findings

1. **Zero Regressions:** All 56 tests passed without any errors or unexpected exits.
2. **Warning Analysis:** 11 warnings observed:
   - 1 Starlette `TestClient` deprecation notice regarding `httpx` (harmless).
   - 10 PyTorch ONNX exporter deprecation notices regarding future PyTorch 2.9 export API transition (tracked in Gap Register).
