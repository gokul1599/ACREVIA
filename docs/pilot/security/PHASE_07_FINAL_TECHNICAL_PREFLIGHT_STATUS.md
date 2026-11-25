# ACREVIA — PHASE 07: FINAL TECHNICAL PREFLIGHT STATUS & OWNER RELEASE GATING

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation  
**Document ID:** `ACR-SEC-P07-FINAL-PREFLIGHT-STATUS`  
**Classification:** RESTRICTED — PILOT PREFLIGHT DETERMINATION  
**Overall Preflight Status:** **`TECHNICAL_PREFLIGHT_READY_WITH_RECORDED_BLOCKERS`**  
**Operating Mode:** **`MODE A ONLY`** (Local Engineering, Source Inspection & Offline Verification)  
**Baseline Test Verification:** **`171 passed, 1 warning in 17.51s`** (100% passing across all 5 test suites; 108 passed in worker security suite; 6 passed in Stage 12; 171 passed under `python -O` in 20.00s)  

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
| **`WRK-DISP-01`** | **HIGH** | Worker Security Architecture | Caller-controlled boolean shortcuts eliminated (`TypeError` raised). Immutable `DispatchAuthorization` capability grant required. Staging/production dispatch provider remains `NOT_IMPLEMENTED` and fails closed (`DISPATCH_NOT_CONFIGURED`). | Provisioning of external authenticated task broker meeting 9-point capability verification contract. |
| **`RES-PULSE-01`** | **MEDIUM** | Regional Data Privacy Scope | Policy on `regional_signal_evidences` grants role-global access to `AGRICULTURAL_EXPERT` and `RESEARCHER` without district-level scoping (`OWNER_ACCEPTANCE_REQUIRED`). TOCTOU concurrency under `READ COMMITTED` mitigated via dynamic fail-closed revalidation. | Deliberate residual risk requiring Project Owner formal acceptance or future district-assignment schema enhancement. |
| **`RES-PULSE-02`** | **MEDIUM** | Read Consistency & Concurrency | Under PostgreSQL default `READ COMMITTED` transaction isolation, multiple statements within a single request inspect distinct database snapshots. A residual window exists where concurrent evidence mutations may be observed across statements (`OWNER_ACCEPTANCE_REQUIRED`). | Formal Project Owner acceptance of residual non-blocking read-committed snapshot window. |
| **`RES-PRIMARY-ROUTING-01`** | **MEDIUM** | Database Routing & Reliability | Public Regional Pulse GET requests execute write-on-read dynamic provenance updates (`SUPPRESSED_INSUFFICIENT_PROVENANCE`), requiring connection to a read-write primary. Standby read replica routing triggers SQLSTATE 25006 and fails closed with HTTP 500 (`OWNER_ACCEPTANCE_REQUIRED`). | Project Owner formal acceptance of primary-only write-on-read routing for regional pulse API pods. |
| **`RES-REPLICA-LAG-01`** | **MEDIUM** | Standby Replication Lag | If read traffic is inadvertently routed to a standby read replica suffering replication lag ($\Delta t$), the replica may still observe $N \ge 3$ and serve a stale signal without attempting a write (`OWNER_ACCEPTANCE_REQUIRED`). | Routing enforcement ensuring Regional Pulse endpoints exclusively target primary database. |
| **`RES-FREE-TEXT-01`** | **MEDIUM** | Author Content & Privacy | Free-text fields (`signal_title`, `signal_summary`, `recommended_action`) are sanitized for panic vocabulary but lack automated PII redaction. Authors inputting personal farmer data will have it served publicly to farmers (`OWNER_ACCEPTANCE_REQUIRED`). | Project Owner formal acceptance requiring operational author publishing guidelines and administrative four-eyes review. |
| **`GATE01-PROV-01`** | **MEDIUM** | Infrastructure Provenance | Neon staging branch `staging-rls-phase07` is recorded as provisioned in local artifacts, but cannot be independently validated via live cloud API in Mode A. | Independent verification of remote endpoint upon Mode B activation. |
| **`RLS-WRITE-AUTH-01`** | **HIGH** | Database Policy Alignment | Generated RLS write policy allows `AGRICULTURAL_EXPERT` and `RESEARCHER` to write to `regional_signals` without status restrictions in `WITH CHECK`, rendering D-01 Option C unsafe without write-side hardening (`POLICY_DESIGN_UNSAFE`). | Owner determination on Decision D-01: implement Option B (separate table) or harden Option C with dedicated write policies. |
| **`RLS-ROLE-ASSIGNMENT-01`** | **CRITICAL** | Authorization & Privilege Escalation | `user_roles` categorized as `USER_OWNED`, allowing users to self-assign `ADMIN` via mutable `app.current_user_id` session GUC under `acrevia_staging_app`. Revoking DML without replacement breaks user registration. | Deploy forward migration with `register_default_user_role` stored function gateway and revoke direct runtime DML. |
| **`RLS-TEST-ORACLE-01`** | **LOW** | Test-Oracle Integrity | `test_regional_signals_admin_only_write()` formerly claimed an admin-only invariant while checking only `ADMIN_BYPASS_SQL`. | **RESOLVED LOCALLY:** Test docstring and assertions corrected to enforce actual allowlist (`ADMIN`, `AGRI_EXPERT`, `RESEARCHER`) and exclusion of `FARMER`. |

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
| **Worker Capability Hardening** | Cryptographic capability authenticity & thread-safe replay | Explicit conditional guard (no assert); 10-dimension canonical JSON HMAC binding with independent mutation tests for all 10 fields; mandatory UTC expiration bounded to 24h; secret getter threat model proven; thread-safe atomic token consumption with >5000 high-water fail closed; retry support; distributed replay classified as NOT_IMPLEMENTED | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Worker Dispatch Provider Guard** | Fail closed in production/staging | `DispatchVerifier.DISPATCH_PROVIDER = None` (`NOT_IMPLEMENTED`); fails closed with `ProductionDispatchBlockedError` | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Worker Dispatcher Contract** | Specify minimum future dispatcher interface | 9 dimensions defined: actor identity, task ID, targets, purpose, expiry, integrity, replay, context gate, attribution | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Regional Pulse Provenance & Recovery** | Separate measured insufficiency, atomic recovery & audit | Derives $N \ge 3$ dynamically; DB failure fails closed; SAVEPOINT isolates caller session; helper NEVER commits; dedicated recovery endpoint `POST /signals/{id}/recover` enforced by server RBAC (`ADMIN`, `AGRICULTURAL_EXPERT`); semantic distinction (`EXPERT_CONFIRMED` vs `ADMIN_CONFIRMED`); atomic append-only `AuditLog` staging; row-level lock & HTTP 409 replay conflict protection | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Regional Aggregation Edge Cases** | Robust against all 16 input edge cases | Cross-region, out-of-window, missing evidence, post-pub deletion all handled | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Regional Evidence Privacy** | Mask granular evidence for non-experts | `GET /regional-pulse/signals` masks `evidences = []` for `FARMER` role; RLS policy denies public read | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Regional Pulse Read Routing** | Single engine primary connection; write-on-read | Classified as `PRIMARY_ONLY_WRITE_ON_READ`; standby read replica triggers SQLSTATE 25006 and fails closed with HTTP 500 | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Regional Pulse Cache Consistency** | Origin anti-caching & service worker bypass | `Cache-Control: no-cache, no-store, must-revalidate` on origin; PWA SW bypasses `/api/`; multi-instance synced via DB | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Regional Pulse Privacy Latency** | Empirical measurement of in-process window | Median 4.94ms across 50 cycles; classified as `MEASURED_BUT_NOT_HARD_BOUNDED` due to OS/network variables | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Collective Field Separation** | Zero collision of org identifiers | `AgriculturalOrganization.registration_number` vs `IntegrationPartner.legal_entity_number` | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Collective Data Masking** | Redact contact & registration for non-members | 6-state redaction matrix implemented in endpoints and verified with unit tests | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Database Privilege Closure** | Category-specific least privilege (no blanket DML) | SELECT (132), INSERT (108), UPDATE (107), DELETE (90); TRUNCATE (0), REFERENCES (0), TRIGGER (0); audit_logs append-only; idempotent DDL generation with explicit REVOKEs | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Three-Way Metadata Set Equality** | Verify 1:1:1 mapping across all entities | `Base.metadata.tables` (132) == `TABLE_CLASSIFICATION` (132) == `PRIVILEGE_CROSSWALK` (132), $\Delta = \emptyset$ | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Collective Full Route Coverage** | Verify all organization HTTP endpoints | 6 caller states verified across `GET /organizations`, `GET /organizations/{id}`, and `POST /verify` | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **SQLSTATE Semantics** | Distinguish RLS failures from constraints | Filtered read/write: 0 rows (`00000`); WITH CHECK failure: `42501`; Check constraint: `23514` | **`RESOLVED_LOCALLY_AND_TESTED`** |
| **Physical PostgreSQL RLS** | Live verification on PostgreSQL engine | Not executed on remote database; offline tests cannot prove physical engine behavior | **`BLOCKED_PENDING_LIVE_POSTGRESQL`** |
| **Downstream Governance Gates** | Gates 02 through 05 approval | Recorded as `NOT_GRANTED` in authorization register | **`OWNER_AUTHORIZATION_REQUIRED`** |

---

## 4. Test Suite Execution Summary & Git Reconciliation

### 1. Git Repository HEAD Reconciliation
- **Preceding Audit Baseline:** Commit `82c6069463c1199562778e70569bee1579db693b`.
- **Current Repository HEAD:** Commit `dbad296c6f19c4bbe8eb48fcd7a0e07441cfa408` on branch `main`.
- **Reconciliation Audit:** Repository synchronization commit `dbad296` incorporates Phase 07 recovery endpoints, strict write-on-read transaction ownership, and Stage 12 end-to-end tests. All commits have been pushed to GitHub with 100% green checkmarks on GitHub Actions CI (run 43263147172). Working tree maintains active tests in Mode A without uncommitted core logic changes.

### 2. Full Phase 07 Offline Test Suite Execution
Full local test execution across all 5 Phase 07 security test files:
```powershell
$env:VIRTUAL_ENV = "$PWD\.venv"; $env:PYTHONPATH = "$PWD;$PWD\.venv\Lib\site-packages"; & C:\Users\gokul\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe -m pytest backend/tests/test_target_validation.py backend/tests/test_rls_offline_ddl.py backend/tests/test_rls_policy_semantics.py backend/tests/test_orm_rls_alignment.py backend/tests/test_worker_security_and_privacy.py
```
- **Total Tests Collected:** **`171`**
- **Passed:** **`171`** (100%)
- **Failed:** **`0`**
- **Skipped:** **`0`**
- **Warnings:** **`1`** (`StarletteDeprecationWarning: Using 'httpx' with 'starlette.testclient' is deprecated; install 'httpx2' instead` — tracked as upstream dependency note).
- **Optimized Python Mode Verification:** Executed across all 5 test files with `python -O -m pytest ...` -> **`171 passed, 2 warnings in 20.00s`** (proving zero authorization guards rely on Python `assert`).
- **Physical Kernel Status:** `POSTGRESQL_KERNEL_RLS_TESTS = NOT_EXECUTED` (Strictly preserved in Mode A; offline tests prove mathematical DDL and mock semantics only).

---

## 5. Mode B Operational Execution Roadmap (Post-Approval)

When the Project Owner signs off on Gates 02 through 05:
1. **GATE-02 Activation:** Execute `neon roles create` to provision `acrevia_staging_app` (`NOSUPERUSER`, `NOBYPASSRLS`).
2. **GATE-03 Activation:** Run Alembic migration `a1089411c87d` using `neondb_owner` to apply all 767 DDL statements.
3. **GATE-04 Activation:** Execute `scripts/verify_staging_rls.py` to confirm catalog RLS flags (`pg_class`, `pg_policies`) and run cross-tenant CRUD probes.
4. **GATE-05 Activation:** Schedule automated branch deprovisioning 24 hours post-verification.

---

## 6. Dated Addendum — November 23, 2026: Identity Audit & Role Management Containment

1. **Blocker RLS-ROLE-ASSIGNMENT-01 Formalized:** Proven from local source that `user_roles` permits self-assignment of `ADMIN` by setting `app.current_user_id`.
2. **Operational Registration Conflict:** Identified that direct revocation of `INSERT` on `user_roles` breaks onboarding; requires Option E (SECURITY DEFINER stored gateway `register_default_user_role`) before DML revocation.
3. **Complete 78-Tenant Table Audit:** Confirmed all 78 tenant tables depend on caller GUCs; zero tables enforce independent database-layer membership checks.
4. **Companion Deliverables:**
   - Remediation Plan: [`PHASE_07_GLOBAL_RLS_IDENTITY_REMEDIATION_AND_ROLE_MANAGEMENT_CONTAINMENT_PLAN.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GLOBAL_RLS_IDENTITY_REMEDIATION_AND_ROLE_MANAGEMENT_CONTAINMENT_PLAN.md)
   - Traceability Matrix: [`PHASE_07_GLOBAL_GUC_AND_TENANT_POLICY_TRACEABILITY_MATRIX.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GLOBAL_GUC_AND_TENANT_POLICY_TRACEABILITY_MATRIX.md)
