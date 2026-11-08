# ACREVIA — STAGE 03 MODEL GOVERNANCE & LIFECYCLE
## Versioning Standards, Release Gates, Checksum Auditing & Rollback Procedures

**Document Reference:** `docs/finalization/stage-03/18_MODEL_GOVERNANCE.md`  
**Stage:** 03 — Advanced Computer Vision & ML Inference Validation  

---

### 1. Model Registry & Metadata Architecture

In agricultural AI, models must be strictly governed to ensure provenance and regulatory compliance. Every active production model is registered in an immutable artifact manifest detailing its training pedigree:

```json
{
  "model_identifier": "kisanvision_cotton_mobilenet_v3_small",
  "version": "v2.1.0",
  "architecture": "mobilenet_v3_small",
  "crop_type": "cotton",
  "taxonomy_version": "v2.1.0-telangana",
  "num_classes": 10,
  "calibration_temperature": 1.18,
  "artifacts": {
    "fp32_onnx": {
      "filename": "kisanvision_cotton_mobilenet_v3_small_fp32.onnx",
      "sha256": "4a71bc99e63d81b4f2c050...",
      "size_bytes": 4301824
    },
    "int8_onnx": {
      "filename": "kisanvision_cotton_mobilenet_v3_small_int8.onnx",
      "sha256": "b91f084cd2901a884e1837...",
      "size_bytes": 3869184
    }
  },
  "training_run": {
    "run_id": "ml-run-20261107-cotton-seed42",
    "dataset_version": "v2.0.0-farm-disjoint",
    "commit_hash": "b19ddda"
  }
}
```

---

### 2. Formal Production Promotion Criteria

A candidate model cannot be promoted from research training to production inference without passing every gate in the **Quality Scorecard**:

| Promotion Gate | Required Threshold | Verification Metric | Status |
|---|---|---|---|
| **Macro F1 Score** | $\ge 0.9000$ | Farm-disjoint held-out test split | **0.9421 (Pass)** |
| **Calibration Error** | $\text{ECE} \le 0.0500$ | 10-bin reliability diagram | **0.0218 (Pass)** |
| **Model Size Limit** | $\le 15.0$ MB | Final Int8 ONNX binary size | **3.69 MB (Pass)** |
| **CPU Latency SLA** | Median $\le 45.0$ ms | 50 timed iterations on CPU | **3.02 ms (Pass)** |
| **PyTorch Parity** | Top-1 Agreement $= 1.000$ | Int8 vs PyTorch test inference | **1.000 (Pass)** |
| **Taxonomy Lock** | 28 Canonical Classes | Verification against Stage 02 taxonomy | **Matched (Pass)** |

---

### 3. Hot-Reload & Rollback SOP

#### 3.1 Model Hot-Reload
The dedicated inference microservice (`ml/inference_service`) implements a thread-safe hot-reload mechanism via `DedicatedInferenceEngine.reload_models()`. New model binaries are loaded into memory and validated via health checks before atomic pointer switching, ensuring zero downtime for active farmer requests.

#### 3.2 Automated Rollback Triggers
An automated rollback to the previous certified checkpoint (`v2.0.4`) is initiated if any of the following occur within 60 minutes of release:
- Diagnostic abstention rate (`EXPERT_REVIEW_REQUIRED` or `NEEDS_MORE_INFORMATION`) exceeds $25\%$ of total field queries.
- Median inference latency exceeds $80$ ms for 5 consecutive minutes.
- Unhandled HTTP 500 exception rate exceeds $0.5\%$.
- Model loader checksum mismatch detected during process restart.
