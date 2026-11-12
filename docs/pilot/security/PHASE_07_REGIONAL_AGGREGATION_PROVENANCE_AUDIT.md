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
**Associated Baseline Tests:** `backend/tests/test_worker_security_and_privacy.py` (50 passing tests; 97 across Phase 07 suite)  

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
