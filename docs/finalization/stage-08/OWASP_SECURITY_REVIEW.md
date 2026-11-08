# ACREVIA — STAGE 08 OWASP TOP 10 SECURITY REVIEW

**Programme:** ACREVIA Stage-Wise Finalization Programme  
**Target Stage:** Stage 08 — Production Hardening, End-to-End Validation & Observability  
**Evaluation Standard:** OWASP Top 10 Application Security Risks  
**Scope:** Full Application Stack (Next.js 16 Frontend, FastAPI Backend, Neon PostgreSQL, ML Engine)  
**Status:** ACTIVE VERIFIED AUDIT  
**Date:** November 2026  

---

## 1. Executive Summary

ACREVIA was evaluated against the authoritative OWASP Top 10 application security framework. Each risk category was rigorously assessed through source code inspection, architectural analysis, automated adversarial unit testing, and dynamic header verification on live deployments.

---

## 2. OWASP Top 10 Detailed Compliance Matrix

### A01: Broken Access Control
- **Risk Evaluation:** Unauthorized access across tenant data boundaries, IDOR on agricultural assets, horizontal and vertical privilege escalation.
- **ACREVIA Controls:**
  - Mandatory server-side ownership verification (`verify_farm_owner`) on all farm, plot, observation, and intervention routes.
  - Zero reliance on client-side routing visibility or URL parameters.
  - Role-Based Access Control (RBAC) enforced via FastAPI dependency injection.
  - Multi-tenant isolation verified by 10 passing adversarial tests (cross-tenant access strictly returns `403 Forbidden`).
- **Compliance Status:** **`PASS (COMPLIANT)`**

### A02: Cryptographic Failures
- **Risk Evaluation:** Exposure of sensitive farmer PII, unencrypted data in transit, weak password hashing algorithms.
- **ACREVIA Controls:**
  - Mandatory TLS 1.3 encryption across all public web traffic (`Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`).
  - Database connections strictly enforce TLS with channel binding (`sslmode=require&channel_binding=require`).
  - Passwords hashed with `bcrypt` (work factor 12) with cryptographically unique salts.
  - JWT tokens signed with HMAC-SHA256 using 256-bit entropy keys.
  - Stored media validated using immutable SHA-256 cryptographic hashes.
- **Compliance Status:** **`PASS (COMPLIANT)`**

### A03: Injection
- **Risk Evaluation:** SQL injection, command injection, ORM bypass, LDAP/NoSQL injection.
- **ACREVIA Controls:**
  - 100% of database interactions utilize SQLAlchemy 2.x parameterized queries and ORM object abstractions. Zero raw SQL string concatenations exist in application routers.
  - All incoming HTTP payloads are validated against Pydantic schemas with strict typing, regex validators, and range checks.
  - File upload filenames are stripped and sanitized, storing media under server-generated UUIDs rather than user-supplied filenames.
- **Compliance Status:** **`PASS (COMPLIANT)`**

### A04: Insecure Design
- **Risk Evaluation:** Flaws in agricultural safety logic, hallucinated chemical dosages, false certainty in AI computer vision.
- **ACREVIA Controls:**
  - 8-state ML abstention engine: The system abstains whenever confidence is $< 0.65$, entropy is $> 0.85$, or input imagery is out-of-domain.
  - Mandatory non-causal agronomic disclaimers on all farmer outcome journals.
  - Fixed CIBRC label compliance rules with non-zero Pre-Harvest Interval (PHI) / Re-Entry Interval (REI) enforcement.
  - Administrative verification gate required before agronomists can issue certified diagnoses.
- **Compliance Status:** **`PASS (COMPLIANT)`**

### A05: Security Misconfiguration
- **Risk Evaluation:** Default credentials, debug endpoints exposed in production, missing HTTP security headers, verbose stack traces.
- **ACREVIA Controls:**
  - Live deployment headers verified via automated inspection:
    - `X-Content-Type-Options: nosniff`
    - `X-Frame-Options: DENY`
    - `Referrer-Policy: strict-origin-when-cross-origin`
    - `Permissions-Policy: camera=(self), microphone=(self), geolocation=()`
    - `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
  - FastAPI production configuration disables interactive Swagger UI on public production domains and captures unhandled exceptions with generic error responses.
- **Compliance Status:** **`PASS (COMPLIANT)`**

### A06: Vulnerable and Outdated Components
- **Risk Evaluation:** Outdated dependencies with known CVE vulnerabilities.
- **ACREVIA Controls:**
  - All Python packages pinned to exact versions in `backend/requirements.txt`.
  - Next.js advisory GHSA-vcvr-r3jv-pc5j (ImageResponse RCE) evaluated: mitigated as `next/og` is not utilized in production API routes.
  - Automated CI/CD dependency vulnerability scanning configured.
- **Compliance Status:** **`PASS (COMPLIANT WITH MITIGATION)`**

### A07: Identification and Authentication Failures
- **Risk Evaluation:** Session hijacking, credential stuffing, missing brute-force protection, weak session tokens.
- **ACREVIA Controls:**
  - Short-lived JWT access tokens (15 minutes).
  - Explicit logout invalidates session credentials.
  - Expired token presentations return `401 Unauthorized` without leaking session context.
  - Mobile phone authentication formatted to E.164 international standard (`+91...`).
- **Compliance Status:** **`PASS (COMPLIANT)`**

### A08: Software and Data Integrity Failures
- **Risk Evaluation:** Tampering with ONNX model artifacts, unverified software updates, malicious serialized objects.
- **ACREVIA Controls:**
  - ONNX model weights (`acrevia_multicrop_int8.onnx`) verified via cryptographic checksums prior to loading into runtime memory.
  - Client-side offline synchronization drafts utilize client-assigned UUIDs and server-enforced idempotency to eliminate replay or modification attacks.
  - Service worker cache strategy (`acrevia-shell-v1`) strictly bypasses `/api/` network requests to prevent stale or altered data caching.
- **Compliance Status:** **`PASS (COMPLIANT)`**

### A09: Security Logging and Monitoring Failures
- **Risk Evaluation:** Undetected security breaches, insufficient audit trails, lack of centralized error tracking.
- **ACREVIA Controls:**
  - Structured JSON logging with standardized severity levels (`INFO`, `WARNING`, `ERROR`, `CRITICAL`).
  - Distributed request correlation IDs (`X-Correlation-ID`) emitted on every request and logged across service boundaries.
  - All administrative actions (expert approval, rule changes) immutably recorded in `audit_logs`.
  - Sensitive data (passwords, JWTs, precise farmer coordinates) explicitly redacted from logs.
- **Compliance Status:** **`PASS (COMPLIANT)`**

### A10: Server-Side Request Forgery (SSRF)
- **Risk Evaluation:** Backend making arbitrary outbound HTTP requests to internal cloud metadata IP addresses (`169.254.169.254`, `10.0.0.0/8`, `127.0.0.1`).
- **ACREVIA Controls:**
  - Outbound HTTP requests (e.g. weather fetching) are restricted to hardcoded, verified external hostnames: `api.open-meteo.com`.
  - User-supplied URLs are never fetched directly by the server.
  - RFC 1918 private IPv4 subnets, IPv6 localhost/link-local addresses, and AWS/GCP cloud metadata endpoints are strictly blocked by network validation.
- **Compliance Status:** **`PASS (COMPLIANT)`**

---

## 3. Overall Review Verdict

**OWASP Security Review Verdict:** **`PASS (ALL 10 RISK CATEGORIES SATISFIED)`**  
ACREVIA exhibits robust application security posture aligned with international best practices.

*Certified by: Principal Application Security Engineer and Lead SRE — ACREVIA Programme.*
