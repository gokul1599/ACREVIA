# ACREVIA — Stage 7 Deployment & Infrastructure Guide
## Neon PostgreSQL, Vercel Singapore (sin1), and Environment Synchronization

---

## 1. Cloud Architecture Overview

```
                      +---------------------------------------+
                      |         FARMER MOBILE CLIENT          |
                      |   - Next.js 16 App Router (PWA)       |
                      |   - Deployed on Vercel Edge (sin1)    |
                      +-------------------+-------------------+
                                          |
                              HTTPS / API | Requests
                                          v
                      +---------------------------------------+
                      |          FASTAPI BACKEND API          |
                      |   - Containerized Python 3.11         |
                      |   - Regional Alignment: Singapore     |
                      +-------------------+-------------------+
                                          |
                              PostgreSQL  | Connection Pool
                                          v
                      +---------------------------------------+
                      |       NEON SERVERLESS POSTGRESQL      |
                      |   - pgvector extension enabled        |
                      |   - Region: Singapore (sin1 / ap-se)  |
                      +---------------------------------------+
```

---

## 2. Environment Variables Configuration

The following environment variables configure Stage 7 services:

```ini
# Database (Neon Serverless PostgreSQL)
DATABASE_URL=postgresql://acrevia_user:password@ep-acrevia-prod.ap-southeast-1.aws.neon.tech/acrevia_db?sslmode=require
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=5

# External Weather Provider (Open-Meteo)
WEATHER_PROVIDER_URL=https://api.open-meteo.com/v1/forecast
WEATHER_REQUEST_TIMEOUT_SECONDS=5.0
WEATHER_CACHE_MINUTES=60

# KrishiBrain Embeddings & RAG
EMBEDDING_PROVIDER=local_deterministic
EMBEDDING_DIMENSION=1536

# Security & Tokens
SECRET_KEY=production-secure-32-byte-hex-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=30
```

---

## 3. Database Migration Deployment Steps

1. **Verify Connection:**
   ```bash
   python -c "from backend.app.database.session import engine; from sqlalchemy import text; with engine.connect() as c: print(c.execute(text('SELECT 1')).scalar())"
   ```
2. **Execute Seed & Table Creation:**
   ```bash
   python -c "from backend.app.database.init_db import init_db; init_db()"
   ```
   This creates `weather_data`, `risk_rules`, `risk_assessment_records`, `risk_alerts`, `expert_profiles`, `expert_review_cases`, `expert_assessments`, `expert_assessment_revisions`, `intervention_records`, and `outcome_observations`, while automatically seeding all 6 PJTSAU risk rules.

---

## 4. Frontend Deployment on Vercel

1. **Build Verification:**
   ```bash
   cd frontend
   npm run build
   ```
2. **Deploy to Vercel:**
   ```bash
   vercel --prod --regions sin1
   ```
3. Set `NEXT_PUBLIC_API_URL` in Vercel Project Settings pointing to the FastAPI backend domain.
