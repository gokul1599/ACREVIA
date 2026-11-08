# ACREVIA Stage 14 — Webhook Architecture & Transactional Outbox

## 1. Transactional Outbox Pattern
To guarantee consistency without dual-write failures, event emission is coupled directly to domain database transactions:

```
[Farm Operation / Diagnosis / Risk Alert]
                 |
                 v
   BEGIN DB TRANSACTION
     1. Insert/Update Domain Entity (e.g. DiagnosisRequest, RiskAlert)
     2. Insert WebhookEvent (status: 'PENDING', payload_json: {...})
   COMMIT DB TRANSACTION
                 |
                 v
   [Async / Background Dispatcher]
     1. Read 'PENDING' WebhookEvents
     2. Query active WebhookEndpoints matching event_type
     3. Generate HMAC-SHA256 signature
     4. Dispatch HTTP POST to endpoint
     5. Record WebhookDelivery audit row
     6. Update WebhookEvent status to 'DELIVERED'
```

---

## 2. Cryptographic Signatures & Replay Prevention
Every webhook delivery includes the following HTTP headers:
- `X-Acrevia-Signature: sha256=<hex_hmac>`
- `X-Acrevia-Timestamp: <unix_epoch_timestamp>`

The signature is computed over:
$$\text{Signature} = \text{HMAC-SHA256}(\text{Secret}, \text{Timestamp} + "." + \text{PayloadBody})$$

### Receiver Verification:
1. Verify `|current_time - X-Acrevia-Timestamp| <= 300` seconds (5 minutes). Replay requests older than 300 seconds are rejected.
2. Compute expected HMAC with shared webhook secret.
3. Compare using constant-time `hmac.compare_digest`.
