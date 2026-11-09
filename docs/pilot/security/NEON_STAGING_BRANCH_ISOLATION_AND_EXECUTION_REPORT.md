# ACREVIA — NEON STAGING BRANCH ISOLATION & EXECUTION REPORT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Environment:** Isolated Neon Staging Database Branch  
**Target Region:** Singapore (`aws-ap-southeast-1` / `sin1`)  
**Security Standard:** Strict Non-Production Isolation & Role Separation  
**Date:** November 9, 2026

---

## 1. Staging Branch Purpose & Architecture

The Neon staging branch `staging-rls-phase05` is specifically designed to validate PostgreSQL Row-Level Security (RLS) policies, Alembic migration `a1089411c87d`, and cross-tenant isolation under real PostgreSQL database engine semantics without endangering the live production database (`ep-muddy-mode-a1nd6rrb-pooler.ap-southeast-1.aws.neon.tech`).

### Isolation Topology:
```
+-----------------------------------------------------------------------------------+
| NEON POSTGRESQL CLOUD PROJECT                                                     |
|                                                                                   |
|  [Production Branch: main] (ep-muddy-mode-a1nd6rrb...)                           |
|    - Status: STRICTLY PROTECTED (Zero DDL, Zero non-authorized migrations)        |
|    - Farmer data: Zero                                                            |
|                                                                                   |
|  [Isolated Staging Branch: staging-rls-phase05] (CREATED ONLY ON OWNER SIGN-OFF) |
|    - Database: neondb_staging                                                     |
|    - Data Scope: Synthetic agronomic profiles only                                |
|    - Migration Role: neondb_owner (Applies DDL a1089411c87d)                      |
|    - Runtime Role: acrevia_staging_app (NOSUPERUSER, NOBYPASSRLS)                 |
+-----------------------------------------------------------------------------------+
```

---

## 2. Authorization Gate for Remote Branch Creation

In accordance with Section 4 and Section 8 of the Phase 05 Master Prompt, creating external cloud resources requires explicit, separate project owner authorization.

- **Gate Status:** `BLOCKED_OWNER_AUTHORIZATION`
- **Owner Action Required:** Formal sign-off on the dedicated decision gate for remote Neon branch creation in `docs/pilot/security/PHASE_05_OWNER_INPUT_AND_APPROVAL_CHECKLIST.md`.
- **Engineering Safety Guarantee:** No remote branches or database modifications were triggered in Phase 05. All tooling, specifications, and automated verification scripts were prepared locally in a non-destructive state.

---

## 3. Database Roles and Privilege Boundary

| Role Name | Scope | `SUPERUSER` | `BYPASSRLS` | Permitted Commands |
| :--- | :--- | :---: | :---: | :--- |
| **`neondb_owner`** | Migration Execution | Yes | Yes | `CREATE TABLE`, `ALTER TABLE`, `CREATE POLICY`, `DROP POLICY` |
| **`acrevia_staging_app`** | Application Runtime | **NO** | **NO** | `SELECT`, `INSERT`, `UPDATE`, `DELETE` (Subject to RLS filtering) |

### Runtime Role Hardening SQL:
```sql
-- Role creation on isolated staging branch
CREATE ROLE acrevia_staging_app WITH LOGIN PASSWORD 'STAGING_SECURE_PASSWORD'
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    NOINHERIT
    NOREPLICATION
    NOBYPASSRLS;

-- Grant standard DML privileges on public schema
GRANT USAGE ON SCHEMA public TO acrevia_staging_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO acrevia_staging_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO acrevia_staging_app;
```

---

## 4. Verification & Safety Tooling

Two standalone automation scripts have been implemented:
1. `scripts/neon_staging_branch_spec.py`:
   - Enforces branch naming convention (`staging-rls-phase05`).
   - Validates non-production host indicators.
   - Outputs the exact Neon CLI / API sequence for deployment.
2. `scripts/verify_staging_rls.py`:
   - Inspects `pg_class.relrowsecurity` and `pg_class.relforcerowsecurity`.
   - Inspects `pg_policies` and verifies `pg_roles` does not possess `BYPASSRLS`.
   - Automatically aborts with exit code 1 if a production host string (`ep-muddy-mode-a1nd6rrb...`) is detected.

---

## 5. Cleanup and Lifecycle Management

Upon completion of Phase 05 physical integration tests on the staging branch:
```bash
neon branches delete staging-rls-phase05 --project-id <PROJECT_ID>
```
This guarantees zero residual infrastructure footprint and zero ongoing cloud costs.
