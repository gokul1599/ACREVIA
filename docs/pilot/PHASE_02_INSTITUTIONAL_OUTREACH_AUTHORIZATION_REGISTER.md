# ACREVIA — PHASE 02 INSTITUTIONAL OUTREACH AUTHORIZATION REGISTER
## FORMAL GO/NO-GO GATING DECISION & UNBUNDLED EXECUTIVE AUTHORIZATION PROTOCOL

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Document Code:** `PHASE_02_INSTITUTIONAL_OUTREACH_AUTHORIZATION_REGISTER.md`  
**Audited Baseline Commit:** `c329b67`  
**Target Geography:** Telangana, India  
**Target Institutions:**
1. Krishi Vigyan Kendra (KVK), Malyal — Mahabubabad District
2. Krishi Vigyan Kendra (KVK), Kampasagar — Nalgonda District
3. Professor Jayashankar Telangana State Agricultural University (PJTSAU) — Directorate of Extension
4. ICAR — Agricultural Technology Application Research Institute (ATARI), Zone X, Hyderabad  
**Date of Audit Review:** November 9, 2026  
**Outreach Gate Decision:** **`GO_FOR_OUTREACH_PENDING_OWNER_APPROVAL`**  
**Field Pilot Authorization Status:** **`FIELD_PILOT_STATUS = NOT_AUTHORIZED`**  
**Communication Dispatch Status:** **`INSTITUTIONAL_EMAILS_SENT = FALSE`**  
**Owner Approval Status:** **`OWNER_APPROVAL_STATUS = PENDING`**  

---

## 1. Executive Outreach Gate Decision

The independent technical, security, legal, and institutional audit evaluated the platform across twelve distinct operational dimensions.

### Gate Classification: **`GO_FOR_OUTREACH_PENDING_OWNER_APPROVAL`**
*(Subject to Explicit Owner Sign-Off Prior to Any External Communication)*

```
+========================================================================================================================+
| FORMAL GATING STATUS REGISTER                                                                                          |
+----+--------------------------------------------+-----------------------------------+----------------------------------+
| #  | Operational Milestone Stage                | Status Decision                   | Operational Directive            |
+----+--------------------------------------------+-----------------------------------+----------------------------------+
| 01 | Phase 01 Technical & Testing Baseline      | COMPLETE_VERIFIED                 | 252/252 tests passing (100% pass)|
| 02 | Phase 01 Staging Deployment Architecture   | COMPLETE_WITH_LIMITS              | Architecture verified; deploy held|
| 03 | Phase 02 Institutional Identity & Outreach | GO_FOR_OUTREACH_PENDING_APPROVAL  | Collateral verified; sign-off req|
| 04 | Phase 03 Farmer Enrolment & Field Trials   | NOT_AUTHORIZED                    | Strictly gated pending MoU/ethics|
+----+--------------------------------------------+-----------------------------------+----------------------------------+
```

> [!CAUTION]
> **CRITICAL OPERATIONAL BOUNDARY:**  
> The `GO_FOR_OUTREACH_PENDING_OWNER_APPROVAL` status establishes that all preparatory technical, governance, and institutional diligence is complete for owner review.  
> **IT DOES NOT AUTHORIZE TRANSMISSION OF EMAILS UNTIL EXPLICITLY SIGNED BELOW.**  
> **IT DOES NOT AUTHORIZE FARMER RECRUITMENT, SENSORS, OR ON-FARM FIELD INTERVENTIONS.**  
> `FIELD_PILOT_STATUS = NOT_AUTHORIZED` remains permanently enforced until formal institutional MoUs, ethical clearance, and bilingual farmer consent forms are executed.

---

## 2. Master 12-Dimension Readiness Assessment

| Dimension ID | Operational Readiness Dimension | Audit Status | Key Evidence / Verification Basis | Remaining Dependencies / Limits |
|---|---|---|---|---|
| **R01** | Repository Integrity & Lineage | `COMPLETE_VERIFIED` | HEAD `c329b67` on `main`; clean working tree; commit lineage unbroken | None |
| **R02** | Automated Test Verification | `COMPLETE_VERIFIED` | 252 physical tests collected and passing (145 backend + 55 ML + 9 vision + 43 frontend); 0 TS errors | None |
| **R03** | Staging Cloud Architecture | `COMPLETE_WITH_LIMITATIONS` | `frontend/vercel.json` (`sin1`), `.env.staging.example` verified; live deploy pending sign-off | Owner authorization for live preview deploy |
| **R04** | Neon DB Staging & Tenant Isolation | `COMPLETE_WITH_LIMITATIONS` | Application-layer tenant isolation verified (HTTP 403 on cross-tenant read); DB-level RLS deferred | Documented limitation (D2) |
| **R05** | AI Availability, Cost & Fallback | `COMPLETE_WITH_LIMITATIONS` | Preview model `qwen/qwen3.8-27b` with extractive RAG fallback; free-tier limits enforced | Documented limitation (D4, D10) |
| **R06** | Weather & Satellite Resilience | `COMPLETE_VERIFIED` | Earth Search $\rightarrow$ Planetary Computer fallback verified; Open-Meteo 15-min cache; NDVI verified | None |
| **R07** | Redis & Rate-Limit Protection | `COMPLETE_WITH_LIMITATIONS` | Staging namespace `acrevia_staging` isolated; fail-open noted as P2 risk for auth endpoints | Add `fail_closed` to login route |
| **R08** | Data Governance & DPDP Posture | `COMPLETE_WITH_LIMITATIONS` | Comprehensive data lifecycle mapped; `DPDP_COMPLIANCE_CERTIFICATION = NOT_CLAIMED` | Formal legal review required (D8) |
| **R09** | Farmer Consent Architecture | `COMPLETE_VERIFIED` | Trilingual consent forms prepared in Telugu, English, Hindi; right to withdraw documented | Awaits cohort onboarding |
| **R10** | Institutional Due Diligence | `COMPLETE_VERIFIED` | Four institutions verified against `pjtau.edu.in`, `icar.org.in`, `telangana.gov.in` | None |
| **R11** | Outreach Correspondence Quality | `COMPLETE_VERIFIED` | Culturally grounded, bilingual (EN/TE) drafts authored with `INTERNAL DRAFT` protections | Awaits owner sign-off |
| **R12** | Supervised Feasibility Protocol | `COMPLETE_VERIFIED` | 30-day feasibility protocol; expert adjudication; separation of feasibility from crop yield | Awaits KVK scientist alignment |

---

## 3. Preparation vs Review vs Authorization Matrix

| Work Item | Preparation Status | Review Status | Owner Approval Status |
|---|---|---|---|
| Technical Audit (252 physical tests) | `COMPLETE` | `VERIFIED` | `[ ] APPROVED   Initials: _______` |
| Four-Institution Identity & Contacts | `COMPLETE` | `VERIFIED` | `[ ] APPROVED   Initials: _______` |
| Non-Binding Collaboration Term Sheet | `COMPLETE` | `QUALIFIED` | `[ ] APPROVED   Initials: _______` |
| DPDP Governance Assessment | `COMPLETE` | `QUALIFIED` | `[ ] APPROVED   Initials: _______` |
| Research Feasibility Protocol | `COMPLETE` | `REVIEWED` | `[ ] APPROVED   Initials: _______` |
| Bilingual Outreach Email Templates | `COMPLETE` | `REVIEWED` | `[ ] APPROVED   Initials: _______` |
| Defect & Risk Register (D1–D13) | `COMPLETE` | `REVIEWED` | `[ ] APPROVED   Initials: _______` |

---

## 4. Unbundled Executive Outreach Authorization Forms

Each institutional communication decision must be evaluated and authorized independently. All decisions are prepopulated as `PENDING`. No checkboxes may be pre-ticked.

```
+========================================================================================================================+
| DECISION 1: KVK MALYAL (MAHABUBABAD DISTRICT) INTRODUCTORY OUTREACH                                                    |
+--------------------------+---------------------------------------------------------------------------------------------+
| Parameter                | Verified Parameter Specification                                                            |
+--------------------------+---------------------------------------------------------------------------------------------+
| Recipient Institution    | Krishi Vigyan Kendra, Malyal (PJTSAU / ICAR)                                                |
| Verified Channel         | kvkwgl@pjtau.edu.in (Alternate: kvk.wgl@gmail.com | Phone: 8333818262)                     |
| Verified Addressee       | The Programme Coordinator (Dr. Banoth Dileep Kumar, Senior Scientist & Head / Entomologist) |
| Approved Version         | [  ] English Only      [  ] Telugu Only      [  ] Bilingual English/Telugu                  |
| Approved Attachments     | [  ] Collaboration Proposal (`KVK_MALYAL_COLLABORATION_PROPOSAL.md`)                        |
|                          | [  ] Term Sheet Summary (`ACREVIA_INSTITUTIONAL_COLLABORATION_TERM_SHEET.md`)               |
|                          | [  ] Feasibility Protocol (`30_DAY_SUPERVISED_FEASIBILITY_EVALUATION_PROTOCOL.md`)          |
| Permitted Scope          | Preliminary exploratory inquiry only; request for 20-min virtual or station briefing        |
| Owner Decision           | [  ] APPROVED          [  ] HOLD             [  ] REJECTED                                  |
| Date & Signature         | Date: ________________________   Signature: _______________________________________________ |
+--------------------------+---------------------------------------------------------------------------------------------+
```

```
+========================================================================================================================+
| DECISION 2: KVK KAMPASAGAR (NALGONDA DISTRICT) INTRODUCTORY OUTREACH                                                   |
+--------------------------+---------------------------------------------------------------------------------------------+
| Parameter                | Verified Parameter Specification                                                            |
+--------------------------+---------------------------------------------------------------------------------------------+
| Recipient Institution    | Krishi Vigyan Kendra, Kampasagar (PJTSAU / ICAR)                                            |
| Verified Channel         | kvkkampasagar@pjtau.edu.in (Alternate: kvkkampasagar2011@gmail.com | Phone: 8333818260)     |
| Verified Addressee       | The Programme Coordinator (Dr. Chandrashekar, Senior Scientist & Head / Agronomist)         |
| Approved Version         | [  ] English Only      [  ] Telugu Only      [  ] Bilingual English/Telugu                  |
| Approved Attachments     | [  ] Collaboration Proposal (`KVK_KAMPASAGAR_COLLABORATION_PROPOSAL.md`)                    |
|                          | [  ] Term Sheet Summary (`ACREVIA_INSTITUTIONAL_COLLABORATION_TERM_SHEET.md`)               |
|                          | [  ] Feasibility Protocol (`30_DAY_SUPERVISED_FEASIBILITY_EVALUATION_PROTOCOL.md`)          |
| Permitted Scope          | Preliminary exploratory inquiry only; request for 20-min virtual or station briefing        |
| Owner Decision           | [  ] APPROVED          [  ] HOLD             [  ] REJECTED                                  |
| Date & Signature         | Date: ________________________   Signature: _______________________________________________ |
+--------------------------+---------------------------------------------------------------------------------------------+
```

```
+========================================================================================================================+
| DECISION 3: PJTSAU DIRECTORATE OF EXTENSION (HYDERABAD) COURTESY NOTICE                                                |
+--------------------------+---------------------------------------------------------------------------------------------+
| Parameter                | Verified Parameter Specification                                                            |
+--------------------------+---------------------------------------------------------------------------------------------+
| Recipient Institution    | Directorate of Extension, Professor Jayashankar Telangana State Agricultural University     |
| Verified Channel         | de@pjtau.edu.in (Phone: 040-24015011 to 040-24015015)                                      |
| Verified Addressee       | To: The Office of the Director of Extension, PJTSAU                                         |
| Approved Version         | [  ] English Only      [  ] Telugu Only      [  ] Bilingual English/Telugu                  |
| Approved Attachments     | [  ] Executive Summary Brief of ACREVIA Research Initiative                                 |
| Permitted Scope          | Informational courtesy notification only; requesting administrative extension guidance      |
| Owner Decision           | [  ] APPROVED          [  ] HOLD             [  ] REJECTED                                  |
| Date & Signature         | Date: ________________________   Signature: _______________________________________________ |
+--------------------------+---------------------------------------------------------------------------------------------+
```

```
+========================================================================================================================+
| DECISION 4: ICAR — ATARI ZONE X (HYDERABAD) COURTESY NOTICE (OPTIONAL)                                                 |
+--------------------------+---------------------------------------------------------------------------------------------+
| Parameter                | Verified Parameter Specification                                                            |
+--------------------------+---------------------------------------------------------------------------------------------+
| Recipient Institution    | ICAR — Agricultural Technology Application Research Institute, Zone X, Hyderabad            |
| Verified Channel         | director.atari-hyd@icar.org.in (Alternate: atarihyderabad@yahoo.com | Phone: 040-24006500)   |
| Verified Addressee       | Dr. Shaik N. Meera, Director, ICAR-ATARI Zone X                                             |
| Approved Version         | [  ] English Only      [  ] Telugu Only      [  ] Bilingual English/Telugu                  |
| Approved Attachments     | [  ] Zonal Briefing Note on ACREVIA Academic Feasibility Study Proposals                    |
| Permitted Scope          | Informational zonal briefing only; requesting academic extension observations                |
| Strategic Context        | OPTIONAL — Direct operational authority for state KVKs resides with PJTSAU DoE             |
| Owner Decision           | [  ] APPROVED          [  ] HOLD             [  ] REJECTED                                  |
| Date & Signature         | Date: ________________________   Signature: _______________________________________________ |
+--------------------------+---------------------------------------------------------------------------------------------+
```

```
+========================================================================================================================+
| DECISION 5: TECHNICAL DEMONSTRATION & PROPOSAL SHARING AUTHORIZATION                                                   |
+--------------------------+---------------------------------------------------------------------------------------------+
| Parameter                | Verified Parameter Specification                                                            |
+--------------------------+---------------------------------------------------------------------------------------------+
| Sharing Scope            | Transmitting detailed proposal documents to KVK scientists upon introductory reply          |
| Meeting Scope            | Hosting a 20-minute virtual or on-station technical walkthrough of CropVision / KrishiBrain |
| Live Staging Deploy      | [  ] AUTHORIZE Vercel Preview staging deployment for demonstration URL                      |
|                          | [  ] HOLD staging deployment; use local screen share demonstration only                     |
| Owner Decision           | [  ] APPROVED          [  ] HOLD             [  ] REJECTED                                  |
| Date & Signature         | Date: ________________________   Signature: _______________________________________________ |
+--------------------------+---------------------------------------------------------------------------------------------+
```

---

## 5. Strictly Prohibited Operational Actions

Until formal written institutional partnership agreements are executed with participating KVKs and PJTSAU, the following activities remain **STRICTLY PROHIBITED**:

1. **NO Production Mutations:** No production database migrations, DDL executions, or configuration alterations.
2. **NO Premature Farmer Recruitment:** No recruiting farmers, surveying smallholders, or collecting farmer personal information (`FARMER_RECRUITMENT_STARTED = FALSE`).
3. **NO On-Farm Field Trials:** No deploying sensors, marking physical test plots, or conducting active agricultural interventions (`FIELD_PILOT_STATUS = NOT_AUTHORIZED`).
4. **NO Unapproved Third-Party Contact:** No contacting farmers, local agricultural extension officers, or input retailers without prior KVK coordination.
5. **NO Paid Service Activation:** No activating paid billing plans on Vercel, Neon, Groq, or Upstash.

---

## 6. Permitted Next Actions Following Owner Execution

```
1. Owner reviews this register and signs individual decisions (Decisions 1–5 above)
   ↓
2. If approved: Populate sender identity [Approved Sender Name] and transmit authorized emails
   ↓
3. Log communication timestamps and delivery receipts in institutional audit trail
   ↓
4. Await formal response from institutional leadership
   ↓
5. Conduct 20-minute technical demonstration under scientist supervision
   ↓
6. Negotiate formal non-binding Collaborative Research MoU
```
