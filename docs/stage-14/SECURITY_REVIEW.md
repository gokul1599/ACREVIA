# ACREVIA Stage 14 — Security, SSRF & Access Control Audit

## 1. Threat Modeling & Safeguards

| Threat Vector | Mitigation Strategy | Implemented In |
|---|---|---|
| **Server-Side Request Forgery (SSRF)** | Validation blocks loopback (`127.0.0.1`, `localhost`), RFC 1918 private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), and cloud metadata (`169.254.169.254`). | `WebhookService.validate_destination_url` |
| **API Secret Leakage** | Plaintext secrets are never stored in the database. Secrets are hashed with SHA-256 and only displayed once upon generation. | `DeveloperService.create_credential` |
| **Replay Attacks** | 300-second maximum clock skew enforced on all incoming webhook signatures. | `WebhookService.verify_incoming_signature` |
| **Cross-Tenant Grant Tampering** | Enforced user ownership verification on all grant revocations and application credential modifications. | `PartnerService.revoke_consent`, `DeveloperService.revoke_credential` |
| **Silent Data Overwrites** | Non-overwriting import guarantee. Conflicting records preserved with `CONFLICT_DETECTED` status. | `DataExchangeService.create_import_job` |
| **Rate Limit Exhaustion** | Per-credential rate limiting (defaults to 60 req/min, configurable up to 1000 req/min). | `ApiCredential.rate_limit_per_minute` |

---

## 2. Automated Test Verification
All threat vectors have dedicated automated tests in `backend/tests/test_stage14.py`:
- `test_developer_applications_and_scoped_credentials`: Tests SHA-256 storage, scope enforcement, and revocation.
- `test_farmer_consent_grants_and_tenant_isolation`: Tests cross-tenant revocation blocking (HTTP 403).
- `test_data_import_with_non_overwriting_conflict_preservation`: Tests conflict preservation without silent overwrites.
- `test_webhook_registration_hmac_and_ssrf_protection`: Tests SSRF rejection of localhost, 127.0.0.1, and 169.254.169.254.
