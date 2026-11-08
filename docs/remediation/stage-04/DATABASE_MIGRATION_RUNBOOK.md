# ACREVIA — DATABASE MIGRATION RUNBOOK
## PRODUCTION MIGRATION PROCEDURES, SAFETY GATES & ROLLBACK PROTOCOLS
**Document:** `DATABASE_MIGRATION_RUNBOOK.md`  
**Classification:** Standard Operating Procedure (SOP)  
**Date:** 2026-11-08  
**Target:** Neon PostgreSQL 18.6 & Alembic CLI  

---

## 1. PRE-MIGRATION GATES & SAFETY CHECKLIST

Before executing any database migration in staging or production:
1. **Approval Gate:** Explicit human authorization from the Lead Database Reliability Engineer is mandatory.
2. **Neon Point-in-Time Restore (PITR):** Confirm Neon snapshot or branching point is recorded.
3. **Database Identity Check:** Verify connection string points to expected database (prevent accidental migrations against production during local testing):
   ```bash
   python -c "from backend.app.core.config import settings; print('Target DB host:', settings.DATABASE_URL.split('@')[-1])"
   ```
4. **Current Revision Inspection:** Verify current version in target database:
   ```bash
   alembic current
   ```

---

## 2. STANDARD MIGRATION WORKFLOW

### Step 1: Model Updates
Update or declare SQLAlchemy 2.0 ORM models in `backend/app/models/`.

### Step 2: Generate Migration Candidate
```bash
alembic revision --autogenerate -m "descriptive_migration_name"
```

### Step 3: DDL Code Review
Inspect the generated file in `backend/app/database/migrations/versions/`:
- Ensure all `op.create_table()` or `op.add_column()` calls include explicit `nullable=False` default strategies.
- Verify indexes and foreign key constraints.
- Implement explicit reversible operations in `downgrade()`.

### Step 4: Staging / Test Verification
Apply migration against an isolated staging PostgreSQL container:
```bash
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

### Step 5: Production Execution
Run migration as a standalone, isolated deployment step:
```bash
alembic upgrade head
```

---

## 3. EMERGENCY ROLLBACK PROCEDURE

If a migration encounters an operational bottleneck or lock contention:
1. Terminate running migration transaction.
2. If reversible DDL was applied:
   ```bash
   alembic downgrade -1
   ```
3. If data loss risk exists or DDL is irreversible:
   - Restore database branch from Neon PITR snapshot.
   - Re-point application connection pooling to restored branch.
