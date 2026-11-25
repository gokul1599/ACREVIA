# ACREVIA — PHASE 07: TENANT-CONTEXT PROVENANCE ACCESS, SECURITY-DEFINER VERIFIER SAFETY, ROW-LOCK POLICY COMPATIBILITY & CREDENTIAL EXPOSURE CORRECTIVE ASSURANCE

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India (33 Administrative Districts)  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** `MODE A ONLY` — Pinned Source Inspection, PostgreSQL Security Analysis, Multi-Tenant Authorization Modeling, Concurrency Analysis & Governance Documentation  
**Audit Standard:** Everything Claude Code (ECC) — `PLAN → INSPECT → TRACE → ADVERSARIAL REVIEW → VERIFY OFFLINE → DOCUMENT`  
**Public Repository:** `https://github.com/gokul1599/ACREVIA`  
**Verified Repository Baseline:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Target Deliverable:** `docs/pilot/security/PHASE_07_TENANT_CONTEXT_VERIFIER_FUNCTION_AND_CREDENTIAL_EXPOSURE_CORRECTIVE_ASSURANCE_REPORT.md`  
**Artifact Mirror:** `C:\Users\gokul\.gemini\antigravity\brain\8d770357-1b73-48ca-9930-eded206539c2\PHASE_07_TENANT_CONTEXT_VERIFIER_FUNCTION_AND_CREDENTIAL_EXPOSURE_CORRECTIVE_ASSURANCE_REPORT.md`  
**Authoritative Governance Register:** `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`  
**Overall Design Readiness:** `NOT_READY_FOR_OWNER_REVIEW`  
**Implementation Authorization:** `NOT_IMPLEMENTATION_AUTHORIZED`  
**Governing Phase Status:** `NOT RELEASED`  

---

## 1. EXECUTIVE ASSURANCE CONCLUSION

This corrective security assurance audit delivers an authoritative, evidence-bound architectural evaluation of ACREVIA's Phase 07 Regional Pulse trusted provenance verification, PostgreSQL Row-Level Security (RLS) tenant isolation, database role delegation, concurrency locking, and secret containment architecture.

Operating strictly under **`MODE A ONLY`** constraints (zero live cloud database queries, zero credential testing, zero source-code mutations, zero migration executions, and zero Git modifications), this evaluation resolves the central architectural challenge of Phase 07:

> **How can ACREVIA safely verify a district-level agricultural signal using source records owned by multiple tenants, while preserving raw-data isolation, preventing forged administrative access, maintaining recovery correctness, and avoiding broad database bypass privileges?**

### 1.1 Core Audit Breakthroughs & Design Truths
1. **The Inherent Multi-Tenant Aggregation Dilemma:**
   - Regional Pulse signals aggregate outbreak telemetry across multiple independently owned farms within a Telangana administrative district to enforce the k-anonymity privacy invariant ($k \ge 3$ distinct farms).
   - Under Phase 07 tenant isolation, underlying source tables (`farms`, `observations`, `risk_alerts`) are classified as `TENANT_DIRECT`. Their generated `RESTRICTIVE` RLS policies require:
     $$\texttt{ADMIN\_BYPASS\_SQL} \quad \lor \quad \texttt{tenant\_column::text = current\_setting('app.current\_tenant\_id', true)}$$
   - When an Agricultural Expert or Application Administrator requests signal recovery via `POST /api/v1/regional-pulse/signals/{id}/recover`, the request is initialized with `tenant_id=None`. The route never calls `verify_farm_access()`.
   - Consequently, `app.current_tenant_id` is empty string (`""`). Because `acrevia_staging_app` cannot satisfy `ADMIN_BYPASS_SQL`, **PostgreSQL silently filters all observations, risk alerts, and farms to ZERO rows**. Provenance recalculation measures `current_count = 0 < 3` and deterministically aborts with `HTTP 400 Bad Request`.
2. **The SECURITY DEFINER Verifier Safety Boundary:**
   - A previously proposed `SECURITY DEFINER` function was syntactically invalid (`RETURNS (INT, BOOLEAN)`) and lacked a comprehensive execution threat model.
   - Declaring a function `SECURITY DEFINER` **does NOT automatically bypass RLS** on tables configured with `FORCE ROW LEVEL SECURITY` unless the function owner is a `SUPERUSER`, possesses `BYPASSRLS`, or owns the target tables.
   - To safely verify multi-tenant provenance without granting the runtime application role table-wide `SELECT` on all tenant records, ACREVIA must implement an encapsulated PostgreSQL function (`verify_regional_signal_provenance`) returning strictly aggregate counts (`RETURNS TABLE (verified_distinct_farms_count integer, is_valid boolean)`), owned by a dedicated capability role, with hardened `search_path = public, pg_temp` (`pg_temp` last), and execution restricted from `PUBLIC`.
3. **Existing Source-Level `FOR ALL` Policies Participate in Row-Locking:**
   - In PostgreSQL 16 engine rules (`src/backend/rewrite/rowsecurity.c`), locking queries (`SELECT ... FOR UPDATE` and `SELECT ... FOR SHARE`) evaluate the `USING` clauses of both `FOR SELECT` and `FOR UPDATE` (or `FOR ALL`) policies.
   - The current generated policies on `regional_signals` and `regional_signal_evidences` apply `FOR ALL`, as do the base and restrictive policies on tenant-direct tables. Therefore, the recovery failure is **not** an absence of an applicable UPDATE policy; rather, it is the empty tenant GUC that triggers the restrictive isolation filter.
4. **Parent-Lock Redundancy Claim Formally Refuted:**
   - A row lock on parent `RegionalSignal` serializes **only concurrent operations that explicitly lock that identical signal**.
   - Independent source mutations—specifically `FarmService.update_farm()` (modifying farm district or archival status), observation deletions, and risk-alert resolutions—commit independently without acquiring parent signal locks. Pruning source locks without an outbox watermark or atomic snapshot verification creates severe concurrency race conditions.
5. **Active Credential Exposure Confirmed Open:**
   - Public baseline commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d` in [frontend/lib/server/db.ts#L8-L10](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/lib/server/db.ts#L8-L10) contains a hard-coded database URI fallback containing an administrative role and embedded password.
   - Declaring `DB-CREDENTIAL-EXPOSURE-01` remediated was false. The blocker is **CRITICAL OPEN**.

---

## 2. AUTHORITATIVE BASELINE AND REPOSITORY STATE

### 2.1 Public GitHub Baseline
- **Repository URL:** `https://github.com/gokul1599/ACREVIA`
- **Active Branch:** `main`
- **Pinned Commit Hash:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d`
- **Baseline Verification:** Confirmed unchanged from prior audit. All public-source citations are strictly pinned to this exact commit SHA.

### 2.2 Local Workspace Working Tree Status
- **Workspace Path:** `c:\Users\gokul\OneDrive\Documents\projects`
- **Local Branch:** `main`
- **Local HEAD Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d`
- **Commit Divergence:** Exactly **0 commits divergence** (`HEAD` is synchronized with `origin/main`).
- **Application Codebase Integrity:** Exactly **0 application source files, models, schemas, services, migrations, or tests modified**.
- **Tracked Historical Governance Files:** 7 historical governance matrices in `docs/pilot/security/` remain in their original tracked modified state.
- **Untracked Historical Reports:** 16 sequentially preserved security assurance reports.

### 2.3 Required Source File Inspection
The technical models and assertions in this report are grounded in direct inspection of:
- [backend/app/database/rls.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py) (RLS architecture, `ADMIN_BYPASS_SQL`, DDL generator, `PRIVILEGE_CROSSWALK`)
- [backend/app/database/session.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/session.py) (`SessionLocal`, connection parameters)
- [backend/app/database/base.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/base.py) (`TimestampMixin`, `updated_at` onupdate lambda)
- [backend/app/security/dependencies.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/security/dependencies.py) (`get_current_user()`, `require_roles()`, `verify_farm_access()`)
- [backend/app/services/regional_pulse_service.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py) (`recover_suppressed_signal()`, `revalidate_signal_provenance()`)
- [backend/app/services/farm_service.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/farm_service.py) (`update_farm()`, independent commit lifecycle)
- [backend/app/models/expert_profile.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/expert_profile.py) (`districts_covered_json` column)
- [frontend/lib/server/db.ts](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/lib/server/db.ts) (Hard-coded administrative fallback connection string)
- [docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md) (GATE-01 through GATE-05)

---

## 3. PREVIOUS REPORT RECONCILIATION

The preceding report ([PHASE_07_REGIONAL_PULSE_TRUSTED_SOURCE_ACCESS_AND_LOCK_PROTOCOL_CORRECTIVE_ASSURANCE_REPORT.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_REGIONAL_PULSE_TRUSTED_SOURCE_ACCESS_AND_LOCK_PROTOCOL_CORRECTIVE_ASSURANCE_REPORT.md)) correctly proved the empty tenant-context collapse and exposed the hard-coded credential fallback. However, deeper scrutiny reveals several remaining technical and design gaps that this audit addresses:

| Item | Previous Report Finding | Corrective Finding in This Audit | Architectural Significance |
| :---: | :--- | :--- | :--- |
| **REC-01** | Noted that `SELECT FOR UPDATE` evaluates `UPDATE` policies, implying missing UPDATE policies cause row rejection. | Reconstructed the actual generated DDL: `regional_signals` and `farms` receive `FOR ALL` policies, which *do* act as applicable UPDATE policies! | The true access blocker is that `app.current_tenant_id` is empty, causing restrictive policies to reject rows, NOT an absence of an UPDATE policy. |
| **REC-02** | Proposed `verify_regional_signal_provenance(p_signal_id UUID) RETURNS (INT, BOOLEAN)`. | PostgreSQL rejects `RETURNS (INT, BOOLEAN)` with syntax error. Must declare `RETURNS TABLE (...)` or composite type. | Proves that the proposed stored function was an unvalidated concept requiring formal DDL engineering. |
| **REC-03** | Assumed `SECURITY DEFINER` automatically enables provenance reads under FORCE RLS. | Under PostgreSQL specifications, `FORCE RLS` enforces table policies even against the table owner unless the owner is superuser or has `BYPASSRLS`. | Proves that function ownership, role attributes, and table RLS policies must be explicitly co-designed. |
| **REC-04** | Argued for removing source locks and relying on the parent lock. | Proved that `FarmService.update_farm()` commits district mutations without locking the parent signal. | Concurrency protection requires either retaining shared source locks, version checks, or atomic snapshot isolation. |
| **REC-05** | Closed several canonical blockers as "Mitigated by Design". | A proposed design does not constitute an implemented control. Canonical blockers cannot be closed prior to merge and verification. | Restores strict governance classification: canonical blockers remain OPEN or BLOCKED. |

---

## 4. TENANT-CONTEXT LIFECYCLE AND REQUEST INITIALIZATION

### 4.1 Exhaustive Trace of `get_current_user()`
In [dependencies.py#L26-L76](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/security/dependencies.py#L26-L76), every authenticated API request undergoes the following exact sequential lifecycle:

1. **JWT Header Extraction & Cryptographic Validation:**
   - Extracts bearer token; decodes payload via `decode_access_token(token)`.
   - Validates signature and extracts subject claim: `user_id = payload.get("sub")`.
2. **Initial Transaction-Local Context Assignment:**
   - Line 56 executes:
     ```python
     set_tenant_context(db, tenant_id=None, user_id=user_id, is_admin=False)
     ```
   - In [rls.py#L276-L291](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L276-L291), `set_tenant_context()` converts `tenant_id=None` into empty string (`""`):
     ```sql
     SELECT set_config('app.current_tenant_id', '', true);
     SELECT set_config('app.current_user_id', '<user_uuid>', true);
     SELECT set_config('app.is_admin', 'false', true);
     ```
   - The third parameter `is_local=true` scopes these settings strictly to the active transaction.
3. **User Record Retrieval Under RLS:**
   - Line 59 executes `user = db.get(User, user_id)`.
   - `users` is classified as `USER_OWNED` (`column: id`). The RESTRICTIVE policy checks:
     `id::text = current_setting('app.current_user_id', true)`
   - Because `app.current_user_id` matches `user_id`, this query succeeds.
4. **Role Evaluation & Admin Context Escalation:**
   - Line 70–74 extracts `user_roles = [r.id for r in user.roles]`.
   - If `SystemRole.ADMIN.value in user_roles`, line 74 executes:
     ```python
     set_tenant_context(db, tenant_id=None, user_id=user.id, is_admin=True)
     ```
     This sets `app.is_admin = 'true'`, but **explicitly leaves `app.current_tenant_id = ''`**!
   - If user has `AGRICULTURAL_EXPERT`, line 74 is **bypassed**. `app.is_admin` remains `'false'`.

### 4.2 Complete Request-Context GUC Matrix
The table below maps the runtime context values across all human and system actors:

| Actor Description | `SESSION_USER` | `CURRENT_USER` | `app.current_user_id` | `app.current_tenant_id` | `app.is_admin` | `app.current_user_districts` | Evidence Classification |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **Farmer** | `acrevia_staging_app`* | `acrevia_staging_app`* | `<farmer_uuid>` | `<farm_uuid>` | `false` | `[NULL]` | `LOCAL_SOURCE_VERIFIED` |
| **Agricultural Expert** | `acrevia_staging_app`* | `acrevia_staging_app`* | `<expert_uuid>` | `""` (Empty) | `false` | `[NULL]` | `LOCAL_SOURCE_VERIFIED` |
| **Application ADMIN** | `acrevia_staging_app`* | `acrevia_staging_app`* | `<admin_uuid>` | `""` (Empty) | `true` | `[NULL]` | `LOCAL_SOURCE_VERIFIED` |
| **Proposed Worker Login** | `acrevia_worker_login` | `acrevia_worker_login` | `'system:worker'` | `""` (Empty) | `false` | `[NULL]` | `PROPOSED_DESIGN` |
| **Proposed Worker Capability** | `acrevia_worker_login` | `acrevia_worker` | `'system:worker'` | `""` (Empty) | `false` | `[NULL]` | `PROPOSED_DESIGN` (Post `SET ROLE`) |
| **Direct Database Admin** | `acrevia_admin` | `acrevia_admin` | Any or None | Any or None | `true` | `[NULL]` | `PUBLIC_SOURCE_VERIFIED` |
| **Unauthenticated Session** | `acrevia_staging_app`* | `acrevia_staging_app`* | `""` (Empty) | `""` (Empty) | `false` | `[NULL]` | `LOCAL_SOURCE_VERIFIED` |

*\*Note: `acrevia_staging_app` is the target runtime identity specified in GATE-02; GATE-02 remains unapproved in the authoritative register.*

### 4.3 Context Mutability and Insecurity
Transaction-local GUCs (`is_local=true`) guarantee that PostgreSQL clears the parameters when the transaction commits or aborts, preventing connection-pool contamination.
However, **transaction-local GUCs provide zero protection against arbitrary SQL execution**:
- Any code or SQL injection executing under the database session can issue:
  `SELECT set_config('app.current_tenant_id', '<target_farm_uuid>', true);`
- Therefore, client-side GUC injection cannot be treated as an unforgeable cryptographic security boundary. It must be paired with database allowlists or stored verification logic.

---

## 5. RECOVERY ROUTE GUC TRACE AND DISCONNECT

### 5.1 Route Invocation Sequence
Tracing `POST /api/v1/regional-pulse/signals/{signal_id}/recover` in [regional_pulse.py#L152-L185](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/regional_pulse.py#L152-L185):

$$egin{aligned}
	extbf{1. Gateway Ingress} &\longrightarrow 	exttt{recover\_signal(signal\_id, payload, current\_user, db)} \
	extbf{2. Auth Dependency} &\longrightarrow 	exttt{require\_roles('ADMIN', 'AGRICULTURAL\_EXPERT')} \
	extbf{3. Base Auth} &\longrightarrow 	exttt{get\_current\_user()} \implies 	exttt{set\_tenant\_context(db, tenant\_id=None, user\_id, is\_admin)} \
	extbf{4. Service Dispatch} &\longrightarrow 	exttt{RegionalPulseService.recover\_suppressed\_signal(db, signal\_id, ...)} \
	extbf{5. Parent Lock} &\longrightarrow 	exttt{select(RegionalSignal)...where(id == signal\_id).with\_for\_update()} \
	extbf{6. Evidence Fetch} &\longrightarrow 	exttt{select(RegionalSignalEvidence)...where(signal\_id == id).with\_for\_update(read=True)} \
	extbf{7. Source Fetch 1} &\longrightarrow 	exttt{select(Observation)...where(id.in\_(obs\_ids)).with\_for\_update(read=True)} \
	extbf{8. Source Fetch 2} &\longrightarrow 	exttt{select(RiskAlert)...where(id.in\_(alert\_ids)).with\_for\_update(read=True)} \
	extbf{9. Source Fetch 3} &\longrightarrow 	exttt{select(Farm)...where(id.in\_(farm\_ids)).with\_for\_update(read=True)}
\end{aligned}$$

### 5.2 Critical Omissions in Route Implementation
- The route **never calls `verify_farm_access()`**.
- The route **never establishes any tenant context** for the referenced farms.
- The route **does not iterate through authorized farm tenants**.
- The route **does not invoke any trusted database function**.
- The route passes the session directly to the service with `app.current_tenant_id = ''`.

---

## 6. TENANT-DIRECT RLS POLICY EVALUATION

In [backend/app/database/rls.py#L325-L362](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L325-L362), `TABLE_CLASSIFICATION` categorizes `farms`, `observations`, and `risk_alerts` as `TENANT_DIRECT`:
- `farms`: `column: "id"`
- `observations`: `column: "farm_id"`
- `risk_alerts`: `column: "farm_id"`

### 6.1 Restrictive Policy Architecture
For every `TENANT_DIRECT` table, `generate_rls_ddl()` generates:
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

### 6.2 Mathematical Evaluation Under Recovery Execution
Let $R$ be any row in `observations`, `risk_alerts`, or `farms`.
Under PostgreSQL RLS composition rules:
$$\text{Row Visible}(R) \iff \text{Permissive}(R) \land \text{Restrictive}(R)$$
Since `base_access_policy` is `USING (true)`, row visibility reduces entirely to:
$$\text{Restrictive}(R) \equiv \texttt{ADMIN\_BYPASS\_SQL} \lor \left(R.\text{tenant\_col}::\text{text} = \texttt{current\_setting('app.current\_tenant\_id', true)}\right)$$

Evaluating each term for an Agricultural Expert or Application Administrator connecting via `acrevia_staging_app`:
1. **Term 1 (`ADMIN_BYPASS_SQL`):**
   - Requires `SESSION_USER::text IN ('neondb_owner', 'acrevia_admin')`.
   - In production staging, `SESSION_USER` is `acrevia_staging_app`.
   - $\implies \texttt{ADMIN\_BYPASS\_SQL} = \textbf{FALSE}$.
2. **Term 2 (`tenant_col = app.current_tenant_id`):**
   - In recovery, `app.current_tenant_id` is `""`.
   - Every valid farm ID or foreign key is a non-empty UUID string (e.g. `'a1b2c3d4-...'`).
   - $\implies R.\text{tenant\_col} = \text{''} = \textbf{FALSE}$.
3. **Conclusion:**
   $$\text{Restrictive}(R) \equiv \textbf{FALSE} \lor \textbf{FALSE} = \textbf{FALSE}$$
   **Every source row is filtered out by PostgreSQL's storage engine.**

---

## 7. CONDITIONAL SOURCE-ACCESS COLLAPSE

### 7.1 Service-Layer Manifestation
When lines 476–512 of `RegionalPulseService.recover_suppressed_signal()` execute against a database enforcing RLS:
- `obs_stmt` returns `[]` $\implies$ `observations = {}`
- `alert_stmt` returns `[]` $\implies$ `alerts = {}`
- `farm_stmt` returns `[]` $\implies$ `farms = {}`

In lines 515–543, the service traverses linked evidence:
```python
for ev in evidences:
    if ev.evidence_type in ("OBSERVATION_REF", "OBSERVATION"):
        obs = observations.get(ev.evidence_reference_id)
        if not obs or not obs.farm_id:
            continue
...
current_count = len(verified_farms) # current_count = 0!
if current_count < MINIMUM_DISTINCT_FARMS_THRESHOLD: # 0 < 3!
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Cannot recover signal: verified distinct farms (0) remains below threshold (3)"
    )
```

### 7.2 Deterministic Failure Matrix Across Source Tables
| Source Table | Evaluated Column | Runtime GUC State | Evaluated SQL Predicate | Engine Result | Application Impact |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `farms` | `id` | `app.current_tenant_id = ''` | `id::text = ''` | 0 rows returned | Farm district/archival unverifiable. |
| `observations` | `farm_id` | `app.current_tenant_id = ''` | `farm_id::text = ''` | 0 rows returned | Observation evidence fails verification. |
| `risk_alerts` | `farm_id` | `app.current_tenant_id = ''` | `farm_id::text = ''` | 0 rows returned | Risk alert evidence fails verification. |

$$\textbf{Result: Provenance recalculation deterministically collapses to zero under FORCE RLS.}$$


---

## 8. EXPERT DISTRICT AUTHORITY ASSESSMENT

### 8.1 The Reality of `districts_covered_json` vs. `app.current_user_districts`
In prior reports, it was claimed that Agricultural Experts are bounded by `district = ANY(string_to_array(current_setting('app.current_user_districts', true), ','))`.
An exhaustive codebase search across all directories confirms:
- `app.current_user_districts`: **0 occurrences** in code, tests, migrations, or scripts.
- `current_user_districts`: **0 occurrences**.
- `string_to_array`: **0 occurrences** in RLS generators.

In [backend/app/models/expert_profile.py#L25](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/expert_profile.py#L25), `ExpertProfile` defines:
```python
districts_covered_json: Mapped[str] = mapped_column(
    String(500), default='["Warangal","Khammam"]', nullable=False
)
```
While this column exists in the SQLAlchemy model:
1. It is stored as an unindexed JSON text string.
2. It is **never queried or loaded during JWT authentication** in `get_current_user()`.
3. It is **never injected into session context or GUCs**.
4. No RLS policy in [backend/app/database/rls.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py) references it.
5. `RegionalPulseService.recover_suppressed_signal()` **never verifies the actor's district jurisdiction** against `signal.district`. An expert assigned to Khammam can recover a signal in Adilabad without any jurisdiction check!

### 8.2 Scope Mechanism Inventory Table
The following matrix assesses every theoretical district-scoping mechanism in the ACREVIA codebase:

| Scope Mechanism | Present in Source? | Loaded During Auth? | Verified by RLS? | Verified by Recovery Service? | Governance Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `districts_covered_json` | **YES** (`expert_profile.py`) | **NO** | **NO** | **NO** | Disconnected data column; not enforced. |
| `app.current_user_districts` | **NO** (0 occurrences) | **NO** | **NO** | **NO** | Unimplemented design proposal. |
| Farm Membership | **YES** (`farm.py`) | **NO** (Only via `verify_farm_access`) | **NO** | **NO** | Enforces single-farm, not district scope. |
| Application Role (`user_roles`) | **YES** (`user.py`) | **YES** (`r.id in user.roles`) | **NO** | **YES** (Role check only) | Role present, but district-blind. |
| Worker District Authority | **NO** | **NO** | **NO** | **NO** | Unimplemented design concept. |

---

## 9. APPLICATION ADMIN VERSUS DATABASE ADMINISTRATOR BEHAVIOR

### 9.1 The Tripartite Structure of `ADMIN_BYPASS_SQL`
In [backend/app/database/rls.py#L22-L27](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L22-L27):
```python
ADMIN_ROLES = ("neondb_owner", "acrevia_admin")
ADMIN_BYPASS_SQL = (
    "(SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') "
    "AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') "
    "AND current_setting('app.is_admin', true) = 'true')"
)
```

### 9.2 Defense-in-Depth Analysis
This predicate deliberately enforces three concurrent boundaries:
1. `SESSION_USER::text IN ('neondb_owner', 'acrevia_admin')`: The authenticated physical database connection must belong to an approved administrative role.
2. `CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin')`: The effective execution context must also belong to an approved role, blocking `SECURITY DEFINER` privilege escalation by unprivileged actors.
3. `current_setting('app.is_admin', true) = 'true'`: The application layer must affirmatively assert administrative mode for the active transaction.

### 9.3 Inability of Application Admin to Bypass
- The web application connects to PostgreSQL via a shared connection pool under the runtime login role `acrevia_staging_app`.
- When an Application Administrator authenticates via JWT, `get_current_user()` sets `app.is_admin = 'true'`.
- However, because `SESSION_USER` remains `acrevia_staging_app`, `ADMIN_BYPASS_SQL` evaluates to **`FALSE`**.
- This dual-identity boundary is an essential security control preventing SQL injection in web routes from escaping tenant isolation. It must **not** be weakened to a GUC-only check.

---

## 10. CORRECTED ROW-LOCK AND TABLE-LOCK TERMINOLOGY

### 10.1 PostgreSQL Engine Lock Hierarchy
To resolve the terminology errata from previous reports, row-level lock strengths and table-level lock modes in PostgreSQL 16 are formally distinguished below:

1. **Row-Level Tuple Lock Strengths (Declared in SQL Query):**
   - `FOR UPDATE`: Strongest exclusive lock. Blocks concurrent `FOR UPDATE`, `FOR NO KEY UPDATE`, `FOR SHARE`, `FOR KEY SHARE`, and any `UPDATE`/`DELETE`.
   - `FOR NO KEY UPDATE`: Exclusive lock excluding foreign-key modifications. Allows concurrent `FOR KEY SHARE`.
   - `FOR SHARE`: Shared lock. Blocks concurrent `FOR UPDATE`, `FOR NO KEY UPDATE`, and data modifications (`UPDATE`/`DELETE`). Allows concurrent `FOR SHARE` and `FOR KEY SHARE`.
   - `FOR KEY SHARE`: Weakest shared lock. Blocks only `FOR UPDATE` and key-modifying `UPDATE`/`DELETE`.

2. **Table-Level Lock Modes (Acquired Automatically by PostgreSQL Engine):**
   - When a client executes `SELECT ... FOR UPDATE` or `SELECT ... FOR SHARE`, PostgreSQL acquires a **`ROW SHARE`** lock on the target table.
   - It **NEVER acquires table-level `ExclusiveLock` or `ShareLock`**!
   - Table-level `ExclusiveLock` is reserved for operations like `REFRESH MATERIALIZED VIEW CONCURRENTLY`.
   - Table-level `ShareLock` is reserved for `CREATE INDEX` (without CONCURRENTLY).
   - Confusing row-level lock strength (`FOR UPDATE`) with the table-level `ExclusiveLock` is an architectural erratum.

---

## 11. SELECT/UPDATE POLICY COMPOSITION

### 11.1 The Policy Evaluation Rule for Locking Queries
In PostgreSQL 16 (`src/backend/rewrite/rowsecurity.c`), row-level security policy evaluation during a locking SELECT statement differs critically from both standard SELECT and standard UPDATE:

1. **Evaluation of `FOR SELECT` Policies:**
   PostgreSQL first applies the `USING` clauses of all applicable `FOR SELECT` (or `FOR ALL`) policies to identify candidate rows.
2. **Evaluation of `FOR UPDATE` Policies:**
   Because `FOR UPDATE`, `FOR NO KEY UPDATE`, and `FOR SHARE` declare an intent to lock rows against concurrent updates, PostgreSQL **also applies the `USING` clauses of all applicable `FOR UPDATE` (or `FOR ALL`) policies**!
3. **Double Qualification Invariant:**
   A row is returned and locked by a locking SELECT if and only if:
   $$\text{Row Qualified} \iff \text{Policy}_{SELECT}(\text{OLD}) \land \text{Policy}_{UPDATE}(\text{OLD})$$
4. **Non-Evaluation of `WITH CHECK`:**
   Because a locking SELECT statement does not modify row values, the `WITH CHECK` expression of the `FOR UPDATE` policy is **NOT evaluated** during the locking SELECT. It evaluates only when an actual SQL `UPDATE` statement executes.

---

## 12. CURRENT `FOR ALL` POLICY APPLICABILITY

### 12.1 The Critical DDL Generator Discovery
Previous assurance reports theorized that `SELECT ... FOR UPDATE` failed because `generate_rls_ddl()` had not created a `FOR UPDATE` policy.
Direct inspection of [backend/app/database/rls.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py) reveals that this explanation was **factually incorrect**:

1. **`regional_signals` and `regional_signal_evidences` (Lines 962–968):**
   ```sql
   CREATE POLICY {table_name}_author_write_policy ON {table_name}
       AS PERMISSIVE
       FOR ALL
       TO PUBLIC
       USING ({write_expr})
       WITH CHECK ({write_expr});
   ```
2. **`farms`, `observations`, and `risk_alerts` (Lines 342–361):**
   ```sql
   CREATE POLICY {table_name}_base_access_policy ON {table_name}
       AS PERMISSIVE FOR ALL TO PUBLIC USING (true) WITH CHECK (true);

   CREATE POLICY {table_name}_tenant_isolation_policy ON {table_name}
       AS RESTRICTIVE FOR ALL TO PUBLIC USING ({expr}) WITH CHECK ({expr});
   ```

### 12.2 True Cause of the Access Failure
Because these policies are declared **`FOR ALL`**, they apply to `SELECT`, `INSERT`, `UPDATE`, and `DELETE` commands alike!
- When PostgreSQL executes `SELECT ... FOR UPDATE` or `SELECT ... FOR SHARE`, the engine finds that applicable UPDATE policies **already exist** (the `FOR ALL` policies).
- Therefore, the recovery operation does **not** fail due to a missing UPDATE policy.
- **The true root cause is that `app.current_tenant_id` is empty (`""`), which causes the restrictive `tenant_isolation_policy` to evaluate to `FALSE`, filtering all source rows to zero!**
- The broad `FOR ALL` declaration is itself an over-broad authorization design issue that must be decomposed into command-scoped policies.

---

## 13. SOURCE MUTATION-PATH INVENTORY

The following inventory identifies all independent write paths in the ACREVIA codebase that can mutate source provenance records without acquiring a `RegionalSignal` lock:

| Source Mutation Operation | Code Location (File & Function) | Relevant Source Fields Mutated | Acquires RegionalSignal Lock? | Emits Invalidation Outbox Event? | Independent Transaction Commit? |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Update Farm District** | [farm_service.py#L93](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/farm_service.py#L93) (`update_farm`) | `Farm.district`, `mandal`, `village` | **NO** | **NO** | **YES** (`db.commit()`) |
| **Archive Farm** | [farm_service.py#L84](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/farm_service.py#L84) (`update_farm`) | `Farm.is_archived` | **NO** | **NO** | **YES** (`db.commit()`) |
| **Delete Observation** | `observation_service.py` (`delete_observation`) | Row Deletion (`DELETE`) | **NO** | **NO** | **YES** (`db.commit()`) |
| **Update Observation** | `observation_service.py` (`update_observation`) | `Observation.farm_id`, `created_at` | **NO** | **NO** | **YES** (`db.commit()`) |
| **Resolve Risk Alert** | `risk_service.py` (`resolve_alert`) | `RiskAlert.is_resolved`, `resolved_at` | **NO** | **NO** | **YES** (`db.commit()`) |
| **Direct Evidence Mutation** | Direct SQL / ORM Session | `confidence_score`, `signal_id` | **NO** | **NO** | **YES** (Permitted in crosswalk) |

---

## 14. PARENT-LOCK CONCURRENCY LIMITATIONS

### 14.1 The Defect in the Parent-Lock Redundancy Claim
The previous report argued that child evidence and source locks could be pruned because parent `RegionalSignal FOR UPDATE` serializes recovery.
This claim is fundamentally defective:
1. **Scope of Row Locks:** A row lock on tuple $S$ in table `regional_signals` serializes **only transactions that explicitly execute a locking SELECT or UPDATE on that same tuple $S$**.
2. **Writer Independence:** Farm owners, managers, and IoT edge workers update `farms` and `observations` directly via `FarmService` and `ObservationService`. None of these source writers read or lock `regional_signals`.
3. **Polymorphic Reference Lack of Foreign Key:** `RegionalSignalEvidence.evidence_reference_id` is a bare `String(100)` column, **not a database foreign key**. The PostgreSQL storage engine does not enforce referential locks or integrity checks between signals and source rows.
4. **Concurrency Race Window:** If source-row locks are pruned, `FarmService.update_farm()` can change a farm's district from Warangal to Khammam concurrently with recovery recalculation. The recovery transaction will read the stale district, validate the farm, and confirm an outbreak in the wrong jurisdiction.


---

## 15. SECURITY DEFINER FUNCTION SYNTAX CORRECTION

### 15.1 Identification of Original Syntax Defect
The previous report proposed the following function signature:
```sql
CREATE OR REPLACE FUNCTION verify_regional_signal_provenance(p_signal_id UUID)
RETURNS (INT, BOOLEAN) -- SYNTACTICALLY INVALID IN POSTGRESQL!
```
In PostgreSQL PL/pgSQL grammar, `RETURNS (INT, BOOLEAN)` is a syntax error. PostgreSQL does not permit anonymous parenthesized tuple declarations in the `RETURNS` clause.

### 15.2 Validated PostgreSQL Return Grammar
PostgreSQL requires one of three syntactically valid constructs:
1. `RETURNS TABLE (verified_distinct_farms_count integer, is_valid boolean)`
2. A pre-declared composite type: `CREATE TYPE provenance_result AS (...); ... RETURNS provenance_result`
3. Named `OUT` parameters: `CREATE FUNCTION ...(p_signal_id uuid, OUT verified_count int, OUT is_valid bool)`

### 15.3 Syntactically Correct Function Specification
```sql
CREATE OR REPLACE FUNCTION verify_regional_signal_provenance(p_signal_id UUID)
RETURNS TABLE (verified_distinct_farms_count INT, is_valid BOOLEAN)
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    RETURN QUERY
    WITH signal_window AS (
        SELECT district, observed_start_date, observed_end_date
        FROM regional_signals 
        WHERE id = p_signal_id
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

---

## 16. FUNCTION OWNER AND RLS THREAT MODEL

### 16.1 The Fallacy of Automatic RLS Bypass Under `SECURITY DEFINER`
A critical architectural misconception in earlier discussions is that marking a function `SECURITY DEFINER` automatically bypasses Row-Level Security.
Under PostgreSQL specifications (`src/backend/rewrite/rowsecurity.c`):

1. **The `FORCE ROW LEVEL SECURITY` Barrier:**
   - In [backend/app/database/rls.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py), every protected table executes:
     `ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;`
   - When `FORCE RLS` is enabled, PostgreSQL **enforces RLS policies even against the owner of the table**!
   - The only roles that bypass `FORCE RLS` are `SUPERUSER` and roles possessing the `BYPASSRLS` attribute.
2. **The `SESSION_USER` vs. `CURRENT_USER` Trap in `ADMIN_BYPASS_SQL`:**
   - In PostgreSQL, when a `SECURITY DEFINER` function executes:
     - `CURRENT_USER` switches to the **owner of the function** (e.g. `acrevia_admin`).
     - `SESSION_USER` **NEVER switches**; it remains the authenticated login role of the connection (`acrevia_staging_app`)!
   - Now review `ADMIN_BYPASS_SQL`:
     ```sql
     (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
      AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
      AND current_setting('app.is_admin', true) = 'true')
     ```
   - Even inside a `SECURITY DEFINER` function owned by `acrevia_admin`, `SESSION_USER` is `acrevia_staging_app`.
   - $\implies 	exttt{SESSION\_USER::text IN ('neondb\_owner', 'acrevia\_admin')} = 	extbf{FALSE}$!
   - **Therefore, a `SECURITY DEFINER` function called by `acrevia_staging_app` STILL CANNOT satisfy `ADMIN_BYPASS_SQL`!**

### 16.2 Architectural Resolution
To enable the verifier function to read source records without weakening `ADMIN_BYPASS_SQL` or making `acrevia_staging_app` a superuser:
1. Establish a dedicated capability role: `acrevia_verifier WITH NOLOGIN`.
2. Assign ownership of `verify_regional_signal_provenance` to `acrevia_verifier`.
3. Add a dedicated, role-targeted `PERMISSIVE` policy on `farms`, `observations`, and `risk_alerts`:
   ```sql
   CREATE POLICY {table}_verifier_read_policy ON {table}
       AS PERMISSIVE FOR SELECT TO acrevia_verifier
       USING (true);
   ```
4. This explicitly confines multi-tenant read visibility to the internal execution of the verifier function, completely isolating the interactive web role!

---

## 17. SECURE SEARCH-PATH AND PRIVILEGE HARDENING

### 17.1 Trojan-Table Search-Path Hijacking
In PostgreSQL, `SECURITY DEFINER` functions execute with elevated privileges. If the `search_path` is mutable or unset:
- An attacker can create a temporary table named `farms` or `observations` in `pg_temp`.
- When the elevated function executes an unqualified `SELECT FROM farms`, PostgreSQL queries the attacker's temporary table instead of the schema table.
- This allows privilege escalation, arbitrary code execution, or falsification of outbreak provenance.

### 17.2 Mandatory Search-Path Hardening
PostgreSQL security standards mandate:
1. `SET search_path = public, pg_temp` — Explicitly positions `pg_temp` **last** (or omits it), preventing temporary table interception.
2. All SQL object references in the function body must be schema-qualified.

### 17.3 Strict Execution Privilege Boundary
By default, PostgreSQL grants `EXECUTE` on newly created functions to `PUBLIC`.
To prevent arbitrary enumeration by unauthorized database actors:
```sql
REVOKE ALL ON FUNCTION verify_regional_signal_provenance(UUID) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION verify_regional_signal_provenance(UUID) TO acrevia_staging_app, acrevia_worker;
```

---

## 18. AGGREGATE-ONLY OUTPUT CONTRACT

### 18.1 Data Minimization Invariant (DPDPA 2023)
Under India's Digital Personal Data Protection Act (DPDPA 2023) and ACREVIA Pillar F privacy principles:
- The verification function must operate as an **aggregate one-way projection**.
- It returns strictly:
  $$	exttt{(verified\_distinct\_farms\_count INT, is\_valid BOOLEAN)}$$
- It **NEVER projects or returns**:
  - `farm_id`, farm name, mandal, or village coordinates.
  - Farmer personal names, phone numbers, or account IDs.
  - Raw observation symptoms, dates, or media attachments.
  - Risk alert thresholds or individual loss estimates.
- Calling actors (Agricultural Experts, Administrators, Workers) receive solely the mathematical determination of provenance validity.

---

## 19. VERIFIER ROLE SPECIFICATION

The dedicated capability role governing stored verification logic is specified as:

```sql
-- DDL Specification (Subject to Owner Approval under DB-AUTH-01)
CREATE ROLE acrevia_verifier WITH NOLOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;

-- Grant SELECT only on relations required for provenance revalidation
GRANT USAGE ON SCHEMA public TO acrevia_verifier;
GRANT SELECT ON regional_signals TO acrevia_verifier;
GRANT SELECT ON regional_signal_evidences TO acrevia_verifier;
GRANT SELECT ON observations TO acrevia_verifier;
GRANT SELECT ON risk_alerts TO acrevia_verifier;
GRANT SELECT ON farms TO acrevia_verifier;

-- Assign function ownership
ALTER FUNCTION verify_regional_signal_provenance(UUID) OWNER TO acrevia_verifier;
```

---

## 20. WORKER LOGIN AND `SET ROLE` SPECIFICATION

### 20.1 Distinction Between Login Identity and Group Capability
To operationalize a background daemon (`acrevia_worker`) without violating PostgreSQL authentication rules:

1. **Physical Login Principal:**
   ```sql
   CREATE ROLE acrevia_worker_login WITH LOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE 
   PASSWORD '[REDACTED_MANAGED_SECRET]';
   ```
2. **Capability Group Role:**
   ```sql
   CREATE ROLE acrevia_worker WITH NOLOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
   GRANT acrevia_worker TO acrevia_worker_login;
   ```
3. **Session Role Assumption Lifecycle:**
   When the background daemon establishes a connection:
   ```sql
   -- Initial State: SESSION_USER = 'acrevia_worker_login', CURRENT_USER = 'acrevia_worker_login'
   SET ROLE acrevia_worker;
   -- Active State: SESSION_USER = 'acrevia_worker_login', CURRENT_USER = 'acrevia_worker'
   ```
   Post-transaction cleanup is guaranteed by executing `RESET ROLE;` prior to returning the connection to the worker pool.

---

## 21. EVIDENCE APPEND-ONLY AND UPDATE PRIVILEGE COMPATIBILITY

### 21.1 Reconciling Row Locks with Immutability
As established in Section 11, executing `SELECT ... FOR SHARE` requires `UPDATE` privilege on at least one column of the locked table (`analyze.c`).
To preserve append-only immutability while satisfying row-locking syntax:

1. **The Privilege/Policy Decoupling Pattern:**
   - Grant `UPDATE` on a non-critical technical column:
     `GRANT UPDATE (updated_at) ON regional_signal_evidences TO acrevia_staging_app;`
   - Define a `FOR UPDATE` RLS policy whose `WITH CHECK` expression is **`WITH CHECK (false)`**!
2. **PostgreSQL Policy Evaluation Mechanics:**
   - When `SELECT ... FOR SHARE` executes, PostgreSQL checks column privileges (passes) and evaluates `USING` (passes).
   - If an attacker attempts an actual `UPDATE regional_signal_evidences SET ...`, PostgreSQL evaluates `WITH CHECK (false)` and immediately aborts with:
     `ERROR: new row violates row-level security policy for table "regional_signal_evidences"`
3. **Comparison with Stored Function Architecture:**
   While the `WITH CHECK (false)` pattern works, implementing the `SECURITY DEFINER` function (`verify_regional_signal_provenance`) is **strictly superior**: it eliminates all client-side `FOR SHARE` locks on evidence and source tables entirely, rendering row-lock privilege workarounds unnecessary!


---

## 22. OUTBOX INVALIDATION COVERAGE

### 22.1 Comprehensive Source Invalidation Inventory
Because Regional Pulse provenance depends dynamically on underlying farm, observation, and alert validity, every source mutation must reliably emit an invalidation event to guarantee eventual consistency:

| Source Mutation Operation | Triggering File / Service | Event Type Emitted | Invalidation Target | Staging Guarantee |
| :--- | :--- | :--- | :--- | :--- |
| Farm District Change | `farm_service.py#L93` | `FARM_DISTRICT_CHANGED` | All signals referencing `farm_id` | Must be atomic with `UPDATE farms` |
| Farm Archival | `farm_service.py#L84` | `FARM_ARCHIVED` | All signals referencing `farm_id` | Must be atomic with `UPDATE farms` |
| Observation Deletion | `observation_service.py` | `OBSERVATION_DELETED` | Signals referencing `observation_id` | Must be atomic with `DELETE observations` |
| Observation Mutation | `observation_service.py` | `OBSERVATION_UPDATED` | Signals referencing `observation_id` | Must be atomic with `UPDATE observations` |
| Risk Alert Resolution | `risk_service.py` | `ALERT_RESOLVED` | Signals referencing `alert_id` | Must be atomic with `UPDATE risk_alerts` |
| Signal Recovery | `regional_pulse_service.py` | `SIGNAL_RECOVERED` | Dashboard / Edge Redis Cache | Must be atomic with `UPDATE regional_signals` |

### 22.2 High-Concurrency Event Processing Model
The asynchronous event processor consumes invalidation records from `outbox_events` using PostgreSQL's concurrent locking primitive:
```sql
SELECT id, aggregate_id, event_type, payload
FROM outbox_events
WHERE status = 'PENDING'
ORDER BY created_at ASC
FOR UPDATE SKIP LOCKED
LIMIT 50;
```

**Operational Invariants:**
1. **Idempotency Key:** Every event contains an `idempotency_key = sha256(aggregate_id + event_type + version)`.
2. **Per-Signal Monotonic Ordering:** Events for a given `signal_id` are processed sequentially by grouping on `aggregate_id`.
3. **Lease Timeout & Crash Recovery:** Claimed events have `locked_at` and `lease_timeout = 60s`. If a worker crashes, orphaned events revert to `PENDING` automatically.
4. **Poison Event & Dead-Letter Handling:** After 3 retries (`retry_count >= 3`), events transition to `DEAD_LETTER` with `error_detail` logged, alerting operations without blocking queue progression.

---

## 23. CREDENTIAL EXPOSURE ASSESSMENT

### 23.1 Pinned Source Audit of `frontend/lib/server/db.ts`
An independent, read-only inspection of [frontend/lib/server/db.ts](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/lib/server/db.ts#L1-L14) in public baseline commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d` confirms:

```typescript
// frontend/lib/server/db.ts lines 8-10:
  const dbUrl =
    process.env.DATABASE_URL ||
    "[REDACTED_DATABASE_CONNECTION_STRING_WITH_CREDENTIALS]";
```

### 23.2 Evidentiary Findings
1. **Hard-Coded Secret Fallback:** Line 10 contains a hard-coded fallback connection URI specifying the administrative user `neondb_owner`, an active plaintext password string, and a live Neon Cloud database host endpoint in `aws-ap-southeast-1`.
2. **Conditional Activation:** In production or staging container deployments where `DATABASE_URL` is omitted, misconfigured, or unset, the application automatically falls back to this hard-coded connection URI.
3. **Public Exposure Evidence:** This file is publicly tracked and readable in GitHub commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d`.
4. **Rotation Unproven:** No verifiable evidence exists in the repository indicating that the cloud credential exposed in line 10 has been rotated in the Neon Cloud management console.
5. **Determination:** Canonical blocker `DB-CREDENTIAL-EXPOSURE-01` is **CRITICAL OPEN**.

---

## 24. SECRET CONTAINMENT RECOMMENDATION

To remediate `DB-CREDENTIAL-EXPOSURE-01` without destabilizing pilot environments, the following owner-controlled containment procedure is formally specified:

$$egin{aligned}
	extbf{Step 1: Treat as Compromised} &\longrightarrow 	ext{Project Owner immediately treats the exposed credential as potentially compromised.} \
	extbf{Step 2: Provider-Side Rotation} &\longrightarrow 	ext{Owner logs into Neon Console and rotates the password for } 	exttt{neondb\_owner}	ext{.} \
	extbf{Step 3: Source Code Remediation} &\longrightarrow 	ext{Remove the hard-coded fallback in } 	exttt{frontend/lib/server/db.ts}	ext{:} \
&\quad 	exttt{const dbUrl = process.env.DATABASE\_URL;} \
&\quad 	exttt{if (!dbUrl) throw new Error("DATABASE\_URL environment variable is required.");} \
	extbf{Step 4: Environment Verification} &\longrightarrow 	ext{Verify that all deployed serverless and container runtimes inject } 	exttt{DATABASE\_URL}	ext{.} \
	extbf{Step 5: Git-History Scrubbing} &\longrightarrow 	ext{Audit repository commit history; evaluate history rewrite with BFG / git-filter-repo.} \
	extbf{Step 6: Build & CI/CD Audit} &\longrightarrow 	ext{Verify build artifacts and deployment pipelines do not leak secrets into logs.} \
	extbf{Step 7: Pre-Commit Secret Scanning} &\longrightarrow 	ext{Enforce TruffleHog / GitGuardian pre-commit hooks to block future literal fallbacks.} \
	extbf{Step 8: Attributable Sign-off} &\longrightarrow 	ext{Project Owner records rotation token in Governance Register to close blocker.}
\end{aligned}$$

---

## 25. CANONICAL BLOCKER EVIDENCE RECONCILIATION

The table below reconciles all 15 canonical Phase 07 security blockers against strict evidentiary classifications:

| Blocker Identifier | Governance Domain | Prior Claimed Status | Corrected Evidence-Bound Status | Detailed Evidentiary Basis | Gating Condition |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **`RLS-WRITE-AUTH-01`** | Write Route RLS | Mitigated by Design | **`OPEN_DESIGN_GAP`** | Command-scoped RLS policies designed on paper; unmerged in source. | Owner Sign-Off |
| **`RLS-ROLE-ASSIGNMENT-01`** | Session GUC Trust | Mitigated by Design | **`OPEN_SOURCE_DEFECT`** | `app.current_user_id` mutable via direct SQL under shared app role. | Code Revision |
| **`DB-AUTH-01`** | Database Roles | Blocked pending Owner | **`OWNER_APPROVAL_PENDING`** | Roles `acrevia_staging_app` and `acrevia_worker` unprovisioned in DB. | Owner GATE-02 |
| **`DB-CREDENTIAL-EXPOSURE-01`**| Secret Exposure | Remediated & Verified | **`OPEN_SOURCE_DEFECT`** | Hard-coded URI fallback remains in `frontend/lib/server/db.ts#L10`. | Owner Rotation |
| **`APP-ROLE-SELF-SELECT-01`** | Role Escalation | Mitigated by Design | **`OPEN_DESIGN_GAP`** | Relies on unverified session context immutability. | Design Hardening |
| **`EXP-AUTH-01`** | Expert Jurisdiction | Mitigated by Design | **`OPEN_DESIGN_GAP`** | `app.current_user_districts` GUC completely absent from codebase. | Schema & Auth Gap |
| **`CASCADE-ROLE-DEL-01`** | Role Lifecycle | Mitigated by Design | **`PROPOSED_MITIGATION_NOT_IMPLEMENTED`** | Migration-based role drop protection designed, unapplied to staging. | Staging DDL |
| **`TENANT-MEMBERSHIP-01`** | Tenant Isolation | Enforced by Policy | **`OPEN_SOURCE_DEFECT`** | Recovery source queries return 0 rows under RLS; recalculation broken. | Verifier DDL |
| **`OWNER-AUTH-01`** | Owner Approval | Pending Signature | **`OWNER_APPROVAL_PENDING`** | Gated on Owner completion of GATE-02 through GATE-05. | Owner Sign-Off |
| **`DB-RLS-01`** | Engine RLS Activation | Designed | **`LIVE_DATABASE_UNVERIFIED`** | Migration `a1089411c87d` unapplied to staging database. | Owner GATE-03 |
| **`WRK-DISP-01`** | Worker Dispatch | Designed | **`OPEN_DESIGN_GAP`** | Proposed `acrevia_worker` does not exist as an operational daemon. | Implementation |
| **`RES-PULSE-01`** | Aggregation Privacy | Designed | **`OPEN_SOURCE_DEFECT`** | Provenance recalculation broken under RLS (measures count=0). | Verifier DDL |
| **`RES-PULSE-02`** | Concurrency Collision | Mitigated by Design | **`OPEN_DESIGN_GAP`** | Source lock pruning leaves unmitigated farm district update races. | Concurrency Model |
| **`GATE01-PROV-01`** | Branch Identity | Identified Discrepancy | **`OPEN_DESIGN_GAP`** | Register mismatch (`staging-rls-phase07` vs `staging-rls-phase05`). | Owner Decision |
| **`RES-PULSE-READ-01`** | Farmer Read Isolation | Designed & Proven | **`LIVE_DATABASE_UNVERIFIED`** | Farmer read boundary unverified under live FORCE RLS kernel execution. | Owner GATE-04 |

---

## 26. RESIDUAL-RISK RECONCILIATION

The 5 canonical residual risks remain active and classified as follows:

| Residual Risk ID | Domain | Severity | Operational Precondition & Threat Profile | Mitigation State |
| :--- | :--- | :---: | :--- | :--- |
| **`RES-PULSE-01`** | Geographic Privacy | **MEDIUM** | In sparse mandals, outbreak publication without valid $\ge 3$ distinct farms allows farmer re-identification. | Open (Recalculation currently broken under RLS). |
| **`RES-PULSE-02`** | Concurrency Collision | **MEDIUM** | Race condition between concurrent farm district updates and signal recovery recalculation. | Open (Source lock pruning removes concurrency protection). |
| **`RES-PRIMARY-ROUTING-01`**| Database Replication | **MEDIUM** | Read replicas serving stale data during recovery revalidation. | Open (Requires strict primary writer node routing). |
| **`RES-REPLICA-LAG-01`** | Telemetry Staleness | **LOW** | Replica lag causing temporary visual discrepancy on public dashboard. | Monitored by timestamp validation. |
| **`RES-FREE-TEXT-01`** | PII Infiltration | **LOW** | Unstructured observation notes containing farmer phone numbers. | Schema excludes raw text notes from regional aggregation. |

### 26.1 Special Governance Items
- **`DB-GRANT-APPLY-01`:** Retains status **`PROPOSED — OWNER APPROVAL REQUIRED`**.
- **`FARMER_READ_BLOCKED_BY_EVIDENCE_ASSOCIATION_RLS`:** Retained as descriptive finding, not a canonical blocker.

---

## 27. OWNER DECISION TRACEABILITY

The authoritative architectural decisions governing Phase 07 are cataloged below:

| Decision ID | Core Architectural Scope | Relationship to Verifier Architecture | Status in Governance Register |
| :--- | :--- | :--- | :---: |
| **D-01** | Official Advisory Public Visibility vs. Minimum Farm Threshold | Enforces $k \ge 3$ distinct farms privacy threshold during provenance verification. | Owner Approved |
| **D-02** | Source Authenticity & Medical/Agronomic Terminology | Requires verified source evidence before lifting outbreak claim suppression. | Owner Approved |
| **D-03** | Agronomic Peer-Review Workflow | Governs expert validation roles (`AGRICULTURAL_EXPERT` vs `ADMIN`). | Owner Approved |
| **DB-AUTH-01** | Trusted Writer Database Architecture | Governs database role provisioning (`acrevia_staging_app`, `acrevia_worker`, `acrevia_verifier`). | Requires Amendment |

---

## 28. GATE-01 THROUGH GATE-05 STATUS

In [docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md):

| Gate ID | Registered Decision Scope | Authoritative Registered State | Mode Impact & Operating Constraint |
| :--- | :--- | :---: | :--- |
| **GATE-01** | Provisioning of isolated Neon staging branch `staging-rls-phase07` in `aws-ap-southeast-1`. | **`[x] APPROVED BY OWNER (2026-11-10)`** | Staging branch creation approved. Do not request re-approval. |
| **GATE-02** | Creation of unprivileged runtime database role `acrevia_staging_app` (`NOSUPERUSER`, `NOBYPASSRLS`). | **`[ ] UNCHECKED (AWAITING SIGN-OFF)`** | Staging role creation locked pending sign-off. Scope excludes secrets. |
| **GATE-03** | Physical execution of Alembic RLS migration `a1089411c87d` applying 751 atomic DDL statements. | **`[ ] UNCHECKED (AWAITING SIGN-OFF)`** | Staging DDL application locked pending sign-off. |
| **GATE-04** | Execution of automated staging RLS verification harness (`scripts/verify_staging_rls.py`). | **`[ ] UNCHECKED (AWAITING SIGN-OFF)`** | Live testing locked pending sign-off. |
| **GATE-05** | Teardown and deprovisioning schedule of `staging-rls-phase05` post-verification. | **`[ ] UNCHECKED (AWAITING SIGN-OFF)`** | Cloud resource destruction locked pending sign-off. |

**Governance Invariant:** MODE B remote cloud execution remains strictly **UNAUTHORIZED**.


---

## 29. ARCHITECTURE COMPARISON

To safely verify district-level agricultural signals across multiple tenant-owned farms while preserving tenant isolation, four candidate architectures are systematically evaluated across 12 security and operational dimensions:

- **Architecture A — Trusted `SECURITY DEFINER` Aggregate Function:** A dedicated capability role (`acrevia_verifier`) owns an encapsulated function returning strictly aggregate counts (`RETURNS TABLE (INT, BOOL)`), with `search_path = public, pg_temp` and execution granted to runtime roles.
- **Architecture B — Dedicated Worker with Narrow RLS Policies:** A background daemon logging in via `acrevia_worker_login`, assuming group role `acrevia_worker`, granted direct table-level `SELECT` on source tables bounded by RLS policies.
- **Architecture C — Precomputed Trusted District Projection:** A background materialization pipeline continuously maintaining precomputed distinct-farm counts in a read-only aggregate projection, updated via outbox events.
- **Architecture D — Controlled Service Gateway:** A separate internal microservice operating under a dedicated administrative database identity, executing verification queries via private gRPC/HTTP APIs.

### 29.1 Multi-Dimensional Architecture Comparison Matrix

| Evaluation Dimension | Architecture A: `SECURITY DEFINER` Function | Architecture B: Dedicated Worker Role | Architecture C: Precomputed Projection | Architecture D: Controlled Service Gateway |
| :--- | :---: | :---: | :---: | :---: |
| **1. Raw Tenant Data Exposure** | **ZERO** (Aggregate output only) | High (Worker sees raw rows) | **ZERO** (Pre-aggregated) | High (Gateway reads raw rows) |
| **2. Cross-Tenant Aggregation** | **YES** (Internal to function) | **YES** (Broad worker SELECT) | **YES** (Precalculated) | **YES** (Service-level bypass) |
| **3. District Scoping** | Strong (SQL parameter check) | Moderate (RLS predicate) | Strong (Keyed by district) | Moderate (Service code check) |
| **4. RLS Compatibility** | **High** (Targeted role policy) | Complex (Custom worker policies) | High (Public projection RLS) | Bypasses RLS entirely |
| **5. Row-Lock Requirements** | **Low** (Zero source client locks) | High (Needs source row locks) | **None** (Read from projection) | High (Cross-service locks) |
| **6. Source Mutation Concurrency** | Atomic statement snapshot | Race-prone without locks | Eventual consistency lag | Race-prone without locks |
| **7. Outbox Dependency** | None (Direct query) | High (Queue-driven) | Critical (Pipeline-driven) | None (Direct query) |
| **8. Stale Publication Window** | **Zero** (Real-time calculation) | Processing delay | Eventual consistency delay | Zero (Real-time query) |
| **9. Operational Complexity** | **Low** (Single database function) | Moderate (Worker daemon) | High (Materialization engine) | Very High (New microservice) |
| **10. Credential Separation** | Strong (Database role boundary) | Strong (Separate login role) | Strong (Worker credentials) | Moderate (Service token) |
| **11. Auditability** | High (Function execution logs) | High (Worker audit trails) | Moderate (Pipeline metrics) | High (gRPC access logs) |
| **12. Owner Approval Requirement** | DB-AUTH-01 Function Addendum | DB-AUTH-01 Role Extension | Schema & Pipeline ADR | Full System Architecture ADR |

### 29.2 Recommended Architecture
**Architecture A (`SECURITY DEFINER` Function) is strongly recommended** as the primary synchronization control, paired with **Architecture C (Outbox Invalidation)** for background cache invalidation:
- Architecture A completely resolves the tenant-context collapse without exposing raw farmer data or granting broad database privileges to `acrevia_staging_app`.
- It eliminates the need for problematic client-side `FOR SHARE` locks on evidence and source tables.
- It operates with zero staleness, guaranteeing immediate consistency during recovery.

---

## 30. FUTURE POSTGRESQL VERIFICATION MATRIX

*Note: In strict adherence to MODE A boundaries, the following 15 test procedures are pre-implementation specifications for future execution only after Owner approval of GATE-02 and GATE-03.*

| Test Scenario ID | Target Focus Area | Database Identity & Context | Executed SQL Statement / Operation | Expected PostgreSQL Engine Response | Security Invariant Verified |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **TEST-VER-01** | Empty Tenant Context Read | `acrevia_staging_app`<br>`app.current_tenant_id = ''` | `SELECT COUNT(*) FROM observations;` | Returns `0` under `FORCE RLS`. | Validates restrictive tenant isolation filter. |
| **TEST-VER-02** | App Admin Dual-Identity Fail | `acrevia_staging_app`<br>`app.is_admin = 'true'` | `SELECT COUNT(*) FROM observations;` | Returns `0` (fails `SESSION_USER` check). | Proves dual-identity gate resists app escalation. |
| **TEST-VER-03** | Stored Function Execution | `acrevia_staging_app` | `SELECT * FROM verify_regional_signal_provenance(:id);` | Returns `(count INT, is_valid BOOL)` cleanly. | Confirms verifier function calculates provenance. |
| **TEST-VER-04** | Function PUBLIC Revocation | Unprivileged Role | `SELECT * FROM verify_regional_signal_provenance(:id);` | `ERROR: permission denied for function ... (SQLSTATE 42501)` | Enforces execution authorization boundary. |
| **TEST-VER-05** | Trojan `pg_temp` Protection | `acrevia_staging_app` | `CREATE TEMP TABLE farms (...); SELECT * FROM verify...();` | Query reads schema `public.farms`, ignores temp table. | Verifies hardened `search_path` security. |
| **TEST-VER-06** | FOR ALL Policy on Locking SELECT | `acrevia_staging_app` | `SELECT * FROM regional_signals WHERE id = :id FOR UPDATE;` | Policy evaluated under both SELECT and UPDATE. | Proves `FOR ALL` policy applicability. |
| **TEST-VER-07** | Evidence Append-Only WITH CHECK | `acrevia_staging_app` | `UPDATE regional_signal_evidences SET confidence_score = 1.0;` | `ERROR: new row violates row-level security policy` | Verifies `WITH CHECK (false)` prevents mutation. |
| **TEST-VER-08** | Concurrent Farm District Change | Tx1: Recovery<br>Tx2: `update_farm` | Tx1 reads farm district; Tx2 updates district to other mandal. | Tx1 fails or blocks cleanly; no phantom validation. | Validates concurrency isolation boundary. |
| **TEST-VER-09** | Outbox Event Insertion Atomicity | `acrevia_staging_app` | Recovery aborts; verify outbox table for invalidation event. | Zero outbox rows created (transaction rolled back). | Prevents split-brain and false notifications. |
| **TEST-VER-10** | Worker NOLOGIN Rejection | `acrevia_worker` | Attempt direct connection: `psql -U acrevia_worker ...` | `FATAL: role "acrevia_worker" is not permitted to log in` | Confirms NOLOGIN group role security. |
| **TEST-VER-11** | Worker `SET ROLE` Assumption | `acrevia_worker_login` | `SET ROLE acrevia_worker; SELECT CURRENT_USER;` | Returns `acrevia_worker`, session remains login role. | Confirms role delegation lifecycle. |
| **TEST-VER-12** | Foreign Key Deletion Restriction | `acrevia_staging_app` | `DELETE FROM regional_signals WHERE id = :id;` | `ERROR: violates foreign key constraint (SQLSTATE 23001)` | Proves `ON DELETE RESTRICT` protects evidence. |
| **TEST-VER-13** | Outbox Concurrent Worker Claim | 2 Worker Sessions | `SELECT * FROM outbox_events ... FOR UPDATE SKIP LOCKED;` | Workers acquire disjoint row batches without blocking. | Confirms deadlock-free outbox consumption. |
| **TEST-VER-14** | Fail-Closed Missing Secret | Node.js Test Harness | Start server with `DATABASE_URL` unset and fallback deleted. | Server crashes immediately; zero connection attempts. | Validates fail-closed secret architecture. |
| **TEST-VER-15** | Cross-District Scope Rejection | `acrevia_staging_app` | Function call on signal outside expert's assigned district. | Function returns `(0, FALSE)` or raises access error. | Enforces district-level authority boundary. |

---

## 31. ADVERSARIAL REVIEW

### 1. Can an attacker exploit `SECURITY DEFINER` if `pg_temp` is not positioned last?
**Defense:** In PostgreSQL, if `search_path` allows `pg_temp` before `public`, any session capable of creating temporary objects can create a spoofed table with matching column names. When the elevated function executes, PostgreSQL resolves the table name to `pg_temp.farms`, allowing an attacker to inject arbitrary farm records and falsely validate outbreak signals. Enforcing `SET search_path = public, pg_temp` eliminates this vulnerability.

### 2. Does `SECURITY DEFINER` automatically bypass `FORCE ROW LEVEL SECURITY`?
**Defense:** No. Under PostgreSQL engine specifications, `FORCE RLS` compels policy evaluation even when queries are issued by the table owner. Unless the function owner is a `SUPERUSER` or possesses `BYPASSRLS`, RLS policies are strictly evaluated. The verifier role must be granted a specific, role-targeted `PERMISSIVE` policy to read source rows.

### 3. Why does `SESSION_USER` prevent a `SECURITY DEFINER` function from satisfying `ADMIN_BYPASS_SQL`?
**Defense:** Inside a `SECURITY DEFINER` function, PostgreSQL switches `CURRENT_USER` to the function owner, but `SESSION_USER` remains permanently bound to the original physical login identity (`acrevia_staging_app`). Because `ADMIN_BYPASS_SQL` checks `SESSION_USER IN ('neondb_owner', 'acrevia_admin')`, the check strictly evaluates to `FALSE`.

### 4. How does `RETURNS TABLE` resolve the PostgreSQL PL/pgSQL syntax defect?
**Defense:** The previous draft specified `RETURNS (INT, BOOLEAN)`, which is unparseable grammar in PostgreSQL. Declaring `RETURNS TABLE (verified_distinct_farms_count INT, is_valid BOOLEAN)` explicitly establishes a strongly typed composite tabular output schema conforming to SQL standard BNF.

### 5. Why does `FarmService.update_farm()` invalidate the parent-lock redundancy assumption?
**Defense:** `FarmService.update_farm()` executes independent `UPDATE farms` transactions committed without reading or locking `regional_signals`. Because source writers do not participate in the parent signal lock protocol, locking the parent signal provides zero synchronization against concurrent farm district changes.

### 6. What prevents `acrevia_staging_app` from directly querying source tables if the verifier role has access?
**Defense:** The targeted RLS policy is granted strictly `TO acrevia_verifier`. Because `acrevia_staging_app` is not a member of `acrevia_verifier`, its direct SQL queries remain strictly bounded by tenant isolation policies.

### 7. Why is `DB-CREDENTIAL-EXPOSURE-01` still open?
**Defense:** A hard-coded fallback connection URI containing an administrative role name and password string remains in the public GitHub commit on `main` ([frontend/lib/server/db.ts#L10](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/lib/server/db.ts#L10)). Until this line is replaced with fail-closed logic and rotation evidence is verified, the blocker must remain open.

### 8. Why can't `app.current_user_districts` be used today?
**Defense:** Because it does not exist. There are 0 occurrences of this GUC in the codebase. Authentication does not load district assignments from `ExpertProfile`, and RLS policies do not evaluate it.

### 9. Why is `WITH CHECK (false)` on evidence UPDATE sound?
**Defense:** PostgreSQL evaluates `USING` to determine which rows can be locked by `SELECT ... FOR SHARE`, and `WITH CHECK` to validate new rows produced by `UPDATE`. By granting `UPDATE (updated_at)` and setting `WITH CHECK (false)`, the locking SELECT passes engine checks while any real UPDATE command is rejected with an RLS violation.

### 10. What is the operational distinction between `acrevia_worker_login` and `acrevia_worker`?
**Defense:** `acrevia_worker_login` has `LOGIN` and authenticates via connection pool credentials. `acrevia_worker` has `NOLOGIN` and holds specific capability grants. The daemon establishes a connection and executes `SET ROLE acrevia_worker;` to assume privileges securely.

---

## 32. IMPLEMENTATION-READINESS CONCLUSION

Based on the discovery of the source provenance RLS collapse, the invalid stored function syntax, unmitigated source mutation race conditions, and active hard-coded credentials in the public source, the implementation readiness ratings for ACREVIA Phase 07 are formally certified as:

| Assurance Evaluation Dimension | Formal Readiness Certification Status | Operational Definition & Governing Constraint |
| :--- | :--- | :--- |
| **Overall Design Readiness** | **`NOT_READY_FOR_OWNER_REVIEW`** | Provenance recalculation fails closed under RLS; verifier function requires formal DDL engineering; credential exposure is active. |
| **Implementation Authorization** | **`NOT_IMPLEMENTATION_AUTHORIZED`** | Strictly zero source code, database, migration, or credential changes permitted. |
| **Phase 07 Release Status** | **`NOT RELEASED`** | Phase 07 cannot be certified or released in its current state. |
| **MODE B Remote Staging Status**| **`NOT AUTHORIZED`** | Cloud staging execution remains strictly locked pending Owner sign-off on GATE-02 through GATE-05. |

---

## 33. EXACT AUDIT LIMITATIONS

In strict adherence to the governing security audit charter:
1. **Mode A Execution Only:** Zero remote database connections were established (Neon Cloud staging and production endpoints remained untouched).
2. **Zero Code Modifications:** No application source files, models, schemas, migrations, or tests were altered.
3. **Zero Git Modifications:** No Git commits, branches, rebases, checkouts, or history manipulations were performed.
4. **Zero Credential Exposure:** No database passwords, JWT secrets, or cloud API tokens were printed or logged.
5. **Preservation of Artifacts:** All 7 tracked governance files and all 16 historical assurance reports were preserved non-destructively.
