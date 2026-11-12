# ACREVIA — PHASE 07: COLLECTIVE & FPO FIELD RECONCILIATION & PRIVACY MATRIX

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation  
**Document ID:** `ACR-SEC-P07-COLLECTIVE-RECON`  
**Classification:** RESTRICTED — PILOT DATA PRIVACY AUDIT  
**Audit Determination:** **`RESOLVED_LOCALLY_AND_TESTED`**  
**Associated Baseline Tests:** `backend/tests/test_worker_security_and_privacy.py` (`test_public_organization_redaction_matrix`, `test_registration_number_vs_legal_entity_number_schema_separation`, `test_collective_organization_http_json_serialization_all_roles`)  

---

## 1. Source-Level Entity & Field Disambiguation

Inspection of the current local source code and migration history resolves all entity property questions:

| Entity Name | Source File | Authoritative Column | Column Datatype | Domain Semantics |
| :--- | :--- | :--- | :--- | :--- |
| **`AgriculturalOrganization`** | `backend/app/models/collective.py` (Line 21) | **`registration_number`** | `String(100)`, Nullable | FPO / Cooperative Registration Number under Telangana Societies Registration Act or Section 581 of Companies Act. |
| **`IntegrationPartner`** | `backend/app/models/interoperability.py` (Line 30) | **`legal_entity_number`** | `String(100)`, Nullable | Corporate / Institutional CIN / LLPIN / GSTIN for external universities, soil testing laboratories, and KVKs. |

### Source Invariant Proof:
- `AgriculturalOrganization` contains **only** `registration_number`. The attribute `legal_entity_number` does not exist on this model.
- `IntegrationPartner` contains **only** `legal_entity_number`. The attribute `registration_number` does not exist on this model.
- There is **zero property collision** between these two classes in `Base.metadata`.

---

## 2. Model-to-Schema-to-Endpoint Privacy Chain

An end-to-end chain audit was conducted across models, Pydantic response schemas, and API serialization routes:

| Confidential / Sensitive Field | Present on ORM Model | Present on Response Schema | Serialized to Privileged Callers | Serialized to Unprivileged Callers | Privacy Mechanism |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`registration_number`** | **Yes** (`collective.py`) | **Yes** (`collective.py`) | **`REG-TS-WGL-001`** | **`None` (Masked)** | Explicit endpoint redaction in `list_organizations` & `get_organization`. |
| **`contact_email`** | **Yes** (`collective.py`) | **Yes** (`collective.py`) | **`director@fpo.org`** | **`None` (Masked)** | Explicit endpoint redaction. |
| **`contact_phone`** | **Yes** (`collective.py`) | **Yes** (`collective.py`) | **`+919876543210`** | **`None` (Masked)** | Explicit endpoint redaction. |
| **`verified_by_user_id`** | **Yes** (`collective.py`) | **NO** | **Never Serialized** | **Never Serialized** | Omitted from `AgriculturalOrganizationResponse` schema; structurally cannot leak. |
| **`verification_notes`** | **NO** (Does not exist) | **NO** | **N/A** | **N/A** | Exists only on `IntegrationPartner`, not on `AgriculturalOrganization`. |

---

## 3. Authoritative Six-State Collective Data Privacy Matrix

Reconciling previous descriptive summaries, the access control matrix formally covers **six unambiguous caller categories**:

| Field Name | 1. Anonymous / Public | 2. Non-Member Farmer | 3. Inactive Member (`is_active=False`) | 4. Member of Other Org | 5. Active Org Member | 6. Platform Admin (`ADMIN`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id`, `name`, `org_type` | **Visible** | **Visible** | **Visible** | **Visible** | **Visible** | **Visible** |
| `state`, `district` | **Visible** | **Visible** | **Visible** | **Visible** | **Visible** | **Visible** |
| `description` | **Visible** | **Visible** | **Visible** | **Visible** | **Visible** | **Visible** |
| `verification_status` | **Visible** | **Visible** | **Visible** | **Visible** | **Visible** | **Visible** |
| **`registration_number`** | `None` (Masked) | `None` (Masked) | `None` (Masked) | `None` (Masked) | **`REG-TS-WGL-001`** | **`REG-TS-WGL-001`** |
| **`contact_email`** | `None` (Masked) | `None` (Masked) | `None` (Masked) | `None` (Masked) | **`director@fpo.org`** | **`director@fpo.org`** |
| **`contact_phone`** | `None` (Masked) | `None` (Masked) | `None` (Masked) | `None` (Masked) | **`+919876543210`** | **`+919876543210`** |
| **`verified_by_user_id`** | `Excluded` | `Excluded` | `Excluded` | `Excluded` | `Excluded` | `Excluded` |

---

## 4. API Endpoint & Serialization Path Audit

All routes in [`backend/app/api/v1/endpoints/collectives.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/collectives.py) were inspected:
1. `GET /collectives/organizations`: Enforces bulk list redaction. Queries active user memberships via `OrganizationMembership` and masks fields for any organization where caller is not an active member and not an admin.
2. `GET /collectives/organizations/{org_id}`: Enforces single-object detail redaction.
3. **Search & Filter:** Handled via query parameters (`district`, `org_type`) on `list_organizations`; uses the same redacted serializer.
4. **Exports & Alternate Routes:** Zero bulk export or CSV endpoints exist that could bypass this redaction.
5. **Nested Serializers:** `CollectiveActivityResponse` contains `organization_id` (foreign key string), but does **not** embed nested `AgriculturalOrganization` objects, preventing secondary leakage.

---

## 5. Verification Test Evidence
- **`test_public_organization_redaction_matrix`**: Proves exact redaction behavior across all 6 caller states.
- **`test_registration_number_vs_legal_entity_number_schema_separation`**: Proves zero property collision between `AgriculturalOrganization` and `IntegrationPartner`.
- **Classification:** **`RESOLVED_LOCALLY_AND_TESTED`**.


---

## 6. Direct HTTP Network Boundary & JSON Serialization Evidence

To prove that sensitive attributes are genuinely suppressed at the HTTP wire boundary rather than merely in internal Python helpers, test `test_collective_organization_http_json_serialization_all_roles` was executed using FastAPI's `TestClient`:

### Serialized HTTP JSON Response Payloads:

#### 1. Unprivileged Callers (Non-Member, Inactive Member, Other Org Member):
```json
{
  "id": "org-http-001",
  "name": "Telangana Rythu Producer Company",
  "org_type": "FPO",
  "registration_number": null,
  "state": "Telangana",
  "district": "Khammam",
  "description": "Organic Cotton Collective",
  "contact_email": null,
  "contact_phone": null,
  "verification_status": "APPROVED",
  "created_at": "2026-11-12T00:00:00Z"
}
```
*Note: `registration_number`, `contact_email`, and `contact_phone` serialize as JSON `null`. Attribute `verified_by_user_id` is completely absent from the JSON key set.*

#### 2. Privileged Callers (Active Organization Member & Platform Administrator):
```json
{
  "id": "org-http-001",
  "name": "Telangana Rythu Producer Company",
  "org_type": "FPO",
  "registration_number": "REG-FPO-TS-2024-999",
  "state": "Telangana",
  "district": "Khammam",
  "description": "Organic Cotton Collective",
  "contact_email": "secretariat@telanganarythu.org",
  "contact_phone": "+919848011223",
  "verification_status": "APPROVED",
  "created_at": "2026-11-12T00:00:00Z"
}
```
*Note: Contact coordinates and registration number are unmasked. Attribute `verified_by_user_id` remains completely absent from the JSON key set due to strict Pydantic response schema exclusion.*
