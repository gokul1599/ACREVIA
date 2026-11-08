# ACREVIA Stage 14 — Architecture & System Design

## 1. System Topology & Boundary

ACREVIA Stage 14 provides external connectivity while preserving strict tenant isolation and data protection:

```
                            [External Ecosystem]
    +-----------------+    +-----------------+    +-----------------+
    | Soil Health Labs|    | Agricultural Uni|    | IoT Gateways /  |
    | (ICAR / PJTSAU) |    | & Research KVKs |    | Sensor Nodes    |
    +--------+--------+    +--------+--------+    +--------+--------+
             |                      |                      |
             +----------------------+----------------------+
                                    |
                            [HTTPS / REST / JSON]
                                    v
       +----------------------------------------------------------+
       |             ACREVIA EDGE & API GATEWAY (/api/v1)         |
       |  - API Credential Verification (SHA-256 Secret Match)    |
       |  - Permission Scope & Rate Limit Checking (60-120 req/m) |
       |  - Farmer Consent Grant Enforcer (Category & Expiry)     |
       +----------------------------+-----------------------------+
                                    |
          +-------------------------+-------------------------+
          |                                                   |
          v                                                   v
+-------------------------+                       +-------------------------+
|     ACREVIA BRIDGE      |                       |    ACREVIA EXCHANGE     |
| Normalized Adapters:    |                       | Export / Import Engine: |
| - SoilLabConnector      |                       | - JSON / CSV / GeoJSON  |
| - MarketPriceConnector  |                       | - ZIP Archive + SHA-256 |
| - WeatherConnector      |                       | - Non-overwriting       |
| - SatelliteConnector    |                       |   Conflict Tracker      |
| - IoTTelemetryConnector |                       +-------------------------+
+-------------------------+                                   |
          |                                                   |
          +-------------------------+-------------------------+
                                    |
                                    v
+---------------------------------------------------------------------------+
|                          TRANSACTIONAL OUTBOX                             |
|  - WebhookEvent: Atomically recorded with domain state changes            |
|  - WebhookDelivery: HMAC-SHA256 signature, SSRF IP Validation             |
+---------------------------------------------------------------------------+
                                    |
                                    v
+---------------------------------------------------------------------------+
|             NEON POSTGRESQL 16 (Singapore sin1) + pgvector                |
|  - integration_partners       - partner_integrations                      |
|  - api_applications           - api_credentials (hashed_secret)           |
|  - data_sharing_grants        - webhook_endpoints                         |
|  - webhook_events             - webhook_deliveries                        |
|  - data_exchange_jobs         - data_mapping_profiles                     |
+---------------------------------------------------------------------------+
```

---

## 2. Invariant Security Enforcement
- **Hashed Secrets:** The database never stores plaintext client secrets. Only `hashlib.sha256(secret.encode()).hexdigest()` is retained.
- **SSRF Blocker:** Before recording or calling webhook endpoints, `WebhookService.validate_destination_url()` ensures destinations are not loopback or RFC-1918 private IPs.
- **HMAC Signatures:** All webhook dispatches carry `X-Acrevia-Signature: sha256=...` and `X-Acrevia-Timestamp: ...` to protect against forgery and replay attacks.
