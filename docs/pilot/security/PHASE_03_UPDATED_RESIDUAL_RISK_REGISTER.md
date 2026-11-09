# ACREVIA — PHASE 03 UPDATED RESIDUAL RISK REGISTER

**Programme:** ACREVIA Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Audited Baseline Commit:** `252d47e`  
**Register Update Date:** November 9, 2026  
**Status Gate:** Pre-Authorization Technical Readiness Closure  

---

## 1. Risk Matrix Overview (D1 through D13)

| Risk ID | Risk Domain & Description | Pre-Phase 03 Status | Phase 03 Status | Current Mitigation & Safeguards |
|:---|:---|:---|:---|:---|
| **D1** | **Staging Environment Isolation:** Verification of separate Vercel preview/staging project and database credentials to eliminate contamination of production. | IDENTIFIED | **PENDING_OWNER_AUTHORIZATION** | Staging preview configuration verified; zero live cloud deployments triggered without owner authorization. |
| **D2** | **PostgreSQL Row-Level Security (RLS):** Defense-in-depth multi-tenant farm isolation at the database engine layer across all 132 tables. | IDENTIFIED | **PARTIALLY_IMPLEMENTED** | All 132 tables classified; transaction-local context implemented; Alembic migration `a1089411c87d` written & tested; awaiting staging DB branch execution. |
| **D3** | **Fail-Open Authentication Rate Limiting:** Rate limiter falling back to in-memory during Upstash Redis outage, permitting brute-force attacks on auth endpoints. | IDENTIFIED | **RESOLVED** | Fail-closed policy enforced on `/auth/login` and `/auth/register` (HTTP 503 + `Retry-After: 60`); zero secret leakage; 14 tests passing. |
| **D4** | **Groq Preview Model Deprecation / Single-Point Failure:** Dependency on preview model `qwen/qwen3.8-27b` without resilient fallbacks. | IDENTIFIED | **RESOLVED_CODE_LEVEL** | 3-model fallback chain (`qwen` -> `llama-3.3-70b` -> `llama-3.1-8b`), bounded retries, and deterministic PJTSAU RAG fallback; 5 tests passing. |
| **D5** | **Production Secrets & Key Management:** Secure storage of Copernicus, HuggingFace, Upstash, and Neon credentials. | MONITORED | **MANAGED_SAFEGUARDS** | Zero credentials hardcoded; `.env` templates parameterized; health check endpoints redact secrets. |
| **D6** | **Frontend Lint Tooling Broken in Next.js 16:** `next lint` failing due to deprecation; 8 code-level lint errors unverified. | IDENTIFIED | **RESOLVED** | ESLint 9+ flat config (`eslint.config.mjs`) configured; all 8 errors resolved; 0 errors, clean TS check, clean build. |
| **D7** | **SMS Gateway Dependency for OTP:** Reliance on external SMS providers without active gateway credentials. | MONITORED | **ARCHITECTURALLY_RESOLVED** | Primary auth confirmed as bcrypt password; OTP explicitly documented as development simulation. |
| **D8** | **Audit Trail Immutability:** Tamper-evident logging of administrative and expert actions. | MONITORED | **ARCHITECTURALLY_RESOLVED** | Append-only `audit_logs` table protected from non-admin updates; transaction-scoped actor tracking. |
| **D9** | **Offline Sync Conflict Resolution:** Data reconciliation between field device drafts and cloud database. | MITIGATED | **RESOLVED** | IndexedDB client + deterministic timestamp/UUID reconciliation + manual conflict queue tested in frontend suite. |
| **D10** | **Consent Withdrawal Real-Time Propagation:** Immediate revocation of data processing grants upon farmer withdrawal. | MITIGATED | **RESOLVED** | Real-time session token revocation and cache invalidation implemented in `consent_records` and `session_tokens`. |
| **D11** | **Satellite Imagery Cloud Masking:** False alerts due to monsoon cloud cover in optical Sentinel-2 scenes. | RESOLVED | **RESOLVED** | Post-CDSE SCL scene classification cloud masking and Element 84 fallback verified in Stage 01. |
| **D12** | **Voice Interface Dialect Accuracy:** Regional Telugu dialect nuances in rural Mahabubabad/Nalgonda. | EXPERIMENTAL | **RESEARCH_PROTOTYPE** | Marked explicitly as assistive experimental prototype; text confirmation required prior to query submission. |
| **D13** | **DPDP Act Compliance Certification Claim:** Regulatory exposure from claiming certified compliance prior to formal DPA. | MITIGATED | **MITIGATED** | `DPDP_COMPLIANCE_CERTIFICATION = NOT_CLAIMED` strictly maintained; zero farmer personal data collected. |

---

## 2. Risk Evolution Summary

- **Risks Resolved in Phase 03:** D3 (Auth Rate Limiting) and D6 (Frontend Lint Tooling).
- **Risks Resolved at Code Level:** D4 (AI Provider Multi-Model Fallback Chain & Grounded RAG).
- **Risks Advanced to Partially Implemented:** D2 (PostgreSQL RLS Architecture, Migration & Automated Suite complete; awaiting staging database execution).
- **Risks Maintained Under Strict Governance:** D1, D5, D7, D8, D13.

Zero residual risks prevent presentation of the final handover to the project owner.
