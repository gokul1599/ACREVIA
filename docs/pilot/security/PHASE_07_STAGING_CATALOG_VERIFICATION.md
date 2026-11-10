# ACREVIA — PHASE 07: STAGING POSTGRESQL CATALOG VERIFICATION SPECIFICATION

**Document ID:** `ACR-SEC-P07-CATALOG-SPEC`  
**Governing Phase:** Phase 07 — Controlled Neon Staging Execution  
**Current Execution State:** **`HELD PENDING OWNER AUTHORIZATION`**  
**Harness Script:** [`scripts/verify_staging_rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/scripts/verify_staging_rls.py)

---

## 1. Catalog Verification Protocol

Upon owner authorization of Decision Gate 1 and successful provisioning of the isolated Neon staging branch, the verification harness will query the live PostgreSQL system catalog tables to establish physical security enforcement.

### Target System Catalog Queries

1. **`pg_class` (RLS & Force RLS Enablement):**
   ```sql
   SELECT relname, relrowsecurity, relforcerowsecurity
   FROM pg_class
   JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
   WHERE pg_namespace.nspname = 'public' AND pg_class.relkind = 'r';
   ```
2. **`pg_policies` (Policy Definitions & Roles):**
   ```sql
   SELECT tablename, policyname, permissive, roles, cmd, qual, with_check
   FROM pg_policies
   WHERE schemaname = 'public';
   ```
3. **`pg_roles` (Runtime Role Security Attributes):**
   ```sql
   SELECT rolname, rolsuper, rolbypassrls, rolcreaterole, rolcreatedb
   FROM pg_roles
   WHERE rolname = 'acrevia_staging_app';
   ```
4. **`pg_auth_members` (Administrative Role Membership Isolation):**
   ```sql
   SELECT m.rolname AS member_role, g.rolname AS granted_role
   FROM pg_auth_members am
   JOIN pg_roles m ON m.oid = am.member
   JOIN pg_roles g ON g.oid = am.roleid
   WHERE m.rolname = 'acrevia_staging_app' AND g.rolname IN ('acrevia_admin', 'neondb_owner');
   ```
5. **`pg_proc` (SECURITY DEFINER Stored Procedure Audit):**
   ```sql
   SELECT p.proname, n.nspname, r.rolname AS owner
   FROM pg_proc p
   JOIN pg_namespace n ON n.oid = p.proowner
   JOIN pg_roles r ON r.oid = p.proowner
   WHERE p.prosecdef = true AND n.nspname NOT IN ('pg_catalog', 'information_schema');
   ```

---

## 2. Expected Live Catalog Targets (132 Classified Tables)

| Metric | Target Specification | Mode A Preflight Evidence | Mode B Live Status |
| :--- | :---: | :--- | :---: |
| **Total Classified Tables** | 132 | 132 tables in `Base.metadata.tables` | `HELD` |
| **RLS Enabled Tables (`relrowsecurity = true`)** | 132 | 132 DDL blocks generated in `rls.py` | `HELD` |
| **FORCE RLS Tables (`relforcerowsecurity = true`)** | 91 | 25 Direct + 13 User + 53 Indirect tables | `HELD` |
| **Total Policies Installed** | 264 | 2 policies per table (1 base + 1 restrictive) | `HELD` |
| **Runtime Role `rolsuper`** | `false` | Specification constrained in `neon_staging_branch_spec.py` | `HELD` |
| **Runtime Role `rolbypassrls`** | `false` | Specification constrained in `neon_staging_branch_spec.py` | `HELD` |
| **Admin Role Memberships** | 0 | Specification verified | `HELD` |
| **Application `SECURITY DEFINER` Functions** | 0 | 0 functions found in repository codebase | `HELD` |

---

## 3. Current Execution Status

- **Live Remote Execution:** **NOT EXECUTED**.
- **Reason:** Project Owner Authorization Register ([`PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md)) is unsigned.
- **Next Action:** Awaiting owner sign-off on Decision Gate 1.
