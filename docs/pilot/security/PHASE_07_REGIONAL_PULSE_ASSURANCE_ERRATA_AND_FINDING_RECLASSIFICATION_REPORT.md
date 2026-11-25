# ACREVIA — PHASE 07: REGIONAL PULSE ASSURANCE ERRATA, EVIDENCE-BOUND FINDING RECLASSIFICATION & GOVERNANCE REGISTER CONSISTENCY AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India (33 Administrative Districts)  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** `MODE A ONLY` — Local Source Inspection, Static Policy Verification, Governance Reconciliation & Non-Destructive Documentation  
**Audit Methodology:** Everything Claude Code (ECC) — `PLAN → INSPECT → TRACE → ADVERSARIAL REVIEW → VERIFY OFFLINE → DOCUMENT`  
**Public Repository:** `https://github.com/gokul1599/ACREVIA`  
**Verified Public & Local Baseline:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Target Document under Review:** `docs/pilot/security/PHASE_07_REGIONAL_PULSE_STATUS_CONTRACT_AND_EVIDENCE_RETENTION_DESIGN_ASSURANCE_REPORT.md`  
**Authoritative Governance Register:** `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`  
**Assurance Release Recommendation:** `CONDITIONALLY_READY_FOR_OWNER_REVIEW`  

---

## 1. EXECUTIVE CORRECTIVE ASSURANCE SUMMARY

This audit delivers an independent, rigorous, and evidence-bound corrective assurance review and errata audit of the previous Phase 07 Regional Pulse security report (`PHASE_07_REGIONAL_PULSE_STATUS_CONTRACT_AND_EVIDENCE_RETENTION_DESIGN_ASSURANCE_REPORT.md`). 

Operating strictly under **MODE A ONLY** restrictions (zero live database connections, zero cloud provisioning, zero credential manipulation, zero application code modification, and zero Git history alterations), this assessment reconciles every finding previously designated under the `SEC-P07-*` series against the actual repository source code, Alembic migrations, PostgreSQL engine mechanics, and the authoritative project governance register.

### 1.1 Core Corrective Findings and Errata Distinctions
1. **Reclassification of Status Vocabulary Finding (`SEC-P07-STATUS-01`):**
   - The prior report asserted that the status `'PUBLISHED'` does not exist in the codebase and that a proposed public read policy using `validation_status IN ('PUBLISHED', 'OFFICIAL_ADVISORY')` would deny 100% of all possible database rows.
   - *Errata Correction:* Inspection reveals that `'PUBLISHED'` does exist within other application domains (specifically Stage 12 Knowledge Commons models, `knowledge_contributions`, and `commons_contributions`). While `'PUBLISHED'` is absent from the `RegionalSignal` lifecycle, asserting that the predicate denies 100% of all possible database rows was an overclaim because `regional_signals.validation_status` is an unconstrained `VARCHAR(50)` column in PostgreSQL without a database `CHECK` constraint or `ENUM` type. An authorized direct SQL writer could persist arbitrary strings. The accurate, defensible finding is that the predicate would fail to match 100% of *currently observed service-generated rows* emitted by `RegionalPulseService`. Furthermore, because this predicate was introduced in an earlier design exploration rather than in active source code, `SEC-P07-STATUS-01` is formally reclassified from an active database defect to a `PROPOSED_DESIGN_INCOMPATIBILITY`.
2. **Narrowing of Researcher POST Contract Mismatch (`SEC-P07-API-RLS-01`):**
   - The prior report claimed that the current implementation causes researchers to crash on `POST /regional-pulse/signals` with HTTP 500 / SQLSTATE `42501` due to an RLS policy omission.
   - *Errata Correction:* Inspection of `backend/app/database/rls.py` (line 928) reveals that the generated `regional_signals_author_write_policy` **already includes `RESEARCHER`** alongside `ADMIN` and `AGRICULTURAL_EXPERT`. In the current repository baseline, both the FastAPI endpoint and the generated RLS write policy are aligned. The mismatch was introduced solely by an earlier *proposed narrower RLS policy*. This finding is reclassified from an existing system bug to a `PROPOSED_DESIGN_INCOMPATIBILITY`.
3. **Refinement of Foreign Key Cascade and Referential Integrity Mechanics (`SEC-P07-CASCADE-01` & `SEC-P07-CASCADE-02`):**
   - The prior report asserted that PostgreSQL FK cascade completely circumvents RLS, rendering database-level evidence immutability impossible.
   - *Errata Correction:* PostgreSQL internal referential integrity cascade triggers (`RI_FKey_cascade_del` in `src/backend/utils/adt/ri_triggers.c`) execute under SPI with `SECURITY_NOFORCE_RLS`. However, this internal cascade is triggered only if the parent `DELETE` statement itself is authorized. Furthermore, while absolute immutability against database superusers or table owners is impossible in PostgreSQL, `APPEND_ONLY_FOR_RUNTIME_ROLES` is achievable through table-level grant revocation, `ON DELETE RESTRICT`, and removing ORM orphan deletion.
4. **Correction of Worker Infrastructure Scope (`SEC-P07-WORKER-01`):**
   - The prior report cited `ProductionDispatchBlockedError: DISPATCH_NOT_CONFIGURED` in `backend/app/tasks/run_riskcast_batch.py` to assert that all Regional Pulse background workers are operationally infeasible.
   - *Errata Correction:* `run_riskcast_batch.py` is specifically a RiskCast batch task. No Regional Pulse worker implementation exists in the repository. The finding is narrowed to: *No configured Regional Pulse worker dispatch implementation was evidenced in the inspected repository source.*
5. **Reconciliation of Role Scope Severity (`SEC-P07-SCOPE-01` vs `RES-PULSE-01`):**
   - The prior report elevated role-based cross-district SELECT eligibility to High severity while retaining canonical `RES-PULSE-01` at Medium. This audit formally separates technical severity (High) from canonical recorded governance severity (Medium), preserving canonical records pending Project Owner review.
6. **Withdrawal of Unsupported Causal Claim (`SEC-P07-LIVE-01`):**
   - The prior report asserted that GATE-01 physical branch provisioning is "blocked by credential rotation." The governance register contains no causal link between the two. The causal assertion is withdrawn.
7. **Identification of Governance Branch-Identity Inconsistency:**
   - `PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md` names `staging-rls-phase07` in GATE-01, but refers to `staging-rls-phase05` in line 20 and GATE-05. This represents an unresolved governance ambiguity requiring Project Owner clarification.

---

## 2. SOURCE BASELINE AND REPORT-INSPECTION EVIDENCE

### 2.1 Public Repository Baseline
- **Remote URL:** `https://github.com/gokul1599/ACREVIA`
- **Tracked Branch:** `main`
- **Public Commit Hash:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d`
- **Public Tree Integrity:** Ground truth baseline verified.

### 2.2 Local Workspace and Working Tree Status
- **Local Working Directory:** `c:\Users\gokul\OneDrive\Documents\projects`
- **Active Git Branch:** `main`
- **Local HEAD Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d`
- **Commit Divergence:** Exactly 0 commits (`HEAD` is synchronized with `origin/main`).
- **Application Source Code Modifications:** Exactly **0 files modified** across `backend/app/`, `backend/alembic/`, `backend/tests/`, and frontend.
- **Tracked Documentation Modifications:** 7 historical Phase 07 planning and decision matrices in `docs/pilot/security/`.
- **Untracked Historical Deliverables:** 10 historical assurance reports preserved without modification.

### 2.3 Report under Review
- **File Inspected:** `docs/pilot/security/PHASE_07_REGIONAL_PULSE_STATUS_CONTRACT_AND_EVIDENCE_RETENTION_DESIGN_ASSURANCE_REPORT.md`
- **File Size:** 36,548 bytes (876 lines).
- **Inspection Status:** Read and verified in its entirety.

### 2.4 Codebase Files Inspected
- `backend/app/models/regional_pulse.py` (lines 1–75)
- `backend/app/schemas/regional_pulse.py` (lines 1–55)
- `backend/app/services/regional_pulse_service.py` (lines 1–570)
- `backend/app/api/v1/endpoints/regional_pulse.py` (lines 1–250)
- `backend/app/database/rls.py` (lines 1–1100)
- `backend/app/tasks/run_riskcast_batch.py` (lines 1–120)
- `backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py` (lines 1–85)
- `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md` (lines 1–120)
- `docs/pilot/security/phase_07_owner_decision_evidence_traceability_matrix.md` (lines 1–210)
- `docs/pilot/security/PHASE_07_REGIONAL_PULSE_PROJECT_OWNER_DECISION_RECORD.md` (lines 1–150)
- `docs/pilot/security/PHASE_07_TRUSTED_WRITER_ARCHITECTURE_DECISION_RECORD.md` (lines 1–180)

---

## 3. EVIDENCE CLASSIFICATION METHODOLOGY

To ensure strict evidentiary hygiene and prevent conflating verified facts with future proposals or unverified runtime assumptions, every finding, claim, and assertion in this report is classified using the following taxonomy:

| Classification | Definition & Evidentiary Standard |
|---|---|
| `PUBLIC_SOURCE_VERIFIED` | Directly evidenced in public commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d`. |
| `LOCAL_SOURCE_VERIFIED` | Directly evidenced in the local working tree without divergence from public state. |
| `LOCAL_TEST_VERIFIED` | Validated via safe, offline unit tests (AST inspection, SQLite/mock) without network access. |
| `POSTGRESQL_ENGINE_DOCUMENTED` | Established from authoritative PostgreSQL source code (`ri_triggers.c`, `rowsecurity.c`) and official engine documentation. |
| `PROPOSED_DESIGN_INCOMPATIBILITY` | A defect or conflict that does not exist in current code, but arises if a proposed future design is applied. |
| `CONDITIONAL_RUNTIME_RISK` | A risk that depends on unverified runtime conditions (e.g. active PostgreSQL grants, GUC settings). |
| `SOURCE_INFERENCE` | Deductions logically derived from source code, schema relationships, and API contracts. |
| `WITHDRAWN_AS_UNSUPPORTED` | A previous assertion found to lack empirical support in repository source or governance records. |
| `LIVE_DATABASE_UNVERIFIED` | Behavior requiring live Neon Cloud catalog inspection; strictly prohibited in Mode A. |
| `OWNER_DECISION_REQUIRED` | Matters reserved exclusively for Project Owner governance sign-off. |

---

## 4. PREVIOUS FINDING-BY-FINDING ERRATA MATRIX

The following master matrix summarizes the corrective reassessment of all ten findings identified in the previous security assurance report:

| Finding ID | Previous Conclusion | Corrective Assessment | Classification | Technical Severity | Canonical Governance Impact | Required Action / Correction |
|---|---|---|---|---|---|---|
| `SEC-P07-STATUS-01` | Proposed predicate `IN ('PUBLISHED', 'OFFICIAL_ADVISORY')` denies 100% of rows because `'PUBLISHED'` does not exist in codebase. | Overclaim corrected: `'PUBLISHED'` exists in Stage 12 Knowledge Commons models. Denies 100% of *service-generated* rows; schema permits arbitrary strings. | `PROPOSED_DESIGN_INCOMPATIBILITY` | **MEDIUM** (was CRITICAL) | Clarifies D-01/D-02 implementation bounds | Reclassify to proposed design incompatibility; qualify 100% denial to service-emitted data. |
| `SEC-P07-STATUS-02` | Bare `String(50)` columns permit arbitrary writes by any database writer. | Confirmed at schema layer. Qualified: runtime persistence depends on table grants and RLS `WITH CHECK`. | `LOCAL_SOURCE_VERIFIED` / `CONDITIONAL_RUNTIME_RISK` | **MEDIUM** | Informing future CHECK constraint design | Retain schema finding; qualify concrete runtime capability on active ACL state. |
| `SEC-P07-CASCADE-01` | PostgreSQL FK cascade bypasses child RLS, proving database-only immutability is impossible. | Overclaim narrowed: FK cascade triggers run via SPI with `SECURITY_NOFORCE_RLS`, but parent DELETE must still be authorized. | `POSTGRESQL_ENGINE_DOCUMENTED` / `SOURCE_INFERENCE` | **HIGH** | Implicates `CASCADE-ROLE-DEL-01` & evidence retention | Clarify that parent authorization is required; distinguish runtime immutability from DBA immutability. |
| `SEC-P07-CASCADE-02` | `ON DELETE RESTRICT` at DB level is negated by ORM `cascade="all, delete-orphan"`. | Confirmed: ORM emits explicit child `DELETE` statements. Note: ORM child delete *is* subject to child RLS and child `DELETE` grants. | `LOCAL_SOURCE_VERIFIED` / `SOURCE_INFERENCE` | **HIGH** | Guides coordinated ORM/DB retention architecture | Retain finding; document that ORM child delete evaluates child RLS and grants unlike FK cascade. |
| `SEC-P07-SCOPE-01` | Permissive `FOR ALL` write policy grants cross-district SELECT access to experts/researchers across 33 districts. Assigned High severity. | Confirmed technically: permissive policies combine with OR; `FOR ALL` applies to SELECT. Severity discrepancy noted. | `SOURCE_INFERENCE` / `GOVERNANCE_RECONCILIATION` | **HIGH** (Technical) / **MEDIUM** (Canonical) | Directly maps to `RES-PULSE-01` | Maintain canonical `RES-PULSE-01` at MEDIUM; flag technical High severity for owner review. |
| `SEC-P07-WORKER-01` | Regional Pulse workers are operationally infeasible because RiskCast raises `DISPATCH_NOT_CONFIGURED`. | Overclaim narrowed: `run_riskcast_batch.py` is RiskCast-specific. Zero Regional Pulse workers exist in repo. | `LOCAL_SOURCE_VERIFIED` | **MEDIUM** (was HIGH) | Governed by `WRK-DISP-01` | Narrow to: no Regional Pulse worker implementation evidenced in source; outline outbox requirements. |
| `SEC-P07-API-RLS-01` | Current code causes researchers to crash on POST `/signals` with HTTP 500 due to RLS write policy omission. | **Factually incorrect for current code**: `backend/app/database/rls.py` (L928) already includes `RESEARCHER`. | `PROPOSED_DESIGN_INCOMPATIBILITY` | **LOW** (Current) / **HIGH** (Conditional) | Prevents breaking researcher API on policy hardening | Reclassify as future design conflict if narrower policy is adopted without API adjustment. |
| `SEC-P07-CHECK-01` | RLS `WITH CHECK` cannot enforce any state transitions whatsoever. | Overclaim corrected: `WITH CHECK` evaluates new rows only, but paired `USING` and `WITH CHECK` can restrict transition sets. | `POSTGRESQL_ENGINE_DOCUMENTED` / `DESIGN_RECOMMENDATION` | **MEDIUM** | Influences trigger vs RLS transition strategy | Explain limited transition enforcement via paired clauses; document triggers for multi-column rules. |
| `SEC-P07-MIGR-01` | `generate_privilege_grants_ddl()` not called in migration `a1089411c87d`, proving DB grants are unconfigured. | Confirmed migration absence. Qualified: does not prove live Neon ACL is empty (could be provisioned externally). | `LOCAL_SOURCE_VERIFIED` / `LIVE_DATABASE_UNVERIFIED` | **MEDIUM** | Maintains `DB-GRANT-APPLY-01` as PROPOSED | Retain migration finding; qualify live database ACL as unverified in Mode A. |
| `SEC-P07-LIVE-01` | Physical branch provisioning remains unverified in Mode A (blocked by credential rotation). | Causal link withdrawn: governance register does not link GATE-01 execution to credential rotation. | `WITHDRAWN_AS_UNSUPPORTED` (Causal Link) | **INFO** (Governance Clarification) | Clarifies GATE-01 vs `DB-CREDENTIAL-EXPOSURE-01` | Remove causal link; preserve GATE-01 approval, Mode A unverified status, and credential exposure separately. |

---

### 4.1 Detailed Reassessment of Individual Findings

#### 4.1.1 SEC-P07-STATUS-01: Corrected Status Vocabulary and Predicate Analysis
- **Finding Reference:** `SEC-P07-STATUS-01`
- **Previous Assertion:** The status `'PUBLISHED'` does not exist in the codebase, and `'OFFICIAL_ADVISORY'` is a `confidence_tier`, not a validation status. Any public SELECT policy relying on `validation_status IN ('PUBLISHED', 'OFFICIAL_ADVISORY')` would evaluate to `FALSE` for 100% of rows, completely denying legitimate farmer reads. Assigned Critical severity.
- **Corrected Conclusion:** 
  1. The string `'PUBLISHED'` does exist in the repository within Stage 12 Knowledge Commons models (`backend/app/models/commons_contribution.py`, `backend/app/models/extension_learning.py`, `backend/app/models/research_hub.py`, `backend/app/services/commons_service.py`), but is **not** part of the `RegionalSignal` lifecycle.
  2. In `RegionalSignal`, `'OFFICIAL_ADVISORY'` is a `confidence_tier`, whereas the corresponding service-generated validation status is `'OFFICIAL_ALERT'`.
  3. The statement that the predicate denies "100% of all possible database rows" was an overclaim. Because `regional_signals.validation_status` is an unconstrained `VARCHAR(50)` column without a database `CHECK` constraint or `ENUM` type, an authorized SQL writer could theoretically insert `'PUBLISHED'`. The accurate finding is that the predicate would fail to match 100% of *service-generated rows* emitted by `RegionalPulseService`.
  4. The predicate was introduced in an earlier design proposal (`PHASE_07_REGIONAL_PULSE_COMMAND_SCOPE_RLS_AND_TRUSTED_PROVENANCE_DESIGN_ASSURANCE_REPORT.md`), not in active code.
- **Evidence Classification:** `PROPOSED_DESIGN_INCOMPATIBILITY`
- **Severity and Confidence:** Severity: **MEDIUM** (reclassified from CRITICAL). Confidence: **HIGH**.
- **Exact Source References:** `backend/app/models/regional_pulse.py` (L23-28), `backend/app/services/regional_pulse_service.py` (L180-215, L340, L379, L442, L560), `docs/pilot/security/PHASE_07_REGIONAL_PULSE_COMMAND_SCOPE_RLS_AND_TRUSTED_PROVENANCE_DESIGN_ASSURANCE_REPORT.md` (L145).
- **Preconditions:** Application of the proposed public read predicate without schema constraints or service adjustments.
- **What is Directly Proven:** `RegionalPulseService` never emits `'PUBLISHED'`. It emits `'OFFICIAL_ALERT'`, `'UNVALIDATED_OBSERVATION'`, `'EXPERT_CONFIRMED'`, `'ADMIN_CONFIRMED'`, and `'SUPPRESSED_INSUFFICIENT_PROVENANCE'`.
- **What Remains Conditional or Unverified:** What raw strings exist in live Neon staging/production tables (`LIVE_DATABASE_UNVERIFIED`).
- **Counterarguments Considered:** Could `'PUBLISHED'` be written by another module? No, `RegionalSignal` is managed exclusively by `RegionalPulseService`.
- **Canonical Association:** Decisions D-01, D-02.
- **Recommended Future Action:** Reject the flawed predicate; adopt an RLS policy aligned with actual service statuses: `validation_status IN ('EXPERT_CONFIRMED', 'ADMIN_CONFIRMED', 'OFFICIAL_ALERT')`.
- **Owner Authorization Required:** Yes (aligns with Decision D-01/D-02 sign-off).

#### 4.1.2 SEC-P07-STATUS-02: Status Constraint and Writer Authority
- **Finding Reference:** `SEC-P07-STATUS-02`
- **Previous Assertion:** Bare `String(50)` columns permit arbitrary writes by any database writer. Status contract enforcement exists exclusively within application service logic.
- **Corrected Conclusion:** 
  1. SQLAlchemy models and Alembic migrations define `validation_status` and `confidence_tier` as bare `String(50)` without `CHECK` constraints, database `ENUM`s, or Pydantic `Enum`/`Literal` validation (`LOCAL_SOURCE_VERIFIED`).
  2. However, the assertion that a *concrete runtime principal* (e.g. `acrevia_staging_app`) can persist arbitrary strings is conditional upon active table-level privileges (`INSERT`/`UPDATE`) and RLS `WITH CHECK` policies (`CONDITIONAL_RUNTIME_RISK`). Schema capability must not be conflated with authorized runtime execution.
- **Evidence Classification:** `LOCAL_SOURCE_VERIFIED` (schema) / `CONDITIONAL_RUNTIME_RISK` (runtime write).
- **Severity and Confidence:** Severity: **MEDIUM**. Confidence: **HIGH**.
- **Exact Source References:** `backend/app/models/regional_pulse.py` (L23-28), `backend/app/schemas/regional_pulse.py` (L15-25), `backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py`.
- **Preconditions:** Direct SQL access or API bypass by an actor holding table write privileges.
- **What is Directly Proven:** Neither PostgreSQL schema DDL nor SQLAlchemy models define constraints on status strings.
- **What Remains Conditional or Unverified:** Active grants on `regional_signals` in Neon Cloud (`LIVE_DATABASE_UNVERIFIED`).
- **Counterarguments Considered:** Does Pydantic validate the string? No, `backend/app/schemas/regional_pulse.py` defines bare `str`.
- **Canonical Association:** Blocker `RLS-WRITE-AUTH-01`, Decision DB-AUTH-01.
- **Recommended Future Action:** Design a database `CHECK` constraint covering all 5 service-emitted statuses.
- **Owner Authorization Required:** Yes (schema migration).

#### 4.1.3 SEC-P07-CASCADE-01: Referential-Integrity Cascade Behavior
- **Finding Reference:** `SEC-P07-CASCADE-01`
- **Previous Assertion:** Database FK cascade completely bypasses child table RLS, making database-only evidence immutability impossible.
- **Corrected Conclusion:** 
  1. Under PostgreSQL engine mechanics (`ri_triggers.c`), internal FK cascade deletion (`RI_FKey_cascade_del`) executes under Server Programming Interface (SPI) with `SECURITY_NOFORCE_RLS`. It deletes child rows without evaluating child RLS and without requiring child `DELETE` privileges (`POSTGRESQL_ENGINE_DOCUMENTED`).
  2. However, this does *not* bypass every security boundary: the parent `DELETE` statement must first be authorized under parent table privileges and parent RLS.
  3. Absolute immutability against database superusers is impossible, but `APPEND_ONLY_FOR_RUNTIME_ROLES` is achievable by revoking parent and child `DELETE` privileges from application roles.
- **Evidence Classification:** `POSTGRESQL_ENGINE_DOCUMENTED` / `SOURCE_INFERENCE`.
- **Severity and Confidence:** Severity: **HIGH**. Confidence: **HIGH**.
- **Exact Source References:** `backend/app/models/regional_pulse.py` (L55), PostgreSQL source `src/backend/utils/adt/ri_triggers.c`.
- **Preconditions:** Successful execution of an authorized parent `DELETE` statement.
- **What is Directly Proven:** Database FK definition has `ondelete="CASCADE"`. PostgreSQL SPI deletes referencing rows without child RLS evaluation.
- **What Remains Conditional or Unverified:** Live database catalog trigger definition in Neon Cloud.
- **Counterarguments Considered:** Does FORCE RLS affect FK triggers? PostgreSQL documentation confirms FK triggers use `SECURITY_NOFORCE_RLS`.
- **Canonical Association:** Blocker `CASCADE-ROLE-DEL-01`.
- **Recommended Future Action:** Transition FK constraint to `ON DELETE RESTRICT` or `NO ACTION` in future migration.
- **Owner Authorization Required:** Yes (schema migration).

#### 4.1.4 SEC-P07-CASCADE-02: ORM Cascade and Restrictive FK Interaction
- **Finding Reference:** `SEC-P07-CASCADE-02`
- **Previous Assertion:** Restricting FK to `ON DELETE RESTRICT` alone is insufficient because SQLAlchemy's relationship defines `cascade="all, delete-orphan"`, scheduling child deletions before parent deletion.
- **Corrected Conclusion:** 
  1. Confirmed: SQLAlchemy's Unit of Work handles `cascade="all, delete-orphan"` by emitting explicit `DELETE FROM regional_signal_evidences WHERE id = ...` before deleting the parent.
  2. Crucial Nuance: Unlike internal database FK cascades, explicit ORM child `DELETE` statements *do* evaluate child table RLS and *do* require child table `DELETE` privileges.
  3. Coordinated Hardening: True evidence retention requires both removing ORM orphan deletion (or configuring `passive_deletes=True`) AND setting database FK to `RESTRICT`.
- **Evidence Classification:** `LOCAL_SOURCE_VERIFIED` / `SOURCE_INFERENCE`.
- **Severity and Confidence:** Severity: **HIGH**. Confidence: **HIGH**.
- **Exact Source References:** `backend/app/models/regional_pulse.py` (L35), SQLAlchemy Unit of Work documentation.
- **Preconditions:** Application-level invocation of `session.delete(signal)` or `signal.evidences.remove(ev)`.
- **What is Directly Proven:** `RegionalSignal.evidences` defines `cascade="all, delete-orphan"`.
- **What Remains Conditional or Unverified:** Whether runtime role has `DELETE` grant on `regional_signal_evidences`.
- **Counterarguments Considered:** Does `passive_deletes` alone suffice? No, without DB `RESTRICT`, parent delete triggers DB cascade.
- **Canonical Association:** Blocker `CASCADE-ROLE-DEL-01`.
- **Recommended Future Action:** Remove `delete-orphan` from relationship, configure `passive_deletes=True`, pair with DB FK `RESTRICT`.
- **Owner Authorization Required:** Yes (code and schema change).

#### 4.1.5 SEC-P07-SCOPE-01: Permissive Policy Composition and Cross-District SELECT
- **Finding Reference:** `SEC-P07-SCOPE-01`
- **Previous Assertion:** Permissive `regional_signals_author_write_policy` (`FOR ALL`) applies to SELECT under PostgreSQL rules, combining with logical OR against public read, granting cross-district visibility across all 33 districts. Assigned High severity.
- **Corrected Conclusion:** 
  1. Confirmed technically: PostgreSQL combines permissive policies with logical `OR`. A policy created `FOR ALL` applies to `SELECT`, `INSERT`, `UPDATE`, and `DELETE`.
  2. In `backend/app/database/rls.py`, `regional_signals_author_write_policy` contains a role subquery checking `ADMIN`, `AGRICULTURAL_EXPERT`, and `RESEARCHER` with no district filter. When an actor with one of these roles queries `regional_signals`, the policy grants row eligibility across all rows, including suppressed, unvalidated, and cross-district signals.
  3. Severity Discrepancy: The technical severity is High, but canonical governance register records `RES-PULSE-01` at **MEDIUM**. The canonical severity must not be unilaterally changed without Project Owner approval.
- **Evidence Classification:** `SOURCE_INFERENCE` / `GOVERNANCE_RECONCILIATION`.
- **Severity and Confidence:** Technical Severity: **HIGH**. Canonical Governance Severity: **MEDIUM**. Confidence: **HIGH**.
- **Exact Source References:** `backend/app/database/rls.py` (L921-968), `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md` (RES-PULSE-01).
- **Preconditions:** Actor possesses role `AGRICULTURAL_EXPERT` or `RESEARCHER` and database role has `SELECT` grant.
- **What is Directly Proven:** The generated SQL policy uses `FOR ALL` and contains no district predicate.
- **What Remains Conditional or Unverified:** Active data distribution across districts in staging/production.
- **Counterarguments Considered:** Does the public read policy restrict them? No, permissive policies combine with `OR`.
- **Canonical Association:** Blocker/Residual Risk `RES-PULSE-01`.
- **Recommended Future Action:** Split `FOR ALL` write policy into command-scoped policies (`FOR INSERT`, `FOR UPDATE`), removing `SELECT`.
- **Owner Authorization Required:** Yes (governance severity reconciliation & DDL modification).

#### 4.1.6 SEC-P07-WORKER-01: Worker Infrastructure and Dispatch Feasibility
- **Finding Reference:** `SEC-P07-WORKER-01`
- **Previous Assertion:** Recommending an asynchronous worker for provenance revalidation is currently operationally infeasible because `run_riskcast_batch.py` raises `ProductionDispatchBlockedError: DISPATCH_NOT_CONFIGURED`.
- **Corrected Conclusion:** 
  1. `run_riskcast_batch.py` is specifically a RiskCast batch processing task. Its dispatch guard does not govern Regional Pulse.
  2. Inspection of `backend/app/tasks/` reveals zero Regional Pulse tasks or worker dispatch implementations.
  3. Narrowing: The accurate finding is that *no configured Regional Pulse worker dispatch implementation was evidenced in the inspected repository source*.
  4. Repository absence proves no local implementation exists; it does not constitute proof of external cloud worker state.
- **Evidence Classification:** `LOCAL_SOURCE_VERIFIED`.
- **Severity and Confidence:** Severity: **MEDIUM** (reclassified from HIGH). Confidence: **HIGH**.
- **Exact Source References:** `backend/app/tasks/run_riskcast_batch.py` (L40-75), `backend/app/tasks/`.
- **Preconditions:** Execution of background task in staging/production environment.
- **What is Directly Proven:** No worker task exists for Regional Pulse in `backend/app/tasks/`.
- **What Remains Conditional or Unverified:** External task runners or schedulers outside the repository.
- **Counterarguments Considered:** Can Celery be configured via environment variables? No task definitions exist in source.
- **Canonical Association:** Blocker `WRK-DISP-01`.
- **Recommended Future Action:** Design a Transactional Outbox pattern before introducing worker dependencies.
- **Owner Authorization Required:** Yes (architecture design sign-off).

#### 4.1.7 SEC-P07-API-RLS-01: Researcher POST Contract Alignment
- **Finding Reference:** `SEC-P07-API-RLS-01`
- **Previous Assertion:** Current implementation causes researchers to crash on `POST /regional-pulse/signals` with HTTP 500 / SQLSTATE `42501` due to a mismatch between endpoint authorization and RLS write policy.
- **Corrected Conclusion:** 
  1. **Factually incorrect for current code baseline.** In `backend/app/database/rls.py` (line 928), `regional_signals_author_write_policy` explicitly includes `'RESEARCHER'`.
  2. In `backend/app/api/v1/endpoints/regional_pulse.py` (line 75), `require_roles` also permits `UserRole.RESEARCHER`.
  3. Both layers currently match. The mismatch was introduced exclusively in an earlier *proposed narrower RLS policy*.
  4. Reclassified as a conditional future design incompatibility.
- **Evidence Classification:** `PROPOSED_DESIGN_INCOMPATIBILITY`.
- **Severity and Confidence:** Current Severity: **LOW** (no defect). Conditional Severity: **HIGH** (if proposed policy applied). Confidence: **HIGH**.
- **Exact Source References:** `backend/app/database/rls.py` (L928), `backend/app/api/v1/endpoints/regional_pulse.py` (L75).
- **Preconditions:** Modification of RLS write expression to exclude `RESEARCHER` without adjusting the endpoint.
- **What is Directly Proven:** Current generated RLS DDL and current API route both include `RESEARCHER`.
- **What Remains Conditional or Unverified:** Whether active live database in Neon has custom DDL applied.
- **Counterarguments Considered:** Did previous tests fail for researchers? Previous tests simulated the *proposed* policy, not the current DDL.
- **Canonical Association:** Blocker `EXP-AUTH-01`, Decision DB-AUTH-01.
- **Recommended Future Action:** Ensure any future RLS policy narrowing coordinates with endpoint role dependencies.
- **Owner Authorization Required:** Yes.

#### 4.1.8 SEC-P07-CHECK-01: USING and WITH CHECK State-Transition Capabilities
- **Finding Reference:** `SEC-P07-CHECK-01`
- **Previous Assertion:** RLS `WITH CHECK` clauses cannot enforce state transitions, so RLS cannot participate in status lifecycle control.
- **Corrected Conclusion:** 
  1. PostgreSQL `WITH CHECK` evaluates only the proposed new row values (`NEW.*`) and cannot reference pre-update values (`OLD.*`). Conversely, `USING` on an UPDATE policy evaluates only existing row values (`OLD.*`).
  2. Correction: Paired `USING` and `WITH CHECK` clauses on a command-scoped `FOR UPDATE` policy *can* enforce constrained state transitions. For example:
     `CREATE POLICY p ON t FOR UPDATE USING (status = 'UNVALIDATED') WITH CHECK (status = 'CONFIRMED');`
     guarantees that only rows currently in `'UNVALIDATED'` can be updated, and their resulting status must be `'CONFIRMED'`.
  3. Limitation: When multiple permissive policies exist, they combine with `OR`, which can broaden allowed transitions. Complex multi-column transitions or transitions requiring actor attribution are better enforced via database triggers or row-locked service transactions.
- **Evidence Classification:** `POSTGRESQL_ENGINE_DOCUMENTED` / `DESIGN_RECOMMENDATION`.
- **Severity and Confidence:** Severity: **MEDIUM**. Confidence: **HIGH**.
- **Exact Source References:** PostgreSQL documentation (Chapter on Row Security Policies), `backend/app/database/rls.py`.
- **Preconditions:** Command-scoped `FOR UPDATE` policy definition.
- **What is Directly Proven:** `USING` evaluates `OLD.*`; `WITH CHECK` evaluates `NEW.*`.
- **What Remains Conditional or Unverified:** Interaction with other concurrent permissive policies.
- **Counterarguments Considered:** Can RLS prevent status rollback? Yes, via targeted `USING`/`WITH CHECK` pairs.
- **Canonical Association:** Blocker `RLS-WRITE-AUTH-01`.
- **Recommended Future Action:** Design targeted UPDATE policies for status transitions; supplement with triggers for complex rules.
- **Owner Authorization Required:** Yes.

#### 4.1.9 SEC-P07-MIGR-01: Privilege Grant Generator Callsite in Migrations
- **Finding Reference:** `SEC-P07-MIGR-01`
- **Previous Assertion:** `generate_privilege_grants_ddl()` is not called in migration `a1089411c87d`, proving that staging database table privileges are unconfigured or empty.
- **Corrected Conclusion:** 
  1. Confirmed: Migration `a1089411c87d_enable_postgresql_rls_tenant_isolation.py` calls `generate_rls_ddl()` but does **not** call `generate_privilege_grants_ddl()`.
  2. Qualification: Absence of the callsite in this migration proves that Alembic does not manage table grants. It does *not* prove that live database grants are absent in Neon staging (grants could be applied via external scripts or DBA actions).
  3. Governance Status: `DB-GRANT-APPLY-01` remains classified as `PROPOSED — OWNER APPROVAL REQUIRED`.
- **Evidence Classification:** `LOCAL_SOURCE_VERIFIED` (migration) / `LIVE_DATABASE_UNVERIFIED` (live ACL).
- **Severity and Confidence:** Severity: **MEDIUM**. Confidence: **HIGH**.
- **Exact Source References:** `backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py` (L1-85), `backend/app/database/rls.py` (L977-1050).
- **Preconditions:** Alembic migration execution as the sole provisioning mechanism.
- **What is Directly Proven:** Migration `a1089411c87d` contains zero `GRANT` statements and no call to `generate_privilege_grants_ddl()`.
- **What Remains Conditional or Unverified:** Active grants in live Neon database (`LIVE_DATABASE_UNVERIFIED`).
- **Counterarguments Considered:** Could grants be executed in another migration? Inspection of all migrations reveals no other RLS grant callsites.
- **Canonical Association:** Item `DB-GRANT-APPLY-01`.
- **Recommended Future Action:** Create an owner-authorized migration or provisioning script to apply `PRIVILEGE_CROSSWALK`.
- **Owner Authorization Required:** Yes (Decision DB-AUTH-01 sign-off).

#### 4.1.10 SEC-P07-LIVE-01: Withdrawal of Credential Rotation Causal Link
- **Finding Reference:** `SEC-P07-LIVE-01`
- **Previous Assertion:** Physical branch provisioning of GATE-01 remains unverified in Mode A "(blocked by credential rotation)".
- **Corrected Conclusion:** 
  1. Inspection of `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md` reveals that GATE-01 was formally approved by the Project Owner on 2026-11-10.
  2. The governance register contains **no causal dependency** linking GATE-01 provisioning to credential rotation.
  3. Credential rotation is an independent open security finding (`DB-CREDENTIAL-EXPOSURE-01`).
  4. The causal statement is formally withdrawn as unsupported by repository records. GATE-01 physical verification remains unverified solely due to Mode A restrictions.
- **Evidence Classification:** `WITHDRAWN_AS_UNSUPPORTED` (causal link) / `LOCAL_SOURCE_VERIFIED` (register).
- **Severity and Confidence:** Severity: **INFO** (Governance Correction). Confidence: **HIGH**.
- **Exact Source References:** `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md` (L28, L59).
- **Preconditions:** Governance register interpretation.
- **What is Directly Proven:** GATE-01 is marked `[x] APPROVED BY OWNER (2026-11-10)`. No credential blocker is cited in GATE-01 scope.
- **What Remains Conditional or Unverified:** Physical status of Neon branch in Singapore (`LIVE_DATABASE_UNVERIFIED`).
- **Counterarguments Considered:** Does credential exposure pose operational risk? Yes, but governance does not define it as a prerequisite for branch creation.
- **Canonical Association:** Blocker `GATE01-PROV-01`, Blocker `DB-CREDENTIAL-EXPOSURE-01`.
- **Recommended Future Action:** Maintain GATE-01 and `DB-CREDENTIAL-EXPOSURE-01` as separate governance items.
- **Owner Authorization Required:** No.

---

## 5. CORRECTED REGIONALSIGNAL STATUS VOCABULARY

### 5.1 Authoritative Service-Emitted Lifecycle
An exhaustive audit of `backend/app/services/regional_pulse_service.py` (lines 180–570) and `backend/app/models/regional_pulse.py` (lines 20–35) establishes the exact status lifecycle emitted by application logic:

```
[Signal Created]
       |
       +---> Actor has ADMIN & confidence_tier == "OFFICIAL_ADVISORY"
       |        ==> validation_status = "OFFICIAL_ALERT"
       |
       +---> Actor has AGRICULTURAL_EXPERT (without ADMIN advisory)
       |        ==> validation_status = "EXPERT_CONFIRMED"
       |
       +---> Ordinary Farmer / Community Aggregation (distinct_farms >= 3)
                ==> validation_status = "UNVALIDATED_OBSERVATION"
       
[Provenance Revalidation on Read / Scheduled]
       |
       +---> Evidence count < 3 AND distinct_farms < 3
                ==> validation_status = "SUPPRESSED_INSUFFICIENT_PROVENANCE"

[Administrative / Expert Recovery]
       |
       +---> Actor has AGRICULTURAL_EXPERT
       |        ==> validation_status = "EXPERT_CONFIRMED"
       |
       +---> Actor has ADMIN (non-expert)
                ==> validation_status = "ADMIN_CONFIRMED"
```

The five concrete lifecycle statuses emitted by the service are:
1. `UNVALIDATED_OBSERVATION`: Initial state for community-aggregated signals ($N \ge 3$) lacking prior agronomic validation. Governed by **Decision D-03**.
2. `EXPERT_CONFIRMED`: Established when an `AGRICULTURAL_EXPERT` validates or directly creates an agronomic observation.
3. `ADMIN_CONFIRMED`: Assigned when an `ADMIN` recovers a suppressed signal or confirms a non-expert observation without holding an expert agronomic credential.
4. `OFFICIAL_ALERT`: Assigned exclusively when an `ADMIN` publishes a state-level agricultural advisory ($N = 0$). Governed by **Decision D-01**.
5. `SUPPRESSED_INSUFFICIENT_PROVENANCE`: Assigned during provenance revalidation when a signal fails minimum farm support thresholds ($N < 3$).

### 5.2 Confidence Tiers vs. Validation Statuses
In `backend/app/models/regional_pulse.py` (line 23), `confidence_tier` is an orthogonal domain attribute representing telemetry origin, distinct from lifecycle status:
- `FARMER_REPORT`
- `MULTIPLE_INDEPENDENT`
- `AI_ASSISTED`
- `EXPERT_REVIEWED`
- `OFFICIAL_ADVISORY`

Conflating `confidence_tier` with `validation_status` introduces severe SQL syntax and semantic errors into RLS policies. In particular, `'OFFICIAL_ADVISORY'` is a `confidence_tier` value; its corresponding lifecycle validation status is `'OFFICIAL_ALERT'`.

### 5.3 Codebase Presence of 'PUBLISHED'
The previous report asserted that the string `'PUBLISHED'` "does not exist in the codebase." This statement is inaccurate:
- `'PUBLISHED'` is actively used in Stage 12 Knowledge Commons models:
  - `backend/app/models/commons_contribution.py`
  - `backend/app/models/extension_learning.py`
  - `backend/app/models/research_hub.py`
  - `backend/app/services/commons_service.py`
  - `backend/app/services/extension_service.py`
  - `backend/app/database/rls.py` (line 780, Knowledge Contributions public read policy)
- However, `'PUBLISHED'` is **completely absent** from the `RegionalSignal` domain model, schemas, migrations, and service logic.

### 5.4 Historical Origin and Corrected Assessment of the Predicate
The flawed predicate:
```sql
validation_status IN ('PUBLISHED', 'OFFICIAL_ADVISORY')
```
originated in an untracked earlier design document: `docs/pilot/security/PHASE_07_REGIONAL_PULSE_COMMAND_SCOPE_RLS_AND_TRUSTED_PROVENANCE_DESIGN_ASSURANCE_REPORT.md` (line 145).

#### Corrected Technical Assessment
1. **Service-Emitted Matching:** This predicate matches **0% of service-generated rows** emitted by `RegionalPulseService`. Neither `'PUBLISHED'` nor `'OFFICIAL_ADVISORY'` is ever assigned to `RegionalSignal.validation_status`.
2. **Database Contract Nuance:** Stating that the predicate denies "100% of all possible database rows" was an overclaim because `regional_signals.validation_status` is an unconstrained `VARCHAR(50)` column in PostgreSQL. An authorized SQL writer could insert `'PUBLISHED'`.
3. **Defensible Conclusion:** The predicate fails to match 100% of *currently observed service-generated data*. Because this predicate exists only in design documentation, it is classified as a `PROPOSED_DESIGN_INCOMPATIBILITY`.

---

## 6. DATABASE STATUS-CONSTRAINT ASSESSMENT

### 6.1 Storage Types and Missing Enums (`LOCAL_SOURCE_VERIFIED`)
Inspection of the storage and schema layers confirms:
- **SQLAlchemy Model:** `RegionalSignal.validation_status` is defined as `Mapped[str] = mapped_column(String(50), default="UNVALIDATED_OBSERVATION", nullable=False)`.
- **Pydantic Schemas:** `RegionalSignalCreate` and `RegionalSignalResponse` define `validation_status: str`.
- **Alembic Migrations:** Migration `a1089411c87d` creates the column as PostgreSQL native type `character varying(50)`.
- **Constraints:** Zero PostgreSQL `CHECK` constraints, zero PostgreSQL `ENUM` types, and zero database trigger constraints exist on `regional_signals.validation_status` or `regional_signals.confidence_tier`.

### 6.2 Schema Capability vs. Runtime Writer Authority
While the PostgreSQL schema layer accepts arbitrary string values (e.g. `'GARBAGE'`, `'SUSPENDED'`, `'PUBLISHED'`), the ability of a concrete runtime principal (such as `acrevia_staging_app`) to persist arbitrary strings depends on:
1. Whether the database role possesses `INSERT` or `UPDATE` privileges on `regional_signals`.
2. Whether the active RLS `WITH CHECK` policy allows the row modification.
3. Whether application service code overrides client-supplied statuses (which `RegionalPulseService.create_signal` does on lines 190–205).

A schema capability must not be conflated with authorized runtime execution. Direct SQL access is required to exploit the lack of database status constraints.

### 6.3 Evaluation of Proposed CHECK Constraint
To establish defense-in-depth against direct SQL corruption, a future database `CHECK` constraint should be introduced:
```sql
ALTER TABLE regional_signals
ADD CONSTRAINT chk_regional_signals_validation_status
CHECK (validation_status IN (
    'UNVALIDATED_OBSERVATION',
    'EXPERT_CONFIRMED',
    'ADMIN_CONFIRMED',
    'OFFICIAL_ALERT',
    'SUPPRESSED_INSUFFICIENT_PROVENANCE'
));
```
This constraint covers all five service-emitted statuses, ensuring that valid community observations, administrative recoveries, official alerts, and suppression states remain fully permissible.

---

## 7. RLS PERMISSIVE-POLICY COMPOSITION

### 7.1 PostgreSQL Engine Semantics: Logical OR Composition
Under PostgreSQL row-level security mechanics (`src/backend/rewrite/rowsecurity.c`):
- Multiple policies defined as `AS PERMISSIVE` for the same command combine using **logical OR**:
  $$\text{Visible Rows} = \text{Policy}_1 \lor \text{Policy}_2 \lor \dots \lor \text{Policy}_n$$
- A policy defined `FOR ALL` applies to all SQL commands: `SELECT`, `INSERT`, `UPDATE`, and `DELETE`.
- Consequently, an actor executing a `SELECT` statement evaluates both the dedicated `FOR SELECT` policy AND any `FOR ALL` policy defined on the table.

### 7.2 Current Generated Policies for Regional Pulse
In `backend/app/database/rls.py` (lines 955–968), the generated DDL creates two policies for `regional_signals`:

1. **Public Read Policy:**
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

2. **Author Write Policy:**
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

### 7.3 Effective SELECT Evaluation for Privileged Roles
When an actor with role `AGRICULTURAL_EXPERT` or `RESEARCHER` queries `regional_signals`:
$$\begin{aligned}
\text{USING} &= \text{public\_read\_policy.USING} \lor \text{author\_write\_policy.USING} \\
&= (\text{distinct\_farms} \ge 3 \land \text{status} \ne \text{'SUSPENDED'}) \\
&\quad \lor (\text{actor has role IN ('ADMIN', 'AGRICULTURAL\_EXPERT', 'RESEARCHER')})
\end{aligned}$$
Because the actor holds a matching role, the second clause evaluates to `TRUE`. The policy grants row eligibility for **every row** in `regional_signals`, regardless of `distinct_farms_count` or `validation_status`.

---

## 8. CORRECTED RESEARCHER/API/RLS COMPATIBILITY ASSESSMENT

### 8.1 Current Code Baseline Alignment (`PUBLIC_SOURCE_VERIFIED`)
A critical errata correction concerns previous finding `SEC-P07-API-RLS-01`. The previous report asserted that the current codebase contains a contract mismatch that causes researchers to crash on `POST /regional-pulse/signals` with HTTP 500 / SQLSTATE `42501`.

Inspection of the actual source code demonstrates that this assertion is **factually false** for the current baseline:

1. **FastAPI Endpoint Authorization:**
   In `backend/app/api/v1/endpoints/regional_pulse.py` (line 75):
   ```python
   @router.post("/signals", response_model=RegionalSignalResponse, status_code=status.HTTP_201_CREATED)
   def create_signal(
       signal_in: RegionalSignalCreate,
       db: Session = Depends(deps.get_db),
       current_user: User = Security(
           deps.require_roles(UserRole.ADMIN, UserRole.AGRICULTURAL_EXPERT, UserRole.RESEARCHER)
       ),
   ) -> Any:
   ```
   The API route explicitly authorizes `RESEARCHER`.

2. **Generated RLS Write Policy Expression:**
   In `backend/app/database/rls.py` (lines 925–930):
   ```python
   AND ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')
   ```
   The generated RLS write policy expression explicitly authorizes `RESEARCHER`.

### 8.2 Reclassification to Proposed Design Incompatibility
Both the API endpoint and the generated RLS write policy currently permit `RESEARCHER`. There is zero contract mismatch in the baseline repository.

The mismatch arose exclusively within an earlier *proposed narrower RLS policy* from a prior audit report that proposed restricting `regional_signals_author_write_policy` to `('ADMIN', 'AGRICULTURAL_EXPERT')` without simultaneously updating `backend/app/api/v1/endpoints/regional_pulse.py`.

Therefore, `SEC-P07-API-RLS-01` is formally reclassified from an active defect to:
$$\text{Classification} = \mathbf{PROPOSED\_DESIGN\_INCOMPATIBILITY}$$
If the project adopts a narrower RLS policy in the future, the API endpoint must be updated in tandem to prevent HTTP 500 / `42501` exceptions for researchers.

---

## 9. CORRECTED USING / WITH CHECK STATE-TRANSITION ANALYSIS

### 9.1 PostgreSQL Engine UPDATE Policy Semantics
Authoritative PostgreSQL documentation establishes the precise roles of `USING` and `WITH CHECK` during an `UPDATE` operation:
- `USING (predicate)`: Evaluates against the **pre-update row** (`OLD.*`). A row is visible and eligible to be updated if and only if `USING` evaluates to `TRUE`.
- `WITH CHECK (predicate)`: Evaluates against the **proposed post-update row** (`NEW.*`). The update succeeds if and only if `WITH CHECK` evaluates to `TRUE`.

### 9.2 Can RLS Enforce State Transitions?
The previous report asserted that RLS "cannot enforce any state transitions whatsoever" because `WITH CHECK` cannot reference `OLD.*`. 

This conclusion was overly broad. While it is true that `WITH CHECK` cannot directly compare `NEW.col` to `OLD.col` within a single expression, a command-scoped `FOR UPDATE` policy pairing `USING` and `WITH CHECK` **can enforce constrained state transitions**:

```sql
-- Example: Allow transitioning ONLY from UNVALIDATED to EXPERT_CONFIRMED
CREATE POLICY regional_signals_expert_confirm_policy ON regional_signals
    FOR UPDATE
    TO acrevia_staging_app
    USING (
        validation_status = 'UNVALIDATED_OBSERVATION'
        AND current_setting('app.actor_roles', true) LIKE '%AGRICULTURAL_EXPERT%'
    )
    WITH CHECK (
        validation_status = 'EXPERT_CONFIRMED'
    );
```
Under this policy:
1. `USING` guarantees that an actor can only target rows currently in `'UNVALIDATED_OBSERVATION'`. Rows in any other status return 0 matching rows.
2. `WITH CHECK` guarantees that the resulting row must have `validation_status = 'EXPERT_CONFIRMED'`. Any attempt to set another status fails with SQLSTATE `44000` (`check_violation`).

### 9.3 Architectural Boundaries and Limitations
While paired clauses enable simple transitions, significant limitations exist:
1. **Permissive Policy Composition:** If multiple permissive `UPDATE` policies exist, they combine with `OR`, which can create unintended transition bypasses.
2. **Actor Attribution & Audit Trails:** RLS policies cannot easily write audit log entries or capture previous state history.
3. **Complex Multi-Field Invariants:** Transitions requiring verification of evidence counts, cryptographic signatures, or dual-party approvals are best handled via row-locked database triggers (`BEFORE UPDATE`) or tightly controlled application service transactions.

---

## 10. ROLE-BASED CROSS-DISTRICT READ-SCOPE ASSESSMENT

### 10.1 Absence of District Predicates in Generated Policies
Inspection of `backend/app/database/rls.py` (lines 900–931) demonstrates that neither `regional_signals_public_read_policy` nor `regional_signals_author_write_policy` contains any district-level filtering:
- There is no `district_id = current_setting('app.current_district', true)`.
- There is no tenant or district foreign key boundary on `regional_signals`.

### 10.2 Exposure Analysis Across 33 Districts
Because `regional_signals_author_write_policy` uses `FOR ALL` and includes `ADMIN`, `AGRICULTURAL_EXPERT`, and `RESEARCHER`, any user holding one of these roles is granted SELECT row eligibility across all 33 administrative districts of Telangana.

This grants privileged actors visibility into:
1. Community signals that fail the privacy threshold ($N < 3$ distinct farms).
2. Unvalidated observations from other jurisdictions.
3. Signals suppressed due to provenance anomalies.

### 10.3 Canonical Governance Severity Reconciliation
The previous report designated this finding (`SEC-P07-SCOPE-01`) as **HIGH** severity. 

However, in the canonical governance register (`docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`), canonical blocker and residual risk **`RES-PULSE-01`** is formally recorded at **`MEDIUM`** severity:

| Item ID | Canonical Description | Recorded Severity | Technical Assessment | Required Governance Action |
|---|---|---|---|---|
| `RES-PULSE-01` | Regional Pulse RLS broad expert/researcher SELECT scope | **MEDIUM** | **HIGH** | Maintain canonical Medium severity in register; submit technical High severity for Project Owner review. |

In accordance with strict MODE A governance rules, the auditor cannot unilaterally upgrade a canonical governance severity. The technical finding is documented as High severity, while the governance record remains at Medium pending Project Owner sign-off.

---

## 11. POSTGRESQL AND ORM CASCADE DISTINCTION

### 11.1 PostgreSQL Referential-Integrity Internals (`POSTGRESQL_ENGINE_DOCUMENTED`)
Inspection of PostgreSQL kernel source code (`src/backend/utils/adt/ri_triggers.c`) reveals the exact referential integrity mechanisms:
- When a table is declared with `ON DELETE CASCADE`, PostgreSQL attaches an internal system trigger (`RI_FKey_cascade_del`).
- This trigger executes within the Server Programming Interface (SPI) under `SECURITY_NOFORCE_RLS`.
- **Key Execution Fact:** The cascade trigger bypasses row-level security on the referencing (child) table. It does **not** evaluate child RLS policies, and it does **not** require the invoking user to possess table-level `DELETE` privileges on the child table.
- **Authorization Boundary:** However, this internal cascade occurs **only if the parent DELETE statement is successfully authorized**. If the actor lacks `DELETE` privileges on the parent table (`regional_signals`) or fails the parent table's RLS policy, the parent DELETE statement fails, and the FK cascade is never initiated.

### 11.2 SQLAlchemy Unit of Work Deletion Mechanics
In `backend/app/models/regional_pulse.py` (line 35):
```python
evidences: Mapped[List["RegionalSignalEvidence"]] = relationship(
    "RegionalSignalEvidence", back_populates="signal", cascade="all, delete-orphan"
)
```
SQLAlchemy's Unit of Work interprets `cascade="all, delete-orphan"` by actively emitting explicit child deletions before deleting the parent:
```sql
DELETE FROM regional_signal_evidences WHERE id = :id;
DELETE FROM regional_signals WHERE id = :parent_id;
```
**Critical Distinction:**
Unlike internal database FK cascades, an explicit child `DELETE` statement emitted by the ORM **is subject to child table RLS** and **requires table-level DELETE privileges** on `regional_signal_evidences`. If the runtime role lacks `DELETE` grants on the child table, the ORM child delete fails with SQLSTATE `42501` (`insufficient_privilege`).

### 11.3 Comprehensive Evidence Deletion Path Matrix
The following matrix formally delineates the five possible deletion paths across ORM and PostgreSQL layers:

| Operation Path | ORM Emits Child DELETE? | Database FK Cascade Triggered? | Child Table RLS Evaluated? | Child DELETE Privilege Required? | Resulting Outcome |
|---|---|---|---|---|---|
| **1. Parent ORM Delete** (`session.delete(signal)`) | **Yes** (Emits explicit child DELETE first) | No (Child rows already deleted by ORM) | **YES** | **YES** | Child deleted if actor holds child DELETE privilege; fails with `42501` if revoked. |
| **2. Child Orphan Removal** (`signal.evidences.remove(ev)`) | **Yes** (Emits explicit child DELETE) | No | **YES** | **YES** | Child deleted if actor holds child DELETE privilege; fails with `42501` if revoked. |
| **3. Direct SQL Parent Delete** (`DELETE FROM regional_signals`) | No | **Yes** (`RI_FKey_cascade_del`) | **NO** (`SECURITY_NOFORCE_RLS`) | **NO** (Bypasses child privilege check) | **Child rows destroyed** if parent DELETE authorized. |
| **4. Bulk ORM Parent Delete** (`db.query(RegionalSignal).delete()`) | No (Bypasses Unit of Work cascade) | **Yes** (`RI_FKey_cascade_del`) | **NO** (`SECURITY_NOFORCE_RLS`) | **NO** | **Child rows destroyed** if parent DELETE authorized. |
| **5. Direct SQL Child Delete** (`DELETE FROM regional_signal_evidences`) | No | No | **YES** | **YES** | Blocked if child DELETE privilege revoked. |

---

## 12. EVIDENCE IMMUTABILITY THREAT-MODEL ANALYSIS

### 12.1 The Threat Model: Application Roles vs. Superusers
The previous report asserted that "true evidence immutability cannot be achieved at the database level alone." To evaluate this claim, the threat model must be formally defined:

1. **Ordinary Runtime Principals (Threat Scope):**
   - Application roles such as `acrevia_staging_app` or compromised web application connections.
   - Attack vectors: SQL injection, ORM cascade deletion, unauthorized administrative API calls, direct SQL execution by agronomists/researchers.
2. **Database Superusers and Table Owners (Out of Scope):**
   - In PostgreSQL, superusers and object owners possess absolute authority. They can execute `ALTER TABLE ... DISABLE ROW LEVEL SECURITY`, `DROP TRIGGER`, or modify catalog tables directly.
   - No relational database can enforce immutability against its own superuser or table owner.

### 12.2 Immutability Classification Taxonomy
To eliminate ambiguity, this audit establishes a three-tier immutability taxonomy:

$$\begin{aligned}
\mathbf{ABSOLUTELY\_IMMUTABLE} &\implies \text{Unmodifiable even by DB owner/superuser (Mathematically impossible in PG)} \\
\mathbf{APPEND\_ONLY\_FOR\_RUNTIME\_ROLES} &\implies \text{Enforced by grants, RLS, triggers, and FK constraints against application roles} \\
\mathbf{PROTECTED\_AGAINST\_ORDINARY\_WRITERS} &\implies \text{Enforced purely by application service logic}
\end{aligned}$$

PostgreSQL **can** achieve `APPEND_ONLY_FOR_RUNTIME_ROLES` when configured with defense-in-depth:
- Table-level `DELETE` and `UPDATE` privileges revoked from `acrevia_staging_app` on `regional_signals` and `regional_signal_evidences`.
- Foreign key defined with `ON DELETE RESTRICT` or `ON DELETE NO ACTION`.
- ORM relationship modified to remove `delete-orphan` (with `passive_deletes=True`).
- Row-level security policies restricting modifications.

### 12.3 Status of 'is_archived' on RegionalSignal
The previous report proposed soft-deletion via `RegionalSignal.is_archived`. 
Inspection of `backend/app/models/regional_pulse.py` and all Alembic migrations confirms:
- **`is_archived` does not exist** on `RegionalSignal`.
- Soft-deletion via `is_archived` is a **proposed future schema design**, not an existing control.

---

## 13. CORRECTED GET-PATH MUTATION AND VISIBILITY ANALYSIS

### 13.1 Complete Data Path of a Regional Pulse GET Request
In `backend/app/api/v1/endpoints/regional_pulse.py` (lines 115–165) and `backend/app/services/regional_pulse_service.py` (lines 330–395):

$$\begin{aligned}
\text{API GET} &\longrightarrow \text{SELECT from } \texttt{regional\_signals} \\
&\longrightarrow \text{Relationship Lazy Load of } \texttt{signal.evidences} \\
&\longrightarrow \text{Call } \texttt{revalidate\_signal\_provenance(signal, db)} \\
&\longrightarrow \text{Check } N < 3 \implies \text{Stage } \texttt{validation\_status = 'SUPPRESSED...'} \\
&\longrightarrow \text{Open } \texttt{with db.begin\_nested():} \text{ (SAVEPOINT)} \\
&\longrightarrow \text{Savepoint Exit Flush} \implies \begin{cases} \text{Actor is privileged} &\implies \text{Flush succeeds} \\ \text{Actor is Farmer (RLS)} &\implies \text{Flush blocked (StaleDataError)} \end{cases} \\
&\longrightarrow \text{Outer Route Execution} \implies \texttt{db.commit()} \\
&\longrightarrow \text{API Response Filter} \implies \text{Return filtered signals}
\end{aligned}$$

### 13.2 Separation of Three Distinct Outcomes
The audit strictly differentiates three distinct outcomes of a GET request:

| Outcome Identifier | Name | Persistence to PostgreSQL | Response Effect | Root Cause |
|---|---|---|---|---|
| **Outcome A** | **Read-Response Denial** | **No** (Database row unchanged) | Signal hidden or 404 returned | Service evaluates `is_valid == False` due to RLS-hidden evidences; filters signal from response. |
| **Outcome B** | **Transient In-Memory Mutation** | **No** (Rollback discards staging) | Clean commit of read session | Savepoint catches RLS `StaleDataError`; executes `ROLLBACK TO SAVEPOINT`; expires modified entity. |
| **Outcome C** | **Persistent Write-on-Read Mutation** | **YES** (Row updated and committed) | Permanent suppression ($N=0$) | Privileged actor (Admin/Expert) issues GET; flush succeeds; outer route executes `db.commit()`. |

### 13.3 Invisibility vs. Absence of Evidence
A fundamental architectural flaw in `revalidate_signal_provenance` is treating an empty evidence relationship collection as proof of absent evidence:
$$\texttt{len(signal.evidences) == 0} \not\implies \text{Evidence Absent in DB}$$
Under RLS, `regional_signal_evidences` is restricted to `ADMIN`, `AGRICULTURAL_EXPERT`, and `RESEARCHER`. When an ordinary farmer issues a query, RLS filters out all child evidence rows. The relationship collection loads as empty (`[]`). The service misinterprets this RLS-enforced privacy filter as a provenance failure and attempts to suppress the legitimate signal.

### 13.4 Reassessment of Previous Remediation Recommendation
The previous report recommended:
1. Permanently removing `revalidate_signal_provenance` from GET list/detail routes.
2. Removing `db.commit()` from GET routes.

#### Cause-and-Effect Analysis on Governed Risks
Removing revalidation and commits from GET routes provides the following specific effects:
- **`RES-PULSE-READ-01` (Write-on-Read):** **Directly eliminated.** Without mutation staging and commits, GET operations are strictly read-only.
- **`RES-PRIMARY-ROUTING-01` (Connection Routing):** **Directly eliminated.** Pure read transactions can be routed to read replicas rather than requiring primary database connections.
- **`RES-REPLICA-LAG-01` (Replica Lag Anomalies):** **Directly mitigated.** Eliminates self-induced read-your-own-writes replication lag anomalies.
- **`FARMER_READ_BLOCKED_BY_EVIDENCE_ASSOCIATION_RLS`:** **Directly resolved on GET.** A valid signal ($N=3$) will no longer be suppressed or rejected during read revalidation.
- **Residual Need:** Provenance revalidation cannot simply be discarded; it must be relocated to an explicit write-time, background, or scheduled reconciliation pipeline.

---

## 14. WORKER-DISPATCH SCOPE AND EVIDENCE (WRK-DISP-01)

### 14.1 Inspection of Task Infrastructure (`LOCAL_SOURCE_VERIFIED`)
Inspection of `backend/app/tasks/` establishes:
1. Exactly one task file exists: `backend/app/tasks/run_riskcast_batch.py`.
2. Lines 40–75 define guards raising `ProductionDispatchBlockedError: DISPATCH_NOT_CONFIGURED` when running in staging or production.
3. This task is explicitly and exclusively tied to RiskCast batch computations.
4. **Zero Regional Pulse background tasks exist** in `backend/app/tasks/` or elsewhere in the codebase.

### 14.2 Narrowed Finding Formulation
The previous report overclaimed by asserting that all Regional Pulse workers are operationally infeasible due to the RiskCast dispatch guard. The accurate, defensible finding is:
$$\text{Finding: } \mathbf{No\ configured\ Regional\ Pulse\ worker\ dispatch\ implementation\ was\ evidenced\ in\ the\ inspected\ repository\ source.}$$
The absence of source code in the repository establishes that no application worker is implemented locally; it does not constitute proof regarding external cloud schedulers or infrastructure.

### 14.3 Transactional Outbox Architectural Requirements
If asynchronous provenance revalidation is adopted, a Transactional Outbox pattern is essential to prevent dual-write inconsistencies. The outbox design must address:
- **Dual-Write Prevention:** Signal updates and outbox event records must commit within a single atomic database transaction.
- **Worker Database Identity:** The worker must connect using a dedicated trusted worker principal, not an ordinary user session.
- **Tenant & District Context:** The worker must explicitly set `app.current_user_id` and administrative bypass GUCs to inspect evidence rows.
- **Idempotency & Row Locking:** Concurrent revalidations must use `SELECT ... FOR UPDATE SKIP LOCKED` to prevent duplicate processing.

---

## 15. PRIVILEGE-GENERATOR CALLSITE AND ACL LIMITATIONS (DB-GRANT-APPLY-01)

### 15.1 Callsite Absence in Migration a1089411c87d
In `backend/app/database/rls.py`, lines 977–1050 define the `PRIVILEGE_CROSSWALK` dictionary and the `generate_privilege_grants_ddl()` generator function.

Inspection of `backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py` confirms:
- The migration imports `generate_rls_ddl`.
- The migration **does not import or execute** `generate_privilege_grants_ddl()`.
- The migration executes zero `GRANT` or `REVOKE` statements.

### 15.2 Distinction Between Migration Callsite and Live ACL
The absence of a callsite in Alembic migration `a1089411c87d` establishes that database privileges are not managed by Alembic. 

However, under MODE A restrictions, this does **not** prove that live database grants are absent or empty in Neon Cloud staging. Table grants could be provisioned via:
- External shell provisioning scripts (`scripts/provision_db.sh`).
- Neon Cloud console administration.
- Database branch initialization scripts.

### 15.3 Canonical Governance Status of DB-GRANT-APPLY-01
Item `DB-GRANT-APPLY-01` remains classified as:
$$\mathbf{PROPOSED\ —\ OWNER\ APPROVAL\ REQUIRED}$$
It must not be promoted to an active blocker or applied to staging without formal Project Owner sign-off under Decision DB-AUTH-01.

---

## 16. GATE-01 AND GATE-05 BRANCH-IDENTITY INCONSISTENCY

### 16.1 Inspection of Governance Register
An audit of `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md` reveals an unresolved branch-identity inconsistency:

1. **Line 20 (Overview Description):**
   > "Provisions an isolated Neon staging database branch (`staging-rls-phase05`) in Singapore (`aws-ap-southeast-1`), creates restricted runtime role `acrevia_staging_app`..."
2. **Line 28 (GATE-01 Authorization Scope):**
   > "| **GATE-01** | Provisioning of isolated Neon staging branch `staging-rls-phase07` from parent `production` in region `aws-ap-southeast-1`. | Project Owner | `[x] APPROVED BY OWNER (2026-11-10)` |"
3. **Line 32 (GATE-05 Teardown Scope):**
   > "| **GATE-05** | Teardown and deprovisioning schedule of `staging-rls-phase05` post-verification. | Project Owner | `[ ] UNCHECKED (AWAITING SIGN-OFF)` |"
4. **Line 59 (Checklist GATE-01):**
   > "[x] GATE-01 APPROVED: Provision Neon branch 'staging-rls-phase07' (aws-ap-southeast-1)"
5. **Line 63 (Checklist GATE-05):**
   > "[ ] GATE-05 APPROVED: Authorize automated branch teardown 24 hours post-verification"

### 16.2 Resolution Strategy: Formal Governance Discrepancy
This discrepancy indicates that either:
- `staging-rls-phase05` is a stale identifier carried over from Phase 05 documentation;
- `staging-rls-phase07` is the intended new branch, but teardown was left referencing the legacy branch; or
- A genuine ambiguity exists regarding the target cloud resource.

**Governance Rule:** The auditor must not silently choose the correct branch name or alter the register. This is documented as a descriptive governance discrepancy requiring formal Project Owner correction. No new canonical blocker ID is assigned.

---

## 17. CREDENTIAL-ROTATION CAUSAL-CLAIM ASSESSMENT

### 17.1 Analysis of the Previous Claim
The previous report stated:
> "Physical branch provisioning remains `LIVE_DATABASE_UNVERIFIED` in Mode A (blocked by credential rotation)."

### 17.2 Evidentiary Audit of Public Governance
Inspection of `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md` establishes:
1. GATE-01 was formally approved by the Project Owner on **10 November 2026**.
2. The scope and conditions of GATE-01 contain **no prerequisite or dependency** on database credential rotation.
3. Database credential rotation is an independent open security issue recorded as **`DB-CREDENTIAL-EXPOSURE-01`**.

### 17.3 Formal Causal Withdrawal
The claim that GATE-01 branch provisioning is "blocked by credential rotation" is **formally withdrawn as unsupported by repository records**:
- GATE-01 physical execution remains `LIVE_DATABASE_UNVERIFIED` solely because the audit is conducted under **MODE A ONLY** restrictions.
- `DB-CREDENTIAL-EXPOSURE-01` remains an active, independent security blocker.
- The two items must not be conflated into a compound blocker.

---

## 18. OWNER DECISIONS AND GOVERNANCE RECONCILIATION

### 18.1 Status of Governed Owner Decisions
Inspection of `docs/pilot/security/phase_07_owner_decision_evidence_traceability_matrix.md` and `docs/pilot/security/PHASE_07_REGIONAL_PULSE_PROJECT_OWNER_DECISION_RECORD.md` establishes that all four core architecture decisions remain formally pending Project Owner sign-off:

| Decision ID | Decision Title | Scope & Architectural Impact | Governance Status |
|---|---|---|---|
| **D-01** | **Official Advisory Public Visibility vs. Minimum Farm Threshold** | Authorizes whether official state advisories ($N=0$) are visible to farmers without requiring 3 distinct plot telemetry sources. | `PENDING_OWNER_SIGN_OFF` |
| **D-02** | **Source Authenticity & Terminology** | Reconciles official advisory terminology (`OFFICIAL_ALERT` vs `OFFICIAL_ADVISORY`) and source attribution contracts. (Must not be conflated with DB role segregation). | `PENDING_OWNER_SIGN_OFF` |
| **D-03** | **Agronomic Peer-Review Workflow** | Governs how community-aggregated observations (`UNVALIDATED_OBSERVATION`) transition to validated alerts. (Must not be conflated with an audit-trail decision). | `PENDING_OWNER_SIGN_OFF` |
| **DB-AUTH-01** | **Trusted Writer Architecture** | Adopts dedicated PostgreSQL database roles (`acrevia_worker`, `acrevia_staging_app`) and applies `PRIVILEGE_CROSSWALK`. | `PENDING_OWNER_SIGN_OFF` |

### 18.2 Evidence Retention Governance Decision Required
The transition from cascade deletion to append-only evidence retention (`ON DELETE RESTRICT`, removing ORM `delete-orphan`, and introducing audit trails) introduces a new operational requirement: **Data Retention, Archival, and Exceptional Purge Policy**. This policy governs how historical evidence rows are preserved, archived, or purged under statutory data protection mandates. A formal Project Owner decision is recommended for this lifecycle.

---

## 19. CANONICAL BLOCKER RECONCILIATION

In strict compliance with pilot governance rules, all fifteen canonical blockers are preserved without alteration of identifiers:

| Blocker ID | Description | Current Architectural Status | Mode A Status |
|---|---|---|---|
| `RLS-WRITE-AUTH-01` | RLS write policy allows arbitrary role updates via unconstrained `WITH CHECK`. | Formally proven in generated DDL; hardened policy designed. | Active Blocker |
| `RLS-ROLE-ASSIGNMENT-01` | Runtime role assignment mechanism susceptible to session variable leakage. | Remediation designed via session variable encapsulation. | Active Blocker |
| `DB-AUTH-01` | Single runtime database role lacks separation between background workers and web apps. | Architectural decision DB-AUTH-01 pending owner sign-off. | Active Blocker |
| `DB-CREDENTIAL-EXPOSURE-01` | Public exposure of database connection strings in legacy commits. | Independent blocker; rotation protocol designed. | Active Blocker |
| `APP-ROLE-SELF-SELECT-01` | Client self-selection of roles during registration/authentication. | Endpoint guards verified; RLS-level role binding required. | Active Blocker |
| `EXP-AUTH-01` | Expert and researcher endpoint authorization inconsistencies. | Current code aligned; proposed policy narrowing requires coordination. | Active Blocker |
| `CASCADE-ROLE-DEL-01` | Cascading deletions undermine evidence integrity and role associations. | Database FK cascade and ORM delete-orphan verified; RESTRICT designed. | Active Blocker |
| `TENANT-MEMBERSHIP-01` | Tenant membership validation absent in cross-tenant join queries. | GUC validation required across collaborative tables. | Active Blocker |
| `OWNER-AUTH-01` | Missing formal Project Owner sign-offs on core security decisions. | Decisions D-01 through D-03 and DB-AUTH-01 pending. | Active Blocker |
| `DB-RLS-01` | Staging database RLS verification unperformed against live Neon instance. | Unverified in Mode A; requires Mode B execution under GATE-01. | Active Blocker |
| `WRK-DISP-01` | Production worker dispatch provider raises `DISPATCH_NOT_CONFIGURED`. | Confirmed in RiskCast; zero Regional Pulse workers implemented in source. | Active Blocker |
| `RES-PULSE-01` | Role-based cross-district SELECT eligibility across 33 districts. | Generated DDL grants cross-district row eligibility; canonical Medium preserved. | Active Blocker |
| `RES-PULSE-02` | Unvalidated community signals visible prior to agronomic peer review. | Governed by Decision D-03; conditional RLS predicate designed. | Active Blocker |
| `GATE01-PROV-01` | Physical provisioning of isolated staging branch unverified in Mode A. | GATE-01 approved on 2026-11-10; physical execution unverified offline. | Active Blocker |
| `RES-PULSE-READ-01` | Write-on-read suppression in Regional Pulse GET endpoints. | Root causes proven; read-only GET refactoring designed. | Active Blocker |

---

## 20. RESIDUAL-RISK RECONCILIATION

All five canonical residual risks are preserved at their authoritatively recorded severities:

| Risk ID | Title | Canonical Recorded Severity | Assessed Technical Severity | Notes & Governance Reconciliation |
|---|---|---|---|---|
| `RES-PULSE-01` | Broad Expert/Researcher SELECT Scope | **MEDIUM** | **HIGH** | Canonical severity maintained at Medium; technical High documented for owner review. |
| `RES-PULSE-02` | Regional Signal Early Visibility ($N \ge 3$) | **MEDIUM** | **MEDIUM** | Governed by Decision D-03 pending sign-off. |
| `RES-PRIMARY-ROUTING-01` | Read Endpoint Primary DB Connection Requirement | **MEDIUM** | **MEDIUM** | Mitigated by removing mutations/commits from GET routes. |
| `RES-REPLICA-LAG-01` | Read-Your-Own-Writes Replication Lag | **LOW** | **LOW** | Mitigated by converting GET routes to pure reads. |
| `RES-FREE-TEXT-01` | Free-Text Advisory Injection in Regional Signals | **LOW** | **LOW** | Governed by sanitization and Pydantic validation. |

---

## 21. FINDINGS REQUIRING FUTURE POSTGRESQL VERIFICATION (DESIGN ONLY)

The following verification matrix specifies safe, offline-designed verification procedures to be executed in PostgreSQL environment upon authorized transition to **MODE B**:

| Test Domain | Target Behavior | Required Database Engine | Required Principal | Required Grants | Test Setup & Input | Expected Result | Failure Interpretation | Owner Authorization Required? |
|---|---|---|---|---|---|---|---|---|
| **1. Status Contract** | Rejection of invalid status strings via DB `CHECK` constraint. | PostgreSQL 15+ | `acrevia_staging_app` | `INSERT`, `UPDATE` on `regional_signals` | `INSERT INTO regional_signals (..., validation_status) VALUES (..., 'PUBLISHED');` | Fails with SQLSTATE `23514` (`check_violation`). | Constraint missing or allowlist misconfigured. | Yes (Schema migration) |
| **2. RLS Public Read** | Farmer cannot view suppressed ($N < 3$) signals. | PostgreSQL 15+ | `acrevia_staging_app` (with farmer session GUC) | `SELECT` on `regional_signals` | Query `regional_signals` where `validation_status = 'SUPPRESSED...'`. | Query returns 0 rows. | Public read policy leaks suppressed rows. | Yes (RLS policy DDL) |
| **3. Permissive Composition** | Expert SELECT scope on cross-district rows. | PostgreSQL 15+ | `acrevia_staging_app` (with expert session GUC) | `SELECT` on `regional_signals` | Expert queries signals across all 33 districts. | Query returns rows across all districts if `FOR ALL` policy active. | Proves `RES-PULSE-01` cross-district row eligibility. | Yes (RLS policy DDL) |
| **4. UPDATE Transition** | Prevention of status regression via paired USING/WITH CHECK. | PostgreSQL 15+ | `acrevia_staging_app` | `UPDATE` on `regional_signals` | Attempt `UPDATE regional_signals SET validation_status = 'UNVALIDATED...' WHERE id = expert_confirmed_id;` | Fails with SQLSTATE `44000` (`check_violation`) or 0 rows matched. | Policy permits status regression. | Yes (RLS policy DDL) |
| **5. Evidence Cascade** | Direct SQL parent DELETE fails when FK is RESTRICT. | PostgreSQL 15+ | `acrevia_staging_app` | `DELETE` on `regional_signals` | `DELETE FROM regional_signals WHERE id = signal_with_evidence_id;` | Fails with SQLSTATE `23001` (`restrict_violation`). | FK still configured as `CASCADE`. | Yes (Schema migration) |
| **6. ORM Cascade** | ORM orphan removal blocked when child DELETE revoked. | PostgreSQL 15+ | `acrevia_staging_app` | `SELECT`, `UPDATE` on child (NO `DELETE`) | `signal.evidences.remove(ev); db.commit()` | Fails with SQLSTATE `42501` (`insufficient_privilege`). | Child DELETE grant active or ORM bypasses grant check. | Yes (Grant application) |
| **7. GET-Path Immutability** | Farmer GET request does not mutate or suppress signal. | PostgreSQL 15+ | `acrevia_staging_app` (via FastAPI test client) | `SELECT` on parent/child | Issue `GET /api/v1/regional-pulse/signals/{id}` as Farmer on signal with $N=3$. | HTTP 200 returned; DB row unchanged ($N=3$, unsuppressed). | GET route still mutates row on read. | No (Local unit test) |
| **8. Worker Execution** | Outbox event delivery atomicity and idempotency. | PostgreSQL 15+ | `acrevia_worker` | `SELECT`, `INSERT` on outbox table | Trigger concurrent provenance revalidations on same signal. | Exactly one revalidation executed; outbox event marked processed. | Dual-write anomaly or race condition in worker. | Yes (Worker architecture) |
| **9. Governance Verification** | Verify Neon staging branch identity against register. | Neon Cloud API / CLI | Cloud Admin | Cloud branch inspection | Inspect Neon project branches in region `aws-ap-southeast-1`. | Branch `staging-rls-phase07` active; child of production. | Branch not provisioned or mismatch with GATE-05. | Yes (Cloud access) |

---

## 22. CORRECTIVE RECOMMENDATIONS RANKED BY URGENCY

### Priority 1: High Urgency (Schema Integrity & Grant Boundary)
1. **Apply Database Status CHECK Constraint:** Introduce a database `CHECK` constraint on `regional_signals.validation_status` covering all five service-emitted statuses.
2. **Transition Foreign Key to RESTRICT:** Change `RegionalSignalEvidence.signal_id` foreign key from `ON DELETE CASCADE` to `ON DELETE RESTRICT` (or `NO ACTION`).
3. **Remove ORM Delete-Orphan:** Modify `RegionalSignal.evidences` relationship in `backend/app/models/regional_pulse.py` to remove `delete-orphan` and set `passive_deletes=True`.
4. **Apply Table-Level Privilege Grants:** Authorize and execute `generate_privilege_grants_ddl()` under Decision DB-AUTH-01 to revoke `DELETE` privileges on child evidence tables from runtime application roles.

### Priority 2: Medium Urgency (API & Service Layer Refactoring)
5. **Convert Regional Pulse GET Routes to Strictly Read-Only:** Remove `revalidate_signal_provenance` and `db.commit()` from GET list and detail endpoints in `backend/app/api/v1/endpoints/regional_pulse.py`.
6. **Decompose Permissive `FOR ALL` Policy:** Split `regional_signals_author_write_policy` into dedicated `FOR INSERT` and `FOR UPDATE` policies, removing `SELECT` to eliminate unintentional cross-district row eligibility (`RES-PULSE-01`).
7. **Coordinate Researcher Role Authorization:** Ensure any future narrowing of RLS write policies preserves `RESEARCHER` access in lockstep with `backend/app/api/v1/endpoints/regional_pulse.py`.

### Priority 3: Governance & Lifecycle Reconciliation (Project Owner Sign-Off)
8. **Resolve GATE-01 vs. GATE-05 Branch Inconsistency:** Correct `docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md` to reconcile `staging-rls-phase07` and `staging-rls-phase05`.
9. **Formalize Owner Decisions D-01 through D-03 and DB-AUTH-01:** Secure formal Project Owner sign-offs on public advisory thresholds, source terminology, peer-review workflows, and trusted writer roles.
10. **Establish Evidence Retention Governance Policy:** Author an evidence lifecycle decision record defining archival, versioning, and exceptional statutory purge procedures.

---

## 23. ADVERSARIAL REVIEW OF REMAINING ASSUMPTIONS

To ensure absolute rigor, this audit subjected all conclusions to the twenty adversarial challenge questions mandated by Section 14:

1. *Does 'PUBLISHED' exist anywhere in the project?*  
   **Rebuttal:** Yes. It exists in Stage 12 Knowledge Commons models (`commons_contribution.py`, `extension_learning.py`, `research_hub.py`, `commons_service.py`). It is absent only from `RegionalSignal`. The previous report's claim that it "does not exist in the codebase" is corrected.
2. *Would the proposed status predicate deny every possible database row?*  
   **Rebuttal:** No. Because `validation_status` is an unconstrained `VARCHAR(50)`, an authorized SQL writer could insert `'PUBLISHED'`. It denies 100% of *service-generated rows*, not 100% of all possible database rows.
3. *Does the lack of a CHECK constraint prove a runtime role can write arbitrary values?*  
   **Rebuttal:** No. Runtime persistence is bounded by table-level grants (`INSERT`/`UPDATE`) and RLS `WITH CHECK`. Conflating schema capability with runtime execution is an overreach.
4. *Can a FOR ALL policy affect SELECT queries?*  
   **Rebuttal:** Yes. Authoritative PostgreSQL engine documentation confirms that `FOR ALL` policies apply to `SELECT`, `INSERT`, `UPDATE`, and `DELETE`.
5. *Does the researcher API currently conflict with the generated RLS policy?*  
   **Rebuttal:** No. Both `backend/app/api/v1/endpoints/regional_pulse.py` (L75) and `backend/app/database/rls.py` (L928) include `RESEARCHER`. The conflict existed only in a proposed narrower policy.
6. *Does WITH CHECK make all old-to-new transition enforcement impossible?*  
   **Rebuttal:** No. Paired `USING` (targeting `OLD.*`) and `WITH CHECK` (enforcing `NEW.*`) on a command-scoped `FOR UPDATE` policy can restrict allowed transition sets.
7. *Do PostgreSQL FK cascades bypass every authorization mechanism?*  
   **Rebuttal:** No. The cascade trigger bypasses child RLS, but the parent `DELETE` statement must first be fully authorized under parent privileges and parent RLS.
8. *Does parent row deletion require authorization?*  
   **Rebuttal:** Yes. The parent DELETE requires table-level `DELETE` privilege and must satisfy parent RLS `USING` clauses.
9. *Do ORM and database cascades have identical security semantics?*  
   **Rebuttal:** No. Database FK cascade executes internally under SPI (`SECURITY_NOFORCE_RLS`) bypassing child RLS; ORM cascade emits explicit child `DELETE` statements that evaluate child RLS and require child table `DELETE` privileges.
10. *Does ON DELETE RESTRICT alone guarantee evidence retention?*  
    **Rebuttal:** No. If the ORM retains `cascade="all, delete-orphan"` and the actor possesses child table `DELETE` privileges, the ORM deletes child rows before the database FK constraint is reached.
11. *Does denying child DELETE alone prevent a parent FK cascade?*  
    **Rebuttal:** No. Internal database cascade (`RI_FKey_cascade_del`) runs under SPI and does not check table-level `DELETE` privileges on the referencing child table.
12. *Can database controls enforce append-only behavior for application roles?*  
    **Rebuttal:** Yes. Through table grant revocation, `ON DELETE RESTRICT`, trigger guards, and RLS, PostgreSQL achieves `APPEND_ONLY_FOR_RUNTIME_ROLES`.
13. *Does a RiskCast dispatch guard prove all Regional Pulse workers are impossible?*  
    **Rebuttal:** No. `run_riskcast_batch.py` is RiskCast-specific. The accurate statement is that no Regional Pulse worker implementation was evidenced in the repository source.
14. *Does a missing grant-generator call in one migration prove live grants are absent?*  
    **Rebuttal:** No. Live database grants could be provisioned via external scripts, DBA actions, or console initialization (`LIVE_DATABASE_UNVERIFIED`).
15. *Does removing GET commits automatically fix all farmer visibility and routing risks?*  
    **Rebuttal:** It eliminates `RES-PULSE-READ-01`, `RES-PRIMARY-ROUTING-01`, and `RES-REPLICA-LAG-01`, but provenance revalidation must still be relocated to a secure write-time or background mechanism.
16. *Do precomputed aggregates eliminate all concurrency and consistency issues?*  
    **Rebuttal:** No. Precomputed aggregates require transactional synchronization, row locking, or eventual consistency pipelines to prevent race conditions during concurrent evidence ingestion.
17. *Is GATE-01 blocked by credential rotation?*  
    **Rebuttal:** No. The governance register contains no causal dependency linking GATE-01 to credential rotation. The causal claim is withdrawn.
18. *Do staging-rls-phase05 and staging-rls-phase07 necessarily refer to the same branch?*  
    **Rebuttal:** Not necessarily. This is an unresolved branch-identity inconsistency in the governance register requiring Project Owner clarification.
19. *Does a technical High severity automatically change canonical Medium severity?*  
    **Rebuttal:** No. Canonical governance records cannot be unilaterally modified by an auditor. Both concepts are documented separately.
20. *Does a documentation recommendation grant permission to implement it?*  
    **Rebuttal:** Absolutely not. Under MODE A restrictions, all implementation changes remain strictly unauthorized until formal Project Owner sign-off and Mode B authorization.

---

## 24. RELEASE-READINESS CONCLUSION

Based on the thorough, evidence-bound corrective reassessment conducted across all repository source files, migrations, PostgreSQL engine mechanics, and governance registers, the release recommendation for Phase 07 documentation is:

$$\mathbf{RELEASE\ RECOMMENDATION:}\quad \mathbf{CONDITIONALLY\_READY\_FOR\_OWNER\_REVIEW}$$

### Conditions for Formal Owner Sign-Off:
1. **Resolution of Branch-Identity Ambiguity:** Project Owner must clarify whether `staging-rls-phase07` or `staging-rls-phase05` is the authoritative target branch for GATE-01 and GATE-05.
2. **Formal Sign-Off on Pending Decisions:** Project Owner must sign off on Decisions D-01 (Advisory Visibility), D-02 (Terminology), D-03 (Peer-Review Workflow), and DB-AUTH-01 (Trusted Writer Architecture).
3. **Approval of Errata Reclassifications:** Project Owner must acknowledge the reclassification of `SEC-P07-STATUS-01` and `SEC-P07-API-RLS-01` to `PROPOSED_DESIGN_INCOMPATIBILITY`, and the withdrawal of the GATE-01 credential-rotation causal claim.
4. **Approval of Mode B Transition:** Physical database provisioning and live catalog verification remain strictly unauthorized until the Project Owner explicitly unlocks Mode B execution.

---

## 25. EXPLICIT AUDIT LIMITATIONS

1. **Strict MODE A Boundary:** All findings are derived exclusively from static source code inspection, AST verification, documentation review, and offline dialect modeling. Zero network connections to Neon Cloud, AWS Singapore, staging, or production databases were initiated.
2. **Catalog and Grant Uncertainty:** Live table grants, database role memberships, active PostgreSQL policies, and trigger definitions in the remote Neon staging database remain `LIVE_DATABASE_UNVERIFIED`.
3. **No Code Modifications:** Zero application source files, schema definitions, Alembic migrations, or test files were created or modified in the workspace.
4. **Advisory Authority:** This report provides assurance and architectural analysis only. It does not constitute Phase 07 operational release approval, which remains the sole prerogative of the Project Owner.
