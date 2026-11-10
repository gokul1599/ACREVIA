# ACREVIA — PHASE 07: OWNER AUTHORIZATION & DECISION REGISTER

**Project:** ACREVIA — Agricultural Intelligence Platform  
**Document ID:** `ACR-SEC-AUTH-P07`  
**Governing Phase:** Phase 07 — Isolated Neon Staging Execution & PostgreSQL RLS Validation  
**Release Date:** November 10, 2026  
**Security Classification:** RESTRICTED — PILOT GOVERNANCE  

---

## 1. Governance Architecture & Operating Modes

To safeguard production integrity and institutional confidentiality, ACREVIA operates under a two-phase governance gate model:

- **MODE A — PRE-AUTHORIZATION SECURITY PREFLIGHT (ACTIVE):**
  - All local audits, DDL compilation checks, in-memory isolation simulations, and static security evaluations are executed.
  - Zero cloud network calls, zero branch provisioning, and zero production database queries are permitted.
- **MODE B — AUTHORIZED REMOTE CLOUD EXECUTION (PENDING OWNER APPROVAL):**
  - Triggered only upon explicit, attributable owner authorization.
  - Provisions an isolated Neon staging database branch (`staging-rls-phase05`) in Singapore (`aws-ap-southeast-1`), creates restricted runtime role `acrevia_staging_app`, executes Alembic migration `a1089411c87d`, runs `verify_staging_rls.py`, and records physical evidence.

---

## 2. Decision Gate Register

| Gate ID | Target Decision Scope | Authority | Current State | Mode Impact |
| :--- | :--- | :--- | :--- | :--- |
| **GATE-01** | Provisioning of isolated Neon staging branch `staging-rls-phase05` from parent `main` in region `aws-ap-southeast-1`. | Project Owner | `[ ] UNCHECKED (AWAITING SIGN-OFF)` | Unlocks Mode B remote branch creation. |
| **GATE-02** | Creation of unprivileged runtime database role `acrevia_staging_app` (`NOSUPERUSER`, `NOBYPASSRLS`, `NOCREATEDB`, `NOCREATEROLE`). | Project Owner | `[ ] UNCHECKED (AWAITING SIGN-OFF)` | Unlocks role provisioning on staging branch. |
| **GATE-03** | Physical execution of Alembic RLS migration `a1089411c87d` applying 751 atomic DDL statements to `neondb_staging`. | Project Owner | `[ ] UNCHECKED (AWAITING SIGN-OFF)` | Unlocks database schema mutation on staging. |
| **GATE-04** | Execution of automated staging RLS verification harness (`scripts/verify_staging_rls.py`) against live staging endpoint. | Project Owner | `[ ] UNCHECKED (AWAITING SIGN-OFF)` | Unlocks automated catalog probe and cross-tenant tests. |
| **GATE-05** | Teardown and deprovisioning schedule of `staging-rls-phase05` post-verification. | Project Owner | `[ ] UNCHECKED (AWAITING SIGN-OFF)` | Controls cloud resource retention and cleanup. |

---

## 3. Infrastructure & Cost Safety Commitments

Prior to requesting owner sign-off, the engineering team guarantees the following technical guardrails:

1. **Compute Sizing:** Target compute is constrained to `shared-0.25` compute units (CU) with auto-suspend set to 5 minutes, incurring minimal cost within the Neon free/pilot tier allowance.
2. **Production Isolation:** The production database endpoint (`ep-muddy-mode-a1nd6rrb...`) will receive zero connections, zero migrations, and zero role adjustments.
3. **Parent Data Privacy:** The parent branch was audited in [`docs/pilot/security/PHASE_07_NEON_PARENT_DATA_PRIVACY_GATE.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_NEON_PARENT_DATA_PRIVACY_GATE.md) and confirmed to contain 100% synthetic seed data. Zero real farmer PII exists in the database.

---

## 4. Owner Authorization Sign-Off Block

*To authorize transition from Mode A to Mode B, the Project Owner must complete the fields below:*

```text
========================================================================================
ACREVIA PHASE 07 — OWNER AUTHORIZATION SIGN-OFF
========================================================================================
Project Owner Name:             ________________________________________________________
Project Owner Email/ID:         ________________________________________________________
Institutional Role / Title:     ________________________________________________________
Date of Sign-off (YYYY-MM-DD):  ________________________________________________________

[ ] GATE-01 APPROVED: Provision Neon branch 'staging-rls-phase05' (aws-ap-southeast-1)
[ ] GATE-02 APPROVED: Create restricted role 'acrevia_staging_app'
[ ] GATE-03 APPROVED: Execute migration 'a1089411c87d' on staging branch
[ ] GATE-04 APPROVED: Run live staging verification harness
[ ] GATE-05 APPROVED: Authorize automated branch teardown 24 hours post-verification

Digital Signature / Token:      ________________________________________________________
========================================================================================
```

---

## 5. Next Authorized Engineering Action

Until the above sign-off block is completed:
1. The repository remains in **MODE A — PRE-AUTHORIZATION PREFLIGHT**.
2. All local tests and documentation updates are preserved and committed to version control.
3. No remote cloud modifications will be attempted.
