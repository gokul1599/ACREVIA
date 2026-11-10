# ACREVIA — PHASE 07: GATE-05 RETENTION & TEARDOWN READINESS
## Ephemeral Lifecycle, Evidence Preservation & Governed Deprovisioning Protocol

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document ID:** `ACR-SEC-P07-GATE05-TEARDOWN-READINESS`  
**Governing Phase:** Phase 07 — Controlled Mode B Infrastructure Operations  
**Target Gate:** GATE-05 — Staging Retention and Teardown Authorization  
**Release Date:** November 10, 2026  
**Security Classification:** RESTRICTED — PILOT GOVERNANCE & ARCHITECTURAL AUDIT  
**Gate Readiness State:** **`LOCAL_PREPARATION_COMPLETE / AWAITING_GATE_05_AUTHORIZATION`**  
**Execution Status:** **`STRICTLY UNEXECUTED ON CLOUD`**  

---

## 1. Executive Summary

GATE-05 governs the controlled decommissioning, data retention, and eventual teardown of the isolated Neon staging branch (`staging-rls-phase07`).

Because staging environments in cloud providers incur potential storage and quota allocation, a formal lifecycle must balance cost minimization against forensic auditability. Destroying an environment prematurely destroys the evidence required for regulatory and compliance audits. Conversely, leaving environments indefinitely increases organizational cloud sprawl and billing.

This dossier establishes:
1. The 24-hour governed audit retention window.
2. The strict decoupling of failure states from automatic teardown.
3. The evidence preservation protocol ensuring physical proof persists permanently.
4. A dry-run teardown procedure ensuring zero impact on the parent trunk `main` or production database.
5. The non-negotiable owner sign-off requirement for final destruction.

---

## 2. Controlled Staging Lifecycle Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STAGING ENVIRONMENT LIFECYCLE (PHASE 07)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  [GATE-01] Provision Ephemeral Staging Branch (staging-rls-phase07)          │
│      │                                                                      │
│      ▼                                                                      │
│  [GATE-02] Provision Least-Privilege Roles (acrevia_staging_app)            │
│      │                                                                      │
│      ▼                                                                      │
│  [GATE-03] Execute 751 Atomic DDL Statements (Migration a1089411c87d)       │
│      │                                                                      │
│      ▼                                                                      │
│  [GATE-04] Execute Verification Harness (10 Cross-Tenant CRUD Probes)       │
│      │                                                                      │
│      ├─── IF SUCCESS ───► Extract Catalog & Test Proof to Version Control   │
│      │                          │                                           │
│      │                          ▼                                           │
│      │                    24-Hour Evidence Audit Window (Auto-Suspended)    │
│      │                          │                                           │
│      │                          ▼                                           │
│      │                    [GATE-05] Owner-Authorized Teardown & Deletion    │
│      │                                                                      │
│      └─── IF FAILURE ───► FREEZE IN PLACE (Auto-Suspend 5 min)              │
│                           Zero Auto-Downgrade | Zero Auto-Deletion          │
│                           Export Trace Logs for Forensic Investigation      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Mandatory Safety Rules Against Automatic Teardown

> [!CAUTION]
> The following actions are **STRICTLY PROHIBITED** in all automation scripts and deployment workflows:

1. **NEVER Automatically Delete Staging on Test Failure:**  
   Deleting a failed branch destroys the exact PostgreSQL catalog, role grants, and policy states needed to diagnose the failure.
2. **NEVER Automatically Downgrade on Failure:**  
   Running Alembic downgrade mutates the database state and strips away row-level security. A failed environment must be frozen as-is.
3. **NEVER Delete a Branch Based Solely on Branch Name:**  
   Teardown commands must verify both `project_id` (`prj_acrevia_pilot`) and the exact unique `branch_id` returned during GATE-01 provisioning.
4. **NEVER Touch Parent Trunk `main`:**  
   Teardown logic must assert `branch_id != parent_branch_id` and explicitly block any command targeting `main`.

---

## 4. Evidence Preservation Protocol

Before any staging branch is destroyed, all physical evidence must be extracted, committed to Git version control, and preserved in `docs/pilot/security/`:

| Evidence Artifact | Content Description | Target Local Path |
| :--- | :--- | :--- |
| **System Catalog Dump** | `pg_class` rows showing 132 `relrowsecurity = true` and 91 `relforcerowsecurity = true` | `docs/pilot/security/LIVE_STAGING_CATALOG_PROOF.txt` |
| **Policy Definitions** | Full output of `pg_policies` showing 264 installed policies | `docs/pilot/security/LIVE_STAGING_POLICIES_PROOF.txt` |
| **Role Verification** | `pg_roles` showing `acrevia_staging_app` attributes (`NOSUPERUSER`, `NOBYPASSRLS`) | `docs/pilot/security/LIVE_STAGING_ROLES_PROOF.txt` |
| **Harness Execution Log** | Complete console output from `scripts/verify_staging_rls.py` | `docs/pilot/security/LIVE_STAGING_HARNESS_LOG.txt` |
| **Risk Register Closure** | Signed update transitioning `DB-RLS-01` to `CLOSED_PHYSICALLY_VERIFIED` | `docs/pilot/security/ACREVIA_GLOBAL_RISK_REGISTER_PHASE_07.md` |

---

## 5. Dry-Run Teardown Plan & Safeguards

The deprovisioning harness must execute a dry-run preflight check before issuing the destructive delete command:

### Dry-Run Verification Checklist:
- [ ] Confirm all 5 evidence artifacts listed in Section 4 are committed to Git.
- [ ] Confirm GATE-05 is explicitly approved and signed by the Project Owner.
- [ ] Verify target branch ID is NOT the parent branch `main`.
- [ ] Verify target branch endpoint is NOT production `ep-muddy-mode-a1nd6rrb...`.
- [ ] Verify that 24 hours have elapsed since verification completion (or owner explicitly waived retention).

---

## 6. Deprovisioning Commands for Authorized Operator (On Hold)

Once GATE-05 is formally authorized:
```bash
# Step 1: Pre-deletion safety assertion (Verify target is NOT parent or production)
python -c "
from scripts.neon_staging_branch_spec import is_production_url
assert not is_production_url('$STAGING_DATABASE_URL'), 'ABORT: Target URL matches production!'
print('Target URL confirmed non-production.')
"

# Step 2: Delete staging branch using Neon CLI
neon branches delete staging-rls-phase07 --project-id prj_acrevia_pilot

# Step 3: Verify deletion from active branch inventory
neon branches list --project-id prj_acrevia_pilot

# Step 4: Record deletion timestamp and deprovisioning confirmation in execution dossier
```

---

## 7. Failure Handling During Teardown

If `neon branches delete` fails or times out:
1. Check whether compute auto-suspend has engaged (compute should be suspended after 5 minutes idle).
2. Query branch status via Neon CLI to determine if deletion was partially processed.
3. If branch remains active, re-attempt deletion via the authenticated Neon Cloud Console.
4. Document the final state in `docs/pilot/security/PHASE_07_GATE_05_RETENTION_AND_TEARDOWN_READINESS.md`.
