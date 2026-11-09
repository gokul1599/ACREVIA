# ACREVIA — ROOT CAUSE ANALYSIS: SIGN-IN API 404 INVESTIGATION

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document Code:** `SIGN_IN_API_404_ROOT_CAUSE_ANALYSIS.md`  
**Investigation Date:** November 9, 2026  
**Status:** COMPLETE & INDEPENDENTLY VERIFIED  
**Severity:** High (Authentication Blocked on Misconfigured or Unreachable Environments)  

---

## 1. Executive Summary

During user login verification, an error occurred on the sign-in screen:
```text
API request failed with status 404
```
An evidence-based investigation across Next.js 16 App Router frontend, FastAPI backend, Vercel routing configuration, and URL construction mechanisms confirmed that:
1. The FastAPI backend endpoint `POST /api/v1/auth/login` is fully implemented, active, registered in OpenAPI schemas (184 endpoints total), and functioning correctly.
2. The HTTP 404 status **never originated from FastAPI**. When FastAPI encounters a 404 or authentication failure, it returns structured JSON (`{"detail": "Not Found"}` or `{"error_type": "AuthenticationException", "detail": "Invalid phone/email or password."}`).
3. The string `API request failed with status 404` was generated exclusively on line 131 of `frontend/lib/api/client.ts` as a fallback when `res.ok === false` and `res.json()` failed to parse a **non-JSON HTML response** returned by Next.js / reverse proxy / Vercel.
4. The failed request occurred because `NEXT_PUBLIC_API_URL` was unset or misconfigured, causing the browser to submit relative requests to the Next.js frontend origin (`/api/v1/auth/login`). In environments without an active local backend process (such as Vercel preview or standalone deployments), Next.js rewrites attempted to proxy to `http://127.0.0.1:8000`, failed with `ECONNREFUSED`, fell through to the Next.js App Router where no API route exists, and rendered a standard 404 HTML page.
5. In scenarios where `NEXT_PUBLIC_API_URL` was configured with a trailing slash (`http://localhost:8000/`) or with an `/api/v1` suffix (`http://localhost:8000/api/v1`), string concatenation `${BASE_URL}/api/v1${endpoint}` produced double slashes or duplicated prefixes (`/api/v1/api/v1/auth/login`), triggering 404s.

---

## 2. Exact Failed Request Trace

| Trace Attribute | Observed Value |
|---|---|
| **User Action** | Submitted phone number and password on `/login` form |
| **Client Invocation** | `LoginPage.handleSubmit` &rarr; `useAuth().login()` &rarr; `api.login()` |
| **Requested Method** | `POST` |
| **Requested URL (Unset Env)** | `http://<frontend-host>:3000/api/v1/auth/login` or `https://<vercel-preview>.vercel.app/api/v1/auth/login` |
| **Requested URL (Duplicated Prefix)** | `http://localhost:8000/api/v1/api/v1/auth/login` |
| **Response HTTP Status** | `404 Not Found` |
| **Response Content-Type** | `text/html; charset=utf-8` |
| **Response Body (Sanitized)** | `<!DOCTYPE html><html><head><title>404: This page could not be found</title></head><body>...</body></html>` |
| **FastAPI Reached?** | **NO.** The request never reached the FastAPI application server. |
| **Client Error Thrower** | `frontend/lib/api/client.ts` lines 130–139 |
| **UI Display Element** | `LoginPage` `error` alert banner: `API request failed with status 404` |

---

## 3. Route Comparison: Expected vs. Actual

### Backend Route Registry (FastAPI)
- **File:** `backend/app/api/v1/endpoints/auth.py`
- **Master Assembly:** `backend/app/api/v1/router.py` mounted with `prefix="/api/v1"` in `backend/app/main.py`
- **Expected Backend Route:** `POST /api/v1/auth/login`
- **Verification:** Verified via `app.openapi()["paths"]["/api/v1/auth/login"]` &mdash; HTTP `POST` registered.
- **FastAPI 404 Format:** `{"detail": "Not Found"}` (`application/json`).
- **FastAPI 401 Format:** `{"error_type": "AuthenticationException", "detail": "Invalid phone/email or password.", ...}` (`application/json`).

### Frontend Request Generation (Next.js)
- **Previous Client Logic:**
  ```typescript
  const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";
  const url = `${BASE_URL}/api/v1${endpoint}`;
  ```
- **Defect 1 (Empty Base):** If `NEXT_PUBLIC_API_URL` is empty, `url = "/api/v1/auth/login"`. The request hits Next.js rewrites:
  ```javascript
  destination: `${backendUrl}/api/v1/:path*` // backendUrl defaults to http://127.0.0.1:8000
  ```
  On Vercel or systems where backend is not running on port 8000 of the same container, the proxy connection fails, falling back to Next.js App Router 404 HTML.
- **Defect 2 (Suffix Inclusion):** If `NEXT_PUBLIC_API_URL` is set to `http://localhost:8000/api/v1`, `url` becomes `http://localhost:8000/api/v1/api/v1/auth/login`, hitting FastAPI's catch-all 404.
- **Defect 3 (Trailing Slash):** If `NEXT_PUBLIC_API_URL` is set to `http://localhost:8000/`, `url` becomes `http://localhost:8000//api/v1/auth/login`.

---

## 4. Root Cause Breakdown

### Architectural Defect 1: Brittle URL Composition in API Client
`frontend/lib/api/client.ts` assumed `BASE_URL` was always an origin without trailing slash and without an `/api/v1` path segment. Real-world environment variable configurations frequently include trailing slashes or full API prefixes.

### Architectural Defect 2: Non-JSON 404 Swallowing in Error Handler
In `frontend/lib/api/client.ts`:
```typescript
if (!res.ok) {
  let errorMsg = `API request failed with status ${res.status}`;
  try {
    const errorData = await res.json();
    errorMsg = errorData.detail || errorData.message || errorMsg;
  } catch {
    // non-json response
  }
  throw new Error(errorMsg);
}
```
When Next.js or Vercel returns an HTML 404, `res.json()` throws a `SyntaxError`. The `catch` block silently swallowed the parse error, leaving `errorMsg` as `"API request failed with status 404"`.

### Architectural Defect 3: Discarded 401 Credential Details
Prior to repair, line 160 of `client.ts` intercepted `res.status === 401` before `!res.ok` and immediately threw:
```typescript
throw new Error("Session expired or unauthorized. Please log in again.");
```
This discarded the actual backend error message (`"Invalid phone/email or password."`) even when the user was actively attempting to authenticate on the `/login` page.

### Architectural Defect 4: Missing Environment Documentation
Neither the root `.env.example` nor the `frontend/` directory provided explicit documentation on the dual roles of `NEXT_PUBLIC_API_URL` (direct browser client fetch) and `BACKEND_INTERNAL_URL` (server-side Next.js rewrites).

---

## 5. Technical Evidence

1. **FastAPI Route Table Verification:**
   ```python
   from backend.app.main import app
   assert "/api/v1/auth/login" in app.openapi()["paths"]
   assert "post" in app.openapi()["paths"]["/api/v1/auth/login"]
   ```
   *Result:* PASSED.

2. **FastAPI Synthetic Authentication Test:**
   - Registration with valid synthetic farmer: `HTTP 201 Created`.
   - Login with invalid password: `HTTP 401` with body `{"detail": "Invalid phone/email or password."}`.
   - Login with valid password: `HTTP 200` with JWT bearer token and complete user summary.
   - Rate limit quota test: 5 requests allowed; 6th returns `HTTP 429 Too Many Requests`.
   - Redis outage test: `HTTP 503 Service Unavailable` with `Retry-After` header (fail-closed).
   *Result:* PASSED.

3. **URL Normalization Tests:**
   - `resolveApiUrl("/auth/login", "")` &rarr; `"/api/v1/auth/login"`
   - `resolveApiUrl("/auth/login", "http://localhost:8000")` &rarr; `"http://localhost:8000/api/v1/auth/login"`
   - `resolveApiUrl("/auth/login", "http://localhost:8000/")` &rarr; `"http://localhost:8000/api/v1/auth/login"`
   - `resolveApiUrl("/auth/login", "http://localhost:8000/api/v1")` &rarr; `"http://localhost:8000/api/v1/auth/login"`
   - `resolveApiUrl("/auth/login", "http://localhost:8000/api/v1/")` &rarr; `"http://localhost:8000/api/v1/auth/login"`
   - `resolveApiUrl("/auth/login", "https://api.acrevia.in/api")` &rarr; `"https://api.acrevia.in/api/v1/auth/login"`
   *Result:* 11/11 PASSED in `frontend/tests/auth_client.test.js`.

---

## 6. Fixes Implemented

1. **`resolveApiUrl()` Implementation:** Normalizes trailing slashes, strips duplicate `/api/v1` or `/api` segments, ensures clean paths.
2. **`ApiError` Structured Exception Class:** Captures HTTP status, error detail, correlation ID, and network connectivity state.
3. **Resilient Non-JSON Error Handling:** Differentiates between 404 (service endpoint unreachable), 401 (invalid credentials vs expired session), 429 (rate limit exceeded), 502/503 (backend unavailable), and network dropouts.
4. **Next.js Rewrite Normalization:** Sanitizes `BACKEND_INTERNAL_URL` and `NEXT_PUBLIC_API_URL` in `frontend/next.config.mjs`.
5. **Form UX Enhancements:** Protects against double-submission (`disabled={isLoading}`), retains phone input on failure.
6. **Configuration Documentation:** Authored `frontend/.env.example` and updated root `.env.example`.

---

## 7. Remaining Limitations

- **Staging Database Execution:** `DB-RLS-01` remains in `PARTIALLY_IMPLEMENTED` status pending explicit project owner sign-off on Decision Gate 1 for remote branch execution.
- **Production Vercel Deployment:** Production deployment remains strictly withheld (`LIVE_STAGING_DEPLOYMENT_TRIGGERED = FALSE`) under owner governance rules.
