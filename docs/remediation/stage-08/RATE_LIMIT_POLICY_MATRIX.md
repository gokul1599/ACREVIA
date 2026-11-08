# ACREVIA Production Rate Limiting Policy Matrix
## Stage 08 Remediation — Distributed Quotas & Endpoint Protection
**Target Stage:** Stage 08 — Production Hardening & Security Engineering  
**Task ID:** TASK-S08-02  
**Implementation File:** `backend/app/core/rate_limit.py`  
**Storage Tier:** Redis (Sorted Sets sliding-window) with In-Memory thread-safe fallback  

---

## 1. Executive Summary

To safeguard the ACREVIA platform against volumetric denial of service, resource exhaustion, brute force credential guessing, and excessive LLM/ML inference compute costs, ACREVIA enforces an atomic sliding-window rate limiting policy.

Unlike naive fixed-window counters that permit $2 \times$ bursts across boundary transitions, ACREVIA's sliding-window algorithm evaluates requests continuously over the trailing window ($T_{\text{window}}$) with millisecond granularity using Redis Sorted Sets (`ZSET`).

---

## 2. Policy Matrix

The following quota tiers are enforced across all public and authenticated endpoints:

| Endpoint Group | Quota (`max_requests`) | Window (`window_seconds`) | Target Endpoints | Primary Protection Objective |
| :--- | :---: | :---: | :--- | :--- |
| **Authentication (`auth`)** | **5** | **60 s** | `/api/v1/auth/login`, `/api/v1/auth/register`, `/api/v1/auth/refresh` | Prevents credential stuffing, brute-force dictionary attacks, and phone verification abuse. |
| **Vision & ML Inference (`ai`)** | **15** | **60 s** | `/api/v1/vision/predict`, `/api/v1/inference/*` | Bounds CPU/memory spikes on ONNX Runtime shared MobileNetV3 multi-crop backbone. |
| **KrishiBrain RAG (`rag`)** | **20** | **60 s** | `/api/v1/chat/*`, `/api/v1/knowledge/query` | Bounds dense vector pgvector search load and external embedding/LLM API consumption. |
| **Media & File Uploads (`upload`)** | **10** | **60 s** | `/api/v1/observations/upload`, `/api/v1/journal/media` | Guards disk storage, bandwidth, and asynchronous thumbnail generation pipelines. |
| **Farmer Operations (`default`)** | **120** | **60 s** | `/api/v1/journal/*`, `/api/v1/weather/*`, `/api/v1/twin/*` | Generous baseline permitting smooth interactive PWA synchronization and browsing. |
| **Supervisor & Admin (`admin`)** | **240** | **60 s** | `/api/v1/admin/*`, `/api/v1/pilot/reports` | High-throughput capacity for extension officers and KVK agronomists reviewing cohort records. |

---

## 3. Sliding-Window Algorithm & Redis Data Structure

Every endpoint group is tracked in Redis using a Sorted Set:
- **Redis Key:** `rl:{namespace}:{tenant_id}:{group}:{client_identifier}`
  - Example: `rl:acrevia:warangal-kvk:ai:usr_8923a1`
  - Unauthenticated Example: `rl:acrevia:public:auth:anon:4e8c3b9a102f`
- **Sorted Set Score:** Request epoch timestamp in milliseconds (`float(time.time() * 1000)`).
- **Sorted Set Member:** Unique UUIDv4 token for each discrete request.

### Atomic Redis Pipeline Execution
```python
pipe = redis.pipeline()
# 1. Purge all requests older than the sliding window boundary
pipe.zremrangebyscore(key, 0, cutoff_timestamp_ms)
# 2. Count active requests within the window
pipe.zcard(key)
# 3. Conditionally record new request if count < limit
# 4. Set key TTL = window_seconds + 5s (prevents key accumulation)
pipe.expire(key, window_seconds + 5)
```

---

## 4. Privacy & DPDP 2023 Compliance

Under the Digital Personal Data Protection (DPDP) Act 2023 of India, IP addresses constitute personal identifiers. 
- In unauthenticated contexts, ACREVIA never persists raw IP addresses in Redis or in-memory caches.
- Unauthenticated client IPs are hashed using SHA-256 with a tenant-isolated salt, and truncated to 12 hex characters:
  $$\text{Client Identifier} = \text{"anon:"} + \text{SHA256}(\text{Salt} \parallel \text{IP})[:12]$$
- Key TTLs strictly purge rate limit tracking data within 65 seconds of inactivity.

---

## 5. Client Response Protocol & HTTP Headers

When a request is processed under rate limiting, RFC 6585 / standard HTTP headers are attached to the response:

| Header | Example | Meaning |
| :--- | :--- | :--- |
| `X-RateLimit-Limit` | `15` | Total permitted requests within the rolling window. |
| `X-RateLimit-Remaining` | `14` | Permitted requests remaining in the current window. |
| `X-RateLimit-Reset` | `1731078000` | Unix epoch seconds when the oldest request rolls out of the window. |
| `Retry-After` *(on 429)* | `34` | Exact seconds client must wait before making another request. |

### Error Response Format (HTTP 429)
```json
{
  "detail": {
    "error_code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded for endpoint group 'ai'. Limit: 15 per 60s.",
    "retry_after": 34,
    "limit": 15,
    "group": "ai"
  }
}
```

---

## 6. High Availability & Fail Modes

1. **`fail_open = true` (Default Production Setting):**
   - If Redis becomes unreachable (network partition, maintenance restart), the system logs an error event and permits request processing to prevent catastrophic platform denial of service for farmers in the field.
2. **`fail_closed = false` (Critical Security Setting):**
   - In environments where strict financial or zero-trust boundaries are required, `fail_open=False` will reject requests with HTTP 503 if Redis is unavailable.
3. **In-Memory Fallback:**
   - In local development or standalone edge test harnesses, `InMemoryRateLimiterBackend` provides identical sliding-window semantics using a synchronized Python dictionary guarded by thread locks.
