# ACREVIA Stage 14 — API Contracts & Endpoints

## 1. REST Endpoints Overview (`/api/v1`)

### Exchange (`/api/v1/exchange`)
- `POST /api/v1/exchange/export`: Request asynchronous or synchronous data export package.
- `GET /api/v1/exchange/export/{job_id}`: Poll status and manifest of export job.
- `GET /api/v1/exchange/download/{job_id}`: Stream exported payload (JSON, CSV, GeoJSON, or ZIP).
- `POST /api/v1/exchange/import`: Ingest data with conflict detection and mapping rules.
- `GET /api/v1/exchange/import/{job_id}`: Poll import job metrics and conflict counts.
- `POST /api/v1/exchange/mapping-profiles`: Save custom CSV/JSON header mapping schema.
- `GET /api/v1/exchange/mapping-profiles`: List user's saved mapping profiles.

### Partners (`/api/v1/partners`)
- `POST /api/v1/partners/register`: Apply for institutional partner onboarding.
- `GET /api/v1/partners`: List registered partners (filter by status or partner_type).
- `GET /api/v1/partners/{id}`: Retrieve partner profile and verified status.
- `POST /api/v1/partners/{id}/verify`: Admin review gate to verify, suspend, or revoke partner.
- `POST /api/v1/partners/{id}/integrations`: Register adapter capabilities for verified partner.
- `GET /api/v1/partners/{id}/integrations`: List registered partner integration adapters.

### Developer Portal (`/api/v1/developer`)
- `POST /api/v1/developer/applications`: Register client application (production or sandbox).
- `GET /api/v1/developer/applications`: List developer applications owned by user.
- `GET /api/v1/developer/applications/{id}`: Get application details and redirect URIs.
- `POST /api/v1/developer/applications/{id}/credentials`: Generate scoped API key (`ak_live_...` or `ak_sand_...`). Returns client secret only once!
- `DELETE /api/v1/developer/credentials/{id}`: Immediately deactivate/revoke API credential.

### Consent & Grants (`/api/v1/consent/grants`)
- `POST /api/v1/consent/grants`: Authorize categorized farm data sharing with verified partner.
- `GET /api/v1/consent/grants`: List all active and revoked grants for current farmer.
- `POST /api/v1/consent/grants/{id}/revoke`: Immediately terminate partner data access.

### Webhooks (`/api/v1/webhooks`)
- `POST /api/v1/webhooks/endpoints`: Register destination receiver with SSRF validation. Returns HMAC secret.
- `GET /api/v1/webhooks/endpoints`: List user's active webhook destinations.
- `DELETE /api/v1/webhooks/endpoints/{id}`: Deactivate destination.
- `POST /api/v1/webhooks/test-dispatch`: Trigger test event delivery.
- `GET /api/v1/webhooks/deliveries`: Audit recent webhook delivery attempts and status codes.
- `POST /api/v1/webhooks/deliveries/{id}/retry`: Manually re-attempt failed delivery.

### Standards (`/api/v1/standards`)
- `GET /api/v1/standards/units`: List supported units and categories.
- `POST /api/v1/standards/convert-unit`: Deterministic unit conversion (mass, area, volume, etc.).
- `GET /api/v1/standards/taxonomy/crops`: Canonical crop taxonomy for Cotton, Rice, Chilli across English, Telugu, and Hindi.
- `GET /api/v1/standards/taxonomy/crops/{code}`: Single crop taxonomy and variety list.
- `GET /api/v1/standards/health`: Real-time health checks of all connector adapters.
