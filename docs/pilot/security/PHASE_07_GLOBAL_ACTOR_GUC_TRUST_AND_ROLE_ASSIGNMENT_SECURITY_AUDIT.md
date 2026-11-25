# ACREVIA — PHASE 07: SHARED DATABASE ACTOR-GUC TRUST BOUNDARY, USER-ROLE PRIVILEGE ESCALATION & GLOBAL RLS IDENTITY ASSURANCE AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** `MODE A ONLY` — Local Source Inspection, Security Engineering, Offline Verification & Governance Documentation  
**Git Baseline Commit:** `dbad296c6f19c4bbe8eb48fcd7a0e07441cfa408` (`main`)  
**Methodology:** Everything Claude Code (ECC): `PLAN → TEST → IMPLEMENT ONLY IF DEFECT PROVEN → REVIEW → VERIFY → DOCUMENT`  
**Evaluation Date:** 2026-11-15T19:30:36+05:30  
**Determination:** `TECHNICAL_PREFLIGHT_BLOCKED_WITH_RECORDED_BLOCKERS`  

---

## 1. Executive Determination

A global adversarial audit of the PostgreSQL application-identity and authorization model was conducted under strict `MODE A ONLY` constraints. While earlier audits isolated write-authority bypass on regional signals (`RLS-WRITE-AUTH-01`) and read-privacy exposure on sub-threshold data (`RES-PULSE-READ-01`), this investigation has discovered and proven a fundamental, platform-wide privilege escalation vulnerability in the database authorization layer:

1. **Proven Role-Assignment Privilege Escalation (`RLS-ROLE-ASSIGNMENT-01`):**  
   [`PROVEN_FROM_LOCAL_POLICY_STRUCTURE`]  
   The `user_roles` table is categorized in `backend/app/database/rls.py` as `TableCategory.USER_OWNED` with column `'user_id'`. Consequently, its restrictive RLS policy evaluates:
   ```sql
   WITH CHECK (ADMIN_BYPASS_SQL OR user_id::text = current_setting('app.current_user_id', true))
   ```
   Simultaneously, `acrevia_staging_app` (the shared runtime database principal) receives full SQL privileges: `GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE user_roles TO acrevia_staging_app;`.  
   Because `app.current_user_id` is an unauthenticated, mutable session GUC set via `SET LOCAL` or `SELECT set_config(...)`, any caller with SQL execution under `acrevia_staging_app` can execute:
   ```sql
   SET LOCAL app.current_user_id = '<their-own-user-id>';
   INSERT INTO user_roles (user_id, role_id) VALUES ('<their-own-user-id>', 'ADMIN');
   ```
   PostgreSQL evaluates `user_id::text = current_setting('app.current_user_id', true)` as `TRUE`. No model constraint, database trigger, or restrictive policy blocks the assignment of the `'ADMIN'` role. The caller immediately acquires platform administrator status across the entire application. Furthermore, by changing `app.current_user_id` to an administrator's UUID, the caller can execute `DELETE FROM user_roles` to demote legitimate administrators. This is formally classified as a critical architectural blocker: **`RLS-ROLE-ASSIGNMENT-01`**.

2. **Global Actor-GUC Impersonation Surface (13 `USER_OWNED` Tables):**  
   [`PROVEN_FROM_LOCAL_POLICY_STRUCTURE`]  
   All 13 `USER_OWNED` tables (including `users`, `session_tokens`, `consent_records`, `expert_profiles`, and `api_applications`) rely on `current_setting('app.current_user_id', true)` with full `SELECT, INSERT, UPDATE, DELETE` grants for `acrevia_staging_app`. Arbitrary SQL under the shared connection can read sensitive PII, steal session refresh tokens, modify user profiles, or delete data for any user by altering `app.current_user_id`.

3. **Global Tenant-GUC Spoofing Surface (78 Tenant Tables):**  
   [`STATIC_POLICY_ANALYSIS`]  
   All 25 `TENANT_DIRECT` tables (e.g., `farms`, `farm_expenses`, `audit_logs`) and 53 `TENANT_INDIRECT` tables (e.g., `plots`, `plants`, `diagnosis_requests`) enforce tenant isolation exclusively against `current_setting('app.current_tenant_id', true)`. The database RLS policies perform **zero independent verification** that `app.current_user_id` is an authorized owner or member of `app.current_tenant_id`. That validation exists solely in the FastAPI application layer (`verify_farm_access`). Direct SQL under `acrevia_staging_app` can switch tenant context to any farm UUID at will.

4. **Restoration of Canonical Governance Register:**  
   [`LOCAL_SOURCE_VERIFIED`]  
   This audit formally restores the canonical definitions of Owner Decisions (`D-01`, `D-02`, `D-03`), `DB-AUTH-01`, and Residual Risks (`RES-PULSE-01`, `RES-PULSE-02`, etc.) to eliminate governance drift introduced in prior working notes.

Therefore, Phase 07 remains **`NOT RELEASED`**, Mode B remains **`STRICTLY NOT AUTHORIZED`**, and `RLS-WRITE-AUTH-01`, `RES-PULSE-READ-01`, and newly recorded **`RLS-ROLE-ASSIGNMENT-01`** remain active architectural blockers.

---

## 2. Exact Local and Public Baselines

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

### Exact Inventory
- **Staged Files:** Exactly **0** files staged.
- **Tracked Modifications:** Exactly **7** pre-existing modified files from prior audit phases.
- **Untracked Dossiers:** Exactly **18** governance documents in `docs/pilot/security/` (including this primary audit report).
- **Core Security Code Integrity:**
  - `backend/app/database/rls.py`: **100% byte-for-byte identical** to public commit `dbad296c` (`git diff HEAD` is empty).
  - Migration `a1089411c87d`: **100% byte-for-byte identical** to public commit `dbad296c` (`git diff HEAD` is empty).
  - Migration `d2894a11c87d`: Untouched.
- **Task Invariant:** Zero lines of application code, ORM models, migrations, or test implementations were created, deleted, or modified during this task.

---

## 3. Global GUC Inventory

[`LOCAL_SOURCE_VERIFIED` / `STATIC_POLICY_ANALYSIS`]

A comprehensive search of the codebase identified every point where custom PostgreSQL configuration parameters (`app.*`) are set, cleared, or read:

| GUC Name | Where Assigned / Set | Where Read / Evaluated | Target Policies & Functions | Authorization Scope & Decision | Trust Assumption & Limitations |
|---|---|---|---|---|---|
| **`app.current_user_id`** | `backend/app/database/rls.py`<br>`backend/app/security/dependencies.py`<br>(via `set_tenant_context`) | `backend/app/database/rls.py`<br>`generate_rls_ddl()` | All 13 `USER_OWNED` tables;<br>`regional_signals` author policy;<br>`regional_signal_evidences` policies | Restricts row visibility and DML to the row's owner (`user_id = current_setting(...)`) | **FLAWED TRUST BOUNDARY:** Transaction-local GUC is mutable by any SQL executing under `acrevia_staging_app`. Assumes application is sole SQL source. |
| **`app.current_tenant_id`** | `backend/app/database/rls.py`<br>`backend/app/security/dependencies.py`<br>(via `set_tenant_context`) | `backend/app/database/rls.py`<br>`generate_rls_ddl()` | All 25 `TENANT_DIRECT` tables;<br>All 53 `TENANT_INDIRECT` tables | Restricts tenant visibility and DML to matching `farm_id` | **UNVERIFIED TENANT CONTEXT:** Database policy does not verify that `current_user_id` is a member of `current_tenant_id`. Mutable via SQL. |
| **`app.is_admin`** | `backend/app/database/rls.py`<br>`backend/app/security/dependencies.py`<br>(via `set_tenant_context`) | `backend/app/database/rls.py`<br>`ADMIN_BYPASS_SQL` | All 132 classified tables | Bypasses all tenant and user isolation when evaluating RLS | **DEFENSE-IN-DEPTH ONLY:** Paired with `SESSION_USER` and `CURRENT_USER` checks. Does not grant bypass alone, but cannot authenticate an admin. |

### Assigning Context Mechanics
- In `backend/app/database/rls.py` (`set_tenant_context`):
  ```python
  session.execute(
      sa.text("SELECT set_config('app.current_tenant_id', :val, true)"),
      {"val": str(tenant_id)},
  )
  ```
  The parameter `is_local=true` scopes the GUC to the active database transaction. While this prevents connection-pool leakage across subsequent requests, it provides **zero cryptographic protection** against SQL executing inside the same transaction.

---

## 4. `user_roles` Table and Constraint Analysis

[`LOCAL_SOURCE_VERIFIED`]

Inspection of [user.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/user.py) and migration history demonstrates the exact schema structure of `user_roles`:

```python
class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        primary_key=True
    )
    role_id: Mapped[str] = mapped_column(
        String(50), 
        ForeignKey("roles.id", ondelete="CASCADE"), 
        primary_key=True
    )
```

### Constraint Verification:
1. **Primary Key:** Composite `(user_id, role_id)`. Enforces uniqueness of role assignments per user.
2. **Foreign Key `user_id`:** References `users.id` with `ON DELETE CASCADE`. Requires that `user_id` exists in `users`.
3. **Foreign Key `role_id`:** References `roles.id` with `ON DELETE CASCADE`. Valid seeded roles in `roles` are: `FARMER`, `AGRICULTURAL_EXPERT`, `RESEARCHER`, `ADMIN`.
4. **CHECK Constraints:** **ZERO**. There are no constraints restricting which roles can be inserted.
5. **Database Triggers:** **ZERO**. There are no triggers validating authorization before inserting into `user_roles`.
6. **Application Schema:** In `backend/app/schemas/auth.py`, `UserRegisterRequest` restricts registration input via Pydantic regex to `^(FARMER|AGRICULTURAL_EXPERT|RESEARCHER)$`. However, this check exists **only at the HTTP gateway**. The database layer has no knowledge of this restriction.

---

## 5. Role-Assignment Escalation Determination (`RLS-ROLE-ASSIGNMENT-01`)

[`PROVEN_FROM_LOCAL_POLICY_STRUCTURE`]

### 5.1 DDL and Grant Analysis
In `backend/app/database/rls.py`:
- **Classification:** `TABLE_CLASSIFICATION["user_roles"] = {"category": TableCategory.USER_OWNED, "column": "user_id"}`.
- **SQL Table Grants for `acrevia_staging_app`:**
  ```sql
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE user_roles TO acrevia_staging_app;
  REVOKE TRUNCATE, REFERENCES, TRIGGER ON TABLE user_roles FROM acrevia_staging_app;
  ```
- **Generated RLS Policies on `user_roles`:**
  ```sql
  CREATE POLICY user_roles_base_access_policy ON user_roles
      AS PERMISSIVE FOR ALL TO PUBLIC
      USING (true) WITH CHECK (true);

  CREATE POLICY user_roles_user_isolation_policy ON user_roles
      AS RESTRICTIVE FOR ALL TO PUBLIC
      USING (
          ADMIN_BYPASS_SQL 
          OR user_id::text = current_setting('app.current_user_id', true)
      )
      WITH CHECK (
          ADMIN_BYPASS_SQL 
          OR user_id::text = current_setting('app.current_user_id', true)
      );
  ```

### 5.2 Mathematical Proof of Privilege Escalation
Let an ordinary user have UUID $U_{\text{farmer}}$.  
Under the shared database connection (`acrevia_staging_app`), the caller executes:
```sql
SELECT set_config('app.current_user_id', 'U_farmer', true);
INSERT INTO user_roles (user_id, role_id) VALUES ('U_farmer', 'ADMIN');
```

1. **Table Grant Check:** `acrevia_staging_app` has `INSERT` on `user_roles`. $\implies \mathbf{PASS}$.
2. **Permissive Policy Check:** `user_roles_base_access_policy` evaluates `WITH CHECK (true)`. $\implies \mathbf{PASS}$.
3. **Restrictive Policy Check:** `user_roles_user_isolation_policy` evaluates:
   $$\text{ADMIN\_BYPASS\_SQL} \lor (U_{\text{farmer}} = \text{current\_setting('app.current\_user\_id', true)})$$
   Since `app.current_user_id` was set to $U_{\text{farmer}}$, the clause evaluates to $\text{FALSE} \lor \text{TRUE} = \mathbf{TRUE}$. $\implies \mathbf{PASS}$.
4. **Foreign Key Integrity:** $U_{\text{farmer}}$ exists in `users`; `'ADMIN'` exists in `roles`. $\implies \mathbf{PASS}$.
5. **Database Result:** **The row `('U_farmer', 'ADMIN')` is committed to `user_roles`.**

### 5.3 Application Elevation
On subsequent HTTP requests with $U_{\text{farmer}}$'s JWT, FastAPI's `get_current_user` ([dependencies.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/security/dependencies.py)) executes:
```python
user_roles = [r.id for r in user.roles]
is_admin = SystemRole.ADMIN.value in user_roles # Now evaluates to True!
if is_admin:
    set_tenant_context(db, tenant_id=None, user_id=user.id, is_admin=True)
```
The farmer is now recognized by FastAPI as a full system administrator, bypassing all `require_roles("ADMIN")` checks platform-wide!

### 5.4 Administrator Demotion / Role Stripping
Similarly, an attacker can demote legitimate administrators:
```sql
SELECT set_config('app.current_user_id', 'U_admin', true);
DELETE FROM user_roles WHERE user_id = 'U_admin' AND role_id = 'ADMIN';
```
Since `user_id = current_setting('app.current_user_id', true)` evaluates to `TRUE`, PostgreSQL permits the deletion.

$$\mathbf{Determination:}\ \mathbf{CRITICAL\ VULNERABILITY\ CONFIRMED\ (RLS-ROLE-ASSIGNMENT-01)}$$

---

## 6. Global Actor-GUC Impersonation Matrix (13 Tables)

[`PROVEN_FROM_LOCAL_POLICY_STRUCTURE`]

Every table categorized as `TableCategory.USER_OWNED` uses the identical restrictive policy template:
$$\text{USING / WITH CHECK}\ (ADMIN\_BYPASS\_SQL \lor \text{column}::\text{text} = current\_setting(\text{'app.current\_user\_id'}, true))$$
and grants `SELECT, INSERT, UPDATE, DELETE` to `acrevia_staging_app`:

| Table Name | Owner Column | Available DML Privileges | Impersonation Consequence via Mutable `app.current_user_id` | Impact Severity |
|---|---|---|---|---|
| **`user_roles`** | `user_id` | SELECT, INSERT, UPDATE, DELETE | **Self-elevation to ADMIN**; demotion of administrators; arbitrary role mutation. | **CRITICAL (`RLS-ROLE-ASSIGNMENT-01`)** |
| **`session_tokens`** | `user_id` | SELECT, INSERT, UPDATE, DELETE | **Theft of active refresh token hashes**; arbitrary revocation of valid user sessions. | **HIGH** |
| **`users`** | `id` | SELECT, INSERT, UPDATE, DELETE | **Read and modification of user PII** (phone, email, password hashes, verified status). | **HIGH** |
| **`api_applications`** | `user_id` | SELECT, INSERT, UPDATE, DELETE | Reading and tampering with external API client credentials and OAuth client secrets. | **HIGH** |
| **`webhook_endpoints`** | `user_id` | SELECT, INSERT, UPDATE, DELETE | Hijacking webhook URLs to redirect real-time agricultural telemetry to external servers. | **HIGH** |
| **`consent_records`** | `user_id` | SELECT, INSERT, UPDATE, DELETE | Unauthorized modification or revocation of DPDP-mandated farmer research consent. | **HIGH** |
| **`expert_profiles`** | `user_id` | SELECT, INSERT, UPDATE, DELETE | Forging expert qualifications, accreditation details, and advisory authorizations. | **MEDIUM** |
| **`data_mapping_profiles`** | `user_id` | SELECT, INSERT, UPDATE, DELETE | Tampering with ingestion data mapping rules and field transformations. | **MEDIUM** |
| **`community_memberships`**| `user_id` | SELECT, INSERT, UPDATE, DELETE | Forging membership or leadership in community collectives. | **LOW** |
| **`organization_memberships`**| `user_id` | SELECT, INSERT, UPDATE, DELETE | Forging administrative membership in agricultural organizations. | **MEDIUM** |
| **`event_registrations`** | `user_id` | SELECT, INSERT, UPDATE, DELETE | Unauthorized registration or cancellation of extension training events. | **LOW** |
| **`knowledge_feedback`** | `user_id` | SELECT, INSERT, UPDATE, DELETE | Spoofing community knowledge ratings and votes. | **LOW** |
| **`learning_feedback`** | `user_id` | SELECT, INSERT, UPDATE, DELETE | Spoofing training course feedback and survey results. | **LOW** |

---

## 7. Global Tenant-GUC Spoofing Matrix (78 Tables)

[`STATIC_POLICY_ANALYSIS`]

Tenant tables are split into `TENANT_DIRECT` (25 tables) and `TENANT_INDIRECT` (53 tables):
- **Policy Mechanism:** `farms_tenant_isolation_policy` and child policies check `farm_id::text = current_setting('app.current_tenant_id', true)`.
- **Structural Vulnerability:** RLS policies **do not verify user membership**. If an attacker sets `SET LOCAL app.current_tenant_id = '<target_farm_id>'`, RLS permits full access to that farm's records under `acrevia_staging_app`.

| Domain | Representative Tables | Tables Count | Potential Cross-Tenant Exposure via `app.current_tenant_id` Spoofing |
|---|---|---|---|
| **Core Farm Entity** | `farms`, `farm_memberships`, `farm_twins` | 3 | Reading farm geofences, land records, ownership details, and membership lists. |
| **Crop & Agronomy** | `plots`, `plants`, `crop_seasons`, `plot_geometries` | 18 | Reading and mutating crop variety, sowing dates, NDVI vegetation indices, and yield data. |
| **Financials** | `farm_expenses`, `crop_season_economics` | 4 | Complete exposure of farmer operating costs, debts, input purchases, and profit margins. |
| **Pest & Disease** | `observations`, `diagnosis_requests`, `predictions` | 12 | Tampering with disease diagnoses, pest observations, and AI prediction confidence scores. |
| **Interventions** | `intervention_records`, `treatment_records` | 6 | Exposing pesticide application history, chemical dosages, and irrigation schedules. |
| **Auditing & Sharing** | `audit_logs`, `data_sharing_grants`, `data_exchange_jobs`| 6 | Reading internal tenant audit trails and altering B2B data-sharing consent grants. |

$$\mathbf{Result:}\ \text{Tenant isolation is enforced exclusively by the application layer; direct database access is completely unpartitioned.}$$

---

## 8. Database Role and Membership Trust Model (`ADMIN_BYPASS_SQL`)

[`LOCAL_SOURCE_VERIFIED` / `STATIC_POLICY_ANALYSIS`]

Inspection of [rls.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py) reveals:
```sql
ADMIN_BYPASS_SQL = (
    SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
    AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
    AND current_setting('app.is_admin', true) = 'true'
)
```

### Analysis of the Dual-Boundary Predicate:
1. **`SESSION_USER`:** Represents the physical database user that established the connection. In PostgreSQL, `SESSION_USER` **cannot be changed** via `SET ROLE`. It can only be changed via `SET SESSION AUTHORIZATION`, which requires superuser privileges. As long as `acrevia_staging_app` is not a superuser, it cannot spoof `SESSION_USER`.
2. **`CURRENT_USER`:** Represents the active privilege context (affected by `SET ROLE` or `SECURITY DEFINER` functions). Requiring `CURRENT_USER IN ('neondb_owner', 'acrevia_admin')` prevents privilege escalation if an admin role invokes code that drops privileges.
3. **`current_setting('app.is_admin', true) = 'true'`:** A supplementary sanity assertion.
4. **Limitation:** While `ADMIN_BYPASS_SQL` securely prevents `acrevia_staging_app` from executing an administrative bypass on tables requiring admin status, it **does not protect `USER_OWNED` or `TENANT_DIRECT` tables**, because those tables contain alternative branches (`OR user_id = ...` or `OR farm_id = ...`) that bypass admin checks entirely!

---

## 9. Application and Worker Identity Boundaries

[`LOCAL_SOURCE_VERIFIED`]

### 9.1 FastAPI Request Boundary
- **JWT Authentication:** Cryptographically verified in `get_current_user` using secret key HMAC-SHA256.
- **Context Injection:** Once verified, `set_tenant_context` sets `app.current_user_id` and `app.current_tenant_id` on the transaction.
- **Security Posture:** Safe against unauthenticated external HTTP clients as long as no SQL injection vulnerabilities exist in endpoint parameters.

### 9.2 Background Worker Boundary (`WRK-DISP-01`)
- **Celery Tasks:** In `backend/app/tasks/run_riskcast_batch.py`, workers connect using the identical `acrevia_staging_app` principal.
- **Context Handling:** Workers invoke `set_tenant_context(db, tenant_id=farm_id, user_id=None, is_admin=False)`.
- **Vulnerability:** Background workers possess identical table-level DML privileges on `user_roles`, `users`, and `regional_signals`. A compromised asynchronous task can perform arbitrary privilege escalation.

---

## 10. Database Privilege-Separation Architecture Options

[`STATIC_POLICY_ANALYSIS`]

| Option | Architecture Concept | Security Boundary | Operational Complexity | Performance Impact |
|---|---|---|---|---|
| **Option A** | **Current Shared Role with Mutable GUCs** | Application layer only. Zero database-level defense against SQL injection or direct access. | Lowest (single connection pool). | None. |
| **Option B** | **Separate Database Logins per Application Role** (`acrevia_farmer`, `acrevia_expert`, `acrevia_admin`) | Kernel-enforced database role privileges. | Extreme complexity (multiple connection pools, dynamic pool routing). | High connection overhead. |
| **Option C** | **Dedicated Trusted Administrative Service / Process** | Administrative DML (role management, official advisories) executed exclusively by a dedicated service with private DB credentials. | Moderate (isolated worker / service process). | Minimal. Recommended long-term. |
| **Option D** | **Restricted Security-Definer Administrative Functions** | Direct table DML revoked; operations routed through audited PostgreSQL stored functions. | Moderate (migration of DML to stored procedures). | Low. |
| **Option E** | **Fail-Closed Privilege Stripping on Sensitive Tables** | Revoke `INSERT, UPDATE, DELETE` on `user_roles` from `acrevia_staging_app`. Role mutations restricted to administrative migrations. | Low. Immediate containment for pilot. | Zero. |

---

## 11. Security Architecture Invariants

[`STATIC_POLICY_ANALYSIS`]

| # | Architecture Invariant | Current Source Status | Evaluation & Evidence |
|---|---|---|---|
| 1 | Ordinary SQL cannot self-assign privileged roles | **VIOLATED** | `user_roles` RLS permits `INSERT` when `user_id = app.current_user_id`. |
| 2 | Ordinary SQL cannot read another user's role records | **VIOLATED** | Permissive OR on `regional_signals` and mutable GUC on `user_roles` permits cross-user inspection. |
| 3 | Ordinary SQL cannot impersonate another user for ownership | **VIOLATED** | All 13 `USER_OWNED` tables evaluate `user_id = app.current_user_id`. |
| 4 | Ordinary SQL cannot bypass regional privacy threshold | **VIOLATED** | Permissive `FOR ALL` policy on `regional_signals` grants statewide sub-threshold access. |
| 5 | Ordinary SQL cannot write official advisory states | **VIOLATED** | `RLS-WRITE-AUTH-01`: Author write policy lacks tier restrictions. |
| 6 | Ordinary SQL cannot modify existing official advisories | **VIOLATED** | `RLS-WRITE-AUTH-01`: Author update policy lacks old-row tier check. |
| 7 | Role modifications require independent authorization | **VIOLATED** | No independent database-level authorization exists for `user_roles`. |
| 8 | Background workers have a distinct identity boundary | **VIOLATED** | `WRK-DISP-01`: Celery workers share `acrevia_staging_app`. |
| 9 | Audit logs record real authorized actor | **PARTIALLY SATISFIED** | Audit service records JWT actor, but SQL caller can forge GUCs. |
| 10| Database grants preserve privilege separation | **VIOLATED** | `acrevia_staging_app` granted full DML on sensitive authorization tables. |
| 11| RLS and SQL grants evaluated as separate layers | **SATISFIED** | Local DDL generator correctly separates RLS policies from table grants. |
| 12| No assumption that application GUC is cryptographically signed | **VIOLATED** | Current RLS design erroneously treats session GUCs as authenticated principals. |

---

## 12. Adversarial Test Matrix (35 Conditions)

The following matrix specifies the full future adversarial test suite covering role escalation, identity impersonation, and tenant spoofing:

| # | Category | Target Assertion | Test Designation | Evidentiary Basis |
|---|---|---|---|---|
| 1 | Role Escalation | Ordinary user cannot self-assign ADMIN role | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Defect proven in Section 5 (`RLS-ROLE-ASSIGNMENT-01`). |
| 2 | Role Escalation | Ordinary user cannot self-assign EXPERT role | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Defect proven in Section 5 (`RLS-ROLE-ASSIGNMENT-01`). |
| 3 | Role Escalation | Ordinary user cannot insert privileged roles for others | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Defect proven in Section 5 (`RLS-ROLE-ASSIGNMENT-01`). |
| 4 | Role Escalation | Ordinary user cannot demote administrators | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Defect proven in Section 5 (`RLS-ROLE-ASSIGNMENT-01`). |
| 5 | Role Escalation | Ordinary user cannot delete another user's roles | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Defect proven in Section 5 (`RLS-ROLE-ASSIGNMENT-01`). |
| 6 | Role Escalation | Revoking DML on `user_roles` blocks direct SQL mutations | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Option E containment verification. |
| 7 | Actor Identity | GUC spoofing cannot grant access to `users` PII | Proposed / `LIVE_POSTGRESQL_REQUIRED` | User-owned policy analysis. |
| 8 | Actor Identity | GUC spoofing cannot grant access to `session_tokens` | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Token hash theft analysis. |
| 9 | Actor Identity | GUC spoofing cannot modify `consent_records` | Proposed / `LIVE_POSTGRESQL_REQUIRED` | DPDP consent compliance analysis. |
| 10 | Actor Identity | GUC spoofing cannot modify `expert_profiles` | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Profile tampering analysis. |
| 11 | Actor Identity | GUC spoofing cannot hijack `webhook_endpoints` | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Telemetry redirection analysis. |
| 12 | Tenant Isolation | `app.current_tenant_id` spoofing cannot switch farm reads | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Cross-tenant inspection analysis. |
| 13 | Tenant Isolation | `app.current_tenant_id` spoofing cannot switch plot reads | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Indirect tenant analysis. |
| 14 | Tenant Isolation | `app.current_tenant_id` spoofing cannot insert crop telemetry | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Cross-tenant write analysis. |
| 15 | Tenant Isolation | Cross-tenant UPDATE is denied by RLS | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Tenant DDL analysis. |
| 16 | Tenant Isolation | Cross-tenant DELETE is denied by RLS | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Tenant DDL analysis. |
| 17 | Tenant Isolation | Parent-child relationships cannot bridge tenants | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Foreign key cascade analysis. |
| 18 | Admin Identity | `app.is_admin=true` alone cannot bypass RLS | `LOCAL_TEST_VERIFIED` | Verified in `test_postgresql_rls.py`. |
| 19 | Admin Identity | `SESSION_USER` cannot be changed via `SET ROLE` | `LOCAL_TEST_VERIFIED` | Verified in `test_postgresql_rls.py`. |
| 20 | Admin Identity | SECURITY DEFINER function cannot spoof `SESSION_USER` | `LOCAL_TEST_VERIFIED` | Verified in `test_postgresql_rls.py`. |
| 21 | Regional Signals | Expert cannot insert `OFFICIAL_ADVISORY` | `LOCAL_TEST_VERIFIED` (Vulnerability Detector) | Proves `RLS-WRITE-AUTH-01`. |
| 22 | Regional Signals | Researcher cannot insert `OFFICIAL_ADVISORY` | `LOCAL_TEST_VERIFIED` (Vulnerability Detector) | Proves `RLS-WRITE-AUTH-01`. |
| 23 | Regional Signals | Expert cannot update signal to `OFFICIAL_ADVISORY` | `LOCAL_TEST_VERIFIED` (Vulnerability Detector) | Proves `RLS-WRITE-AUTH-01`. |
| 24 | Regional Signals | Researcher cannot update signal to `OFFICIAL_ADVISORY` | `LOCAL_TEST_VERIFIED` (Vulnerability Detector) | Proves `RLS-WRITE-AUTH-01`. |
| 25 | Regional Signals | Ordinary actor cannot modify existing official advisory | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Option D USING contract. |
| 26 | Regional Signals | Ordinary actor cannot demote official advisory | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Option D USING contract. |
| 27 | Regional Signals | Farmer cannot read sub-threshold signals ($N < 3$) | `LOCAL_TEST_VERIFIED` | Passed in worker test suite. |
| 28 | Regional Signals | Permissive OR does not leak sub-threshold signals | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Proves `RES-PULSE-READ-01`. |
| 29 | Evidence Lifecycle | Evidence INSERT requires non-official parent | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Child INSERT contract test. |
| 30 | Evidence Lifecycle | Evidence UPDATE prevents reparenting to official | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Child UPDATE contract test. |
| 31 | Evidence Lifecycle | Evidence DELETE denied for ordinary actors | `LOCAL_SOURCE_VERIFIED` | SQL grant `REVOKE DELETE`. |
| 32 | Indirect Paths | Ordinary principal cannot TRUNCATE | `LOCAL_SOURCE_VERIFIED` | SQL grant `REVOKE TRUNCATE`. |
| 33 | Indirect Paths | Zero triggers reintroduce write privileges | `LOCAL_SOURCE_VERIFIED` | Codebase audit clean. |
| 34 | Indirect Paths | Zero procedures bypass RLS boundaries | `LOCAL_SOURCE_VERIFIED` | Codebase audit clean. |
| 35 | Worker Identity | Worker tasks execute under dedicated DB identity | Proposed / `LIVE_POSTGRESQL_REQUIRED` | Proves `WRK-DISP-01`. |

---

## 13. New Blocker Assessment: `RLS-ROLE-ASSIGNMENT-01`

[`PROVEN_FROM_LOCAL_POLICY_STRUCTURE`]

- **Blocker Identifier:** `RLS-ROLE-ASSIGNMENT-01`
- **Title:** Mutable-GUC Role Assignment Privilege Escalation
- **Severity:** **CRITICAL** (Security Architecture & Privilege Boundary)
- **Status:** **`ACTIVE_ARCHITECTURAL_BLOCKER`**
- **Affected Table:** `user_roles`
- **Applicable Policy:** `user_roles_user_isolation_policy` (`AS RESTRICTIVE FOR ALL TO PUBLIC USING (ADMIN_BYPASS_SQL OR user_id::text = current_setting('app.current_user_id', true)) WITH CHECK (...)`)
- **Applicable Grants:** `GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE user_roles TO acrevia_staging_app;`
- **Exploitation Impact:** Any session executing SQL under `acrevia_staging_app` can assign itself the `'ADMIN'` role or demote existing administrators by executing transaction-local `SET LOCAL app.current_user_id`.
- **Immediate Containment:** Revoke `INSERT, UPDATE, DELETE ON TABLE user_roles FROM acrevia_staging_app;`. Ordinary application runtime does not mutate user roles; role assignments must be restricted to administrative migrations or a dedicated administrative service.
- **Architectural Remediation:** Implement Option E (privilege stripping) immediately in forward migration `a1089411c87e`, followed by Option C (dedicated administrative writer principal) for production.

---

## 14. Governance-Register Corrections

[`LOCAL_SOURCE_VERIFIED`]

Prior working notes inadvertently altered the definitions of Project Owner decisions and residual risks. The authoritative canonical records are restored as follows:

### 14.1 Canonical Project Owner Decisions:
- **Decision D-01 (Official Advisory Visibility & Data Model):**
  - *Option A:* Universal $N \ge 3$ Farm Privacy Threshold (No RLS exemption; state advisories require $\ge 3$ farms).
  - *Option B:* Dedicated `official_advisories` Table (Separates telemetry signals from administrative notices).
  - *Option C:* Conditional RLS Exception on `regional_signals` for `OFFICIAL_ADVISORY` ($N=0$ visible to public if official).
  - *Option D:* Privileged-Only Visibility During Pilot ($N=0$ visible only to admins/experts).
- **Decision D-02 (Government-Source Authenticity & Pilot Terminology):**
  - *Option A:* Retain `OFFICIAL_ADVISORY` enum with mandatory UI disclosure: `"Platform Administrator Broadcast — Not Verified Government Gazette"`.
  - *Option B:* Renaming enum to `ADMINISTRATIVE_NOTICE` across schema and API.
  - *Option C:* Strict external integration gate (no official advisory publication until verified API integration with Telangana Department of Agriculture).
- **Decision D-03 (Independent Agronomic Peer-Review Workflow):**
  - *Option A:* Single-Expert Creation Permitted for Pilot.
  - *Option B:* Dual-Expert Verification Gate (Creation staged as `PENDING_PEER_REVIEW`, requiring second independent expert).
  - *Option C:* Phase 08 Deferral (Advisory authoring restricted to Admin only until Phase 08).
- **Decision DB-AUTH-01 (Database Actor Identity & Writer Trust):**
  - *Option A:* Dual-Principal Architecture (`acrevia_staging_app` for ordinary read/write, `acrevia_trusted_writer` for official advisories).
  - *Option B:* Security-Definer Administrative Promotion Gateway (`promote_to_official_advisory()` stored function).
  - *Option C:* Direct Neon superuser / `BYPASSRLS` access — **REJECTED AS INSECURE BY ARCHITECTURE**.
  - *Option D:* Fail-Closed Application-Role Policy Enforcement.

### 14.2 Canonical Residual Risk Definitions:
- **`RES-PULSE-01`:** Role-global evidence access for experts/researchers without district scoping.
- **`RES-PULSE-02`:** Read Committed snapshot/concurrency consistency window.
- **`RES-PRIMARY-ROUTING-01`:** Read/write primary-routing dependency.
- **`RES-REPLICA-LAG-01`:** Replica-lag exposure.
- **`RES-FREE-TEXT-01`:** PII exposure through author-controlled free text.

---

## 15. ECC Adversarial Review Findings

1. **`architect`:** Confirms that categorizing `user_roles` as `USER_OWNED` is an architectural defect. Users must never possess row-level DML ownership over their authorization records. Revoking DML privileges from `acrevia_staging_app` is structurally required.
2. **`security-reviewer`:** Formally validates the proof of `RLS-ROLE-ASSIGNMENT-01`. Confirms that mutable session GUCs fail as security boundaries across all 13 `USER_OWNED` and 78 tenant tables when arbitrary SQL execution is possible.
3. **`database-reviewer`:** Confirms PostgreSQL 15/16 RLS behavior: restrictive `WITH CHECK` on `user_roles` evaluates to `TRUE` when `user_id = current_setting('app.current_user_id')`. Confirms that table-level `REVOKE INSERT, UPDATE, DELETE` overrides RLS and immediately blocks exploitation.
4. **`python-reviewer`:** Confirms that `backend/app/services/auth_service.py` only modifies `user.roles` during initial user registration. The application layer never requires runtime `UPDATE` or `DELETE` on `user_roles`.
5. **`fastapi-reviewer`:** Confirms that Pydantic regex validation on `UserRegisterRequest` (`^(FARMER|AGRICULTURAL_EXPERT|RESEARCHER)$`) blocks `ADMIN` registration via HTTP, but proves this provides zero defense against direct database SQL.
6. **`silent-failure-hunter`:** Discovered that tenant isolation across 78 tables contains zero database-level user verification, completely relying on FastAPI's `verify_farm_access`.
7. **`verification-loop`:** Traced all 35 adversarial test conditions and confirmed that existing test suites did not test `user_roles` self-elevation.
8. **`delivery-gate`:** Reconfirms that Phase 07 release gates remain closed. Prevents unauthorized Mode B transition.

---

## 16. Documentation Updated

[`LOCAL_SOURCE_VERIFIED`]

The following governance documents have been updated with dated addenda and synchronized to both `docs/pilot/security/` and the artifact directory:

1. [PHASE_07_GLOBAL_ACTOR_GUC_TRUST_AND_ROLE_ASSIGNMENT_SECURITY_AUDIT.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GLOBAL_ACTOR_GUC_TRUST_AND_ROLE_ASSIGNMENT_SECURITY_AUDIT.md) *(Primary Deliverable)*
2. [PHASE_07_READ_PRIVACY_AND_EVIDENCE_ASSOCIATION_SECURITY_COMPLETENESS_AUDIT.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_READ_PRIVACY_AND_EVIDENCE_ASSOCIATION_SECURITY_COMPLETENESS_AUDIT.md)
3. [PHASE_07_OPTION_D_READ_PRIVACY_AND_EVIDENCE_ASSOCIATION_COMPLETENESS_AUDIT.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OPTION_D_READ_PRIVACY_AND_EVIDENCE_ASSOCIATION_COMPLETENESS_AUDIT.md)
4. [PHASE_07_OPTION_D_FAIL_CLOSED_POLICY_CONTRACT_AND_REMEDIATION_READINESS.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OPTION_D_FAIL_CLOSED_POLICY_CONTRACT_AND_REMEDIATION_READINESS.md)
5. [PHASE_07_TRUSTED_WRITER_ARCHITECTURE_DECISION_RECORD.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_TRUSTED_WRITER_ARCHITECTURE_DECISION_RECORD.md)
6. [PHASE_07_PROJECT_OWNER_DECISION_AND_MODE_B_AUTHORIZATION_BRIEFING.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_PROJECT_OWNER_DECISION_AND_MODE_B_AUTHORIZATION_BRIEFING.md)
7. [phase_07_database_actor_identity_architecture_decision_analysis.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/phase_07_database_actor_identity_architecture_decision_analysis.md)
8. [phase_07_owner_decision_evidence_traceability_matrix.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/phase_07_owner_decision_evidence_traceability_matrix.md)
9. [PHASE_07_RLS_WRITE_AUTHORITY_HARDENING_AND_ACTOR_TRUST_AUDIT.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_RLS_WRITE_AUTHORITY_HARDENING_AND_ACTOR_TRUST_AUDIT.md)

---

## 17. Remaining Security Blockers

| Blocker ID | Severity | Description & Root Cause | Status | Resolution Requirement |
|---|---|---|---|---|
| **`RLS-ROLE-ASSIGNMENT-01`** | **CRITICAL** | `user_roles` categorized as `USER_OWNED` with full DML grants allows arbitrary self-assignment of `ADMIN` role via mutable GUC. | **ACTIVE ARCHITECTURAL BLOCKER** | Revoke DML privileges on `user_roles` from `acrevia_staging_app` via migration `a1089411c87e`. |
| **`RLS-WRITE-AUTH-01`** | **HIGH** | `regional_signals_author_write_policy` allows experts/researchers to insert and update `OFFICIAL_ADVISORY` states. | **ACTIVE ARCHITECTURAL BLOCKER** | Replace permissive `FOR ALL` policy with Option D command-specific policies. |
| **`RES-PULSE-READ-01`** | **HIGH** | Permissive `FOR ALL` policy combines via OR with public read, leaking sub-threshold ($N<3$) and suspended signals. | **ACTIVE ARCHITECTURAL BLOCKER** | Separate SELECT policy with scoped internal read boundary. |
| **`OWNER-AUTH-01`** | **HIGH** | Project Owner decisions D-01, D-02, D-03, and DB-AUTH-01 require formal recorded selections. | **GOVERNANCE BLOCKER** | Project Owner execution of decision register. |
| **`WRK-DISP-01`** | **MEDIUM** | Background Celery workers execute under shared `acrevia_staging_app` database identity. | **ACTIVE ARCHITECTURAL BLOCKER** | Define dedicated worker DB role with least-privilege grants. |
| **`DB-RLS-01`** | **HIGH** | RLS DDL and privilege crosswalk unvalidated against live PostgreSQL catalogs. | **INFRASTRUCTURE BLOCKER** | Execute Mode B live database validation once authorized. |
| **`GATE01-PROV-01`** | **MEDIUM** | Gate 01 signed in register but live database validation pending. | **RELEASE GATE BLOCKER** | Validate on staging DB. |

---

## 18. Owner Decisions (Pending & Blank)

[`OWNER_DECISION_REQUIRED`]

All Project Owner decision fields remain unselected and pending:

```text
[   ] D-01: OFFICIAL STATE ADVISORY PUBLIC READ PRIVACY EXCEPTION & DATA MODEL
      [ ] Option A — Universal N >= 3 Privacy Threshold (No RLS exemption; state advisories require >= 3 farms)
      [ ] Option B — Dedicated official_advisories Table (Architectural separation of telemetry from notices)
      [ ] Option C — Conditional RLS Exception on regional_signals for OFFICIAL_ADVISORY (N=0 visible if official)
      [ ] Option D — Privileged-Only Visibility During Pilot (N=0 visible only to admins/experts)
      STATUS: PENDING_PROJECT_OWNER_AUTHORIZATION

[   ] D-02: GOVERNMENT-SOURCE AUTHENTICITY AND PILOT TERMINOLOGY
      [ ] Option A — Retain OFFICIAL_ADVISORY with UI Disclosure ("Platform Administrator Broadcast — Not Verified Government Gazette")
      [ ] Option B — Rename Enum to ADMINISTRATIVE_NOTICE Across Schema and API
      [ ] Option C — Strict External Integration Gate (No official advisories until direct API with Agriculture Dept)
      STATUS: PENDING_PROJECT_OWNER_AUTHORIZATION

[   ] D-03: INDEPENDENT EXPERT PEER-REVIEW WORKFLOW
      [ ] Option A — Single-Expert Creation Permitted for Pilot
      [ ] Option B — Dual-Expert Verification Gate (Creation staged as PENDING_PEER_REVIEW)
      [ ] Option C — Phase 08 Deferral (Advisory authoring restricted to Admin only until Phase 08)
      STATUS: PENDING_PROJECT_OWNER_AUTHORIZATION

[   ] DB-AUTH-01: DATABASE WRITER IDENTITY & TRUST ARCHITECTURE
      [ ] Option A — Dual-Principal Architecture (acrevia_staging_app + acrevia_trusted_writer)
      [ ] Option B — Security-Definer Administrative Promotion Gateway
      [ ] Option D — Fail-Closed Application-Role Policy Enforcement
      [!] Option C — Direct Neon Superuser / BYPASSRLS Access (REJECTED AS INSECURE BY ARCHITECTURE)
      STATUS: PROPOSED — PENDING OWNER AUTHORIZATION
```

---

## 19. Live PostgreSQL Requirements

The following verification items cannot be resolved in Mode A and require live PostgreSQL access under Mode B:
1. Verification of physical role attributes (`SUPERUSER`, `BYPASSRLS`, `INHERIT`) for `acrevia_staging_app`.
2. Verification of live catalog grants in `information_schema.table_privileges`.
3. Verification that `acrevia_staging_app` cannot execute `SET ROLE neondb_owner` or `SET ROLE acrevia_admin`.
4. Verification of actual table constraints (`NOT NULL`, foreign keys) in `pg_constraint`.
5. Execution of live RLS policy evaluations under unprivileged multi-session connections.

---

## 20. Final Release Determination

$$\mathbf{DETERMINATION:\ TECHNICAL\_PREFLIGHT\_BLOCKED\_WITH\_RECORDED\_BLOCKERS}$$

### Justification:
1. **Critical Blocker `RLS-ROLE-ASSIGNMENT-01` Proven:** Ordinary SQL callers can self-assign `ADMIN` via mutable GUC on `user_roles`.
2. **Blockers `RLS-WRITE-AUTH-01` and `RES-PULSE-READ-01` Active:** Regional pulse write bypass and read privacy leaks remain open in current DDL.
3. **Decisions D-01, D-02, D-03, DB-AUTH-01 Pending:** Project Owner must sign decisions.
4. **Phase Status:** Phase 07 is **`NOT RELEASED`**. Mode B is **`STRICTLY NOT AUTHORIZED`**.

---

## 21. Exact Files Modified or Created

1. **Created (Primary Deliverable):**
   - [docs/pilot/security/PHASE_07_GLOBAL_ACTOR_GUC_TRUST_AND_ROLE_ASSIGNMENT_SECURITY_AUDIT.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GLOBAL_ACTOR_GUC_TRUST_AND_ROLE_ASSIGNMENT_SECURITY_AUDIT.md)
   - [PHASE_07_GLOBAL_ACTOR_GUC_TRUST_AND_ROLE_ASSIGNMENT_SECURITY_AUDIT.md](file:///C:/Users/gokul/.gemini/antigravity/brain/8d770357-1b73-48ca-9930-eded206539c2/PHASE_07_GLOBAL_ACTOR_GUC_TRUST_AND_ROLE_ASSIGNMENT_SECURITY_AUDIT.md) *(Artifact)*
2. **Updated with Dated Addenda & Synced to Artifact Directory:**
   - [docs/pilot/security/PHASE_07_READ_PRIVACY_AND_EVIDENCE_ASSOCIATION_SECURITY_COMPLETENESS_AUDIT.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_READ_PRIVACY_AND_EVIDENCE_ASSOCIATION_SECURITY_COMPLETENESS_AUDIT.md)
   - [docs/pilot/security/PHASE_07_OPTION_D_READ_PRIVACY_AND_EVIDENCE_ASSOCIATION_COMPLETENESS_AUDIT.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OPTION_D_READ_PRIVACY_AND_EVIDENCE_ASSOCIATION_COMPLETENESS_AUDIT.md)
   - [docs/pilot/security/PHASE_07_OPTION_D_FAIL_CLOSED_POLICY_CONTRACT_AND_REMEDIATION_READINESS.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OPTION_D_FAIL_CLOSED_POLICY_CONTRACT_AND_REMEDIATION_READINESS.md)
   - [docs/pilot/security/PHASE_07_TRUSTED_WRITER_ARCHITECTURE_DECISION_RECORD.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_TRUSTED_WRITER_ARCHITECTURE_DECISION_RECORD.md)
   - [docs/pilot/security/PHASE_07_PROJECT_OWNER_DECISION_AND_MODE_B_AUTHORIZATION_BRIEFING.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_PROJECT_OWNER_DECISION_AND_MODE_B_AUTHORIZATION_BRIEFING.md)
   - [phase_07_database_actor_identity_architecture_decision_analysis.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/phase_07_database_actor_identity_architecture_decision_analysis.md)
   - [phase_07_owner_decision_evidence_traceability_matrix.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/phase_07_owner_decision_evidence_traceability_matrix.md)
   - [PHASE_07_RLS_WRITE_AUTHORITY_HARDENING_AND_ACTOR_TRUST_AUDIT.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_RLS_WRITE_AUTHORITY_HARDENING_AND_ACTOR_TRUST_AUDIT.md)
3. **Application & Migration Code Modified:** **NONE** (0 lines changed).

---

### Final Governance Invariant
$$\mathbf{PHASE\ 07\ IS\ NOT\ RELEASED.}$$
$$\mathbf{MODE\ B\ IS\ STRICTLY\ NOT\ AUTHORIZED.}$$
$$\mathbf{ZERO\ APPLICATION\ SOURCE\ OR\ MIGRATION\ CODE\ MODIFIED.}$$

---

## 22. Dated Addendum — November 23, 2026: User-Role Containment, Registration Compatibility & Complete 78-Tenant Reconciliation

### 1. Operational Registration Conflict Identification
An adversarial review of `AuthService.register_user` (`backend/app/services/auth_service.py`) and Next.js onboarding routes (`frontend/app/api/v1/auth/register/route.ts`) proves that a naive blanket revocation of `INSERT` on `user_roles` from `acrevia_staging_app` causes immediate catastrophic failure (HTTP 500) for all user registrations. Role assignment during registration directly writes to `user_roles` under `acrevia_staging_app`.

### 2. Unverified Role Self-Selection Vulnerability
Both backend (`UserRegisterRequest`) and frontend schemas permit registrants to self-select `AGRICULTURAL_EXPERT` and `RESEARCHER` directly in the unauthenticated registration payload. This completely bypasses the administrative accreditation and verification workflow in `ExpertService.approve_or_reject_profile`.

### 3. Referential Integrity Cascade Risk
The foreign key `user_roles.user_id → users.id ON DELETE CASCADE` allows cascading role deletion if a user account is deleted. Because `acrevia_staging_app` possesses `GRANT DELETE ON TABLE users`, spoofing `app.current_user_id` allows an attacker to delete any user and wipe their roles without direct `DELETE` privileges on `user_roles`.

### 4. Complete 78-Table Tenant Reconciliation
All 25 direct tenant tables and 53 indirect tenant tables have been reconciled. Crucially, **0 out of 78 tables enforce independent user-membership verification in their PostgreSQL RLS policies.** All 78 tables exhibit `DIRECT_GUC_DEPENDENCY` or `INDIRECT_GUC_DEPENDENCY`.

### 5. Recommended Containment: Option E (Stored Function Gateway)
Direct DML on `user_roles` must be revoked from `acrevia_staging_app`, and registration must be transitioned to a secure `SECURITY DEFINER` stored procedure (`register_default_user_role(p_user_id)`), hardcoded to `'FARMER'` with zero caller parameterization. Privileged roles must be provisioned exclusively via administrative verification functions.

### 6. Companion Governance Documents
- Comprehensive Remediation Plan: [PHASE_07_GLOBAL_RLS_IDENTITY_REMEDIATION_AND_ROLE_MANAGEMENT_CONTAINMENT_PLAN.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GLOBAL_RLS_IDENTITY_REMEDIATION_AND_ROLE_MANAGEMENT_CONTAINMENT_PLAN.md)
- Complete Traceability Matrix: [PHASE_07_GLOBAL_GUC_AND_TENANT_POLICY_TRACEABILITY_MATRIX.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GLOBAL_GUC_AND_TENANT_POLICY_TRACEABILITY_MATRIX.md)

