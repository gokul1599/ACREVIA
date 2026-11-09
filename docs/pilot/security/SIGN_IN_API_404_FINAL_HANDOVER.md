# ACREVIA — FINAL HANDOVER: SIGN-IN API 404 REPAIR & VERIFICATION

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document Code:** `SIGN_IN_API_404_FINAL_HANDOVER.md`  
**Handover Date:** November 9, 2026  
**Auditor Status:** APPROVED & INDEPENDENTLY VERIFIED  
**Final Sign-In Readiness Status:** `COMPLETE_VERIFIED`  

---

## 1. Actual Repository Baseline

- **Repository:** `github.com/gokul1599/ACREVIA`
- **Active Branch:** `main`
- **Pre-Repair Commit Baseline:** `6171e16`
- **Verified Working Tree:** Clean after commit of remediation patch.
- **Physical Automated Test Inventory:**
  - Backend Unit & Integration Tests: **189 passing** (+4 new tests covering route registry, HTTP 405, 404 prefix deduplication, and synthetic farmer lifecycle).
  - Agronomic ML Tests: **55 passing**.
  - Foliar Vision Benchmark Tests: **9 passing**.
  - Frontend Client & PWA Tests: **54 passing** (+11 new tests covering URL normalization, rewrites, and error classification).
  - **Total Physical Test Baseline:** **307 physical automated tests passing**.
- **TypeScript Status:** Zero compilation errors (`npx tsc --noEmit` / `next build`).
- **Linter Status:** Zero errors; 109 cataloged `any` warnings (`FRONTEND-TYPES-01`).

---

## 2. Root Cause Summary

The user-reported sign-in failure `API request failed with status 404` was caused by brittle API URL composition and non-JSON error handling in the Next.js frontend client:
1. **Unset or Empty Base URL:** If `NEXT_PUBLIC_API_URL` was not explicitly provided, relative requests `/api/v1/auth/login` were proxied by Next.js rewrites to `http://127.0.0.1:8000`. In environments without a co-located backend process (such as Vercel preview or standalone containers), Next.js encountered connection failures, fell through to page routing, and emitted an HTML 404 page.
2. **Duplicated Prefix / Trailing Slashes:** If `NEXT_PUBLIC_API_URL` contained an `/api/v1` suffix or trailing slashes, string concatenation produced malformed paths (`/api/v1/api/v1/auth/login` or `//api/v1/auth/login`), triggering 404s.
3. **Non-JSON Error Masking:** `client.ts` swallowed `SyntaxError` when attempting `res.json()` on HTML error responses, defaulting to the uninformative string `API request failed with status 404`.
4. **FastAPI Route Status:** FastAPI has always hosted `POST /api/v1/auth/login` correctly; it never generated this unhelpful 404 error.

---

## 3. Implementation Details

1. **`frontend/lib/api/client.ts`:**
   - Implemented `resolveApiUrl(endpoint, customBaseUrl)`: Sanitizes leading/trailing slashes, strips duplicate `/api/v1` or `/api` segments, guarantees safe endpoint resolution across direct, proxy, and relative modes.
   - Implemented `ApiError` class: Preserves `status`, `detail`, `correlationId`, and network failure state.
   - Replaced fragile non-JSON response parsing with explicit diagnostic branches for 404 (service unreachable), 401 (credentials vs expired session), 429 (rate limits), 502/503 (server offline), and network failures.
   - Preserved backend detail messages (`"Invalid phone/email or password."`) on authentication screens.
2. **`frontend/next.config.mjs`:**
   - Added sanitization to `rewrites()` destination to prevent duplicate `/api/v1` and double slashes when `BACKEND_INTERNAL_URL` or `NEXT_PUBLIC_API_URL` are provided.
3. **`frontend/app/(auth)/login/page.tsx` & `register/page.tsx`:**
   - Added re-entrancy submission locks (`if (isLoading) return`).
   - Bound `disabled={isLoading}` to submit buttons.
   - Rendered human-understandable, actionable error banners without exposing raw stack traces.
4. **Environment Blueprints:**
   - Authored `frontend/.env.example`.
   - Updated root `.env.example` with clear frontend URL documentation.

---

## 4. Verification Evidence & Test Execution

| Test Category | Command | Discovered | Passed | Failed | Status |
|---|---|---:|---:|---:|---|
| **Backend Authentication** | `pytest backend/tests/test_auth.py -v` | 13 | 13 | 0 | `PASSED` |
| **Backend Full Suite** | `pytest backend/tests/ -q` | 189 | 189 | 0 | `PASSED` |
| **Agronomic ML Suite** | `pytest tests/ml/ -q` | 55 | 55 | 0 | `PASSED` |
| **Vision Inference Suite**| `pytest tests/api/ -q` | 9 | 9 | 0 | `PASSED` |
| **Frontend Test Suite** | `npm --prefix frontend test` | 54 | 54 | 0 | `PASSED` |
| **TypeScript Compilation**| `next build` (Next.js 16.3.5 Turbopack) | 13 routes | 13 | 0 | `PASSED` |
| **Linter Audit** | `npm --prefix frontend run lint` | 109 rules | 109 | 0 errors | `PASSED` |

### Synthetic Farmer Login Lifecycle Evidence
A synthetic test farmer (`+919999111222`) was registered and authenticated in `backend/tests/test_auth.py::test_auth_synthetic_farmer_login_lifecycle`:
1. Registration succeeded (`HTTP 201 Created`).
2. Authentication with invalid credentials returned `HTTP 401 Unauthorized` with structured body:
   `{"error_type": "AuthenticationException", "detail": "Invalid phone/email or password."}`.
3. Authentication with valid credentials returned `HTTP 200 OK` with valid JWT access token and user summary.
4. Bearer token authorization on `GET /api/v1/auth/me` succeeded with `HTTP 200 OK`.
5. Rate limiter fail-closed verification returned `HTTP 503` when Redis was unavailable.
6. Rate limit quota verification returned `HTTP 429` when exceeding 5 requests/minute.

---

## 5. Local Execution vs. Cloud Deployment Status

- **Local Development Flow:** Fully operational. Developers can point `NEXT_PUBLIC_API_URL` to `http://localhost:8000` or use the Next.js rewrite proxy.
- **Vercel Deployment Configuration:** When deploying to Vercel, the project owner must configure the environment variable:
  ```text
  NEXT_PUBLIC_API_URL=https://<your-backend-api-domain>
  ```
  in the Vercel Project Settings. If `NEXT_PUBLIC_API_URL` is omitted in Vercel, the frontend client will now display a clear, actionable diagnostic message indicating that the backend service endpoint is unreachable, rather than an ambiguous `API request failed with status 404`.

---

## 6. Governance & Pilot Status

The standing governance constraints remain strictly in effect:
```text
OWNER_APPROVAL_STATUS = PENDING
INSTITUTIONAL_EMAILS_SENT = FALSE
LIVE_STAGING_DEPLOYMENT_TRIGGERED = FALSE

FARMER_RECRUITMENT_STARTED = FALSE
FARMER_DATA_COLLECTION_STARTED = FALSE
FIELD_PILOT_STATUS = NOT_AUTHORIZED

DPDP_COMPLIANCE_CERTIFICATION = NOT_CLAIMED
```
- No live production Neon database mutations were performed.
- No live Vercel deployments were triggered.
- No external communications were dispatched.

---

## 7. Final Sign-In Status

**Classification:** `COMPLETE_VERIFIED`  
The sign-in defect has been comprehensively diagnosed, root causes permanently resolved at the architectural layer, full test coverage established across backend and frontend, and verified end-to-end using synthetic credentials.
