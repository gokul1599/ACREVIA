# ACREVIA — GLOBAL RISK REGISTER (PHASE 06 RECONCILIATION)
## Comprehensive Risk Matrix, Historical Crosswalk & Mitigation Evidence

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document Code:** `ACREVIA_GLOBAL_RISK_REGISTER_PHASE_06.md`  
**Execution Date:** November 9, 2026  
**Audited Baseline:** Post-Phase 06 Implementation & Verification  

---

## 1. Global Risk Matrix (Canonical IDs & Historical Crosswalk)

| Canonical ID | Legacy ID | Risk Description | Severity | Phase 06 Status | Verification Evidence |
|---|---|---|---|---|---|
| **`DB-RLS-01`** | D2 | PostgreSQL RLS Physical Tenant Isolation & Policy Hardening | High | **`PARTIALLY_IMPLEMENTED`** | Code hardened with role-based check `CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin')`; GUC self-escalation probe verified blocked; 26 RLS tests passing; cloud branch execution held pending owner sign-off on Decision Gate 1. |
| **`AUTH-RATE-01`** | D3 | Authentication Brute-Force & Rate Limiting Architecture | Medium | **`COMPLETE_VERIFIED`** | Distinct HTTP semantics: HTTP 429 for quota exhaustion; HTTP 503 for Redis dependency failures (fail-closed); 0 credentials leaked. |
| **`AI-FALLBACK-01`** | D4 | Agronomic AI Inference & Multi-Model Resilience | Medium | **`COMPLETE_VERIFIED`** | Four-tier fallback: `qwen/qwen3.8-27b` -> `llama-3.3-70b-versatile` -> `llama-3.1-8b-instant` -> offline PJTSAU vector RAG degradation; all passing in test suite. |
| **`AI-PROVIDER-02`** | — | Single Upstream AI Infrastructure Dependency | Low | **`ACCEPTED_SINGLE_PROVIDER_DEPENDENCY`** | Documented dependency on GroqCloud provider; mitigated via local vector RAG fallback. |
| **`FRONTEND-TYPES-01`** | D5 | Frontend Type Safety & API Response Envelopes | Low | **`COMPLETE_VERIFIED`** | Zero TypeScript compilation errors (`tsc --noEmit`); clean Next.js Turbopack build; 109 `any` envelope warnings documented with runtime validation. |
| **`SMS-INTEGRATION-01`** | D6 | SMS Gateway & OTP Verification Service | Medium | **`PENDING_OWNER_INPUT`** | SMS gateway integration deferred pending owner selection of Indian telecommunications provider. |
| **`AUDIT-INTEGRITY-01`** | D7 | Audit Log Tamper Resistance & Key Management | Medium | **`PARTIALLY_IMPLEMENTED`** | Schema and append-only audit logging tables established in RLS; AWS KMS / HashiCorp Vault envelope encryption deferred to Phase 07. |
| **`PRIVACY-GOVERNANCE-01`**| D8 | DPDP Act 2023 Compliance & Data Protection | High | **`GOVERNED_PRE_PILOT`** | Zero personal farmer data collected; `DPDP_COMPLIANCE_CERTIFICATION = NOT_CLAIMED`; compliance assessment completed. |
| **`STAGING-DEPLOY-01`** | D9 | Cloud Staging Environment Isolation | Medium | **`AWAITING_OWNER_SIGN_OFF`** | Vercel Preview configuration prepared; deployment strictly blocked (`LIVE_STAGING_DEPLOYMENT_TRIGGERED = FALSE`). |
| **`OWNER-AUTH-01`** | D10 | Project Leadership Identity & Formal Decision Sign-Off | Critical | **`AWAITING_OWNER_INPUT`** | Formal decision document prepared; identity fields and Gates A01–A05 unpopulated awaiting direct leadership input. |
| **`FIELD-PILOT-01`** | D11 | On-Farm Pilot Trials & Agricultural Chemical Advice | Critical | **`STRICTLY_PROHIBITED`** | Gates A10, A11, A12 strictly enforced; field trials, surveying, and personal data collection prohibited. |
| **`SATELLITE-PROVIDER-01`**| D12/D13 | Geospatial Satellite Data Ingestion Resilience | Medium | **`COMPLETE_VERIFIED`** | Primary Earth Search STAC (AWS Singapore) with Planetary Computer fallback; automated cloud masking verified. |
| **`AUTH-ROUTING-01`** | — | Authentication API URL Composition & 404 Routing Diagnostics | High | **`COMPLETE_VERIFIED`** | Implemented `resolveApiUrl()` with automatic `/api/v1` and trailing slash deduplication; implemented `ApiError` with explicit non-JSON 404, 429, 503, and network failure diagnostics; Next.js rewrites normalized; synthetic login lifecycle independently verified; 11 frontend and 4 backend tests passing. |

---

## 2. D2 Detailed Status & Completion Criteria

Under Phase 06 Section 23:
- Promotion of `DB-RLS-01` to `COMPLETE_VERIFIED` requires real execution against an active PostgreSQL staging branch with system catalog queries (`pg_class`, `pg_policies`, `pg_roles`).
- Because remote branch creation is contingent on owner authorization (Decision Gate 1), `DB-RLS-01` is classified as:
  ```text
  DB-RLS-01 = PARTIALLY_IMPLEMENTED (Awaiting Staging Database Branch Execution; Live Production Protected)
  ```
- **Code Hardening:** Complete and independently verified.
- **Vulnerability Remediation:** Complete (unprivileged self-escalation via `app.is_admin` blocked).
- **Automated Regression Suite:** Complete (292/292 tests passing).
- **Physical Staging Verification:** Ready to execute immediately upon owner approval.
