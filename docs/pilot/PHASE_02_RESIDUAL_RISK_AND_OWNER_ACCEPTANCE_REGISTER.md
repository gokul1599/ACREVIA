# ACREVIA — PHASE 02 RESIDUAL RISK & OWNER ACCEPTANCE REGISTER
## UNVARNISHED TECHNICAL, SECURITY, LEGAL & OPERATIONAL RISK AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Document Code:** `PHASE_02_RESIDUAL_RISK_AND_OWNER_ACCEPTANCE_REGISTER.md`  
**Audited Baseline Commit:** `41b36f3`  
**Date of Audit Review:** November 9, 2026  
**Risk Governance Standard:** Truthful Classification • Evidence Before Claims • No Premature Mitigation Claims  

---

## 1. Executive Risk Governance Standard

In strict adherence to the project's engineering and governance standards:
- **A risk is not mitigated merely because it is documented.**
- **A local test pass is not proof of cloud deployment health.**
- **Application-layer access control is not database-level row-level security.**
- **Service availability during a cache outage is not proof of rate-limiting security.**
- **No owner risk acceptance may be inferred without explicit attributable documentation.**

---

## 2. Master Residual Risk Register (D1–D13)

```
+==================================================================================================================================================+
| MASTER RESIDUAL RISK AUDIT MATRIX                                                                                                                |
+----+----+-------------------------------------+---------------------------------------------------------------+----------------------------------+
| ID |Sev | Finding Description                 | Accurate Technical Analysis & Residual Exposure               | Formal Risk Status Code          |
+----+----+-------------------------------------+---------------------------------------------------------------+----------------------------------+
| D1 | P1 | Live Vercel staging deploy absent   | Local Next.js build passes, vercel.json (sin1) configured.    | OPEN — LIVE_DEPLOYMENT_PENDING_  |
|    |    |                                     | However, no live cloud deployment exists; cloud network, SSL, | OWNER_APPROVAL                   |
|    |    |                                     | and edge environment variables remain physically unverified.   |                                  |
+----+----+-------------------------------------+---------------------------------------------------------------+----------------------------------+
| D2 | P2 | PostgreSQL engine RLS absent        | Application layer enforces verify_farm_access() (HTTP 403 on  | DOCUMENTED_RESIDUAL_DATABASE_    |
|    |    |                                     | cross-tenant read verified in test suite). However, database  | SECURITY_LIMITATION              |
|    |    |                                     | engine-level Row-Level Security policies are NOT implemented. |                                  |
|    |    |                                     | Direct database access bypasses tenant boundary protections.  |                                  |
+----+----+-------------------------------------+---------------------------------------------------------------+----------------------------------+
| D3 | P2 | Redis rate-limiter fail-open mode   | In-memory fallback prevents legitimate smallholder disruption | DOCUMENTED_RESIDUAL_SECURITY_    |
|    |    |                                     | during Redis outages. However, distributed rate limits are no | RISK — OWNER RISK ACCEPTANCE NOT |
|    |    |                                     | longer enforced across multi-instance edge nodes. Sensitive   | RECORDED                         |
|    |    |                                     | authentication and expensive AI routes risk unthrottled load. |                                  |
+----+----+-------------------------------------+---------------------------------------------------------------+----------------------------------+
| D4 | P2 | Groq preview model dependency       | Model qwen/qwen3.8-27b is a preview release subject to sudden | DOCUMENTED_AI_AVAILABILITY_RISK —|
|    |    |                                     | deprecation or provider rate limits. Mitigated by extractive  | GROQ_ACCOUNT_BILLING_STATUS_NOT_ |
|    |    |                                     | deterministic RAG fallback. Account billing status unverifiable| VERIFIABLE                       |
+----+----+-------------------------------------+---------------------------------------------------------------+----------------------------------+
| D5 | P3 | Previous test-accounting discrepancy| Earlier documents cited 240 tests due to double-counting.     | RESOLVED_RECONCILED              |
|    |    |                                     | Reconciled to exact physical count: 252 physical tests        |                                  |
|    |    |                                     | (145 be + 55 ml + 9 vis + 43 fe, 100% pass rate).             |                                  |
+----+----+-------------------------------------+---------------------------------------------------------------+----------------------------------+
| D6 | P4 | Frontend lint script configuration  | `next lint` fails because eslint and eslint-config-next are   | OPEN_DEFERRED — TOOLING_DEFECT   |
|    |    |                                     | not installed in devDependencies. Build & TS pass cleanly.    |                                  |
+----+----+-------------------------------------+---------------------------------------------------------------+----------------------------------+
| D7 | P2 | Institutional identity discrepancies| Early drafts had typos ('A Dileep Kumar', Suryapet confusion).| RESOLVED_VERIFIED_PRIMARY_SOURCE |
|    |    |                                     | Resolved via official university directories (pjtau.edu.in).  |                                  |
+----+----+-------------------------------------+---------------------------------------------------------------+----------------------------------+
| D8 | P2 | DPDP legal assessment not certified | Platform enforces DPDP data protection principles by design.  | QUALIFIED_STATUS — DPDP_         |
|    |    |                                     | However, no formal legal certification has been obtained.     | COMPLIANCE_CERTIFICATION_NOT_    |
|    |    |                                     | Formal legal counsel review remains pending.                  | CLAIMED                          |
+----+----+-------------------------------------+---------------------------------------------------------------+----------------------------------+
| D9 | P2 | Operational 48-hr deletion claim    | Active PostgreSQL tables and Redis cache purge records within | QUALIFIED_OPERATIONAL_DELETION_  |
|    |    |                                     | 48h. However, immutable automated database backup snapshots  | PATH                             |
|    |    |                                     | cannot be selectively edited and age out over 30-day cycle.   |                                  |
+----+----+-------------------------------------+---------------------------------------------------------------+----------------------------------+
| D10| P2 | Unqualified zero-cost commitment    | Platform operates within free-tier quotas; project absorbs    | QUALIFIED_NO_FEE_PARTICIPATION_  |
|    |    |                                     | all compute. Zero fees billed to KVKs. However, permanent     | MODEL                            |
|    |    |                                     | zero-cost scaling cannot be promised unconditionally.         |                                  |
+----+----+-------------------------------------+---------------------------------------------------------------+----------------------------------+
| D11| P2 | Unqualified joint-authorship terms  | Early drafts promised co-authorship. Corrected to adhere to   | QUALIFIED_ICMJE_CONTRIBUTION_    |
|    |    |                                     | standard ICMJE academic contribution criteria.                | BASED_AUTHORSHIP                 |
+----+----+-------------------------------------+---------------------------------------------------------------+----------------------------------+
| D12| P2 | Double-blind methodology overstate  | Double-blind evaluation is methodologically infeasible in     | QUALIFIED_FEASIBLE_BLINDED_IMAGE_|
|    |    |                                     | frontline agricultural extension. Replaced with blinded       | REVIEW                           |
|    |    |                                     | foliar image diagnostic reviews by independent expert panels. |                                  |
+----+----+-------------------------------------+---------------------------------------------------------------+----------------------------------+
| D13| P2 | Withdrawal vs MoU termination mix-up| Disentangled: Individual farmers retain immediate voluntary   | RESOLVED_DISENTANGLED_RIGHTS     |
|    |    |                                     | withdrawal rights; institutional MoU termination requires 30  |                                  |
|    |    |                                     | days advance written notice.                                  |                                  |
+----+----+-------------------------------------+---------------------------------------------------------------+----------------------------------+
```

---

## 3. Detailed Technical Analysis of Residual Risks

### 3.1 Finding D1: Live Cloud Staging Deployment Absent (Severity: P1)
- **Technical Context:** The repository contains a complete, verified Next.js 16 build (`frontend/vercel.json`), pre-configured for Singapore (`sin1`) with enterprise security headers. The backend harness includes 9 staging acceptance tests (`backend/tests/test_staging_acceptance.py`) which pass cleanly.
- **Residual Risk:** In the absence of an actual Vercel Preview cloud deployment, network-level DNS propagation, SSL termination, real edge cold-start latency, and live environment variable injection remain ungrounded in physical cloud reality.
- **Remediation Gate:** Gate A08 in the Owner Authorization Form allows the project owner to explicitly trigger the live preview deployment, or maintain the default local screen-share demonstration mode (Gate A07).

### 3.2 Finding D2: PostgreSQL Engine-Level Row-Level Security (Severity: P2)
- **Technical Context:** Tenant isolation is enforced in application code via `verify_farm_access()` dependencies in FastAPI routes. Automated integration tests verify that cross-tenant read/write attempts strictly return HTTP 403 Forbidden.
- **Residual Risk:** PostgreSQL engine-level RLS (`ALTER TABLE ... ENABLE ROW LEVEL SECURITY`) is not active. If an application bug, raw SQL query, or database admin access bypasses the ORM session filter, tenant data isolation could be compromised.
- **Status:** Documented residual architectural limitation. Migration to engine-level RLS is scheduled for the post-pilot database refactoring milestone.

### 3.3 Finding D3: Redis Rate-Limiter Fail-Open Mode (Severity: P2)
- **Technical Context:** Upstash Redis is configured with the isolated staging namespace `acrevia_staging:*`. To prevent denial of service to smallholder farmers during rural cellular connectivity flickers, the rate limiter falls back to an in-memory token bucket if Redis is unreachable.
- **Residual Risk:** Under a sustained Redis outage, distributed rate limits are not synchronized across serverless instances. An attacker could flood the `/api/v1/auth/login` or `/api/v1/advisory` endpoints with traffic exceeding free-tier Groq quotas.
- **Status:** Requires explicit project owner risk acceptance. Recommended patch: Implement `fail_closed` strictly for authentication and AI inference routes, retaining `fail_open` only for read-only weather and agronomic reference data.

### 3.4 Finding D4: Groq Preview Model Dependency (Severity: P2)
- **Technical Context:** KrishiBrain uses `qwen/qwen3.8-27b` on GroqCloud for low-latency multilingual advisory generation.
- **Residual Risk:** Being a preview model, availability SLAs are not guaranteed by Groq, and breaking model updates may occur without advance notice. Furthermore, account-level billing settings cannot be verified via API keys (`GROQ_ACCOUNT_BILLING_STATUS = NOT_VERIFIABLE`).
- **Mitigation:** The platform implements a deterministic extractive RAG fallback that retrieves and displays verbatim PJTSAU package of practices text if Groq inference fails or throttles (HTTP 429).
### 3.5 Finding D5: Previous Test-Accounting Discrepancy (Severity: P3)
- **Technical Context:** Earlier project documentation cited 240 tests (Stage 10 baseline) or 261 tests (caused by double-counting the 9 staging acceptance tests from 	est_staging_acceptance.py on top of the 145 backend total).
- **Reconciliation:** Reconciled against the physical test inventory in the repository: 145 backend tests (including the 9 staging acceptance tests), 55 ML/agronomic tests, 9 computer vision API tests, and 43 frontend Jest/React unit tests.
- **Final Pass Rate:** 252/252 passing tests (100% pass rate, zero test failures, zero regressions).
- **Status:** RESOLVED_RECONCILED.

### 3.6 Finding D6: Frontend Lint Script Configuration (Severity: P4)
- **Technical Context:** Executing 
pm run lint (
ext lint) in the rontend/ directory exits with error code 1 due to missing eslint and eslint-config-next packages in devDependencies within rontend/package.json.
- **Residual Risk:** While TypeScript compilation (
px tsc --noEmit) passes with 0 errors and production build (
px next build) succeeds cleanly, stylistic defects, unreachable code patterns, or subtle React Hook dependency issues are not caught by an automated linter.
- **Status:** OPEN_DEFERRED — TOOLING_DEFECT. A TypeScript pass does not equal a lint pass. Installation of ESLint dependencies is scheduled for post-handover frontend tooling maintenance.

### 3.7 Finding D7: Institutional Identity Discrepancies (Severity: P2)
- **Technical Context:** Earlier working drafts contained administrative discrepancies, including referring to KVK Malyal\'s head as \'A Dileep Kumar\' (omitting the official tribal surname Banoth) and misidentifying administrative district boundaries.
- **Resolution:** Cross-referenced against primary university directories on pjtau.edu.in and official ICAR-ATARI Zone X records. Confirmed Dr. Banoth Dileep Kumar (Senior Scientist & Head, Entomology) at KVK Malyal, Mahabubabad District, and Dr. Chandrashekar (Senior Scientist & Head, Agronomy) at KVK Kampasagar, Nalgonda District.
- **Status:** RESOLVED_VERIFIED_PRIMARY_SOURCE.

### 3.8 Finding D8: DPDP Legal Assessment Not Certified (Severity: P2)
- **Technical Context:** ACREVIA\'s data architecture is designed according to the principles of India\'s Digital Personal Data Protection (DPDP) Act 2023 (consent management, purpose specification, local server storage in p-south-1, right to erasure).
- **Residual Risk:** The platform has not undergone formal statutory audit or certification by licensed Indian legal counsel.
- **Status:** QUALIFIED_STATUS — DPDP_COMPLIANCE_CERTIFICATION_NOT_CLAIMED. Compliance certification is explicitly NOT claimed. Independent legal counsel review is required prior to collecting any live farmer personal data.

### 3.9 Finding D9: Operational 48-Hour Deletion Claim Qualification (Severity: P2)
- **Technical Context:** Deletion requests execute programmatic cascading deletions across active PostgreSQL tables and invalidate Upstash Redis cache entries within 48 hours.
- **Residual Risk:** Immutable write-ahead logs (WAL), cryptographic ledger records, and automated cloud backup snapshots cannot be selectively mutated on demand. Backup snapshots age out according to a standard 30-day lifecycle retention schedule.
- **Status:** QUALIFIED_OPERATIONAL_DELETION_PATH. Operational database records are purged within 48 hours; backup archives expire over 30 days. Full multi-stage verification across all replicas remains ongoing.

### 3.10 Finding D10: Unqualified Zero-Cost Commitment Qualification (Severity: P2)
- **Technical Context:** ACREVIA is offered to KVK partner institutions and participating smallholders on a strict non-commercial, zero-fee participation basis.
- **Residual Risk:** The software relies on third-party cloud free tiers (Render, Vercel, Upstash, Supabase, Groq). If query volume exceeds free-tier thresholds, the initiative absorbs operational compute expenses. Permanent, infinite zero-cost scaling cannot be promised without dedicated research funding.
- **Status:** QUALIFIED_NO_FEE_PARTICIPATION_MODEL. Institutional correspondence distinguishes no-participation-fee smallholder access from underlying cloud and API infrastructure costs.

### 3.11 Finding D11: Academic Joint-Authorship Qualification (Severity: P2)
- **Technical Context:** Earlier outreach drafts unconditionally promised joint authorship on published research papers to participating KVK scientists.
- **Residual Risk:** Blanket co-authorship promises without peer-reviewed intellectual contribution violate International Committee of Medical Journal Editors (ICMJE) and ICAR research integrity guidelines.
- **Status:** QUALIFIED_ICMJE_CONTRIBUTION_BASED_AUTHORSHIP. Authorship is strictly contribution-based, requiring substantial contribution to trial design, data acquisition, or analysis.

### 3.12 Finding D12: Blinded Image Diagnostic Review Methodology (Severity: P2)
- **Technical Context:** Early proposal drafts referred to a \'double-blind clinical trial\' methodology for pest and disease diagnostics in frontline agriculture.
- **Residual Risk:** True double-blinding is structurally impossible in agricultural field extension, where participating farmers and field scientists observe physical crop conditions, foliage, and ambient field environments.
- **Status:** QUALIFIED_FEASIBLE_BLINDED_IMAGE_REVIEW. Methodology revised to rigorous blinded foliar image diagnostic reviews: independent senior agronomists evaluate randomized crop photographs without seeing AI model predictions.

### 3.13 Finding D13: Disentangled Individual Farmer Withdrawal vs Institutional MoU Termination (Severity: P2)
- **Technical Context:** Previous governance drafts conflated individual farmer consent withdrawal with institutional MoU cancellation.
- **Resolution:** The governance framework strictly disentangles these rights: individual participating farmers possess the unconditional right to withdraw consent and halt data collection immediately with zero penalty; institutional MoU termination requires 30 days advance written notice by either party.
- **Status:** RESOLVED_DISENTANGLED_RIGHTS.

---

## 4. Owner Risk Acceptance & Governance Directives

`
+========================================================================================================================+
| OWNER RESIDUAL RISK ACCEPTANCE SPECIFICATION                                                                           |
+----+----+-------------------------------------+----------------------------------+-------------------------------------+
| ID |Sev | Finding Description                 | Current Risk Status Code         | Owner Acceptance Evidence Required  |
+----+----+-------------------------------------+----------------------------------+-------------------------------------+
| D1 | P1 | Live Vercel staging deploy absent   | OPEN — LIVE_DEPLOYMENT_PENDING   | Gate A08 in Owner Input Form        |
| D2 | P2 | PostgreSQL engine RLS absent        | DOCUMENTED_RESIDUAL_LIMITATION   | Acknowledged in System Architecture |
| D3 | P2 | Redis rate-limiter fail-open mode   | DOCUMENTED_RESIDUAL_RISK         | Owner Risk Acceptance (Gate A07/A08)|
| D4 | P2 | Groq preview model dependency       | DOCUMENTED_AI_AVAILABILITY_RISK  | Extractive Fallback Acknowledged    |
| D5 | P3 | Previous test-accounting discrepancy| RESOLVED_RECONCILED              | None (Reconciled to 252 tests)      |
| D6 | P4 | Frontend lint script configuration  | OPEN_DEFERRED — TOOLING_DEFECT   | Post-Handover Tooling Acceptance    |
| D7 | P2 | Institutional identity discrepancies| RESOLVED_VERIFIED_PRIMARY_SOURCE | None (Verified against PJTSAU)      |
| D8 | P2 | DPDP legal assessment not certified | QUALIFIED_STATUS — NOT_CLAIMED   | Legal Review Required for Phase 03  |
| D9 | P2 | Operational 48-hr deletion claim    | QUALIFIED_OPERATIONAL_PATH       | 48h Live / 30d Backup Path Noted    |
| D10| P2 | Unqualified zero-cost commitment    | QUALIFIED_NO_FEE_MODEL           | No-Fee Outreach Scope Acknowledged  |
| D11| P2 | Unqualified joint-authorship terms  | QUALIFIED_ICMJE_AUTHORSHIP       | ICMJE Standard Acknowledged         |
| D12| P2 | Double-blind methodology overstate  | QUALIFIED_FEASIBLE_IMAGE_REVIEW  | Blinded Image Review Acknowledged   |
| D13| P2 | Withdrawal vs MoU termination mix-up| RESOLVED_DISENTANGLED_RIGHTS     | Individual vs MoU Split Accepted    |
+----+----+-------------------------------------+----------------------------------+-------------------------------------+
`

> [!IMPORTANT]
> **GOVERNANCE NOTICE ON RESIDUAL RISKS:**  
> Residual risks D1, D2, D3, D4, D6, D8, D9, D10, D11, D12, and D13 have been completely audited and transparently classified.  
> **No owner risk acceptance has been inferred or recorded.**  
> The project owner reviews and accepts or defers these residual exposures via [PHASE_02_OWNER_INPUT_AND_AUTHORIZATION_FORM.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/PHASE_02_OWNER_INPUT_AND_AUTHORIZATION_FORM.md).
