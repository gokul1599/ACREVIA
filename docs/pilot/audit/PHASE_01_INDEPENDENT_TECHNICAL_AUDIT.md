# ACREVIA — PHASE 01 INDEPENDENT TECHNICAL AUDIT
## COMPREHENSIVE REPOSITORY INSPECTION, TRACEABILITY AUDIT & TECHNICAL ASSURANCE

**Programme:** ACREVIA Agricultural Intelligence Platform  
**Audit Scope:** Phase 01 Staging Readiness & Phase 02 Outreach Gate  
**Target Geography:** Telangana, India  
**Audited Commit:** `2af491e49be8beb1d28fc03e42f642ed4fb7b21b` (`2af491e`)  
**Audit Baseline:** `f320466`  
**Execution Standard:** Evidence Before Claims • Implementation Before Completion • Verification Before Authorization  
**Audit Date:** November 9, 2026  
**Final Technical Audit Status:** **`COMPLETE_WITH_LIMITATIONS`** (Staging configuration & tests verified; database-level RLS & live staging URL pending)  

---

## 1. Executive Summary & Audit Mandate

This independent technical audit was conducted to establish the genuine state of the ACREVIA codebase, automated test suites, infrastructure isolation, data governance, external provider bindings, and institutional readiness prior to authorizing institutional outreach to Krishi Vigyan Kendras (KVK Malyal and KVK Kampasagar).

Rather than accepting previous optimistic completion reports at face value, this audit independently inspected actual Python, TypeScript, and SQL source code, re-executed all automated test suites, traced physical calculations to raw data, and evaluated security boundaries.

### Summary of Authoritative Findings:
1. **Repository Identity & Baseline:** Git HEAD is verified at `2af491e` on branch `main` with a clean working tree. The prior reported completion commit is present and reconciled against baseline `f320466`.
2. **Automated Test Inventory:** Re-execution of the test harness confirms **252 physical tests collected and passing (100% pass rate)**. The previously reported figure of 240 tests resulted from double-counting 9 staging tests (which were already collected inside the 145 backend tests) while undercounting the 55 ML unit tests.
3. **Staging Environment Reality:** Staging deployment configuration (`frontend/vercel.json`, Next.js 16, regional co-location `sin1`, security headers, `.env.staging.example`) is verified. However, **no live external preview deployment has been executed**; live deployment remains gated awaiting explicit owner authorization.
4. **Tenant Isolation Reality:** Multi-tenant security is strictly enforced at the **FastAPI application dependency layer** (`verify_farm_access()` returning HTTP 403 Forbidden). However, **PostgreSQL engine-level Row-Level Security (`ENABLE ROW LEVEL SECURITY`) is NOT declared in Alembic migrations**. This is documented as a P2 architectural limitation.
5. **Satellite NDVI Tracing:** The dual NDVI figures in earlier reports are traced and reconciled: **`0.2927`** was computed from a real 10,000-pixel Sentinel-2 L2A tile window (`S2A_44QLE_20240328_0_L2A`) over Warangal; **`0.6364`** is a deterministic synthetic unit test fixture array verifying mathematical formula accuracy under SCL masking.
6. **Free-Tier Cost Certainty:** Code-level enforcement of zero-cost boundaries (HTTP 429 backoff, local failovers) is verified. However, account-level billing instrument presence cannot be audited via public APIs without private console access; therefore, account billing status is formally recorded as `NOT_VERIFIABLE`.

---

## 2. Git & Repository Reconciliation

An inspection of the local Git repository was conducted to verify tree clean state, commit provenance, and baseline continuity:

| Attribute | Expected State | Actual Inspected State | Audit Result | Evidence / Notes |
|---|---|---|---|---|
| **Repository Root** | `projects/` workspace | `C:\Users\gokul\OneDrive\Documents\projects` | **MATCH** | Working directory confirmed |
| **Current Branch** | `main` | `main` | **MATCH** | Primary branch active |
| **Pre-Phase Baseline** | `f320466` | `f320466` | **MATCH** | Commit exists in linear log |
| **Phase 01 Completion** | `2af491e` | `2af491e` | **MATCH** | HEAD points to `2af491e` |
| **Working Tree Status** | Clean | Clean (`nothing to commit`) | **MATCH** | 0 untracked / modified files |
| **Recent Commit Log** | Linear, unbroken | 5 consecutive clean commits | **MATCH** | `2af491e` $\rightarrow$ `f320466` $\rightarrow$ `c46f98b` |

---

## 3. Implementation Traceability Matrix

Every critical functional claim from Phase 01 was traced directly to source code, test suites, verified evidence, and operational limitations:

```
+========================================================================================================================+
| ACREVIA IMPLEMENTATION TRACEABILITY MATRIX                                                                             |
+----+----------------------+---------------------------------+--------------------------+-------------------------------+
| #  | Capability           | Implementation Source File      | Verification Test        | Operational Limitation        |
+----+----------------------+---------------------------------+--------------------------+-------------------------------+
| 01 | User Registration    | backend/app/api/v1/auth.py      | test_auth.py             | OTP is currently simulated in |
|    | & Authentication     | backend/app/core/security.py    | test_staging_acceptance  | dev/test; SMS gateway pending |
+----+----------------------+---------------------------------+--------------------------+-------------------------------+
| 02 | Farm & Plot GeoJSON  | backend/app/api/v1/farms.py     | test_farms_plots.py      | PostGIS requires GEOS library;|
|    | Boundary Validation  | backend/app/services/geo_service| test_staging_acceptance  | fallback bbox validation used |
+----+----------------------+---------------------------------+--------------------------+-------------------------------+
| 03 | CropVision Multi-Crop| backend/app/services/diagnosis  | test_vision_endpoints.py | ONNX CPU runtime used; large  |
|    | Leaf Diagnostics     | backend/app/integrations/ml     | test_staging_acceptance  | batch inference throttled     |
+----+----------------------+---------------------------------+--------------------------+-------------------------------+
| 04 | KrishiBrain Grounded | backend/app/services/knowledge  | test_knowledge.py        | Requires seeded PJTSAU PDFs in|
|    | Multilingual RAG     | backend/app/api/v1/knowledge.py | test_staging_acceptance  | vector DB for full grounding  |
+----+----------------------+---------------------------------+--------------------------+-------------------------------+
| 05 | Chemical Safety &    | backend/app/services/knowledge/ | test_knowledge.py        | High-risk queries trigger     |
|    | CIBRC Abstention     | generation/generator.py         | test_staging_acceptance  | REQUIRES_EXPERT_REVIEW state  |
+----+----------------------+---------------------------------+--------------------------+-------------------------------+
| 06 | Satellite STAC &     | backend/app/integrations/       | test_earth_search_       | Public Element 84 rate limits;|
|    | Planetary Fallback   | satellite_client.py             | satellite.py (16 tests)  | Planetary Computer fallback   |
+----+----------------------+---------------------------------+--------------------------+-------------------------------+
| 07 | Sentinel-2 NDVI      | backend/app/integrations/       | test_earth_search_       | Heavy cloud cover in monsoon  |
|    | & SCL Cloud Masking  | satellite_client.py             | satellite.py             | triggers cloud mask policy    |
+----+----------------------+---------------------------------+--------------------------+-------------------------------+
| 08 | Open-Meteo Weather   | backend/app/integrations/       | test_system_weather.py   | Public API 10,000 call/day;   |
|    | & RiskCast Engine    | weather_client.py               | test_staging_acceptance  | 15-minute in-memory cache     |
+----+----------------------+---------------------------------+--------------------------+-------------------------------+
| 09 | Upstash Redis Rate   | backend/app/core/rate_limit.py  | test_distributed_rate_   | Defaults to fail_open across  |
|    | Limiting & Namespace |                                 | limiter.py (6 tests)     | unauthenticated endpoints     |
+----+----------------------+---------------------------------+--------------------------+-------------------------------+
| 10 | Multi-Tenant Data    | backend/app/security/           | test_authorization.py    | Application-level enforcement;|
|    | Boundary Isolation   | dependencies.py                 | test_staging_acceptance  | Engine-level RLS not in DDL   |
+----+----------------------+---------------------------------+--------------------------+-------------------------------+
| 11 | Offline Field Queue  | frontend/src/lib/offline/       | frontend/tests/          | Browser IndexedDB quota; sync |
|    | (IndexedDB / Dexie)  |                                 | offline-queue.test.js    | requires active network       |
+----+----------------------+---------------------------------+--------------------------+-------------------------------+
| 12 | Agronomist Portal    | backend/app/api/v1/endpoints/   | test_diagnoses.py        | Requires agricultural expert  |
|    | (ExpertConnect)      | expertconnect.py                | test_staging_acceptance  | role assignment by admin      |
+----+----------------------+---------------------------------+--------------------------+-------------------------------+
```

---

## 4. Test Suite Audit & Independent Execution

All test suites were executed independently in the workspace virtual environment (`.venv`, Python 3.11.16, Node.js 24.19.0). 

### 4.1 Test Accounting Reconciliation

The previous report claimed `145 + 9 + 6 + 43 + 37 = 240`. Our audit reveals the true physical distribution:

| Test Suite Location | Collected | Passed | Failed | Skipped | Execution Time | Audit Reconciliation Finding |
|---|---:|---:|---:|---:|---:|---|
| `backend/tests/` (Master Backend) | **145** | **145** | 0 | 0 | 356.09s | Includes 9 staging acceptance tests inside `test_staging_acceptance.py` |
| `tests/ml/` (Machine Learning) | **55** | **55** | 0 | 0 | 39.17s (shared) | Contains 19 test files (models, calibration, archival, Grad-CAM, transforms) |
| `tests/api/` (Vision API Endpoints)| **9** | **9** | 0 | 0 | 39.17s (shared) | Dedicated vision FastAPI test client suite |
| `frontend/tests/` (Node.js Runner) | **43** | **43** | 0 | 0 | 1.19s | IndexedDB, offline sync, PWA, trilingual localization parity |
| **TOTAL PHYSICAL TEST SUITE** | **252** | **252** | **0** | **0** | **396.45s** | **100% PASS RATE — Zero Test Failures** |

> [!NOTE]
> The physical codebase contains **252 unique passing automated tests**. The earlier report undercounted ML tests (listing only 6 dataset archival tests rather than all 55 ML tests) while double-counting staging acceptance tests.

### 4.2 TypeScript & Static Verification
- Command: `cd frontend; npx tsc --noEmit`
- Result: **0 errors** (Clean compilation across all Next.js App Router components, API client adapters, and localization dictionaries).

---

## 5. Staging Deployment Reality Check

| Verification Item | Required State | Actual Inspected State | Audit Status | Evidence |
|---|---|---|---|---|
| Configuration File | `frontend/vercel.json` | Exists, valid JSON | **VERIFIED** | Pinned to `sin1`, security headers configured |
| Environment File | `.env.staging.example` | Exists, non-secret | **VERIFIED** | Staging namespaces, preview model, zero secrets |
| Live Preview URL | Public URL accessible | None provisioned | **BLOCKED_EXTERNAL** | Deployment requires explicit owner authorization |
| Neon Staging Branch | Isolated DB branch | Documented pattern | **VERIFIED_CONFIG** | Copy-on-write branching documented |
| Redis Staging Prefix | `acrevia_staging:*` | Implemented in code | **VERIFIED** | Key generator prepends `RATE_LIMIT_NAMESPACE` |

---

## 6. Database Tenancy & Security Assessment

### 6.1 Application-Level Tenancy: `COMPLETE_VERIFIED`
FastAPI dependency `verify_farm_access()` in `backend/app/security/dependencies.py` intercepts requests for farm-scoped entities. Cross-tenant access attempts were tested in `test_staging_tenant_isolation` and `test_authorization.py`:
- Farmer A querying Farmer B's farm $\rightarrow$ HTTP 403 Forbidden.
- Farmer A attempting to create plots on Farmer B's farm $\rightarrow$ HTTP 403 Forbidden.

### 6.2 PostgreSQL Engine-Level RLS: `NOT_IMPLEMENTED`
An inspection of `backend/app/database/migrations/versions/` confirmed that `ENABLE ROW LEVEL SECURITY` and `CREATE POLICY` statements are **absent from all Alembic migration files**.
- **Implication:** If a developer bypasses FastAPI dependencies or runs direct SQL queries, PostgreSQL will not enforce isolation at the storage level.
- **Remediation Plan:** Classified as **Finding `DEF-02` (Severity: P2)**. An Alembic migration introducing PostgreSQL RLS policies should be scheduled for the next milestone.

---

## 7. External Provider & Scientific Verification

### 7.1 NDVI Calculations Tracing (0.2927 vs 0.6364)
- **`0.2927`:** Derived from a real Sentinel-2 L2A tile window read over Warangal, Telangana (`S2A_44QLE_20240328_0_L2A`, acquisition date March 28, 2024). Valid pixels: 10,000 (100x100 window); Red (B04), NIR (B08); Mean NDVI: 0.2927 (min: 0.0866, max: 0.8816, std: 0.1358).
- **`0.6364`:** Derived from synthetic unit test arrays in `test_earth_search_satellite.py` and `test_staging_acceptance.py`. Arrays: $\text{NIR} = 4500$, $\text{Red} = 1000$. Formula $\frac{4500 - 1000}{4500 + 1000} = \frac{3500}{5500} \approx 0.6364$.
- **Audit Conclusion:** Both measurements are authentic for their respective purposes. The report explicitly clarifies that `0.6364` is a test fixture, not a real field observation.

### 7.2 GroqCloud AI Inference
- Configured Model: `qwen/qwen3.8-27b` (Preview Model under Free Developer Tier).
- Failure Fallback: Extractive RAG chunks with PJTSAU citations returned immediately upon HTTP 429 or timeout.
- Account Billing: **`NOT_VERIFIABLE`** via public APIs without private console access.

---

## 8. Consolidated Defect & Risk Register (P0–P4)

```
+======================================================================================================================+
| ACREVIA DEFECT & RISK REGISTER                                                                                       |
+----+-----+----------------------+------------------------------------+-----------------------------+-----------------+
| ID | Sev | Component            | Finding Description                | Recommended Remediation     | Status          |
+----+-----+----------------------+------------------------------------+-----------------------------+-----------------+
| D1 | P1  | Staging Deployment   | Live Vercel staging deployment has | Await owner authorization   | BLOCKED_        |
|    |     |                      | not been executed; only config     | before running live deploy  | EXTERNAL        |
+----+-----+----------------------+------------------------------------+-----------------------------+-----------------+
| D2 | P2  | Database Security    | PostgreSQL engine-level RLS absent;| Add Alembic migration with  | PLANNED_        |
|    |     |                      | enforced only at application layer | Postgres RLS policies       | NEXT_STAGE      |
+----+-----+----------------------+------------------------------------+-----------------------------+-----------------+
| D3 | P2  | Distributed Rate     | Uniform fail_open used across all  | Configure fail_closed for   | PLANNED_        |
|    |     | Limiting             | routes, including auth endpoints   | /auth/login and /register   | NEXT_STAGE      |
+----+-----+----------------------+------------------------------------+-----------------------------+-----------------+
| D4 | P2  | AI Provider Model    | qwen/qwen3.8-27b is a preview model| Maintain robust fallback    | COMPLETE_WITH_  |
|    |     |                      | subject to upstream deprecation    | chain & extractive fallback | LIMITATIONS     |
+----+-----+----------------------+------------------------------------+-----------------------------+-----------------+
| D5 | P3  | Documentation        | Test accounting double-counted     | Updated documentation to    | CLOSED_         |
|    |     |                      | staging tests; undercounted ML     | reflect true 252 tests      | VERIFIED        |
+----+-----+----------------------+------------------------------------+-----------------------------+-----------------+
| D6 | P4  | Frontend Tooling     | npm run lint fails due to missing  | Add eslint devDependencies  | PLANNED_        |
|    |     |                      | eslint packages in package.json    | in frontend/package.json    | NEXT_STAGE      |
+----+-----+----------------------+------------------------------------+-----------------------------+-----------------+
```

---

## 9. Final Independent Technical Assessment

- **Critical Security Breaches (P0):** `0` (Zero).
- **Pilot-Blocking Technical Defects (P1):** `1` (Live staging deployment awaiting owner authorization).
- **Important Architectural Limitations (P2):** `3` (Database RLS, rate limit fail mode, preview model volatility).
- **Automated Test Quality:** **252/252 Passed (100%)**.

**Audit Verdict:** The technical foundation of ACREVIA is solid, robust, and reproducible. The application is technically sound for institutional demonstration, with clear and documented operational limitations.
