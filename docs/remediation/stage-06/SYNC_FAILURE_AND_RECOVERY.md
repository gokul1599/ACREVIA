# ACREVIA — OFFLINE SYNC FAILURE MODES & RECOVERY PROTOCOLS
## TRANSIENT ERRORS, CONFLICT RESOLUTION & RECOVERY STRATEGIES
**Document:** `SYNC_FAILURE_AND_RECOVERY.md`  
**Classification:** Operational Reliability Protocol  
**Date:** 2026-11-08  
**Component:** `frontend/lib/offline/queue.ts`  
**Status:** `COMPLETE_VERIFIED`  

---

## 1. FAILURE CLASSIFICATION & MITIGATION

Smallholder farming environments in Telangana experience erratic 2G/3G connectivity, intermittent tower blackouts, and low-bandwidth connections. The sync engine classifies failures into three operational categories:

| Category | Typical Scenarios | Engine Action | User Impact |
|---|---|---|---|
| **Transient Network Errors** | TCP reset, connection timeout, DNS failure, 502/503/504 Bad Gateway | Transition to `RETRY_PENDING`; schedule exponential backoff with jitter | Background retry without disturbing farmer |
| **Domain Concurrency Conflicts** | HTTP 409 Conflict, plot/farm deleted remotely, observation timestamp collision | Transition to `CONFLICT`; save snapshot in `conflict_records` | Non-destructive alert badge; farmer prompted to review |
| **Terminal Validation Errors** | HTTP 400 Bad Request, 422 Unprocessable Entity, missing required coordinates | Transition to `FAILED`; retain record in IndexedDB with error explanation | Error badge displayed in dashboard; edit action provided |

---

## 2. EXPONENTIAL BACKOFF WITH JITTER ALGORITHM

To prevent "thundering herd" problems when cell towers resume service in rural villages, the retry schedule applies truncated exponential backoff with uniform random jitter:

$$t_{\text{backoff}} = \min\left(t_{\text{max}}, t_{\text{base}} \times 2^{\text{retry\_count}}\right) + \text{random}(0, 500\text{ ms})$$

- $t_{\text{base}} = 1000\text{ ms}$ ($1\text{ s}$)
- $t_{\text{max}} = 30000\text{ ms}$ ($30\text{ s}$)
- **Retry 0:** $1000\text{ ms} + \text{jitter} \implies [1.0\text{ s}, 1.5\text{ s}]$
- **Retry 1:** $2000\text{ ms} + \text{jitter} \implies [2.0\text{ s}, 2.5\text{ s}]$
- **Retry 2:** $4000\text{ ms} + \text{jitter} \implies [4.0\text{ s}, 4.5\text{ s}]$
- **Retry 5+:** Capped at $30\text{ s} + \text{jitter} \implies [30.0\text{ s}, 30.5\text{ s}]$

Verified in unit test: `OfflineQueue - exponential backoff with jitter calculation`.

---

## 3. CONFLICT PRESERVATION & DATA LOSS PREVENTION
When the server rejects an observation with `HTTP 409 Conflict`:
1. The engine **never overwrites** the server record.
2. The engine **never drops** the farmer's offline draft.
3. The local draft is serialized into `conflict_records` with timestamp, local values, and server rejection reason.
4. The draft remains visible in the farmer's review tray with an explicit "Needs Attention" badge.
