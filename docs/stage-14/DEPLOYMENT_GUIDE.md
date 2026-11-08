# ACREVIA Stage 14 — Production Deployment Guide

## 1. Prerequisites & Environment Setup
- **Database:** Neon PostgreSQL 16 + pgvector (Singapore `sin1`).
- **Backend Host:** FastAPI on Vercel Functions (`sin1`) with Python 3.11+.
- **Frontend Host:** Next.js 16 (App Router) on Vercel Edge Network (`sin1`).

---

## 2. Database Migrations
Run Alembic upgrade to apply Stage 14 migration:
```bash
alembic upgrade head
```
This applies `f4894a11c87d_stage14_interoperability_ecosystem.py` on top of `e3894a11c87d`, creating:
- `integration_partners`
- `partner_integrations`
- `api_applications`
- `api_credentials`
- `data_sharing_grants`
- `webhook_endpoints`
- `webhook_events`
- `webhook_deliveries`
- `data_exchange_jobs`
- `data_mapping_profiles`

---

## 3. Environment Variables
Ensure the following variables are configured in the deployment environment:
```ini
# Core Configuration
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Stage 14 Interoperability Settings
WEBHOOK_MAX_CLOCK_SKEW_SECONDS=300
DEFAULT_API_RATE_LIMIT=60
MAX_IMPORT_RECORDS_PER_JOB=10000
```
