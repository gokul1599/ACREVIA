# ACREVIA — PHASE 07 NEON PARENT-DATA PRIVACY GATE AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document Code:** `PHASE_07_NEON_PARENT_DATA_PRIVACY_GATE.md`  
**Execution Date:** November 10, 2026  
**Auditor Status:** AUDITED & PRIVACY GATE ENFORCED  
**Privacy Gate Verdict:** **`PASS_SYNTHETIC_ONLY_DATASET / HELD_PENDING_OWNER_BRANCH_AUTHORIZATION`**  

---

## 1. Executive Summary & Privacy Gate Mandate

In serverless cloud databases like Neon PostgreSQL, child branches (`staging-rls-phase05`) are created using Copy-on-Write (CoW). A child branch inherits the exact state of its parent branch at the moment of creation, including all rows, schemas, and credentials.

Before any child branch is spawned:
1. It must be proven whether the parent branch contains any real farmer, user, personal, institutional, private financial, consent, or farm-coordinate data.
2. If real personal data exists on the parent, branch creation is **STRICTLY BLOCKED** to prevent unconsented replication under India's Digital Personal Data Protection (DPDP) Act 2023.

---

## 2. Evidence-Based Parent Branch Inspection

An exhaustive forensic audit of all data ingestion paths, database seeds, and project operational registers confirms:

### A. Database Seed Analysis ([`init_db.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/init_db.py))
The database initialization script seeds only:
- 4 system roles (`FARMER`, `AGRICULTURAL_EXPERT`, `RESEARCHER`, `ADMIN`).
- 3 public crop definitions (`cotton`, `rice`, `chilli`) with scientific nomenclature.
- 5 agronomic pest/disease risk rules derived from published PJTSAU bulletins.
- Public Knowledge Graph nodes for agronomic conditions.

### B. Standing Governance Register State
Throughout all 6 development phases, the project leadership has maintained:
- `FARMER_RECRUITMENT_STARTED = FALSE`
- `FARMER_DATA_COLLECTION_STARTED = FALSE`
- `FIELD_PILOT_STATUS = NOT_AUTHORIZED`
- `DPDP_COMPLIANCE_CERTIFICATION = NOT_CLAIMED`

### C. Live Production Endpoint Protection
The live production database endpoint:
`ep-muddy-mode-a1nd6rrb-pooler.ap-southeast-1.aws.neon.tech`
has never been queried, migrated, or populated with personal farmer survey data. Zero real farmer names, phone numbers, Aadhaar numbers, or GPS plot polygons exist in any ACREVIA database.

---

## 3. Privacy Boundary Assessment

| Data Category | Present in Parent Branch? | Verification Evidence | Privacy Risk Assessment |
|---|:---:|---|---|
| **Real Farmer Identifiers** | **NO** | `FARMER_RECRUITMENT_STARTED = FALSE` across all phases. | **ZERO RISK** |
| **Aadhaar / National ID** | **NO** | No schema field exists for government IDs. | **ZERO RISK** |
| **Farm Coordinates (GPS)** | **NO** | Zero on-farm surveys conducted. | **ZERO RISK** |
| **Institutional Contacts** | **NO** | Introductory outreach held pending Gate 3. | **ZERO RISK** |
| **Financial / Banking Info**| **NO** | Ledger contains synthetic mock transactions only. | **ZERO RISK** |
| **Authentication Passwords**| **NO** | Seed users use synthetic bcrypt hashes; 0 real accounts. | **ZERO RISK** |
| **Foliar Pathology Media** | **NO** | Synthetic Kaggle/PlantVillage open-access benchmarks only. | **ZERO RISK** |

---

## 4. Mode A Enforcement: Branch Creation Block

Although the data boundary is confirmed 100% synthetic, **branch creation remains BLOCKED in Mode A** because:
1. Decision Gate 1 (`NEON_BRANCH_AUTHORIZATION`) has not received explicit, attributable sign-off from the project owner.
2. In accordance with Section 10 of the Phase 07 directive:
   "An incomplete form, an empty checkbox, an inferred approval, or a general statement of project support is not authorization. If any authorization condition fails, return to Mode A."

---

## 5. Approved Staging Branch Alternative (Ready for Mode B)

Upon owner authorization of Decision Gate 1, the safe staging branch deployment must follow this isolated sequence:
1. Create ephemeral child branch:
   `neon branches create --name staging-rls-phase05 --parent main`
2. Create unprivileged runtime application role:
   `neon roles create --branch staging-rls-phase05 --name acrevia_staging_app`
3. Execute migration `a1089411c87d` using `neondb_owner`.
4. Run verification harness [`scripts/verify_staging_rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/scripts/verify_staging_rls.py).
5. Destroy branch upon verification completion.
