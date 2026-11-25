# ACREVIA — PHASE 07: PUBLIC CREDENTIAL EXPOSURE, DATABASE PRINCIPAL RECONCILIATION & TRUSTED ROLE-PROVISIONING ARCHITECTURE ASSURANCE REPORT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** `MODE A ONLY` — Local Source Inspection, Security Engineering, Offline Verification, Architecture Design & Governance Documentation  
**Audit Baseline:** Commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Public Repository:** `https://github.com/gokul1599/ACREVIA`  
**Methodology:** Everything Claude Code (ECC): `PLAN → TEST → IMPLEMENT ONLY IF DEFECT PROVEN → REVIEW → VERIFY → DOCUMENT`  
**Date:** November 23, 2026  
**Final Governance Status:** `TECHNICAL_PREFLIGHT_BLOCKED_WITH_RECORDED_BLOCKERS` — `MODE B STRICTLY NOT AUTHORIZED`

---

## 1. Executive Determination

$$\mathbf{DETERMINATION:\ TECHNICAL\_PREFLIGHT\_BLOCKED\_WITH\_RECORDED\_BLOCKERS}$$

This security engineering assessment delivers a definitive preflight determination: Phase 07 is **strictly blocked from staging/production activation (`MODE B`)** due to an urgent, unmitigated public database-owner credential exposure in the frontend repository tree, combined with critical architectural gaps in application-role management and tenant-isolation enforcement.

### Key Incident & Architecture Determinations:
1. **Urgent Incident — Public Database-Owner Credential Exposure (`DB-CREDENTIAL-EXPOSURE-01`):**
   A plaintext database connection string with username `neondb_owner` and a cleartext password was committed to public source in [`frontend/lib/server/db.ts`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/lib/server/db.ts#L8-L11) (commit `63deadd`). The credential targets a live Neon Serverless PostgreSQL instance in AWS `ap-southeast-1`. It represents an unmitigated compromise of the database owner principal if active.
   - Classification: `PUBLIC_SECRET_EXPOSURE_CONFIRMED`.
   - Live Validity: `PUBLIC_SECRET_PATTERN_FOUND_LIVE_VALIDITY_UNKNOWN` (untested/unexercised).
   - Immediate Requirement: `REQUIRES_PROVIDER_OWNER_ACTION` (manual credential revocation and rotation in Neon Console).
2. **Database Principal Divergence Between Frontend and Backend:**
   The assumption that all application components share `acrevia_staging_app` is false in the repository source:
   - FastAPI Backend (`backend/app/database/session.py`): Defaults in source to local SQLite (`sqlite:///./acrevia_dev.db`), dynamically loading `settings.DATABASE_URL`. Effective deployed principal is `EFFECTIVE_RUNTIME_PRINCIPAL_UNKNOWN`.
   - Next.js Frontend (`frontend/lib/server/db.ts`): Uses `process.env.DATABASE_URL` with a committed fallback to `neondb_owner`. If the environment variable is absent or empty, the frontend executes raw SQL as the privileged database owner!
   - RiskCast Worker (`backend/app/tasks/run_riskcast_batch.py`): Inherits the backend's `SessionLocal` and fails closed in production/staging (`WRK-DISP-01`).
3. **Decoupled Threat Models for `RLS-ROLE-ASSIGNMENT-01`:**
   - **Scenario A (Public HTTP Registration Self-Selection):** Unauthenticated registrants can supply `role: "AGRICULTURAL_EXPERT"` or `role: "RESEARCHER"` in `UserRegisterRequest`, immediately gaining access to triage queues, farmer clinical dossiers, and regional signal aggregation without administrative verification.
   - **Scenario B (Arbitrary-SQL Administrative Escalation):** An attacker executing SQL under `acrevia_staging_app` spoofs `app.current_user_id` and inserts `('<user_id>', 'ADMIN')` into `user_roles`. Because `user_roles` is categorized as `USER_OWNED`, the restrictive `WITH CHECK` evaluates to `TRUE`, granting instant application platform administrator privileges on the next API request.
4. **Registration Gateway Design Proof (Capability A vs Capability B):**
   - **Capability A (Default FARMER Registration):** Safe to implement as a `SECURITY DEFINER` stored function (`register_default_user_role(p_user_id)`). It hardcodes `'FARMER'` with zero caller parameterization, completely eliminating self-escalation while preserving registration functionality.
   - **Capability B (Privileged Role Assignment):** **UNSAFE** if exposed as a `SECURITY DEFINER` function callable by `acrevia_staging_app`. Because `acrevia_staging_app` is a shared database login, any SQL caller can forge caller/admin identifiers in function arguments. Privileged role assignment MUST be restricted to an independently authenticated, trusted administrative database principal (`acrevia_admin`) via **Option D**.
5. **Universal Tenant GUC Dependency (All 78 Tenant Tables):**
   Exhaustive reconciliation of all 78 tenant tables (25 direct + 53 indirect) confirms that **zero tables enforce independent user-membership validation in PostgreSQL RLS**. Tenant boundary enforcement is 100% dependent on application-layer GUC assignment (`app.current_tenant_id`).

---

## 2. Mode A Scope and Limitations

- **Mode of Operation:** Strictly `MODE A ONLY` (Local Source Inspection, Static Security Modeling, Offline Testing, Governance Documentation).
- **Prohibitions Preserved:**
  - Zero connections to Neon, AWS, or remote databases.
  - Zero testing, verification, or reuse of discovered database passwords or connection URLs.
  - Zero SQL statements executed against live/staging databases.
  - Zero modifications to application source, ORM models, migrations, or tests.
  - Zero git commits, pushes, staging, rebases, or branch manipulations.
  - Zero secret values printed in terminal, test output, or audit reports.
- **Evidence Classifications Applied:**
  `LOCAL_SOURCE_VERIFIED`, `LOCAL_TEST_VERIFIED`, `PUBLIC_GITHUB_VERIFIED`, `STATICALLY_INFERRED`, `REQUIRES_LIVE_POSTGRESQL_VALIDATION`, `REQUIRES_PROVIDER_OWNER_ACTION`.

---

## 3. Local Git Baseline and Working-Tree Integrity

- **Repository Root:** `c:\Users\gokul\OneDrive\Documents\projects` [LOCAL_SOURCE_VERIFIED]
- **Current Branch:** `main` [LOCAL_SOURCE_VERIFIED]
- **Local HEAD SHA:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d` [LOCAL_SOURCE_VERIFIED]
- **Commit Metadata:** `Mon Nov 16 12:19:44 2026 +0530` — `docs(phase-07): record global actor-GUC trust, role-assignment, and regional pulse security assurance audits`
- **Configured Remote URL:** `https://github.com/gokul1599/ACREVIA.git` [LOCAL_SOURCE_VERIFIED]
- **Staged Changes:** Exactly 0 files (`git diff --cached --stat` is empty) [LOCAL_SOURCE_VERIFIED].
- **Tracked Modifications in Working Tree:** Exactly 7 documentation files in `docs/pilot/security/` (+101 lines):
  - `PHASE_07_FINAL_TECHNICAL_PREFLIGHT_STATUS.md`
  - `PHASE_07_GLOBAL_ACTOR_GUC_TRUST_AND_ROLE_ASSIGNMENT_SECURITY_AUDIT.md`
  - `PHASE_07_PROJECT_OWNER_DECISION_AND_MODE_B_AUTHORIZATION_BRIEFING.md`
  - `PHASE_07_READ_PRIVACY_AND_EVIDENCE_ASSOCIATION_SECURITY_COMPLETENESS_AUDIT.md`
  - `PHASE_07_TRUSTED_WRITER_ARCHITECTURE_DECISION_RECORD.md`
  - `phase_07_database_actor_identity_architecture_decision_analysis.md`
  - `phase_07_owner_decision_evidence_traceability_matrix.md`
- **Untracked Documentation Files:**
  - `docs/pilot/security/PHASE_07_GLOBAL_GUC_AND_TENANT_POLICY_TRACEABILITY_MATRIX.md`
  - `docs/pilot/security/PHASE_07_GLOBAL_RLS_IDENTITY_REMEDIATION_AND_ROLE_MANAGEMENT_CONTAINMENT_PLAN.md`
- **Core Security Source Invariants:**
  - `backend/app/database/rls.py`: 100% byte-for-byte identical to HEAD (`git diff HEAD` empty) [LOCAL_SOURCE_VERIFIED].
  - `backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py`: 100% identical to HEAD [LOCAL_SOURCE_VERIFIED].
  - `backend/app/database/migrations/versions/d2894a11c87d_stage12_collaborative_intelligence.py`: 100% identical to HEAD [LOCAL_SOURCE_VERIFIED].

---

## 4. Public GitHub Baseline and Commit Evidence

- **Observed Public Remote Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d` on branch `main` [PUBLIC_GITHUB_VERIFIED].
- **Public Lineage:** Commit `c9e334d` is an ancestor of the public history and contains the complete Phase 07 security preflight documentation.
- **Git History Ancestry:** Commit `63deadd` (`fix(auth): implement resilient serverless authentication, farmer registration and onboarding routes on neon postgresql and deploy to vercel`), which introduced the hardcoded credential fallback, is a confirmed public ancestor (`git merge-base --is-ancestor 63deadd c9e334d` returned 0) [PUBLIC_GITHUB_VERIFIED].

---

## 5. Public Credential-Exposure Incident Finding (`DB-CREDENTIAL-EXPOSURE-01`)

```text
================================================================================
INCIDENT FINDING: DB-CREDENTIAL-EXPOSURE-01
Classification:   PUBLIC_SECRET_EXPOSURE_CONFIRMED
Live Validity:    PUBLIC_SECRET_PATTERN_FOUND_LIVE_VALIDITY_UNKNOWN
Severity:         CRITICAL (CVSS 9.8 / CWE-798: Use of Hard-coded Credentials)
Location:         frontend/lib/server/db.ts, Lines 8-11
Repository Scope: Committed to public Git tree (commit 63deadd to HEAD c9e334d)
================================================================================
```

### 5.1 Exposure Mechanics
In [`frontend/lib/server/db.ts`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/lib/server/db.ts#L8-L13):
```typescript
  const dbUrl =
    process.env.DATABASE_URL ||
    "postgresql://neondb_owner:[REDACTED_PASSWORD]@ep-muddy-mode-a1nd6rrb-pooler.ap-southeast-1.aws.neon.tech/neondb?[REDACTED_PARAMS]";

  sqlInstance = neon(dbUrl);
  return sqlInstance;
```
- **Principal:** `neondb_owner` (Neon project owner, administrative database role).
- **Target Host:** `ep-muddy-mode-a1nd6rrb-pooler.ap-southeast-1.aws.neon.tech` (AWS Asia Pacific Singapore Neon connection pooler).
- **Target Database:** `neondb`.
- **Preconditions:** The secret is readable by anyone who clones or views the public GitHub repository. If an attacker extracts this connection URI and the endpoint remains active with the committed password, the attacker connects directly as the database owner.
- **Security Impact:**
  - Bypasses all application-layer authentication and FastAPI gateways.
  - Bypasses PostgreSQL Row-Level Security (as table owner / superuser-equivalent).
  - Permits arbitrary SELECT, INSERT, UPDATE, DELETE, and TRUNCATE across all 132 database entities.
  - Permits arbitrary schema modifications (`DROP TABLE`, `ALTER TABLE`), credential rotation, or data exfiltration.

---

## 6. Credential Scan Scope and Redacted Evidence Inventory

A repository-wide pattern scan covering all source code, configuration files, environment templates, and Git history identified 94 matching lines. All findings were scrubbed under the mandatory secret-redaction protocol:

| Source File | Line | Credential Pattern Type | Principal | Redacted Representative Snippet | Tree Presence |
|---|---|---|---|---|---|
| `frontend/lib/server/db.ts` | 10 | PostgreSQL Connection URI with plaintext password | `neondb_owner` | `"postgresql://neondb_owner:[REDACTED_PASSWORD]@ep-muddy-mode-a1nd6rrb-pooler.ap-southeast-1.aws.neon.tech/neondb?[REDACTED_PARAMS]"` | **Public Current Source & History** |
| `.env` (gitignored) | 13 | Local Environment Variable | `neondb_owner` | `DATABASE_URL="postgresql://neondb_owner:[REDACTED_PASSWORD]@ep-muddy-mode-a1nd6rrb-pooler.ap-southeast-1.aws.neon.tech/neondb?[REDACTED_PARAMS]"` | Local Workspace Only |
| `.env.staging.example` | 23 | Template Reference | `acrevia_staging_user` | `DATABASE_URL="postgresql://acrevia_staging_user:[REDACTED_PASSWORD]@ep-staging-pooler.../neondb"` | Public Source (Template) |
| `backend/tests/test_target_validation.py` | 150 | Mock Unit Test Fixture | `neondb_owner` | `prod_url = "postgresql://neondb_owner:[REDACTED_PASSWORD]@ep-muddy-mode-a1nd6rrb.../neondb"` | Public Source (Offline Test) |
| `docs/pilot/security/PHASE_07_MIGRATION_SAFETY_REPORT.md` | 55 | Documentation Example | `neondb_owner` | `STAGING_DATABASE_URL="postgresql://neondb_owner:[REDACTED_PASSWORD]@ep-staging.../neondb_staging"` | Public Documentation |

### Git History Scan:
- Search for commits introducing or altering `neondb_owner`: Commits `f5b3cc5`, `6171e16`, `2195b80`, `63deadd`, `fcce53a`, `428812d`, `b290158`, `5a3f1dc`, `bbd475d`, `c9e334d`.
- Commit `63deadd` physically introduced the production connection string into `frontend/lib/server/db.ts`.

---

## 7. Owner-Controlled Incident Response Plan

The following manual response actions must be executed exclusively by the authorized Project Owner. **No automated tool may attempt these actions:**

```text
[ ] STEP 1: Revoke / rotate the exposed password for 'neondb_owner' in the Neon Console immediately.
[ ] STEP 2: Verify role attributes, grants, and memberships of 'neondb_owner' in the Neon Console.
[ ] STEP 3: Review Neon Console query and connection logs for unauthorized access originating from external IPs.
[ ] STEP 4: Remove the hardcoded fallback from 'frontend/lib/server/db.ts', requiring process.env.DATABASE_URL.
[ ] STEP 5: Configure fail-closed application behavior: if DATABASE_URL is missing, throw a fatal startup error.
[ ] STEP 6: Provision a dedicated, least-privilege runtime role (e.g., 'acrevia_frontend_app') with NOSUPERUSER, NOBYPASSRLS.
[ ] STEP 7: Update deployment environment variables in Vercel / hosting provider with the new restricted role credentials.
[ ] STEP 8: Purge the plaintext secret from Git history using git-filter-repo or BFG Repo-Cleaner on a sanitized release branch.
[ ] STEP 9: Confirm that all replacement connection strings are stored exclusively in deployment secret stores.
[ ] STEP 10: Record the rotation date, operator, and incident resolution evidence in the governance register.
```

---

## 8. Backend / Frontend / Worker Database-Principal Matrix

| Client Component | Source Connection Helper | Environment Variable | Source Fallback Present? | Principal Derivable from Source | Effective Runtime Principal in Deployment |
|---|---|---|---|---|---|
| **FastAPI Backend** | `backend/app/database/session.py` | `DATABASE_URL` | Yes (`sqlite:///./acrevia_dev.db`) | None (Local SQLite) | `DEPLOYED_VALUE_NOT_ACCESSIBLE` / `UNKNOWN` |
| **Next.js Registration** | `frontend/lib/server/db.ts` | `DATABASE_URL` | **Yes (Hardcoded Neon URI)** | `neondb_owner` | `SOURCE_DEFAULT_IDENTIFIED` (`neondb_owner` if unset) |
| **Next.js Farm / Plot APIs** | `frontend/lib/server/db.ts` | `DATABASE_URL` | **Yes (Hardcoded Neon URI)** | `neondb_owner` | `SOURCE_DEFAULT_IDENTIFIED` (`neondb_owner` if unset) |
| **RiskCast Batch Worker** | `backend/app/tasks/run_riskcast_batch.py` | `DATABASE_URL` (via `SessionLocal`) | Yes (via backend settings) | None (Local SQLite) | `DEPLOYED_VALUE_NOT_ACCESSIBLE` (Fails closed: `WRK-DISP-01`) |
| **Alembic Migrations** | `backend/app/database/migrations/env.py` | `DATABASE_URL` | Yes (via backend settings) | None (Local SQLite) | Requires DDL Owner (`neondb_owner`) |

### Key Architectural Finding:
The frontend and backend do **not** necessarily run under the same database identity. If Vercel or local frontend environments omit `DATABASE_URL`, the frontend executes as the table owner `neondb_owner`, completely bypassing PostgreSQL RLS!

---

## 9. `ADMIN_BYPASS_SQL` Exposure Analysis

From [`backend/app/database/rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L22-L27):
```sql
ADMIN_ROLES = ("neondb_owner", "acrevia_admin")
ADMIN_BYPASS_SQL = (
    "(SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') "
    "AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') "
    "AND current_setting('app.is_admin', true) = 'true')"
)
```

### Analysis Under Frontend Fallback Principal (`neondb_owner`):
1. **`SESSION_USER` Condition:** When connecting via the frontend fallback, `SESSION_USER` is `neondb_owner` $\rightarrow$ **TRUE**.
2. **`CURRENT_USER` Condition:** In a standard serverless direct query, `CURRENT_USER` is `neondb_owner` $\rightarrow$ **TRUE**.
3. **`app.is_admin` Condition:** An SQL query executed through this session can issue `SELECT set_config('app.is_admin', 'true', false)` $\rightarrow$ **TRUE**.
4. **Conclusion:** If the frontend connects as `neondb_owner`, the full `ADMIN_BYPASS_SQL` condition can be satisfied by application code. Furthermore, on tables without `FORCE ROW LEVEL SECURITY`, `neondb_owner` as table owner bypasses RLS without evaluating any policy at all!

---

## 10. `user_roles` Policy and Privilege Reconstruction

### 10.1 Transcription Correction
The previous report contained an inaccurate transcription of the restrictive `WITH CHECK` expression.
- **Erroneous Transcription in Previous Summary:** `(ADMIN_BYPASS_SQL OR current_setting('app.current_user_id', true) = 'true')`.
- **Actual Verified Source Code ([`backend/app/database/rls.py#L387`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L387)):**
  ```sql
  WITH CHECK (
      (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
       AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
       AND current_setting('app.is_admin', true) = 'true')
      OR user_id::text = current_setting('app.current_user_id', true)
  );
  ```
The actual source code compares `user_id::text = current_setting('app.current_user_id', true)`. The erroneous string comparison was strictly a prose transcription error and does not exist in the codebase.

---

## 11. Separate Public Registration and Arbitrary-SQL Threat Models

| Dimension | Threat Model 1: Public HTTP Registration | Threat Model 2: Arbitrary-SQL Execution |
|---|---|---|
| **Vulnerability ID** | `APP-ROLE-SELF-SELECT-01` | `RLS-ROLE-ASSIGNMENT-01` |
| **Attacker Position** | Public internet, unauthenticated HTTP client | Attacker possessing SQL execution under `acrevia_staging_app` |
| **Attack Vector** | Submitting `{"role": "AGRICULTURAL_EXPERT"}` to `/auth/register` | Executing `SET LOCAL app.current_user_id = '<uuid>'; INSERT INTO user_roles ...` |
| **Roles Attainable** | `AGRICULTURAL_EXPERT`, `RESEARCHER` | `ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER` |
| **Database Grant Used** | Legitimate application execution of `INSERT` | Direct table grant `GRANT INSERT ON user_roles TO acrevia_staging_app` |
| **RLS Policy Check** | Bypassed / satisfied by app context | Restrictive `WITH CHECK` evaluates `user_id = app.current_user_id` $\rightarrow$ **TRUE** |
| **Downstream Impact** | Immediate access to clinical triage, management plans, and regional signals | Immediate platform administrator elevation across entire platform |
| **Remediation** | Lock registration schemas to `FARMER` only | Revoke DML on `user_roles`; deploy `register_default_user_role` gateway |

---

## 12. Endpoint-by-Endpoint Expert & Researcher Authorization Review

An exhaustive scan across all 212 API routes in `backend/app/api/v1/endpoints/` identified 10 privileged endpoints requiring expert or researcher roles:

| Route & Method | Required System Roles | Approval Dependency Enforced? | `ExpertProfile.verification_status` Checked? | `user.is_verified` Checked? | Tenant / Farm Membership Verified? | Self-Selected Registrant Access Result | Evidence Path & Line |
|---|---|---|---|---|---|---|---|
| `GET /api/v1/expertconnect/cases` | `AGRICULTURAL_EXPERT`, `ADMIN` | **NO** | **NO** | **NO** | No (queue-wide) | **FULL ACCESS GRANTED** | `expertconnect.py:177` |
| `POST /api/v1/expertconnect/cases/{id}/claim` | `AGRICULTURAL_EXPERT`, `ADMIN` | **NO** | **NO** | **NO** | No (claims queued case) | **FULL ACCESS GRANTED** | `expertconnect.py:196` |
| `GET /api/v1/expertconnect/cases/{id}` | Any authenticated user | **NO** | **NO** | **NO** | No (dossier view) | **FULL ACCESS GRANTED** | `expertconnect.py:223` |
| `POST /api/v1/expertconnect/cases/{id}/assess` | `AGRICULTURAL_EXPERT`, `ADMIN` | **NO** | **NO** | **NO** | No (prescribes IPM plan) | **FULL ACCESS GRANTED** | `expertconnect.py:236` |
| `PUT /api/v1/expertconnect/cases/{id}/assess` | `AGRICULTURAL_EXPERT`, `ADMIN` | **NO** | **NO** | **NO** | No (revises IPM plan) | **FULL ACCESS GRANTED** | `expertconnect.py:278` |
| `POST /api/v1/diagnoses/{id}/expert-review` | `AGRICULTURAL_EXPERT` | **NO** | **NO** | **NO** | No (diagnostic override) | **FULL ACCESS GRANTED** | `expert_reviews.py:26` |
| `POST /api/v1/knowledge/sources` | `ADMIN`, `AGRICULTURAL_EXPERT` | **NO** | **NO** | **NO** | No (registers sources) | **FULL ACCESS GRANTED** | `knowledge.py:89` |
| `POST /api/v1/knowledge/ingest` | `ADMIN`, `AGRICULTURAL_EXPERT` | **NO** | **NO** | **NO** | No (triggers ETL) | **FULL ACCESS GRANTED** | `knowledge.py:142` |
| `POST /api/v1/regional-pulse/signals` | `ADMIN`, `EXPERT`, `RESEARCHER` | **NO** | **NO** | **NO** | No (regional aggregation) | **FULL ACCESS GRANTED** | `regional_pulse.py:31` |
| `POST /api/v1/regional-pulse/signals/{id}/recover` | `ADMIN`, `AGRICULTURAL_EXPERT` | **NO** | **NO** | **NO** | No (recovers signals) | **FULL ACCESS GRANTED** | `regional_pulse.py:156` |

### Critical Finding:
`get_current_user` checks **only** `user.is_active`. It does **not** check `user.is_verified`. `require_roles` checks **only** `role in user.roles`. **Not a single expert route checks `ExpertProfile.verification_status == 'APPROVED'`.** A self-selected expert who registers via HTTP can immediately inspect farmer foliar images, claim triage cases, prescribe pesticide management plans, and view unredacted regional evidence.
- Classification: `PUBLIC_ROLE_SELF_SELECTION_CONFIRMED` + `PRIVILEGED_ENDPOINT_ACCESS_CONFIRMED`.

---

## 13. Role Cache, JWT and Revocation Analysis

- **JWT Validation:** In [`backend/app/security/dependencies.py#L43-L70`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/security/dependencies.py#L43-L70), `get_current_user` validates the JWT signature, extracts `sub=user_id`, and then executes `db.get(User, user_id)`.
- **Role Source of Truth:** It evaluates `user_roles = [r.id for r in user.roles]` directly from the database table on every single request.
- **Cache Absence:** There is **no Redis or in-memory cache** for user roles.
- **Propagation Speed:**
  - When an attacker inserts a role into `user_roles`, it becomes active **immediately** on their next HTTP request.
  - When a role is deleted from `user_roles`, the revocation takes effect **immediately** on the next request.

---

## 14. User-Deletion and FK-Cascade Analysis

- `user_roles.user_id` references `users.id` with `ON DELETE CASCADE`.
- In PostgreSQL, foreign-key referential actions **bypass Row-Level Security**.
- The privilege crosswalk grants `GRANT DELETE ON TABLE users TO acrevia_staging_app`.
- An attacker with SQL access under `acrevia_staging_app` can set `SET LOCAL app.current_user_id = '<target_admin_uuid>'` and execute:
  ```sql
  DELETE FROM users WHERE id = '<target_admin_uuid>';
  ```
  PostgreSQL deletes the `users` row. The database engine automatically cascades and deletes all rows for that user in `user_roles`, **even if `acrevia_staging_app` has ZERO DELETE privileges on `user_roles`!**
- **Mandate:** Direct `DELETE` on `users` must be revoked from `acrevia_staging_app`. Account termination must be handled via soft-delete (`is_active = False`).

---

## 15. Complete 13-Table User-Owned Table Implications

All 13 user-owned tables share the restrictive policy:
$$\text{USING / WITH CHECK}\ (ADMIN\_BYPASS\_SQL \lor user\_id::\text{text} = \text{current\_setting}('app.current\_user\_id', \text{true}))$$
and are granted `SELECT, INSERT, UPDATE, DELETE` to `acrevia_staging_app`.

| Table | Sensitive Data Exposed Under Spoofed GUC | Modification Impact Under Spoofed GUC | Severity |
|---|---|---|---|
| `users` | Password hash, phone, email | Overwrite password hash, account takeover, cascade delete | **CRITICAL** |
| `session_tokens` | Refresh token hash (metadata only) | Token deletion (DoS), inserting arbitrary sessions | **HIGH** |
| `user_roles` | Current system roles | Self-escalation to `ADMIN`, demoting administrators | **CRITICAL** |
| `consent_records` | Statutory DPDPA consent flags | Forging or revoking data-processing consent | **HIGH** |
| `api_applications` | Registered OAuth clients, redirect URIs | Altering redirect URIs for auth code interception | **HIGH** |
| `webhook_endpoints` | Destination URLs, subscribed event types | Redirection of outgoing webhooks to attacker host | **HIGH** |
| `data_mapping_profiles`| Proprietary ETL schemas | Corrupting data transformation rules | **MEDIUM** |
| `expert_profiles` | Verification status, registration number | Self-approval of agronomic accreditation | **HIGH** |
| `community_memberships`| Community membership status | Self-promotion to community moderator | **HIGH** |
| `organization_memberships`| Org membership status | Self-promotion to organization admin | **HIGH** |
| `event_registrations` | Training event enrollment | Event registration manipulation | **LOW** |
| `knowledge_feedback` | Feedback text, resolution notes | Feedback tampering | **LOW** |
| `learning_feedback` | Course review ratings | Rating score manipulation | **LOW** |

---

## 16. Complete 78-Table Tenant Inventory Reconciliation

The database contains exactly **78 tenant tables** (25 direct + 53 indirect):
- **Direct Tenant Tables (25):** `audit_logs`, `crop_loss_evidence_packages`, `data_exchange_jobs`, `data_sharing_grants`, `expert_review_cases`, `farm_expenses`, `farm_memberships`, `farm_twins`, `farms`, `intervention_records`, `location_permissions`, `observations`, `optimization_problems`, `plots`, `produce_lots`, `risk_alerts`, `risk_assessment_records`, `risk_assessments`, `sensor_devices`, `storage_locations`, `twin_snapshots`, `water_sources`, `weather_data`, `weather_observations`, `webhook_events`.
- **Indirect Tenant Tables (53):** `api_credentials`, `climate_adaptation_scenarios`, `climate_exposure_assessments`, `crop_season_economics`, `crop_seasons`, `crop_stage_events`, `crop_tasks`, `decision_feedbacks`, `decision_records`, `diagnosis_requests`, `environmental_accounting_estimates`, `expert_assessment_revisions`, `expert_assessments`, `expert_reviews`, `farm_operations`, `farm_practice_records`, `financial_corrections`, `fusion_explanations`, `harvest_measurements`, `harvest_plans`, `harvest_sessions`, `image_quality_assessments`, `irrigation_events`, `lot_movements`, `nutrient_assessments`, `nutrient_expert_reviews`, `observation_media`, `optimization_results`, `outcome_observations`, `plants`, `plot_geometries`, `prediction_candidates`, `predictions`, `quality_measurements`, `resilience_assessments`, `resilience_scenario_simulations`, `sale_transactions`, `satellite_observations`, `sensor_calibrations`, `sensor_measurements`, `simulation_results`, `simulation_scenarios`, `soil_carbon_measurements`, `soil_moisture_observations`, `soil_profiles`, `soil_samples`, `soil_test_results`, `storage_lots`, `twin_state_records`, `twin_synchronization_events`, `water_balance_snapshots`, `webhook_deliveries`, `yield_forecast_records`.

### Source Comment Stale Count Reconciliation:
- `backend/app/database/rls.py`, line 41: Comment says `24 tables` $\rightarrow$ Actual count is **25**.
- `backend/app/database/rls.py`, line 83: Comment says `51 tables` $\rightarrow$ Actual count is **53**.

---

## 17. Direct / Indirect GUC Policy Reconciliation

- **Direct Tenant Policy (`generate_rls_ddl`):**
  Checks `farm_id::text = current_setting('app.current_tenant_id', true)`.
  *Special Case `farms`:* Uses `id::text = current_setting('app.current_tenant_id', true)`. The `owner_column: "owner_id"` recorded in metadata is **never referenced in the generated SQL policy**.
- **Indirect Tenant Policy (`generate_rls_ddl`):**
  Checks parent join matching `current_setting('app.current_tenant_id', true)` OR `current_setting('app.current_user_id', true)`.
- **Core Defect:** **0 out of 78 tables verify tenant membership in PostgreSQL RLS.** Both direct and indirect policies trust caller-supplied session GUCs completely.

---

## 18. SECURITY DEFINER Registration-Gateway Design (Capability A)

### 18.1 Function Specification
```sql
CREATE OR REPLACE FUNCTION register_default_user_role(p_user_id UUID)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    -- Verify user exists
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = p_user_id::text) THEN
        RAISE EXCEPTION 'User % does not exist', p_user_id;
    END IF;

    -- Strictly insert default FARMER role; zero parameterization of role_id
    INSERT INTO user_roles (user_id, role_id)
    VALUES (p_user_id::text, 'FARMER')
    ON CONFLICT (user_id, role_id) DO NOTHING;
END;
$$;

REVOKE ALL ON FUNCTION register_default_user_role(UUID) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION register_default_user_role(UUID) TO acrevia_staging_app;
```

### 18.2 Security Proof
- **No Privileged Role Parameter:** The caller cannot pass `'ADMIN'` or `'AGRICULTURAL_EXPERT'`.
- **Least Privilege:** `acrevia_staging_app` has `REVOKE ALL ON TABLE user_roles`, possessing only `EXECUTE` on this function.
- **Atomicity:** Executed in the same transaction as user creation in `AuthService.register_user`.
- **Integrity:** `users.id` foreign key and existence check ensure orphaned roles cannot be created.

---

## 19. Privileged Role-Provisioning Design (Capability B)

### 19.1 Why SECURITY DEFINER Fails for Privileged Roles Under a Shared Principal
If a function `assign_privileged_role(p_user_id, p_role_id, p_admin_id)` is granted to `acrevia_staging_app`:
Any attacker executing SQL under `acrevia_staging_app` passes the UUID of an existing admin as `p_admin_id`. The database engine **cannot distinguish** between a legitimate administrator and an attacker spoofing that administrator's ID.

### 19.2 The Correct Architecture: Option D (Separate Trusted Administrative Principal)
- **Runtime App Principal (`acrevia_staging_app`):** Zero write permissions on `user_roles`. Zero execute permissions on privileged role functions.
- **Trusted Role Admin Principal (`acrevia_admin`):** A dedicated, physically isolated database principal with separate credentials, used exclusively by:
  1. Administrative back-office services.
  2. The expert verification approval endpoint (`ExpertService.approve_or_reject_profile`).
  3. Out-of-band administrative provisioning CLIs.

---

## 20. Architecture Options and Recommendation

| Option | Role Containment | Registration Preserved? | Prevents Privilege Escalation? | Complexity | Recommendation |
|---|---|---|---|---|---|
| **1. Blanket DML Revocation** | High | **NO (BREAKS REGISTRATION)** | Yes | Low | Rejected (Non-functional) |
| **2. Trigger-Guarded DML** | Medium | Yes | Partial | Medium | Suboptimal |
| **3. Capability A Gateway (Default) + Option D (Privileged)** | **Highest** | **YES** | **YES** | Medium | **RECOMMENDED** |
| **4. Direct Superuser Application Access** | None | Yes | **NO (INSECURE)** | Low | **REJECTED (INSECURE)** |

---

## 21. Migration Graph and Forward-Only Implementation Plan

- **Current Graph HEAD:** `a1089411c87d_enable_postgresql_rls_tenant_isolation.py`.
- **Next Forward Migration:** `a1089411c87e` (`down_revision = 'a1089411c87d'`).
- **Downgrade Hazard:** Downgrading `a1089411c87d` executes `ALTER TABLE {tbl} DISABLE ROW LEVEL SECURITY;` across all 132 tables.
- **Mandate:** All database security changes must be **forward-only**.

---

## 22. Worker Privilege and Task Identity Review

- Worker script: [`backend/app/tasks/run_riskcast_batch.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/tasks/run_riskcast_batch.py).
- Fails closed in production/staging (`ProductionDispatchBlockedError: DISPATCH_NOT_CONFIGURED`) (`WRK-DISP-01`).
- Uses `SYSTEM_WORKER_IDENTITY = "system:worker:riskcast"`.
- Threat: In local dev, inherits the shared backend principal's database privileges.

---

## 23. Adversarial Test Specification (38 Tests Across 5 Domains)

- **Domain 1 (01–12):** Role Assignment, Default Farmer Registration, Expert Self-Selection Denial, Cache Invalidation.
- **Domain 2 (13–19):** Actor-GUC Boundary, `users` Password Overwrite Denial, Session Token Integrity, Consent Falsification Denial.
- **Domain 3 (20–27):** Tenant-GUC Boundary, Cross-Farm Access Denial, Worker Tenant Bounds.
- **Domain 4 (28–33):** Role & Database Identity, `SET ROLE` Denial, `ADMIN_BYPASS_SQL` GUC Forgery Denial.
- **Domain 5 (34–38):** Privilege Crosswalk, FK Cascade Deletion Verification, TRUNCATE Denial.

---

## 24. ECC Independent Review

Conducted across 6 specialized review roles:
- **`security-reviewer`:** Confirmed that `DB-CREDENTIAL-EXPOSURE-01` is a critical public secret incident requiring immediate provider-level password rotation.
- **`database-reviewer`:** Validated that 0/78 tenant tables independently check membership in PostgreSQL RLS.
- **`architect`:** Proved that Capability B cannot be safely implemented as a SECURITY DEFINER function under a shared database login; endorsed Option D.
- **`fastapi-reviewer`:** Proved that `require_roles` checks only `user_roles`, allowing self-selected experts to access all triage and clinical endpoints.
- **`silent-failure-hunter`:** Proved that blanket DML revocation breaks user registration.
- **`delivery-gate`:** Verified that zero application source code, tests, or migrations were modified under Mode A.

---

## 25. Owner Decisions and Release-Gate Register

### Canonical Owner Decisions:
```text
D-01: OFFICIAL ADVISORY DATA MODEL & VISIBILITY
      [ ] Choice 1 — Universal N>=3 Threshold Across All Signal Types
      [ ] Choice 2 — Dedicated official_advisories Table
      [ ] Choice 3 — Conditional Exception with Strict Write Restrictions
      [ ] Choice 4 — Privileged-Only Visibility During Pilot Phase
      STATUS: PENDING_PROJECT_OWNER_AUTHORIZATION

D-02: GOVERNMENT-SOURCE AUTHENTICITY & PILOT TERMINOLOGY (RESTORED CANONICAL)
      [ ] Option A — Retain OFFICIAL_ADVISORY with disclosure: "Platform Administrator Broadcast — Not Verified Government Gazette"
      [ ] Option B — Rename enum to ADMINISTRATIVE_NOTICE
      [ ] Option C — Make external government API integration a release gate
      STATUS: PENDING_PROJECT_OWNER_AUTHORIZATION

D-03: INDEPENDENT AGRONOMIC PEER-REVIEW WORKFLOW
      [ ] Path 1 — Single-Expert Creation and Publication
      [ ] Path 2 — Dual-Expert Verification Gate Before Promotion
      [ ] Path 3 — Deferral to Phase 08
      STATUS: PENDING_PROJECT_OWNER_AUTHORIZATION

DB-AUTH-01: TRUSTED DATABASE WRITER IDENTITY ARCHITECTURE
      [ ] Option A — Dual-Principal Database Architecture (Runtime App vs Trusted Admin)
      [ ] Option B — Dedicated SECURITY DEFINER Stored Function Gateway
      [ ] Option D — Fail-Closed Application-Role Policy Enforcement
      [!] Option C — Direct Neon Superuser / BYPASSRLS Access (REJECTED AS INSECURE)
      STATUS: PROPOSED — PENDING OWNER AUTHORIZATION
```

### Release Gates:
- `GATE-01`: Staging branch provisioned; live validation pending.
- `GATE-02` through `GATE-05`: `NOT_GRANTED` / `UNCHECKED`.
- `MODE B`: `STRICTLY NOT AUTHORIZED`.

---

## 26. Blocker and Residual-Risk Register

### Active Blockers:
1. **`DB-CREDENTIAL-EXPOSURE-01` (CRITICAL):** Hardcoded plaintext `neondb_owner` connection URL in `frontend/lib/server/db.ts` committed to public GitHub history.
2. **`RLS-ROLE-ASSIGNMENT-01` (CRITICAL):** Mutable-GUC application role escalation on `user_roles`.
3. **`RLS-WRITE-AUTH-01` (HIGH):** Regional official-advisory write-authority bypass on `regional_signals`.
4. **`RES-PULSE-READ-01` (HIGH):** Role-global sub-threshold and suspended signal read privacy exposure.
5. **`WRK-DISP-01` (HIGH):** Unconfigured background worker production dispatch provider.
6. **`DB-RLS-01` (HIGH):** Live PostgreSQL RLS catalog verification pending.
7. **`OWNER-AUTH-01` (HIGH):** Governance decisions pending Project Owner authorization.
8. **`GATE01-PROV-01` (MEDIUM):** Neon staging branch live cloud API validation pending.

### Canonical Residual Risks:
- `RES-PULSE-01`: Role-global evidence access for experts/researchers without district scoping.
- `RES-PULSE-02`: READ COMMITTED snapshot/concurrency consistency window.
- `RES-PRIMARY-ROUTING-01`: Read/write primary-routing dependency.
- `RES-REPLICA-LAG-01`: Replica-lag exposure.
- `RES-FREE-TEXT-01`: PII exposure through author-controlled free text.

---

## 27. Required Live PostgreSQL Verification

1. Rotate `neondb_owner` password and confirm revocation via Neon Console.
2. Query `information_schema.table_privileges` to verify runtime role grants.
3. Validate `SET ROLE` denial under unprivileged roles.
4. Execute concurrent multi-session tests verifying `ON DELETE CASCADE` under `FORCE RLS`.
5. Verify live catalog RLS flags in `pg_class` and `pg_policies`.

---

## 28. Exact Source Files Inspected

- `frontend/lib/server/db.ts`
- `frontend/lib/server/auth.ts`
- `frontend/app/api/v1/auth/register/route.ts`
- `frontend/app/api/v1/auth/login/route.ts`
- `frontend/app/api/v1/farms/route.ts`
- `backend/app/core/config.py`
- `backend/app/database/session.py`
- `backend/app/database/rls.py`
- `backend/app/database/migrations/env.py`
- `backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py`
- `backend/app/database/migrations/versions/d2894a11c87d_stage12_collaborative_intelligence.py`
- `backend/app/models/user.py`
- `backend/app/models/farm.py`
- `backend/app/schemas/auth.py`
- `backend/app/security/dependencies.py`
- `backend/app/services/auth_service.py`
- `backend/app/services/expertconnect/expert_service.py`
- `backend/app/tasks/run_riskcast_batch.py`
- `backend/app/api/v1/endpoints/expertconnect.py`
- `backend/app/api/v1/endpoints/expert_reviews.py`
- `backend/app/api/v1/endpoints/knowledge.py`
- `backend/app/api/v1/endpoints/regional_pulse.py`

---

## 29. Commands and Offline Tests Actually Executed

1. `git rev-parse --show-toplevel; git branch --show-current; git rev-parse HEAD; git status --short; git diff --cached --stat; git diff --stat; git remote -v`
2. `git diff HEAD -- backend/app/database/rls.py backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py backend/app/database/migrations/versions/d2894a11c87d_stage12_collaborative_intelligence.py`
3. Custom Python secret scanner (`scan_all_repo_secrets.py`) with regex redaction across all workspace files and Git history.
4. Git commit history probe: `git log -S "neondb_owner" --oneline`.
5. Custom Python route scanner (`scan_all_routes.py`, `scan_manual_role_checks.py`) auditing all 212 FastAPI routes.

---

## 30. Exact Documentation Files Created or Updated

1. **Created (Primary Assurance Report):**
   - [`docs/pilot/security/PHASE_07_PUBLIC_CREDENTIAL_EXPOSURE_AND_ROLE_GATEWAY_ASSURANCE_REPORT.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_PUBLIC_CREDENTIAL_EXPOSURE_AND_ROLE_GATEWAY_ASSURANCE_REPORT.md)
   - [Artifact Mirror](file:///C:/Users/gokul/.gemini/antigravity/brain/8d770357-1b73-48ca-9930-eded206539c2/PHASE_07_PUBLIC_CREDENTIAL_EXPOSURE_AND_ROLE_GATEWAY_ASSURANCE_REPORT.md)
2. **Previously Created & Maintained in Working Tree:**
   - [`docs/pilot/security/PHASE_07_GLOBAL_RLS_IDENTITY_REMEDIATION_AND_ROLE_MANAGEMENT_CONTAINMENT_PLAN.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GLOBAL_RLS_IDENTITY_REMEDIATION_AND_ROLE_MANAGEMENT_CONTAINMENT_PLAN.md)
   - [`docs/pilot/security/PHASE_07_GLOBAL_GUC_AND_TENANT_POLICY_TRACEABILITY_MATRIX.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GLOBAL_GUC_AND_TENANT_POLICY_TRACEABILITY_MATRIX.md)
3. **Application, Test, or Migration Code Changes:** **`ZERO`** (0 lines modified).
