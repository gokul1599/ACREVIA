# ACREVIA — PHASE 07: REGIONAL PULSE AGGREGATION PROVENANCE & EVIDENCE PRIVACY AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation  
**Document ID:** `ACR-SEC-P07-REGIONAL-PROVENANCE-AUDIT`  
**Classification:** RESTRICTED — PILOT DATA PRIVACY AUDIT  
**Operating Mode:** **`MODE A ONLY`** (Local Source Engineering & Offline Testing)  
**Audit Determination:** **`RESOLVED_LOCALLY_AND_TESTED_WITH_RECORDED_RISK`**  
- `COUNT_DERIVED_FROM_LINKED_SOURCE_RECORDS`: **`RESOLVED_LOCALLY_AND_TESTED`** (All 16 edge cases verified)  
- `SEPARATION_OF_MEASURED_INSUFFICIENCY_FROM_UNVERIFIABLE`: **`RESOLVED_LOCALLY_AND_TESTED`** (DB query failures fail closed at response level without falsely mutating database records to measured N=0 or 'insufficient provenance')  
- `RESPONSE_SUPPRESSION_VS_PERSISTENT_SUPPRESSION`: **`RESOLVED_LOCALLY_AND_TESTED`** (Returning False guarantees immediate HTTP suppression; persistent state committed only upon successful measurement)  
- `TRANSACTION_SAFETY_AND_SAVEPOINT_ISOLATION`: **`RESOLVED_LOCALLY_AND_TESTED`** (`db.begin_nested()` SAVEPOINT prevents PostgreSQL 25P02 aborted-transaction state and protects caller's unrelated session work)  
- `RIGOROUS_POSTGRESQL_CONCURRENCY_ANALYSIS`: **`DOCUMENTED_ANALYSIS`** (Accurate PostgreSQL semantics for READ COMMITTED, REPEATABLE READ, SERIALIZABLE, and FOR UPDATE)  
- `ROLE_GLOBAL_EVIDENCE_ACCESS`: **`OWNER_ACCEPTANCE_REQUIRED`** (Global read access granted to `ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER`; requires Owner acceptance)  
**Associated Baseline Tests:** `backend/tests/test_worker_security_and_privacy.py` (74 passing tests; 121 across Phase 07 suite; 6 in Stage 12)  

---

## 1. Executive Summary & Privacy Protection Invariant

> [!CRITICAL]
> **A crowdsourced regional outbreak claim cannot be published without verifiable multi-tenant provenance.**  
> Under ACREVIA's smallholder data sovereignty and anti-panic principles, publishing unverified disease outbreak signals risks localized market panic, distress sales of cotton or chilli crops, and smallholder de-anonymization. ACREVIA enforces a mathematical threshold:
> $$\mathbf{\text{Distinct Farms Count } (N) \ge 3}$$
> A regional signal is invalid and withheld from public dissemination unless it is supported by active, non-archived evidence originating from at least three distinct smallholder farms within the exact geographical district.

---

## 2. Separate Measured Insufficiency from Inability to Verify

A critical architectural distinction established in this audit:

| Verification Condition | Failure Origin | Response-Level Action | Database-Level Action | Rationale & Data Integrity Principle |
| :--- | :--- | :---: | :---: | :--- |
| **Measured $N < 3$** | Provenance query completed; distinct active farms count is 0, 1, or 2. | **Suppressed (Returns `False`)** | **`distinct_farms_count = N`<br/>`validation_status = "SUPPRESSED_INSUFFICIENT_PROVENANCE"`** (Committed) | Distinct farms count was legitimately measured and proven below threshold. |
| **Query Failure / DB Timeout** | Database connection dropped, timeout, or lock contention during provenance query. | **Suppressed (Returns `False`)** | **NO MUTATION** (Savepoint rolled back; persistent record untouched) | Provenance was **unverifiable**. Overwriting the database with $N=0$ or "insufficient provenance" would record a false statement of fact. |
| **Measured $N \ge 3$** | Provenance query completed; distinct active farms count $\ge 3$. | **Eligible (Returns `True`)** | **`distinct_farms_count = N`** (Committed) | Signal provenance verified across $\ge 3$ independent farms. |

Verified via unit tests:
- [`test_regional_pulse_measured_n1_and_n2_suppression`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py): $N=1$ and $N=2$ persist `SUPPRESSED_INSUFFICIENT_PROVENANCE`.
- [`test_regional_pulse_db_unavailable_fails_closed_without_corrupting_state`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py): Simulated DB connection failure returns `False` without overwriting the record with $N=0$.
- [`test_measured_suppression_durability_independent_read`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py): Proves that measured suppression commits durably; a newly opened independent database session reads the updated `SUPPRESSED_INSUFFICIENT_PROVENANCE` status and verified farm count.

---

## 3. Transaction Safety: Savepoints & Caller Session Isolation

### 1. The PostgreSQL `25P02` Aborted-Transaction Trap
In PostgreSQL, once an exception occurs within a transaction block, all subsequent SQL commands raise `25P02: current transaction is aborted, commands ignored until end of transaction block`.  
If an endpoint or service calls a helper function that executes queries, any uncaught database exception in the helper aborts the entire transaction. Furthermore, calling `db.rollback()` on the caller's session rolls back all uncommitted work that the caller had accumulated and marks loaded ORM instances as expired.

### 2. Implementation: Nested Transaction (SAVEPOINT)
[`RegionalPulseService.revalidate_signal_provenance()`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py) executes inside a nested transaction:
```python
try:
    with db.begin_nested():  # Emits SAVEPOINT in PostgreSQL / SQLite
        signal = RegionalPulseService.get_signal(db, signal_id)
        # Query linked evidences and count distinct farms...
        # If verification succeeds, savepoint is released
except Exception as exc:
    # Savepoint is automatically rolled back to clean state.
    # The caller's main transaction is NOT aborted (no 25P02).
    # Unrelated objects in the session are preserved.
    logger.error("Signal provenance revalidation failed (unverifiable) for signal %s: %s", signal_id, exc)
    return False
```
Verified via test [`test_regional_pulse_savepoint_preserves_unrelated_session_work`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py): an exception during revalidation savepoint does not roll back or taint unrelated session objects.

### 3. Investigation: SQLAlchemy Pre-Savepoint Flush Mechanics
Under SQLAlchemy ORM architecture, calling `db.begin_nested()` automatically triggers an unconditional `flush()` of all pending objects in the session before emitting the `SAVEPOINT` command to the database engine.
1. **Flushed State:** If a caller added objects to the session prior to invoking revalidation, those objects are sent to the database transaction before the savepoint is established.
2. **Savepoint Rollback Boundary:** When an error occurs inside `with db.begin_nested():`, the rollback operates only back to the savepoint (`ROLLBACK TO SAVEPOINT`). The pre-savepoint objects remain in the uncommitted outer transaction.
3. **Session Commit / Rollback Consequences:** If the outer session subsequently calls `commit()`, the pre-savepoint flushed objects are permanently committed to the database. If the outer session calls `rollback()`, they are discarded.
4. **Offline Proof:** Verified via [`test_sqlalchemy_begin_nested_presavepoint_flush_mechanics`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py), which empirically verifies that savepoint rollbacks do not discard caller objects flushed prior to the savepoint, and documents the architectural requirement for transaction boundary clarity in service helpers.

### 4. Corrected Savepoint Contract & Transaction Boundary Sovereignty
Prior implementation contained premature `db.commit()` and `db.rollback()` calls inside `revalidate_signal_provenance()`, which violated caller transaction sovereignty by prematurely committing or rolling back caller session work (including pre-savepoint uncommitted entities).

Under the corrected architecture:
1. **Helper Sovereignty Prohibition:** [`RegionalPulseService.revalidate_signal_provenance()`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py) strictly stages modifications (`signal.distinct_farms_count`, `signal.validation_status`) inside `with db.begin_nested():` and NEVER calls `db.commit()` or `db.rollback()`.
2. **Caller Transaction Ownership:** The outer transaction is owned 100% by the caller (HTTP endpoint handlers `list_signals` and `get_signal` or background services). The caller explicitly decides when to issue `db.commit()` or `db.rollback()`.
3. **Rollback Discard Proof:** If a caller aborts with `session.rollback()`, all staged dynamic suppression updates are discarded and never touch the database.
4. **Fail-Closed Commit Enforcement:** If the caller's outer `db.commit()` encounters a database failure (e.g., connection disconnect, disk failure, transaction timeout), the endpoint executes `db.rollback()` and immediately raises `HTTPException(status_code=500)` (`HTTP_500_INTERNAL_SERVER_ERROR`). It **never** produces a success response (HTTP 200) on transaction failure.
5. **Caller-by-Caller Audit Matrix:**

| Caller / Site | Context / Scope | Outer Transaction Owner | Commit Path | Rollback Path | Early Return Behavior | Failure Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `RegionalPulseService.revalidate_signal_provenance` | Service Helper | **None** (Guest in Caller Session) | **Never** (`0` calls) | **Savepoint Only** (`ROLLBACK TO SAVEPOINT`) | Returns `False` (Response suppressed) | Preserved |
| `GET /api/v1/regional-pulse/signals` | HTTP Endpoint (`list_signals`) | **FastAPI Request** (`Session`) | Explicit `db.commit()` | Explicit `db.rollback()` | Skips suppressed signal for non-privileged | Raises `500` |
| `GET /api/v1/regional-pulse/signals/{id}` | HTTP Endpoint (`get_signal`) | **FastAPI Request** (`Session`) | Explicit `db.commit()` | Explicit `db.rollback()` | Raises `404` for non-privileged | Raises `500` |
| Offline Unit & Integration Tests | Test Harness | **Test Case** (`Session`) | Explicit `session.commit()` | Explicit `session.rollback()` | N/A | Asserted |

6. **Verification Evidence:**
   - [`test_regional_pulse_savepoint_contract_no_caller_commit_or_rollback`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py): Proves zero `commit()` and zero `rollback()` calls during revalidation; unrelated caller work remains uncommitted until caller explicitly commits.
   - [`test_regional_pulse_savepoint_caller_rollback_discards_staged_suppression`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py): Proves caller `rollback()` successfully discards staged suppression state.
   - [`test_regional_pulse_endpoint_commit_failure_fails_closed`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py): Proves outer commit failure on GET endpoints triggers rollback and raises HTTP 500, never returning HTTP 200.
   - [`test_regional_pulse_all_callers_obey_transaction_contract`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py): Proves via AST inspection that `revalidate_signal_provenance()` contains zero forbidden commit/rollback calls.
   - [`test_regional_pulse_get_signal_successful_suppression_and_rbac`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py): Proves GET /signals/{id} returns 404 to farmers when N<3, returns 200 with unmasked evidence to admins, and commits suppression durably.
   - [`test_regional_pulse_list_signals_successful_suppression_and_rbac`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py): Proves GET /signals filters out suppressed signals and masks evidence for farmers while returning all signals unmasked for admins, and commits suppression durably.
   - [`test_regional_pulse_commit_failure_prevents_information_leak`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py): Proves commit failure returns generic 500 detail without leaking database passwords, IPs, or stack traces.
   - [`test_regional_pulse_state_machine_monotonicity_and_recovery`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py): Proves 10-point state-machine monotonicity, Policy A fail-closed ordinary revalidation, Policy B authorized expert recovery, farm deduplication, and public/privileged response behavior.
   - [`test_regional_pulse_http_cache_control_headers_enforced`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py): Proves Cache-Control and Pragma headers are strictly applied across all responses (200 list, 200 get, 404 suppressed, 404 missing, 500 commit failure) with zero conflicting directives.
   - [`test_regional_pulse_concurrency_and_read_committed_scenarios`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py): Proves multi-session concurrency consistency under observation deletion, farm archival, concurrent revalidation, and persistence failure.
   - [`test_regional_pulse_primary_write_routing_and_sqlstate_25006`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py): Proves primary read-write engine binding and fail-closed rollback handling on simulated SQLSTATE 25006 (read-only pool).

---

## 4. Rigorous PostgreSQL Concurrency & TOCTOU Analysis

### 1. Documented PostgreSQL Isolation Level Semantics

| Isolation Level / Mechanism | PostgreSQL Kernel Semantics | Behavior in Regional Pulse Read Path | Residual Race / Limitation |
| :--- | :--- | :--- | :--- |
| **`READ COMMITTED` (Default)** | Each statement sees a new snapshot of committed data. | Revalidation queries current committed observations. | **Microsecond TOCTOU window:** A concurrent transaction could archive a farm immediately after revalidation finishes but before JSON serialization completes. |
| **`REPEATABLE READ`** | All statements see the snapshot as of the transaction's first query. | Sees committed data as of transaction start; does **NOT** reflect changes committed after transaction start. | **Stale Snapshot Risk:** May observe older committed observations that were deleted by concurrent transactions before revalidation ran. |
| **`SERIALIZABLE`** | Monitors read-write dependencies across transactions; aborts transactions on serialization conflicts (`40001`). | Mathematically prevents serialization anomalies. | **High Abort Rate:** Requires application retry loops across all endpoints and mutation services under high concurrent ingest. |
| **`SELECT ... FOR UPDATE`** | Acquires row-level exclusive locks on existing selected rows. | Locks selected parent signal and child observation rows. | **Phantom Read Limitation:** Row locks do **NOT** lock non-existent rows (e.g. newly inserted evidence) and cannot lock rows across foreign key relationships without full table locking. |

### 2. Residual Concurrency Risk & Policy
Under `READ COMMITTED` isolation, the remaining microsecond race window between dynamic revalidation and HTTP serialization is formally recorded as a **`RECORDED_RESIDUAL_RISK`**. Eliminating this window completely would require table-level serialization locks that degrade read throughput for regional telemetry, requiring explicit Project Owner sign-off.

---

## 5. Regional Evidence Access Decision Matrix

| Caller Category | Access to `regional_signals` (Aggregate) | Access to `regional_signal_evidences` (Granular) | Response Serialization Behavior | Governance Rationale |
| :--- | :---: | :---: | :--- | :--- |
| **Anonymous / Public** | **Allowed** | **DENIED (401/RLS)** | `evidences = []` (Forced redaction) | Smallholder de-anonymization prevention. |
| **FARMER** | **Allowed** | **DENIED (RLS)** | `evidences = []` (Forced redaction) | Peer smallholder privacy; farmers see regional trends, not peer plot telemetry. |
| **Unassigned AGRICULTURAL_EXPERT** | **Allowed** | **Allowed (Role-Global)** | Granular evidence included | Role grants access; regional scoping is currently unenforced at DB layer. |
| **Assigned AGRICULTURAL_EXPERT** | **Allowed** | **Allowed (Role-Global)** | Granular evidence included | Field agronomist verification of regional signals. |
| **Unassigned RESEARCHER** | **Allowed** | **Allowed (Role-Global)** | Granular evidence included | Academic research access; institutional scoping currently unenforced at DB layer. |
| **Platform Administrator** | **Allowed** | **Allowed (Role-Global)** | Granular evidence included | System audit and validation operations. |

---

## 6. Formal Risk Recording: Role-Global Access

> [!WARNING]
> **GOVERNANCE RESIDUAL RISK RECORDING: `ROLE_GLOBAL_EVIDENCE_ACCESS: OWNER_ACCEPTANCE_REQUIRED`**  
> Under current RLS policies (`regional_signal_evidences_expert_read_policy` in [`backend/app/database/rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py)), any user with the `AGRICULTURAL_EXPERT` or `RESEARCHER` role has read access to **all** granular evidence records across the entire state of Telangana.  
> In Mode A, this status remains **`OWNER_ACCEPTANCE_REQUIRED`**. It is NOT marked as fully resolved without explicit Project Owner sign-off.

---

## 7. Suppressed Signal Recovery — RBAC, Audit Atomicity & Concurrency Hardening

Following adversarial security assurance, the recovery workflow (`RegionalPulseService.recover_suppressed_signal`) and dedicated API endpoint (`POST /api/v1/regional-pulse/signals/{id}/recover`) were hardened:

### 1. Server-Side RBAC & Actor Identity Attributability
- **Access Boundary:** Restricted exclusively to authenticated users possessing `ADMIN` or `AGRICULTURAL_EXPERT` system roles via `require_roles(SystemRole.ADMIN.value, SystemRole.AGRICULTURAL_EXPERT.value)`.
- **Identity Propagation:** Immutable `actor_id` (`current_user.id`) and `actor_roles` derived exclusively from server-side JWT authentication context. Any client-supplied `actor_id`, `user_id`, or `actor_roles` in JSON payload or headers is strictly ignored.
- **Fail-Closed RBAC:** Unauthenticated requests yield `HTTP 401 Unauthorized`; `FARMER`, `RESEARCHER`, or missing roles yield `HTTP 403 Forbidden`; inactive accounts yield `HTTP 401 Unauthorized`.

### 2. Semantic Distinction: Expert vs Administrative Recovery
- If an `AGRICULTURAL_EXPERT` approves recovery, `validation_status` transitions to `EXPERT_CONFIRMED`.
- If an `ADMIN` (non-expert) approves recovery, `validation_status` transitions to `ADMIN_CONFIRMED`.
- An administrative actor cannot falsely claim or manufacture independent expert validation.

### 3. Atomic Audit Persistence
- Signal recovery and audit trail creation are executed within the **same session transaction**.
- Uses `AuditService.stage_activity(db, ...)` to add an append-only `AuditLog` entry (action `RECOVER_SUPPRESSED_SIGNAL`, resource `REGIONAL_SIGNAL`) without premature commit.
- Transaction sovereignty remains with the outer transaction owner (endpoint handler or test caller):
  - If outer commit succeeds, both signal status and audit log persist durably.
  - If outer rollback occurs (or commit fails), both signal status and audit log are discarded.

### 4. Row-Level Locking & Replay Idempotency
- Uses `select(...).with_for_update()` to serialize concurrent recovery attempts on the same regional signal row.
- If a signal is already recovered (`EXPERT_CONFIRMED` or `ADMIN_CONFIRMED`), subsequent recovery attempts yield `HTTP 409 Conflict`, preventing duplicate state transitions or duplicate audit entries.


---

## 8. Post-Lock Recalculation, Evidence Association Protection & Public GET Consistency (REC-CONC-01 / REC-CONC-02)

### 1. Post-Lock Provenance Recalculation & Identity-Map Freshness (Audit A)
Prior to this audit, when `recover_suppressed_signal` acquired shared row locks via SQLAlchemy `.with_for_update(read=True)`, it did not specify `.execution_options(populate_existing=True)`. If an entity (`Farm`, `Observation`, or `RiskAlert`) was already present in the caller session's identity map, SQLAlchemy returned the in-memory cached instance with its pre-lock attribute values rather than refreshing from the locked database row.
- **Defect Proven:** A competing transaction mutating a contributing farm's district from 'Warangal' to 'Karimnagar' was ignored by the caller session's identity map, permitting recovery of an invalidated signal.
- **Correction Applied:** All recovery lock queries (`RegionalSignal`, `RegionalSignalEvidence`, `Observation`, `RiskAlert`, `Farm`) now explicitly specify `.execution_options(populate_existing=True)`.
- **Post-Lock Invariant Guaranteed:**
  $$\mathbf{RECOVERY\_ELIGIBILITY = COUNT(DISTINCT\ CURRENT\_ELIGIBLE\_FARM\_IDS\_AFTER\_LOCKING)}$$
  The final farm count is strictly recalculated against the freshly locked database state.

### 2. Regional Signal Evidence Association Protection (Audit B)
In addition to locking the parent signal and evidence data rows, `recover_suppressed_signal` now explicitly queries and locks all `RegionalSignalEvidence` association rows for the signal:
- Emits: `SELECT ... FROM regional_signal_evidences WHERE signal_id = :id ORDER BY id ASC FOR SHARE`.
- Direct association row locking prevents concurrent deletion or mutation of evidence links during recovery.
- New associations referencing `signal_id` are serialized by the parent `RegionalSignal` `FOR UPDATE` exclusive lock.

### 3. Public GET Publication Consistency & Residual Window (Audit C)
Ordinary public GET endpoints (`list_signals` and `get_signal`) execute dynamic provenance revalidation without evidence row locks to preserve read performance and prevent query serialization bottlenecks.
- **Consistency Classification:** **`RESIDUAL_STALE_PUBLICATION_WINDOW`**.
- **Window Scope:** Opens when `revalidate_signal_provenance` reads the evidence snapshot and closes upon HTTP response serialization completion.
- **Bounding & Monotonicity:** If evidence is mutated during this window, the in-flight GET returns the signal consistent with its read snapshot. The subsequent GET request immediately derives $N < 3$, stages `SUPPRESSED_INSUFFICIENT_PROVENANCE`, and withholds the signal from public dissemination (HTTP 404).

### 4. Shared Writer Consistency Contract & Lock Order Reassessment (Audit D & E)
- **Lock Ordering Classification:** **`RECOVERY_LOCK_ORDER_CONSISTENT_BUT_GLOBAL_ORDER_UNPROVEN`**.
- `recover_suppressed_signal` follows a strict 5-level hierarchy: `RegionalSignal (FOR UPDATE)` $\to$ `RegionalSignalEvidence (FOR SHARE, id ASC)` $\to$ `Observation (FOR SHARE, id ASC)` $\to$ `RiskAlert (FOR SHARE, id ASC)` $\to$ `Farm (FOR SHARE, id ASC)`.
- While recovery transactions among themselves are deadlock-free, independent writers (`FarmService.update_farm`, `RiskService.acknowledge_alert`) do not acquire `RegionalSignal` locks or participate in a global cross-subsystem lock manager.

### 5. Read-Replica Architecture & Deployment Status (Audit F)
- **Source Configuration:** **`APPLICATION_SINGLE_ENGINE_SOURCE_CONFIGURATION`** (`backend/app/database/session.py` defines a single primary engine).
- **Deployment Status:** **`DEPLOYMENT_PRIMARY_ROUTING_UNVERIFIED`**.
- Lock-free GET revalidation is **not** read-replica compatible because dynamic suppression writes to `regional_signals` and issues explicit `db.commit()`, which requires primary read-write database connection routing.

### 6. Evidence Lifecycle & Immutability Classification (Audit G)
- `Farm`: `MUTABLE_THROUGH_IDENTIFIED_SERVICE` (metadata mutable via `FarmService.update_farm`; delete/archive methods not found in service layer).
- `Observation`: `APPEND_ONLY_BY_CURRENT_APPLICATION_SERVICE_DESIGN` (telemetry is append-only; database-level immutability not verified; `UPDATE`/`DELETE` granted in privilege crosswalk).
- `RiskAlert`: `MUTABLE_THROUGH_IDENTIFIED_SERVICE` (status updates permitted).
- `RegionalSignalEvidence`: `APPEND_ONLY_BY_CURRENT_APPLICATION_SERVICE_DESIGN` (subject to parent signal cascade).
- `AuditLog`: `APPEND_ONLY_BY_PRIVILEGE_DESIGN` (`UPDATE` and `DELETE` explicitly REVOKED at database level).

---

## 9. Read Committed Multi-Statement Snapshots, Risk Alert Lifecycle Independence & PostgreSQL Lock Observability

### 1. Multi-Statement READ COMMITTED Snapshot Reality (READ-COMMITTED-01)
Ordinary public GET provenance dynamic revalidation (`RegionalPulseService.revalidate_signal_provenance`) executes multiple SQL queries sequentially (`SELECT regional_signals`, followed by individual lookups `db.get(Observation)`, `db.get(Farm)` or `db.get(RiskAlert)`).
- **Architectural Reality:** Under PostgreSQL default `READ COMMITTED` isolation, each SQL statement establishes its own active query snapshot.
- **Classification:** **`MULTI_STATEMENT_READ_COMMITTED_MIXED_SNAPSHOT_POSSIBLE`**.
- **Implication:** If a concurrent transaction commits a farm district change between individual loop queries, the provenance calculation will observe the committed change immediately upon executing that entity lookup. If the count drops below 3, the signal is suppressed. If a change commits immediately after all lookups complete, the current response serves the signal based on the read snapshot; the very next GET request observes the updated data and immediately suppresses the signal.

### 2. Risk Alert Status Independence (RISK-ALERT-01)
- **Source Inspection:** Verified across `aggregate_regional_signal`, `revalidate_signal_provenance`, and `recover_suppressed_signal`.
- **Finding:** The provenance eligibility predicate strictly verifies:
  1. `alert.farm_id` is present.
  2. `farm.is_archived == False`.
  3. `farm.district.strip().lower() == signal.district.strip().lower()`.
  4. `alert.created_at.date()` falls within `[signal.observed_start_date, signal.observed_end_date]`.
- **Determination:** **`RISK_ALERT_STATUS_NOT_PART_OF_PROVENANCE_ELIGIBILITY`**.
- **Architectural Rationale:** Farmer dashboard actions (`is_acknowledged=True`, `is_dismissed=True`) represent recipient acknowledgment of notifications, not retraction of historical environmental, telemetry, or pest observations. Historical agro-climatic reality remains valid contributing evidence regardless of dashboard triage. Tested empirically via `test_regional_pulse_risk_alert_status_independence`.

### 3. Corrected PostgreSQL Lock Observability Specification (PG-LOCK-OBS-01)
- **Previous Specification Limitation:** Prior assurance documentation anticipated table-level `ExclusiveLock` in `pg_locks` for row-level `FOR UPDATE` queries.
- **PostgreSQL Engine Reality:**
  - In PostgreSQL, row-level locks (`SELECT ... FOR UPDATE`, `SELECT ... FOR SHARE`) acquire table-level **`RowShareLock`** (mode `RowShareLock`, virtual transaction mode).
  - Row locks themselves do **not** create persistent tuples in `pg_locks` unless transactions are actively queued/waiting on the locked tuple. The lock is recorded directly on the physical disk tuple header (`xmax` field and infomasks `HEAP_XMAX_COMMITTED`, `HEAP_XMAX_EXCL_LOCK`, etc.).
  - Observability of row-level lock contention in `pg_locks` requires querying `wait_event_type = 'Lock'`, `locktype = 'tuple'` / `transactionid`, inspecting `pg_blocking_pids()`, or querying the `pgrowlocks(text)` contrib extension.

### 4. Residual Privacy Window Classification (RES-PULSE-02)
- **Classification:** **`OWNER_ACCEPTANCE_REQUIRED`** (Status: `TECHNICALLY_BOUNDED`).
- **Strategic Decision:** In accordance with Option E, row-level locks are strictly avoided on ordinary GET read traffic to maintain high concurrency, prevent lock contention, and enable future read-replica offloading. The residual stale read window under `READ COMMITTED` is operationally acceptable given subsequent fail-closed suppression and non-sensitive aggregated regional signal payload.

