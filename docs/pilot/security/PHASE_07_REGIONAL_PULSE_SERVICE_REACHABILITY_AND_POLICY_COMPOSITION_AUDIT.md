# ACREVIA — PHASE 07: REGIONAL PULSE SERVICE REACHABILITY, WRITE-ON-READ SUPPRESSION & POSTGRESQL POLICY COMPOSITION ASSURANCE AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** MODE A ONLY — Local Source Inspection, Public Repository Inspection, Offline Security Analysis, Architecture Review & Governance Documentation  
**Methodology:** Everything Claude Code (ECC) — `PLAN → INSPECT → MODEL → TEST OFFLINE ONLY WHERE SAFE → ADVERSARIAL REVIEW → VERIFY → DOCUMENT`  
**Public Repository:** `https://github.com/gokul1599/ACREVIA`  
**Verified Baseline:** Commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Audit Status:** COMPLETE — FORMAL GOVERNANCE DELIVERABLE  
**Classification:** STRICTLY CONFIDENTIAL — AGRICULTURAL SECURITY & REGIONAL GOVERNANCE  

---

## 1. EXECUTIVE DETERMINATION

### Overall Audit Determination: `END_TO_END_AUTHORIZATION_BLOCKED_WITH_PROVEN_SOURCE_DEFECTS`

Following exhaustive multi-layer source inspection, formal policy composition modeling, and cross-layer execution tracing across the ACREVIA codebase at baseline `c9e334d14110e8a6e4c9b71b89cae3294288af0d`, the security assurance determination for Phase 07 is **`END_TO_END_AUTHORIZATION_BLOCKED_WITH_PROVEN_SOURCE_DEFECTS`**.

The application exhibits severe authorization and data-integrity defects in its source code, but the complete end-to-end attack paths reported in previous preliminary analyses are **substantially mitigated or blocked by downstream service guards and PostgreSQL RLS tenant isolation**, while simultaneously revealing a **critical, newly proven write-on-read denial-of-service vulnerability**:

1. **Critical Write-on-Read Signal Suppression Confirmed (`WRITE_ON_READ_MUTATION_POSSIBLE` / `SOURCE_PATH_CONFIRMED`):**  
   A critical architectural flaw exists in `GET /api/v1/regional-pulse/signals` and `GET /api/v1/regional-pulse/signals/{signal_id}`. Both HTTP read endpoints invoke `RegionalPulseService.revalidate_signal_provenance()` and explicitly execute `db.commit()` on the outer database session. Under standard authenticated read requests (`app.current_tenant_id = ''`), PostgreSQL RLS filters out all underlying observation and farm records. The revalidation logic interprets these hidden rows as invalid evidence, resets the verified farm count to zero, and stages a status mutation to `SUPPRESSED_INSUFFICIENT_PROVENANCE`. Because the generated `regional_signals_author_write_policy` is a permissive `FOR ALL` policy that grants UPDATE permissions to role-bearing actors (`AGRICULTURAL_EXPERT`, `RESEARCHER`), **any HTTP GET request by a self-selected expert or researcher permanently suppresses legitimate published signals in the database**. For unprivileged farmers, the mutation fails at `db.commit()` due to an RLS check violation, crashing the read endpoint with an HTTP 500 error.

2. **Normal Signal Publication Blocked by Downstream RLS Guard (`SERVICE_GUARD_BLOCKS`):**  
   While self-selected experts and researchers can pass the FastAPI route-level `@require_roles` check on `POST /api/v1/regional-pulse/signals`, they **cannot successfully publish regional signals**. The service requires evidence linking at least 3 distinct farms. During evidence verification under an empty tenant context (`app.current_tenant_id = ''`), RLS filters out cross-tenant observations (`RLS_FILTERS_ROW`), causing the service guard to calculate `verified_distinct_farms = 0 < 3` and abort with `HTTP 400 Bad Request`.

3. **Official Advisory Publication Strictly Guarded (`SERVICE_GUARD_BLOCKS`):**  
   Self-selected experts and researchers are strictly prevented from issuing official state advisories via `POST /api/v1/regional-pulse/signals` by an explicit, mandatory service-layer role check (`if data.confidence_tier == 'OFFICIAL_ADVISORY' and 'ADMIN' not in effective_roles: raise HTTPException(403)`).

4. **Knowledge Ingestion Write-Path Blocked at Step 1 (`TABLE_GRANT_BLOCKS` / `RLS_WITH_CHECK_BLOCKS_WRITE`):**  
   Self-selected experts cannot create malicious ingestion jobs via `POST /api/v1/knowledge/ingest`. Although `ingestion_jobs` has a permissive role-based RLS write policy, `IngestionService.ingest_document()` executes an ordered write sequence where Step 1 inserts into `knowledge_documents` (`SHARED_REFERENCE`). The generated privilege crosswalk grants `acrevia_staging_app` SELECT only on this table, and the RLS write policy requires `ADMIN_BYPASS_SQL`. Step 1 flushes and aborts the transaction before any ingestion job can be created.

5. **Raw Farmer Evidence Privacy Preserved at API Boundary (`SOURCE_CONFIRMED`):**  
   `RegionalSignalEvidence` API schemas expose only association metadata (UUIDs, signal ID, evidence type, evidence reference ID, notes, timestamp). The underlying farmer observations, plots, sensor telemetries, and farm PII reside in `TENANT_DIRECT` tables and remain strictly protected by PostgreSQL RLS. Cross-district signal viewing does not leak raw farmer records.

6. **Privilege Grants Never Executed in Migrations (`LOCALLY_SPECIFIED_NEVER_EXECUTED_IN_MIGRATIONS`):**  
   The privilege generator function `generate_privilege_grants_ddl()` is completely absent from all Alembic migrations (`backend/migrations/versions/a1089411c87d_*.py` calls only `generate_rls_ddl()`). Live database table grants depend entirely on external DBA scripts or cloud defaults, leaving deployed ACLs unverified (`LIVE_ACL_NOT_VERIFIED`).

7. **Open Public Database Credential Incident (`DB-CREDENTIAL-EXPOSURE-01`):**  
   A live Neon PostgreSQL administrative connection string remains exposed in public repository history in `frontend/lib/db.ts`. The credential provides connection access as `neondb_owner`. Until formal rotation is confirmed by the project owner, this incident remains **OPEN** with release blocker status.

8. **Phase 07 Release Gate Status (`GATE-01` through `GATE-05` BLOCKED):**  
   Phase 07 remains **NOT RELEASED**. Mode B live execution remains **NOT AUTHORIZED**.

---

## 2. BASELINE AND SCOPE

### 2.1 Repository Baseline
- **Inspected Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`HEAD` -> `main`, `origin/main`).
- **Initial User-Reported Baseline:** `dbad296c6f19c4bbe8eb48fcd7a0e07441cfa408`.
- **Intervening History:** Commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d` updated documentation and security governance dossiers without altering application source code, ORM models, migrations, or test suites.
- **Working Tree Integrity:** Clean working tree; zero modifications to application source, models, tests, or database configuration files.

### 2.2 Mode A Non-Negotiable Boundaries
This audit was conducted strictly under **MODE A**:
- **Prohibited & Not Attempted:** Connecting to Neon, PostgreSQL staging, production databases or any remote endpoint; validating discovered credentials; executing SQL on live databases; executing Alembic migrations; mutating application source code, ORM models, or tests.
- **Scope:** Complete source-level AST parsing, route-to-database dependency tracing, formal RLS policy composition analysis, service transaction modeling, and governance register reconciliation.

---

## 3. EVIDENCE CLASSIFICATION METHODOLOGY

Every material finding in this audit is classified under one of nine standardized evidence tiers:

1. `SOURCE_CONFIRMED` — Directly proven by inspected application source code.
2. `POLICY_GENERATOR_CONFIRMED` — Established by SQL emitted from `generate_rls_ddl()`.
3. `STATIC_SERVICE_PATH_CONFIRMED` — Established by tracing service methods and ordered operations.
4. `OFFLINE_TEST_CONFIRMED` — Verified through isolated, offline mock testing without network access.
5. `CONDITIONAL_ON_DEPLOYED_GRANTS` — Requires actual PostgreSQL table privileges (`GRANT ...`).
6. `CONDITIONAL_ON_DEPLOYED_RLS` — Requires generated policies to be installed and active on the database.
7. `CONDITIONAL_ON_EFFECTIVE_DB_PRINCIPAL` — Depends on the effective database role attributes (`BYPASSRLS`, table owner, superuser).
8. `USER_REPORTED_NOT_INDEPENDENTLY_VERIFIED` — Supplied in prior reports but not independently verifiable in Mode A.
9. `LIVE_POSTGRESQL_NOT_VERIFIED` — Unverifiable without live database access (strictly prohibited in Mode A).

### 3.1 Required Route-to-Database 11-Layer Evidence Model

To eliminate false positives from single-layer analysis, every endpoint is evaluated through the complete 11-layer execution chain:

```
[1. HTTP ROUTE] 
      │
[2. AUTHENTICATION (JWT)]
      │
[3. APPLICATION ROLE (@require_roles)]
      │
[4. ACTOR GUC (app.current_user_id)]
      │
[5. TENANT GUC (app.current_tenant_id)]
      │
[6. SERVICE GUARD (Logic/Role/Threshold)]
      │
[7. ORM QUERY / WRITE (db.get / db.add / db.flush)]
      │
[8. TABLE CLASSIFICATION (TENANT_DIRECT / COLLABORATIVE / SHARED)]
      │
[9. GENERATED GRANT (PRIVILEGE_CROSSWALK)]
      │
[10. GENERATED RLS POLICY (USING / WITH CHECK)]
      │
[11. EXPECTED OUTCOME]
```

---

## 4. COMPLETE API ROUTE MANIFEST AND COUNT RECONCILIATION

### 4.1 Route Count Discrepancy Resolution: 212 vs 214 Routes
Previous preliminary scans reported 212 routes, omitting two critical authentication endpoints due to a regex parsing flaw that failed to match multi-line Python decorators:

```python
# backend/app/api/v1/endpoints/auth.py:48-52
@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account"
)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
```

A full AST parse utilizing Python's standard library `ast` module independently proves:
- **Total Router Modules:** Exactly **49 router modules** in `backend/app/api/v1/endpoints/*.py` (excluding `__init__.py`).
- **Total Master Mounted Routers:** All 49 router modules are imported and included in `backend/app/api/v1/router.py` via `api_v1_router.include_router(...)`.
- **Total v1 API Routes:** Exactly **214 routes** defined across the 49 modules.
- **Root Diagnostic Routes:** Exactly **3 endpoints** mounted directly on `app` in `backend/app/main.py` (`GET /health`, `GET /ready`, `GET /`).
- **Total Application Routes:** Exactly **217 endpoints**.

### 4.2 Route Distribution by HTTP Method (v1 API)
- `GET`: 119 routes (55.6%)
- `POST`: 72 routes (33.6%)
- `PUT`: 15 routes (7.0%)
- `DELETE`: 7 routes (3.3%)
- `PATCH`: 1 route (0.5%)
- **Total:** **214 routes**

### 4.3 High-Risk / Privileged Endpoint Classification
Of the 214 routes, seven endpoints enforce role-based dependencies via `@require_roles`, while three sensitive ExpertConnect routes enforce only general authentication:

| Endpoint Path | HTTP Method | Router File | Authentication | Role Check | Target Sensitive Entity |
|---|---|---|---|---|---|
| `/api/v1/regional-pulse/signals` | `POST` | `regional_pulse.py` | `get_current_user` | `ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER` | `RegionalSignal`, `RegionalSignalEvidence` |
| `/api/v1/regional-pulse/signals/{signal_id}/recover` | `POST` | `regional_pulse.py` | `get_current_user` | `ADMIN`, `AGRICULTURAL_EXPERT` | `RegionalSignal` |
| `/api/v1/knowledge/sources` | `POST` | `knowledge.py` | `get_current_user` | `ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER` | `KnowledgeSource` |
| `/api/v1/knowledge/ingest` | `POST` | `knowledge.py` | `get_current_user` | `ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER` | `KnowledgeDocument`, `IngestionJob` |
| `/api/v1/expertconnect/cases/{case_id}/claim` | `POST` | `expertconnect.py` | `get_current_user` | `ADMIN`, `AGRICULTURAL_EXPERT` | `ExpertReviewCase` |
| `/api/v1/expertconnect/cases/{case_id}/assess` | `POST` | `expertconnect.py` | `get_current_user` | `ADMIN`, `AGRICULTURAL_EXPERT` | `ExpertAssessment`, `ExpertAssessmentRevision` |
| `/api/v1/expertconnect/cases/{case_id}/assess` | `PUT` | `expertconnect.py` | `get_current_user` | `ADMIN`, `AGRICULTURAL_EXPERT` | `ExpertAssessment`, `ExpertAssessmentRevision` |
| `/api/v1/diagnoses/{diagnosis_id}/expert-review` | `POST` | `expert_reviews.py` | `get_current_user` | `ADMIN`, `AGRICULTURAL_EXPERT` | `ExpertReview` |
| `/api/v1/expertconnect/cases/{case_id}` | `GET` | `expertconnect.py` | `get_current_user` | *None (Auth-Only)* | `ExpertReviewCase`, `Observation` |
| `/api/v1/expertconnect/cases/{case_id}/revisions` | `GET` | `expertconnect.py` | `get_current_user` | *None (Auth-Only)* | `ExpertAssessmentRevision` |
| `/api/v1/expertconnect/cases/create-from-observation/{obs_id}` | `POST` | `expertconnect.py` | `get_current_user` | *None (Auth-Only)* | `ExpertReviewCase`, `Observation` |

---

## 5. REGISTRATION, ACCREDITATION AND TOKEN ISSUANCE FINDINGS

Inspection of `backend/app/schemas/auth.py`, `backend/app/services/auth_service.py`, `backend/app/security/dependencies.py`, and `frontend/app/api/v1/auth/register/route.ts` establishes the answers to the eight mandatory registration and accreditation questions:

### 1. Role Self-Selection at Registration: `YES` (`SOURCE_CONFIRMED`)
`UserCreate` (`backend/app/schemas/auth.py:46-52`) defines:
```python
role: Optional[str] = Field(
    default="FARMER",
    description="Requested user role: FARMER, EXTENSION_OFFICER, AGRICULTURAL_EXPERT, RESEARCHER, ADMIN"
)
```
Any registering user can supply `AGRICULTURAL_EXPERT` or `RESEARCHER` in the registration payload.

### 2. Administrative Pre-Authorization Requirement: `NO` (`SOURCE_CONFIRMED`)
`AuthService.register_user` (`backend/app/services/auth_service.py:100-145`) directly looks up the requested role in the database (`db.query(Role).filter(Role.name == requested_role).first()`) and binds it via `UserRole(user_id=new_user.id, role_id=role_record.id)` without checking for administrator approval, invitation tokens, or verification credentials.

### 3. Immediate JWT Issuance upon Registration: `YES` (`SOURCE_CONFIRMED`)
`register_user()` calls `create_access_token()` immediately following database commit and returns a valid Bearer JWT in `TokenResponse`.

### 4. Login Verification / Profile Approval Gating: `NO` (`SOURCE_CONFIRMED`)
`AuthService.authenticate_user` (`backend/app/services/auth_service.py:150-185`) verifies only email and password hash (`verify_password`). It does not verify `is_verified`, does not query `ExpertProfile`, and does not check accreditation status before issuing tokens.

### 5. Role Claims in JWT: `ROLE NAMES EMBEDDED` (`SOURCE_CONFIRMED`)
The JWT payload includes `sub: str(user.id)`, `roles: [r.name for r in user.roles]`, and `exp`.

### 6. `require_roles` Behavior: `MEMBERSHIP ONLY` (`SOURCE_CONFIRMED`)
`backend/app/security/dependencies.py:require_roles` checks:
```python
user_roles = [r.name for r in current_user.roles]
if not any(role in user_roles for role in allowed_roles):
    raise HTTPException(status_code=403, detail="Insufficient permissions")
```
It validates solely that the role string exists in the user's assigned roles; it never verifies professional accreditation or profile validation.

### 7. Administrator Approval Workflow Coupling: `DECOUPLED` (`SOURCE_CONFIRMED`)
`ExpertProfile` (`backend/app/models/expert.py:22-55`) and `ExpertService.verify_expert_profile()` exist in the codebase, but they operate as an asynchronous post-registration profile. The `AGRICULTURAL_EXPERT` role is assigned at registration and remains active regardless of `ExpertProfile.status`.

### 8. Existence of Researcher Accreditation Workflow: `COMPLETELY ABSENT` (`SOURCE_CONFIRMED`)
An exhaustive scan across all models, services, schemas, and endpoints reveals that **no researcher profile model, verification service, accreditation check, or administrative approval workflow exists anywhere in the repository**. The `RESEARCHER` role is purely self-selected with zero downstream governance.

### 5.1 Registration Transaction Integrity
In `backend/app/services/auth_service.py`:
- `db.add(new_user)`
- `db.flush()`
- `db.add(user_role)`
- `audit_service.log_event(db, ...)`
- `db.commit()`
User creation, role assignment, and audit logging share a single SQLAlchemy transaction. If role lookup or audit logging fails, the transaction rolls back atomically. A user cannot be committed without their assigned role.

---

## 6. ACTOR/TENANT GUC LIFECYCLE AND DATABASE CONTEXT

### 6.1 Context Matrix for Sensitive Endpoints

| Context Property | Source Implementation | Transaction Scope | Clearing / Cleanup | Regional Pulse GET / POST | ExpertConnect Cases | Knowledge Ingest |
|---|---|---|---|---|---|---|
| `app.current_user_id` | `get_current_user` via JWT `sub` | Connection / Local | None (relies on pool reset) | Set to authenticated user | Set to authenticated user | Set to authenticated user |
| `app.current_tenant_id` | `set_tenant_context()` | Transaction `SET LOCAL` | Per-transaction rollback | **EMPTY (`""`)** | **EMPTY (`""`)** | **EMPTY (`""`)** |
| `app.is_admin` | `get_current_user` | Connection / Local | None | `'false'` (unless Admin) | `'false'` (unless Admin) | `'false'` (unless Admin) |
| Farm Authorization | `verify_farm_access()` | N/A | N/A | **NOT CALLED** | **NOT CALLED** | **NOT CALLED** |

### 6.2 The Empty Tenant Context Reality (`SOURCE_CONFIRMED`)
`backend/app/security/dependencies.py:get_current_user` sets `app.current_user_id = str(user.id)`, but **never sets `app.current_tenant_id`**.
`set_tenant_context(db, tenant_id)` is invoked only on farm-scoped routes (such as `/api/v1/farms/{farm_id}/...`). 
Because Regional Pulse, general ExpertConnect, and Knowledge Ingestion routes are global/regional, **they execute with `app.current_tenant_id = ''`**.

### 6.3 Critical PostgreSQL Architectural Distinctions
- **Application Role Check Passing:** Evaluated in Python before any database interaction.
- **RLS-Protected SELECT Filtering (`RLS_FILTERS_ROW`):** PostgreSQL silently omits rows failing the `USING` clause. The query succeeds and returns `None` or an empty list without raising an SQL exception.
- **RLS-Protected Write Rejection (`RLS_WITH_CHECK_BLOCKS_WRITE`):** PostgreSQL raises `insufficient_privilege` (SQLSTATE `42501`) when an INSERT or UPDATE violates the `WITH CHECK` clause.
- **Missing Table Privilege (`TABLE_GRANT_BLOCKS`):** PostgreSQL raises `permission denied for table ...` (SQLSTATE `42501`) before RLS policies are even evaluated.

---

## 7. REGIONAL PULSE — RECONSTRUCT THE COMPLETE POST PATH

### 7.1 Execution Trace: `POST /api/v1/regional-pulse/signals`

```
1. HTTP Request arrives at POST /api/v1/regional-pulse/signals
2. Authentication Dependency: get_current_user decodes JWT, sets app.current_user_id = user.id
   app.current_tenant_id remains empty ('')
3. Role Gate: @require_roles('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER') -> PASSES
4. Route calls RegionalPulseService.aggregate_regional_signal(db, data, current_user.id)
5. Service Guard 1: Official Advisory Check:
   if data.confidence_tier == 'OFFICIAL_ADVISORY' and 'ADMIN' not in effective_roles:
       raise HTTPException(403, 'Only verified state agricultural administrators...')
       --> BLOCKS non-admin users attempting to issue official advisories
6. Service Guard 2: Evidence Provenance & Minimum 3-Farm Threshold:
   Iterates through data.evidence_references:
   - For 'OBSERVATION': db.get(Observation, ref_id)
     * Observation table is TENANT_DIRECT: USING (tenant_id = current_tenant_id())
     * Since current_tenant_id is '', RLS filters row -> returns None!
   - Since obs is None, db.get(Farm, obs.farm_id) is NOT called or fails
   - Verified distinct farms remains 0
   - Service evaluates: if len(distinct_farms) < 3:
         raise HTTPException(400, 'Regional signal requires evidence linking at least 3 distinct farms')
7. Execution terminates with HTTP 400 Bad Request!
8. Database INSERT on regional_signals is NEVER REACHED!
```

### 7.2 Reachability Determinations
- **Official Advisory Publication:** **`SERVICE_GUARD_BLOCKS`** (`SOURCE_CONFIRMED`). Non-admin actors are strictly blocked at line 76 of `regional_pulse_service.py`.
- **Normal Regional Signal Publication:** **`SERVICE_GUARD_BLOCKS`** under standard RLS (`SOURCE_CONFIRMED` / `STATIC_SERVICE_PATH_CONFIRMED`). Because `app.current_tenant_id = ''`, RLS silently filters out all observations (`RLS_FILTERS_ROW`). The service derives zero verified farms and aborts with `HTTP 400`. Unconfined signal spam via the API is completely blocked under standard tenant isolation.

---

## 8. REGIONAL PULSE — INVESTIGATE THE WRITE-ON-READ SUPPRESSION PATH

### 8.1 Vulnerability Discovery: Write-on-Read Signal Suppression
In `backend/app/api/v1/endpoints/regional_pulse.py`, both `GET /signals` (lines 75-92) and `GET /signals/{signal_id}` (lines 120-142) execute mutative revalidation:

```python
# GET /signals endpoint
@router.get("/signals", response_model=List[RegionalSignalResponse])
def get_regional_signals(..., db: Session = Depends(get_db)):
    signals = RegionalPulseService.query_signals(db, ...)
    for sig in signals:
        RegionalPulseService.revalidate_signal_provenance(db, sig.id)
    db.commit()  # <-- EXPLICIT COMMIT IN HTTP GET ROUTE!
    return signals
```

### 8.2 Execution Trace of `revalidate_signal_provenance()`

```
1. Caller executes GET /api/v1/regional-pulse/signals or GET /api/v1/regional-pulse/signals/{id}
2. Endpoint calls RegionalPulseService.revalidate_signal_provenance(db, signal.id)
3. Service enters savepoint: with db.begin_nested():
4. Service iterates signal.evidences:
   - For 'OBSERVATION': executes db.get(Observation, ref.evidence_reference_id)
   - Database evaluates RLS on observations: tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
   - Under GET request, app.current_tenant_id is '' -> RLS filters row!
   - db.get() returns None!
5. Service finds obs is None -> skips evidence, does NOT add farm to verified_farms
6. Service calculates verified_farms = 0
7. Service sets:
   signal.distinct_farms_count = 0
   signal.validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'
8. Nested savepoint completes without SQL exception (RLS filtering is not an error)
9. Revalidation returns False
10. Endpoint executes outer db.commit()!
```

### 8.3 PostgreSQL Policy Composition on `regional_signals`
In `backend/app/database/rls.py`, the generated policies on `regional_signals` are:
1. `regional_signals_read_policy`: `FOR SELECT USING (is_active = true OR is_admin() = 'true')`.
2. `regional_signals_author_write_policy`: `FOR ALL USING (...) WITH CHECK (...)`:
```sql
CREATE POLICY regional_signals_author_write_policy ON regional_signals
FOR ALL TO acrevia_staging_app
USING (
    author_id = NULLIF(current_setting('app.current_user_id', true), '')::uuid
    OR (SELECT NULLIF(current_setting('app.is_admin', true), '')) = 'true'
    OR (SELECT current_setting('app.current_user_roles', true)) ~* '(AGRICULTURAL_EXPERT|RESEARCHER)'
)
WITH CHECK (
    author_id = NULLIF(current_setting('app.current_user_id', true), '')::uuid
    OR (SELECT NULLIF(current_setting('app.is_admin', true), '')) = 'true'
    OR (SELECT current_setting('app.current_user_roles', true)) ~* '(AGRICULTURAL_EXPERT|RESEARCHER)'
);
```

### 8.4 Policy Composition & Outcome
PostgreSQL combines permissive policies using logical `OR`. 
Because `regional_signals_author_write_policy` is a `FOR ALL` policy, it applies to `SELECT`, `INSERT`, `UPDATE`, and `DELETE`.

- **When Caller is `AGRICULTURAL_EXPERT` or `RESEARCHER`:**  
  The `current_setting('app.current_user_roles', true) ~* '(AGRICULTURAL_EXPERT|RESEARCHER)'` predicate evaluates to **TRUE**.
  The RLS `WITH CHECK` clause allows the UPDATE!
  The outer `db.commit()` **SUCCEEDS**, permanently overwriting `validation_status` to `SUPPRESSED_INSUFFICIENT_PROVENANCE` and `distinct_farms_count` to `0`!
  **Outcome:** **`WRITE_ON_READ_MUTATION_POSSIBLE`** (`SOURCE_PATH_CONFIRMED`). A simple read request destroys published signals.

- **When Caller is an Ordinary Farmer:**  
  The role check is FALSE and `author_id` does not match.
  The RLS `WITH CHECK` clause **BLOCKS** the UPDATE, raising `insufficient_privilege` (SQLSTATE `42501`).
  The outer route catches the exception in `db.rollback()`, and the GET endpoint crashes with an HTTP 500 Internal Server Error!

### 8.5 Test Gap Identification
Existing tests in `tests/test_regional_pulse.py` mock `revalidate_signal_provenance` or test it in an isolated environment where all observations belong to the test user's tenant or RLS is disabled. **Zero existing tests model the complete sequence of an empty tenant GUC, cross-tenant observation invisibility, revalidation failure, and outer GET transaction commit.**

---

## 9. RECOVERY PATH — VERIFY THE SERVICE-LEVEL RESULT

### 9.1 Trace of `POST /api/v1/regional-pulse/signals/{signal_id}/recover`
1. Route decorator `@require_roles('ADMIN', 'AGRICULTURAL_EXPERT')` passes for self-selected experts (`APPLICATION_ROLE_GATE_PASSES`).
2. Endpoint calls `RegionalPulseService.recover_suppressed_signal(db, signal_id, current_user.id, payload.reason)`.
3. Service locks `RegionalSignal` using `with_for_update()`.
4. Service iterates through associated evidence and queries `db.get(Observation, ref_id)` and `db.get(Farm, obs.farm_id)`.
5. Under `app.current_tenant_id = ''`, PostgreSQL RLS filters out observations (`RLS_FILTERS_ROW`), returning `None`.
6. Service calculates `verified_farms = 0 < 3`.
7. Service raises:
   `HTTPException(400, 'Cannot recover signal: verified distinct farms remains below threshold')`.
8. Recovery transaction aborts.

### 9.2 Conclusion
**`SERVICE_GUARD_BLOCKS`** (`SOURCE_CONFIRMED`). Signal recovery by an expert fails closed under standard RLS. Recovery can only succeed if executed by an administrative principal with `ADMIN_BYPASS_SQL` or within a context that possesses cross-tenant read privileges.

---

## 10. REGIONAL EVIDENCE PRIVACY — ASSOCIATIONS VS UNDERLYING RECORDS

A rigorous distinction must be maintained between evidence association metadata and underlying source records:

### 10.1 Association Metadata Visibility (`SOURCE_CONFIRMED`)
`RegionalSignalEvidence` (`backend/app/models/regional_pulse.py:90-130`) defines:
- `id`: UUID (Primary Key)
- `signal_id`: UUID (Foreign Key)
- `evidence_type`: String (`OBSERVATION`, `RISK_ALERT`, `SATELLITE_ANOMALY`)
- `evidence_reference_id`: UUID (Foreign Key to underlying record)
- `evidence_notes`: Text
- `created_at`: DateTime

Under `regional_signal_evidences_collaborative_read_policy`, actors with `AGRICULTURAL_EXPERT` or `RESEARCHER` roles can read association rows across all districts. They can observe UUID references and expert notes.

### 10.2 Underlying Record Visibility (`SOURCE_CONFIRMED`)
The underlying data sources reside in distinct, strictly isolated tables:
- `observations`: `TENANT_DIRECT` table (`USING (tenant_id = current_tenant_id())`).
- `farms`: `TENANT_DIRECT` table (`USING (id = current_tenant_id())`).
- `plots`: `TENANT_DIRECT` table (`USING (farm_id = current_tenant_id())`).

Under an empty tenant context (`app.current_tenant_id = ''`), an expert cannot select or join these tables. Attempting to query `observations` directly returns zero rows (`RLS_FILTERS_ROW`).

### 10.3 API Response Exposure Analysis
The API response schema `RegionalSignalResponse` embeds `List[RegionalSignalEvidenceResponse]`. It serializes only the association fields (`id`, `evidence_type`, `evidence_reference_id`, `evidence_notes`). **It does not join, serialize, or return the farmer's name, phone number, plot geometry, cadastral details, or raw field telemetry.**

### 10.4 Finding Refinement: `RES-PULSE-01`
Previous reports characterized `RES-PULSE-01` as "cross-district leakage of raw farmer evidence". This audit formally refines the finding:
- **Actual Risk:** Cross-district visibility of **association metadata and evidence UUIDs**.
- **Refinement:** Raw farmer observation records and farm PII remain protected by PostgreSQL RLS. Privacy leak is bounded to evidence association identifiers and notes, not underlying tenant records.

---

## 11. KNOWLEDGE INGESTION — ORDERED WRITE-PATH AUDIT

### 11.1 Source Registration: `POST /api/v1/knowledge/sources`
- Route Gate: `@require_roles('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')` -> `APPLICATION_ROLE_GATE_PASSES`.
- Table: `knowledge_sources` (`SHARED_REFERENCE`).
- Generated RLS Write Policy: Requires `is_admin() = 'true'` (`ADMIN_BYPASS_SQL`).
- Outcome: **`RLS_WITH_CHECK_BLOCKS_WRITE`** (`POLICY_GENERATOR_CONFIRMED`). Non-admin users are blocked from inserting knowledge sources at the database layer.

### 11.2 Ingestion Job Pipeline: `POST /api/v1/knowledge/ingest`
`IngestionService.ingest_document()` executes the following ordered sequence:

```python
# Step 1: Insert KnowledgeDocument
doc = KnowledgeDocument(...)
db.add(doc)
db.flush()  # <-- STEP 1 WRITE FLUSH

# Step 2: Insert KnowledgeDocumentVersion
doc_version = KnowledgeDocumentVersion(...)
db.add(doc_version)
db.flush()  # <-- STEP 2 WRITE FLUSH

# Step 3: Insert IngestionJob
job = IngestionJob(...)
db.add(job)
db.commit() # <-- STEP 3 COMMIT
```

### 11.3 Multi-Layer Policy Analysis of Step 1

| Table | Classification | Generated Table Grant (`PRIVILEGE_CROSSWALK`) | Generated RLS Policy (`generate_rls_ddl`) | Expected Step 1 Result |
|---|---|---|---|---|
| `knowledge_documents` | `SHARED_REFERENCE` | `can_insert = False` (SELECT only for `acrevia_staging_app`) | `WITH CHECK (is_admin() = 'true')` | **FAILS AT FLUSH** (`TABLE_GRANT_BLOCKS` or `RLS_WITH_CHECK_BLOCKS_WRITE`) |
| `knowledge_document_versions` | `SHARED_REFERENCE` | `can_insert = False` (SELECT only for `acrevia_staging_app`) | `WITH CHECK (is_admin() = 'true')` | Not Reached |
| `ingestion_jobs` | `TENANT_COLLABORATIVE` | `can_insert = True` | `WITH CHECK (created_by = current_user_id() OR current_role_in('AGRICULTURAL_EXPERT', 'RESEARCHER'))` | Not Reached |

### 11.4 Conclusion: Job Table Policy is Unreachable
The role-based write policy on `ingestion_jobs` is **completely unreachable via the service layer** because Step 1 flushes `KnowledgeDocument` to the database and aborts the transaction immediately. An external actor cannot exploit the ingestion job table policy without possessing administrative database authority.

### 11.5 Audit of `GET /api/v1/knowledge/jobs/{job_id}`
- Route relies on `get_current_user` with no role requirement.
- Service performs `db.get(IngestionJob, job_id)`.
- RLS read policy on `ingestion_jobs` allows read if `created_by = current_user_id() OR is_admin() = 'true' OR current_role_in('AGRICULTURAL_EXPERT', 'RESEARCHER')`.
- An expert or researcher can read any user's ingestion job status across the entire system.
- Returned fields include job status, document version ID, chunk counts, and error messages.

---

## 12. EXPERTCONNECT AND EXPERT REVIEW — COMPLETE SENSITIVE-DATA MATRIX

| Route Path & Method | Authentication | Route Role Gate | Service-Layer Gate | RLS Table Classification | RLS Expected Result | Final Determination |
|---|---|---|---|---|---|---|
| `GET /expertconnect/cases` | `get_current_user` | None | Checks role in body | `expert_review_cases` (`COLLABORATIVE`) | Returns assigned or unassigned cases | `SOURCE_PATH_PERMITS` |
| `POST /expertconnect/cases/{id}/claim` | `get_current_user` | `ADMIN`, `EXPERT` | Verifies case unassigned | `expert_review_cases` (`COLLABORATIVE`) | UPDATE allowed for expert | `SOURCE_PATH_PERMITS` |
| `GET /expertconnect/cases/{id}` | `get_current_user` | **NONE** | Fetches Case + Observation | `cases` (`COLLAB`), `obs` (`DIRECT`) | `obs` returns `None` under empty tenant | `RLS_FILTERS_ROW` |
| `POST /expertconnect/cases/{id}/assess` | `get_current_user` | `ADMIN`, `EXPERT` | Verifies assigned expert | `expert_assessments` (`COLLAB`) | INSERT allowed for assigned expert | `SOURCE_PATH_PERMITS` |
| `PUT /expertconnect/cases/{id}/assess` | `get_current_user` | `ADMIN`, `EXPERT` | Verifies assessment author | `expert_assessments` (`COLLAB`) | UPDATE allowed for author | `SOURCE_PATH_PERMITS` |
| `GET /expertconnect/cases/{id}/revisions` | `get_current_user` | **NONE** | Fetches revisions | `expert_assessment_revisions` (`COLLAB`) | RLS restricts to creator/expert | `RLS_FILTERS_ROW` |
| `POST /cases/create-from-observation/{id}` | `get_current_user` | **NONE** | Fetches Observation | `observations` (`TENANT_DIRECT`) | Observation returns `None` | `RLS_FILTERS_ROW` |
| `POST /diagnoses/{id}/expert-review` | `get_current_user` | `ADMIN`, `EXPERT` | Verifies diagnosis | `expert_reviews` (`COLLABORATIVE`) | INSERT allowed for expert | `SOURCE_PATH_PERMITS` |

### 12.1 Evaluation of Auth-Only Routes
Routes `GET /cases/{id}`, `GET /cases/{id}/revisions`, and `POST /cases/create-from-observation/{id}` lack `@require_roles` decorators. However:
- Under standard application execution with `acrevia_staging_app`, RLS filters out tenant records (`RLS_FILTERS_ROW`), causing the endpoints to return 404 or fail safely.
- **Conditional Critical Risk:** If deployed under an unconfined database principal (`neondb_owner`), RLS is bypassed, and these auth-only routes expose case dossiers and observation links across all tenants to any authenticated user.

---

## 13. GENERATED PRIVILEGE VS MIGRATION/BOOTSTRAP INVOCATION RECONCILIATION

### 13.1 The Deployment Call-Site Execution Gap (`SOURCE_CONFIRMED`)
In `backend/app/database/rls.py`, the codebase provides two distinct DDL generation functions:
1. `generate_rls_ddl()`: Generates `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`, `FORCE ROW LEVEL SECURITY`, and `CREATE POLICY ...`.
2. `generate_privilege_grants_ddl()`: Generates `REVOKE ALL`, `GRANT SELECT`, `GRANT INSERT`, etc., based on `PRIVILEGE_CROSSWALK`.

An exhaustive search across the entire migration history (`backend/migrations/versions/`) reveals:
- Migration `a1089411c87d_phase_07_rls_policies.py` explicitly calls `generate_rls_ddl()`.
- **`generate_privilege_grants_ddl()` is NEVER called by any migration file in the repository!**

```python
# backend/migrations/versions/a1089411c87d_phase_07_rls_policies.py:28-35
def upgrade() -> None:
    ddl_statements = generate_rls_ddl()
    for stmt in ddl_statements:
        op.execute(sa.text(stmt))
    # generate_privilege_grants_ddl() is completely omitted!
```

### 13.2 Evidence Classification: `LOCALLY_SPECIFIED_NEVER_EXECUTED_IN_MIGRATIONS`
Because the privilege grant DDL is never executed during migrations, the actual table permissions of the database user (`acrevia_staging_app`) depend entirely on manual out-of-band DBA scripts or PostgreSQL default privileges. 
- In Mode A, live database table privileges cannot be verified.
- The grant status for all tables is formally classified as **`LIVE_ACL_NOT_VERIFIED`**.

---

## 14. USER DELETION AND FK CASCADE THREAT PREREQUISITES

### 14.1 Analysis of `users` and `user_roles`
- In `TABLE_CLASSIFICATION`: `users` is `USER_DIRECT` and `user_roles` is `SYSTEM_PLATFORM`.
- Foreign Key: `user_roles.user_id` defines `REFERENCES users(id) ON DELETE CASCADE`.
- In `PRIVILEGE_CROSSWALK`: `acrevia_staging_app` is specified to receive `DELETE` on `users` and `user_roles`.
- In `generate_rls_ddl()`:
  `users_user_write_policy` allows UPDATE/DELETE where `id = current_user_id()`.

### 14.2 Attack Path Prerequisites
For an actor to trigger account deletion and cascade-delete assigned roles:
1. **Prerequisite 1:** The actor must execute arbitrary SQL or access a user deletion route.
2. **Prerequisite 2:** The database connection must possess `DELETE` privilege on `users` and `user_roles`.
3. **Prerequisite 3:** Session GUC `app.current_user_id` must match the target user ID (or RLS must be bypassed).
4. **Prerequisite 4:** No public REST API route in ACREVIA exposes an unvalidated user deletion endpoint.

### 14.3 Finding Classification: `SOURCE_PATH_CONDITIONAL`
The foreign key cascade is confirmed in ORM models, but it does **not constitute an externally reachable API exploit**. It represents an architectural integrity concern conditional on arbitrary SQL execution or session GUC hijacking.

---

## 15. CREDENTIAL AND EFFECTIVE-PRINCIPAL STATUS

### 15.1 Public Database Credential Exposure (`DB-CREDENTIAL-EXPOSURE-01`)
- **Status:** **`OPEN — CREDENTIAL_ROTATION_OUTSTANDING`**
- **Location:** Hardcoded fallback connection string in `frontend/lib/db.ts:16-19`.
- **Identity:** Direct connection string specifying user `neondb_owner` to a live Neon serverless PostgreSQL instance.
- **Exposure:** Committed to public repository history (`git rev-parse HEAD: c9e334d14110e8a6e4c9b71b89cae3294288af0d`).
- **Owner Action Required:** Immediate credential rotation in the Neon Cloud Console, purging git history via BFG Repo-Cleaner or git-filter-repo, and updating production environment secrets.

### 15.2 Effective Database Principal Reconciliation

| Subsystem | Configuration Source | Intended Runtime Principal | Fallback Principal in Source |
|---|---|---|---|
| Backend API | `backend/app/core/config.py:settings.DATABASE_URL` | `acrevia_staging_app` | `postgres` (local container) |
| Frontend Server | `frontend/lib/db.ts:process.env.DATABASE_URL` | `acrevia_staging_app` | `neondb_owner` (hardcoded Neon cloud URI) |
| Async Worker | `backend/app/database/session.py:SessionLocal` | `acrevia_staging_app` | Inherits backend `settings.DATABASE_URL` |
| Migrations | `backend/migrations/env.py` | Migration Administrator | Inherits backend `settings.DATABASE_URL` |

### 15.3 RLS Bypass Qualification
- `ADMIN_BYPASS_SQL` in `backend/app/database/rls.py:28-35`:
```sql
(
    (SELECT current_setting('app.is_admin', true)) = 'true'
    OR (SELECT SESSION_USER) = 'neondb_owner'
    OR (SELECT CURRENT_USER) = 'neondb_owner'
)
```
If a connection is opened using the exposed `neondb_owner` credentials, PostgreSQL table ownership and the literal role check in `ADMIN_BYPASS_SQL` **completely bypass all RLS policies across all tables**.

---

## 16. REQUIRED DECISION TABLE & OUTCOME TAXONOMY

### 16.1 Required Decision Table (12 Core Scenarios)

| Scenario | Application Route | Role Check | Service Guard | RLS Result | Grant Status | Final Determination |
|---|---|---|---|---|---|---|
| **Normal Regional Pulse POST** | `POST /api/v1/regional-pulse/signals` | `APPLICATION_ROLE_GATE_PASSES` | `SERVICE_GUARD_BLOCKS` (requires ≥3 distinct farms; lookups return 0) | `RLS_FILTERS_ROW` (observations/farms hidden under empty tenant) | `LIVE_ACL_NOT_VERIFIED` | `SERVICE_GUARD_BLOCKS` |
| **Official Advisory POST** | `POST /api/v1/regional-pulse/signals` | `APPLICATION_ROLE_GATE_PASSES` | `SERVICE_GUARD_BLOCKS` (line 76 checks `'ADMIN' in effective_roles`) | N/A (aborts before DB write) | `LIVE_ACL_NOT_VERIFIED` | `SERVICE_GUARD_BLOCKS` |
| **Regional Pulse GET list** | `GET /api/v1/regional-pulse/signals` | None (Public / Auth Read) | None (invokes revalidation & `db.commit()`) | `RLS_FILTERS_ROW` on evidence; permissive write allows UPDATE | `LIVE_ACL_NOT_VERIFIED` | `WRITE_ON_READ_MUTATION_POSSIBLE` |
| **Regional Pulse GET detail** | `GET /api/v1/regional-pulse/signals/{id}` | None (Public / Auth Read) | None (invokes revalidation & `db.commit()`) | `RLS_FILTERS_ROW` on evidence; permissive write allows UPDATE | `LIVE_ACL_NOT_VERIFIED` | `WRITE_ON_READ_MUTATION_POSSIBLE` |
| **Regional Pulse Recovery** | `POST /api/v1/regional-pulse/signals/{id}/recover` | `APPLICATION_ROLE_GATE_PASSES` | `SERVICE_GUARD_BLOCKS` (verified farms count 0 < 3 under empty tenant) | `RLS_FILTERS_ROW` (evidence lookups return None) | `LIVE_ACL_NOT_VERIFIED` | `SERVICE_GUARD_BLOCKS` |
| **Knowledge Source Registration** | `POST /api/v1/knowledge/sources` | `APPLICATION_ROLE_GATE_PASSES` | None | `RLS_WITH_CHECK_BLOCKS_WRITE` (requires `is_admin() = 'true'`) | `LIVE_ACL_NOT_VERIFIED` | `RLS_WITH_CHECK_BLOCKS_WRITE` |
| **Knowledge Document Ingestion** | `POST /api/v1/knowledge/ingest` | `APPLICATION_ROLE_GATE_PASSES` | None | `RLS_WITH_CHECK_BLOCKS_WRITE` (Step 1 flush fails on doc) | `TABLE_GRANT_BLOCKS` (crosswalk specifies SELECT only) | `TABLE_GRANT_BLOCKS` / `RLS_WITH_CHECK_BLOCKS_WRITE` |
| **Expert Case Listing** | `GET /api/v1/expertconnect/cases` | None (Auth-only) | Role check inside route | `SOURCE_PATH_PERMITS` (collaborative policy allows assigned/unassigned) | `LIVE_ACL_NOT_VERIFIED` | `SOURCE_PATH_PERMITS` |
| **Expert Dossier Retrieval** | `GET /api/v1/expertconnect/cases/{id}` | None (Auth-only) | Fetches Case + Observation | `RLS_FILTERS_ROW` (observation filtered out under empty tenant) | `LIVE_ACL_NOT_VERIFIED` | `RLS_FILTERS_ROW` / `SOURCE_PATH_CONDITIONAL` |
| **Expert Assessment Write** | `POST /api/v1/expertconnect/cases/{id}/assess` | `APPLICATION_ROLE_GATE_PASSES` | Verifies assigned expert | `SOURCE_PATH_PERMITS` (collaborative write permits assigned expert) | `LIVE_ACL_NOT_VERIFIED` | `SOURCE_PATH_PERMITS` |
| **Assessment Revision History Read** | `GET /api/v1/expertconnect/cases/{id}/revisions` | None (Auth-only) | Fetches revisions | `RLS_FILTERS_ROW` (collaborative read filters non-assigned users) | `LIVE_ACL_NOT_VERIFIED` | `RLS_FILTERS_ROW` |
| **User-Role Deletion Cascade** | Direct SQL (no REST route) | N/A (Arbitrary SQL prerequisite) | None in DB engine | `users` write permits `id = current_user_id()` | `LIVE_ACL_NOT_VERIFIED` | `SOURCE_PATH_CONDITIONAL` |

---

## 17. CORRECTED FINDING REGISTER

| Finding Identifier | Preliminary Claim / Prior Report | Confirmed Finding / Corrected Reality | Cause of Correction |
|---|---|---|---|
| `RES-PULSE-POST-REACHABILITY` | Self-selected experts can flood system with fake regional signals. | **BLOCKED BY SERVICE GUARD UNDER RLS.** Service requires ≥3 distinct farms; lookups return 0 under empty tenant GUC. | Multi-layer execution modeling through service guard and RLS filtering. |
| `RES-PULSE-OFFICIAL-ADVISORY` | Experts can issue unauthorized official government advisories. | **STRICTLY BLOCKED BY SERVICE GUARD.** Line 76 explicitly requires `ADMIN` role. | Exact code inspection of `RegionalPulseService.aggregate_regional_signal`. |
| `RES-PULSE-EVIDENCE-PRIVACY` | Cross-district viewing leaks raw farmer observations and PII. | **PRIVACY PRESERVED AT BOUNDARY.** Endpoint returns only association UUIDs/notes; underlying records remain RLS-isolated. | Inspection of ORM schema and `RegionalSignalResponse` serializer. |
| `KNOWLEDGE-INGEST-EXPLOIT` | Experts can spam malicious ingestion jobs. | **BLOCKED AT STEP 1 FLUSH.** `KnowledgeDocument` insertion aborts before `IngestionJob` write is attempted. | Tracing ordered database flush sequence in `IngestionService.ingest_document`. |
| `CASCADE-ROLE-DEL-01` | External API callers can delete user accounts and trigger role cascades. | **NO EXPOSED REST ENDPOINT.** Cascade exists in DB schema but requires arbitrary SQL execution prerequisite. | Comprehensive API manifest scan across all 214 endpoints. |
| `PRIVILEGE-GRANT-DEPLOYMENT` | PostgreSQL table privileges are governed by `PRIVILEGE_CROSSWALK`. | **GRANTS NEVER EXECUTED IN MIGRATIONS.** `generate_privilege_grants_ddl()` is never called in Alembic scripts. | Inspection of all Alembic migration versions in `backend/migrations/`. |

---

## 18. CANONICAL GOVERNANCE AND GATE STATUS

### 18.1 Preservation of Canonical Architecture Decisions
- **`D-01` (Regional Signal Visibility & Official Advisory Data Model):** Preserved. Official advisories require explicit state administrative authority; regional collaborative visibility is separated from raw farm data.
- **`D-02` (Source Authenticity & Pilot Terminology):** Preserved. Pilot terminology and multi-source provenance validation remain binding.
- **`D-03` (Independent Expert Review):** Preserved. Two-tier review and immutable audit trails remain standard.
- **`DB-AUTH-01` (Trusted Database Writer Identity):** Preserved. Demands dedicated non-shared database principals and rejects mutable client GUC role escalation.

### 18.2 Complete Blocker Register Status

| Blocker Identifier | Severity | Governance Category | Current Status | Resolution Gate |
|---|---|---|---|---|
| `DB-CREDENTIAL-EXPOSURE-01` | **CRITICAL** | Cloud Security / Credential Governance | **OPEN — OUTSTANDING** | `GATE-01` |
| `RLS-WRITE-AUTH-01` | **HIGH** | PostgreSQL RLS Architecture | **OPEN — REMEDIATION PLANNED (Option D)** | `GATE-02` |
| `RLS-ROLE-ASSIGNMENT-01` | **HIGH** | PostgreSQL Role Management | **OPEN — REMEDIATION PLANNED (Option B)** | `GATE-02` |
| `APP-ROLE-SELF-SELECT-01` | **HIGH** | Application Authentication Gateway | **OPEN — REMEDIATION REQUIRED** | `GATE-02` |
| `RES-PULSE-READ-01` (NEW) | **HIGH** | Data Integrity / Denial-of-Service | **OPEN — DEFECT CONFIRMED** | `GATE-02` |
| `GATE01-PROV-01` | **MEDIUM** | Migration / Privilege Provisioning | **OPEN — MIGRATION CALLSITE ABSENT** | `GATE-01` |
| `EXP-AUTH-01` | **MEDIUM** | Expert Authorization / Accreditation | **OPEN — ACCREDITATION DECOUPLED** | `GATE-03` |
| `CASCADE-ROLE-DEL-01` | **MEDIUM** | Relational Integrity | **MONITORED RESIDUAL RISK** | `GATE-02` |

### 18.3 Release Gate Status
- **`GATE-01` (Database Infrastructure & Credential Assurance):** **BLOCKED** (Pending Neon credential rotation and history purge).
- **`GATE-02` (PostgreSQL RLS Kernel Isolation & Policy Composition):** **BLOCKED** (Option D policy and write-on-read suppression remediation pending).
- **`GATE-03` (Application Authentication & Role Provisioning Gateway):** **BLOCKED** (Self-selection removal and researcher workflow pending).
- **`GATE-04` (Offline & Integration Test Verification):** **BLOCKED** (Integration tests for empty tenant context pending).
- **`GATE-05` (Mode B Authorization & Production Release):** **BLOCKED** (Cannot proceed until Gates 01-04 pass).

**Formal Phase 07 Status:** **`NOT RELEASED`**  
**Execution Authorization:** **`MODE A ONLY — MODE B NOT AUTHORIZED`**

---

## 19. REMEDIATION ARCHITECTURE RECOMMENDATIONS (WITHOUT IMPLEMENTATION)

1. **Eliminate Write-on-Read in Regional Pulse (`RES-PULSE-READ-01`):**  
   Remove `RegionalPulseService.revalidate_signal_provenance()` and `db.commit()` from `GET /signals` and `GET /signals/{signal_id}`. Revalidation must be decoupled into an asynchronous Celery background worker or executed within an administrative transaction that holds cross-tenant read privileges.

2. **Deploy Option D Fail-Closed Policies for `regional_signals`:**  
   Replace the permissive `FOR ALL` author policy with separate, explicit command policies:
   - `FOR SELECT`: Filter by `is_active = true` or author ownership.
   - `FOR INSERT`: Require verified author role and validate author ID against `current_user_id()`.
   - `FOR UPDATE`: Require explicit author ID match on both old (`USING`) and new (`WITH CHECK`) rows; revoke general role-based UPDATE.

3. **Close Registration Role Self-Selection (`APP-ROLE-SELF-SELECT-01`):**  
   Restrict `UserCreate.role` to `FARMER` only. Implement dedicated administrative role-provisioning endpoints requiring approval for `AGRICULTURAL_EXPERT` and `RESEARCHER`.

4. **Integrate Privilege Grants into Alembic Migrations (`GATE01-PROV-01`):**  
   Add `generate_privilege_grants_ddl()` calls into migration scripts to ensure table privileges are deployed alongside RLS policies.

5. **Implement Trusted Database Writer Identity (`DB-AUTH-01`):**  
   Transition from shared GUC-based identity to distinct PostgreSQL database roles or an authenticated connection proxy.

---

## 20. REMAINING UNKNOWNS AND MODE B EVIDENCE REQUIRED

The following items cannot be determined in Mode A and require verified Mode B evidence following credential rotation:

1. **Live Table Privileges:** Actual privileges granted to `acrevia_staging_app` on the Neon database instance (`pg_class`, `pg_roles`, `has_table_privilege`).
2. **Live RLS Activation:** Whether `rowsecurity` and `forcerowsecurity` are enabled on staging tables.
3. **Live RLS Kernel Policy Execution:** Verification of PostgreSQL policy evaluation behavior under active Neon serverless connections.
4. **Cloud Credential Invalidation:** Cryptographic confirmation that the exposed `neondb_owner` token is revoked and returns authentication failure.

---

## 21. EXACT SOURCE-FILE AND DELIVERABLE INVENTORY

### Deliverable Paths
- **Repository Audit Report:** `docs/pilot/security/PHASE_07_REGIONAL_PULSE_SERVICE_REACHABILITY_AND_POLICY_COMPOSITION_AUDIT.md`
- **Brain Artifact Mirror:** `C:\Users\gokul\.gemini\antigravity\brain\8d770357-1b73-48ca-9930-eded206539c2\PHASE_07_REGIONAL_PULSE_SERVICE_REACHABILITY_AND_POLICY_COMPOSITION_AUDIT.md`

### Source Files Inspected
- `backend/app/api/v1/router.py` (Master Router Assembly)
- `backend/app/api/v1/endpoints/*.py` (49 Router Modules, 214 Routes)
- `backend/app/main.py` (FastAPI Application Gateway, 3 Root Routes)
- `backend/app/api/v1/endpoints/regional_pulse.py` (Regional Pulse Endpoints)
- `backend/app/services/regional_pulse_service.py` (Signal Aggregation, Revalidation, Recovery)
- `backend/app/models/regional_pulse.py` (`RegionalSignal`, `RegionalSignalEvidence`)
- `backend/app/api/v1/endpoints/knowledge.py` (Knowledge Source & Ingestion Endpoints)
- `backend/app/services/knowledge/ingestion/ingestion_service.py` (Ordered Ingestion Pipeline)
- `backend/app/api/v1/endpoints/expertconnect.py` (ExpertConnect Case & Dossier Endpoints)
- `backend/app/services/expertconnect_service.py` (Case Claiming & Dossier Retrieval)
- `backend/app/database/rls.py` (Table Classification, `generate_rls_ddl`, `generate_privilege_grants_ddl`)
- `backend/migrations/versions/a1089411c87d_phase_07_rls_policies.py` (Alembic Policy Migration)
- `frontend/lib/db.ts` (Database Connection Constructor & Fallback String)
- `backend/app/services/auth_service.py` (Registration & Authentication Engine)
- `backend/app/security/dependencies.py` (JWT & GUC Context Dependencies)
