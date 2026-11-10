# ACREVIA — GLOBAL RISK REGISTER (PHASE 07 RECONCILIATION)
## Comprehensive Risk Matrix, Historical Crosswalk & Mitigation Evidence

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document Code:** `ACREVIA_GLOBAL_RISK_REGISTER_PHASE_07.md`  
**Execution Date:** November 10, 2026  
**Audited Baseline:** Post-Phase 07 Implementation & Preflight Verification  
**Automated Test Baseline:** 309 physical automated tests passing  

---

## 1. Global Risk Matrix (Canonical IDs & Historical Crosswalk)

| Canonical ID | Legacy ID | Risk Description | Severity | Phase 07 Status | Verification Evidence |
|---|---|---|---|---|---|
| **`DB-RLS-01`** | D2 | PostgreSQL RLS Physical Tenant Isolation & Policy Hardening | High | **`PARTIALLY_IMPLEMENTED`** | Hardened dual-identity trust boundary (`SESSION_USER` + `CURRENT_USER` + `app.is_admin`); 132/132 tables mapped; 751 atomic DDL statements generated; 28 RLS automated tests passing; cloud branch execution held pending owner sign-off on Decision Gate 1. |
| **`ADMIN-TRUST-01`** | — | Administrative Bypass Context & Role Spoofing Resistance | High | **`COMPLETE_VERIFIED`** | Upgraded SQL bypass to demand `SESSION_USER` and `CURRENT_USER` in `('neondb_owner', 'acrevia_admin')` plus `app.is_admin = 'true'`. Tested and verified immune to session context manipulation. |
| **`ADMIN-DEFINER-01`** | — | Security Definer Function Privilege Escalation | High | **`COMPLETE_VERIFIED`** | Codebase verified to contain 0 stored procedures/functions (`pg_proc` check added to harness). Dual-boundary check structurally immune to `CURRENT_USER` elevations because `SESSION_USER` remains unprivileged connecting role. |
| **`DB-POLICY-01`** | — | Complete Entity Classification & Policy Compilation Coverage | High | **`COMPLETE_VERIFIED`** | All 132 tables classified (25 Direct, 13 User, 53 Indirect, 25 Reference, 16 Collaborative). `produce_quality_profiles` safely reclassified to Reference. 751 atomic DDL statements generated with zero errors. |
| **`DB-HIERARCHY-01`** | — | Relational Subquery Referential Integrity in Indirect Policies | Medium | **`COMPLETE_VERIFIED`** | All 53 indirect tenant tables audited; 8 foreign-key bindings aligned with model schemas; zero column mismatches across entire schema. |
| **`DB-MIGRATION-01`** | — | Alembic Migration Dialect Guarding & Idempotency | Medium | **`COMPLETE_VERIFIED`** | Migration `a1089411c87d` verified safe, non-destructive, dialect-guarded, and reversible with zero data loss. |
| **`DB-PRIVACY-01`** | — | Neon Parent-Branch Data Privacy & Leakage Prevention | High | **`COMPLETE_VERIFIED`** | Parent database audited; 100% synthetic seed data; zero real farmer PII present. Remote branch creation held in Mode A. |
| **`AUTH-ROUTING-01`** | — | Authentication API URL Composition & 404 Routing Diagnostics | High | **`COMPLETE_VERIFIED`** | Implemented `resolveApiUrl()` with automatic `/api/v1` and trailing slash deduplication; implemented `ApiError` with explicit non-JSON 404, 429, 503 diagnostics; Next.js rewrites normalized; 15 synthetic auth tests passing. |
| **`AUTH-RATE-01`** | D3 | Authentication Brute-Force & Rate Limiting Architecture | Medium | **`COMPLETE_VERIFIED`** | Distinct HTTP semantics: HTTP 429 for quota exhaustion; HTTP 503 for Redis dependency failures (fail-closed); 0 credentials leaked. |
| **`AI-FALLBACK-01`** | D4 | Agronomic AI Inference & Multi-Model Resilience | Medium | **`COMPLETE_VERIFIED`** | Four-tier fallback: `qwen/qwen3.8-27b` -> `llama-3.3-70b-versatile` -> `llama-3.1-8b-instant` -> offline PJTSAU vector RAG degradation; all passing in test suite. |
| **`AI-PROVIDER-02`** | — | Single Upstream AI Infrastructure Dependency | Low | **`ACCEPTED_SINGLE_PROVIDER_DEPENDENCY`** | Documented dependency on GroqCloud provider; mitigated via local vector RAG fallback. |
| **`FRONTEND-TYPES-01`** | D5 | Frontend Type Safety & API Response Envelopes | Low | **`COMPLETE_VERIFIED`** | Zero TypeScript compilation errors (`tsc --noEmit`); clean Next.js Turbopack build; 109 `any` envelope warnings documented with runtime validation. |
| **`SMS-INTEGRATION-01`** | D6 | SMS Gateway & OTP Verification Service | Medium | **`PENDING_OWNER_INPUT`** | SMS gateway integration deferred pending owner selection of Indian telecommunications provider. |
| **`AUDIT-INTEGRITY-01`** | D7 | Audit Log Tamper Resistance & Key Management | Medium | **`PARTIALLY_IMPLEMENTED`** | Schema and append-only audit logging tables established in RLS; AWS KMS / HashiCorp Vault envelope encryption deferred to Phase 08. |
| **`PRIVACY-GOVERNANCE-01`**| D8 | DPDP Act 2023 Compliance & Data Protection | High | **`GOVERNED_PRE_PILOT`** | Zero personal farmer data collected; `DPDP_COMPLIANCE_CERTIFICATION = NOT_CLAIMED`; compliance assessment completed. |
| **`STAGING-DEPLOY-01`** | D9 | Cloud Staging Environment Isolation | Medium | **`AWAITING_OWNER_SIGN_OFF`** | Vercel Preview configuration prepared; deployment strictly blocked (`LIVE_STAGING_DEPLOYMENT_TRIGGERED = FALSE`). |
| **`OWNER-AUTH-01`** | D10 | Project Leadership Identity & Formal Decision Sign-Off | Critical | **`AWAITING_OWNER_INPUT`** | Formal decision document prepared; identity fields and Gates 1–5 unpopulated awaiting direct leadership input. |
| **`FIELD-PILOT-01`** | D11 | On-Farm Pilot Trials & Agricultural Chemical Advice | Critical | **`STRICTLY_PROHIBITED`** | Gates strictly enforced; field trials, surveying, and personal data collection prohibited. |
| **`SATELLITE-PROVIDER-01`**| D12/D13 | Geospatial Satellite Data Ingestion Resilience | Medium | **`COMPLETE_VERIFIED`** | Primary Earth Search STAC (AWS Singapore) with Planetary Computer fallback; automated cloud masking verified. |

---

## 2. D2 Detailed Status & Progression to Mode B

Under Phase 07 Governance:
- Promotion of `DB-RLS-01` to `COMPLETE_VERIFIED` requires real execution against an active PostgreSQL staging branch with live system catalog queries (`pg_class`, `pg_policies`, `pg_roles`, `pg_auth_members`).
- Because remote branch creation is contingent on owner authorization (Decision Gate 1), `DB-RLS-01` is held as:
  ```text
  DB-RLS-01 = PARTIALLY_IMPLEMENTED (Preflight Complete; Awaiting Remote Staging Execution; Live Production Protected)
  ```
- **Code Hardening:** Complete, dual-boundary hardened, and independently verified.
- **Vulnerability Remediation:** Complete (unprivileged self-escalation and `SECURITY DEFINER` bypass blocked).
- **Automated Regression Suite:** Complete (309/309 physical tests passing).
- **Physical Staging Verification:** Ready to execute immediately upon owner sign-off on Gate 1.
