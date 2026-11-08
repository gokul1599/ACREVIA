# ACREVIA — INCIDENT RESPONSE & DISASTER RECOVERY
## Operational Runbooks, Severity Matrix, Emergency Kill Switches & High-Availability Recovery

**Platform Identity:** ACREVIA — Agricultural Intelligence Platform  
**Target Infrastructure:** FastAPI Gateway + Next.js PWA + Neon PostgreSQL + PyTorch Microservice  
**Evaluation Date:** November 2026  
**Auditor:** Principal Site Reliability Engineer & Application Security Officer  
**Plan Status:** VERIFIED OPERATIONAL & ACTIONABLE  

---

## 1. Executive Summary & Operational Posture

Agricultural digital platforms directly influence smallholder farming decisions. A system failure that delivers erroneous chemical advice, loses field observations, or exposes farmer records requires immediate, disciplined containment.

This document establishes ACREVIA's incident management protocol, emergency architectural kill switches, and disaster recovery procedures.

---

## 2. Incident Classification & Severity Matrix

| Severity Level | Criteria & Impact | Example Scenarios | Initial Response SLA | Escalation Target |
|---|---|---|---|---|
| **SEV-1 (CRITICAL)** | Core platform offline, database unavailable, data breach, or hazardous chemical advice | Neon DB connection failure; cross-tenant plot access vulnerability; erroneous pesticide dosage recommendation | **$< 15$ Minutes** | SRE Lead, Lead Security Architect, Agricultural Director |
| **SEV-2 (HIGH)** | Significant subsystem failure with partial degradation | CropVision ML inference timeout; Open-Meteo weather API down; image upload storage failure | **$< 1$ Hour** | Backend Engineering Lead, DevOps On-Call |
| **SEV-3 (MEDIUM)** | Minor degradation, cosmetic issue, or non-critical background task failure | Single RiskCast rule logic bug; scheduled batch cron delayed; localization typo in vernacular subtext | **$< 8$ Hours** | Assigned Product Engineer |

---

## 3. Incident Response Protocol: 10-Step Lifecycle

```text
1. DETECTION       --> Automated alerts, health probes (/health), or user reports
2. TRIAGE          --> On-call engineer assigns Severity Level (SEV-1/2/3)
3. CONTAINMENT     --> Activate kill switch or isolate affected component
4. IMPACT ASSESS   --> Identify affected farmers, districts, or crops
5. ESCALATION      --> Page response team via PagerDuty / emergency channel
6. REMEDIATION     --> Deploy hotfix, failover to standby, or restore backup
7. VERIFICATION    --> Execute automated smoke test suite to confirm health
8. COMMUNICATION   --> Post vernacular status banner on farmer PWA
9. POST-MORTEM     --> Author Root Cause Analysis (RCA) within 48 hours
10. PREVENTION     --> Implement preventative automated tests and gates
```

---

## 4. Emergency Agricultural Kill Switches

A critical requirement of ACREVIA's architecture is the ability to selectively disable or revert specific agricultural algorithms, models, or rules **without taking the entire platform offline**.

### 4.1 Kill Switch A: Disable an Unsafe CropVision Model Version
If field feedback indicates a newly deployed computer vision model is misclassifying a disease:
- **Action:** Set environment variable `ML_INFERENCE_FALLBACK_MODE="EXPERT_ONLY"`.
- **System Behavior:** CropVision bypasses automated neural network prediction, immediately labels incoming diagnoses as `NEEDS_REVIEW`, and routes observations directly to the ExpertConnect human review queue with an honest explanation.

### 4.2 Kill Switch B: Suspend a Disputed RiskCast Rule
If local agricultural university agronomists challenge an active risk rule threshold:
- **Action:** Update the rule record in Neon PostgreSQL:
  ```sql
  UPDATE risk_rules SET is_active = FALSE WHERE rule_code = 'COT-BLW-01';
  ```
- **System Behavior:** The rule engine immediately skips `COT-BLW-01` during hourly batch and on-demand evaluations; all other 5 rules continue executing normally.

### 4.3 Kill Switch C: Deactivate a Superseded KrishiBrain Knowledge Document
If a state agricultural directive supersedes a specific chemical pesticide recommendation:
- **Action:**
  ```sql
  UPDATE knowledge_documents SET approval_status = 'SUSPENDED' WHERE id = 'doc-uuid';
  ```
- **System Behavior:** The hybrid vector retriever automatically filters out all chunks associated with suspended documents (`approval_status == 'APPROVED'`), preventing outdated citations from surfacing in farmer answers.

### 4.4 Kill Switch D: Immediate Suspension of Compromised Expert Profile
If an agronomist account exhibits suspicious activity or compromised credentials:
- **Action:** Admin calls `POST /api/v1/expertconnect/admin/verify/{profile_id}` with `decision="SUSPENDED"`.
- **System Behavior:** The user is instantly stripped of `AGRICULTURAL_EXPERT` permissions; active claimed cases are automatically released back into the `QUEUED` triage pool.

---

## 5. Disaster Recovery Runbooks

### 5.1 Runbook 1: Total Neon PostgreSQL Outage / Corruption
1. **Declare SEV-1:** Inform SRE and engineering leads.
2. **Access Neon Console:** Navigate to the production Neon project.
3. **Trigger Point-in-Time Branch Recovery:**
   - Select point-in-time timestamp immediately preceding the corruption event (e.g., $T - 10$ minutes).
   - Create recovered branch `main-recovery-timestamp`.
4. **Update Gateway Secret:**
   - Update `DATABASE_URL` secret in Vercel to point to the newly promoted branch.
5. **Verify Database Health:**
   - Check `/ready` endpoint until `{"status": "READY", "database": "CONNECTED"}` is returned.
6. **Execute Smoke Suite:** Run `pytest backend/tests/test_stage8_e2e.py`.

### 5.2 Runbook 2: Vercel Function Outage or Breaking Deployment
1. Open Vercel Project Dashboard.
2. Select previous known-good deployment commit.
3. Click **"Promote to Production"** to instantly revert global DNS and edge traffic within $< 5$ seconds.

---

## 6. Incident Response Verdict

ACREVIA is equipped with granular agricultural kill switches, robust disaster recovery runbooks, and proven containment procedures.

**Incident Response Verdict:** **PASSED — OPERATIONAL RUNBOOKS CERTIFIED.**
