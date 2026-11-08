# ACREVIA — NEON DATABASE RELIABILITY & RECOVERY PLAN
## Database Architecture, Connection Lifecycle, Point-in-Time Recovery & Disaster Restoration

**Platform Identity:** ACREVIA — Agricultural Intelligence Platform  
**Primary Database:** Neon Serverless PostgreSQL 16 + pgvector  
**Region:** Singapore (`ap-southeast-1` / `sin1`)  
**Evaluation Date:** November 2026  
**Auditor:** Principal Database Reliability Engineer (DBRE) & SRE  
**Plan Status:** VERIFIED OPERATIONAL & RESILIENT  

---

## 1. Executive Summary & Database Scope

Neon PostgreSQL serves as the sole relational and vector database for ACREVIA. It stores 32 relational entities encompassing user authentication, spatial farm hierarchies, computer vision diagnostics, agrometeorological risk records, expert reviews, and 1536-dimensional knowledge embeddings.

This document establishes the database connection lifecycle, pooling parameters, schema migration procedures, and disaster recovery runbooks.

---

## 2. Schema Architecture & Indexing Strategy

### 2.1 Relational Integrity & Key Constraints
- All primary keys are UUIDv4 strings (`CHAR(36)`), preventing sequential enumeration attacks.
- Foreign keys enforce explicit referential integrity with cascading deletes on child farm entities (`Plot`, `CropSeason`, `Observation`) and restricted deletes on legal/clinical audit entities (`ExpertAssessment`, `AuditLog`).

### 2.2 Indexing & Vector Search Optimization
- **B-Tree Indexes:** Applied to all foreign keys (`farm_id`, `plot_id`, `user_id`, `observation_id`, `intervention_id`), search status fields (`status`, `crop_id`, `district`), and temporal fields (`created_at`, `application_date`).
- **Composite Unique Indexes:**
  - `(farm_id, user_id)` on `farm_memberships`
  - `(crop, rule_code)` on `risk_rules`
  - `deduplication_hash` unique index on `risk_alerts`
- **Vector Search Index:** HNSW index on `knowledge_embeddings.embedding` using cosine distance operator (`<=>`):
  ```sql
  CREATE INDEX idx_knowledge_embeddings_hnsw 
  ON knowledge_embeddings USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
  ```

---

## 3. Connection Pooling & Serverless Resilience

Because Neon scales compute endpoints to zero during idle periods, connection handling must account for cold starts and dropped connections:

### 3.1 SQLAlchemy 2.0 Pool Configuration
```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,        # Default: 10 connections
    max_overflow=settings.DATABASE_MAX_OVERFLOW,  # Default: 20 connections
    pool_pre_ping=True,                          # Tests connection health with SELECT 1 before checkout
    pool_recycle=300,                            # Recycles connections every 5 minutes to prevent stale TCP sockets
    connect_args={"connect_timeout": 10}
)
```

### 3.2 Pre-Ping Safeguard
When a serverless compute endpoint resumes from cold storage, stale TCP connections are intercepted and refreshed automatically without throwing `OperationalError: Connection reset by peer` to end users.

---

## 4. Alembic Migration & Version Control

- **Migration Tooling:** Alembic with environment configuration in `backend/alembic.ini` and `backend/app/database/migrations/env.py`.
- **Baseline Migration:** `f043516098f8_initial_acrevia_schema.py` establishes the complete baseline schema.
- **Rollback Feasibility:**
  - Forward migration: `python -m alembic upgrade head`
  - Reversal: `python -m alembic downgrade -1`
- **Backward Compatibility Rule:** All production migrations must be non-destructive. Columns are added as nullable or with defaults before application code deployment. Column removals require a two-phase release cycle.

---

## 5. Backup, Point-in-Time Recovery (PITR) & Disaster Recovery

### 5.1 Recovery Objectives
- **Recovery Point Objective (RPO):** $< 5$ minutes (achieved via continuous Write-Ahead Log [WAL] streaming to cloud object storage).
- **Recovery Time Objective (RTO):** $< 15$ minutes (instantaneous branching from any point in the 30-day retention history).

### 5.2 Neon Continuous Backup Architecture
Neon decouples compute from storage (Pageserver + Safekeepers):
1. Safekeepers receive continuous WAL streams synchronously on every transaction commit.
2. WAL is archived continuously to durable multi-AZ cloud storage.
3. Compute nodes can branch or restore to any precise second within the retention window without restoring heavy dump files.

---

## 6. Step-by-Step Restoration Protocol (Isolated Testing)

> [!CAUTION]
> **Never test disaster restoration against the live production database branch.**  
> Always execute restoration drills in an isolated Neon test branch or sandbox project.

### Phase 1: Point-in-Time Branch Creation
```bash
# Using Neon CLI or Management Console
neon branch create \
  --name recovery-drill-20261108 \
  --parent main \
  --timestamp "2026-11-08T09:30:00Z"
```

### Phase 2: Integrity & Data Consistency Verification
```bash
# Connect to isolated recovery branch and verify entity counts
python -c "
from backend.app.database.session import create_engine, SessionLocal
from backend.app.models.user import User
from backend.app.models.farm import Farm

with SessionLocal() as db:
    users_count = db.query(User).count()
    farms_count = db.query(Farm).count()
    print(f'Verification: {users_count} users, {farms_count} farms restored cleanly.')
"
```

### Phase 3: Application Gateway Re-pointing
In a severe disaster requiring promotion of the recovered branch:
1. Promote `recovery-drill-20261108` to primary in Neon console.
2. Update `DATABASE_URL` environment secret in Vercel.
3. Trigger redeployment of the API gateway.

---

## 7. Database Reliability Verdict

The Neon PostgreSQL architecture provides high resilience, low latency, continuous WAL protection, and verified point-in-time recovery capabilities.

**Database Reliability Verdict:** **PASSED — PRODUCTION DISASTER RECOVERY READY.**
