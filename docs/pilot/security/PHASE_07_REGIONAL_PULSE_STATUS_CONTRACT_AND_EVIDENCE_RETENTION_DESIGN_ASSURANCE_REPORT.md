# ACREVIA — PHASE 07: REGIONAL PULSE STATUS CONTRACT ENFORCEMENT, CASCADE-RESILIENT EVIDENCE RETENTION & PUBLIC READ POLICY DECISION-READINESS ASSURANCE REPORT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** `MODE A ONLY` — Local Source Inspection, Security Engineering Analysis, Concurrency Modeling, Test-Design Assessment & Governance Documentation  
**Methodology:** Everything Claude Code (ECC): `PLAN → INSPECT / TRACE → ADVERSARIAL REVIEW → IMPLEMENT ONLY IF DEFECT PROVEN → REVIEW → VERIFY → DOCUMENT`  
**Inspected Baseline Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Public Repository:** `https://github.com/gokul1599/ACREVIA`  
**Governing Governance Register:** `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`  
**Decision Traceability Matrix:** `docs/pilot/security/phase_07_owner_decision_evidence_traceability_matrix.md`  
**Prior Deliverables Preserved:**  
- `docs/pilot/security/PHASE_07_REGIONAL_PULSE_FARMER_READ_AVAILABILITY_AND_SAVEPOINT_FAILURE_ASSURANCE_REPORT.md`  
- `docs/pilot/security/PHASE_07_REGIONAL_PULSE_COMMAND_SCOPE_RLS_AND_TRUSTED_PROVENANCE_DESIGN_ASSURANCE_REPORT.md`  
- `docs/pilot/security/PHASE_07_REGIONAL_PULSE_POLICY_COMPATIBILITY_AND_WORKER_DISPATCH_CORRECTIVE_ASSURANCE_REPORT.md`  
**Release Readiness Recommendation:** `CONDITIONALLY_READY_FOR_OWNER_REVIEW`  
**Governance Gate Status:** `GATE-01: RECORDED_OWNER_APPROVED (2026-11-10) — LIVE_DATABASE_UNVERIFIED` | `GATE-02` through `GATE-05: AWAITING_OWNER_SIGN_OFF`  
**Phase 07 Status:** **NOT RELEASED** | **Mode B Status:** **STRICTLY NOT AUTHORIZED**  

---

## 1. EXECUTIVE ASSURANCE SUMMARY

This assurance audit was conducted under strict **MODE A** constraints to establish decision-readiness for the ACREVIA Phase 07 PostgreSQL Row Level Security (RLS) and Regional Pulse architecture.

### 1.1 Core Assurance Findings
1. **Absence of Database-Enforced Status Constraints (`LOCAL_SOURCE_VERIFIED`):**
   - The Regional Pulse domain attributes `validation_status` and `confidence_tier` in `RegionalSignal` are defined in SQLAlchemy and Alembic as bare `String(50)` columns without database `CHECK` constraints, database `ENUM` types, or Python enum validation.
   - Any authorized database writer or direct SQL connection can persist arbitrary strings. Status contract enforcement exists exclusively within application service logic.
2. **True Status Lifecycle vs. Proposed Predicates (`LOCAL_SOURCE_VERIFIED`):**
   - The actual lifecycle statuses emitted by `RegionalPulseService` are: `UNVALIDATED_OBSERVATION`, `EXPERT_CONFIRMED`, `ADMIN_CONFIRMED`, `OFFICIAL_ALERT`, and `SUPPRESSED_INSUFFICIENT_PROVENANCE`.
   - The status `'PUBLISHED'` does not exist in the codebase, and `'OFFICIAL_ADVISORY'` is a `confidence_tier`, not a validation status.
   - Any public SELECT policy relying on `validation_status IN ('PUBLISHED', 'OFFICIAL_ADVISORY')` would evaluate to `FALSE` for 100% of rows, completely denying legitimate farmer reads.
   - Furthermore, a naive allowlist restricted to `EXPERT_CONFIRMED` and `ADMIN_CONFIRMED` would exclude community signals that reach $N \ge 3$ distinct farms but remain in `UNVALIDATED_OBSERVATION` pending agronomic review (**Decision D-03**), and would exclude official state advisories ($N=0$) (**Decision D-01**).
3. **Foreign Key Cascade Undermines Append-Only Evidence Guarantee (`LOCAL_SOURCE_VERIFIED`):**
   - In `backend/app/models/regional_pulse.py`, `RegionalSignalEvidence.signal_id` defines `ForeignKey("regional_signals.id", ondelete="CASCADE")`.
   - Under PostgreSQL engine semantics (`ri_triggers.c`), referential integrity cascade triggers (`RI_FKey_cascade_del`) execute with `SECURITY_NOFORCE_RLS` under SPI, bypassing child-table RLS policies and table-level `DELETE` privilege checks.
   - Deleting a parent `regional_signals` row permanently purges all linked `regional_signal_evidences` rows.
   - Restricting the FK to `ON DELETE RESTRICT` alone is insufficient because SQLAlchemy's relationship defines `cascade="all, delete-orphan"`, causing the ORM to schedule child deletions before parent deletion. Cascade resilience requires coordinating both ORM and database layers.
4. **Permissive Policy Composition and Role-Scope Exposure (`SOURCE_INFERENCE`, `RES-PULSE-01`):**
   - The permissive `regional_signals_author_write_policy` (`FOR ALL`) applies to `SELECT` under PostgreSQL engine rules, combining with logical `OR` against the public read policy.
   - A blanket role check grants statewide, cross-district visibility into suppressed, below-threshold, and draft signals across all 33 districts of Telangana. `RES-PULSE-01` is maintained at canonical **`MEDIUM`** severity.
5. **Worker Infrastructure Infeasibility (`LOCAL_SOURCE_VERIFIED`, `WRK-DISP-01`):**
   - Recommending an asynchronous worker for provenance revalidation is currently operationally infeasible.
   - Under `WRK-DISP-01`, `run_riskcast_batch.py` raises `ProductionDispatchBlockedError: DISPATCH_NOT_CONFIGURED` in staging/production environments. Zero Celery queues or task runners exist for Regional Pulse.
   - Moving revalidation out of GET routes is essential to eliminate `RES-PULSE-READ-01`, but worker deployment requires resolving `WRK-DISP-01` with a Transactional Outbox.

---

## 2. AUDIT SCOPE, EXCLUSIONS, AND MODE A RESTRICTIONS

### 2.1 Scope of Inspection
- Source code in `backend/app/` (models, schemas, endpoints, services, tasks, database configuration).
- Migration definitions in `backend/app/database/migrations/versions/`.
- Security documentation and governance registers in `docs/pilot/security/`.
- Local offline unit test execution and dialect verification.

### 2.2 Mandatory MODE A Operational Restrictions
In accordance with pilot governance, the following boundaries were strictly observed:
- Zero live connections to Neon Cloud, staging, or production databases.
- Zero remote SQL executions against live catalogs (`pg_policies`, `pg_roles`).
- Zero database provisioning, role creation, or credential manipulation.
- Zero source-code, schema, or test-file modifications.
- Zero Git write operations (no branch, commit, push, stash, or reset).
- Zero deletion or replacement of existing user deliverables.
- Credential values in source were neither printed, tested, nor reproduced.

---

## 3. REPOSITORY BASELINE AND WORKING-TREE EVIDENCE

### 3.1 Baseline Synchronization
- **Local Git Branch:** `main`
- **Local HEAD Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d`
- **Remote `origin/main` Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d`
- **Divergence:** Exactly 0 commits (`HEAD` is synchronized with `origin/main`).

### 3.2 Working Tree Status
- **Modified Tracked Governance Files (7):** Historical Phase 07 planning and decision matrices.
- **Untracked Historical Assurance Reports (10):** Sequentially generated assurance reports in `docs/pilot/security/`.
- **Application Source Code Modifications:** Exactly **0 files modified** across `backend/app/`, `backend/alembic/`, `backend/tests/`, and frontend.

---

## 4. EVIDENCE CLASSIFICATION METHODOLOGY

Every material claim in this report is tagged with its formal classification:

| Classification | Meaning & Scope |
|---|---|
| `PUBLIC_SOURCE_VERIFIED` | Established directly from public commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d`. |
| `LOCAL_SOURCE_VERIFIED` | Established directly from the local repository working tree. |
| `LOCAL_TEST_VERIFIED` | Executed offline in Python/SQLite/mock environment without network calls. |
| `USER_REPORTED` | Derived from earlier audit documentation or user briefings. |
| `SOURCE_INFERENCE` | Deduced logically from code structure and official documentation. |
| `DESIGN_RECOMMENDATION` | Recommended architecture or control; not currently implemented. |
| `LIVE_DATABASE_UNVERIFIED` | Requires authorized live PostgreSQL inspection; unverified in Mode A. |
| `OWNER_DECISION_REQUIRED` | Requires formal Project Owner governance sign-off. |

---

## 5. REGIONAL PULSE SCHEMA AND STATUS-CONTRACT FINDINGS

### 5.1 Storage and Validation Types (`LOCAL_SOURCE_VERIFIED`)
Inspection of `backend/app/models/regional_pulse.py` (lines 20–35) and migration `backend/app/database/migrations/versions/d2894a11c87d_stage12_collaborative_intelligence.py` reveals:

```python
class RegionalSignal(Base, TimestampMixin):
    __tablename__ = "regional_signals"

    confidence_tier: Mapped[str] = mapped_column(String(50), nullable=False)
    validation_status: Mapped[str] = mapped_column(String(50), default="UNVALIDATED_OBSERVATION", nullable=False)
```

In migration `d2894a11c87d`:
```python
def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)
```

**Architectural Findings:**
1. **Bare String Types:** `validation_status` and `confidence_tier` are stored as PostgreSQL `VARCHAR(50)`.
2. **No Database Constraints:** There are no `CHECK (validation_status IN (...))` constraints, no user-defined PostgreSQL `ENUM` types, and no table triggers validating status values.
3. **No Schema Enums:** Pydantic schema `RegionalSignalCreate` defines `validation_status: str = "UNVALIDATED_OBSERVATION"` as a bare Python `str` without `Literal` or enum constraints.
4. **Vulnerability to Direct SQL Writes:** Any database principal holding `UPDATE` privilege on `regional_signals` can execute `UPDATE regional_signals SET validation_status = 'ANY_ARBITRARY_STRING'` without violating database integrity constraints.
5. **Enforcement Layer:** Status contract enforcement exists **exclusively in Python service-layer logic** (`backend/app/services/regional_pulse_service.py`).

---

## 6. ACTUAL SERVICE STATUS-TRANSITION MATRIX

### 6.1 State Machine Dissection (`LOCAL_SOURCE_VERIFIED`)
Tracing all methods in `RegionalPulseService` yields the complete status-transition matrix:

| Operation | Initial State | Resulting State | Required Actor / Authority | Evidence Requirement | Source Reference |
|---|---|---|---|---|---|
| **Create Crowd Signal** | Non-existent | `UNVALIDATED_OBSERVATION` | `ADMIN`, `EXPERT`, or `RESEARCHER` | $N \ge 3$ distinct farms | `services/regional_pulse_service.py` L200 |
| **Create Researcher Draft** | Non-existent | `UNVALIDATED_OBSERVATION` | `RESEARCHER` | $N \ge 3$ distinct farms | `services/regional_pulse_service.py` L196 |
| **Create Confirmed Signal** | Non-existent | `EXPERT_CONFIRMED` | `AGRICULTURAL_EXPERT` or `ADMIN` | $N \ge 3$ distinct farms; `confidence_tier = 'EXPERT_REVIEWED'` | `services/regional_pulse_service.py` L198 |
| **Create State Advisory** | Non-existent | `OFFICIAL_ALERT` | `ADMIN` only | $N=0$ telemetry; `confidence_tier = 'OFFICIAL_ADVISORY'` | `services/regional_pulse_service.py` L71, L192 |
| **GET Revalidation (Failure)** | `EXPERT_CONFIRMED` / `UNVALIDATED_OBSERVATION` | `SUPPRESSED_INSUFFICIENT_PROVENANCE` | Any actor calling GET (staged in session) | Verified distinct farms $< 3$ (or empty evidence list) | `services/regional_pulse_service.py` L340, L379 |
| **GET Revalidation (Success)** | `EXPERT_CONFIRMED` / `UNVALIDATED_OBSERVATION` | Unchanged (`EXPERT_CONFIRMED` / `UNVALIDATED...`) | Any actor calling GET | Verified distinct farms $\ge 3$ | `services/regional_pulse_service.py` L385 |
| **Expert Recovery** | `SUPPRESSED_INSUFFICIENT_PROVENANCE` | `EXPERT_CONFIRMED` | `AGRICULTURAL_EXPERT` | Fresh revalidation verifies $N \ge 3$ | `services/regional_pulse_service.py` L285 |
| **Admin Recovery** | `SUPPRESSED_INSUFFICIENT_PROVENANCE` | `ADMIN_CONFIRMED` | `ADMIN` (non-expert) | Fresh revalidation verifies $N \ge 3$ | `services/regional_pulse_service.py` L287 |

---

## 7. RLS POLICY-COMPOSITION ANALYSIS

### 7.1 PostgreSQL Permissive Combining Rules (`SOURCE_INFERENCE`)
Generated in `backend/app/database/rls.py` lines 955–969:
- **Policy 1 (`regional_signals_public_read_policy`):**
  `AS PERMISSIVE FOR SELECT TO PUBLIC USING (ADMIN_BYPASS_SQL OR (distinct_farms_count >= 3 AND validation_status != 'SUSPENDED'))`
- **Policy 2 (`regional_signals_author_write_policy`):**
  `AS PERMISSIVE FOR ALL TO PUBLIC USING (write_expr) WITH CHECK (write_expr)`
  where `write_expr = ADMIN_BYPASS_SQL OR (current_setting('app.current_user_id', true) != '' AND EXISTS (SELECT 1 FROM user_roles ur WHERE ur.user_id::text = current_setting('app.current_user_id', true) AND ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')))`

Under PostgreSQL Documentation (Section 5.8):
1. `FOR ALL` applies to all SQL commands, including `SELECT`.
2. Permissive policies for the same command combine using logical **`OR`**:
   $$\text{Effective SELECT} = \text{Policy 1} \lor \text{Policy 2}$$
3. Consequence: Privileged actors (`ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER`) can SELECT **any row** that satisfies `write_expr`, completely bypassing the public read threshold (`distinct_farms_count >= 3`).
4. Ordinary farmers fail `write_expr` and can SELECT only rows satisfying `distinct_farms_count >= 3 AND validation_status != 'SUSPENDED'`.

---

## 8. FARMER-FACING PUBLIC-READ ELIGIBILITY ASSESSMENT

### 8.1 The Proposed Status Allowlist Dilemma (`SOURCE_INFERENCE`, `OWNER_DECISION_REQUIRED`)
If a future RLS policy replaces negative exclusion (`!= 'SUSPENDED'`) with a positive status allowlist:

```sql
validation_status IN ('EXPERT_CONFIRMED', 'ADMIN_CONFIRMED') AND distinct_farms_count >= 3
```

**Impact on Emitted States:**
1. **`UNVALIDATED_OBSERVATION` ($N \ge 3$):** Community signals with 3, 5, or 10 verified distinct farms that have not yet undergone expert review are **completely hidden from farmers**.
   - *Governance Question (Decision D-03):* Should unvalidated multi-farm crowd signals be publicly visible with an "Unverified" banner (Decision D-02 Option A), or hidden until an agronomist confirms them?
2. **`OFFICIAL_ALERT` ($N = 0$):** Official state government advisories have `distinct_farms_count = 0`.
   - Requiring $N \ge 3$ suppresses 100% of official government alerts from farmers!
   - *Governance Question (Decision D-01):* Official state advisories must be granted an explicit policy exception.
3. **Corrected Public Read Specification:**
   ```sql
   (
       (validation_status IN ('EXPERT_CONFIRMED', 'ADMIN_CONFIRMED') AND distinct_farms_count >= 3)
       OR
       (validation_status = 'OFFICIAL_ALERT' AND confidence_tier = 'OFFICIAL_ADVISORY' /* Governed by D-01 */)
       OR
       (validation_status = 'UNVALIDATED_OBSERVATION' AND distinct_farms_count >= 3 /* Governed by D-03 */)
   )
   ```

---

## 9. INTERNAL VERIFICATION AND RECOVERY AUTHORIZATION ASSESSMENT

### 9.1 Separation of Read Audiences (`DESIGN_RECOMMENDATION`)

| Audience | Target Operation | Required Status Visibility | Required Farm Count Scope | Required Evidence Access | State Modification Authority | Enforcement Mechanism |
|---|---|---|---|---|---|---|
| **1. Ordinary Farmer** | Public Read (`GET /signals`) | Confirmed signals + Official Advisories (D-01) | Strictly $N \ge 3$ (except D-01) | **NONE** (Filtered out) | Read-only | RLS `FOR SELECT` Policy |
| **2. Field Expert** | District Verification | Unvalidated, Suppressed, Confirmed | Any count | District evidence metadata | Transitions to `EXPERT_CONFIRMED` | District-scoped RLS + Service |
| **3. State Administrator** | Statewide Oversight | All statuses (inc. Suspended) | Any count | Statewide evidence metadata | Creates `OFFICIAL_ALERT`, Admin Recovery | `ADMIN_BYPASS_SQL` / Service |
| **4. Recovery Workflow** | `POST /signals/{id}/recover` | `SUPPRESSED_INSUFFICIENT_PROVENANCE` | Revalidates $N \ge 3$ | Verification-only evidence read | Reverts to `CONFIRMED` | Row-locked Service Transaction |
| **5. Suppression Review** | Audit / Diagnostics | `SUPPRESSED_INSUFFICIENT_PROVENANCE` | Measured $N < 3$ | Audit metadata | Flag for expert reinvestigation | AuditLog Service |
| **6. Background Verifier** | Out-of-band Revalidation | All statuses | Calculates distinct farms | Direct evidence counting | Updates count & status | Dedicated DB Principal (DB-AUTH-01) |
| **7. Anonymous Caller** | Web API | None | None | None | None | FastAPI `get_current_user` (401) |

---

## 10. EVIDENCE-ASSOCIATION VISIBILITY AND FARMER-READ IMPACT

### 10.1 End-to-End Execution Trace (`LOCAL_SOURCE_VERIFIED`)
In `backend/app/api/v1/endpoints/regional_pulse.py` and `backend/app/services/regional_pulse_service.py`:
1. Farmer queries `GET /regional-pulse/signals`.
2. Initial SELECT retrieves `RegionalSignal` row ($N \ge 3$).
3. Query executes `options(selectinload(RegionalSignal.evidences))`.
4. RLS on `regional_signal_evidences` filters out all rows for non-privileged actors (`RLS_FILTERS_ROW`).
5. SQLAlchemy populates `signal.evidences = []`.
6. Endpoint invokes `revalidate_signal_provenance(db, sig.id)`.
7. Line 338 checks `if not signal.evidences:`. Evaluating `True`, it stages `signal.distinct_farms_count = 0` and `signal.validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'`, returning `False`.
8. Endpoint filters out the signal (omits from list or raises 404).
9. **Descriptive Finding:** Maintained as `FARMER_READ_BLOCKED_BY_EVIDENCE_ASSOCIATION_RLS`.

---

## 11. GET-PATH PROVENANCE REVALIDATION AND TRANSACTION ANALYSIS

### 11.2 Three Distinct Outcomes (`SOURCE_INFERENCE`)
The audit formally separates three distinct outcomes of a GET request:

| Outcome | Description | Persistence to PostgreSQL | API Response Effect | Governing Concern |
|---|---|---|---|---|
| **A. Read-Response Denial** | Signal is valid in DB ($N=3$), but API skips it or raises 404 due to `is_valid == False`. | **No** (Database row unchanged) | Signal denied to farmer | `FARMER_READ_BLOCKED_BY_EVIDENCE_ASSOCIATION_RLS` |
| **B. Transient In-Memory Mutation** | Staged mutations in session are rolled back upon savepoint exit failure. | **No** (Rollback discards mutations) | Clean commit of read session | Savepoint Rollback Semantics |
| **C. Persistent Read Mutation** | A GET request by an authorized writer flushes and commits a suppression update. | **Yes** (Row mutated to $N=0$, `SUPPRESSED...`) | Permanently suppresses signal | `RES-PULSE-READ-01` |

---

## 12. SQLALCHEMY SAVEPOINT AND ORM STATE BEHAVIOR

### 12.1 Transaction Lifecycle (`SQLALCHEMY-DOCUMENTATION-CONFIRMED`)
1. **Pre-Savepoint State:** With `SessionLocal(autoflush=False)`, `db.begin_nested()` does not flush pending changes before issuing `SAVEPOINT sa_savepoint_X`.
2. **Exit Flush:** Exiting `with db.begin_nested():` calls `savepoint.commit()`, which flushes dirty entities before releasing the savepoint.
3. **Flush Exception:** When a farmer fails the RLS UPDATE policy, the update matches 0 rows, raising `StaleDataError` (or `42501 permission denied`).
4. **Savepoint Rollback & Expiration:**
   - The context manager executes `ROLLBACK TO SAVEPOINT sa_savepoint_X`.
   - SQLAlchemy calls `session.expire()` on the modified object.
   - **Critical Nuance:** Expiration does not manually restore in-memory fields; it marks them expired so subsequent access reloads the persisted state from the database.
5. **Outer Commit:** Lines 387–395 catch the exception and return `False`. The outer route executes `db.commit()` on an un-aborted session, committing a clean read transaction.

---

## 13. ORM DELETION AND POSTGRESQL FK CASCADE ANALYSIS

### 13.1 Deletion-Path Matrix (`LOCAL_SOURCE_VERIFIED`, `SOURCE_INFERENCE`)
Inspecting `RegionalSignal` and `RegionalSignalEvidence` across ORM and PostgreSQL engine layers:

| Deletion Path | Triggering Operation | ORM Child Deletion? | Database FK Cascade? | Child Table RLS Evaluated? | Evidence Retention Consequence |
|---|---|---|---|---|---|
| **1. Parent ORM Delete** | `session.delete(signal)` | **Yes** (Emits explicit child `DELETE`) | No (ORM deletes child first) | Yes (Evaluates child RLS) | **Child Evidence Destroyed** |
| **2. Child Orphan Removal** | `signal.evidences.remove(ev)` | **Yes** (Emits explicit child `DELETE`) | No | Yes (Evaluates child RLS) | **Child Evidence Destroyed** |
| **3. Direct SQL Parent Delete** | `DELETE FROM regional_signals` | No | **Yes** (`RI_FKey_cascade_del`) | **NO (`SECURITY_NOFORCE_RLS`)** | **Child Evidence Destroyed** |
| **4. Bulk ORM Parent Delete** | `delete(RegionalSignal)` | No | **Yes** (`RI_FKey_cascade_del`) | **NO** | **Child Evidence Destroyed** |
| **5. Direct SQL Child Delete** | `DELETE FROM regional_signal_evidences` | No | No | Yes (Denied by grants) | Blocked by `PRIVILEGE_CROSSWALK` |

### 13.2 PostgreSQL Engine Referential Integrity Internals
Under PostgreSQL source code (`src/backend/utils/adt/ri_triggers.c`):
- Foreign key cascade deletions are executed by internal trigger `RI_FKey_cascade_del`.
- The SPI execution plan runs with `SECURITY_NOFORCE_RLS`.
- The engine enforces referential integrity without evaluating child table RLS policies and without requiring table-level `DELETE` privileges on the child table.
- **Security Conclusion:** Foreign key cascade completely bypasses child-table append-only controls.

---

## 14. EVIDENCE-RETENTION DESIGN ALTERNATIVES

### 14.1 Comparison of Retention Models (`DESIGN_RECOMMENDATION`)

| Control Layer | Model 1: Operational Append-Only Evidence | Model 2: Controlled Lifecycle Deletion |
|---|---|---|
| **PostgreSQL Foreign Key** | Alter to `ON DELETE RESTRICT` | Retain `ON DELETE RESTRICT` (Admin override procedure) |
| **SQLAlchemy Relationship** | `cascade="save-update, merge, refresh-expire"` (Remove `delete, delete-orphan`) | Remove `delete-orphan`; require explicit lifecycle service |
| **SQL Table Grants** | Revoke `DELETE` on signals & evidences for all runtime roles | Revoke `DELETE` for runtime roles; grant to purge utility |
| **Signal Deletion Paradigm** | Soft-deletion only (`is_archived = True`) | Soft-deletion with 7-year retention purge |
| **Audit Logging** | Atomic mirror to append-only `AuditLog` | Comprehensive audit trail before purge execution |
| **Operational Trade-Off** | Relational rows persist permanently; storage growth | Requires periodic retention batch jobs |
| **Governance Status** | **RECOMMENDED PRIMARY (Pilot Phase 07)** | Future Enterprise Scale Pattern |

---

## 15. SQL PRIVILEGE VERSUS RLS CROSSWALK

### 15.1 Privilege Crosswalk Analysis (`LOCAL_SOURCE_VERIFIED`)
In `backend/app/database/rls.py`:
- `PRIVILEGE_CROSSWALK` marks `regional_signals` and `regional_signal_evidences` with `SELECT: True`, `INSERT: True`, `UPDATE: True`, `DELETE: False`.
- `generate_privilege_grants_ddl()` emits corresponding GRANTs/REVOKEs.
- **Migration Gap:** Migration `a1089411c87d` calls `generate_rls_ddl()`, but **never calls `generate_privilege_grants_ddl()`**.
- Table grants in Neon staging/production remain `LIVE_DATABASE_UNVERIFIED`.
- `DB-GRANT-APPLY-01` remains `PROPOSED — OWNER APPROVAL REQUIRED`.

---

## 16. WORKER DISPATCH AND EVENT-ARCHITECTURE ASSESSMENT

### 16.1 Feasibility Assessment (`LOCAL_SOURCE_VERIFIED`, `WRK-DISP-01`)
- Audit of `backend/app/tasks/run_riskcast_batch.py` confirms that in staging/production, tasks raise:
  `ProductionDispatchBlockedError: DISPATCH_NOT_CONFIGURED`.
- Zero Celery or Redis dispatch infrastructure is configured for Regional Pulse.
- **Dual-Write Vulnerability:** Direct post-commit queue publishing risks committing evidence changes while losing event dispatch on broker network failure.
- **Recommended Event Architecture:** Implement a **Transactional Outbox Table** (`outbox_events`) written in the same database transaction as evidence creation, polled by a dedicated relay process.

---

## 17. ACTOR IDENTITY AND TRUSTED-WRITER DEPENDENCIES

### 17.1 Identity Boundaries (`SOURCE_INFERENCE`, `RLS-ROLE-ASSIGNMENT-01`)
- All application web traffic connects as `acrevia_staging_app`.
- Actor identity relies on `app.current_user_id` and `app.is_admin` GUCs set by the application pool.
- `ADMIN_BYPASS_SQL` requires `SESSION_USER` in `('neondb_owner', 'acrevia_admin')`; application ADMINs do not bypass RLS.
- `User.roles` uses `lazy="joined"` (`LEFT OUTER JOIN`); a user loads cleanly even if association rows are filtered out by RLS (`User.roles = []`).
- Reconciling `RLS-ROLE-ASSIGNMENT-01` and `DB-AUTH-01` requires dedicated database roles or cryptographically signed session tokens.

---

## 18. OWNER DECISION AND GOVERNANCE TRACEABILITY MATRIX

| Recommendation | Security Rationale | Product / Governance Impact | Related Owner Decision | Evidence Required | Approval Status |
|---|---|---|---|---|---|
| **1. Official Advisory Public Read Exemption** | Prevents hiding official alerts ($N=0$) from farmers | Enables immediate public broadcast of government alerts | **`D-01`** | Owner option selection (A, B, or D) | `PENDING_OWNER_AUTHORIZATION` |
| **2. Regional Signal Terminology Standards** | Aligns credibility labels with actual confidence tiers | Clear UI presentation of source reliability | **`D-02`** | Owner option selection | `PENDING_OWNER_AUTHORIZATION` |
| **3. District-Scoped Expert Verification** | Restricts expert read/review authority to assigned district | Prevents statewide evidence and signal leakage | **`D-03`** | Owner option selection | `PENDING_OWNER_AUTHORIZATION` |
| **4. Database Role Segregation Architecture** | Eliminates shared-principal GUC impersonation risks | Segregates application pool from verifier and admin | **`DB-AUTH-01`** | Architecture option selection | `PENDING_OWNER_AUTHORIZATION` |
| **5. FK Cascade Removal (`ON DELETE RESTRICT`)** | Prevents accidental cascade-deletion of evidence records | Enforces relational evidence immutability | Data Retention Policy | Migration verification in Mode B | `PROPOSED_CONTROL` |
| **6. Removal of Mutations from GET Routes** | Eliminates write-on-read risks and read latency | Pure read idempotency; precomputed aggregates | `RES-PULSE-READ-01` | Service refactoring plan | `PROPOSED_CONTROL` |
| **7. Transactional Outbox for Background Verification**| Guarantees reliable asynchronous provenance checks | Enables reliable decoupled verification | `WRK-DISP-01` | Worker dispatch implementation | `PROPOSED_CONTROL` |

---

## 19. CANONICAL BLOCKER RECONCILIATION

All 15 canonical blocker identifiers are preserved with original definitions:

| # | Blocker ID | Canonical Description | Current Disposition | Evidence Classification | Release-Blocking Status |
|---|---|---|---|---|---|
| 1 | `RLS-WRITE-AUTH-01` | Blanket DML write authority on collaborative tables | OPEN | `LOCAL_SOURCE_VERIFIED` | BLOCKING |
| 2 | `RLS-ROLE-ASSIGNMENT-01` | Mutable GUC role escalation on `user_roles` | OPEN | `LOCAL_SOURCE_VERIFIED` | BLOCKING |
| 3 | `DB-AUTH-01` | Shared database principal boundary ambiguity | OPEN | `LOCAL_SOURCE_VERIFIED` | BLOCKING |
| 4 | `DB-CREDENTIAL-EXPOSURE-01` | Public repository database credential exposure | OPEN | `PUBLIC_SOURCE_VERIFIED` | BLOCKING (`CREDENTIAL_ROTATION_OUTSTANDING`) |
| 5 | `APP-ROLE-SELF-SELECT-01` | User role self-selection on registration | OPEN | `LOCAL_SOURCE_VERIFIED` | BLOCKING |
| 6 | `EXP-AUTH-01` | Unprotected expert/researcher endpoint authorization | OPEN | `LOCAL_SOURCE_VERIFIED` | BLOCKING |
| 7 | `CASCADE-ROLE-DEL-01` | Unrestricted role cascade deletion vulnerability | OPEN | `LOCAL_SOURCE_VERIFIED` | BLOCKING |
| 8 | `TENANT-MEMBERSHIP-01` | Incomplete tenant membership authorization boundary | OPEN | `LOCAL_SOURCE_VERIFIED` | BLOCKING |
| 9 | `OWNER-AUTH-01` | Superadmin bypass dependency on untrusted GUCs | OPEN | `LOCAL_SOURCE_VERIFIED` | BLOCKING |
| 10 | `DB-RLS-01` | Absence of FORCE RLS on sensitive relations | OPEN | `LOCAL_SOURCE_VERIFIED` | BLOCKING |
| 11 | `WRK-DISP-01` | Worker dispatch tenant context leakage | OPEN | `LOCAL_SOURCE_VERIFIED` | BLOCKING |
| 12 | `RES-PULSE-01` | Role-global evidence association visibility without district scoping | OPEN | `LOCAL_SOURCE_VERIFIED` | **BLOCKING (SEVERITY PRESERVED AT MEDIUM)** |
| 13 | `RES-PULSE-02` | READ COMMITTED multi-statement concurrency window | OPEN | `SQLALCHEMY-DOCUMENTATION-CONFIRMED` | BLOCKING |
| 14 | `GATE01-PROV-01` | Missing automated role-provisioning gateway | OPEN | `LOCAL_SOURCE_VERIFIED` | BLOCKING |
| 15 | `RES-PULSE-READ-01` | Write-on-read suppression mutation in GET endpoints | OPEN | `LOCAL_SOURCE_VERIFIED` | BLOCKING |

*Working Finding:* `FARMER_READ_BLOCKED_BY_EVIDENCE_ASSOCIATION_RLS` is tracked as a distinct read-availability defect.

---

## 20. RESIDUAL RISK RECONCILIATION

All five residual risks are preserved with original canonical definitions:
1. **`RES-PULSE-01` (Severity: `MEDIUM`):** Role-global evidence association visibility without district scoping.
2. **`RES-PULSE-02` (Severity: `MEDIUM`):** READ COMMITTED multi-statement snapshot/concurrency window.
3. **`RES-PRIMARY-ROUTING-01` (Severity: `MEDIUM`):** Primary database routing dependency for write-on-read operations.
4. **`RES-REPLICA-LAG-01` (Severity: `LOW`):** Potential stale visibility due to read replica lag.
5. **`RES-FREE-TEXT-01` (Severity: `LOW`):** PII exposure in author-controlled free-text fields.

---

## 21. FUTURE POSTGRESQL-SPECIFIC VERIFICATION PLAN (DESIGN ONLY)

Execution requires Project Owner approval of `GATE-02` through `GATE-05`. **Not executed in Mode A.**

| Test Area | Scenario Description | Required Engine | Required Role / Context | Expected Outcome | Failure Interpretation |
|---|---|---|---|---|---|
| **Status Contract** | Direct SQL INSERT of arbitrary status string | PostgreSQL 16 | `acrevia_staging_app` | Blocked if CHECK constraint installed | Fails if table remains unconstrained VARCHAR |
| **Public Read** | Farmer reads `EXPERT_CONFIRMED` signal ($N=3$) | PostgreSQL 16 | `app.current_user_id = farmer_uuid` | HTTP 200 (Signal visible, evidences omitted) | RLS policy composition failure |
| **Official Advisory** | Farmer reads official state alert ($N=0$) | PostgreSQL 16 | `app.current_user_id = farmer_uuid` | HTTP 200 (Advisory visible via D-01) | Suppressed if $N \ge 3$ blanket rule applied |
| **Cascade Deletion** | Direct SQL `DELETE FROM regional_signals` | PostgreSQL 16 | `acrevia_admin` | Blocked by FK RESTRICT | Child evidence destroyed if CASCADE active |
| **ORM Deletion** | `session.delete(signal)` via ORM | PostgreSQL 16 | `acrevia_staging_app` | Blocked by ORM cascade removal | ORM issues child DELETE before parent |
| **GET Idempotency** | 50 concurrent GET requests to suppressed signal | PostgreSQL 16 | Concurrent farmer sessions | Zero UPDATE statements issued | Race condition if revalidation active on GET |
| **Outbox Atomicity** | Commit evidence, kill worker broker | PostgreSQL 16 | Application pool | Outbox record committed; job durable | Dual-write failure if direct broker publish |

---

## 22. ADVERSARIAL COUNTERARGUMENTS AND ALTERNATIVE EXPLANATIONS

1. **Counterargument: "Why not keep `validation_status != 'SUSPENDED'` as it was originally written?"**
   - *Adversarial Challenge:* Negative exclusion permits unvalidated drafts (`UNVALIDATED_OBSERVATION`) with $N \ge 3$ to be publicly visible to farmers before any agronomist has reviewed the claim.
2. **Counterargument: "Why not grant farmers SELECT on `regional_signal_evidences` with a view masking sensitive columns?"**
   - *Adversarial Challenge:* In PostgreSQL RLS, column-level security is distinct from row-level security. Exposing the table risks leaking farm IDs and observation IDs, violating Pillar F aggregation privacy.
3. **Counterargument: "Does changing FK to `ON DELETE RESTRICT` completely prevent child deletion?"**
   - *Adversarial Challenge:* No. As proven in Workstream E, SQLAlchemy's `cascade="all, delete-orphan"` will emit explicit `DELETE FROM regional_signal_evidences` statements *before* deleting the parent, bypassing the database RESTRICT constraint unless the ORM relationship cascade is also modified.
4. **Counterargument: "Can a background worker completely eliminate database locks?"**
   - *Adversarial Challenge:* No. A background worker must acquire row-level locks (`SELECT ... FOR UPDATE`) when updating `distinct_farms_count` and `validation_status` to prevent concurrent write skew.

---

## 23. FINDINGS RANKED BY SEVERITY AND EVIDENCE CONFIDENCE

| Rank | Finding Identifier | Title | Severity | Confidence | Evidence Classification | Release Impact |
|---|---|---|---|---|---|---|
| 1 | `SEC-P07-STATUS-01` | Non-Existent Status Vocabulary in Proposed RLS | **CRITICAL** | HIGH | `LOCAL_SOURCE_VERIFIED` | Blocks Farmer Read Policy |
| 2 | `SEC-P07-CASCADE-01` | Foreign Key Cascade Destroys Evidence Rows | **HIGH** | HIGH | `LOCAL_SOURCE_VERIFIED` | Violates Evidence Immutability |
| 3 | `SEC-P07-SCOPE-01` | Un-scoped Global Expert/Researcher SELECT | **HIGH** | HIGH | `SOURCE_INFERENCE` | Reproduces `RES-PULSE-01` |
| 4 | `SEC-P07-WORKER-01` | Worker Dispatch Infeasibility under WRK-DISP-01 | **HIGH** | HIGH | `LOCAL_SOURCE_VERIFIED` | Infeasible in Staging/Prod |
| 5 | `SEC-P07-API-RLS-01`| Researcher POST Contract Mismatch | **MEDIUM** | HIGH | `LOCAL_SOURCE_VERIFIED` | Causes HTTP 500 on Insert |
| 6 | `SEC-P07-CHECK-01` | Inability of `WITH CHECK` to Enforce State Transitions | **MEDIUM** | HIGH | `STATIC-POLICY-INFERENCE` | Requires Service/Trigger |
| 7 | `SEC-P07-MIGR-01` | Privilege Grant Generator Callsite Absent | **MEDIUM** | HIGH | `LOCAL_SOURCE_VERIFIED` | `DB-GRANT-APPLY-01` Pending |

---

## 24. RELEASE-READINESS CONCLUSION

### Recommendation: `CONDITIONALLY_READY_FOR_OWNER_REVIEW`

**Justification:**
1. The technical preflight analysis, status-contract reconciliation, cascade deletion mechanics, and transaction lifecycle have been rigorously analyzed and documented under Mode A.
2. However, Phase 07 **cannot be released** and Mode B **cannot be authorized** until the Project Owner renders formal decisions on:
   - Decision D-01 (Official Advisory public read boundary).
   - Decision D-03 (Agronomic peer-review and unvalidated observation visibility).
   - Decision DB-AUTH-01 (Database principal role segregation).
   - Public database credential rotation (`DB-CREDENTIAL-EXPOSURE-01`).
   - Downstream gate authorizations (`GATE-02` through `GATE-05`).

---

## 25. EXACT LIMITATIONS AND OUTSTANDING EVIDENCE REQUESTS

1. **Mode A Boundary Limitations:**
   - No verification of live Neon database catalogs, active roles, or physical staging branches was performed.
   - All tests were conducted offline without PostgreSQL kernel verification.
2. **Outstanding Evidence Required for Mode B Transition:**
   - Formal owner sign-off on Decisions D-01, D-02, D-03, and DB-AUTH-01.
   - Verification of secret zeroization and credential rotation for `DB-CREDENTIAL-EXPOSURE-01`.
   - Attributable owner signature on `GATE-02` (Role Provisioning) and `GATE-03` (Migration Execution).

---
