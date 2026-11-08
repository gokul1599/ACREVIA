# ACREVIA — Agricultural Intelligence Platform
### Research-Grade Computer Vision, Multimodal RAG & Agronomic Decision Support for Smallholder Farmers

---

## 1. Overview & Canonical Identity

**ACREVIA** (formerly KisanVision) is an enterprise-grade agricultural intelligence platform built specifically for smallholder farmers in **Telangana, India**. It combines lightweight edge-ready computer vision, agrometeorological risk modeling, multimodal Retrieval-Augmented Generation (RAG), and certified agronomist human validation.

- **Initial Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*)
- **Supported Languages:** Telugu (`te`), English (`en`), Hindi (`hi`)
- **Frontend Architecture:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4, PWA (Service Worker & Manifest)
- **Backend Architecture:** Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL 16 + pgvector (Neon / SQLite fallback)
- **ML / Inference Architecture:** PyTorch 2.15, MobileNetV3-Small/Large, ONNX Runtime, Int8 Quantization
- **Knowledge / RAG Subsystem:** KrishiBrain (Structure-Aware Chunking, 1536d Deterministic & Cloud Embeddings, Hybrid Retrieval, CIBRC Safety Guardrails)
- **Security & Authorization:** Bcrypt (12 rounds), JWT (HS256), Multi-Tenant Farm Isolation (`verify_farm_access`)

---

## 2. Repository Layout

```text
projects/
├── backend/                    # ACREVIA Enterprise Backend Gateway
│   ├── app/
│   │   ├── api/v1/             # REST Endpoints (Auth, Farms, Plots, Diagnoses, Weather, etc.)
│   │   ├── core/               # App Settings, Logging, Security, Exceptions
│   │   ├── database/           # SQLAlchemy 2.0 Base, Session, and Seed Scripts
│   │   ├── integrations/       # ML Microservice, Object Storage & Weather Clients
│   │   ├── models/             # 24 Relational Entities (Users, Farms, Diagnoses, Audit)
│   │   ├── schemas/            # Pydantic v2 Request & Response Schemas
│   │   ├── security/           # JWT & Multi-Tenant Dependency Layer
│   │   └── services/           # Encapsulated Business Logic Services
│   ├── tests/                  # 31 Comprehensive Integration & Authorization Tests
│   └── Dockerfile              # Production Multi-Stage Container Definition
├── ml/                         # Advanced Agricultural Computer Vision Subsystem
│   ├── models/                 # MultiCrop Backbones, Heads & Abstention Engines
│   ├── training/               # FocalLoss, LabelSmoothing, Cosine Schedulers
│   ├── evaluation/             # Grad-CAM Explainability & Field Robustness Harness
│   └── inference_service/      # Dedicated Standalone ML Microservice (:8001)
├── docs/                       # Comprehensive Architecture & Research Documents
│   ├── architecture/           # System, Database, API Contract & Completion Reports
│   ├── security/               # Authentication, Authorization & OWASP Security Reviews
│   ├── infrastructure/         # Local Dev Guide & Storage Lifecycle Specs
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

# Initialize database schema & seed base taxonomies
python -c "from backend.app.database.init_db import init_db; init_db()"
```

### 3.2 Running the Application
```powershell
# Terminal 1: Start ML Inference Microservice
uvicorn ml.inference_service.app.main:app --port 8001 --reload

# Terminal 2: Start ACREVIA Backend API Gateway
uvicorn backend.app.main:app --port 8000 --reload
```
Interactive API documentation is accessible at `http://localhost:8000/docs`.

### 3.3 Running Automated Tests
```powershell
# Run backend test suite (39 tests including KrishiBrain)
python -m pytest backend/tests -v

# Run frontend test suite (9 tests)
npm test --prefix frontend

# Run entire repository test suite (113 automated tests)
python -m pytest tests/ml tests/api ml/inference_service/tests backend/tests -v
```

---

## 4. Current Milestone Status

- **Stage 1 (Environment Audit & Research Foundation):** Complete (Verdict: PASSED)
- **Stage 2 (Dataset Engineering & Baseline ML):** Complete (Verdict: PASSED WITH OPEN RISKS)
- **Stage 3 (Advanced CV, Uncertainty & Inference Engineering):** Complete (Verdict: PASSED WITH OPEN RISKS)
- **Stage 4 (Enterprise Backend, Database, Auth & Multi-Tenancy):** Complete (Verdict: PASSED WITH OPEN RISKS)
- **Stage 5 (KrishiBrain Multimodal RAG & Knowledge Engine):** Complete (Verdict: PASSED WITH OPEN RISKS)
- **Stage 6 (Farmer Experience, Multilingual PWA & Voice):** Complete (Verdict: PASSED WITH OPEN RISKS)
- **Stage 7 (RiskCast, Climate Risk, ExpertConnect & Interventions):** Next Scheduled Milestone (Weeks 13–14)
