# ACREVIA — Agricultural Intelligence Platform
### Research-Grade Computer Vision, Multimodal RAG & Agronomic Decision Support for Smallholder Farmers

---

## 1. Overview & Canonical Identity

**ACREVIA** (formerly KisanVision) is an enterprise-grade agricultural intelligence platform built specifically for smallholder farmers in **Telangana, India**. It combines lightweight edge-ready computer vision, agrometeorological risk modeling, multimodal Retrieval-Augmented Generation (RAG), and certified agronomist human validation.

- **Target Geography:** Telangana-first, India (Warangal, Khammam, Karimnagar, Nalgonda, Adilabad, Mahabubnagar)
- **Initial Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*)
- **Supported Languages:** Telugu (`te`), English (`en`), Hindi (`hi`)
- **Frontend Architecture:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4, PWA (Service Worker & Manifest)
- **Backend Architecture:** Python 3.11, FastAPI, SQLAlchemy 2.0, PostgreSQL 16 + pgvector (Neon / SQLite fallback)
- **ML / Inference Architecture:** PyTorch 2.15, MobileNetV3-Small/Large, ONNX Runtime, Int8 Quantization
- **Knowledge / RAG Subsystem:** KrishiBrain (Structure-Aware Chunking, 1536d Embeddings, Hybrid Retrieval, CIBRC Safety Guardrails)
- **Climate Risk Subsystem:** RiskCast (Hourly Observations vs. Forecasts, PJTSAU Rules, Leaf Wetness Hours, Idempotent Alerts)
- **Human Expert Network:** ExpertConnect (Agronomist Credentialing, Case Triage, Multimodal Evidence Dossiers, Immutable Revisions)
- **Farm Action Journal:** Intervention Intelligence (Biological/Chemical tracking, PHI/REI, Outcome Observations, Non-Causal Disclaimers)
- **Precision Agriculture (Stage 09):** Acrevia Geo (WGS84 Geometries), Acrevia Earth (Sentinel-2/Landsat-9 NDVI/EVI/NDMI), Acrevia Sense (IoT & Calibration QC), Acrevia Fusion (Contradiction Resolution), Acrevia Predict (Governed Feasibility & Withholding), and Agricultural Knowledge Graph.
- **Intelligent Farm Digital Twin & Decision Intelligence (Stage 10):** ACREVIA Twin (8-Tier Provenance & Snapshots), ACREVIA Simulate (FAO-56 Dual-$K_c$ Water Balance, GDD Staging, Waterlogging), ACREVIA Optimize (Simplex Multi-Plot Water & Nutrient Allocation with Transparent Infeasibility Diagnosis), ACREVIA Plan (PJTSAU Calendars, Sowing-Date Scheduling, Weather Spray Conflict Guards), and ACREVIA Decision (7 Canonical Recommendation States, Grounded Explanation Engine en/te/hi, Zero Automated Actuation Boundary).
- **Agricultural Economics, Market Analytics & Produce Traceability (Stage 11):** ACREVIA Ledger (Decimal-accurate CACP $A_1$ expenses, receipts & immutable corrections), ACREVIA Market (Agmarknet/e-NAM Telangana mandis, modal benchmarks, distance-adjusted comparative net realization), ACREVIA Harvest (Multi-picking tracking, field loss accounting, automated ProduceLot minting), ACREVIA Quality (Calibrated moisture assay provenance, cold storage lots), ACREVIA Trace (Quantity conservation balance, privacy-redacted public QR verification), and ACREVIA Economics (Cost of cultivation, gross revenues, unit margins, and SHA-256 sealed PMFBY crop loss packages).
- **Agricultural Collaboration Network & Regional Pulse (Stage 12):** ACREVIA Connect (Moderated community spaces, post taxonomies, verified agronomist reply badges, non-scientific helpful voting disclaimers, misinformation reporting), ACREVIA Commons (Governed knowledge submissions, expert agronomic review gates, multilingual translation versions, KrishiBrain RAG handoff), ACREVIA Collectives (Private FPO/cooperative workspaces, role isolation, shared calendars, minimum cohort size rule $N \ge 5$ farms with strict suppression of individual financials/GPS), ACREVIA Research Hub (Institutional projects, purpose-specific farmer consent, farm-disjoint dataset splits, inter-annotator disagreement tracking), ACREVIA Extension (Educational crop guides, interactive workshops, capacity management, farmer feedback), and ACREVIA Regional Pulse (District-level signal aggregation, privacy-preserving $N \ge 3$ distinct farm threshold, automatic sensational outbreak rumor suppression).
- **Climate-Resilient & Sustainable Agriculture (Stage 13):** ACREVIA Soil (Accredited lab assays, Walkley-Black SOC, composite core tracking, spatial coverage density warnings), ACREVIA Water (Water asset inventory, metered irrigation, in-situ soil moisture telemetry, transparent hydrological water accounting separating measured from modeled components), ACREVIA Climate (30-year climatological normals 1991-2020, 5-tier hazard taxonomy, crop vulnerability windows, PJTSAU/CRIDA contingency adaptations), ACREVIA Nutrient (Soil-test-driven N-P-K & micronutrient management, split schedules, strict dosage rejection guards, agronomist escalation), ACREVIA Sustain (Verified regenerative practices, empirical SOC tracking, research-grade IPCC Tier 1/2 GHG accounting with non-certified disclaimers), and ACREVIA Resilience (Multi-dimensional vulnerability auditing, Evidence Quality Score $EQS$, climate adaptation scenario simulations).
- **Agricultural Interoperability & Open API Ecosystem (Stage 14):** ACREVIA Exchange (Data portability in JSON, CSV, GeoJSON, and Cryptographic ZIP with SHA-256 manifests; non-overwriting conflict preservation), ACREVIA Connect (Scoped developer credentials `ak_live_...`/`ak_sand_...`, SHA-256 secret hashing, scope enforcement, sandbox isolation), ACREVIA Partners (Governed institutional registry for Universities, Soil Labs, KVKs, and FPOs with verification lifecycle gates), ACREVIA Bridge (Provider-independent connector adapters for soil testing, market prices, weather stations, satellite feeds, and IoT sensors), ACREVIA Events (Transactional outbox pattern, HMAC-SHA256 signatures, 300s replay protection, strict SSRF loopback/RFC-1918 blocking), ACREVIA Standards (Canonical unit registry and multi-language crop taxonomies across EN/TE/HI), and Integration Hub (Farmer-facing consent portal, export builder, and developer console).
- **Security & Authorization:** Bcrypt (12 rounds), JWT (HS256), Multi-Tenant Farm Isolation (`verify_farm_access`)

---

## 2. Repository Layout

```text
projects/
├── backend/                    # ACREVIA Enterprise Backend Gateway
│   ├── app/
│   │   ├── api/v1/             # REST Endpoints (Auth, Farms, Diagnoses, Knowledge, RiskCast, ExpertConnect, Interventions)
│   │   ├── core/               # App Settings, Logging, Security, Exceptions
│   │   ├── database/           # SQLAlchemy 2.0 Base, Session, and Seed Scripts
│   │   ├── integrations/       # ML Microservice, Object Storage & Weather Clients
│   │   ├── models/             # 32 Relational Entities (Users, Farms, Diagnoses, Risk, Experts, Interventions)
│   │   ├── schemas/            # Pydantic v2 Request & Response Schemas
│   │   ├── security/           # JWT & Multi-Tenant Dependency Layer
│   │   ├── services/           # Encapsulated Business Logic (RiskCast, ExpertConnect, Interventions, KrishiBrain)
│   │   └── tasks/              # Standalone Bounded Cron Tasks (Batch RiskCast Runner)
│   ├── tests/                  # 68 Comprehensive Integration, Security, Stage 9 & Stage 10 E2E Tests
│   └── Dockerfile              # Production Multi-Stage Container Definition
├── ml/                         # Advanced Agricultural Computer Vision Subsystem
│   ├── models/                 # MultiCrop Backbones, Heads & Abstention Engines
│   ├── training/               # FocalLoss, LabelSmoothing, Cosine Schedulers
│   ├── evaluation/             # Grad-CAM Explainability & Field Robustness Harness
│   └── inference_service/      # Dedicated Standalone ML Microservice (:8001) with 7 automated tests
├── frontend/                   # Farmer & Expert Progressive Web Application
│   ├── app/                    # Next.js 16 App Router Pages (Dashboard, Diagnosis, KrishiBrain, CropPulse, Workspace)
│   ├── components/             # Reusable UI & Stage 10 Twin, Simulation, Optimization, Planning & Decision Cards
│   ├── lib/api/                # Strongly Typed API Client & Data Interfaces
│   ├── messages/               # 100% Key-Parity Multilingual Dictionaries (Telugu, English, Hindi)
│   └── tests/                  # 23 Frontend Unit, Security, Stage 9 & Stage 10 Verification Tests
├── docs/                       # Comprehensive Architecture & Research Documents
│   ├── stage-14/               # 13 Interoperability, Open API, Partner Integrations & Data Exchange Deliverables
│   ├── stage-13/               # 15 Soil Health, Water, Climate Resilience, Nutrient & Sustainability Deliverables
│   ├── stage-09/               # 17 Advanced Precision Agriculture, Satellite, IoT & Predict Deliverables
│   ├── stage-08/               # 20 Production Hardening, Audit & Validation Deliverables for Stage 8
│   ├── stage-07/               # 15 Architectural, Governance & Evaluation Specifications for Stage 7
│   ├── stage-06/               # PWA, Mobile UX & Localization Specs
│   ├── stage-05/               # KrishiBrain RAG Architecture & Evaluation
│   ├── architecture/           # System, Database & API Contracts
│   ├── security/               # Authentication, Authorization & OWASP Security Reviews
│   └── research/               # Taxonomy, Uncertainty, Calibration & Evaluation Reports
├── docker-compose.yml          # Local Container Topology (Backend + Postgres + ML)
└── .env.example                # Environment Variable Configuration Template
```

---

## 3. Quickstart & Local Setup

### 3.1 Installation
```powershell
# Create Python 3.11 virtual environment
uv venv .venv --python 3.11
.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Copy environment template
Copy-Item .env.example .env

# Initialize database schema & seed base taxonomies & risk rules
python -c "from backend.app.database.init_db import init_db; init_db()"
```

### 3.2 Running the Application
```powershell
# Terminal 1: Start ML Inference Microservice
uvicorn ml.inference_service.app.main:app --port 8001 --reload

# Terminal 2: Start ACREVIA Backend API Gateway
uvicorn backend.app.main:app --port 8000 --reload

# Terminal 3: Start Farmer & Expert Frontend
cd frontend
npm run dev
```
Interactive API documentation is accessible at `http://localhost:8000/docs`.

### 3.3 Running Automated Tests
```powershell
# Run backend test suite (45 tests including Stage 7)
python -m pytest backend/tests -v

# Run frontend test suite (13 tests)
npm test --prefix frontend

# Run entire repository test suite (116 automated tests)
python -m pytest tests/ml tests/api backend/tests -v
```

---

## 4. Current Milestone Status

- **Stage 1 (Environment Audit & Research Foundation):** Complete (Verdict: PASSED)
- **Stage 2 (Dataset Engineering & Baseline ML):** Complete (Verdict: PASSED WITH OPEN RISKS)
- **Stage 3 (Advanced CV, Uncertainty & Inference Engineering):** Complete (Verdict: PASSED WITH OPEN RISKS)
- **Stage 4 (Enterprise Backend, Database, Auth & Multi-Tenancy):** Complete (Verdict: PASSED WITH OPEN RISKS)
- **Stage 5 (KrishiBrain Multimodal RAG & Knowledge Engine):** Complete (Verdict: PASSED WITH OPEN RISKS)
- **Stage 6 (Farmer Experience, Multilingual PWA & Voice):** Complete (Verdict: PASSED WITH OPEN RISKS)
- **Stage 7 (RiskCast, Climate Risk, ExpertConnect & Interventions):** Complete (Verdict: PASSED)
- **Stage 8 (Production Hardening, E2E Validation, Security & Launch Readiness):** Complete (Verdict: GO — CONTROLLED PRODUCTION RELEASE)
- **Stage 9 (Advanced Precision Agriculture, Satellite, IoT & Predict):** Complete (Verdict: PASSED)
- **Stage 10 (Farm Digital Twin, Scenario Simulation & Decision Intelligence):** Complete (Verdict: PASSED)
- **Stage 11 (Agricultural Economics, Market Analytics & Produce Traceability):** Complete (Verdict: PASSED)
- **Stage 12 (Agricultural Collaboration, Collectives, Research & Regional Pulse):** Complete (Verdict: PASSED)
- **Stage 13 (Soil Health, Precision Water, Climate Resilience, Nutrient Governance & Sustainability):** Complete (Verdict: PASSED)

---

## 5. Verification & Testing Evidence

```powershell
# Run entire repository automated test suite (128 passing automated tests)
.venv\Scripts\python -m pytest backend/tests/ -v     # 88 passed, 0 failed
.venv\Scripts\python -m pytest ml/inference_service/tests/ -v  # 7 passed, 0 failed
npm test --prefix frontend                          # 33 passed, 0 failed
npm run build --prefix frontend                     # 13/13 static pages compiled
```

Comprehensive technical monographs and audit records are documented in [`docs/stage-13/`](./docs/stage-13/):
- `STAGE_13_READINESS_AUDIT.md`
- `SOIL_HEALTH_INTELLIGENCE.md`
- `WATER_INTELLIGENCE_ARCHITECTURE.md`
- `CLIMATE_RESILIENCE_ARCHITECTURE.md`
- `NUTRIENT_INTELLIGENCE_AND_GOVERNANCE.md`
- `SUSTAINABLE_AGRICULTURE_INTELLIGENCE.md`
- `AGRICULTURAL_RESILIENCE_ENGINE.md`
- `AGRICULTURAL_SOURCE_AND_METHOD_GOVERNANCE.md`
- `DATABASE_AND_DOMAIN_MODEL.md`
- `API_CONTRACTS.md`
- `SECURITY_AND_PRIVACY_REVIEW.md`
- `PERFORMANCE_AND_COST_REPORT.md`
- `TESTING_AND_SCIENTIFIC_VALIDATION.md`
- `DEPLOYMENT_GUIDE.md`
- `STAGE_13_COMPLETION_REPORT.md`
- `STAGE_12_COMPLETION_REPORT.md`

Comprehensive technical monographs and audit records are documented in [`docs/stage-11/`](./docs/stage-11/):
- `STAGE_11_READINESS_AUDIT.md`
- `FARM_FINANCIAL_LEDGER.md`
- `MARKET_INTELLIGENCE_ARCHITECTURE.md`
- `MARKET_DATA_SOURCE_REVIEW.md`
- `HARVEST_MANAGEMENT.md`
- `POST_HARVEST_QUALITY_AND_STORAGE.md`
- `PRODUCE_TRACEABILITY_ARCHITECTURE.md`
- `CROP_SEASON_ECONOMICS.md`
- `SELLING_DECISION_SUPPORT.md`
- `DATABASE_AND_DOMAIN_MODEL.md`
- `API_CONTRACTS.md`
- `SECURITY_AND_PRIVACY_REVIEW.md`
- `PERFORMANCE_AND_COST_REPORT.md`
- `TESTING_REPORT.md`
- `DEPLOYMENT_GUIDE.md`
- `STAGE_11_COMPLETION_REPORT.md`

Comprehensive technical monographs and audit records are documented in [`docs/stage-08/`](./docs/stage-08/):
- `STAGE_08_SYSTEM_READINESS_AUDIT.md`
- `SYSTEM_ARCHITECTURE_VERIFICATION.md`
- `CROPVISION_MODEL_VALIDATION_REPORT.md`
- `KRISHIBRAIN_RAG_VALIDATION_REPORT.md`
- `RISKCAST_VALIDATION_REPORT.md`
- `EXPERTCONNECT_VALIDATION_REPORT.md`
- `AGRICULTURAL_FIELD_PILOT_PROTOCOL.md`
- `AGRICULTURAL_FIELD_PILOT_REPORT.md`
- `SECURITY_ASSESSMENT.md`
- `DATA_GOVERNANCE_AND_PRIVACY_REPORT.md`
- `NEON_DATABASE_RECOVERY_PLAN.md`
- `VERCEL_PRODUCTION_DEPLOYMENT_GUIDE.md`
- `CI_CD_RELEASE_PROCESS.md`
- `OBSERVABILITY_AND_MONITORING.md`
- `PERFORMANCE_AND_COST_REPORT.md`
- `ACCESSIBILITY_AND_LANGUAGE_AUDIT.md`
- `INCIDENT_RESPONSE_AND_DISASTER_RECOVERY.md`
- `ACREVIA_PRODUCTION_READINESS_SCORECARD.md`
- `ACREVIA_RESEARCH_AND_TECHNICAL_REPORT.md`
- `STAGE_08_COMPLETION_REPORT.md`

---

## 5. Security & Technical Assurance Status

ACREVIA Phase 07 (Multi-Tenant Isolation, Dynamic Provenance Verification & Regional Pulse Hardening) has achieved verified preflight status:
- **Phase 07 Security Suite:** 123 tests passing (100% green; verified under standard and `python -O` optimized mode).
- **Frontend Test Suite:** 58 tests passing across IndexedDB offline persistence, localized dictionaries, and client security.
- **Backend & ML Integration Test Suite:** 252 tests passing in CI/CD automation pipeline.
- **CI/CD Status:** GitHub Actions automated matrix verifying Next.js production builds and full Pytest execution on push.

