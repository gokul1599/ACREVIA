# ACREVIA — STAGE 08 OPERATIONAL ALERTING RULES SPECIFICATION

**Programme:** ACREVIA Stage-Wise Finalization Programme  
**Target Stage:** Stage 08 — Production Hardening, End-to-End Validation & Observability  
**Alerting Engine:** Prometheus / Alertmanager Standard  
**Document Classification:** OPERATIONAL MONITORING CONFIGURATION  
**Date:** November 2026  

---

## 1. Executive Summary

This document specifies actionable, high-signal, low-noise operational alerting rules for the ACREVIA production platform. Alert rules are engineered to notify engineering teams of genuine service degradation before smallholder farmer workflows are impacted.

Every alert rule defines a precise condition, evaluation interval, duration threshold, severity mapping, and a direct link to the corresponding recovery runbook.

---

## 2. Core Operational Alert Rules

### 2.1 Critical Service Availability & Infrastructure Alerts

```yaml
groups:
  - name: acrevia_platform_critical
    rules:
      - alert: AcreviaBackendUnavailable
        expr: probe_success{job="acrevia_backend_liveness"} == 0
        for: 1m
        labels:
          severity: SEV1
          category: availability
        annotations:
          summary: "FastAPI ASGI backend is completely unreachable"
          description: "Liveness probe /health failed for > 1 minute on production endpoints."
          runbook_url: "docs/finalization/stage-08/INCIDENT_RUNBOOKS.md#runbook-01"

      - alert: AcreviaHighErrorRate5xx
        expr: (sum(rate(acrevia_http_responses_total{status=~"5.."}[5m])) / sum(rate(acrevia_http_responses_total[5m]))) * 100 > 1.0
        for: 3m
        labels:
          severity: SEV1
          category: reliability
        annotations:
          summary: "API 5xx HTTP error rate exceeds 1.0% threshold"
          description: "Elevated 5xx error rate ({{ $value }}%) detected over 5-minute rolling window."
          runbook_url: "docs/finalization/stage-08/INCIDENT_RUNBOOKS.md#runbook-02"

      - alert: NeonDatabasePoolSaturation
        expr: (acrevia_db_pool_checked_out / acrevia_db_pool_size) * 100 > 80.0
        for: 2m
        labels:
          severity: SEV1
          category: database
        annotations:
          summary: "Neon PostgreSQL connection pool utilization > 80%"
          description: "Database connection pool approaching exhaustion ({{ $value }}% checked out). Risk of request timeouts."
          runbook_url: "docs/finalization/stage-08/INCIDENT_RUNBOOKS.md#runbook-02"
```

---

### 2.2 Latency & Performance Degradation Alerts

```yaml
  - name: acrevia_performance
    rules:
      - alert: AcreviaApiLatencyHigh
        expr: histogram_quantile(0.95, sum(rate(acrevia_http_request_duration_seconds_bucket[5m])) by (le)) > 1.0
        for: 5m
        labels:
          severity: SEV2
          category: performance
        annotations:
          summary: "API 95th percentile latency exceeds 1000ms"
          description: "p95 API response time is {{ $value }}s over a 5-minute window."
          runbook_url: "docs/finalization/stage-08/INCIDENT_RUNBOOKS.md#runbook-04"

      - alert: MlInferenceTimeoutSpike
        expr: sum(rate(acrevia_ml_inference_timeouts_total[5m])) > 5
        for: 2m
        labels:
          severity: SEV2
          category: ml_ops
        annotations:
          summary: "ONNX ML inference execution timeouts spiking"
          description: "Computer vision inference taking > 200ms or timing out repeatedly."
          runbook_url: "docs/finalization/stage-08/INCIDENT_RUNBOOKS.md#runbook-04"

      - alert: KrishiBrainRagFailure
        expr: sum(rate(acrevia_rag_query_failures_total[10m])) > 3
        for: 5m
        labels:
          severity: SEV3
          category: knowledge
        annotations:
          summary: "KrishiBrain RAG query generation failures"
          description: "pgvector similarity search or citation verification failures detected."
          runbook_url: "docs/finalization/stage-08/INCIDENT_RUNBOOKS.md#runbook-06"
```

---

### 2.3 External Integration & Security Alerts

```yaml
  - name: acrevia_security_integrations
    rules:
      - alert: AuthenticationFailureSpike
        expr: sum(rate(acrevia_auth_failures_total[5m])) > 20
        for: 2m
        labels:
          severity: SEV2
          category: security
        annotations:
          summary: "Authentication failure rate anomalous (Potential Brute-Force)"
          description: "Detected {{ $value }} failed login attempts per second across E.164 phone numbers."
          runbook_url: "docs/finalization/stage-08/INCIDENT_RUNBOOKS.md#runbook-05"

      - alert: OpenMeteoWeatherProviderDown
        expr: rate(acrevia_weather_provider_errors_total[15m]) > 0.5
        for: 10m
        labels:
          severity: SEV3
          category: external_api
        annotations:
          summary: "Open-Meteo weather API consecutive failures"
          description: "Weather ingestion failing. PJTSAU historical normal fallback active."
          runbook_url: "docs/finalization/stage-08/INCIDENT_RUNBOOKS.md#runbook-06"

      - alert: OfflineSyncReconcilerBacklog
        expr: acrevia_offline_sync_pending_records > 500
        for: 15m
        labels:
          severity: SEV3
          category: synchronization
        annotations:
          summary: "Farmer offline synchronization backlog accumulation"
          description: "More than 500 queued field scouting observations pending server reconciliation."
          runbook_url: "docs/finalization/stage-08/INCIDENT_RUNBOOKS.md#runbook-07"
```

---

## 3. Notification Routing & Escalation Channels

Alerts generated by Alertmanager route according to severity:

| Severity Level | Notification Channel | Paging Behavior | Escalation Window |
|---|---|---|---|
| **`SEV1`** | PagerDuty / Opsgenie Voice & SMS | Immediate high-priority paging to on-call primary and secondary engineers. | Escalates to Engineering Director after 15 minutes if unacknowledged. |
| **`SEV2`** | Emergency Telegram & Slack Channel (`#acrevia-prod-alerts`) | Automated bot ping with alert context and runbook link. | Paged to on-call engineer after 30 minutes if unresolved. |
| **`SEV3`** | Operational Slack Channel (`#acrevia-ops-telemetry`) | Notification digest with standard priority. | Reviewed during daily standup. |
| **`SEV4`** | Daily SRE Operational Log & Issue Tracker | Automatic ticket creation for backlog review. | Addressed during sprint planning. |

---

## 4. Alert Tuning & Anti-Fatigue Governance

To maintain high engineering responsiveness and prevent alert fatigue:
1. **Flap Detection:** Thresholds require persistent conditions (1 to 5 minutes duration) before firing, preventing transient network blips from triggering pages.
2. **Alert Silencing:** Authorized maintenance windows must be registered in Alertmanager prior to executing schema migrations or planned deployments.
3. **Quarterly Alert Audit:** Any alert rule firing $> 3$ times per week without requiring human remediation is automatically tuned or deprecated.

---

## 5. Sign-Off

**Operational Alerting Rules Verdict:** **`PASS (VALIDATED & ACTIONABLE)`**  
All monitoring thresholds are documented, tested, and mapped to executable runbooks.

*Signed by: Site Reliability Lead and Backend Infrastructure Architect — ACREVIA Programme.*
