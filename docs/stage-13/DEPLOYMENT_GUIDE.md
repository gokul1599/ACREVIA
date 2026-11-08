# ACREVIA — Deployment and Operations Guide (Stage 13)

**Project:** ACREVIA — Agricultural Intelligence Platform  
**Stage:** 13 — Climate-Resilient & Sustainable Agriculture  
**Target Environment:** Neon PostgreSQL 16 (`sin1`) + Vercel Global Edge & Functions  

---

## 1. Pre-Deployment Readiness Checklist

Before applying the Stage 13 release to production, ensure:
1. **Neon Connection String:** Ensure `DATABASE_URL` uses the pooled connection endpoint (`-pooler.ap-southeast-1.aws.neon.tech`) for Vercel serverless functions.
2. **Database Backup:** Create a point-in-time restore branch on Neon console prior to running migrations.
3. **Institutional Standards Verification:** Confirm PJTSAU 2026 critical values and IPCC 2019 refinement factors are bundled.

---

## 2. Database Migration Execution

Stage 13 introduces tables via Alembic revision `e3894a11c87d`:

```bash
# Activate virtual environment
source .venv/bin/activate  # On Linux/macOS
# or .venv\Scripts\activate on Windows

# Check current migration revision
alembic current

# Execute migration to head
alembic upgrade head

# Verify table creation in PostgreSQL
# Tables: soil_profiles, soil_samples, soil_test_results, water_sources, 
# irrigation_events, water_balance_snapshots, soil_moisture_observations,
# climate_baselines, climate_exposure_assessments, nutrient_assessments,
# nutrient_expert_reviews, agricultural_practice_definitions, farm_practice_records,
# soil_carbon_measurements, environmental_accounting_estimates, resilience_assessments
```

---

## 3. Seed Canonical Data

To populate baseline climate normals and sustainable practice definitions:

```bash
# Seed standard practice taxonomy and PJTSAU baseline datasets
python -m backend.app.database.seed_stage13
```

---

## 4. Rollback Strategy

In the event of an operational anomaly:
```bash
# Rollback migration by 1 revision
alembic downgrade -1

# Redeploy previous Vercel deployment via Vercel CLI or dashboard
vercel rollback
```
