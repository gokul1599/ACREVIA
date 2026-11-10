# ACREVIA — PHASE 07 REPOSITORY & PHASE 06 RECONCILIATION REPORT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document Code:** `PHASE_07_REPOSITORY_AND_PHASE_06_RECONCILIATION.md`  
**Execution Date:** November 10, 2026  
**Auditor Status:** VERIFIED & RECONCILED  
**Starting Commit Baseline:** `6171e16`  
**Current Implementation HEAD:** `d42a9c7` (Post Sign-in API 404 Resolution)  

---

## 1. Executive Reconciliation Summary

This report establishes the baseline reconciliation between Phase 06 reported state and the actual current repository tree prior to Phase 07 execution.

1. **Commit Lineage:**
   - The reported Phase 06 starting commit is `6171e16`.
   - The actual repository advanced to commit `d42a9c7` to permanently repair the user-reported Sign-In API 404 issue (URL normalization, Next.js rewrite sanitization, non-JSON error handling, and synthetic authentication tests).
   - `6171e16` is confirmed as a direct ancestor of `d42a9c7` (`git merge-base --is-ancestor 6171e16 d42a9c7` &rarr; `0`).
   - Per Section 4 instructions, `d42a9c7` is adopted as the true current implementation baseline without overwriting or resetting any newer work.

2. **Entity Classification Reconciliation:**
   - Phase 06 reported 132 database entities classified across 5 categories.
   - An independent audit of all tables in SQLAlchemy `Base.metadata.tables` confirms exactly 132 registered tables with 0 discrepancies against `TABLE_CLASSIFICATION`.
   - Field-level foreign key analysis identified that table `produce_quality_profiles` (which contains AGMARK quality grading definitions per crop and no tenant data) was previously counted under `TENANT_INDIRECT`. Its true relationship structure is `SHARED_REFERENCE`.
   - The audited classification is reconciled as:
     - `TENANT_DIRECT`: 25 tables
     - `USER_OWNED`: 13 tables
     - `TENANT_INDIRECT`: 53 tables (down from 54 following proper re-categorization of `produce_quality_profiles`)
     - `SHARED_REFERENCE`: 25 tables (up from 24)
     - `COMMUNITY_COLLABORATIVE`: 16 tables
     - **Total Reconciled Entities:** 132 tables.

3. **Administrative Trust Boundary Reconciliation:**
   - In Phase 06, the trust boundary check was hardened to:
     `CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') AND current_setting('app.is_admin', true) = 'true'`
   - In Phase 07, a defense-in-depth audit of PostgreSQL role-switching and `SECURITY DEFINER` semantics established that checking both the authenticated session user (`SESSION_USER`) and the execution identity (`CURRENT_USER`) prevents hypothetical privilege elevation via `SECURITY DEFINER` functions:
     `SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') AND current_setting('app.is_admin', true) = 'true'`
   - This hardened expression was verified across [`backend/app/database/rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py), [`scripts/verify_staging_rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/scripts/verify_staging_rls.py), and [`backend/tests/test_postgresql_rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_postgresql_rls.py).

---

## 2. File Verification Inventory

| File Path | Phase 06 Status | Phase 07 Reconciled Status | Verification Notes |
|---|---|---|---|
| `backend/app/database/rls.py` | Exists | Modified | Enhanced `ADMIN_BYPASS_SQL` with dual `SESSION_USER` + `CURRENT_USER` check; corrected 9 indirect FK column names. |
| `backend/tests/test_postgresql_rls.py` | 26 tests | 28 tests (+2) | Added `test_security_definer_privilege_escalation_blocked` and `test_ddl_enforces_dual_session_and_current_user_boundary`. |
| `backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py` | Exists | Verified | Verified upgrade/downgrade hooks; dialect guard confirmed for SQLite test safety. |
| `scripts/neon_staging_branch_spec.py` | Exists | Verified | Reconfirmed `is_production_url()` blocks `ep-muddy-mode-a1nd6rrb`. |
| `scripts/verify_staging_rls.py` | Exists | Modified | Added catalog checks for `pg_proc` (SECURITY DEFINER) and `pg_class` (table ownership). |
| `docs/pilot/security/ACREVIA_GLOBAL_RISK_REGISTER_PHASE_06.md` | Exists | Modified | Updated with `AUTH-ROUTING-01` and Phase 07 risk evaluations. |
| `docs/pilot/PHASE_02_OWNER_INPUT_AND_AUTHORIZATION_FORM.md` | Pending Owner | Re-audited | Identity fields unpopulated; Decision Gates A01–A05 unassigned. |
| `docs/pilot/security/PHASE_05_OWNER_INPUT_AND_APPROVAL_CHECKLIST.md` | Pending Owner | Re-audited | Decision Gate 1 unchecked; Mode A strictly enforced. |

---

## 3. Discrepancy Resolution Matrix

| Discrepancy | Previous Reported State | Audited Actual State | Resolution Applied |
|---|---|---|---|
| **`produce_quality_profiles`** | `TENANT_INDIRECT` (`fk: lot_id`) | Columns: `id, crop_id, standard_name, grade_definitions_json` (No `lot_id`) | Reclassified as `SHARED_REFERENCE` catalog table. Eliminates runtime DDL failure in PostgreSQL. |
| **`decision_feedbacks` FK** | `fk: decision_record_id` | Actual column: `decision_id` | Updated `TABLE_CLASSIFICATION` `fk` to `decision_id`. |
| **`expert_reviews` FK** | `parent: predictions, fk: prediction_id` | Actual parent: `diagnosis_requests`, `fk: diagnosis_request_id` | Updated `parent_table` and `fk` to direct diagnosis request link. |
| **`fusion_explanations` FK** | `parent: observations, fk: observation_id`| Actual parent: `plots`, `fk: plot_id` | Updated `parent_table` and `fk` to direct plot link. |
| **`harvest_sessions` FK** | `fk: plan_id` | Actual column: `harvest_plan_id` | Updated `fk` to `harvest_plan_id`. |
| **`nutrient_assessments` FK** | `parent: plots, fk: plot_id` | Actual parent: `soil_test_results`, `fk: soil_test_result_id` | Updated `parent_table` and `fk` to soil test result. |
| **`nutrient_expert_reviews` FK**| `fk: assessment_id` | Actual column: `nutrient_assessment_id` | Updated `fk` to `nutrient_assessment_id`. |
| **`quality_measurements` FK** | `parent: produce_quality_profiles, fk: profile_id` | Actual parent: `produce_lots`, `fk: lot_id` | Updated `parent_table` and `fk` to `produce_lots`. |
| **`resilience_scenario_simulations` FK** | `fk: resilience_assessment_id` | Actual column: `assessment_id` | Updated `fk` to `assessment_id`. |

---

## 4. Test Baseline Reconciliation

- **Backend Tests:** 185 (Phase 06) &rarr; 189 (Auth Repair) &rarr; **191** (+2 RLS tests).
- **ML Agronomic Tests:** 55 (Unchanged, 100% pass).
- **Vision Inference Tests:** 9 (Unchanged, 100% pass).
- **Frontend Unit & PWA Tests:** 43 (Phase 06) &rarr; **54** (+11 Auth Client tests).
- **Total Physical Test Baseline:** **309 physical automated tests passing**.
