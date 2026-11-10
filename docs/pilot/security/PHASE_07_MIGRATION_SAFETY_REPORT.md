# ACREVIA — PHASE 07 MIGRATION SAFETY & ROLLBACK REPORT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document Code:** `PHASE_07_MIGRATION_SAFETY_REPORT.md`  
**Execution Date:** November 10, 2026  
**Auditor Status:** VERIFIED SAFE & IDEMPOTENT  
**Migration Revision:** `a1089411c87d`  
**Predecessor Revision:** `f4894a11c87d`  

---

## 1. Migration Specification

The RLS isolation migration is defined in:
[`backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py)

- **Revision Identifier:** `a1089411c87d`
- **Down Revision:** `f4894a11c87d` (Stage 14 master schema baseline with 133 tables including Alembic version table)
- **Scope:** 132 application entities.
- **Total Executed DDL Statements:** 751 atomic SQL commands.
- **Dialect Guard:** Automatically checks `bind.dialect.name == "postgresql"`. Safely skips execution on SQLite unit tests.

---

## 2. Safety Guarantees & Invariants

| Safety Criterion | Architectural Implementation | Verification Evidence |
|---|---|---|
| **Zero Data Loss** | Migration executes `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` and `CREATE POLICY`. Zero `DROP TABLE`, `ALTER TABLE ... DROP COLUMN`, or `TRUNCATE` statements exist. | Audited in AST of `a1089411c87d`. |
| **Idempotent Re-execution** | Every policy statement is preceded by `DROP POLICY IF EXISTS <policy_name> ON <table_name>`. Partial failures can be re-run safely without name collisions. | Verified across all 751 generated statements. |
| **Clean Rollback (Downgrade)**| `downgrade()` executes `ALTER TABLE ... NO FORCE ROW LEVEL SECURITY` and `DISABLE ROW LEVEL SECURITY`. Leaves table structures and stored records completely intact. | Tested in rollback verification suite. |
| **Atomic Transactionality**| PostgreSQL supports transactional DDL. If any syntax or catalog error occurs during migration, PostgreSQL rolls back the entire migration transaction, leaving the catalog at `f4894a11c87d`. | Standard PostgreSQL transactional DDL guarantee. |
| **Zero Production Fallback** | Migration runner scripts check `is_production_url()` and strictly abort if pointing to production hosts (`ep-muddy-mode-a1nd6rrb`). | Hard stop in `scripts/verify_staging_rls.py`. |

---

## 3. Generated Statement Breakdown (132 Tables)

| Statement Type | Count | Purpose |
|---|---:|---|
| `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` | 132 | Activates row-level filtering on the relation. |
| `ALTER TABLE ... FORCE ROW LEVEL SECURITY` | 91 | Forces RLS on table owner for private tenant and user tables. |
| `DROP POLICY IF EXISTS ...` | 264 | Clears pre-existing policy versions to guarantee idempotency. |
| `CREATE POLICY ...` | 264 | Establishes base permissive and restrictive isolation policies. |
| **Total Atomic Statements** | **751** | **Complete coverage across 132 entities** |

---

## 4. Upgrade & Downgrade Execution Runbook

### Authorized Cloud Staging Upgrade (Mode B Only)
```bash
# Execute strictly as neondb_owner on isolated staging branch
STAGING_DATABASE_URL="postgresql://neondb_owner:<pwd>@ep-staging.ap-southeast-1.aws.neon.tech/neondb_staging?sslmode=require"
python -m alembic upgrade a1089411c87d
```

### Rollback (Downgrade)
```bash
# Safely disables RLS without dropping any table data
python -m alembic downgrade f4894a11c87d
```

---

## 5. Verification Conclusion

Migration `a1089411c87d` is verified safe, idempotent, non-destructive, and structurally sound.
