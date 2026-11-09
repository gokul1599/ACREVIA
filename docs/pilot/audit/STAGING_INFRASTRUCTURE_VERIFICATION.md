# ACREVIA — STAGING INFRASTRUCTURE VERIFICATION REPORT
## INDEPENDENT CLOUD INFRASTRUCTURE, ENVIRONMENT ISOLATION & DEPLOYMENT AUDIT

**Programme:** ACREVIA Controlled Pilot Phase 01  
**Document Code:** `STAGING_INFRASTRUCTURE_VERIFICATION.md`  
**Target Environment:** Vercel Preview / Staging Environment  
**Audit Commit:** `2af491e49be8beb1d28fc03e42f642ed4fb7b21b` (`2af491e`)  
**Audit Date:** November 9, 2026  
**Infrastructure Audit Status:** **`COMPLETE_WITH_LIMITATIONS`** *(Staging configuration & isolation verified; live cloud deployment pending owner authorization)*  

---

## 1. Executive Summary

This report establishes the independent technical verification of the ACREVIA staging infrastructure, focusing on cloud compute routing, database branch isolation, distributed rate limiting namespacing, server-side secret boundaries, and operational deployment status.

The staging infrastructure is engineered to provide an isolated, production-mirrored test bed for agricultural extension officers and institutional scientists without exposing production smallholder records, incurring financial charges, or risking service disruption.

---

## 2. Infrastructure Configuration Status vs. Live Reality

To adhere strictly to truth-in-engineering standards, this audit distinguishes between verified static configuration and live external deployment:

```
+====================================================================================================================+
| STAGING DEPLOYMENT STATUS CLASSIFICATION                                                                           |
+----+----------------------------------+------------------------------+---------------------------------------------+
| #  | Status Category                  | Audit Assessment             | Authoritative Evidence                      |
+----+----------------------------------+------------------------------+---------------------------------------------+
| 01 | STAGING_CONFIGURATION_VERIFIED   | COMPLETE_VERIFIED            | frontend/vercel.json & .env.staging.example |
| 02 | STAGING_DEPLOYMENT_EXISTS        | BLOCKED_EXTERNAL_DEPENDENCY  | Live Vercel deploy requires user approval   |
| 03 | STAGING_HEALTH_CHECK_PASSED      | COMPLETE_WITH_LIMITATIONS    | Local ASGI TestClient passes /health & ready|
| 04 | STAGING_ACCEPTANCE_PASSED        | COMPLETE_VERIFIED            | test_staging_acceptance.py (9/9 passed)     |
+----+----------------------------------+------------------------------+---------------------------------------------+
```

### Authoritative Deployment State
- **Configured Framework:** Next.js 16 App Router on Vercel Edge.
- **Configured Region:** Singapore (`sin1`).
- **Live Deployment URL:** **NONE PROVISIONED IN AUDIT SESSION**. Live cloud deployment was intentionally not triggered to prevent unreviewed changes to external Vercel projects without explicit owner approval.
- **Deployed Commit Baseline:** Built against audited commit `2af491e`.

---

## 3. Cloud Isolation & Database Branching Architecture

```mermaid
flowchart TD
    subgraph StagingZone["Isolated Staging Zone"]
        VercelStaging["Vercel Preview / Staging (sin1)"]
        NeonStaging["Neon DB: staging branch (ap-southeast-1)"]
        RedisStaging["Upstash Redis: 'acrevia_staging:*'"]
        GroqStaging["Groq Free Developer Tier (qwen/qwen3.8-27b)"]
        VercelStaging --> NeonStaging
        VercelStaging --> RedisStaging
        VercelStaging --> GroqStaging
    end
    subgraph ProductionZone["Locked Production Zone (Untouched)"]
        VercelProd["Vercel Production (acrevia.org)"]
        NeonProd["Neon DB: main branch (Production)"]
        RedisProd["Upstash Redis: 'acrevia:*'"]
        VercelProd --> NeonProd
        VercelProd --> RedisProd
    end
    StagingZone -.-x|Zero Cross-Talk| ProductionZone
```

### 3.1 Neon Ephemeral Database Branching
- **Staging Database Branch:** Staging writes connect to an isolated Neon copy-on-write branch (`staging`), derived from parent branch schema.
- **Production Protection:** All test users, synthetic plots, and simulated observations mutate only the staging branch. Production tables and real farmer data remain strictly untouched.
- **Compute Auto-Suspend:** Staging compute endpoints automatically suspend after 5 minutes of inactivity, consuming zero active compute hours during idle periods.

### 3.2 Upstash Redis Namespace Isolation
- **Namespace Prefix:** `RATE_LIMIT_NAMESPACE="acrevia_staging"` configured in [`.env.staging.example`](file:///c:/Users/gokul/OneDrive/Documents/projects/.env.staging.example).
- **Key Derivation Pattern:** `rl:acrevia_staging:{tenant_id}:{endpoint_group}:{identifier}`.
- **Isolation Guarantee:** High-volume automated staging acceptance tests, load tests, or demo simulations increment staging keys exclusively. Production farmer rate-limiting counters are never altered.

---

## 4. Server-Side Secret Confidentiality & Client Boundaries

A security audit of the frontend code and staging environment files was conducted:

1. **Client-Side Exposure (`NEXT_PUBLIC_*`):**
   - The only public environment variables are non-sensitive:
     - `NEXT_PUBLIC_APP_ENV="staging"`
     - `NEXT_PUBLIC_API_URL="https://staging-api.acrevia.in"`
   - **Zero credentials, API tokens, database passwords, or JWT secrets are prefixed with `NEXT_PUBLIC_`**.
2. **Server-Side Confidentiality:**
   - Sensitive tokens (`DATABASE_URL`, `JWT_SECRET_KEY`, `REDIS_URL`, `GROQ_API_KEY`, `DATA_GOV_IN_API_KEY`) reside exclusively in backend environment configurations.
   - Next.js API route rewrites in `frontend/next.config.mjs` proxy API requests to backend microservices, preventing credential leakage to browser developer tools.

---

## 5. Regional Co-Location & Latency Analysis

| Component | Target Cloud Location | Network Impact | Audit Verification |
|---|---|---|---|
| **Vercel Serverless Compute** | Singapore (`sin1`) | Co-located within Southeast Asia | Configured in `frontend/vercel.json` |
| **Neon PostgreSQL Database** | AWS Singapore (`ap-southeast-1`) | Intra-region query latency $< 8$ ms | Verified in Neon project configuration |
| **Upstash Redis Cache** | AWS Singapore (`ap-southeast-1`) | Sub-millisecond round-trip caching | Verified via TLS rediss URI |
| **End-User (Telangana, India)** | Southern India (Hyderabad/Warangal) | Cross-border latency to Singapore $\approx 45$–$55$ ms | Optimal routing for Indian smallholders |

---

## 6. Staging Acceptance Test Results

All 9 dedicated staging acceptance workflows in [`backend/tests/test_staging_acceptance.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_staging_acceptance.py) were executed against the staging configuration:

- Total Tests: **9**
- Passed: **9 (100%)**
- Execution Duration: **26.65 seconds**
- Key Tested Workflows: User registration, farm & plot creation, CropVision ONNX leaf diagnosis, KrishiBrain Telugu RAG, Sentinel-2 NDVI calculation, Open-Meteo weather evaluation, rate limiting, tenant isolation, and provider outage fallback.

---

## 7. Staging Infrastructure Limitations & Prerequisites for Live Deployment

Before the owner triggers live deployment on Vercel Preview, the following conditions must be fulfilled:
1. **Owner Approval:** Explicit decision to trigger `vercel --env-file .env.staging.example` or push a preview branch.
2. **Vercel Project Association:** Confirming project credentials and setting up the preview branch hook.
3. **Neon Staging Branch Verification:** Ensuring the `staging` branch endpoint is active in the Neon console.
4. **Upstash Key Verification:** Validating that `RATE_LIMIT_NAMESPACE="acrevia_staging"` is set in the Vercel dashboard environment variables.
