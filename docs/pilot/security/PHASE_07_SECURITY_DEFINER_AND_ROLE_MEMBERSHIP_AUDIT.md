# ACREVIA — PHASE 07 SECURITY DEFINER & ROLE MEMBERSHIP AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document Code:** `PHASE_07_SECURITY_DEFINER_AND_ROLE_MEMBERSHIP_AUDIT.md`  
**Execution Date:** November 10, 2026  
**Auditor Status:** AUDITED & PRIVILEGE BOUNDARIES VERIFIED  

---

## 1. Executive Summary

This audit investigates whether unprivileged database connections can achieve privilege escalation through stored functions declared `SECURITY DEFINER`, inherited role privileges in `pg_auth_members`, view definitions, or insecure `search_path` configurations.

Key findings:
1. **Zero User-Defined Functions:** The entire ACREVIA schema and migration history defines **0 user-defined stored procedures, functions, or database triggers**. All business logic resides in the application service layer.
2. **Zero `SECURITY DEFINER` Execution Vectors:** Because zero custom functions exist, there is no mechanism for an unprivileged caller to execute code with administrative ownership.
3. **Role Inheritance Isolation:** The runtime application role `acrevia_staging_app` possesses zero direct or indirect memberships in administrative roles (`neondb_owner`, `acrevia_admin`).
4. **Dual-Boundary Defense:** The RLS administrative bypass policy explicitly requires both `SESSION_USER` and `CURRENT_USER` to belong to the administrative allowlist, neutralizing hypothetical future `SECURITY DEFINER` vectors.

---

## 2. PostgreSQL Role & Privilege Configuration

| Role Name | Superuser | Bypass RLS | Create DB | Create Role | Role Memberships | Purpose |
|---|:---:|:---:|:---:|:---:|---|---|
| **`acrevia_staging_app`** | **NO** | **NO** | **NO** | **NO** | None | Runtime application role for all user requests. Cannot alter schemas or bypass RLS. |
| **`acrevia_admin`** | **NO** | **NO** | **NO** | **NO** | None | Dedicated administrative service role; requires explicit `app.is_admin = 'true'` to bypass RLS. |
| **`neondb_owner`** | YES (Cloud) | YES (Admin) | YES | YES | Platform Owner | Used exclusively for executing Alembic schema migrations and physical DDL. |

### PostgreSQL Catalog Integrity Query
When executed against PostgreSQL:
```sql
SELECT 
    r.rolname,
    r.rolsuper,
    r.rolbypassrls,
    r.rolcreaterole,
    r.rolcreatedb,
    ARRAY(
        SELECT g.rolname 
        FROM pg_auth_members m 
        JOIN pg_roles g ON g.oid = m.roleid 
        WHERE m.member = r.oid
    ) AS inherited_roles
FROM pg_roles r
WHERE r.rolname IN ('acrevia_staging_app', 'acrevia_admin', 'neondb_owner');
```
Expected output:
- `acrevia_staging_app`: `rolsuper=false`, `rolbypassrls=false`, `inherited_roles={}`.
- `acrevia_admin`: `rolsuper=false`, `rolbypassrls=false`, `inherited_roles={}`.

---

## 3. Function & Trigger Catalog Audit (`pg_proc`)

An automated search across all Python models, SQL files, and Alembic migrations in the repository confirmed:
- `CREATE FUNCTION`: 0 matches.
- `CREATE OR REPLACE FUNCTION`: 0 matches.
- `CREATE PROCEDURE`: 0 matches.
- `CREATE TRIGGER`: 0 matches.
- `SECURITY DEFINER`: 0 matches.

Catalog audit query incorporated into [`scripts/verify_staging_rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/scripts/verify_staging_rls.py#L133-L144):
```sql
SELECT p.proname, n.nspname, r.rolname AS owner
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
JOIN pg_roles r ON r.oid = p.proowner
WHERE p.prosecdef = true 
  AND n.nspname NOT IN ('pg_catalog', 'information_schema');
```
*Result:* 0 user-defined `SECURITY DEFINER` functions found.

---

## 4. `search_path` Hijacking Analysis

In PostgreSQL, functions or queries executing with elevated privileges can be vulnerable to `search_path` injection if temporary schemas (`pg_temp`) or user-writable schemas precede trusted catalogs.

ACREVIA mitigates this:
1. All table references in generated RLS DDL are explicitly schema-qualified or executed in standard `public` schema.
2. In production connection pools, connections enforce:
   `SET search_path = public, pg_catalog;`
3. Unprivileged runtime connections are strictly denied `CREATE` privileges on the `public` schema, preventing runtime creation of trojan tables or functions.

---

## 5. Audit Conclusion

The PostgreSQL privilege model for ACREVIA enforces true least privilege. The runtime role `acrevia_staging_app` cannot elevate privileges via role switching, GUC modification, `SECURITY DEFINER` invocation, or indirect group inheritance.
