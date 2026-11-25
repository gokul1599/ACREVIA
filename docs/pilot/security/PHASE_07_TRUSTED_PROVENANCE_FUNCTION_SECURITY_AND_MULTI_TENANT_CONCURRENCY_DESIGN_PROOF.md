# ACREVIA — PHASE 07: TRUSTED PROVENANCE VERIFICATION FUNCTION SECURITY PROOF, MULTI-TENANT AUTHORITY BOUNDARIES & CONCURRENT SOURCE-MUTATION ASSURANCE

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India — 33 Administrative Districts  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** `MODE A ONLY` — Offline Source Inspection, PostgreSQL Security Architecture Analysis, Function-Privilege Modeling, Concurrency Analysis & Governance Documentation  
**Audit Standard:** Everything Claude Code (ECC) — `PLAN → INSPECT → TRACE → MODEL → ADVERSARIAL REVIEW → VERIFY OFFLINE → DOCUMENT`  
**Public Repository:** `https://github.com/gokul1599/ACREVIA`  
**Pinned Baseline Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Target Deliverable:** `docs/pilot/security/PHASE_07_TRUSTED_PROVENANCE_FUNCTION_SECURITY_AND_MULTI_TENANT_CONCURRENCY_DESIGN_PROOF.md`  
**Artifact Mirror:** `C:\Users\gokul\.gemini\antigravity\brain\8d770357-1b73-48ca-9930-eded206539c2\PHASE_07_TRUSTED_PROVENANCE_FUNCTION_SECURITY_AND_MULTI_TENANT_CONCURRENCY_DESIGN_PROOF.md`  
**Implementation Authorization:** `NONE` (`NOT_IMPLEMENTATION_AUTHORIZED`)  
**Design Proof Status:** `DESIGN_NOT_YET_PROVEN` (Preferred Candidate: Hybrid `SECURITY DEFINER` Verifier + Transactional Outbox Invalidation)  

---

## 1. EXECUTIVE ASSURANCE CONCLUSION

This security design proof evaluates whether ACREVIA's proposed trusted multi-tenant provenance verification function—`verify_regional_signal_provenance(p_signal_id)`—can be implemented securely under the actual repository architecture at commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d`.

Operating strictly under **`MODE A ONLY`** constraints (zero Neon/PostgreSQL connections, zero migrations, zero role provisioning, zero source edits, and zero secret reproduction), this proof establishes five foundational conclusions:

1. **Current Recovery Fails Closed Under Intended `FORCE RLS` (`PUBLIC_SOURCE_VERIFIED` / `STATIC_SQL_SEMANTICS_VERIFIED`):**  
   `get_current_user()` initializes `app.current_tenant_id = ''` when `tenant_id=None`. `POST /api/v1/regional-pulse/signals/{signal_id}/recover` never calls `verify_farm_access()` and never sets a farm context. Because `farms`, `observations`, and `risk_alerts` are `TENANT_DIRECT` tables with `RESTRICTIVE FOR ALL` policies requiring either `ADMIN_BYPASS_SQL` or `tenant_col::text = current_setting('app.current_tenant_id', true)`, both `AGRICULTURAL_EXPERT` and application `ADMIN` sessions (connecting via a restricted runtime role) filter all source rows to **zero**. Provenance recalculation measures `current_count = 0 < 3` and aborts with `HTTP 400`.

2. **`SECURITY DEFINER` Does Not Automatically Bypass `FORCE RLS` or Satisfy `ADMIN_BYPASS_SQL` (`STATIC_SQL_SEMANTICS_VERIFIED`):**  
   In PostgreSQL, `FORCE ROW LEVEL SECURITY` enforces policies even against the table owner unless the role is a `SUPERUSER` or has `BYPASSRLS`. Furthermore, inside a `SECURITY DEFINER` function, `CURRENT_USER` switches to the function owner, but **`SESSION_USER` remains the caller's login identity**. Because `ADMIN_BYPASS_SQL` requires `SESSION_USER::text IN ('neondb_owner', 'acrevia_admin')`, a `SECURITY DEFINER` function invoked by `acrevia_staging_app` still evaluates `ADMIN_BYPASS_SQL` to `FALSE`.

3. **A Constrained `SECURITY DEFINER` Verifier Can Work *Only* With Explicit Co-Controls (`DESIGN_PROPOSAL`):**  
   To avoid granting `acrevia_staging_app` unrestricted cross-tenant `SELECT` or `BYPASSRLS`, the function must be owned by a dedicated non-login capability role (`acrevia_verifier` with `NOSUPERUSER NOBYPASSRLS`), granted a role-targeted `PERMISSIVE FOR SELECT` policy on source tables, hardened with `SET search_path = public, pg_temp` (`pg_temp` last), revoked from `PUBLIC`, typed to match `RegionalSignal.id` (`VARCHAR(36)`), and restricted to aggregate-only output.

4. **Parent-Lock Redundancy and Source Concurrency Remain Unresolved (`PUBLIC_SOURCE_VERIFIED`):**  
   `FarmService.update_farm()` mutates `Farm.district` and commits independently without locking `RegionalSignal`, and `RegionalSignalEvidence.evidence_reference_id` is a `VARCHAR(100)` string without a database foreign key. Neither a parent `FOR UPDATE` lock nor a `SECURITY DEFINER` wrapper alone prevents concurrent source mutations from racing with recovery unless paired with `REPEATABLE READ`/`SERIALIZABLE` isolation or transactional outbox invalidation.

5. **Overall Proof Verdict: `DESIGN_NOT_YET_PROVEN`:**  
   Because `acrevia_verifier` and `acrevia_worker` are unprovisioned, district-scope enforcement (`EXP-AUTH-01`) does not exist in code or auth context, source-mutation outbox triggers are unimplemented, `DB-CREDENTIAL-EXPOSURE-01` remains open in `frontend/lib/server/db.ts#L10`, and live PostgreSQL catalog verification is prohibited in Mode A, **implementation cannot be authorized**.

---

## 2. BASELINE AND EVIDENCE CLASSIFICATION

### 2.1 Immutable Baseline Verification
- **Public Repository:** `https://github.com/gokul1599/ACREVIA`
- **Branch:** `main`
- **Pinned Public Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d`
- **Local Workspace:** `c:\Users\gokul\OneDrive\Documents\projects` (`HEAD` and `origin/main` both verified at `c9e334d14110e8a6e4c9b71b89cae3294288af0d`, 0 commit divergence).
- **Working Tree:** 0 application source, model, schema, migration, or test files modified. 7 tracked historical governance matrices in `docs/pilot/security/` remain in their prior modified state; 17 prior untracked Phase 07 assurance reports remain preserved non-destructively.

### 2.2 Evidence Classification Taxonomy
Every conclusion in this design proof is tagged with one of the following classifications:
- `PUBLIC_SOURCE_VERIFIED`: Directly observed in files pinned at `c9e334d14110e8a6e4c9b71b89cae3294288af0d`.
- `STATIC_SQL_SEMANTICS_VERIFIED`: Derived from PostgreSQL 16 official documentation and engine semantics (`analyze.c`, `rowsecurity.c`) applied to inspected DDL.
- `ORM_BEHAVIOR_VERIFIED`: Derived from SQLAlchemy 2.0 (`sqlalchemy>=2.0.30` in `requirements.txt`) model mappings and session lifecycle code.
- `DESIGN_PROPOSAL`: Candidate architecture, DDL, or contract not present in pinned source.
- `OWNER_DECISION_REQUIRED`: Gated on formal Project Owner approval.
- `LIVE_DATABASE_UNVERIFIED`: Cannot be observed without connecting to Neon/PostgreSQL (prohibited in Mode A).
- `NOT_ESTABLISHED`: Claimed in prior reports without supporting source or catalog evidence.

---

## 3. CURRENT IDENTITY AND GUC LIFECYCLE

### 3.1 Ten-Step Request & Recovery Lifecycle (`PUBLIC_SOURCE_VERIFIED`)
1. **JWT Verification:** `get_current_user()` ([dependencies.py#L26-L52](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/security/dependencies.py#L26-L52)) decodes the Bearer token and extracts `user_id = payload.get("sub")`.
2. **Initial GUC Assignment:** Line 56 calls `set_tenant_context(db, tenant_id=None, user_id=user_id, is_admin=False)`. In [rls.py#L276-L291](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L276-L291), `None` maps to `""`, executing transaction-local (`is_local=true`) `set_config` for `app.current_tenant_id = ''`, `app.current_user_id = user_id`, and `app.is_admin = 'false'`.
3. **User Lookup:** Line 59 executes `db.get(User, user_id)` under `USER_OWNED` RLS (`id::text = current_setting('app.current_user_id', true)`). On missing/inactive user (L60-L63), context is cleared.
4. **Role Lookup & Admin Flag:** Lines 70-74 read `user.roles`. Only if `SystemRole.ADMIN.value in user_roles` does line 74 call `set_tenant_context(db, tenant_id=None, user_id=user.id, is_admin=True)`—which **still leaves `app.current_tenant_id = ''`**.
5. **Endpoint Authorization:** `recover_signal()` ([regional_pulse.py#L152-L158](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/regional_pulse.py#L152-L158)) uses `Depends(require_roles(SystemRole.ADMIN.value, SystemRole.AGRICULTURAL_EXPERT.value))`. It does **not** call `verify_farm_access()`.
6. **Recovery Service Execution:** Calls `RegionalPulseService.recover_suppressed_signal()` ([regional_pulse_service.py#L395-L570](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py#L395-L570)).
7. **Source-Table Queries:** Queries `RegionalSignal` (`FOR UPDATE`), `RegionalSignalEvidence` (`FOR SHARE`), `Observation` (`FOR SHARE`), `RiskAlert` (`FOR SHARE`), and `Farm` (`FOR SHARE`).
8. **PostgreSQL RLS Evaluation:** Evaluates `RESTRICTIVE` `TENANT_DIRECT` policies on `observations`, `risk_alerts`, and `farms` with `app.current_tenant_id = ''`.
9. **Recovery UPDATE & Audit Staging:** Mutates `distinct_farms_count`, `validation_status`, `is_outbreak_claim_suppressed`, and `updated_at` (via Python `onupdate`), then stages an `AuditLog` via `AuditService.stage_activity()`.
10. **Outer Transaction Commit:** `recover_signal()` ([regional_pulse.py#L175](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/regional_pulse.py#L175)) calls `db.commit()`, clearing `is_local=true` GUCs; `get_db()` ([session.py#L83](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/session.py#L83)) calls `clear_tenant_context(db)` in `finally`.

### 3.2 Complete Identity Matrix
| Identity / Principal | `SESSION_USER` | `CURRENT_USER` | `app.current_user_id` | `app.current_tenant_id` | `app.is_admin` | App Roles | Authorized Districts | Expected SELECT (Source Tables) | Expected UPDATE (Signals) | RLS Bypass Eligibility |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ordinary Farmer** | `acrevia_staging_app`* | `acrevia_staging_app`* | `<farmer_uuid>` | `<farm_uuid>` (via `verify_farm_access`) or `''` | `'false'` | `FARMER` | None | Own farm rows only (when tenant set) | Denied | No |
| **Agricultural Expert** | `acrevia_staging_app`* | `acrevia_staging_app`* | `<expert_uuid>` | `''` (empty on recovery) | `'false'` | `AGRICULTURAL_EXPERT` | `NOT_ESTABLISHED` (`districts_covered_json` unenforced) | **0 rows** on `farms`, `observations`, `risk_alerts` | Permitted by `regional_signals_author_write_policy` if visible | No |
| **Application ADMIN** | `acrevia_staging_app`* | `acrevia_staging_app`* | `<admin_uuid>` | `''` (empty on recovery) | `'true'` | `ADMIN` | Unbounded in app; unenforced in DB | **0 rows** (`ADMIN_BYPASS_SQL` fails `SESSION_USER`) | Permitted by `regional_signals_author_write_policy` | **No** (not DB admin) |
| **Researcher** | `acrevia_staging_app`* | `acrevia_staging_app`* | `<researcher_uuid>` | `''` | `'false'` | `RESEARCHER` | None | **0 rows** on source tables | Permitted by `regional_signals_author_write_policy` | No |
| **Proposed Web Runtime (`acrevia_staging_app`)** | `acrevia_staging_app` (`LIVE_DATABASE_UNVERIFIED`) | `acrevia_staging_app` | Set per request | Set per farm or `''` | `'false'`/`'true'` | Session-dependent | None | Tenant-matched only | Per crosswalk & policy | No (`NOSUPERUSER NOBYPASSRLS`) |
| **Proposed Worker Login (`acrevia_worker_login`)** | `acrevia_worker_login` (`DESIGN_PROPOSAL`) | `acrevia_worker_login` | N/A | `''` | `'false'` | System | N/A | Minimal (should not read raw tenants) | None directly | No |
| **Proposed Worker Role (`acrevia_worker` post `SET ROLE`)** | `acrevia_worker_login` (`DESIGN_PROPOSAL`) | `acrevia_worker` | `'system:worker'` | `''` | `'false'` | Worker | Proposed only | Via verifier function only (recommended) | Bounded worker columns | No |
| **Database Owner (`neondb_owner`)** | `neondb_owner` (`LIVE_DATABASE_UNVERIFIED`) | `neondb_owner` | Any/Unset | Any/Unset | `'true'` (for bypass) | DB Owner | All | All (if `app.is_admin='true'` or superuser/table owner without `FORCE RLS`) | All | Yes (if `app.is_admin='true'` or `BYPASSRLS`/superuser) |
| **Physical DB Admin (`acrevia_admin`)** | `acrevia_admin` (`LIVE_DATABASE_UNVERIFIED`) | `acrevia_admin` | Any/Unset | Any/Unset | `'true'` (for bypass) | DB Admin | All | All (when `app.is_admin='true'`) | All | Yes (satisfies `ADMIN_BYPASS_SQL`) |

*\*`acrevia_staging_app` is the planned GATE-02 runtime role; GATE-02 is unapproved (`OWNER_DECISION_REQUIRED`).*

---

## 4. TENANT-CONTEXT FAILURE PROOF

In [rls.py#L349-L361](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L349-L361), every `TENANT_DIRECT` table receives a `PERMISSIVE FOR ALL` base policy (`USING (true)`) combined via `AND` with a `RESTRICTIVE FOR ALL` policy:

```sql
USING (
    (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin')
     AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin')
     AND current_setting('app.is_admin', true) = 'true')
    OR {column_name}::text = current_setting('app.current_tenant_id', true)
)
```

| Source Table | RLS Tenant Column | Assigned Tenant GUC (`recover_signal`) | Policy Expression | Expected Matching Behavior (`STATIC_SQL_SEMANTICS_VERIFIED`) | Effect on Recovery Recalculation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `observations` | `farm_id` | `''` (empty string) | `ADMIN_BYPASS_SQL OR farm_id::text = ''` | `ADMIN_BYPASS_SQL` is `FALSE` for `acrevia_staging_app`; `farm_id::text = ''` is `FALSE` for all UUIDs. | `observations` dict is `{}` (0 rows). |
| `risk_alerts` | `farm_id` | `''` (empty string) | `ADMIN_BYPASS_SQL OR farm_id::text = ''` | `ADMIN_BYPASS_SQL` is `FALSE`; `farm_id::text = ''` is `FALSE`. | `alerts` dict is `{}` (0 rows). |
| `farms` | `id` | `''` (empty string) | `ADMIN_BYPASS_SQL OR id::text = ''` | `ADMIN_BYPASS_SQL` is `FALSE`; `id::text = ''` is `FALSE`. | `farms` dict is `{}` (0 rows). |

**Result:** Under the intended restricted runtime role and `FORCE RLS`, `verified_farms` remains empty, `current_count` is `0 < 3`, and `recover_suppressed_signal()` raises `HTTP 400 Bad Request`. *(Note: This is a `STATIC_SQL_SEMANTICS_VERIFIED` design failure derived from generated DDL, not a live database observation.)*

---

## 5. RECOVERY SOURCE-QUERY TRACE

Tracing [regional_pulse_service.py#L430-L551](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py#L430-L551):
1. **L430-437:** `RegionalSignal` queried with `.with_for_update()`. Under [rls.py#L901-L907](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L901-L907), `regional_signals_public_read_policy` requires `ADMIN_BYPASS_SQL OR (distinct_farms_count >= 3 AND validation_status != 'SUSPENDED')`. Wait: if a suppressed signal has `distinct_farms_count < 3`, **even the parent `RegionalSignal` SELECT fails visibility** for `acrevia_staging_app`! (Unless `distinct_farms_count >= 3` and status is `'SUPPRESSED_INSUFFICIENT_PROVENANCE'`).
2. **L459-466:** `RegionalSignalEvidence` queried with `.with_for_update(read=True)` (`FOR SHARE`).
3. **L476-483:** `Observation` queried with `.with_for_update(read=True)` (`FOR SHARE`) -> **filtered to 0 rows by `observations_tenant_isolation_policy`**.
4. **L487-494:** `RiskAlert` queried with `.with_for_update(read=True)` (`FOR SHARE`) -> **filtered to 0 rows by `risk_alerts_tenant_isolation_policy`**.
5. **L505-512:** `Farm` queried with `.with_for_update(read=True)` (`FOR SHARE`) -> **filtered to 0 rows by `farms_tenant_isolation_policy`**.
6. **L515-544:** Loop finds no `obs` or `alert`; `verified_farms` is empty (`current_count = 0`).
7. **L545-551:** `signal.distinct_farms_count = 0`, raises `HTTPException(400)`.

---

## 6. POSTGRESQL RLS LOCKING SEMANTICS (`STATIC_SQL_SEMANTICS_VERIFIED`)

Under PostgreSQL 16 (`src/backend/rewrite/rowsecurity.c`):
1. **Lock Terminology:**
   - **Row-level tuple lock strengths:** `FOR UPDATE`, `FOR NO KEY UPDATE`, `FOR SHARE`, `FOR KEY SHARE`.
   - **Table-level lock mode:** A `SELECT` with any row-locking clause acquires a table-level **`ROW SHARE`** lock on the relation (never table-level `ExclusiveLock` or `ShareLock`).
2. **Policy Composition on Locking SELECTs:**
   - PostgreSQL evaluates the `USING` clauses of **both** applicable `FOR SELECT` (or `FOR ALL`) policies **and** applicable `FOR UPDATE` (or `FOR ALL`) policies.
   - `WITH CHECK` is **not** evaluated during `SELECT ... FOR UPDATE/SHARE` (it applies only to actual `UPDATE` writes).
3. **Current `FOR ALL` Policy Reality:**
   - Both `regional_signals` / `regional_signal_evidences` (`author_write_policy`, L962-968) and `TENANT_DIRECT` tables (`base_access_policy` + `tenant_isolation_policy`, L342-361) use **`FOR ALL`**.
   - Therefore, an applicable `UPDATE` policy **already exists** in the generated DDL. The source-access failure is **not** caused by a missing `UPDATE` policy—it is caused by `app.current_tenant_id = ''` failing the restrictive isolation predicate, while the broad `FOR ALL` policies remain an over-broad authorization concern (`RLS-WRITE-AUTH-01`).


---

## 7. ROW-LOCK PRIVILEGE COMPATIBILITY (`STATIC_SQL_SEMANTICS_VERIFIED`)

Under PostgreSQL 16 (`src/backend/parser/analyze.c`, `transformLockingClause()`):
- Any locking `SELECT` (`FOR UPDATE`, `FOR NO KEY UPDATE`, `FOR SHARE`, `FOR KEY SHARE`) requires `SELECT` privilege on the selected columns **AND `UPDATE` privilege on at least one column** of every locked table.
- Granting `UPDATE` on one column satisfies the locking check without granting `UPDATE` on other columns, **unless** an `UPDATE` policy also permits updating that column.

### 7.1 Privilege & Lock Compatibility Matrix
| Table | Current `PRIVILEGE_CROSSWALK` (`rls.py`) | Locking Clause in `recover_suppressed_signal()` | Table-Level Lock | Required SQL Privilege for Lock | Conflict with Append-Only Goal? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `regional_signals` | `COMMUNITY_COLLABORATIVE_DML` (`SELECT, INSERT, UPDATE`) | `FOR UPDATE` (L434) | `ROW SHARE` | `SELECT` + `UPDATE` (needs `distinct_farms_count`, `validation_status`, `is_outbreak_claim_suppressed`, `updated_at`) | No (parent mutates on recovery) |
| `regional_signal_evidences` | `COMMUNITY_COLLABORATIVE_DML` (`SELECT, INSERT, UPDATE`) | `FOR SHARE` (L463) | `ROW SHARE` | `SELECT` + `UPDATE` (1+ col) | **YES** — revoking `UPDATE` breaks `FOR SHARE` (`42501`) |
| `observations` | `TENANT_DIRECT_DML` (`SELECT, INSERT, UPDATE, DELETE`) | `FOR SHARE` (L480) | `ROW SHARE` | `SELECT` + `UPDATE` (1+ col) | **YES** — requires `UPDATE` on tenant table |
| `risk_alerts` | `TENANT_DIRECT_DML` (`SELECT, INSERT, UPDATE, DELETE`) | `FOR SHARE` (L491) | `ROW SHARE` | `SELECT` + `UPDATE` (1+ col) | **YES** — requires `UPDATE` on tenant table |
| `farms` | `TENANT_DIRECT_DML` (`SELECT, INSERT, UPDATE, DELETE`) | `FOR SHARE` (L509) | `ROW SHARE` | `SELECT` + `UPDATE` (1+ col) | **YES** — requires `UPDATE` on tenant table |

*Note: `PRIVILEGE_CROSSWALK` is a specification; `a1089411c87d` does not invoke `generate_privilege_grants_ddl()`. Live ACLs are `LIVE_DATABASE_UNVERIFIED`.*

---

## 8. `SECURITY DEFINER` THREAT MODEL (`STATIC_SQL_SEMANTICS_VERIFIED` / `DESIGN_PROPOSAL`)

Evaluating `verify_regional_signal_provenance(p_signal_id VARCHAR(36))` under PostgreSQL 16 semantics:

### 8.1 Direct Answers to Core Security Questions
1. **Would `ADMIN_BYPASS_SQL` evaluate to `true` inside a `SECURITY DEFINER` function called by `acrevia_staging_app`?**  
   **NO (`UNSAFE` if relied upon).** `CURRENT_USER` switches to the function owner, but **`SESSION_USER` remains `acrevia_staging_app`**. `ADMIN_BYPASS_SQL` checks `SESSION_USER::text IN ('neondb_owner', 'acrevia_admin')`, which evaluates to `FALSE`.
2. **Does changing `CURRENT_USER` alone satisfy the dual-identity predicate?**  
   **NO.** Both `SESSION_USER` and `CURRENT_USER` must be in the allowlist.
3. **Would a function owner subject to `FORCE RLS` still see only rows permitted by its RLS policies?**  
   **YES.** Under PostgreSQL `FORCE ROW LEVEL SECURITY`, even the table owner is bound by RLS unless the role is `SUPERUSER` or has `BYPASSRLS`.
4. **Would granting the function owner `BYPASSRLS` defeat the intended least-privilege boundary?**  
   **YES (`UNSAFE` as default).** A `BYPASSRLS` owner can read every table in the database if the function has any dynamic SQL, search-path, or parameter-injection flaw.
5. **Could a caller supply a signal identifier belonging to an unauthorized district?**  
   **YES (`UNSAFE` without explicit district validation).** Passing an arbitrary `p_signal_id` allows cross-district enumeration unless the function or gateway verifies caller jurisdiction.
6. **Could a function return sensitive counts or existence information below the privacy threshold?**  
   **YES (`UNSAFE` if exact raw counts `< 3` are returned to unauthorized callers).** Below-threshold counts (`1` or `2`) can leak small-sample farm presence in sparse mandals.
7. **Can the function be safely executed by the application without granting unrestricted source-table `SELECT`?**  
   **CONDITIONALLY SAFE** — only if owned by a dedicated `NOLOGIN NOSUPERUSER NOBYPASSRLS` role (`acrevia_verifier`) granted a targeted `PERMISSIVE FOR SELECT` policy on source tables, `SET search_path = public, pg_temp`, `REVOKE ALL FROM PUBLIC`, schema-qualified references, no dynamic SQL, input/district validation, and threshold-gated output.

### 8.2 Hardening Verdict Matrix
| Security Control | Configuration | Verdict | Rationale |
| :--- | :--- | :---: | :--- |
| **Function Owner** | `SUPERUSER` or `BYPASSRLS` role | **`UNSAFE`** | Defeats least-privilege blast-radius containment. |
| **Function Owner** | Unprivileged `NOLOGIN` role with no targeted RLS policy | **`UNSAFE`** | Blocked by `FORCE RLS` + `ADMIN_BYPASS_SQL` (`SESSION_USER` check). |
| **Function Owner** | Dedicated `acrevia_verifier` (`NOLOGIN NOSUPERUSER NOBYPASSRLS`) + role-targeted `SELECT` policy | **`CONDITIONALLY SAFE`** | Isolates cross-tenant reads strictly to the function's owner policy. |
| **Search Path** | Unset or `pg_temp` before `public` | **`UNSAFE`** | Vulnerable to temporary-table shadowing (`pg_temp.farms`). |
| **Search Path** | `SET search_path = public, pg_temp` + schema-qualified tables | **`SAFE`** | Eliminates object-name shadowing. |
| **Execution Grants** | Default `PUBLIC` execute | **`UNSAFE`** | Allows any DB role to invoke and probe signals. |
| **Execution Grants** | `REVOKE ALL FROM PUBLIC; GRANT EXECUTE TO acrevia_staging_app, acrevia_worker;` | **`SAFE`** | Confines invocation to authorized runtime roles. |
| **Return Type** | `RETURNS (INT, BOOLEAN)` | **`UNSAFE` (Invalid)** | PostgreSQL syntax error. Must use `RETURNS TABLE (...)` or composite type. |

---

## 9. `SECURITY INVOKER` COMPARISON

A `SECURITY INVOKER` function executes with the privileges and `CURRENT_USER` of the **caller** (`acrevia_staging_app`).
- Because `app.current_tenant_id = ''` and `SESSION_USER = acrevia_staging_app`, `SECURITY INVOKER` hits the **exact same `RESTRICTIVE` tenant-isolation wall** on `farms`, `observations`, and `risk_alerts` as direct SQL queries.
- **Verdict:** `UNSAFE / NON-FUNCTIONAL` for cross-tenant provenance verification without opening raw table `SELECT` to `acrevia_staging_app`.

---

## 10. FUNCTION-OWNER AND `FORCE RLS` MATRIX

| Function Owner Type | `SESSION_USER` (App Call) | `CURRENT_USER` (Inside Function) | Subject to `FORCE RLS`? | Satisfies `ADMIN_BYPASS_SQL`? | Source Rows Visible | Least-Privilege Verdict |
| :--- | :--- | :--- | :---: | :---: | :--- | :---: |
| **`acrevia_staging_app`** | `acrevia_staging_app` | `acrevia_staging_app` | Yes | No | **0 rows** (`app.current_tenant_id=''`) | **FAILS CLOSED** |
| **`acrevia_admin` (without `BYPASSRLS`)** | `acrevia_staging_app` | `acrevia_admin` | Yes | **No** (`SESSION_USER` fails!) | **0 rows** unless targeted policy exists | **FAILS CLOSED** |
| **`neondb_owner` (`BYPASSRLS`/Superuser)** | `acrevia_staging_app` | `neondb_owner` | Bypassed | N/A (Superuser bypass) | All rows (global) | **UNSAFE** (Over-privileged) |
| **`acrevia_verifier` (`NOLOGIN NOBYPASSRLS`) + Role Policy** | `acrevia_staging_app` | `acrevia_verifier` | Yes, satisfied by `TO acrevia_verifier` policy | No | Scoped source rows inside function | **`CONDITIONALLY SAFE`** |

---

## 11. TRUSTED DISTRICT AUTHORIZATION (`PUBLIC_SOURCE_VERIFIED` / `DESIGN_PROPOSAL`)

### 11.1 Current State (`EXP-AUTH-01` Remains Open)
- `app.current_user_districts`: **0 occurrences** in the pinned codebase (`NOT_ESTABLISHED`).
- `ExpertProfile.districts_covered_json` ([expert_profile.py#L25](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/expert_profile.py#L25)): Exists in the model, defaulted to `'["Warangal","Khammam"]'`, but is **never loaded in `get_current_user()`**, never validated against Telangana's 33 districts, and never checked by `recover_suppressed_signal()` or `rls.py`.

### 11.2 Required Trustworthy District Contract (`DESIGN_PROPOSAL`)
To prevent experts from recovering signals outside their jurisdiction and prevent GUC tampering:
1. Normalize expert district assignments in a database-enforced table (`expert_district_assignments(user_id, district, is_active)`), **not** an unvalidated JSON string or client-mutable GUC.
2. Inside the recovery service / verification function, validate `EXISTS (SELECT 1 FROM expert_district_assignments WHERE user_id = current_setting('app.current_user_id', true) AND district = signal.district AND is_active = true)` (or explicit `ADMIN` authority).
3. Validate `farm.district` against `signal.district` inside the verifier so cross-district evidence is never counted.

---

## 12. MULTI-TENANT PROVENANCE DESIGN (`PUBLIC_SOURCE_VERIFIED`)

Inspecting the actual ORM schemas:
- `RegionalSignal.id`: `String(36)` (`VARCHAR(36)`), **not native `UUID`** ([regional_pulse.py#L18](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/regional_pulse.py#L18)).
- `RegionalSignalEvidence.signal_id`: `String(36)` FK to `regional_signals.id` (`ondelete="CASCADE"`).
- `RegionalSignalEvidence.evidence_reference_id`: `String(100)` — **no database foreign key** to `observations.id` or `risk_alerts.id` ([regional_pulse.py#L50](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/regional_pulse.py#L50)).
- `Observation`: `id` (`String(36)`), `farm_id` (`String(36)` FK `farms.id`), `created_at` (`TimestampMixin`).
- `RiskAlert`: `id` (`String(36)`), `farm_id` (`String(36)` FK `farms.id`), `created_at`. *(Note: `RiskAlert` has `is_acknowledged` and `is_dismissed`, not `is_resolved`.)*
- `Farm`: `id` (`String(36)`), `district` (`String(50)`), `is_archived` (`Boolean`).

### 12.1 Required Aggregation & Disclosure Rules
1. Valid `evidence_type` (`OBSERVATION_REF`, `OBSERVATION`, `RISKCAST_ALERT`, `RISK_ALERT`).
2. Source record exists and is active (`farm.is_archived = FALSE`).
3. District match (`LOWER(TRIM(farm.district)) = LOWER(TRIM(signal.district))`).
4. Date window match (`source.created_at::date BETWEEN signal.observed_start_date AND signal.observed_end_date`).
5. Distinct `farm.id` count across mixed evidence types (`COUNT(DISTINCT f.id) >= 3`).
6. **Output Minimization:** Return `(is_valid BOOLEAN, meets_threshold BOOLEAN)` or `(verified_count INT, is_valid BOOLEAN)` strictly to authorized recovery/worker callers—never return raw farmer IDs, names, coordinates, or below-threshold counts to public/farmer endpoints.


---

## 13. SOURCE MUTATION INVENTORY (`PUBLIC_SOURCE_VERIFIED`)

A parent `RegionalSignal FOR UPDATE` lock serializes **only** transactions that lock that identical `RegionalSignal` row. Independent writers do not participate in that lock protocol:

| Source Mutation | Code Location / Specification | Mutated Fields | Locks `RegionalSignal`? | Locks Source Row? | Changes Provenance Validity? | Concurrent Commit with Recovery? | Detected/Prevented by Standalone Function? |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Farm District Change** | `FarmService.update_farm()` ([farm_service.py#L93-L102](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/farm_service.py#L93-L102)) | `Farm.district`, `mandal`, `village` | **NO** | Yes (`UPDATE farms`) | **YES** | **YES** | **NO** under `READ COMMITTED` |
| **Farm Archival** | `Farm.is_archived` (`TENANT_DIRECT_DML` in `rls.py#L997`) | `Farm.is_archived` | **NO** | Yes (if updated) | **YES** | **YES** | **NO** under `READ COMMITTED` |
| **Observation Update / Delete** | `ObservationService` (`create_observation` only in service; `UPDATE`/`DELETE` in `PRIVILEGE_CROSSWALK`) | `farm_id`, `created_at`, or row deletion | **NO** | Yes (DML) | **YES** | **YES** | **NO** (no FK on `evidence_reference_id`) |
| **RiskAlert Update / Delete** | `RiskService.acknowledge_alert()` / `dismiss_alert()` ([risk_service.py#L266-L290](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/riskcast/risk_service.py#L266-L290)); `PRIVILEGE_CROSSWALK` DML | `is_acknowledged`, `is_dismissed`, or row deletion | **NO** | Yes (DML) | Yes (existence/status) | **YES** | **NO** (no FK on `evidence_reference_id`) |
| **Evidence Association Insert** | `RegionalPulseService.aggregate_regional_signal()` (`PRIVILEGE_CROSSWALK` `INSERT=True`) | New `RegionalSignalEvidence` | Only if parent locked | Yes (`INSERT`) | **YES** | Blocked only if parent `FOR UPDATE` held? **Wait:** `INSERT` into child checks parent FK with `FOR KEY SHARE`, which blocks `DELETE`/`PK UPDATE` on parent, **not** `FOR NO KEY UPDATE`, whereas `FOR UPDATE` on parent blocks `FOR KEY SHARE`! | Serialized only if parent locked `FOR UPDATE` |
| **Evidence Association Update / Delete** | `PRIVILEGE_CROSSWALK` (`can_update=True` on `COMMUNITY_COLLABORATIVE`, `rls.py#L1002`) | `signal_id`, `evidence_reference_id` | **NO** | Yes (DML) | **YES** | **YES** | **NO** unless `UPDATE`/`DELETE` revoked |
| **Signal Recovery** | `RegionalPulseService.recover_suppressed_signal()` ([regional_pulse_service.py#L430](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py#L430)) | `distinct_farms_count`, `validation_status`, `is_outbreak_claim_suppressed`, `updated_at` | **YES** (`FOR UPDATE`) | Previously `FOR SHARE` | **YES** | Serialized against other recoveries on same `signal_id` | Serialized by parent `FOR UPDATE` |

---

## 14. CONCURRENCY AND ISOLATION-LEVEL ANALYSIS (`STATIC_SQL_SEMANTICS_VERIFIED`)

A single SQL statement inside a `SECURITY DEFINER` function **does not eliminate concurrency races** between verification and commit:
- Under PostgreSQL's default **`READ COMMITTED`** isolation:
  1. Statement 1 (`SELECT * FROM regional_signals WHERE id = :id FOR UPDATE`) acquires a snapshot at `T1`.
  2. Statement 2 (`SELECT * FROM verify_regional_signal_provenance(:id)`) acquires a **new snapshot at `T2`**.
  3. Between `T2` and the outer `COMMIT` at `T3`, an independent transaction (`FarmService.update_farm()`) can change `Farm.district` and commit at `T2.5`. Recovery commits at `T3` based on stale provenance!

### 14.1 Concurrency Mechanism Comparison
| Mechanism | Snapshot Consistency | Blocks Concurrent Farm District Change? | Stale Window Between Verify & Commit? | Deadlock / Retry Risk | Required Control |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **`READ COMMITTED` + Function** | Per-statement only | **NO** | **YES** (`T2` to `T3`) | Low | Insufficient alone; needs outbox reconciliation |
| **`REPEATABLE READ` + Function** | Transaction-wide snapshot (`T1`) | **NO** (detects only write-write conflict on same row) | **YES** (non-overlapping row writes commit) | Low | Prevents intra-tx skew, not cross-table farm skew |
| **`SERIALIZABLE` (`SSI`)** | Full serializability | Detects read-write anti-dependencies (`40001`) | **NO** (aborts one tx on `40001`) | High (requires app retry loop) | Strongest isolation, requires retry handler |
| **Deterministic Source Row Locking (`FOR SHARE`)** | Locking reads current committed rows | **YES** (blocks `update_farm` until commit) | **NO** | Moderate (requires ascending ID lock order) | Blocked if `UPDATE` revoked on source/evidence |
| **Advisory Locks (`pg_advisory_xact_lock`)** | Only if all writers participate | **NO** (unless `FarmService` also acquires lock) | **YES** if uncoordinated | Low | Requires universal writer participation |
| **Transactional Outbox + Watermark** | Eventual consistency | **NO** (allows write, triggers async re-suppression) | Bounded by worker lag | **None** | **Required companion** to `SECURITY DEFINER` verifier |

**Concurrency Conclusion:** Because `acrevia_staging_app` should not hold `UPDATE` privileges on tenant source tables to run `FOR SHARE`, the defensible protocol is **Parent `FOR UPDATE` + `REPEATABLE READ` (or `SERIALIZABLE` with retry) for the recovery transaction + Transactional Outbox invalidation on source mutations** so any concurrent district/archival commit immediately triggers asynchronous revalidation.

---

## 15. APPEND-ONLY EVIDENCE RETENTION (`PUBLIC_SOURCE_VERIFIED` / `ORM_BEHAVIOR_VERIFIED`)

### 15.1 Current Code State (`PUBLIC_SOURCE_VERIFIED`)
- [regional_pulse.py#L36](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/regional_pulse.py#L36): `evidences = relationship(..., cascade="all, delete-orphan")` — ORM deletes child evidence on parent deletion or orphan removal.
- [regional_pulse.py#L47](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/regional_pulse.py#L47): `ForeignKey("regional_signals.id", ondelete="CASCADE")` — DB deletes child evidence on parent deletion.
- [rls.py#L1002-L1006](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L1002-L1006): `PRIVILEGE_CROSSWALK` grants `SELECT, INSERT, UPDATE` (`can_delete=False`) on `regional_signal_evidences`.

### 15.2 Required Hardening (`DESIGN_PROPOSAL`)
1. **ORM:** Change to `cascade="save-update, merge", passive_deletes="all"` (prevents SQLAlchemy from issuing `DELETE` or `SET signal_id = NULL` even on loaded collections).
2. **Database FK:** Change to `ON DELETE RESTRICT` (aborts parent deletion with SQLSTATE `23001` if evidence exists).
3. **Runtime ACLs vs. Owner Immutability:** Revoke `UPDATE` and `DELETE` on `regional_signal_evidences` from `acrevia_staging_app` and `acrevia_worker`. *(Note: This protects against runtime application roles; `neondb_owner` / table owners can still alter schema/data unless blocked by append-only triggers.)*

---

## 16. WORKER AND LOGIN-ROLE ARCHITECTURE (`DESIGN_PROPOSAL` / `OWNER_DECISION_REQUIRED`)

| Role / Principal | PostgreSQL Attributes | Authentication & `SET ROLE` | Governance Status (`PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`) |
| :--- | :--- | :--- | :--- |
| **Web App Login (`acrevia_staging_app`)** | `LOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE` | Direct pool login | Named in **GATE-02** (`PENDING`). |
| **Worker Login (`acrevia_worker_login`)** | `LOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE` | Direct worker pool login; executes `SET ROLE acrevia_worker;` | **Not in register** — requires **DB-AUTH-01 extension**. |
| **Worker Execution (`acrevia_worker`)** | `NOLOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE` | Assumed via `SET ROLE` from `acrevia_worker_login` | **Not in register** — requires **DB-AUTH-01 extension**. |
| **Verifier Owner (`acrevia_verifier`)** | `NOLOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE` | Owns `verify_regional_signal_provenance()` only | **Not in register** — requires **DB-AUTH-01 extension**. |
| **Migration / DB Admin (`acrevia_admin` / `neondb_owner`)** | Admin / Owner | Direct admin session only (`ADMIN_BYPASS_SQL`) | `acrevia_admin` in `rls.py#L22`. |

**Principle:** `acrevia_worker` must **not** receive unrestricted global `SELECT` on `farms`, `observations`, or `risk_alerts`. It should invoke `verify_regional_signal_provenance(p_signal_id)` and hold `SELECT, UPDATE (distinct_farms_count, validation_status, is_outbreak_claim_suppressed, updated_at)` on `regional_signals`, `SELECT, INSERT` on `regional_signal_evidences`, and `SELECT, UPDATE` on `outbox_events`.

---

## 17. TRANSACTIONAL OUTBOX (`DESIGN_PROPOSAL`)

To maintain recovery consistency without dual-write gaps:
1. **Atomic Staging:** `recover_suppressed_signal()` stages the `SIGNAL_RECOVERED` outbox row, parent `RegionalSignal` update, and `AuditLog` record inside the **same** database transaction before `recover_signal()` calls `db.commit()`.
2. **Idempotency & Retries:** Each outbox event carries `idempotency_key` (unique index), `status` (`PENDING`, `PROCESSING`, `COMPLETED`, `DEAD_LETTER`), `locked_at`, `lease_expires_at`, and `retry_count`.
3. **Worker Claiming:** `SELECT ... FROM outbox_events WHERE status = 'PENDING' ORDER BY created_at ASC FOR UPDATE SKIP LOCKED LIMIT 50;` (requires `SELECT` + `UPDATE` on claim/status columns).
4. **Crash Recovery:** If a worker crashes after processing side effects but before acknowledging completion, `lease_expires_at` expires, another worker reclaims the row, and downstream consumers deduplicate via `idempotency_key` (**at-least-once delivery + idempotent consumers**, not unverified "exactly-once" claims).

---

## 18. CREDENTIAL EXPOSURE REASSESSMENT (`PUBLIC_SOURCE_VERIFIED`)

Inspection of [frontend/lib/server/db.ts#L8-L10](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/lib/server/db.ts#L8-L10) at pinned commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d`:
- **Source Exposure:** Line 9 reads `process.env.DATABASE_URL`, but line 10 retains a **hard-coded PostgreSQL connection URI fallback** containing an administrative role (`neondb_owner`), an embedded password-like credential, and a Neon pooler host in `aws-ap-southeast-1`. *(Secret value deliberately omitted per Mode A rules.)*
- **Separate Statuses:**
  - *Source exposure:* **Confirmed present** in `frontend/lib/server/db.ts#L10` (`PUBLIC_SOURCE_VERIFIED`).
  - *Public repository history exposure:* **Confirmed present** in `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`PUBLIC_SOURCE_VERIFIED`).
  - *Credential rotation / revocation evidence:* **NOT_ESTABLISHED** (no attributable Neon rotation record).
  - *Deployment configuration / live validity:* **LIVE_DATABASE_UNVERIFIED** (prohibited in Mode A).
- **Verdict:** `DB-CREDENTIAL-EXPOSURE-01` **MUST REMAIN OPEN** (`OPEN_SOURCE_DEFECT`).


---

## 19. CANONICAL BLOCKER RECONCILIATION (`PUBLIC_SOURCE_VERIFIED`)

All 15 canonical Phase 07 blocker identifiers are preserved without renaming, silencing, or premature closure:

| Blocker ID | Current Source Evidence | Previous Canonical State | New Evidence / Audit Finding | Design Mitigation | Implementation Status | Live Verification | Owner Decision Dependency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`RLS-WRITE-AUTH-01`** | `rls.py#L921-L930` (`FOR ALL` without status `WITH CHECK`) | `ACTIVE_BLOCKER` | Confirmed `FOR ALL` applies to locking SELECT & UPDATE | Command-scoped `FOR SELECT` / `FOR UPDATE` policies | **NOT IMPLEMENTED** | `LIVE_DATABASE_UNVERIFIED` | D-01, DB-AUTH-01 |
| **`RLS-ROLE-ASSIGNMENT-01`** | `rls.py#L280-L291` (`set_config` mutable in session) | `ACTIVE_BLOCKER` | Shared role can alter `app.current_user_id` via SQL | Server-enforced verifier / dedicated writer roles | **NOT IMPLEMENTED** | `LIVE_DATABASE_UNVERIFIED` | DB-AUTH-01 |
| **`DB-AUTH-01`** | `PHASE_07_TRUSTED_WRITER_ARCHITECTURE_DECISION_RECORD.md` | `OWNER_DECISION_REQUIRED` | Needs extension for `acrevia_verifier` & `acrevia_worker` | Dedicated login + capability roles | **NOT IMPLEMENTED** | `LIVE_DATABASE_UNVERIFIED` | DB-AUTH-01, GATE-02 |
| **`DB-CREDENTIAL-EXPOSURE-01`** | `frontend/lib/server/db.ts#L10` | `OPEN` | Hard-coded fallback URI confirmed still present at `c9e334d` | Remove fallback, fail closed, rotate in Neon | **NOT IMPLEMENTED** | `LIVE_DATABASE_UNVERIFIED` | Owner Secret Rotation |
| **`APP-ROLE-SELF-SELECT-01`** | `rls.py#L378-L389` (`USER_OWNED` `user_roles`) | `ACTIVE_BLOCKER` | Coupled to mutable `app.current_user_id` GUC | Immutable DB identity / restricted `user_roles` ACL | **NOT IMPLEMENTED** | `LIVE_DATABASE_UNVERIFIED` | DB-AUTH-01 |
| **`EXP-AUTH-01`** | `expert_profile.py#L25` (`districts_covered_json` unused) | `ACTIVE_BLOCKER` | `app.current_user_districts` = 0 occurrences in repo | Normalized `expert_district_assignments` table + check | **NOT IMPLEMENTED** | `LIVE_DATABASE_UNVERIFIED` | D-03 / Expert Contract |
| **`CASCADE-ROLE-DEL-01`** | `rls.py` / `a1089411c87d` | `ACTIVE_BLOCKER` | Role lifecycle unprovisioned | Migration-safe role grants without destructive drops | **NOT IMPLEMENTED** | `LIVE_DATABASE_UNVERIFIED` | GATE-02, GATE-03 |
| **`TENANT-MEMBERSHIP-01`** | `dependencies.py#L56,117` | `ACTIVE_BLOCKER` | `recover_signal` has `app.current_tenant_id=''` $\to$ 0 source rows | `verify_regional_signal_provenance()` (`acrevia_verifier`) | **NOT IMPLEMENTED** | `LIVE_DATABASE_UNVERIFIED` | DB-AUTH-01 |
| **`OWNER-AUTH-01`** | `PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md` | `CRITICAL` / `ACTIVE_BLOCKER` | GATE-01 approved (2026-11-10); GATE-02..05 unchecked | Owner sign-off on GATE-02..05 | **PENDING** | `LIVE_DATABASE_UNVERIFIED` | GATE-02..05 |
| **`DB-RLS-01`** | `a1089411c87d_enable_postgresql_rls_tenant_isolation.py` | `ACTIVE_BLOCKER` | Unexecuted in Mode A; lacks `generate_privilege_grants_ddl()` | Execute migration in Mode B after fixes | **NOT EXECUTED** | `LIVE_DATABASE_UNVERIFIED` | GATE-03, GATE-04 |
| **`WRK-DISP-01`** | `backend/app/tasks/run_riskcast_batch.py` (no `workers/`) | `ACTIVE_BLOCKER` | `acrevia_worker` & outbox daemon do not exist in code | Worker login/role + outbox consumer | **NOT IMPLEMENTED** | `LIVE_DATABASE_UNVERIFIED` | DB-AUTH-01 |
| **`RES-PULSE-01`** | `regional_pulse_service.py#L476-L551` | `ACTIVE_BLOCKER` | Provenance recalculation returns `0` under `FORCE RLS` | `verify_regional_signal_provenance()` + $k \ge 3$ | **NOT IMPLEMENTED** | `LIVE_DATABASE_UNVERIFIED` | D-01, DB-AUTH-01 |
| **`RES-PULSE-02`** | `farm_service.py#L84-L103` vs `regional_pulse_service.py` | `ACTIVE_BLOCKER` | Parent `FOR UPDATE` does not block `update_farm()` | `REPEATABLE READ` + source outbox invalidation | **NOT IMPLEMENTED** | `LIVE_DATABASE_UNVERIFIED` | Concurrency ADR |
| **`GATE01-PROV-01`** | `PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md` | `ACTIVE_BLOCKER` | `staging-rls-phase07` vs `staging-rls-phase05` mismatch | Owner branch clarification + live verify | **UNRESOLVED** | `LIVE_DATABASE_UNVERIFIED` | Owner Clarification |
| **`RES-PULSE-READ-01`** | `rls.py#L901-L907` & `regional_pulse.py#L68-L149` | `ACTIVE_BLOCKER` | Farmer read boundary unverified under live `FORCE RLS` | Command-scoped `FOR SELECT` + read-only GET | **NOT IMPLEMENTED** | `LIVE_DATABASE_UNVERIFIED` | D-01, GATE-04 |

---

## 20. RESIDUAL-RISK RECONCILIATION

All five canonical residual risks retain their exact governance severities:
- **`RES-PULSE-01` — MEDIUM:** Global expert/researcher evidence access without district scoping (`rls.py#L910-L920`).
- **`RES-PULSE-02` — MEDIUM:** Snapshot/concurrency skew across multi-query provenance verification under `READ COMMITTED`.
- **`RES-PRIMARY-ROUTING-01` — MEDIUM:** Write-on-read GET routes (`list_signals`, `get_signal`) failing on read replicas (SQLSTATE `25006`).
- **`RES-REPLICA-LAG-01` — LOW:** Read-replica lag serving stale signal states prior to suppression/recovery propagation.
- **`RES-FREE-TEXT-01` — LOW:** Unredacted PII risk in free-text fields.

**Preserved Governance Items:**
- **`DB-GRANT-APPLY-01`:** **`PROPOSED — OWNER APPROVAL REQUIRED`**.
- **`FARMER_READ_BLOCKED_BY_EVIDENCE_ASSOCIATION_RLS`:** Retained as a descriptive finding, not a canonical blocker ID.

---

## 21. OWNER DECISION AND EXECUTION-GATE RECONCILIATION

From [PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md) and [phase_07_owner_decision_evidence_traceability_matrix.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/phase_07_owner_decision_evidence_traceability_matrix.md):
- **D-01, D-02, D-03:** `OWNER_DECISION_REQUIRED` (`PENDING_PROJECT_OWNER_AUTHORIZATION`).
- **DB-AUTH-01:** `OWNER_DECISION_REQUIRED` — requires explicit extension to cover `acrevia_verifier`, `acrevia_worker_login`, and `acrevia_worker`.
- **GATE-01:** `[x] APPROVED BY OWNER (2026-11-10)` (`AUTH-TOKEN-GOKULK-20261110-GATE01-APPROVED`) — physical provisioning `LIVE_DATABASE_UNVERIFIED` in Mode A. Do not request re-approval.
- **GATE-02 through GATE-05:** `[ ] UNCHECKED (AWAITING SIGN-OFF)`.
- **Branch Discrepancy:** Register Section 1 & GATE-05 state `staging-rls-phase05`; GATE-01 states `staging-rls-phase07` (`GATE01-PROV-01`).
- **MODE B:** Strictly **`NOT_AUTHORIZED`**.

---

## 22. ADVERSARIAL SCENARIO MATRIX (ALL 28 SCENARIOS)

| # | Scenario | Attack / Failure Precondition | Expected PostgreSQL / App Behavior | Security / Operational Impact | Required Control |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | Expert recovery with empty tenant GUC | `app.current_tenant_id=''` | Source tables return 0 rows (`HTTP 400`) | Denial of service for legitimate recovery | `acrevia_verifier` `SECURITY DEFINER` function |
| 2 | App ADMIN with `app.is_admin='true'` & restricted `SESSION_USER` | `SESSION_USER='acrevia_staging_app'` | `ADMIN_BYPASS_SQL` = `FALSE` $\to$ 0 source rows | App admin cannot recover signals directly | Same verifier function + app role auth |
| 3 | Function under non-privileged owner | Owner lacks policy & `BYPASSRLS` | `FORCE RLS` filters source rows to 0 | Function always returns `(0, false)` | Targeted `TO acrevia_verifier` `SELECT` policy |
| 4 | Function under table owner with `FORCE RLS` | Table has `FORCE ROW LEVEL SECURITY` | Owner still subject to RLS | No automatic bypass | Explicit role policy (do not drop `FORCE RLS`) |
| 5 | Function under `BYPASSRLS` owner | Owner has `BYPASSRLS` | Reads all tables globally | Violates least privilege if function flawed | Prohibit `BYPASSRLS`; use targeted `SELECT` policy |
| 6 | Unauthorized district supplied by caller | Caller requests signal in foreign district | Currently succeeds if source visible | Cross-district unauthorized recovery | Enforce `expert_district_assignments` check |
| 7 | Signal ID belonging to another district | Expert in Khammam passes Adilabad `signal_id` | No district check in `recover_suppressed_signal` | Unauthorized state transition | DB + service district-jurisdiction check |
| 8 | Evidence references belonging to another tenant | Evidence links Farm A (Warangal) + Farm B (Khammam) | `recover_suppressed_signal` filters by `farm.district` | Must be excluded from count | Enforce `farm.district = signal.district` in SQL |
| 9 | Farm district changed during verification | `FarmService.update_farm()` commits concurrently | `READ COMMITTED` sees inconsistent snapshot | Stale outbreak confirmation | `REPEATABLE READ`/`SERIALIZABLE` + outbox invalidation |
| 10 | Farm archived during verification | `Farm.is_archived` set `True` concurrently | Same stale snapshot risk | Archived farm counted as active | `REPEATABLE READ` + outbox invalidation |
| 11 | Observation deleted during verification | `DELETE FROM observations` commits concurrently | `evidence_reference_id` dangles (no FK) | Ghost evidence counted | Soft-delete / outbox invalidation / `REPEATABLE READ` |
| 12 | Risk alert updated during verification | `acknowledge_alert`/`dismiss_alert` or DML | Concurrent commit | Stale alert status | Outbox invalidation + state predicate |
| 13 | Evidence inserted during verification | New `RegionalSignalEvidence` inserted | Parent `FOR UPDATE` blocks FK `FOR KEY SHARE` | Serialized if parent locked | Parent `FOR UPDATE` lock |
| 14 | Evidence association removed during verification | `DELETE` / `UPDATE` on `regional_signal_evidences` | Permitted if `UPDATE` granted in crosswalk | Evidence tampering | Revoke `UPDATE`/`DELETE`; `ON DELETE RESTRICT` |
| 15 | Duplicate recovery requests | Two experts POST `/recover` concurrently | Parent `FOR UPDATE` serializes; 2nd gets `HTTP 409` | Safe replay protection | Retain parent `FOR UPDATE` + status check |
| 16 | Worker crash during outbox processing | Worker dies after processing before ACK | Lease expires; row reclaimed by next worker | Potential duplicate processing | Idempotency keys + at-least-once consumer |
| 17 | Function owner privilege escalation | Attacker alters function or steals ownership | Blocked if `acrevia_staging_app` not owner/member | Severe if app role owns function | Separate `acrevia_verifier` owner; `NOCREATEROLE` |
| 18 | Search-path object shadowing | `CREATE TEMP TABLE farms(...)` | Hijacks unqualified `farms` if `pg_temp` first | Fake `count >= 3` | `SET search_path = public, pg_temp` + `public.farms` |
| 19 | Function `EXECUTE` granted to `PUBLIC` | Default PostgreSQL grant | Any role can enumerate signal IDs | Information disclosure | `REVOKE ALL FROM PUBLIC` |
| 20 | Below-threshold count disclosure | Function returns `count = 1` or `2` | Leaks sparse farm presence | Privacy leak ($k < 3$) | Return `is_valid` / gate raw count to authorized actors |
| 21 | Direct SQL manipulation of session GUCs | `SELECT set_config('app.current_user_id', ...)` | Succeeds in shared session (`RLS-ROLE-ASSIGNMENT-01`) | Impersonation if SQLi exists | Do not rely solely on GUCs; separate DB principals |
| 22 | Cross-district aggregate contamination | `farm.district` differs from `signal.district` | Filtered by `LOWER(TRIM(f.district)) = LOWER(TRIM(s.district))` | Inflated count if omitted | Mandatory district equality in verifier SQL |
| 23 | Parent lock acquired without source locks | Pruned `FOR SHARE` on `farms`/`observations` | Concurrent `update_farm` not blocked | Race condition (`RES-PULSE-02`) | Outbox invalidation + `REPEATABLE READ`/`SERIALIZABLE` |
| 24 | Source locks acquired without `UPDATE` privilege | `FOR SHARE` with `SELECT`-only grant | PostgreSQL throws SQLSTATE `42501` | Runtime crash | Remove client `FOR SHARE`; use verifier function |
| 25 | Recovery `UPDATE` rejected by column grants | Grant omits `is_outbreak_claim_suppressed` or `updated_at` | SQLAlchemy flush throws SQLSTATE `42501` | Recovery fails | Grant `UPDATE` on all 4 mutated parent columns |
| 26 | Audit record and recovery state inconsistent | Audit commits separately from signal | Already atomic (`AuditService.stage_activity` + outer commit) | Broken audit trail if split | Keep single outer transaction |
| 27 | Stale replica read used for recovery eligibility | Recovery routed to read replica | `FOR UPDATE` fails (`25006`) or stale count | Incorrect eligibility | Route recovery & writes strictly to primary |
| 28 | Credential fallback selected in deployment | `DATABASE_URL` unset in Next.js runtime | `db.ts#L10` connects with exposed `neondb_owner` URI | Unauthorized owner access | Remove fallback; fail closed; rotate secret |

---

## 23. FUTURE POSTGRESQL VERIFICATION MATRIX (`NOT EXECUTED — MODE A`)

All live PostgreSQL verification tests below are **`NOT EXECUTED — MODE A`** and require Owner approval of **GATE-02, GATE-03, and GATE-04**:

| Test ID | Verification Focus | Execution Status | Target Identity | Pass Criterion |
| :--- | :--- | :---: | :--- | :--- |
| **PG-V-01** | Role & effective identity assertions (`SESSION_USER` vs `CURRENT_USER`) | `NOT EXECUTED — MODE A` | `acrevia_staging_app`, `acrevia_worker_login` | `NOSUPERUSER NOBYPASSRLS`; `SET ROLE` switches `CURRENT_USER` only |
| **PG-V-02** | `FORCE RLS` & empty tenant GUC filter | `NOT EXECUTED — MODE A` | `acrevia_staging_app` | `SELECT` on `farms`/`observations`/`risk_alerts` returns 0 rows when `app.current_tenant_id=''` |
| **PG-V-03** | `SELECT`/`UPDATE` & `FOR ALL` policy composition on `FOR UPDATE`/`FOR SHARE` | `NOT EXECUTED — MODE A` | `acrevia_staging_app` | Locking `SELECT` evaluates both `SELECT` and `UPDATE` `USING`; ignores `WITH CHECK` |
| **PG-V-04** | `SECURITY DEFINER` function owner & `FORCE RLS` | `NOT EXECUTED — MODE A` | `acrevia_staging_app` calling `acrevia_verifier` fn | `ADMIN_BYPASS_SQL` stays `FALSE`; targeted `TO acrevia_verifier` policy permits aggregate read |
| **PG-V-05** | `search_path` shadowing & `PUBLIC` `EXECUTE` revocation | `NOT EXECUTED — MODE A` | Unprivileged role & `pg_temp.farms` | `PUBLIC` gets `42501`; temp table ignored |
| **PG-V-06** | District authorization & cross-tenant isolation | `NOT EXECUTED — MODE A` | Expert in Warangal | Adilabad `signal_id` rejected; cross-district farms excluded |
| **PG-V-07** | Minimum threshold (`N >= 3`) & below-threshold masking | `NOT EXECUTED — MODE A` | `acrevia_staging_app` | 2 distinct farms $\to$ `is_valid = false`; 3 distinct farms $\to$ `is_valid = true` |
| **PG-V-08** | Append-only evidence (`UPDATE`/`DELETE` revoked + `ON DELETE RESTRICT`) | `NOT EXECUTED — MODE A` | `acrevia_staging_app` | Evidence `UPDATE`/`DELETE` $\to$ `42501`; parent `DELETE` $\to$ `23001` |
| **PG-V-09** | Concurrent farm district update & `REPEATABLE READ` / outbox invalidation | `NOT EXECUTED — MODE A` | Concurrent sessions | Outbox event staged atomically; signal re-suppressed if count drops `< 3` |
| **PG-V-10** | Recovery idempotency, outbox `SKIP LOCKED`, & audit atomicity | `NOT EXECUTED — MODE A` | Concurrent experts + worker | 2nd expert gets `409`; rollback discards audit & outbox |
| **PG-V-11** | Credential configuration fail-closed check | `NOT EXECUTED — MODE A` | Next.js server process | Startup throws error when `DATABASE_URL` unset; zero hardcoded fallback |


---

## 24. REJECTED ARCHITECTURE ALTERNATIVES (`STATIC_SQL_SEMANTICS_VERIFIED`)

| Option | Architecture | Reason for Rejection / Non-Viability |
| :--- | :--- | :--- |
| **Option A** | **Current Application-Session Queries** | Fails closed under `FORCE RLS` (`app.current_tenant_id=''` $\to$ 0 rows). Requires either global `SELECT` on all tenant tables (violates tenant isolation) or weakening `ADMIN_BYPASS_SQL` (unsafe). |
| **Option B** | **Standalone Dedicated Worker with Global `SELECT`** | Granting `acrevia_worker` unrestricted raw `SELECT` across `farms`, `observations`, and `risk_alerts` violates least privilege; also introduces async recovery latency if used alone. |
| **Option C** | **`SECURITY INVOKER` Function** | Executes as caller (`acrevia_staging_app`); hits the exact same `RESTRICTIVE` tenant-isolation filter as Option A and returns 0 rows. |
| **Option E (Standalone)** | **Precomputed Provenance Projection Alone** | Without transactional source-mutation triggers/outbox on every writer, the projection drifts stale and fails during synchronous recovery verification. |

---

## 25. FINAL DESIGN VERDICT: `DESIGN_NOT_YET_PROVEN`

### 25.1 Explicit Proof Status
**Verdict:** **`DESIGN_NOT_YET_PROVEN`**

While a **Hybrid Option D + Option E** architecture (Constrained `SECURITY DEFINER` Verifier Function + Transactional Outbox Invalidation) is the **only viable candidate** that preserves tenant isolation, avoids `BYPASSRLS`, and eliminates client-side `FOR SHARE` lock-privilege conflicts, it is **not yet proven** for Phase 07 because five critical proof obligations remain unresolved:
1. `acrevia_verifier`, `acrevia_worker_login`, and `acrevia_worker` are unprovisioned and unapproved under `DB-AUTH-01`.
2. District jurisdiction enforcement (`EXP-AUTH-01` / normalized `expert_district_assignments`) does not exist in code or auth context.
3. Source-mutation outbox emitters (`FarmService.update_farm()`, `ObservationService`, `RiskService`) are unimplemented (`RES-PULSE-02`).
4. `RegionalSignal.id` (`VARCHAR(36)`) and `evidence_reference_id` (`VARCHAR(100)`, no FK) require schema/type alignment in the function DDL.
5. Live PostgreSQL 16 verification of `FORCE RLS` + `SECURITY DEFINER` + `TO acrevia_verifier` policy composition has not been executed (`LIVE_DATABASE_UNVERIFIED`).

### 25.2 Preferred Candidate Specification (Target Architecture)
1. **Trusted Identity Boundary:** `acrevia_staging_app` calls `verify_regional_signal_provenance(p_signal_id VARCHAR(36))`; `CURRENT_USER` switches to `acrevia_verifier` (`NOLOGIN NOSUPERUSER NOBYPASSRLS`); `SESSION_USER` remains `acrevia_staging_app` (`ADMIN_BYPASS_SQL` remains `FALSE`).
2. **Role & Ownership Model:** Function owned by `acrevia_verifier`; `REVOKE ALL FROM PUBLIC`; `GRANT EXECUTE TO acrevia_staging_app, acrevia_worker`.
3. **RLS Policy Model:** Role-targeted `PERMISSIVE FOR SELECT TO acrevia_verifier USING (true)` on `farms`, `observations`, `risk_alerts`, `regional_signals`, `regional_signal_evidences` (with `FORCE RLS` preserved). Command-scoped `FOR SELECT` / `FOR UPDATE` on `regional_signals` for `acrevia_staging_app`.
4. **District Authorization Model:** Normalized `expert_district_assignments(user_id, district, is_active)` verified inside recovery/function against `signal.district` (no client-mutable district GUC).
5. **Function Execution Contract:** `RETURNS TABLE (meets_threshold BOOLEAN, verified_distinct_farms_count INT)` with `SET search_path = public, pg_temp`, schema-qualified `public.*` tables, zero dynamic SQL, and threshold masking for non-privileged callers.
6. **Minimum Privilege Matrix:** `acrevia_staging_app` has `SELECT` + `UPDATE (distinct_farms_count, validation_status, is_outbreak_claim_suppressed, updated_at)` on `regional_signals`, `SELECT` on `regional_signal_evidences`, and `EXECUTE` on the verifier function—**zero** `UPDATE` on evidence and **zero** cross-tenant `SELECT` on `farms`/`observations`/`risk_alerts`.
7. **Concurrency Protocol:** Parent `RegionalSignal FOR UPDATE` + `REPEATABLE READ` (or `SERIALIZABLE` with retry) on recovery transaction + transactional outbox invalidation on all source mutations.
8. **Audit & Outbox Behavior:** Single outer transaction commits parent `RegionalSignal` update, `AuditService.stage_activity()`, and `SIGNAL_RECOVERED` outbox event atomically.
9. **Append-Only Evidence Guarantees:** `passive_deletes="all"` + `cascade="save-update, merge"` in ORM; `ON DELETE RESTRICT` on FK; `UPDATE`/`DELETE` revoked from `acrevia_staging_app` and `acrevia_worker`.
10. **Failure Handling:** Fail closed on invalid `p_signal_id`, unauthorized district, `< 3` distinct farms (`HTTP 400`), or replay (`HTTP 409`).

---

## 26. REQUIRED OWNER DECISIONS

1. **D-01, D-02, D-03:** Formal Project Owner selection in the Regional Pulse Decision Record.
2. **DB-AUTH-01 Extension:** Explicit authorization for `acrevia_verifier`, `acrevia_worker_login`, and `acrevia_worker` in addition to `acrevia_staging_app`.
3. **GATE-02 through GATE-05:** Signed authorization in `PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md` (keeping GATE-01 recorded as approved on 2026-11-10).
4. **`GATE01-PROV-01` Reconciliation:** Resolve `staging-rls-phase07` vs `staging-rls-phase05`.
5. **`DB-CREDENTIAL-EXPOSURE-01`:** Rotate exposed `neondb_owner` credential in Neon Console and authorize removal of the fallback in `frontend/lib/server/db.ts#L10`.

---

## 27. IMPLEMENTATION PREREQUISITES

Before any implementation or Mode B execution can be authorized:
1. Rotate exposed database credentials and remove `frontend/lib/server/db.ts#L10` fallback.
2. Obtain Owner sign-off on D-01..D-03, DB-AUTH-01 extension, and GATE-02..05.
3. Implement normalized `expert_district_assignments` and district validation (`EXP-AUTH-01`).
4. Implement `verify_regional_signal_provenance(VARCHAR(36))` owned by `acrevia_verifier` with hardened `search_path` and targeted `SELECT` policies.
5. Remove client-side `FOR SHARE` locks in `regional_pulse_service.py`, add `passive_deletes="all"` + `ON DELETE RESTRICT`, and decompose `FOR ALL` policies into command-scoped policies.
6. Implement transactional outbox invalidation emitters on source mutation paths and `acrevia_worker` consumer.
7. Execute the full Future PostgreSQL Verification Matrix (`PG-V-01` through `PG-V-11`) in Mode B staging.

---

## 28. EXPLICIT MODE A LIMITATIONS

- **Zero Live Database Connections:** No Neon Cloud staging or production SQL was executed (`LIVE_DATABASE_UNVERIFIED`).
- **Zero Modifications:** No source code, migrations, tests, governance registers, or Git history were modified.
- **Zero Credential Operations:** No credentials were printed, tested, or rotated.
- **Preservation:** All 7 tracked governance matrices and all 17 prior untracked Phase 07 assurance reports remain intact.
