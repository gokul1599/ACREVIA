# ACREVIA — PHASE 07: REGIONAL PULSE REMEDIATION ARCHITECTURE DESIGN PROOF, COMMAND-SCOPED RLS COMPOSITION & TRUSTED VERIFICATION AUTHORITY ASSURANCE

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India (33 Administrative Districts)  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** `MODE A ONLY` — Offline Source Inspection, Security Architecture Design, PostgreSQL Policy Analysis, ORM Transaction Modeling, Privilege Verification & Governance Documentation  
**Audit Standard:** Everything Claude Code (ECC) — `PLAN → INSPECT → TRACE → DESIGN → ADVERSARIAL REVIEW → VERIFY OFFLINE → DOCUMENT`  
**Public Repository:** `https://github.com/gokul1599/ACREVIA`  
**Verified Repository Baseline:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Target Deliverable:** `docs/pilot/security/PHASE_07_REGIONAL_PULSE_REMEDIATION_ARCHITECTURE_DESIGN_PROOF_AND_PREIMPLEMENTATION_GATE_REPORT.md`  
**Artifact Mirror:** `C:\Users\gokul\.gemini\antigravity\brain\8d770357-1b73-48ca-9930-eded206539c2\PHASE_07_REGIONAL_PULSE_REMEDIATION_ARCHITECTURE_DESIGN_PROOF_AND_PREIMPLEMENTATION_GATE_REPORT.md`  
**Authoritative Governance Register:** `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`  
**Overall Design Classification:** `CONDITIONALLY_READY_FOR_OWNER_REVIEW`  
**Implementation Authorization Status:** `NOT_IMPLEMENTATION_AUTHORIZED`  

---

## 1. EXECUTIVE DESIGN-ASSURANCE CONCLUSION

This audit delivers an independent, rigorous design-proof assessment of the proposed ACREVIA Regional Pulse remediation architecture. Following the preceding farmer-read-boundary and errata audits, this evaluation answers the governing architectural question:

> **Can the proposed design safely permit farmers to read only owner-approved Regional Pulse signals, while keeping raw evidence private, preserving expert recovery operations, preventing unauthorized state promotion, retaining evidence, and avoiding database writes during GET requests?**

Operating strictly under **MODE A ONLY** restrictions (zero live database connections, zero cloud provisioning, zero credential manipulation, zero application code modification, and zero Git history alterations), this assessment establishes that while the remediation architecture is conceptually sound, **the raw proposed design contains four critical defects and operational gaps** that must be resolved prior to implementation:

### 1.1 Critical Design Defects Identified in the Proposed Controls
1. **Fatal SQL Syntax Error in Candidate Administrator Bypass (`DEFECT-SQL-01`):**
   - The candidate public policy expression proposed using `app.is_admin = 'true'`.
   - *Design Proof Finding:* In PostgreSQL, `app.is_admin` is NOT a valid table column on `regional_signals`. Executing this expression results in an immediate SQL parse/validation failure: `ERROR: column "app.is_admin" does not exist` (or `ERROR: missing FROM-clause entry for table "app"`).
   - Furthermore, replacing it with a bare GUC check `current_setting('app.is_admin', true) = 'true'` fatally destroys the existing dual-identity boundary in `ADMIN_BYPASS_SQL`, allowing any untrusted connection capable of setting session variables to bypass all tenant and privacy controls. The secure, tested `ADMIN_BYPASS_SQL` definition checking `SESSION_USER` and `CURRENT_USER` in `('neondb_owner', 'acrevia_admin')` must be preserved intact.
2. **Breakage of Expert Recovery Operations via Unscoped SELECT Removal (`DEFECT-REC-01`):**
   - The proposed design eliminates the broad `FOR ALL` policy and restricts `FOR SELECT` strictly to published states (`EXPERT_CONFIRMED`, `ADMIN_CONFIRMED`, `OFFICIAL_ALERT`).
   - *Design Proof Finding:* In `backend/app/services/regional_pulse_service.py` (lines 430–436), `recover_suppressed_signal()` acquires a row-level lock using `SELECT ... FOR UPDATE` on a suppressed signal (`validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'`).
   - In PostgreSQL, `SELECT ... FOR UPDATE` evaluates the **`FOR SELECT`** policy of the target table. Because suppressed signals are excluded from the proposed public `FOR SELECT` policy, the query returns **0 rows**, causing `recover_suppressed_signal` to fail with HTTP 404!
   - Removing `FOR ALL` without providing an explicit, scoped internal SELECT capability for suppressed rows **completely breaks administrative and expert recovery**.
3. **ORM Column-Grant Rejection on Automatic Timestamps (`DEFECT-GRANT-01`):**
   - The proposed design recommended: `GRANT UPDATE (distinct_farms_count, validation_status) ON regional_signals TO acrevia_staging_app;`.
   - *Design Proof Finding:* `RegionalSignal` inherits `TimestampMixin` ([backend/app/database/base.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/base.py)), which configures an automatic `onupdate` callback on `updated_at`.
   - Whenever SQLAlchemy updates a signal, the Unit of Work flushes: `UPDATE regional_signals SET distinct_farms_count = :c, validation_status = :s, updated_at = :now WHERE id = :id`.
   - Because `updated_at` was omitted from the proposed column-level grant, PostgreSQL throws SQLSTATE `42501` (`permission denied for column "updated_at"`), causing all status updates and recoveries to crash. The grant must explicitly include `updated_at` or delegate timestamps to database triggers.
4. **Write-Side Official Advisory Spoofing Risk (`DEFECT-AUTH-01`):**
   - The proposed public read exception allows zero-telemetry official alerts (`OFFICIAL_ALERT` / `OFFICIAL_ADVISORY` / $N=0$) to be visible to farmers.
   - *Design Proof Finding:* In the current `author_write_policy`, non-admin writers holding `AGRICULTURAL_EXPERT` or `RESEARCHER` roles possess write authority. Without command-scoped write constraints, an expert or researcher connected via direct SQL could insert or update an `OFFICIAL_ALERT` row with $N=0$, publishing an arbitrary, unverified official state broadcast.
   - Write policies must explicitly enforce `WITH CHECK` clauses preventing non-admins from writing official advisory tuples.

---

## 2. PUBLIC AND LOCAL REPOSITORY BASELINE

### 2.1 Public Repository State
- **Repository URL:** `https://github.com/gokul1599/ACREVIA`
- **Tracked Branch:** `main`
- **Public Commit SHA:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d`
- **Integrity Status:** `PUBLIC_SOURCE_VERIFIED`. All design evaluations in this report are pinned to this commit.

### 2.2 Local Workspace Working Tree
- **Working Directory:** `c:\Users\gokul\OneDrive\Documents\projects`
- **Active Git Branch:** `main`
- **Local HEAD Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d`
- **Commit Divergence:** Exactly **0 commits divergence** (`HEAD` is synchronized with `origin/main`).
- **Application Source Code Status:** Exactly **0 application files modified**. All models, schemas, endpoints, tasks, migrations, and tests are clean.
- **Tracked Documentation Modifications (7):** Historical governance matrices in `docs/pilot/security/`.
- **Untracked Historical Deliverables (13):** Sequentially generated security assurance reports preserved without overwriting.

---

## 3. PREVIOUS ASSURANCE REPORT RECONCILIATION

This design proof integrates and builds upon the findings of the three preceding assurance reports:

1. **`PHASE_07_REGIONAL_PULSE_STATUS_CONTRACT_AND_EVIDENCE_RETENTION_DESIGN_ASSURANCE_REPORT.md`:**
   - Established the baseline discovery of FK cascade deletion vulnerabilities, un-scoped expert SELECT eligibility, and write-on-read suppression.
2. **`PHASE_07_REGIONAL_PULSE_ASSURANCE_ERRATA_AND_FINDING_RECLASSIFICATION_REPORT.md`:**
   - Successfully reclassified status vocabulary findings (`SEC-P07-STATUS-01` -> `PROPOSED_DESIGN_INCOMPATIBILITY`), corrected researcher API alignment, and withdrew the unsupported causal link between GATE-01 and credential rotation.
3. **`PHASE_07_REGIONAL_PULSE_FARMER_VISIBILITY_AND_GET_READ_BOUNDARY_FINAL_ASSURANCE_REPORT.md`:**
   - Formally proved the decoupling of database RLS from API publication eligibility, demonstrated that unvalidated signals are withheld only by an accidental false-absence side-effect, traced savepoint rollback mechanics, and corrected the execution-gate register mappings.

---

## 4. CURRENT FARMER-READ CONTRACT

### 4.1 End-to-End Execution Trace
In the baseline repository, invoking `GET /regional-pulse/signals` or `GET /regional-pulse/signals/{id}` executes the following chain:

```
FastAPI get_current_user (JWT Validation)
       |
       v
Session GUC Set: app.current_user_id = '<user_id>'
       |
       v
PostgreSQL Parent SELECT on regional_signals:
  Evaluates: (distinct_farms_count >= 3 AND validation_status != 'SUSPENDED')
  Result: Community signals (N >= 3) are RETURNED regardless of status.
       |
       v
Relationship Load: selectinload(RegionalSignal.evidences)
  PostgreSQL Child SELECT on regional_signal_evidences:
  Evaluates: ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')
  Result for Farmer: DENIED (PostgreSQL returns 0 rows; signal.evidences == [])
       |
       v
Service Revalidation: revalidate_signal_provenance()
  Evaluates: if not signal.evidences:
  Result: Stages distinct_farms_count = 0, validation_status = 'SUPPRESSED...'
       |
       v
Savepoint Block: with db.begin_nested():
  Exit Flush: Attempts UPDATE regional_signals
  RLS on Parent UPDATE: Requires Admin/Expert/Researcher -> 0 rows updated!
  SQLAlchemy Driver: Raises StaleDataError
  Context Manager: Catches error -> ROLLBACK TO SAVEPOINT -> session.expire(signal)
  Helper: Catches error -> logs warning -> returns False
       |
       v
Route Execution:
  Executes db.commit() -> Commits clean read transaction (DB unchanged)
  Checks if not is_valid and not is_privileged: -> FILTERS SIGNAL / RAISES HTTP 404
```

---

## 5. PARENT RLS ELIGIBILITY TRUTH TABLE

The following truth table evaluates current baseline parent table PostgreSQL RLS SELECT eligibility across all valid lifecycle statuses, farm counts ($N$), and actor identities:

| Validation Status | Farm Count ($N$) | Farmer SELECT Eligibility | Agricultural Expert | Application Admin | Database Bypass Identity | Underlying PostgreSQL Engine Rule |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `UNVALIDATED_OBSERVATION` | $N < 3$ | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; expert passes via `FOR ALL` role branch. |
| `UNVALIDATED_OBSERVATION` | $N \ge 3$ | **TRUE** | **TRUE** | **TRUE** | **TRUE** | **RLS Leak:** Farmer passes $N \ge 3$ and status $\ne$ `'SUSPENDED'`. |
| `EXPERT_CONFIRMED` | $N < 3$ | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; expert passes via `FOR ALL`. |
| `EXPERT_CONFIRMED` | $N \ge 3$ | **TRUE** | **TRUE** | **TRUE** | **TRUE** | Legitimate confirmed signal passes public read. |
| `ADMIN_CONFIRMED` | $N < 3$ | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; expert passes via `FOR ALL`. |
| `ADMIN_CONFIRMED` | $N \ge 3$ | **TRUE** | **TRUE** | **TRUE** | **TRUE** | Legitimate admin-confirmed signal passes public read. |
| `OFFICIAL_ALERT` | $N = 0$ | **FALSE** | **TRUE** | **TRUE** | **TRUE** | **Decision D-01 Defect:** Farmer fails $0 \ge 3$; alert blocked! |
| `OFFICIAL_ALERT` | $N \ge 3$ | **TRUE** | **TRUE** | **TRUE** | **TRUE** | Telemetry-backed alert passes public read. |
| `SUPPRESSED_INSUFFICIENT...`| $N < 3$ | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$. |
| `SUPPRESSED_INSUFFICIENT...`| $N \ge 3$ | **TRUE** | **TRUE** | **TRUE** | **TRUE** | **RLS Leak:** Suppressed row passes if $N \ge 3$ preserved! |
| `SUSPENDED` | Any $N$ | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Explicitly rejected by `validation_status != 'SUSPENDED'`. |

---

## 6. API PUBLICATION ELIGIBILITY TRUTH TABLE

The application layer imposes an independent layer of filtering on top of database row selection:

| Signal Status | Farm Count ($N$) | Parent RLS Eligible? | Dynamic Revalidation Result | Farmer API List Outcome | Farmer API Detail Outcome | Privileged API Outcome | Governing Factor |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `UNVALIDATED_OBSERVATION` | $N < 3$ | **NO** | Not reached (RLS hides row) | Excluded (Query empty) | HTTP 404 (Query empty) | Visible (via `FOR ALL`) | Filtered by PostgreSQL RLS. |
| `UNVALIDATED_OBSERVATION` | $N \ge 3$ | **YES** | **FAILS (False Absence)** | **Excluded** (`not is_valid`) | **HTTP 404** (`not is_valid`) | **Visible** (Evidences verified) | **Accidental Block:** Evidence RLS causes revalidation failure. |
| `EXPERT_CONFIRMED` | $N < 3$ | **NO** | Not reached (RLS hides row) | Excluded | HTTP 404 | Visible (Full detail) | Filtered by PostgreSQL RLS. |
| `EXPERT_CONFIRMED` | $N \ge 3$ | **YES** | **FAILS for Farmer** | **Excluded** (`not is_valid`) | **HTTP 404** (`not is_valid`) | **Visible** (Full detail) | **Defect:** Farmer denied legitimate verified signal! |
| `ADMIN_CONFIRMED` | $N < 3$ | **NO** | Not reached (RLS hides row) | Excluded | HTTP 404 | Visible (Full detail) | Filtered by PostgreSQL RLS. |
| `ADMIN_CONFIRMED` | $N \ge 3$ | **YES** | **FAILS for Farmer** | **Excluded** (`not is_valid`) | **HTTP 404** (`not is_valid`) | **Visible** (Full detail) | **Defect:** Farmer denied legitimate recovered signal! |
| `OFFICIAL_ALERT` | $N = 0$ | **NO** | **PASSES** (Tier check bypasses) | **Excluded (RLS query empty)**| **HTTP 404 (RLS query empty)**| **Visible** (Full detail) | **Decision D-01:** RLS blocks farmer read despite valid alert! |
| `OFFICIAL_ALERT` | $N \ge 3$ | **YES** | **PASSES** (Tier check bypasses) | **Visible** (Evidence stripped) | **Visible** (Evidence stripped) | **Visible** (Full detail) | Legitimate alert visible to all. |
| `SUPPRESSED_INSUFFICIENT...`| $N < 3$ | **NO** | Not reached (RLS hides row) | Excluded | HTTP 404 | Visible (Full detail) | Filtered by PostgreSQL RLS. |
| `SUPPRESSED_INSUFFICIENT...`| $N \ge 3$ | **YES** | Fails ($N=0$ staged) | **Excluded (Route filter)** | **HTTP 404 (Route filter)** | **Visible** (Full detail) | Filtered by API route check (`L89`, `L140`). |
| `SUSPENDED` | Any $N$ | **NO** | Not reached (RLS hides row) | Excluded | HTTP 404 | Visible (Full detail) | Filtered by PostgreSQL RLS. |

---

## 7. EVIDENCE ASSOCIATION FALSE-ABSENCE MODEL

### 7.1 Five Evidence States vs. Binary Service Logic
The platform architecture must differentiate between five distinct physical and transactional states of evidence associations:

1. **State 1 (Physical Absence):** Zero rows exist in `regional_signal_evidences`. Provenance is genuinely absent.
2. **State 2 (Privacy Invisibility):** Evidence rows exist, but child-table RLS denies SELECT to the farmer's session.
3. **State 3 (Referential Invalidity):** Evidence rows exist, but linked observation or risk alert rows were deleted or archived.
4. **State 4 (Verification Failure):** Evidence rows exist, but referenced farms fail district boundary or time-window criteria.
5. **State 5 (Stale / Detached):** Relationship collection was not populated by the ORM loader.

In `RegionalPulseService.revalidate_signal_provenance()`, lines 338–341 evaluate:
```python
if not signal.evidences:
    signal.distinct_farms_count = 0
    signal.validation_status = "SUPPRESSED_INSUFFICIENT_PROVENANCE"
    return False
```
Because `signal.evidences` is loaded under the farmer's database connection, child-table RLS filters out all records. The service treats State 2 (Privacy Invisibility) as State 1 (Physical Absence).

### 7.2 Descriptive Finding Preservation
This vulnerability is formally tracked under the descriptive identifier:
$$\mathbf{FARMER\_READ\_BLOCKED\_BY\_EVIDENCE\_ASSOCIATION\_RLS}$$
This is maintained as a descriptive architectural defect rather than an invented canonical blocker ID, preserving canonical register integrity.

---

## 8. CURRENT GET MUTATION ANALYSIS

### 8.1 Count-Only vs. Suppression Mutations
The previous assurance analysis focused primarily on suppression mutations. However, a deeper code trace reveals that **dynamic provenance revalidation can persist count-only mutations** even when a signal remains valid:

1. Suppose a verified signal has `distinct_farms_count = 5` and `validation_status = 'EXPERT_CONFIRMED'`.
2. An underlying observation is archived, reducing the number of valid distinct farms from 5 to 4.
3. An Agricultural Expert or Admin calls `GET /regional-pulse/signals/sig_123`.
4. In `revalidate_signal_provenance()` (line 376):
   `signal.distinct_farms_count = current_count` (sets count to 4).
   Because $4 \ge 3$, the service returns `True`.
5. However, `signal.distinct_farms_count` is now dirty in the SQLAlchemy session!
6. When the GET route executes `db.commit()` ([endpoints/regional_pulse.py#L128](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/regional_pulse.py#L128)), the count update ($5 \to 4$) **is permanently committed to PostgreSQL on a read request**!

### 8.2 Spectrum of GET Mutation Behaviors

| Scenario | Actor | Revalidation Outcome | SQL Statement Emitted on Read | Persistence to DB | Architectural Violation |
|---|---|---|---|---|---|
| **A. Farmer Read** | Ordinary Farmer | False (False absence) | `UPDATE regional_signals ...` (0 rows matched) | **NO** (Rolled back at savepoint) | Outcome A: Read Denial |
| **B. Privileged Valid Count Shift** | Expert / Admin | True ($N$ drops from 5 to 4) | `UPDATE regional_signals SET distinct_farms_count = 4` | **YES (COMMITTED)** | `RES-PULSE-READ-01` (Count mutation) |
| **C. Privileged Suppression** | Expert / Admin | False ($N$ drops from 3 to 1) | `UPDATE regional_signals SET validation_status = 'SUPPRESSED...', ...` | **YES (COMMITTED)** | `RES-PULSE-READ-01` (Suppression mutation) |
| **D. Official Advisory Read** | Any Actor | True (Tier check bypass) | None (Revalidation exits early) | **NO** | Safe Read |

---

## 9. CORRECTED SQLALCHEMY SAVEPOINT BEHAVIOR

### 9.1 Transaction Lifecycle Specification
Inspection of `backend/app/database/session.py` confirms that `SessionLocal` is configured with:
- `autocommit = False`
- `autoflush = False`
- `expire_on_commit = False`

Under SQLAlchemy 2.0 with PostgreSQL driver `psycopg2-binary`:
1. `with db.begin_nested():` emits SQL `SAVEPOINT sa_savepoint_X`.
2. Because `autoflush = False`, modifications staged in Python memory prior to or within the block do not trigger preliminary SQL emissions.
3. Upon block exit without an unhandled Python exception, SQLAlchemy calls `savepoint.commit()`, which immediately executes `session.flush()`.
4. **Exception Handling:**
   - If the update matches 0 rows (Farmer RLS), the driver reports `rowcount = 0`, raising `sqlalchemy.orm.exc.StaleDataError`.
   - If the actor lacks table UPDATE grants, PostgreSQL returns SQLSTATE `42501` (`insufficient_privilege`).
   - If a column value violates constraints, PostgreSQL returns SQLSTATE `23514` (`check_violation`).
5. In all failure cases, the context manager catches the exception, executes `ROLLBACK TO SAVEPOINT sa_savepoint_X`, calls `session.expire(modified_instances)`, and re-raises the error.
6. The `try...except` block in `revalidate_signal_provenance()` (lines 387–392) catches the re-raised exception.
7. Because the savepoint was rolled back, the PostgreSQL connection is **NOT** in an aborted transaction state (SQLSTATE `25P02`). The outer route can call `db.commit()` without error, committing only clean read operations.

---

## 10. CANDIDATE PUBLIC SELECT POLICY ASSESSMENT

### 10.1 Evaluation of the Candidate Allowlist
The proposed remediation architecture designs an explicit public publication allowlist:
```sql
CREATE POLICY regional_signals_public_read_policy ON regional_signals
    AS PERMISSIVE FOR SELECT TO PUBLIC
    USING (
        /* Mandatory Authenticated Database Bypass */
        (
            (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') OR CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin'))
            AND current_setting('app.is_admin', true) = 'true'
        )
        OR (
            distinct_farms_count >= 3
            AND validation_status IN ('EXPERT_CONFIRMED', 'ADMIN_CONFIRMED')
        )
        OR (
            validation_status = 'OFFICIAL_ALERT'
            AND confidence_tier = 'OFFICIAL_ADVISORY'
            AND distinct_farms_count = 0
        )
    );
```

### 10.2 Security and Product State Analysis
1. **`UNVALIDATED_OBSERVATION` ($N \ge 3$):** **Explicitly Excluded.** Prevents unvalidated community signals from leaking to farmers prior to agronomic peer review, successfully satisfying **Decision D-03**.
2. **`EXPERT_CONFIRMED` & `ADMIN_CONFIRMED` ($N \ge 3$):** **Explicitly Permitted.** Verified community signals and recovered signals are visible to farmers without requiring child evidence inspection.
3. **`SUPPRESSED_INSUFFICIENT_PROVENANCE`:** **Explicitly Excluded.** Suppressed signals cannot be read by farmers even if $N \ge 3$ is preserved in the database column.
4. **`SUSPENDED`:** **Explicitly Excluded.** Legitimate quarantine status remains inaccessible to the public.
5. **`OFFICIAL_ALERT` ($N = 0$):** **Conditionally Permitted.** Resolves the zero-telemetry blocker for official advisories upon Project Owner sign-off on **Decision D-01**.

---

## 11. ADMINISTRATOR BYPASS EXPRESSION VALIDATION (DEFECT-SQL-01)

### 11.1 The Invalid Identifier Defect
The previous report proposed the candidate clause:
```sql
app.is_admin = 'true'
```
**Fatal Defect (`DEFECT-SQL-01`):** In PostgreSQL SQL grammar, `app.is_admin` is parsed as `<table_or_alias>.<column_name>`. Because `regional_signals` does not have a column named `is_admin`, and there is no table aliased as `app` in the query, PostgreSQL aborts query planning with:
$$\texttt{ERROR: column app.is_admin does not exist}$$
or:
$$\texttt{ERROR: missing FROM-clause entry for table "app"}$$

### 11.2 Catastrophic Vulnerability of Bare GUC Checks
If an engineer attempts to fix the syntax error by writing:
```sql
current_setting('app.is_admin', true) = 'true'
```
This introduces a **critical authentication bypass vulnerability**:
- Any connected client (including an untrusted web session or compromised runtime connection) can execute `SET app.is_admin = 'true';`.
- If the RLS bypass evaluates only the session GUC, the actor immediately bypasses all tenant isolation, district scoping, and publication policies across all 132 database tables!

### 11.3 Authentic Identity Boundary Preservation
The existing, verified `ADMIN_BYPASS_SQL` in `backend/app/database/rls.py` (lines 14–19) enforces a strict **dual-identity barrier**:
```python
ADMIN_BYPASS_SQL = (
    "(SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') "
    "AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') "
    "AND current_setting('app.is_admin', true) = 'true')"
)
```
1. `SESSION_USER` and `CURRENT_USER` check the physical PostgreSQL database credentials. Ordinary application connections (`acrevia_staging_app`) evaluate to `FALSE`.
2. `current_setting('app.is_admin', true) = 'true'` verifies that the application explicitly requested administrative scope.

**Mandatory Architecture Rule:** The candidate public read policy **must NEVER use bare `app.is_admin` or a lone GUC check**. It must strictly embed `ADMIN_BYPASS_SQL`.

---

## 12. COMMAND-SPECIFIC RLS POLICY ARCHITECTURE

To eliminate cross-district SELECT leakage (`RES-PULSE-01`) while preserving write capabilities, the broad `regional_signals_author_write_policy` (`FOR ALL`) must be decomposed into command-specific policies:

| Table Name | Policy Identifier | Command Scope | Target DB Role | `USING` Expression | `WITH CHECK` Expression | Security & Functional Purpose |
|---|---|---|---|---|---|---|
| `regional_signals` | `signals_public_select` | `FOR SELECT` | `PUBLIC` | Public allowlist (D-01/D-03 allowlist + `ADMIN_BYPASS_SQL`) | N/A | Governs farmer public visibility. |
| `regional_signals` | `signals_internal_select` | `FOR SELECT` | `acrevia_staging_app` | Role in Admin/Expert + `status = 'SUPPRESSED...'` | N/A | **Enables expert recovery (`SELECT FOR UPDATE`).** |
| `regional_signals` | `signals_expert_insert` | `FOR INSERT` | `acrevia_staging_app` | N/A | Role in Expert/Researcher + `status != 'OFFICIAL_ALERT'` | Prevents advisory spoofing on INSERT. |
| `regional_signals` | `signals_admin_insert` | `FOR INSERT` | `acrevia_staging_app` | N/A | Role in `ADMIN` | Authorizes official advisory creation. |
| `regional_signals` | `signals_expert_update` | `FOR UPDATE` | `acrevia_staging_app` | Role in Expert + `status = 'SUPPRESSED...'` | `status IN ('EXPERT_CONFIRMED', 'SUPPRESSED...')` | Scopes recovery UPDATE to valid transitions. |
| `regional_signals` | `signals_worker_update` | `FOR UPDATE` | `acrevia_worker` | `TRUE` (Worker session) | `status IN ('EXPERT_CONFIRMED', 'SUPPRESSED...')` | Enables worker provenance revalidation updates. |
| `regional_signal_evidences`| `evidences_privileged_select` | `FOR SELECT` | `acrevia_staging_app`, `acrevia_worker` | Role in Admin/Expert/Researcher OR Worker identity | N/A | Keeps evidence hidden from farmers; accessible to verifiers. |
| `regional_signal_evidences`| `evidences_insert_policy` | `FOR INSERT` | `acrevia_staging_app` | N/A | Role in Admin/Expert/Researcher | Permits evidence attachment at creation. |
| `regional_signal_evidences`| `evidences_deny_update` | `FOR UPDATE` | `PUBLIC` | `FALSE` | `FALSE` | Enforces strictly append-only evidence. |
| `regional_signal_evidences`| `evidences_deny_delete` | `FOR DELETE` | `PUBLIC` | `FALSE` | N/A | Blocks application evidence deletion. |

---

## 13. INTERNAL SELECT AND RECOVERY DESIGN (DEFECT-REC-01)

### 13.1 The Recovery SELECT FOR UPDATE Mechanics
In `backend/app/services/regional_pulse_service.py` (lines 430–436), the expert recovery workflow executes:
```python
stmt = (
    select(RegionalSignal)
    .options(selectinload(RegionalSignal.evidences))
    .where(RegionalSignal.id == signal_id)
    .with_for_update()
    .execution_options(populate_existing=True)
)
signal = db.scalars(stmt).first()
if not signal:
    raise HTTPException(status_code=404, detail="Regional signal not found")
```

### 13.2 The PostgreSQL Engine Concurrency Rule
Under PostgreSQL engine rules (`src/backend/executor/execMain.c`):
- A `SELECT ... FOR UPDATE` statement **is a SELECT command**, not an UPDATE command.
- The PostgreSQL query rewriter evaluates row filtering against the table's **`FOR SELECT`** policies. The `FOR UPDATE` policy is not evaluated during row selection or locking; it is evaluated only when an `UPDATE` statement is subsequently executed.

### 13.3 Recovery Failure in Naive Policy Separation (`DEFECT-REC-01`)
If an engineer implements a candidate `FOR SELECT` policy that restricts rows to public publication states:
$$\text{Candidate SELECT:} \quad \text{validation\_status IN ('EXPERT\_CONFIRMED', 'ADMIN\_CONFIRMED', 'OFFICIAL\_ALERT')}$$
When an Agricultural Expert calls `recover_suppressed_signal(sig_id)`:
1. The target signal has `validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'`.
2. PostgreSQL RLS evaluates the `FOR SELECT` policy. The condition returns `FALSE`.
3. The query returns **0 rows**.
4. Line 438 executes: `if not signal: raise HTTPException(404)`.
5. **Legitimate recovery of suppressed signals becomes mathematically impossible!**

### 13.4 Corrected Internal Recovery SELECT Policy
To resolve `DEFECT-REC-01`, a dedicated permissive `FOR SELECT` policy must be introduced specifically for internal recovery:
```sql
CREATE POLICY regional_signals_recovery_select_policy ON regional_signals
    AS PERMISSIVE
    FOR SELECT
    TO acrevia_staging_app
    USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            WHERE ur.user_id::text = current_setting('app.current_user_id', true)
            AND ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT')
        )
        AND validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'
    );
```
- **Farmers:** Evaluate to `FALSE` (they lack the required role). Suppressed rows remain completely hidden.
- **Experts / Admins:** Evaluate to `TRUE` for suppressed signals, enabling `SELECT ... FOR UPDATE` to lock and return the record for recovery.

---

## 14. TRUSTED WORKER ROLE SPECIFICATION

### 14.1 Worker Database Identity Contract
The proposed worker identity `acrevia_worker` must be defined under strict least-privilege constraints:
- **Role Attributes:** `LOGIN`, `NOSUPERUSER`, `NOBYPASSRLS`, `NOCREATEDB`, `NOCREATEROLE`.
- **Table Privilege Grants:**
  - `GRANT SELECT, UPDATE (distinct_farms_count, validation_status, updated_at) ON regional_signals TO acrevia_worker;`
  - `GRANT SELECT, INSERT ON regional_signal_evidences TO acrevia_worker;`
  - `GRANT SELECT, UPDATE ON outbox_events TO acrevia_worker;`
  - `GRANT SELECT ON observations, risk_alerts, farms, user_roles TO acrevia_worker;`
  - `REVOKE DELETE, TRUNCATE ON ALL TABLES FROM acrevia_worker;`
- **Worker Session Context:** When the worker connects, it must set a dedicated worker context GUC:
  `SET app.is_worker = 'true';`
  This enables child evidence SELECT policies while preventing the worker from posing as an interactive web user.

### 14.2 DB-AUTH-01 Governance Relationship
Inspection of `docs/pilot/security/PHASE_07_TRUSTED_WRITER_ARCHITECTURE_DECISION_RECORD.md` confirms that `DB-AUTH-01` currently models Options A, B, C, and D for web application roles, but **does not formalize an independent background worker database principal**.

**Governance Status:** Introducing `acrevia_worker` represents a **proposed extension to Decision DB-AUTH-01**. It requires formal Project Owner sign-off before cloud role provisioning in Mode B.

---

## 15. TRANSACTIONAL OUTBOX AND RECONCILIATION MODEL

### 15.1 Outbox Event Schema and Trigger Points
To eliminate write-on-read execution, provenance revalidation must be triggered asynchronously via a Transactional Outbox pattern:

```sql
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id VARCHAR(36) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING' NOT NULL,
    retry_count INT DEFAULT 0 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT clock_timestamp() NOT NULL,
    processed_at TIMESTAMPTZ
);
```

Events must be written within the **same atomic database transaction** as the mutating operation:
1. `REGIONAL_SIGNAL_CREATED`: Written during `RegionalPulseService.aggregate_regional_signal()`.
2. `EVIDENCE_ATTACHED`: Written when observations or risk alerts are linked to a signal.
3. `OBSERVATION_ARCHIVED` / `OBSERVATION_DELETED`: Emitted when an underlying observation is invalidated.
4. `FARM_ARCHIVED`: Emitted when a participating farm is soft-deleted.

### 15.2 Worker Polling and Concurrency Control
The worker polls the outbox using PostgreSQL's non-blocking row locking:
```sql
SELECT id, aggregate_id, event_type, payload
FROM outbox_events
WHERE status = 'PENDING'
ORDER BY created_at ASC
FOR UPDATE SKIP LOCKED
LIMIT 50;
```
This guarantees that multiple concurrent worker instances never process the same event simultaneously.

### 15.3 Stale Publication Window and Policy Choices
Between the moment an observation is deleted and the moment the worker reconciles the parent signal, there is an unavoidable **reconciliation lag window** (typically 100ms–2s).
- **Product Policy Choice 1 (Eventual Consistency):** The signal remains visible under its previously verified count until the worker executes suppression.
- **Product Policy Choice 2 (Fail-Closed on Invalidation):** When an observation is deleted, a database trigger immediately sets `regional_signals.validation_status = 'PENDING_REVALIDATION'`, hiding it from farmers instantly.
This is a product safety decision reserved for the Project Owner.

---

## 16. PARENT UPDATE GRANT AND TIMESTAMP ANALYSIS (DEFECT-GRANT-01)

### 16.1 The SQLAlchemy TimestampMixin onupdate Mechanism
In `backend/app/models/regional_pulse.py` (line 21):
```python
class RegionalSignal(Base, TimestampMixin):
    __tablename__ = "regional_signals"
```
In `backend/app/database/base.py`:
```python
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(...)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
```

### 16.2 The Column-Level Grant Failure (`DEFECT-GRANT-01`)
The previous design proposed:
```sql
GRANT UPDATE (distinct_farms_count, validation_status) ON regional_signals TO acrevia_staging_app;
```
When SQLAlchemy executes an update on `RegionalSignal` (e.g. during recovery or worker revalidation):
1. Because `updated_at` defines an `onupdate` lambda, SQLAlchemy's Unit of Work marks `updated_at` dirty and includes it in the compiled SQL:
   ```sql
   UPDATE regional_signals
   SET distinct_farms_count = %(distinct_farms_count)s,
       validation_status = %(validation_status)s,
       updated_at = %(updated_at)s
   WHERE regional_signals.id = %(regional_signals_id)s;
   ```
2. PostgreSQL checks the user's column privileges on `regional_signals`.
3. The user possesses UPDATE grants on `distinct_farms_count` and `validation_status`, but **NOT on `updated_at`**.
4. PostgreSQL aborts the transaction immediately:
   $$\texttt{ERROR: permission denied for column "updated_at" of relation "regional_signals" (SQLSTATE 42501)}$$

### 16.3 Corrective Architectural Options
1. **Option 1 (Recommended): Explicit Column Grant Inclusion:**
   ```sql
   GRANT UPDATE (distinct_farms_count, validation_status, updated_at) ON regional_signals TO acrevia_staging_app, acrevia_worker;
   ```
2. **Option 2: Database-Side Trigger Timestamping:**
   Remove the SQLAlchemy `onupdate` lambda from Python models, and attach a PostgreSQL `BEFORE UPDATE` trigger that sets `NEW.updated_at = clock_timestamp();`. Under trigger execution, column-level UPDATE grants on `updated_at` are not required from the invoking role.

---

## 17. STATE TRANSITION AUTHORIZATION MATRIX

The following state transition matrix establishes least-privilege authority for every lifecycle transition:

| Pre-Transition Status | Target Post-Transition Status | Authorized Principal | Invocation Mechanism | Required Evidence / Invariants | Audit Event Logged |
|---|---|---|---|---|---|
| *Non-existent* | `UNVALIDATED_OBSERVATION` | `acrevia_staging_app` (Farmer/Community) | `POST /signals` | Minimum farm count $N \ge 3$ staged. | `SIGNAL_CREATED` |
| *Non-existent* | `EXPERT_CONFIRMED` | `acrevia_staging_app` (Expert) | `POST /signals` | Expert credential verified in session. | `EXPERT_SIGNAL_CREATED` |
| *Non-existent* | `OFFICIAL_ALERT` | `acrevia_staging_app` (Admin ONLY) | `POST /signals` | Admin credential verified; $N=0$ permitted. | `OFFICIAL_ALERT_PUBLISHED` |
| `UNVALIDATED_OBSERVATION` | `EXPERT_CONFIRMED` | `acrevia_staging_app` (Expert) | `POST /signals/{id}/validate` | Agronomic review completed; $N \ge 3$ active. | `SIGNAL_VALIDATED_EXPERT` |
| `EXPERT_CONFIRMED` | `SUPPRESSED_INSUFFICIENT...`| `acrevia_worker` | Outbox Worker Task | Provenance revalidation returns $N < 3$. | `SIGNAL_SUPPRESSED_PROVENANCE` |
| `ADMIN_CONFIRMED` | `SUPPRESSED_INSUFFICIENT...`| `acrevia_worker` | Outbox Worker Task | Provenance revalidation returns $N < 3$. | `SIGNAL_SUPPRESSED_PROVENANCE` |
| `SUPPRESSED_INSUFFICIENT...`| `EXPERT_CONFIRMED` | `acrevia_staging_app` (Expert) | `POST /signals/{id}/recover` | Expert re-validates evidence; locked row. | `SIGNAL_RECOVERED_EXPERT` |
| `SUPPRESSED_INSUFFICIENT...`| `ADMIN_CONFIRMED` | `acrevia_staging_app` (Admin) | `POST /signals/{id}/recover` | Admin confirms without agronomic credential. | `SIGNAL_RECOVERED_ADMIN` |
| *Any Status* | `SUSPENDED` | `acrevia_admin` / Database Owner | Administrative Killswitch | Emergency quarantine action. | `SIGNAL_QUARANTINED` |

---

## 18. EVIDENCE APPEND-ONLY RETENTION DESIGN

### 18.1 Multi-Layer Defense-in-Depth Specification
To achieve `APPEND_ONLY_FOR_RUNTIME_ROLES` across `regional_signal_evidences`:

```
Layer 1: SQL Table Privileges
  REVOKE UPDATE, DELETE, TRUNCATE ON regional_signal_evidences FROM acrevia_staging_app, acrevia_worker;
       |
       v
Layer 2: PostgreSQL Foreign Key Action
  ALTER TABLE regional_signal_evidences
  DROP CONSTRAINT regional_signal_evidences_signal_id_fkey,
  ADD CONSTRAINT regional_signal_evidences_signal_id_fkey
      FOREIGN KEY (signal_id) REFERENCES regional_signals(id)
      ON DELETE RESTRICT;
       |
       v
Layer 3: SQLAlchemy ORM Relationship Mapping
  In backend/app/models/regional_pulse.py:
  evidences = relationship("RegionalSignalEvidence", cascade="save-update, merge", passive_deletes=True)
       |
       v
Layer 4: PostgreSQL RLS Defense-in-Depth
  CREATE POLICY evidences_deny_delete ON regional_signal_evidences FOR DELETE TO PUBLIC USING (false);
```

### 18.2 Deletion Resistance Across All Trigger Paths
- **Direct Child Deletion:** Blocked by Layer 1 (`42501`) and Layer 4 (RLS).
- **ORM Child Orphan Removal:** Blocked by Layer 1 (`42501`) when Unit of Work flushes explicit child DELETE.
- **Direct SQL Parent Deletion:** Blocked by Layer 2 (`23001 restrict_violation`) via PostgreSQL internal referential integrity trigger (`RI_FKey_cascade_del`).
- **ORM Parent Deletion:** SQLAlchemy observes `passive_deletes=True` and emits parent DELETE without child DELETE; Layer 2 triggers and halts the parent deletion.

---

## 19. FK AND ORM CASCADE COMPATIBILITY

### 19.1 Behavior of passive_deletes in SQLAlchemy
In SQLAlchemy, `passive_deletes` controls whether the ORM eagerly queries and deletes child entities in Python before emitting a parent `DELETE`:
- **Default (`passive_deletes=False`):** When deleting a parent, SQLAlchemy executes `SELECT` on all referencing child entities, issues explicit `DELETE FROM child WHERE id = :id`, and then deletes the parent. This triggers child table privileges and RLS policies.
- **`passive_deletes=True`:** SQLAlchemy does **not** load or delete child records. It issues the parent `DELETE` directly and relies on the PostgreSQL database foreign key to handle referential integrity.
- **`passive_deletes="all"`:** Disables nullification and cascade deletion even for unloaded relationships, completely deferring to database constraints.

### 19.2 The Essential Interlock: ORM + Database FK
$$\begin{aligned}
\textbf{Case A:} &\quad \text{ORM has } \texttt{delete-orphan} + \text{DB has } \texttt{RESTRICT} \implies \text{ORM deletes child first! Evidence destroyed!} \\
\textbf{Case B:} &\quad \text{ORM has } \texttt{passive\_deletes=True} + \text{DB has } \texttt{CASCADE} \implies \text{DB cascades child delete! Evidence destroyed!} \\
\textbf{Case C (Hardened):} &\quad \text{ORM has } \texttt{passive\_deletes=True} + \text{DB has } \texttt{RESTRICT} \implies \mathbf{Evidence\ Protected!\ Parent\ Delete\ Blocked!}
\end{aligned}$$

Neither control is sufficient on its own. True evidence retention requires coordinating both the SQLAlchemy relationship declaration and the PostgreSQL foreign key definition.

---

## 20. STATUS CHECK CONSTRAINT READINESS

### 20.1 Comprehensive Status Vocabulary Reconciliation
The candidate database `CHECK` constraint covers all six operational and reserved statuses:
```sql
ALTER TABLE regional_signals
ADD CONSTRAINT chk_regional_signals_validation_status
CHECK (validation_status IN (
    'UNVALIDATED_OBSERVATION',
    'EXPERT_CONFIRMED',
    'ADMIN_CONFIRMED',
    'OFFICIAL_ALERT',
    'SUPPRESSED_INSUFFICIENT_PROVENANCE',
    'SUSPENDED'
));
```

### 20.2 Status Provenance & Lifecycle Traceability
1. **Service-Emitted (Active Lifecycle):**
   - `UNVALIDATED_OBSERVATION`: Initial community aggregation state.
   - `EXPERT_CONFIRMED`: Validation by Agricultural Expert.
   - `ADMIN_CONFIRMED`: Recovery confirmation by Admin without expert credentials.
   - `OFFICIAL_ALERT`: Broadcast state alert by Admin.
   - `SUPPRESSED_INSUFFICIENT_PROVENANCE`: Automated suppression upon provenance failure.
2. **Reserved Administrative State:**
   - `SUSPENDED`: Referenced in existing public read RLS policy (`validation_status != 'SUSPENDED'`) and Alembic migration `a1089411c87d`. Retained in the CHECK constraint to accommodate quarantine actions and prevent migration rollback errors if historical rows contain this status.

### 20.3 Pre-Migration Data Compatibility & Rollback Strategy
Prior to applying this constraint in a future migration:
1. **Pre-Check Query:** `SELECT DISTINCT validation_status FROM regional_signals WHERE validation_status NOT IN ('UNVALIDATED_OBSERVATION', 'EXPERT_CONFIRMED', 'ADMIN_CONFIRMED', 'OFFICIAL_ALERT', 'SUPPRESSED_INSUFFICIENT_PROVENANCE', 'SUSPENDED');`
2. **Downgrade Migration:** `ALTER TABLE regional_signals DROP CONSTRAINT IF EXISTS chk_regional_signals_validation_status;`

---

## 21. OFFICIAL ADVISORY WRITER-AUTHENTICITY BOUNDARY (DEFECT-AUTH-01)

### 21.1 The Vulnerability of Unrestricted Writes
Under Candidate Public Policy Clause:
```sql
OR (validation_status = 'OFFICIAL_ALERT' AND confidence_tier = 'OFFICIAL_ADVISORY' AND distinct_farms_count = 0)
```
In the baseline code, `regional_signals_author_write_policy` allows any user with `AGRICULTURAL_EXPERT` or `RESEARCHER` to perform inserts and updates. 

**Vulnerability Scenario (`DEFECT-AUTH-01`):** An agronomist or researcher with direct SQL access could insert a row claiming to be an official government alert for an entire district without obtaining government sign-off. Because the row matches `OFFICIAL_ALERT` / `OFFICIAL_ADVISORY` / $N=0$, it would immediately bypass the $N \ge 3$ threshold and appear in all farmer mobile feeds!

### 21.2 Command-Scoped Hardening
To eliminate `DEFECT-AUTH-01`, RLS write policies must enforce that non-admins can **never** create or update rows to `OFFICIAL_ALERT` or `OFFICIAL_ADVISORY`:

```sql
-- Enforced via WITH CHECK in regional_signals_expert_insert_policy
WITH CHECK (
    validation_status != 'OFFICIAL_ALERT'
    AND confidence_tier != 'OFFICIAL_ADVISORY'
);

-- Enforced via WITH CHECK in regional_signals_expert_update_policy
WITH CHECK (
    validation_status != 'OFFICIAL_ALERT'
    AND confidence_tier != 'OFFICIAL_ADVISORY'
);
```

### 21.3 Platform Admin Authorship vs. Government Source Authenticity (Decision D-02)
Platform administrator authorization must not be conflated with sovereign government authenticity:
- An `ADMIN` creating an alert proves platform administrative privilege.
- It does **not** cryptographically prove authenticity from the Telangana Department of Agriculture.
- Under **Decision D-02**, official advisories should capture provenance metadata: `source_department`, `official_reference_number`, and `gazette_date`.

---

## 22. OWNER DECISION TRACEABILITY

The following matrix connects the technical design proof to governing Project Owner decisions:

| Decision ID | Decision Title | Architectural Impact in Remediation Design | Current Governance State | Prerequisite for Implementation |
|---|---|---|---|---|
| **D-01** | **Official Advisory Public Visibility vs. Minimum Farm Threshold** | Authorizes public read RLS exception for zero-telemetry official state alerts ($N=0$). | `PENDING_OWNER_SIGN_OFF` | Mandatory before deploying candidate public read policy. |
| **D-02** | **Source Authenticity & Terminology** | Governs distinction between platform admin broadcasts and government-authenticated alerts. | `PENDING_OWNER_SIGN_OFF` | Mandatory before establishing official advisory metadata schema. |
| **D-03** | **Agronomic Peer-Review Workflow** | Enforces exclusion of unvalidated community observations ($N \ge 3$) from public RLS read policy. | `PENDING_OWNER_SIGN_OFF` | Mandatory before deploying candidate public read policy. |
| **DB-AUTH-01** | **Trusted Writer Architecture** | Adopts dedicated worker role `acrevia_worker` and column-level privilege crosswalk. | `PENDING_OWNER_SIGN_OFF` | Mandatory before creating worker database principal. |

---

## 23. GATE-01 THROUGH GATE-05 RECONCILIATION

### 23.1 Exact Scope and Status of Registered Execution Gates
Inspection of `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md` establishes the exact gate scopes:

| Gate Identifier | Authoritative Scope Defined in Governance Register | Recorded State | Authority | Execution Impact |
| :--- | :--- | :--- | :--- | :--- |
| **GATE-01** | Provisioning of isolated Neon staging branch `staging-rls-phase07` from parent `production` in `aws-ap-southeast-1`. | **`[x] APPROVED BY OWNER (2026-11-10)`** | Project Owner | **Approved.** Branch creation authorized; physical execution unverified in Mode A. |
| **GATE-02** | Creation of unprivileged runtime database role `acrevia_staging_app` (`NOSUPERUSER`, `NOBYPASSRLS`, `NOCREATEDB`, `NOCREATEROLE`). | `[ ] UNCHECKED (AWAITING SIGN-OFF)` | Project Owner | Required before provisioning runtime role on staging branch. |
| **GATE-03** | Physical execution of Alembic RLS migration `a1089411c87d` applying 751 atomic DDL statements to `neondb_staging`. | `[ ] UNCHECKED (AWAITING SIGN-OFF)` | Project Owner | Required before applying RLS policies on staging database. |
| **GATE-04** | Execution of automated staging RLS verification harness (`scripts/verify_staging_rls.py`) against live staging endpoint. | `[ ] UNCHECKED (AWAITING SIGN-OFF)` | Project Owner | Required before running automated catalog probes and tenant UAT. |
| **GATE-05** | Teardown and deprovisioning schedule of `staging-rls-phase05` post-verification. | `[ ] UNCHECKED (AWAITING SIGN-OFF)` | Project Owner | Controls cloud branch cleanup 24 hours post-verification. |

### 23.2 Why MODE B Execution Remains Strictly Blocked
Although GATE-01 was approved on 2026-11-10, **MODE B execution remains completely unauthorized**:
1. GATE-02 (role creation), GATE-03 (migration execution), and GATE-04 (harness execution) remain unchecked.
2. Decisions D-01 through D-03 and DB-AUTH-01 remain pending owner sign-off.
3. No remote connection to Neon Cloud may be established until all prerequisite gates are signed.

### 23.3 Branch-Identity Ambiguity
An explicit discrepancy exists in the register:
- GATE-01 Scope & Checklist: `staging-rls-phase07`
- Overview line 20 & GATE-05 Scope: `staging-rls-phase05`
This unresolved ambiguity must be formally clarified by the Project Owner prior to Mode B execution.

---

## 24. CANONICAL BLOCKER RECONCILIATION

All fifteen canonical blockers are preserved without alteration:

| Blocker ID | Description | Resolution in Remediation Design | Mode A Status |
|---|---|---|---|
| `RLS-WRITE-AUTH-01` | RLS write policy allows arbitrary role updates via unconstrained `WITH CHECK`. | Resolved via command-scoped `FOR INSERT`/`FOR UPDATE` policies and DB status constraints. | Active Blocker |
| `RLS-ROLE-ASSIGNMENT-01` | Runtime role assignment mechanism susceptible to session variable leakage. | Session GUCs encapsulated strictly within transaction boundaries. | Active Blocker |
| `DB-AUTH-01` | Single runtime database role lacks separation between background workers and web apps. | Resolved via dedicated `acrevia_worker` identity (extension to DB-AUTH-01). | Active Blocker |
| `DB-CREDENTIAL-EXPOSURE-01` | Public exposure of database connection strings in legacy commits. | Independent blocker; rotation protocol required prior to production cutover. | Active Blocker |
| `APP-ROLE-SELF-SELECT-01` | Client self-selection of roles during registration/authentication. | Enforce database-level role binding on API actors. | Active Blocker |
| `EXP-AUTH-01` | Expert and researcher endpoint authorization inconsistencies. | Baseline code aligned; policy narrowing coordinates with API dependencies. | Active Blocker |
| `CASCADE-ROLE-DEL-01` | Cascading deletions undermine evidence integrity and role associations. | Resolved via FK `ON DELETE RESTRICT` and ORM `passive_deletes=True`. | Active Blocker |
| `TENANT-MEMBERSHIP-01` | Tenant membership validation absent in cross-tenant join queries. | GUC validation required across collaborative tables. | Active Blocker |
| `OWNER-AUTH-01` | Missing formal Project Owner sign-offs on core security decisions. | Pending formal sign-offs on D-01 through D-03 and DB-AUTH-01. | Active Blocker |
| `DB-RLS-01` | Staging database RLS verification unperformed against live Neon instance. | Unverified in Mode A; requires Mode B execution under GATE-01–04. | Active Blocker |
| `WRK-DISP-01` | Production worker dispatch provider raises `DISPATCH_NOT_CONFIGURED`. | Resolved via Transactional Outbox pattern decoupled from RiskCast. | Active Blocker |
| `RES-PULSE-01` | Role-based cross-district SELECT eligibility across 33 districts. | Resolved by removing `FOR ALL` policy and scoping internal SELECT. | Active Blocker |
| `RES-PULSE-02` | Unvalidated community signals visible prior to agronomic peer review. | Resolved by public read allowlist explicitly excluding `UNVALIDATED...` (D-03). | Active Blocker |
| `GATE01-PROV-01` | Physical provisioning of isolated staging branch unverified in Mode A. | GATE-01 approved on 2026-11-10; physical branch creation unverified offline. | Active Blocker |
| `RES-PULSE-READ-01` | Write-on-read suppression in Regional Pulse GET endpoints. | Resolved by removing revalidation mutations and `db.commit()` from GET routes. | Active Blocker |

---

## 25. RESIDUAL-RISK RECONCILIATION

All five canonical residual risks remain preserved at their recorded governance severities:

| Risk Identifier | Title | Canonical Recorded Severity | Technical Assessment | Mitigation in Remediation Architecture |
|---|---|---|---|---|
| `RES-PULSE-01` | Broad Expert/Researcher SELECT Scope | **MEDIUM** | **HIGH** | Mitigated by decomposing `FOR ALL` and scoping internal SELECT to suppressed rows. |
| `RES-PULSE-02` | Regional Signal Early Visibility ($N \ge 3$) | **MEDIUM** | **MEDIUM** | Mitigated by public read allowlist explicitly excluding `UNVALIDATED...` (D-03). |
| `RES-PRIMARY-ROUTING-01` | Read Endpoint Primary DB Connection Requirement | **MEDIUM** | **MEDIUM** | Mitigated by removing mutations/commits from GET routes, allowing replica offloading. |
| `RES-REPLICA-LAG-01` | Read-Your-Own-Writes Replication Lag | **LOW** | **LOW** | Mitigated by eliminating write-on-read execution on GET routes. |
| `RES-FREE-TEXT-01` | Free-Text Advisory Injection in Regional Signals | **LOW** | **LOW** | Managed via Pydantic input sanitization and schema bounds. |

*Replication Lag Reality:* Eliminating GET commits removes *self-induced* read-your-own-writes replication lag on Regional Pulse, but does not solve cluster-wide replication lag, which remains dependent on database infrastructure.

---

## 26. FUTURE POSTGRESQL TEST CONTRACT

The following pre-implementation test contract specifies the exact verification cases to be executed in PostgreSQL upon authorized transition to **MODE B**:

| Test Contract ID | Target Security Control | Required DB Identity | Required Grants | Test Query / Setup | Expected Outcome | Failure Condition & Impact |
|---|---|---|---|---|---|---|
| **TEST-BYPASS-01** | `ADMIN_BYPASS_SQL` syntax and identity barrier. | `neondb_owner` (with GUC) vs `acrevia_staging_app` | Full catalog access | `SELECT count(*) FROM regional_signals;` with/without GUC and identities. | Only `neondb_owner`/`acrevia_admin` with GUC bypasses RLS. | Syntax error (`DEFECT-SQL-01`) or naked GUC bypass. |
| **TEST-PUB-READ-01** | Public read allowlist enforces D-01 and D-03. | `acrevia_staging_app` (Farmer session) | `SELECT` on `regional_signals` | Query unvalidated ($N=3$), confirmed ($N=3$), and official alert ($N=0$). | Confirmed and official alerts returned; unvalidated hidden. | Unvalidated leaks to farmers, or official alert blocked. |
| **TEST-REC-SEL-01** | Internal SELECT on suppressed rows for recovery. | `acrevia_staging_app` (Expert session) | `SELECT` on `regional_signals` | `SELECT * FROM regional_signals WHERE id = suppressed_id FOR UPDATE;` | Row successfully returned and locked. | `DEFECT-REC-01`: Query returns 0 rows; recovery crashes. |
| **TEST-ADV-SPOOF-01**| Write-side block on official advisory creation. | `acrevia_staging_app` (Expert/Researcher) | `INSERT` on `regional_signals` | Attempt `INSERT` with `validation_status = 'OFFICIAL_ALERT'`. | Fails with SQLSTATE `44000` (`check_violation`). | `DEFECT-AUTH-01`: Non-admin creates official alert! |
| **TEST-TIMESTAMP-01**| Column grant compatibility with SQLAlchemy `updated_at`. | `acrevia_staging_app` | Restricted UPDATE grants | Update signal via SQLAlchemy ORM session flush. | Update succeeds; `updated_at` updated. | `DEFECT-GRANT-01`: Fails with SQLSTATE `42501`. |
| **TEST-CASCADE-01** | Evidence append-only retention against parent delete. | `acrevia_staging_app` | Table grants per crosswalk | Attempt parent DELETE via ORM and direct SQL. | Blocked with SQLSTATE `23001` (`restrict_violation`). | Linked evidence rows purges via cascade! |
| **TEST-GET-IDEMP-01**| Read-only GET endpoint idempotency. | `acrevia_staging_app` (FastAPI TestClient) | `SELECT` on parent/child | Issue 10 consecutive GET requests on valid/suppressed signals. | Zero writes emitted; DB rows completely unmutated. | Write-on-read persists count or suppression mutation. |

---

## 27. DESIGN ALTERNATIVES AND TRADE-OFFS

| Architecture Dimension | Evaluated Alternative | Selected Remediation Design | Security & Operational Trade-Off |
|---|---|---|---|
| **Public Read Boundary** | Dynamic provenance revalidation on GET. | **Option A: Pure Read-Only GET with Explicit Publication Predicate.** | Trade-off: Provenance counts must be maintained at write time or via outbox worker; completely eliminates GET mutations. |
| **Evidence Privacy** | Expose de-identified evidence to farmers. | **Maintain Strict Evidence Table RLS + Response Masking.** | Trade-off: Evidence rows remain 100% inaccessible to farmers; verification delegated to worker. |
| **Administrator Bypass** | Bare GUC `app.is_admin = 'true'`. | **Preserve Dual-Identity `ADMIN_BYPASS_SQL`.** | Trade-off: Slightly longer SQL predicate, but completely prevents GUC spoofing bypasses. |
| **Internal SELECT** | Retain broad `FOR ALL` policy. | **Command-Scoped `FOR SELECT` on Suppressed Rows.** | Trade-off: Requires defining separate policy for recovery, but eliminates statewide cross-district SELECT leakage. |
| **Timestamp Updates** | Omit `updated_at` from column grant. | **Explicit Grant on `updated_at` (or DB Trigger).** | Trade-off: Grants UPDATE on timestamp, but prevents SQLAlchemy ORM flush crashes. |
| **Evidence Retention** | Rely on ORM `cascade="all, delete-orphan"`. | **FK `ON DELETE RESTRICT` + ORM `passive_deletes=True`.** | Trade-off: Requires explicit archival workflow; guarantees zero cascade evidence loss. |

---

## 28. ADVERSARIAL DESIGN REVIEW

This audit subjected the proposed remediation architecture to all twenty-two challenge questions mandated by Section 17:

1. *Is `app.is_admin = 'true'` a valid PostgreSQL policy expression?*  
   **Rebuttal:** **No.** It causes SQL parse error `column app.is_admin does not exist`. It must be rejected (`DEFECT-SQL-01`).
2. *Does checking only the admin GUC preserve the current bypass identity boundary?*  
   **Rebuttal:** **No.** A lone GUC check allows any untrusted connection to execute `SET app.is_admin = 'true'` and bypass RLS.
3. *Is a public official advisory exception safe while non-admin writers can create the matching tuple?*  
   **Rebuttal:** **No.** Without command-scoped write RLS (`DEFECT-AUTH-01`), non-admins could spoof official state alerts.
4. *Does removing `FOR ALL` break recovery?*  
   **Rebuttal:** **Yes**, unless a dedicated internal `FOR SELECT` policy is added (`DEFECT-REC-01`). `SELECT ... FOR UPDATE` evaluates `FOR SELECT`.
5. *Does an UPDATE policy alone provide all SELECT visibility needed by UPDATE and SELECT FOR UPDATE?*  
   **Rebuttal:** **No.** `SELECT ... FOR UPDATE` requires SELECT eligibility under the table's `FOR SELECT` policies.
6. *Can a dedicated worker SELECT policy recreate statewide exposure?*  
   **Rebuttal:** Only if the worker's credentials leak to interactive web users. Bounding the worker to a non-login or private worker principal isolates the scope.
7. *Is the worker role already authorized by DB-AUTH-01?*  
   **Rebuttal:** **No.** It is a proposed extension requiring formal Project Owner sign-off.
8. *Does a dedicated worker session automatically fix evidence false absence?*  
   **Rebuttal:** Yes, because the worker session holds privileged SELECT access on evidence rows, avoiding the farmer child-RLS block.
9. *Does moving revalidation to a worker remove all stale-publication windows?*  
   **Rebuttal:** No. There is an unavoidable reconciliation lag window (100ms–2s) between evidence deletion and worker suppression.
10. *Does removing GET commits eliminate count-only persistent mutations without any other change?*  
    **Rebuttal:** Yes. If the route does not execute `db.commit()`, dirty entity counts in the session are discarded upon session close.
11. *Does `GRANT UPDATE (distinct_farms_count, validation_status)` cover SQLAlchemy updates?*  
    **Rebuttal:** **No.** SQLAlchemy flushes `updated_at`, failing with `42501` unless `updated_at` is granted (`DEFECT-GRANT-01`).
12. *Can `updated_at` be included automatically in ORM UPDATE statements?*  
    **Rebuttal:** Yes. `TimestampMixin` defines `onupdate`, which marks `updated_at` dirty on any entity change.
13. *Does removing `delete-orphan` alone protect evidence?*  
    **Rebuttal:** No. If the database FK remains `CASCADE`, a parent DELETE still cascades child deletion in PostgreSQL.
14. *Does `passive_deletes=True` guarantee parent deletion cannot remove evidence?*  
    **Rebuttal:** Only when paired with database FK `ON DELETE RESTRICT`. Without `RESTRICT`, the database cascades deletion.
15. *Is `ON DELETE RESTRICT` effective if ORM child-delete cascade remains active?*  
    **Rebuttal:** No. The ORM would delete the child rows before parent deletion reaches the database constraint.
16. *Can parent UPDATE be removed without breaking suppression and recovery?*  
    **Rebuttal:** **No.** Revoking parent UPDATE breaks all provenance adjustments, recoveries, and validation transitions.
17. *Does the proposed CHECK constraint include every intended lifecycle state and no incompatible legacy values?*  
    **Rebuttal:** Yes. It covers all 5 service lifecycle states plus reserved administrative state `'SUSPENDED'`.
18. *Is the official advisory exception equivalent to government source authentication?*  
    **Rebuttal:** No. Platform admin authorship does not equal sovereign cryptographic verification (Decision D-02).
19. *Do D-01/D-02/D-03 approvals automatically authorize MODE B?*  
    **Rebuttal:** No. MODE B requires owner sign-off on GATE-02 through GATE-05 in the execution register.
20. *Does GATE-01 remain pending?*  
    **Rebuttal:** No. GATE-01 was formally approved by the Project Owner on 10 November 2026.
21. *Does GET read-only architecture eliminate replica lag?*  
    **Rebuttal:** It eliminates self-induced read-your-own-writes lag on GET routes, but cluster replication lag remains governed by infra.
22. *Does a conditional `CONDITIONALLY_READY_FOR_OWNER_REVIEW` report mean the design is ready to implement?*  
    **Rebuttal:** **No.** Implementation remains strictly unauthorized (`NOT_IMPLEMENTATION_AUTHORIZED`) until owner sign-off.

---

## 29. IMPLEMENTATION-READINESS DECISION

### 29.1 Multi-Dimensional Readiness Assessment

| Evaluation Dimension | Readiness Status | Findings & Pre-Implementation Defect Reconciliation |
|---|---|---|
| **A. Documentation Readiness** | **`READY_FOR_OWNER_REVIEW`** | Comprehensive architectural proof, error tracing, and truth tables completed. |
| **B. Policy Design Readiness** | **`CONDITIONALLY_READY_FOR_OWNER_REVIEW`** | Must correct `DEFECT-SQL-01` (`ADMIN_BYPASS_SQL`), `DEFECT-REC-01` (recovery SELECT), and `DEFECT-AUTH-01`. |
| **C. API / Service Readiness** | **`CONDITIONALLY_READY_FOR_OWNER_REVIEW`** | GET routes ready for read-only refactor; Outbox event emission design established. |
| **D. Database Privilege Readiness**| **`CONDITIONALLY_READY_FOR_OWNER_REVIEW`** | Must correct `DEFECT-GRANT-01` (`updated_at` inclusion) and apply `PRIVILEGE_CROSSWALK`. |
| **E. Worker Readiness** | **`CONDITIONALLY_READY_FOR_OWNER_REVIEW`** | Worker identity and Outbox model designed; requires owner approval under DB-AUTH-01. |
| **F. Governance Readiness** | **`CONDITIONALLY_READY_FOR_OWNER_REVIEW`** | GATE-01 recognized; branch discrepancy and Decisions D-01–03 pending sign-off. |

### 29.2 Overall Design Classification
$$\mathbf{OVERALL\ DESIGN\ CLASSIFICATION:}\quad \mathbf{CONDITIONALLY\_READY\_FOR\_OWNER\_REVIEW}$$

### 29.3 Implementation Authorization Status
$$\mathbf{IMPLEMENTATION\ AUTHORIZATION\ STATUS:}\quad \mathbf{NOT\_IMPLEMENTATION\_AUTHORIZED}$$

*Strict Operational Constraint:* Zero application source files, Alembic migrations, or database roles may be modified until the Project Owner formally resolves the four identified design defects and unlocks execution gates.

---

## 30. EXPLICIT LIMITATIONS AND UNVERIFIED FACTS

1. **Strict MODE A Boundary:** Conducted exclusively via static code analysis, AST inspection, and offline transaction modeling. Zero network calls to Neon Cloud or AWS Singapore were initiated.
2. **Catalog & Grant Uncertainty:** Live table grants, role memberships, and active policy installations in Neon Cloud remain `LIVE_DATABASE_UNVERIFIED`.
3. **No Code Modifications:** Exactly zero application source files, schema definitions, Alembic migrations, or test suites were modified in the workspace.
4. **Advisory Authority:** This report provides security assurance and architectural analysis only; formal operational approval remains the sole authority of the Project Owner.
