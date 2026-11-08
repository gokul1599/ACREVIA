# ACREVIA — STAGE 03 GAP & REMEDIATION REGISTER
## Prioritized Technical Debt, Deprecation Tracking & Future Optimizations

**Document Reference:** `docs/finalization/stage-03/21_STAGE_03_GAP_REGISTER.md`  
**Stage:** 03 — Advanced Computer Vision & ML Inference Validation  

---

### 1. Stage 03 Identified Technical Debt

All identified gaps are classified by priority and evaluated against platform security, agronomic reliability, and deployment timelines:

| Gap ID | Category | Description | Severity | Impact on Stage 03 Gate | Remediation Strategy |
|---|---|---|---|---|---|
| **GAP-03-01** | Framework Deprecation | PyTorch 2.9 legacy TorchScript ONNX export deprecation warnings | Low | None (Models fully functional in Opset 17) | Migrate to `torch.onnx.dynamo_export` in future maintenance cycle. |
| **GAP-03-02** | Training Compute | Full 50-epoch multi-crop retraining requires GPU cluster offload | Medium | None (Current ONNX checkpoints verified) | Configure automated cloud GPU training job for future seasonal updates. |
| **GAP-03-03** | Explainability Caching | Grad-CAM heatmaps computed on CPU on-demand | Low | None (Sub-100ms generation) | Pre-generate and cache heatmap PNGs in S3 for KVK review queues. |
| **GAP-03-04** | Rare Class Sample Size | Field specimens for early *Ustilaginoidea virens* false smut are scarce | Medium | Managed (Covered by `UNKNOWN_CONDITION` bucket) | Active field collection during upcoming Telangana Kharif harvest. |
| **GAP-03-05** | Test Client Library | Starlette TestClient warning regarding `httpx` upgrade | Low | None (All tests pass green) | Bump test harness dependency when upstream Starlette updates. |

---

### 2. Remediation Sign-Off

None of the registered items compromise the operational stability, calibration accuracy, or safety of the Stage 03 deliverables. Stage 03 is approved for formal certification.
