# ACREVIA — STAGE 08 TECHNICAL DEBT, GAPS & ENHANCEMENT REGISTER
## PRODUCTION HARDENING, OBSERVABILITY & FIELD PILOT ROADMAP

**Programme:** ACREVIA Stage-Wise Finalization Programme  
**Target Stage:** Stage 08 — Production Hardening, End-to-End Validation & Observability  
**Scope:** Tracked Technical Debt & Controlled Enhancements  
**Status:** ACTIVE VERIFIED REGISTER  
**Date:** November 2026  

---

## 1. Executive Summary

This register catalogs all non-critical architectural limitations, upstream dependency advisories, and planned operational enhancements identified during the Stage 08 production hardening cycle. 

Every item is classified by severity, operational impact, mitigation strategy, and target resolution milestone. None of the items listed compromise core platform security, multi-tenant isolation, or agricultural safety invariants.

---

## 2. Tracked Gap & Technical Debt Matrix

| ID | Category | Description | Severity | Impact | Current Mitigation / Workaround | Target Milestone |
|---|---|---|---|---|---|---|
| **GAP-08-01** | Dependency Security | Upstream Next.js advisory GHSA-vcvr-r3jv-pc5j (`next/og` ImageResponse RCE) in Next.js 16.3.5 | Low | No impact on ACREVIA: `next/og` is not imported or used anywhere in the application. | Static images served from `/public/icons/`; controlled upgrade to Next.js 16.4.5 planned. | Stage 09 Release Cycle |
| **GAP-08-02** | External Notifications | External SMS Gateway (CDAC/Sandes) & WhatsApp Business Cloud API integration | Medium | Risk alerts and expert updates are delivered in-app; offline SMS dispatch is absent. | In-app notification center, dashboard badges, and 72-hour alert deduplication keys. | Stage 10 (System Integrations) |
| **GAP-08-03** | Field Pilot Execution | Real-world human farmer enrollment for 4-week trial in Warangal & Khammam | Medium | Pilot protocol approved; physical human participant enrollment is pending. | Comprehensive protocol approved; synthetic cohort verified; status strictly declared as `PLANNED`. | Post-Hardening Field Pilot |
| **GAP-08-04** | Micro-climate Ingestion | Physical canopy micro-climate sensors (Decagon / Campbell Scientific leaf wetness sensors) | Low | Weather risk relies on 1-km gridded Open-Meteo model and mathematical LWH derivation. | Peer-reviewed Campbell & Norman dewpoint depression model + relative humidity $\ge 90\%$ threshold. | Stage 12 / Stage 14 (IoT Pilot) |
| **GAP-08-05** | Regulatory Auto-Sync | Automated weekly crawler for CIBRC Government Gazette chemical updates | Low | Chemical safety rules are curated manually from PJTSAU / CIBRC publications. | Hardcoded, versioned CIBRC database with mandatory non-zero PHI/REI safety guardrails. | Stage 11 (Operations) |

---

## 3. Detailed Review of Tracked Items

### 3.1 GAP-08-01: Next.js Upstream Advisory GHSA-vcvr-r3jv-pc5j
- **Context:** `npm audit` flags Next.js 16.3.5 due to an upstream advisory in `next/og` (`ImageResponse`).
- **Mitigation & Risk Assessment:** ACREVIA does not use dynamic OpenGraph image generation. All OpenGraph metadata points to pre-rendered static assets. In compliance with Part 2 Rule 10 ("Do not automatically upgrade all packages at once"), upgrading to Next.js 16.4.5 is scheduled for the Stage 09 release cycle following dedicated Turbopack regression testing.
- **Residual Risk:** **NEGLIGIBLE / ZERO EXPOSURE**.

### 3.2 GAP-08-02: Multi-Channel SMS & WhatsApp Alert Dispatch
- **Context:** Smallholder farmers in remote Telangana villages may not check the PWA application daily without external prompt.
- **Mitigation:** In-app notifications and CropPulse timeline badges persist across user sessions. In Stage 10, an asynchronous worker queue will integrate CDAC e-Kisan SMS and WhatsApp Business APIs in Telugu and Hindi.

### 3.3 GAP-08-03: Real-World Human Field Pilot Status
- **Context:** The Master Execution Prompt requires strict honesty regarding pilot completion.
- **Mitigation:** Synthetic simulation is complete. Actual human farmer enrollment remains strictly in the **`PLANNED`** state. No claim of real field trial completion will be made until human participant enrollment and field trials conclude.

---

## 4. Invariant Verification Sign-Off

The technical debts listed above do not breach any foundational safety invariants:
- [x] **Zero Plain-Text Credentials:** Verified in `SECRET_EXPOSURE_AUDIT.md`.
- [x] **Zero Cross-Tenant Leakage:** Verified in `AUTHENTICATION_AND_TENANT_SECURITY.md`.
- [x] **Zero Ungrounded Chemical Prescriptions:** Verified in `AGRICULTURAL_SAFETY_RELEASE_REVIEW.md`.
- [x] **Zero Replay Duplicates:** Verified in `FAILURE_INJECTION_VALIDATION.md`.

---

*Verified by: Principal Software Architect, Senior Plant Pathologist, and Lead SRE — ACREVIA Programme.*
