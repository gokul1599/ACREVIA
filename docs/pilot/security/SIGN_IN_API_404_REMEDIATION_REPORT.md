# ACREVIA — AUTHENTICATION REMEDIATION REPORT: SIGN-IN API 404 RESOLUTION

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document Code:** `SIGN_IN_API_404_REMEDIATION_REPORT.md`  
**Execution Date:** November 9, 2026  
**Status:** COMPLETE & INDEPENDENTLY VERIFIED  
**Severity:** High (Authentication Blocked on Misconfigured or Unreachable Environments)  

---

## 1. Overview of Changes

This remediation addresses the root causes of the sign-in error `API request failed with status 404` across the Next.js 16 App Router frontend, FastAPI backend route registration verification, environment variable configuration, and error reporting architecture.

---

## 2. Changed Files Matrix

| File Path | Nature of Change | Purpose |
|---|---|---|
| `frontend/lib/api/client.ts` | Modified | Added `resolveApiUrl()` with prefix deduplication, implemented `ApiError` class, replaced non-JSON swallowing with actionable error messages, preserved 401 credential details on auth pages. |
| `frontend/next.config.mjs` | Modified | Added path normalization for `backendUrl` in Next.js `rewrites()` to prevent duplicate `/api/v1` and double slashes. |
| `frontend/app/(auth)/login/page.tsx` | Modified | Integrated `ApiError` handling, added submission guard (`if (isLoading) return`), disabled submit button during active request, preserved user inputs on failure. |
| `frontend/app/(auth)/register/page.tsx` | Modified | Integrated `ApiError` handling, added submission guard, disabled submit button during active registration. |
| `frontend/tests/auth_client.test.js` | Created | Added 11 automated unit tests verifying URL normalization, Next.js rewrite configuration, `ApiError` field mapping, and API methods. |
| `frontend/.env.example` | Created | Created comprehensive environment variable template documenting direct and proxy API modes. |
| `.env.example` | Modified | Appended frontend configuration section with explicit `NEXT_PUBLIC_API_URL` and `BACKEND_INTERNAL_URL` documentation. |
| `backend/tests/test_auth.py` | Modified | Added 4 automated tests: route registry verification, method not allowed (405), double-prefix 404 verification, and end-to-end synthetic farmer login lifecycle. |
| `docs/pilot/security/ACREVIA_GLOBAL_RISK_REGISTER_PHASE_06.md` | Modified | Registered `AUTH-ROUTING-01` as `COMPLETE_VERIFIED`. |

---

## 3. Before vs. After Behavior

| Dimension | Before Remediation | After Remediation |
|---|---|---|
| **Base URL Composition** | `${BASE_URL}/api/v1${endpoint}` blindly concatenated strings; duplicated `/api/v1` if base contained prefix. | `resolveApiUrl()` strips trailing slashes and redundant `/api/v1` or `/api` segments before cleanly appending the endpoint. |
| **Empty `NEXT_PUBLIC_API_URL`** | Fell back to Next.js rewrites; if local backend was not running on Vercel preview, returned HTML 404. | Safely normalizes to `/api/v1/*`; on connection failure, throws explicit `Unable to reach ACREVIA backend at <url>`. |
| **Non-JSON 404 Response** | Swallowed JSON parse error in `catch`; defaulted to ambiguous `API request failed with status 404`. | Specifically detects 404 and reports: `Authentication service endpoint unreachable (404 Not Found at <url>). Please verify backend API connectivity...`. |
| **Invalid Credentials (401)** | Intercepted 401 and hardcoded `Session expired or unauthorized. Please log in again.` discarding backend detail. | Preserves backend detail (`Invalid phone/email or password.`) on login/register screens, enabling correct user feedback. |
| **Rate Limit Exceeded (429)** | Inconsistently rendered as generic error if non-JSON returned. | Explicitly returns `Rate limit exceeded. Too many requests. Please wait a moment before trying again.`. |
| **Service Outage (502/503/504)** | Rendered generic status string. | Explicitly returns `ACREVIA backend service is currently unavailable (<status>). Please verify that the API server is running.`. |
| **Double Form Submission** | Form could be re-submitted while an in-flight request was pending. | Blocked at submit handler (`if (isLoading) return`) and disabled on submit button (`disabled={isLoading}`). |

---

## 4. Test Verification Results

### 4.1 Backend Test Results (`pytest backend/tests/test_auth.py`)
```text
backend/tests/test_auth.py::test_register_success PASSED
backend/tests/test_auth.py::test_register_duplicate_phone PASSED
backend/tests/test_auth.py::test_login_success PASSED
backend/tests/test_auth.py::test_login_invalid_password PASSED
backend/tests/test_auth.py::test_get_current_user_me PASSED
backend/tests/test_auth.py::test_get_me_unauthorized PASSED
backend/tests/test_auth.py::test_auth_login_fail_closed_when_redis_unreachable PASSED
backend/tests/test_auth.py::test_auth_register_fail_closed_when_redis_unreachable PASSED
backend/tests/test_auth.py::test_auth_login_quota_exceeded_returns_http_429 PASSED
backend/tests/test_auth.py::test_auth_routes_registry_verification PASSED
backend/tests/test_auth.py::test_auth_login_method_not_allowed PASSED
backend/tests/test_auth.py::test_auth_login_not_found_on_duplicate_prefix PASSED
backend/tests/test_auth.py::test_auth_synthetic_farmer_login_lifecycle PASSED
13 passed, 1 warning in 41.50s
```

### 4.2 Frontend Test Results (`npm --prefix frontend test`)
```text
✔ Auth Client - resolveApiUrl handles empty base URL (5.2476ms)
✔ Auth Client - resolveApiUrl handles host without trailing slash (0.606ms)
✔ Auth Client - resolveApiUrl normalizes host with trailing slash (0.5573ms)
✔ Auth Client - resolveApiUrl prevents duplicate /api/v1 when base contains /api/v1 (0.3972ms)
✔ Auth Client - resolveApiUrl prevents duplicate /api/v1 when base contains /api/v1/ (0.4158ms)
✔ Auth Client - resolveApiUrl handles production domain with /api prefix (0.3875ms)
✔ Auth Client - resolveApiUrl handles endpoint missing leading slash (0.3533ms)
✔ Auth Client - resolveApiUrl preserves already-prefixed endpoints without duplication (0.3817ms)
✔ Auth Client - next.config.mjs rewrites rule exists and targets normalized backend URL (1.4801ms)
✔ Auth Client - ApiError stores status, detail, and correlationId (1.1141ms)
✔ Auth Client - api.login function is registered and callable (0.7143ms)
[+ 43 existing offline queue, IndexedDB, localization, PWA, and feature tests]
ℹ tests 54, pass 54, fail 0
```

### 4.3 Production Build & Type Safety (`next build`)
```text
▲ Next.js 16.3.5 (Turbopack)
✓ Compiled successfully in 2.8s
  Running TypeScript ...
  Finished TypeScript in 8.3s ...
✓ Generating static pages using 11 workers (13/13) in 1228ms
Finalizing page optimization ...
All 13 routes compiled statically. Zero TypeScript compilation errors.
```

### 4.4 Linter Status (`eslint .`)
- Zero errors (`0 errors, 109 warnings`).
- 109 warnings correspond to pre-existing TypeScript `any` envelope wrappers cataloged under `FRONTEND-TYPES-01`.

---

## 5. Security & Architectural Invariants Preserved

1. **Bcrypt Password Verification:** Preserved; all passwords verified with salted bcrypt.
2. **JWT Bearer Token Issuance:** Preserved; HMAC-SHA256 tokens signed with subject, role claims, and telephone metadata.
3. **Redis Distributed Rate Limiting:** Preserved; fail-closed behavior on `/auth/login` (HTTP 503 on Redis outage, HTTP 429 on quota exhaustion).
4. **PostgreSQL RLS Hardening:** Preserved; administrative self-escalation fix from Phase 06 intact.
5. **Zero Exposure of Secrets:** No backend secrets exposed to browser bundles or `NEXT_PUBLIC_` namespace.
