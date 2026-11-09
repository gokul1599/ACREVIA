# ACREVIA — AUTHENTICATION & RATE LIMITING REVERIFICATION REPORT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Module:** Distributed Rate Limiter & Authentication Endpoints  
**Execution Date:** November 9, 2026  
**Status:** `D3_STATUS = INDEPENDENTLY_VERIFIED`

---

## 1. HTTP Status Semantics Reconciliation

Work Package 07 required reconciling the status code semantics between quota exhaustion and infrastructure dependency failure:

| Condition | Status Code | RFC / Standards Basis | System Behavior |
| :--- | :---: | :--- | :--- |
| **Quota Exceeded** | **`429 Too Many Requests`** | RFC 6585 Section 4 | Rate limit window exceeded. Returns `Retry-After` header. Does not leak account existence. |
| **Redis Outage / Timeout** | **`503 Service Unavailable`** | RFC 7231 Section 6.6.4 | Redis cluster down or TLS failed on a `fail_closed` critical authentication route (`/auth/login`, `/auth/register`). Rejects safely with `Retry-After` without exposing connection strings or cluster hostnames. |
| **Redis Outage (Public Route)** | **`200 OK` (Degraded)** | Graceful Degradation | Low-risk public routes (`fail_mode="fail_open"`) fall back to local in-memory sliding window limiter to maintain system availability. |

---

## 2. Implementation Verification

In `backend/app/core/rate_limit.py`:
- `RateLimitResult` carries `service_unavailable: bool`.
- When `result.service_unavailable == True`:
  ```python
  raise ServiceUnavailableException(
      service_name="RateLimiter",
      message="Authentication rate limiting dependency is currently unavailable. Please retry shortly.",
      retry_after=result.retry_after,
  )
  ```
  FastAPI's global handler catches `ServiceUnavailableException` and returns HTTP 503 with `Retry-After`.
- When `result.allowed == False`:
  ```python
  raise RateLimitExceededException(
      message=f"Rate limit exceeded: maximum {max_requests} requests per {window_seconds} seconds.",
      retry_after=result.retry_after,
  )
  ```
  FastAPI's global handler catches `RateLimitExceededException` and returns HTTP 429 with `Retry-After`.

---

## 3. Automated Test Evidence

Both conditions are verified by physical automated tests:
1. `backend/tests/test_distributed_rate_limiter.py`:
   - `test_fail_closed_mode_on_unreachable_redis`: Asserts `service_unavailable=True`.
   - `test_fail_closed_redis_timeout_handling`: Asserts `service_unavailable=True`.
   - `test_fail_closed_redis_auth_failure_handling`: Asserts `service_unavailable=True`.
   - `test_fail_closed_redis_tls_failure_handling`: Asserts `service_unavailable=True`.
   - `test_fail_closed_http_503_and_no_secret_leakage`: Live TestClient asserts HTTP 503 and zero password/hostname leakage.
   - `test_rate_limit_fastapi_dependency`: Live TestClient asserts HTTP 429 when quota is exceeded.
2. `backend/tests/test_auth.py`:
   - `test_auth_login_fail_closed_when_redis_unreachable`: Asserts `/api/v1/auth/login` returns HTTP 503 when Redis is down.
   - `test_auth_register_fail_closed_when_redis_unreachable`: Asserts `/api/v1/auth/register` returns HTTP 503 when Redis is down.
   - `test_auth_login_quota_exceeded_returns_http_429`: Asserts `/api/v1/auth/login` returns HTTP 429 after 5 failed attempts.
