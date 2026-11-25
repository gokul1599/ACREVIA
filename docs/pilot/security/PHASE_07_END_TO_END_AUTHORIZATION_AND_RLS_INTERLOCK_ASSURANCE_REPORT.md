# ACREVIA — PHASE 07: END-TO-END AUTHORIZATION REACHABILITY & RLS/GRANT INTERLOCK ASSURANCE REPORT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** **MODE A ONLY — Local Source Inspection, Public Repository Inspection, Security Engineering, Offline Verification & Governance Documentation**  
**Methodology:** Everything Claude Code (ECC) — `PLAN → TEST → IMPLEMENT ONLY IF DEFECT PROVEN → REVIEW → VERIFY → DOCUMENT`  
**Audit Baseline:** Git Commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Timestamp:** November 24, 2026  
**Overall Determination:** **`END_TO_END_AUTHORIZATION_BLOCKED_WITH_PROVEN_SOURCE_DEFECTS`**  
**Phase 07 Production Release Status:** **`NOT RELEASED`**  
**Mode B Live Database Execution:** **`STRICTLY NOT AUTHORIZED`**

---

## 1. Executive Determination

An exhaustive, end-to-end authorization reachability and PostgreSQL Row-Level Security (RLS) / Grant interlock audit was conducted across the ACREVIA codebase under strict **MODE A ONLY** discipline.

### 1.1 Formal Classification Summary
- **Overall Operational Status:** **`END_TO_END_AUTHORIZATION_BLOCKED_WITH_PROVEN_SOURCE_DEFECTS`**
- **Public Credential Status:** **`CREDENTIAL_ROTATION_OUTSTANDING`** (`DB-CREDENTIAL-EXPOSURE-01` remains **OPEN**)
- **Registration Role Self-Selection:** **`PUBLIC_ROLE_SELF_SELECTION_CONFIRMED`** (`APP-ROLE-SELF-SELECT-01`)
- **Downstream Accreditation Defect:** **`PRIVILEGED_ROUTE_ROLE_ONLY`** (`EXP-AUTH-01` — 0/10 routes check accreditation)
- **Regional Pulse Reachability:** **`SOURCE_PATH_PERMITS`** (100% reachable at both API and Database layers)
- **Tenant Case / Dossier Reachability:** **`RLS_FILTERS_ROW`** (Blocked by RLS under standard unprivileged app role due to unset tenant context)
- **Knowledge Sources Reachability:** **`TABLE_GRANT_MISSING_IN_GENERATED_CONTRACT`** / **`RLS_FILTERS_ROW`** (API permits; DB denies write)
- **Grant-Source Deployment Gap:** **`LOCALLY_SPECIFIED_NEVER_EXECUTED_IN_MIGRATIONS`**
- **Phase 07 Release Gates:** **`GATES G-01 THROUGH G-05 REMAIN STRICTLY BLOCKED`**
- **Mode B Live Database Execution:** **`STRICTLY NOT AUTHORIZED`**

---

## 2. Mode A Scope and Mandatory Boundaries

Under strict **MODE A ONLY** rules:
- **No Remote Database Connections:** Zero network sockets or TLS handshakes initiated to Neon, AWS, PostgreSQL staging, or production.
- **No Credential Testing:** Zero attempts to authenticate or test the live validity of discovered passwords.
- **No SQL Execution:** Zero DDL, DML, or queries executed against live databases.
- **No Secrets Management / Cloud Console Access:** Zero interaction with Neon Console, Vercel dashboards, AWS IAM, or external secrets providers.
- **No Git History Rewrites or Branches:** Zero commits, pushes, force-pushes, branch creation, checkouts, resets, or stashes.
- **No Code Modifications:** Zero modifications to application source files, ORM models, test suites, or Alembic migrations.
- **Mandatory Redaction Protocol:** No cleartext passwords, complete connection strings, or secret-bearing tokens printed to terminal outputs, reports, logs, or persistent artifacts.

---

## 3. Repository Baseline and Evidence Provenance

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
- **Untracked Documentation Files (5 files):**
  - `?? docs/pilot/security/PHASE_07_GLOBAL_GUC_AND_TENANT_POLICY_TRACEABILITY_MATRIX.md`
  - `?? docs/pilot/security/PHASE_07_GLOBAL_RLS_IDENTITY_REMEDIATION_AND_ROLE_MANAGEMENT_CONTAINMENT_PLAN.md`
  - `?? docs/pilot/security/PHASE_07_PUBLIC_CREDENTIAL_EXPOSURE_AND_ROLE_GATEWAY_ASSURANCE_REPORT.md`
  - `?? docs/pilot/security/PHASE_07_PUBLIC_CREDENTIAL_INCIDENT_AND_GOVERNANCE_CONSISTENCY_ASSURANCE_REPORT.md`
  - `?? docs/pilot/security/PHASE_07_END_TO_END_AUTHORIZATION_AND_RLS_INTERLOCK_ASSURANCE_REPORT.md`
- **Application Source Code Modifications:** Exactly **0 files**.
- **ORM Models / Migration Modifications:** Exactly **0 files**.

---

## 4. Open Database Credential Incident Status (`DB-CREDENTIAL-EXPOSURE-01`)

- **Current File Status:** The fallback URI containing role `neondb_owner` and a 16-character cleartext password remains present in `frontend/lib/server/db.ts` (lines 8–11) in both local source and public `main` (`c9e334d`).
- **Owner Rotation Confirmation:** **NONE**. No signed, verifiable, or authorized confirmation of password rotation or credential revocation has been provided.
- **Incident Lifecycle Status:** **`CREDENTIAL_ROTATION_OUTSTANDING`**.
- **`DB-CREDENTIAL-EXPOSURE-01` remains strictly OPEN.**
- **PostgreSQL Role Attributes:** The username `neondb_owner` does not prove `rolsuper = true` or `rolbypassrls = true` in live PostgreSQL catalogs. However, it is the table owner and is explicitly whitelisted in `ADMIN_BYPASS_SQL`.

---

## 5. Complete Registration & Login Sequences

### 5.1 Scenario A: Public User Chooses Privileged Role (HTTP Path)
```
[Public Client]
      │
      │ 1. POST /api/v1/auth/register {"phone": "+919876543210", "role": "AGRICULTURAL_EXPERT"}
      ▼
[FastAPI / Next.js Handler]
      │
      │ 2. Schema validates role: pattern="^(FARMER|AGRICULTURAL_EXPERT|RESEARCHER)$"
      │ 3. Creates User record with is_active=true, is_verified=false
      │ 4. Inserts ("<user_uuid>", "AGRICULTURAL_EXPERT") directly into user_roles
      │ 5. Returns HTTP 201 Created with UserResponse body [NO JWT TOKEN ISSUED]
      ▼
[Client Calls Login]
      │
      │ 6. POST /api/v1/auth/login {"phone": "+919876543210", "password": "..."}
      ▼
[FastAPI / Next.js Auth Service]
      │
      │ 7. Verifies password hash
      │ 8. Verifies user.is_active [DOES NOT VERIFY user.is_verified]
      │ 9. Loads user.roles -> ["AGRICULTURAL_EXPERT"]
      │ 10. Signs JWT token carrying roles=["AGRICULTURAL_EXPERT"]
      │ 11. Returns HTTP 200 OK with TokenResponse {access_token: "eyJ...", token_type: "bearer"}
      ▼
[Client Invokes Privileged API Routes]
```

### 5.2 Scenario B: SQL-Level Privilege Escalation Under Application Principal
```
[Compromised App DB Session / SQLi]
      │
      │ 1. Attacker sets mutable GUC:
      │    SET LOCAL app.current_user_id = '<target_user_uuid>';
      ▼
[Direct SQL Execution]
      │
      │ 2. Attacker executes:
      │    INSERT INTO user_roles (user_id, role) VALUES ('<target_user_uuid>', 'ADMIN');
      ▼
[PostgreSQL RLS Engine]
      │
      │ 3. Evaluates user_roles_user_isolation_policy WITH CHECK:
      │    ({ADMIN_BYPASS_SQL} OR user_id::text = current_setting('app.current_user_id', true))
      │    -> ('<target_user_uuid>' = '<target_user_uuid>') evaluates to TRUE!
      │ 4. Insert commits successfully!
      ▼
[Target User API Request]
      │
      │ 5. Client sends standard JWT for <target_user_uuid>
      │ 6. FastAPI get_current_user loads user.roles from database -> contains 'ADMIN'
      │ 7. get_current_user executes:
      │    set_tenant_context(db, tenant_id=None, user_id=user.id, is_admin=True)
      │ 8. User is elevated to global application administrator!
```

### 5.3 Registration Transaction Atomicity Analysis
- **FastAPI (`auth_service.py`):** User creation and role assignment are committed via `db.commit()` in transaction 1. Audit logging is executed via `audit_service.record_activity`, which issues a separate `db.commit()` in transaction 2. If transaction 2 fails, the user and role remain committed. **Registration and audit logging are non-atomic.**
- **Next.js (`register/route.ts`):** Neon serverless HTTP queries execute as independent HTTP POST requests. There is **zero `BEGIN / COMMIT` transaction wrapper**.
  - If `INSERT INTO user_roles` fails, the `users` row has already been committed, leaving an orphaned user with **zero roles**.
  - If `INSERT INTO audit_logs` fails, it is caught by an empty `try/catch` block and swallowed silently, leaving an **unaudited account registration**.

---

## 6. Complete Route & Module Count Reconciliation

An exhaustive syntax and router-inclusion audit of `backend/app/api/v1/router.py` and `backend/app/api/v1/endpoints/` resolves all prior numerical discrepancies:

| Dimension | Previous Report Claim | Actual Reconstructed Count | Root-Cause Explanation |
| :--- | :--- | :--- | :--- |
| **Total Router Modules** | 22 modules | **49 modules** | Previous text counted a pre-Stage 14 core subset. `api_v1_router` in `router.py` explicitly mounts 49 endpoint files. |
| **Total Endpoint Routes** | 212 routes | **214 routes** | Previous AST regex parsing missed `POST /auth/register` and `POST /auth/login` due to multi-line rate-limit decorator parentheses. |
| **Privileged Expert/Researcher Routes** | 10 routes | **10 routes** | Confirmed exactly 10 routes across 4 specific modules. |

---

## 7. Ten Privileged-Route Manifest

| Route ID | HTTP Method & Full Path | Router File & Line | Handler Function | Role Dependency | Service Invoked | Target Tables |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PR-01** | `POST /api/v1/diagnoses/{id}/expert-review` | `expert_reviews.py:18` | `submit_expert_review` | `AGRICULTURAL_EXPERT` | `DiagnosisService.submit_expert_review` | `expert_reviews`, `diagnosis_requests` |
| **PR-02** | `GET /api/v1/expertconnect/cases` | `expertconnect.py:172` | `list_expert_cases` | `AGRICULTURAL_EXPERT`, `ADMIN` | `ExpertConnectService.list_cases` | `expert_review_cases` |
| **PR-03** | `POST /api/v1/expertconnect/cases/{id}/claim` | `expertconnect.py:193` | `claim_case` | `AGRICULTURAL_EXPERT`, `ADMIN` | `ExpertConnectService.claim_case` | `expert_review_cases` |
| **PR-04** | `GET /api/v1/expertconnect/cases/{id}` | `expertconnect.py:220` | `get_case_dossier` | `get_current_user` (Auth only) | `ExpertConnectService.get_case_dossier` | `expert_review_cases`, `observations`, `farms`, `plots` |
| **PR-05** | `POST /api/v1/expertconnect/cases/{id}/assess` | `expertconnect.py:232` | `submit_expert_assessment` | `AGRICULTURAL_EXPERT`, `ADMIN` | `ExpertConnectService.submit_assessment` | `expert_assessments`, `expert_review_cases` |
| **PR-06** | `PUT /api/v1/expertconnect/cases/{id}/assess` | `expertconnect.py:274` | `revise_expert_assessment` | `AGRICULTURAL_EXPERT`, `ADMIN` | `ExpertConnectService.revise_assessment` | `expert_assessments`, `expert_assessment_revisions` |
| **PR-07** | `POST /api/v1/knowledge/sources` | `knowledge.py:86` | `register_knowledge_source` | `ADMIN`, `AGRICULTURAL_EXPERT` | `IngestionService.register_source` | `knowledge_sources` |
| **PR-08** | `POST /api/v1/knowledge/ingest` | `knowledge.py:132` | `ingest_document` | `ADMIN`, `AGRICULTURAL_EXPERT` | `IngestionService.ingest_document` | `ingestion_jobs` |
| **PR-09** | `POST /api/v1/regional-pulse/signals` | `regional_pulse.py:27` | `aggregate_signal` | `ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER` | `RegionalPulseService.aggregate_signal` | `regional_signals`, `regional_signal_evidences` |
| **PR-10** | `POST /api/v1/regional-pulse/signals/{id}/recover` | `regional_pulse.py:152` | `recover_signal` | `ADMIN`, `AGRICULTURAL_EXPERT` | `RegionalPulseService.recover_signal` | `regional_signals` |

---

## 8. ExpertConnect Route & Service Audit

### 8.1 `list_expert_cases` (PR-02)
- **Application Layer:** `require_roles(AGRICULTURAL_EXPERT, ADMIN)` passes for any user who registered with `role: "AGRICULTURAL_EXPERT"`.
- **Database Layer:** Issues `db.query(ExpertReviewCase).filter(...).all()`.
- **RLS Evaluation:** `expert_review_cases` is categorized as `TENANT_DIRECT` (`farm_id`). Policy evaluates `farm_id::text = current_setting('app.current_tenant_id', true)`. Because `get_current_user` set `app.current_tenant_id = ''`, `farm_id = ''` is **FALSE** for all valid UUIDs.
- **Database Result:** **`RLS_FILTERS_ROW`**. The query returns an empty list (`[]`).

### 8.2 `claim_case` (PR-03)
- **Application Layer:** Passes role check. Checks `case.status == "QUEUED"`. Does NOT check expert verification.
- **Database Layer:** Issues `case = db.get(ExpertReviewCase, case_id)`.
- **RLS Evaluation:** Row is filtered out by `expert_review_cases_tenant_isolation_policy` (`farm_id = ''` is FALSE).
- **Database Result:** **`RLS_FILTERS_ROW`**. `db.get` returns `None`; service raises `NotFoundException("Case not found")`.

### 8.3 `get_case_dossier` (PR-04)
- **Application Layer:** Depends ONLY on `get_current_user` (Basic authentication). Does NOT check `AGRICULTURAL_EXPERT` role! Does NOT check case assignment! Does NOT check farm membership!
- **Database Layer:** Queries `ExpertReviewCase`, `Observation`, `Farm`, `Plot`.
- **RLS Evaluation:** All 4 tables are `TENANT_DIRECT`. Because `app.current_tenant_id = ''`, all rows are filtered out.
- **Database Result:** **`RLS_FILTERS_ROW`**. Raises `NotFoundException`.
- **Critical Conditional Exposure:** If the frontend connects using the `neondb_owner` fallback, RLS is bypassed. An attacker with any standard authenticated farmer token could read the entire clinical foliar dossier and farm identity!

### 8.4 `submit_expert_assessment` & `revise_expert_assessment` (PR-05 & PR-06)
- **Application Layer:** Passes role check. Does NOT check expert accreditation or case assignment.
- **Database Layer:** `expert_assessments` is `TENANT_INDIRECT` joining to `expert_review_cases`.
- **RLS Evaluation:** Parent case lookup returns `None` due to unset tenant GUC.
- **Database Result:** **`RLS_FILTERS_ROW`**. Raises `NotFoundException`.

### 8.5 Revision History Endpoint (`GET /cases/{case_id}/revisions`)
- **Inspection:** Located at `expertconnect.py:312`. Requires ONLY `get_current_user`.
- **Defect:** Any authenticated user can request revision histories. Under standard app RLS, returns `NotFoundException` due to tenant GUC filtering. Under owner fallback, exposes full agronomist prescription audit history.

---

## 9. Expert Review, Knowledge & Regional-Pulse Paths

### 9.1 `submit_expert_review` (PR-01)
- **Path:** `POST /api/v1/diagnoses/{diagnosis_id}/expert-review`
- **Application Layer:** `require_roles(AGRICULTURAL_EXPERT)` passes. Service checks `AGRICULTURAL_EXPERT in user.roles`. Zero checks on `is_verified` or `ExpertProfile`.
- **Database Layer:** Queries `DiagnosisRequest` (`TENANT_INDIRECT` -> parent `observations` -> `TENANT_DIRECT`).
- **RLS Evaluation:** `app.current_tenant_id = ''`. Observation join fails.
- **Database Result:** **`RLS_FILTERS_ROW`**. `db.get(DiagnosisRequest)` returns `None`; service raises `HTTPException(404, "Diagnosis request not found.")`.

### 9.2 Knowledge Source Registration (PR-07)
- **Path:** `POST /api/v1/knowledge/sources`
- **Application Layer:** `require_roles(ADMIN, AGRICULTURAL_EXPERT)` passes.
- **Database Layer:** Attempts `INSERT INTO knowledge_sources`.
- **Classification:** `knowledge_sources` is `TableCategory.SHARED_REFERENCE` with `access_type: PUBLIC_REFERENCE`.
- **Table Grant:** `PRIVILEGE_CROSSWALK` sets `can_insert = False`. Generated grant is `GRANT SELECT ON TABLE knowledge_sources TO acrevia_staging_app`.
- **RLS Write Policy:** Requires `{ADMIN_BYPASS_SQL}`.
- **Database Result:** **`TABLE_GRANT_MISSING_IN_GENERATED_CONTRACT`** / **`RLS_FILTERS_ROW`**. Database raises `permission denied for table knowledge_sources`.
- **Finding:** Complete architectural mismatch between FastAPI (permits expert) and PostgreSQL (restricts write to admin).

### 9.3 Document Ingestion (PR-08)
- **Path:** `POST /api/v1/knowledge/ingest`
- **Application Layer:** `require_roles(ADMIN, AGRICULTURAL_EXPERT)` passes.
- **Database Layer:** `ingestion_jobs` is `SHARED_REFERENCE` (`access_type: PRIVATE_OPERATIONAL`).
- **Table Grant:** `PRIVILEGE_CROSSWALK` sets `can_insert = True`.
- **RLS Policy:** Evaluates `ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')` -> TRUE!
- **Database Result:** **`SOURCE_PATH_PERMITS`**. A self-selected expert CAN successfully create an ingestion job at the database layer!

### 9.4 Regional Signal Aggregation & Recovery (PR-09 & PR-10)
- **Paths:** `POST /api/v1/regional-pulse/signals` and `POST /api/v1/regional-pulse/signals/{id}/recover`
- **Application Layer:** `require_roles` passes for `AGRICULTURAL_EXPERT` or `RESEARCHER`.
- **Database Layer:** `regional_signals` and `regional_signal_evidences` are `COMMUNITY_COLLABORATIVE`.
- **Table Grant:** `acrevia_staging_app` receives `GRANT SELECT, INSERT, UPDATE`.
- **RLS Policy:** Write policy checks:
  ```sql
  current_setting('app.current_user_id', true) != ''
  AND EXISTS (
      SELECT 1 FROM user_roles ur
      WHERE ur.user_id::text = current_setting('app.current_user_id', true)
      AND ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')
  )
  ```
- **Database Result:** **`SOURCE_PATH_PERMITS`**!
- **CRITICAL SECURITY PROOF:** The regional pulse write path does NOT depend on `app.current_tenant_id`! Because `app.current_user_id` is set and the self-selected role is present in `user_roles`, **both the application layer and database layer permit full row creation and mutation!** Any self-selected expert or researcher can publish pest signals and read raw cross-farm crop loss evidence!

---

## 10. Actor and Tenant Context Lifecycle

| Lifecycle Phase | Invoked By | `app.current_user_id` | `app.current_tenant_id` | `app.is_admin` | RLS Impact on `TENANT_DIRECT` Tables |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Request Start** | Connection acquisition (`get_db`) | Unset / empty | Unset / empty | Unset / `'false'` | Filtered out |
| **Post-Authentication** | `get_current_user` | `<user_uuid>` | `""` (empty string) | `'false'` (or `'true'` if Admin) | **Filtered out** (`farm_id = ''` is False) |
| **Post-Role Dependency** | `require_roles(...)` | `<user_uuid>` | `""` (empty string) | Unchanged | **Filtered out** |
| **Farm Authorization** | `verify_farm_access(farm_id)` | `<user_uuid>` | `<farm_id>` | Unchanged | **Permitted** for `<farm_id>` |
| **Session Cleanup** | `finally: clear_tenant_context` | `""` (empty string) | `""` (empty string) | `'false'` | Reset |

---

## 11. Runtime Grant-Source Reconciliation

A complete search for `generate_privilege_grants_ddl` across the codebase establishes:
- The generator exists in `backend/app/database/rls.py:1040`.
- It is exercised in unit tests (`test_worker_security_and_privacy.py`).
- **IT IS NEVER INVOKED BY ANY ALEMBIC MIGRATION FILE.**
- In `a1089411c87d_enable_postgresql_rls_tenant_isolation.py`, only `generate_rls_ddl()` is called.
- **Architectural Conclusion:** The least-privilege grant crosswalk is **`LOCALLY_SPECIFIED_NEVER_EXECUTED_IN_MIGRATIONS`**. If a database was provisioned via `alembic upgrade head`, table grants depend entirely on initial database creation scripts or cloud defaults, representing a critical deployment-architecture gap.

---

## 12. Complete Route-to-Query Reachability Matrix

| Route ID | Route Path | Table Name | Category | DML Operation | Table Grant in Crosswalk | RLS Policy Evaluation | GUC State Required | Reachability Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PR-01** | `POST /diagnoses/{id}/expert-review` | `diagnosis_requests` | `TENANT_INDIRECT` | SELECT | SELECT = True | Joins to observation; checks tenant ID | `tenant_id = ''` | **`RLS_FILTERS_ROW`** |
| **PR-01** | `POST /diagnoses/{id}/expert-review` | `expert_reviews` | `TENANT_INDIRECT` | INSERT | INSERT = True | Joins to diagnosis; checks tenant ID | `tenant_id = ''` | **`RLS_FILTERS_ROW`** |
| **PR-02** | `GET /expertconnect/cases` | `expert_review_cases` | `TENANT_DIRECT` | SELECT | SELECT = True | `farm_id = app.current_tenant_id` | `tenant_id = ''` | **`RLS_FILTERS_ROW`** |
| **PR-03** | `POST /expertconnect/cases/{id}/claim` | `expert_review_cases` | `TENANT_DIRECT` | UPDATE | UPDATE = True | `farm_id = app.current_tenant_id` | `tenant_id = ''` | **`RLS_FILTERS_ROW`** |
| **PR-04** | `GET /expertconnect/cases/{id}` | `expert_review_cases` | `TENANT_DIRECT` | SELECT | SELECT = True | `farm_id = app.current_tenant_id` | `tenant_id = ''` | **`RLS_FILTERS_ROW`** |
| **PR-04** | `GET /expertconnect/cases/{id}` | `observations` | `TENANT_DIRECT` | SELECT | SELECT = True | `farm_id = app.current_tenant_id` | `tenant_id = ''` | **`RLS_FILTERS_ROW`** |
| **PR-05** | `POST /expertconnect/cases/{id}/assess` | `expert_assessments` | `TENANT_INDIRECT` | INSERT | INSERT = True | Parent case join requires tenant ID | `tenant_id = ''` | **`RLS_FILTERS_ROW`** |
| **PR-06** | `PUT /expertconnect/cases/{id}/assess` | `expert_assessment_revisions` | `TENANT_INDIRECT` | INSERT | INSERT = True | Parent assessment join requires tenant ID | `tenant_id = ''` | **`RLS_FILTERS_ROW`** |
| **PR-07** | `POST /knowledge/sources` | `knowledge_sources` | `SHARED_REFERENCE` | INSERT | **INSERT = False** | Requires `{ADMIN_BYPASS_SQL}` | `is_admin = 'false'` | **`TABLE_GRANT_MISSING_IN_GENERATED_CONTRACT`** |
| **PR-08** | `POST /knowledge/ingest` | `ingestion_jobs` | `SHARED_REFERENCE` | INSERT | INSERT = True | Checks `role IN ('ADMIN', 'EXPERT', 'RESEARCHER')` | `user_id = <uuid>` | **`SOURCE_PATH_PERMITS`** |
| **PR-09** | `POST /regional-pulse/signals` | `regional_signals` | `COMMUNITY_COLLAB` | INSERT / UPDATE | INSERT = True, UPDATE = True | Checks `role IN ('ADMIN', 'EXPERT', 'RESEARCHER')` | `user_id = <uuid>` | **`SOURCE_PATH_PERMITS`** |
| **PR-09** | `POST /regional-pulse/signals` | `regional_signal_evidences` | `COMMUNITY_COLLAB` | INSERT / SELECT | INSERT = True, SELECT = True | Checks `role IN ('ADMIN', 'EXPERT', 'RESEARCHER')` | `user_id = <uuid>` | **`SOURCE_PATH_PERMITS`** |
| **PR-10** | `POST /regional-pulse/signals/{id}/recover` | `regional_signals` | `COMMUNITY_COLLAB` | UPDATE | UPDATE = True | Checks `role IN ('ADMIN', 'EXPERT')` | `user_id = <uuid>` | **`SOURCE_PATH_PERMITS`** |

---

## 13. Application-Layer vs. Database-Layer Conclusions

### 13.1 Distinct Boundary Findings
1. **Tenant Isolation Disconnect (ExpertConnect & Expert Reviews):**  
   - *Application Layer:* Vulnerable. Permits unaccredited self-selected experts to invoke triage and clinical endpoints.
   - *Database Layer:* Protected under standard unprivileged app role. Fails closed (`RLS_FILTERS_ROW`) because `app.current_tenant_id` is empty.
   - *Exploit Reachability:* **CONDITIONAL ON DATABASE PRINCIPAL**. If deployed using the hardcoded `neondb_owner` fallback, RLS is bypassed and data is exposed. If deployed using `acrevia_staging_app`, data is inaccessible.
2. **Regional Pulse Vulnerability (Complete Reachability):**  
   - *Application Layer:* Vulnerable. Permits self-selected experts and researchers to broadcast signals and view evidence.
   - *Database Layer:* Vulnerable. Policy explicitly permits write and evidence read based on `user_roles` membership without tenant context scoping.
   - *Exploit Reachability:* **100% REACHABLE**. Proven end-to-end vulnerability across both layers.
3. **Knowledge Base Inconsistency:**  
   - *Application Layer:* Permits experts to register sources.
   - *Database Layer:* Blocks writes with permission denied. Defective contract alignment.

---

## 14. Role Approval & Researcher Lifecycle Scope

- **Expert Lifecycle:** `ExpertProfile` model exists (`models/expert_profile.py`). Admin verification endpoint exists (`POST /expertconnect/admin/verify/{profile_id}`). However, **no operational endpoints require `verification_status == 'APPROVED'`**. The verification process is completely disconnected from authorization.
- **Researcher Lifecycle:** A scan of the entire repository confirms:
  **`RESEARCHER_APPROVAL_WORKFLOW_NOT_FOUND_IN_SCANNED_SCOPE`**.
  Zero profile models, zero application tables, zero verification services exist. Any user registering as `RESEARCHER` is permanently trusted across all researcher-scoped routes.

---

## 15. User Deletion & Foreign Key Cascades (`CASCADE-ROLE-DEL-01`)

- `user_roles.user_id` references `users.id` with `ON DELETE CASCADE`.
- In PostgreSQL, foreign key referential integrity cascades bypass RLS on child tables.
- `PRIVILEGE_CROSSWALK` gives `acrevia_staging_app` `GRANT DELETE ON TABLE users`.
- An SQL caller setting `app.current_user_id = '<admin_uuid>'` can execute `DELETE FROM users WHERE id = '<admin_uuid>'`.
- PostgreSQL deletes the user row and cascades to `user_roles`, permanently stripping all administrator roles.
- **Remediation:** Revoke direct `DELETE ON users` and implement soft-deletion.

---

## 16. Governance, Blocker & Risk Register Reconciliation

### 16.1 Canonical Governance Decisions
- **`D-01` (Regional Signal Visibility & Official-Advisory Data Model):** Options A, B, C, D (Pending Owner Selection).
- **`D-02` (Source Authenticity & Pilot Terminology):** Options A, B, C (Canonical definition restored).
- **`D-03` (Independent Expert Review):** Options A, B, C (Canonical definition restored).
- **`DB-AUTH-01` (Trusted Database Writer Identity):** Options A, B, C, D (Option D Recommended).

### 16.2 Canonical Release Gates
- `GATE-01` through `GATE-05` remain **`BLOCKED`** / **`NOT_GRANTED`**.

### 16.3 Complete Blocker Register
1. `BLOCKER-01` (`RLS-WRITE-AUTH-01`): Regional-signal author write policy allows unvetted expert/researcher row modification.
2. `BLOCKER-02` (`RLS-ROLE-ASSIGNMENT-01`): Mutable-GUC application role escalation via direct `user_roles` write access.
3. `BLOCKER-03` (`DB-AUTH-01`): Shared database principal (`acrevia_staging_app`) prevents database-level actor authentication.
4. `BLOCKER-04` (`DB-CREDENTIAL-EXPOSURE-01`): Public database owner credential exposure in `frontend/lib/server/db.ts`.
5. `BLOCKER-05` (`APP-ROLE-SELF-SELECT-01`): Unverified self-selection of expert/researcher roles during public HTTP registration.
6. `BLOCKER-06` (`EXP-AUTH-01`): Downstream API routes grant privileged access without verifying `ExpertProfile.verification_status`.
7. `BLOCKER-07` (`CASCADE-ROLE-DEL-01`): `ON DELETE CASCADE` from `users` to `user_roles` bypasses RLS, permitting denial of administrative roles.
8. `BLOCKER-08` (`TENANT-MEMBERSHIP-01`): 0 of 78 tenant tables enforce user-to-farm authorization in database policies.
9. `BLOCKER-09` (`OWNER-AUTH-01`): Outstanding Project Owner governance decisions and written Mode B execution authorization.
10. `BLOCKER-10` (`DB-RLS-01`): Live PostgreSQL RLS catalog verification pending.
11. `BLOCKER-11` (`WRK-DISP-01`): RiskCast batch worker production dispatch guard prevents unauthenticated task execution.
12. `BLOCKER-12` (`RES-PULSE-01`): Role-global evidence-table access without district scoping.
13. `BLOCKER-13` (`RES-PULSE-02`): READ COMMITTED snapshot/concurrency consistency window.
14. `BLOCKER-14` (`GATE01-PROV-01`): Live validation of staging branch provisioning pending.
15. `BLOCKER-15` (`RES-PULSE-READ-01`): Stale read policy exception and farm count threshold coupling.

---

## 17. Everything Claude Code (ECC) Independent Review

| Review Angle | Reviewer Challenge | Evidence-Grounded Resolution |
| :--- | :--- | :--- |
| **Security Reviewer** | Does public registration self-selection immediately expose farmer foliar dossiers? | **Conditionally.** At the API layer, yes. At the database layer, `TENANT_DIRECT` RLS filters out cases unless deployed with the exposed `neondb_owner` fallback. |
| **Database Reviewer** | Can a self-selected researcher modify regional signals under RLS? | **Yes. 100% Reachable.** `regional_signals` is community-collaborative; policy checks `user_roles` without tenant context restrictions. |
| **FastAPI Reviewer** | Why did previous reports state 212 routes instead of 214? | Multi-line rate-limit decorator formatting in `auth.py` omitted `/register` and `/login` in early AST regex scanners. |
| **Architect** | Are the least-privilege grants in `rls.py` executed by Alembic migrations? | **No.** `generate_privilege_grants_ddl()` is never invoked by any migration file. |
| **Delivery Gate** | Can Phase 07 be released? | **Strictly No.** Credential rotation remains outstanding. 15 active blockers remain. |

---

## 18. Release-Readiness Determination

- **Phase 07 Production Release Status:** **`NOT RELEASED`**
- **Mode B Live Database Execution:** **`STRICTLY NOT AUTHORIZED`**

---

## 19. Exact Source Files Inspected
- `frontend/lib/server/db.ts`
- `frontend/app/api/v1/auth/register/route.ts`
- `frontend/app/api/v1/auth/login/route.ts`
- `backend/app/api/v1/router.py`
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/database/session.py`
- `backend/app/database/rls.py`
- `backend/app/database/migrations/env.py`
- `backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py`
- `backend/app/schemas/auth.py`
- `backend/app/services/auth_service.py`
- `backend/app/services/audit_service.py`
- `backend/app/security/dependencies.py`
- `backend/app/models/user.py`
- `backend/app/models/expert_profile.py`
- `backend/app/api/v1/endpoints/expertconnect.py`
- `backend/app/services/expertconnect/expert_service.py`
- `backend/app/api/v1/endpoints/expert_reviews.py`
- `backend/app/services/diagnosis_service.py`
- `backend/app/api/v1/endpoints/knowledge.py`
- `backend/app/api/v1/endpoints/regional_pulse.py`
- `backend/app/services/regional_pulse_service.py`
- `backend/app/api/v1/endpoints/research.py`
- `backend/app/services/research_service.py`

---

## 20. Exact Commands & Offline Tests Executed
- `git rev-parse --show-toplevel; git branch --show-current; git log -1; git remote -v; git status --short`
- `git rev-parse HEAD origin/main`
- Python scanner scripts in brain scratch directory:
  - `inspect_set_context.py`
  - `check_expert_categories.py`
  - `inspect_indirect_policy_gen.py`
  - `find_regional_categories.py`
  - `find_knowledge_categories.py`
  - `find_grant_generator_calls.py`
  - `find_researcher_approval.py`
  - `inspect_get_revisions.py`
  - `list_all_modules_and_routes.py`
  - `inspect_v1_router.py`
  - `compare_route_counts.py`
  - `find_diagnosis_categories.py`

---

## 21. Files Created or Modified
- **Created (Formal Assurance Report):**  
  `docs/pilot/security/PHASE_07_END_TO_END_AUTHORIZATION_AND_RLS_INTERLOCK_ASSURANCE_REPORT.md`
- **Mirrored in Brain Artifacts Directory:**  
  `C:\Users\gokul\.gemini\antigravity\brain\8d770357-1b73-48ca-9930-eded206539c2\PHASE_07_END_TO_END_AUTHORIZATION_AND_RLS_INTERLOCK_ASSURANCE_REPORT.md`
- **Application Source Code Modified:** Exactly **0 files**.
- **ORM Models / Migrations Modified:** Exactly **0 files**.
