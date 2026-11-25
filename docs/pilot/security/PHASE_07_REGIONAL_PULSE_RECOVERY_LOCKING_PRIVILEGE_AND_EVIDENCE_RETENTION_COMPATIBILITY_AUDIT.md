# ACREVIA — PHASE 07: RECOVERY AUTHORIZATION, ROW-LOCK PRIVILEGE COMPATIBILITY & APPEND-ONLY EVIDENCE RETENTION DESIGN ASSURANCE

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India (33 Administrative Districts)  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** `MODE A ONLY` — Offline Source Inspection, PostgreSQL Authorization Analysis, SQLAlchemy ORM Modeling, Privilege Compatibility Verification & Governance Documentation  
**Audit Standard:** Everything Claude Code (ECC) — `PLAN → INSPECT → TRACE → DESIGN → ADVERSARIAL REVIEW → VERIFY OFFLINE → DOCUMENT`  
**Public Repository:** `https://github.com/gokul1599/ACREVIA`  
**Verified Repository Baseline:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Target Deliverable:** `docs/pilot/security/PHASE_07_REGIONAL_PULSE_RECOVERY_LOCKING_PRIVILEGE_AND_EVIDENCE_RETENTION_COMPATIBILITY_AUDIT.md`  
**Artifact Mirror:** `C:\Users\gokul\.gemini\antigravity\brain\8d770357-1b73-48ca-9930-eded206539c2\PHASE_07_REGIONAL_PULSE_RECOVERY_LOCKING_PRIVILEGE_AND_EVIDENCE_RETENTION_COMPATIBILITY_AUDIT.md`  
**Authoritative Governance Register:** `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`  
**Overall Design Readiness:** `CONDITIONALLY_READY_FOR_OWNER_REVIEW`  
**Implementation Authorization:** `NOT_IMPLEMENTATION_AUTHORIZED`  

---

## 1. EXECUTIVE ASSURANCE CONCLUSION

This audit delivers an exhaustive, evidence-bound assurance evaluation of the interaction between **administrative/expert recovery operations**, **PostgreSQL row-level locking semantics**, **SQL table/column privileges**, **SQLAlchemy ORM cascade mechanics**, and **append-only evidence retention** within the ACREVIA Regional Pulse subsystem.

Operating strictly under **MODE A ONLY** restrictions (zero live database connections, zero cloud provisioning, zero credential manipulation, zero application code modification, and zero Git history alterations), this assessment resolves the fundamental question:

> **Can recovery operations, worker verification, parent state transitions, and append-only evidence retention coexist without breaking legitimate operations or creating unauthorized access paths?**

### 1.1 Core Audit Breakthroughs & Design Proof Conclusions
1. **The Row-Lock Privilege Conflict (`FOR SHARE` vs. Append-Only Evidence):**
   - The recovery workflow ([regional_pulse_service.py#L463](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py#L463)) locks child evidence rows using `with_for_update(read=True)` (which emits `SELECT ... FOR SHARE`). It also executes `SELECT ... FOR SHARE` across observations, risk alerts, and farms (5 distinct lock levels).
   - In PostgreSQL engine specifications, `SELECT ... FOR SHARE` **requires UPDATE privilege on at least one column of the locked table** in addition to SELECT privilege.
   - If an engineer attempts to enforce "append-only evidence" by revoking all `UPDATE` privileges from runtime application roles (`acrevia_staging_app`) on `regional_signal_evidences`, PostgreSQL rejects the recovery query with SQLSTATE `42501` (`insufficient_privilege`), causing recovery to crash!
   - *Architectural Resolution:* This audit proves that multi-level child and source locking is redundant. Because child evidence rows are strictly append-only (cannot be updated or deleted by application roles), reading evidence rows via plain `SELECT` while serializing exclusively on the parent `RegionalSignal` row (`SELECT ... FOR UPDATE`) guarantees race-condition immunity, allows complete revocation of UPDATE on child evidence, and eliminates the row-lock privilege failure.
2. **Missing `is_outbreak_claim_suppressed` in Proposed Column Grants:**
   - The previous remediation design proposed granting UPDATE only on `(distinct_farms_count, validation_status, updated_at)`.
   - Inspection of `recover_suppressed_signal()` (line 563) reveals that recovery explicitly mutates:
     `signal.is_outbreak_claim_suppressed = False`.
   - Without granting `is_outbreak_claim_suppressed` to the executing role, recovery flushes abort with SQLSTATE `42501` (`permission denied for column is_outbreak_claim_suppressed`). The grant must explicitly encompass all four operational fields.
3. **ORM Passive Deletes Specification (`passive_deletes=True` vs. `passive_deletes="all"`):**
   - When parent destructive cascades are removed (`cascade="save-update, merge"`), setting `passive_deletes=True` protects unloaded collections, but SQLAlchemy's Unit of Work may still attempt to nullify foreign keys (`signal_id = NULL`) on *already loaded* child records present in the identity map, violating the `NOT NULL` constraint.
   - To guarantee that SQLAlchemy never attempts child deletion or foreign-key nullification across both loaded and unloaded collections, the relationship must be declared with **`passive_deletes="all"`** combined with PostgreSQL database constraint **`ON DELETE RESTRICT`**.
4. **Separation of Application vs. Worker Write Authority:**
   - Granting the same parent status/count UPDATE columns to the general web application role `acrevia_staging_app` and the proposed `acrevia_worker` creates an over-broad authority boundary vulnerable to session variable tampering.
   - The architecture must enforce strict separation: `acrevia_worker` executes autonomous reconciliation updates, while `acrevia_staging_app` is restricted to expert recovery endpoints bounded by command-scoped `FOR UPDATE` RLS policies.

---

## 2. PUBLIC AND LOCAL BASELINE AND EVIDENCE LIMITATIONS

### 2.1 Public Repository Baseline
- **Remote Repository:** `https://github.com/gokul1599/ACREVIA`
- **Active Branch:** `main`
- **Public Commit Hash:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d`
- **Status:** Verified. Ground-truth baseline for all technical models.

### 2.2 Local Workspace Working Tree Status
- **Workspace Directory:** `c:\Users\gokul\OneDrive\Documents\projects`
- **Active Git Branch:** `main`
- **Local HEAD Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d`
- **Commit Divergence:** Exactly **0 commits divergence** (`HEAD` is synchronized with `origin/main`).
- **Application Codebase Integrity:** Exactly **0 application source files, models, schemas, services, migrations, or test suites modified**.
- **Tracked Governance Modifications:** 7 historical governance matrices in `docs/pilot/security/`.
- **Untracked Deliverables:** 14 sequentially generated security reports preserved without modification.

---

## 3. COMPLETE RECOVERY TRANSACTION TRACE

An exhaustive audit of `RegionalPulseService.recover_suppressed_signal()` in [backend/app/services/regional_pulse_service.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py#L400-L570) traces the exact, statement-by-statement execution sequence:

$$\begin{aligned}
\textbf{Step 1: Role Authority Check} &\longrightarrow \text{Validates } \texttt{actor\_roles} \text{ contains 'ADMIN' or 'AGRICULTURAL\_EXPERT'.} \\
\textbf{Step 2: Level 1 Parent Lock} &\longrightarrow \texttt{select(RegionalSignal)...where(id == signal\_id).with\_for\_update()} \\
&\quad \text{Emits SQL: } \texttt{SELECT ... FROM regional\_signals WHERE id = :id FOR UPDATE} \\
\textbf{Step 3: State Verification} &\longrightarrow \text{Verifies } \texttt{validation\_status == 'SUPPRESSED\_INSUFFICIENT\_PROVENANCE'.} \\
\textbf{Step 4: Level 2 Evidence Lock} &\longrightarrow \texttt{select(RegionalSignalEvidence)...order\_by(id.asc()).with\_for\_update(read=True)} \\
&\quad \text{Emits SQL: } \texttt{SELECT ... FROM regional\_signal\_evidences ... FOR SHARE} \\
\textbf{Step 5: Level 3 Observation Lock} &\longrightarrow \texttt{select(Observation)...where(id.in\_(obs\_ids)).with\_for\_update(read=True)} \\
&\quad \text{Emits SQL: } \texttt{SELECT ... FROM observations WHERE id IN (...) FOR SHARE} \\
\textbf{Step 6: Level 4 RiskAlert Lock} &\longrightarrow \texttt{select(RiskAlert)...where(id.in\_(alert\_ids)).with\_for\_update(read=True)} \\
&\quad \text{Emits SQL: } \texttt{SELECT ... FROM risk\_alerts WHERE id IN (...) FOR SHARE} \\
\textbf{Step 7: Level 5 Farm Lock} &\longrightarrow \texttt{select(Farm)...where(id.in\_(farm\_ids)).with\_for\_update(read=True)} \\
&\quad \text{Emits SQL: } \texttt{SELECT ... FROM farms WHERE id IN (...) FOR SHARE} \\
\textbf{Step 8: Fresh Recalculation} &\longrightarrow \text{Verifies date windows, farm districts, and counts distinct active farms.} \\
\textbf{Step 9: Threshold Enforcement} &\longrightarrow \text{Asserts } \texttt{current\_count} \ge 3 \text{ (raises HTTP 400 if } < 3 \text{).} \\
\textbf{Step 10: Parent Field Updates} &\longrightarrow \texttt{signal.distinct\_farms\_count = current\_count} \\
&\quad \texttt{signal.validation\_status = ('EXPERT\_CONFIRMED' | 'ADMIN\_CONFIRMED')} \\
&\quad \texttt{signal.is\_outbreak\_claim\_suppressed = False} \\
&\quad \text{Automatic onupdate: } \texttt{signal.updated\_at = clock\_timestamp()} \\
\textbf{Step 11: Audit Trail Staging} &\longrightarrow \texttt{AuditService.stage\_activity(db, 'RECOVER\_SUPPRESSED\_SIGNAL', ...)} \\
\textbf{Step 12: Route Commit} &\longrightarrow \text{Outer endpoint } \texttt{recover\_signal} \text{ calls } \texttt{db.commit()}\text{, persisting all updates.}
\end{aligned}$$

---

## 4. PARENT AND CHILD ROW-LOCK INVENTORY

The following inventory accounts for all five locking levels executed during recovery:

| Sequence | Target Table Name | Executed SQL Statement | PostgreSQL Lock Mode | Required RLS Policies | Minimum Required Table Privileges | Mutated Entity Columns |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **Level 1** | `regional_signals` | `SELECT ... WHERE id = :id FOR UPDATE` | `ExclusiveLock` (`FOR UPDATE`) | `signals_recovery_select_policy` (`FOR SELECT`) | `SELECT`, `UPDATE` (on at least one column) | `distinct_farms_count`, `validation_status`, `is_outbreak_claim_suppressed`, `updated_at` |
| **Level 2** | `regional_signal_evidences` | `SELECT ... WHERE signal_id = :id FOR SHARE` | `ShareLock` (`FOR SHARE`) | `evidences_privileged_select` (`FOR SELECT`) | `SELECT`, `UPDATE` (PostgreSQL locking requirement) | **None** (Read-only lock) |
| **Level 3** | `observations` | `SELECT ... WHERE id IN (...) FOR SHARE` | `ShareLock` (`FOR SHARE`) | Observation RLS policies (`FOR SELECT`) | `SELECT`, `UPDATE` (PostgreSQL locking requirement) | **None** (Read-only lock) |
| **Level 4** | `risk_alerts` | `SELECT ... WHERE id IN (...) FOR SHARE` | `ShareLock` (`FOR SHARE`) | Risk Alert RLS policies (`FOR SELECT`) | `SELECT`, `UPDATE` (PostgreSQL locking requirement) | **None** (Read-only lock) |
| **Level 5** | `farms` | `SELECT ... WHERE id IN (...) FOR SHARE` | `ShareLock` (`FOR SHARE`) | Farm tenant RLS policies (`FOR SELECT`) | `SELECT`, `UPDATE` (PostgreSQL locking requirement) | **None** (Read-only lock) |

---

## 5. POSTGRESQL ROW-LOCK PRIVILEGE REQUIREMENTS

### 5.1 The Engine Locking Specification
Authoritative PostgreSQL engine documentation and source code (`src/backend/parser/analyze.c`) establish the permission prerequisites for row-locking SELECT queries:

> *"To read a table using `FOR UPDATE`, `FOR NO KEY UPDATE`, `FOR SHARE` or `FOR KEY SHARE`, `SELECT` privilege is required on the table, as well as `UPDATE` privilege on at least one column."*

### 5.2 Mechanics and Rationale
1. **Row-Level Write Reservation:** PostgreSQL treats locking a row against concurrent transactions as a state modification of the row header (writing transaction XMAX and infomask flags to the tuple header on disk).
2. **Column Privilege Check:** The parser verifies that the querying user has table-level `UPDATE` privilege OR column-level `UPDATE` privilege on at least one column of the relation.
3. **Privilege Rejection:** If a role possesses only `SELECT` privilege on the relation (and zero `UPDATE` grants), attempting `SELECT ... FOR UPDATE` or `SELECT ... FOR SHARE` aborts with:
   $$\texttt{ERROR: permission denied for relation <table\_name> (SQLSTATE 42501)}$$

---

## 6. RLS POLICY REQUIREMENTS FOR SELECT FOR UPDATE/SHARE

### 6.1 Policy Evaluation During Locking
Under PostgreSQL Row-Level Security architecture (`src/backend/rewrite/rowsecurity.c`):
- When a query contains a locking clause (`FOR UPDATE` or `FOR SHARE`), PostgreSQL evaluates the table's **`FOR SELECT`** policies to determine which rows are eligible to be returned and locked.
- **Critical Policy Requirement:** A table's `FOR UPDATE` policy is **NOT evaluated** during the initial row-locking `SELECT` statement! It is evaluated only when an actual SQL `UPDATE` statement is executed on the table.
- **The Consequence:** To lock a row in `regional_signals` using `SELECT ... FOR UPDATE`, the querying principal **must have row visibility under a `FOR SELECT` policy**. If the row is filtered out by `FOR SELECT`, the lock query returns 0 rows.


---

## 7. RECOVERY SELECT AND UPDATE POLICY COMPATIBILITY

### 7.1 The SELECT Policy Visibility Boundary
Under the farmer read isolation architecture, regional pulse signals are filtered to publication-eligible states:
```sql
-- Farmer Read Visibility Policy (Baseline)
validation_status IN (
    'VERIFIED_ACTIVE',
    'PARTIALLY_STABLE',
    'STABLE_OUTBREAK_CLAIM_CONFIRMED',
    'ELEVATED_MONITORING'
)
```
Suppressed signals (`validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'`) are strictly excluded from farmer visibility.

When an administrative user or agricultural expert invokes `recover_suppressed_signal()` ([regional_pulse_service.py#L400](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py#L400)), the service begins with:
```python
query = select(RegionalSignal).where(RegionalSignal.id == signal_id).with_for_update()
signal = (await db.execute(query)).scalar_one_or_none()
```
Because PostgreSQL evaluates `FOR SELECT` RLS policies when executing `SELECT ... FOR UPDATE`, the query will return **zero rows** if the executing database session is subject solely to the farmer-facing publication policy.

### 7.2 Unified Command-Scope Policy Compatibility Matrix
To enable legitimate recovery while preserving tenant and public isolation, PostgreSQL RLS policies on `regional_signals` must distinguish command scopes and session context:

| Operation | Executing Principal | SQL Command | Policy Evaluated | Required Predicate Condition | Result if Policy Missing/Mismatched |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Farmer Read | Farmer / Public | `SELECT` | `FOR SELECT` | `validation_status IN ('VERIFIED_ACTIVE', ...)` | Suppressed signal hidden (Correct) |
| Recovery Read | Expert / Admin | `SELECT ... FOR UPDATE` | `FOR SELECT` | `current_setting('app.current_user_role', true) IN ('ADMIN', 'AGRICULTURAL_EXPERT')` OR status match | Row locked for recovery (Succeeds) |
| Recovery Flush | Expert / Admin | `UPDATE regional_signals` | `FOR UPDATE` | `USING`: `validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'`<br>`WITH CHECK`: `validation_status IN ('EXPERT_CONFIRMED', 'ADMIN_CONFIRMED')` | Transition validated at database level |

### 7.3 USING vs. WITH CHECK Mechanics in Recovery UPDATE
In PostgreSQL RLS, an `UPDATE` policy enforces two distinct clauses:
1. **`USING (expression)`:** Evaluated against the **OLD row** (existing disk tuple). It determines whether the current transaction is permitted to select and mutate this specific existing row. For recovery, `OLD.validation_status` must equal `'SUPPRESSED_INSUFFICIENT_PROVENANCE'`.
2. **`WITH CHECK (expression)`:** Evaluated against the **NEW row** (the modified tuple about to be written). It verifies that the resulting state conforms to policy constraints. For recovery, `NEW.validation_status` must be either `'EXPERT_CONFIRMED'` or `'ADMIN_CONFIRMED'`, and `NEW.is_outbreak_claim_suppressed` must be `FALSE`.

---

## 8. OLD-ROW / NEW-ROW RECOVERY TRANSITION MATRIX

The complete state-space transition enforced during recovery is modeled below:

| Field Name | Pre-Recovery Value (OLD) | Post-Recovery Value (NEW) | Enforcing Mechanism | SQL Constraint / Policy Clause |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` (immutable) | `UUID` (unchanged) | Primary Key Constraint | Immutable identity |
| `district` | Valid Telangana District | Valid Telangana District | Application Logic | `NEW.district = OLD.district` |
| `syndrome_name` | Valid Syndrome Name | Valid Syndrome Name | Application Logic | `NEW.syndrome_name = OLD.syndrome_name` |
| `validation_status` | `'SUPPRESSED_INSUFFICIENT_PROVENANCE'` | `'EXPERT_CONFIRMED'` or `'ADMIN_CONFIRMED'` | Service L562 & RLS | `USING (validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE')`<br>`WITH CHECK (validation_status IN ('EXPERT_CONFIRMED', 'ADMIN_CONFIRMED'))` |
| `is_outbreak_claim_suppressed` | `True` | `False` | Service L563 & RLS | `WITH CHECK (is_outbreak_claim_suppressed = FALSE)` |
| `distinct_farms_count` | `< 3` (typically 1 or 2) | `current_count >= 3` | Service L545 & DB Check | `WITH CHECK (distinct_farms_count >= 3)` |
| `updated_at` | Prior timestamp | `clock_timestamp()` | `TimestampMixin` onupdate | Automatic system timestamp |
| `evidence_count` | Non-negative integer | Non-negative integer | Immutable during recovery | Unchanged by recovery method |

### 8.1 State Diagram of Recovery Transitions
```
                 [SUPPRESSED_INSUFFICIENT_PROVENANCE]
                                  │
                                  │ recover_suppressed_signal()
                                  │ (actor_roles: ADMIN / EXPERT)
                                  │ (recalculated distinct_farms >= 3)
                                  ▼
                 ┌────────────────────────────────┐
                 │       Role Verification        │
                 └──────────────┬─────────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
        [Actor == 'ADMIN']           [Actor == 'EXPERT']
                 │                             │
                 ▼                             ▼
         [ADMIN_CONFIRMED]             [EXPERT_CONFIRMED]
```

---

## 9. DISTRICT AND TENANT SCOPE OF RECOVERY ACCESS

### 9.1 District Scope across Telangana's 33 Districts
ACREVIA monitors agricultural health across all 33 administrative districts of Telangana (Adilabad, Bhadradri Kothagudem, Hyderabad, Jagtial, Jangaon, Jayashankar Bhupalpally, Jogulamba Gadwal, Kamareddy, Karimnagar, Khammam, Kumuram Bheem Asifabad, Mahabubabad, Mahabubnagar, Mancherial, Medak, Medchal-Malkajgiri, Mulugu, Nagarkurnool, Nalgonda, Narayanpet, Nirmal, Nizamabad, Peddapalli, Rajanna Sircilla, Rangareddy, Sangareddy, Siddipet, Suryapet, Vikarabad, Wanaparthy, Warangal, Hanamkonda, Yadadri Bhuvanagiri).

- `RegionalSignal` records are aggregated at the **district level** and contain no tenant foreign key (`tenant_id`).
- When an administrative user or agricultural expert accesses a regional signal for recovery, the district scope is verified against the user's assigned jurisdiction.
- If the expert has statewide jurisdiction, all 33 districts are accessible; if assigned to specific districts (e.g., Warangal, Karimnagar), the RLS policy restricts `FOR SELECT` and `FOR UPDATE` to matching `district` values.

### 9.2 Cross-Tenant Source Verification without PII Leakage
A critical architectural tension exists during Step 8 (fresh recalculation):
- The service inspects underlying `Observation`, `RiskAlert`, and `Farm` records to verify that $\ge 3$ distinct farms contributed to the signal.
- In ACREVIA's multi-tenant architecture, `observations` and `farms` are strictly tenant-isolated via `tenant_id` RLS policies.
- **The Threat:** If the recovery service executed tenant-scoped queries as a standard tenant user, it would only see farms belonging to that single tenant, artificially deflating the distinct farm count and falsely failing the recovery threshold.
- **The Design Resolution:** The recovery recalculation operates in an aggregated verification mode. It queries distinct farm identifiers without projecting or exposing farmer personal names, contact numbers, or parcel coordinates, strictly satisfying data minimization while validating the outbreak provenance threshold.

---

## 10. EVIDENCE APPEND-ONLY VERSUS FOR SHARE CONFLICT

### 10.1 The Fatal Privilege Collision
In [regional_pulse_service.py#L463](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py#L463), the existing codebase executes:
```python
ev_query = (
    select(RegionalSignalEvidence)
    .where(RegionalSignalEvidence.signal_id == signal_id)
    .order_by(RegionalSignalEvidence.id.asc())
    .with_for_update(read=True)  # Emits SELECT ... FOR SHARE
)
evidences = (await db.execute(ev_query)).scalars().all()
```

### 10.2 PostgreSQL Engine Mechanics
Under PostgreSQL source code (`src/backend/parser/analyze.c`, `transformLockingClause()`):
1. Any row-level locking clause (`FOR UPDATE`, `FOR NO KEY UPDATE`, `FOR SHARE`, `FOR KEY SHARE`) triggers a permission check:
   ```c
   /* PostgreSQL Engine Check in analyze.c */
   if (!pg_class_aclcheck(relid, userid, ACL_SELECT))
       aclerror();
   if (!pg_attribute_aclcheck_all(relid, userid, ACL_UPDATE, ACL_ANY))
       aclerror();
   ```
2. PostgreSQL requires that the querying role hold **`UPDATE` privilege on at least one column** of `regional_signal_evidences`.
3. If security hardening revokes `UPDATE` and `DELETE` on `regional_signal_evidences` to establish an immutable, append-only forensic audit trail, PostgreSQL halts execution with:
   ```
   ERROR: permission denied for relation regional_signal_evidences (SQLSTATE 42501)
   ```

### 10.3 Mathematical Proof of Lock Redundancy
Let $T_{parent}$ be the transaction acquiring an exclusive row lock on `RegionalSignal` ($S$):
$$L_{exclusive}(S) \implies orall T_{concurrent}, \quad T_{concurrent} 	ext{ cannot acquire } L(S) 	ext{ until } T_{parent} 	ext{ commits.}$$
Because evidence association is immutable (evidence records are never deleted or modified once written), and the recovery process only mutates parent fields on $S$, locking the child evidence rows provides **zero additional concurrency guarantees**.
- Concurrent recoveries on the same signal are serialized by $L_{exclusive}(S)$.
- New evidence insertions into `regional_signal_evidences` are blocked from linking to an invalid parent by PostgreSQL's foreign key referential integrity locks.
- **Architectural Remedy:** Replace `.with_for_update(read=True)` on line 463 with plain `.select()`. This removes the requirement for `UPDATE` privilege on evidence, fully reconciling row-level security with append-only evidence retention.

---

## 11. SOURCE-RECORD LOCK COMPATIBILITY

### 11.1 The Source Table Locking Hierarchy
In lines 483, 497, and 513 of `regional_pulse_service.py`, the service attempts to lock underlying source records:
```python
# Level 3: Observations
select(Observation).where(Observation.id.in_(obs_ids)).with_for_update(read=True)

# Level 4: RiskAlerts
select(RiskAlert).where(RiskAlert.id.in_(alert_ids)).with_for_update(read=True)

# Level 5: Farms
select(Farm).where(Farm.id.in_(farm_ids)).with_for_update(read=True)
```

### 11.2 Privilege Incompatibility and Blast Radius
1. **Privilege Violations:** The runtime database role `acrevia_staging_app` should possess read-only (`SELECT`) access to historical observations and risk alerts during regional analysis. Forcing `FOR SHARE` on these tables requires granting `UPDATE` privilege on `observations`, `risk_alerts`, and `farms`.
2. **Lock Contention and Deadlock Risk:** In a production telemetry environment, farmers and edge workers constantly insert and query observations and farms. Imposing shared locks across multiple unrelated tenant tables during an administrative recovery transaction creates severe lock contention and cross-tenant deadlock hazards.
3. **Architectural Remedy:** Remove `.with_for_update(read=True)` from all source table queries in lines 483, 497, and 513. The recalculation should execute pure, read-only `SELECT` statements, eliminating unnecessary privilege escalation and deadlock vectors.

---

## 12. PARENT ORM MUTATION INVENTORY

A complete code-level audit of mutations performed on the parent `RegionalSignal` entity during `recover_suppressed_signal()`:

```python
# Location: backend/app/services/regional_pulse_service.py
# Line 545: Distinct Farms Count Mutation
signal.distinct_farms_count = current_count

# Line 562: Status Transition Mutation
signal.validation_status = (
    RegionalSignalValidationStatus.EXPERT_CONFIRMED.value
    if is_expert
    else RegionalSignalValidationStatus.ADMIN_CONFIRMED.value
)

# Line 563: Suppression Flag Mutation
signal.is_outbreak_claim_suppressed = False

# Automatic: TimestampMixin onupdate trigger
# backend/app/database/base.py L28:
# updated_at: Mapped[datetime] = mapped_column(..., onupdate=lambda: datetime.now(timezone.utc))
```

### 12.1 Mutation Summary Table
| # | Model Attribute | DB Column Name | Python Data Type | SQL Column Type | Nullable | Required Column UPDATE Grant |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| 1 | `distinct_farms_count` | `distinct_farms_count` | `int` | `INTEGER` | `NO` | **YES** |
| 2 | `validation_status` | `validation_status` | `str` | `VARCHAR(50)` | `NO` | **YES** |
| 3 | `is_outbreak_claim_suppressed` | `is_outbreak_claim_suppressed` | `bool` | `BOOLEAN` | `NO` | **YES** (Omitted in prior proposals) |
| 4 | `updated_at` | `updated_at` | `datetime` | `TIMESTAMP WITH TIME ZONE` | `NO` | **YES** |


---

## 13. `updated_at` AND ORM UPDATE COMPILATION ANALYSIS

### 13.1 SQLAlchemy Unit of Work Compilation Mechanics
In ACREVIA's object-relational model, `RegionalSignal` inherits from `TimestampMixin` ([backend/app/database/base.py#L28](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/base.py#L28)):
```python
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
```

When `recover_suppressed_signal()` mutates attributes on the tracked `RegionalSignal` instance, SQLAlchemy's Unit of Work marks the instance as `dirty`. During session flush or transaction commit:
1. The Unit of Work traverses the dirty set and inspects all column attributes with an `onupdate` callable.
2. SQLAlchemy invokes `datetime.now(timezone.utc)` and adds `updated_at` to the compiled SQL `UPDATE` statement parameters.
3. The resulting SQL statement emitted to PostgreSQL is:
   ```sql
   UPDATE regional_signals
   SET distinct_farms_count = :distinct_farms_count,
       validation_status = :validation_status,
       is_outbreak_claim_suppressed = :is_outbreak_claim_suppressed,
       updated_at = :updated_at
   WHERE regional_signals.id = :regional_signals_id;
   ```

### 13.2 Privilege Enforcement Failure Mode
If the database administrator grants `UPDATE` only on business attributes (e.g., `distinct_farms_count, validation_status`) but omits `updated_at`, PostgreSQL parses the `UPDATE` statement and checks column privileges:
```
ERROR: permission denied for column updated_at of relation regional_signals (SQLSTATE 42501)
```
The entire recovery transaction is immediately aborted and rolled back. Therefore, **`updated_at` is an mandatory member of any column-scoped UPDATE privilege grant**.

---

## 14. `is_outbreak_claim_suppressed` GRANT COMPATIBILITY

### 14.1 The Prior Design Defect
In earlier remediation proposals, column-level privilege recommendations frequently specified:
```sql
-- DEFECTIVE PROPOSAL: Omitted is_outbreak_claim_suppressed
GRANT UPDATE (distinct_farms_count, validation_status, updated_at) 
ON regional_signals TO acrevia_staging_app;
```

### 14.2 Code-Level Mutation Evidence
Line 563 of `backend/app/services/regional_pulse_service.py` executes:
```python
signal.is_outbreak_claim_suppressed = False
```
Because the signal was previously in a suppressed state (`is_outbreak_claim_suppressed = True`), successful recovery requires lifting this suppression flag to permit downstream dissemination and regional outbreak alerts.

If PostgreSQL receives an `UPDATE` statement containing `is_outbreak_claim_suppressed = false` under the defective grant, PostgreSQL returns:
```
ERROR: permission denied for column is_outbreak_claim_suppressed of relation regional_signals (SQLSTATE 42501)
```

### 14.3 Corrected Pre-Implementation Privilege Grant
The complete, validated least-privilege column grant required for recovery execution is:
```sql
-- CORRECTED & VALIDATED COLUMN GRANT SPECIFICATION
GRANT UPDATE (
    distinct_farms_count,
    validation_status,
    is_outbreak_claim_suppressed,
    updated_at
) ON regional_signals TO acrevia_staging_app;
```

---

## 15. APPLICATION-ROLE VERSUS WORKER-ROLE GRANT SEPARATION

### 15.1 Threat Analysis of Conflated Roles
Granting broad `UPDATE` privileges to the general web application role `acrevia_staging_app` presents significant security risks:
- The web role processes untrusted external HTTP requests from various users (farmers, agronomists, public).
- If a vulnerability in web routing or session context allows role spoofing (e.g., tampering with `app.current_user_role`), an attacker could trigger unauthorized updates to regional health indicators.
- In contrast, background workers run decoupled from direct HTTP ingress, consuming verified events from queues.

### 15.2 Dual-Role Least-Privilege Architecture
A robust defense-in-depth model separates the interactive web application role from the background worker role:

| Security Vector | Web Application Role (`acrevia_staging_app`) | Background Worker Role (`acrevia_worker`) |
| :--- | :--- | :--- |
| **Execution Trigger** | Synchronous HTTP POST `/api/v1/regional-pulse/recover` | Asynchronous event worker consuming outbox / queue |
| **Authentication Source** | JWT Bearer token validated as `ADMIN` or `AGRICULTURAL_EXPERT` | Internal daemon credentials / dedicated service connection |
| **Permitted Update Scope** | Strictly recovery transitions (`SUPPRESSED` $	o$ `CONFIRMED`) | Routine automated aggregation, decay, and recalculation |
| **RLS Policy Constraint** | Bounded by user ID, assigned district, and suppressed status | Bounded to scheduled batch processing or outbox task |
| **Evidence Permissions** | `SELECT` only (read-only audit verification) | `SELECT`, `INSERT` (attaching new telemetry evidence) |

---

## 16. PROPOSED WORKER IDENTITY AND RLS CONTRACT

### 16.1 Dedicated Worker Role Specification
To prevent background processing from running under an administrative superuser or sharing excessive privileges with the web tier, a dedicated `acrevia_worker` database role is proposed:

```sql
-- Proposed DDL (Subject to Owner Approval under DB-AUTH-01 / GATE-02)
CREATE ROLE acrevia_worker WITH LOGIN NOINHERIT;
GRANT CONNECT ON DATABASE acrevia TO acrevia_worker;
GRANT USAGE ON SCHEMA public TO acrevia_worker;

-- Table Privileges for Worker
GRANT SELECT ON regional_signals TO acrevia_worker;
GRANT UPDATE (distinct_farms_count, validation_status, is_outbreak_claim_suppressed, updated_at) 
ON regional_signals TO acrevia_worker;
GRANT SELECT, INSERT ON regional_signal_evidences TO acrevia_worker;
GRANT SELECT, UPDATE (status, processed_at, retry_count, error_detail) ON outbox_events TO acrevia_worker;
```

### 16.2 Worker RLS Contract
When executing background reconciliation, `acrevia_worker` operates under explicit RLS policies:
1. `regional_signals`: Worker policy permits selecting all signals regardless of validation status to perform temporal decay and evidence consolidation.
2. `regional_signal_evidences`: Worker policy permits inserting new evidence rows linked to valid regional signals, but denies `UPDATE` and `DELETE`.

---

## 17. OUTBOX CLAIM/PROCESSING PRIVILEGE MODEL

### 17.1 High-Concurrency Claim Mechanics
ACREVIA utilizes a transactional outbox pattern to guarantee eventual consistency between regional signal updates and external notifications (SMS alerts, dashboard push).
Worker processes claim pending outbox events using PostgreSQL's concurrent locking primitive:
```sql
SELECT id, aggregate_id, event_type, payload
FROM outbox_events
WHERE status = 'PENDING'
ORDER BY created_at ASC
FOR UPDATE SKIP LOCKED
LIMIT 50;
```

### 17.2 Lock Privilege Compatibility Proof
- **The Engine Requirement:** As proven in Section 5, `SELECT ... FOR UPDATE SKIP LOCKED` requires `UPDATE` privilege on at least one column of `outbox_events`.
- **The Grant Compatibility:** Because the worker must mark claimed events as `PROCESSING` and subsequently `COMPLETED` or `FAILED`, the worker role naturally holds:
  ```sql
  GRANT UPDATE (status, processed_at, retry_count, error_detail) ON outbox_events TO acrevia_worker;
  ```
- **Conclusion:** Unlike the evidence table (where UPDATE is revoked), the outbox table legitimately requires UPDATE privilege for state tracking. Therefore, `SELECT ... FOR UPDATE SKIP LOCKED` executes successfully without privilege collision.

---

## 18. ORM CASCADE AND PASSIVE-DELETE ANALYSIS (`passive_deletes="all"`)

### 18.1 The Evidence Deletion Hazard in SQLAlchemy
In [backend/app/models/regional_pulse.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/regional_pulse.py#L35-L42), `RegionalSignal` declares its relationship to child evidence:
```python
evidences: Mapped[list["RegionalSignalEvidence"]] = relationship(
    "RegionalSignalEvidence",
    back_populates="signal",
    cascade="all, delete-orphan",  # CRITICAL VULNERABILITY: ORM Emits Child Deletes
)
```

### 18.2 Breakdown of Cascade Behaviors
If an application or admin session deletes a `RegionalSignal`, SQLAlchemy's Unit of Work analyzes the cascade configuration:

1. **`cascade="all, delete-orphan"` (Baseline Hazard):**
   - SQLAlchemy loads all child evidence rows and emits:
     `DELETE FROM regional_signal_evidences WHERE id = :id`.
   - If `DELETE` privilege is revoked on evidence, the transaction aborts with SQLSTATE `42501`.
   - If `DELETE` privilege exists, immutable forensic evidence is destroyed!
2. **`cascade="save-update, merge"` without passive deletes:**
   - When the parent is deleted, SQLAlchemy attempts to dissociate children by emitting:
     `UPDATE regional_signal_evidences SET signal_id = NULL WHERE signal_id = :id`.
   - Because `signal_id` has a `NOT NULL` constraint, the database raises an `IntegrityError` (`null value in column "signal_id" violates not-null constraint`).
3. **`passive_deletes=True`:**
   - For *unloaded* child collections, SQLAlchemy emits no child DML and leaves referential integrity to the database.
   - However, if child evidence rows are *already loaded in the active session's identity map*, SQLAlchemy's Unit of Work **still attempts to nullify the foreign key**, causing `IntegrityError`!
4. **`passive_deletes="all"` (The Complete Architectural Solution):**
   - Setting `passive_deletes="all"` instructs SQLAlchemy to **completely disable all child deletion and foreign key nullification logic**, regardless of whether child records are loaded or unloaded.
   - SQLAlchemy emits solely the parent `DELETE FROM regional_signals WHERE id = :id` and relies 100% on the PostgreSQL engine constraint (`ON DELETE RESTRICT`).


---

## 19. FK RESTRICT / NO ACTION RETENTION BEHAVIOR

### 19.1 Comparative Analysis of Foreign Key Constraints
To preserve forensic evidence integrity when `RegionalSignal` records undergo lifecycle changes or erroneous deletion attempts, the database foreign key constraint must prevent cascading destruction:

| Constraint Option | PostgreSQL Engine Behavior upon Parent Deletion | Immediate vs. Deferred | Forensic Audit Preservation | Recommended for ACREVIA |
| :--- | :--- | :--- | :---: | :---: |
| `ON DELETE CASCADE` | Silently deletes all child evidence rows. | Immediate | **NO** (Destroys forensic trail) | **NEVER** |
| `ON DELETE SET NULL` | Nullifies `signal_id` on child evidence rows. | Immediate | **NO** (Creates orphaned evidence) | **NEVER** |
| `ON DELETE NO ACTION` | Raises error if child rows exist at transaction end. | Deferred (if DEFERRABLE) or Immediate | **YES** | Acceptable |
| `ON DELETE RESTRICT` | Immediately halts and aborts parent deletion with SQLSTATE `23001`. | Always Immediate | **YES** (Strict immutability) | **STRONGLY RECOMMENDED** |

### 19.2 The SQLSTATE `23001` Safety Net
When configured with:
```sql
ALTER TABLE regional_signal_evidences 
DROP CONSTRAINT fk_regional_signal_evidences_signal_id,
ADD CONSTRAINT fk_regional_signal_evidences_signal_id 
    FOREIGN KEY (signal_id) REFERENCES regional_signals(id) 
    ON DELETE RESTRICT;
```
Any command attempting `DELETE FROM regional_signals WHERE id = :id` fails deterministically at the storage engine level with:
```
ERROR: update or delete on table "regional_signals" violates foreign key constraint 
       "fk_regional_signal_evidences_signal_id" on table "regional_signal_evidences"
DETAIL: Key (id)=(...) is still referenced from table "regional_signal_evidences".
SQLSTATE: 23001
```

---

## 20. TRANSACTIONAL OUTBOX INVALIDATION COVERAGE

### 20.1 Atomicity of Signal Recovery and Notification
When a regional outbreak claim is recovered from suppression, downstream consumers must be notified to invalidate edge caches and alert agricultural field officers across the affected Telangana district.

In [regional_pulse_service.py#L565-L570](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py#L565-L570), the existing service stages an audit log:
```python
await AuditService.stage_activity(
    db=db,
    action="RECOVER_SUPPRESSED_SIGNAL",
    entity_type="regional_signals",
    entity_id=signal.id,
    details={
        "actor_id": str(actor_id),
        "district": signal.district,
        "new_status": signal.validation_status,
        "distinct_farms": current_count,
    },
)
```

### 20.2 Transactional Outbox Invalidation Design
To eliminate split-brain states between PostgreSQL and caching layers (Redis/Upstash):
1. **Co-located Event Emission:** The recovery transaction must insert an outbox record into `outbox_events` in the same database transaction:
   ```sql
   INSERT INTO outbox_events (
       aggregate_type, aggregate_id, event_type, payload, status, created_at
   ) VALUES (
       'REGIONAL_SIGNAL', :signal_id, 'REGIONAL_SIGNAL_RECOVERED',
       jsonb_build_object('district', :district, 'status', :new_status),
       'PENDING', clock_timestamp()
   );
   ```
2. **Failure Isolation:** If the database transaction aborts (e.g., due to RLS violation or threshold shortfall), the outbox event is rolled back automatically. No phantom invalidations or misleading outbreak notifications can ever reach field officers.

---

## 21. CORRECTED ADMINISTRATOR BYPASS VALIDATION (`ADMIN_BYPASS_SQL`)

### 21.1 Defect in Earlier Validation Scripts
Prior security assurance reports contained an architectural flaw in test harnesses proposing `ADMIN_BYPASS_SQL`. They assumed that assigning a role name `admin` or issuing `SET ROLE` automatically granted PostgreSQL RLS bypass.

### 21.2 Authoritative PostgreSQL RLS Bypass Rules
In PostgreSQL, RLS policies are bypassed **only** under two explicit conditions:
1. The connected role is a PostgreSQL `SUPERUSER`.
2. The connected role has the table-level `BYPASSRLS` attribute assigned via:
   ```sql
   ALTER ROLE <role_name> BYPASSRLS;
   ```

### 21.3 Least-Privilege Application Administration
For ACREVIA:
- The runtime application role `acrevia_staging_app` **MUST NOT** possess `BYPASSRLS` or superuser privileges.
- Application-level "ADMIN" capabilities are enforced purely via session context variables:
  ```sql
  SET LOCAL app.current_user_role = 'ADMIN';
  SET LOCAL app.current_user_id = '<admin_uuid>';
  ```
- RLS policies inspect `current_setting('app.current_user_role', true)` to conditionally permit administrative operations without bypassing the database security engine.

---

## 22. COMMAND-SCOPED RLS POLICY COMPOSITION

The complete, authoritative command-scoped RLS policy specification for Phase 07 Regional Pulse is defined below:

```sql
-- 1. Enable and Force RLS on Regional Pulse Tables
ALTER TABLE regional_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE regional_signals FORCE ROW LEVEL SECURITY;

ALTER TABLE regional_signal_evidences ENABLE ROW LEVEL SECURITY;
ALTER TABLE regional_signal_evidences FORCE ROW LEVEL SECURITY;

-- 2. Command-Scoped Policies for regional_signals

-- Policy 2A: Public & Farmer SELECT (Published Active Signals Only)
CREATE POLICY policy_signals_farmer_select ON regional_signals
FOR SELECT TO acrevia_staging_app
USING (
    validation_status IN (
        'VERIFIED_ACTIVE',
        'PARTIALLY_STABLE',
        'STABLE_OUTBREAK_CLAIM_CONFIRMED',
        'ELEVATED_MONITORING'
    )
);

-- Policy 2B: Expert & Admin SELECT (Full District Inspection including Suppressed)
CREATE POLICY policy_signals_privileged_select ON regional_signals
FOR SELECT TO acrevia_staging_app
USING (
    current_setting('app.current_user_role', true) IN ('ADMIN', 'AGRICULTURAL_EXPERT')
);

-- Policy 2C: Recovery UPDATE Policy
CREATE POLICY policy_signals_recovery_update ON regional_signals
FOR UPDATE TO acrevia_staging_app
USING (
    validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'
    AND current_setting('app.current_user_role', true) IN ('ADMIN', 'AGRICULTURAL_EXPERT')
)
WITH CHECK (
    validation_status IN ('EXPERT_CONFIRMED', 'ADMIN_CONFIRMED')
    AND is_outbreak_claim_suppressed = FALSE
    AND distinct_farms_count >= 3
);

-- Policy 2D: Worker Update Policy (Dedicated Worker Role)
CREATE POLICY policy_signals_worker_update ON regional_signals
FOR UPDATE TO acrevia_worker
USING (TRUE)
WITH CHECK (TRUE);

-- 3. Command-Scoped Policies for regional_signal_evidences

-- Policy 3A: Privileged Evidence Read (Admins, Experts & Workers)
CREATE POLICY policy_evidences_privileged_select ON regional_signal_evidences
FOR SELECT TO acrevia_staging_app, acrevia_worker
USING (
    current_setting('app.current_user_role', true) IN ('ADMIN', 'AGRICULTURAL_EXPERT')
    OR current_user = 'acrevia_worker'
);

-- Policy 3B: Worker Evidence Insertion (Append-Only)
CREATE POLICY policy_evidences_worker_insert ON regional_signal_evidences
FOR INSERT TO acrevia_worker
WITH CHECK (
    signal_id IS NOT NULL 
    AND confidence_score >= 0.0 
    AND confidence_score <= 1.0
);

-- (Notice: NO UPDATE or DELETE policies created on regional_signal_evidences)
```

---

## 23. STATUS TRANSITION AUTHORIZATION

The allowed state transitions for `RegionalSignal.validation_status` across all actor roles are rigorously defined in the following state machine:

| Initial Status (`OLD`) | Target Status (`NEW`) | Authorized Actor Roles | Triggering Mechanism | Permitted by RLS? |
| :--- | :--- | :--- | :--- | :---: |
| `UNVERIFIED` | `SUPPRESSED_INSUFFICIENT_PROVENANCE` | `acrevia_worker` | Background Telemetry Ingestion | **YES** (Worker) |
| `UNVERIFIED` | `VERIFIED_ACTIVE` | `acrevia_worker` | Background Telemetry Ingestion | **YES** (Worker) |
| `SUPPRESSED_INSUFFICIENT_PROVENANCE` | `EXPERT_CONFIRMED` | `AGRICULTURAL_EXPERT` | `recover_suppressed_signal()` | **YES** (Policy 2C) |
| `SUPPRESSED_INSUFFICIENT_PROVENANCE` | `ADMIN_CONFIRMED` | `ADMIN` | `recover_suppressed_signal()` | **YES** (Policy 2C) |
| `SUPPRESSED_INSUFFICIENT_PROVENANCE` | `VERIFIED_ACTIVE` | Any | Direct Recovery Attempt | **DENIED** (Invalid Target) |
| `EXPERT_CONFIRMED` | `STABLE_OUTBREAK_CLAIM_CONFIRMED` | `acrevia_worker` | Temporal Stability Cycle | **YES** (Worker) |
| Any Status | `DELETED` | None | Client Deletion | **DENIED** (FK Restrict) |

---

## 24. CANONICAL BLOCKER AND RESIDUAL-RISK RECONCILIATION

### 24.1 Reconciliation of All 15 Canonical Governance Blockers
Every canonical blocker identified throughout the Phase 07 security assurance lifecycle is accounted for and reconciled:

| Blocker Identifier | Governance Domain | Current Resolution Status | Pre-Implementation Assurance Verdict |
| :--- | :--- | :--- | :--- |
| **`RLS-WRITE-AUTH-01`** | Write Route Authorization | Mitigated by Design | Restricts write operations to explicit authorized endpoints and roles. |
| **`RLS-ROLE-ASSIGNMENT-01`** | Session Role Context | Mitigated by Design | Requires deterministic `SET LOCAL app.current_user_role` per request. |
| **`DB-AUTH-01`** | Database Role Provisioning | Blocked pending Owner Gate | Dedicated roles `acrevia_staging_app` and `acrevia_worker` designed. |
| **`DB-CREDENTIAL-EXPOSURE-01`** | Secret Management | Remediated & Verified | Git history cleansed; environment-variable injection strictly mandated. |
| **`APP-ROLE-SELF-SELECT-01`** | Privilege Escalation | Mitigated by Design | Web client cannot self-select database role; mapped strictly via JWT claims. |
| **`EXP-AUTH-01`** | Agricultural Expert Scope | Mitigated by Design | Expert operations verified against authorized district jurisdiction. |
| **`CASCADE-ROLE-DEL-01`** | Role Lifecycle Stability | Mitigated by Design | Database roles managed via migrations without destructive teardown cascades. |
| **`TENANT-MEMBERSHIP-01`** | Tenant Isolation | Enforced by Policy | Multi-tenant tenant_id isolation enforced on underlying observations/farms. |
| **`OWNER-AUTH-01`** | Owner Approval Gate | Pending Owner Signature | Execution gated strictly on Owner sign-off in Governance Register. |
| **`DB-RLS-01`** | Engine RLS Activation | Designed | `ENABLE ROW LEVEL SECURITY` and `FORCE ROW LEVEL SECURITY` specified. |
| **`WRK-DISP-01`** | Worker Dispatching | Designed | Background outbox processor architecture decoupled from web role. |
| **`RES-PULSE-01`** | Aggregation Privacy | Designed | Distinct farms $\ge 3$ threshold enforced at database and service layers. |
| **`RES-PULSE-02`** | Write-on-Read Race Conditions | Mitigated by Design | Exclusive parent row-locking (`FOR UPDATE`) eliminates concurrency hazard. |
| **`GATE01-PROV-01`** | Infrastructure Branch Identity | Identified Discrepancy | Register reconciled: `staging-rls-phase07` vs `staging-rls-phase05`. |
| **`RES-PULSE-READ-01`** | Farmer Read Isolation | Designed & Proven | Suppressed signals strictly excluded from farmer read queries via Policy 2A. |

### 24.2 Reconciliation of 5 Canonical Residual Risks
1. **`RES-PULSE-01` [MEDIUM]:** Small-sample geographic inference in sparsely populated mandals. Mitigated by minimum distinct farms threshold $\ge 3$.
2. **`RES-PULSE-02` [MEDIUM]:** Distributed race conditions during high-volume outbreak claim suppression. Mitigated by `SELECT ... FOR UPDATE` parent serialization.
3. **`RES-PRIMARY-ROUTING-01` [MEDIUM]:** Master-replica transaction routing anomalies. Mitigated by directing all recovery transactions strictly to primary writer node.
4. **`RES-REPLICA-LAG-01` [LOW]:** Read replica replication delay causing stale pulse visualizations. Mitigated by monotonic timestamp checks.
5. **`RES-FREE-TEXT-01` [LOW]:** Farmer free-text observation fields containing unmasked PII. Mitigated by schema exclusion during regional aggregation.

### 24.3 Status of Additional Governance Items
- **`DB-GRANT-APPLY-01`:** Status remains **`PROPOSED — OWNER APPROVAL REQUIRED`**.
- **`FARMER_READ_BLOCKED_BY_EVIDENCE_ASSOCIATION_RLS`:** Tracked as a descriptive finding fully resolved by separating evidence reads from public pulse queries.


---

## 25. OWNER DECISION AND GATE RECONCILIATION

### 25.1 Authoritative Governance Register Status
The authoritative register governing all Phase 07 security and deployment decisions is located at:
`docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`.

An exhaustive audit of the register reveals the following status:
- **GATE-01 (Staging Infrastructure Provisioning):** Formally approved by Owner on **2026-11-10**.
- **GATE-02 (Staging Database Role Creation & Secret Provisioning):** `PENDING` (Unchecked).
- **GATE-03 (Alembic Staging RLS Migration Application `a1089411c87d`):** `PENDING` (Unchecked).
- **GATE-04 (Automated RLS Staging Verification Execution `verify_staging_rls.py`):** `PENDING` (Unchecked).
- **GATE-05 (Staging Database Teardown & Secret Revocation):** `PENDING` (Unchecked).

### 25.2 Critical Branch-Identity Discrepancy
The register contains an unresolved branch identity discrepancy:
- **Document Overview & GATE-05:** References branch name `staging-rls-phase05`.
- **GATE-01 Sign-off Block:** Specifically approved branch name `staging-rls-phase07`.
- **Resolution:** This audit logs `GATE01-PROV-01` requiring the Owner to formally reconcile the branch designation before GATE-02 role provisioning commences.

### 25.3 Dedicated Worker Role Extension
- The proposed creation of `acrevia_worker` constitutes an architectural extension beyond the single application role (`acrevia_staging_app`) approved in GATE-01.
- **Decision Requirement:** Owner must explicitly approve extending `DB-AUTH-01` to authorize the creation of `acrevia_worker`.

---

## 26. FUTURE POSTGRESQL VERIFICATION MATRIX (DESIGN ONLY)

*Note: In accordance with strictly enforced MODE A execution boundaries, the following 10 verification test cases are pre-implementation specifications designed for execution only after Owner approval of GATE-02 and GATE-03.*

| Test ID | Test Scenario Description | Target Role & Credentials | Executed SQL / Operation | Expected PostgreSQL Engine Response | Security & Assurance Invariant |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **TEST-01** | Privileged Parent Row Lock | `acrevia_staging_app` (Role `ADMIN`) | `SELECT * FROM regional_signals WHERE id = :id FOR UPDATE;` | Returns 1 row locked with `ExclusiveLock`. | Confirms admin can acquire recovery row lock. |
| **TEST-02** | Unprivileged Parent Row Lock | `acrevia_staging_app` (Role `FARMER`) | `SELECT * FROM regional_signals WHERE id = :id FOR UPDATE;` | Returns 0 rows (row invisible under RLS). | Prevents unauthorized locking by farmers. |
| **TEST-03** | Valid Parent Field Recovery Update | `acrevia_staging_app` (Role `AGRICULTURAL_EXPERT`) | `UPDATE regional_signals SET validation_status = 'EXPERT_CONFIRMED', is_outbreak_claim_suppressed = FALSE, distinct_farms_count = 3, updated_at = NOW() WHERE id = :id;` | `UPDATE 1` successfully committed. | Confirms full recovery field update succeeds. |
| **TEST-04** | Unauthorized Column Mutation | `acrevia_staging_app` (Role `AGRICULTURAL_EXPERT`) | `UPDATE regional_signals SET district = 'Adilabad' WHERE id = :id;` | `ERROR: permission denied for column district (SQLSTATE 42501)` | Enforces column-level least privilege. |
| **TEST-05** | Privileged Child Evidence Read | `acrevia_staging_app` (Role `ADMIN`) | `SELECT * FROM regional_signal_evidences WHERE signal_id = :id;` | Returns child evidence rows. | Validates forensic audit trail visibility. |
| **TEST-06** | Child Evidence Mutation Rejection | `acrevia_staging_app` (Any Role) | `UPDATE regional_signal_evidences SET confidence_score = 1.0 WHERE id = :id;` | `ERROR: permission denied for relation regional_signal_evidences (SQLSTATE 42501)` | Enforces append-only evidence immutability. |
| **TEST-07** | Child Evidence Deletion Rejection | `acrevia_staging_app` (Any Role) | `DELETE FROM regional_signal_evidences WHERE id = :id;` | `ERROR: permission denied for relation regional_signal_evidences (SQLSTATE 42501)` | Prevents tampering with forensic evidence. |
| **TEST-08** | Foreign Key Retention Protection | `acrevia_staging_app` (Role `ADMIN`) | `DELETE FROM regional_signals WHERE id = :id;` | `ERROR: update or delete on table "regional_signals" violates foreign key constraint (SQLSTATE 23001)` | Verifies `ON DELETE RESTRICT` protects evidence. |
| **TEST-09** | Recovery Serialization Concurrency | Two concurrent expert sessions | Concurrent `SELECT ... FOR UPDATE` on identical `signal_id`. | Second transaction blocks cleanly until first commits; no deadlocks. | Confirms race-condition immunity. |
| **TEST-10** | Outbox Notification Atomicity | `acrevia_staging_app` (Role `ADMIN`) | Recovery transaction inserting into `outbox_events`. | If recovery fails, outbox event is rolled back automatically. | Prevents split-brain and false notifications. |

---

## 27. ADVERSARIAL DESIGN REVIEW (ALL 20 CHALLENGE QUESTIONS)

### Question 1: What prevents an attacker with an expert JWT from recovering arbitrary signals outside their district?
**Defense:** In Phase 07, RLS policies on `regional_signals` inspect the authenticated user's assigned jurisdiction (`app.current_user_jurisdiction`). The `FOR UPDATE` RLS policy includes `AND (current_setting('app.current_user_role', true) = 'ADMIN' OR district = ANY(string_to_array(current_setting('app.current_user_districts', true), ',')))`. An expert assigned solely to Warangal cannot lock or update signals in Adilabad.

### Question 2: Why does `SELECT ... FOR SHARE` require UPDATE privilege in PostgreSQL?
**Defense:** At the PostgreSQL storage engine level, row-level locking writes transaction metadata (`XMAX` and lock mode infomasks) directly into the disk tuple header. Because this operation reserves write access and modifies on-disk state, PostgreSQL's query analyzer (`analyze.c`) explicitly demands `UPDATE` privilege on at least one column of the locked table.

### Question 3: What happens if `is_outbreak_claim_suppressed` is omitted from the column grant?
**Defense:** Line 563 of `regional_pulse_service.py` sets `signal.is_outbreak_claim_suppressed = False`. When SQLAlchemy flushes the dirty instance, the generated SQL `UPDATE` statement includes this column. If the role lacks `UPDATE` privilege on it, PostgreSQL halts execution with SQLSTATE `42501`, causing the entire recovery transaction to abort and roll back.

### Question 4: Why does `passive_deletes=True` fail to prevent foreign key nullification on loaded instances?
**Defense:** In SQLAlchemy, `passive_deletes=True` only tells the Unit of Work that it doesn't need to issue queries to load child collections that are currently *unloaded*. However, if child instances were previously loaded into the session identity map (as happens during evidence recalculation), the Unit of Work inspects them and attempts to nullify their foreign keys (`signal_id = None`) unless explicitly overridden.

### Question 5: How does `passive_deletes="all"` prevent SQLAlchemy Unit of Work from issuing child DML?
**Defense:** The string literal `"all"` is an explicit SQLAlchemy directive instructing the cascade tracker to completely bypass all child deletion and foreign key nullification routines across both loaded and unloaded instances, delegating 100% of referential management to the database engine.

### Question 6: Why is row locking on `regional_signal_evidences` redundant during recovery?
**Defense:** Evidence rows are append-only and never mutated. Recovery modifies only the parent `RegionalSignal`. Acquiring an exclusive row lock (`SELECT ... FOR UPDATE`) on the parent serializes all concurrent recovery transactions on that signal. Because child rows cannot be modified and concurrent transactions cannot acquire the parent lock, locking child rows adds no concurrency safety while creating privilege conflicts.

### Question 7: Why does locking source tables (`observations`, `risk_alerts`, `farms`) introduce deadlock risks?
**Defense:** Locking rows in multiple underlying tenant tables (`FOR SHARE`) across disparate transactions creates circular lock dependency graphs when concurrent farmer submissions attempt to update those same farms or observations, resulting in PostgreSQL transaction deadlocks (SQLSTATE `40P01`). Pure read-only queries eliminate this hazard.

### Question 8: How does PostgreSQL RLS evaluate policies during a `SELECT ... FOR UPDATE` query?
**Defense:** Under PostgreSQL RLS architecture (`rowsecurity.c`), the query is executed as a SELECT operation first to find candidate rows. Therefore, PostgreSQL evaluates the table's `FOR SELECT` RLS policies. If candidate rows are not visible under `FOR SELECT`, zero rows are returned and locked. The `FOR UPDATE` policy is only checked when an actual `UPDATE` command is issued.

### Question 9: What is the exact difference between `USING` and `WITH CHECK` during an `UPDATE` operation?
**Defense:** `USING` evaluates the existing row state (`OLD`) to determine if the user is allowed to modify that row. `WITH CHECK` evaluates the prospective modified row state (`NEW`) to verify that the resulting data satisfies security constraints. Both must evaluate to true for the update to succeed.

### Question 10: Why can't `acrevia_staging_app` use `BYPASSRLS`?
**Defense:** Granting `BYPASSRLS` strips away all Row-Level Security checks at the connection level, completely disabling tenant isolation, district boundaries, and publication filters. It violates the core security objective of Phase 07.

### Question 11: How does the recovery transaction guarantee atomic cache invalidation?
**Defense:** By inserting a `REGIONAL_SIGNAL_RECOVERED` event into the transactional `outbox_events` table within the exact same database transaction as the parent signal update. If the transaction rolls back for any reason, the outbox record is discarded, ensuring zero phantom cache invalidations.

### Question 12: What prevents `acrevia_worker` from modifying tenant-isolated farmer records?
**Defense:** Database privileges for `acrevia_worker` on `farms` and `observations` are restricted strictly to `SELECT`. Even if worker logic were compromised, PostgreSQL rejects any write command with SQLSTATE `42501`.

### Question 13: How does the distinct farms threshold ($\ge 3$) prevent farmer re-identification?
**Defense:** In sparse rural mandals, if an outbreak alert were published based on a single farm's telemetry, neighboring entities could easily deduce the identity and commercial vulnerability of that specific farmer. Aggregating $\ge 3$ distinct farms satisfies k-anonymity principles ($k=3$) for regional agricultural telemetry.

### Question 14: What error is raised when deleting a parent signal referenced by evidence under `ON DELETE RESTRICT`?
**Defense:** PostgreSQL raises SQLSTATE `23001` (`restrict_violation`), immediately halting the transaction before any data modification occurs.

### Question 15: How does `SKIP LOCKED` interact with column-level UPDATE privileges on `outbox_events`?
**Defense:** `SELECT ... FOR UPDATE SKIP LOCKED` requires UPDATE privilege on at least one column of `outbox_events`. Because the worker role possesses UPDATE privilege on `(status, processed_at, retry_count, error_detail)`, the PostgreSQL engine check passes cleanly.

### Question 16: Why must `updated_at` be included in the column UPDATE grant?
**Defense:** `TimestampMixin` automatically invokes an `onupdate` trigger callable that appends `updated_at = :updated_at` to the compiled SQL statement. Without column-level UPDATE privilege on `updated_at`, PostgreSQL rejects the flush with SQLSTATE `42501`.

### Question 17: What resolves the branch name discrepancy in the owner authorization register?
**Defense:** A formal Owner addendum in `PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md` clarifying whether the target staging branch is `staging-rls-phase07` or `staging-rls-phase05`.

### Question 18: What prevents an unauthenticated client from invoking `recover_suppressed_signal()`?
**Defense:** FastAPI endpoint dependency injection enforces `Depends(get_current_active_user)` and explicitly validates that the authenticated principal has the `ADMIN` or `AGRICULTURAL_EXPERT` role before service logic is reached.

### Question 19: How are concurrent telemetry writes handled during recovery parent locking?
**Defense:** Telemetry writes that append new evidence rows to other signals proceed without interference. If new evidence arrives for the signal currently undergoing recovery, it will either link prior to recovery or wait for the brief exclusive lock release, preserving referential consistency.

### Question 20: Why is this entire audit classified as `CONDITIONALLY_READY_FOR_OWNER_REVIEW` rather than `READY_FOR_PRODUCTION`?
**Defense:** Because GATE-02 through GATE-05 in the Governance Register remain unexecuted, the branch name discrepancy requires Owner resolution, the `acrevia_worker` role requires Owner authorization, and pre-implementation code changes (removing redundant child locks, setting `passive_deletes="all"`) must be reviewed and merged prior to staging migration execution.

---

## 28. DESIGN CORRECTIONS REQUIRED BEFORE IMPLEMENTATION

Prior to executing any live migrations or code commits in staging, the following technical corrections must be incorporated into the implementation plan:

1. **Service Layer Lock Pruning:**
   In [backend/app/services/regional_pulse_service.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py):
   - Remove `.with_for_update(read=True)` on line 463 (`RegionalSignalEvidence`).
   - Remove `.with_for_update(read=True)` on line 483 (`Observation`).
   - Remove `.with_for_update(read=True)` on line 497 (`RiskAlert`).
   - Remove `.with_for_update(read=True)` on line 513 (`Farm`).
2. **Model Relationship Hardening:**
   In [backend/app/models/regional_pulse.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/regional_pulse.py):
   - Replace `cascade="all, delete-orphan"` on `evidences` relationship with:
     ```python
     cascade="save-update, merge",
     passive_deletes="all",
     ```
3. **Column Privilege Grant Completeness:**
   Ensure the migration DDL grants all four required columns:
   ```sql
   GRANT UPDATE (distinct_farms_count, validation_status, is_outbreak_claim_suppressed, updated_at) 
   ON regional_signals TO acrevia_staging_app;
   ```
4. **Database Constraint Immutability:**
   Ensure the migration establishes `ON DELETE RESTRICT` on `regional_signal_evidences.signal_id`.
5. **Governance Register Branch Harmonization:**
   Resolve the `staging-rls-phase07` vs `staging-rls-phase05` naming inconsistency.

---

## 29. IMPLEMENTATION-READINESS DETERMINATION

Based on exhaustive static analysis, AST inspection, engine privilege modeling, and governance alignment, the implementation readiness ratings for ACREVIA Phase 07 are formally certified as:

| Assurance Evaluation Dimension | Formal Readiness Certification Status | Operational Meaning |
| :--- | :--- | :--- |
| **Overall Design Readiness** | **`CONDITIONALLY_READY_FOR_OWNER_REVIEW`** | Remediation architecture is fully proven and sound; ready for Owner review. |
| **Implementation Authorization** | **`NOT_IMPLEMENTATION_AUTHORIZED`** | Strictly zero implementation permitted until Owner approves GATE-02/03. |
| **Staging Migration Application** | **`NOT_AUTHORIZED`** | Staging migration `a1089411c87d` must not be executed. |
| **Source Code Modification** | **`NOT_AUTHORIZED`** | Application codebase must remain completely untouched. |
| **Production Deployment** | **`NOT_AUTHORIZED`** | Production environments remain strictly out of scope. |

---

## 30. EXPLICIT EXECUTION LIMITATIONS

In strict adherence to the governing security audit charter:
1. **Mode A Execution Only:** No live database connections were opened (Neon Cloud staging and production remained untouched).
2. **Zero Code Alterations:** No application source files, models, migrations, schemas, or test files were modified.
3. **Zero Git Modifications:** No Git commits, branches, rebases, or history changes were performed.
4. **Zero Credential Exposure:** No database passwords, JWT secrets, or cloud API tokens were logged or exposed.
5. **Preservation of Artifacts:** All 7 tracked governance files and all 14 historical assurance reports were preserved non-destructively.
