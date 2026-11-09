# ACREVIA — GLOBAL RISK REGISTER RECONCILIATION & DEFICIT CROSSWALK

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Architecture:** System-Wide Audit Traceability & Risk Governance  
**Execution Date:** November 9, 2026  
**Audited Baseline:** Commit `7f0e7e5`

---

## 1. Historical Deficit Drift & Reconciliation Crosswalk

Across previous project phases (Phase 01 through Phase 04), several risk identifiers ("D1" through "D13") drifted in meaning between early planning notes and subsequent technical audit reports.

To establish permanent, tamper-proof auditability, this crosswalk maps each historical identifier to its canonical descriptive code:

| Historical ID | Historical Meaning | Current Phase Meaning | Canonical Descriptive ID | Actual Code / File Location | Phase 05 Verified Status | Reconciliation Evidence / Technical Decision |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **D1** | Live Cloud Staging Deploy | SMS Gateway Integration | **`SMS-INTEGRATION-01`** | `backend/app/services/auth_service.py` | `NOT_INTEGRATED_PASSWORD_PRIMARY` | Authentication uses bcrypt + JWT. No live external SMS credentials configured. |
| **D2** | Database Tenant Isolation | PostgreSQL RLS Verification | **`DB-RLS-01`** | `backend/app/database/rls.py`, migration `a1089411c87d` | `PARTIALLY_IMPLEMENTED` | DDL and 23 tests complete. Awaiting remote staging database branch execution. |
| **D3** | Distributed Rate Limiting | Rate Limiting Fail-Closed | **`AUTH-RATE-01`** | `backend/app/core/rate_limit.py`, `backend/tests/test_distributed_rate_limiter.py` | `COMPLETE_VERIFIED` | Fail-closed Redis rate limiter audited. Returns 503 on Redis outage, 429 on quota exhaustion. |
| **D4** | AI Inference Resilience | Groq Multi-Model Fallback | **`AI-FALLBACK-01`** | `backend/app/integrations/groq_client.py` | `COMPLETE_VERIFIED_CODE_LEVEL` | 3-model chain (`qwen` -> `llama-70b` -> `llama-8b`) with PJTSAU vector RAG fallback. |
| **—** | Single Provider Dependency | GroqCloud Infrastructure | **`AI-PROVIDER-02`** | `backend/app/integrations/groq_client.py` | `DOCUMENTED_LIMITATION` | Formally classified as `SAME_PROVIDER_MULTI_MODEL_FALLBACK`. No multi-cloud AI redundancy. |
| **D5** | Automated Test Inventory | Satellite STAC Migration | **`SATELLITE-PROVIDER-01`** | `backend/app/integrations/satellite_client.py` | `COMPLETE_VERIFIED` | Copernicus CDSE OAuth replaced with Element 84 Earth Search STAC + MS Planetary Computer. |
| **D6** | Frontend Lint & Build | Frontend Dead Code Warnings | **`FRONTEND-TYPES-01`** | `frontend/lib/api/client.ts`, `frontend/lib/api/types.ts` | `COMPLETE_VERIFIED` | All 32 unused variable warnings fixed. 109 `any` casts safely retained on API envelopes. Build clean. |
| **D7** | PyTorch / ONNX Weights | Model Asset Integrity | **`MODEL-INTEGRITY-01`** | `ml/models/weights/` | `COMPLETE_VERIFIED` | SHA-256 integrity manifests enforced for all local inference assets. |
| **D8** | Tamper-Proof Audit Log | Audit Trail Integrity | **`AUDIT-INTEGRITY-01`** | `backend/app/models/governance.py` | `PARTIALLY_IMPLEMENTED` | Application-layer append-only active. Cryptographic signing / cloud KMS pending production deployment. |
| **D9** | DPDP Act Compliance | Consent & Data Privacy | **`PRIVACY-GOVERNANCE-01`** | `backend/app/models/governance.py` | `PROTOTYPE_SPECIFIED` | Consent lifecycle models defined. DPDP certification NOT claimed. Zero field data collected. |
| **D10**| Offline PWA Storage | IndexedDB Sync Engine | **`OFFLINE-PWA-01`** | `frontend/lib/offline/db.ts` | `COMPLETE_VERIFIED` | Offline IndexedDB storage and exponential backoff sync verified (43 frontend tests pass). |
| **D11**| Agronomic Advisory | PJTSAU Knowledge Base | **`AGRO-ADVISORY-01`** | `backend/app/database/init_db.py` | `COMPLETE_VERIFIED` | Verified agronomic rules grounded in official PJTSAU & ICAR bulletins with citations. |
| **D12**| Telemetry & Metrics | Prometheus / JSON Logs | **`OBSERVABILITY-01`** | `backend/app/core/logging.py`, `backend/app/main.py` | `COMPLETE_VERIFIED` | Structured JSON logging with Correlation IDs and latency tracking active. |
| **D13**| Pre-Authorization Gate | Institutional Outreach Gate | **`OWNER-AUTH-01`** | `docs/pilot/PHASE_02_OWNER_INPUT_AND_AUTHORIZATION_FORM.md` | `BLOCKED_OWNER_AUTHORIZATION` | Blocked pending Owner Sign-Off. Zero emails sent. Zero field activities authorized. |

---

## 2. Satellite Provider Architecture Reconciliation

The Phase 04 report table accidentally contained a historical reference describing "CDSE OAuth2 as active".

### Authoritative Architecture Established in Repository:
1. **Primary STAC Provider:** **Element 84 Earth Search STAC API** (`https://earth-search.aws.element84.com/v1`). Provides authentication-free access to Sentinel-2 L2A imagery.
2. **Fallback STAC Provider:** **Microsoft Planetary Computer STAC API** (`https://planetarycomputer.microsoft.com/api/stac/v1`) with automatic SAS token caching.
3. **Copernicus CDSE OAuth Status:** **Permanently Eliminated**. The earlier CDSE OAuth2 dependency required paid or rate-limited API keys and was superseded in Stage 09. Zero Copernicus CDSE credentials exist in active production code.
