# ACREVIA — Observability and Operations Guide
**Stage:** 12 — Collaborative Agricultural Intelligence  
**Focus:** Collaboration Metrics, Telemetry, Moderation Queues, and Audit Logging

---

## 1. Operational Telemetry & Metrics

| Subsystem | Metric Key | Alert Threshold | Operational Action |
| :--- | :--- | :---: | :--- |
| **ACREVIA Connect** | `connect.reports.unresolved_count` | $> 20$ reports | Notify community moderation team for urgent triage. |
| **ACREVIA Commons** | `commons.review_queue_depth` | $> 15$ pending | Alert ExpertConnect agronomists to review backlog. |
| **ACREVIA Collectives** | `collectives.unverified_orgs_count` | $> 5$ pending | Request ROC / Department registration verification. |
| **ACREVIA Research Hub** | `research.disputed_annotations_ratio` | $> 25\%$ tasks | Escalate disputed tasks to senior agronomy panel. |
| **Regional Pulse** | `regional_pulse.suppressed_outbreak_claims` | $> 10$ claims/day | Investigate potential field rumors or localized anomalies with KVK scientists. |

---

## 2. Redaction Invariant in Audit Logging

Under no circumstances should the logging infrastructure record:
- User plaintext passwords or JWT credentials.
- Unredacted private farmer identity documents.
- Private phone numbers or Aadhaar details in trace logs.
- Sensitive attachments or private medical/financial notes.
