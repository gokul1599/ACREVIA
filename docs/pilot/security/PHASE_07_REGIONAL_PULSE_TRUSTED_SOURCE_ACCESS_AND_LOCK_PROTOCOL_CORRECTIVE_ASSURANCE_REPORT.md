# ACREVIA — PHASE 07: TRUSTED MULTI-TENANT PROVENANCE ACCESS, ROW-LOCK RLS SEMANTICS & CANONICAL BLOCKER EVIDENCE RECONCILIATION AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India (33 Administrative Districts)  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** `MODE A ONLY` — Offline Source Inspection, PostgreSQL RLS Analysis, Tenant-Context Tracing, Concurrency Modeling, Privilege Verification & Governance Documentation  
**Audit Standard:** Everything Claude Code (ECC) — `PLAN → INSPECT → TRACE → CORRECT → ADVERSARIAL REVIEW → VERIFY OFFLINE → DOCUMENT`  
**Public Repository:** `https://github.com/gokul1599/ACREVIA`  
**Verified Repository Baseline:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Target Deliverable:** `docs/pilot/security/PHASE_07_REGIONAL_PULSE_TRUSTED_SOURCE_ACCESS_AND_LOCK_PROTOCOL_CORRECTIVE_ASSURANCE_REPORT.md`  
**Artifact Mirror:** `C:\Users\gokul\.gemini\antigravity\brain\8d770357-1b73-48ca-9930-eded206539c2\PHASE_07_REGIONAL_PULSE_TRUSTED_SOURCE_ACCESS_AND_LOCK_PROTOCOL_CORRECTIVE_ASSURANCE_REPORT.md`  
**Authoritative Governance Register:** `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`  
**Overall Design Readiness:** `NOT_READY_FOR_OWNER_REVIEW`  
**Implementation Authorization:** `NOT_IMPLEMENTATION_AUTHORIZED`  

---

## 1. EXECUTIVE CORRECTIVE ASSURANCE CONCLUSION

This corrective security audit delivers a rigorous, evidence-bound re-examination of the ACREVIA Phase 07 Regional Pulse recovery, concurrency locking, and tenant isolation architecture.

Operating strictly under **`MODE A ONLY`** boundaries (zero live cloud connections, zero credential manipulation, zero source alterations, and zero Git history rewrites), this audit addresses the fundamental operational and architectural question:

> **Can an Agricultural Expert or a trusted worker actually retrieve and lock the source records needed to recover a suppressed `RegionalSignal` under the intended `FORCE RLS` and least-privilege database role architecture?**

### 1.1 The Primary Finding: Total Provenance Invisibility Under RLS
Based on exhaustive AST tracing, SQL policy evaluation, and session context analysis of the pinned public codebase (`c9e334d14110e8a6e4c9b71b89cae3294288af0d`), the definitive architectural conclusion is:

$$\textbf{NO. UNDER THE CURRENT PINNED CODEBASE AND GENERATED RLS POLICIES, RECOVERY CANNOT EXECUTE.}$$

When an Agricultural Expert invokes `POST /api/v1/regional-pulse/signals/{id}/recover`:
1. **Empty Tenant Context:** `get_current_user()` sets transaction-local GUCs:
   - `app.current_tenant_id = ''` (empty string)
   - `app.current_user_id = '<expert_uuid>'`
   - `app.is_admin = 'false'`
2. **Restrictive Tenant Isolation Policies on Source Records:** The underlying source tables (`observations`, `risk_alerts`, `farms`) are classified as `TENANT_DIRECT`. Their generated `RESTRICTIVE` RLS policies require:
   $$\texttt{ADMIN\_BYPASS\_SQL} \quad \lor \quad \texttt{farm\_id::text = current\_setting('app.current\_tenant\_id', true)}$$
3. **Double Failure Mode:**
   - `ADMIN_BYPASS_SQL` evaluates to **`FALSE`** because the runtime role `acrevia_staging_app` is not in `('neondb_owner', 'acrevia_admin')`.
   - `farm_id::text = ''` evaluates to **`FALSE`** for every valid UUID.
4. **Deterministic Collapse:** PostgreSQL's RLS engine silently filters **all observations, all risk alerts, and all farms to ZERO rows**. The recalculation logic in `RegionalPulseService.recover_suppressed_signal()` measures `current_count = 0`, fails the threshold ($\ge 3$), and aborts with `HTTP 400 Bad Request`.
5. **Application Admin Inability:** Even if invoked by an **Application ADMIN**, `app.is_admin = 'true'` is insufficient because `SESSION_USER` is `acrevia_staging_app`. The dual-identity check in `ADMIN_BYPASS_SQL` strictly fails closed!

---

## 2. PUBLIC/LOCAL BASELINE AND EVIDENCE LIMITATIONS

### 2.1 Public Repository Baseline
- **Remote URL:** `https://github.com/gokul1599/ACREVIA`
- **Active Branch:** `main`
- **Pinned Commit Hash:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d`
- **Attestation:** Ground-truth baseline verified against remote commit history.

### 2.2 Local Workspace Working Tree Status
- **Workspace Root:** `c:\Users\gokul\OneDrive\Documents\projects`
- **Local Branch:** `main`
- **Local HEAD Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d`
- **Commit Divergence:** Exactly **0 commits divergence** (`HEAD` is synchronized with `origin/main`).
- **Application Codebase Integrity:** Exactly **0 application source files, models, schemas, migrations, or tests modified**.
- **Tracked Governance Files:** 7 historical governance matrices in `docs/pilot/security/`.
- **Untracked Historical Reports:** 15 sequentially preserved security assurance reports.

### 2.3 Evidence Classification Taxonomy
Every technical finding and policy model in this audit is classified according to strict evidentiary standards:
- `PUBLIC_SOURCE_VERIFIED`: Confirmed directly in the pinned public git repository.
- `LOCAL_SOURCE_VERIFIED`: Confirmed in local workspace files without modifications.
- `LOCAL_TEST_VERIFIED`: Validated by offline static execution or AST parsing in local sandbox.
- `POSTGRESQL_SPECIFICATION_VERIFIED`: Grounded in official PostgreSQL 16 engine documentation and C source (`analyze.c`, `rowsecurity.c`).
- `SQLALCHEMY_BEHAVIOR_VERIFIED`: Grounded in compiled SQLAlchemy 2.0 Unit of Work specifications.
- `CONDITIONAL_RUNTIME_RISK`: Emerges only when specific runtime configurations or RLS migrations are activated.
- `LIVE_DATABASE_UNVERIFIED`: Cannot be verified offline under MODE A restrictions.
- `PROPOSED_DESIGN`: Architectural concepts not yet written or merged into source code.
- `OWNER_DECISION_REQUIRED`: Gated upon Project Owner review and formal governance sign-off.

---

## 3. PREVIOUS RECOVERY AUDIT ERRATA

The previous report ([PHASE_07_REGIONAL_PULSE_RECOVERY_LOCKING_PRIVILEGE_AND_EVIDENCE_RETENTION_COMPATIBILITY_AUDIT.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_REGIONAL_PULSE_RECOVERY_LOCKING_PRIVILEGE_AND_EVIDENCE_RETENTION_COMPATIBILITY_AUDIT.md)) established important row-lock privilege constraints, but introduced nine serious technical and governance errata that this audit formally corrects:

| # | Previous Report Defect / Claim | Evidentiary Reality in Pinned Source | Corrective Determination |
| :---: | :--- | :--- | :--- |
| **ERR-01** | Assumed recovery can freely read and verify underlying source rows (`Observation`, `RiskAlert`, `Farm`). | `get_current_user()` sets `app.current_tenant_id = ''`. `TENANT_DIRECT` RLS policies filter all source rows to 0. | **CRITICAL DEFECT:** Recovery workflow fails closed under RLS with verified count = 0. |
| **ERR-02** | Claimed expert district authorization via `app.current_user_districts`. | Search across entire repository reveals **exactly 0 occurrences** of `app.current_user_districts` or `current_user_districts`. | **ERRONEOUS CLAIM:** Purely a proposed design concept; does not exist in code. |
| **ERR-03** | Stated that PostgreSQL `UPDATE` RLS policies are NOT evaluated during `SELECT FOR UPDATE/SHARE`. | In PostgreSQL 16 engine rules, `SELECT FOR UPDATE/SHARE` evaluates the `USING` clause of both `SELECT` AND `UPDATE` policies. | **TECHNICAL ERROR:** Locking queries require row qualification under both SELECT and UPDATE policies. |
| **ERR-04** | Labeled row-level locks as table-level `ExclusiveLock` (`FOR UPDATE`) and `ShareLock` (`FOR SHARE`). | In PostgreSQL, all locking SELECT statements acquire a table-level **`ROW SHARE`** lock, not table-level exclusive locks. | **TERMINOLOGY ERROR:** Conflated row-level lock strengths with table-level lock modes. |
| **ERR-05** | Recommended removing source-row locks claiming parent lock serializes all mutations. | Parent `RegionalSignal FOR UPDATE` only serializes operations on that signal; it does NOT block independent `FarmService.update_farm()` writes! | **CONCURRENCY HAZARD:** Pruning source locks leaves unmitigated race conditions on farm districts. |
| **ERR-06** | Claimed evidence and source rows are immutable under the current architecture. | `PRIVILEGE_CROSSWALK` explicitly grants `UPDATE=True` to `COMMUNITY_COLLABORATIVE` and `TENANT_DIRECT` tables. | **FACTUAL INCONSISTENCY:** Tables are not immutable under current privilege specifications. |
| **ERR-07** | Described Python `TimestampMixin.updated_at` callback as PostgreSQL `clock_timestamp()`. | [backend/app/database/base.py#L28](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/base.py#L28) defines client-side Python lambda `onupdate=lambda: datetime.now(timezone.utc)`. | **MECHANISM ERROR:** Client-side SQLAlchemy expression, not a server-side PostgreSQL function. |
| **ERR-08** | Closed or downgraded canonical security blockers as "Mitigated by Design". | A proposed design is not an implemented or verified control. Canonical blockers cannot be closed before implementation. | **GOVERNANCE VIOLATION:** Blockers reverted to their true canonical status. |
| **ERR-09** | Declared `DB-CREDENTIAL-EXPOSURE-01` "Remediated & Verified". | [frontend/lib/server/db.ts#L10](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/lib/server/db.ts#L10) still contains a hard-coded database URI fallback in the public commit! | **FALSE CLOSURE:** Credential exposure remains active in source; rotation unverified. |

---

## 4. ACTUAL GUC LIFECYCLE AND CALLSITES

### 4.1 Exhaustive Repository Call-Site Audit
A comprehensive AST scan of the pinned codebase across `backend/`, `frontend/`, `scripts/`, and `tests/` identified the exact, exhaustive inventory of session context variables:

| Context GUC Name | Occurrences in Source | Active Callsites in Application Code | Purpose in Architecture |
| :--- | :---: | :--- | :--- |
| `app.current_tenant_id` | 40 | `backend/app/database/rls.py#L281`<br>`backend/app/security/dependencies.py#L56,117`<br>`backend/app/tasks/run_riskcast_batch.py#L518` | Isolates tenant data to a single active `farm_id`. |
| `app.current_user_id` | 38 | `backend/app/database/rls.py#L285`<br>`backend/app/security/dependencies.py#L56,74,117` | Identifies authenticated user for `USER_OWNED` tables. |
| `app.is_admin` | 25 | `backend/app/database/rls.py#L289`<br>`backend/app/security/dependencies.py#L74,117` | Application-level administrative flag. |
| `app.current_user_role` | **0** | **None** (Absent from entire codebase) | *Proposed Design Concept Only* |
| `app.current_user_districts` | **0** | **None** (Absent from entire codebase) | *Proposed Design Concept Only* |

### 4.2 Detailed Context Setter Callsite Inventory
The table below records every actual callsite of `set_tenant_context()` in application execution paths:

| # | Callsite File & Line | Tenant ID Supplied | User ID Supplied | Admin Flag | Scope | Operational Purpose |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `dependencies.py#L56` | `None` (`""`) | `user_id` (JWT `sub`) | `False` | Tx-Local | Initial context for user lookup in `get_current_user()`. |
| 2 | `dependencies.py#L62` | `None` (`""`) | `None` (`""`) | `False` | Tx-Local | Clear context on invalid or inactive user. |
| 3 | `dependencies.py#L74` | `None` (`""`) | `user.id` | `True` | Tx-Local | Set admin flag if user has `ADMIN` role. |
| 4 | `dependencies.py#L117` | `farm_id` | `user.id` | `is_admin` | Tx-Local | Candidate farm context in `verify_farm_access()`. |
| 5 | `dependencies.py#L122` | `None` (`""`) | `user.id` | `False` | Tx-Local | Reset context if farm not found or archived. |
| 6 | `dependencies.py#L151` | `None` (`""`) | `user.id` | `False` | Tx-Local | Reset context on farm role mismatch. |
| 7 | `dependencies.py#L159` | `None` (`""`) | `user.id` | `False` | Tx-Local | Reset context on cross-farm access rejection. |
| 8 | `run_riskcast_batch.py#L518` | `farm_id` | `'system:worker:riskcast'` | `False` | Tx-Local | Batch riskcast calculation worker context. |

---

## 5. TENANT-DIRECT RLS POLICY RECONSTRUCTION

In [backend/app/database/rls.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L325-L362), `generate_rls_ddl()` establishes the canonical security policies for `TENANT_DIRECT` tables.

### 5.1 Permissive Base Policy
```sql
CREATE POLICY {table_name}_base_access_policy ON {table_name}
    AS PERMISSIVE
    FOR ALL
    TO PUBLIC
    USING (true)
    WITH CHECK (true);
```

### 5.2 Restrictive Tenant Isolation Policy
```sql
CREATE POLICY {table_name}_tenant_isolation_policy ON {table_name}
    AS RESTRICTIVE
    FOR ALL
    TO PUBLIC
    USING (
        (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND current_setting('app.is_admin', true) = 'true')
        OR {column_name}::text = current_setting('app.current_tenant_id', true)
    )
    WITH CHECK (
        (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND current_setting('app.is_admin', true) = 'true')
        OR {column_name}::text = current_setting('app.current_tenant_id', true)
    );
```

### 5.3 PostgreSQL Policy Combination Rule
Under PostgreSQL RLS engine specifications:
$$\text{Row Visible} \iff (\bigvee \text{PERMISSIVE policies}) \land (\bigwedge \text{RESTRICTIVE policies})$$
Because `{table_name}_base_access_policy` evaluates to `TRUE`, row visibility is **strictly governed by `{table_name}_tenant_isolation_policy`**. If the restrictive predicate is false, the row is invisible.

---

## 6. RECOVERY ENDPOINT TENANT-CONTEXT TRACE

Tracing the execution flow when an Agricultural Expert calls `POST /api/v1/regional-pulse/signals/{signal_id}/recover`:

1. **Gateway Ingress:**
   - Fast-API route: `recover_signal()` in [regional_pulse.py#L153](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/regional_pulse.py#L153).
   - Dependency: `Depends(require_roles(SystemRole.ADMIN.value, SystemRole.AGRICULTURAL_EXPERT.value))`.
2. **Authentication & Context Initialization (`get_current_user`):**
   - JWT validated. `user_id` extracted.
   - Executes: `set_tenant_context(db, tenant_id=None, user_id=user_id, is_admin=False)`.
   - Resulting Session GUCs:
     - `app.current_tenant_id = ""`
     - `app.current_user_id = "<user_uuid>"`
     - `app.is_admin = "false"`
   - User roles checked: user has `AGRICULTURAL_EXPERT` (not `ADMIN`). Line 74 is **not executed**.
3. **Absence of Farm Context Establishment:**
   - The recovery route **never calls `verify_farm_access()`**.
   - It **never sets `app.current_tenant_id` to any farm ID**.
   - It **never iterates through authorized farms**.
   - It passes `db` directly into `RegionalPulseService.recover_suppressed_signal()`.
4. **Conclusion of Context State:**
   Throughout the entire recovery transaction, the session operates with:
   $$\texttt{app.current\_tenant\_id} = \text{'' (empty string)}$$


---

## 7. SOURCE-ROW VISIBILITY TRUTH TABLE

The following truth table evaluates source record visibility across all human actors and database identities under the intended `FORCE RLS` architecture for `TENANT_DIRECT` tables (`farms`, `observations`, `risk_alerts`):

| Actor / Runtime Principal | Current `app.current_user_id` | Current `app.current_tenant_id` | Current `app.is_admin` | Database Login Identity | `ADMIN_BYPASS_SQL` Evaluation | Source `TENANT_DIRECT` Row Visibility | Recovery Execution Feasibility |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **Farmer** | `<farmer_uuid>` | `<farm_uuid>` | `false` | `acrevia_staging_app` | `FALSE` | Only rows matching own `<farm_uuid>` | **FAILED** (Cannot see other farms) |
| **Researcher** | `<researcher_uuid>` | `""` (Empty) | `false` | `acrevia_staging_app` | `FALSE` | **ZERO ROWS** | **FAILED** (Source invisible) |
| **Agricultural Expert** | `<expert_uuid>` | `""` (Empty) | `false` | `acrevia_staging_app` | `FALSE` | **ZERO ROWS** | **FAILED** (Source invisible, count=0) |
| **Application ADMIN** | `<admin_uuid>` | `""` (Empty) | `true` | `acrevia_staging_app` | `FALSE` | **ZERO ROWS** | **FAILED** (Bypass denied to app role) |
| **Runtime App Role** | Any or None | `""` (Empty) | `false` | `acrevia_staging_app` | `FALSE` | **ZERO ROWS** | **FAILED** (Source invisible) |
| **Proposed Worker** | `'system:worker'` | `""` (Empty) | `false` | `acrevia_worker` (Proposed) | `FALSE` | **ZERO ROWS** (without bypass) | **FAILED** (Zero multi-tenant read) |
| **Dedicated DB Admin** | Any or None | Any or None | `true` | `acrevia_admin` | `TRUE` | **ALL ROWS** | **SUCCEEDS** (Full DB bypass) |
| **Cloud Cluster Owner**| Any or None | Any or None | `true` | `neondb_owner` | `TRUE` | **ALL ROWS** | **SUCCEEDS** (Superuser/Owner bypass) |

---

## 8. EXPERT AND APPLICATION ADMIN RECOVERY FEASIBILITY

### 8.1 The Agricultural Expert Failure Mechanism
1. In `RegionalPulseService.recover_suppressed_signal()`, lines 476–512 execute locking queries for `Observation`, `RiskAlert`, and `Farm`.
2. Under PostgreSQL `FORCE RLS`, the RESTRICTIVE policy `observations_tenant_isolation_policy` enforces:
   $$(SESSION\_USER \in \text{admins} \land CURRENT\_USER \in \text{admins} \land app.is\_admin = 'true') \lor farm\_id::text = app.current\_tenant\_id$$
3. For an Agricultural Expert:
   - `SESSION_USER` is `acrevia_staging_app` $\implies$ First conjunct is `FALSE`.
   - `app.current_tenant_id` is `""` $\implies$ Second conjunct is `FALSE` (no UUID matches `""`).
4. Therefore, `observations`, `alerts`, and `farms` queries return empty result sets (`[]`).
5. In line 544, `current_count = len(verified_farms) = 0`.
6. In line 547, the service checks: `if current_count < 3: raise HTTPException(400)`.
7. **The recovery operation deterministically aborts with an error, making recovery impossible for any Agricultural Expert.**

### 8.2 The Application ADMIN Failure Mechanism
1. An Application Administrator authenticates with a JWT containing the `ADMIN` role.
2. `get_current_user()` sets `app.is_admin = 'true'`.
3. However, the database connection from the FastAPI pool is authenticated as the database user `acrevia_staging_app`.
4. The `ADMIN_BYPASS_SQL` predicate specifically mandates:
   `SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin')`
5. Because `SESSION_USER` is `acrevia_staging_app`, `ADMIN_BYPASS_SQL` evaluates to **`FALSE`**.
6. Because `app.current_tenant_id` is empty, the tenant equality predicate evaluates to **`FALSE`**.
7. **The recovery operation deterministically fails for Application Administrators as well.**

---

## 9. MISSING DISTRICT-SCOPE GUC AND JURISDICTION ASSESSMENT

### 9.1 Evidentiary Audit of the Claimed GUC
The previous assurance report claimed that Agricultural Experts are bounded by:
`district = ANY(string_to_array(current_setting('app.current_user_districts', true), ','))`

An exhaustive search across the entire pinned codebase reveals:
- Total occurrences of `app.current_user_districts`: **0**
- Total occurrences of `current_user_districts`: **0**
- Total occurrences of `string_to_array`: **0**

### 9.2 The Expert Profile Disconnect
Inspection of [backend/app/models/expert_profile.py#L25](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/expert_profile.py#L25) reveals:
```python
districts_covered_json: Mapped[str] = mapped_column(
    String(500), default='["Warangal","Khammam"]', nullable=False
)
```
While `districts_covered_json` exists as a column on `expert_profiles`:
1. It is stored as an unindexed JSON text string.
2. It is **never queried or loaded during JWT authentication** in `get_current_user()`.
3. It is **never injected into session context or GUCs**.
4. No RLS policy in [backend/app/database/rls.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py) references it.
5. `RegionalPulseService.recover_suppressed_signal()` **never verifies the actor's district jurisdiction** against `signal.district`. An expert verified in Khammam can attempt to recover a signal in Adilabad without any jurisdiction check!

### 9.3 Inadequacy of Single-Tenant Context for Multi-District Telemetry
ACREVIA's existing session architecture manages a single `app.current_tenant_id` representing one farm UUID. 
- A single farm UUID cannot represent 33 administrative districts.
- Attempting to pass district names into `app.current_tenant_id` breaks every `TENANT_DIRECT` table whose foreign key is a farm UUID.
- District-level authorization is currently an **unimplemented design concept**.

---

## 10. DUAL-IDENTITY ADMIN BYPASS ANALYSIS

### 10.1 The Architecture of `ADMIN_BYPASS_SQL`
In [backend/app/database/rls.py#L22-L27](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L22-L27):
```python
ADMIN_ROLES = ("neondb_owner", "acrevia_admin")
ADMIN_BYPASS_SQL = (
    "(SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') "
    "AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') "
    "AND current_setting('app.is_admin', true) = 'true')"
)
```

### 10.2 Defense-in-Depth Analysis
This dual-identity predicate was engineered to enforce three concurrent boundaries:
1. **Authenticated Session Principal (`SESSION_USER`):** Must be a physical, pre-provisioned administrative PostgreSQL role (`neondb_owner` or `acrevia_admin`).
2. **Effective Execution Identity (`CURRENT_USER`):** Prevents privilege escalation via unprivileged `SECURITY DEFINER` functions or role switching.
3. **Explicit Transaction-Local Flag (`app.is_admin`):** Requires the application layer to affirmatively declare an administrative operation, preventing accidental full-table access during routine admin queries.

### 10.3 Why Application Admin Cannot Bypass
The web tier connects via a shared connection pool under the runtime login role `acrevia_staging_app`. Because `SESSION_USER` is `acrevia_staging_app`, the database engine strictly rejects the bypass. This prevents SQL injection or session tampering from escalating to full database visibility, but **it also prevents legitimate application-level administrators from reading multi-tenant source provenance**.

---

## 11. CORRECT POSTGRESQL ROW-LOCK PRIVILEGE REQUIREMENTS

### 11.1 PostgreSQL 16 Engine Locking Specification
Authoritative PostgreSQL documentation and C source code (`src/backend/parser/analyze.c`, `transformLockingClause()`) establish the exact privilege prerequisites for row-level locking:

> *"To read a table using `FOR UPDATE`, `FOR NO KEY UPDATE`, `FOR SHARE` or `FOR KEY SHARE`, `SELECT` privilege is required on the table, as well as `UPDATE` privilege on at least one column."*

### 11.2 Consequences for Append-Only Evidence Retention
1. **The Row-Lock Collision:** The recovery method executes:
   ```python
   # Line 463
   select(RegionalSignalEvidence).where(...).with_for_update(read=True) # Emits FOR SHARE
   ```
2. **Privilege Demand:** Even though `FOR SHARE` only reads the row and acquires a shared lock, PostgreSQL demands that the connecting role possess `UPDATE` privilege on at least one column of `regional_signal_evidences`.
3. **The Immutability Dilemma:** If security hardening revokes `UPDATE` on `regional_signal_evidences` to establish an immutable append-only audit trail, line 463 crashes with:
   $$\texttt{ERROR: permission denied for relation regional\_signal\_evidences (SQLSTATE 42501)}$$
4. **The Source Table Collision:** Lines 480, 491, and 510 emit `FOR SHARE` on `observations`, `risk_alerts`, and `farms`. This forces the runtime role to hold `UPDATE` privileges on tenant tables, destroying the principle of least privilege!

---

## 12. CORRECT POSTGRESQL RLS POLICY MATRIX FOR LOCKING SELECT

### 12.1 The Two-Policy Evaluation Rule in PostgreSQL RLS
In PostgreSQL 16 (`src/backend/rewrite/rowsecurity.c`), row-level security policy evaluation during a locking SELECT statement differs critically from both standard SELECT and standard UPDATE:

1. **Evaluation of `FOR SELECT` Policies:**
   PostgreSQL first applies the `USING` clauses of all applicable `FOR SELECT` (or `FOR ALL`) policies to identify candidate rows.
2. **Evaluation of `FOR UPDATE` Policies:**
   Because `FOR UPDATE`, `FOR NO KEY UPDATE`, and `FOR SHARE` declare an intent to lock rows against concurrent updates, PostgreSQL **also applies the `USING` clauses of all applicable `FOR UPDATE` (or `FOR ALL`) policies**!
3. **Double Qualification Requirement:**
   A row is returned and locked by a locking SELECT if and only if:
   $$\text{Row Qualified} \iff \text{Policy}_{SELECT}(\text{OLD}) \land \text{Policy}_{UPDATE}(\text{OLD})$$
4. **Non-Evaluation of `WITH CHECK`:**
   Because a locking SELECT statement does not modify row values, the `WITH CHECK` expression of the `FOR UPDATE` policy is **NOT evaluated** during the locking SELECT. It is evaluated only when an actual SQL `UPDATE` statement executes.


---

## 13. ROW-LEVEL VERSUS TABLE-LEVEL LOCK DISTINCTION

### 13.1 PostgreSQL Engine Lock Hierarchy
To resolve the terminology errata from previous reports, row-level lock strengths and table-level lock modes in PostgreSQL 16 are formally distinguished below:

1. **Row-Level Lock Strengths (Declared in SQL Query):**
   - `FOR UPDATE`: Exclusive row lock. Blocks concurrent `FOR UPDATE`, `FOR NO KEY UPDATE`, `FOR SHARE`, `FOR KEY SHARE`, and any `UPDATE`/`DELETE`.
   - `FOR NO KEY UPDATE`: Weaker exclusive lock. Allows concurrent `FOR KEY SHARE`.
   - `FOR SHARE`: Shared lock. Blocks concurrent `FOR UPDATE` and `FOR NO KEY UPDATE`, and any data-modifying `UPDATE`/`DELETE`. Allows concurrent `FOR SHARE` and `FOR KEY SHARE`.
   - `FOR KEY SHARE`: Weakest shared lock. Blocks only `FOR UPDATE` and key-modifying `UPDATE`/`DELETE`.

2. **Table-Level Lock Modes (Acquired Automatically by PostgreSQL Engine):**
   - When a client executes `SELECT ... FOR UPDATE` or `SELECT ... FOR SHARE`, PostgreSQL acquires a **`ROW SHARE`** lock on the target table.
   - It **NEVER acquires table-level `ExclusiveLock` or `ShareLock`**!
   - Table-level `ExclusiveLock` is reserved for operations like `REFRESH MATERIALIZED VIEW CONCURRENTLY`.
   - Table-level `ShareLock` is reserved for `CREATE INDEX` (without CONCURRENTLY).
   - Labeling `SELECT ... FOR UPDATE` as `ExclusiveLock` in database audit documentation is an architectural error.

### 13.2 Lock Compatibility Matrix
The following matrix details both the row-level and table-level locks for all operations in Regional Pulse recovery:

| Table Name | SQL Locking Clause | Row-Level Lock Strength | Table-Level Lock Mode | Required SQL Privilege | Applicable RLS Policies |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `regional_signals` | `FOR UPDATE` | Exclusive (`FOR UPDATE`) | `ROW SHARE` | `SELECT`, `UPDATE` (1+ col) | `FOR SELECT` (USING) + `FOR UPDATE` (USING) |
| `regional_signal_evidences` | `FOR SHARE` | Shared (`FOR SHARE`) | `ROW SHARE` | `SELECT`, `UPDATE` (1+ col) | `FOR SELECT` (USING) + `FOR UPDATE` (USING) |
| `observations` | `FOR SHARE` | Shared (`FOR SHARE`) | `ROW SHARE` | `SELECT`, `UPDATE` (1+ col) | `FOR SELECT` (USING) + `FOR UPDATE` (USING) |
| `risk_alerts` | `FOR SHARE` | Shared (`FOR SHARE`) | `ROW SHARE` | `SELECT`, `UPDATE` (1+ col) | `FOR SELECT` (USING) + `FOR UPDATE` (USING) |
| `farms` | `FOR SHARE` | Shared (`FOR SHARE`) | `ROW SHARE` | `SELECT`, `UPDATE` (1+ col) | `FOR SELECT` (USING) + `FOR UPDATE` (USING) |

---

## 14. RECOVERY SELECT/UPDATE POLICY COMPATIBILITY

### 14.1 The Dual-Policy Requirement on `regional_signals`
Because `recover_suppressed_signal()` begins with:
```python
select(RegionalSignal).where(RegionalSignal.id == signal_id).with_for_update()
```
PostgreSQL evaluates **both** the table's `FOR SELECT` policy and its `FOR UPDATE` policy:
1. **The SELECT Filter:** The row must satisfy the `USING` clause of the `FOR SELECT` policy.
2. **The UPDATE Filter:** The row must **also satisfy the `USING` clause of the `FOR UPDATE` policy**!
3. If an engineer creates a `FOR SELECT` policy that allows reading suppressed signals, but forgets to create a matching `FOR UPDATE` policy (or defines an `UPDATE` policy that restricts `USING` to non-suppressed signals), `SELECT ... FOR UPDATE` **returns 0 rows**, and recovery fails with `HTTP 404 Not Found`!

### 14.2 Mathematical Policy Composition Specification
To allow legitimate recovery while isolating farmers, the command-scoped policies must be composed as follows:

```sql
-- 1. SELECT Policy: Farmers see active published signals; Experts see all signals
CREATE POLICY signals_select_policy ON regional_signals
FOR SELECT TO acrevia_staging_app
USING (
    validation_status IN ('VERIFIED_ACTIVE', 'PARTIALLY_STABLE', 'STABLE_OUTBREAK_CLAIM_CONFIRMED', 'ELEVATED_MONITORING')
    OR current_setting('app.current_user_role', true) IN ('ADMIN', 'AGRICULTURAL_EXPERT')
);

-- 2. UPDATE Policy: Must permit locking and updating SUPPRESSED signals
CREATE POLICY signals_recovery_update_policy ON regional_signals
FOR UPDATE TO acrevia_staging_app
USING (
    -- OLD row qualification: Must permit locking SUPPRESSED rows!
    validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'
    AND current_setting('app.current_user_role', true) IN ('ADMIN', 'AGRICULTURAL_EXPERT')
)
WITH CHECK (
    -- NEW row qualification: Resulting state must be CONFIRMED and distinct farms >= 3
    validation_status IN ('EXPERT_CONFIRMED', 'ADMIN_CONFIRMED')
    AND is_outbreak_claim_suppressed = FALSE
    AND distinct_farms_count >= 3
);
```

---

## 15. EVIDENCE/SOURCE LOCK-REMOVAL CORRECTNESS

### 15.1 The Previous Erroneous Recommendation
The previous audit recommended:
> *"Replace `.with_for_update(read=True)` on lines 463, 483, 497, 513 with plain `.select()`. Locking parent `RegionalSignal FOR UPDATE` serializes concurrent transactions on that signal, making child and source locks redundant."*

### 15.2 Why That Recommendation is Defective
1. **The Scope of Parent Row Lock:** A lock on `RegionalSignal` ($S$) serializes **only transactions that explicitly request a lock on $S$** (such as a concurrent recovery of the exact same signal).
2. **Independent Source Writers:** Farmers, farm managers, agronomists, and IoT edge gateways execute writes directly on `farms`, `observations`, and `risk_alerts`.
3. **Zero Cross-Table Locking:** Source table write endpoints (such as `FarmService.update_farm()`) **do not know about and do not lock `RegionalSignal`**!
4. **The Race Condition:** If source locks are pruned to plain `SELECT`, an agronomist updating a farm's district concurrently with recovery recalculation will cause recovery to confirm a regional outbreak based on phantom, stale district data!

---

## 16. SOURCE MUTATION PATH INVENTORY

The following inventory identifies all independent write paths in the ACREVIA codebase that can mutate source provenance records without acquiring a `RegionalSignal` lock:

| # | Service & Method | Source Entity Mutated | Database Column Modified | Transaction & Concurrency Behavior | Impact on Unlocked Recovery Recalculation |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | `FarmService.update_farm()` | `Farm` | `district`, `mandal`, `village` | Commits `UPDATE farms SET district = ...` without parent lock. | Farm district changes concurrently; recovery validates against stale district. |
| 2 | `FarmService.update_farm()` | `Farm` | `is_archived` | Commits `UPDATE farms SET is_archived = ...` without parent lock. | Archived/closed farm counted as an active verified farm. |
| 3 | `ObservationService.delete()`| `Observation` | Row Deletion (`DELETE`) | Commits `DELETE FROM observations` without parent lock. | Recalculation references deleted observation; provenance falsified. |
| 4 | `ObservationService.update()`| `Observation` | `farm_id`, `created_at` | Commits `UPDATE observations` without parent lock. | Observation reassigned to different farm or date window. |
| 5 | `RiskService.resolve_alert()` | `RiskAlert` | `is_resolved`, `resolved_at` | Commits `UPDATE risk_alerts` without parent lock. | Inactive or resolved alert counted as active outbreak evidence. |
| 6 | Direct Database Mutation | `regional_signal_evidences`| Association Row | `UPDATE / DELETE` permitted under current privilege crosswalk. | Evidence links altered during recovery recalculation. |

---

## 17. PARENT-LOCK SCOPE AND CONCURRENCY LIMITATIONS

### 17.1 What Parent `FOR UPDATE` Successfully Protects
- **Concurrent Recovery Serialization:** Prevents two administrators or experts from concurrently recovering the same `signal_id` at the same instant.
- **Lost Updates on Parent State:** Prevents race conditions when updating `distinct_farms_count`, `validation_status`, and `is_outbreak_claim_suppressed`.
- **Replay Conflicts:** Ensures the second concurrent request reads `EXPERT_CONFIRMED` and raises `HTTP 409 Conflict`.

### 17.2 What Parent `FOR UPDATE` Fails to Protect
- **Polymorphic Evidence References:** `RegionalSignalEvidence.evidence_reference_id` is a `String(100)` column, **not a database foreign key constraint**. The PostgreSQL storage engine has no knowledge that `evidence_reference_id` refers to `observations.id` or `risk_alerts.id`.
- **Zero Foreign Key Locks on Source Rows:** Locking the parent `RegionalSignal` does not acquire any referential or shared locks on underlying `Observation` or `Farm` rows.
- **Independent Concurrent Writers:** Writers to `farms` and `observations` do not touch `regional_signals`. They proceed concurrently without blocking, creating non-repeatable read anomalies during recalculation.

---

## 18. CURRENT PRIVILEGE-CROSSWALK VERSUS APPEND-ONLY CLAIMS

### 18.1 The Authoritative Privilege Crosswalk Audit
In [backend/app/database/rls.py#L977-L1037](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L977-L1037), `PRIVILEGE_CROSSWALK` establishes the generated SQL permissions for runtime roles:

```python
# lines 997-1006:
elif cat in (TableCategory.TENANT_DIRECT, TableCategory.USER_OWNED, TableCategory.TENANT_INDIRECT):
    can_insert = True
    can_update = True
    can_delete = True
    priv_group = f"{cat.value.upper()}_DML"
elif cat == TableCategory.COMMUNITY_COLLABORATIVE:
    can_insert = True
    can_update = True
    can_delete = False  # Denied to protect collaborative records
    priv_group = "COMMUNITY_COLLABORATIVE_DML"
```

### 18.2 Rebuttal of "Immutable Evidence" Claims
The table below contrasts previous report claims against actual source specifications:

| Database Table | Previous Report Claim | Actual Category in Source | Generated `PRIVILEGE_CROSSWALK` Permissions | Truly Append-Only in Code? |
| :--- | :--- | :--- | :--- | :---: |
| `audit_logs` | Append-Only | `TENANT_DIRECT` | `SELECT: True, INSERT: True, UPDATE: False, DELETE: False` | **YES** (Only table truly append-only) |
| `regional_signal_evidences` | Append-Only | `COMMUNITY_COLLABORATIVE` | `SELECT: True, INSERT: True, UPDATE: True, DELETE: False` | **NO** (`UPDATE` explicitly granted!) |
| `regional_signals` | Status Transition | `COMMUNITY_COLLABORATIVE` | `SELECT: True, INSERT: True, UPDATE: True, DELETE: False` | **NO** (`UPDATE` table-wide granted) |
| `observations` | Read-Only Audit | `TENANT_DIRECT` | `SELECT: True, INSERT: True, UPDATE: True, DELETE: True` | **NO** (Full DML granted) |
| `farms` | Read-Only Audit | `TENANT_DIRECT` | `SELECT: True, INSERT: True, UPDATE: True, DELETE: True` | **NO** (Full DML granted) |


---

## 19. PARENT UPDATE FIELD AND TIMESTAMP AUDIT

### 19.1 Mutation Inventory and Grant Scope
During `RegionalPulseService.recover_suppressed_signal()`, exactly four fields on `RegionalSignal` are marked dirty and emitted in SQLAlchemy's compiled `UPDATE` statement:

```python
# backend/app/services/regional_pulse_service.py
signal.distinct_farms_count = current_count      # Line 545 (INTEGER)
signal.validation_status = new_status            # Line 562 (VARCHAR(50))
signal.is_outbreak_claim_suppressed = False      # Line 563 (BOOLEAN)
# Automatic client-side onupdate: updated_at     # Line 89  (TIMESTAMPTZ)
```

To prevent SQLSTATE `42501` (`permission denied for column ...`), the column grant must encompass all four fields:
```sql
GRANT UPDATE (
    distinct_farms_count,
    validation_status,
    is_outbreak_claim_suppressed,
    updated_at
) ON regional_signals TO acrevia_staging_app;
```

### 19.2 The Timestamp Mechanism Rebuttal
The previous assurance report erroneously claimed that `updated_at` is generated by PostgreSQL `clock_timestamp()`.
Inspection of [backend/app/database/base.py#L28](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/base.py#L28) proves:
```python
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc),
    nullable=False,
)
```
1. `onupdate=lambda: datetime.now(timezone.utc)` is a **Python client-side callable** invoked by SQLAlchemy in the application memory space prior to compilation.
2. SQLAlchemy compiles the resulting SQL statement with a bound parameter:
   `UPDATE regional_signals SET ..., updated_at = :updated_at WHERE id = :id`
3. There is **zero server-side PostgreSQL trigger or `clock_timestamp()` default** in the database DDL.
4. Calling it `clock_timestamp()` misrepresents the execution boundary: the timestamp is generated by the application container's system clock, making it vulnerable to container clock skew.

---

## 20. WORKER IDENTITY AND MULTI-TENANT AUTHORITY DESIGN

### 20.1 Non-Login Role Technical Semantics
The previous report proposed creating `acrevia_worker` with `NOLOGIN`.
In PostgreSQL:
- A `NOLOGIN` role **cannot authenticate directly via TCP/IP or establish a database session**.
- Any attempt by a worker process to connect using `postgresql://acrevia_worker:...` is immediately rejected with:
  `FATAL: role "acrevia_worker" is not permitted to log in`
- **Architectural Prerequisite:** To operationalize a worker role, PostgreSQL requires:
  1. An authenticating login role (e.g., `acrevia_worker_login WITH LOGIN`).
  2. Membership assignment: `GRANT acrevia_worker TO acrevia_worker_login;`.
  3. The worker session must execute: `SET ROLE acrevia_worker;` upon acquiring a connection from the pool.

### 20.2 The Multi-Tenant Worker Boundary Dilemma
If `acrevia_worker` is granted table-level `SELECT` on `farms`, `observations`, and `risk_alerts` to revalidate regional signals, it acquires **unrestricted global read visibility over all farmer records across Telangana**.
This violates the core tenet of Phase 07 (Tenant Isolation).

### 20.3 Recommended Design: Trusted Stored Verification Function
Rather than granting broad multi-tenant `SELECT` to application or worker roles, ACREVIA should implement an encapsulated PostgreSQL function:

```sql
CREATE OR REPLACE FUNCTION verify_regional_signal_provenance(p_signal_id UUID)
RETURNS TABLE (verified_farms_count INT, passes_threshold BOOLEAN)
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    RETURN QUERY
    WITH signal_window AS (
        SELECT district, observed_start_date, observed_end_date
        FROM regional_signals WHERE id = p_signal_id
    ),
    valid_farms AS (
        SELECT DISTINCT f.id
        FROM regional_signal_evidences rse
        CROSS JOIN signal_window sw
        LEFT JOIN observations o ON rse.evidence_type IN ('OBSERVATION', 'OBSERVATION_REF') 
                                AND rse.evidence_reference_id = o.id::text
        LEFT JOIN risk_alerts ra ON rse.evidence_type IN ('RISK_ALERT', 'RISKCAST_ALERT') 
                                AND rse.evidence_reference_id = ra.id::text
        JOIN farms f ON f.id = COALESCE(o.farm_id, ra.farm_id)
        WHERE rse.signal_id = p_signal_id
          AND f.is_archived = FALSE
          AND LOWER(TRIM(f.district)) = LOWER(TRIM(sw.district))
          AND (
              (o.created_at::date >= sw.observed_start_date AND o.created_at::date <= sw.observed_end_date)
              OR (ra.created_at::date >= sw.observed_start_date AND ra.created_at::date <= sw.observed_end_date)
          )
    )
    SELECT COUNT(*)::INT, (COUNT(*) >= 3)
    FROM valid_farms;
END;
$$ LANGUAGE plpgsql;
```
**Benefits:**
- Runs with elevated privileges (`SECURITY DEFINER`) strictly inside the function boundary.
- Exposes **zero raw farmer PII, coordinates, or farm names** to the calling role.
- Eliminates the need to grant `SELECT` or `UPDATE` on source tables to `acrevia_staging_app` or `acrevia_worker`.
- Atomically executes recalculation without client-side row-lock conflicts.

---

## 21. OUTBOX EVENT AND CLAIM PRIVILEGE MODEL

### 21.1 Concurrent Outbox Consumption
ACREVIA uses `outbox_events` for asynchronous notification dispatch.
Worker processes claim pending events using:
```sql
SELECT id, aggregate_id, event_type, payload
FROM outbox_events
WHERE status = 'PENDING'
ORDER BY created_at ASC
FOR UPDATE SKIP LOCKED
LIMIT 50;
```

### 21.2 Privilege and RLS Prerequisites
1. **Engine Check:** As proven in Section 11, `SELECT ... FOR UPDATE SKIP LOCKED` requires:
   - `SELECT` privilege on `outbox_events`.
   - `UPDATE` privilege on at least one column of `outbox_events`.
2. **Column Privilege Scope:** The worker role must be granted:
   ```sql
   GRANT SELECT ON outbox_events TO acrevia_worker;
   GRANT UPDATE (status, processed_at, retry_count, error_detail) ON outbox_events TO acrevia_worker;
   ```
3. **Locking RLS Evaluation:** Because `SKIP LOCKED` uses `FOR UPDATE`, PostgreSQL evaluates both `FOR SELECT` and `FOR UPDATE` RLS policies. The worker policy must permit `USING (status IN ('PENDING', 'RETRY'))` under both command scopes.

---

## 22. SECRET-SAFE CREDENTIAL-EXPOSURE STATUS

### 22.1 Public Repository Audit of `frontend/lib/server/db.ts`
The previous assurance report claimed:
> *"DB-CREDENTIAL-EXPOSURE-01: Remediated and verified (Git history cleaned; environment variable injection mandated)."*

An independent offline inspection of [frontend/lib/server/db.ts](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/lib/server/db.ts#L8-L10) in public baseline commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d` reveals:

```typescript
// frontend/lib/server/db.ts lines 8-10:
  const dbUrl =
    process.env.DATABASE_URL ||
    "[REDACTED_DATABASE_CONNECTION_STRING_WITH_CREDENTIALS]";
```

### 22.2 Evidentiary Findings
1. **Hard-Coded Fallback Still Present:** While line 9 reads `process.env.DATABASE_URL`, line 10 provides a **hard-coded fallback string containing an active Neon cloud database connection URI with embedded administrative role name and password**!
2. **Public Exposure Confirmed:** This hard-coded URI is present in the public GitHub commit on `main`.
3. **Rotation Unproven:** No verifiable record exists in the repository proving that this exposed database credential has been rotated in the Neon Cloud console.
4. **Conclusion:** Declaring `DB-CREDENTIAL-EXPOSURE-01` "Remediated & Verified" is **factually false**. The blocker is **OPEN and UNREMEDIATED**.

---

## 23. CANONICAL BLOCKER RECONCILIATION

The table below reconciles all 15 canonical security blockers from Phase 07, restoring their evidence-bound statuses:

| Blocker Identifier | Previous Report Status | Corrected Audit Status | Evidentiary Basis for Correction | Owner Approval Gating |
| :--- | :--- | :--- | :--- | :---: |
| **`RLS-WRITE-AUTH-01`** | Mitigated by Design | **OPEN** | Write route RLS policies are proposed designs; not merged in source. | Owner Gate Required |
| **`RLS-ROLE-ASSIGNMENT-01`** | Mitigated by Design | **OPEN** | Transaction-local GUCs remain mutable by any client SQL execution. | Owner Gate Required |
| **`DB-AUTH-01`** | Blocked pending Owner Gate | **BLOCKED** | Roles `acrevia_staging_app` and `acrevia_worker` unprovisioned in staging. | Owner GATE-02 |
| **`DB-CREDENTIAL-EXPOSURE-01`** | Remediated & Verified | **CRITICAL OPEN** | Hard-coded URI fallback remains in `frontend/lib/server/db.ts#L10`. | Owner Secret Rotation |
| **`APP-ROLE-SELF-SELECT-01`** | Mitigated by Design | **OPEN** | Relies on unverified session context immutability. | Owner Gate Required |
| **`EXP-AUTH-01`** | Mitigated by Design | **OPEN** | `app.current_user_districts` is completely absent from codebase. | Owner Gate Required |
| **`CASCADE-ROLE-DEL-01`** | Mitigated by Design | **OPEN** | Migration-based role management designed but not applied in staging. | Owner Gate Required |
| **`TENANT-MEMBERSHIP-01`** | Enforced by Policy | **CRITICAL BLOCKER** | Recovery queries return 0 source rows under tenant RLS; recovery broken. | Remediation Required |
| **`OWNER-AUTH-01`** | Pending Owner Signature | **BLOCKED** | Execution gated on Owner completion of GATE-02 through GATE-05. | Owner Sign-Off |
| **`DB-RLS-01`** | Designed | **BLOCKED** | Migration `a1089411c87d` unapplied to staging database. | Owner GATE-03 |
| **`WRK-DISP-01`** | Designed | **OPEN** | Proposed `acrevia_worker` does not exist as an operational daemon. | Design & Implementation |
| **`RES-PULSE-01`** | Designed | **OPEN** | Distinct farms calculation fails closed under RLS (measures count=0). | Remediation Required |
| **`RES-PULSE-02`** | Mitigated by Design | **OPEN** | Pruning source locks leaves unmitigated race conditions on farm districts. | Remediation Required |
| **`GATE01-PROV-01`** | Identified Discrepancy | **OPEN** | Branch naming mismatch (`staging-rls-phase07` vs `staging-rls-phase05`). | Owner Clarification |
| **`RES-PULSE-READ-01`** | Designed & Proven | **OPEN** | Farmer read boundary unverified under live FORCE RLS kernel execution. | Owner GATE-04 |

---

## 24. RESIDUAL-RISK RECONCILIATION

The 5 canonical residual risks remain active and classified as follows:

| Residual Risk ID | Risk Domain | Severity | Operational Precondition & Risk Profile | Mitigation Status |
| :--- | :--- | :---: | :--- | :--- |
| **`RES-PULSE-01`** | Geographic Privacy | **MEDIUM** | In sparse rural mandals, outbreak publication could allow inference of single-farm telemetry if threshold check fails. | Open (Recalculation currently broken under RLS). |
| **`RES-PULSE-02`** | Concurrency Collision | **MEDIUM** | Race conditions between concurrent farm updates and signal recovery recalculation. | Open (Source lock pruning removes concurrency protection). |
| **`RES-PRIMARY-ROUTING-01`**| Database Replication | **MEDIUM** | Read replicas serving stale data during recovery transactions. | Open (Requires strict primary writer node routing). |
| **`RES-REPLICA-LAG-01`** | Telemetry Delay | **LOW** | Replica lag causing temporary visual discrepancy on public dashboard. | Monitored by timestamp validation. |
| **`RES-FREE-TEXT-01`** | PII Infiltration | **LOW** | Unstructured observation notes containing farmer phone numbers. | Schema excludes raw text notes from regional aggregation. |

### 24.1 Status of Additional Governance Items
- **`DB-GRANT-APPLY-01`:** Retains status **`PROPOSED — OWNER APPROVAL REQUIRED`**.
- **`FARMER_READ_BLOCKED_BY_EVIDENCE_ASSOCIATION_RLS`:** Retains status as a descriptive finding, not a canonical blocker identifier.


---

## 25. GOVERNANCE GATE RECONCILIATION

### 25.1 The Authoritative Register Record
Inspection of [docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md) establishes the exact recorded status of all five execution gates:

| Gate Identifier | Authoritative Scope Defined in Register | Recorded State in Register | Mode Impact & Authorization Boundary |
| :--- | :--- | :---: | :--- |
| **GATE-01** | Provisioning of isolated Neon staging branch `staging-rls-phase07` from parent `production` in `aws-ap-southeast-1`. | **`[x] APPROVED BY OWNER (2026-11-10)`** | Staging branch creation approved. Do not request re-approval. |
| **GATE-02** | Creation of unprivileged runtime database role `acrevia_staging_app` (`NOSUPERUSER`, `NOBYPASSRLS`, `NOCREATEDB`, `NOCREATEROLE`). | **`[ ] UNCHECKED (AWAITING SIGN-OFF)`** | Staging role creation locked pending sign-off. Scope excludes secrets. |
| **GATE-03** | Physical execution of Alembic RLS migration `a1089411c87d` applying 751 atomic DDL statements to `neondb_staging`. | **`[ ] UNCHECKED (AWAITING SIGN-OFF)`** | Staging DDL application locked pending sign-off. |
| **GATE-04** | Execution of automated staging RLS verification harness (`scripts/verify_staging_rls.py`) against live staging endpoint. | **`[ ] UNCHECKED (AWAITING SIGN-OFF)`** | Live testing locked pending sign-off. |
| **GATE-05** | Teardown and deprovisioning schedule of `staging-rls-phase05` post-verification. | **`[ ] UNCHECKED (AWAITING SIGN-OFF)`** | Cloud resource destruction locked pending sign-off. |

### 25.2 Crucial Governance Enforcements
1. **GATE-01 Status:** Recorded as formally approved on 2026-11-10. It must not be presented as pending.
2. **GATE-02 Scope Discipline:** The register explicitly limits GATE-02 to creating role `acrevia_staging_app`. It does **not include secret provisioning or credential rotation**.
3. **Branch-Identity Discrepancy (`GATE01-PROV-01`):** GATE-01 specifies branch `staging-rls-phase07`, while Document Overview and GATE-05 specify `staging-rls-phase05`. Owner reconciliation is required.
4. **MODE B Unauthorized:** MODE B remote execution remains strictly unauthorized until GATE-02 through GATE-05 are signed off.

---

## 26. FUTURE POSTGRESQL VERIFICATION PLAN

*Note: In strict compliance with MODE A boundaries, the following 15 verification procedures are design specifications for future execution only after Owner approval of GATE-02, GATE-03, and GATE-04.*

### 26.1 Tenant Context and Source Provenance Verification
1. **TEST-P07-CTX-01 (Expert Request with Empty Tenant Context):**
   - *Setup:* Connect as `acrevia_staging_app`. Issue `SET LOCAL app.current_user_id = '<expert_uuid>'; SET LOCAL app.current_tenant_id = ''; SET LOCAL app.is_admin = 'false';`.
   - *Execution:* Query `SELECT COUNT(*) FROM observations WHERE id IN (...);`.
   - *Expected Result:* Returns `0` under `FORCE RLS`, proving the provenance visibility defect.
2. **TEST-P07-CTX-02 (Application ADMIN with Normal Role):**
   - *Setup:* Connect as `acrevia_staging_app`. Issue `SET LOCAL app.is_admin = 'true'; SET LOCAL app.current_tenant_id = '';`.
   - *Execution:* Query `SELECT COUNT(*) FROM observations WHERE id IN (...);`.
   - *Expected Result:* Returns `0`, proving `ADMIN_BYPASS_SQL` dual-identity check fails closed against runtime roles.
3. **TEST-P07-CTX-03 (Dedicated Database Admin Bypass):**
   - *Setup:* Connect as `acrevia_admin`. Issue `SET LOCAL app.is_admin = 'true';`.
   - *Execution:* Query `SELECT COUNT(*) FROM observations WHERE id IN (...);`.
   - *Expected Result:* Returns full observation count, proving bypass works only for dedicated DB administrative roles.
4. **TEST-P07-CTX-04 (Stored Verification Function Provenance Read):**
   - *Setup:* Connect as `acrevia_staging_app`.
   - *Execution:* `SELECT * FROM verify_regional_signal_provenance(:signal_id);`.
   - *Expected Result:* Returns `(verified_farms_count, passes_threshold)` correctly without exposing raw table rows.

### 26.2 Row-Level Locking and RLS Policy Semantics
5. **TEST-P07-LCK-01 (Locking SELECT with SELECT-Only Privilege):**
   - *Setup:* Grant `SELECT` on `farms` to `acrevia_staging_app`; revoke all `UPDATE`.
   - *Execution:* `SELECT * FROM farms WHERE id = :id FOR SHARE;`.
   - *Expected Result:* Aborts with SQLSTATE `42501` (`insufficient_privilege`), verifying engine requirement from `analyze.c`.
6. **TEST-P07-LCK-02 (Locking SELECT with Column-Level UPDATE Privilege):**
   - *Setup:* Grant `UPDATE (updated_at)` on `farms` to `acrevia_staging_app`.
   - *Execution:* `SELECT * FROM farms WHERE id = :id FOR SHARE;`.
   - *Expected Result:* Succeeds, confirming column-level UPDATE satisfies row-lock engine check.
7. **TEST-P07-LCK-03 (Locking SELECT with SELECT Policy but No UPDATE Policy):**
   - *Setup:* Define `FOR SELECT` policy on `regional_signals`; omit `FOR UPDATE` policy.
   - *Execution:* `SELECT * FROM regional_signals WHERE id = :id FOR UPDATE;`.
   - *Expected Result:* Returns `0` rows (default deny under RLS for locking command), proving both policies are evaluated.
8. **TEST-P07-LCK-04 (Outbox `FOR UPDATE SKIP LOCKED`):**
   - *Setup:* Connect as `acrevia_worker`.
   - *Execution:* `SELECT * FROM outbox_events WHERE status = 'PENDING' FOR UPDATE SKIP LOCKED LIMIT 10;`.
   - *Expected Result:* Successfully locks unclaimed rows without blocking on concurrent worker leases.

### 26.3 Source Mutation Concurrency Protection
9. **TEST-P07-CNC-01 (Recovery Concurrent with Farm District Update):**
   - *Setup:* Tx1 starts `recover_suppressed_signal()`. Tx2 concurrently executes `FarmService.update_farm(farm_id, district='Khammam')`.
   - *Evaluation:* If source lock is absent, Tx1 validates farm against old district while Tx2 commits new district.
10. **TEST-P07-CNC-02 (Recovery Concurrent with Observation Deletion):**
    - *Setup:* Tx1 starts recovery. Tx2 executes `DELETE FROM observations WHERE id = :id;`.
    - *Evaluation:* Verifies whether polymorphic string reference (`evidence_reference_id`) permits deletion during recalculation.
11. **TEST-P07-CNC-03 (Parent Deletion Evidence Cascade Retention):**
    - *Setup:* Attempt `DELETE FROM regional_signals WHERE id = :id;` on a signal with linked evidence.
    - *Expected Result:* Aborts with SQLSTATE `23001` (`ON DELETE RESTRICT`), verifying forensic evidence is retained.

---

## 27. ADVERSARIAL REVIEW AND CORRECTED CONCLUSIONS

This review systematically addresses and corrects all 25 critical adversarial assertions:

1. **Assertion 1: The current recovery path already establishes tenant scope for every source farm.**  
   *Correction:* **FALSE.** `get_current_user()` sets `app.current_tenant_id = ''`. The recovery route never calls `verify_farm_access()`.
2. **Assertion 2: `app.current_user_districts` exists in the current repository.**  
   *Correction:* **FALSE.** Exact repository count is **0 occurrences**. It is an unmerged design proposal.
3. **Assertion 3: Application ADMIN automatically satisfies the custom database bypass predicate.**  
   *Correction:* **FALSE.** `ADMIN_BYPASS_SQL` checks `SESSION_USER IN ('neondb_owner', 'acrevia_admin')`. Runtime role `acrevia_staging_app` strictly fails this check.
4. **Assertion 4: A transaction-local GUC is impossible for a database client to change.**  
   *Correction:* **FALSE.** Any client capable of executing arbitrary SQL on the session can issue `SELECT set_config('app.is_admin', 'true', true);`.
5. **Assertion 5: Parent `FOR UPDATE` locks all evidence and source records.**  
   *Correction:* **FALSE.** Parent lock applies solely to the tuple in `regional_signals`. It does not lock rows in other tables.
6. **Assertion 6: A parent lock serializes `FarmService` district updates.**  
   *Correction:* **FALSE.** `FarmService.update_farm()` writes directly to `farms` without reading or locking `regional_signals`.
7. **Assertion 7: A parent lock protects source rows referenced through string IDs.**  
   *Correction:* **FALSE.** Polymorphic string references carry zero database-level foreign key locks or engine protections.
8. **Assertion 8: The evidence-reference ID is a foreign key to Observation or RiskAlert.**  
   *Correction:* **FALSE.** `evidence_reference_id` is a bare `String(100)` column in `backend/app/models/regional_pulse.py#L65`.
9. **Assertion 9: Evidence records are currently immutable under the privilege crosswalk.**  
   *Correction:* **FALSE.** `PRIVILEGE_CROSSWALK` explicitly grants `UPDATE = True` to `COMMUNITY_COLLABORATIVE` tables.
10. **Assertion 10: Removing source-row locks cannot change the verified count.**  
    *Correction:* **FALSE.** Pruning source locks allows concurrent updates to `Farm.district` or `is_archived` during recalculation, altering the count.
11. **Assertion 11: UPDATE RLS policies do not apply to `SELECT FOR UPDATE/SHARE`.**  
    *Correction:* **FALSE.** In PostgreSQL 16 engine rules, the `USING` clause of the `FOR UPDATE` policy is evaluated during locking SELECT queries.
12. **Assertion 12: A recovery SELECT policy alone authorizes row locking.**  
    *Correction:* **FALSE.** If the `FOR UPDATE` policy rejects the row under its `USING` clause, `SELECT ... FOR UPDATE` returns 0 rows.
13. **Assertion 13: `FOR UPDATE` is the PostgreSQL table lock `ExclusiveLock`.**  
    *Correction:* **FALSE.** `FOR UPDATE` is an exclusive **row-level** lock. The table lock acquired is **`ROW SHARE`**.
14. **Assertion 14: `FOR SHARE` is the PostgreSQL table lock `ShareLock`.**  
    *Correction:* **FALSE.** `FOR SHARE` is a shared **row-level** lock. The table lock acquired is **`ROW SHARE`**.
15. **Assertion 15: `updated_at` is generated by `clock_timestamp()`.**  
    *Correction:* **FALSE.** Generated client-side by Python lambda `datetime.now(timezone.utc)` in SQLAlchemy `TimestampMixin`.
16. **Assertion 16: The parent UPDATE grant covers every recovery field.**  
    *Correction:* **FALSE in prior proposals.** Prior proposals omitted `is_outbreak_claim_suppressed`, causing SQLSTATE `42501` crashes.
17. **Assertion 17: A worker with SELECT-only access can run the existing `FOR SHARE` queries.**  
    *Correction:* **FALSE.** PostgreSQL engine requires `UPDATE` privilege on at least one column to execute `FOR SHARE`.
18. **Assertion 18: A NOLOGIN role can directly establish a database connection.**  
    *Correction:* **FALSE.** PostgreSQL rejects connection attempts to `NOLOGIN` roles with a fatal authentication error.
19. **Assertion 19: A designed worker has mitigated `WRK-DISP-01`.**  
    *Correction:* **FALSE.** A design on paper is not an operational worker. `WRK-DISP-01` remains **OPEN**.
20. **Assertion 20: A hard-coded database URI fallback is compatible with declaring credential exposure remediated.**  
    *Correction:* **FALSE.** A hard-coded credential string in public source (`frontend/lib/server/db.ts#L10`) leaves `DB-CREDENTIAL-EXPOSURE-01` **OPEN**.
21. **Assertion 21: Deterministic GUC injection resolves mutable-GUC role escalation.**  
    *Correction:* **FALSE.** GUCs can be overwritten by subsequent SQL in the same session unless connection isolation or dual-identity checks protect them.
22. **Assertion 22: The 15 blockers are mitigated because a design proposal exists.**  
    *Correction:* **FALSE.** Canonical blockers remain open until implementations are committed, migrated, and verified.
23. **Assertion 23: GATE-02 includes secret provisioning without register evidence.**  
    *Correction:* **FALSE.** The authoritative register limits GATE-02 strictly to role creation (`acrevia_staging_app`).
24. **Assertion 24: GATE-01 remains pending.**  
    *Correction:* **FALSE.** GATE-01 was signed and approved by the Project Owner on 2026-11-10.
25. **Assertion 25: GATE-01 approval authorizes the complete MODE B sequence.**  
    *Correction:* **FALSE.** GATE-01 authorizes only branch provisioning. GATE-02 through GATE-05 require separate, explicit sign-offs.

---

## 28. DESIGN ALTERNATIVES AND REMAINING DECISIONS

### 28.1 Provenance Verification Architecture Alternatives
To resolve the provenance invisibility defect (Section 8) while preserving tenant isolation, four alternatives are evaluated:

| Architectural Alternative | Source Rows Accessible | Tenant Isolation Preserved? | Concurrency Safety Guarantee | Required SQL Privileges | Recommended? |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **Alt 1: Global Multi-Tenant SELECT** | All farms across all tenants | **NO** (Violates tenant isolation) | High contention, deadlock risk | Table-wide `SELECT, UPDATE` | **REJECTED** |
| **Alt 2: Iterative Per-Farm Context** | One farm at a time in loop | **YES** | Complex, multiple round-trips | Standard tenant role | **NOT RECOMMENDED** |
| **Alt 3: Trusted Verification Function** | Encapsulated inside stored function | **YES** (Zero raw PII exposed) | Engine-level subquery, repeatable read | `EXECUTE` on function only | **STRONGLY RECOMMENDED** |
| **Alt 4: Materialized Provenance Projection**| Precomputed distinct count table | **YES** | Read from aggregate view | `SELECT` on projection | **ACCEPTABLE** |

### 28.2 Decisions Required from Project Owner
1. **Decision D-01 (Farmer Read Boundary):** Formally approve the command-scoped public read policy on `regional_signals` isolating suppressed signals.
2. **Decision D-02 (Provenance Verification Pattern):** Authorize the implementation of the PostgreSQL `SECURITY DEFINER` function `verify_regional_signal_provenance()` (Alternative 3).
3. **Decision D-03 (Credential Remediation):** Mandate the removal of the hard-coded URI fallback in `frontend/lib/server/db.ts#L10` and trigger cloud credential rotation in Neon Console.
4. **Decision DB-AUTH-01:** Formally sign off on GATE-02 to provision `acrevia_staging_app`.

---

## 29. IMPLEMENTATION-READINESS CLASSIFICATION

Based on the discovery of the source provenance RLS invisibility defect, unmitigated source lock pruning, and active credential fallback in public source, the implementation readiness ratings are formally certified as:

| Assurance Evaluation Dimension | Formal Readiness Certification Status | Technical Operational Meaning |
| :--- | :--- | :--- |
| **Overall Design Readiness** | **`NOT_READY_FOR_OWNER_REVIEW`** | Recovery architecture contains fatal RLS visibility defects and unaddressed concurrency races. Design must be revised. |
| **Implementation Authorization** | **`NOT_IMPLEMENTATION_AUTHORIZED`** | Strictly zero source code, database, migration, or credential changes permitted. |
| **Staging Migration Application** | **`NOT_AUTHORIZED`** | Migration `a1089411c87d` must not be executed. |
| **Source Code Modification** | **`NOT_AUTHORIZED`** | Application codebase must remain untouched. |
| **Production Deployment** | **`NOT_AUTHORIZED`** | Production environments remain strictly locked. |

---

## 30. EXPLICIT MODE A LIMITATIONS

In strict adherence to the governing security audit charter:
1. **Mode A Execution Only:** Zero remote database connections were established (Neon Cloud staging and production remained completely untouched).
2. **Zero Code Modifications:** No application source files, models, schemas, migrations, or tests were altered.
3. **Zero Git Modifications:** No Git commits, branches, rebases, checkouts, or history manipulations were performed.
4. **Zero Credential Exposure:** No database passwords, JWT secrets, or cloud API tokens were printed or logged.
5. **Preservation of Artifacts:** All 7 tracked governance files and all 15 historical assurance reports were preserved non-destructively.
