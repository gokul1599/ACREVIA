# ACREVIA — PHASE 05 OWNER INPUT & APPROVAL CHECKLIST

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document Purpose:** Independent Decision Gate Register for Project Leadership  
**Execution Date:** November 9, 2026  
**Operational Status:** `AWAITING_OWNER_INPUT`

---

## 1. Owner & Sender Contact Specification

Please complete the following professional identity parameters in [`docs/pilot/PHASE_02_OWNER_INPUT_AND_AUTHORIZATION_FORM.md`](../PHASE_02_OWNER_INPUT_AND_AUTHORIZATION_FORM.md):

```
[  ] Project Owner Full Name:        [OWNER INPUT REQUIRED]
[  ] Professional Designation:       [OWNER INPUT REQUIRED]
[  ] Institutional Affiliation:     [OWNER INPUT REQUIRED]
[  ] Monitored Sender Email:        [OWNER INPUT REQUIRED]
[  ] Monitored Contact Mobile:       [OPTIONAL OWNER INPUT]
```

---

## 2. Independent Decision Gates

Each gate is strictly independent. Approving one gate does not grant authorization for any other action.

### Decision Gate 1: Isolated Neon Staging Branch Creation
- **Action:** Authorize creating remote branch `staging-rls-phase05` on Neon PostgreSQL project.
- **Resource Scope:** Free-tier compute (shared-0.25 CU), Singapore (`sin1`). Zero production data.
- **Decision:** `[  ] AUTHORIZE` &nbsp;&nbsp;&nbsp;&nbsp; `[  ] HOLD` &nbsp;&nbsp;&nbsp;&nbsp; `[  ] REJECT`

### Decision Gate 2: Alembic Migration `a1089411c87d` Execution on Staging Branch
- **Action:** Execute RLS migration and policy creation on `staging-rls-phase05` using `neondb_owner`.
- **Scope:** 132 database tables. Creates base permissive policies and restrictive tenant isolation.
- **Decision:** `[  ] AUTHORIZE` &nbsp;&nbsp;&nbsp;&nbsp; `[  ] HOLD` &nbsp;&nbsp;&nbsp;&nbsp; `[  ] REJECT`

### Decision Gate 3: Institutional Outreach Package Approval
- **Action:** Approve non-commercial introductory emails to agricultural scientists.
  - Gate A01: KVK Malyal (Dr. Banoth Dileep Kumar) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `[  ] APPROVE  [  ] HOLD`
  - Gate A02: KVK Kampasagar (Dr. S. Srinivasa Rao) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `[  ] APPROVE  [  ] HOLD`
  - Gate A03: PJTSAU Directorate of Extension &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `[  ] APPROVE  [  ] HOLD`
  - Gate A04: ICAR-ATARI Zone X (Hyderabad) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `[  ] APPROVE  [  ] HOLD`

### Decision Gate 4: Vercel Preview Staging Cloud Deployment (Gate A08)
- **Action:** Trigger staging deployment on Vercel (`sin1`) with basic authentication.
- **Alternative:** Conduct live briefings using local screen sharing with synthetic data (Gate A07).
- **Decision:** `[  ] AUTHORIZE CLOUD URL` &nbsp;&nbsp;&nbsp;&nbsp; `[  ] HOLD (Local Share Only)` &nbsp;&nbsp;&nbsp;&nbsp; `[  ] REJECT`

### Decision Gate 5: Field Pilot Preparation & MoU Formulation (Gate A09)
- **Action:** Formulate non-binding institutional collaboration term sheet after briefings.
- **Decision:** `[  ] APPROVE` &nbsp;&nbsp;&nbsp;&nbsp; `[  ] HOLD (Recommended)` &nbsp;&nbsp;&nbsp;&nbsp; `[  ] REJECT`

---

## 3. Hard Gated Restrictions (Gates A10–A12)

The following activities remain **STRICTLY PROHIBITED** and cannot be authorized by preliminary correspondence:
- **Gate A10:** Farmer recruitment and surveying (`NOT_AUTHORIZED`).
- **Gate A11:** Farmer personal data, mobile numbers, or GPS coordinate collection (`NOT_AUTHORIZED`).
- **Gate A12:** On-farm field pilot trials or chemical recommendations (`NOT_AUTHORIZED`).
