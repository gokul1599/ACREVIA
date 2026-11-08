# ACREVIA 50-Farmer Telangana Pilot Monitoring Plan
## Real-Time Observability, Engagement Tracking & Agronomic Metrics
**Target Stage:** Stage 08 Remediation (`TASK-S08-01`)  
**Scope:** 30-Day Field Trial in Warangal and Nalgonda Clusters  
**Monitoring Cadence:** Real-time alerting, daily automated summaries, and weekly KVK reviews  

---

## 1. Monitoring Architecture & Telemetry Flow

The pilot monitoring system collects privacy-preserving telemetry across three layers:

```
[Client PWA (IndexedDB / Sync Telemetry)]
                    │
                    v
[FastAPI Backend & Redis Rate Limiter] ──> [Prometheus / OpenTelemetry]
                    │                                 │
                    v                                 v
        [Neon PostgreSQL + pgvector]      [Grafana Real-Time Dashboard]
                    │                                 │
                    +───────────────┬─────────────────+
                                    │
                                    v
                     [Daily Automated Ops Digest]
```

---

## 2. Core Telemetry Metric Tiers

### Tier 1: Technical Infrastructure & Sync Health
| Metric Name | Collection Source | Normal Target | Alert Threshold (Red) |
| :--- | :--- | :---: | :---: |
| **Offline Sync Success Rate** | `sync_metadata` / API logs | $\ge 99.0\%$ | $< 95.0\%$ |
| **Sync Retry Count per Record** | Client sync queue telemetry | $\le 1.2$ attempts | $> 3.0$ attempts |
| **API p95 Response Time** | FastAPI middleware | $< 250\text{ ms}$ | $> 1000\text{ ms}$ |
| **ONNX Inference Latency** | Vision service metrics | $< 180\text{ ms}$ | $> 500\text{ ms}$ |
| **Rate Limit 429 Errors** | Redis rate limiter | $< 0.1\%$ of farmer requests | $> 2.0\%$ |
| **Client JS Unhandled Errors** | PWA Sentry / error reporter | $< 0.5\%$ sessions | $> 2.0\%$ |

### Tier 2: User Engagement & Adoption Health
| Metric Name | Collection Source | Normal Target | Action If Breached |
| :--- | :--- | :---: | :--- |
| **Daily Active Farmers (DAF)** | Authenticated session logs | $\ge 35 / 50$ (70%) | Field assistant calls inactive farmers. |
| **Scouting Compliance** | `observations` count per farmer | $\ge 2$ / farmer / week | Field assistant conducts on-site visit. |
| **KrishiBrain Q&A Volume** | RAG query table | $\ge 10$ queries / day | Encourage voice queries at village meeting. |
| **Voice vs Text Interaction** | Query input modality flag | $\ge 40\%$ voice queries | Check microphone permissions on devices. |
| **Telugu Vernacular Usage** | User language preference flag | $\ge 90\%$ Telugu | Ensure all new prompt cards are translated. |

### Tier 3: Agronomic & Pathology Quality
| Metric Name | Collection Source | Normal Target | Action If Breached |
| :--- | :--- | :---: | :--- |
| **Out-of-Distribution (OOD) Rate** | Vision inference output | $< 8\%$ of captures | Retrain farmers on 5-point capture rule. |
| **Expert Review Turnaround Time** | `expert_reviews` timestamps | $< 4\text{ hours}$ (high risk) | Escalate to KVK Programme Coordinator. |
| **AI vs KVK Pathologist Concordance**| Blinded field audit sample | $\ge 85\%$ Top-3 match | Trigger ML research team inspection. |
| **Chemical Safety Violations** | Audit log scraper | **0 violations** | Emergency SEV-1 kill switch trip. |

---

## 3. Daily & Weekly Reporting Cadence

1. **Daily Automated 07:00 IST Standup Digest:**
   - Total active farmers yesterday.
   - Total observations synced (split by Warangal and Nalgonda).
   - Top-3 diagnosed diseases across Cotton, Rice, and Chilli.
   - Any pending unreviewed high-risk cases.
   - Number of sync failures or client retries.

2. **Weekly Friday KVK Synthesis Meeting:**
   - Formal review of blinded field audit results with KVK Pathologists.
   - Review of farmer qualitative feedback gathered by Field Assistants.
   - Evaluation of localized disease outbreaks (e.g. rising Yellow Mosaic in Chilli or Blast in Rice).

---

## 4. Alerting Thresholds & PagerDuty Integration

Automated alerts are triggered to the engineering and operations channels:
- **Red Alert (Immediate WhatsApp & Phone Call):**
  - Offline sync failure rate exceeding 10% in any 1-hour window.
  - Zero observations logged in an entire cluster for $> 24$ hours (potential network blackout).
  - Any advisory generated with confidence $< 0.40$ that recommended chemical intervention.
- **Amber Alert (Slack / Email Digest):**
  - Average inference latency exceeding 400ms.
  - Single farmer failing to sync for 5 consecutive days.
