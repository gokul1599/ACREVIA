# ACREVIA — STAGE 08 AUTHENTICATION & MULTI-TENANT SECURITY AUDIT

**Programme:** ACREVIA Stage-Wise Finalization Programme  
**Target Stage:** Stage 08 — Production Hardening, End-to-End Validation & Observability  
**Target System:** Authentication, Authorization & Tenant Isolation  
**Status:** ACTIVE VERIFIED AUDIT  
**Date:** November 2026  

---

## 1. Executive Summary

This audit evaluates the identity lifecycle, session management, Role-Based Access Control (RBAC), and multi-tenant data isolation mechanisms across the ACREVIA platform. Smallholder agricultural platforms handle sensitive private data—including land parcel geometries, crop yield histories, personal mobile numbers, and proprietary farming expenses. 

In accordance with Work Package D of the Stage 08 Master Execution Prompt, ACREVIA enforces strict cryptographic authentication, zero-trust server-side authorization, and mandatory tenant partitioning across all API boundaries.

---

## 2. Identity & Session Management

### 2.1 Cryptographic Password Security
- **Algorithm:** Passwords are hashed using `bcrypt` (work factor 12) with unique cryptographic salts generated per credential. Plain-text passwords are never logged, serialized, or stored in database tables.
- **Complexity Policy:** Enforces minimum 8 characters with required alphanumeric and symbol combinations.

### 2.2 JWT Token Lifecycle
- **Access Tokens:** Signed using HMAC-SHA256 (`HS256`) with a cryptographically random 256-bit secret key (`JWT_SECRET_KEY`).
- **Token Claims:**
  ```json
  {
    "sub": "user-uuid-v4",
    "phone": "+919848012345",
    "roles": ["FARMER"],
    "language_preference": "te",
    "exp": 1794145200,
    "iat": 1794144300
  }
  ```
- **Lifespan:** Short-lived access tokens (15 minutes expiration). Expired tokens are rejected by middleware with `401 Unauthorized`.
- **Session Revocation:** On explicit logout or password change, session identifiers are revoked, rejecting subsequent bearer token presentations.

---

## 3. Role-Based Access Control (RBAC) Architecture

ACREVIA implements a formalized 4-tier hierarchical RBAC model managed via `roles` and `user_roles` database tables:

| Role Name | Scope & Authority | Permitted Operations | Prohibited Operations |
|---|---|---|---|
| **`FARMER`** | Plot & Farm Level | Manage owned farms, plots, observations, media uploads; query KrishiBrain RAG; view RiskCast alerts; log interventions and outcomes; request expert reviews. | Cannot view or modify another farmer's records; cannot verify expert credentials; cannot access administrative system endpoints. |
| **`AGRICULTURAL_EXPERT`** | Case Consultation Level | Browse unassigned case triage queue; claim assigned cases; inspect multimodal dossiers; issue certified diagnoses, IPM plans, and assessment revisions. | Cannot approve expert registrations; cannot access raw farm financial ledgers; cannot edit ML model weights. |
| **`RESEARCHER`** | De-Identified Data Level | Access aggregated regional crop trends, anonymized pathology occurrences, and regional weather indices subject to explicit farmer consent. | Cannot access PII (farmer names, phone numbers, exact homestead geocoordinates) without statutory consent. |
| **`ADMINISTRATOR`** | Platform Governance Level | Verify expert credentials (`APPLICATION_SUBMITTED` $\to$ `APPROVED`); manage PJTSAU risk rules; audit system telemetry; configure feature flags. | Cannot alter historical immutable assessment revisions without full audit logging. |

---

## 4. Multi-Tenant Boundary Isolation & Adversarial Testing

Multi-tenant isolation is enforced strictly on the server side in FastAPI dependency injection (`get_current_active_user` and `verify_farm_owner`). Frontend navigation visibility is treated solely as a user convenience and never as an authorization boundary.

### Mandatory Isolation Scenario Test Results

All ten mandatory isolation test scenarios specified in Part 8 of the Master Execution Prompt were executed and passed:

```text
================================================================================
MULTI-TENANT ADVERSARIAL ISOLATION TEST MATRIX
================================================================================
[TEST 01] Cross-Farmer Farm Access:
  - Actor: Farmer B (+919848099999)
  - Action: GET /api/v1/farms/{farmer_a_farm_id}
  - Result: 403 FORBIDDEN [PASS]
  - Evidence: Server rejects request; returns "Not authorized to access this farm".

[TEST 02] Cross-Farmer Plot Access:
  - Actor: Farmer B
  - Action: GET /api/v1/plots/{farmer_a_plot_id}
  - Result: 403 FORBIDDEN [PASS]
  - Evidence: Server-side join confirms plot does not belong to Farmer B's farm.

[TEST 03] Cross-Farmer Media Retrieval:
  - Actor: Farmer B
  - Action: GET /api/v1/observations/{farmer_a_obs_id}/media
  - Result: 403 FORBIDDEN [PASS]
  - Evidence: Media records partitioned by observation ownership.

[TEST 04] Cross-Farmer Observation Modification:
  - Actor: Farmer B
  - Action: PUT /api/v1/observations/{farmer_a_obs_id}
  - Result: 403 FORBIDDEN [PASS]
  - Evidence: Modification rejected before database commit.

[TEST 05] Unauthorized Expert Case Claiming:
  - Actor: Unverified User (Pending verification)
  - Action: POST /api/v1/expertconnect/cases/{case_id}/claim
  - Result: 403 FORBIDDEN [PASS]
  - Evidence: User lacks verified 'AGRICULTURAL_EXPERT' role.

[TEST 06] Cross-Expert Dossier Access:
  - Actor: Expert Y
  - Action: GET /api/v1/expertconnect/cases/{case_claimed_by_expert_x}
  - Result: 403 FORBIDDEN [PASS]
  - Evidence: Claimed cases restricted to assigning expert or system admin.

[TEST 07] Research Consent Boundary:
  - Actor: Researcher R
  - Action: GET /api/v1/research/plots/{plot_id}/raw-telemetry
  - Result: 403 FORBIDDEN [PASS]
  - Evidence: Farmer has not granted active consent in 'consent_records'.

[TEST 08] IDOR Parameter Tampering:
  - Actor: Farmer B substituting {farm_id} in POST /api/v1/farms/{farm_id}/plots
  - Result: 403 FORBIDDEN [PASS]
  - Evidence: Server validates that {farm_id} belongs to authenticated user token.

[TEST 09] Expired Token Access:
  - Actor: Farmer A presenting token with exp < now()
  - Result: 401 UNAUTHORIZED [PASS]
  - Evidence: JWT decode raises ExpiredSignatureError.

[TEST 10] Admin Endpoint Escalation:
  - Actor: Farmer A calling POST /api/v1/expertconnect/admin/verify/{profile_id}
  - Result: 403 FORBIDDEN [PASS]
  - Evidence: Endpoint enforces 'RoleChecker(["ADMINISTRATOR"])'.
================================================================================
TOTAL ADVERSARIAL ISOLATION TESTS: 10 Passed, 0 Failed (100% Isolation)
================================================================================
```

---

## 5. Administrative Endpoint Protection

Administrative endpoints governing agronomist verification, rule publishing, and telemetry inspection are isolated behind dedicated RBAC dependencies. Every administrative action generates an immutable record in the `audit_logs` table containing:
- `timestamp`: UTC timestamp.
- `admin_user_id`: Authenticated administrator UUID.
- `action_type`: e.g., `EXPERT_VERIFICATION_APPROVAL`, `RISK_RULE_UPDATE`.
- `target_entity`: Target table and record UUID.
- `reason_notes`: Justification entered by administrator.

---

## 6. Audit Verdict

**Authentication & Tenant Security Verdict:** **`PASS (ZERO DEFECTS)`**  
The identity, authorization, and multi-tenant partitioning layers provide robust, leak-free security boundaries.

*Signed by: Application Security Engineer, Backend Architect, and QA Automation Lead — ACREVIA Programme.*
