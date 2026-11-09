# ACREVIA — PHASE 05: NEON STAGING & POSTGRESQL RLS VERIFICATION MASTER REPORT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India (KVK Malyal, KVK Kampasagar, PJTSAU, ICAR-ATARI Zone X)  
**Report Identifier:** SEC-PHASE05-MASTER-2026-11-09  
**Execution Date:** November 9, 2026  
**Repository Branch:** `main`  
**Previous Baseline Commit:** `7f0e7e5`  
**Total Automated Tests:** 289 physical tests passing across 4 independent runners (100% pass rate)

---

## 1. Executive Summary

Phase 05 established the complete engineering and governance foundation to advance ACREVIA from code-level Row-Level Security (RLS) definitions to independently evidenced PostgreSQL database-level tenant isolation, while strictly protecting live cloud infrastructure and preserving project owner decision boundaries.

### Key Milestones Delivered:
1. **Repository & Runtime Baseline Forensic Audit (WP-01):**
   - Verified Git repository HEAD at `7f0e7e5`, branch `main`, working tree clean.
   - Identified runtime environment: Windows 11 Home, Python 3.11.16 (`.venv`), Node.js v24.19.0, npm 11.17.0.
   - Confirmed absence of local PostgreSQL daemon, Docker, and `neon` CLI on PATH.
   - Confirmed configured database endpoint in `.env`: `ep-muddy-mode-a1nd6rrb-pooler.ap-southeast-1.aws.neon.tech` (strictly protected from non-authorized migrations).
2. **Entity Classification Reconciliation (WP-02):**
   - Reconciled all 132 database entities in `Base.metadata`.
   - Forensically explained the historical Phase 03 typographic reporting mismatch (where Phase 03 headers stated "51" indirect and "19" collaborative, but actually listed 54 indirect and 16 collaborative tables).
   - Confirmed exact 132-table topology: 25 `TENANT_DIRECT`, 13 `USER_OWNED`, 54 `TENANT_INDIRECT`, 24 `SHARED_REFERENCE`, and 16 `COMMUNITY_COLLABORATIVE`. Zero unmapped tables.
3. **RLS Policy Architecture & Composition Fix (WP-03):**
   - Identified and resolved the PostgreSQL RLS policy composition requirement where `RESTRICTIVE` policies alone without an applicable `PERMISSIVE` policy deny all operations.
   - Enhanced `generate_rls_ddl()` in `backend/app/database/rls.py` to generate base `PERMISSIVE` policies (`_base_access_policy`) alongside `RESTRICTIVE` tenant isolation policies (`_tenant_isolation_policy`).
   - Replaced static `information_schema.columns` checks in `TENANT_INDIRECT` with dynamic parent column evaluation (`parent.farm_id`, `parent.id`, and `parent.user_id`).
4. **Isolated Neon Staging Branch Specification & Tooling (WP-04 & WP-05):**
   - Enforced strict authorization gate: `OWNER_APPROVAL_STATUS = PENDING`. No remote branch creation was performed without explicit owner consent.
   - Authored `scripts/neon_staging_branch_spec.py` and `scripts/verify_staging_rls.py` with automatic rejection of production hosts (`ep-muddy-mode-a1nd6rrb...`).
   - Retained `D2_IMPLEMENTATION_STATUS = PARTIALLY_IMPLEMENTED` awaiting staging database branch execution.
5. **Rate-Limiting HTTP Status Semantics Reverification (WP-07):**
   - Reconciled HTTP 429 vs. HTTP 503 semantics:
     - HTTP 429 Too Many Requests: Exceeded quota limit.
     - HTTP 503 Service Unavailable: Redis dependency failure on fail-closed authentication routes.
   - Added `test_auth_login_quota_exceeded_returns_http_429` in `backend/tests/test_auth.py`, proving both conditions pass at the live HTTP route layer.
6. **AI Provider Fallback Classification & Grounding (WP-08):**
   - Formally reclassified Groq fallback chain as `SAME_PROVIDER_MULTI_MODEL_FALLBACK` (`qwen/qwen3.8-27b` -> `llama-3.3-70b-versatile` -> `llama-3.1-8b-instant`).
   - Verified that fallback routes directly to deterministic PJTSAU agronomic vector advisory data (`PJTSAU_GROUNDED_RAG`) with strict citation retention.
7. **Global Risk Register Reconciliation (WP-11):**
   - Resolved historical drift across Phase 01–04 risk identifiers by introducing canonical descriptive IDs (`DB-RLS-01`, `AUTH-RATE-01`, `AI-FALLBACK-01`, etc.).
   - Reconciled satellite provider architecture: Element 84 Earth Search is primary STAC, Microsoft Planetary Computer is fallback; Copernicus CDSE OAuth dependency was permanently eliminated.
8. **Automated Test Accounting (WP-14):**
   - Expanded physical test baseline to **289 physical automated tests** (182 backend, 55 ML, 9 vision, 43 frontend). 100% passing.

---

## 2. Status Flag Manifest

```ini
OWNER_APPROVAL_STATUS = PENDING
SENDER_IDENTITY_STATUS = PENDING_OWNER_INPUT
INSTITUTIONAL_EMAILS_SENT = FALSE
LIVE_STAGING_DEPLOYMENT_TRIGGERED = FALSE
FARMER_RECRUITMENT_STARTED = FALSE
FARMER_DATA_COLLECTION_STARTED = FALSE
FIELD_PILOT_STATUS = NOT_AUTHORIZED
DPDP_COMPLIANCE_CERTIFICATION = NOT_CLAIMED
D2_IMPLEMENTATION_STATUS = PARTIALLY_IMPLEMENTED
D3_STATUS = INDEPENDENTLY_VERIFIED
D4_STATUS = INDEPENDENTLY_VERIFIED_CODE_LEVEL
D6_STATUS = INDEPENDENTLY_VERIFIED
TOTAL_PHYSICAL_TESTS = 289
TOTAL_PASS_RATE = 100%
```
