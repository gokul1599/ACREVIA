# ACREVIA Final Pending Work & Remediation Register
## Post-Remediation Task Status & Audit Resolution Matrix
**Programme:** ACREVIA Master Remediation (Stages 02–10)  
**Evaluation Baseline:** Master Implementation Audit  
**Certification Status:** ALL AUDITED REMEDIATIONS COMPLETED & CERTIFIED  

---

## 1. Remediation Task Resolution Register

| Task ID | Stage | Priority | Description | Pre-Remediation Status | Post-Remediation Status | Verification Artifact |
| :--- | :---: | :---: | :--- | :---: | :---: | :--- |
| **`TASK-S06-01`** | **Stage 06** | **P1** | **IndexedDB Offline-First Migration**<br>Replace volatile `localStorage` with versioned `IndexedDB` (`acrevia_offline_db_v2`, version 2), 5 stores, Blob attachments, legacy migration, and exponential backoff retry. | `PARTIALLY_IMPLEMENTED` | **`COMPLETE_VERIFIED`** | `frontend/lib/offline/db.ts`<br>`frontend/lib/offline/queue.ts`<br>`frontend/tests/indexeddb_persistence.test.js` (7 tests) |
| **`TASK-S02-01`** | **Stage 02** | **P2** | **Training Dataset Archival & Reproducibility**<br>Implement automated dataset archival manager with deterministic SHA-256 manifests, local & S3 object storage adapters, path traversal protection, and verification CLI. | `PARTIALLY_IMPLEMENTED` | **`COMPLETE_VERIFIED`** | `ml/data/archival_manager.py`<br>`scripts/sync_training_corpus.py`<br>`tests/ml/test_dataset_archival.py` (6 tests) |
| **`TASK-S04-01`** | **Stage 04** | **P2** | **Alembic Migration Discipline & Zero-DDL Startup**<br>Eliminate implicit `Base.metadata.create_all()` runtime DDL on application startup; implement read-only `check_db_readiness()` probe on `alembic_version`. | `PARTIALLY_IMPLEMENTED` | **`COMPLETE_VERIFIED`** | `backend/app/database/init_db.py`<br>`backend/app/main.py`<br>`backend/tests/test_alembic_migrations.py` (4 tests) |
| **`TASK-S08-02`** | **Stage 08** | **P2** | **Distributed Redis Rate Limiting**<br>Implement atomic sliding-window rate limiting in Redis (`ZSET`), DPDP-safe IP hashing, quota policies for auth/ai/rag/uploads, fail-open resiliency, and RFC 6585 headers. | `PARTIALLY_IMPLEMENTED` | **`COMPLETE_VERIFIED`** | `backend/app/core/rate_limit.py`<br>`backend/app/core/config.py`<br>`backend/tests/test_distributed_rate_limiter.py` (6 tests) |
| **`TASK-S08-01`** | **Stage 08** | **P1** | **50-Farmer Telangana Pilot Preparation**<br>Author complete operational protocols, KVK institutional proposal, trilingual consent forms (TE/EN/HI), field training manuals, weekly supervisor checklists, and safety governance. | `BLOCKED_EXTERNAL_DEPENDENCY` | **`COMPLETE_VERIFIED`** *(Software & Operational Packages)*<br>**`CONTROLLED_PILOT_READY`** *(Gated on Field Execution)* | `docs/pilot/telangana-50-farmer/` (21 comprehensive operational documents) |

---

## 2. Real-World Field Pilot Execution Gate

While all software engineering, data architecture, security hardening, and operational documentation tasks are **100% complete and verified**, real-world field pilot execution involves human participants, institutional KVK visits, and agricultural growing seasons. 

In strict adherence to engineering integrity:
- **Platform Software & Infrastructure:** `COMPLETE_VERIFIED`
- **Field Operational Documentation:** `COMPLETE_VERIFIED`
- **Live Physical 30-Day Cohort Trial:** `CONTROLLED_PILOT_READY` (Gated upon physical mobilization with KVK Malyal & KVK Kampasagar).

---

## 3. Post-Pilot Long-Term Evolution Register (Future Roadmap)

These standing items are noted for subsequent programme cycles following the completion of the 50-farmer controlled pilot:

| Tracking Code | Target Horizon | Future Scope Description | Dependency |
| :--- | :---: | :--- | :--- |
| `FUT-EVAL-01` | Post-Pilot | Multi-season randomized controlled trial (RCT) measuring yield impact across 500+ smallholder plots. | Requires completion and publication of the 30-day controlled pilot. |
| `FUT-ML-01` | Post-Pilot | Retrain shared MobileNetV3 backbone incorporating field images captured during the 30-day trial to expand the 28-class taxonomy. | Requires field dataset collection and KVK pathologist labeling. |
| `FUT-GEO-01` | Post-Pilot | Ingest hyperspectral satellite bands (Sentinel-2 Level 2A) and drone imagery for sub-meter weed and canopy analysis. | High-resolution commercial satellite or UAV licensing. |
