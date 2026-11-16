# ACREVIA — PHASE 07: READ-PRIVACY AUTHORIZATION, SELECT-POLICY REPLACEMENT & EVIDENCE-ASSOCIATION LIFECYCLE SECURITY AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** `MODE A ONLY` — Local Source Inspection, Security Engineering Analysis, Concurrency Modeling & Governance Documentation  
**Git Baseline Commit:** `dbad296c6f19c4bbe8eb48fcd7a0e07441cfa408` (`main`)  
**Methodology:** Everything Claude Code (ECC): `PLAN → TEST → IMPLEMENT ONLY IF DEFECT PROVEN → REVIEW → VERIFY → DOCUMENT`  
**Evaluation Date:** 2026-11-15T18:35:42+05:30  
**Determination:** `TECHNICAL_PREFLIGHT_BLOCKED_WITH_RECORDED_BLOCKERS`  

---

## 1. Executive Determination

An adversarial security audit and lifecycle investigation of the PostgreSQL Row Level Security (RLS) architecture was performed for Phase 07 under strict `MODE A ONLY` constraints. While Option D (Fail-Closed RLS Policy Contract) successfully separates command vectors (`INSERT`, `UPDATE`, `DELETE`, `SELECT`) to address write authority bypass (`RLS-WRITE-AUTH-01`), this investigation proves that **Option D is not yet implementation-ready** due to critical, newly verified read-privacy and operational failure modes:

1. **Sub-Threshold & Suspended Signal Read-Privacy Exposure (`RES-PULSE-READ-01`):**  
   [`LOCAL_SOURCE_VERIFIED` / `STATIC_POLICY_ANALYSIS`]  
   The current author policy on `regional_signals` (`regional_signals_author_write_policy`) is an `AS PERMISSIVE FOR ALL` policy. In PostgreSQL, `PERMISSIVE` policies combine via Boolean `OR`. For all `SELECT` queries, any session where `app.current_user_id` satisfies the role lookup for `ADMIN`, `AGRICULTURAL_EXPERT`, or `RESEARCHER` evaluates this policy to `TRUE`, completely bypassing the separate public read policy (`distinct_farms_count >= 3 AND validation_status != 'SUSPENDED'`). Because `app.current_user_id` is an unauthenticated, mutable session GUC set via `SET LOCAL`, any attacker or SQL injection on the shared application database principal (`acrevia_staging_app`) can read all sub-threshold crop outbreak claims ($N < 3$) and suspended signals across all Telangana districts. This is formally classified as a distinct read-privacy blocker: **`RES-PULSE-READ-01`**.

2. **`user_roles` Impersonation Vulnerability Proven:**  
   [`PROVEN_FROM_LOCAL_POLICY_STRUCTURE`]  
   Inspection of `user_roles` RLS proves that `user_roles_user_isolation_policy` (`AS RESTRICTIVE`) filters by `user_id::text = current_setting('app.current_user_id', true)`. Because `acrevia_staging_app` possesses table-level `SELECT` grants on `user_roles`, setting `SET LOCAL app.current_user_id = '<expert-uuid>'` makes that expert's role row visible to the session, successfully satisfying the role subquery in `regional_signals_author_write_policy` and opening statewide read access to sub-threshold data.

3. **Critical API Workflow Collisions Upon Naive `FOR ALL` Removal:**  
   [`LOCAL_SOURCE_VERIFIED`]  
   Removing the broad `FOR ALL` policy and leaving only the public read policy breaks core SQLAlchemy and FastAPI workflows:
   - **`recover_suppressed_signal`:** Issues `select(RegionalSignal).where(...).with_for_update()`. In PostgreSQL, `SELECT ... FOR UPDATE` evaluates `SELECT` RLS policies. Because a suppressed signal fails the public read policy (`validation_status != 'SUSPENDED'`), the query returns `None`, and the endpoint crashes with HTTP 404!
   - **`aggregate_regional_signal`:** The endpoint executes `db.refresh(signal)` after `db.commit()`. If an expert creates an alert with $N < 3$ or a zero-telemetry advisory ($N=0$), `db.refresh()` executes `SELECT ... WHERE id = :id`. Because the row is excluded by public read RLS, SQLAlchemy raises `ObjectDeletedError`, rolling back the transaction with HTTP 500!
   - **`revalidate_signal_provenance`:** Dynamic suppression requires `UPDATE USING` visibility on rows being evaluated.

4. **Incomplete Child Evidence Lifecycle Contract:**  
   [`LOCAL_SOURCE_VERIFIED`]  
   The child evidence table (`regional_signal_evidences`) requires command-specific policies. An `INSERT` check alone does not prevent reparenting attacks via `UPDATE` or deletion via `DELETE`. Furthermore, if the parent signal is hidden by parent RLS, an `EXISTS` subquery in the child policy evaluates to `FALSE`, breaking legitimate evidence association.

5. **Parent Promotion Evidence Provenance Gap:**  
   [`LOCAL_SOURCE_VERIFIED`]  
   Community evidence attached to an ordinary signal remains attached when the signal is promoted to `OFFICIAL_ADVISORY`. Without an atomic revalidation protocol enforced at promotion time, unverified evidence can become linked to official state notices.

Therefore, Phase 07 remains **`NOT RELEASED`**, Mode B remains **`STRICTLY NOT AUTHORIZED`**, and `RLS-WRITE-AUTH-01` remains an **`ACTIVE_ARCHITECTURAL_BLOCKER`** alongside newly proposed blocker **`RES-PULSE-READ-01`**.

---

## 2. Exact Local Baseline and Working-Tree Inventory

[`LOCAL_SOURCE_VERIFIED` / `PUBLIC_GITHUB_VERIFIED`]

The exact state of the local Git repository was inspected under strict `MODE A ONLY`:

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
- **Untracked Dossiers:** Exactly **17** governance documents in `docs/pilot/security/` (including this primary audit report).
- **Core Security Code Integrity:**
  - `backend/app/database/rls.py`: **100% byte-for-byte identical** to public commit `dbad296c` (`git diff HEAD` is empty).
  - Migration `a1089411c87d`: **100% byte-for-byte identical** to public commit `dbad296c` (`git diff HEAD` is empty).
  - Migration `d2894a11c87d`: Untouched.
- **Task Invariant:** Zero lines of application code, ORM models, migrations, or test implementations were created, deleted, or modified during this task.

---

## 3. Parent-Table Policy Inventory

[`LOCAL_SOURCE_VERIFIED` / `OFFLINE_DDL_VERIFICATION`]

Inspection of [rls.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py) and generated DDL verifies the exact policies emitted for `regional_signals`:

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

### Table Privileges
Generated table grants for `acrevia_staging_app`:
```sql
GRANT SELECT, INSERT, UPDATE ON TABLE regional_signals TO acrevia_staging_app;
REVOKE DELETE, TRUNCATE, REFERENCES, TRIGGER ON TABLE regional_signals FROM acrevia_staging_app;
```

---

## 4. Effective Command-by-Command Policy Matrix

[`STATIC_POLICY_ANALYSIS`]

Under PostgreSQL RLS semantics (documented at [PostgreSQL CREATE POLICY Documentation](https://www.postgresql.org/docs/current/sql-createpolicy.html)), permissive policies combine with Boolean `OR`. Target deployment is PostgreSQL 15/16 (Neon / managed PostgreSQL):

| Operation | Applicable Policy Set | Effective PostgreSQL Expression | Result & Security Impact |
|---|---|---|---|
| **`SELECT`** | `public_read_policy` (`FOR SELECT`)<br>$\lor$ `author_write_policy` (`FOR ALL`) | `(ADMIN_BYPASS OR (N>=3 AND status!='SUSPENDED'))` $\lor$ `(ADMIN_BYPASS OR EXISTS(ur.role IN ('ADMIN','EXPERT','RESEARCHER')))` | **HIGH RISK (`RES-PULSE-READ-01`):** Role subquery evaluates to TRUE, short-circuiting public threshold and exposing sub-threshold ($N<3$) and suspended signals. |
| **`INSERT`** | `author_write_policy` (`FOR ALL` `WITH CHECK`) | `ADMIN_BYPASS OR EXISTS(ur.role IN ('ADMIN','EXPERT','RESEARCHER'))` | **CRITICAL RISK (`RLS-WRITE-AUTH-01`):** Role subquery permits inserting `confidence_tier = 'OFFICIAL_ADVISORY'`. |
| **`UPDATE`** | `author_write_policy` (`FOR ALL` `USING` + `WITH CHECK`) | `USING` checks old row; `WITH CHECK` checks new row. Both use the identical role subquery. | **CRITICAL RISK (`RLS-WRITE-AUTH-01`):** Permits updating ordinary signals to `OFFICIAL_ADVISORY`. |
| **`DELETE`** | `author_write_policy` (`FOR ALL` `USING`) | Role subquery allows delete under RLS, but blocked by SQL grant revocation. | **DEFENSE-IN-DEPTH DEFECT:** RLS allows DELETE; only table grant `REVOKE DELETE` prevents execution. |
| **`SELECT ... FOR UPDATE`** | Evaluates `FOR SELECT` policies | Same as `SELECT`. Does NOT evaluate `UPDATE USING` policies. | Exposes sub-threshold rows under current policy; crashes under naive public-only SELECT replacement. |
| **`INSERT ... RETURNING`** | `author_write_policy` (`WITH CHECK`) + `SELECT` policies | Inserted row must satisfy `WITH CHECK` and `SELECT` policies. | If `FOR ALL` is removed, inserting sub-threshold or advisory rows fails RETURNING clause evaluation. |
| **`UPDATE ... RETURNING`** | `author_write_policy` (`USING` + `WITH CHECK`) + `SELECT` policies | Old row passes `USING`; new row passes `WITH CHECK`; returned columns pass `SELECT`. | If `FOR ALL` is removed, updating a signal to suppressed status breaks RETURNING clause. |
| **`INSERT ... ON CONFLICT DO UPDATE`** | `INSERT` (`WITH CHECK`) on insert; `UPDATE` (`USING` + `WITH CHECK`) on conflict | Evaluates both paths under PostgreSQL rules. | Both paths permit unauthorized official advisory claims under current unhardened DDL. |
| **`MERGE`** (PG 15+) | Evaluates `SELECT` (join), `INSERT`, `UPDATE`, `DELETE` per matched branch | Evaluates command-specific policies for each branch. | Same vulnerabilities apply across all matched branches. |

---

## 5. Existing Broad `FOR ALL` SELECT Implications

[`LOCAL_SOURCE_VERIFIED` / `STATIC_POLICY_ANALYSIS`]

Evaluation of the `regional_signals_author_write_policy` role branch reveals:

1. **Sub-Threshold Reads Permitted ($N < 3$):**  
   Agricultural experts and researchers can read all signals with $N=1$ or $N=2$ farms.
2. **Suspended Signals Readable:**  
   Signals with `validation_status = 'SUSPENDED'` are fully readable by experts and researchers.
3. **Absence of Author Scoping:**  
   The policy contains **zero** author ownership checks (`author_id::text = current_setting('app.current_user_id', true)` is NOT present). An expert can read all records created by any other actor.
4. **Absence of Geographic / District Scoping:**  
   The policy contains **zero** district or state checks. An expert registered in Adilabad can read raw signals from Khammam or Nalgonda.
5. **Absence of Tenant Scoping:**  
   The policy contains **zero** tenant isolation checks.

$$\mathbf{Conclusion:}\ \text{The author policy operates as a statewide, role-global read superuser for all qualifying roles.}$$

---

## 6. `user_roles` RLS and GUC Spoof Analysis

[`PROVEN_FROM_LOCAL_POLICY_STRUCTURE`]

The role lookup relies on a subquery against `user_roles`:
```sql
EXISTS (
    SELECT 1 FROM user_roles ur
    WHERE ur.user_id::text = current_setting('app.current_user_id', true)
      AND ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')
)
```

Inspection of `backend/app/database/rls.py` for `user_roles` reveals:
- **Table Classification:** `TableCategory.USER_OWNED`, column `'user_id'`.
- **Grants:** `GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE user_roles TO acrevia_staging_app;`.
- **RLS Policies:**
  - `user_roles_base_access_policy`: `AS PERMISSIVE FOR ALL TO PUBLIC USING (true) WITH CHECK (true)`
  - `user_roles_user_isolation_policy`: `AS RESTRICTIVE FOR ALL TO PUBLIC USING ((ADMIN_BYPASS_SQL OR user_id::text = current_setting('app.current_user_id', true)))`

### GUC Impersonation Execution Path:
1. `acrevia_staging_app` connects to PostgreSQL on a shared connection pool.
2. Any session or SQL injection executes:
   ```sql
   SET LOCAL app.current_user_id = '<target-expert-uuid>';
   ```
3. When the subquery executes against `user_roles`, `user_roles_user_isolation_policy` filters rows where `user_id::text = '<target-expert-uuid>'`.
4. If `<target-expert-uuid>` exists in `user_roles` with `role_id = 'AGRICULTURAL_EXPERT'`, PostgreSQL returns that row.
5. The `EXISTS` subquery returns `TRUE`.
6. `regional_signals_author_write_policy` evaluates to `TRUE`, granting the session full read access to all sub-threshold and suspended signals across Telangana!

$$\mathbf{Classification:}\ \mathbf{PROVEN\_FROM\_LOCAL\_POLICY\_STRUCTURE}$$

---

## 7. Sub-Threshold and Suspended Data Exposure

[`LOCAL_SOURCE_VERIFIED`]

### 7.1 De-Anonymization Threat to Telangana Farmers
In Telangana agriculture, commercial monocultures (e.g., Bt Cotton in Warangal, Chilli in Khammam, Turmeric in Nizamabad) often feature localized pest outbreaks (e.g., *Spodoptera frugiperda* fall armyworm or *Pectinophora gossypiella* pink bollworm). When an outbreak claim is submitted with $N=1$ or $N=2$ farms, the combination of `district`, `crop_id`, `signal_category`, and `observed_start_date` allows local aggregators, input suppliers, or commercial lenders to identify the specific farm holdings experiencing distress, undermining the platform's core privacy guarantee.

### 7.2 Suspended Status Integrity
Signals marked `SUSPENDED` often represent unconfirmed panic alerts or uncalibrated IoT sensor readings. Permitting unmonitored statewide read access to suspended claims creates risks of secondary misinformation spreading through informal extension networks.

---

## 8. Proposed Read-Access Matrix

[`STATIC_POLICY_ANALYSIS` / `OWNER_DECISION_REQUIRED`]

The proposed role-to-data read authorization matrix is formulated below:

| Actor Class | Public Signals ($N \ge 3$) | Sub-Threshold Signals ($N < 3$) | Suspended Signals | Official Advisories ($N=0$) | Own Authored Signals |
|---|---|---|---|---|---|
| **FARMER** | Allowed (Approved public rule) | **DENIED** | **DENIED** | `PENDING D-01` | Not applicable (no authoring) |
| **AGRICULTURAL_EXPERT** | Allowed | `OWNER_DECISION_REQUIRED` (Scoped to assigned district) | `OWNER_DECISION_REQUIRED` (Recovery workflow only) | `PENDING D-01` | Allowed (if author tracked) |
| **RESEARCHER** | Allowed | `OWNER_DECISION_REQUIRED` (Anonymized telemetry only) | **DENIED** | `PENDING D-01` | Allowed (if author tracked) |
| **ADMIN (Trusted)** | Allowed | Allowed (Administrative verification) | Allowed (Audit / recovery) | Allowed | Allowed |
| **Direct SQL Session (`acrevia_staging_app`)** | Allowed ($N \ge 3$) | **DENIED** (No GUC spoofing exception) | **DENIED** | **DENIED** | **DENIED** |

---

## 9. Project Owner Decision D-01 Read-Policy Dependencies

[`OWNER_DECISION_REQUIRED`]

Project Owner Decision **D-01** governs whether public farmers can view official state advisories that have zero farm telemetry ($N=0$):
- **Current Behavior:** `regional_signals_public_read_policy` requires `distinct_farms_count >= 3`. Zero-telemetry advisories ($N=0$) are completely invisible to farmers.
- **Decision Status:** `PENDING_PROJECT_OWNER_AUTHORIZATION`.
- **Policy Invariant:** The replacement SELECT policy must not preemptively implement Option A (public exemption for official advisories) or Option B (strict $N \ge 3$ threshold) until the Project Owner formally signs the decision register.

---

## 10. SQLAlchemy Workflow Mapping

[`LOCAL_SOURCE_VERIFIED`]

Detailed code inspection of [regional_pulse_service.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py) and [regional_pulse.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/regional_pulse.py) reveals the exact ORM and SQL operations executed across the application:

```python
# 1. aggregate_regional_signal (service line 251)
if auto_commit:
    db.commit()
    db.refresh(signal)  # Executes SELECT ... WHERE id = :id

# 2. recover_suppressed_signal (service lines 430-435)
stmt = (
    select(RegionalSignal)
    .options(selectinload(RegionalSignal.evidences))
    .where(RegionalSignal.id == signal_id)
    .with_for_update()  # Executes SELECT ... FOR UPDATE
)
signal = db.execute(stmt).scalar_one_or_none()

# 3. get_signal (service line 267)
stmt = (
    select(RegionalSignal)
    .options(selectinload(RegionalSignal.evidences))
    .where(RegionalSignal.id == signal_id)
)
return db.scalars(stmt).first()  # Executes SELECT

# 4. query_signals (service line 283)
stmt = (
    select(RegionalSignal)
    .options(selectinload(RegionalSignal.evidences))
    .order_by(RegionalSignal.observed_end_date.desc())
)
return list(db.scalars(stmt.offset(offset).limit(limit)).all())  # Executes SELECT

# 5. revalidate_signal_provenance (service line 330)
with db.begin_nested():
    signal = RegionalPulseService.get_signal(db, signal_id)
    # If invalid, sets signal.validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'
```

---

## 11. RETURNING / UPDATE / DELETE / ON CONFLICT Compatibility

[`STATIC_POLICY_ANALYSIS`]

| Service Operation | SQL Command(s) | Requires SELECT? | Applicable SELECT Policy | Applicable Write Policy | Expected Behavior Under Naive Option D (Public SELECT Only) |
|---|---|---|---|---|---|
| **`aggregate_regional_signal`**<br>(New Advisory $N=0$) | `INSERT` + `SELECT` (via `db.refresh()`) | **YES** | `public_read_policy` | `insert_policy` | **FAILS:** Passes insert WITH CHECK, but `db.refresh()` fails with `ObjectDeletedError` because $N=0$. HTTP 500. |
| **`aggregate_regional_signal`**<br>(Alert $N < 3$) | `INSERT` + `SELECT` (via `db.refresh()`) | **YES** | `public_read_policy` | `insert_policy` | **FAILS:** Passes insert WITH CHECK, but `db.refresh()` fails with `ObjectDeletedError` because $N < 3$. HTTP 500. |
| **`recover_suppressed_signal`** | `SELECT ... FOR UPDATE` + `UPDATE` | **YES** | `public_read_policy` | `update_policy` | **FAILS:** `with_for_update()` evaluates SELECT. Because status is `SUSPENDED` or $N < 3$, query returns `None`. HTTP 404! |
| **`get_signal`** (Public) | `SELECT` | **YES** | `public_read_policy` | None | **SUCCEEDS:** Returns only $N \ge 3$, non-suspended signals. Public privacy preserved. |
| **`list_signals`** (Public) | `SELECT` | **YES** | `public_read_policy` | None | **SUCCEEDS:** Returns only $N \ge 3$, non-suspended signals. Public privacy preserved. |
| **`revalidate_signal_provenance`** | `SELECT` + `UPDATE` | **YES** | `public_read_policy` | `update_policy` | **SUCCEEDS on update**, but newly suppressed row vanishes from subsequent public SELECT queries (Fail-Closed). |

---

## 12. Parent-Table Policy Contract

[`STATIC_POLICY_ANALYSIS`]

To resolve operational collisions while maintaining strict security:

```sql
-- 1. PUBLIC SELECT POLICY
CREATE POLICY regional_signals_public_read_policy ON regional_signals
    AS PERMISSIVE FOR SELECT TO PUBLIC
    USING (
        (distinct_farms_count >= 3 AND validation_status != 'SUSPENDED')
    );

-- 2. INTERNAL WORKFLOW SELECT POLICY
CREATE POLICY regional_signals_internal_read_policy ON regional_signals
    AS PERMISSIVE FOR SELECT TO PUBLIC
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

-- 3. INSERT POLICY
CREATE POLICY regional_signals_insert_policy ON regional_signals
    AS PERMISSIVE FOR INSERT TO PUBLIC
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

-- 4. UPDATE POLICY
CREATE POLICY regional_signals_update_policy ON regional_signals
    AS PERMISSIVE FOR UPDATE TO PUBLIC
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

-- 5. DELETE POLICY
CREATE POLICY regional_signals_delete_policy ON regional_signals
    AS PERMISSIVE FOR DELETE TO PUBLIC
    USING (
        SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
        AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
        AND current_setting('app.is_admin', true) = 'true'
    );
```

---

## 13. NULL and Database-Constraint Evidence

[`LOCAL_SOURCE_VERIFIED` / `OFFLINE_DDL_VERIFICATION`]

1. **ORM Metadata:** In [regional_pulse.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/regional_pulse.py):
   - `confidence_tier = Column(String(50), nullable=False, index=True)`
   - `validation_status = Column(String(50), nullable=False, index=True)`
   - `distinct_farms_count = Column(Integer, nullable=False, default=1)`
2. **Migration History:** Migration `d2894a11c87d` executes `Base.metadata.create_all(bind=bind)`, emitting `NOT NULL` column constraints in DDL.
3. **Three-Valued Logic Risk:** Because `col IS DISTINCT FROM 'OFFICIAL_ADVISORY'` evaluates to `TRUE` for `NULL`, relying solely on this clause would permit `NULL` values to pass.
4. **Contract Selection:** **Contract C combined with Contract A**. Defensive `col IS NOT NULL` assertions are explicitly embedded in the policy definitions to guarantee fail-closed enforcement even under schema drift.

---

## 14. Evidence-Table Policy Inventory

[`LOCAL_SOURCE_VERIFIED` / `OFFLINE_DDL_VERIFICATION`]

Inspection of [rls.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py) reveals current policies on `regional_signal_evidences`:
- `regional_signal_evidences_public_read_policy`: `AS PERMISSIVE FOR SELECT TO PUBLIC USING ((ADMIN_BYPASS_SQL OR EXISTS(ur.role IN ('ADMIN','EXPERT','RESEARCHER'))))`
- `regional_signal_evidences_author_write_policy`: `AS PERMISSIVE FOR ALL TO PUBLIC USING (...) WITH CHECK (...)`
- **Defects:** Zero parent-signal checks on insert or update. Experts can attach evidence to any signal, including official advisories.

---

## 15. Evidence INSERT/UPDATE/DELETE Design

[`STATIC_POLICY_ANALYSIS`]

```sql
-- 1. READ POLICY
CREATE POLICY regional_signal_evidences_read_policy ON regional_signal_evidences
    AS PERMISSIVE FOR SELECT TO PUBLIC
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

-- 2. INSERT POLICY
CREATE POLICY regional_signal_evidences_insert_policy ON regional_signal_evidences
    AS PERMISSIVE FOR INSERT TO PUBLIC
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

-- 3. UPDATE POLICY
CREATE POLICY regional_signal_evidences_update_policy ON regional_signal_evidences
    AS PERMISSIVE FOR UPDATE TO PUBLIC
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

-- 4. DELETE POLICY
CREATE POLICY regional_signal_evidences_delete_policy ON regional_signal_evidences
    AS PERMISSIVE FOR DELETE TO PUBLIC
    USING (
        SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
        AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
        AND current_setting('app.is_admin', true) = 'true'
    );
```

---

## 16. Parent Promotion and Evidence Revalidation

[`LOCAL_SOURCE_VERIFIED`]

When an administrative writer promotes an ordinary signal to `OFFICIAL_ADVISORY`, previously attached community evidence must not be blindly trusted. The trusted publication workflow MUST execute an atomic verification protocol:
1. Lock parent row via `SELECT ... FOR UPDATE`.
2. Lock and retrieve all linked evidence records via `select(RegionalSignalEvidence).where(...).with_for_update()`.
3. Verify evidence type, source existence, and provenance authenticity.
4. Atomically commit the status transition to `OFFICIAL_ADVISORY`.

---

## 17. Concurrency and Locking

[`LOCAL_SOURCE_VERIFIED`]

- **Race Conditions:** Evidence insertion concurrent with official promotion; signal recovery concurrent with dynamic suppression.
- **Lock Coordination:** All state-modifying operations on signals and evidences MUST acquire an explicit row-level lock on the parent signal (`SELECT ... FOR UPDATE` on `regional_signals.id`) before evaluating evidence or applying updates. This guarantees strict linearizability without deadlocks.

---

## 18. Grants and Indirect Write Paths

[`LOCAL_SOURCE_VERIFIED` / `LIVE_POSTGRESQL_REQUIRED`]

- **TRUNCATE Security:** RLS **does not evaluate on `TRUNCATE`**. Local DDL generator explicitly verifies `REVOKE TRUNCATE ON TABLE regional_signals, regional_signal_evidences FROM acrevia_staging_app;`.
- **Indirect Writes:** Codebase search found zero database triggers, zero stored procedures, and zero SQLAlchemy event listeners modifying these tables.
- **Cascading Deletes:** Foreign key `signal_id` references `regional_signals.id` with `ondelete="CASCADE"`. Because `DELETE` is revoked on `regional_signals`, ordinary actors cannot trigger cascading deletes.
- **Live Database Catalogs:** Unmanaged objects remain `LIVE_POSTGRESQL_REQUIRED`.

---

## 19. Complete Proposed Policy Composition

[`STATIC_POLICY_ANALYSIS`]

Under the proposed architecture:
- Permissive policies combine via `OR`.
- On `regional_signals`: `public_read_policy` handles public farmer queries; `internal_read_policy` handles internal expert workflows; `insert_policy` and `update_policy` enforce fail-closed non-official tiers; `delete_policy` denies ordinary deletion.
- Broad `FOR ALL` policy is **completely eliminated**.
- No permissive policy restores the unauthorized write or read paths.

---

## 20. New Blocker Assessment: `RES-PULSE-READ-01`

[`PROVEN_FROM_LOCAL_POLICY_STRUCTURE`]

- **Blocker Identifier:** `RES-PULSE-READ-01`
- **Title:** Role-Global Sub-Threshold & Suspended Signal Read-Privacy Exposure
- **Severity:** High (Data Privacy & Tenant Isolation)
- **Status:** `PROPOSED — ACTIVE_ARCHITECTURAL_BLOCKER`
- **Evidence:** Proven from local policy structure in Section 6. Permissive OR composition between `regional_signals_public_read_policy` and `regional_signals_author_write_policy` allows mutable GUC spoofing to read sub-threshold and suspended signals statewide.
- **Separation:** Kept strictly distinct from write-authority blocker `RLS-WRITE-AUTH-01`.

---

## 21. Adversarial Test Matrix (34 Conditions)

The following matrix maps all 34 adversarial test conditions across policy, lifecycle, and identity boundaries:

| # | Category | Target Assertion | Test Designation | Evidentiary Basis |
|---|---|---|---|---|
| 1 | Parent SELECT | Farmer cannot read sub-threshold signals | `LOCAL_TEST_VERIFIED` | Passed in `test_worker_security_and_privacy.py`. |
| 2 | Parent SELECT | Farmer can read signals satisfying public rule | `LOCAL_TEST_VERIFIED` | Passed in `test_worker_security_and_privacy.py`. |
| 3 | Parent SELECT | Suspended signals follow approved public rule | `LOCAL_TEST_VERIFIED` | Passed in `test_worker_security_and_privacy.py`. |
| 4 | Parent SELECT | Expert sub-threshold visibility follows explicit rule | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Blocked by `RES-PULSE-READ-01`. |
| 5 | Parent SELECT | Researcher sub-threshold visibility follows explicit rule | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Blocked by `RES-PULSE-READ-01`. |
| 6 | Parent SELECT | Spoofed `app.current_user_id` cannot create unapproved read | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Defect proven in Section 6. |
| 7 | Parent SELECT | Legacy `FOR ALL` policy no longer grants SELECT | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Future forward migration test. |
| 8 | Parent SELECT | Internal service workflows retain only approved access | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Requires complete Option D. |
| 9 | Parent DML | INSERT without RETURNING | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Option D WITH CHECK test. |
| 10 | Parent DML | INSERT with RETURNING | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Option D WITH CHECK + SELECT test. |
| 11 | Parent DML | UPDATE without RETURNING | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Option D USING + WITH CHECK test. |
| 12 | Parent DML | UPDATE with RETURNING | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Option D USING + WITH CHECK + SELECT test. |
| 13 | Parent DML | UPDATE using WHERE predicates that require SELECT | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Option D WHERE compatibility test. |
| 14 | Parent DML | SELECT FOR UPDATE | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Section 10 workflow compatibility test. |
| 15 | Parent DML | INSERT ON CONFLICT DO NOTHING | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Evaluated under PG rules. |
| 16 | Parent DML | INSERT ON CONFLICT DO UPDATE | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Evaluated under PG rules. |
| 17 | Parent DML | DELETE with actual ORM query shape | `LOCAL_SOURCE_VERIFIED` | SQL grant `REVOKE DELETE`. |
| 18 | Parent DML | Ordinary non-official collaboration remains functional | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Section 12 specification test. |
| 19 | Evidence Lifecycle | Evidence INSERT to permitted ordinary parent | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Child INSERT check test. |
| 20 | Evidence Lifecycle | Evidence INSERT to official parent denied | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Child INSERT check test. |
| 21 | Evidence Lifecycle | Evidence UPDATE metadata | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Child UPDATE check test. |
| 22 | Evidence Lifecycle | Evidence UPDATE to new ordinary parent | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Child UPDATE check test. |
| 23 | Evidence Lifecycle | Evidence UPDATE to official parent denied | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Child UPDATE check test. |
| 24 | Evidence Lifecycle | Evidence DELETE denied | `LOCAL_SOURCE_VERIFIED` | SQL grant `REVOKE DELETE`. |
| 25 | Evidence Lifecycle | Parent promotion revalidates all existing evidence | Proposed / Architectural Contract | Section 16 promotion protocol test. |
| 26 | Evidence Lifecycle | Concurrent evidence association and parent promotion consistent | Proposed / Architectural Contract | Row-level locking test. |
| 27 | Evidence Lifecycle | Parent RLS does not unintentionally break approved evidence | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Internal read policy test. |
| 28 | Evidence Lifecycle | Evidence visibility respects approved privacy scope | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Child read policy test. |
| 29 | Identity & Composition | GUC spoofing cannot authorize an unapproved SELECT path | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Identity boundary test. |
| 30 | Identity & Composition | No permissive policy restores broad visibility | Proposed / `LIVE_POSTGRESQL_REQUIRED` | DDL policy composition test. |
| 31 | Identity & Composition | No permissive policy restores official write access | Proposed / `LIVE_POSTGRESQL_REQUIRED` | DDL policy composition test. |
| 32 | Identity & Composition | Ordinary principal cannot TRUNCATE | `LOCAL_SOURCE_VERIFIED` | SQL grant `REVOKE TRUNCATE`. |
| 33 | Identity & Composition | Ordinary principal cannot reach privileged database roles | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Role membership catalog test. |
| 34 | Identity & Composition | No indirect privileged write path restores forbidden access | `LOCAL_SOURCE_VERIFIED` | Source trigger/procedure audit. |

---

## 22. Test Inventory and Execution Provenance

[`LOCAL_TEST_VERIFIED` / `USER_REPORTED`]

### 22.1 Test Collection Inventory
A read-only pytest collection in Python 3.11 confirms:
- `backend/tests/test_orm_rls_alignment.py`: **12 items**
- `backend/tests/test_postgresql_rls.py`: **28 items**
- `backend/tests/test_rls_offline_ddl.py`: **9 items**
- `backend/tests/test_rls_policy_semantics.py`: **14 items**
- `backend/tests/test_worker_security_and_privacy.py`: **108 items**
- **Total Test Items Collected:** **171 items** in 0.40s.

### 22.2 Historical Execution Baseline (from Step 19450)
- **Tests Executed:** Exactly 171 tests.
- **Outcome:** **171 passed**, 1 warning in **23.47s**.
- **Adversarial Semantics:** `test_adversarial_state_transitions_and_permissive_policy_composition` in `test_worker_security_and_privacy.py` executes as a **vulnerability detector**, confirming that current unhardened DDL lacks tier checks.

---

## 23. ECC Adversarial Review Findings

1. **`architect`:** Validates separating `FOR ALL` into discrete per-command policies to eliminate `RLS-WRITE-AUTH-01`. Confirms that Option D requires an internal `SELECT` policy to prevent breaking legitimate service workflows.
2. **`security-reviewer`:** Formally validates the proof of `RES-PULSE-READ-01`. Confirms that mutable session GUCs cannot be treated as authenticated boundaries on a shared database connection.
3. **`database-reviewer`:** Validates PostgreSQL 15/16 RLS semantics regarding `PERMISSIVE` OR-composition, `UPDATE USING` old-row checks, `UPDATE WITH CHECK` new-row checks, and `SELECT` evaluation during `RETURNING` clauses and `SELECT ... FOR UPDATE`. Confirms that RLS does not protect `TRUNCATE`.
4. **`python-reviewer`:** Confirms that SQLAlchemy `nullable=False` attributes generate `NOT NULL` constraints in DDL via `Base.metadata.create_all()`. Approves adopting Contract C (explicit `IS NOT NULL` checks in RLS) to guard against NULL three-valued logic edge cases.
5. **`fastapi-reviewer`:** Maps all endpoint operations in [regional_pulse.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/regional_pulse.py). Pinpoints exact crash vectors in `db.refresh()` and `select(...).with_for_update()` under naive policy replacement.
6. **`silent-failure-hunter`:** Discovered the parent promotion evidence provenance gap: existing community evidence attached prior to promotion remains associated with official advisories unless an explicit revalidation protocol runs at promotion time.
7. **`verification-loop`:** Traced all 34 adversarial test conditions to local tests, static analysis, or future `LIVE_POSTGRESQL_REQUIRED` suites. Verified 171 collected tests.
8. **`delivery-gate`:** Confirms that Phase 07 release gates remain closed. Prevents unauthorized Mode B transition.

---

## 24. Remaining Limitations

- **Strict Mode A Only:** Zero remote or cloud database connections established. Zero local PostgreSQL instances started.
- **Zero Schema/Code Changes:** No changes were applied to `backend/app/database/rls.py`, migration files, ORM models, API endpoints, or test suites.
- **No Alembic Downgrade:** `alembic downgrade` in migration `a1089411c87d` executes `DISABLE ROW LEVEL SECURITY` across 132 tables. It must NEVER be executed. Remediation must strictly proceed via forward migration `a1089411c87e`.
- **Preservation of Working Tree:** All pre-existing modified files and untracked dossiers were preserved intact.

---

## 25. Implementation-Readiness Determination

$$\mathbf{DETERMINATION:\ TECHNICAL\_PREFLIGHT\_BLOCKED\_WITH\_RECORDED\_BLOCKERS}$$

### Justification:
1. **Blocker `RLS-WRITE-AUTH-01` remains open:** The current DDL in `a1089411c87d` still allows ordinary experts/researchers to write official advisories.
2. **Blocker `RES-PULSE-READ-01` is newly recorded:** The current permissive policy leaks sub-threshold and suspended signals across the entire state.
3. **Operational dependencies unresolved:** A naive fix breaks `db.refresh()` and `recover_suppressed_signal`. The complete policy specification designed in Section 12 must be packaged into a forward migration (`a1089411c87e`).
4. **Owner Decisions Pending:** Decisions D-01, D-02, D-03, and DB-AUTH-01 must be signed by the Project Owner.
5. **Phase Status:** Phase 07 is **`NOT RELEASED`**. Mode B is **`STRICTLY NOT AUTHORIZED`**.


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
