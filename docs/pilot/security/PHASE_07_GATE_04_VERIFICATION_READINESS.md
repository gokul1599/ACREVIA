# ACREVIA — PHASE 07: GATE-04 RLS VERIFICATION & TEST READINESS
## Verification Harness, 10 Cross-Tenant Scenarios & Catalog Probe Protocol

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document ID:** `ACR-SEC-P07-GATE04-VERIFICATION-READINESS`  
**Governing Phase:** Phase 07 — Controlled Mode B Infrastructure Operations  
**Target Gate:** GATE-04 — Staging RLS Verification and Cross-Tenant Testing  
**Harness Script:** [`scripts/verify_staging_rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/scripts/verify_staging_rls.py)  
**Test Suite:** [`backend/tests/test_postgresql_rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_postgresql_rls.py)  
**Release Date:** November 10, 2026  
**Security Classification:** RESTRICTED — PILOT GOVERNANCE & ARCHITECTURAL AUDIT  
**Gate Readiness State:** **`LOCAL_PREPARATION_COMPLETE / AWAITING_GATE_04_AUTHORIZATION`**  
**Execution Status:** **`STRICTLY UNEXECUTED ON CLOUD`**  

---

## 1. Executive Summary

GATE-04 governs the physical execution of automated Row-Level Security verification probes against the live Neon staging database endpoint.

The verification process consists of two complementary layers:
1. **Catalog Integrity Audit:** Querying PostgreSQL system catalogs (`pg_class`, `pg_policies`, `pg_roles`, `pg_auth_members`) to prove that 132 tables have RLS enabled, 110 have `FORCE RLS`, 261 policies are registered, and runtime role `acrevia_staging_app` is unprivileged.
2. **Active Cross-Tenant CRUD Probes:** Executing multi-tenant transactions using `acrevia_staging_app` across 10 cross-tenant (CT) scenarios to verify that cross-tenant reads return 0 rows, cross-tenant inserts fail, cross-tenant updates/deletes affect 0 rows, and shared catalogs function correctly.

This dossier establishes the full test inventory, coverage matrix, safe local test evidence, and the forensic protocol for live execution.

---

## 2. Test Inventory & Evidential Classification

The repository maintains an exhaustive suite of 28 automated RLS tests in `backend/tests/test_postgresql_rls.py`:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          28 AUTOMATED RLS TESTS                             │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ Group                    │ Functions & Scope                                │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ Classification & DDL (7) │ test_complete_table_classification_coverage      │
│                          │ test_table_classification_categories             │
│                          │ test_generate_rls_ddl_tenant_direct              │
│                          │ test_generate_rls_ddl_user_owned                 │
│                          │ test_generate_rls_ddl_shared_reference           │
│                          │ test_generate_rls_ddl_tenant_indirect            │
│                          │ test_generate_rls_ddl_community_collaborative    │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ Context Lifecycle (2)    │ test_tenant_context_lifecycle_sqlite             │
│                          │ test_tenant_context_lifecycle_simulated_pg       │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 16 Isolation Criteria    │ 14 Functions covering Criteria 01 through 16:    │
│ (14 Functions)           │ - Criteria 01 & 02: Permitted tenant access      │
│                          │ - Criterion 03: Cross-tenant read denied         │
│                          │ - Criterion 04: Cross-tenant update denied       │
│                          │ - Criterion 05: Cross-tenant delete denied       │
│                          │ - Criterion 06: Cross-tenant insert denied       │
│                          │ - Criteria 07 & 08: Missing/invalid context      │
│                          │ - Criterion 09: Unauthenticated denied           │
│                          │ - Criterion 10: Parent-child ownership           │
│                          │ - Criterion 11: Collaborative access             │
│                          │ - Criterion 12: Shared reference access          │
│                          │ - Criterion 13: Rollback clears context          │
│                          │ - Criterion 14: Connection pool reuse            │
│                          │ - Criterion 15: Concurrent requests              │
│                          │ - Criterion 16: Admin bypass explicit            │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ Trust Boundary (5)       │ test_unprivileged_role_guc_self_escalation_block │
│                          │ test_security_definer_privilege_escalation_block │
│                          │ test_ddl_enforces_dual_session_and_current_user  │
│                          │ test_admin_role_bypass_requires_role_and_guc     │
│                          │ test_tenant_context_trust_boundary_backend_enforce│
└──────────────────────────┴──────────────────────────────────────────────────┘
```

### Classification Boundary:
- **`LOCAL_TEST_VERIFIED`:** 54 automated checks across 5 dedicated offline test suites pass cleanly:
  1. `backend/tests/test_target_validation.py` (12/12 passed)
  2. `backend/tests/test_rls_offline_ddl.py` (9/9 passed)
  3. `backend/tests/test_rls_policy_semantics.py` (14/14 passed)
  4. `backend/tests/test_orm_rls_alignment.py` (12/12 passed)
  5. `backend/tests/test_worker_security_and_privacy.py` (7/7 passed)
  Total offline automated verification: **54 passed, 0 failed**.
- **`REMOTE_TEST_NOT_EXECUTED`:** Zero tests have been executed against live Neon PostgreSQL. Local test passes are never represented as proof of live cloud enforcement. Live enforcement requires authorized completion of GATE-01 through GATE-04.

---

## 3. Comprehensive Cross-Tenant Test Matrix (10 CT Scenarios)

| Scenario ID | Tested Security Semantic | Target Table Category | Tested Tables | Expected Physical Outcome | Live Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **CT-01** | Direct Read Isolation | `TENANT_DIRECT` | `farms`, `plots` | Tenant A context returns Tenant A rows; Tenant B rows hidden (0 rows returned) | `HELD` |
| **CT-02** | Indirect Child Read Isolation | `TENANT_INDIRECT` | `crop_seasons`, `observations` | FK traversal returns Tenant A child records only; Tenant B child records hidden | `HELD` |
| **CT-03** | Cross-Tenant Write Isolation (Insert) | `TENANT_DIRECT` | `plots` | Attempting to insert row with foreign `farm_id` raises RLS policy violation | `HELD` |
| **CT-04** | Cross-Tenant Write Isolation (Update) | `TENANT_INDIRECT` | `observations` | Attempting to update Tenant B record results in 0 rows updated | `HELD` |
| **CT-05** | Cross-Tenant Write Isolation (Delete) | `TENANT_DIRECT` | `produce_lots` | Attempting to delete Tenant B record results in 0 rows deleted | `HELD` |
| **CT-06** | Shared Reference Read Access | `SHARED_REFERENCE` | `crops`, `commodities` | Unauthenticated / all tenants can read reference catalog without leakage | `HELD` |
| **CT-07** | Shared Reference Write Denial | `SHARED_REFERENCE` | `crops` | Ordinary tenant attempting to insert/update reference catalog is rejected | `HELD` |
| **CT-08** | Community Hub Collaboration | `COMMUNITY_COLLABORATIVE` | `community_posts` | Public read permitted; update/delete permitted only to author | `HELD` |
| **CT-09** | Administrative Bypass Probe | Trust Boundary | Dual Identity Condition | Ordinary user setting `app.is_admin = 'true'` is rejected; dual check enforced | `HELD` |
| **CT-10** | Connection Pool Cleansing | Session Lifecycle | Context GUCs | Consecutive queries with alternating contexts reset GUCs; zero context bleed | `HELD` |

---

## 4. Policy Edge Cases & Security Invariants

The live verification harness also probes specific edge cases:
1. **Null Tenant Identifier:** Query executed with `app.current_tenant_id` unset or empty. Evaluates to `FALSE`; returns 0 private rows.
2. **Cross-Tenant Joins:** Joining `farms` and `plots` across different tenant IDs. PostgreSQL filters rows at each table level; joined result set contains zero cross-tenant tuples.
3. **Forged Tenant ID in Payload:** Application payload contains `farm_id = 'tenant-b'` while session context is `tenant-a`. `WITH CHECK` clause fails; PostgreSQL raises `23514 check_violation`.
4. **Ownership Transfer Attempts:** Updating `owner_id` on `farms` by non-owner. Rejected by `WITH CHECK` expression.

---

## 5. Live Staging Verification Protocol (On Hold)

Once GATE-04 is formally authorized by the Project Owner:
```bash
# Step 1: Run the automated verification harness
python scripts/verify_staging_rls.py --url "$STAGING_DATABASE_URL"

# Step 2: Capture live system catalog proof to evidence file
psql "$STAGING_DATABASE_URL" -c "
SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity 
FROM pg_class c 
JOIN pg_namespace n ON n.oid = c.relnamespace 
WHERE n.nspname = 'public' AND c.relkind = 'r' 
ORDER BY c.relname;" > docs/pilot/security/LIVE_STAGING_CATALOG_PROOF.txt

# Step 3: Capture live policy definitions
psql "$STAGING_DATABASE_URL" -c "
SELECT tablename, policyname, permissive, roles, cmd, qual, with_check 
FROM pg_policies 
WHERE schemaname = 'public' 
ORDER BY tablename, policyname;" > docs/pilot/security/LIVE_STAGING_POLICIES_PROOF.txt
```

---

## 6. Failure Investigation & Triage Protocol

If any test in `verify_staging_rls.py` fails:
1. **FREEZE IN PLACE:** Do NOT run `downgrade()` or delete the staging branch.
2. Capture the exact SQL error code (e.g. `42501 insufficient_privilege` vs `23514 check_violation`).
3. Inspect `session.info` to verify whether `set_tenant_context` was called prior to the failing query.
4. Export the current transaction log to `docs/pilot/security/GATE_04_FAILURE_TRACE.txt`.
5. Report status as `VALIDATION_FAILED` and notify the Principal PostgreSQL Security Architect.
