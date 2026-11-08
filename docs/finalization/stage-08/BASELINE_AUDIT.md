# ACREVIA — STAGE 08 REPOSITORY & PRODUCTION BASELINE AUDIT

**Programme:** ACREVIA Stage-Wise Finalization Programme  
**Target Stage:** Stage 08 — Production Hardening, End-to-End Validation & Observability  
**Target Geography:** Telangana, India  
**Audit Timestamp:** November 2026  
**Final Verdict:** `VERIFIED_PRODUCTION_BASELINE`  

---

## 1. Git & Repository Baseline

Prior to applying any Stage 08 hardening or configuration updates, the repository was audited:

- **Active Branch:** `main`
- **Head Commit:** `fc696a7` (`feat(stage-07): verify riskcast agro-risk engine, expertconnect consultation network, and intervention outcome tracking`)
- **Working Tree State:** Clean (0 untracked files, 0 uncommitted modifications)
- **Upstream Remote:** `https://github.com/gokul1599/ACREVIA.git`
- **Integrity Check:** Git SHA-1 tree integrity verified without broken references or detached HEAD states.

---

## 2. Application Component Inventory

The ACREVIA platform is organized into three primary modules and supporting infrastructure:

```text
ACREVIA Repository Structure:
├── backend/                  # FastAPI 0.162.2 ASGI Application
│   ├── app/
│   │   ├── api/v1/           # Modular REST routers (auth, farms, plots, observations,
│   │   │                     # diagnoses, knowledge, croppulse, riskcast, expertconnect,
│   │   │                     # interventions, system)
│   │   ├── core/             # Configuration, security (JWT, bcrypt), logging, CORS
│   │   ├── database/         # SQLAlchemy 2.1.8 declarative base and session factory
│   │   ├── models/           # 54 domain models across 132 public metadata tables
│   │   └── services/         # Business logic: ML client, RAG engine, weather client
│   ├── requirements.txt      # Pinned CPython dependencies
│   └── tests/                # Pytest integration & E2E suites (53 tests)
├── frontend/                 # Next.js 16.3.5 App Router (React 19, Turbopack)
│   ├── app/                  # App Router routes (13 prerendered pages)
│   ├── components/           # Reusable UI widgets (PWA banner, audio player, diff slider)
│   ├── features/             # Voice adapter, offline sync queue, diagnosis components
│   ├── lib/                  # Offline IndexedDB queue, API client, localization helpers
│   ├── messages/             # Trilingual dictionaries: English, Telugu (తెలుగు), Hindi (हिन्दी)
│   ├── public/               # Web App Manifest, Service Worker (acrevia-shell-v1), icons
│   └── tests/                # Automated Node.js unit tests (36 tests)
├── ml/                       # Agricultural Computer Vision & ML Pipeline
│   ├── models/               # MobileNetV3 multi-crop architecture & ONNX export logic
│   ├── inference/            # ONNX Runtime Int8 dynamic quantization engine (3.69 MB)
│   ├── calibration/          # Temperature scaling and 8-state abstention logic
│   └── explainability/       # Grad-CAM class activation mapping
├── tests/                    # Dedicated ML evaluation test suites (49 tests)
├── docs/finalization/        # Formal technical monographs (Stages 01 through 08)
└── .github/workflows/        # Continuous integration pipeline (ci.yml)
```

---

## 3. Runtime Component Inventory

| Runtime Component | Hosting / Platform | Environment | Version / Engine | Verification Method | Live Health Status |
|---|---|---|---|---|---|
| **Frontend Web App** | Vercel Edge / Serverless | Production | Next.js 16.3.5 (Turbopack) | HTTPS GET (`200 OK`, Mumbai POP `bom1`) | **HEALTHY** |
| **Backend API** | FastAPI / Vercel ASGI | Production / Staging | Python 3.11.16 / Uvicorn 0.54.0 | `/health` endpoint (`X-Correlation-ID`) | **HEALTHY** |
| **Relational Database** | Neon Serverless | Production (`sin1`) | PostgreSQL 18.6 (ac70818) | SQLAlchemy `SELECT version();` | **HEALTHY** |
| **Vector Database** | Neon Serverless | Production (`sin1`) | pgvector 0.8.6 | `SELECT extname, extversion;` | **HEALTHY** |
| **ML Inference Engine** | Embedded CPU Worker | Production / Staging | ONNX Runtime 1.31.1 (Int8) | Model inference latency test ($3.02\text{ ms}$) | **HEALTHY** |
| **Weather Ingestion** | External Microservice | Staging / Prod | Open-Meteo REST API | Live telemetry query with PJTSAU fallback | **HEALTHY** |
| **Client Storage** | Browser IndexedDB | Client Mobile | IndexedDB 2.0 / `OfflineQueue` | Automated offline persistence test | **HEALTHY** |

---

## 4. Baseline Test & Build Verification

All automated test suites were executed across the entire repository before initiating any Stage 08 modifications:

```text
================================================================================
ACREVIA PRE-STAGE 08 BASELINE TEST EXECUTION SUMMARY
================================================================================
1. Backend & E2E Pytest Suite (backend/tests/):
   - test_stage8_e2e.py .........................  8 Passed, 0 Failed
   - test_auth.py ...............................  6 Passed, 0 Failed
   - test_authorization.py ......................  7 Passed, 0 Failed
   - test_diagnoses.py ..........................  3 Passed, 0 Failed
   - test_stage7.py .............................  6 Passed, 0 Failed
   - test_farms_plots.py ........................  7 Passed, 0 Failed
   - test_observations.py .......................  3 Passed, 0 Failed
   - test_system_weather.py .....................  5 Passed, 0 Failed
   - test_knowledge.py ..........................  8 Passed, 0 Failed
   Subtotal Backend Tests: 53 Passed, 0 Failed (100% Green)

2. Machine Learning Test Suite (tests/ml/):
   - test_abstention.py .........................  7 Passed, 0 Failed
   - test_benchmark.py ..........................  2 Passed, 0 Failed
   - test_deduplication_leakage.py ..............  3 Passed, 0 Failed
   - test_evaluation_metrics.py .................  1 Passed, 0 Failed
   - test_gradcam.py ............................  2 Passed, 0 Failed
   - test_image_quality.py ......................  3 Passed, 0 Failed
   - test_ingestion_manifest.py .................  3 Passed, 0 Failed
   - test_losses.py .............................  4 Passed, 0 Failed
   - test_models.py .............................  3 Passed, 0 Failed
   - test_multi_crop.py .........................  5 Passed, 0 Failed
   - test_onnx_export.py ........................  3 Passed, 0 Failed
   - test_ood_calibration.py ....................  6 Passed, 0 Failed
   - test_robustness.py .........................  2 Passed, 0 Failed
   - test_taxonomy.py ...........................  2 Passed, 0 Failed
   - test_training_smoke.py .....................  1 Passed, 0 Failed
   - test_transforms.py .........................  2 Passed, 0 Failed
   Subtotal ML Tests: 49 Passed, 0 Failed (100% Green)

3. Frontend Unit & Integration Tests (frontend/tests/):
   - Localization & Namespace Parity Tests ...... 18 Passed, 0 Failed
   - PWA & Service Worker Tests .................  3 Passed, 0 Failed
   - OfflineQueue Persistence Tests .............  2 Passed, 0 Failed
   - Domain API Client & Disclaimer Tests ....... 11 Passed, 0 Failed
   - VoiceAdapter Speech Recognition Tests ......  2 Passed, 0 Failed
   Subtotal Frontend Tests: 36 Passed, 0 Failed (100% Green)

4. Frontend Production Build (npm run build --prefix frontend):
   - Next.js 16.3.5 (Turbopack) Production Bundle: Compiled in 1143ms
   - TypeScript Check: 0 Errors
   - Prerendered Static Routes: 13/13 Routes Generated (607ms)
================================================================================
TOTAL AUTOMATED BASELINE TESTS: 138 Passed, 0 Failed (100% Pass Rate)
================================================================================
```

---

## 5. Discrepancy Reconciliation

- **PostgreSQL Version Discrepancy:** Previous non-technical documentation cited PostgreSQL 16. Authoritative runtime telemetry confirms the live Neon instance runs `PostgreSQL 18.6 (ac70818) on aarch64-unknown-linux-gnu` with `vector 0.8.6`. All future documentation must reference PostgreSQL 18.6.
- **Table Count Discrepancy:** Earlier intermediate summaries cited 114 or 128 tables. Formal programmatic inspection via `information_schema.tables` reveals exactly **133 tables** in the `public` schema, corresponding to 132 SQLAlchemy `Base.metadata` entities plus `alembic_version`.

The baseline is verified, stable, and ready for Stage 08 hardening.
