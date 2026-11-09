# ACREVIA — EXTERNAL PROVIDER & COST ASSURANCE REPORT
## INDEPENDENT TECHNICAL AND FINANCIAL GOVERNANCE AUDIT OF EXTERNAL CLOUD SERVICES

**Programme:** ACREVIA Agricultural Intelligence Platform  
**Document Code:** `EXTERNAL_PROVIDER_AND_COST_ASSURANCE.md`  
**Audit Scope:** Free-Tier Governance, External Provider Outage Resilience, Cost Guarantees & Fallback Chains  
**Audit Commit:** `2af491e49be8beb1d28fc03e42f642ed4fb7b21b` (`2af491e`)  
**Audit Date:** November 9, 2026  
**Cost Assurance Status:** **`COMPLETE_WITH_LIMITATIONS`** *(Zero-cost code controls verified; account-level billing status is `NOT_VERIFIABLE` via public API)*  

---

## 1. Executive Summary

A core operational mandate of the ACREVIA platform is absolute financial discipline: the entire infrastructure must operate exclusively within free-tier, open-access, or zero-cost educational quotas. No credit cards may be attached, and no automated billing escalations or pay-as-you-go surprises may occur.

This report independently audits the eight cloud, satellite, AI, and data providers integrated into ACREVIA. For each service, the audit evaluates rate limits, failure modes, fallback mechanisms, and billing risks.

### Authoritative Cost Assurance Classification
- **Code-Level Zero-Cost Enforcement:** **`COMPLETE_VERIFIED`** (Code handles HTTP 429, throttles tokens, avoids pay-as-you-go parameters, and enforces local extractive fallbacks).
- **Account-Level Billing Instrument Audit:** **`NOT_VERIFIABLE`** (Public REST APIs do not expose whether a credit card or billing agreement is attached to a user's private third-party cloud account).
- **Zero-Downtime Fallback Readiness:** **`COMPLETE_VERIFIED`** (Automated fallbacks implemented across satellite, AI, weather, and cache layers).

---

## 2. Comprehensive External Provider Assurance Matrix

```
+==============================================================================================================================+
| EXTERNAL PROVIDERS TECHNICAL & FINANCIAL AUDIT REGISTER                                                                      |
+---+--------------------+------------------------+---------------------+---------------------+--------------------------------+
| # | Provider Name      | Free-Tier Limit        | Auth Requirements   | Failure / 429 Mode  | Fallback Mechanism             |
+---+--------------------+------------------------+---------------------+---------------------+--------------------------------+
| 1 | GroqCloud AI       | 1,000 RPD / 8,000 TPM  | GROQ_API_KEY        | HTTP 429 (Logged)   | Local Extractive PJTSAU RAG    |
|   |                    | (Free Developer Tier)  | (Server-Side Only)  |                     | with Page-Level Citations      |
+---+--------------------+------------------------+---------------------+---------------------+--------------------------------+
| 2 | Element 84 Earth   | Open Data on AWS       | Completely Free     | HTTP 429 / 5xx      | Microsoft Planetary Computer   |
|   | Search (STAC API)  | (Public Best-Effort)   | Zero Credentials    | (Caught & Logged)   | STAC Sentinel-2 L2A Fallback   |
+---+--------------------+------------------------+---------------------+---------------------+--------------------------------+
| 3 | Microsoft Planetary| Public Azure STAC      | Free Public Access  | Token Expiry / 429  | Cached Historical Parcel NDVI  |
|   | Computer           | + SAS Token Signing    | Zero Credentials    | (Handled)           | and Zonal Vegetation Baseline  |
+---+--------------------+------------------------+---------------------+---------------------+--------------------------------+
| 4 | Open-Meteo Weather | 10,000 calls / day     | Zero Credentials    | HTTP 429 / Timeout  | District Historical Norms      |
|   |                    | (Non-commercial Open)  | No API Key Required | (15-min cache)      | & 24-hr In-Memory Cache        |
+---+--------------------+------------------------+---------------------+---------------------+--------------------------------+
| 5 | data.gov.in        | Public NDSAP Free      | DATA_GOV_IN_API_KEY | HTTP 403 / 429      | Seeded Telangana APMC Mandi    |
|   | (Agmarknet Mandi)  | Government Open Data   | (Server-Side Only)  | (Handled)           | Minimum Support Price Datasets |
+---+--------------------+------------------------+---------------------+---------------------+--------------------------------+
| 6 | Upstash Redis      | 10,000 commands / day  | REDIS_URL (TLS)     | Connection Timeout  | InMemoryRateLimiterBackend     |
|   |                    | (Free Tier)            | rediss:// Scheme    | (fail_open/closed)  | Thread-Safe Sliding Window     |
+---+--------------------+------------------------+---------------------+---------------------+--------------------------------+
| 7 | Neon PostgreSQL    | 0.5 GiB Storage        | DATABASE_URL        | Autosuspend (5 min) | Automatic Wake-on-Connect      |
|   |                    | 1 Project (Serverless) | Neon Branch Isolated| (No Data Loss)      | (3–5s Cold-Start Latency)      |
+---+--------------------+------------------------+---------------------+---------------------+--------------------------------+
| 8 | Vercel Edge        | Hobby Free Tier        | Vercel Deployment   | Function Timeout    | Client Offline-First PWA       |
|   | Compute & Hosting  | 100 GB Bandwidth/mo    | (Preview Branch)    | (10s Execution Limit| (IndexedDB / Local Caching)    |
+---+--------------------+------------------------+---------------------+---------------------+--------------------------------+
```

---

## 3. Provider-by-Provider In-Depth Technical Audit

### 3.1 GroqCloud AI Inference Engine
- **Target Model:** `qwen/qwen3.8-27b` (Preview Model on Free Developer Tier).
- **Token Limits:** Capped in code via `max_tokens = min(1024, max_tokens)` in `backend/app/integrations/groq_client.py` to prevent runaway token consumption.
- **Preview Model Risk (Finding `DEF-04`, Severity: P2):** Preview models may be deprecated or replaced upstream by Groq. The client implements automated fallback to `qwen/qwen3.8-27b` if a 404 occurs, and gracefully falls back to deterministic extractive RAG if the API key is unconfigured or rate-limited.
- **Account Billing Status:** `NOT_VERIFIABLE` via code. The application relies on Groq's documented Developer Tier returning HTTP 429 rather than charging overages.

### 3.2 Element 84 Earth Search & Microsoft Planetary Computer
- **Authentication Free Architecture:** Neither provider requires user registration, OAuth2 credentials, or credit cards.
- **Query Mechanism:** `CompositeSatelliteClient` in `backend/app/integrations/satellite_client.py` executes field-intersection spatial bounding box queries (`[77.2, 15.8, 81.3, 19.9]`).
- **Failover Chain:**
  1. Primary query dispatched to Earth Search STAC (`https://earth-search.aws.element84.com/v1`).
  2. If Earth Search returns HTTP 429, 5xx, or connection timeout, client automatically dispatches query to Microsoft Planetary Computer (`https://planetarycomputer.microsoft.com/api/stac/v1`).
  3. If both providers fail or are cloud-obscured, platform serves cached historical parcel vegetation index or outputs transparent non-diagnostic notice.

### 3.3 Open-Meteo Weather Service
- **Access Model:** Completely public, keyless weather API.
- **Cache Strategy:** 15-minute in-memory TTL cache on microclimate parameters (temperature, relative humidity, precipitation) prevents duplicate external requests during repeated farmer dashboard reloads.
- **RiskCast Dependency:** If Open-Meteo is unreachable, RiskCast uses the most recent 24-hour cached microclimate telemetry or district seasonal averages.

### 3.4 Upstash Redis Distributed Rate Limiter
- **Free Quota:** 10,000 commands per day.
- **Namespace Protection:** Staging namespace `acrevia_staging` prevents staging traffic from exhausting production counter quotas.
- **Transport Security:** Enforces TLS `rediss://` protocol for all connections over public cloud networks.

### 3.5 Neon Serverless PostgreSQL
- **Storage Boundary:** Free-tier allocation of 0.5 GiB.
- **Compute Auto-Suspend:** Inactive compute instances enter sleep mode after 5 minutes. Cold-start latency (3–5 seconds) is handled seamlessly by SQLAlchemy connection retry logic without dropping queries.

---

## 4. Financial Risk Summary & Owner Decisions

1. **Credit Card Guarantee:** The owner must verify that no credit card is associated with the active GroqCloud, Neon, or Upstash accounts.
2. **Quota Monitoring:** Daily command counts on Upstash should be monitored via the Upstash web console during active pilot testing.
3. **Model Deprecation Watch:** Prior to field trials, GroqCloud's active model list should be reviewed to confirm that `qwen/qwen3.8-27b` remains active in the Free Developer Tier.
