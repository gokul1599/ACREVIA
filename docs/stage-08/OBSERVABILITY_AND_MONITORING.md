# ACREVIA — OBSERVABILITY & PRODUCTION MONITORING
## Telemetry Architecture, Structured Logging, Health Probes, AI Metrics & Alerting Strategy

**Platform Identity:** ACREVIA — Agricultural Intelligence Platform  
**Target Environment:** Production (FastAPI Gateway + Next.js + Neon + PyTorch Microservice)  
**Evaluation Date:** November 2026  
**Auditor:** Principal Site Reliability Engineer (SRE) & Observability Specialist  
**Monitoring Status:** VERIFIED OPERATIONAL & INSTRUMENTED  

---

## 1. Executive Summary & Telemetry Philosophy

Production agricultural technology systems must be observable without compromising smallholder farmer privacy. ACREVIA implements a privacy-first telemetry architecture:
1. **Zero PII in Logs:** Farmer names, phone numbers, and raw GPS coordinates are strictly excluded from application log streams.
2. **Correlation ID Tracking:** Every HTTP request carries a unique `X-Correlation-ID` traced from the edge gateway through all internal services.
3. **Multi-Subsystem Telemetry:** Unified observability covering API latencies, database connection pool statistics, ML inference performance, and RAG citation rates.

---

## 2. Gateway Probes & Structured Logging

### 2.1 Health & Readiness Probes

| Endpoint | HTTP Method | Probe Function | Response Payload | Status Codes |
|---|---|---|---|---|
| `/health` | GET | Liveness probe for load balancers | `{"status": "HEALTHY", "service": "acrevia-backend", "version": "1.0.0"}` | 200 OK |
| `/ready` | GET | Readiness probe checking database connectivity | `{"status": "READY", "database": "CONNECTED"}` | 200 OK / 503 Unavailable |
| `/api/v1/system/observability` | GET | Detailed telemetry for monitoring agents | DB pool stats, active crops, storage provider, system health | 200 OK (Admin/Monitoring) |

### 2.2 Structured Logging Standards
Log entries follow standardized JSON/text formatting:
```text
2026-11-08 09:48:38 [INFO] [cid:d451ea36-df4d-4afd-8498-b8334c00e472] acrevia: 
POST /api/v1/observations/81bb1c08-eaba-4907-a7df-1977ed5d50b4/media - 201 (36.33ms) [CID: d451ea36-df4d-4afd-8498-b8334c00e472]
```
- Injects `X-Response-Time-Ms` into HTTP response headers for real-time client-side performance auditing.

---

## 3. Subsystem-Specific AI & Agricultural Telemetry

### 3.1 CropVision Computer Vision Monitoring
- **Model Version Tracking:** Injected into every prediction record (`acrevia-cropvision-mobilenetv3-v1.0.0`).
- **Inference Latency:** Target p95 $< 250$ ms on CPU.
- **Abstention Rate Telemetry:** Percentage of diagnoses flagged as `NEEDS_REVIEW`. An abnormal surge ($> 20\%$) signals potential out-of-distribution field conditions or widespread camera distortion.
- **Quality Rejection Rate:** Tracking percentage of images rejected for blurriness or exposure extremes.

### 3.2 KrishiBrain RAG Knowledge Telemetry
- **Retrieval Latency:** Tracked across pgvector cosine search and BM25 hybrid ranking.
- **Citation Coverage Ratio:** Monitored to ensure 100% of generated advice contains valid literature citations.
- **Abstention Triggers:** Logging queries that trigger regulatory CIBRC abstention (banned pesticides, off-label dosage requests).

### 3.3 RiskCast Agrometeorological Telemetry
- **Weather Provider Freshness:** Hourly verification of Open-Meteo observation timestamps.
- **Fallback Activation Rate:** Alerts engineering if the engine shifts to PJTSAU 30-year historical climate normals due to external provider downtime.
- **Deduplication Rate:** Tracking suppressed duplicate alerts to verify idempotency and prevent farmer alert fatigue.

### 3.4 ExpertConnect Triage Telemetry
- **Queue Dwell Time:** Time elapsed between case creation and agronomist claim (Target: $< 4$ hours for `URGENT`, $< 24$ hours for `ROUTINE`).
- **Clinical Revision Frequency:** Percentage of assessments receiving post-hoc revisions.

---

## 4. Engineering Incident Alerting Hierarchy

Incidents are classified into three operational tiers:

| Severity Level | Definition | Examples | Response Target | Notification Channel |
|---|---|---|---|---|
| **SEV-1 (CRITICAL)** | Core service down or data breach | Database unreachable, authentication failure, cross-tenant data exposure | $< 15$ mins | PagerDuty / On-call SMS / Slack #incidents-critical |
| **SEV-2 (HIGH)** | Core subsystem degraded | Weather API down, ML inference service timeout $> 10\%$, upload storage failure | $< 1$ hour | Slack #incidents-high / Email |
| **SEV-3 (MEDIUM)** | Minor feature degradation | Single RiskCast rule syntax error, non-blocking telemetry export failure | $< 8$ hours | JIRA / GitHub Issues |

---

## 5. Observability Verdict

ACREVIA's observability and monitoring stack provides deep operational visibility, automated health probes, AI inference monitoring, and privacy-preserving audit logs.

**Observability Verdict:** **PASSED — PRODUCTION TELEMETRY ACTIVE.**
