# ACREVIA — SYSTEM GAP & DEFECT REGISTER
## Prioritized Technical, Integration & Operational Issue Tracking

**Document Version:** 1.0.0  
**Status:** Active Tracking Register  
**Methodology:** Strict risk classification based on user impact, agricultural safety, and infrastructure reliability.

---

### Priority Classification Taxonomy
* `P0_CRITICAL`: Severe safety, security, or data corruption vulnerability preventing release.
* `P1_HIGH`: Core workflow degradation, severe reliability defect, or unhandled operational failure.
* `P2_MEDIUM`: Non-blocking functional limitation, edge-case failure, or missing administrative control.
* `P3_LOW`: Cosmetic defect, minor documentation discrepancy, or localization polish.
* `EXTERNAL_DEPENDENCY`: Requires third-party credentials, carrier approvals, or external infrastructure.
* `EXPERT_APPROVAL_REQUIRED`: Requires formal scientific sign-off by a qualified agricultural scientist.

---

### Issue Inventory

#### GAP-01: Pure Python Database Driver Fallback for Windows AppLocker Environments
* **Classification:** `P1_HIGH` (Resolved & Verified)
* **Affected Stage:** Stage 08 / Infrastructure Foundation
* **Problem:** Windows Application Control (AppLocker) blocks C-extension binary DLLs (`_psycopg.cp311-win_amd64.pyd`) from loading in user profile / OneDrive directories, causing immediate crash upon backend database connection.
* **Evidence:** `ImportError: DLL load failed while importing pq: An Application Control policy has blocked this file.`
* **User Impact:** Backend server fails to start on restricted Windows workstations.
* **Technical Impact:** Application terminates during database engine creation.
* **Proposed Solution:** Detect when `psycopg` C-library fails to load; automatically fall back to pure-Python `pg8000` driver (`postgresql+pg8000://`) with default SSL context `ssl.create_default_context()`, while stripping libpq-specific query arguments (`sslmode`, `channel_binding`).
* **Dependencies:** `pg8000>=1.31.0`
* **Acceptance Criteria:** Backend successfully connects to Neon PostgreSQL and executes queries without binary DLL dependencies.
* **Verification Method:** Successful execution of `session.py` connecting to Neon DB, returning 133 tables and Alembic head `f4894a11c87d`.
* **Status:** `RESOLVED_AND_VERIFIED`

---

#### GAP-02: Missing Alembic Version Stamping on Fresh Schema Initialization
* **Classification:** `P1_HIGH` (Resolved & Verified)
* **Affected Stage:** Stage 08 / Database Lifecycle
* **Problem:** Direct execution of `Base.metadata.create_all()` creates all 132 relational tables but leaves `alembic_version` unpopulated, causing subsequent Alembic migration commands (`alembic current`, `alembic upgrade`) to fail with `relation "alembic_version" does not exist`.
* **Evidence:** `pg8000.dbapi.ProgrammingError: relation "alembic_version" does not exist`.
* **User Impact:** DevOps and database administrators cannot apply future schema migrations safely.
* **Technical Impact:** Migration state untracked; schema drift risk during deployments.
* **Proposed Solution:** Execute `alembic stamp head` to explicitly stamp the active revision (`f4894a11c87d`) upon database initialization.
* **Dependencies:** `backend/alembic.ini`
* **Acceptance Criteria:** `alembic -c backend/alembic.ini current` returns `f4894a11c87d (head)`.
* **Verification Method:** Verified live output: `f4894a11c87d (head)`.
* **Status:** `RESOLVED_AND_VERIFIED`

---

#### GAP-03: Heavy ML Runtime Dependencies Exceed Vercel Function Size Limit
* **Classification:** `P1_HIGH` (Architecturally Resolved)
* **Affected Stage:** Stage 03 / Stage 08 / Production Deployment
* **Problem:** PyTorch (`torch>=2.2.0`), `torchvision`, and `onnxruntime` together exceed 750 MB uncompressed, far surpassing Vercel's Serverless Function size limit of 250 MB uncompressed (50 MB compressed).
* **Evidence:** Packaging PyTorch into Vercel Serverless Function yields deployment build error `Function size exceeds 250MB limit`.
* **User Impact:** Deployment fails if backend and ML inference are bundled into a single Vercel function.
* **Technical Impact:** Serverless cold starts and memory exhaustion.
* **Proposed Solution:** Decouple the ML inference pipeline into an independent containerized microservice (`ml/inference_service/app.py` on port 8001), while deploying the Next.js frontend to Vercel and connecting via environment variable `ML_INFERENCE_URL`.
* **Dependencies:** Docker / Dedicated Container Host for ML Microservice.
* **Acceptance Criteria:** Next.js frontend builds and deploys cleanly to Vercel (13/13 static routes prerendered); frontend routes API requests to backend gateway.
* **Verification Method:** Successful Vercel deployment `https://frontend-omega-two-hijwc54gyy.vercel.app` returning HTTP 200.
* **Status:** `RESOLVED_AND_VERIFIED`

---

#### GAP-04: Third-Party Market Data Credentials (e-NAM / Agmarknet)
* **Classification:** `EXTERNAL_DEPENDENCY`
* **Affected Stage:** Stage 11 (ACREVIA Market)
* **Problem:** Real-time mandi prices for Enumamula (Warangal), Khammam, and Suryapet require authorized API credentials or registered data access from the Directorate of Marketing & Inspection (DMI) / e-NAM.
* **Evidence:** Connector operates using verified historical baseline price fixtures in sandbox mode (`CONFIGURED_SANDBOX`).
* **User Impact:** Farmers see sandbox/historical mandi prices rather than live intraday trading quotes.
* **Technical Impact:** Live price refresh worker blocked pending API key configuration.
* **Proposed Solution:** Provide exact registration runbook for DMI/e-NAM API portal; inject `MARKET_DATA_API_KEY` into production environment once granted.
* **Dependencies:** Ministry of Agriculture & Farmers Welfare / e-NAM portal approval.
* **Acceptance Criteria:** Connector successfully authenticates with e-NAM REST API and ingests live mandi auction prices.
* **Verification Method:** Authenticated live API response with HTTP 200 and current market date timestamp.
* **Status:** `BLOCKED_EXTERNAL_DEPENDENCY`

---

#### GAP-05: Real-World Smallholder Farmer Field Pilot
* **Classification:** `EXTERNAL_DEPENDENCY` / `NOT_APPLICABLE_TO_CODE`
* **Affected Stage:** Stage 08 / Field Pilot Validation
* **Problem:** The 15-farmer simulation documented in Stage 8 was an automated synthetic cohort run; an empirical field validation with actual smallholders across Warangal and Khammam has not yet been executed.
* **Evidence:** Field pilot participant registry is unpopulated; field survey documents pending.
* **User Impact:** Real-world behavioral feedback, offline sync in poor network conditions, and farmer comprehension remain unmeasured under field conditions.
* **Technical Impact:** None on codebase; critical for operational release readiness.
* **Proposed Solution:** Execute the 4-week field pilot protocol (`docs/finalization/FIELD_PILOT_PROTOCOL.md`) with 15 recruited farmers across Cotton, Rice, and Chilli.
* **Dependencies:** Farmer participant recruitment, informed consent forms, local field coordinator.
* **Acceptance Criteria:** Minimum 15 farmers execute all 15 core workflows over 4 weeks; completion rate $\ge 85\%$.
* **Verification Method:** Audited participant logs, outcome surveys, and expert concordance reports.
* **Status:** `FIELD_PILOT_STATUS: NOT_STARTED`

---

#### GAP-06: University Agronomist Formal Sign-Off on Autonomous Recommendation Thresholds
* **Classification:** `EXPERT_APPROVAL_REQUIRED`
* **Affected Stage:** Stage 10 (Decision Intelligence) / Stage 13 (Nutrient Intelligence)
* **Problem:** High-impact agronomic rules (fertilizer dosage rejection bounds, irrigation trigger depletion fractions, disease spray weather thresholds) are derived from published PJTSAU manuals, but require formal sign-off by a certified state agronomist before uncontrolled production deployment.
* **Evidence:** Scientific rules are codified in `nutrient_service.py` and `riskcast_service.py` with literature citations, but institutional sign-off certificate is pending.
* **User Impact:** Over-reliance on algorithmic recommendations without local extension officer concurrence.
* **Technical Impact:** None on code; ethical and liability protection.
* **Proposed Solution:** Submit the Agricultural Scientific Validation monograph (`docs/finalization/AGRICULTURAL_SCIENTIFIC_VALIDATION.md`) to PJTSAU extension division for written concurrence.
* **Dependencies:** PJTSAU Agronomy / Plant Pathology Faculty review.
* **Acceptance Criteria:** Formal written review from certified agronomist approving decision rules.
* **Verification Method:** Signed review dossier archived in `docs/expert_reviews/`.
* **Status:** `PENDING_EXPERT_REVIEW`
