# ACREVIA — API SECURITY AUDIT & OWASP COMPLIANCE REVIEW
## Comprehensive Evaluation against OWASP Top 10 API Security Risks (2023 Standard)

---

## 1. Executive Security Evaluation

An exhaustive security audit was conducted on the ACREVIA Stage 4 backend implementation. The platform enforces defense-in-depth principles across transport, authentication, tenant boundaries, and third-party integrations.

| OWASP Vulnerability | Risk Level | Mitigation Architecture | Verification Status |
| :--- | :--- | :--- | :--- |
| **API1: Broken Object Level Auth (BOLA)** | Critical | `verify_farm_access` enforces owner/membership checks on all farm/plot/media accesses. | **PASSED** (Verified in `test_authorization.py`) |
| **API2: Broken Authentication** | Critical | Bcrypt 12 rounds, JWT HS256, expiration lifetimes, unguessable UUID subjects. | **PASSED** (Verified in `test_auth.py`) |
| **API3: Broken Property Level Auth** | High | Strict Pydantic v2 schemas reject unauthorized field mutations (no mass assignment). | **PASSED** |
| **API4: Unrestricted Resource Consumption** | High | Maximum media upload size capped at 15MB; query pagination capped at 50 records. | **PASSED** |
| **API5: Broken Function Level Auth (BFLA)** | High | `require_roles(AGRICULTURAL_EXPERT)` enforces agronomist review restrictions. | **PASSED** (Verified in `test_diagnoses.py`) |
| **API6: Unrestricted Business Flows** | Medium | Deduplication via SHA-256 prevents duplicate media and diagnostic flooding. | **PASSED** |
| **API7: Server-Side Request Forgery (SSRF)** | High | Hardcoded Telangana centroid coordinates in weather adapter; zero client URLs followed. | **PASSED** |
| **API8: Security Misconfiguration** | Medium | Docker runs as unprivileged `acrevia:10001`; secrets read strictly from `.env`. | **PASSED** |
| **API9: Improper Inventory Management** | Low | Canonical `/api/v1` prefix; OpenAPI schema auto-generated; no shadow APIs. | **PASSED** |
| **API10: Unsafe Consumption of APIs** | Medium | Strict bounded timeouts (5.0s weather, 10.0s ML client) with automated fallback. | **PASSED** |

---

## 2. In-Depth Vulnerability Analysis & Countermeasures

### 2.1 BOLA Prevention (API1)
In agricultural multi-tenancy, BOLA occurs when a farmer replaces `farm_id` in a URL to view another cultivator's land records or disease observations.
- **Countermeasure:** ACREVIA's `verify_farm_access` executes on every request involving `farm_id`, `plot_id`, or `observation_id`. It confirms that the authenticated subject (`sub`) is either the owner or an active member.
- **Empirical Evidence:** In `backend/tests/test_authorization.py`, `test_cross_farm_read_blocked`, `test_cross_farm_plot_creation_blocked`, and `test_cross_farm_observation_blocked` confirm that cross-farm requests are rejected with `HTTP 403 Forbidden`.

### 2.2 Path Traversal Prevention in Object Storage
When serving foliar photographs from local storage (`/api/v1/observations/{id}/media/{mid}/file`), attackers might supply malicious filenames (e.g., `../../etc/passwd`).
- **Countermeasure:** `LocalStorageProvider.get_absolute_path()` enforces path sanitization using `Path(storage_path).name`, completely stripping directory traversal characters before resolving within the isolated storage directory.

### 2.3 SSRF Defense in Agrometeorological Client (API7)
ACREVIA never accepts user-supplied URLs for weather forecasting. It maps validated district names to predetermined agricultural coordinates (`TELANGANA_DISTRICT_COORDS`), querying the fixed Open-Meteo endpoint with sanitized parameters.
