# ACREVIA — PHASE 04 UPDATED RESIDUAL RISK REGISTER

**Programme:** ACREVIA Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Audited Baseline Commit:** `5cdd087`  
**Register Update Date:** November 9, 2026  
**Status Gate:** Phase 04 Database Verification & Technical Readiness  

---

## 1. Comprehensive Reconciliation of Residual Risks (D1 through D13)

| Risk ID | Risk Domain & Description | Pre-Phase 04 Status | Current Phase 04 Status | Technical Evidence & Mitigation Strategy | Owner Dependency |
|:---|:---|:---|:---|:---|:---|
| **D1** | **Staging Environment Isolation:** Separation of Vercel preview and Neon staging database to prevent production contamination. | PENDING_OWNER_AUTH | **PENDING_OWNER_AUTHORIZATION** | Preview deployment configuration verified; zero cloud deploys triggered without authorization. | Owner Gate A08 required |
| **D2** | **PostgreSQL Row-Level Security (RLS):** Database engine level multi-tenant isolation across all 132 entities. | PARTIALLY_IMPLEMENTED | **PARTIALLY_IMPLEMENTED** | 132 entities classified; context lifecycle implemented; Alembic migration `a1089411c87d` verified; 23 tests passing. Awaiting staging DB branch execution. | Authorize staging DB branch |
| **D3** | **Fail-Open Authentication Rate Limiting:** Brute-force exposure during Upstash Redis outage. | RESOLVED | **INDEPENDENTLY_VERIFIED** | Fail-closed policy on auth endpoints returning HTTP 503 + Retry-After: 60; zero secret leakage; 20 tests passing. | None (Fully resolved) |
| **D4** | **Groq AI Preview Model Deprecation / Outage:** Dependency on single preview model without resilient fallbacks. | RESOLVED_CODE_LEVEL | **INDEPENDENTLY_VERIFIED_CODE_LEVEL** | 3-model chain on Groq + deterministic PJTSAU grounded RAG fallback; 5 tests passing. | None (Fully resolved) |
| **D5** | **Production Secrets & Key Management:** Secure storage of external API credentials. | MANAGED_SAFEGUARDS | **MANAGED_SAFEGUARDS** | Parameterized in `.env`; zero secrets committed; health check endpoints redact sensitive credentials. | Monitor key rotation |
| **D6** | **Broken Frontend Lint Tooling in Next.js 16:** Inability to run ESLint checks in CI/CD pipeline. | RESOLVED | **INDEPENDENTLY_VERIFIED** | Flat config `eslint.config.mjs`; all 32 unused var warnings fixed; warnings reduced from 141 to 109; 0 errors; clean TS & build. | None (Fully resolved) |
| **D7** | **SMS Gateway Dependency for OTP:** Reliance on external telecommunications providers. | ARCHITECTURALLY_RESOLVED | **NOT_INTEGRATED_PASSWORD_PRIMARY** | Password-based primary auth confirmed; zero external SMS dependencies present in repository. | None (Pilot uses password) |
| **D8** | **Audit Trail Immutability:** Tampering risk on administrative and expert logs. | ARCHITECTURALLY_RESOLVED | **ARCHITECTURALLY_RESOLVED** | Append-only `audit_logs` table protected from non-admin modification; actor context bound to sessions. | None (Fully resolved) |
| **D9** | **Offline Sync Conflict Resolution:** Reconciliation of offline field records with server state. | RESOLVED | **RESOLVED** | IndexedDB client + deterministic timestamp/UUID reconciliation + conflict queue verified in test suite. | None (Fully resolved) |
| **D10** | **Consent Revocation Real-Time Propagation:** Timely revocation of farmer data grants. | RESOLVED | **RESOLVED** | Real-time session token revocation and cache invalidation implemented in `consent_records`. | None (Fully resolved) |
| **D11** | **Satellite Imagery Cloud Masking:** False alerts due to monsoon cloud cover. | RESOLVED | **RESOLVED** | Post-CDSE SCL scene classification cloud masking and Element 84 fallback verified in Stage 01. | None (Fully resolved) |
| **D12** | **Voice Interface Dialect Accuracy:** Regional Telugu dialect nuances. | RESEARCH_PROTOTYPE | **RESEARCH_PROTOTYPE** | Marked explicitly as assistive experimental prototype; text confirmation required prior to query submission. | None (Assistive only) |
| **D13** | **DPDP Act Compliance Certification Claim:** Regulatory exposure from claiming certified compliance prior to formal DPA. | MITIGATED | **MITIGATED** | `DPDP_COMPLIANCE_CERTIFICATION = NOT_CLAIMED` strictly maintained; zero farmer personal data collected. | Execute institutional DPA |

---

## 2. Risk Status Evolution

- **Independently Verified in Phase 04:** D3 (Rate Limiting), D4 (AI Fallback), D6 (Frontend Lint).
- **Advanced in Testing & Completeness:** D2 (PostgreSQL RLS expanded to 23 automated tests covering all 16 isolation criteria; Alembic migration `a1089411c87d` verified).
- **Classified with High Fidelity:** D7 (OTP/SMS confirmed not connected; password primary authentication).
- **Maintained Under Strict Governance:** D1, D5, D8, D13.
