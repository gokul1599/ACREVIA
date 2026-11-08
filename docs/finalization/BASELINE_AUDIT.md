# ACREVIA — BASELINE ENVIRONMENT & REPOSITORY AUDIT
## Phase 1 Inspection Baseline Prior to Modifications

**Audit Execution Timestamp:** 2026-11-08T14:48:19+05:30  
**Auditor:** ACREVIA Principal Architecture & SRE Team  
**Host Environment:** Windows 11 Pro 64-bit (Host Machine)  
**Python Runtime:** CPython 3.11.16 (`.venv\Scripts\python.exe`)  
**Node.js Runtime:** v24.19.0 (npm 11.17.0)  

---

### 1. Version Control & Working Tree State
* **Repository Root:** `C:\Users\gokul\OneDrive\Documents\projects`
* **Active Branch:** `main`
* **Current Commit Hash:** `878fccc` (`feat(database): enable seamless Neon PostgreSQL pooling and pg8000 support`)
* **Remote Upstream:** `https://github.com/gokul1599/ACREVIA.git` (synchronized, clean working tree)
* **Untracked / Modified Files at Inspection:**
  * Clean working tree confirmed via `git status`.
  * Pre-existing database artifact: `acrevia_dev.db` (local SQLite fallback, 2.4 MB).
  * Monorepo submodules / external folders present in workspace: `aheadguard-mvp-starter`, `tabmind-ai`, `tap-house-20`, `teluguva`.

---

### 2. Live Database & Extensions Verification
* **Database Provider:** Neon Serverless PostgreSQL 16
* **Database Host:** `ep-muddy-mode-a1nd6rrb-pooler.ap-southeast-1.aws.neon.tech` (AWS Singapore `sin1`/`ap-southeast-1`)
* **Engine Version Reported:** `PostgreSQL 18.6 (ac70818) on aarch64-unknown-linux-gnu, compiled by aarch64-unknown-linux-gnu-gcc (GCC) 7.4.0, 64-bit`
* **Installed Extensions:**
  * `plpgsql` (version 1.0)
  * `vector` (version 0.8.6 — pgvector enabled for 1536-dimensional semantic vector indexing)
* **Active Schema Table Count:** 133 tables (132 agricultural domain entities + 1 `alembic_version`)
* **Active Alembic Revision Head:** `f4894a11c87d (head)` (`stage14_interoperability_ecosystem`)
* **Database Driver:** Pure Python `pg8000` (version 1.31.6) with TLS `ssl.create_default_context()` enabled in `backend/app/database/session.py` to bypass Windows AppLocker restrictions on unmanaged DLLs (`_psycopg.cp311-win_amd64.pyd`).

---

### 3. Baseline Automated Test Verification
All test suites were executed independently and verified:

| Test Suite | Command | Result | Duration | Notes |
|---|---|---|---|---|
| **Backend Unit & Integration** | `python -m pytest backend/tests/ -v` | **97 Passed, 0 Failed** | 574.42s | Covers Auth, RBAC, Diagnoses, Knowledge RAG, Observations, Weather, and Stages 7 through 14 |
| **ML Inference Microservice** | `python -m pytest ml/inference_service/tests/ -v` | **7 Passed, 0 Failed** | 17.46s | Covers Health, Model Info, MobileNetV3 multi-crop, blur rejection, OOD non-plant rejection |
| **Frontend Component & PWA** | `npm --prefix frontend test` | **36 Passed, 0 Failed** | 0.98s | Node.js native test runner (`node --test`), covers localization parity across EN/TE/HI, OfflineQueue, SpeechAdapter |
| **Frontend Production Build** | `npm --prefix frontend run build` | **13/13 Static Pages** | 12.8s | Turbopack compilation succeeded with zero warnings; prerendered static routes |
| **TOTAL** | | **140 / 140 Passed (100% Green)** | | Zero broken assertions, zero skipped tests |

---

### 4. Live Deployment Baseline
* **Platform:** Vercel Global Edge Platform
* **Vercel Account:** `gokul1599`
* **Authentication Token:** Provided user deployment token (`vcp_...`) validated via `vercel whoami`.
* **Frontend Project:** `gokul1599/frontend`
* **Live Production URL:** `https://frontend-e1dh1orfd-gokul1599.vercel.app`
* **Aliased URL:** `https://frontend-omega-two-hijwc54gyy.vercel.app`
* **Deployment ID:** `dpl_ZRh4NS4YaiyNWVHGRXmzjw36Vuwn`
* **HTTP Status:** 200 OK (verified via live network request returning default Telugu `<html lang="te">` interface).

---

### 5. Identified Baseline Gaps & Focus Areas
1. **Third-Party Live Production Credentials:** Market data (e-NAM/Agmarknet), Sentinel-2 STAC/Hub credentials, and WhatsApp Business API tokens are currently operating on simulated sandbox adapters (`CONFIGURED_SANDBOX`). Real farmer SMS/WhatsApp delivery requires registered DLT templates and carrier credentials.
2. **FastAPI Backend Serverless Constraint:** Due to PyTorch and ONNX dependencies exceeding Vercel's 250 MB uncompressed function limit, the production architecture must maintain separation between the Next.js Vercel frontend and the dedicated ML microservice.
3. **Field Pilot Status:** The 15-farmer simulation conducted in Stage 8 is a synthetic simulation; a real-world field pilot with actual Telangana farmers remains in `NOT_STARTED` status.
