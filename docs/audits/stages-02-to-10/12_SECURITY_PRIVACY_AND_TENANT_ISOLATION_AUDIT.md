# ACREVIA — SECURITY, PRIVACY & TENANT ISOLATION AUDIT
## COMPREHENSIVE CYBERSECURITY, THREAT MODEL & DATA GOVERNANCE REVIEW
**Audit Document:** `12_SECURITY_PRIVACY_AND_TENANT_ISOLATION_AUDIT.md`  
**Classification Standard:** Strictly Evidence-Based Repository Inspection & Static Code Analysis  
**Audit Date:** 2026-11-08  
**Repository Snapshot:** Commit `3de8ceb` (Clean working tree, Branch: `main`)  
**Auditor:** Principal Cybersecurity Architect, Lead Application Security Engineer  

---

## 1. THREAT MODEL & SECURITY POSTURE OVERVIEW

ACREVIA manages sensitive smallholder agricultural assets, including high-resolution geotagged farm boundaries, crop disease photographic records, agrochemical purchase journals, and Soil Health Card nutrient profiles. The threat model accounts for:
1. Cross-tenant data leakage between neighboring farms or commercial competitors.
2. Manipulation of epidemiological alerts or pesticide recommendations.
3. Tampering with digital twin biophysical simulation baselines.
4. Unauthorized exfiltration of smallholder coordinates under India's Digital Personal Data Protection (DPDP) Act 2023.

---

## 2. DETAILED SECURITY & PRIVACY CONTROLS INSPECTION

### 2.1 Authentication & Token Lifecycle
- **Implementation:** `backend/app/core/security.py`, `backend/app/api/deps.py`
- **Algorithm:** HMAC-SHA256 (HS256) JWT access tokens with configurable expiration (default: 60 minutes) and refresh token rotation.
- **Password Hashing:** Passwords hashed using bcrypt via `passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")` with work factor 12.
- **Finding:** Clean implementation. Inactive or disabled users are rejected at dependency injection time (`get_current_active_user`).
- **Severity:** `Informational` (No defects observed).

---

### 2.2 Authorization & Role-Based Access Control (RBAC)
- **Implementation:** `backend/app/api/deps.py` (`get_current_admin`, `get_current_verified_expert`)
- **Roles Defined:** `farmer`, `expert`, `admin`.
- **Finding:** Expert routes (`/api/v1/expert-connect/*`) enforce both `role == "expert"` and `is_verified == True`. Admin endpoints require `is_superuser == True`.
- **Severity:** `Informational` (Well-partitioned roles).

---

### 2.3 Row-Level Multi-Tenant Isolation & IDOR Protection
- **Implementation:** All service layer queries filter by `farmer_id = current_user.id` or `farm.owner_id == current_user.id`.
- **Inspection in Code:**
  - `backend/app/api/v1/endpoints/farms.py`: Query checks `filter(Farm.id == farm_id, Farm.owner_id == current_user.id)`. If missing or owned by another farmer, raises `HTTP 404 Not Found` or `HTTP 403 Forbidden`.
  - `backend/app/api/v1/endpoints/digital_twin.py`: Verifies farm ownership before snapshot generation, scenario execution, or decision retrieval.
- **Evidence:** Automated tests in `backend/tests/test_stage8_e2e.py::test_multi_tenant_isolation_idor` verify that Farmer A receives `HTTP 403` or `HTTP 404` when attempting to access Farmer B's farm, observations, or digital twin scenarios.
- **Severity:** `Informational` (Strictly enforced at ORM and service layers).

---

### 2.4 SQL Injection Defense
- **Implementation:** SQLAlchemy 2.0 ORM with 100% parameterized queries.
- **Inspection in Code:** Repository grep for `text(` and `execute(` revealed that all raw SQL queries (e.g., pgvector cosine distance `<=>` in `backend/app/services/krishibrain.py`) utilize bound parameters (`:embedding`, `:crop_type`) rather than formatted strings or f-string interpolation.
- **Severity:** `Informational` (Zero SQL injection vectors detected).

---

### 2.5 Cross-Site Scripting (XSS) & Input Validation
- **Frontend:** React 19 / Next.js 16 App Router auto-escapes JSX text content. No usage of `dangerouslySetInnerHTML` was found in farmer-facing views.
- **Backend:** Pydantic v2 schemas (`BaseModel`) enforce strict data types, string length bounds, and regex validation on all input fields.
- **Severity:** `Informational` (XSS defended by framework defaults and schema constraints).

---

### 2.6 CSRF & CORS Policy
- **CORS Configuration:** `backend/app/main.py` defines `CORSMiddleware` with explicit allowed origins (`FRONTEND_URL`, localhost development ports). Wildcard `*` is explicitly disabled when credentials are supported.
- **CSRF Risk:** Low. Primary API authentication utilizes stateless `Authorization: Bearer <JWT>` headers, making requests inherently immune to standard browser cross-origin cookie CSRF attacks.
- **Severity:** `Informational`.

---

### 2.7 Server-Side Request Forgery (SSRF)
- **External Network Calls:**
  - Open-Meteo Weather API (`backend/app/services/weather_service.py`)
  - Sentinel Hub / Copernicus Satellite API (`backend/app/services/satellite_service.py`)
- **Inspection:** External fetch URLs are hardcoded to official HTTPS endpoints (`api.open-meteo.com`, `services.sentinel-hub.com`). User coordinates (latitude/longitude) are cast to bounded floats ($-90 \le \text{lat} \le 90$) and interpolated into query parameters; arbitrary user-supplied target URLs are rejected.
- **Severity:** `Informational` (No arbitrary SSRF surface).

---

### 2.8 File Upload & Private Storage Security
- **Implementation:** `backend/app/services/storage_service.py`
- **Validation:**
  - Enforces MIME type allowlist (`image/jpeg`, `image/png`, `image/webp`).
  - Validates image magic bytes via header inspection.
  - Generates random UUID4 storage keys (`storage_key = f"crops/{uuid.uuid4()}.jpg"`) preventing directory traversal (`../`) attacks.
  - Rejects files exceeding 15MB limit.
- **Access Control:** Storage buckets are private; media streaming is routed through authenticated FastAPI proxy (`/api/v1/media/{storage_key}`) verifying user tenancy before streaming bytes.
- **Severity:** `Informational`.

---

### 2.9 Secrets Management & Repository Hygiene
- **Inspection:** Git history search across all commits (`3de8ceb` through initial commit) for live API keys, JWT secret keys, and database passwords.
- **Finding:**
  - No production credentials committed to repository.
  - `.env` is listed in `.gitignore`.
  - `.env.example` provides placeholder values (`SECRET_KEY=change_this_to_a_secure_random_string_in_production`).
  - Production secrets (Neon Postgres connection string, Vercel environment variables) reside in cloud environment variable managers.
- **Severity:** `Informational`.

---

### 2.10 Sensitive Logging & Redaction
- **Implementation:** `backend/app/core/logging_config.py`
- **Inspection:** Standard logging formatters filter out `Authorization` headers, passwords, and sensitive JWT tokens. Traceback logging in production suppresses local environment variables.
- **Severity:** `Informational`.

---

### 2.11 Farmer Privacy & DPDP Act 2023 Compliance
- **Consent Management:** `FarmerConsentRecord` ORM table records timestamped explicit consent for:
  - Geolocation tracking.
  - Satellite remote sensing analysis.
  - Anonymized research aggregation.
- **Data Deletion / Forget-Me:** Endpoint `DELETE /api/v1/farmers/me/purge` implements cascading soft/hard delete of farmer profile, crop observations, and digital twin records.
- **Coordinate Obfuscation:** Regional analytics endpoints apply spatial dithering (truncating GPS coordinates to 2 decimal places $\approx 1.1\text{ km}$ precision) when presenting regional epidemiological heatmaps to non-admin users.
- **Severity:** `Informational`.

---

### 2.12 Agricultural Safety & Chemical Safeguards (CIBRC Interceptors)
- **Implementation:** `backend/app/services/agricultural_safety.py`
- **Audit Finding:**
  - Implements Central Insecticide Board and Registration Committee (CIBRC) banned pesticide filter (e.g., rejecting monocrotophos, endosulfan, carbofuran).
  - Pre-harvest interval (PHI) and re-entry interval (REI) minimum waiting periods strictly enforced before application confirmation.
  - Mandatory disclaimer appended to all automated advisories stating recommendations require local agronomist validation.
- **Severity:** `Informational` (Safety guardrails functioning as specified).

---

## 3. IDENTIFIED VULNERABILITIES & RISKS CLASSIFICATION

While overall security hygiene is exemplary, the following risks have been identified:

| Risk ID | Title | Description | Severity | Affected Component | Recommended Remediation |
|---|---|---|---|---|---|
| **SEC-01** | Client Storage Image Exposure | Farmer PWA stores raw base64 photographic data in unencrypted browser `localStorage` instead of isolated IndexedDB or encrypted cache. Vulnerable to XSS reading client storage on shared mobile devices. | **Medium** | `frontend/lib/offline/queue.ts` | Migrate offline queue to IndexedDB with optional Web Crypto API encryption at rest. |
| **SEC-02** | Rate Limiting Granularity | Rate limiting uses in-memory sliding window on FastAPI instances; lacks distributed Redis backing in multi-replica configurations. | **Low** | `backend/app/core/rate_limiter.py` | Add Redis-backed sliding window rate limiter for multi-instance production deployments. |
| **SEC-03** | Service Worker Cache Scope | Service worker caches static assets aggressively; cache versioning must invalidate immediately upon emergency security patches. | **Low** | `frontend/public/sw.js` | Implement cache header `stale-while-revalidate` with immediate service worker update checks on route transitions. |

---

## 4. SECURITY AUDIT VERDICT

| Category | Finding | Compliance Status |
|---|---|---|
| **Authentication & RBAC** | BCrypt + JWT + Role Dependencies | **COMPLIANT** |
| **Multi-Tenant Isolation** | Strict row-level tenancy (`HTTP 403` on cross-tenant access) | **COMPLIANT** |
| **Injection Defenses** | Parameterized ORM queries throughout | **COMPLIANT** |
| **Data Privacy (DPDP 2023)** | Consent tracking, coordinate dithering, purge endpoint | **COMPLIANT** |
| **Agricultural Safety** | CIBRC chemical interceptors & safety disclaimers active | **COMPLIANT** |
| **Secret Management** | Zero secrets in repository history | **COMPLIANT** |

**Conclusion:** The platform achieves an enterprise-grade security baseline suitable for controlled farmer pilot deployments. Zero Critical or High vulnerabilities were detected. Medium-severity finding `SEC-01` must be remediated prior to commercial multi-tenant launch.
