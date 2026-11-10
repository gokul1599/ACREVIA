# ACREVIA — PHASE 07: GATE-03 RLS MIGRATION READINESS
## Migration Implementation, 132-Entity Inventory & Downgrade Risk Audit

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document ID:** `ACR-SEC-P07-GATE03-MIGRATION-READINESS`  
**Governing Phase:** Phase 07 — Controlled Mode B Infrastructure Operations  
**Target Gate:** GATE-03 — Physical PostgreSQL RLS Migration Execution  
**Target Migration:** `a1089411c87d` (`enable_postgresql_rls_tenant_isolation`)  
**Down Revision:** `f4894a11c87d`  
**Release Date:** November 10, 2026  
**Security Classification:** RESTRICTED — PILOT GOVERNANCE & ARCHITECTURAL AUDIT  
**Gate Readiness State:** **`LOCAL_PREPARATION_COMPLETE / AWAITING_GATE_03_AUTHORIZATION`**  
**Execution Status:** **`STRICTLY UNEXECUTED ON CLOUD`**  

---

## 1. Executive Summary

GATE-03 governs the physical application of Alembic migration `a1089411c87d` to the isolated staging database (`neondb_staging` on `staging-rls-phase07`).

This migration is the architectural milestone where ACREVIA transitions from application-only filtering to database kernel-enforced multi-tenant isolation across all 132 database entities registered in SQLAlchemy metadata.

This dossier establishes:
1. Full reconciliation of the 132-entity RLS inventory and category breakdown.
2. The mathematical validation of the 767 atomic DDL statements.
3. Dialect safety guards and non-destructive execution guarantees.
4. PostgreSQL engine compatibility analysis.
5. The **Critical Downgrade Warning**: why Alembic downgrade de-escalates security and must never be triggered automatically.
6. A reproducible pre-migration and post-migration validation checklist.

---

## 2. Migration Chain & Source Implementation Inspection

### A. Alembic Revision Chain
Inspection of [`backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py):
- **Revision ID:** `a1089411c87d`
- **Down Revision:** `f4894a11c87d`
- **Linearity:** Cleanly connects to previous schema version `f4894a11c87d` with zero divergent branch labels.

### B. Dialect Guard Verification
Line 24:
```python
bind = op.get_bind()
if bind.dialect.name != "postgresql":
    print(f"[RLS Migration] Current dialect is '{bind.dialect.name}'. Skipping PostgreSQL RLS DDL execution.")
    return
```
- **Safety Guarantee:** If offline unit tests run against SQLite, this guard cleanly intercepts execution, preventing syntax errors while preserving test execution integrity.

---

## 3. Entity Classification & 767 DDL Statement Reconciliation

An exhaustive audit of `Base.metadata.tables` and [`backend/app/database/rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py) confirms the exact inventory:

| Classification Category | Entity Count | Security Semantic | `ENABLE RLS` | `FORCE RLS` | Drop Policy | Create Policy | Total DDL |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **`TENANT_DIRECT`** | **25** | Direct `farm_id` match to tenant context | 25 | 25 | 50 | 50 | 150 |
| **`USER_OWNED`** | **13** | Direct `user_id` match to user context | 13 | 13 | 26 | 26 | 78 |
| **`TENANT_INDIRECT`** | **53** | FK traversal to parent entity matching tenant | 53 | 53 | 106 | 106 | 318 |
| **`SHARED_REFERENCE` (Public)** | **22** | Permissive `SELECT (true)`; Admin write bypass only | 22 | 0 | 44 | 44 | 110 |
| **`SHARED_REFERENCE` (Admin/Private)** | **3** | Sensitive operational/partner configs; Admin bypass only | 3 | 3 | 6 | 3 | 15 |
| **`COMMUNITY_COLLABORATIVE`** | **16** | Public/scoped `SELECT`; Author ownership write only | 16 | 16 | 32 | 32 | 96 |
| **TOTAL** | **132** | **100% Coverage of Project Tables** | **132** | **110** | **264** | **261** | **767** |

### Reconciliation of `produce_quality_profiles` and Category Clarifications:
- `produce_quality_profiles` stores national AGMARK crop grading standards.
- Possesses no `farm_id`, no `user_id`, and zero links to private tenant data.
- Correctly classified as **`SHARED_REFERENCE` (Public)** (within the 22 public reference tables).
- Within `SHARED_REFERENCE`, three sensitive operational/partner tables (`partner_integrations`, `integration_partners`, `ingestion_jobs`) are classified as `ADMINISTRATIVE` / `PRIVATE_OPERATIONAL` with `FORCE RLS` and zero public read permissions.
- All 16 `COMMUNITY_COLLABORATIVE` tables enforce `FORCE RLS` and row-level author ownership isolation (`author_col = current_user_id`).
- Explains why `FORCE RLS` count is exactly **110**:
  $$\text{FORCE RLS Tables} = 25\ (\text{Direct}) + 13\ (\text{User}) + 53\ (\text{Indirect}) + 3\ (\text{Sensitive Reference}) + 16\ (\text{Collaborative}) = \mathbf{110}$$
- Total installed policies: 50 + 26 + 106 + 44 + 3 + 32 = **261 created policies** (and 264 dropped during idempotent pre-cleanup).

---

## 4. PostgreSQL Engine Compatibility

ACREVIA targets **PostgreSQL 15+** on Neon Serverless Cloud:
- **`ENABLE ROW LEVEL SECURITY`:** Supported natively since PostgreSQL 9.5.
- **`FORCE ROW LEVEL SECURITY`:** Supported natively since PostgreSQL 9.5 (ensures table owners are bound by RLS policies).
- **`AS RESTRICTIVE` Policies:** Supported natively since PostgreSQL 10.0 (enables combining permissive baseline access with strict tenant filtering via logical `AND`).
- **Subquery Foreign-Key Traversal:** The `EXISTS (SELECT 1 FROM parent WHERE ...)` clauses used in `TENANT_INDIRECT` policies are standard SQL conforming to PostgreSQL subquery optimization rules.

---

## 5. Critical Downgrade Warning & Security De-escalation

Inspection of `downgrade()` in migration `a1089411c87d`:
```python
def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    for table_name, meta in TABLE_CLASSIFICATION.items():
        category = meta.get("category")
        if category in (TableCategory.TENANT_DIRECT, TableCategory.USER_OWNED, TableCategory.TENANT_INDIRECT, TableCategory.COMMUNITY_COLLABORATIVE):
            op.execute(sa.text(f"ALTER TABLE {table_name} NO FORCE ROW LEVEL SECURITY;"))
        op.execute(sa.text(f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY;"))
```

### Architectural Risk Analysis:
1. **Security De-escalation:**  
   Executing `DISABLE ROW LEVEL SECURITY` instructs the database engine to stop enforcing policies. Multi-tenant isolation immediately falls back to application-layer code only.
2. **Dormant Policy Retention:**  
   Downgrade does **not** drop policy definitions from `pg_policies`; they remain stored but inactive.
3. **MANDATORY POLICY: FREEZE ON FAILURE, NEVER AUTO-DOWNGRADE:**  
   If migration execution or subsequent validation tests fail, operators must **NEVER** trigger an automatic Alembic downgrade. Automatic downgrade obscures the failure state and strips away database protection. The staging database must be frozen for forensic triage.

---

## 6. Pre-Migration Checklist (GATE-03)

Before executing `alembic upgrade a1089411c87d` on Neon:
- [ ] GATE-01 complete; staging branch active.
- [ ] GATE-02 complete; runtime roles `acrevia_staging_app` and `acrevia_admin` verified.
- [ ] Decision Gate 3 approved and signed in [`PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md).
- [ ] Target connection URL confirmed pointing to `neondb_staging` (never production `ep-muddy-mode-a1nd6rrb`).
- [ ] Connection established as `neondb_owner` (migration DDL requires owner/DDL privileges).

---

## 7. Execution Commands for Authorized Operator (On Hold)

Once GATE-03 is formally authorized:
```bash
# Step 1: Confirm current Alembic revision is f4894a11c87d
alembic current

# Step 2: Apply RLS migration in a single transactional block
alembic upgrade a1089411c87d

# Step 3: Verify migration status in alembic_version table
psql "$STAGING_DATABASE_URL" -c "SELECT version_num FROM alembic_version;"

# Step 4: Verify RLS enablement across all 132 tables
psql "$STAGING_DATABASE_URL" -c "
SELECT count(*) AS rls_enabled_tables 
FROM pg_class c 
JOIN pg_namespace n ON n.oid = c.relnamespace 
WHERE n.nspname = 'public' AND c.relrowsecurity = true;"

# Step 5: Verify FORCE RLS across exactly 110 tables
psql "$STAGING_DATABASE_URL" -c "
SELECT count(*) AS force_rls_tables 
FROM pg_class c 
JOIN pg_namespace n ON n.oid = c.relnamespace 
WHERE n.nspname = 'public' AND c.relforcerowsecurity = true;"

# Step 6: Verify total installed policies equals 261
psql "$STAGING_DATABASE_URL" -c "
SELECT count(*) AS installed_policies 
FROM pg_policies 
WHERE schemaname = 'public';"
```

---

## 8. Failure Handling & Triage Protocol

If `alembic upgrade a1089411c87d` fails:
1. Capture PostgreSQL error logs and failed statement line.
2. Confirm Alembic rolled back the transaction cleanly.
3. Freeze the staging branch in place.
4. Record forensic findings in `PHASE_07_GATE_03_MIGRATION_READINESS.md`.
5. Do NOT execute `downgrade()` or delete the staging branch without owner review.
