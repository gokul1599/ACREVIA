# ACREVIA — PHASE 07: FINAL TECHNICAL PREFLIGHT STATUS & OWNER RELEASE GATING

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation  
**Document ID:** `ACR-SEC-P07-FINAL-PREFLIGHT-STATUS`  
**Classification:** RESTRICTED — PILOT PREFLIGHT DETERMINATION  
**Overall Preflight Status:** **`TECHNICAL_PREFLIGHT_READY_WITH_RECORDED_BLOCKERS`**  
**Operating Mode:** **`MODE A ONLY`** (Local Engineering, Source Inspection & Offline Verification)  
**Baseline Test Verification:** **`73 passed, 1 warning in 10.42s`** (100% passing across all 5 test suites)  

---

## 1. Overall Engineering Determination

ACREVIA Phase 07 has attained the defensible status of:

$$\mathbf{TECHNICAL\_PREFLIGHT\_READY\_WITH\_RECORDED\_BLOCKERS}$$

### Justification:
All local source code, database policies, role architectures, background task safety constraints, dynamic regional privacy engines, and offline unit test harnesses are mathematically and structurally complete. However, Phase 07 **cannot and must not be declared released** because physical PostgreSQL enforcement on live infrastructure requires genuine Project Owner authorization for Decision Gates 02 through 05, and task dispatch authorization requires an external production scheduler.

---

## 2. Active Blocker Register

| Blocker ID | Severity | Blocker Category | Nature & Description | Resolution Requirement |
| :--- | :--- | :--- | :--- | :--- |
| **`OWNER-AUTH-01`** | **CRITICAL** | Governance & Authorization | Decision Gates 02, 03, 04, and 05 in [`PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md) are unapproved (`[ ] UNCHECKED`). | Project Owner must sign off on subsequent gates prior to any remote mutation. |
| **`DB-RLS-01`** | **HIGH** | Database Engine Verification | Physical PostgreSQL Row-Level Security enforcement, `FORCE ROW LEVEL SECURITY` behavior, catalog reflection (`pg_class`, `pg_policies`), and cross-tenant isolation probes have not been executed on live PostgreSQL. | Execution of migration `a1089411c87d` and verification harness on staging branch under GATE-03 & GATE-04. |
| **`WRK-DISP-01`** | **HIGH** | Worker Security Architecture | Production worker fails closed (`DISPATCH_NOT_CONFIGURED`) and unscoped discovery query is removed. Production deployment requires external authenticated task queue/scheduler. | Provisioning of external authenticated task broker (e.g. SQS, Redis, Celery) meeting 9-point contract. |
| **`RES-PULSE-01`** | **MEDIUM** | Regional Data Privacy Scope | Policy on `regional_signal_evidences` grants role-global access to `AGRICULTURAL_EXPERT` and `RESEARCHER` without district-level scoping. | Deliberate residual risk requiring Project Owner sign-off or future district-assignment schema enhancement. |
| **`GATE01-PROV-01`** | **MEDIUM** | Infrastructure Provenance | Neon staging branch `staging-rls-phase07` is recorded as provisioned in local artifacts, but cannot be independently validated via live cloud API in Mode A. | Independent verification of remote endpoint upon Mode B activation. |

---

## 3. Comprehensive Preflight Assessment Matrix

| Subsystem / Dimension | Target Requirement | Implemented Reality | Evidence Classification |
| :--- | :--- | :--- | :--- |
| **ORM & Classification Equality** | Exact 1:1 match across all entities | `Base.metadata.tables` (132) == `TABLE_CLASSIFICATION` (132), $\Delta = \emptyset$ | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **RLS DDL Compilation** | 767 statements mathematically verified | 132 `ENABLE RLS`, 110 `FORCE RLS`, 264 `DROP`, 261 `CREATE` | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Worker Identity Model** | No farmer impersonation; UUID type safe | `system:worker:riskcast` sentinel; all policies use `col::text`; no `USER_OWNED` access | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Worker Dispatch Boundary** | Validate & sanitize dispatch farm IDs | Validates UUID format, de-duplicates, bounds batch size $\le 100$, handles empty gracefully | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Worker Dispatch Boundary** | Validate & sanitize dispatch farm IDs | Validates UUID format, de-duplicates, bounds batch size $\le 100$, handles empty gracefully | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Worker Dispatch Production Guard** | Fail closed without trusted dispatcher | Raises `ProductionDispatchBlockedError: DISPATCH_NOT_CONFIGURED` in production/staging | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Worker Discovery Query Elimination** | Eliminate unscoped cross-tenant query | Legacy `SELECT id FROM farms` completely removed; unbacked calls raise `ValueError` | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Worker Internal Function Guard** | Block unverified single-farm evaluation | `evaluate_single_farm` raises `PermissionError` before creating session or tenant context | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Worker Dispatcher Contract** | Specify minimum future dispatcher interface | 9 dimensions defined: actor identity, task ID, targets, purpose, expiry, integrity, replay, context gate, attribution | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Regional Pulse Provenance** | Do not trust client farm counts | $N \ge 3$ dynamically derived from linked `Observation`/`RiskAlert` records; invalid counts rejected | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Regional Aggregation Edge Cases** | Robust against all 16 input edge cases | Cross-region, out-of-window, missing evidence, post-pub deletion all handled | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Regional Evidence Privacy** | Mask granular evidence for non-experts | `GET /regional-pulse/signals` masks `evidences = []` for `FARMER` role; RLS policy denies public read | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Collective Field Separation** | Zero collision of org identifiers | `AgriculturalOrganization.registration_number` vs `IntegrationPartner.legal_entity_number` | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Collective Data Masking** | Redact contact & registration for non-members | 6-state redaction matrix implemented in endpoints and verified with unit tests | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Database Privilege Closure** | Deny TRUNCATE and whole-table bypass | Runtime role `acrevia_staging_app` denied `TRUNCATE` and `REFERENCES`; 0 views, 0 secdef funcs | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **SQLSTATE Semantics** | Distinguish RLS failures from constraints | Filtered read/write: 0 rows (`00000`); WITH CHECK failure: `42501`; Check constraint: `23514` | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Physical PostgreSQL RLS** | Live verification on PostgreSQL engine | Not executed on remote database; offline tests cannot prove physical engine behavior | **`BLOCKED_PENDING_LIVE_POSTGRESQL`** |
| **Downstream Governance Gates** | Gates 02 through 05 approval | Recorded as `NOT_GRANTED` in authorization register | **`OWNER_AUTHORIZATION_REQUIRED`** |

---

## 4. Test Suite Execution Summary

Full local test execution across all 5 test files:
```powershell
.venv\Scripts\python.exe -m pytest backend/tests/test_target_validation.py backend/tests/test_rls_offline_ddl.py backend/tests/test_rls_policy_semantics.py backend/tests/test_orm_rls_alignment.py backend/tests/test_worker_security_and_privacy.py
```
- **Total Tests Collected:** **`67`**
- **Passed:** **`67`** (100%)
- **Failed:** **`0`**
- **Skipped:** **`0`**
- **Warnings:** **`1`** (`StarletteDeprecationWarning: Using 'httpx' with 'starlette.testclient' is deprecated; install 'httpx2' instead` — tracked as upstream dependency note).

---

## 5. Mode B Operational Execution Roadmap (Post-Approval)

When the Project Owner signs off on Gates 02 through 05:
1. **GATE-02 Activation:** Execute `neon roles create` to provision `acrevia_staging_app` (`NOSUPERUSER`, `NOBYPASSRLS`).
2. **GATE-03 Activation:** Run Alembic migration `a1089411c87d` using `neondb_owner` to apply all 767 DDL statements.
3. **GATE-04 Activation:** Execute `scripts/verify_staging_rls.py` to confirm catalog RLS flags (`pg_class`, `pg_policies`) and run cross-tenant CRUD probes.
4. **GATE-05 Activation:** Schedule automated branch deprovisioning 24 hours post-verification.
