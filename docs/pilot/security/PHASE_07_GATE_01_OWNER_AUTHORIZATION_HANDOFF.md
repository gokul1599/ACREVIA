# ACREVIA — PHASE 07: GATE-01 OWNER AUTHORIZATION HANDOFF
## Final Authorization Readiness, Blocker Management & Pre-Execution Governance

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document ID:** `ACR-SEC-P07-GATE01-HANDOFF`  
**Governing Phase:** Phase 07 — Controlled Mode B Infrastructure Operations  
**Target Gate:** GATE-01 — Isolated Neon Staging Branch Provisioning  
**Release Date:** November 10, 2026  
**Security Classification:** RESTRICTED — PILOT GOVERNANCE & AUDIT TRAIL  
**Governance State:** **`READY_FOR_GENUINE_OWNER_REVIEW`**  
**Execution Blocker:** **`AWAITING_OWNER_AUTHORIZATION`** (`OWNER-AUTH-01`)  

---

## 1. Executive Summary

This Owner Authorization Handoff document provides the Project Owner with a definitive, structured brief on the exact state of **Phase 07 GATE-01 (Isolated Neon Staging Branch Provisioning)**.

The previous operational attempt to execute GATE-01 was evaluated and correctly halted under the mandatory stop condition:
$$\text{Status} = \mathbf{BLOCKED\_BY\_OWNER\_AUTHORIZATION}$$

Because the Project Owner Authorization Register remains unpopulated and unsigned, zero remote cloud commands were executed, zero Neon database branches were created, and zero production endpoints were contacted.

This handoff establishes:
1. The audited status of all five decision gates.
2. The exact operational boundary and scope authorized by GATE-01.
3. The division of responsibilities across Owner, Account Administrator, and Engineering teams.
4. The prerequisites (Neon account access, live parent privacy check, cost ceilings) that unlock execution.
5. The unambiguous retry criteria and strict prohibitions preventing scope creep into subsequent gates.

With all technical specifications reconciled, the authorization packet is formally designated as **`READY_FOR_GENUINE_OWNER_REVIEW`**.

---

## 2. Latest Execution Outcome

| Dimension | Audited Reality | Evidence / Finding | Governance Impact |
| :--- | :--- | :--- | :--- |
| **Operational Command** | GATE-01 Branch Provisioning | Halted prior to network transmission | Zero cloud mutations |
| **Execution Result** | `BLOCKED_BY_OWNER_AUTHORIZATION` | Line 59 of register is unchecked | Mode B locked |
| **Operating Mode** | `MODE_A_PREFLIGHT_COMPLETE` | Preserved in local read-only state | Production protected |
| **Repository Baseline** | Branch `main`, Commit `428812d` | `git status` clean tracked tree | Baseline intact |
| **Neon Provider Status** | Uncontacted | Zero API requests issued | Zero cost incurred |

---

## 3. Authorization Register Status

Inspection of [`docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md) (Lines 24–67) confirms:

```text
GATE-01:  [ ] UNCHECKED (AWAITING SIGN-OFF) — Provisioning Neon branch 'staging-rls-phase05'
GATE-02:  [ ] UNCHECKED (AWAITING SIGN-OFF) — Creating unprivileged role 'acrevia_staging_app'
GATE-03:  [ ] UNCHECKED (AWAITING SIGN-OFF) — Executing migration 'a1089411c87d' (751 atomic DDL)
GATE-04:  [ ] UNCHECKED (AWAITING SIGN-OFF) — Running live verification harness
GATE-05:  [ ] UNCHECKED (AWAITING SIGN-OFF) — Authorizing 24-hour teardown schedule

Project Owner Name:             ________________________________________________________ [BLANK]
Project Owner Email/ID:         ________________________________________________________ [BLANK]
Institutional Role / Title:     ________________________________________________________ [BLANK]
Date of Sign-off (YYYY-MM-DD):  ________________________________________________________ [BLANK]
Digital Signature / Token:      ________________________________________________________ [BLANK]
```

**Finding:** The register is 100% unsigned and unpopulated. Engineering will never infer, simulate, or fabricate owner approval.

---

## 4. Owner Decisions Required

Before GATE-01 can execute, the Project Owner must render explicit decisions on four core parameters:

1. **Target Branch Name Selection:**
   - *Option A:* `staging-rls-phase05` (Matches historical text in line 59 of the register).
   - *Option B (Recommended):* `staging-rls-phase07` (Provides clean 1-to-1 audit traceability with Phase 07 documentation).
2. **Parent Branch Approval:**
   - Confirm parent trunk as `main`, which contains 100% synthetic seed data.
3. **Infrastructure Sizing & Auto-Suspend:**
   - Approve `shared-0.25` compute units with 5-minute auto-suspend in region `aws-ap-southeast-1` (Singapore).
4. **Billing & Cost Acknowledgment:**
   - Acknowledge that while compute consumption is minimal (~0.125 CU-hours for 30 minutes), cloud usage is billed against the owner's Neon organizational account.

---

## 5. Precise Scope of GATE-01

To prevent scope creep, the boundary of GATE-01 is explicitly demarcated:

### What GATE-01 AUTHORIZES:
- Identification of Neon pilot project `prj_acrevia_pilot`.
- Querying Neon API for account tier, branch quota, and compute availability.
- Performing a live, read-only aggregate parent database privacy check.
- Performing a collision check for `staging-rls-phase07`.
- Executing `neon branches create --name <approved-name> --parent main`.
- Read-only post-provisioning inspection of branch metadata, region, compute, and endpoint status.

### What GATE-01 DOES NOT AUTHORIZE (Strictly Excluded):
- Creating database roles (`acrevia_staging_app`, `acrevia_admin`) &rarr; **Requires GATE-02**.
- Applying Alembic migration `a1089411c87d` or 751 atomic DDL &rarr; **Requires GATE-03**.
- Executing `scripts/verify_staging_rls.py` or cross-tenant CRUD tests &rarr; **Requires GATE-04**.
- Deprovisioning or deleting the staging branch &rarr; **Requires GATE-05**.

---

## 6. Approved Staging Infrastructure Configuration

| Parameter | Recommended Specification | Operational Constraint |
| :--- | :--- | :--- |
| **Neon Project** | ACREVIA pilot project (`prj_acrevia_pilot`) | Must match approved project ID |
| **Parent Branch** | `main` | Audited synthetic seed branch |
| **Staging Branch Name** | `staging-rls-phase07` *(or `staging-rls-phase05`)* | Decided by Project Owner |
| **Region** | `aws-ap-southeast-1` (Singapore) | Matches production latency zone |
| **Compute Type** | `shared-0.25` CU | Minimum provisionable serverless compute |
| **Auto-Suspend** | 5 minutes | Prevents idle credit burn |
| **Database Container** | `neondb_staging` | Standard staging database container |
| **Retention Schedule** | 24 hours post-verification | Governed by GATE-05 |

---

## 7. Cost Transparency & Provider Uncertainties

The engineering team provides the following transparent financial disclosure:

1. **Estimated Resource Consumption:**
   $$\text{Compute Time} = 0.5\ \text{hours} \times 0.25\ \text{CU} = \mathbf{0.125\ \text{CU-hours}}$$
   At standard provider rates (~$0.16/CU-hour), total estimated compute cost is **under \$0.05 USD**.
2. **Storage Allocation:**
   Neon copy-on-write branches consume zero additional storage pages at inception; storage costs accrue only as new blocks are written during migrations.
3. **Provider Account Uncertainties (Unverifiable without Account Access):**
   - *Account Plan:* Whether the account operates under Free tier (100 CU-hours/month quota) or a paid plan (Launch/Scale).
   - *Branch Quota:* Whether the project has available branch slots (Free plan limit: 10 branches).
   - *Overage Incurrence:* If the account's free allowance is exhausted, provider overage charges will apply.
4. **Owner Safeguard:**
   Engineering will not upgrade plans or purchase compute credits. If quotas are exceeded, execution halts immediately with `BLOCKED_BY_BILLING_OR_QUOTA`.

---

## 8. Live Parent-Data Privacy Requirements

> [!CRITICAL]
> Although historical audits ([`PHASE_07_NEON_PARENT_DATA_PRIVACY_GATE.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_NEON_PARENT_DATA_PRIVACY_GATE.md)) confirm 100% synthetic seed data on `main`, **live parent privacy has NOT been freshly verified against the cloud database** because remote connections are prohibited in Mode A.

### Mandatory Pre-Provisioning Live Privacy Check:
Immediately upon receipt of owner authorization and prior to issuing `neon branches create`, engineering must:
1. Connect in read-only mode to the parent endpoint.
2. Execute schema-accurate aggregate count queries across personal data tables:
   ```sql
   -- Total distinct users
   SELECT count(*) FROM users;
   
   -- Distinct farmer accounts via user_roles join
   SELECT count(DISTINCT ur.user_id) 
   FROM user_roles ur 
   JOIN roles r ON r.id = ur.role_id 
   WHERE r.id = 'FARMER';
   
   -- Core domain entities
   SELECT count(*) FROM farms;
   SELECT count(*) FROM plots;
   
   -- Non-synthetic email domain check (synthetic seed uses @acrevia.test)
   SELECT count(*) FROM users 
   WHERE email IS NOT NULL AND email NOT LIKE '%@acrevia.test';
   ```
3. Confirm that all row counts reflect known synthetic test profiles only.
4. **Zero-Export Rule:** Under no circumstances will any personal records, phone numbers, names, or GPS plot polygons be exported, logged, or printed.
5. If any real personal data is detected: **ABORT IMMEDIATELY** with `BLOCKED_BY_PARENT_PRIVACY`.

---

## 9. Account Access Requirements

To execute GATE-01, the Account Administrator must provide valid cloud credentials:

1. **Neon API Access Token:** An authorized API key (`NEON_API_KEY`) with permissions to create branches in `prj_acrevia_pilot`.
2. **Environment Injection:** The token must be set in the secure execution environment prior to running the provisioning harness.
3. **Least Privilege:** The token requires branch management privileges only; full organization administrative control is not required.
4. **Secret Handling:** API keys and connection strings must be completely redacted in all generated documentation and console output.

---

## 10. Engineering Responsibilities Checklist

Upon receipt of attributable owner sign-off and account access, the engineering team guarantees:

- [ ] **Collision Check:** Verify `staging-rls-phase07` does not already exist on Neon.
- [ ] **Project Identity Match:** Verify project identifier matches `prj_acrevia_pilot`.
- [ ] **Quota Verification:** Verify available branch slots prior to request.
- [ ] **Live Privacy Probe:** Execute aggregate synthetic count on parent `main`.
- [ ] **Branch Provisioning:** Issue `neon branches create` with exact approved parameters.
- [ ] **Metadata Capture:** Record branch ID, region, and compute configuration.
- [ ] **Production Boundary Check:** Verify endpoint `ep-muddy-mode-a1nd6rrb...` remains isolated.
- [ ] **Evidence Dossier:** Update [`PHASE_07_GATE_01_BRANCH_PROVISIONING_REPORT.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GATE_01_BRANCH_PROVISIONING_REPORT.md) with physical proof.

---

## 11. Retry Conditions & State Machine

When GATE-01 is re-evaluated, execution must transition into exactly one of the following states:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       GATE-01 RETRY DECISION MATRIX                         │
├───────────────────────────────────┬─────────────────────────────────────────┤
│ Condition Evaluated               │ Resulting Status Code                   │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ Register remains unsigned         │ BLOCKED_BY_OWNER_AUTHORIZATION          │
│ Register signed, but no API key   │ BLOCKED_BY_MISSING_ACCOUNT_ACCESS       │
│ API key present, parent has PII   │ BLOCKED_BY_PARENT_PRIVACY               │
│ Quota full or billing exceeded    │ BLOCKED_BY_BILLING_OR_QUOTA             │
│ Branch name already exists        │ BLOCKED_BY_CONFIGURATION_MISMATCH       │
│ Provider API call errors          │ FAILED_STAGING_PROVISIONING             │
│ All checks pass, branch created   │ GATE01_STAGING_BRANCH_PROVISIONED       │
└───────────────────────────────────┴─────────────────────────────────────────┘
```

> [!NOTE]
> GATE-01 will **not** be retried in a continuous loop while the register remains unchanged. Re-invocation is triggered only upon formal notification of owner sign-off.

---

## 12. Prohibited Subsequent Operations

Even after GATE-01 succeeds and the staging branch is provisioned, the following operations remain **STRICTLY PROHIBITED** until their governing gates are independently signed:

- **DO NOT create database roles** (`acrevia_staging_app`, `acrevia_admin`) &rarr; Governed by **GATE-02**.
- **DO NOT execute migration `a1089411c87d`** &rarr; Governed by **GATE-03**.
- **DO NOT apply 751 atomic DDL statements** &rarr; Governed by **GATE-03**.
- **DO NOT run `scripts/verify_staging_rls.py`** &rarr; Governed by **GATE-04**.
- **DO NOT execute cross-tenant CRUD probes** &rarr; Governed by **GATE-04**.
- **DO NOT deprovision or delete the branch** &rarr; Governed by **GATE-05**.

---

## 13. Final Owner Action Required

To authorize the provisioning of the isolated Neon staging branch, the Project Owner must complete the following actions:

1. **Review Documentation:**
   - [`PHASE_07_GATE_1_FINAL_OWNER_DECISION_BRIEF.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GATE_1_FINAL_OWNER_DECISION_BRIEF.md)
   - [`PHASE_07_GATE_1_FINAL_GOVERNANCE_ADDENDUM.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GATE_1_FINAL_GOVERNANCE_ADDENDUM.md)
   - This Handoff Document ([`PHASE_07_GATE_01_OWNER_AUTHORIZATION_HANDOFF.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GATE_01_OWNER_AUTHORIZATION_HANDOFF.md))
2. **Fill & Sign Authorization Register:**
   Open [`docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md) and complete lines 54–65:
   - Check `[x] GATE-01 APPROVED` (and confirm target branch name as `staging-rls-phase07`).
   - Populate Name, Email/ID, Institutional Title, and Date.
   - Enter Digital Signature or Authorization Token.
3. **Notify Engineering Team:**
   Confirm authorization completion so that Mode B Infrastructure Operation 01 may proceed cleanly and safely.
