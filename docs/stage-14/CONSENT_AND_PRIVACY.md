# ACREVIA Stage 14 — Consent & Privacy Governance

## 1. Farmer-First Data Ownership Invariants
1. **Explicit Granular Consent:** Data sharing is never automatic or blanket. Each `DataSharingGrant` explicitly specifies:
   - Partner ID (must be a verified entity).
   - Stated purpose.
   - Categories permitted (`FARM_PROFILE`, `SOIL_HEALTH`, `WATER_RESOURCES`, `OBSERVATIONS`, `DIAGNOSTICS`, `HARVEST_YIELD`).
   - Expiration date (defaults to 90 days, maximum 730 days).
2. **Instant Revocation:** Farmers can revoke access at any moment through `/api/v1/consent/grants/{id}/revoke`. Revocation takes effect immediately across all background jobs and integration bridges.
3. **Tenant Boundary Protection:** Only the owning farmer can view or revoke their grants. Cross-tenant access attempts return HTTP 403 Forbidden.

---

## 2. Privacy Redaction & De-Identification
1. **PII Masking (`redact_pii=True`):**
   - Farmer full name is masked to a random identifier (e.g. `Farm-8a31b412`).
   - Phone numbers, personal emails, and national IDs are omitted.
2. **GPS Coarsening (`redact_gps=True`):**
   - Precise polygon vertices and centimeter GPS points are replaced with district or mandal centroid representations, preventing external actors from pinpointing physical field boundaries without explicit commercial justification.
