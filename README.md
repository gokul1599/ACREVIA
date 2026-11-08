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
│   ├── tests/                  # 53 Comprehensive Integration, Security & Stage 8 E2E Tests
│   └── Dockerfile              # Production Multi-Stage Container Definition
├── ml/                         # Advanced Agricultural Computer Vision Subsystem
│   ├── models/                 # MultiCrop Backbones, Heads & Abstention Engines
│   ├── training/               # FocalLoss, LabelSmoothing, Cosine Schedulers
│   ├── evaluation/             # Grad-CAM Explainability & Field Robustness Harness
│   └── inference_service/      # Dedicated Standalone ML Microservice (:8001)
├── frontend/                   # Farmer & Expert Progressive Web Application
│   ├── app/                    # Next.js 14 App Router Pages (Dashboard, Diagnosis, KrishiBrain, CropPulse, Workspace)
│   ├── lib/api/                # Strongly Typed API Client & Data Interfaces
│   ├── messages/               # 100% Key-Parity Multilingual Dictionaries (Telugu, English, Hindi)
│   └── tests/                  # 16 Frontend Unit, Security & Stage 8 Verification Tests
├── docs/                       # Comprehensive Architecture & Research Documents
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

---

## 5. Verification & Testing Evidence

```powershell
# Run entire repository automated test suite (127 passing automated tests)
python -m pytest backend/tests tests/ml tests/api -v   # 111 passed, 0 failed
npm test --prefix frontend                            # 16 passed, 0 failed
npm run build --prefix frontend                       # 13/13 static pages compiled
```

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
