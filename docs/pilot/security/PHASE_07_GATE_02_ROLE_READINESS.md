# ACREVIA — PHASE 07: GATE-02 DATABASE ROLE & PERMISSION READINESS
## Least-Privilege Role Architecture, Administrative Boundary & Local SQL Audit

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document ID:** `ACR-SEC-P07-GATE02-ROLE-READINESS`  
**Governing Phase:** Phase 07 — Controlled Mode B Infrastructure Operations  
**Target Gate:** GATE-02 — Database Roles and Least-Privilege Permissions  
**Release Date:** November 10, 2026  
**Security Classification:** RESTRICTED — PILOT GOVERNANCE & ARCHITECTURAL AUDIT  
**Gate Readiness State:** **`LOCAL_PREPARATION_COMPLETE / AWAITING_GATE_02_AUTHORIZATION`**  
**Execution Status:** **`STRICTLY UNEXECUTED ON CLOUD`**  

---

## 1. Executive Summary

GATE-02 governs the creation and least-privilege configuration of database roles on the isolated Neon staging branch (`staging-rls-phase07`).

Under PostgreSQL Row-Level Security architecture, the enforcement of RLS policies depends entirely on the privileges and attributes of the connecting database user. If an application connects using a role with `SUPERUSER` or `BYPASSRLS`, PostgreSQL completely bypasses all RLS policies, rendering tenant isolation moot.

This dossier provides the exhaustive local engineering preparation for GATE-02, establishing:
1. The three-tier role separation model (`acrevia_staging_app`, `acrevia_admin`, `neondb_owner`).
2. The exact privilege grants required on schemas, tables, sequences, and functions.
3. The non-negotiable list of prohibited privileges.
4. An audit of the hardened administrative trust boundary (`ADMIN_BYPASS_SQL`).
5. Connection-pool cleansing behavior (`RESET ALL`) to eliminate cross-request context bleeding.
6. A local SQL review template ready for execution once GATE-02 is genuinely authorized.

---

## 2. Role Separation & Responsibility Matrix

ACREVIA strictly decouples application runtime execution from administrative migration workflows:

| Role Identifier | Role Purpose & Classification | Login Allowed | Superuser | Bypass RLS | Create Role / DB | Inherit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`acrevia_staging_app`** | Runtime application role used by FastAPI database pool | **YES** | **`false`** | **`false`** | **`false`** | **`false`** |
| **`acrevia_admin`** | **`POLICY_AUTHORIZED_ADMINISTRATIVE_ROLE`** (Subject to RLS; authorized via policy expression) | **YES** | **`false`** | **`false`** | **`false`** | **`false`** |
| **`neondb_owner`** | Neon branch owner; used strictly for applying Alembic DDL migrations | **YES** | **`false`** | **`true`** *(Neon default)* | **`true`** | **`true`** |

### Core Architectural Invariants:
1. **Application Separation:** The application runtime (`acrevia_staging_app`) MUST NEVER connect as `neondb_owner`.
2. **No Membership Leakage:** `acrevia_staging_app` MUST NOT be granted membership in `neondb_owner` or `acrevia_admin`.
3. **Dedicated Admin Session:** Administrative operations requiring `ADMIN_BYPASS_SQL` evaluation must connect directly as `acrevia_admin` and explicitly execute `SET LOCAL app.is_admin = 'true'`.
4. **Credential Trust Boundary:** The custom GUC parameter `app.is_admin = 'true'` is an **additional policy predicate condition**, NOT a second authentication factor. Cryptographic authentication relies solely on `acrevia_admin` database credentials; any session connected as `acrevia_admin` can execute `SET app.is_admin = 'true'`.
5. **Separation of Application Admin vs. Database Role:** Application-level administrator status (`role_id = 'ADMIN'` in JWT and `user_roles`) is handled at the application routing layer. Normal admin web requests still connect through the unprivileged `acrevia_staging_app` pool. Only dedicated administrative backend workers use the `acrevia_admin` database user.

---

## 3. Privilege Matrix & DDL Specification

### A. Grants Required for `acrevia_staging_app`
```sql
-- Schema Usage
GRANT USAGE ON SCHEMA public TO acrevia_staging_app;

-- Table DML Permissions (Subject to RLS filtering)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO acrevia_staging_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO acrevia_staging_app;

-- Sequence Permissions (For auto-increment IDs)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO acrevia_staging_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO acrevia_staging_app;

-- Function Execution Permissions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO acrevia_staging_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO acrevia_staging_app;
```

### B. Privileges that MUST NEVER Be Granted to `acrevia_staging_app`
- ❌ **`SUPERUSER`:** Grants total bypass of all PostgreSQL security checks.
- ❌ **`BYPASSRLS`:** Instructs PostgreSQL to ignore row-level security policies.
- ❌ **`CREATEDB` / `CREATEROLE`:** Allows privilege escalation and schema tampering.
- ❌ **`DROP TABLE` / `TRUNCATE`:** Prevents catastrophic data destruction.
- ❌ **`GRANT acrevia_admin TO acrevia_staging_app`:** Prevents role escalation.

---

## 4. Administrative Trust-Boundary Audit

In [`backend/app/database/rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py), the administrative bypass expression is codified as:

```sql
(
    SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
    AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
    AND current_setting('app.is_admin', true) = 'true'
)
```

### Threat Evaluation & Mitigations:
1. **Unprivileged GUC Manipulation:**  
   If an attacker or unprivileged tenant issues `SET LOCAL app.is_admin = 'true'`, the expression evaluates to `FALSE` because `SESSION_USER` and `CURRENT_USER` evaluate to `'acrevia_staging_app'`, which is excluded from the allowlist.
2. **`SECURITY DEFINER` Exploit Prevention:**  
   If an application procedure owned by `acrevia_admin` runs as `SECURITY DEFINER`, `CURRENT_USER` becomes `acrevia_admin`, but `SESSION_USER` remains `acrevia_staging_app`. The dual condition requires **both** to match, preventing privilege hijacking.
3. **Fail-Safe Defaults:**  
   The second parameter in `current_setting('app.is_admin', true)` ensures that if the GUC is unset or null, PostgreSQL returns `NULL` rather than raising a fatal error, evaluating the clause safely to `FALSE`.

---

## 5. Connection-Pool Context Cleansing & Session Lifecycle

In FastAPI, SQLAlchemy connection pools reuse physical connections across asynchronous requests. If tenant context variables persist on a checked-in connection, subsequent requests from a different tenant could inherit foreign context.

### Cleansing Implementation:
In [`backend/app/database/session.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/session.py) and [`backend/app/database/rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py):
1. **Session Initialization:** Every request executes `set_tenant_context(session, tenant_id, user_id, is_admin)`.
2. **Transactional Scope:** Settings are applied via `SET LOCAL` so that transaction commit or rollback automatically discards the configuration.
3. **Session Teardown:** The session teardown listener executes `DISCARD ALL` or `RESET ALL` upon connection return to the pool:
   ```sql
   RESET app.current_tenant_id;
   RESET app.current_user_id;
   RESET app.is_admin;
   ```
4. **Offline Test Verification:** Verified in `backend/tests/test_postgresql_rls.py` (`test_tenant_isolation_criteria_13_rollback_clears_context` and `test_tenant_isolation_criteria_14_connection_pool_reuse`) and `backend/tests/test_rls_policy_semantics.py` (`test_farm_access_unauthorized_clears_candidate_context`).
5. **Fail-Closed Context Execution Guarantee:** Under PostgreSQL, `set_tenant_context()` enforces fail-closed semantics: any failure during `set_config` triggers an immediate session rollback and raises `RuntimeError`, preventing any subsequent query from executing in an uninitialized or unauthenticated state. Verified in `test_missing_guc_fails_closed`.

---

## 6. Pre-Execution Checklist for GATE-02

Before executing GATE-02 on Neon Cloud:
- [ ] GATE-01 is complete; staging branch `staging-rls-phase07` is active and reachable.
- [ ] Decision Gate 2 is explicitly approved and signed in [`PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md).
- [ ] `NEON_API_KEY` is present with role creation permissions.
- [ ] Pre-creation role inspection confirms `acrevia_staging_app` does not already exist.

---

## 7. Execution Commands for Authorized Operator (On Hold)

Once GATE-02 is formally authorized by the Project Owner:
```bash
# Step 1: Create unprivileged application runtime role
neon roles create --branch staging-rls-phase07 --name acrevia_staging_app

# Step 2: Create administrative bypass role
neon roles create --branch staging-rls-phase07 --name acrevia_admin

# Step 3: Verify role attributes via psql (neondb_owner connection)
psql "$STAGING_DATABASE_URL" -c "
SELECT rolname, rolsuper, rolbypassrls, rolcreaterole, rolcreatedb 
FROM pg_roles 
WHERE rolname IN ('acrevia_staging_app', 'acrevia_admin');"

# Step 4: Verify zero administrative memberships
psql "$STAGING_DATABASE_URL" -c "
SELECT m.rolname AS member, g.rolname AS granted 
FROM pg_auth_members am
JOIN pg_roles m ON m.oid = am.member
JOIN pg_roles g ON g.oid = am.roleid
WHERE m.rolname = 'acrevia_staging_app';"
```

---

## 8. Failure and Recovery Protocol

If role provisioning fails:
1. **Do not proceed to GATE-03 (Migration).**
2. If role creation fails due to naming collision, verify existing role attributes. If attributes deviate from `NOSUPERUSER, NOBYPASSRLS`, drop and recreate the role.
3. If permissions are misapplied, re-run schema privilege reset script.
4. Record all error traces in `PHASE_07_GATE_02_ROLE_READINESS.md`.

---

## 9. Seeded Application Role Constants vs. Database Roles

ACREVIA establishes a strict distinction between PostgreSQL database roles and application-level domain roles:

### Seeded System Roles
The authoritative roles seeded in `backend/app/database/init_db.py` and defined in `backend/app/security/permissions.py` (`SystemRole` enum) are strictly:
1. `FARMER`: Smallholder farm operators. Bound by tenant isolation to owned farms and personal records.
2. `AGRICULTURAL_EXPERT`: Agronomists and extension specialists. Authorized to author community advisories and contribute knowledge entities.
3. `RESEARCHER`: Academic and institutional researchers. Authorized to evaluate aggregated data and knowledge graphs.
4. `ADMIN`: System operations administrators.

> [!NOTE]
> Historical narrative audit references to `'EXPERT'` and `'EXTENSION_OFFICER'` were non-conforming aliases. All RLS policy expressions in `backend/app/database/rls.py` have been aligned to require `ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')`.

---

## 10. Background Worker Security Architecture (Option A)

Asynchronous workers executing outside user HTTP requests (e.g., RiskCast batch risk scoring in `backend/app/tasks/run_riskcast_batch.py`) adhere to strict least-privilege principles:

1. **Unprivileged Connection:** Workers connect to PostgreSQL using `acrevia_staging_app`. They **do not** connect as `acrevia_admin` or `neondb_owner`.
2. **Tenant Scoping (Option A):** Workers iterate through active tenant IDs and execute individual evaluations inside dedicated sessions:
   ```python
   set_tenant_context(session, tenant_id=farm_id, user_id=owner_id, is_admin=False)
   try:
       # Tenant-isolated evaluation logic
       ...
       session.commit()
   finally:
       clear_tenant_context(session)
   ```
3. **No Connection Leakage:** The unconditional `finally:` block clears tenant GUC parameters prior to returning the database connection to the SQLAlchemy pool, preventing cross-tenant context bleed. Verified in `backend/tests/test_worker_security_and_privacy.py`.
