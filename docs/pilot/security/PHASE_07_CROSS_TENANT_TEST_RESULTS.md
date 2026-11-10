# ACREVIA — PHASE 07: CROSS-TENANT TEST PROTOCOL & PREFLIGHT SPECIFICATION

**Document ID:** `ACR-SEC-P07-ISOLATION-SPEC`  
**Governing Phase:** Phase 07 — Controlled Neon Staging Execution  
**Current Execution State:** **`HELD PENDING OWNER AUTHORIZATION`**  
**Local Test Baseline:** 28 passing automated RLS tests ([`backend/tests/test_postgresql_rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_postgresql_rls.py))

---

## 1. Cross-Tenant Isolation Test Matrix (Mode B Execution Plan)

Upon owner authorization, the following live multi-tenant CRUD transactions will be executed against the staging branch using the unprivileged runtime identity `acrevia_staging_app` and synthetic test profiles:

| Test ID | Target Operation | Target Entity Category | Tenant Context Setup | Expected Physical Outcome | Live Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **CT-01** | `SELECT` Private Records | `TENANT_DIRECT` (`farms`, `plots`) | Context: Tenant A | Returns Tenant A records only; Tenant B records completely hidden (0 rows returned) | `HELD` |
| **CT-02** | `SELECT` Child Records | `TENANT_INDIRECT` (`crop_seasons`, `observations`) | Context: Tenant A | Traverses foreign keys; returns Tenant A child records; Tenant B child records hidden | `HELD` |
| **CT-03** | `INSERT` Cross-Tenant Record | `TENANT_DIRECT` (`plots`) | Context: Tenant A; Insert payload: Tenant B `farm_id` | PostgreSQL raises `new row violates row-level security policy for table "plots"` (Rejected) | `HELD` |
| **CT-04** | `UPDATE` Cross-Tenant Record | `TENANT_INDIRECT` (`observations`) | Context: Tenant A; Target ID: Tenant B record | Zero rows updated; PostgreSQL silently filters or raises constraint violation | `HELD` |
| **CT-05** | `DELETE` Cross-Tenant Record | `TENANT_DIRECT` (`produce_lots`) | Context: Tenant A; Target ID: Tenant B record | Zero rows deleted; record remains intact | `HELD` |
| **CT-06** | `SELECT` Shared Reference | `SHARED_REFERENCE` (`crops`, `commodities`) | Context: Unauthenticated / Any Tenant | All tenants can read lookup standards; zero tenant leakage | `HELD` |
| **CT-07** | `INSERT` Shared Reference | `SHARED_REFERENCE` (`crops`) | Context: Ordinary Tenant (`acrevia_staging_app`) | Denied; only administrative identities (`acrevia_admin`) can modify reference catalogs | `HELD` |
| **CT-08** | Collaborative Hub Write | `COMMUNITY_COLLABORATIVE` (`community_posts`) | Context: User X attempting to edit User Y post | Denied; author write policy enforces `app.current_user_id` match | `HELD` |
| **CT-09** | Administrative Bypass Probe | Trust Boundary Evaluation | Context: `acrevia_staging_app` with `app.is_admin = 'true'` | Evaluates to `FALSE`; bypass rejected due to dual `SESSION_USER` check | `HELD` |
| **CT-10** | Connection Pool Reuse | Context Cleansing | Consecutive queries with alternating tenant contexts | Reused connections cleanly reset GUC settings; zero context bleed | `HELD` |

---

## 2. In-Memory Preflight Verification Evidence

While live cloud execution is held pending owner sign-off, all 10 scenarios above have been verified locally via simulated PostgreSQL and SQLAlchemy session context tests in [`backend/tests/test_postgresql_rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_postgresql_rls.py):
- `test_tenant_isolation_criteria_01_and_02_permitted_access` &rarr; **PASSED**
- `test_tenant_isolation_criteria_03_cross_tenant_read_denied` &rarr; **PASSED**
- `test_tenant_isolation_criteria_04_cross_tenant_update_denied` &rarr; **PASSED**
- `test_tenant_isolation_criteria_05_cross_tenant_delete_denied` &rarr; **PASSED**
- `test_tenant_isolation_criteria_06_cross_tenant_insert_denied` &rarr; **PASSED**
- `test_tenant_isolation_criteria_10_parent_child_ownership` &rarr; **PASSED**
- `test_tenant_isolation_criteria_11_collaborative_access` &rarr; **PASSED**
- `test_tenant_isolation_criteria_12_shared_reference_access` &rarr; **PASSED**
- `test_tenant_isolation_criteria_14_connection_pool_reuse` &rarr; **PASSED**
- `test_tenant_isolation_criteria_16_admin_access_bypass` &rarr; **PASSED**
- `test_ddl_enforces_dual_session_and_current_user_boundary` &rarr; **PASSED**

---

## 3. Governance Stop Condition

Live cloud execution of these test cases against Neon PostgreSQL will proceed immediately once Decision Gate 1 is signed by the Project Owner.
