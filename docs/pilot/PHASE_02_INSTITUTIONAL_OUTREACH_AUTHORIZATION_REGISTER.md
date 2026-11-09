# ACREVIA — PHASE 02 INSTITUTIONAL OUTREACH AUTHORIZATION REGISTER
## FORMAL GO/NO-GO GATING DECISION & EXECUTIVE AUTHORIZATION PROTOCOL

**Programme:** ACREVIA Agricultural Intelligence Platform  
**Document Code:** `PHASE_02_INSTITUTIONAL_OUTREACH_AUTHORIZATION_REGISTER.md`  
**Audit Baseline Commit:** `2af491e49be8beb1d28fc03e42f642ed4fb7b21b` (`2af491e`)  
**Target Institutions:**
- KVK Malyal — Mahabubabad District, Telangana
- KVK Kampasagar — Nalgonda District, Telangana  
**Parent University:** Professor Jayashankar Telangana State Agricultural University (PJTSAU)  
**Date of Audit Review:** November 9, 2026  

---

## 1. Executive Outreach Gate Decision

The independent technical, security, and institutional audit evaluated the platform across twelve distinct operational dimensions.

### Gate Classification: **`GO_FOR_OUTREACH`**
*(Subject to Explicit Owner Sign-Off Prior to Email Transmission)*

```
+========================================================================================================================+
| FORMAL GATING STATUS REGISTER                                                                                          |
+----+--------------------------------------------+-----------------------+----------------------------------------------+
| #  | Operational Milestone Stage                | Status Decision       | Operational Directive                        |
+----+--------------------------------------------+-----------------------+----------------------------------------------+
| 01 | Phase 01 Technical & Testing Baseline      | COMPLETE_VERIFIED     | 252/252 automated tests passing (100% pass)  |
| 02 | Phase 01 Staging Deployment Configuration  | COMPLETE_WITH_LIMITS  | Configuration verified; live deploy pending  |
| 03 | Phase 02 Institutional Outreach Gate       | GO_FOR_OUTREACH       | Outreach collateral verified; owner sign-off |
| 04 | Phase 03 Farmer Enrolment & Field Trial    | NOT_AUTHORIZED        | Strictly prohibited until formal MoU executed|
+----+--------------------------------------------+-----------------------+----------------------------------------------+
```

> [!CAUTION]
> **CRITICAL OPERATIONAL BOUNDARY:**  
> Approval of `GO_FOR_OUTREACH` permits the project owner to authorize sending introductory email inquiries and proposals to the Programme Coordinators of KVK Malyal and KVK Kampasagar.  
> **IT DOES NOT AUTHORIZE FARMER RECRUITMENT, FIELD DATA COLLECTION, OR ON-FARM TRIALS.**  
> `FIELD_PILOT_STATUS = NOT_AUTHORIZED` until institutional MoUs and formal farmer consent are executed.

---

## 2. Master 12-Dimension Readiness Assessment

| Dimension ID | Operational Readiness Dimension | Audit Status | Key Evidence / Verification Basis | Remaining Dependencies |
|---|---|---|---|---|
| **R01** | Repository Integrity & Reproducibility | `COMPLETE_VERIFIED` | Git HEAD `2af491e` verified; working tree clean; commit lineage unbroken | None |
| **R02** | Automated Test Verification | `COMPLETE_VERIFIED` | 252 physical tests collected and passing (145 backend + 55 ML + 9 vision + 43 frontend); 0 TS errors | None |
| **R03** | Actual Staging Deployment | `COMPLETE_WITH_LIMITATIONS` | `frontend/vercel.json`, `sin1` region, `.env.staging.example` verified; live preview deploy pending | Owner authorization for live preview deploy |
| **R04** | Neon DB Staging & Tenant Isolation | `COMPLETE_WITH_LIMITATIONS` | App-layer isolation verified (HTTP 403 on cross-tenant read); Postgres-level RLS deferred to next milestone | Alembic migration for DB engine RLS |
| **R05** | AI Availability, Billing & Fallback | `COMPLETE_WITH_LIMITATIONS` | Preview model `qwen/qwen3.8-27b` with extractive fallback; account billing status `NOT_VERIFIABLE` | Confirm zero credit card on Groq console |
| **R06** | Weather & Satellite Resilience | `COMPLETE_VERIFIED` | Earth Search $\rightarrow$ Planetary Computer fallback verified; Open-Meteo 15-min cache verified; NDVI traced | None |
| **R07** | Redis & Rate-Limit Protection | `COMPLETE_WITH_LIMITATIONS` | Staging namespace `acrevia_staging` verified; uniform `fail_open` noted as P2 risk for auth endpoints | Add `fail_closed` to login route |
| **R08** | Data Governance & DPDP Compliance | `COMPLETE_VERIFIED` | Trilingual consent, farmer data ownership, 48-hour erasure protocol, no land titles requested | None |
| **R09** | Farmer Consent Preparation | `COMPLETE_VERIFIED` | Multilingual consent forms prepared in Telugu, English, Hindi in `docs/pilot/` | Ready for cohort execution |
| **R10** | Institutional Documentation Quality | `COMPLETE_VERIFIED` | KVK Malyal and Kampasagar proposals authored with complete agro-climatic context & MoU outlines | None |
| **R11** | Institutional Identity Verification | `COMPLETE_VERIFIED` | Official verification from `pjtsau.edu.in` and `telangana.gov.in` for both KVKs | None |
| **R12** | Field Pilot Research Protocol | `COMPLETE_VERIFIED` | Double-blind diagnostic verification, Cohen's Kappa concordance, water AWD metrics defined | Awaits KVK scientist alignment |

---

## 3. Executive Authorization Sign-Off Register

To execute Phase 02 institutional outreach, the project leadership must complete and sign this register:

```
+========================================================================================================================+
| PHASE 02 OUTREACH AUTHORIZATION FORM                                                                                   |
+------------------------------------------------+-----------------------------------------------------------------------+
| Authorization Action                           | Owner Decision & Signature                                            |
+------------------------------------------------+-----------------------------------------------------------------------+
| 1. Approval of KVK Malyal Collaboration Package| [  ] APPROVED    [  ] REVISE    Signature: __________________________ |
|                                                |                                 Date: _______________________________ |
+------------------------------------------------+-----------------------------------------------------------------------+
| 2. Approval of KVK Kampasagar Package          | [  ] APPROVED    [  ] REVISE    Signature: __________________________ |
|                                                |                                 Date: _______________________________ |
+------------------------------------------------+-----------------------------------------------------------------------+
| 3. Approval of Outreach Email Correspondence   | [  ] APPROVED    [  ] REVISE    Signature: __________________________ |
|                                                |                                 Date: _______________________________ |
+------------------------------------------------+-----------------------------------------------------------------------+
| 4. Authorization to Dispatch Introductory Mail | [  ] AUTHORIZED  [  ] HOLD      Signature: __________________________ |
|                                                |                                 Date: _______________________________ |
+------------------------------------------------+-----------------------------------------------------------------------+
```

---

## 4. Strictly Prohibited Operational Actions

Until formal written institutional partnership agreements are executed with KVK Malyal and KVK Kampasagar, the following activities remain **STRICTLY PROHIBITED**:

1. **NO Production Mutations:** No production database migrations, DDL executions, or configuration alterations.
2. **NO Premature Farmer Recruitment:** No recruiting farmers, surveying smallholders, or collecting farmer personal information.
3. **NO On-Farm Field Trials:** No deploying sensors, marking physical test plots, or conducting active agricultural interventions.
4. **NO Unapproved Third-Party Contact:** No contacting farmers, local agricultural extension officers, or input retailers without prior KVK coordination.
5. **NO Paid Service Activation:** No activating paid billing plans on Vercel, Neon, Groq, or Upstash.

---

## 5. Next Permitted Action Sequence

Upon obtaining owner signature on this register, the permitted operational sequence is:
1. **Action 1:** Transmit formal introductory outreach email to Programme Coordinator, KVK Malyal (`docs/pilot/kvk/KVK_OUTREACH_EMAIL_DRAFTS.md`, Section 1).
2. **Action 2:** Transmit formal introductory outreach email to Programme Coordinator, KVK Kampasagar (`docs/pilot/kvk/KVK_OUTREACH_EMAIL_DRAFTS.md`, Section 2).
3. **Action 3:** Transmit informational courtesy notice to Director of Extension, PJTSAU (`docs/pilot/kvk/KVK_OUTREACH_EMAIL_DRAFTS.md`, Section 3).
4. **Action 4:** Schedule and conduct a 20-minute virtual or in-person technical demonstration of the platform for KVK scientists.
5. **Action 5:** Draft and execute formal non-binding Memoranda of Understanding (MoU) with participating institutions.
