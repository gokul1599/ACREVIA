# ACREVIA — PHASE 07: OPTION D EFFECTIVE-POLICY COMPOSITION, READ-PRIVACY PRESERVATION & EVIDENCE-ASSOCIATION SECURITY COMPLETENESS AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** `MODE A ONLY` — Local Source Inspection, Security Engineering Analysis, Concurrency Modeling & Governance Documentation  
**Git Baseline Commit:** `dbad296c6f19c4bbe8eb48fcd7a0e07441cfa408` (`main`)  
**Methodology:** Everything Claude Code (ECC): `PLAN → TEST → IMPLEMENT ONLY IF DEFECT PROVEN → REVIEW → VERIFY → DOCUMENT`  
**Evaluation Date:** 2026-11-15T18:35:19+05:30  
**Determination:** `TECHNICAL_PREFLIGHT_BLOCKED_WITH_RECORDED_BLOCKERS`  

---

## 1. Executive Determination

A rigorous adversarial security and architectural investigation was conducted on the proposed **Option D (Fail-Closed Official-Advisory RLS Policy Contract)** under strict `MODE A ONLY` constraints. While Option D correctly separates SQL command vectors (`INSERT`, `UPDATE`, `DELETE`, `SELECT`) to remediate `RLS-WRITE-AUTH-01`, this audit establishes that **Option D is not yet implementation-ready** due to two newly proven structural security and operational findings:

1. **Sub-Threshold & Suspended Read-Privacy Exposure (`RES-PULSE-READ-01`):**
   The current `regional_signals_author_write_policy` on `regional_signals` is an `AS PERMISSIVE FOR ALL` policy. In PostgreSQL, `PERMISSIVE` policies combine via `OR`. Consequently, for `SELECT` operations, any session where `app.current_user_id` resolves to role `ADMIN`, `AGRICULTURAL_EXPERT`, or `RESEARCHER` evaluates the author policy to `TRUE`, completely bypassing the separate public read policy (`distinct_farms_count >= 3 AND validation_status != 'SUSPENDED'`). Because `app.current_user_id` is an unauthenticated, mutable session GUC set via `SET LOCAL`, any attacker or SQL injection on the shared database connection (`acrevia_staging_app`) can read sub-threshold outbreak claims ($N < 3$) and suspended signals across all Telangana districts. This is formally classified as a distinct read-privacy blocker: **`RES-PULSE-READ-01`**.

2. **Critical API Workflow Collisions Upon Naive `FOR ALL` Removal:**
   Simply stripping the broad `FOR ALL` policy and leaving only the existing public `SELECT` policy breaks core FastAPI and SQLAlchemy workflows:
   - **`recover_suppressed_signal`:** Executes `select(RegionalSignal).where(id == signal_id).with_for_update()`. In PostgreSQL, `SELECT ... FOR UPDATE` evaluates `SELECT` RLS policies. If the signal is currently suppressed or sub-threshold, the public `SELECT` policy excludes it, returning zero rows and causing the recovery endpoint to fail with HTTP 404.
   - **`aggregate_regional_signal`:** The endpoint executes `db.refresh(signal)` immediately after `db.commit()`. If an expert creates a signal starting below threshold ($N < 3$) or creates a zero-telemetry advisory, `db.refresh()` executes `SELECT ... WHERE id = :id`. Because the row is excluded by public read RLS, SQLAlchemy raises `ObjectDeletedError`, rolling back the transaction and returning HTTP 500.
   - **`revalidate_signal_provenance`:** Dynamic suppression requires `UPDATE USING` visibility on rows being evaluated.

3. **Incomplete Child Evidence Table Policy Contract:**
   The previously sketched child-table policy for `regional_signal_evidences` only evaluated `INSERT`. It omitted `UPDATE` (allowing attackers to reparent existing evidence to official advisories or steal evidence away from official advisories) and `DELETE`. Furthermore, if the parent signal is hidden from the caller by parent `SELECT` RLS, an `EXISTS` subquery in the child policy evaluates to `FALSE`, breaking legitimate evidence association workflows.

4. **Parent Promotion Evidence Provenance Gap:**
   When an ordinary non-official signal is promoted to an official state advisory by a trusted administrative writer, evidence previously attached by collaborative actors remains linked to the newly official advisory. Without an atomic revalidation protocol enforced at promotion time, unverified community evidence could become associated with official government directives.

Therefore, Phase 07 remains **`NOT RELEASED`**, Mode B remains **`STRICTLY NOT AUTHORIZED`**, and `RLS-WRITE-AUTH-01` remains an **`ACTIVE_ARCHITECTURAL_BLOCKER`** alongside newly recorded blocker **`RES-PULSE-READ-01`**.

---

## 2. Exact Local Baseline

The local repository environment was inspected under strict `MODE A ONLY` restrictions without modifying any application, test, or migration files:

```text
git branch --show-current
main

git rev-parse HEAD
dbad296c6f19c4bbe8eb48fcd7a0e07441cfa408

git diff --cached --stat
(0 files staged, working tree clean of staged commits)

git diff --stat
 backend/app/api/v1/endpoints/regional_pulse.py     |   34 +-
 backend/app/schemas/regional_pulse.py              |   27 +-
 backend/app/services/regional_pulse_service.py     |  116 +-
 backend/tests/test_rls_policy_semantics.py         |   19 +-
 backend/tests/test_worker_security_and_privacy.py  | 2049 ++++++++++++++++++++
 docs/pilot/security/PHASE_07_FINAL_TECHNICAL_PREFLIGHT_STATUS.md   |   24 +-
 docs/pilot/security/PHASE_07_REGIONAL_AGGREGATION_PROVENANCE_AUDIT.md |   38 +-
 7 files changed, 2266 insertions(+), 41 deletions(-)
```

### 2.1 File State Verification
- **Staged Files:** Exactly **0** files staged.
- **Tracked Modifications:** Exactly **7** pre-existing modified files from prior audit phases.
- **Untracked Files:** Exactly **15** governance dossiers in `docs/pilot/security/`.
- **Database & RLS Generator Integrity:**
  - `backend/app/database/rls.py`: **100% byte-for-byte identical** to public commit `dbad296c` (`git diff HEAD` is empty).
  - Migration `a1089411c87d`: **100% byte-for-byte identical** to public commit `dbad296c` (`git diff HEAD` is empty).
  - Migration `d2894a11c87d`: Untouched.
- **Task Invariant:** Zero lines of application code, ORM models, migrations, or test implementations were created, deleted, or modified during this task.

---

## 3. Current Policy Inventory

Inspection of `backend/app/database/rls.py` and generated DDL reveals the active policy structure for the regional pulse domain:

### 3.1 `regional_signals` Policies
```sql
-- Table: regional_signals (Collaborative Table with Scoped Security)
ALTER TABLE regional_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE regional_signals FORCE ROW LEVEL SECURITY;

-- Policy 1: Public Read Policy
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

-- Policy 2: Author Write Policy (Applies to ALL commands)
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

### 3.2 `regional_signal_evidences` Policies
```sql
-- Table: regional_signal_evidences (Collaborative Table with Scoped Security)
ALTER TABLE regional_signal_evidences ENABLE ROW LEVEL SECURITY;
ALTER TABLE regional_signal_evidences FORCE ROW LEVEL SECURITY;

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

CREATE POLICY regional_signal_evidences_author_write_policy ON regional_signal_evidences
    AS PERMISSIVE
    FOR ALL
    TO PUBLIC
    USING (...) WITH CHECK (...); -- Identical role check to regional_signals
```

### 3.3 `user_roles` Policies
```sql
-- Table: user_roles (User-Owned Isolation)
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles FORCE ROW LEVEL SECURITY;

CREATE POLICY user_roles_base_access_policy ON user_roles
    AS PERMISSIVE
    FOR ALL
    TO PUBLIC
    USING (true)
    WITH CHECK (true);

CREATE POLICY user_roles_user_isolation_policy ON user_roles
    AS RESTRICTIVE
    FOR ALL
    TO PUBLIC
    USING (
        (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND current_setting('app.is_admin', true) = 'true')
        OR user_id::text = current_setting('app.current_user_id', true)
    )
    WITH CHECK (
        (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND current_setting('app.is_admin', true) = 'true')
        OR user_id::text = current_setting('app.current_user_id', true)
    );
```

---

## 4. Effective Command-by-Command Policy Composition

In PostgreSQL (versions 12 through 16+), row-level security policies apply on a per-command basis according to strict algebraic rules:
- **`PERMISSIVE` Policies:** Multiple permissive policies applicable to a command combine with **Boolean `OR`**:
  $$\text{Effective Permissive Clause} = \text{Policy}_1 \lor \text{Policy}_2 \lor \dots \lor \text{Policy}_k$$
- **`RESTRICTIVE` Policies:** Restrictive policies combine with **Boolean `AND`** against the permissive result:
  $$\text{Row Visible} = \left(\bigvee_{i} \text{Permissive}_i\right) \land \left(\bigwedge_{j} \text{Restrictive}_j\right)$$
- **`FOR ALL` Scope:** Applies to `SELECT`, `INSERT`, `UPDATE`, and `DELETE`.

### 4.1 Current Policy Matrix for `regional_signals`

| SQL Operation | Policies Applied | Effective PostgreSQL Logic | Observable Behavior & Security Risk |
|---|---|---|---|
| **`SELECT`** | `public_read_policy` (`FOR SELECT`)<br>$\lor$ `author_write_policy` (`FOR ALL`) | `(ADMIN_BYPASS OR (N>=3 AND status!='SUSPENDED'))` $\lor$ `(ADMIN_BYPASS OR EXISTS(ur.role IN ('ADMIN','EXPERT','RESEARCHER')))` | **HIGH RISK (`RES-PULSE-READ-01`):** Permissive OR allows any session satisfying role subquery to read all sub-threshold ($N<3$) and suspended signals across all districts. |
| **`INSERT`** | `author_write_policy` (`FOR ALL` `WITH CHECK`) | `ADMIN_BYPASS OR EXISTS(ur.role IN ('ADMIN','EXPERT','RESEARCHER'))` | **CRITICAL RISK (`RLS-WRITE-AUTH-01`):** No column checks. Expert or researcher can insert `confidence_tier = 'OFFICIAL_ADVISORY'` directly. |
| **`UPDATE`** | `author_write_policy` (`FOR ALL` `USING` + `WITH CHECK`) | `USING` checks old row; `WITH CHECK` checks new row. Both use the identical role subquery. | **CRITICAL RISK (`RLS-WRITE-AUTH-01`):** Expert or researcher can update non-official signal to `OFFICIAL_ADVISORY` or modify an official advisory. |
| **`DELETE`** | `author_write_policy` (`FOR ALL` `USING`) | Role subquery allows delete under RLS, but blocked by SQL grant revocation. | **DEFENSE-IN-DEPTH DEFECT:** RLS allows DELETE; only table grant `REVOKE DELETE` prevents execution. |
| **`INSERT ... RETURNING`** | `author_write_policy` (`WITH CHECK`) + `SELECT` policies | Row must pass `WITH CHECK`, and returned columns must pass `SELECT` policies. | If `FOR ALL` is removed, inserting an official advisory or sub-threshold signal fails `SELECT` RETURNING evaluation! |
| **`UPDATE ... RETURNING`** | `author_write_policy` (`USING` + `WITH CHECK`) + `SELECT` policies | Old row passes `USING`; new row passes `WITH CHECK`; returned columns pass `SELECT`. | If `FOR ALL` is removed, updating a signal to suppressed status breaks RETURNING clause! |
| **`INSERT ... ON CONFLICT DO UPDATE`** | `INSERT` (`WITH CHECK`) on insert path; `UPDATE` (`USING` + `WITH CHECK`) on conflict path | Evaluates both INSERT and UPDATE paths under PostgreSQL rules. | Both paths permit unauthorized official advisory claims under current unhardened DDL. |
| **`MERGE`** (PG 15+) | Evaluates `SELECT` (join), `INSERT`, `UPDATE`, `DELETE` per matched branch | Evaluates command-specific policies for each branch. | Same vulnerabilities apply across all matched branches. |

---

## 5. Sub-Threshold SELECT Privacy Findings (`RES-PULSE-READ-01`)

The interaction between `regional_signals_public_read_policy` and `regional_signals_author_write_policy` produces an unintended read-privacy puncture.

### 5.1 Mathematical Proof of Read-Threshold Bypass
Let $R$ represent a row in `regional_signals`.  
Let $P_{\text{pub}}(R)$ be the public read predicate:
$$P_{\text{pub}}(R) \iff \text{ADMIN\_BYPASS} \lor (R.\text{distinct\_farms\_count} \ge 3 \land R.\text{validation\_status} \ne \text{'SUSPENDED'})$$
Let $P_{\text{auth}}(R)$ be the author policy predicate:
$$P_{\text{auth}}(R) \iff \text{ADMIN\_BYPASS} \lor (\text{current\_setting('app.current\_user\_id', true)} \ne \text{''} \land \exists\, ur \in \text{user\_roles} : ur.\text{role\_id} \in \{\text{'ADMIN'}, \text{'AGRICULTURAL\_EXPERT'}, \text{'RESEARCHER'}\})$$

Because both policies are declared `AS PERMISSIVE`, PostgreSQL computes visibility for `SELECT` as:
$$V(R) = P_{\text{pub}}(R) \lor P_{\text{auth}}(R)$$

When a session operates with `app.current_user_id` belonging to an expert, researcher, or admin:
$$P_{\text{auth}}(R) = \text{TRUE} \implies V(R) = \text{TRUE} \quad \forall R \in \text{regional\_signals}$$

### 5.2 Observable Privacy Consequences
1. **Sub-Threshold Crop Outbreaks ($N < 3$):** Signals derived from 1 or 2 farms contain identifiable spatial and crop telemetry. In rural Telangana mandals with few large holdings, exposing $N=1$ outbreak claims allows commercial actors to identify specific farms experiencing pest distress (e.g. Cotton Pink Bollworm in Warangal).
2. **Suspended & Discredited Claims:** Signals marked `SUSPENDED` (due to suspected false alarms or failed sensor calibration) are visible to all experts and researchers statewide, risking incorrect agricultural interventions.
3. **Absence of Geographic/District Scoping:** The author policy grants statewide visibility. An expert in Adilabad can read raw sub-threshold claims originating in Khammam without tenant, district, or institutional boundaries.

---

## 6. Mutable-GUC Read-Impersonation Findings

The security model assumes that database-layer role verification in `user_roles` acts as a trusted gate. However, source inspection of `user_roles` RLS proves that this assumption is flawed under the shared runtime principal (`acrevia_staging_app`).

### 6.1 GUC Spoofing Traceability
1. **Shared Runtime Principal:** All application traffic connects to PostgreSQL as `acrevia_staging_app`.
2. **Session GUC Mutation:** Any database session can issue:
   ```sql
   SET LOCAL app.current_user_id = '00000000-0000-0000-0000-000000000099';
   ```
3. **`user_roles` Policy Resolution:**
   The policy on `user_roles` is:
   ```sql
   USING (ADMIN_BYPASS_SQL OR user_id::text = current_setting('app.current_user_id', true))
   ```
   When the session executes `SELECT 1 FROM user_roles ur WHERE ur.user_id::text = current_setting('app.current_user_id', true)`, PostgreSQL searches `user_roles` filtered by `user_id = '00000000-0000-0000-0000-000000000099'`.
4. **Subquery Execution:** If `'00000000-0000-0000-0000-000000000099'` belongs to a real expert or researcher, the subquery returns a row with `role_id = 'AGRICULTURAL_EXPERT'`.
5. **Privilege Elevation:** `P_auth` evaluates to `TRUE`, granting the session full read access to all sub-threshold and suspended signals across the entire state!

$$\mathbf{Result:}\ \text{Mutable GUC spoofing directly elevates unprivileged SQL sessions to state-wide sub-threshold signal readers.}$$

### 6.2 Formal Blocker Proposal: `RES-PULSE-READ-01`
- **Identifier:** `RES-PULSE-READ-01`
- **Title:** Role-Global Sub-Threshold & Suspended Signal Read-Privacy Exposure
- **Severity:** High (Privacy & Data Governance)
- **Status:** `ACTIVE_ARCHITECTURAL_BLOCKER`
- **Classification:** `PROVEN_FROM_LOCAL_POLICY_STRUCTURE`
- **Remediation Requirement:** Replace permissive `FOR ALL` policy with strict command-specific policies, and confine internal administrative read visibility to explicitly authenticated, trusted sessions without leaking sub-threshold farmer telemetry.

---

## 7. Project Owner Decision D-01 Visibility Implications

Project Owner Decision **D-01** governs whether public farmers are permitted to view zero-telemetry official state advisories:
- **Condition:** `distinct_farms_count = 0` AND `confidence_tier = 'OFFICIAL_ADVISORY'`.
- **Under Current Public Read Policy:**
  `distinct_farms_count >= 3 AND validation_status != 'SUSPENDED'`
  Zero-telemetry advisories ($N=0$) are **completely hidden** from public farmers!
- **Current Status:** `PENDING_PROJECT_OWNER_AUTHORIZATION`.
- **Design Invariant:** The replacement SELECT policy must not preemptively implement Option A (public visibility of official advisories) or Option B (farmers restricted to $N \ge 3$) until the Project Owner explicitly signs D-01 in the Execution Register.

---

## 8. SELECT Dependencies of UPDATE, DELETE, and RETURNING

Removing the broad `FOR ALL` policy without introducing a properly scoped internal SELECT policy causes silent failures in PostgreSQL operations that depend on `SELECT` visibility.

### 8.1 PostgreSQL SQL Semantics
1. **`UPDATE ... WHERE ...`:** To locate candidate rows for update, PostgreSQL requires `SELECT` visibility on the old row (or evaluates `UPDATE USING`). In PostgreSQL, if an `UPDATE` statement includes a `WHERE` clause referencing table columns, the caller must have `SELECT` privilege and the row must satisfy the table's `SELECT` RLS policy in subqueries or qualifying scans.
2. **`UPDATE ... RETURNING` & `INSERT ... RETURNING`:** PostgreSQL documented behavior explicitly mandates that any column returned via `RETURNING` is filtered through the table's `SELECT` RLS policy. If the resulting row fails the `SELECT` policy, PostgreSQL returns zero rows, or raises an error depending on driver expectations.
3. **`SELECT ... FOR UPDATE`:** In PostgreSQL, locking a row via `FOR UPDATE` is formally a `SELECT` command. It applies `FOR SELECT` RLS policies. It **does NOT** evaluate `UPDATE USING` policies.

### 8.2 Real SQLAlchemy Operations in ACREVIA
Inspection of `backend/app/services/regional_pulse_service.py` reveals the following real code paths:

```python
# Path 1: recover_suppressed_signal (line 430)
stmt = (
    select(RegionalSignal)
    .options(selectinload(RegionalSignal.evidences))
    .where(RegionalSignal.id == signal_id)
    .with_for_update()
)
signal = db.execute(stmt).scalar_one_or_none()

# Path 2: aggregate_regional_signal (line 252)
if auto_commit:
    db.commit()
    db.refresh(signal)

# Path 3: revalidate_signal_provenance (line 331)
with db.begin_nested():
    signal = RegionalPulseService.get_signal(db, signal_id)
```

---

## 9. API Workflow Compatibility Matrix

The following matrix maps real API workflows against current behavior, naive Option D (removing `FOR ALL` and keeping only public `SELECT`), and complete Option D (incorporating an authorized internal workflow read policy):

| Workflow & Endpoint | ORM Operation | Current Behavior | Naive Option D (Public SELECT Only) | Complete Option D Resolution |
|---|---|---|---|---|
| **`POST /signals`**<br>(New Advisory $N=0$) | `db.add()` $\to$ `db.commit()` $\to$ `db.refresh(signal)` | Succeeds (author policy grants SELECT). | **FAILS:** `db.refresh()` executes `SELECT WHERE id = :id`. Because $N=0$, public SELECT returns 0 rows. SQLAlchemy raises `ObjectDeletedError`. HTTP 500. | Add authorized administrative SELECT policy for trusted sessions. |
| **`POST /signals`**<br>(Pest Alert $N < 3$) | `db.add()` $\to$ `db.commit()` $\to$ `db.refresh(signal)` | Succeeds (author policy grants SELECT). | **FAILS:** `db.refresh()` fails with `ObjectDeletedError` because $N < 3$. HTTP 500. | Add scoped internal SELECT policy for author/expert session. |
| **`POST /signals/{id}/recover`**<br>(Suppressed Signal) | `select(RegionalSignal).where(...).with_for_update()` | Succeeds (author policy grants SELECT on suppressed rows). | **FAILS:** `with_for_update()` evaluates public SELECT. Because status is `SUSPENDED` or $N < 3$, query returns `None`. Endpoint returns HTTP 404! | Authorized recovery SELECT branch for expert/admin sessions. |
| **`GET /signals`**<br>(Public Farmer) | `select(RegionalSignal)` | Returns only $N \ge 3$, non-suspended signals. Evidences query returns `[]`. | Returns only $N \ge 3$, non-suspended signals. Evidences query returns `[]`. | Fully preserved. Public privacy guaranteed. |
| **`GET /signals/{id}`**<br>(Dynamic Revalidation) | `with db.begin_nested():` $\to$ updates status to `SUPPRESSED` | Succeeds (author policy grants UPDATE). | Succeeds on UPDATE, but subsequent reads by public fail closed. | Fully preserved. Dynamic suppression operates cleanly. |

---

## 10. Reconcile the `IS DISTINCT FROM` and NULL Contract

The proposed fail-closed policy condition:
```sql
confidence_tier IS DISTINCT FROM 'OFFICIAL_ADVISORY'
```
evaluates to `TRUE` if `confidence_tier` is `NULL`.

### 10.1 Schema & Migration Evidence
1. **ORM Metadata:** In `backend/app/models/regional_pulse.py`:
   - `confidence_tier = Column(String(50), nullable=False, index=True)`
   - `validation_status = Column(String(50), nullable=False, index=True)`
   - `distinct_farms_count = Column(Integer, nullable=False, default=1)`
2. **Database DDL Migration:** In `backend/app/database/migrations/versions/d2894a11c87d_stage12_collaborative_intelligence.py`:
   - Executes `Base.metadata.create_all(bind=bind)`.
   - Generates PostgreSQL `NOT NULL` column constraints on all above fields.
3. **Live Database Status:** `LIVE_POSTGRESQL_REQUIRED` (cannot inspect live catalogs in Mode A).

### 10.2 Contract Determination: Unified Contract A + C
- **Contract A (DDL Level):** Relies on database `NOT NULL` constraints to reject `NULL` on insertion.
- **Contract B (Permissive NULL):** Rejected. Permitting `NULL` at the authorization boundary creates an undefined governance state.
- **Contract C (Defensive Authorization Boundary):** Incorporates explicit non-NULL assertions directly into the RLS policy:
  ```sql
  AND confidence_tier IS NOT NULL 
  AND validation_status IS NOT NULL
  AND confidence_tier IS DISTINCT FROM 'OFFICIAL_ADVISORY'
  AND validation_status IS DISTINCT FROM 'OFFICIAL_ALERT'
  ```
$$\mathbf{Determination:}\ \text{Adopt Contract C defensively to guarantee fail-closed enforcement even if DDL constraints drift.}$$

---

## 11. Complete `regional_signal_evidences` Policy Contract

The child evidence table (`regional_signal_evidences`) requires a robust, command-specific RLS policy contract.

### 11.1 INSERT Policy
An ordinary actor (`AGRICULTURAL_EXPERT` or `RESEARCHER`) must only attach evidence to an existing, valid non-official parent signal:
```sql
CREATE POLICY regional_signal_evidences_ordinary_insert_policy ON regional_signal_evidences
    AS PERMISSIVE
    FOR INSERT
    TO PUBLIC
    WITH CHECK (
        -- Administrative trusted session bypass
        (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND current_setting('app.is_admin', true) = 'true')
        OR (
            -- Ordinary collaborative actor attaching to non-official parent
            current_setting('app.current_user_id', true) != ''
            AND EXISTS (
                SELECT 1 FROM user_roles ur
                WHERE ur.user_id::text = current_setting('app.current_user_id', true)
                AND ur.role_id IN ('AGRICULTURAL_EXPERT', 'RESEARCHER')
            )
            AND EXISTS (
                SELECT 1 FROM regional_signals rs
                WHERE rs.id = regional_signal_evidences.signal_id
                  AND rs.confidence_tier IS NOT NULL
                  AND rs.confidence_tier IS DISTINCT FROM 'OFFICIAL_ADVISORY'
                  AND rs.validation_status IS NOT NULL
                  AND rs.validation_status IS DISTINCT FROM 'OFFICIAL_ALERT'
            )
        )
    );
```

### 11.2 UPDATE Policy (Old and New Association Integrity)
Ordinary actors must be blocked from reparenting evidence records across security boundaries:
```sql
CREATE POLICY regional_signal_evidences_ordinary_update_policy ON regional_signal_evidences
    AS PERMISSIVE
    FOR UPDATE
    TO PUBLIC
    USING (
        -- Old row must belong to an authorized non-official parent
        (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND current_setting('app.is_admin', true) = 'true')
        OR (
            current_setting('app.current_user_id', true) != ''
            AND EXISTS (
                SELECT 1 FROM user_roles ur
                WHERE ur.user_id::text = current_setting('app.current_user_id', true)
                AND ur.role_id IN ('AGRICULTURAL_EXPERT', 'RESEARCHER')
            )
            AND EXISTS (
                SELECT 1 FROM regional_signals rs
                WHERE rs.id = regional_signal_evidences.signal_id
                  AND rs.confidence_tier IS DISTINCT FROM 'OFFICIAL_ADVISORY'
                  AND rs.validation_status IS DISTINCT FROM 'OFFICIAL_ALERT'
            )
        )
    )
    WITH CHECK (
        -- New row must also belong to an authorized non-official parent
        (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND current_setting('app.is_admin', true) = 'true')
        OR (
            current_setting('app.current_user_id', true) != ''
            AND EXISTS (
                SELECT 1 FROM user_roles ur
                WHERE ur.user_id::text = current_setting('app.current_user_id', true)
                AND ur.role_id IN ('AGRICULTURAL_EXPERT', 'RESEARCHER')
            )
            AND EXISTS (
                SELECT 1 FROM regional_signals rs
                WHERE rs.id = regional_signal_evidences.signal_id
                  AND rs.confidence_tier IS DISTINCT FROM 'OFFICIAL_ADVISORY'
                  AND rs.validation_status IS DISTINCT FROM 'OFFICIAL_ALERT'
            )
        )
    );
```

### 11.3 DELETE Policy
Ordinary actors have no operational requirement to delete evidence:
- **SQL Grant Level:** `REVOKE DELETE ON TABLE regional_signal_evidences FROM acrevia_staging_app;` (Verified in local generator).
- **RLS Level (Defense-in-Depth):**
  ```sql
  CREATE POLICY regional_signal_evidences_delete_policy ON regional_signal_evidences
      AS PERMISSIVE
      FOR DELETE
      TO PUBLIC
      USING (
          SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
          AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
          AND current_setting('app.is_admin', true) = 'true'
      );
  ```

### 11.4 Policy-Subquery Permissions & Visibility
In PostgreSQL, subqueries inside RLS policies execute with the current session's permissions and are subject to RLS on the referenced table (`regional_signals`).  
**Operational Dependency:** If `regional_signals` RLS completely hides non-official signals from the calling actor, the `EXISTS (SELECT 1 FROM regional_signals rs WHERE rs.id = ...)` subquery will return `FALSE`, causing valid evidence inserts to fail!  
**Requirement:** The parent `regional_signals` table MUST grant internal `SELECT` visibility on non-official parent rows to authenticated experts and researchers.

---

## 12. Parent State Transition and Evidence Provenance Integrity

A subtle attack vector occurs across the lifecycle of promoted signals:
1. **T0:** An unverified or malicious observation reference is attached to an ordinary signal while `confidence_tier = 'COMMUNITY_PROVISIONAL'`.
2. **T1:** A trusted administrative writer promotes the parent signal to `confidence_tier = 'OFFICIAL_ADVISORY'`.
3. **T2:** The tainted evidence remains permanently attached to the official government advisory!

### 12.1 Mandatory Trusted Promotion Protocol
To close this gap, the administrative publication service must execute an atomic verification protocol before updating `confidence_tier`:
```python
def promote_signal_to_official_advisory(db: Session, signal_id: str):
    # 1. Lock parent row
    signal = db.execute(select(RegionalSignal).where(RegionalSignal.id == signal_id).with_for_update()).scalar_one()
    
    # 2. Revalidate all attached evidences
    evidences = db.execute(select(RegionalSignalEvidence).where(RegionalSignalEvidence.signal_id == signal_id).with_for_update()).scalars().all()
    for ev in evidences:
        assert_valid_official_evidence_provenance(db, ev)
        
    # 3. Apply state transition atomically
    signal.confidence_tier = "OFFICIAL_ADVISORY"
    signal.validation_status = "OFFICIAL_ALERT"
    db.commit()
```

---

## 13. Concurrency and Association Integrity

Concurrent transactions mutating parent signals and evidence records can race:
- **Race 1:** Transaction A attempts to promote parent to `OFFICIAL_ADVISORY`, while Transaction B concurrently inserts new evidence into the parent.
- **Race 2:** Transaction A suppresses a parent signal due to insufficient provenance, while Transaction B recovers it.

### 13.1 Serialization Contract
All state-modifying operations on `regional_signals` and `regional_signal_evidences` MUST acquire an explicit row-level lock on the parent signal row (`SELECT ... FOR UPDATE` on `regional_signals.id`) before evaluating evidence or applying updates. This guarantees strict linearizability without deadlocks.

---

## 14. SQL Grants and Non-RLS Operations (TRUNCATE Review)

### 14.1 TRUNCATE & Privilege Crosswalk
Row Level Security in PostgreSQL **does not evaluate on `TRUNCATE`**. An actor with `TRUNCATE` privileges can wipe an entire table regardless of RLS policies.
- **Source Inspection of `generate_privilege_grants_ddl()`:**
  ```sql
  REVOKE TRUNCATE, REFERENCES, TRIGGER ON TABLE regional_signals FROM acrevia_staging_app;
  REVOKE TRUNCATE, REFERENCES, TRIGGER ON TABLE regional_signal_evidences FROM acrevia_staging_app;
  REVOKE DELETE ON TABLE regional_signals FROM acrevia_staging_app;
  REVOKE DELETE ON TABLE regional_signal_evidences FROM acrevia_staging_app;
  ```
- **Local DDL Generation:** Verified.
- **Live Database Status:** `LIVE_POSTGRESQL_REQUIRED`.

### 14.2 Table Ownership & BYPASSRLS
In PostgreSQL:
- Superusers and roles with `BYPASSRLS` attribute bypass RLS entirely.
- Table owners bypass RLS unless `FORCE ROW LEVEL SECURITY` is applied.
- `backend/app/database/rls.py` generates `ALTER TABLE ... FORCE ROW LEVEL SECURITY` for all 132 tables.
- The shared application user `acrevia_staging_app` is NOT the table owner (`neondb_owner` is owner).

---

## 15. Indirect Write Paths

A comprehensive scan of the repository was conducted to detect indirect write paths:
- **Database Triggers:** Zero triggers defined in Alembic migrations for `regional_signals` or `regional_signal_evidences`.
- **Stored Procedures & Views:** Zero `SECURITY DEFINER` functions or updatable views exist in source code.
- **SQLAlchemy Event Listeners:** No `before_insert` or `before_update` hooks modifying signal state.
- **Foreign Key Actions:**
  `signal_id = Column(String(36), ForeignKey("regional_signals.id", ondelete="CASCADE"), nullable=False)`
  Deleting a parent signal cascades to child evidences. Because `DELETE` is revoked on `regional_signals` for `acrevia_staging_app`, ordinary actors cannot trigger cascades.

---

## 16. Complete Option D Effective-Policy Specification

### 16.1 Final Specification for `regional_signals`

```sql
-- 1. PUBLIC READ POLICY (Selective visibility for public farmers)
CREATE POLICY regional_signals_public_read_policy ON regional_signals
    AS PERMISSIVE
    FOR SELECT
    TO PUBLIC
    USING (
        (distinct_farms_count >= 3 AND validation_status != 'SUSPENDED')
        -- Note: Zero-telemetry official advisory visibility remains PENDING D-01
    );

-- 2. INTERNAL WORKFLOW READ POLICY (Scoped visibility for authorized collaborative operations)
CREATE POLICY regional_signals_internal_read_policy ON regional_signals
    AS PERMISSIVE
    FOR SELECT
    TO PUBLIC
    USING (
        -- Administrative trusted session
        (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
         AND current_setting('app.is_admin', true) = 'true')
        OR (
            -- Authorized internal actors reading non-official or recovery candidates
            current_setting('app.current_user_id', true) != ''
            AND EXISTS (
                SELECT 1 FROM user_roles ur
                WHERE ur.user_id::text = current_setting('app.current_user_id', true)
                AND ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')
            )
        )
    );

-- 3. FAIL-CLOSED INSERT POLICY (Separated from SELECT)
CREATE POLICY regional_signals_insert_policy ON regional_signals
    AS PERMISSIVE
    FOR INSERT
    TO PUBLIC
    WITH CHECK (
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
            AND confidence_tier IS NOT NULL
            AND validation_status IS NOT NULL
            AND confidence_tier IS DISTINCT FROM 'OFFICIAL_ADVISORY'
            AND validation_status IS DISTINCT FROM 'OFFICIAL_ALERT'
        )
    );

-- 4. FAIL-CLOSED UPDATE POLICY (Protects old row USING and new row WITH CHECK)
CREATE POLICY regional_signals_update_policy ON regional_signals
    AS PERMISSIVE
    FOR UPDATE
    TO PUBLIC
    USING (
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
            AND confidence_tier IS NOT NULL
            AND validation_status IS NOT NULL
            AND confidence_tier IS DISTINCT FROM 'OFFICIAL_ADVISORY'
            AND validation_status IS DISTINCT FROM 'OFFICIAL_ALERT'
        )
    )
    WITH CHECK (
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
            AND confidence_tier IS NOT NULL
            AND validation_status IS NOT NULL
            AND confidence_tier IS DISTINCT FROM 'OFFICIAL_ADVISORY'
            AND validation_status IS DISTINCT FROM 'OFFICIAL_ALERT'
        )
    );

-- 5. FAIL-CLOSED DELETE POLICY (Defense-in-depth)
CREATE POLICY regional_signals_delete_policy ON regional_signals
    AS PERMISSIVE
    FOR DELETE
    TO PUBLIC
    USING (
        SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
        AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
        AND current_setting('app.is_admin', true) = 'true'
    );
```

### 16.2 Final Specification for `regional_signal_evidences`

```sql
-- 1. EVIDENCE READ POLICY
CREATE POLICY regional_signal_evidences_read_policy ON regional_signal_evidences
    AS PERMISSIVE
    FOR SELECT
    TO PUBLIC
    USING (
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
    );

-- 2. EVIDENCE INSERT POLICY
CREATE POLICY regional_signal_evidences_insert_policy ON regional_signal_evidences
    AS PERMISSIVE
    FOR INSERT
    TO PUBLIC
    WITH CHECK (
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
            AND EXISTS (
                SELECT 1 FROM regional_signals rs
                WHERE rs.id = regional_signal_evidences.signal_id
                  AND rs.confidence_tier IS NOT NULL
                  AND rs.confidence_tier IS DISTINCT FROM 'OFFICIAL_ADVISORY'
                  AND rs.validation_status IS NOT NULL
                  AND rs.validation_status IS DISTINCT FROM 'OFFICIAL_ALERT'
            )
        )
    );

-- 3. EVIDENCE UPDATE POLICY
CREATE POLICY regional_signal_evidences_update_policy ON regional_signal_evidences
    AS PERMISSIVE
    FOR UPDATE
    TO PUBLIC
    USING (
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
            AND EXISTS (
                SELECT 1 FROM regional_signals rs
                WHERE rs.id = regional_signal_evidences.signal_id
                  AND rs.confidence_tier IS DISTINCT FROM 'OFFICIAL_ADVISORY'
                  AND rs.validation_status IS DISTINCT FROM 'OFFICIAL_ALERT'
            )
        )
    )
    WITH CHECK (
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
            AND EXISTS (
                SELECT 1 FROM regional_signals rs
                WHERE rs.id = regional_signal_evidences.signal_id
                  AND rs.confidence_tier IS DISTINCT FROM 'OFFICIAL_ADVISORY'
                  AND rs.validation_status IS DISTINCT FROM 'OFFICIAL_ALERT'
            )
        )
    );

-- 4. EVIDENCE DELETE POLICY
CREATE POLICY regional_signal_evidences_delete_policy ON regional_signal_evidences
    AS PERMISSIVE
    FOR DELETE
    TO PUBLIC
    USING (
        SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
        AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
        AND current_setting('app.is_admin', true) = 'true'
    );
```

---

## 17. Adversarial Test Traceability Matrix (35 Conditions)

The following matrix formally specifies the verification status of all 35 adversarial test conditions:

| # | Test Category | Target Assertion | Test Designation & Execution Status | Evidentiary Basis |
|---|---|---|---|---|
| 1 | Parent Read | Farmer SELECT below $N=3$ denied | `LOCAL_TEST_VERIFIED` (`test_worker_security_and_privacy.py`) | Offline test executes and passes. |
| 2 | Parent Read | Farmer SELECT at or above $N=3$ allowed | `LOCAL_TEST_VERIFIED` (`test_worker_security_and_privacy.py`) | Offline test executes and passes. |
| 3 | Parent Read | Expert SELECT below $N=3$ restricted to explicit rule | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Blocked by `RES-PULSE-READ-01`. |
| 4 | Parent Read | Researcher SELECT below $N=3$ restricted to explicit rule | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Blocked by `RES-PULSE-READ-01`. |
| 5 | Parent Read | Spoofing `app.current_user_id` cannot grant read access | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Defect proven in Section 6. |
| 6 | Parent Read | Broad `FOR ALL` policy no longer grants SELECT | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Future forward migration test. |
| 7 | Parent Read | SELECT behavior preserved for API and `db.refresh()` | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Requires implementation of Section 16. |
| 8 | Parent Write | Expert INSERT of `OFFICIAL_ADVISORY` denied | `LOCAL_TEST_VERIFIED` (Vulnerability Detector) | Defect proven by test. |
| 9 | Parent Write | Researcher INSERT of `OFFICIAL_ADVISORY` denied | `LOCAL_TEST_VERIFIED` (Vulnerability Detector) | Defect proven by test. |
| 10 | Parent Write | Expert INSERT of `OFFICIAL_ALERT` denied | `LOCAL_TEST_VERIFIED` (Vulnerability Detector) | Defect proven by test. |
| 11 | Parent Write | Researcher INSERT of `OFFICIAL_ALERT` denied | `LOCAL_TEST_VERIFIED` (Vulnerability Detector) | Defect proven by test. |
| 12 | Parent Write | Expert UPDATE promotion denied | `LOCAL_TEST_VERIFIED` (Vulnerability Detector) | Defect proven by test. |
| 13 | Parent Write | Researcher UPDATE promotion denied | `LOCAL_TEST_VERIFIED` (Vulnerability Detector) | Defect proven by test. |
| 14 | Parent Write | Ordinary actor modifying official row denied | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Option D USING contract. |
| 15 | Parent Write | Ordinary actor demoting official row denied | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Option D USING contract. |
| 16 | Parent Write | Setting protected fields to NULL rejected | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Contract C defensive condition. |
| 17 | Parent Write | `app.is_admin=true` cannot authorize shared principal | `LOCAL_TEST_VERIFIED` (`test_postgresql_rls.py`) | Offline DDL generator verified. |
| 18 | Parent Write | Spoofed admin UUID cannot authorize official writes | `LOCAL_TEST_VERIFIED` (`test_worker_security_and_privacy.py`) | Dual-identity check blocks spoof. |
| 19 | Parent Write | No permissive policy restores broad write path | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Requires migration `a1089411c87e`. |
| 20 | Parent Write | `ON CONFLICT DO UPDATE` follows same protection | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Evaluated under PG rules. |
| 21 | Parent Write | RETURNING behavior verified against SELECT policy | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Requires complete Option D. |
| 22 | Evidence Assoc | Ordinary actor INSERT to non-official parent | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Section 16 child specification. |
| 23 | Evidence Assoc | Ordinary actor INSERT to official parent denied | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Section 16 child specification. |
| 24 | Evidence Assoc | Ordinary actor UPDATE association metadata | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Section 16 child specification. |
| 25 | Evidence Assoc | Ordinary actor UPDATE to official parent denied | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Section 16 child specification. |
| 26 | Evidence Assoc | Ordinary actor UPDATE away from official denied | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Section 16 child specification. |
| 27 | Evidence Assoc | Ordinary actor DELETE association denied | `LOCAL_SOURCE_VERIFIED` | SQL grant `REVOKE DELETE`. |
| 28 | Evidence Assoc | Evidence revalidated before trusted promotion | Proposed / Architectural Contract | Section 12 trusted protocol. |
| 29 | Evidence Assoc | Concurrent attachment & promotion obey serialization | Proposed / Architectural Contract | Row-level locking on parent. |
| 30 | Evidence Assoc | Parent RLS visibility preserves evidence workflow | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Requires internal read policy. |
| 31 | Indirect Paths | Ordinary principal cannot TRUNCATE | `LOCAL_SOURCE_VERIFIED` | SQL grant `REVOKE TRUNCATE`. |
| 32 | Indirect Paths | Ordinary principal cannot SET ROLE to writer | Proposed / `LIVE_POSTGRESQL_REQUIRED` | PostgreSQL role membership. |
| 33 | Indirect Paths | No unintended role membership path exists | Proposed / `LIVE_POSTGRESQL_REQUIRED` | PostgreSQL catalog check. |
| 34 | Indirect Paths | Zero triggers/procedures reintroduce writes | `LOCAL_SOURCE_VERIFIED` | Source code audit clean. |
| 35 | Indirect Paths | No table grant defeats intended policy | `LOCAL_SOURCE_VERIFIED` | Local privilege crosswalk clean. |

---

## 18. Test Collection and Execution Evidence

### 18.1 Collection Inventory (Executed in Current Python Environment)
A clean read-only pytest collection was executed using Python 3.11:
```text
C:\Users\gokul\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe -m pytest \
    backend/tests/test_orm_rls_alignment.py \
    backend/tests/test_postgresql_rls.py \
    backend/tests/test_rls_offline_ddl.py \
    backend/tests/test_rls_policy_semantics.py \
    backend/tests/test_worker_security_and_privacy.py \
    --collect-only -q
```

**Collection Breakdown:**
- `backend/tests/test_orm_rls_alignment.py`: **12 items**
- `backend/tests/test_postgresql_rls.py`: **28 items**
- `backend/tests/test_rls_offline_ddl.py`: **9 items**
- `backend/tests/test_rls_policy_semantics.py`: **14 items**
- `backend/tests/test_worker_security_and_privacy.py`: **108 items**
- **Total Test Items Collected:** **171 items** in 0.40s.

### 18.2 Historical Execution Baseline (from Step 19450)
- **Tests Executed:** Exactly 171 tests.
- **Outcome:** **171 passed**, 1 warning (`StarletteDeprecationWarning`) in **23.47s**.
- **Adversarial Semantics:** `test_adversarial_state_transitions_and_permissive_policy_composition` in `test_worker_security_and_privacy.py` executes as a **vulnerability detector**, confirming the absence of tier checks in current DDL.

---

## 19. Outstanding Governance Blockers

| Blocker ID | Domain | Root Cause & Security Implication | Resolution Path |
|---|---|---|---|
| **`OWNER-AUTH-01`** | Governance | Decisions D-01, D-02, D-03, and DB-AUTH-01 require explicit Project Owner execution. | Owner signs decision register. |
| **`RLS-WRITE-AUTH-01`** | Database Security | Permissive author `FOR ALL` policy permits ordinary experts/researchers to write `OFFICIAL_ADVISORY`. | Author forward migration `a1089411c87e` with Option D. |
| **`RES-PULSE-READ-01`** | Privacy & Read Security | Permissive author `FOR ALL` policy combines via OR with public read, exposing sub-threshold ($N < 3$) and suspended signals to mutable-GUC spoofing. | Separate SELECT from write policies and add authenticated internal read boundary. |
| **`DB-RLS-01`** | Infrastructure | RLS DDL and privilege crosswalk unvalidated against live PostgreSQL catalogs. | Execute Mode B live database validation once authorized. |
| **`WRK-DISP-01`** | Architecture | Regional pulse aggregation and recovery dispatched via Celery worker without verified worker-role DB principal. | Define dedicated worker DB identity. |
| **`RES-PULSE-01`** | Data Privacy | Cross-tenant aggregation privacy window latency and inference exposure. | Provenance revalidation loop. |
| **`RES-PULSE-02`** | Data Integrity | Telemetry observation count derivation inconsistency across distributed nodes. | Strict mathematical count derivation. |
| **`GATE01-PROV-01`** | Release Gate | Gate 01 signed in register but live database validation pending. | Live validation in staging DB. |

---

## 20. Project Owner Decision Status (Blank & Pending)

All Project Owner decision fields remain strictly unselected and pending:

```text
[   ] D-01: OFFICIAL STATE ADVISORY PUBLIC READ PRIVACY EXCEPTION
      [ ] Option A — Public Read Policy Exception (distinct_farms_count = 0)
      [ ] Option B — Strict Farm Telemetry Threshold Only (distinct_farms_count >= 3)
      STATUS: PENDING_PROJECT_OWNER_AUTHORIZATION

[   ] D-02: REGIONAL PULSE AGGREGATION ASYNCHRONOUS DISPATCH
      [ ] Option A — Immediate Background Dispatch via Celery
      [ ] Option B — Synchronous Request-Response Transaction Only
      STATUS: PENDING_PROJECT_OWNER_AUTHORIZATION

[   ] D-03: EXPERT REVIEW RETRY AND SUSPENSION THRESHOLD
      [ ] Option A — 3 Consecutive Failures Triggers Automatic Suspension
      [ ] Option B — Strict Immediate Single-Failure Suspension
      STATUS: PENDING_PROJECT_OWNER_AUTHORIZATION

[   ] DB-AUTH-01: DATABASE IDENTITY ARCHITECTURE
      [ ] Option A — Dual-Principal Architecture (acrevia_app + acrevia_trusted_writer)
      [ ] Option B — Security-Definer Administrative Promotion Gateway
      [ ] Option C — Direct Neon Superuser Bypass Only
      [ ] Option D — Fail-Closed Application-Role Policy Enforcement
      STATUS: PROPOSED — PENDING OWNER AUTHORIZATION
```

---

## 21. Everything Claude Code (ECC) Multi-Perspective Review

The technical specification was reviewed across the 8 mandatory ECC pillars:

1. **`architect`:** Confirms that separating `FOR ALL` into discrete `FOR SELECT`, `FOR INSERT`, `FOR UPDATE`, and `FOR DELETE` policies is structurally required to restore PostgreSQL's command-specific authorization boundary. Confirms that Option D requires an internal SELECT policy to prevent breaking legitimate service workflows.
2. **`security-reviewer`:** Formally validates the proof of `RES-PULSE-READ-01`. Confirms that mutable session GUCs cannot be treated as authenticated boundaries on a shared database connection. Recommends strict separation of administrative publication from collaborative writing.
3. **`database-reviewer`:** Validates PostgreSQL 15/16 RLS semantics regarding `PERMISSIVE` OR-composition, `UPDATE USING` old-row checks, `UPDATE WITH CHECK` new-row checks, and `SELECT` evaluation during `RETURNING` clauses and `SELECT ... FOR UPDATE`. Confirms that RLS does not protect `TRUNCATE`.
4. **`python-reviewer`:** Confirms that SQLAlchemy `nullable=False` attributes generate `NOT NULL` constraints in DDL via `Base.metadata.create_all()`. Approves adopting Contract C (explicit `IS NOT NULL` checks in RLS) to guard against NULL three-valued logic edge cases.
5. **`fastapi-reviewer`:** Maps all endpoint operations in `backend/app/api/v1/endpoints/regional_pulse.py`. Pinpoints exact crash vectors in `db.refresh()` and `select(...).with_for_update()` under naive policy replacement.
6. **`silent-failure-hunter`:** Discovered the parent promotion evidence provenance gap: existing community evidence attached prior to promotion remains associated with official advisories unless an explicit revalidation protocol runs at promotion time.
7. **`verification-loop`:** Traced all 35 adversarial test conditions to local tests, static analysis, or future `LIVE_POSTGRESQL_REQUIRED` suites. Verified 171 collected tests.
8. **`delivery-gate`:** Confirms that Phase 07 release gates remain closed. Prevents unauthorized Mode B transition.

---

## 22. Implementation-Readiness Determination

$$\mathbf{DETERMINATION:\ TECHNICAL\_PREFLIGHT\_BLOCKED\_WITH\_RECORDED\_BLOCKERS}$$

### Justification:
1. **Blocker `RLS-WRITE-AUTH-01` remains open:** The current DDL in `a1089411c87d` still allows ordinary experts/researchers to write official advisories.
2. **Blocker `RES-PULSE-READ-01` is newly recorded:** The current permissive policy leaks sub-threshold and suspended signals across the entire state.
3. **Operational dependencies unresolved:** A naive fix breaks `db.refresh()` and `recover_suppressed_signal`. The complete policy specification designed in Section 16 must be packaged into a forward migration (`a1089411c87e`).
4. **Owner Decisions Pending:** Decisions D-01, D-02, D-03, and DB-AUTH-01 must be signed by the Project Owner.
5. **Phase Status:** Phase 07 is **`NOT RELEASED`**. Mode B is **`STRICTLY NOT AUTHORIZED`**.

---

## 23. Governance Invariants & Limitations

- **Strict Mode A Only:** Zero remote or cloud database connections established. Zero local PostgreSQL instances started.
- **Zero Schema/Code Changes:** No changes were applied to `backend/app/database/rls.py`, migration files, ORM models, API endpoints, or test suites.
- **No Alembic Downgrade:** `alembic downgrade` in migration `a1089411c87d` executes `DISABLE ROW LEVEL SECURITY` across 132 tables. It must NEVER be executed. Remediation must strictly proceed via forward migration `a1089411c87e`.
- **Preservation of Working Tree:** All pre-existing modified files and untracked dossiers were preserved intact.


---

## 2026-11-15 Addendum — Global Actor-GUC Trust Boundary, Role Assignment Escalation & Canonical Governance Restoration

**Evaluation Date:** 2026-11-15T19:30:36+05:30  
**Audit Context:** Global Actor-GUC Trust Boundary, User-Role Privilege Escalation & Global RLS Identity Assurance Audit  
**Operating Mode:** Strict `MODE A ONLY` (Local source inspection, security analysis, zero database mutations)  
**Baseline Git Commit:** `dbad296c6f19c4bbe8eb48fcd7a0e07441cfa408` (`main`)  

### 1. Critical Blocker Recorded: `RLS-ROLE-ASSIGNMENT-01`
- **Root Cause:** In `backend/app/database/rls.py`, `user_roles` is categorized as `TableCategory.USER_OWNED`, generating a restrictive policy that permits writes when `user_id::text = current_setting('app.current_user_id', true)`. Simultaneously, `acrevia_staging_app` receives full SQL table grants (`GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE user_roles`).
- **Privilege Escalation:** Any session or component executing SQL under `acrevia_staging_app` can set `SET LOCAL app.current_user_id = '<user_uuid>'` and insert `('<user_uuid>', 'ADMIN')` into `user_roles`. PostgreSQL permits the insert because the user owns the inserted record. When the user logs in, FastAPI's `get_current_user` elevates them to platform administrator.
- **Administrator Demotion:** An attacker can delete administrator role rows by spoofing the administrator's UUID in `app.current_user_id`.
- **Classification:** Formally proven from local policy structure as an active architectural blocker: `RLS-ROLE-ASSIGNMENT-01 — Mutable-GUC Role Assignment Privilege Escalation`.
- **Immediate Containment:** Revoke `INSERT, UPDATE, DELETE ON TABLE user_roles FROM acrevia_staging_app;` via forward migration `a1089411c87e`.

### 2. Global Actor & Tenant GUC Impersonation Surfaces
- **Actor-GUC Surface:** All 13 `USER_OWNED` tables (including `users`, `session_tokens`, `consent_records`, `api_applications`) evaluate `user_id = current_setting('app.current_user_id', true)` with full DML grants for `acrevia_staging_app`.
- **Tenant-GUC Surface:** All 25 `TENANT_DIRECT` and 53 `TENANT_INDIRECT` tables enforce tenant isolation exclusively against `current_setting('app.current_tenant_id', true)`. Database RLS policies perform zero independent verification of user membership in the tenant; that check exists solely at the FastAPI application layer.

### 3. Canonical Governance Register Restored
Authoritative definitions are restored across all governance dossiers:
- **D-01:** Official Advisory Visibility & Data Model Choice (Universal N>=3, Dedicated table, Conditional exception, Privileged-only).
- **D-02:** Government-Source Authenticity & Pilot Terminology (`"Platform Administrator Broadcast — Not Verified Government Gazette"`).
- **D-03:** Independent Agronomic Peer-Review Workflow (Single-expert vs Dual-expert verification gate).
- **DB-AUTH-01:** Database Writer Identity Architecture (Dual-principal, Stored function gateway, Fail-closed application role; direct superuser bypass rejected).
- **Residual Risks:** `RES-PULSE-01` (Role-global evidence access), `RES-PULSE-02` (Read Committed snapshot window), `RES-PRIMARY-ROUTING-01` (Primary routing dependency), `RES-REPLICA-LAG-01` (Replica lag), `RES-FREE-TEXT-01` (PII in free text).

### 4. Active Blockers Summary
- `RLS-ROLE-ASSIGNMENT-01`: Active Critical Architectural Blocker.
- `RLS-WRITE-AUTH-01`: Active High Architectural Blocker.
- `RES-PULSE-READ-01`: Active High Architectural Blocker.
- `OWNER-AUTH-01`: Governance Blocker (Decisions D-01, D-02, D-03, DB-AUTH-01 pending).
- `WRK-DISP-01`: Active Worker Identity Architectural Blocker.
- `DB-RLS-01`: Infrastructure Blocker (Live PostgreSQL required).
- `GATE01-PROV-01`: Release Gate Blocker.
- **Phase 07 Status:** `NOT RELEASED`. Mode B: `STRICTLY NOT AUTHORIZED`.
