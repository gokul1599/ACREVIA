# ACREVIA — PHASE 07: PUBLIC CREDENTIAL INCIDENT, DATABASE PRINCIPAL RECONCILIATION & GOVERNANCE CONSISTENCY ASSURANCE REPORT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** **MODE A ONLY — Local Source Inspection, Public Repository Inspection, Security Engineering, Offline Verification & Governance Documentation**  
**Methodology:** Everything Claude Code (ECC) — `PLAN → TEST → IMPLEMENT ONLY IF DEFECT PROVEN → REVIEW → VERIFY → DOCUMENT`  
**Audit Baseline:** Git Commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Timestamp:** November 23, 2026  
**Overall Determination:** **`CREDENTIAL_INCIDENT_CONFIRMED_REQUIRES_OWNER_ACTION`** / **`TECHNICAL_PREFLIGHT_BLOCKED_WITH_RECORDED_BLOCKERS`**  
**Phase 07 Production Release Status:** **`NOT RELEASED`**  
**Mode B Live Execution Authorization:** **`STRICTLY NOT AUTHORIZED`**

---

## 1. Executive Determination

A rigorous adversarial security inspection, credential exposure incident evaluation, component principal reconciliation, and governance consistency audit was conducted across the ACREVIA codebase under strict **MODE A ONLY** discipline.

### 1.1 Formal Classification Summary
- **Overall Operational Status:** **`TECHNICAL_PREFLIGHT_BLOCKED_WITH_RECORDED_BLOCKERS`**
- **Public Credential Status:** **`CREDENTIAL_INCIDENT_CONFIRMED_REQUIRES_OWNER_ACTION`**
- **Credential Pattern Exposure:** **`PUBLIC_SECRET_EXPOSURE_CONFIRMED`** (`DB-CREDENTIAL-EXPOSURE-01`)
- **Credential Live Validity:** **`PUBLIC_SECRET_PATTERN_FOUND_LIVE_VALIDITY_UNKNOWN`** (strictly unverified under Mode A)
- **Phase 07 Release Gate Status:** **`GATES G-01 THROUGH G-05 REMAIN STRICTLY BLOCKED`**
- **Mode B Live Database Execution:** **`STRICTLY NOT AUTHORIZED`**

### 1.2 Core Critical Findings
1. **Critical Public Credential Exposure (`DB-CREDENTIAL-EXPOSURE-01`):** A plaintext database connection fallback containing the administrative role `neondb_owner` and a 16-character cleartext password targeting a live AWS `ap-southeast-1` Neon PostgreSQL cluster is committed to public `main` in `frontend/lib/server/db.ts` (lines 8–11). It was introduced in commit `63deadd41770adcfd976a453bb591c3367ed4379` (Nov 10, 2026), a direct ancestor of current public `main` (`c9e334d`).
2. **Database Principal Divergence:** FastAPI backend defaults to local SQLite (`settings.DATABASE_URL`), with its deployed production/staging identity unverified in source (`EFFECTIVE_RUNTIME_PRINCIPAL_UNKNOWN`). Next.js frontend directly evaluates `process.env.DATABASE_URL || "postgresql://neondb_owner:[REDACTED]..."`, connecting as the database owner if environment configuration is omitted.
3. **`ADMIN_BYPASS_SQL` Interaction:** The RLS bypass macro allowlists `SESSION_USER::text IN ('neondb_owner', 'acrevia_admin')`. Direct connections via the exposed credential satisfy `SESSION_USER`, permitting any SQL query setting `app.is_admin = 'true'` to bypass all application RLS policies.
4. **Decoupled Role Vulnerabilities:** 
   - `APP-ROLE-SELF-SELECT-01`: Public HTTP registration accepts `AGRICULTURAL_EXPERT` and `RESEARCHER` without verification or approval.
   - `RLS-ROLE-ASSIGNMENT-01`: Runtime role `acrevia_staging_app` possesses direct `INSERT/UPDATE` on `user_roles`. An SQL caller setting `app.current_user_id` can self-assign `ADMIN` under RLS `WITH CHECK`.
5. **Endpoint Authorization Audit (212 Routes Total, 10 Privileged):** Scanned all 212 FastAPI routes. Identified 10 privileged routes across expert triage, foliar dossier examination, clinical assessments, pesticide recommendations, knowledge curation, and regional pulse broadcasting. **Zero out of 10 routes verify accreditation or `ExpertProfile.verification_status`.**
6. **SECURITY DEFINER Gateway Challenge:** Capability A (`register_default_user_role`) is **NOT** proven safe under the existing RLS policy because `ADMIN_BYPASS_SQL` requires `SESSION_USER IN ('neondb_owner', 'acrevia_admin')`. When called by `acrevia_staging_app`, `SESSION_USER` is NOT allowlisted, causing `ADMIN_BYPASS_SQL` to evaluate to FALSE. Capability B (`assign_privileged_role`) is fundamentally unsafe if exposed to the shared application role.
7. **Foreign Key Cascade Vulnerability (`CASCADE-ROLE-DEL-01`):** `user_roles.user_id` references `users.id` with `ON DELETE CASCADE`. In PostgreSQL, foreign key cascades bypass RLS. `acrevia_staging_app` possesses `GRANT DELETE ON TABLE users`, enabling an attacker spoofing `app.current_user_id` to delete an administrator's user record and cascade-wipe their roles.
8. **Tenant Isolation Gap (`TENANT-MEMBERSHIP-01`):** Exactly 78 tenant tables reconciled (25 direct + 53 indirect). **Zero out of 78 tables verify user-to-farm membership in PostgreSQL RLS.** Both direct and indirect policies trust caller-supplied session GUCs completely.
9. **Governance Register Reconciliation:** Canonical decisions `D-01`, `D-02`, `D-03`, and `DB-AUTH-01` are restored to their original definitions. Newer invalidation/tombstoning and evidence-association topics are decoupled and classified as proposed decisions `PROP-DEC-05` and `PROP-DEC-06`. Canonical gates `GATE-01` through `GATE-05` are restored.

---

## 2. Mode A Scope and Mandatory Boundaries

Under strict **MODE A ONLY** discipline:
- **No Remote Database Connections:** Zero network sockets or TLS handshakes initiated to Neon, AWS, PostgreSQL staging, or production.
- **No Credential Testing:** Zero attempts to authenticate or verify the live validity of discovered passwords.
- **No SQL Execution:** Zero DDL, DML, or queries executed against live databases.
- **No Secrets Management / Cloud Console Access:** Zero interaction with Neon Console, Vercel dashboards, AWS IAM, or external secrets providers.
- **No Git History Rewrites or Branches:** Zero commits, pushes, force-pushes, branch creation, checkouts, resets, or stashes.
- **No Code Modifications:** Zero modifications to application source files, ORM models, test suites, or Alembic migrations.
- **Mandatory Redaction Protocol:** No cleartext passwords, complete connection strings, or secret-bearing tokens printed to terminal outputs, reports, logs, or persistent artifacts.

---

## 3. Repository Baseline and Working-Tree Integrity

### 3.1 Local Repository Baseline
| Parameter | Recorded State | Evidence Class |
| :--- | :--- | :--- |
| **Repository Root** | `C:/Users/gokul/OneDrive/Documents/projects` | `LOCAL_SOURCE_VERIFIED` |
| **Active Branch** | `main` | `LOCAL_GIT_VERIFIED` |
| **Local HEAD SHA** | `c9e334d14110e8a6e4c9b71b89cae3294288af0d` | `LOCAL_GIT_VERIFIED` |
| **Commit Timestamp** | `Mon Nov 16 12:19:44 2026 +0530` | `LOCAL_GIT_VERIFIED` |
| **Commit Author** | `Gokul Karpurapu <gokulkarpurapu@gmail.com>` | `LOCAL_GIT_VERIFIED` |
| **Commit Subject** | `docs(phase-07): record global actor-GUC trust, role-assignment, and regional pulse security assurance audits` | `LOCAL_GIT_VERIFIED` |
| **Configured Remote** | `origin -> https://github.com/gokul1599/ACREVIA.git` | `LOCAL_GIT_VERIFIED` |
| **Staged Changes** | `0 files` | `LOCAL_GIT_VERIFIED` |

### 3.2 Working-Tree Status (`git status --short`)
- **Tracked Modified Files (7 files — Documentation Addenda Only):**
  - `M docs/pilot/security/PHASE_07_FINAL_TECHNICAL_PREFLIGHT_STATUS.md`
  - `M docs/pilot/security/PHASE_07_GLOBAL_ACTOR_GUC_TRUST_AND_ROLE_ASSIGNMENT_SECURITY_AUDIT.md`
  - `M docs/pilot/security/PHASE_07_PROJECT_OWNER_DECISION_AND_MODE_B_AUTHORIZATION_BRIEFING.md`
  - `M docs/pilot/security/PHASE_07_READ_PRIVACY_AND_EVIDENCE_ASSOCIATION_SECURITY_COMPLETENESS_AUDIT.md`
  - `M docs/pilot/security/PHASE_07_TRUSTED_WRITER_ARCHITECTURE_DECISION_RECORD.md`
  - `M docs/pilot/security/phase_07_database_actor_identity_architecture_decision_analysis.md`
  - `M docs/pilot/security/phase_07_owner_decision_evidence_traceability_matrix.md`
- **Untracked Documentation Files (3 files — New Governance Dossiers):**
  - `?? docs/pilot/security/PHASE_07_GLOBAL_GUC_AND_TENANT_POLICY_TRACEABILITY_MATRIX.md`
  - `?? docs/pilot/security/PHASE_07_GLOBAL_RLS_IDENTITY_REMEDIATION_AND_ROLE_MANAGEMENT_CONTAINMENT_PLAN.md`
  - `?? docs/pilot/security/PHASE_07_PUBLIC_CREDENTIAL_EXPOSURE_AND_ROLE_GATEWAY_ASSURANCE_REPORT.md`
- **Application Source Code Modifications:** Exactly **0 files**.
- **ORM Models / Migration Modifications:** Exactly **0 files**.

---

## 4. Public GitHub Baseline Verification

Independent inspection confirms:
- **Local HEAD vs Public `main`:** `git rev-parse HEAD origin/main` confirms both point identically to `c9e334d14110e8a6e4c9b71b89cae3294288af0d`.
- **Public Tree State:** Public commit `c9e334d` on GitHub does NOT contain the three newly created dossiers or the local addenda. They exist solely on the local filesystem as uncommitted modifications and untracked files in `docs/pilot/security/`.
- **Integrity Assertion:** No code drift exists between local `main` and public `origin/main`.

---

## 5. Public Database Owner Credential Incident (`DB-CREDENTIAL-EXPOSURE-01`)

### 5.1 Exposure Specification
- **Vulnerability Identifier:** `DB-CREDENTIAL-EXPOSURE-01`
- **Exposed Entity:** Hardcoded database connection URL fallback
- **File Location:** `frontend/lib/server/db.ts`, lines 8–11
- **Exact Code Structure:**
  ```typescript
  const dbUrl =
    process.env.DATABASE_URL ||
    "postgresql://neondb_owner:[REDACTED_PASSWORD]@ep-muddy-mode-a1nd6rrb-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require";
  ```
- **Connection Components:**
  - **Scheme:** `postgresql`
  - **Username / Role:** `neondb_owner`
  - **Password:** Present (16 characters, alphanumeric, strictly redacted)
  - **Host / Endpoint:** `ep-muddy-mode-a1nd6rrb-pooler.ap-southeast-1.aws.neon.tech` (Neon PgBouncer connection pooler in AWS Singapore `ap-southeast-1`)
  - **Database Name:** `/neondb`
  - **Parameters:** `sslmode=require`
- **Exposure Classification:** `PUBLIC_SECRET_EXPOSURE_CONFIRMED`
- **Live Validity Classification:** `PUBLIC_SECRET_PATTERN_FOUND_LIVE_VALIDITY_UNKNOWN`
- **Required Action:** `REQUIRES_PROVIDER_OWNER_ACTION`

---

## 6. Redacted Credential-Scan Inventory Across Codebase

A comprehensive scan of all configuration, templates, docker, CI, and test files was conducted with automated password redaction:

| File Path | Line Range | Exposure Type | Public Status | First Known Commit | Latest Exposed Commit | Credential Identity | Live Validity | Required Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `frontend/lib/server/db.ts` | 8–11 | Hardcoded PostgreSQL connection fallback | Current public tree & history | `63deadd41770` | `c9e334d14110` | `neondb_owner` | Unknown | Immediate Owner Rotation |
| `.env` (gitignored) | 13 | Local developer environment configuration | Disk only (Never tracked in Git) | N/A (Untracked) | N/A (Untracked) | `neondb_owner` | Matches db.ts password | Local file rotation |
| `backend/tests/test_target_validation.py` | 82, 150 | Unit test validation fixture URLs | Current public tree & history | `63deadd41770` | `c9e334d14110` | Synthetic test credentials | Dummy values (lengths 10 & 4, non-matching) | No rotation needed (Synthetic) |
| `aheadguard-mvp-starter/lib/db.ts` | 80–86 | Neon serverless connection helper | Current public tree & history | Initial commit | `c9e334d14110` | None (Fails closed on missing env) | N/A | None (Safe implementation) |
| `aheadguard-mvp-starter/.env.example` | 14, 21 | Environment configuration template | Current public tree & history | Initial commit | `c9e334d14110` | Template placeholders (`[user]`) | N/A | None (Template documentation) |
| `.env.example` | 20 | Root environment template | Current public tree & history | Initial commit | `c9e334d14110` | Template placeholders (`<user>`) | N/A | None (Template documentation) |
| `docker-compose.yml` | 41 | Container compose environment string | Current public tree & history | Initial commit | `c9e334d14110` | Parameter expansion (`${POSTGRES_USER:...}`) | N/A | None (Standard Docker config) |

---

## 7. Git-History Exposure Analysis

### 7.1 Introducing Commit Verification
- **Full Commit SHA:** `63deadd41770adcfd976a453bb591c3367ed4379`
- **Commit Author:** `Gokul Karpurapu <gokulkarpurapu@gmail.com>`
- **Commit Date:** `Tue Nov 10 10:16:15 2026 +0530`
- **Commit Subject:** `fix(auth): implement resilient serverless authentication, farmer registration and onboarding routes on neon postgresql and deploy to vercel`
- **File Introduced:** `frontend/lib/server/db.ts`
- **Ancestry Verification:** Verified via `git merge-base 63deadd41770... HEAD` -> returns `63deadd41770...` (`Is ancestor: True`).
- **Subsequent Modifications:** `git log --follow frontend/lib/server/db.ts` confirms exactly **1 commit** has ever touched this file. The credential has persisted unchanged across all intermediate commits up to HEAD `c9e334d`.
- **String History Search:** `git log -S [PASSWORD]` confirms `63deadd` is the single introducing commit in the entire repository history. The secret was never copied to other tracked paths.
- **Git Tags / Branch Status:** Zero tags exist in the repository (`git tag --list` returns empty). Active branch is `main`.

---

## 8. Owner-Controlled Incident-Response Checklist

The Project Owner must execute the following manual containment checklist through authenticated provider dashboards. No agent or CLI tool may perform these actions:

```
[ ] Step 1: Provider-Side Password Rotation (Neon Console)
    - Log into Neon Cloud Console (https://console.neon.tech).
    - Navigate to Project -> Database Roles -> 'neondb_owner'.
    - Reset/rotate password immediately, invalidating the exposed credential.
    - Note: If connection pooling is enabled, reset pooler endpoints.

[ ] Step 2: Role Privileges & Catalog Audit
    - Inspect privileges of 'neondb_owner'.
    - Confirm whether 'neondb_owner' possesses CREATEROLE, CREATEDB, or table ownership.
    - Provision restricted application role 'acrevia_staging_app' with least-privilege grants.

[ ] Step 3: Provider Connection History & Access Review
    - Review Neon connection logs and audit trails covering Nov 10, 2026 to present.
    - Audit for unauthorized IP addresses, unexpected query spikes, or table exports.

[ ] Step 4: Local Source Remediation (frontend/lib/server/db.ts)
    - Remove the hardcoded fallback URI string from frontend/lib/server/db.ts.
    - Implement fail-closed validation:
      const dbUrl = process.env.DATABASE_URL;
      if (!dbUrl) throw new Error("DATABASE_URL is not configured.");

[ ] Step 5: Secure Environment Variable Configuration
    - Update Vercel / serverless deployment environment variables with the newly rotated connection string.
    - Ensure DATABASE_URL references the restricted runtime principal, NOT 'neondb_owner'.

[ ] Step 6: Git History Sanitization Planning
    - Do NOT immediately force-push or rewrite history without team coordination.
    - Plan history sanitization using 'git-filter-repo' or BFG Repo-Cleaner after rotation is confirmed.
    - Notify all contributors to pull a fresh clone following history rewrite.

[ ] Step 7: Push-Protection & Secret Scanning
    - Enable GitHub Secret Scanning and Push Protection on repository 'gokul1599/ACREVIA'.
```

---

## 9. Database Principal Boundaries & Reconciliation Matrix

| Process / Component | Connection Helper | Configuration Source | Source Default | Source-Inferred Identity | Effective Deployment Identity | RLS Enforcement Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FastAPI Backend** | `engine` / `SessionLocal` (`session.py`) | `backend.app.core.config.settings.DATABASE_URL` | `sqlite:///./acrevia_dev.db` (`SOURCE_DEFAULT_IDENTIFIED`) | `acrevia_staging_app` (Inferred from RLS grants) | `EFFECTIVE_RUNTIME_PRINCIPAL_UNKNOWN` (`OWNER_CONFIGURATION_REQUIRED`) | Enforced if connecting as unprivileged app role |
| **Next.js Registration** | `getDb()` (`frontend/lib/server/db.ts`) | `process.env.DATABASE_URL` | Fallback Neon URI (`FALLBACK_CONNECTION_PRESENT`) | `neondb_owner` | `EFFECTIVE_RUNTIME_PRINCIPAL_UNKNOWN` (`FALLBACK_CONNECTION_PRESENT`) | **BYPASSES RLS** if fallback active |
| **Next.js Login** | `getDb()` (`frontend/lib/server/db.ts`) | `process.env.DATABASE_URL` | Fallback Neon URI (`FALLBACK_CONNECTION_PRESENT`) | `neondb_owner` | `EFFECTIVE_RUNTIME_PRINCIPAL_UNKNOWN` (`FALLBACK_CONNECTION_PRESENT`) | **BYPASSES RLS** if fallback active |
| **Next.js Direct Routes** (`farms`, `plots`, `seasons`) | `getDb()` (`frontend/lib/server/db.ts`) | `process.env.DATABASE_URL` | Fallback Neon URI (`FALLBACK_CONNECTION_PRESENT`) | `neondb_owner` | `EFFECTIVE_RUNTIME_PRINCIPAL_UNKNOWN` (`FALLBACK_CONNECTION_PRESENT`) | **BYPASSES RLS** if fallback active |
| **RiskCast Batch Worker** | `SessionLocal` (`run_riskcast_batch.py`) | Backend `settings.DATABASE_URL` | Inherits backend default (`SOURCE_DEFAULT_IDENTIFIED`) | `acrevia_staging_app` / `system:worker:riskcast` | `EFFECTIVE_RUNTIME_PRINCIPAL_UNKNOWN` (`WRK-DISP-01` blocks dispatch) | Blocked by `ProductionDispatchBlockedError` |
| **Alembic Migrations** | `context.configure` (`env.py`) | Backend `settings.DATABASE_URL` | Inherits backend default (`SOURCE_DEFAULT_IDENTIFIED`) | Table Owner / DDL Admin Required | `EFFECTIVE_RUNTIME_PRINCIPAL_UNKNOWN` (`OWNER_CONFIGURATION_REQUIRED`) | N/A (DDL migration execution) |

---

## 10. `ADMIN_BYPASS_SQL` Identity & Privilege Analysis

### 10.1 Macro Definition
In `backend/app/database/rls.py`, lines 22–27:
```sql
ADMIN_ROLES = ("neondb_owner", "acrevia_admin")
ADMIN_BYPASS_SQL = (
    "(SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') "
    "AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') "
    "AND current_setting('app.is_admin', true) = 'true')"
)
```

### 10.2 Conditional Impact Under Frontend Fallback
If the Next.js frontend connects using the fallback credential:
1. `SESSION_USER` evaluates to `'neondb_owner'` (matches allowlist).
2. `CURRENT_USER` evaluates to `'neondb_owner'` (matches allowlist).
3. Any SQL query in that session executing `SELECT set_config('app.is_admin', 'true', false)` satisfies `current_setting('app.is_admin', true) = 'true'`.
4. All three clauses evaluate to **TRUE**, completely satisfying `ADMIN_BYPASS_SQL`.
5. Every RLS policy containing `OR ({ADMIN_BYPASS_SQL})` treats the frontend session as a global database administrator.

### 10.3 PostgreSQL Identity & Attribute Disambiguation
- **`rolsuper` (SUPERUSER):** In cloud-managed Neon PostgreSQL, user roles (including `neondb_owner`) are NOT PostgreSQL superusers (`rolsuper = false`). Superuser attributes cannot be inferred from role names.
- **`rolbypassrls` (BYPASSRLS):** Whether `neondb_owner` possesses `BYPASSRLS` in Neon's live system catalogs (`pg_roles`) is unknown without live inspection (`REQUIRES_LIVE_POSTGRESQL_VALIDATION`).
- **Table Ownership & `FORCE ROW LEVEL SECURITY`:** PostgreSQL native rules allow table owners to bypass RLS unless `FORCE ROW LEVEL SECURITY` is set. In ACREVIA, `rls.py` generates `ALTER TABLE ... FORCE ROW LEVEL SECURITY` for direct, indirect, and user-owned tables. However, because `neondb_owner` is explicitly included in `ADMIN_BYPASS_SQL`, RLS policies evaluate to TRUE regardless!

---

## 11. Decoupled Role-Assignment Analysis

### 11.1 Threat Model 1: Public HTTP Registration Role Self-Selection (`APP-ROLE-SELF-SELECT-01`)
- **Vulnerability:** Public registration endpoints permit users to self-select privileged roles.
- **Backend Schema:** `UserRegisterRequest` (`backend/app/schemas/auth.py:16`):
  ```python
  role: str = Field(default="FARMER", pattern="^(FARMER|AGRICULTURAL_EXPERT|RESEARCHER)$")
  ```
- **Backend Service:** `AuthService.register_user` (`auth_service.py:44–48`):
  ```python
  role_record = db.get(Role, req.role)
  if not role_record:
      role_record = Role(id=req.role, description=f"{req.role} system role")
      db.add(role_record)
  user.roles.append(role_record)
  ```
- **Frontend Route:** `frontend/app/api/v1/auth/register/route.ts` (lines 58–63, 137–141):
  ```typescript
  const cleanRole = ["FARMER", "AGRICULTURAL_EXPERT", "RESEARCHER"].includes(role) ? role : "FARMER";
  ...
  await sql`INSERT INTO user_roles (user_id, role_id) VALUES (${userId}, ${cleanRole})`;
  ```
- **Finding:** Any anonymous internet actor can register as `AGRICULTURAL_EXPERT` or `RESEARCHER`. The role is inserted directly into `user_roles` without administrative approval.

### 11.2 Threat Model 2: SQL-Level Arbitrary Privilege Escalation (`RLS-ROLE-ASSIGNMENT-01`)
- **Vulnerability:** Mutable-GUC privilege escalation under shared database principal `acrevia_staging_app`.
- **Precondition:** Arbitrary SQL execution (e.g. SQL injection or shared connection hijacking) under `acrevia_staging_app`.
- **Privilege Grants:** In `rls.py`, `user_roles` is categorized as `TableCategory.USER_OWNED`. Under `PRIVILEGE_CROSSWALK` (lines 997–1001), `acrevia_staging_app` receives:
  ```sql
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE user_roles TO acrevia_staging_app;
  ```
- **RLS Policy on `user_roles` (lines 386–389):**
  ```sql
  WITH CHECK (
      {ADMIN_BYPASS_SQL}
      OR user_id::text = current_setting('app.current_user_id', true)
  )
  ```
- **Escalation Mechanism:**
  1. Attacker executes: `SET LOCAL app.current_user_id = '<target_uuid>';`
  2. Attacker executes: `INSERT INTO user_roles (user_id, role) VALUES ('<target_uuid>', 'ADMIN');`
  3. PostgreSQL evaluates `WITH CHECK`: `user_id::text = current_setting('app.current_user_id', true)` evaluates to TRUE!
  4. On the user's next API request, `get_current_user` loads `user.roles`, sees `ADMIN`, and sets `app.is_admin = 'true'`, elevating them to global application administrator.

---

## 12. Registration & Login Token Lifecycle Sequence

The precise authentication token issuance sequence is reconstructed as follows:
```
1. Public HTTP Client -> POST /api/v1/auth/register {"phone": "...", "role": "AGRICULTURAL_EXPERT"}
   │
   ▼
2. Backend (or Frontend) validates schema, creates User record with is_active=true, is_verified=false.
   │
   ▼
3. Inserts requested role directly into user_roles.
   │
   ▼
4. Endpoint returns HTTP 201 Created with UserResponse body.
   [CRITICAL: ZERO JWT TOKENS RETURNED AT REGISTRATION]
   │
   ▼
5. Public HTTP Client -> POST /api/v1/auth/login {"phone": "...", "password": "..."}
   │
   ▼
6. Backend (or Frontend) checks password hash and user.is_active.
   [CRITICAL: DOES NOT CHECK user.is_verified]
   │
   ▼
7. Loads user.roles from database, signs JWT carrying role claims.
   │
   ▼
8. Returns HTTP 200 OK with TokenResponse {access_token: "eyJ...", token_type: "bearer"}.
   │
   ▼
9. Client invokes privileged endpoint with Authorization: Bearer <token>.
```

---

## 13. Expert & Researcher Endpoint Authorization Inventory

An exhaustive static audit of all 212 API endpoints across 22 router files in `backend/app/api/v1/endpoints/` was conducted:
- **Total Backend Endpoints:** Exactly **212 routes**.
- **Privileged Expert / Researcher Endpoints:** Exactly **10 routes** across 4 modules.

### 13.1 Privileged Route Inventory Table
| Route Method & Path | Router Module | Handler Function | Role Dependency | Accreditation / Verification Check | Farm / Tenant Check | Response Sensitivity / Capability | Evidence Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET /api/v1/expertconnect/cases` | `expertconnect.py:172` | `list_expert_cases` | `AGRICULTURAL_EXPERT`, `ADMIN` | **NONE** (Zero check on `verification_status`) | Global queue | Triage queue of farmer consultations across Telangana | `PRIVILEGED_ROUTE_ROLE_ONLY` |
| `POST /api/v1/expertconnect/cases/{id}/claim` | `expertconnect.py:193` | `claim_case` | `AGRICULTURAL_EXPERT`, `ADMIN` | **NONE** (Zero check on `verification_status`) | Case-specific | Claims consultation case; establishes agronomist assignment | `PRIVILEGED_ROUTE_ROLE_ONLY` |
| `GET /api/v1/expertconnect/cases/{id}` | `expertconnect.py:220` | `get_case_dossier` | `get_current_user` (Any auth user) | **NONE** | Case-specific | **Full Clinical Evidence Dossier:** foliar images, AI vision, location | `DOWNSTREAM_IMPACT_CONFIRMED` |
| `POST /api/v1/expertconnect/cases/{id}/assess` | `expertconnect.py:232` | `submit_expert_assessment` | `AGRICULTURAL_EXPERT`, `ADMIN` | **NONE** (Zero check on `verification_status`) | Case-specific | **Certified Clinical Prescription:** IPM strategy, CIBRC pesticide advisories | `DOWNSTREAM_IMPACT_CONFIRMED` |
| `PUT /api/v1/expertconnect/cases/{id}/assess` | `expertconnect.py:274` | `revise_expert_assessment` | `AGRICULTURAL_EXPERT`, `ADMIN` | **NONE** (Zero check on `verification_status`) | Case-specific | Revises clinical prescription and differential diagnoses | `DOWNSTREAM_IMPACT_CONFIRMED` |
| `POST /api/v1/diagnoses/{id}/expert-review` | `expert_reviews.py:18` | `submit_expert_review` | `AGRICULTURAL_EXPERT` | **NONE** (Zero check on `verification_status`) | Diagnosis-specific | **Certified Clinical Override:** Overrides AI disease diagnosis | `DOWNSTREAM_IMPACT_CONFIRMED` |
| `POST /api/v1/knowledge/sources` | `knowledge.py:86` | `register_knowledge_source` | `ADMIN`, `AGRICULTURAL_EXPERT` | **NONE** | Platform-wide | Registers authoritative knowledge source for KrishiBrain RAG | `DOWNSTREAM_IMPACT_CONFIRMED` |
| `POST /api/v1/knowledge/ingest` | `knowledge.py:132` | `ingest_document` | `ADMIN`, `AGRICULTURAL_EXPERT` | **NONE** | Platform-wide | Triggers document ingestion into shared vector database | `DOWNSTREAM_IMPACT_CONFIRMED` |
| `POST /api/v1/regional-pulse/signals` | `regional_pulse.py:27` | `aggregate_signal` | `ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER` | **NONE** | District-wide | **Broadcasts regional agricultural signals** to farmers | `DOWNSTREAM_IMPACT_CONFIRMED` |
| `POST /api/v1/regional-pulse/signals/{id}/recover` | `regional_pulse.py:152` | `recover_signal` | `ADMIN`, `AGRICULTURAL_EXPERT` | **NONE** | District-wide | Recovers/reactivates invalidated regional signals | `DOWNSTREAM_IMPACT_CONFIRMED` |

### 13.2 Core Authorization Defect
- `get_current_user` checks **only** `user.is_active` (does NOT check `user.is_verified`).
- `require_roles` checks **only** `role in user.roles` (does NOT check `ExpertProfile.verification_status`).
- `ExpertProfile` verification workflow exists in `expertconnect.py` (`POST /admin/verify/{profile_id}`), but **no operational endpoints check profile status**.
- For `RESEARCHER`, there is **zero profile model and zero verification workflow** in the codebase.
- **Result:** Any self-selected expert or researcher obtains immediate operational access to clinical dossiers, pesticide prescriptions, knowledge curation, and regional broadcasting!

---

## 14. SECURITY DEFINER Gateway Technical Challenge

The prior report claimed Capability A was "PROVEN SAFE". Under rigorous PostgreSQL function-identity analysis, this claim is **REFUTED**:

### 14.1 Function-Identity Analysis (`SESSION_USER` vs `CURRENT_USER`)
- When `acrevia_staging_app` calls a `SECURITY DEFINER` function owned by `acrevia_admin`:
  - `CURRENT_USER` switches to `acrevia_admin`.
  - `SESSION_USER` **REMAINS** `acrevia_staging_app`.
- The restrictive RLS policy macro `ADMIN_BYPASS_SQL` requires:
  ```sql
  SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') 
  AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
  AND current_setting('app.is_admin', true) = 'true'
  ```
- Because `SESSION_USER` is `'acrevia_staging_app'`, `ADMIN_BYPASS_SQL` **FAILS**!
- Furthermore, `user_roles` has `FORCE ROW LEVEL SECURITY`, binding `acrevia_admin` to RLS.
- Inside the function, `INSERT INTO user_roles` evaluates `WITH CHECK`:
  ```sql
  WITH CHECK ({ADMIN_BYPASS_SQL} OR user_id::text = current_setting('app.current_user_id', true))
  ```
- If `app.current_user_id` has not been set to `p_user_id`, the insert is **BLOCKED BY POSTGRESQL RLS**!
- **Conclusion:** Capability A cannot function simply by being `SECURITY DEFINER`. It requires either an explicit RLS policy exception for the function or setting `app.current_user_id = p_user_id` within the function.

### 14.2 Capability B Privilege Analysis
Exposing `assign_privileged_role(p_user_id, p_role)` to `acrevia_staging_app` is fundamentally unsafe. Because `acrevia_staging_app` is a shared database login pool, any SQL injection or attacker setting `app.is_admin = 'true'` can forge arguments to assign `ADMIN`. Privileged role management **MUST** be executed over a physically isolated administrative database principal (`acrevia_admin`) under **Option D**.

---

## 15. User Deletion & Foreign Key Cascade Vulnerability (`CASCADE-ROLE-DEL-01`)

### 15.1 Architectural Vulnerability
- In `backend/app/models/user.py:45`:
  ```python
  user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
  ```
- In PostgreSQL, foreign key cascade actions (`ON DELETE CASCADE`) are executed by internal system triggers that **BYPASS ROW LEVEL SECURITY ON CHILD TABLES**.
- `acrevia_staging_app` possesses `GRANT DELETE ON TABLE users`.
- `users` RLS policy evaluates:
  ```sql
  USING ({ADMIN_BYPASS_SQL} OR id::text = current_setting('app.current_user_id', true))
  ```
- **Exploitation:** An attacker executing SQL under `acrevia_staging_app` issues:
  ```sql
  SET LOCAL app.current_user_id = '<admin_uuid>';
  DELETE FROM users WHERE id = '<admin_uuid>';
  ```
  PostgreSQL deletes the admin's `users` record and automatically cascades, deleting all of the administrator's role assignments from `user_roles`.
- **Remediation:**
  1. Revoke `DELETE ON TABLE users FROM acrevia_staging_app`.
  2. Transition account termination to an auditable soft-delete lifecycle (`is_active = FALSE`).

---

## 16. Complete 13-Table User-Owned Matrix

All 13 `USER_OWNED` tables are protected by `user_isolation_policy` evaluating `column_name::text = current_setting('app.current_user_id', true)`:

| Table Name | User Column | Policy Name | Permissive Grants | Disallowed DML |
| :--- | :--- | :--- | :--- | :--- |
| `users` | `id` | `users_user_isolation_policy` | SELECT, INSERT, UPDATE, DELETE | TRUNCATE, REFERENCES, TRIGGER |
| `session_tokens` | `user_id` | `session_tokens_user_isolation_policy` | SELECT, INSERT, UPDATE, DELETE | TRUNCATE, REFERENCES, TRIGGER |
| `user_roles` | `user_id` | `user_roles_user_isolation_policy` | SELECT, INSERT, UPDATE, DELETE | TRUNCATE, REFERENCES, TRIGGER |
| `consent_records` | `user_id` | `consent_records_user_isolation_policy` | SELECT, INSERT, UPDATE, DELETE | TRUNCATE, REFERENCES, TRIGGER |
| `api_applications` | `owner_id` | `api_applications_user_isolation_policy` | SELECT, INSERT, UPDATE, DELETE | TRUNCATE, REFERENCES, TRIGGER |
| `webhook_endpoints` | `user_id` | `webhook_endpoints_user_isolation_policy` | SELECT, INSERT, UPDATE, DELETE | TRUNCATE, REFERENCES, TRIGGER |
| `data_mapping_profiles` | `created_by_user_id` | `data_mapping_profiles_user_isolation_policy` | SELECT, INSERT, UPDATE, DELETE | TRUNCATE, REFERENCES, TRIGGER |
| `expert_profiles` | `user_id` | `expert_profiles_user_isolation_policy` | SELECT, INSERT, UPDATE, DELETE | TRUNCATE, REFERENCES, TRIGGER |
| `community_memberships` | `user_id` | `community_memberships_user_isolation_policy` | SELECT, INSERT, UPDATE, DELETE | TRUNCATE, REFERENCES, TRIGGER |
| `organization_memberships` | `user_id` | `organization_memberships_user_isolation_policy` | SELECT, INSERT, UPDATE, DELETE | TRUNCATE, REFERENCES, TRIGGER |
| `event_registrations` | `user_id` | `event_registrations_user_isolation_policy` | SELECT, INSERT, UPDATE, DELETE | TRUNCATE, REFERENCES, TRIGGER |
| `knowledge_feedback` | `user_id` | `knowledge_feedback_user_isolation_policy` | SELECT, INSERT, UPDATE, DELETE | TRUNCATE, REFERENCES, TRIGGER |
| `learning_feedback` | `user_id` | `learning_feedback_user_isolation_policy` | SELECT, INSERT, UPDATE, DELETE | TRUNCATE, REFERENCES, TRIGGER |

---

## 17. Complete 78-Table Tenant Reconciliation & Membership Gap

### 17.1 Table Breakdown
- Exactly **78 tenant-isolated tables**:
  - **25 `TENANT_DIRECT` tables** (direct `farm_id` or `id` tenant key).
  - **53 `TENANT_INDIRECT` tables** (joining through plot, season, farm, or observation).
- Discrepancy Note: Comments in `rls.py:41` claim 24 direct tables (actual 25) and `rls.py:83` claim 51 indirect tables (actual 53).

### 17.2 Farm Ownership Metadata vs Policy
In `farms`:
- `column = "id"`
- `owner_column = "owner_id"`
- Generated Policy: `USING ({ADMIN_BYPASS_SQL} OR id::text = current_setting('app.current_tenant_id', true))`
- **Finding:** `owner_column` is descriptive metadata only; it is NOT checked in PostgreSQL RLS.

### 17.3 Tenant Membership Gap (`TENANT-MEMBERSHIP-01`)
- **0 out of 78 tenant tables verify user-to-farm membership in PostgreSQL RLS.**
- Both direct and indirect policies trust caller-supplied session GUCs (`app.current_tenant_id`) completely. If an attacker under `acrevia_staging_app` sets `app.current_tenant_id = '<target_farm_id>'`, RLS permits full access regardless of membership.

---

## 18. Migration Graph & Forward-Only Design

### 18.1 Linear Migration Graph
Inspection of `backend/app/database/migrations/versions/` confirms a strictly linear migration chain with **zero branches and zero multiple heads**:
```
None -> f043516098f8 (initial schema)
         │
         ▼
       e738192a54b1 (stage 9)
         │
         ▼
       b894a11c87d2 (stage 10)
         │
         ▼
       c1894a11c87d (stage 11)
         │
         ▼
       d2894a11c87d (stage 12)
         │
         ▼
       e3894a11c87d (stage 13)
         │
         ▼
       f4894a11c87d (stage 14)
         │
         ▼
       a1089411c87d (enable RLS tenant isolation) [CURRENT HEAD]
```

### 18.2 Forward-Only Remediation Requirement
Migration `a1089411c87d` is the current head and may already be applied in existing deployments. Any remediation DDL (revoking `user_roles` grants, adding membership checks, soft-delete constraints) **MUST** be authored as a forward migration (e.g. `a1089411c87e` with `down_revision = 'a1089411c87d'`).

---

## 19. Remediation Architecture Comparison

| Dimension | Option A: Uncontained Runtime | Option B: SECURITY DEFINER Gateway Only | Option C: Hardcoded Direct Bypasses | Option D: Dual-Principal + Fail-Closed Runtime (Recommended) |
| :--- | :--- | :--- | :--- | :--- |
| **Registration Role Control** | Permissive self-selection (`FARMER`, `EXPERT`, `RESEARCHER`) | `FARMER`-only hardcoded capability | Permissive self-selection | Hardcoded `FARMER` registration + administrative approval workflow |
| **SQL Privilege Escalation** | Vulnerable (`WITH CHECK` allows self-escalation) | Unresolved `SESSION_USER` barrier in `ADMIN_BYPASS_SQL` | Permissive | **Eliminated:** Revoke DML on `user_roles` from runtime role |
| **Privileged Role Assignment** | Unrestricted DML under shared app login | Unsafe if exposed to shared app login | Dangerous | **Isolated:** Dedicated `acrevia_admin` principal only |
| **Endpoint Accreditation** | Missing (0/10 routes check accreditation) | Missing | Missing | Mandatory `verification_status == 'APPROVED'` dependency |
| **Account Deletion Cascades** | Vulnerable (`ON DELETE CASCADE` wipes roles) | Vulnerable | Vulnerable | **Eliminated:** Revoke `DELETE ON users`; soft-delete only |
| **Tenant Membership Boundary** | Trust caller GUCs completely | Trust caller GUCs completely | Trust caller GUCs completely | Enforce `farm_memberships` verification in PostgreSQL RLS |

---

## 20. Adversarial Test Specification (Offline Design Only)

The following test suite must be authored and executed under Mode B when authorized:
1. **Credential Exposure:**
   - Verify `frontend/lib/server/db.ts` throws error when `DATABASE_URL` is omitted.
   - Verify zero fallback URIs exist in current source.
2. **Registration Role Containment:**
   - Attempt registration with `role: "AGRICULTURAL_EXPERT"` -> must reject or assign `FARMER`.
   - Attempt registration with `role: "ADMIN"` -> must return HTTP 422.
3. **Endpoint Accreditation Gate:**
   - Register expert user -> attempt `POST /api/v1/expertconnect/cases/{id}/claim` before admin approval -> must return HTTP 403 Forbidden.
   - Set `verification_status = 'APPROVED'` -> attempt claim -> must succeed.
4. **SQL-Level Escalation Containment:**
   - Connect as `acrevia_staging_app` -> execute `SET LOCAL app.current_user_id = '<uuid>'; INSERT INTO user_roles ...` -> must raise `permission denied for table user_roles`.
5. **Cascading Deletion Containment:**
   - Connect as `acrevia_staging_app` -> execute `DELETE FROM users WHERE id = '<admin_uuid>'` -> must raise `permission denied for table users`.
6. **Tenant Membership RLS:**
   - Set `app.current_tenant_id = '<farm_id>'` for non-member user -> execute `SELECT * FROM farms WHERE id = '<farm_id>'` -> must return 0 rows.

---

## 21. Governance, Decision Drift & Blocker Register Reconciliation

### 21.1 Canonical Decision Register Preservation
The canonical decision register is strictly preserved. All checkboxes remain unselected `[ ]`:

- **`D-01` — Regional Signal Visibility and Official-Advisory Data Model:**
  - `[ ]` Option D-01-A: Universal three-distinct-farm aggregation threshold.
  - `[ ]` Option D-01-B: Dedicated `official_advisories` table (Recommended).
  - `[ ]` Option D-01-C: Conditional RLS exception for official state with zero observations.
  - `[ ]` Option D-01-D: Privileged-only visibility during Pilot.
- **`D-02` — Source Authenticity and Pilot Terminology (Canonical Definition Restored):**
  - `[ ]` Option D-02-A: Retain `OFFICIAL_ADVISORY` with explicit disclosure: `Platform Administrator Broadcast — Not Verified Government Gazette`.
  - `[ ]` Option D-02-B: Rename enum to `ADMINISTRATIVE_NOTICE`.
  - `[ ]` Option D-02-C: Make external government API integration a release gate.
- **`D-03` — Independent Expert Review (Canonical Definition Restored):**
  - `[ ]` Option D-03-A: Single expert validation.
  - `[ ]` Option D-03-B: Two independent expert verifications.
  - `[ ]` Option D-03-C: Defer to Phase 08 and remain Admin-only until implemented.
- **`DB-AUTH-01` — Trusted Database Writer Identity Architecture:**
  - `[ ]` Option DB-AUTH-01-A: Dual-principal ordinary runtime and trusted writer.
  - `[ ]` Option DB-AUTH-01-B: Restricted SECURITY DEFINER promotion capability.
  - `[ ]` Option DB-AUTH-01-C: Direct Neon superuser / BYPASSRLS access (**REJECTED**).
  - `[ ]` Option DB-AUTH-01-D: Dedicated trusted administrative database principal (`acrevia_admin`) (Recommended).

### 21.2 Proposed Distinct Decision Topics (Decoupled from D-02 / D-03)
- **`PROP-DEC-05` — Official-Advisory Invalidation / Tombstoning Lifecycle:**
  - `[ ]` Option 5-A: Soft-tombstoning via `is_active = FALSE`.
  - `[ ]` Option 5-B: Hard-tombstoning via state transition to `INVALIDATED`.
  - `[ ]` Option 5-C: Append-only supersession chain.
- **`PROP-DEC-06` — Evidence-Association & Farm Anonymization Lifecycle:**
  - `[ ]` Option 6-A: Decoupled regional evidence association table.
  - `[ ]` Option 6-B: In-memory signal aggregation with zero row linkage.

### 21.3 Canonical Gate Definitions Restored
The unauthorized re-interpretation of gates is revoked. Canonical definitions remain:
- **`GATE-01` (Staging-Branch Provisioning):** `BLOCKED` (Live validation pending).
- **`GATE-02` (Live Application-Role Grants):** `NOT_GRANTED` / `BLOCKED`.
- **`GATE-03` (Live Migration Execution):** `NOT_GRANTED` / `BLOCKED`.
- **`GATE-04` (Live PostgreSQL Catalogs & Probes):** `NOT_GRANTED` / `BLOCKED`.
- **`GATE-05` (Deprovisioning Schedule):** `NOT_GRANTED` / `BLOCKED`.

### 21.4 Complete Technical Blocker Register
1. **`BLOCKER-01` (`RLS-WRITE-AUTH-01`):** Permissive author write policy allows unvetted expert/researcher row modification.
2. **`BLOCKER-02` (`RLS-ROLE-ASSIGNMENT-01`):** Mutable-GUC role escalation via direct `user_roles` write access.
3. **`BLOCKER-03` (`DB-AUTH-01`):** Shared database principal (`acrevia_staging_app`) prevents database-level actor authentication.
4. **`BLOCKER-04` (`DB-CREDENTIAL-EXPOSURE-01`):** Public database owner credential exposure in `frontend/lib/server/db.ts`.
5. **`BLOCKER-05` (`APP-ROLE-SELF-SELECT-01`):** Unverified self-selection of expert/researcher roles during public HTTP registration.
6. **`BLOCKER-06` (`EXP-AUTH-01`):** Downstream API routes grant privileged access without verifying `ExpertProfile.verification_status`.
7. **`BLOCKER-07` (`CASCADE-ROLE-DEL-01`):** `ON DELETE CASCADE` from `users` to `user_roles` bypasses RLS, permitting denial of administrative roles.
8. **`BLOCKER-08` (`TENANT-MEMBERSHIP-01`):** 0 of 78 tenant tables enforce user-to-farm authorization in database policies.

### 21.5 Canonical Residual Risks
- **`RES-PULSE-01`:** Role-global evidence-table access without district scoping.
- **`RES-PULSE-02`:** READ COMMITTED snapshot/concurrency consistency window.
- **`RES-PRIMARY-ROUTING-01`:** Read/write primary-routing dependency.
- **`RES-REPLICA-LAG-01`:** Replica-lag exposure.
- **`RES-FREE-TEXT-01`:** PII exposure through author-controlled free text.

---

## 22. Documentation & Commit-State Reconciliation

| File Path | Local Disk State | Tracked in Git? | Committed in `c9e334d`? | Mirrored in Artifacts? | Explanation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `PHASE_07_PUBLIC_CREDENTIAL_INCIDENT_AND_GOVERNANCE_CONSISTENCY_ASSURANCE_REPORT.md` | Present | No (`??`) | No | Yes | Created during current audit; uncommitted per Mode A rules |
| `PHASE_07_PUBLIC_CREDENTIAL_EXPOSURE_AND_ROLE_GATEWAY_ASSURANCE_REPORT.md` | Present | No (`??`) | No | Yes | Created during previous audit; uncommitted per Mode A rules |
| `PHASE_07_GLOBAL_GUC_AND_TENANT_POLICY_TRACEABILITY_MATRIX.md` | Present | No (`??`) | No | Yes | Created during previous audit; uncommitted per Mode A rules |
| `PHASE_07_GLOBAL_RLS_IDENTITY_REMEDIATION_AND_ROLE_MANAGEMENT_CONTAINMENT_PLAN.md` | Present | No (`??`) | No | Yes | Created during previous audit; uncommitted per Mode A rules |
| 7 Tracked Security Dossiers in `docs/pilot/security/` | Present | Yes (`M`) | No (Addenda uncommitted) | Yes | Dated addenda appended locally; working tree uncommitted per Mode A rules |

---

## 23. Everything Claude Code (ECC) Independent Review

| Review Angle | Reviewer Challenge | Evidence-Grounded Resolution |
| :--- | :--- | :--- |
| **Security Reviewer** | Did the frontend fallback actually expose a live superuser? | **No.** `neondb_owner` is a cloud-managed role, not `rolsuper`. Live validity is unverified. However, it owns tables and satisfies `ADMIN_BYPASS_SQL`. |
| **Database Reviewer** | Can a `SECURITY DEFINER` function bypass RLS under `ADMIN_BYPASS_SQL`? | **No.** `SESSION_USER` remains `acrevia_staging_app`. `ADMIN_BYPASS_SQL` evaluates to FALSE. Capability A is NOT proven safe without policy adjustments. |
| **FastAPI Reviewer** | Does registration return an immediate JWT token? | **No.** Registration returns HTTP 201 with `UserResponse` (no token). Token is issued upon subsequent `/login` call, which checks only `is_active`. |
| **Architect** | Can `ON DELETE CASCADE` wipe roles if `DELETE ON user_roles` is revoked? | **Yes.** In PostgreSQL, foreign key cascades run with system privileges, bypassing child RLS and table grants. `DELETE ON users` must be revoked. |
| **Delivery Gate** | Can Phase 07 be released or Mode B authorized? | **Strictly No.** Credential rotation remains outstanding. Gates G-01 through G-05 are blocked. 8 active blockers remain. |

---

## 24. Release-Readiness Determination

- **Phase 07 Status:** **`NOT RELEASED`**
- **Mode B Authorization:** **`STRICTLY NOT AUTHORIZED`**
- **Immediate Requirement:** Project Owner must execute provider-side credential rotation and git history sanitization.

---

## 25. Exact Source Files Inspected
- `frontend/lib/server/db.ts`
- `frontend/app/api/v1/auth/register/route.ts`
- `frontend/app/api/v1/auth/login/route.ts`
- `frontend/app/api/v1/auth/me/route.ts`
- `aheadguard-mvp-starter/lib/db.ts`
- `backend/app/core/config.py`
- `backend/app/database/session.py`
- `backend/app/database/rls.py`
- `backend/app/database/migrations/env.py`
- `backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py`
- `backend/app/database/migrations/versions/d2894a11c87d_stage12_collaborative_intelligence.py`
- `backend/app/tasks/run_riskcast_batch.py`
- `backend/app/schemas/auth.py`
- `backend/app/services/auth_service.py`
- `backend/app/security/dependencies.py`
- `backend/app/models/user.py`
- `backend/app/api/v1/endpoints/auth.py`
- `backend/app/api/v1/endpoints/expertconnect.py`
- `backend/app/api/v1/endpoints/expert_reviews.py`
- `backend/app/api/v1/endpoints/knowledge.py`
- `backend/app/api/v1/endpoints/regional_pulse.py`
- `backend/app/api/v1/endpoints/research.py`
- `backend/tests/test_target_validation.py`

---

## 26. Exact Commands & Offline Tests Executed
- `git rev-parse --show-toplevel; git branch --show-current; git log -1; git remote -v`
- `git status --short`
- `git rev-parse HEAD origin/main`
- `git merge-base 63deadd41770adcfd976a453bb591c3367ed4379 HEAD`
- `git log --oneline 63deadd41770adcfd976a453bb591c3367ed4379..HEAD -- frontend/lib/server/db.ts`
- `git log --follow --format="%H %ad %s" -- frontend/lib/server/db.ts`
- `git tag --list`
- `git branch -a`
- `git check-ignore -v .env`
- Standalone redacted Python scanners in brain scratch directory:
  - `print_db_ts_redacted.py`
  - `parse_db_url_safe.py`
  - `find_getdb_fast.py`
  - `scan_all_postgres_urls.py`
  - `find_pw_in_git_history.py`
  - `count_and_inspect_routes.py`
  - `inspect_privileged_modules.py`
  - `find_verification_status.py`
  - `exact_route_inventory.py`
  - `count_tables.py`
  - `inspect_chain_clean.py`

---

## 27. Exact Files Created or Modified
- **Created (Formal Assurance Report):**  
  `docs/pilot/security/PHASE_07_PUBLIC_CREDENTIAL_INCIDENT_AND_GOVERNANCE_CONSISTENCY_ASSURANCE_REPORT.md`
- **Mirrored in Brain Artifacts Directory:**  
  `C:\Users\gokul\.gemini\antigravity\brain\8d770357-1b73-48ca-9930-eded206539c2\PHASE_07_PUBLIC_CREDENTIAL_INCIDENT_AND_GOVERNANCE_CONSISTENCY_ASSURANCE_REPORT.md`
- **Application Source Code Modified:** Exactly **0 files**.
- **ORM Models / Migrations Modified:** Exactly **0 files**.
