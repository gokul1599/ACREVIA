# ACREVIA — PHASE 07: FINAL RESIDUAL SECURITY CLOSURE, WORKER IDENTITY VALIDATION & DATABASE ACCESS-PATH AUDIT REPORT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document ID:** `ACR-SEC-P07-RESIDUAL-RISK-CLOSURE-REPORT`  
**Governing Phase:** Phase 07 — Controlled Mode B Infrastructure Operations  
**Auditor:** Principal PostgreSQL Security Architect, Database Reliability Engineer, Cloud Infrastructure Governance Specialist & Technical Audit Lead  
**Audit Date:** November 10, 2026  
**Execution Mode:** `MODE A ONLY — LOCAL ENGINEERING, SOURCE INSPECTION, OFFLINE TESTING & GOVERNANCE PREPARATION`  
**Final Governance Determination:** **`TECHNICAL_PREFLIGHT_READY_WITH_RECORDED_BLOCKERS`**  

---

## 1. Executive Summary & Repository Baseline

### 1.1 Source-Verified Repository State
- **Git Branch:** `main`
- **HEAD Commit:** `b290158c421add5b40eab8a5a56ccf5a5484bbc9`
- **Remote Tracking:** Synchronized with `https://github.com/gokul1599/ACREVIA.git`
- **Tracked Modifications in Working Tree:**
  - `backend/app/services/riskcast/risk_service.py` (Worker non-impersonation support)
  - `backend/app/tasks/run_riskcast_batch.py` (Non-impersonation worker execution & discovery notice)
  - `backend/app/database/rls.py` (Granular evidence table read restriction)
  - `backend/tests/test_orm_rls_alignment.py` (Evidence privacy assertions updated)
  - `backend/tests/test_worker_security_and_privacy.py` (Expanded to 11 tests covering worker non-impersonation, collective matrix, schema separation)
  - `docs/pilot/security/PHASE_07_ACTUAL_ORM_TABLE_INVENTORY.md` (Updated access behavior for regional pulse)

---

## 2. Independent ORM Metadata vs. RLS Classification Reconciliation

### 2.1 Dynamic Mathematical Proof ($M = R$)
All model definitions from Stage 7 through Stage 14 exported in `backend/app/models/__init__.py` were loaded into SQLAlchemy Declarative Base.

Comparing the set of registered table names in `Base.metadata.tables` ($M$) against the classification keys in `TABLE_CLASSIFICATION` ($R$):

$$|M| = 132, \quad |R| = 132$$
$$M - R = \emptyset$$
$$R - M = \emptyset$$
$$\text{sorted}(M) == \text{sorted}(R) \implies \mathbf{TRUE}$$

### 2.2 Category Breakdown & DDL Mathematical Balance
- **`TENANT_DIRECT`:** 25 tables (Direct `farm_id` match) &rarr; `ENABLE RLS` + `FORCE RLS`
- **`USER_OWNED`:** 13 tables (Direct `user_id` match) &rarr; `ENABLE RLS` + `FORCE RLS`
- **`TENANT_INDIRECT`:** 53 tables (Foreign key traversal to parent tenant) &rarr; `ENABLE RLS` + `FORCE RLS`
- **`SHARED_REFERENCE` (Public):** 22 tables (Public read, admin write) &rarr; `ENABLE RLS` (FORCE RLS: **NO**)
- **`SHARED_REFERENCE` (Admin/Private):** 3 tables (`ingestion_jobs`, `partner_integrations`, `integration_partners`) &rarr; `ENABLE RLS` + `FORCE RLS`
- **`COMMUNITY_COLLABORATIVE`:** 16 tables (Author isolation, strict privacy) &rarr; `ENABLE RLS` + `FORCE RLS`

$$\text{Total DDL} = 132\ \text{ENABLE} + 110\ \text{FORCE} + 264\ \text{DROP POLICY} + 261\ \text{CREATE POLICY} = \mathbf{767\ \text{statements}}$$

---

## 3. RiskCast Worker Security & Identity Architecture

### 3.1 The Farm Discovery Paradox Under PostgreSQL RLS
**Investigation Finding:**  
In `backend/app/tasks/run_riskcast_batch.py`, the initial discovery query:
```python
farms = db.query(Farm.id).filter_by(is_archived=False).all()
```
When executed by an unprivileged database connection (`acrevia_staging_app`) without an active tenant context, **returns exactly 0 rows under PostgreSQL RLS**.

- **Root Cause:** Table `farms` enforces `FORCE ROW LEVEL SECURITY`. Its permissive policy requires either:
  1. `ADMIN_BYPASS_SQL` (which requires `SESSION_USER` in `neondb_owner`, `acrevia_admin`), OR
  2. `current_setting('app.current_tenant_id', true) != '' AND id::text = current_setting(...)`.
  Neither condition is satisfied during unscoped startup queries.
- **Evidentiary Reality:** Mocked tests and SQLite unit tests bypass this check because SQLite lacks native RLS enforcement. Under live PostgreSQL, the batch job would silently exit having evaluated 0 farms.
- **Architectural Solution:** An unprivileged worker cannot perform global table scans. Production dispatch must supply `target_farm_ids` explicitly via:
  1. An external task dispatcher / scheduler (e.g. Celery beat / Redis manifest), OR
  2. A dedicated `SECURITY DEFINER` function (e.g., `get_active_farm_ids_for_riskcast()`) owned by `acrevia_admin` with `SET search_path = public`, granted specifically to `acrevia_staging_app`.

### 3.2 Farmer Impersonation Eliminated
**Investigation Finding:**  
The earlier implementation executed:
```python
owner = db.get(User, farm.owner_id)
set_tenant_context(db, tenant_id=farm_id, user_id=owner.id, is_admin=False)
```
**Security Consequences of Farmer Impersonation:**
1. **Visible Records:** Setting `user_id = owner.id` granted the worker full read access to all 13 `USER_OWNED` tables belonging to the farmer (e.g., `session_tokens`, `consent_records`, `audit_logs`, `location_permissions`).
2. **Unauthorized Mutation:** The worker gained `WITH CHECK` write privileges under the farmer's personal identity.
3. **Audit Trail Falsification:** Background system actions were stamped with the farmer's user ID, corrupting operational auditability.

**Remediation Implemented:**
- The worker establishes:
  `set_tenant_context(db, tenant_id=farm_id, user_id="system:worker:riskcast", is_admin=False)`
- `RiskCastService.evaluate_plot` updated to accept `current_user=None` with `actor_identity="system:worker:riskcast"`.
- When `current_user is None`, `evaluate_plot` verifies that `plot.farm_id == db.info['tenant_context']['tenant_id']` and evaluates plots purely within the farm tenant scope.
- The worker **never accesses the `users` table** and has **zero access to `USER_OWNED` tables**.

---

## 4. Regional Pulse, Ingestion Jobs & Collective Privacy Audit

### 4.1 Regional Pulse Aggregation Provenance ($N \ge 3$)
**Investigation Finding:**  
In `backend/app/services/regional_pulse_service.py`, the threshold check:
```python
if data.distinct_farms_count < MINIMUM_DISTINCT_FARMS_THRESHOLD:
```
evaluates an integer supplied **directly by the HTTP request payload (`RegionalSignalCreate`)**, rather than computing the count dynamically from linked evidence records.

- **Security Consequence:** An authenticated expert or compromised agronomist credential could submit a fabricated `distinct_farms_count = 5` representing data from only 1 farm.
- **Status:** **`RECORDED_LIMITATION_LOCAL`**. Genuine $k$-anonymity requires dynamic verification counting distinct `observations.farm_id` linked via `regional_signal_evidences`.
- **Evidence Table Hardening Implemented:** `backend/app/database/rls.py` was updated so that `regional_signal_evidences` is **NO LONGER PUBLICLY READABLE**. Reads are restricted to `ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER`, or `{ADMIN_BYPASS_SQL}`, ensuring granular observation references and field notes cannot be scraped by public users.

### 4.2 Ingestion Jobs & Shared Reference Audit
- **Private Shared References (3 tables):**
  1. `ingestion_jobs` (`PRIVATE_OPERATIONAL`): Restricts pipeline logs, error traces, and source URLs to `ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER`, and `{ADMIN_BYPASS_SQL}`.
  2. `partner_integrations` (`ADMINISTRATIVE`): Third-party integration configurations and webhook secrets. Admin only.
  3. `integration_partners` (`ADMINISTRATIVE`): Partner organizational metadata, legal entity numbers, compliance status. Admin only.
- **Public Shared References (22 tables):**
  Public `SELECT` is justified for agronomic reference catalogs (`crops`, `crop_varieties`, `produce_quality_profiles`, `risk_rules`, `market_commodities`, `market_locations`, `market_price_observations`, `climate_baselines`, `agricultural_practice_definitions`, `roles`, `satellite_sources`, `satellite_acquisitions`, `crop_calendar_definitions`, `training_events`, `learning_resources`, and approved knowledge graph entities/relationships).
- **Public Reference Sensitivity Finding:**
  `knowledge_document_versions` includes `original_file_path`, which can expose internal server directory structures. Ingestion pipelines should sanitize or omit filesystem paths prior to public distribution.

### 4.3 Collective & FPO Response-Field Privacy Matrix
**Schema Separation Confirmed:**
- **`registration_number`:** Belongs to `AgriculturalOrganization` in `backend/app/models/collective.py`.
- **`legal_entity_number`:** Belongs to `IntegrationPartner` in `backend/app/models/interoperability.py`.
- There is zero property collision in ORM models or schemas.

**Endpoint Response Field Matrix (`/api/v1/collectives/organizations`):**

| Request Scenario | `contact_email` | `contact_phone` | `registration_number` | `verification_status` | Status Code |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Anonymous User** | N/A | N/A | N/A | N/A | `401 Unauthorized` |
| **Authenticated Non-Member** | `None` | `None` | `None` | Unmasked | `200 OK` |
| **Authenticated Inactive Member** | `None` | `None` | `None` | Unmasked | `200 OK` |
| **Member of Different Org** | `None` | `None` | `None` | Unmasked | `200 OK` |
| **Active Member of Exact Org** | **Unmasked** | **Unmasked** | **Unmasked** | Unmasked | `200 OK` |
| **System Administrator** | **Unmasked** | **Unmasked** | **Unmasked** | Unmasked | `200 OK` |

Verified via unit test `test_collective_organization_endpoint_privacy_matrix`.

---

## 5. Offline Test Evidence Summary

Full automated test suite executed in the local environment:

```text
============================= test session starts =============================
platform win32 -- Python 3.11.16, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\gokul\OneDrive\Documents\projects
collected 58 items

backend/tests/test_target_validation.py ............                     [ 20%]
backend/tests/test_rls_offline_ddl.py .........                           [ 36%]
backend/tests/test_rls_policy_semantics.py ..............                [ 60%]
backend/tests/test_orm_rls_alignment.py ............                     [ 81%]
backend/tests/test_worker_security_and_privacy.py ...........            [100%]

======================== 58 passed, 1 warning in 7.66s ========================
```

- **Total Tests Collected:** 58
- **Passed:** 58 (100%)
- **Failed:** 0
- **Skipped:** 0
- **Warnings:** 1 (`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated` &mdash; upstream third-party library notice; non-actionable).

### Evidentiary Classification of Tests:
- `test_target_validation.py` (12 tests): **OFFLINE_UNIT_TEST** (URL parsing and fail-closed target guards).
- `test_rls_offline_ddl.py` (9 tests): **STATIC_POLICY_GENERATION_TEST** (DDL AST and statement count validation).
- `test_rls_policy_semantics.py` (14 tests): **STATIC_POLICY_GENERATION_TEST & MOCKED_SESSION_TEST**.
- `test_orm_rls_alignment.py` (12 tests): **STATIC_METADATA_TEST** (Dynamic model metadata inspection).
- `test_worker_security_and_privacy.py` (11 tests): **OFFLINE_UNIT_TEST & STATIC_METADATA_TEST**.

> [!WARNING]
> None of these 58 passing tests constitute proof of physical PostgreSQL kernel RLS enforcement. Physical enforcement requires executing against a live PostgreSQL 15+ engine on the provisioned staging branch.

---

## 6. Remaining Live PostgreSQL Verification Checklist

The following verifications strictly require the authorized live Neon staging branch:

1. **Kernel-Level Policy Injection:** Proving that PostgreSQL query planner applies `USING` filtering to `acrevia_staging_app` queries.
2. **`FORCE ROW LEVEL SECURITY` Enforcement:** Confirming that table owners cannot bypass policies.
3. **Cross-Tenant Probes (CT-01 through CT-10):** Physical execution verifying that cross-tenant `SELECT` returns 0 rows and cross-tenant `INSERT/UPDATE/DELETE` fail.
4. **Catalog Integrity Audit:** Querying live `pg_class.relrowsecurity`, `pg_class.relforcerowsecurity`, and `pg_policies`.
5. **Session-Level Context Reset:** Proving that connection pool reuse under async load executes clean transaction rollback of GUCs.

---

## 7. Governance Status

- **GATE-01:** PROVISIONED & ACTIVE (`staging-rls-phase07` on Neon Cloud).
- **GATE-02:** `NOT_GRANTED` (Database roles unprovisioned).
- **GATE-03:** `NOT_GRANTED` (Migration unexecuted).
- **GATE-04:** `NOT_GRANTED` (Live verification unexecuted).
- **GATE-05:** `NOT_GRANTED` (Teardown unexecuted).
- **Operating Mode:** `MODE A ONLY` maintained for this audit turn. Zero remote commands executed.
