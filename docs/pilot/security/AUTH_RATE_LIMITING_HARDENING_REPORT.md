# ACREVIA — AUTHENTICATION RATE LIMITING HARDENING REPORT

**Report Identifier:** SEC-RATE-2026-11-09  
**Target Vulnerability:** D3 (Fail-Open Rate Limiting on Authentication Endpoints)  
**Remediation Classification:** `D3_STATUS = RESOLVED`  
**Verification Date:** November 9, 2026  

---

## 1. Vulnerability Analysis & Risk Context

Prior to Phase 03 remediation, the distributed rate limiter backend (`RedisRateLimiterBackend` in `backend/app/core/rate_limit.py`) caught all Redis exceptions (unreachable host, DNS resolution error, timeouts, authentication errors) and silently fell back to an in-memory sliding window rate limiter.

While acceptable for low-risk public endpoints, this default fail-open behavior posed a critical risk on sensitive authentication routes (`/api/v1/auth/login` and `/api/v1/auth/register`):
1. In multi-instance or serverless staging deployments, each instance maintained an independent in-memory window.
2. An attacker could exploit an Upstash Redis outage or trigger connection saturation to bypass distributed rate limits and conduct credential brute-forcing against farmer or expert accounts.

---

## 2. Hardened Architecture & Implementation

### A. Dual Fail-Mode Architecture
The rate limiter now explicitly supports two operational modes:
- `fail_mode="fail_closed"` (Strict security): Required for `/auth/login` and `/auth/register`. If Redis is unreachable, the request is blocked, returning HTTP 503 Service Unavailable with a standard `Retry-After: 60` header.
- `fail_mode="fail_open"` (Availability prioritized): Maintained for public read-only endpoints (e.g., market intelligence, public advisory, weather forecasts). Falls back to in-memory window during Redis disruptions.

### B. Exception Propagation & Sanitization
In `backend/app/core/rate_limit.py` and `backend/app/core/exceptions.py`:
- `RateLimitResult` was extended with `service_unavailable: bool = False`.
- In `rate_limit` FastAPI dependency, when `result.service_unavailable` is detected, it raises `ServiceUnavailableException(service_name="RateLimiter", message="Authentication rate limiting service temporarily unavailable. Please retry shortly.", retry_after=60)`.
- `AcreviaException` propagates `headers={"Retry-After": "60"}` to the top-level exception handler in `backend/app/main.py`.
- **Zero Information Leakage:** Redis connection strings, hostnames, passwords, and internal tracebacks are strictly excluded from API error envelopes.

### C. Explicit Route Protection
In `backend/app/api/v1/endpoints/auth.py`:
- `/register`: `rate_limit(max_requests=5, window_seconds=60, endpoint_group="auth_register", fail_mode="fail_closed")`
- `/login`: `rate_limit(max_requests=5, window_seconds=60, endpoint_group="auth_login", fail_mode="fail_closed")`

---

## 3. Automated Test Verification

The hardened behavior was validated through 14 automated tests:

### Unit Tests (`backend/tests/test_distributed_rate_limiter.py`):
1. `test_redis_unreachable_fail_open_allows_request`: Verifies in-memory fallback for non-auth endpoints.
2. `test_redis_unreachable_fail_closed_denies_request`: Verifies `service_unavailable=True` and `allowed=False`.
3. `test_redis_timeout_fail_closed_denies_request`: Verifies timeout handling under network delay.
4. `test_redis_auth_error_fail_closed_denies_request`: Verifies behavior during bad credentials/rotation.
5. `test_redis_tls_error_fail_closed_denies_request`: Verifies behavior during certificate errors.
6. `test_redis_recovery_restores_normal_operation`: Verifies automatic recovery when Redis reconnects.
7. `test_fail_closed_exception_has_retry_after_and_503`: Confirms HTTP 503 status and `Retry-After` header.
8. `test_fail_closed_response_does_not_leak_secrets`: Confirms zero secret or host string leakage.
9. `test_health_endpoint_not_impacted_by_fail_closed_auth`: Confirms health check isolation.
10. + 3 existing sliding window and quota limit unit tests.

### Integration Tests (`backend/tests/test_auth.py`):
1. `test_auth_login_fail_closed_when_redis_unreachable`: Simulates Redis failure during POST `/api/v1/auth/login` and asserts HTTP 503 with `Retry-After`.
2. `test_auth_register_fail_closed_when_redis_unreachable`: Simulates Redis failure during POST `/api/v1/auth/register` and asserts HTTP 503 with `Retry-After`.

All tests executed and passed cleanly with exit code 0.

---

## 4. Remediation Sign-Off

The fail-closed authentication rate-limiting mechanism is production-ready and fully verified. Risk item **D3** is formally marked **RESOLVED**.
