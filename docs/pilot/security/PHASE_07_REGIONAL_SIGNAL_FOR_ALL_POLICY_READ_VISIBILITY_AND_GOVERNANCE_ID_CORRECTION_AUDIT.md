# ACREVIA — PHASE 07: COMMAND-SCOPE RLS POLICY COMPOSITION, POST-SUPPRESSION READ VISIBILITY & GOVERNANCE REGISTER CORRECTIVE ASSURANCE AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** MODE A ONLY — Offline Source Inspection, Static PostgreSQL Policy Modeling, ORM Transaction Analysis & Governance Documentation  
**Methodology:** Everything Claude Code (ECC) — `PLAN → INSPECT → MODEL → ADVERSARIAL REVIEW → VERIFY → DOCUMENT`  
**Public Repository:** `https://github.com/gokul1599/ACREVIA`  
**Verified Baseline:** Commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Prior Deliverables Preserved:**  
- `docs/pilot/security/PHASE_07_REGIONAL_PULSE_SERVICE_REACHABILITY_AND_POLICY_COMPOSITION_AUDIT.md`  
- `docs/pilot/security/PHASE_07_WRITE_ON_READ_PERSISTENCE_AND_ROUTE_CLASSIFICATION_CORRECTIVE_ASSURANCE_REPORT.md`  
**Audit Status:** COMPLETE — FORMAL GOVERNANCE CORRECTIVE AUDIT  
**Classification:** STRICTLY CONFIDENTIAL — AGRICULTURAL SECURITY & REGIONAL GOVERNANCE  

---

## 1. EXECUTIVE DETERMINATION

### Overall Audit Determination: `FOR_ALL_POLICY_PERMITS_PRIVILEGED_SELECT_POST_SUPPRESSION_VISIBILITY_CONFIRMED_FOR_EXPERTS`

Following exhaustive command-by-command SQL policy modeling and cross-layer transaction evaluation against PostgreSQL row-level security semantics, this corrective audit establishes:

1. **`FOR ALL` Command Scope Extends to SELECT (`POLICY_COMMAND_SCOPE_CONFIRMED` / `FOR_ALL_APPLIES_TO_SELECT`):**  
   In PostgreSQL kernel architecture, a policy defined with `FOR ALL` applies to all SQL commands (`SELECT`, `INSERT`, `UPDATE`, `DELETE`). The policy [`regional_signals_author_write_policy`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L962-L968) is generated `AS PERMISSIVE FOR ALL TO PUBLIC`. Consequently, its `USING` expression is evaluated on `SELECT` statements as well as mutations.

2. **Permissive Policy OR-Composition Preserves Privileged Visibility (`PERMISSIVE_POLICY_OR_COMPOSITION` / `ROLE_BEARING_SELECT_POSSIBLE`):**  
   PostgreSQL combines multiple permissive policies applicable to `SELECT` using logical `OR`. On `regional_signals`, the effective read predicate is:
   $$\text{Effective SELECT} = (\text{public\_read\_policy USING}) \lor (\text{author\_write\_policy USING})$$
   When a signal's verified farm count drops to zero (`distinct_farms_count = 0`), the public read condition (`distinct_farms_count >= 3`) evaluates to `FALSE`. However, for role-bearing actors (`ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER`), the `author_write_policy` `USING` clause evaluates to `TRUE` via the subquery on `user_roles`. Because $\text{FALSE} \lor \text{TRUE} = \text{TRUE}$, **role-bearing experts and researchers can still SELECT and read the suppressed signal directly from the database**.

3. **Public Read Denial Bounded to Ordinary Farmers and Unauthenticated Actors (`PUBLIC_THRESHOLD_READ_BLOCKED`):**  
   Ordinary farmers and unauthenticated callers fail both the public read condition and the `user_roles` role check. For these actors, $\text{FALSE} \lor \text{FALSE} = \text{FALSE}$. The row is filtered out by PostgreSQL RLS (`RLS_FILTERS_ROW`). The statement in prior reports that a suppressed signal becomes "hidden from all ordinary visibility" is corrected: **the signal is hidden from ordinary farmers and public consumers, but remains fully visible to role-bearing experts, researchers, and administrators**.

4. **API Response Logic Symmetrically Preserves Privileged Retrieval (`SOURCE_CONFIRMED`):**  
   In [`backend/app/api/v1/endpoints/regional_pulse.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/regional_pulse.py#L80-L95), the check `and not is_privileged` explicitly ensures that privileged roles bypass response-level suppression filtering and 404 aborts on both the initial request and all subsequent GET requests.

5. **Persistence of the Write-on-Read Mutation Remains Conditional (`CONDITIONAL_ON_DEPLOYED_GRANTS` / `LIVE_COMMIT_NOT_VERIFIED`):**  
   While the ORM mutation is staged in Python memory and the generated policy allows UPDATE, `generate_privilege_grants_ddl()` is never executed by Alembic migrations or startup scripts. Deployed table privileges remain `LIVE_ACL_NOT_VERIFIED`. A live database commit has not been verified in Mode A.

6. **Restoration of Canonical Governance Identifiers:**  
   This audit formally restores the canonical meanings of all 15 blocker identifiers:
   - `OWNER-AUTH-01`: Formal Project Owner decisions and Mode B execution authorization remain pending.
   - `DB-RLS-01`: Physical PostgreSQL RLS kernel enforcement, FORCE RLS, and catalog validation remain unverified.
   - `GATE01-PROV-01`: Neon staging branch status recorded in local artifacts remains unverified live.
   - `RES-PULSE-01`: Role-global evidence association visibility without district scoping (residual risk).
   - `RES-PULSE-02`: READ COMMITTED multi-statement snapshot/concurrency window (residual risk).
   - `DB-GRANT-APPLY-01`: New proposed blocker for the unexecuted privilege grant DDL generator (`PROPOSED — OWNER APPROVAL REQUIRED`).

---

## 2. EXACT REPOSITORY BASELINE

- **Inspected Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`HEAD` -> `main`, `origin/main`).
- **Public Baseline Match:** Matches `origin/main` commit exactly.
- **Working Tree Integrity:** All previous audit deliverables are preserved intact. Zero modifications to application source code, ORM models, schemas, services, migrations, or tests.
- **Mode A Execution:** Strictly offline inspection, static policy parsing, and transaction modeling. No remote database connection or SQL execution occurred.

---

## 3. EVIDENCE CLASSIFICATION LEGEND

Every material finding in this audit carries one or more of the following standardized evidence tiers:

1. `SOURCE_CONFIRMED` — Verified directly in application source code.
2. `POLICY_GENERATOR_CONFIRMED` — Verified in the SQL generated by `backend/app/database/rls.py`.
3. `POLICY_COMMAND_SCOPE_CONFIRMED` — Verified by PostgreSQL command-scoping rules under SQL standard/PostgreSQL engine specifications.
4. `ORM_MUTATION_STAGED` — Verified by tracing attribute assignment in SQLAlchemy Session identity maps.
5. `STATIC_TRANSACTION_PATH_CONFIRMED` — Verified by tracing service call sequences and transaction boundaries.
6. `ORM_BEHAVIOR_INFERRED` — Inferred from documented SQLAlchemy unit-of-work mechanics.
7. `OFFLINE_TEST_CONFIRMED` — Verified by offline mocked unit tests without external connectivity.
8. `CONDITIONAL_ON_DEPLOYED_GRANTS` — Dependent on actual PostgreSQL table privileges granted on the database.
9. `CONDITIONAL_ON_DEPLOYED_RLS` — Dependent on active PostgreSQL row-level security policies on the target table.
10. `CONDITIONAL_ON_EFFECTIVE_DB_PRINCIPAL` — Dependent on the effective PostgreSQL role attributes (`BYPASSRLS`, superuser, owner).
11. `LIVE_POSTGRESQL_NOT_VERIFIED` — Unverifiable without live database access (strictly prohibited in Mode A).
12. `LIVE_COMMIT_NOT_VERIFIED` — Physical persistence unverified without live execution evidence.

---

## 4. EXACT GENERATED `regional_signals` DDL

From [`backend/app/database/rls.py:899-970`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L899-L970):

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

---

## 5. EXACT GENERATED `regional_signal_evidences` DDL

From [`backend/app/database/rls.py:909-970`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L909-L970):

```sql
-- Table: regional_signal_evidences (Collaborative Table with Scoped Security)
ALTER TABLE regional_signal_evidences ENABLE ROW LEVEL SECURITY;
ALTER TABLE regional_signal_evidences FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS regional_signal_evidences_public_read_policy ON regional_signal_evidences;
CREATE POLICY regional_signal_evidences_public_read_policy ON regional_signal_evidences
    AS PERMISSIVE
    FOR SELECT
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
    ));

DROP POLICY IF EXISTS regional_signal_evidences_author_write_policy ON regional_signal_evidences;
CREATE POLICY regional_signal_evidences_author_write_policy ON regional_signal_evidences
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

---

## 6. `FOR ALL` COMMAND-SCOPE EXPLANATION

### PostgreSQL Engine Specification
- Under PostgreSQL documentation (Section 5.8 "Row Security Policies"):
  "The command to which the policy applies. Valid commands are ALL, SELECT, INSERT, UPDATE, and DELETE. ALL is the default... Using ALL for a policy means that it will apply to all commands, regardless of the type of command."
- The `USING` clause of a `FOR ALL` policy is evaluated for **every command that reads rows**—namely `SELECT`, `UPDATE` (which reads the current row before updating), and `DELETE` (which reads the row before deleting).
- A policy named `author_write_policy` does **not** restrict its operation to write operations if its SQL definition uses `FOR ALL`. PostgreSQL does not inspect English words in policy identifiers; it executes strictly according to the specified command keyword.
- Because `regional_signals_author_write_policy` declares `FOR ALL`, **it is actively evaluated by PostgreSQL for SELECT queries**.

---

## 7. POSTGRESQL PERMISSIVE / RESTRICTIVE POLICY COMPOSITION

PostgreSQL RLS applies two composition rules:
1. **Permissive Policies (`AS PERMISSIVE`):** When multiple permissive policies apply to the same command on a table, they are combined with **logical `OR`**. If any one permissive policy permits access, access is granted.
2. **Restrictive Policies (`AS RESTRICTIVE`):** When restrictive policies apply, they are combined with **logical `AND`**, and all must pass.

On `regional_signals`:
- `regional_signals_public_read_policy` is `AS PERMISSIVE FOR SELECT`.
- `regional_signals_author_write_policy` is `AS PERMISSIVE FOR ALL`.
- Zero restrictive policies are defined on `regional_signals`.

Therefore, for any `SELECT` query on `regional_signals`, the effective database predicate is:

$$\text{SELECT Filter} = \text{read\_expr} \lor \text{write\_expr}$$

---

## 8. ACTOR-BY-ACTOR SELECT MATRIX

| Actor Class | Public Read Policy (`distinct_farms >= 3`) | `FOR ALL` Write Policy (`user_roles` Subquery) | Permissive Combination (`OR`) | Final PostgreSQL SELECT Result |
|---|---|---|---|---|
| **ADMIN** | Passes via `ADMIN_BYPASS_SQL` (`TRUE`) | Passes via `ADMIN_BYPASS_SQL` / role check (`TRUE`) | $\text{TRUE} \lor \text{TRUE} = \text{TRUE}$ | **`ROLE_BEARING_SELECT_POSSIBLE`** |
| **AGRICULTURAL_EXPERT** | Fails when count < 3 (`FALSE`) | Passes via `role_id = 'AGRICULTURAL_EXPERT'` (`TRUE`) | $\text{FALSE} \lor \text{TRUE} = \text{TRUE}$ | **`ROLE_BEARING_SELECT_POSSIBLE`** |
| **RESEARCHER** | Fails when count < 3 (`FALSE`) | Passes via `role_id = 'RESEARCHER'` (`TRUE`) | $\text{FALSE} \lor \text{TRUE} = \text{TRUE}$ | **`ROLE_BEARING_SELECT_POSSIBLE`** |
| **FARMER** | Fails when count < 3 (`FALSE`) | Fails (`role_id` is `'FARMER'`) (`FALSE`) | $\text{FALSE} \lor \text{FALSE} = \text{FALSE}$ | **`PUBLIC_THRESHOLD_READ_BLOCKED`** |
| **Unauthenticated** | Fails when count < 3 (`FALSE`) | Fails (`current_user_id` is empty) (`FALSE`) | $\text{FALSE} \lor \text{FALSE} = \text{FALSE}$ | **`PUBLIC_THRESHOLD_READ_BLOCKED`** |

---

## 9. POST-SUPPRESSION VISIBILITY ANALYSIS

Under the hypothesis that a write-on-read revalidation commits to the database, setting `distinct_farms_count = 0` and `validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'`:

### Visibility Breakdown by Consumer Category
1. **Public Consumers & Ordinary Farmers:**  
   - Denied SELECT access by PostgreSQL RLS. The row is filtered out before reaching application logic (`PUBLIC_THRESHOLD_READ_BLOCKED` / `RLS_FILTERS_ROW`).
   - The signal disappears from public dashboards, farm advisories, and unauthenticated feeds.
2. **State Agricultural Administrators:**  
   - Granted full SELECT access via `ADMIN_BYPASS_SQL` and the `user_roles` subquery.
3. **Agricultural Experts & Researchers:**  
   - **Granted SELECT access** by PostgreSQL RLS because the `FOR ALL` policy's `USING` clause evaluates to `TRUE` via their role assignment in `user_roles`.
   - The signal remains queryable, visible, and inspectable in expert triage interfaces.

---

## 10. SAME-REQUEST AND SUBSEQUENT-REQUEST API RESPONSE BEHAVIOR

Inspection of [`backend/app/api/v1/endpoints/regional_pulse.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/regional_pulse.py#L80-L150) establishes the application-level response logic:

### Same-Request Response (The Request That Staged Revalidation)
- In `list_signals`:
  ```python
  is_valid = RegionalPulseService.revalidate_signal_provenance(db, sig.id)
  if not is_valid and not is_privileged:
      continue
  if sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE" and not is_privileged:
      continue
  sig_data = RegionalSignalResponse.model_validate(sig)
  if not is_privileged:
      sig_data.evidences = []
  results.append(sig_data)
  ```
  Because `is_privileged = True` for experts and researchers, the endpoint **does not skip the signal**. The actor receives the signal in the JSON response even as the suppression status is written.
- In `get_signal`:
  ```python
  if (not is_valid or sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE") and not is_privileged:
      raise HTTPException(status_code=404, detail="Regional signal not found or suppressed...")
  ```
  For an expert or researcher, `not is_privileged` is `False`, so the 404 is bypassed, and the suppressed signal is returned.

### Subsequent-Request Retrieval
- An expert or researcher executing `GET /signals` or `GET /signals/{id}` on a later connection:
  1. PostgreSQL evaluates RLS for SELECT. As proven in Section 8, the `FOR ALL` policy permits the query.
  2. The ORM loads the signal object.
  3. The route's `is_privileged` guard evaluates to `True`, bypassing the suppression filter.
  4. The signal is successfully returned to the expert/researcher.
- An ordinary farmer executing the same request:
  1. PostgreSQL RLS filters the row at the database level (`RLS_FILTERS_ROW`).
  2. For `list_signals`, the row never appears in `results`.
  3. For `get_signal`, `RegionalPulseService.get_signal()` returns `None`, raising `HTTP 404 Not Found`.

---

## 11. REGIONAL PULSE ORM MUTATION AND OUTER-COMMIT CONDITIONS

### Persistence Conditions Register
For the staged mutation (`distinct_farms_count = 0`) to physically persist in the database, the following distinct conditions must all be satisfied:

1. **ORM Mutation Staged:** Confirmed in source (`ORM_MUTATION_STAGED`).
2. **Savepoint Clean Release:** Confirmed in source (`STATIC_TRANSACTION_PATH_CONFIRMED`).
3. **Outer Commit Invocation:** Confirmed in source (`db.commit()` at lines 99 and 128).
4. **Policy Predicate Match:** Confirmed for role-bearing actors (`POLICY_PREDICATE_MATCHES`).
5. **Subquery Executability on `user_roles`:** Confirmed by `USER_OWNED` policy (`POLICY_GENERATOR_CONFIRMED`).
6. **Deployed Table Privilege on `user_roles`:** Unverified (`CONDITIONAL_ON_DEPLOYED_GRANTS` / `LIVE_ACL_NOT_VERIFIED`).
7. **Deployed Table Privilege on `regional_signals` (UPDATE):** Unverified (`CONDITIONAL_ON_DEPLOYED_GRANTS` / `LIVE_ACL_NOT_VERIFIED`).
8. **Physical Database Persistence:** Unverified in Mode A (`LIVE_COMMIT_NOT_VERIFIED`).

---

## 12. ROLE-SUBQUERY AND `USER_ROLES` DEPENDENCY ANALYSIS

The subquery inside `regional_signals_author_write_policy` is:
```sql
EXISTS (
    SELECT 1 FROM user_roles ur
    WHERE ur.user_id::text = current_setting('app.current_user_id', true)
    AND ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')
)
```

### Policy on `user_roles`
`user_roles` is generated with restrictive isolation:
```sql
USING ((SESSION_USER IN (...) AND CURRENT_USER IN (...) AND current_setting('app.is_admin', true) = 'true')
       OR user_id::text = current_setting('app.current_user_id', true))
```
- Because the subquery explicitly filters by `ur.user_id::text = current_setting('app.current_user_id', true)`, **the query satisfies the RLS policy on `user_roles`**.
- The query can succeed provided `acrevia_staging_app` has been granted `SELECT` on `user_roles`.

---

## 13. FARMER UPDATE AND EXPECTED ORM BEHAVIOR

When an ordinary farmer invokes the GET endpoint:
1. `signal.evidences` is filtered by RLS to `[]`.
2. Revalidation stages `distinct_farms_count = 0` and `validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'`.
3. Outer `db.commit()` flushes the UPDATE.
4. In PostgreSQL RLS:
   - The farmer fails the `USING` clause of `regional_signals_author_write_policy`.
   - **PostgreSQL does NOT throw an RLS check violation on the `USING` clause.**
   - Instead, the UPDATE statement matches **zero rows (`rowcount = 0`)**.
5. In SQLAlchemy ORM:
   - Flushing a persistent instance that updates zero rows raises **`sqlalchemy.orm.exc.StaleDataError`**.
6. Alternatively, if table-level `UPDATE` privilege is not granted to `acrevia_staging_app`, PostgreSQL raises `permission denied for table regional_signals` (SQLSTATE `42501`).
7. In either case, the outer route catches the exception, calls `db.rollback()`, and returns `HTTP 500`.

Formal Classification: **`EXACT_LIVE_EXCEPTION_NOT_VERIFIED`**.

---

## 14. ACTUAL GRANT UNKNOWNS AND MIGRATION/BOOTSTRAP INVOCATION RESULTS

- Repository-wide AST search confirms that `generate_privilege_grants_ddl()` is called **only in unit tests**, never in migrations (`backend/migrations/`) or runtime startup (`backend/app/database/init_db.py`).
- Table privileges on the live Neon staging instance cannot be determined from source alone.
- Status: **`LIVE_ACL_NOT_VERIFIED`**.

---

## 15. CORRECTED EXPERTCONNECT CLASSIFICATIONS AND ROUTE CONCLUSIONS

- Public source in [`backend/app/database/rls.py:47`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L47) establishes:
  `"expert_review_cases": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"}`.
- This classification is **already present** in source. There is no source-level metadata defect.
- The failure of ExpertConnect case listing is an **application tenant-context architecture issue**: global triage routes do not establish a farm tenant context (`app.current_tenant_id = ''`), causing PostgreSQL RLS to filter out all cases (`RLS_FILTERS_ROW`).
- This finding is properly classified under **`TENANT-MEMBERSHIP-01`**, not `DB-RLS-01`.

---

## 16. CANONICAL BLOCKER REGISTER WITH ALL 15 IDENTIFIERS

The canonical 15-item blocker register is restored to its exact historical definitions:

| Identifier | Severity | Canonical Category & Definition | Current Disposition | Owner Action Required | Release Status |
|---|---|---|---|---|---|
| **`RLS-WRITE-AUTH-01`** | `HIGH` | PostgreSQL RLS Architecture: Permissive `FOR ALL` policy on `regional_signals` allows role-bearing actors to execute UPDATE, enabling write-on-read signal suppression. | **OPEN — REMEDIATION PLANNED (Option D)** | Approve Option D command-separated fail-closed policies (`FOR INSERT`, `FOR UPDATE`). | **RELEASE BLOCKER** (`GATE-02`) |
| **`RLS-ROLE-ASSIGNMENT-01`** | `HIGH` | PostgreSQL Role Management: Application uses shared principal (`acrevia_staging_app`) relying on mutable client GUCs for role authorization rather than database roles. | **OPEN — REMEDIATION PLANNED (Option B)** | Adopt trusted writer gateway or dedicated database roles for privileged operations. | **RELEASE BLOCKER** (`GATE-02`) |
| **`DB-AUTH-01`** | `HIGH` | Trusted Database Writer Architecture: Architectural requirement for non-shared database principals; rejects client GUC role escalation. | **OPEN — ARCHITECTURE SPECIFIED** | Approve trusted database writer architecture decision record. | **RELEASE BLOCKER** (`GATE-02`) |
| **`DB-CREDENTIAL-EXPOSURE-01`** | `CRITICAL` | Cloud Security / Credential Governance: Administrative database URI (`neondb_owner`) committed to public GitHub history in `frontend/lib/server/db.ts:9-10`. | **OPEN — ROTATION OUTSTANDING** | Rotate Neon password, purge Git history with BFG / git-filter-repo, configure secrets. | **RELEASE BLOCKER** (`GATE-01`) |
| **`APP-ROLE-SELF-SELECT-01`** | `HIGH` | Application Authentication Gateway: Registration schema (`UserCreate.role`) allows self-selecting `AGRICULTURAL_EXPERT` and `RESEARCHER` without pre-approval. | **OPEN — REMEDIATION REQUIRED** | Restrict public registration to `FARMER`; mandate admin approval for privileged roles. | **RELEASE BLOCKER** (`GATE-02`) |
| **`EXP-AUTH-01`** | `MEDIUM` | Expert Authorization & Accreditation: Professional expert accreditation (`ExpertProfile`) is decoupled from role assignment; researcher workflow absent. | **OPEN — ACCREDITATION DECOUPLED** | Implement accreditation gating for expert and researcher roles. | **RELEASE BLOCKER** (`GATE-03`) |
| **`CASCADE-ROLE-DEL-01`** | `MEDIUM` | Relational Schema Integrity: Foreign key `ON DELETE CASCADE` from `users.id` to `user_roles.user_id` allows role deletion if user is deleted (requires arbitrary SQL). | **MONITORED RESIDUAL RISK** | Review FK cascade constraints on security-critical tables. | Residual Risk |
| **`TENANT-MEMBERSHIP-01`** | `HIGH` | Tenant Context Resolution: Authenticated requests set `app.current_user_id` but leave `app.current_tenant_id = ''`, breaking triage in `expert_review_cases`. | **OPEN — CONTEXT GAP** | Implement tenant context resolution for regional and cross-farm triage workflows. | **RELEASE BLOCKER** (`GATE-02`) |
| **`OWNER-AUTH-01`** | `HIGH` | Project Governance & Authorization: Formal Project Owner governance decisions (`D-01`, `D-02`, `D-03`, `DB-AUTH-01`) and written Mode B execution authorization remain pending. | **OPEN — AWAITING OWNER ACTION** | Project Owner must sign Decision Gates 02 through 05 in the execution register. | **RELEASE BLOCKER** (`GATE-01`) |
| **`DB-RLS-01`** | `HIGH` | Physical PostgreSQL Enforcement: Physical PostgreSQL kernel RLS, FORCE RLS, policy catalogs, and cross-tenant isolation remain unverified in the live instance. | **OPEN — LIVE RLS UNVERIFIED** | Execute live schema and policy catalog verification under authorized Mode B. | **RELEASE BLOCKER** (`GATE-02`) |
| **`WRK-DISP-01`** | `MEDIUM` | Asynchronous Worker Security: Celery/background workers inherit database connection parameters; unconfined worker principals could bypass RLS. | **MONITORED RESIDUAL RISK** | Ensure worker tasks establish appropriate session-local tenant and user GUCs. | Residual Risk |
| **`RES-PULSE-01`** | `LOW` | Collaborative Privacy Boundary: Evidence association metadata (`id`, `evidence_type`, `evidence_reference_id`, `added_at`) visible cross-district to privileged roles. | **MONITORED RESIDUAL RISK** | Evaluate district-scoping requirements for evidence association metadata. | Residual Risk |
| **`RES-PULSE-02`** | `MEDIUM` | Concurrency & Snapshot Isolation: READ COMMITTED multi-statement snapshot/concurrency window in Regional Pulse aggregation and revalidation. | **MONITORED RESIDUAL RISK** | Implement advisory locking or SERIALIZABLE isolation for regional aggregations. | Residual Risk |
| **`GATE01-PROV-01`** | `MEDIUM` | Staging Infrastructure Assurance: Neon staging branch provisioning is recorded in local artifacts, but live-validated branch status is unavailable in Mode A. | **OPEN — LIVE BRANCH UNVERIFIED** | Live-validate staging branch existence and connectivity under authorized Mode B. | **RELEASE BLOCKER** (`GATE-01`) |
| **`RES-PULSE-READ-01`** | `HIGH` | Data Integrity / Denial-of-Service: Dynamic provenance revalidation and `db.commit()` inside HTTP GET read endpoints stages and persists signal suppression. | **OPEN — DEFECT CONFIRMED** | Decouple revalidation from read routes; remove `db.commit()` from GET endpoints. | **RELEASE BLOCKER** (`GATE-02`) |

### Proposed Blocker for Missing Privilege Grant Deployment
- **`DB-GRANT-APPLY-01`** (`PROPOSED — OWNER APPROVAL REQUIRED`):  
  *Definition:* `generate_privilege_grants_ddl()` is defined in `backend/app/database/rls.py` but is completely absent from all Alembic migrations and database bootstrap scripts, leaving deployed table ACLs unmanaged by schema migrations.

---

## 17. CANONICAL RESIDUAL-RISK REGISTER

The five canonical residual risks remain active with their original meanings:

1. **`RES-PULSE-01`:** Role-global evidence association visibility without district scoping.
2. **`RES-PULSE-02`:** READ COMMITTED multi-statement snapshot/concurrency window during regional aggregation.
3. **`RES-PRIMARY-ROUTING-01`:** Regional Pulse write-on-read primary database routing dependency (read routes requiring write access).
4. **`RES-REPLICA-LAG-01`:** Read-replica replication lag causing stale signal visibility during dynamic revalidation.
5. **`RES-FREE-TEXT-01`:** Potential farmer PII leakage in author-controlled free-text fields (`evidence_notes`).

---

## 18. CANONICAL GOVERNANCE DECISION AND RELEASE-GATE STATUS

### Canonical Architecture Decisions
- **`D-01` (Regional Signal Visibility & Official Advisory Data Model):** Preserved. Official advisories require verified state administrative authority; regional collaborative visibility is separated from raw farm data.
- **`D-02` (Source Authenticity & Pilot Terminology):** Preserved. Multi-source provenance verification remains mandatory.
- **`D-03` (Independent Expert Review):** Preserved. Two-tier review and immutable audit trails remain standard.
- **`DB-AUTH-01` (Trusted Database Writer Identity Architecture):** Preserved. Demands non-shared database principals and rejects client GUC role escalation.

### Release Gate Status
- **`GATE-01` (Database Infrastructure & Credential Assurance):** **BLOCKED** (Credential rotation and live branch status unverified).
- **`GATE-02` (PostgreSQL RLS Kernel Isolation & Policy Composition):** **BLOCKED** (Option D remediation and write-on-read removal pending).
- **`GATE-03` (Application Authentication & Role Provisioning Gateway):** **BLOCKED** (Registration role restriction and accreditation gating pending).
- **`GATE-04` (Offline & Integration Test Verification):** **BLOCKED** (Empty tenant context integration tests pending).
- **`GATE-05` (Mode B Authorization & Production Release):** **BLOCKED** (Gates 01 through 04 must pass first).

**Formal Phase 07 Status:** **`NOT RELEASED`**  
**Execution Authorization:** **`MODE A ONLY — MODE B NOT AUTHORIZED`**

---

## 19. REMEDIATION ARCHITECTURE RECOMMENDATIONS (WITHOUT IMPLEMENTATION)

1. **Decouple Revalidation from HTTP GET Routes (`RES-PULSE-READ-01`):**  
   Remove `RegionalPulseService.revalidate_signal_provenance()` and `db.commit()` from `list_signals` and `get_signal`. Revalidation must be executed asynchronously via background worker or performed as an in-memory filter without committing state changes to the database.
2. **Deploy Option D Command-Specific Policies (`RLS-WRITE-AUTH-01`):**  
   Replace `regional_signals_author_write_policy` (`FOR ALL`) with separate `FOR INSERT` and `FOR UPDATE` policies, strictly prohibiting general UPDATE permissions on published signals.
3. **Incorporate Table Grants into Alembic Migrations (`DB-GRANT-APPLY-01`):**  
   Add `generate_privilege_grants_ddl()` into Alembic revision scripts to ensure table privileges are deployed alongside RLS policies.
4. **Implement Tenant Context Resolution for Expert Triage (`TENANT-MEMBERSHIP-01`):**  
   Provide cross-farm triage context or reclassify `expert_review_cases` to allow experts to query cases without failing tenant RLS.
5. **Rotate Neon Cloud Credentials (`DB-CREDENTIAL-EXPOSURE-01`):**  
   Rotate the exposed credential in the Neon console, purge Git history, and configure runtime secrets.

---

## 20. REQUIRED FINDING MATRIX

| Question | Source / Policy Finding | Actor Scope | Grant Dependency | Live Status | Final Determination |
|---|---|---|---|---|---|
| **Does GET stage mutation?** | `SOURCE_PATH_CONFIRMED` (lines 339, 376) | All callers on GET | None (ORM memory) | Staged in Session | **`ORM_MUTATION_STAGED`** |
| **Can role-bearing actor satisfy UPDATE `USING`?** | `POLICY_PREDICATE_MATCHES` (`user_roles` subquery matches) | `ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER` | `CONDITIONAL_ON_DEPLOYED_GRANTS` (SELECT on `user_roles`) | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`POLICY_PREDICATE_MATCHES`** |
| **Can farmer satisfy UPDATE `USING`?** | `POLICY_PREDICATE_FAILS` (farmer role excluded) | `FARMER` | None (policy excludes) | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`UPDATE_USING_FILTERS_ROW`** |
| **Does `FOR ALL` apply to SELECT?** | `POLICY_COMMAND_SCOPE_CONFIRMED` (PostgreSQL standard) | All actors | None (engine rule) | Architectural certainty | **`FOR_ALL_APPLIES_TO_SELECT`** |
| **Does the write policy contribute to SELECT?** | `PERMISSIVE_POLICY_OR_COMPOSITION` (Permissive policies combine with OR) | All actors | `CONDITIONAL_ON_DEPLOYED_RLS` | Architectural certainty | **`PERMISSIVE_POLICY_OR_COMPOSITION`** |
| **Can expert/researcher SELECT count-zero signal?** | `ROLE_BEARING_SELECT_POSSIBLE` ($\text{FALSE} \lor \text{TRUE} = \text{TRUE}$) | `ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER` | `CONDITIONAL_ON_DEPLOYED_GRANTS` & RLS | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`ROLE_BEARING_SELECT_POSSIBLE`** |
| **Can farmer SELECT count-zero signal?** | `PUBLIC_THRESHOLD_READ_BLOCKED` ($\text{FALSE} \lor \text{FALSE} = \text{FALSE}$) | `FARMER`, Unauthenticated | `CONDITIONAL_ON_DEPLOYED_RLS` | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`PUBLIC_THRESHOLD_READ_BLOCKED`** |
| **Does triggering expert GET return suppressed signal?** | `SOURCE_CONFIRMED` (`and not is_privileged` bypasses 404/filter) | `ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER` | None (Python logic) | `SOURCE_CONFIRMED` | **`SOURCE_PATH_PERMITS_PRIVILEGED_RESPONSE`** |
| **Does subsequent expert GET still return it?** | `ROLE_BEARING_SELECT_POSSIBLE` (Database SELECT succeeds; route permits) | `ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER` | `CONDITIONAL_ON_DEPLOYED_GRANTS` & RLS | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`ROLE_BEARING_SELECT_POSSIBLE`** |
| **Does subsequent farmer GET hide it?** | `PUBLIC_THRESHOLD_READ_BLOCKED` (Database filters row; route 404s) | `FARMER`, Unauthenticated | `CONDITIONAL_ON_DEPLOYED_RLS` | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`PUBLIC_THRESHOLD_READ_BLOCKED`** |
| **Can evidence associations still be SELECTed?** | `SOURCE_CONFIRMED` (`regional_signal_evidences` allows expert role) | `ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER` | `CONDITIONAL_ON_DEPLOYED_GRANTS` | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`ROLE_BEARING_EVIDENCE_SELECT_POSSIBLE`** |
| **Is the role subquery executable?** | `POLICY_GENERATOR_CONFIRMED` (`user_roles` policy allows reading own row) | Authenticated actors | `CONDITIONAL_ON_DEPLOYED_GRANTS` (SELECT on `user_roles`) | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`CONDITIONAL_ON_DEPLOYED_GRANTS`** |
| **Is UPDATE privilege deployed?** | `LOCALLY_SPECIFIED_NEVER_EXECUTED_IN_MIGRATIONS` | Database role `acrevia_staging_app` | Live database ACL catalog | `LIVE_ACL_NOT_VERIFIED` | **`UNKNOWN (LIVE_ACL_NOT_VERIFIED)`** |
| **Was outer commit verified?** | `STATIC_TRANSACTION_PATH_CONFIRMED` (`db.commit()` in route) | GET endpoints | Live database execution | `LIVE_COMMIT_NOT_VERIFIED` | **`CONDITIONAL (LIVE_COMMIT_NOT_VERIFIED)`** |
| **Is the actual Neon policy set known?** | `MIGRATION_CALLS_GENERATE_RLS_DDL` (Migration calls generator, but live catalog unread) | Live database instance | Live database catalog | `LIVE_POSTGRESQL_NOT_VERIFIED` | **`CONDITIONAL_ON_DEPLOYED_RLS`** |

---

## 21. EXACT SOURCE INVENTORY AND FINAL WORKING-TREE PRESERVATION

### Inspected Files
- `backend/app/api/v1/endpoints/regional_pulse.py` (GET endpoints, revalidation calls, response suppression filters)
- `backend/app/services/regional_pulse_service.py` (Revalidation logic, savepoint, status mutation)
- `backend/app/database/rls.py` (`regional_signals` & `regional_signal_evidences` policy generators, `TABLE_CLASSIFICATION`, `PRIVILEGE_CROSSWALK`)
- `backend/app/models/regional_pulse.py` (`RegionalSignal`, `RegionalSignalEvidence`, `added_at` field)
- `backend/app/schemas/regional_pulse.py` (`RegionalSignalResponse`, `RegionalSignalEvidenceItem`)
- `backend/app/api/v1/endpoints/expertconnect.py` (ExpertConnect route dependencies & `@require_roles`)
- `backend/app/services/expertconnect/expert_service.py` (`list_cases` implementation)
- `backend/migrations/versions/a1089411c87d_phase_07_rls_policies.py` (Alembic RLS policy migration)
- `frontend/lib/server/db.ts` (Database helper & exposed fallback URI)

### Final Working-Tree Preservation Statement
- All existing source files, ORM models, schemas, endpoints, migrations, and test files remain **unmodified (0 modifications)**.
- All prior security reports remain **intact and unedited**.
- The single new report created is:  
  `docs/pilot/security/PHASE_07_REGIONAL_SIGNAL_FOR_ALL_POLICY_READ_VISIBILITY_AND_GOVERNANCE_ID_CORRECTION_AUDIT.md`.
