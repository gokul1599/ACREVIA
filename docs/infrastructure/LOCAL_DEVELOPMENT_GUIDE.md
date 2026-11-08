# ACREVIA — LOCAL DEVELOPMENT & DEPLOYMENT GUIDE
## Developer Environment Setup, Dual Database Modes, Docker Compose Topology, and Testing Protocols

---

## 1. System Requirements & Runtime Prerequisites

- **Python Runtime:** CPython 3.11.x (Pinned in `.python-version`)
- **Package Manager:** `uv` (recommended) or `pip`
- **Container Runtime:** Docker Desktop / Podman with Compose v2+
- **Database Engine (Production / Container):** PostgreSQL 16
- **Database Engine (Zero-Dependency Local Dev):** SQLite 3 (built into Python)

---

## 2. Fast-Track Local Setup

### 2.1 Clone & Virtual Environment Creation
```powershell
# 1. Create and activate Python 3.11 virtual environment
uv venv .venv --python 3.11
.venv\Scripts\activate      # Windows PowerShell
# source .venv/bin/activate # Linux / macOS

# 2. Install pinned dependencies
uv pip install -r requirements.txt
```

### 2.2 Configure Environment Variables
```powershell
Copy-Item .env.example .env
```
Edit `.env` to verify default parameters:
```ini
ENVIRONMENT=development
DATABASE_URL=sqlite:///./acrevia_dev.db
JWT_SECRET_KEY=dev_secret_key_change_in_production_32chars
ML_INFERENCE_URL=http://localhost:8001
STORAGE_PROVIDER=LOCAL
STORAGE_LOCAL_DIR=data/storage
```

### 2.3 Initialize Database & Baseline Taxonomies
```powershell
python -c "from backend.app.database.init_db import init_db; init_db()"
```
This automatically provisions tables and seeds the 4 system roles (`FARMER`, `AGRICULTURAL_EXPERT`, `RESEARCHER`, `ADMIN`) and 3 Telangana target crops (`cotton`, `rice`, `chilli`).

---

## 3. Running Services Locally

### Option A: Bare-Metal Development (Fastest iteration)
```powershell
# Terminal 1: Start Stage 3 ML Inference Microservice
uvicorn ml.inference_service.app.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2: Start ACREVIA Core Backend API
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Navigate to `http://localhost:8000/docs` to interact with Swagger UI.

### Option B: Full Containerized Stack (Docker Compose)
```powershell
docker compose up --build -d
```
This spins up three healthy containers:
1. `acrevia_postgres`: PostgreSQL 16 on port `5432` with volume persistence.
2. `acrevia_ml_inference`: Zero-Torch Stage 3 microservice on port `8001`.
3. `acrevia_backend`: FastAPI Core API Gateway on port `8000`.

Check cluster status:
```powershell
docker compose ps
docker compose logs -f backend
```

---

## 4. Running the Test Suite

Execute the comprehensive test suite across all modules:
```powershell
# Run backend API & authorization tests
python -m pytest backend/tests -v

# Run entire repository test suite (ML + Backend + Microservice)
python -m pytest tests/ml tests/api ml/inference_service/tests backend/tests -v
```
All 96 automated tests must pass before opening PRs or initiating production deployments.
