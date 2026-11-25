# ACREVIA — PHASE 07: FARMER-FACING PUBLICATION ELIGIBILITY, EVIDENCE-ASSOCIATION AUTHORIZATION & GET READ-BOUNDARY FINAL ASSURANCE AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India (33 Administrative Districts)  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** `MODE A ONLY` — Offline Source Inspection, Static PostgreSQL Policy Analysis, API Authorization Tracing, Transaction Modeling & Governance Documentation  
**Audit Standard:** Everything Claude Code (ECC) — `PLAN → INSPECT → TRACE → ADVERSARIAL REVIEW → VERIFY OFFLINE → DOCUMENT`  
**Public Repository:** `https://github.com/gokul1599/ACREVIA`  
**Verified Repository Baseline:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Target Deliverable:** `docs/pilot/security/PHASE_07_REGIONAL_PULSE_FARMER_VISIBILITY_AND_GET_READ_BOUNDARY_FINAL_ASSURANCE_REPORT.md`  
**Artifact Mirror:** `C:\Users\gokul\.gemini\antigravity\brain\8d770357-1b73-48ca-9930-eded206539c2\PHASE_07_REGIONAL_PULSE_FARMER_VISIBILITY_AND_GET_READ_BOUNDARY_FINAL_ASSURANCE_REPORT.md`  
**Authoritative Governance Register:** `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`  
**Release Recommendation:** `CONDITIONALLY_READY_FOR_OWNER_REVIEW`  

---

## 1. EXECUTIVE ASSURANCE CONCLUSION

This final assurance audit delivers an exhaustive, evidence-bound investigation into the farmer-facing read architecture of the ACREVIA Regional Pulse subsystem. Operating strictly under **MODE A ONLY** constraints (zero live database connections, zero cloud provisioning, zero credential manipulation, zero application code modification, and zero Git history alterations), this assessment resolves the critical boundaries separating:
1. **Database Row Visibility** (determined by PostgreSQL Row-Level Security policies).
2. **API Publication Eligibility** (determined by FastAPI application routes, status filters, and serialization masking).
3. **Evidence Relationship Visibility** (determined by child-table RLS and ORM relationship loading).
4. **Service Provenance Verification** (determined by algorithmic threshold checks and savepoint execution).
5. **Internal Verification Access** (which requires privileged database credentials to inspect child evidence rows).
6. **State Mutation & Transaction Ownership** (where GET read requests commit domain state changes).
7. **Owner-Approved Public Publication Policy** (governed by Project Owner Decisions D-01, D-02, D-03, and DB-AUTH-01).

### 1.1 Core Audit Breakthroughs & Findings
1. **Decoupling of Database RLS from API Publication Eligibility:**
   - The PostgreSQL public read policy on `regional_signals` (`distinct_farms_count >= 3 AND validation_status != 'SUSPENDED'`) **does not exclude `UNVALIDATED_OBSERVATION`**! If a community signal reaches $N \ge 3$, it is 100% visible at the database RLS layer, even prior to agronomic expert review.
   - The platform currently withholds unvalidated observations from farmers **only because of an accidental side-effect**: the farmer's session cannot read child evidence records due to child-table RLS, causing `revalidate_signal_provenance()` to experience a false-absence condition, return `False`, and prompt the API route to filter out the signal or return HTTP 404!
   - Neither PostgreSQL RLS nor the API route explicitly implements an owner-approved publication policy requiring expert review. Decision D-03 remains unimplemented as an intentional policy boundary.
2. **False Absence of Evidence & Write-on-Read Mechanics:**
   - In `backend/app/services/regional_pulse_service.py` (lines 338–341), `revalidate_signal_provenance()` interprets an empty evidence collection (`not signal.evidences`) as proof of insufficient provenance, staging `distinct_farms_count = 0` and `validation_status = "SUPPRESSED_INSUFFICIENT_PROVENANCE"`.
   - For ordinary farmers, child evidence rows are hidden by evidence-table RLS. The relationship loads as empty (`[]`). The service misinterprets privacy-isolated evidence as missing evidence.
   - When the farmer's savepoint exits, SQLAlchemy flushes the dirty entity. The update is rejected by PostgreSQL RLS (0 rows matched), raising `StaleDataError`. The savepoint context manager executes `ROLLBACK TO SAVEPOINT`, expunging the staged mutation and returning `False`. The outer route executes `db.commit()` on an untainted read session, returning HTTP 404 or filtering the signal (Outcome A: Read-Response Denial via Outcome B: Transient In-Memory Mutation).
   - For privileged users (Admin, Expert, Researcher), evidence is visible. However, if provenance genuinely fails on a privileged read, the savepoint flush succeeds and the outer route commits the suppression update to PostgreSQL (Outcome C: Persistent Write-on-Read Mutation / `RES-PULSE-READ-01`).
3. **Official State Advisory Blind Spot (Decision D-01):**
   - Official state alerts published with `confidence_tier = 'OFFICIAL_ADVISORY'`, `validation_status = 'OFFICIAL_ALERT'`, and `distinct_farms_count = 0` are completely hidden from farmers at the database layer because PostgreSQL public read RLS requires `distinct_farms_count >= 3`.
   - Without an owner-authorized public exception under Decision D-01, farmers can never read official alerts.
4. **Correction of Errata Governance Errors:**
   - The previous errata report contained factual inaccuracies regarding the governance register: it mischaracterized GATE-02, GATE-03, and GATE-04, and asserted that GATE-01 remains pending approval.
   - This audit corrects the record: **GATE-01 was formally approved by the Project Owner on 10 November 2026**. GATE-02 (create role `acrevia_staging_app`), GATE-03 (execute migration `a1089411c87d`), GATE-04 (run verification harness `verify_staging_rls.py`), and GATE-05 (teardown schedule) remain pending owner sign-off.
   - MODE B execution remains unauthorized because GATE-02 through GATE-05 and Decisions D-01 through D-03 remain uncompleted prerequisites.
5. **Privilege Hardening Reconciliation:**
   - The previous report's recommendation to revoke `UPDATE` from `acrevia_staging_app` on `regional_signals` would break legitimate service operations (provenance count adjustments, suppression, administrative recovery, and validation transitions).
   - This audit delivers a safe, least-privilege architecture: revoke `DELETE` and `UPDATE` on `regional_signal_evidences` (strictly append-only child table), revoke `DELETE` on `regional_signals`, and retain `UPDATE` on `regional_signals` bounded by column-level grants or command-scoped `FOR UPDATE` RLS policies.

---

## 2. PUBLIC AND LOCAL REPOSITORY BASELINE

### 2.1 Public Repository State
- **Repository URL:** `https://github.com/gokul1599/ACREVIA`
- **Tracked Branch:** `main`
- **Public Baseline Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d`
- **Verification Status:** `PUBLIC_SOURCE_VERIFIED`. Public tree reflects the exact Phase 07 baseline.

### 2.2 Local Workspace and Working Tree Status
- **Workspace Path:** `c:\Users\gokul\OneDrive\Documents\projects`
- **Active Git Branch:** `main`
- **Local HEAD Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d`
- **Divergence:** Exactly **0 commits divergence** (`HEAD` is synchronized with `origin/main`).
- **Application Source Integrity:** Exactly **0 application source files, models, schemas, services, migrations, or test files modified**.
- **Tracked Governance Modifications:** 7 historical Phase 07 planning and decision matrices in `docs/pilot/security/`.
- **Untracked Historical Deliverables:** 11 historical assurance reports preserved non-destructively in `docs/pilot/security/`, including the newly generated `PHASE_07_REGIONAL_PULSE_ASSURANCE_ERRATA_AND_FINDING_RECLASSIFICATION_REPORT.md`.

---

## 3. EXISTING REPORT RECONCILIATION

The audit reconciled the entire sequence of prior assurance deliverables:

1. **`PHASE_07_REGIONAL_PULSE_STATUS_CONTRACT_AND_EVIDENCE_RETENTION_DESIGN_ASSURANCE_REPORT.md` (Untracked):**
   - Established the initial discovery of FK cascade deletion risks and write-on-read suppression.
   - Overclaimed that `'PUBLISHED'` was nonexistent project-wide and that public read predicates would deny 100% of all database rows.
2. **`PHASE_07_REGIONAL_PULSE_ASSURANCE_ERRATA_AND_FINDING_RECLASSIFICATION_REPORT.md` (Untracked):**
   - Successfully corrected the vocabulary finding (`SEC-P07-STATUS-01` -> `PROPOSED_DESIGN_INCOMPATIBILITY`), narrowed FK cascade mechanics, and withdrew the unsupported causal link between GATE-01 and credential rotation.
   - *Errata Identified by Current Audit:* Inaccurately mapped GATE-02 as "migration verification", GATE-03 as "privilege hardening", and GATE-04 as "read-privacy UAT", and incorrectly implied that GATE-01 required approval. Furthermore, its recommendation to blanket-revoke `UPDATE` on `regional_signals` would break legitimate application service workflows.
3. **`PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md` (Tracked):**
   - Authoritative source for gate scopes. Confirms GATE-01 approved on 2026-11-10; GATE-02 through GATE-05 unchecked. Contains an unresolved branch-identity ambiguity between `staging-rls-phase07` (lines 28, 59) and `staging-rls-phase05` (lines 20, 32).
4. **`phase_07_owner_decision_evidence_traceability_matrix.md` & `PHASE_07_REGIONAL_PULSE_PROJECT_OWNER_DECISION_RECORD.md` (Tracked):**
   - Confirm Decisions D-01, D-02, D-03, and DB-AUTH-01 remain formally `PENDING_OWNER_SIGN_OFF`.

---

## 4. EVIDENCE CLASSIFICATION METHODOLOGY

Every material finding in this report is assigned a formal classification standard:

| Classification | Meaning & Standard of Evidence |
|---|---|
| `PUBLIC_SOURCE_VERIFIED` | Evidenced directly in public commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d`. |
| `LOCAL_SOURCE_VERIFIED` | Evidenced directly in the local workspace working tree without public divergence. |
| `LOCAL_TEST_VERIFIED` | Verified via safe offline AST analysis or static Python inspection. |
| `POSTGRESQL_SPECIFICATION_VERIFIED` | Verified against PostgreSQL 15/16 engine source code (`ri_triggers.c`, `rowsecurity.c`) and official documentation. |
| `SQLALCHEMY_BEHAVIOR_VERIFIED` | Verified against SQLAlchemy 2.0 Unit of Work and `Session.begin_nested()` specification. |
| `SOURCE_INFERENCE` | Deduced logically from code structure, schema foreign keys, and API route parameters. |
| `CONDITIONAL_RUNTIME_RISK` | A risk dependent on unverified live catalog state, database grants, or session GUCs. |
| `LIVE_DATABASE_UNVERIFIED` | State requiring remote Neon Cloud catalog inspection; strictly prohibited in Mode A. |
| `OWNER_DECISION_REQUIRED` | Policy or architectural choice reserved exclusively for Project Owner governance sign-off. |
| `PROPOSED_DESIGN` | Architectural or schema design option; not currently implemented in baseline code. |

---

## 5. COMPLETE REGIONAL PULSE AUTHORIZATION-LAYER ARCHITECTURE

The Regional Pulse subsystem does not operate under a single monolithic access control check. An incoming HTTP request traverses **eight distinct authorization, privacy, and transaction layers**:

```
[Client HTTP Request]
       |
       v
Layer 1: Authenticated API Access (FastAPI Depends(get_current_user) / JWT Validation)
       |
       v
Layer 2: API Role Authorization (FastAPI Depends(require_roles) / Route Guards)
       |
       v
Layer 3: Database SQL Privileges (PostgreSQL Table-Level Grants: SELECT, INSERT, UPDATE, DELETE)
       |
       v
Layer 4: PostgreSQL RLS Row Eligibility (Parent Table 'regional_signals' USING Predicates)
       |
       v
Layer 5: Relationship & Evidence Visibility (Child Table 'regional_signal_evidences' RLS)
       |
       v
Layer 6: Service-Layer Provenance Verification (RegionalPulseService.revalidate_signal_provenance)
       |
       v
Layer 7: API Response Filtering & Masking (Pydantic Serialization & Evidence Strip)
       |
       v
Layer 8: Transactional State Changes & Commit Ownership (Savepoint Rollback vs Outer db.commit())
       |
       v
[Client HTTP Response]
```

### 5.1 Capability Matrix Across the Eight Authorization Layers

| Layer | Component | Governed Rules & Mechanisms | Ordinary Farmer Capability | Agricultural Expert / Researcher | Application ADMIN |
|---|---|---|---|---|---|
| **1. Authenticated API** | `backend/app/api/deps.py` | JWT bearer token verification; extracts `user_id`. | Permitted (authenticated). | Permitted (authenticated). | Permitted (authenticated). |
| **2. API Route Guard** | `endpoints/regional_pulse.py` | `require_roles` on mutations; open GET routes. | Allowed on GET; blocked on POST `/signals` & `/recover`. | Allowed on GET, POST `/signals`, POST `/recover` (Expert). | Allowed on all endpoints. |
| **3. Database Grants** | PostgreSQL Table ACL | `PRIVILEGE_CROSSWALK` table grants for `acrevia_staging_app`. | Bound to application role grants (SELECT, INSERT, UPDATE granted; DELETE denied). | Bound to application role grants. | Bound to application role grants (or bypass). |
| **4. Parent RLS** | `database/rls.py` (L901) | `regional_signals` public read policy vs `FOR ALL` policy. | Eligible ONLY if $N \ge 3$ AND status $\ne$ `'SUSPENDED'`. | Eligible for ALL rows via `author_write_policy` (`FOR ALL`). | Eligible for ALL rows (Admin bypass). |
| **5. Child Evidence RLS**| `database/rls.py` (L910) | `regional_signal_evidences` public read policy. | **DENIED (0 rows visible)**. Child table restricted to Admin/Expert/Researcher. | **ELIGIBLE**. Can SELECT child evidence rows. | **ELIGIBLE**. Can SELECT child evidence rows. |
| **6. Provenance Service** | `regional_pulse_service.py` | Evaluates `signal.evidences`; requires $N \ge 3$. | **FAILS CLOSED**. Empty evidence triggers false-absence suppression. | **EVALUATED ACCURATELY**. Evidence loaded and farm IDs counted. | **EVALUATED ACCURATELY** (or bypassed if Official Advisory). |
| **7. Response Filtering**| `endpoints/regional_pulse.py` | Route status check & Pydantic evidence masking. | Filtered if revalidation fails or suppressed; evidences stripped (`[]`). | Receives full data including evidence metadata. | Receives full data including evidence metadata. |
| **8. Transaction State** | `endpoints` & `SessionLocal` | Savepoint flush vs outer `db.commit()`. | Update flush blocked by RLS (`StaleDataError`); rolled back cleanly. | Update flush succeeds; outer route **commits persistent mutation**. | Update flush succeeds; outer route commits mutation. |

---

## 6. PARENT RLS POLICY COMPOSITION

### 6.1 Policy Composition Mechanics in PostgreSQL
In `backend/app/database/rls.py` (lines 901–968), the generated DDL creates two policies on the parent table `regional_signals`:

1. **Public Read Policy (`regional_signals_public_read_policy`):**
   ```sql
   CREATE POLICY regional_signals_public_read_policy ON regional_signals
       AS PERMISSIVE
       FOR SELECT
       TO PUBLIC
       USING (
           app.is_admin = 'true'
           OR (
               distinct_farms_count >= 3
               AND validation_status != 'SUSPENDED'
           )
       );
   ```
2. **Author Write Policy (`regional_signals_author_write_policy`):**
   ```sql
   CREATE POLICY regional_signals_author_write_policy ON regional_signals
       AS PERMISSIVE
       FOR ALL
       TO PUBLIC
       USING (
           app.is_admin = 'true'
           OR (
               current_setting('app.current_user_id', true) != ''
               AND EXISTS (
                   SELECT 1 FROM user_roles ur
                   WHERE ur.user_id::text = current_setting('app.current_user_id', true)
                   AND ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')
               )
           )
       )
       WITH CHECK ( ... );
   ```

Under PostgreSQL row security mechanics (`src/backend/rewrite/rowsecurity.c`):
- Both policies are declared `AS PERMISSIVE`. When multiple permissive policies apply to the same command, they are combined with **logical OR**:
  $$\text{Row Eligible for SELECT} = \text{public\_read\_policy.USING} \lor \text{author\_write\_policy.USING}$$
- A policy declared `FOR ALL` applies to all SQL commands: `SELECT`, `INSERT`, `UPDATE`, and `DELETE`.
- Therefore, for any actor possessing an active role in `('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')`, `author_write_policy.USING` evaluates to `TRUE` during a `SELECT` statement, granting cross-district, cross-status row eligibility across the entire table.

### 6.2 Critical Status Questions Answered
1. **Can `UNVALIDATED_OBSERVATION` with $N \ge 3$ pass parent SELECT RLS?**  
   **YES.** The public read policy requires only `distinct_farms_count >= 3 AND validation_status != 'SUSPENDED'`. Because `'UNVALIDATED_OBSERVATION' != 'SUSPENDED'` evaluates to `TRUE`, any community observation meeting the farm threshold passes parent SELECT RLS unconditionally.
2. **Can `SUPPRESSED_INSUFFICIENT_PROVENANCE` with $N \ge 3$ pass parent SELECT RLS?**  
   **YES.** If a suppressed row maintains $N \ge 3$ in the database column, it passes parent SELECT RLS because `'SUPPRESSED_INSUFFICIENT_PROVENANCE' != 'SUSPENDED'` is `TRUE`. The RLS policy does not explicitly check for suppression.
3. **Does the policy explicitly reject `SUSPENDED`?**  
   **YES.** Both the public read policy and baseline tests explicitly enforce `validation_status != 'SUSPENDED'`. Rows in `'SUSPENDED'` are denied to ordinary farmers.
4. **Does it explicitly reject `OFFICIAL_ALERT` with $N = 0$ for ordinary farmers?**  
   **YES.** For ordinary farmers, the public read policy evaluates `distinct_farms_count >= 3`. Since $0 \ge 3$ evaluates to `FALSE`, official state alerts with zero plot telemetry are completely blocked from farmer SELECT queries at the database layer.
5. **Can researchers and experts pass the parent SELECT policy below threshold through the `FOR ALL` branch?**  
   **YES.** The `FOR ALL` policy applies to `SELECT` and contains no farm count or validation status predicate. Privileged actors receive 100% row eligibility across all signals.
6. **Does the parent policy enforce district isolation for internal privileged readers?**  
   **NO.** Neither policy contains a district predicate (e.g. `district_id = current_setting(...)`). Privileged actors receive statewide visibility across all 33 districts of Telangana (`RES-PULSE-01`).

---

## 7. PARENT RLS TRUTH TABLE

The following truth table evaluates parent table PostgreSQL RLS SELECT eligibility across all valid lifecycle statuses, farm counts ($N$), and actor identities:

| Validation Status | $N$ | Farmer RLS SELECT | Researcher RLS SELECT | Expert RLS SELECT | Application Admin | Reason & SQL Mechanics |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `UNVALIDATED_OBSERVATION` | 0 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; privileged pass via `FOR ALL` role branch. |
| `UNVALIDATED_OBSERVATION` | 1 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; privileged pass via `FOR ALL` role branch. |
| `UNVALIDATED_OBSERVATION` | 2 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; privileged pass via `FOR ALL` role branch. |
| `UNVALIDATED_OBSERVATION` | 3 | **TRUE** | **TRUE** | **TRUE** | **TRUE** | Farmer passes: $3 \ge 3$ and status $\ne$ `'SUSPENDED'`. |
| `UNVALIDATED_OBSERVATION` | >3 | **TRUE** | **TRUE** | **TRUE** | **TRUE** | Farmer passes: $N \ge 3$ and status $\ne$ `'SUSPENDED'`. |
| `EXPERT_CONFIRMED` | 0 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; privileged pass via `FOR ALL`. |
| `EXPERT_CONFIRMED` | 1 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; privileged pass via `FOR ALL`. |
| `EXPERT_CONFIRMED` | 2 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; privileged pass via `FOR ALL`. |
| `EXPERT_CONFIRMED` | 3 | **TRUE** | **TRUE** | **TRUE** | **TRUE** | Legitimate verified community signal; farmer passes. |
| `EXPERT_CONFIRMED` | >3 | **TRUE** | **TRUE** | **TRUE** | **TRUE** | Legitimate verified community signal; farmer passes. |
| `ADMIN_CONFIRMED` | 0 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; privileged pass via `FOR ALL`. |
| `ADMIN_CONFIRMED` | 1 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; privileged pass via `FOR ALL`. |
| `ADMIN_CONFIRMED` | 2 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; privileged pass via `FOR ALL`. |
| `ADMIN_CONFIRMED` | 3 | **TRUE** | **TRUE** | **TRUE** | **TRUE** | Legitimate admin-recovered signal; farmer passes. |
| `ADMIN_CONFIRMED` | >3 | **TRUE** | **TRUE** | **TRUE** | **TRUE** | Legitimate admin-recovered signal; farmer passes. |
| `OFFICIAL_ALERT` | 0 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | **Critical Defect (D-01):** Farmer denied because $0 < 3$. |
| `OFFICIAL_ALERT` | 1 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; privileged pass via `FOR ALL`. |
| `OFFICIAL_ALERT` | 2 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; privileged pass via `FOR ALL`. |
| `OFFICIAL_ALERT` | 3 | **TRUE** | **TRUE** | **TRUE** | **TRUE** | Farmer passes $N \ge 3$; privileged pass via `FOR ALL`. |
| `OFFICIAL_ALERT` | >3 | **TRUE** | **TRUE** | **TRUE** | **TRUE** | Farmer passes $N \ge 3$; privileged pass via `FOR ALL`. |
| `SUPPRESSED_INSUFFICIENT_PROVENANCE` | 0 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; privileged pass via `FOR ALL`. |
| `SUPPRESSED_INSUFFICIENT_PROVENANCE` | 1 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; privileged pass via `FOR ALL`. |
| `SUPPRESSED_INSUFFICIENT_PROVENANCE` | 2 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer fails $N \ge 3$; privileged pass via `FOR ALL`. |
| `SUPPRESSED_INSUFFICIENT_PROVENANCE` | 3 | **TRUE** | **TRUE** | **TRUE** | **TRUE** | **RLS Leak:** Farmer passes because $N \ge 3$ and status $\ne$ `'SUSPENDED'`. |
| `SUPPRESSED_INSUFFICIENT_PROVENANCE` | >3 | **TRUE** | **TRUE** | **TRUE** | **TRUE** | **RLS Leak:** Farmer passes because $N \ge 3$ and status $\ne$ `'SUSPENDED'`. |
| `SUSPENDED` | 0 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer denied by status predicate; privileged pass via `FOR ALL`. |
| `SUSPENDED` | 1 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer denied by status predicate; privileged pass via `FOR ALL`. |
| `SUSPENDED` | 2 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer denied by status predicate; privileged pass via `FOR ALL`. |
| `SUSPENDED` | 3 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer denied by status predicate; privileged pass via `FOR ALL`. |
| `SUSPENDED` | >3 | **FALSE** | **TRUE** | **TRUE** | **TRUE** | Farmer denied by status predicate; privileged pass via `FOR ALL`. |

---

## 8. API PUBLICATION ELIGIBILITY TRUTH TABLE

While the database RLS layer governs row selection, the application layer imposes additional route guards, dynamic provenance revalidation, status filters, and response masking:

| Signal Status | $N$ | Parent RLS Eligible? | Dynamic Revalidation Outcome | Farmer API List Outcome | Farmer API Detail Outcome | Privileged API Outcome | Governing Factor |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `UNVALIDATED_OBSERVATION` | $N < 3$ | **NO** | Not reached (RLS hides parent row) | Excluded (Not in query) | HTTP 404 (Not found) | Visible (via `FOR ALL`) | Blocked by PostgreSQL RLS. |
| `UNVALIDATED_OBSERVATION` | $N \ge 3$ | **YES** | **FAILS (False Absence)** | **Excluded** (`not is_valid`) | **HTTP 404** (`not is_valid`) | **Visible** (Evidences verified) | **Accidental Block:** Evidence RLS triggers false absence. |
| `EXPERT_CONFIRMED` | $N < 3$ | **NO** | Not reached (RLS hides parent row) | Excluded | HTTP 404 | Visible (Full detail) | Blocked by PostgreSQL RLS. |
| `EXPERT_CONFIRMED` | $N \ge 3$ | **YES** | **FAILS for Farmer** | **Excluded** (`not is_valid`) | **HTTP 404** (`not is_valid`) | **Visible** (Full detail) | **Defect:** Farmer denied legitimate signal due to false absence! |
| `ADMIN_CONFIRMED` | $N < 3$ | **NO** | Not reached (RLS hides parent row) | Excluded | HTTP 404 | Visible (Full detail) | Blocked by PostgreSQL RLS. |
| `ADMIN_CONFIRMED` | $N \ge 3$ | **YES** | **FAILS for Farmer** | **Excluded** (`not is_valid`) | **HTTP 404** (`not is_valid`) | **Visible** (Full detail) | **Defect:** Farmer denied recovered signal due to false absence! |
| `OFFICIAL_ALERT` | $N = 0$ | **NO** | **PASSES** (Tier check bypasses) | **Excluded (RLS query empty)**| **HTTP 404 (RLS query empty)**| **Visible** (Full detail) | **Decision D-01:** RLS blocks farmer read despite valid alert! |
| `OFFICIAL_ALERT` | $N \ge 3$ | **YES** | **PASSES** (Tier check bypasses) | **Visible** (Evidence stripped) | **Visible** (Evidence stripped) | **Visible** (Full detail) | Legitimate alert visible to all. |
| `SUPPRESSED_INSUFFICIENT...`| $N < 3$ | **NO** | Not reached (RLS hides row) | Excluded | HTTP 404 | Visible (Full detail) | Blocked by PostgreSQL RLS. |
| `SUPPRESSED_INSUFFICIENT...`| $N \ge 3$ | **YES** | Fails ($N=0$ staged) | **Excluded (Route filter)** | **HTTP 404 (Route filter)** | **Visible** (Full detail) | Filtered by API status check (`L89`, `L140`). |
| `SUSPENDED` | Any | **NO** | Not reached (RLS hides row) | Excluded | HTTP 404 | Visible (Full detail) | Blocked by PostgreSQL RLS. |

---

## 9. UNVALIDATED-SIGNAL VISIBILITY ASSESSMENT (DECISION D-03)

### 9.1 Deconstruction of Current Behavior
A critical question in this audit is whether community-aggregated signals ($N \ge 3$) that remain in `validation_status = 'UNVALIDATED_OBSERVATION'` are intentionally withheld from farmers pending agronomic peer review under **Decision D-03**, or whether their exclusion is accidental:

1. **Database RLS Check:**
   In PostgreSQL, the row satisfies `distinct_farms_count >= 3 AND validation_status != 'SUSPENDED'`. The row **is selected and returned to the application**.
2. **API Route Status Filter Check:**
   In `backend/app/api/v1/endpoints/regional_pulse.py`:
   - Line 89 (`list_signals`): `if sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE" and not is_privileged: continue`
   - Line 140 (`get_signal`): `if (not is_valid or sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE") and not is_privileged: raise HTTPException(404)`
   Notice that the route status filter **does not filter out `UNVALIDATED_OBSERVATION`**!
3. **The Accidental Exclusion Mechanism:**
   The unvalidated observation is filtered out **only because** line 86 / line 125 executes `RegionalPulseService.revalidate_signal_provenance(db, sig.id)`. In that helper:
   - The query attempts to inspect `signal.evidences`.
   - Child-table RLS denies the farmer SELECT access to `regional_signal_evidences`.
   - `signal.evidences` is loaded as an empty list (`[]`).
   - The service hits line 338: `if not signal.evidences: return False`.
   - Because `is_valid` is `False`, line 87 skips the signal and line 140 raises HTTP 404!

### 9.2 Audit Finding
The withholding of unvalidated observations from farmers is **NOT an intentional enforcement of Decision D-03**. It is an accidental side-effect of evidence-association RLS triggering a false-absence failure in dynamic provenance revalidation!

If the write-on-read revalidation logic were removed from GET routes (as previously recommended), or if provenance were evaluated using a trusted aggregate count, **unvalidated observations ($N \ge 3$) would immediately leak into farmer responses**, directly violating Decision D-03!

To safely implement Decision D-03, the policy must be enforced explicitly at both layers:
- At the PostgreSQL RLS layer: `validation_status IN ('EXPERT_CONFIRMED', 'ADMIN_CONFIRMED', 'OFFICIAL_ALERT')`.
- At the API layer: an explicit filter rejecting unvalidated observations for non-privileged users.

---

## 10. SUPPRESSED-SIGNAL VISIBILITY ASSESSMENT

### 10.1 Suppression Row State ($N < 3$ vs. $N \ge 3$)
When `RegionalPulseService.revalidate_signal_provenance()` suppresses a signal, it sets:
- `signal.distinct_farms_count = current_count` (which is $< 3$, typically $0$).
- `signal.validation_status = "SUPPRESSED_INSUFFICIENT_PROVENANCE"`.

Under normal circumstances, where $N < 3$, the suppressed signal is blocked by PostgreSQL public read RLS because $0 \ge 3$ evaluates to `FALSE`.

### 10.2 The High-N Suppression Anomaly ($N \ge 3$)
However, consider a signal where an administrator or direct SQL query sets `validation_status = "SUPPRESSED_INSUFFICIENT_PROVENANCE"` while preserving `distinct_farms_count = 3` (e.g., manual suppression due to data quality disputes without zeroing farm counts):
- **Database RLS Layer:** The row satisfies `distinct_farms_count >= 3` and `'SUPPRESSED...' != 'SUSPENDED'`. The row **is returned by PostgreSQL SELECT**!
- **API Gateway Layer:** The route explicitly filters `sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"`. The API hides the record.

**Architectural Risk:** The suppression status is enforced **only at the API application layer**, not at the PostgreSQL RLS layer! Any direct database connection or internal query bypassing the FastAPI route will expose suppressed signals to unprivileged readers. PostgreSQL RLS must be updated to explicitly include `validation_status != 'SUPPRESSED_INSUFFICIENT_PROVENANCE'`.

---

## 11. OFFICIAL ADVISORY VISIBILITY ASSESSMENT (DECISION D-01)

### 11.1 The Official State Alert Paradox
State-level agricultural advisories issued by government authorities (e.g. Telangana Department of Agriculture) do not originate from farm plot telemetry. They represent broadcast alerts (pest swarms, cyclone warnings, heatwave alerts) where:
- `confidence_tier = 'OFFICIAL_ADVISORY'`
- `validation_status = 'OFFICIAL_ALERT'`
- `distinct_farms_count = 0`

### 11.2 Multi-Layer Conflict Analysis
1. **Service Revalidation Layer:**
   In `RegionalPulseService.revalidate_signal_provenance()` (lines 335–336):
   ```python
   if signal.confidence_tier == "OFFICIAL_ADVISORY":
       return True
   ```
   The service layer explicitly recognizes the validity of official advisories with $N = 0$ and returns `True`.
2. **API Route Layer:**
   The route receives `is_valid == True` and `validation_status == "OFFICIAL_ALERT"`. The API route logic permits the alert to be returned to farmers.
3. **Database RLS Layer (The Blocker):**
   When the farmer's session issues `SELECT FROM regional_signals`:
   The public read policy evaluates:
   $$(0 \ge 3) \land (\text{'OFFICIAL\_ALERT'} \ne \text{'SUSPENDED'}) \implies \mathbf{FALSE}$$
   PostgreSQL RLS filters out the row entirely!
   `query_signals()` returns an empty list, and `get_signal()` raises HTTP 404!

### 11.3 Governance Impact (Decision D-01)
Ordinary farmers in Telangana **can never view official government agricultural advisories** under the current database policy! 

To resolve this, Project Owner sign-off on **Decision D-01** is required to approve an explicit exception in the PostgreSQL RLS public read policy:
```sql
CREATE POLICY regional_signals_public_read_policy ON regional_signals
    AS PERMISSIVE FOR SELECT TO PUBLIC
    USING (
        app.is_admin = 'true'
        OR (distinct_farms_count >= 3 AND validation_status NOT IN ('SUSPENDED', 'SUPPRESSED_INSUFFICIENT_PROVENANCE'))
        OR (validation_status = 'OFFICIAL_ALERT' AND confidence_tier = 'OFFICIAL_ADVISORY' AND distinct_farms_count = 0)
    );
```

---

## 12. EVIDENCE-ASSOCIATION RLS ANALYSIS

### 12.1 Child Table Policy Definition
In `backend/app/database/rls.py` (lines 908–920), the public read policy for `regional_signal_evidences` is defined as:
```sql
CREATE POLICY regional_signal_evidences_public_read_policy ON regional_signal_evidences
    AS PERMISSIVE
    FOR SELECT
    TO PUBLIC
    USING (
        app.is_admin = 'true'
        OR (
            current_setting('app.current_user_id', true) != ''
            AND EXISTS (
                SELECT 1 FROM user_roles ur
                WHERE ur.user_id::text = current_setting('app.current_user_id', true)
                AND ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')
            )
        )
    );
```
Under this policy, when an ordinary farmer queries `regional_signal_evidences`, the subquery evaluates to `FALSE`. PostgreSQL returns **0 rows**.

### 12.2 Distinguishing Five Distinct Evidence States
A sound security architecture must differentiate between five fundamentally distinct states of evidence associations:

| State Identifier | State Name | Physical Database Reality | Application In-Memory View | Current Service Interpretation | Required Architectural Treatment |
|---|---|---|---|---|---|
| **State 1** | **True Absence** | 0 evidence rows exist in `regional_signal_evidences`. | `signal.evidences == []` | Treated as insufficient provenance ($N=0$). | Correctly suppressed as unverified. |
| **State 2** | **Privacy Invisibility** | Evidence rows exist, but are filtered by child RLS. | `signal.evidences == []` | **Falsely treated as State 1 ($N=0$).** | **Architectural Flaw:** Must NOT trigger suppression on read! |
| **State 3** | **Referential Invalidity** | Evidence rows exist, but referenced observation/alert was deleted or archived. | `ev.evidence_reference_id` points to missing entity. | Observation loop skips entity; farm count decremented. | Correctly suppressed if active $N < 3$. |
| **State 4** | **Verification Failure** | Evidence rows exist, but fail date window or district boundaries. | Entities loaded, but cross-district check fails. | Observation loop skips entity; farm count decremented. | Correctly suppressed if active $N < 3$. |
| **State 5** | **Unloaded / Stale** | Evidence rows exist, but relationship was not eagerly loaded by ORM query. | `signal.evidences` raises `DetachedInstanceError` or is unpopulated. | Triggers lazy load or raises unhandled error. | Must be loaded via trusted service session. |

Under the current architecture, the application layer **cannot distinguish State 1 from State 2**. An ordinary farmer is presented with an empty collection in both cases, causing the platform to mistake privacy-enforced filtering for a collapse in signal provenance.

---

## 13. FALSE-EVIDENCE-ABSENCE ANALYSIS

### 13.1 Service-Layer Suppression Logic
In `backend/app/services/regional_pulse_service.py` (lines 338–341):
```python
if not signal.evidences:
    signal.distinct_farms_count = 0
    signal.validation_status = "SUPPRESSED_INSUFFICIENT_PROVENANCE"
    return False
```
When this logic executes within a farmer's session, `signal.evidences` is empty because of child-table RLS (State 2). The service immediately executes this branch, staging a destructive suppression mutation in the session.

### 13.2 Response Masking vs. Database-Level Isolation
The platform employs two separate mechanisms to protect farmer anonymity:
1. **Application-Layer Response Masking:**
   In `backend/app/api/v1/endpoints/regional_pulse.py` (lines 51–52, 93–94, 147–148):
   ```python
   if not is_privileged:
       sig_data.evidences = []
   ```
   This strips evidence metadata from the Pydantic serialization model before returning the JSON payload to the client.
2. **Database-Layer RLS Isolation:**
   PostgreSQL RLS on `regional_signal_evidences` prevents raw evidence records from ever being read by an unprivileged database connection.

**Key Insight:** Application response masking is sufficient to protect farmer privacy in HTTP responses. However, because child-table RLS was also applied to the shared database session used by the service layer, the service layer was starved of the evidence rows it needed to verify the signal! 

The solution is not to remove child-table RLS (which would risk leaking evidence via direct SQL), but to **decouple provenance revalidation from the farmer's unprivileged read session**.

---

## 14. FARMER GET LIST/DETAIL EXECUTION TRACE

### 14.1 Detailed Execution Trace (Farmer Session)

$$\begin{aligned}
\textbf{Step 1: HTTP Request} &\longrightarrow \text{Farmer issues } \texttt{GET /api/v1/regional-pulse/signals/sig\_123} \\
\textbf{Step 2: Authentication} &\longrightarrow \texttt{get\_current\_user} \text{ validates JWT; sets GUC } \texttt{app.current\_user\_id = 'farmer\_456'} \\
\textbf{Step 3: Parent SELECT} &\longrightarrow \texttt{db.get(RegionalSignal, 'sig\_123')} \text{ executes in PostgreSQL.} \\
&\quad \text{Parent RLS: } \texttt{distinct\_farms\_count = 3} \ge 3 \implies \mathbf{PASSED} \text{ (Signal loaded in memory)} \\
\textbf{Step 4: Revalidation Call} &\longrightarrow \text{Route invokes } \texttt{revalidate\_signal\_provenance(db, 'sig\_123')} \\
\textbf{Step 5: Savepoint Open} &\longrightarrow \texttt{with db.begin\_nested():} \text{ issues } \texttt{SAVEPOINT sa\_savepoint\_1} \\
\textbf{Step 6: Evidence Load} &\longrightarrow \text{SQLAlchemy loads } \texttt{signal.evidences} \\
&\quad \text{Child RLS: Farmer denied } \implies \text{PostgreSQL returns } \mathbf{0\text{ rows}} \\
&\quad \text{Python state: } \texttt{signal.evidences == []} \\
\textbf{Step 7: False Absence} &\longrightarrow \texttt{if not signal.evidences:} \text{ matches!} \\
&\quad \text{Staged in session: } \texttt{signal.distinct\_farms\_count = 0} \\
&\quad \text{Staged in session: } \texttt{signal.validation\_status = 'SUPPRESSED...'} \\
\textbf{Step 8: Savepoint Exit Flush} &\longrightarrow \text{Context manager attempts } \texttt{session.flush()} \\
&\quad \text{SQL: } \texttt{UPDATE regional\_signals SET distinct\_farms\_count = 0, ...} \\
&\quad \text{Parent UPDATE Policy: } \texttt{author\_write\_policy} \text{ requires Admin/Expert/Researcher!} \\
&\quad \text{PostgreSQL RLS: } \mathbf{0\text{ rows updated}} \\
&\quad \text{SQLAlchemy Driver: Raises } \texttt{StaleDataError: UPDATE statement on predicate did not match} \\
\textbf{Step 9: Savepoint Rollback} &\longrightarrow \text{Context manager catches } \texttt{StaleDataError;} \\
&\quad \text{Issues } \texttt{ROLLBACK TO SAVEPOINT sa\_savepoint\_1} \\
&\quad \text{Calls } \texttt{session.expire(signal)} \text{ (staged mutations discarded from memory)} \\
\textbf{Step 10: Exception Handled} &\longrightarrow \text{Helper lines 387--392 catch error; log error; return } \mathbf{False} \\
\textbf{Step 11: Outer Route Commit} &\longrightarrow \text{Route calls } \texttt{db.commit()} \\
&\quad \text{Transaction untainted; commits clean read session. DB row unchanged.} \\
\textbf{Step 12: Route Denial} &\longrightarrow \texttt{if not is\_valid ...: raise HTTPException(404)} \\
&\quad \text{Client receives: } \mathbf{HTTP\ 404\ NOT\ FOUND}
\end{aligned}$$

---

## 15. PRIVILEGED GET EXECUTION TRACE

### 15.1 Detailed Execution Trace (Privileged Session)

$$\begin{aligned}
\textbf{Step 1: HTTP Request} &\longrightarrow \text{Agricultural Expert issues } \texttt{GET /api/v1/regional-pulse/signals/sig\_123} \\
\textbf{Step 2: Authentication} &\longrightarrow \texttt{get\_current\_user} \text{ validates JWT; sets GUC } \texttt{app.current\_user\_id = 'expert\_789'} \\
\textbf{Step 3: Parent SELECT} &\longrightarrow \texttt{db.get(RegionalSignal, 'sig\_123')} \\
&\quad \text{Parent RLS: Passes via } \texttt{author\_write\_policy} \text{ (role in Expert) } \implies \mathbf{PASSED} \\
\textbf{Step 4: Revalidation Call} &\longrightarrow \text{Route invokes } \texttt{revalidate\_signal\_provenance(db, 'sig\_123')} \\
\textbf{Step 5: Savepoint Open} &\longrightarrow \texttt{with db.begin\_nested():} \text{ issues } \texttt{SAVEPOINT sa\_savepoint\_1} \\
\textbf{Step 6: Evidence Load} &\longrightarrow \text{SQLAlchemy loads } \texttt{signal.evidences} \\
&\quad \text{Child RLS: Expert permitted } \implies \text{PostgreSQL returns active evidence rows} \\
\textbf{Step 7: Verification Logic} &\longrightarrow \text{Loop counts verified farms matching district and time window.} \\
&\quad \text{Scenario A (Valid): } \text{Count } = 3 \implies \texttt{signal.distinct\_farms\_count = 3;} \text{ returns } \mathbf{True} \\
&\quad \text{Scenario B (Defective): } \text{Count } = 1 \implies \text{stages } \texttt{validation\_status = 'SUPPRESSED...';} \text{ returns } \mathbf{False} \\
\textbf{Step 8: Savepoint Exit Flush} &\longrightarrow \text{Context manager flushes dirty entities.} \\
&\quad \text{Parent UPDATE Policy: Expert satisfies } \texttt{author\_write\_policy} \implies \mathbf{1\text{ row updated!}} \\
&\quad \text{Savepoint commits: } \texttt{RELEASE SAVEPOINT sa\_savepoint\_1} \\
\textbf{Step 9: Outer Route Commit} &\longrightarrow \text{Route executes } \texttt{db.commit()} \\
&\quad \textbf{CRITICAL:} \text{ In Scenario B, the GET request } \mathbf{COMMITS A PERSISTENT MUTATION} \\
&\quad \text{to PostgreSQL, mutating the signal to } N=0 \text{ and } \texttt{'SUPPRESSED...'} \\
\textbf{Step 10: Response} &\longrightarrow \text{Expert receives full signal data including unmasked evidence items.}
\end{aligned}$$

---

## 16. SQLALCHEMY SAVEPOINT AND FLUSH ANALYSIS

### 16.1 Deployed Engine and Configuration
- **FastAPI Version:** `>= 0.115.0`
- **SQLAlchemy Version:** `>= 2.0.30`
- **PostgreSQL Driver:** `psycopg2-binary >= 2.9.9`
- **Session Configuration (`backend/app/database/session.py`):**
  - `autocommit = False`
  - `autoflush = False`
  - `expire_on_commit = False`

### 16.2 Savepoint Execution Mechanics
1. **`db.begin_nested()` Invocation:**  
   Because `autoflush = False`, SQLAlchemy issues `SAVEPOINT sa_savepoint_X` without emitting preliminary flush statements.
2. **Context Manager Exit (`__exit__`):**  
   Under SQLAlchemy 2.0, exiting a nested transaction context manager without an unhandled Python exception calls `savepoint.commit()`. `savepoint.commit()` unconditionally triggers `session.flush()` to persist changes staged during the subtransaction.
3. **The StaleDataError Mechanism:**  
   During the exit flush, SQLAlchemy issues an `UPDATE` statement. In PostgreSQL, RLS evaluates the `USING` clause of `regional_signals_author_write_policy`. For an ordinary farmer, this clause evaluates to `FALSE`. PostgreSQL quietly updates **0 rows**.  
   SQLAlchemy's ORM persistence layer expects exactly 1 row to be updated when persisting a loaded entity. Upon observing `cursor.rowcount == 0`, SQLAlchemy raises:
   ```python
   sqlalchemy.orm.exc.StaleDataError: UPDATE statement on table 'regional_signals' expected to update 1 row(s); 0 were matched.
   ```
4. **Subtransaction Rollback and State Expiration:**  
   The `with db.begin_nested():` context manager catches `StaleDataError`, issues `ROLLBACK TO SAVEPOINT sa_savepoint_X`, and calls `session.expire()` on the modified object. This restores the session state in PostgreSQL and prevents the main transaction from entering an aborted transaction state (SQLSTATE `25P02`).
5. **Outer Transaction Integrity:**  
   Because the subtransaction rollback cleared the PostgreSQL error, the outer session remains valid. When the route subsequently executes `db.commit()`, the commit succeeds cleanly without committing the failed update.

---

## 17. PERSISTENT READ-TRIGGERED MUTATION ASSESSMENT

### 17.1 Root Causes of Persistent Mutations on Read
The existence of `db.commit()` within `list_signals` (line 99) and `get_signal` (line 128) creates a severe architectural anomaly:
1. **HTTP GET Idempotency Violation (RFC 9110):** HTTP GET requests must be safe and idempotent. Committing database state during a GET request violates HTTP specifications.
2. **Privileged Writer Exposure (`RES-PULSE-READ-01`):** When an authenticated `ADMIN`, `AGRICULTURAL_EXPERT`, or `RESEARCHER` queries signals, their updates are authorized by RLS. If provenance verification decrements the farm count below 3, the GET route permanently persists the suppression mutation to PostgreSQL.
3. **Primary-Only Database Routing (`RES-PRIMARY-ROUTING-01`):** Because GET endpoints execute `db.commit()`, read requests cannot be offloaded to PostgreSQL read replicas (which operate in read-only mode). All read traffic is forced onto the primary database instance.
4. **Read-Your-Own-Writes Replication Lag Anomalies (`RES-REPLICA-LAG-01`):** In multi-node database clusters, write-on-read requests trigger replication lag anomalies where consecutive reads by the same user return fluctuating state.

---

## 18. CORRECTED FARMER-READ FAILURE MODEL

The following master outcome matrix formally classifies the behavior of GET read requests across all actor roles and database conditions:

| Actor Identity | Evidence Association Visible? | Parent UPDATE Policy Eligible? | Service Revalidation Result | Savepoint Flush Status | Persistent PostgreSQL Mutation? | API Response Effect | Governing Outcome Category |
|---|---|---|---|---|---|---|---|
| **Ordinary Farmer** | **NO** (Filtered by child RLS) | **NO** (Denied by author write policy) | **False** (False absence) | **Fails** (`StaleDataError`) -> Rolled Back | **NO** (Clean commit of read session) | **HTTP 404** (Detail) / **Excluded** (List) | **Outcome A** (Read Denial via Outcome B) |
| **Agricultural Expert** | **YES** (Permitted by child RLS) | **YES** (Permitted by author write policy) | **True** (Verified $N \ge 3$) | **Succeeds** (Savepoint released) | **NO** (Row already valid) | **HTTP 200** (Full data returned) | Normal Verified Read |
| **Agricultural Expert** | **YES** (Permitted by child RLS) | **YES** (Permitted by author write policy) | **False** (Genuine $N < 3$) | **Succeeds** (Savepoint released) | **YES** ($N=0$, `SUPPRESSED...` committed) | **HTTP 200** (Suppressed row returned) | **Outcome C** (Persistent Write-on-Read / `RES-PULSE-READ-01`) |
| **Researcher** | **YES** (Permitted by child RLS) | **YES** (Permitted by author write policy) | **False** (Genuine $N < 3$) | **Succeeds** (Savepoint released) | **YES** ($N=0$, `SUPPRESSED...` committed) | **HTTP 200** (Suppressed row returned) | **Outcome C** (Persistent Write-on-Read / `RES-PULSE-READ-01`) |
| **Application Admin** | **YES** (Permitted by child RLS) | **YES** (Permitted by author write policy) | **True** (Advisory $N=0$ bypassed) | **Succeeds** (Savepoint released) | **NO** (Advisory valid) | **HTTP 200** (Full data returned) | Normal Verified Read |

---

## 19. ALTERNATIVE SAFE FARMER-READ ARCHITECTURES

To resolve the write-on-read anomaly and false-evidence absence, four architectural designs were evaluated:

### Option A: Read-Only GET with Explicit Publication Predicate (Recommended for Pilot)
- **Mechanics:** Permanently remove `revalidate_signal_provenance()` and `db.commit()` from GET routes. Rely on persisted `distinct_farms_count` and `validation_status` columns. Update parent RLS public read policy to explicitly require:
  `validation_status IN ('EXPERT_CONFIRMED', 'ADMIN_CONFIRMED', 'OFFICIAL_ALERT')`.
- **Advantages:** Eliminates `RES-PULSE-READ-01`, `RES-PRIMARY-ROUTING-01`, and `RES-REPLICA-LAG-01`. Enables read replica offloading. Eliminates farmer read blocking.
- **Trade-offs:** Requires an asynchronous worker or write-time trigger to update provenance counts when observations are added or archived.

### Option B: Trusted Aggregate Projection Table
- **Mechanics:** Create an unprivileged projection table `regional_signal_public_projections` containing precomputed, de-identified public signals. Ordinary farmers query only this table.
- **Advantages:** Completely separates the internal collaborative model from the public publication model. Zero evidence foreign keys on the projection table.
- **Trade-offs:** Introduces dual-table maintenance, projection synchronization latency, and additional storage overhead.

### Option C: Controlled SECURITY DEFINER Verification Function
- **Mechanics:** Encapsulate provenance verification inside a PostgreSQL `SECURITY DEFINER` function owned by a trusted administrative role (`acrevia_admin`). The function inspects evidence rows and returns a boolean verification status to the caller without exposing raw evidence rows.
- **Advantages:** Allows application read sessions to verify provenance dynamically without granting child table SELECT privileges to farmers.
- **Trade-offs:** High security risk if search paths are unpinned or function permissions are leaked. Violates standard Mode A pure RLS pattern.

### Option D: Asynchronous Reconciliation with Transactional Outbox
- **Mechanics:** Provenance revalidation is completely decoupled from read endpoints and executed asynchronously by a background worker consuming events from an outbox table.
- **Advantages:** High performance, strictly read-only GET routes, resilient to traffic spikes.
- **Trade-offs:** Higher infrastructure complexity. Requires resolving `WRK-DISP-01` and provisioning message queue or scheduler workers.

### 19.1 Comprehensive Design Comparison Matrix

| Design Option | Farmer Privacy | Read Availability | Consistency | Complexity | Primary Security Risk | Required Owner Decision |
|---|---|---|---|---|---|---|
| **Option A: Pure Read-Only GET** | **HIGH** (Response masked + RLS) | **HIGH** (Zero write-on-read blocks) | **HIGH** (Atomic at write time) | **LOW** (Removes bad code) | Stale provenance if observations deleted without trigger. | Decision D-01 & D-03 sign-off. |
| **Option B: Projection Table** | **MAXIMAL** (Physical isolation) | **HIGH** (Query isolated projection) | **MEDIUM** (Eventual consistency) | **MEDIUM** (New table & sync worker) | Projection desynchronization. | Architecture Decision required. |
| **Option C: Security Definer** | **MEDIUM** (Function bypass risk) | **MEDIUM** (Dynamic query overhead) | **HIGH** (Dynamic query) | **HIGH** (DB function maintenance) | Privilege escalation if search path unpinned. | Architecture Decision required. |
| **Option D: Outbox Worker** | **HIGH** (Response masked + RLS) | **HIGH** (Pure read endpoints) | **MEDIUM** (Worker polling window) | **HIGH** (Queue & worker infra) | Worker failure creates stale state window. | Decision DB-AUTH-01 & WRK-DISP-01. |

---

## 20. PARENT/EVIDENCE PRIVILEGE SEPARATION

### 20.1 Why Blanket Parent UPDATE Revocation Breaks the Service
The previous errata report recommended revoking both `DELETE` and `UPDATE` table privileges from runtime application roles (`acrevia_staging_app`) on both `regional_signals` and `regional_signal_evidences`.

An audit of `RegionalPulseService` reveals that a blanket revocation of `UPDATE` on `regional_signals` **completely cripples legitimate platform operations**:
1. **Provenance Count Maintenance:** When observations are aggregated, `aggregate_regional_signal()` updates existing signals.
2. **Signal Suppression:** When provenance revalidation runs, the service must update `validation_status` to `'SUPPRESSED_INSUFFICIENT_PROVENANCE'`.
3. **Administrative Recovery:** `recover_suppressed_signal()` updates `validation_status` to `'ADMIN_CONFIRMED'` or `'EXPERT_CONFIRMED'`.
4. **Agronomic Validation:** Experts confirming community observations update `validation_status`.

### 20.2 Granular Least-Privilege Architecture
To establish robust defense-in-depth without breaking service workflows, privileges must be decoupled between parent and child tables:

| Database Table | Role: `acrevia_staging_app` | Role: `acrevia_worker` | Security Rationale |
|---|---|---|---|
| `regional_signal_evidences` (Child) | `SELECT` (Privileged), `INSERT` | `SELECT`, `INSERT` | **Revoke UPDATE & DELETE**. Evidence rows are strictly append-only telemetry records. |
| `regional_signals` (Parent) | `SELECT`, `INSERT`, `UPDATE` (Restricted) | `SELECT`, `UPDATE` | **Revoke DELETE**. Retain `UPDATE` bounded by column grants or command-scoped RLS policies. |

#### Column-Level Grant Alternative:
```sql
-- Restrict UPDATE on parent table to operational status columns only
REVOKE UPDATE ON regional_signals FROM acrevia_staging_app;
GRANT UPDATE (distinct_farms_count, validation_status, confidence_tier) ON regional_signals TO acrevia_staging_app;
```

---

## 21. STATUS-TRANSITION AUTHORIZATION REQUIREMENTS

### 21.1 Enforcing State Transitions via Command-Scoped RLS Policies
To eliminate the vulnerabilities of broad `FOR ALL` policies, `regional_signals` should transition to command-scoped policies pairing `USING` and `WITH CHECK`:

```sql
-- Drop the broad FOR ALL policy
DROP POLICY IF EXISTS regional_signals_author_write_policy ON regional_signals;

-- Command-Scoped INSERT Policy
CREATE POLICY regional_signals_insert_policy ON regional_signals
    FOR INSERT TO acrevia_staging_app
    WITH CHECK (
        current_setting('app.current_user_id', true) != ''
        AND EXISTS (
            SELECT 1 FROM user_roles ur
            WHERE ur.user_id::text = current_setting('app.current_user_id', true)
            AND ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')
        )
    );

-- Command-Scoped UPDATE Policy: Allow expert recovery transition ONLY
CREATE POLICY regional_signals_expert_update_policy ON regional_signals
    FOR UPDATE TO acrevia_staging_app
    USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            WHERE ur.user_id::text = current_setting('app.current_user_id', true)
            AND ur.role_id = 'AGRICULTURAL_EXPERT'
        )
    )
    WITH CHECK (
        validation_status IN ('EXPERT_CONFIRMED', 'SUPPRESSED_INSUFFICIENT_PROVENANCE')
    );
```

### 21.2 Database Status CHECK Constraint
A database `CHECK` constraint must be applied to `regional_signals.validation_status` to guarantee that only valid lifecycle statuses can be persisted by any SQL writer:
```sql
ALTER TABLE regional_signals
ADD CONSTRAINT chk_regional_signals_validation_status
CHECK (validation_status IN (
    'UNVALIDATED_OBSERVATION',
    'EXPERT_CONFIRMED',
    'ADMIN_CONFIRMED',
    'OFFICIAL_ALERT',
    'SUPPRESSED_INSUFFICIENT_PROVENANCE',
    'SUSPENDED'
));
```
*Note:* The constraint intentionally includes `'SUSPENDED'` to accommodate legacy or administratively suspended rows, while ensuring arbitrary strings (e.g. `'PUBLISHED'`) are rejected.

---

## 22. EVIDENCE RETENTION AND CASCADE IMPLICATIONS

### 22.1 Foreign Key Constraint & Referential Integrity
- **Database Layer:** The foreign key `RegionalSignalEvidence.signal_id -> regional_signals.id` must be altered from `ON DELETE CASCADE` to `ON DELETE RESTRICT` (or `ON DELETE NO ACTION`).
- **PostgreSQL Kernel Execution:** When `ON DELETE RESTRICT` is active, any direct SQL attempt to execute `DELETE FROM regional_signals WHERE id = :id` immediately fails with SQLSTATE `23001` (`restrict_violation`) if linked child evidence rows exist.

### 22.2 SQLAlchemy ORM Relationship Coordination
- **ORM Layer:** In `backend/app/models/regional_pulse.py` (line 35), the relationship definition must be modified:
  ```python
  # Hardened relationship: Remove delete-orphan, enable passive_deletes
  evidences: Mapped[List["RegionalSignalEvidence"]] = relationship(
      "RegionalSignalEvidence",
      back_populates="signal",
      cascade="save-update, merge",
      passive_deletes=True,
  )
  ```
- **Execution Effect:** With `passive_deletes=True`, SQLAlchemy does **not** emit explicit child `DELETE` statements when a parent is deleted. It leaves deletion handling entirely to the PostgreSQL foreign key constraint, triggering the database-level `RESTRICT` violation.

### 22.3 Threat Model: Runtime Roles vs. Superusers
$$\begin{aligned}
\mathbf{Threat\ Scope:} &\quad \text{Protects against application-level deletions, ORM cascade purges, and compromised runtime roles.} \\
\mathbf{Superuser\ Scope:} &\quad \text{PostgreSQL superusers and table owners retain inherent catalog authority to drop constraints.}
\end{aligned}$$
The platform achieves **`APPEND_ONLY_FOR_RUNTIME_ROLES`**, which satisfies compliance and security requirements for Pilot Release.

---

## 23. OWNER DECISION TRACEABILITY

The following matrix formally links technical findings to governing Project Owner decisions:

| Decision ID | Decision Title | Current Architectural State | Required Owner Resolution | Mode B Dependency |
|---|---|---|---|---|
| **D-01** | **Official Advisory Public Visibility vs. Minimum Farm Threshold** | Official alerts ($N=0$) are blocked from farmers by RLS `distinct_farms_count >= 3`. | Authorize conditional RLS exception: `(validation_status = 'OFFICIAL_ALERT' AND confidence_tier = 'OFFICIAL_ADVISORY' AND distinct_farms_count = 0)`. | **Prerequisite** for farmer alert visibility in Mode B. |
| **D-02** | **Source Authenticity & Terminology** | Code uses `OFFICIAL_ALERT` for status and `OFFICIAL_ADVISORY` for tier. | Formally approve terminology mapping; establish that platform admin approval does not represent government signing. | Informs API contract documentation. |
| **D-03** | **Agronomic Peer-Review Workflow** | Unvalidated observations ($N \ge 3$) are database-visible to farmers; hidden only via false-absence side-effect. | Authorize whether community signals must be expert-confirmed before public release: `validation_status IN ('EXPERT_CONFIRMED', 'ADMIN_CONFIRMED', 'OFFICIAL_ALERT')`. | **Prerequisite** for public read policy DDL in Mode B. |
| **DB-AUTH-01** | **Trusted Writer Architecture** | Single runtime role `acrevia_staging_app` handles web traffic and background jobs. | Authorize dedicated database roles (`acrevia_worker`, `acrevia_staging_app`) and execute `generate_privilege_grants_ddl()`. | **Prerequisite** for least-privilege role creation in Mode B. |

---

## 24. CORRECTED EXECUTION-GATE REGISTER

### 24.1 Reversal of Previous Errata Mischaracterizations
The previous errata report contained significant errors regarding the execution gates. This audit formally restores the exact scope and registered status from `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`:

| Gate ID | Authoritative Registered Scope | Recorded State | Authority | Execution Impact & Prerequisites |
| :--- | :--- | :--- | :--- | :--- |
| **GATE-01** | Provisioning of isolated Neon staging branch `staging-rls-phase07` from parent `production` in region `aws-ap-southeast-1`. | **`[x] APPROVED BY OWNER (2026-11-10)`** | Project Owner | **Formally Approved.** Physical execution remains `LIVE_DATABASE_UNVERIFIED` under Mode A restrictions. |
| **GATE-02** | Creation of unprivileged runtime database role `acrevia_staging_app` (`NOSUPERUSER`, `NOBYPASSRLS`, `NOCREATEDB`, `NOCREATEROLE`). | `[ ] UNCHECKED (AWAITING SIGN-OFF)` | Project Owner | **Pending Sign-Off.** Required to provision runtime credentials on staging branch. |
| **GATE-03** | Physical execution of Alembic RLS migration `a1089411c87d` applying 751 atomic DDL statements to `neondb_staging`. | `[ ] UNCHECKED (AWAITING SIGN-OFF)` | Project Owner | **Pending Sign-Off.** Required to apply RLS policies and table classifications. |
| **GATE-04** | Execution of automated staging RLS verification harness (`scripts/verify_staging_rls.py`) against live staging endpoint. | `[ ] UNCHECKED (AWAITING SIGN-OFF)` | Project Owner | **Pending Sign-Off.** Required to execute catalog verification and tenant isolation probes. |
| **GATE-05** | Teardown and deprovisioning schedule of `staging-rls-phase05` post-verification. | `[ ] UNCHECKED (AWAITING SIGN-OFF)` | Project Owner | **Pending Sign-Off.** Governs cloud branch cleanup 24 hours post-verification. |

### 24.2 Why MODE B Execution Remains Unauthorized
A critical distinction must be maintained between **GATE-01 Approval** and **Overall MODE B Authorization**:
- GATE-01 approved the *concept* of provisioning the staging branch on 2026-11-10.
- However, **MODE B execution remains strictly unauthorized** because:
  1. GATE-02 (role creation), GATE-03 (migration execution), and GATE-04 (harness execution) remain unchecked (`AWAITING_OWNER_SIGN_OFF`).
  2. Owner Decisions D-01 through D-03 and DB-AUTH-01 remain uncompleted prerequisites.
  3. Physical branch provisioning has not been initiated in Mode A.
- Therefore, the engineering team cannot connect to Neon Cloud or execute remote SQL until all prerequisite gates are signed off.

### 24.3 Branch-Identity Ambiguity
An explicit contradiction exists within the authoritative register:
- **GATE-01 Scope & Checklist:** Designates branch name `staging-rls-phase07`.
- **Overview Text (Line 20) & GATE-05 Scope:** Designates branch name `staging-rls-phase05`.

**Governance Treatment:** The auditor cannot silently pick a branch identifier. This is preserved as an open governance discrepancy requiring Project Owner clarification prior to Mode B execution.

---

## 25. CANONICAL BLOCKER AND RESIDUAL-RISK RECONCILIATION

### 25.1 Canonical Blocker Register Preservation
All fifteen canonical blockers are preserved without modification of IDs or definitions:

| Blocker ID | Canonical Blocker Title | Core Technical Status in Regional Pulse Read Context |
|---|---|---|
| `RLS-WRITE-AUTH-01` | RLS write policy allows arbitrary role updates via unconstrained `WITH CHECK`. | Decompose `author_write_policy` into command-scoped policies; add DB status constraint. |
| `RLS-ROLE-ASSIGNMENT-01` | Runtime role assignment mechanism susceptible to session variable leakage. | Session GUCs must be encapsulated within transaction boundaries. |
| `DB-AUTH-01` | Single runtime database role lacks separation between background workers and web apps. | Authorize dedicated worker role `acrevia_worker` to execute provenance revalidation. |
| `DB-CREDENTIAL-EXPOSURE-01` | Public exposure of database connection strings in legacy commits. | Independent blocker; requires rotation before production cutover. |
| `APP-ROLE-SELF-SELECT-01` | Client self-selection of roles during registration/authentication. | Enforce database-level role binding on API actors. |
| `EXP-AUTH-01` | Expert and researcher endpoint authorization inconsistencies. | Baseline code currently aligned; future RLS narrowing must coordinate with API. |
| `CASCADE-ROLE-DEL-01` | Cascading deletions undermine evidence integrity and role associations. | Coordinate FK `ON DELETE RESTRICT` with ORM `passive_deletes=True`. |
| `TENANT-MEMBERSHIP-01` | Tenant membership validation absent in cross-tenant join queries. | GUC validation required across collaborative tables. |
| `OWNER-AUTH-01` | Missing formal Project Owner sign-offs on core security decisions. | Formalize sign-offs on Decisions D-01 through D-03 and DB-AUTH-01. |
| `DB-RLS-01` | Staging database RLS verification unperformed against live Neon instance. | Unverified in Mode A; requires Mode B execution under GATE-01–04. |
| `WRK-DISP-01` | Production worker dispatch provider raises `DISPATCH_NOT_CONFIGURED`. | Zero Regional Pulse workers implemented in source; requires Outbox pattern. |
| `RES-PULSE-01` | Role-based cross-district SELECT eligibility across 33 districts. | Generated `FOR ALL` policy grants statewide row eligibility; canonical Medium preserved. |
| `RES-PULSE-02` | Unvalidated community signals visible prior to agronomic peer review. | Governed by Decision D-03; parent RLS must explicitly exclude unvalidated rows. |
| `GATE01-PROV-01` | Physical provisioning of isolated staging branch unverified in Mode A. | GATE-01 approved on 2026-11-10; physical branch creation unverified offline. |
| `RES-PULSE-READ-01` | Write-on-read suppression in Regional Pulse GET endpoints. | Proven in GET routes; refactor to strictly read-only GET endpoints. |

### 25.2 Canonical Residual Risk Preservation
All five canonical residual risks remain active at their formally recorded severities:

| Risk Identifier | Title | Canonical Recorded Severity | Assessed Technical Severity | Risk Notes & Discrepancy Reconciliation |
|---|---|---|---|---|
| `RES-PULSE-01` | Broad Expert/Researcher SELECT Scope | **MEDIUM** | **HIGH** | Canonical severity preserved at Medium; technical High documented for owner review. |
| `RES-PULSE-02` | Regional Signal Early Visibility ($N \ge 3$) | **MEDIUM** | **MEDIUM** | Dependent on Decision D-03 sign-off. |
| `RES-PRIMARY-ROUTING-01` | Read Endpoint Primary DB Connection Requirement | **MEDIUM** | **MEDIUM** | Mitigated by removing mutations/commits from GET routes. |
| `RES-REPLICA-LAG-01` | Read-Your-Own-Writes Replication Lag | **LOW** | **LOW** | Mitigated by converting GET routes to pure reads. |
| `RES-FREE-TEXT-01` | Free-Text Advisory Injection in Regional Signals | **LOW** | **LOW** | Managed via Pydantic input sanitization and schema bounds. |

*Descriptive Tracking:* `FARMER_READ_BLOCKED_BY_EVIDENCE_ASSOCIATION_RLS` is tracked as a descriptive finding documenting the false-absence failure model, not as an invented canonical blocker ID.

---

## 26. FUTURE POSTGRESQL VERIFICATION PLAN (DESIGN ONLY)

The following verification suite is designed for offline execution upon authorized transition to **MODE B**:

| Verification Domain | Test Objective | Required Database Engine | Required Identity | Required Grants | Test Execution Setup & Query | Expected Test Result | Failure Meaning & Interpretation | Owner Decision Required? |
|---|---|---|---|---|---|---|---|---|
| **1. Public Parent SELECT** | Farmer reads verified signal ($N=3$, `EXPERT_CONFIRMED`). | PostgreSQL 15+ | `acrevia_staging_app` (Farmer GUC) | `SELECT` on `regional_signals` | `SELECT count(*) FROM regional_signals WHERE id = expert_sig_id;` | Returns `1`. | Public read policy rejects valid confirmed signal. | Yes (Decision D-03) |
| **2. Public Parent SELECT** | Farmer denied unvalidated signal ($N=3$, `UNVALIDATED...`). | PostgreSQL 15+ | `acrevia_staging_app` (Farmer GUC) | `SELECT` on `regional_signals` | `SELECT count(*) FROM regional_signals WHERE id = unvalidated_sig_id;` | Returns `0` (under hardened D-03 policy). | RLS leaks unvalidated observations to farmers. | Yes (Decision D-03) |
| **3. Public Parent SELECT** | Farmer reads official state alert ($N=0$, `OFFICIAL_ALERT`). | PostgreSQL 15+ | `acrevia_staging_app` (Farmer GUC) | `SELECT` on `regional_signals` | `SELECT count(*) FROM regional_signals WHERE id = official_sig_id;` | Returns `1` (under hardened D-01 policy). | Official alerts blocked from farmers by $N \ge 3$. | Yes (Decision D-01) |
| **4. Evidence Relationship** | Farmer query denied child evidence rows. | PostgreSQL 15+ | `acrevia_staging_app` (Farmer GUC) | `SELECT` on `regional_signal_evidences` | `SELECT count(*) FROM regional_signal_evidences WHERE signal_id = sig_id;` | Returns `0`. | Evidence table leaks raw farmer telemetry. | No (RLS core rule) |
| **5. GET Path Idempotency** | Farmer GET request does not mutate database row. | PostgreSQL 15+ | `acrevia_staging_app` (FastAPI TestClient) | `SELECT` on parent/child | Issue `GET /api/v1/regional-pulse/signals/sig_123` as Farmer. | HTTP 200/404; DB row unchanged ($N=3$, status unchanged). | GET request executed persistent or transient write. | No (API route refactor) |
| **6. Privileged GET Safety** | Privileged GET request cannot commit suppression update. | PostgreSQL 15+ | `acrevia_staging_app` (Expert TestClient) | `SELECT` on parent/child | Issue `GET /api/v1/regional-pulse/signals/sig_defective` as Expert. | HTTP 200; DB row remains unmutated. | Privileged read persisted state change (`RES-PULSE-READ-01`). | No (API route refactor) |
| **7. Savepoint Isolation** | Savepoint rollback does not taint outer transaction. | PostgreSQL 15+ | `acrevia_staging_app` | `SELECT`, `UPDATE` | Simulate `StaleDataError` inside `with db.begin_nested():`. | Savepoint rolled back; outer session commits clean read. | Outer transaction enters SQLSTATE `25P02`. | No (SQLAlchemy spec) |
| **8. Status Constraint** | Direct SQL insertion of invalid status rejected. | PostgreSQL 15+ | `acrevia_staging_app` | `INSERT` on `regional_signals` | `INSERT INTO regional_signals (..., validation_status) VALUES (..., 'PUBLISHED');` | Fails with SQLSTATE `23514` (`check_violation`). | Database status CHECK constraint missing. | Yes (Schema migration) |
| **9. Evidence Retention** | Parent DELETE blocked when child evidence exists. | PostgreSQL 15+ | `acrevia_staging_app` | `DELETE` on `regional_signals` | `DELETE FROM regional_signals WHERE id = signal_with_evidence;` | Fails with SQLSTATE `23001` (`restrict_violation`). | FK still configured as `CASCADE`. | Yes (Schema migration) |
| **10. Child Grant Revocation** | Application role denied child DELETE statement. | PostgreSQL 15+ | `acrevia_staging_app` | Table grants per crosswalk | `DELETE FROM regional_signal_evidences WHERE id = ev_id;` | Fails with SQLSTATE `42501` (`insufficient_privilege`). | Child DELETE grant active on application role. | Yes (Decision DB-AUTH-01) |

---

## 27. ADVERSARIAL ASSUMPTIONS REVIEW

This audit subjected all findings to the eighteen rigorous challenge questions mandated by Section 17:

1. *Are all unvalidated signals hidden by the current parent SELECT predicate?*  
   **Rebuttal:** **No.** The parent SELECT policy requires only `distinct_farms_count >= 3 AND validation_status != 'SUSPENDED'`. Unvalidated observations with $N \ge 3$ pass parent RLS unconditionally.
2. *Do the public RLS policy and API response filter enforce identical rules?*  
   **Rebuttal:** **No.** Parent RLS permits $N \ge 3$ unvalidated signals; the API route filters them out because of the false-absence revalidation failure. Parent RLS permits suppressed signals with $N \ge 3$; the API route explicitly filters them out.
3. *Does a farmer's empty evidence relationship prove there are no evidence rows?*  
   **Rebuttal:** **No.** Child-table RLS denies farmers SELECT access on `regional_signal_evidences`. The empty collection reflects privacy filtering, not physical absence.
4. *Is farmer read denial necessarily caused by status eligibility?*  
   **Rebuttal:** **No.** For verified community signals ($N=3$, `EXPERT_CONFIRMED`), farmers are denied because child RLS causes false-absence revalidation failure, returning `is_valid == False` and triggering HTTP 404.
5. *Can a privileged GET request persist a status mutation?*  
   **Rebuttal:** **Yes.** If an Expert or Admin issues a GET request on a signal failing provenance verification, the savepoint update flush succeeds under their privileges, and the outer route commits the suppression update to PostgreSQL.
6. *Does a failed nested flush always produce the same SQLAlchemy exception?*  
   **Rebuttal:** **No.** A 0-row update produces `StaleDataError`; an ungranted privilege produces `psycopg2.errors.InsufficientPrivilege` (`42501`); an invalid column value produces `DataError`.
7. *Does a failed savepoint always invalidate the outer transaction?*  
   **Rebuttal:** **No.** When `ROLLBACK TO SAVEPOINT` is executed, the subtransaction error is cleared in PostgreSQL. The outer transaction remains valid and can commit subsequent read work.
8. *Does removing GET commits fix replica lag?*  
   **Rebuttal:** It eliminates self-induced read-your-own-writes replication lag on Regional Pulse read routes, but underlying cluster replication lag is governed by database replication infrastructure.
9. *Does removing parent UPDATE privilege affect recovery or suppression?*  
   **Rebuttal:** **Yes, catastrophically.** Revoking parent `UPDATE` completely breaks provenance updates, signal suppression, administrative recovery, and expert validation transitions.
10. *Does evidence child DELETE revocation prevent internal FK cascade?*  
    **Rebuttal:** **No.** PostgreSQL internal FK cascade triggers (`RI_FKey_cascade_del`) execute under SPI with `SECURITY_NOFORCE_RLS`, bypassing child table DELETE privilege checks.
11. *Does passive_deletes=True always guarantee parent deletion is blocked?*  
    **Rebuttal:** Only when the database foreign key is configured with `ON DELETE RESTRICT` or `ON DELETE NO ACTION`. If the database FK remains `CASCADE`, PostgreSQL cascades deletion regardless of `passive_deletes`.
12. *Is SUSPENDED irrelevant to a proposed status CHECK constraint?*  
    **Rebuttal:** **No.** The CHECK constraint must include `'SUSPENDED'` because existing database policies and legacy records reference this state. Omitting it would cause check violations during table re-validation.
13. *Does GATE-01 remain unchecked?*  
    **Rebuttal:** **No.** The register confirms: `[x] APPROVED BY OWNER (2026-11-10)`. The previous errata's assertion was factually wrong.
14. *Is GATE-02 migration execution?*  
    **Rebuttal:** **No.** The register explicitly defines GATE-02 as: "Creation of unprivileged runtime database role `acrevia_staging_app`".
15. *Is GATE-03 privilege hardening?*  
    **Rebuttal:** **No.** The register explicitly defines GATE-03 as: "Physical execution of Alembic RLS migration `a1089411c87d` applying 751 atomic DDL statements".
16. *Is GATE-04 read-privacy UAT?*  
    **Rebuttal:** **No.** The register explicitly defines GATE-04 as: "Execution of automated staging RLS verification harness (`scripts/verify_staging_rls.py`)".
17. *Does GATE-01 approval alone authorize complete MODE B execution?*  
    **Rebuttal:** **No.** GATE-01 authorized only branch provisioning. GATE-02 through GATE-05 and Decisions D-01 through D-03 remain uncompleted prerequisites.
18. *Does a technical severity change automatically change canonical governance severity?*  
    **Rebuttal:** **No.** Canonical governance records can only be updated by the Project Owner. Technical findings must be documented separately.

---

## 28. RELEASE-READINESS CONCLUSION

$$\mathbf{ASSURANCE\ RELEASE\ RECOMMENDATION:}\quad \mathbf{CONDITIONALLY\_READY\_FOR\_OWNER\_REVIEW}$$

### Governing Release Conditions
The Phase 07 assurance package is conditionally ready for formal Project Owner review, subject to:
1. **Resolution of Branch-Identity Inconsistency:** Project Owner must resolve whether `staging-rls-phase07` or `staging-rls-phase05` is the authoritative target branch.
2. **Owner Decision Sign-Offs:** Project Owner must formally execute Decisions D-01 (Official Advisory Exception), D-02 (Terminology), D-03 (Agronomic Peer-Review Publication Rule), and DB-AUTH-01 (Trusted Writer Architecture).
3. **Approval of GET Route Read-Only Refactoring:** Project Owner must authorize removing dynamic revalidation and `db.commit()` from GET routes.
4. **Maintenance of Mode A Boundary:** Zero cloud provisioning or live database queries may occur until GATE-02 through GATE-05 are formally signed off.

---

## 29. EXPLICIT EVIDENCE AND EXECUTION LIMITATIONS

1. **Strict MODE A Boundary:** Conducted exclusively via static code analysis, AST inspection, and offline transaction modeling. Zero network calls to Neon Cloud or AWS Singapore were initiated.
2. **Catalog & Grant Uncertainty:** Live table grants and role configurations on Neon staging remain `LIVE_DATABASE_UNVERIFIED`.
3. **No Code Modifications:** Exactly zero application source files, schema definitions, Alembic migrations, or test suites were modified in the workspace.
4. **Advisory Authority:** This report provides security assurance and architectural analysis only; formal operational approval remains the sole authority of the Project Owner.
