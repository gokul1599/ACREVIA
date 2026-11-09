# ACREVIA — PHASE 02 CORRECTIVE DOSSIER FINALIZATION & OWNER AUTHORIZATION REPORT
## COMPREHENSIVE INSTITUTIONAL DUE DILIGENCE, RESEARCH GOVERNANCE, DPDP REASSESSMENT & EXECUTIVE AUTHORIZATION DOSSIER

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Target Institutions:**
1. Krishi Vigyan Kendra (KVK), Malyal — Mahabubabad District
2. Krishi Vigyan Kendra (KVK), Kampasagar — Nalgonda District
3. Professor Jayashankar Telangana State Agricultural University (PJTSAU) — Directorate of Extension
4. ICAR — Agricultural Technology Application Research Institute (ATARI), Zone X, Hyderabad  
**Audited Commit Baseline:** `c329b67`  
**Report Date:** November 9, 2026  
**Document Code:** `PHASE_02_CORRECTIVE_DOSSIER_FINALIZATION_REPORT.md`  
**Execution Standard:** Evidence Before Claims • Verified Identity Before Correspondence • Legal Review Before Compliance Claims • Scientific Integrity Before Research Commitments • Consent Before Personal Data Collection • Owner Authorization Before External Action • Institutional Approval Before Field Activities  

---

## 1. Executive Summary

This final report consolidates the complete corrective institutional due diligence, contact verification, research governance, DPDP data protection reassessment, and owner outreach pre-authorization framework for Phase 02 of the ACREVIA agricultural intelligence initiative.

### Core Audit Outcomes:
1. **Repository Integrity & Verification:** The repository baseline is confirmed at commit `c329b67` on branch `main` with a clean working tree. The true physical test suite stands verified at **252 physical tests (145 backend + 55 ML + 9 vision + 43 frontend, 100% pass rate)**, with zero TypeScript compiler errors.
2. **Four-Institution Grounding:** Institutional identities, physical campuses, agro-ecological mandates, scientific leadership, and official communication channels for all four institutions (KVK Malyal, KVK Kampasagar, PJTSAU Directorate of Extension, and ICAR-ATARI Zone X) have been verified against primary university and government records.
3. **Discrepancy Resolution:** Prior discrepancies in leadership names, spellings, and administrative designations were systematically resolved:
   - KVK Malyal: Confirmed **Dr. Banoth Dileep Kumar** (Entomology); third-party OCR typo `A Dileep Kumar` debunked. Active official inbox: `kvkwgl@pjtau.edu.in`.
   - KVK Kampasagar: Confirmed **Dr. Chandrashekar** (Agronomy); disambiguated from `Dr. K. Chandrasekhar` at KVK Suryapet. Active official inbox: `kvkkampasagar@pjtau.edu.in`.
   - PJTSAU Directorate of Extension: Addressed generically to `The Office of the Director of Extension` (`de@pjtau.edu.in`) to accommodate administrative leadership rotations between senior faculty (`Dr. Ch. Venu Gopal Reddy` and `Dr. M. Yakadri`).
   - ICAR-ATARI Zone X: Fully profiled under Director **Dr. Shaik N. Meera** (`director.atari-hyd@icar.org.in`). Evaluated Option A (KVK-first via PJTSAU) vs Option B (concurrent zonal outreach); Option A recommended as primary.
4. **Research Governance Alignment:** Replaced open-ended research claims with a rigorous **30-Day Supervised Feasibility Evaluation Protocol** (`30_DAY_SUPERVISED_FEASIBILITY_EVALUATION_PROTOCOL.md`) and a formal non-binding Collaboration Term Sheet (`ACREVIA_INSTITUTIONAL_COLLABORATION_TERM_SHEET.md`). Feasibility metrics are cleanly separated from long-term crop yields, authorship is contribution-based under ICMJE guidelines, and individual participant withdrawal is cleanly disentangled from institutional MoU termination.
5. **DPDP Act 2023 Posture:** Fully assessed under the Digital Personal Data Protection Act, 2023. Compliance claims are legally qualified (`DPDP_COMPLIANCE_CERTIFICATION = NOT_CLAIMED`). A master data lifecycle and third-party processor matrix is established, zero government IDs or land revenue titles are collected, and an operational 48-hour deletion pathway is documented.
6. **Bilingual Outreach Collateral:** Complete, professionally translated English and formal Telugu correspondence drafts are prepared for all four institutions (`KVK_OUTREACH_EMAIL_DRAFTS.md`), with sender placeholders and mandatory `INTERNAL DRAFT — DO NOT SEND WITHOUT OWNER APPROVAL` banners.
7. **Strict Operational Boundary:** **No external communication has been transmitted.** All owner decision checkboxes are prepopulated as `PENDING`. **`FIELD_PILOT_STATUS = NOT_AUTHORIZED`** remains strictly enforced.

---

## 2. Repository Reconciliation

The complete repository and test inventory was re-audited and reconciled against physical disk artifacts:

| Item | Previous Report Claim | Actual Physical Status | Verifiable Evidence |
|---|---|---|---|
| **Git Lineage** | Commit `c329b67` | Verified at HEAD `c329b67` | Branch `main`, clean working tree |
| **Backend Tests** | 145 tests | 145 tests passing | `backend/tests/` (includes 9 staging acceptance tests) in 356.09s |
| **ML Models Tests** | 55 tests | 55 tests passing | `tests/ml/test_crop_vision.py` & `test_krishi_brain.py` in 21.05s |
| **Vision API Tests** | 9 tests | 9 tests passing | `tests/api/test_vision_endpoints.py` in 18.12s |
| **Frontend Tests** | 43 tests | 43 tests passing | Vitest in `frontend/` (offline queue, PWA, sync, i18n parity) in 1.19s |
| **TypeScript Static Check** | 0 errors | 0 errors | `cd frontend; npx tsc --noEmit` executed with 0 errors |
| **Total Test Inventory** | Misstated as 240 in older docs | **252 physical tests** | 145 + 55 + 9 + 43 = 252 physical automated tests (100% pass rate) |
| **Staging Infrastructure** | Configured for Vercel Preview | Architecture verified; deploy held | `frontend/vercel.json` (`sin1`), `.env.staging.example`, isolated headers |
| **Application Tenancy** | Multi-tenant isolation | App-layer isolation verified | `verify_farm_access()` returns HTTP 403 on cross-tenant access |
| **Satellite Pipeline** | Anonymous STAC | Earth Search $\rightarrow$ Planetary Computer | STAC API search and COG windowing intact; no Copernicus credentials |
| **Redis Cache / Limit** | Upstash Redis | Isolated staging prefix `acrevia_staging:*` | Fail-open on outage; memory fallback verified |
| **Financial Restrictions** | Zero-cost operation | Code enforces free quotas | Hard HTTP 429 on quota exhaustion; no paid fallbacks |

---

## 3. Four-Institution Due Diligence

### 3.1 Krishi Vigyan Kendra, Malyal (Mahabubabad District)
- **Official Institutional Entity:** Krishi Vigyan Kendra, Malyal.
- **Administrative Location:** Malyal Village & Farm, Mahabubabad Mandal, Mahabubabad District, Telangana – 506 101.
- **Establishment History:** Established in 1989 on the historic Malyal agricultural farm. Originally under erstwhile undivided Warangal district; updated to Mahabubabad district jurisdiction following state administrative reorganization in 2016.
- **Host University & Funding:** PJTSAU (host university) / ICAR ATARI Zone X (100% plan funding).
- **Scientific Leadership:** **Dr. Banoth Dileep Kumar** (Dr. B. Dileep Kumar), Senior Scientist & Head / Programme Coordinator (Department of Entomology).
- **Official Contact Channels:**
  - Official Institutional Email: `kvkwgl@pjtau.edu.in` (`CURRENT_OFFICIAL_CONTACT`)
  - Secondary Operational Email: `kvk.wgl@gmail.com` (`CURRENT_OFFICIAL_ALTERNATE`)
  - Personal University Email: `dileep_kumar453@pjtau.edu.in` (`CURRENT_OFFICIAL_ALTERNATE`)
  - Official Landline: `08719-240182` (`CURRENT_OFFICIAL_CONTACT`)
  - Published Mobile Numbers: `8333818262` / `9849988231` (`CURRENT_OFFICIAL_CONTACT`)
- **Agro-Ecological Mandate:** Central Telangana Zone. Major crops: Cotton (*Gossypium hirsutum*), Chilli (*Capsicum annuum*), Maize, and Pulses. Key agronomic focus: Pink Bollworm (*Pectinophora gossypiella*), Chilli Black Thrips (*Thrips parvispinus*), fungal wilt complexes, and integrated pest management (IPM).

### 3.2 Krishi Vigyan Kendra, Kampasagar (Nalgonda District)
- **Official Institutional Entity:** Krishi Vigyan Kendra, Kampasagar.
- **Administrative Location:** Co-located within the Agricultural Research Station (ARS) Campus, Babusaipet (Post), Tripuraram Mandal, Nalgonda District, Telangana – 508 207.
- **Host University & Funding:** PJTSAU / ICAR ATARI Zone X.
- **Scientific Leadership:** **Dr. Chandrashekar**, Senior Scientist & Head / Programme Coordinator (Department of Agronomy / Crop Production).
- **Official Contact Channels:**
  - Official Institutional Email: `kvkkampasagar@pjtau.edu.in` (`CURRENT_OFFICIAL_CONTACT`)
  - Secondary Operational Email: `kvkkampasagar2011@gmail.com` (`CURRENT_OFFICIAL_ALTERNATE`)
  - Published Mobile / Office Phone: `8333818260` (`CURRENT_OFFICIAL_CONTACT`)
- **Agro-Ecological Mandate:** Southern Telangana Zone. Major crops: Rice (*Oryza sativa*) and Cotton (*Gossypium hirsutum*) in the Nagarjuna Sagar Project (NSP) Left Canal command network. Key agronomic focus: Alternate Wetting and Drying (AWD) water management, direct-seeded rice (DSR), Rice Blast (*Magnaporthe oryzae*), and Brown Planthopper (*Nilaparvata lugens*).

### 3.3 Professor Jayashankar Telangana State Agricultural University (PJTSAU) — Directorate of Extension
- **Official Entity:** Directorate of Extension, PJTSAU.
- **Administrative Campus:** Administrative Building, PJTSAU Campus, Rajendranagar, Hyderabad, Telangana – 500 030.
- **Administrative Function:** Exercises statewide administrative, operational, and scientific oversight over all university-administered KVKs and DAATTCs across Telangana.
- **Official Contact Channels:**
  - Directorate Statutory Email: `de@pjtau.edu.in` (`CURRENT_OFFICIAL_CONTACT`)
  - University PBX Range: `040-24015011` to `040-24015015` (`CURRENT_OFFICIAL_CONTACT`)
- **Protocol Addressing Rule:** Due to rotating administrative appointments between senior professors (`Dr. Ch. Venu Gopal Reddy` and `Dr. M. Yakadri`), correspondence must be addressed generically to:  
  `To: The Office of the Director of Extension, PJTSAU`.

### 3.4 ICAR — Agricultural Technology Application Research Institute (ATARI), Zone X
- **Official Entity:** ICAR — Agricultural Technology Application Research Institute, Zone X, Hyderabad.
- **Campus Address:** CRIDA Campus, Santoshnagar, Hyderabad, Telangana – 500 059.
- **Jurisdiction:** Telangana, Andhra Pradesh, Tamil Nadu, and Puducherry.
- **Leadership:** **Dr. Shaik N. Meera**, Director, ICAR-ATARI Zone X.
- **Official Contact Channels:**
  - Director Inbox: `director.atari-hyd@icar.org.in` (`CURRENT_OFFICIAL_CONTACT`)
  - Alternate Email: `atarihyderabad@yahoo.com` (`CURRENT_OFFICIAL_ALTERNATE`)
  - Official Telephone: `040-24006500` / `040-24536648` (`CURRENT_OFFICIAL_CONTACT`)
- **Role Evaluation & Strategy Recommendation:**
  - ATARI coordinates ICAR plan budgets, institutional monitoring, and zonal technology application across Zone X. However, direct operational jurisdiction, scientist deployment, and on-farm approvals for state KVKs reside with the PJTSAU Directorate of Extension.
  - **Option A (Recommended — Focused KVK-First Engagement):** Direct initial exploratory outreach solely to KVK Malyal, KVK Kampasagar, and PJTSAU Directorate of Extension.
  - **Option B (Concurrent Courtesy Outreach):** Transmit an informational courtesy note to ATARI Zone X simultaneously.
  - **Decision:** Option A is primary. ATARI outreach is retained as an optional unbundled draft requiring explicit owner authorization.

---

## 4. Institutional Discrepancy Register

| Entity / Parameter | Previous Claim in Early Drafts | Current Authoritative Official Evidence | Discrepancy Resolution | Remaining Uncertainty | Document Updates Made |
|---|---|---|---|---|---|
| **KVK Malyal Coordinator** | `A Dileep Kumar` / `Dr. B. Dileep Kumar` | PJTSAU faculty directory confirms **Dr. Banoth Dileep Kumar**, Senior Scientist & Head (Entomology). | Typo `A Dileep Kumar` traced to OCR error from third-party aggregator. Confirmed as **Dr. Banoth Dileep Kumar**. | None | Updated in `INSTITUTIONAL_DUE_DILIGENCE_REPORT.md`, `INSTITUTIONAL_CONTACT_VERIFICATION_REGISTER.md`, and drafts. |
| **KVK Malyal Email Prefix** | Claimed invalid because of `wgl` prefix | PJTSAU domain records confirm `kvkwgl@pjtau.edu.in` is active official inbox. | Preserves historical Warangal district code from 1989, but remains active institutional inbox. | None | Verified and classified as `CURRENT_OFFICIAL_CONTACT`. |
| **KVK Kampasagar Coordinator** | `Dr. K. Chandrashaker` vs `Dr. Chandrashekar` | PJTSAU staff directory lists **Dr. Chandrashekar** (Agronomy) at Kampasagar. `Dr. K. Chandrasekhar` is at KVK Suryapet. | Disambiguated between two separate PJTSAU scientists. Confirmed **Dr. Chandrashekar** at Kampasagar. | None | Corrected across all proposals and email templates. |
| **PJTSAU Director of Extension** | `Dr. Ch. Venu Gopal Reddy` vs `Dr. M. Yakadri` | University leadership directories show concurrent/transitioning portfolio assignments. | Correspondence protocol revised to address generically to `The Office of the Director of Extension, PJTSAU`. | Specific current officeholder | Generic addressing rule strictly enforced in all correspondence. |
| **ATARI Zone X Inclusion** | Omitted in Stage 01–10; added without strategic justification | ICAR website and CRIDA campus directories confirm ATARI Zone X under Dr. Shaik N. Meera. | Formally evaluated Option A (KVK-first) vs Option B (concurrent courtesy). Structured as optional decision. | None | Documented in due diligence and authorization register. |

---

## 5. Agricultural Scientific Claim Review

1. **Focal Cropping Systems & Pathological Scope:**
   - **Cotton (*Gossypium hirsutum*):** Focused on Pink Bollworm (*Pectinophora gossypiella*) larval infestation and sucking pest complexes. Platform scope strictly limited to foliar and square/boll surface symptoms.
   - **Chilli (*Capsicum annuum*):** Focused on Chilli Black Thrips (*Thrips parvispinus*) foliar curling and fungal wilt complexes. Claims of local infestation intensity are strictly framed as regional research context, not unverified local field observations.
   - **Rice (*Oryza sativa*):** Focused on Neck and Leaf Blast (*Magnaporthe oryzae*), Sheath Blight (*Rhizoctonia solani*), and Brown Planthopper (*Nilaparvata lugens*).
   - **Water Management (AWD):** Formulated strictly as an exploratory decision-support research hypothesis comparing satellite NDWI/NDVI and weather evapotranspiration against canal schedules. All claims of guaranteed water savings have been removed.
2. **Separation of Evidence Categories:**
   - Published University Findings (PJTSAU *Vyavasaya Panchangam*, ICAR guides) are strictly separated from platform experimental hypotheses.
   - Probabilistic machine-learning classifications are explicitly labeled as computer vision estimates, never as certified laboratory pathology.
3. **CropVision Inference Safeguards:**
   - On-device classification models run with calibrated confidence thresholds ($>0.70$).
   - Grad-CAM saliency heatmaps provide spatial explainability for foliar lesion localization.
   - Low-confidence or out-of-domain images trigger an automated abstention and request clear re-capture or expert review.
4. **KrishiBrain & Chemical Safety (CIBRC Governance):**
   - Grounded RAG indexes PJTSAU and ICAR approved packages of practices with page-level citations.
   - Strict automated safety filters prevent recommending banned, restricted, or off-label pesticides under Central Insecticides Board & Registration Committee (CIBRC) regulations.
   - Highly hazardous chemicals (WHO Class Ia/Ib) trigger mandatory abstention and immediate escalation to human scientists.

---

## 6. Collaboration Term Sheet Review

The non-binding collaboration term sheet (`ACREVIA_INSTITUTIONAL_COLLABORATION_TERM_SHEET.md`) establishes a legally grounded, non-commercial framework:

```
+========================================================================================================================+
| ACREVIA NON-BINDING COLLABORATION TERM SHEET SUMMARY                                                                   |
+----+-------------------------------+-----------------------------------------------------------------------------------+
| #  | Covenant Dimension            | Negotiated Principle & Legal Boundary                                             |
+----+-------------------------------+-----------------------------------------------------------------------------------+
| 01 | Academic Positioning          | Non-commercial, non-exclusive research collaboration; zero vendor agency.        |
| 02 | Transparent Cost Allocation   | Free-tier cloud infrastructure. Zero fees billed to KVKs or farmers.              |
| 03 | Provisional Cohort & Scope    | 20–30 farmers in 1 village cluster per KVK for a 30-day feasibility evaluation.   |
| 04 | Human-in-the-Loop Oversight   | KVK scientists review and calibrate all AI outputs via ExpertConnect.             |
| 05 | Data Sovereignty & Rights     | Farmers retain full data ownership. 10-class rights matrix defined.               |
| 06 | Qualified 48-Hour Deletion    | Active PostgreSQL and Redis deletion in 48h; backup archives aged out under policy.|
| 07 | Academic Authorship           | Contribution-based co-authorship governed by standard ICMJE academic criteria.    |
| 08 | Feasible Evaluation Design    | Replaced double-blind claims with feasible blinded image review by scientist panel.|
| 09 | Withdrawal vs Termination     | Immediate voluntary farmer withdrawal vs 30 days written notice for MoU exit.     |
| 10 | Legal Disclaimer              | Research decision-support tool; no liability for agricultural yield outcomes.     |
+----+-------------------------------+-----------------------------------------------------------------------------------+
```

---

## 7. DPDP Act, 2023 and Data Governance Reassessment

The comprehensive data protection assessment (`DPDP_GOVERNANCE_AND_DATA_LIFECYCLE_ASSESSMENT.md`) documents:

1. **Statutory Status:** The Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023) received Presidential assent on August 11, 2023. As of November 9, 2026, central implementing rules and Data Protection Board operational procedures remain in active regulatory formulation.
2. **Compliance Labeling:** Compliance claims are qualified as **`DPDP_COMPLIANCE_CERTIFICATION = NOT_CLAIMED`**. The platform enforces DPDP principles by design, but makes no unauthorized claim of statutory certification.
3. **Data Minimization:**
   - **Zero Prohibited Data:** No national identity credentials (Aadhaar, PAN), land ownership titles (Pahani/1-B passbooks), or banking details are collected or stored.
   - **Collected Data:** Limited strictly to mobile phone number (OTP login), first name/alias, village name, parcel boundary polygon, crop type, and crop leaf photos.
4. **Third-Party Data Processor Boundaries:**
   - Supabase / Neon: Encrypted database storage (`eu-central-1` / `ap-southeast-1`), application-layer tenant isolation.
   - Upstash Redis: In-memory rate limiting with isolated `acrevia_staging:*` namespace.
   - GroqCloud: Ephemeral AI inference (`qwen/qwen3.8-27b`), zero-retention API mode, no personal farmer data transmitted in prompt payloads.
   - Element 84 Earth Search: Anonymous STAC query by parcel bounding box; zero user tokens transmitted.
   - Open-Meteo: Anonymous weather query by latitude/longitude coordinate; zero user tokens transmitted.
5. **Farmer Consent & Language Rights:** Trilingual consent documentation (Telugu, English, Hindi) guaranteeing voluntary enrollment, informed participation, and unconditional right to withdraw.

---

## 8. Research Protocol Assessment

The field evaluation methodology (`30_DAY_SUPERVISED_FEASIBILITY_EVALUATION_PROTOCOL.md`) defines a structured, scientifically defensible evaluation:

1. **Protocol Title:** 30-Day Supervised Agricultural Technology Feasibility and Workflow Evaluation.
2. **Metric Separation:**
   - *Technical Feasibility Metrics:* Mobile app crash rate ($<1\%$), offline observation sync success rate ($>98\%$), image upload and inference latency ($<3.5\text{ s}$).
   - *Diagnostic Evaluation Metrics:* Cohen's Kappa ($\kappa$) concordance between CropVision predictions and ground-truth scientist diagnoses; percentage of diagnostic abstentions on ambiguous symptoms; Grad-CAM clinical utility rating by scientists.
   - *Agricultural Outcome Metrics:* Exploratory observation of water-scheduling adherence under AWD; farmer self-reported confidence. **Explicitly acknowledges that a 30-day study cannot establish statistical yield differences.**
3. **Expert Adjudication & Safety Suspension:**
   - If a CropVision diagnosis conflicts with a scientist evaluation, the scientist's judgment is authoritative.
   - If an unexpected phytotoxicity event or disease outbreak occurs, the protocol enforces immediate suspension of automated advisories and transitions to manual KVK extension advisories.

---

## 9. Outreach Package

The outreach package (`KVK_OUTREACH_EMAIL_DRAFTS.md`) contains four complete correspondence drafts:

| Recipient Institution | Addressee | Official Verified Channel | Language Versions | Attachments Prepared |
|---|---|---|---|---|
| **KVK Malyal** | Dr. Banoth Dileep Kumar, Sr. Scientist & Head | `kvkwgl@pjtau.edu.in` | Complete English & formal Telugu | Proposal, Term Sheet, Protocol |
| **KVK Kampasagar** | Dr. Chandrashekar, Sr. Scientist & Head | `kvkkampasagar@pjtau.edu.in` | Complete English & formal Telugu | Proposal, Term Sheet, Protocol |
| **PJTSAU Extension** | The Office of the Director of Extension | `de@pjtau.edu.in` | Complete English & formal Telugu | Executive Summary Brief |
| **ICAR-ATARI Zone X** | Dr. Shaik N. Meera, Director | `director.atari-hyd@icar.org.in` | Complete English & formal Telugu | Zonal Briefing Note |

- **Sender Safeguards:** All sender details are maintained as unpopulated placeholders (`[Approved Sender Name]`, `[Approved Position / Organisation]`).
- **Internal Protection:** Every draft carries the prominent warning banner:  
  `> [!CAUTION] INTERNAL DRAFT — DO NOT SEND WITHOUT OWNER APPROVAL`.

---

## 10. Risk Register

| ID | Severity | Finding | Root Cause / Impact | Mitigation Strategy | Current Status |
|---|---|---|---|---|---|
| **D1** | P1 | Live Vercel staging deployment absent | Deployment held pending owner sign-off. | Complete staging build verified locally; ready for Vercel Preview. | `MITIGATED_PENDING_DEPLOY` |
| **D2** | P2 | PostgreSQL engine RLS absent | Relies on app-layer tenant filtering. | `verify_farm_access()` tested via HTTP 403 suites; DB RLS scheduled. | `DOCUMENTED_LIMITATION` |
| **D3** | P2 | Redis rate limiter fail-open policy | Fail-open prevents legitimate farmer disruption. | In-memory fallback verified; `fail_closed` scheduled for login endpoint. | `ACCEPTED_PILOT_RISK` |
| **D4** | P2 | Groq preview model dependency | `qwen/qwen3.8-27b` preview status. | Deterministic extractive RAG fallback operates when Groq unavailable. | `MITIGATED_FALLBACK` |
| **D5** | P3 | Test-accounting discrepancy | Inconsistent test totals in older docs. | Reconciled across repository to true physical total of 252 tests. | `RESOLVED_RECONCILED` |
| **D6** | P4 | Frontend lint script configuration | `next lint` fails due to uninstalled ESLint. | Build and TypeScript compilation pass with 0 errors; non-blocking. | `DEFERRED_NON_BLOCKING` |
| **D7** | P2 | Institutional identity discrepancies | Typo in Malyal; Kampasagar confusion. | Primary source university directories resolved all identities. | `RESOLVED_VERIFIED` |
| **D8** | P2 | DPDP legal assessment not certified | Potential misrepresentation of compliance. | Qualified as non-certified technical audit; formal review required. | `QUALIFIED_ACKNOWLEDGED` |
| **D9** | P2 | Operational 48-hr deletion claim | Unqualified deletion promises. | Qualified to active database tables; backup tape lifecycle documented. | `QUALIFIED_RESOLVED` |
| **D10** | P2 | Unqualified zero-cost commitment | Scaling costs could become liability. | Replaced with transparent cost allocation model and free-tier boundaries. | `QUALIFIED_RESOLVED` |
| **D11** | P2 | Unqualified joint-authorship terms | Academic integrity concerns. | Replaced with ICMJE contribution-based scientific authorship terms. | `QUALIFIED_RESOLVED` |
| **D12** | P2 | Double-blind methodology overstatement | Infeasible in open agricultural extension. | Replaced with feasible blinded image review by expert panel. | `QUALIFIED_RESOLVED` |
| **D13** | P2 | Withdrawal vs MoU termination confusion | Mixed individual rights with institutional pact. | Separated immediate participant exit from 30-day institutional notice. | `QUALIFIED_RESOLVED` |

---

## 11. Readiness Decision

### Readiness Classification:
# **`READY_FOR_OWNER_REVIEW`**

**Rationale:**  
All technical, geospatial, security, legal, and institutional requirements for Phase 02 preparation have been completed with rigorous physical evidence. The test harness stands at 252 passing tests, institutional contacts are grounded in primary university records, correspondence drafts are prepared in bilingual English and Telugu, data governance is properly qualified, and unbundled decision forms are established for the project owner. The dossier is fully prepared for owner evaluation.

---

## 12. Outreach Authorization Status

### Outreach Authorization Classification:
# **`GO_FOR_OUTREACH_PENDING_OWNER_APPROVAL`**

**Rationale:**  
All outreach collateral, contact channels, and institutional proposals are verified and ready for deployment. However, in accordance with the project's foundational governance principle (**Authorization Before External Action**), **no emails may be transmitted until the project owner explicitly signs the authorization register**. Outreach status is strictly gated pending owner sign-off.

---

## 13. Owner Decision Checklist

The project owner must evaluate the following independent, unbundled decisions in `PHASE_02_INSTITUTIONAL_OUTREACH_AUTHORIZATION_REGISTER.md`:

```
[  ] Decision 1: Authorize KVK Malyal introductory inquiry email (kvkwgl@pjtau.edu.in)
[  ] Decision 2: Authorize KVK Kampasagar introductory inquiry email (kvkkampasagar@pjtau.edu.in)
[  ] Decision 3: Authorize PJTSAU Directorate courtesy notice email (de@pjtau.edu.in)
[  ] Decision 4: Authorize ICAR-ATARI Zone X optional courtesy notice email (director.atari-hyd@icar.org.in)
[  ] Decision 5: Authorize sharing detailed collaboration proposals upon institutional reply
[  ] Decision 6: Authorize scheduling 20-minute virtual or on-station technical demonstrations
[  ] Decision 7: Authorize Vercel Preview staging deployment for live demonstration URL
```

*Current Status: All decisions are prepopulated as `PENDING`. No checkboxes have been pre-ticked.*

---

## 14. Field-Pilot Status

### Mandatory Operational Directive:
# **`FIELD_PILOT_STATUS = NOT_AUTHORIZED`**

**Operational Boundary:**  
Under no circumstances does this report or the pre-authorization dossier authorize on-ground agricultural field trials, farmer recruitment, collection of farmer personal data, or physical farm interventions. Field activities remain strictly prohibited until:
1. Formal non-binding Memoranda of Understanding (MoU) are executed with participating KVKs and PJTSAU.
2. Institutional ethics committee clearance is obtained.
3. Voluntary, informed, bilingual farmer consent forms are physically executed.

---

## 15. Final Handover

### 15.1 Modified & Newly Authored Deliverables:
1. `docs/pilot/kvk/INSTITUTIONAL_CONTACT_VERIFICATION_REGISTER.md` — Authoritative four-institution contact directory with evidence sources.
2. `docs/pilot/kvk/INSTITUTIONAL_DUE_DILIGENCE_REPORT.md` — Comprehensive due diligence report with discrepancy resolutions.
3. `docs/pilot/kvk/ACREVIA_INSTITUTIONAL_COLLABORATION_TERM_SHEET.md` — Legally grounded 12-section non-commercial research term sheet.
4. `docs/pilot/governance/DPDP_GOVERNANCE_AND_DATA_LIFECYCLE_ASSESSMENT.md` — Detailed DPDP Act 2023 evaluation and data lifecycle mapping.
5. `docs/pilot/research/30_DAY_SUPERVISED_FEASIBILITY_EVALUATION_PROTOCOL.md` — 30-day feasibility evaluation protocol with metric separation.
6. `docs/pilot/kvk/KVK_OUTREACH_EMAIL_DRAFTS.md` — Complete bilingual (English/Telugu) correspondence drafts for all four institutions.
7. `docs/pilot/PHASE_02_OUTREACH_PRE_AUTHORIZATION_DOSSIER.md` — Consolidated pre-authorization dossier with risk register and governance terms.
8. `docs/pilot/PHASE_02_INSTITUTIONAL_OUTREACH_AUTHORIZATION_REGISTER.md` — Redesigned unbundled owner authorization register with prepopulated `PENDING` states.
9. `docs/pilot/PHASE_02_CORRECTIVE_DOSSIER_FINALIZATION_REPORT.md` — Master final handover report covering all 15 audit dimensions.

### 15.2 Unresolved Dependencies:
- **Owner Sign-Off:** Execution of the unbundled decisions in `PHASE_02_INSTITUTIONAL_OUTREACH_AUTHORIZATION_REGISTER.md`.
- **Sender Identity:** Insertion of verified sender credentials (`[Approved Sender Name]`, `[Verified Sender Email]`) by the project owner upon approval.
- **Staging Deployment:** Optional trigger of Vercel Preview live staging deployment if live URL is desired for demonstration.

### 15.3 Next Permissible Action:
**STOP AND AWAIT OWNER INSTRUCTION.**  
Present this report to the project owner for formal review and unbundled outreach authorization. No automated actions or external transmissions may occur.
