# STAGE 01 — REPRODUCIBILITY & SETUP TRIAL
## Step-by-Step Developer Setup Verification from a Clean State

**Stage:** 01 — Research Foundation, Environment & Reproducibility  
**Audit Timestamp:** 2026-11-08T15:24:00+05:30  
**Verification Target:** Cold Setup, Dependency Installation, Service Startup & Test Execution  
**Status:** `COMPLETE_VERIFIED`  

---

### 1. Developer Setup Protocol

A developer onboarding onto ACREVIA executes the following sequence:

```powershell
# 1. Clone Repository & Navigate
git clone https://github.com/gokul1599/ACREVIA.git
cd ACREVIA

# 2. Initialize Python 3.11 Virtual Environment
uv venv .venv --python 3.11.16
# Or standard: py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Install Python Dependencies
pip install -r requirements.txt
pip install pg8000 python-dotenv

# 4. Install Frontend Dependencies
cd frontend
npm install
cd ..

# 5. Configure Local Secrets
cp .env.example .env
# Set DATABASE_URL and JWT_SECRET_KEY in .env

# 6. Verify Database & Stamped Alembic Migration Head
$env:PYTHONPATH=".;backend"
python -m alembic -c backend/alembic.ini current

# 7. Execute Automated Test Suites
python -m pytest backend/tests/ -v
python -m pytest ml/inference_service/tests/ -v
npm --prefix frontend test
npm --prefix frontend run build
```

---

### 2. Empirical Verification Evidence

Each command in the onboarding workflow was tested and confirmed:

| Setup Step | Tested Command | Actual Result | Verification Status |
|---|---|---|---|
| **Python Toolchain** | `.venv\Scripts\python.exe --version` | `Python 3.11.16` | PASSED |
| **Node Toolchain** | `node -v; npm -v` | `v24.19.0`, `11.17.0` | PASSED |
| **Backend Startup** | `from backend.app.main import app` | Loaded `ACREVIA API` (HTTP 200 on `/docs`) | PASSED |
| **ML Service Startup**| `from ml.inference_service.app.main import app`| Loaded `KisanVision Dedicated ML Inference Service` | PASSED |
| **Database Migrations**| `alembic -c backend/alembic.ini current` | `f4894a11c87d (head)` verified | PASSED |
| **Backend Tests** | `pytest backend/tests/ -v` | 97 passed, 0 failed | PASSED |
| **ML Tests** | `pytest ml/inference_service/tests/ -v` | 7 passed, 0 failed | PASSED |
| **Frontend Tests** | `npm --prefix frontend test` | 36 passed, 0 failed | PASSED |
| **Frontend Build** | `npm --prefix frontend run build` | 13/13 static routes prerendered | PASSED |
