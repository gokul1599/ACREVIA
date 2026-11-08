# ACREVIA — Security, Governance & Privacy Review (Stage 7)
## Threat Modeling, Tenant Boundaries, RBAC Enforcement & Data Integrity

---

## 1. Multi-Tenant Farm Data Isolation

Stage 7 operates within ACREVIA's multi-tenant architecture. Every endpoint handling plots, interventions, alerts, or observations invokes `verify_farm_access(farm_id, user, db)`.

### 1.1 Attack Vector: Cross-Farm Intervention Tampering
- **Risk:** Malicious farmer attempts to post an erroneous chemical intervention on an adjacent competitor's plot by guessing or enumerating the `plot_id`.
- **Mitigation:**
  1. The server loads the `Plot` record and resolves its parent `Farm`.
  2. The server verifies that `current_user.id` is either the registered `owner_id` or possesses an active `FarmMembership` on that specific farm.
  3. If unauthorized, the request is immediately aborted with `403 Forbidden` and audited to `AuditLog`.
  4. Verified in automated tests (`test_interventions_lifecycle_and_outcomes`).

---

## 2. Expert Credentialing & Authorization Boundaries

### 2.1 Attack Vector: Self-Declared Expert Privilege Escalation
- **Risk:** User registers as a standard farmer, then calls `/expertconnect/cases/.../assess` to issue fraudulent pesticide recommendations.
- **Mitigation:**
  1. Setting `AGRICULTURAL_EXPERT` role is strictly restricted to platform administrators.
  2. Registration applications reside in `APPLICATION_SUBMITTED` state with zero special capabilities.
  3. All case claim and assessment endpoints enforce `require_roles("AGRICULTURAL_EXPERT", "ADMIN")`. Standard farmers receive `403 Forbidden`.
  4. Verified in automated tests (`test_expertconnect_application_and_admin_verification`).

---

## 3. Data Integrity & Immutability Guarantees

### 3.1 Immutable Assessment Revisioning
- **Risk:** An agronomist modifies previous diagnostic notes after a crop failure to avoid liability, deleting evidence of hazardous chemical advice.
- **Mitigation:**
  1. Updates to `ExpertAssessment` trigger the creation of a permanent `ExpertAssessmentRevision` record.
  2. The prior state (primary condition, differentials, chemical plan, PHI advice) is serialized into `previous_assessment_json` and committed in the same database transaction.
  3. The revision table has no update or delete routes, guaranteeing a tamper-evident audit trail for agricultural authorities.

---

## 4. Privacy & Location Masking

1. **Weather Coordinates:**
   - Weather queries do not expose exact GPS coordinates of farmer fields to external third-party APIs (Open-Meteo).
   - Queries are mapped to district/mandal centroids (`TELANGANA_DISTRICT_COORDS`), protecting sensitive farm boundary geojson from third-party IP scraping.
2. **Farmer PII Protection in Expert Triage:**
   - Reviewing experts view farm name, mandal/district, soil type, and crop phenology needed for diagnosis.
   - Farmer personal phone numbers and national ID details are hidden from the triage dossier to prevent unsolicited off-platform contact.
