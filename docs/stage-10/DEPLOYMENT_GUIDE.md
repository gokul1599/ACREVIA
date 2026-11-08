# ACREVIA STAGE 10: DEPLOYMENT AND OPERATIONS GUIDE
## Migration Procedures, Environment Configuration & Vercel Singapore Deployment

---

## 1. Prerequisites & Environment Configuration

Stage 10 builds directly upon the existing Stage 4–9 architecture. Ensure the following environment variables are active in your production and preview environments (Vercel Project Settings & `.env`):

```bash
# Database (Neon PostgreSQL with pgvector - Singapore sin1)
DATABASE_URL=postgresql+asyncpg://<username>:<password>@<ep-id>.sin1.neon.tech/acrevia_db?sslmode=require
DATABASE_URL_SYNC=postgresql://<username>:<password>@<ep-id>.sin1.neon.tech/acrevia_db?sslmode=require

# Application Secrets & Authentication
SECRET_KEY=<production_secret_key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# KrishiBrain & Embeddings (Singapore region aligned)
OPENAI_API_KEY=<openai_api_key>
EMBEDDING_MODEL=text-embedding-3-small

# Simulation & Serverless Controls
MAX_SIMULATION_DAYS=30
MAX_OPTIMIZATION_PLOTS=10
SIMULATION_TIMEOUT_MS=150
```

---

## 2. Database Migration Execution (Alembic)

Execute the Stage 10 schema migration against the Neon PostgreSQL database:

```bash
# Run migration to apply Stage 10 tables
poetry run alembic upgrade head
# or using active python environment:
.venv/Scripts/python -m alembic upgrade head
```

### Tables Created:
1. `farm_twins`
2. `twin_snapshots`
3. `twin_state_records`
4. `twin_synchronization_events`
5. `simulation_scenarios`
6. `simulation_results`
7. `optimization_problems`
8. `optimization_results`
9. `crop_calendar_definitions`
10. `crop_tasks`
11. `decision_records`
12. `decision_feedbacks`

---

## 3. Seed Agronomic Baseline Data

Seed official PJTSAU package of practice crop calendars for Telangana agro-climatic zones:

```bash
.venv/Scripts/python -m backend.app.services.crop_planning_service --seed-calendars
```

---

## 4. Vercel Build & Deployment Verification

1. **Frontend Static & SSR Build Check:**
   ```bash
   cd frontend
   npm run build
   ```
   Ensure all pages compile with zero TypeScript or Linting errors.

2. **Backend Automated Test Suite:**
   ```bash
   .venv/Scripts/python -m pytest backend/tests/test_stage10.py -v
   ```

3. **Deploy to Vercel Singapore (`sin1`):**
   ```bash
   vercel --prod
   ```

---

## 5. Post-Deployment Smoke Test Checklist

- [ ] Verify `GET /api/v1/twin/farms/{id}` returns twin status `SYNCHRONIZED` for an existing farm.
- [ ] Verify `POST /api/v1/simulations` completes in <100ms and returns valid FAO-56 depletion values.
- [ ] Verify `POST /api/v1/optimization/problems` correctly identifies infeasibility when constrained resources are insufficient.
- [ ] Verify `POST /api/v1/decisions/analyze` generates localized explanations across English, Telugu, and Hindi.
- [ ] Verify Next.js frontend renders Digital Twin Dashboard and Scenario Laboratory components cleanly.
