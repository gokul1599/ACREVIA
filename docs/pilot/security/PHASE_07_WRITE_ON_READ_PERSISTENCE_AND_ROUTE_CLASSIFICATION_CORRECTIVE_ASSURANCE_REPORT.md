# ACREVIA — PHASE 07: WRITE-ON-READ PERSISTENCE CONDITIONS, ORM ROWCOUNT SEMANTICS & CROSS-LAYER ROUTE CLASSIFICATION CORRECTIVE ASSURANCE AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** MODE A ONLY — Offline Source Inspection, Static Policy Analysis, ORM Transaction Modeling, AST Verification & Governance Documentation  
**Methodology:** Everything Claude Code (ECC) — `PLAN → INSPECT → MODEL → ADVERSARIAL REVIEW → VERIFY → DOCUMENT`  
**Public Repository:** `https://github.com/gokul1599/ACREVIA`  
**Verified Baseline:** Commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Prior Deliverable:** `PHASE_07_REGIONAL_PULSE_SERVICE_REACHABILITY_AND_POLICY_COMPOSITION_AUDIT.md` (Preserved intact)  
**Audit Status:** COMPLETE — FORMAL GOVERNANCE CORRECTIVE DELIVERABLE  
**Classification:** STRICTLY CONFIDENTIAL — AGRICULTURAL SECURITY & REGIONAL GOVERNANCE  

---

## 1. EXECUTIVE DETERMINATION

### Overall Audit Determination: `WRITE_ON_READ_MUTATION_STAGED_PERSISTENCE_CONDITIONAL_ON_UNVERIFIED_DEPLOYED_GRANTS`

Following rigorous cross-layer verification across SQLAlchemy ORM transaction lifecycles, nested savepoint boundaries, PostgreSQL row-level security policy compositions, and table privilege generator call sites, this corrective audit establishes:

1. **ORM Mutation Staging is Source-Confirmed (`ORM_MUTATION_STAGED` / `SOURCE_PATH_CONFIRMED`):**  
   Both [`GET /api/v1/regional-pulse/signals`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/regional_pulse.py#L67-L108) and [`GET /api/v1/regional-pulse/signals/{signal_id}`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/regional_pulse.py#L111-L150) invoke `RegionalPulseService.revalidate_signal_provenance()` and explicitly execute `db.commit()` on the outer database session. Under standard authenticated read requests (`app.current_tenant_id = ''`), PostgreSQL RLS filters out all underlying observation and farm records. The revalidation method executes inside `with db.begin_nested():`. Because RLS row filtering returns `None` cleanly without raising an SQL exception, the savepoint releases cleanly, and the mutations (`distinct_farms_count = 0`, `validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'`) **are preserved in the SQLAlchemy Session's identity map as dirty attributes**.

2. **Persistence is Conditional on Unverified Deployed Table Grants (`CONDITIONAL_ON_DEPLOYED_GRANTS` / `LIVE_COMMIT_NOT_VERIFIED`):**  
   For a role-bearing actor (`AGRICULTURAL_EXPERT` or `RESEARCHER`), the generated RLS write predicate on `regional_signals` evaluates to `TRUE` via the subquery on `user_roles`. Furthermore, `PRIVILEGE_CROSSWALK` specifies `UPDATE = True` for `COMMUNITY_COLLABORATIVE` tables. However, repository-wide AST inspection confirms that **`generate_privilege_grants_ddl()` is never invoked by any Alembic migration or bootstrap script**. Consequently, whether the outer `db.commit()` persists the mutation or aborts with `permission denied` depends entirely on unverified, out-of-band DBA grants on the live PostgreSQL instance (`LIVE_ACL_NOT_VERIFIED`). A live commit has **not been verified** in Mode A.

3. **Ordinary Farmer UPDATE Denial Semantics Corrected (`EXACT_LIVE_EXCEPTION_NOT_VERIFIED`):**  
   The previous report asserted that ordinary farmers receive an RLS `WITH CHECK` violation. In PostgreSQL kernel RLS mechanics, an UPDATE statement filters existing rows against the policy's `USING` clause first. Because the farmer fails the `USING` predicate, PostgreSQL matches **zero rows (`rowcount = 0`)** rather than raising a check violation. In SQLAlchemy ORM, attempting to flush an existing entity that affects zero rows raises **`sqlalchemy.orm.exc.StaleDataError`**. Alternatively, if table-level UPDATE grants are absent, PostgreSQL raises `permission denied` (SQLSTATE `42501`). In Mode A without live database execution, the exact runtime exception is formally classified as **`EXACT_LIVE_EXCEPTION_NOT_VERIFIED`**.

4. **ExpertConnect Table Classifications Corrected (`SOURCE_CONFIRMED`):**  
   The previous report erroneously described `expert_review_cases` and related tables as `TENANT_COLLABORATIVE`. In `backend/app/database/rls.py`, the authoritative classifications are:
   - `expert_review_cases`: **`TENANT_DIRECT`** (`column = 'farm_id'`)
   - `expert_assessments`: **`TENANT_INDIRECT`** (`parent_table = 'expert_review_cases'`, `fk = 'case_id'`)
   - `expert_assessment_revisions`: **`TENANT_INDIRECT`** (`parent_table = 'expert_assessments'`, `fk = 'assessment_id'`)
   - `expert_reviews`: **`TENANT_INDIRECT`** (`parent_table = 'diagnosis_requests'`, `fk = 'diagnosis_request_id'`)  
   Because `expert_review_cases` is `TENANT_DIRECT`, its generated RLS policy restricts visibility strictly to `farm_id = app.current_tenant_id`. Under standard expert requests where `app.current_tenant_id = ''`, **PostgreSQL RLS filters out ALL cases (`RLS_FILTERS_ROW`)**. The entire cross-farm expert triage workflow returns an empty result set (`[]`) or 404 under standard RLS tenant isolation.

5. **Route Decorator and Evidence Schema Accuracy Corrected (`SOURCE_CONFIRMED`):**  
   - [`GET /api/v1/expertconnect/cases`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/expertconnect.py#L98-L105) does **not** lack a role check; it enforces `current_user = Depends(require_roles(SystemRole.AGRICULTURAL_EXPERT.value, SystemRole.ADMIN.value))`.
   - The serialized evidence schema is [`RegionalSignalEvidenceItem`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/schemas/regional_pulse.py#L42-L50) (not `RegionalSignalEvidenceResponse`), and its timestamp property is **`added_at`** (not `created_at`).
   - The actual frontend database helper path is **`frontend/lib/server/db.ts`** (not `frontend/lib/db.ts`).

---

## 2. BASELINE AND SCOPE

- **Inspected Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`HEAD` -> `main`, `origin/main`).
- **Working Tree Integrity:** Clean working tree. The prior report [`docs/pilot/security/PHASE_07_REGIONAL_PULSE_SERVICE_REACHABILITY_AND_POLICY_COMPOSITION_AUDIT.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_REGIONAL_PULSE_SERVICE_REACHABILITY_AND_POLICY_COMPOSITION_AUDIT.md) is preserved intact.
- **Mode A Compliance:** Zero remote database connections, zero SQL executions on live instances, zero Alembic migrations executed, zero source or test modifications.

---

## 3. EVIDENCE CLASSIFICATION LEGEND

Every finding in this corrective audit is categorized under the following ten formal tiers:

1. `SOURCE_CONFIRMED` — Directly established by inspected application source code.
2. `POLICY_GENERATOR_CONFIRMED` — Established by SQL emitted from `generate_rls_ddl()`.
3. `STATIC_TRANSACTION_PATH_CONFIRMED` — Established by tracing service methods and ORM session lifecycles.
4. `ORM_MUTATION_STAGED` — Established by tracing Python object attribute mutation in the SQLAlchemy identity map.
5. `POLICY_PREDICATE_MATCHES` — Established by evaluating generated SQL policy predicates against actor GUCs.
6. `GENERATED_GRANT_SPECIFICATION_PERMITS` — Established by Python least-privilege dictionary specifications (`PRIVILEGE_CROSSWALK`).
7. `CONDITIONAL_ON_DEPLOYED_GRANTS` — Requires actual PostgreSQL table privileges (`GRANT ...`).
8. `CONDITIONAL_ON_DEPLOYED_RLS` — Requires generated policies to be installed and active on the database.
9. `LIVE_COMMIT_NOT_VERIFIED` — Database persistence cannot be verified in Mode A without live database access.
10. `EXACT_LIVE_EXCEPTION_NOT_VERIFIED` — Exact PostgreSQL runtime error cannot be determined without live execution.

---

## 4. EXACT REGIONAL PULSE GET EXECUTION TRACES

### 4.1 Trace of `GET /api/v1/regional-pulse/signals`

```
1. Request arrives at GET /api/v1/regional-pulse/signals
2. Dependency get_current_user decodes JWT:
   - Sets app.current_user_id = str(user.id)
   - app.current_tenant_id remains empty ('')
   - app.is_admin remains 'false' (unless user possesses ADMIN role)
3. RegionalPulseService.query_signals() executes:
   - SELECT regional_signals WITH selectinload(RegionalSignal.evidences)
   - Pre-suppression read policy permits rows where distinct_farms_count >= 3
4. Route iterates over signals:
   - Invokes RegionalPulseService.revalidate_signal_provenance(db, sig.id)
5. Inside revalidate_signal_provenance():
   - Opens savepoint: with db.begin_nested()
   - Iterates sig.evidences and executes db.get(Observation, ...)
   - observations table is TENANT_DIRECT: USING (farm_id = app.current_tenant_id)
   - Since app.current_tenant_id is '', RLS filters row -> returns None!
   - current_count = len(verified_farms) = 0
   - sig.distinct_farms_count = 0
   - sig.validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'
   - Nested savepoint releases cleanly (no SQL error occurred)
   - Returns False
6. Route checks:
   - if not is_valid and not is_privileged: continue (omits suppressed signal from response)
7. Route executes outer database commit:
   - db.commit() at line 99!
8. Flush & Commit Evaluation:
   - SQLAlchemy attempts UPDATE regional_signals SET distinct_farms_count = 0, validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE' WHERE id = :id
```

### 4.2 Trace of `GET /api/v1/regional-pulse/signals/{signal_id}`

```
1. Request arrives at GET /api/v1/regional-pulse/signals/{signal_id}
2. Dependency get_current_user decodes JWT:
   - Sets app.current_user_id = str(user.id); app.current_tenant_id = ''
3. RegionalPulseService.get_signal() executes:
   - SELECT regional_signals WHERE id = :signal_id WITH selectinload(RegionalSignal.evidences)
4. Route calls RegionalPulseService.revalidate_signal_provenance(db, sig.id):
   - Opens savepoint: with db.begin_nested()
   - Evidence lookups return None under empty tenant context
   - sig.distinct_farms_count = 0; sig.validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'
   - Nested savepoint releases cleanly; returns False
5. Route executes outer database commit:
   - db.commit() at line 128!
6. If commit succeeds and actor is unprivileged:
   - if not is_valid and not is_privileged: raise HTTPException(404)
```

---

## 5. SEPARATE EXPERT/RESEARCHER AND FARMER PATH ANALYSIS

### 5.1 Case A — Role-Bearing Actor (`AGRICULTURAL_EXPERT` or `RESEARCHER`)
1. **Actor Context:** `app.current_user_id` is set to the actor's UUID; `app.current_tenant_id` is empty.
2. **Evidence Association Loading:** Under [`regional_signal_evidences_author_write_policy`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L909-L931), role-bearing actors pass the `EXISTS (SELECT 1 FROM user_roles WHERE role_id IN (...))` check, loading the association rows into memory.
3. **Underlying Evidence Filtering:** In `revalidate_signal_provenance()`, `db.get(Observation, ...)` executes against `observations` (`TENANT_DIRECT`). RLS filters the rows (`RLS_FILTERS_ROW`), returning `None`.
4. **Mutation Staging:** `sig.distinct_farms_count = 0` and `sig.validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'` are staged in the ORM session.
5. **UPDATE Execution:** When `db.commit()` flushes:
   - The generated `regional_signals_author_write_policy` allows UPDATE because the subquery on `user_roles` matches the actor's role (`POLICY_PREDICATE_MATCHES`).
   - If the database principal possesses table-level `UPDATE` privilege on `regional_signals` and `SELECT` privilege on `user_roles`, PostgreSQL applies the update.
   - The outer transaction commits (`CONDITIONAL_ON_DEPLOYED_GRANTS` / `LIVE_COMMIT_NOT_VERIFIED`).
6. **Resulting Visibility:** The signal is immediately suppressed from all subsequent public reads.

### 5.2 Case B — Ordinary Farmer
1. **Actor Context:** `app.current_user_id` is set to the farmer's UUID; `app.current_tenant_id` is empty.
2. **Evidence Association Filtering:** The SELECT query for `RegionalSignal.evidences` executes against `regional_signal_evidences`. Because the farmer lacks an expert role, RLS filters out all evidence rows (`RLS_FILTERS_ROW`), returning an empty collection `[]`.
3. **Mutation Staging via Empty Collection:** In `revalidate_signal_provenance()` at line 338:
   ```python
   if not signal.evidences:
       signal.distinct_farms_count = 0
       signal.validation_status = "SUPPRESSED_INSUFFICIENT_PROVENANCE"
       return False
   ```
   The empty evidence list triggers immediate mutation staging in Python memory!
4. **UPDATE Execution & Denial:** When `db.commit()` flushes:
   - PostgreSQL evaluates `regional_signals_author_write_policy` for the UPDATE.
   - The farmer fails the `USING` clause of the policy (the `user_roles` subquery returns false).
   - PostgreSQL excludes the row from the update; **zero rows are matched (`rowcount = 0`)**.
   - SQLAlchemy detects rowcount 0 on an expected entity update and raises **`StaleDataError`** (or PostgreSQL raises `permission denied` if table-level UPDATE is absent).
   - The exception is caught at line 100 or line 129, `db.rollback()` is invoked, and the endpoint returns `HTTP 500`.

---

## 6. EXACT REGIONAL SIGNAL RLS POLICY COMPOSITION

Generated DDL emitted by `backend/app/database/rls.py:generate_table_rls_ddl("regional_signals")`:

```sql
-- Table: regional_signals (Collaborative Table with Scoped Security)
ALTER TABLE regional_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE regional_signals FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS regional_signals_public_read_policy ON regional_signals;
CREATE POLICY regional_signals_public_read_policy ON regional_signals
    AS PERMISSIVE
    FOR SELECT
    TO PUBLIC
    USING ((
        (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND current_setting('app.is_admin', true) = 'true')
        OR (
            distinct_farms_count >= 3
            AND validation_status != 'SUSPENDED'
        )
    ));

DROP POLICY IF EXISTS regional_signals_author_write_policy ON regional_signals;
CREATE POLICY regional_signals_author_write_policy ON regional_signals
    AS PERMISSIVE
    FOR ALL
    TO PUBLIC
    USING ((
        (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND current_setting('app.is_admin', true) = 'true')
        OR (
            current_setting('app.current_user_id', true) != ''
            AND EXISTS (
                SELECT 1 FROM user_roles ur
                WHERE ur.user_id::text = current_setting('app.current_user_id', true)
                AND ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')
            )
        )
    ))
    WITH CHECK ((
        (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND current_setting('app.is_admin', true) = 'true')
        OR (
            current_setting('app.current_user_id', true) != ''
            AND EXISTS (
                SELECT 1 FROM user_roles ur
                WHERE ur.user_id::text = current_setting('app.current_user_id', true)
                AND ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')
            )
        )
    ));
```

### Policy Characteristics
- **Read Policy:** Permissive `FOR SELECT`. Allows public read if `distinct_farms_count >= 3` and `validation_status != 'SUSPENDED'`.
- **Write Policy:** Permissive `FOR ALL`. Governs `SELECT`, `INSERT`, `UPDATE`, and `DELETE`.
- **Policy Combination:** Permissive policies are combined with logical `OR`. An UPDATE statement requires the write policy's `USING` clause to match the pre-update row and its `WITH CHECK` clause to match the post-update row.

---

## 7. `USER_ROLES` POLICY AND SUBQUERY DEPENDENCY ANALYSIS

The `EXISTS (SELECT 1 FROM user_roles ...)` subquery inside `regional_signals_author_write_policy` executes within PostgreSQL's security context during the UPDATE statement.

### RLS Policies on `user_roles`
`user_roles` is categorized as `USER_OWNED`:
```sql
CREATE POLICY user_roles_base_access_policy ON user_roles
    AS PERMISSIVE FOR ALL TO PUBLIC USING (true) WITH CHECK (true);

CREATE POLICY user_roles_user_isolation_policy ON user_roles
    AS RESTRICTIVE FOR ALL TO PUBLIC
    USING (
        (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') AND current_setting('app.is_admin', true) = 'true')
        OR user_id::text = current_setting('app.current_user_id', true)
    )
    WITH CHECK (
        (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') AND current_setting('app.is_admin', true) = 'true')
        OR user_id::text = current_setting('app.current_user_id', true)
    );
```

### Subquery Executability
- Because the restrictive policy on `user_roles` permits reading rows where `user_id::text = current_setting('app.current_user_id', true)`, and the subquery explicitly filters on `ur.user_id::text = current_setting('app.current_user_id', true)`, **the actor can read their own role assignment row**.
- **Privilege Dependency:** The database connection role (`acrevia_staging_app`) must possess table-level `SELECT` privilege on `user_roles`. In `PRIVILEGE_CROSSWALK`, `USER_OWNED` specifies `SELECT = True` (`CONDITIONAL_ON_DEPLOYED_GRANTS`).

---

## 8. GENERATED UPDATE GRANT SPECIFICATION

In `backend/app/database/rls.py:PRIVILEGE_CROSSWALK`:
- Table: `regional_signals`
- Category: `TableCategory.COMMUNITY_COLLABORATIVE`
- Permissions Specified for `acrevia_staging_app`:
  - `SELECT`: `True`
  - `INSERT`: `True`
  - `UPDATE`: `True`
  - `DELETE`: `False` (Denied to protect collaborative records)
  - `TRUNCATE`: `False`
  - `REFERENCES`: `False`
  - `TRIGGER`: `False`

Classification: **`GENERATED_GRANT_SPECIFICATION_PERMITS`**. The local specification intended for the application role to have `UPDATE` authority.

---

## 9. MIGRATION/BOOTSTRAP INVOCATION SEARCH RESULTS

A repository-wide search across all migrations, startup scripts, and deployment configurations reveals:
- Callsites of `generate_privilege_grants_ddl()`:
  1. `backend/app/database/rls.py:1040` (Definition)
  2. `backend/tests/test_worker_security_and_privacy.py:34` (Offline unit test)
- Callsites in Alembic Migrations (`backend/migrations/`): **ZERO**
- Callsites in Database Initialization (`backend/app/database/init_db.py`): **ZERO**
- Callsites in CI/CD Scripts (`.github/`, `scripts/`): **ZERO**

Classification: **`LOCALLY_SPECIFIED_NEVER_EXECUTED_IN_MIGRATIONS`**.

---

## 10. DEPLOYED ACL STATUS AND UNKNOWNS

Because `generate_privilege_grants_ddl()` is never invoked in migrations:
- It is **unknown** whether `acrevia_staging_app` was granted `UPDATE` on `regional_signals` in the live Neon staging database.
- It is **unknown** whether `acrevia_staging_app` was granted `SELECT` on `user_roles`.
- It is **unknown** whether table ownership or default cloud privileges apply.

Formal Status: **`LIVE_ACL_NOT_VERIFIED`**. The statement that a live commit succeeds is **conditional on unknown deployment state**.

---

## 11. ORM MUTATION AND SAVEPOINT LIFECYCLE

In `RegionalPulseService.revalidate_signal_provenance()`:
```python
with db.begin_nested():
    ...
    signal.distinct_farms_count = current_count
    if current_count < MINIMUM_DISTINCT_FARMS_THRESHOLD:
        signal.validation_status = "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        return False
    return True
```

### Savepoint Mechanics
1. `db.begin_nested()` issues `SAVEPOINT sa_savepoint_1`.
2. `db.get(Observation, ...)` returns `None` due to RLS row filtering.
3. No SQL exception occurs; the Python context manager exits normally.
4. SQLAlchemy issues `RELEASE SAVEPOINT sa_savepoint_1`.
5. The mutations on the `signal` ORM instance remain in the `Session` identity map as **dirty state**.
6. When the endpoint executes `db.commit()`, SQLAlchemy initiates a unit-of-work flush, emitting the SQL `UPDATE` statement.

---

## 12. FARMER UPDATE DENIAL SEMANTICS AND UNVERIFIED EXCEPTION HANDLING

When an ordinary farmer triggers the read endpoint:
1. `signal.distinct_farms_count = 0` is staged in memory.
2. The outer route calls `db.commit()`.
3. SQLAlchemy flushes `UPDATE regional_signals SET distinct_farms_count = 0, validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE' WHERE id = :id`.
4. In PostgreSQL, because the farmer fails the `USING` clause of `regional_signals_author_write_policy`, the row is filtered out from the update:
   - **PostgreSQL does NOT throw an RLS check violation on the `USING` clause.**
   - Instead, the UPDATE executes and matches **zero rows (`UPDATE 0`)**.
5. SQLAlchemy ORM inspects the returned rowcount (0) vs expected rowcount (1) and raises:
   ```
   sqlalchemy.orm.exc.StaleDataError: UPDATE statement on table 'regional_signals' expected to update 1 row(s); 0 were matched.
   ```
6. If the application role lacks table-level `UPDATE` privilege, PostgreSQL raises:
   ```
   psycopg2.errors.InsufficientPrivilege: permission denied for table regional_signals
   ```
7. In either case, the outer route's `except Exception:` catches the error, calls `db.rollback()`, and raises `HTTP 500`.

Classification: **`EXACT_LIVE_EXCEPTION_NOT_VERIFIED`**. The assertion that an "RLS check violation" occurs is incorrect; the actual failure is either an ORM rowcount mismatch (`StaleDataError`) or a table privilege denial.

---

## 13. SUBSEQUENT-READ VISIBILITY AFTER A HYPOTHETICAL SUCCESSFUL SUPPRESSION COMMIT

If the mutation commits to the database:
- `distinct_farms_count = 0`
- `validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'`

### Subsequent Read Query
A subsequent `GET /api/v1/regional-pulse/signals` executes:
```sql
SELECT * FROM regional_signals WHERE ...;
```
PostgreSQL applies `regional_signals_public_read_policy`:
```sql
USING (
    {ADMIN_BYPASS_SQL}
    OR (
        distinct_farms_count >= 3
        AND validation_status != 'SUSPENDED'
    )
)
```
- Because `distinct_farms_count` is 0, `distinct_farms_count >= 3` evaluates to **FALSE**.
- PostgreSQL silently excludes the row from the result set (`RLS_FILTERS_ROW`).
- The signal becomes **persistently suppressed from ordinary public visibility**.
- **Reversibility:** The signal can still be seen by administrators under `ADMIN_BYPASS_SQL` and can be restored via `RegionalPulseService.recover_suppressed_signal()`. It is **not irreversible**.

---

## 14. CORRECTED EXPERTCONNECT CLASSIFICATION AND ROUTE MATRIX

### 14.1 Table Classification Corrections
The previous report incorrectly labeled ExpertConnect tables as `TENANT_COLLABORATIVE`. The authoritative classifications in `backend/app/database/rls.py` are:

| Table Name | True Category | Direct Column / Foreign Key Parent | RLS Isolation Model |
|---|---|---|---|
| `expert_review_cases` | **`TENANT_DIRECT`** | `column = 'farm_id'` | `farm_id = app.current_tenant_id` |
| `expert_assessments` | **`TENANT_INDIRECT`** | `parent_table = 'expert_review_cases'`, `fk = 'case_id'` | Subquery on `case_id` $\rightarrow$ `farm_id = app.current_tenant_id` |
| `expert_assessment_revisions` | **`TENANT_INDIRECT`** | `parent_table = 'expert_assessments'`, `fk = 'assessment_id'` | Nested subquery $\rightarrow$ `farm_id = app.current_tenant_id` |
| `expert_reviews` | **`TENANT_INDIRECT`** | `parent_table = 'diagnosis_requests'`, `fk = 'diagnosis_request_id'` | Subquery $\rightarrow$ `farm_id = app.current_tenant_id` |

### 14.2 Corrected Route Dependency and Reachability Matrix

| Route Path & Method | Authentication | Role Dependency in Route | Service Guard / Lookups | Generated RLS Result under Standard Context (`app.current_tenant_id = ''`) | Final Determination |
|---|---|---|---|---|---|
| `GET /api/v1/expertconnect/cases` | `get_current_user` | **`require_roles(AGRICULTURAL_EXPERT, ADMIN)`** | `ExpertConnectService.list_cases()` | `RLS_FILTERS_ROW` (`expert_review_cases` requires `farm_id = ''`) | `APPLICATION_ROLE_GATE_PASSES` / `RLS_FILTERS_ROW` (Returns `[]`) |
| `POST /api/v1/expertconnect/cases/{id}/claim` | `get_current_user` | `require_roles(AGRICULTURAL_EXPERT, ADMIN)` | `db.get(ExpertReviewCase, id)` | `RLS_FILTERS_ROW` (Lookup returns `None`) | `SERVICE_GUARD_BLOCKS` (Raises 404) |
| `GET /api/v1/expertconnect/cases/{id}` | `get_current_user` | *None (Auth-Only)* | `db.get(ExpertReviewCase, id)` | `RLS_FILTERS_ROW` (Lookup returns `None`) | `RLS_FILTERS_ROW` (Raises 404) |
| `POST /api/v1/expertconnect/cases/{id}/assess` | `get_current_user` | `require_roles(AGRICULTURAL_EXPERT, ADMIN)` | `db.get(ExpertReviewCase, id)` | `RLS_FILTERS_ROW` (Lookup returns `None`) | `SERVICE_GUARD_BLOCKS` (Raises 404) |
| `PUT /api/v1/expertconnect/cases/{id}/assess` | `get_current_user` | `require_roles(AGRICULTURAL_EXPERT, ADMIN)` | `db.get(ExpertAssessment, id)` | `RLS_FILTERS_ROW` (Lookup returns `None`) | `SERVICE_GUARD_BLOCKS` (Raises 404) |
| `GET /api/v1/expertconnect/cases/{id}/revisions` | `get_current_user` | *None (Auth-Only)* | Queries revisions | `RLS_FILTERS_ROW` (Child rows filtered) | `RLS_FILTERS_ROW` (Returns `[]`) |
| `POST /api/v1/expertconnect/cases/create-from-observation/{id}` | `get_current_user` | *None (Auth-Only)* | `db.get(Observation, id)` | `RLS_FILTERS_ROW` (Observation filtered) | `SERVICE_GUARD_BLOCKS` (Raises 404) |
| `POST /api/v1/diagnoses/{id}/expert-review` | `get_current_user` | `require_roles(AGRICULTURAL_EXPERT)` | `db.get(DiagnosisRequest, id)` | `RLS_FILTERS_ROW` (Diagnosis filtered) | `SERVICE_GUARD_BLOCKS` (Raises 404) |

> [!CRITICAL]
> **Architectural Breakdown:** Because `expert_review_cases` is classified as `TENANT_DIRECT` (`farm_id`), and expert endpoints do not (and cannot) set a single farm tenant context during multi-farm case triage, **the entire ExpertConnect subsystem fails closed under standard RLS tenant isolation**. Experts see zero cases and cannot claim or assess cases unless running under an administrative bypass.

---

## 15. EXACT REGIONALSIGNALEVIDENCE SERIALIZATION FIELDS

Inspection of [`backend/app/models/regional_pulse.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/regional_pulse.py#L90-L115) and [`backend/app/schemas/regional_pulse.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/schemas/regional_pulse.py#L42-L50) confirms:

### ORM Model: `RegionalSignalEvidence`
- `id`: `String(36)` (UUID)
- `signal_id`: `String(36)` (Foreign Key to `regional_signals.id`)
- `evidence_type`: `String(50)` (`OBSERVATION_REF`, `RISKCAST_ALERT`, `EXPERT_CASE_REF`, `SATELLITE_INDEX`)
- `evidence_reference_id`: `String(100)`
- `evidence_notes`: `Text` (Nullable)
- **`added_at`**: `DateTime(timezone=True)` (**Confirmed: `added_at`, NOT `created_at`**)

### Response Schema: `RegionalSignalEvidenceItem`
```python
class RegionalSignalEvidenceItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    evidence_type: str
    evidence_reference_id: str
    evidence_notes: Optional[str] = None
    added_at: datetime
```

- Schema Name: **`RegionalSignalEvidenceItem`** (NOT `RegionalSignalEvidenceResponse`).
- Serialized Properties: Exactly 5 fields (`id`, `evidence_type`, `evidence_reference_id`, `evidence_notes`, `added_at`).
- `signal_id` is omitted from the item schema because it is embedded inside [`RegionalSignalResponse.evidences`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/schemas/regional_pulse.py#L75).
- Raw farmer observations, plot geometries, sensor telemetries, and farm PII are **completely absent** from this response structure.

---

## 16. KNOWLEDGE INGESTION ORDERED WRITE-PATH ASSESSMENT

In [`backend/app/services/knowledge/ingestion/ingestion_service.py:106-130`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/knowledge/ingestion/ingestion_service.py#L106-L130):
```python
# Step 1:
doc = KnowledgeDocument(...)
db.add(doc)
db.flush()

# Step 2:
doc_version = KnowledgeDocumentVersion(...)
db.add(doc_version)
db.flush()

# Step 3:
job = IngestionJob(...)
db.add(job)
db.commit()
```

### Multi-Layer Assessment
1. **Step 1 (`knowledge_documents`):** Classified as `SHARED_REFERENCE` (`PUBLIC_REFERENCE`).
   - `PRIVILEGE_CROSSWALK` specifies `can_insert = False` (SELECT only for `acrevia_staging_app`).
   - Generated RLS write policy requires `{ADMIN_BYPASS_SQL}`.
   - When `db.flush()` executes at line 107, execution is blocked by `TABLE_GRANT_BLOCKS` (generated prediction) or `RLS_WITH_CHECK_BLOCKS_WRITE`.
2. **Step 3 (`ingestion_jobs`):** Classified as `SHARED_REFERENCE` (`PRIVATE_OPERATIONAL`).
   - Generated RLS write policy permits role-bearing actors (`ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER`).
3. **Conclusion:** The role-based write policy on `ingestion_jobs` is **unreachable** via `POST /api/v1/knowledge/ingest` because Step 1 flushes and aborts prior to Step 3.
4. **Deployment Qualification:** Whether Step 1 fails with `permission denied` or an RLS check violation on a live server remains `LIVE_ACL_NOT_VERIFIED`.

---

## 17. CORRECTED ROUTE-COUNT RESULTS

An independent AST scan using the standard library `ast` module independently proves:
- **Total Endpoint Router Files:** Exactly **49 modules** in `backend/app/api/v1/endpoints/*.py` (excluding `__init__.py`).
- **Total Master Mounted Routers:** All 49 modules are mounted in `backend/app/api/v1/router.py`.
- **Total Version-One Routes:** Exactly **214 routes**.
- **Unique (Method, Full Path) Combinations:** Exactly **214 unique endpoints** (zero duplicates).
- **Root Diagnostic Endpoints in `backend/app/main.py`:** Exactly **3 routes** (`GET /health`, `GET /ready`, `GET /`).
- **Total FastAPI Application Endpoints:** Exactly **217 endpoints**.

The prior count of 212 omitted [`POST /register`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/auth.py#L48) and [`POST /login`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/auth.py#L55) because of regex failure on multi-line decorators. The AST count of 214 is 100% verified.

---

## 18. CORRECT CREDENTIAL-SOURCE PATH

- **Correct File Location:** [`frontend/lib/server/db.ts`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/lib/server/db.ts#L8-L11) (specifically within the `server/` subdirectory, NOT `frontend/lib/db.ts`).
- **Fallback Code:**
  ```typescript
  const dbUrl =
    process.env.DATABASE_URL ||
    "postgresql://neondb_owner:***@ep-muddy-mode-a1nd6rrb-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require";
  ```
- **Service Using Helper:** Frontend Next.js server-side database helper (`getDb()`).
- **Selection Condition:** Selected only if `process.env.DATABASE_URL` is undefined or empty.
- **Deployed Use:** `UNKNOWN` in Mode A (environment variables of deployed container cannot be inspected).
- **Incident Status:** `DB-CREDENTIAL-EXPOSURE-01` remains **OPEN — CREDENTIAL_ROTATION_OUTSTANDING**.

---

## 19. FULL BLOCKER-REGISTER RECONCILIATION

| Identifier | Severity | Governance Category | Current Disposition | Evidence Level | Release Status |
|---|---|---|---|---|---|
| `DB-CREDENTIAL-EXPOSURE-01` | **CRITICAL** | Cloud Security | **OPEN** | `SOURCE_CONFIRMED` | **RELEASE BLOCKER** (`GATE-01`) |
| `RLS-WRITE-AUTH-01` | **HIGH** | PostgreSQL RLS Architecture | **OPEN — OPTION D PLANNED** | `POLICY_GENERATOR_CONFIRMED` | **RELEASE BLOCKER** (`GATE-02`) |
| `RLS-ROLE-ASSIGNMENT-01` | **HIGH** | PostgreSQL Role Management | **OPEN — OPTION B PLANNED** | `SOURCE_CONFIRMED` | **RELEASE BLOCKER** (`GATE-02`) |
| `APP-ROLE-SELF-SELECT-01` | **HIGH** | Application Authentication Gateway | **OPEN — RESTRICTION REQUIRED** | `SOURCE_CONFIRMED` | **RELEASE BLOCKER** (`GATE-02`) |
| `RES-PULSE-READ-01` | **HIGH** | Data Integrity / Denial-of-Service | **OPEN — MUTATION CONFIRMED** | `ORM_MUTATION_STAGED` | **RELEASE BLOCKER** (`GATE-02`) |
| `TENANT-MEMBERSHIP-01` | **HIGH** | Tenant Context Resolution | **OPEN — EMPTY CONTEXT BREAKS TRIAGE** | `STATIC_TRANSACTION_PATH_CONFIRMED` | **RELEASE BLOCKER** (`GATE-02`) |
| `DB-RLS-01` | **HIGH** | RLS Entity Model Alignment | **OPEN — EXPERT CASES MISCLASSIFIED** | `POLICY_GENERATOR_CONFIRMED` | **RELEASE BLOCKER** (`GATE-02`) |
| `GATE01-PROV-01` | **MEDIUM** | Migration / Privilege Provisioning | **OPEN — CALLSITE ABSENT** | `SOURCE_CONFIRMED` | **RELEASE BLOCKER** (`GATE-01`) |
| `EXP-AUTH-01` | **MEDIUM** | Expert Authorization / Accreditation | **OPEN — ACCREDITATION DECOUPLED** | `SOURCE_CONFIRMED` | **RELEASE BLOCKER** (`GATE-03`) |
| `RES-PULSE-02` | **MEDIUM** | Aggregation Service Guard | **OPEN — 3-FARM THRESHOLD FAILS** | `STATIC_TRANSACTION_PATH_CONFIRMED` | **RELEASE BLOCKER** (`GATE-02`) |
| `OWNER-AUTH-01` | **MEDIUM** | Administrative RLS Bypass | **OPEN — HARDCODED VENDOR IDENTITY** | `SOURCE_CONFIRMED` | **RELEASE BLOCKER** (`GATE-01`) |
| `CASCADE-ROLE-DEL-01` | **MEDIUM** | Relational Schema Integrity | **MONITORED RESIDUAL RISK** | `SOURCE_CONFIRMED` | Residual Risk (Requires Arbitrary SQL) |
| `WRK-DISP-01` | **MEDIUM** | Background Worker Security | **MONITORED RESIDUAL RISK** | `SOURCE_CONFIRMED` | Residual Risk |
| `RES-PULSE-01` | **LOW** | Collaborative Privacy Boundary | **MONITORED RESIDUAL RISK** | `SOURCE_CONFIRMED` | Residual Risk (Metadata Visible) |
| `RES-PULSE-READ-PERSIST-01` | **HIGH** | Write-on-Read Persistence | **RECONCILED UNDER RES-PULSE-READ-01** | `CONDITIONAL_ON_DEPLOYED_GRANTS` | Governed under `RES-PULSE-READ-01` |

---

## 20. CANONICAL GOVERNANCE AND GATE STATUS

- **Preservation of Canonical Architecture Decisions:**
  - `D-01` (Regional Signal Visibility & Official Advisory Data Model): Preserved.
  - `D-02` (Source Authenticity & Pilot Terminology): Preserved.
  - `D-03` (Independent Expert Review): Preserved.
  - `DB-AUTH-01` (Trusted Database Writer Identity): Preserved.
- **Release Gate Status:**
  - `GATE-01` (Database Infrastructure & Credential Assurance): **BLOCKED**
  - `GATE-02` (PostgreSQL RLS Kernel Isolation & Policy Composition): **BLOCKED**
  - `GATE-03` (Application Authentication & Role Provisioning Gateway): **BLOCKED**
  - `GATE-04` (Offline & Integration Test Verification): **BLOCKED**
  - `GATE-05` (Mode B Authorization & Production Release): **BLOCKED**
- **Formal Phase 07 Status:** **`NOT RELEASED`**.
- **Execution Authorization:** **`MODE A ONLY — MODE B NOT AUTHORIZED`**.

---

## 21. REMEDIATION DESIGN RECOMMENDATIONS (WITHOUT IMPLEMENTATION)

1. **Decouple Dynamic Revalidation from HTTP GET Routes (`RES-PULSE-READ-01`):**  
   Remove `revalidate_signal_provenance()` and `db.commit()` from `list_signals` and `get_signal`. Revalidation must be executed asynchronously via background worker or performed as an in-memory filter without committing state changes to the database.
2. **Reclassify ExpertConnect Entities (`DB-RLS-01` / `TENANT-MEMBERSHIP-01`):**  
   Transition `expert_review_cases` from `TENANT_DIRECT` to a dedicated collaborative or triaged category where verified experts can query cross-tenant cases without requiring a single tenant context.
3. **Deploy Option D Command-Specific Policies:**  
   Replace `regional_signals_author_write_policy` (`FOR ALL`) with separate `FOR INSERT` and `FOR UPDATE` policies, strictly prohibiting general UPDATE permissions on published signals.
4. **Integrate Privilege Grants into Alembic Migrations (`GATE01-PROV-01`):**  
   Incorporate `generate_privilege_grants_ddl()` into Alembic revision scripts.
5. **Rotate Neon Cloud Credentials (`DB-CREDENTIAL-EXPOSURE-01`):**  
   Rotate the exposed credential via the Neon console, purge Git history, and verify container environment variables.

---

## 22. REQUIRED FINAL DETERMINATION MATRIX

| Question | Source Finding | Grant/Policy Condition | Live Evidence | Final Result |
|---|---|---|---|---|
| **Does GET call provenance revalidation?** | `SOURCE_PATH_CONFIRMED` (lines 86, 125) | None (Python execution) | None required | **`YES (SOURCE_PATH_CONFIRMED)`** |
| **Can revalidation stage a signal mutation?** | `ORM_MUTATION_STAGED` (lines 339, 376) | Underlying lookups return None | None required | **`YES (ORM_MUTATION_STAGED)`** |
| **Can empty tenant context hide underlying evidence?** | `STATIC_TRANSACTION_PATH_CONFIRMED` (`app.current_tenant_id = ''`) | `CONDITIONAL_ON_DEPLOYED_RLS` | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`YES (CONDITIONAL_ON_DEPLOYED_RLS)`** |
| **Can an expert satisfy the generated update predicate?** | `POLICY_PREDICATE_MATCHES` (`user_roles` subquery matches) | `CONDITIONAL_ON_DEPLOYED_RLS` | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`YES (POLICY_PREDICATE_MATCHES)`** |
| **Is the `user_roles` RLS subquery executable?** | `POLICY_GENERATOR_CONFIRMED` (User can read own roles) | `CONDITIONAL_ON_DEPLOYED_GRANTS` (SELECT on `user_roles`) | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`YES (CONDITIONAL_ON_DEPLOYED_GRANTS)`** |
| **Does the generated grant specification include UPDATE?** | `SOURCE_CONFIRMED` (`PRIVILEGE_CROSSWALK` sets UPDATE=True) | Local Python specification | None | **`YES (GENERATED_GRANT_SPECIFICATION_PERMITS)`** |
| **Is the UPDATE grant deployed?** | `LOCALLY_SPECIFIED_NEVER_EXECUTED_IN_MIGRATIONS` | Unknown external DBA grants | `LIVE_ACL_NOT_VERIFIED` | **`UNKNOWN (LIVE_ACL_NOT_VERIFIED)`** |
| **Can the outer GET commit persist the mutation?** | `STATIC_TRANSACTION_PATH_CONFIRMED` (`db.commit()` called) | `CONDITIONAL_ON_DEPLOYED_GRANTS` & RLS | `LIVE_COMMIT_NOT_VERIFIED` | **`CONDITIONAL (LIVE_COMMIT_NOT_VERIFIED)`** |
| **Does a subsequent read hide the suppressed signal?** | `POLICY_PREDICATE_MATCHES` (`distinct_farms_count >= 3` fails) | `CONDITIONAL_ON_DEPLOYED_RLS` | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`YES (PERSISTENTLY_SUPPRESSED_FROM_ORDINARY_VISIBILITY)`** |
| **Does a farmer UPDATE fail with the claimed exact exception?** | `SOURCE_CONFIRMED` (Row filtered at `USING`, rowcount=0) | SQLAlchemy `StaleDataError` or grant error | `EXACT_LIVE_EXCEPTION_NOT_VERIFIED` | **`NO / UNVERIFIED (EXACT_LIVE_EXCEPTION_NOT_VERIFIED)`** |
| **Can case listing read tenant-direct cases with empty tenant context?** | `SOURCE_CONFIRMED` (`expert_review_cases` is `TENANT_DIRECT`) | `farm_id = ''` fails for all cases | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`NO (RLS_FILTERS_ROW / EMPTY_RESULT)`** |
| **Can assessment writes reach the service guard?** | `STATIC_TRANSACTION_PATH_CONFIRMED` (Parent case lookup fails) | `expert_review_cases` filtered by RLS | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`NO (SERVICE_GUARD_UNREACHABLE / 404)`** |
| **Does the knowledge ingestion path reach its job insert?** | `STATIC_TRANSACTION_PATH_CONFIRMED` (Step 1 doc flush aborts) | `TABLE_GRANT_BLOCKS` / `RLS_WITH_CHECK_BLOCKS_WRITE` | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`NO (BLOCKED_AT_STEP_1_FLUSH)`** |
| **Is the frontend credential fallback active in deployment?** | `SOURCE_CONFIRMED` (`frontend/lib/server/db.ts:9-10`) | Depends on `process.env.DATABASE_URL` | `UNKNOWN (DEPLOYED_ENV_NOT_INSPECTABLE)` | **`UNKNOWN (DEPLOYED_USE_UNVERIFIED)`** |

---

## 23. EXACT INSPECTED SOURCE INVENTORY AND FINAL WORKING-TREE STATUS

### Inspected Files
- `backend/app/api/v1/router.py` (Master Router Assembly)
- `backend/app/api/v1/endpoints/regional_pulse.py` (Lines 67-150: GET signal routes & `db.commit()`)
- `backend/app/services/regional_pulse_service.py` (Lines 295-390: `revalidate_signal_provenance` & savepoint)
- `backend/app/models/regional_pulse.py` (Lines 90-115: `RegionalSignalEvidence` & `added_at`)
- `backend/app/schemas/regional_pulse.py` (Lines 42-50: `RegionalSignalEvidenceItem`)
- `backend/app/database/rls.py` (Lines 40-75, 895-970, 975-1040: `TABLE_CLASSIFICATION`, `PRIVILEGE_CROSSWALK`, policy DDL)
- `backend/app/api/v1/endpoints/expertconnect.py` (Lines 98-150: ExpertConnect routes & `@require_roles`)
- `backend/app/services/expertconnect/expert_service.py` (Lines 15-60: `list_cases` implementation)
- `backend/app/api/v1/endpoints/knowledge.py` (Knowledge endpoints)
- `backend/app/services/knowledge/ingestion/ingestion_service.py` (Lines 80-145: Ordered write flushes)
- `backend/migrations/versions/a1089411c87d_phase_07_rls_policies.py` (Alembic RLS policy migration)
- `frontend/lib/server/db.ts` (Lines 1-15: Database helper & Neon URI fallback)

### Working Tree Verification
- Source, ORM, schema, service, migration, and test files modified: **`0 files`**.
- Existing audit documents overwritten or modified: **`0 files`**.
- Single new report created: `docs/pilot/security/PHASE_07_WRITE_ON_READ_PERSISTENCE_AND_ROUTE_CLASSIFICATION_CORRECTIVE_ASSURANCE_REPORT.md`.
