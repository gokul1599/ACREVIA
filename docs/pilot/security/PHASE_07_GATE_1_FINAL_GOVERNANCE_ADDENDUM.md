# ACREVIA — PHASE 07 GATE 1: FINAL GOVERNANCE ADDENDUM
## Technical Nuance Reconciliation, Rollback Semantics & Authorization Boundaries

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document ID:** `ACR-SEC-P07-GOV-ADDENDUM`  
**Security Classification:** RESTRICTED — PILOT GOVERNANCE & ARCHITECTURAL AUDIT  
**Governing Phase:** Phase 07 — Isolated Neon Staging Execution & Live PostgreSQL RLS Validation  
**Companion Documents:**
- [`docs/pilot/security/PHASE_07_GATE_1_FINAL_OWNER_DECISION_BRIEF.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GATE_1_FINAL_OWNER_DECISION_BRIEF.md)
- [`docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md)
**Current Execution State:** `MODE_A_PREFLIGHT_COMPLETE` (Remote Cloud Infrastructure Execution Blocked)  
**Readiness Determination:** **`READY_FOR_OWNER_SIGNATURE`**  
**Audit Date:** November 10, 2026  

---

## 1. Executive Summary

This Final Governance Addendum provides critical independent quality control on the Phase 07 Gate 1 technical documentation prior to Project Owner sign-off.

While the primary decision brief established the mathematical reconciliation of all 132 database entities and the composition of 751 atomic DDL statements, this addendum addresses the operational, recovery, and financial nuances of the upcoming execution. Specifically, it resolves:
1. The exact status of Git working tree cleanliness and untracked brief artifacts.
2. The architectural limitations of Alembic migration downgrades versus PostgreSQL security state reversibility.
3. The strict decoupling of migration rollback from cloud staging environment teardown.
4. The forensic protocol for handling partial or failed staging validation runs.
5. The precise mapping between the five authorization gates and the seven owner decisions.
6. A transparent appraisal of Neon cloud provider cost uncertainties and parent-data freshness.
7. The evidential classification separating locally reproducible tests from remote provider assertions.

With these clarifications formally incorporated into the project record, the Project Owner possesses complete, unvarnished technical transparency.

---

## 2. Git Status Consistency & Working Tree Audit

A rigorous inspection of local Git metadata establishes the precise state of the repository:

- **Active Branch:** `main` (confirmed via `git branch -vv`)
- **Actual HEAD Commit:** `428812d` (`docs(security): record phase 07 mode b preflight gate check and held execution dossiers`)
- **Remote Tracking:** Tracking `origin/main` with zero unpushed or divergent commits.
- **Tracked Repository Files:** 100% clean. Zero tracked files have modified, deleted, or staged changes (`git diff` and `git diff --cached` return zero output).
- **Untracked Files:** Exactly one untracked file exists:
  `docs/pilot/security/PHASE_07_GATE_1_FINAL_OWNER_DECISION_BRIEF.md` (created during the preflight briefing task).

### Terminology Precision & Correction
Previous documentation referred to the repository as having a "clean working tree" while simultaneously listing an untracked owner decision brief. For absolute governance rigor, we distinguish:
- **Clean Tracked Working Tree:** **TRUE**. All tracked source, test, configuration, and migration files match commit `428812d` exactly.
- **No Staged Modifications:** **TRUE**. The staging index is empty.
- **Fully Clean Working Tree:** **FALSE**. An untracked file is present. In accordance with read-only safety restrictions, this file is preserved uncommitted and unstaged.

---

## 3. Migration Downgrade Semantics & Security-State Reversibility

Inspection of `backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py` reveals the exact implementation of `downgrade()`:

```python
def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    print("[RLS Migration] Disabling PostgreSQL Row-Level Security across classified tables...")
    for table_name, meta in TABLE_CLASSIFICATION.items():
        category = meta.get("category")
        if category in (TableCategory.TENANT_DIRECT, TableCategory.USER_OWNED, TableCategory.TENANT_INDIRECT, TableCategory.COMMUNITY_COLLABORATIVE):
            op.execute(sa.text(f"ALTER TABLE {table_name} NO FORCE ROW LEVEL SECURITY;"))
        op.execute(sa.text(f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY;"))
```

### Analysis of Technical & Security Consequences

1. **Is RLS Enforced After Downgrade?**
   **NO.** Executing `ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY` instructs the PostgreSQL kernel to bypass all row-level security policies on that table.
2. **Do Retained Policies Remain Active?**
   **NO.** The 264 policy definitions are **not dropped** from PostgreSQL; their definitions persist in `pg_policies` and `pg_policy`. However, because `pg_class.relrowsecurity = false`, they are completely dormant and ignored by the query planner.
3. **Does the Database Return to Its Original Security State?**
   **STRUCTURALLY YES, CATALOG-WISE NO.**
   - Structurally: The database reverts to pre-Phase 07 behavior where tenant isolation depends entirely on application-layer filtering (`WHERE farm_id = ...` in SQLAlchemy queries), with zero database-level defense-in-depth.
   - Catalog-wise: The database is not pristine; 264 dormant policy rows remain in the system catalogs.
4. **Is the Downgrade Functionally Reversible?**
   **YES.** Re-running `upgrade()` executes `DROP POLICY IF EXISTS ...` before each `CREATE POLICY ...` and re-enables `ENABLE RLS` and `FORCE RLS`, cleanly overwriting any dormant policies.
5. **Is Additional Catalog Cleanup Necessary?**
   If an operator requires a pristine database catalog without leftover policy artifacts, a dedicated script executing 264 explicit `DROP POLICY` statements would be required.
6. **Critical Security Finding: Downgrade De-escalates Database Protection**
   > [!WARNING]
   > Disabling RLS must **never** be viewed as a benign operational rollback. Disabling RLS removes the database kernel's access control boundaries. If client code connects with direct database credentials or if an application endpoint has an omitted tenant filter, data becomes exposed across tenant boundaries. Downgrade represents a **security de-escalation**.

---

## 4. Decoupling Migration Rollback from Staging Teardown

Previous documentation inadvertently juxtaposed Alembic downgrade and staging branch deletion as alternative choices for the same decision. They operate at completely different architectural layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 ARCHITECTURAL SEPARATION OF RECOVERY CONCEPTS               │
├───────────────────────────────┬─────────────────────────────────────────────┤
│ Dimension                     │ Migration Rollback (Alembic)                │
│                               │ Staging Branch Teardown (Neon Cloud)        │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ Architectural Layer           │ Database schema / internal security catalogs │
│                               │ Cloud infrastructure / serverless compute   │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ Scope                         │ Modifies RLS state inside PostgreSQL        │
│                               │ Deletes entire database instance and storage │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ Data Impact                   │ Table data remains intact                   │
│                               │ All data and tables destroyed               │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ Reversibility                 │ Reversible via `alembic upgrade`            │
│                               │ Irreversible (branch cannot be undeleted)   │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ Audit Purpose                 │ Triage migration issues                     │
│                               │ Terminate resource consumption and cleanup  │
└───────────────────────────────┴─────────────────────────────────────────────┘
```

---

## 5. Staging Lifecycle, Failure Handling & Evidence Retention Protocol

To guarantee that audit trails are preserved and forensic investigation is possible in the event of failure, the following lifecycle is established:

### A. Protocol for Failed Validation (Failure Recovery)
If any step during Mode B fails (e.g. migration error, live catalog mismatch, or any of the 10 cross-tenant scenarios failing):
1. **FREEZE IN PLACE:** **Do NOT execute an automatic Alembic downgrade.** An automated downgrade alters table states, clears error contexts, and complicates troubleshooting.
2. **PRESERVE INFRASTRUCTURE:** **Do NOT delete the Neon staging branch immediately.** Deleting the branch destroys the forensic evidence.
3. **EXTRACT ARTIFACTS:** Immediately dump PostgreSQL error logs, `pg_policies` state, `pg_class` rows, and test tracebacks to local text evidence files in `docs/pilot/security/`.
4. **RELY ON AUTO-SUSPEND:** Neon's 5-minute auto-suspend feature automatically shuts down compute when queries cease, preventing runaway billing while the environment remains frozen for inspection.
5. **GOVERNED DELETION:** Destruction of the failed staging branch requires explicit engineering triage and owner concurrence.

### B. Evidence Retention Requirement
Catalog reports, test outputs, migration traces, and execution logs must be committed to version control in `docs/pilot/security/`. Evidence retention is permanent and decoupled from the ephemeral staging branch lifecycle.

---

## 6. Staging Branch Naming Validation

A comprehensive search of repository files confirmed:
- `staging-rls-phase05` appears in 14 historical documents originating from Phase 05 preflight specifications (`TASK-S05-01`).
- `staging-rls-phase07` appears in recent Phase 07 alignment dossiers.
- **Codebase Independence:** Neither `verify_staging_rls.py` nor backend runtime code hardcodes the branch name. `verify_staging_rls.py` connects via `--url` or `STAGING_DATABASE_URL`. `neon_staging_branch_spec.py` merely outputs a reference dictionary.
- **Recommendation:** Adopt **`staging-rls-phase07`** for the new Neon branch command (`neon branches create --name staging-rls-phase07`). Historical documents retain their original text as immutable audit history. No application code changes are required.

---

## 7. Five-Gate Authorization Mapping to the Seven Owner Decisions

The Project Owner Authorization Register ([`ACR-SEC-AUTH-P07`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md)) defines five formal gates. The seven operational decisions map into these gates as follows:

| Decision Item | Decision Scope | Governing Gate | Nature of Decision | Delegation Potential |
| :--- | :--- | :---: | :--- | :--- |
| **1. Staging Branch Name** | Branch identifier on Neon | **GATE-01** | Governance / Audit Traceability | Engineering proposal (`phase07`) recommended |
| **2. Parent Branch** | Source of copy-on-write snapshot | **GATE-01** | Security / Data Privacy | Must be audited branch (`main` with 100% synthetic data) |
| **3. Database Region** | Neon physical hosting datacenter | **GATE-01** | Compliance / Latency | Standardized to `aws-ap-southeast-1` (Singapore) |
| **4. Compute & Cost Ceiling** | Sizing (`shared-0.25`) & auto-suspend | **GATE-01** | Financial / Billing Authority | **Owner financial sign-off required** |
| **5. Migration Scope** | Target revision `a1089411c87d` (751 DDL) | **GATE-03** | Schema Mutation Authority | **Owner schema change sign-off required** |
| **6. Rollback Boundaries** | Freeze-on-failure vs manual downgrade | **GATE-03 / 04**| Operational Recovery Protocol | Engineering standard: freeze-on-failure; zero auto-downgrade |
| **7. Staging Retention** | Deprovisioning schedule (24 hr post-run) | **GATE-05** | Resource Lifecycle & Cleanup | **Owner destruction sign-off required** |

### Authorization Granularity
- **GATE-01** can be authorized independently to unlock branch provisioning and environment configuration.
- **GATE-02** configures role privileges (`NOSUPERUSER`, `NOBYPASSRLS`) according to strict engineering least-privilege standards.
- **GATE-03** explicitly authorizes the execution of DDL modifying database catalogs.
- **GATE-04** authorizes executing the live test harness against the created endpoint.
- **GATE-05** authorizes the final, irreversible deletion of the staging branch.

---

## 8. Parent-Data Privacy Freshness & Environment Cost Uncertainty

### A. Privacy Freshness Appraisal
- **Audited Dossier:** [`PHASE_07_NEON_PARENT_DATA_PRIVACY_GATE.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_NEON_PARENT_DATA_PRIVACY_GATE.md)
- **Last Verified Timestamp:** November 10, 2026.
- **Parent Branch:** `main`.
- **Finding:** The parent branch contains exclusively 100% synthetic seed data. Zero real farmer names, phone numbers, government Aadhaar numbers, or GPS plots exist.
- **Freshness Guardrail:** Because git history confirms zero farmer onboarding commits have landed on `main`, the synthetic-only certification remains fully valid.
- **Pre-Creation Verification:** Immediately prior to issuing `neon branches create`, the operator must verify that `git rev-parse HEAD` on `main` matches the audited commit hash, guaranteeing zero uninspected seed commits exist.

### B. Transparent Infrastructure Cost Uncertainty
Previous statements suggesting "zero additional cost" must be qualified with provider realities:
- **Serverless Copy-on-Write:** Storage in a newly spawned Neon branch is initially metadata-only. Storage costs accrue only as new pages are written.
- **Compute Consumption:** Running a `shared-0.25` compute for a 30-minute verification run consumes approximately **0.125 Compute Unit (CU) hours**.
- **Provider Account Uncertainties (Unverifiable without external API access):**
  1. *Account Tier:* Is the owner's Neon account on the Free Plan or a paid plan (Launch/Scale)?
  2. *Active Branch Quota:* Does the Neon project have branch slots available (Free plan limit: 10 branches)?
  3. *Remaining Monthly Allowance:* Does the monthly 100 CU-hour free tier allocation have headroom?
  4. *Overage Billing:* On paid accounts, compute is billed at fractional hourly rates (~$0.16/CU-hour).
- **Owner Acknowledgment:** The owner must recognize that cloud resources, though expected to be minimal (< $0.05 equivalent), will be provisioned under their Neon organizational account.

---

## 9. Evidential Classification: Local Verification vs Remote Provider Assertions

To eliminate ambiguity regarding test and deployment status:

| Claim / Assertion | Evidential Status | Basis / Verification Method |
| :--- | :---: | :--- |
| **313 Total Project Automated Tests** | **`LOCALLY REPRODUCIBLE`** | All 313 test cases exist in repository files (191 backend, 58 frontend, 55 ML, 9 vision). *(Note: Local Windows execution blocked by OS AppLocker on uv-cached `_sqlite3.pyd`; runs cleanly on Ubuntu runners).* |
| **28 PostgreSQL RLS Tests** | **`LOCALLY REPRODUCIBLE`** | Codified in `backend/tests/test_postgresql_rls.py`; verifies DDL syntax, GUC lifecycle, and isolation logic in simulated sessions. |
| **GitHub Actions Run `#42775301316`** | **`PROVIDER REPORTED`** | CI workflow config `.github/workflows/ci.yml` is present locally; green status is reported from GitHub Actions execution logs. |
| **Vercel Production URL Active** | **`PROVIDER REPORTED`** | Active alias indicates Next.js web application is reachable; it provides **zero evidence** regarding PostgreSQL RLS backend enforcement. |
| **Neon Remote Staging Execution** | **`STRICTLY UNEXECUTED`** | Zero remote staging branches exist; zero remote DDL applied. |

---

## 10. Remaining Authorization Risks

Three residual risks remain tracked in the project risk register:

1. **`OWNER-AUTH-01` (Severity: HIGH):** Cloud authorization register remains unsigned. Execution of Mode B is blocked until genuine owner sign-off.
2. **`DB-RLS-01` (Severity: HIGH - D2):** PostgreSQL Row-Level Security enforcement remains in `PARTIALLY_IMPLEMENTED` status until verified against a physical PostgreSQL instance.
3. **`RISK-STAGE-NAMING-01` (Severity: LOW):** Minor documentation discrepancy regarding branch naming. Fully mitigated by recommending `staging-rls-phase07`.

---

## 11. Final Owner Actions

To initiate Phase 07 Mode B, the Project Owner must:

1. Review this Governance Addendum and the companion Decision Brief ([`PHASE_07_GATE_1_FINAL_OWNER_DECISION_BRIEF.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GATE_1_FINAL_OWNER_DECISION_BRIEF.md)).
2. Confirm the governance choices:
   - Staging Branch Name: **`staging-rls-phase07`**
   - Parent Branch: **`main`**
   - Region: **`aws-ap-southeast-1`**
   - Compute: **`shared-0.25` CU**
   - Recovery Protocol: **Freeze-on-failure; no automated downgrade**
   - Staging Retention: **24 hours post-verification**
3. Complete lines 54–65 of [`docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md) with authentic name, email, date, checked gates, and digital signature/token.
