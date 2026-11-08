# ACREVIA Pilot Field Supervisor & Agronomist Weekly Checklist
## Standard Quality Assurance Audit Protocols
**Target Stage:** Stage 08 Remediation (`TASK-S08-01`)  
**Auditor:** Field Operations Lead & KVK Senior Pathologist  
**Target Sample:** 50 Participating Farmers (Warangal & Nalgonda)  

---

## Week 1: Onboarding, Consent & Technical Readiness Checklist

| Inspection Item | Verification Method | Target Standard | Pass / Fail |
| :--- | :--- | :--- | :---: |
| **Consent Form Completeness** | Physical audit of 50 signed/thumb-printed DPDP forms. | 100% (50/50 executed) | [ ] |
| **Phone Number & OTP Verification** | Check backend user accounts for verified SMS flags. | 100% verified | [ ] |
| **PWA Home Screen Installation** | Spot-check on 10 farmer phones per cluster. | 100% installed | [ ] |
| **Offline Cache Verification** | Put phone in Airplane Mode $\to$ verify offline splash renders. | 100% functional | [ ] |
| **Baseline Profile Registration** | Confirm acreage, crop variety, sowing date in DB. | 50 complete profiles | [ ] |
| **Dry-Run Sync Test** | Capture dummy photo offline $\to$ reconnect $\to$ verify backend upload. | 100% sync success | [ ] |

*Supervisor Sign-Off (Week 1):* _______________________  *Date:* ______________

---

## Week 2: Initial Scouting Cycle & Offline Sync Audit

| Inspection Item | Verification Method | Target Standard | Pass / Fail |
| :--- | :--- | :--- | :---: |
| **Scouting Compliance Rate** | Check observation records logged between Day 4 and Day 10. | $\ge 90\%$ (at least 45 active) | [ ] |
| **Image Framing Quality** | Pathologist reviews uploaded photos for the 5-point capture rule. | $\ge 85\%$ acceptable quality | [ ] |
| **IndexedDB Sync Queue Health** | Inspect client sync queues; check for orphaned or stuck records. | 0 records stuck $> 24$ hours | [ ] |
| **OOD Rejection Behavior** | Check observations rejected as "Unclear/Non-Crop". | $< 10\%$ false rejections | [ ] |
| **Farmer Comprehension** | Interview 5 farmers per cluster on Telugu audio/text clarity. | $\ge 80\%$ positive comprehension | [ ] |

*Supervisor Sign-Off (Week 2):* _______________________  *Date:* ______________

---

## Week 3: Mid-Pilot Pathology Concordance & Expert SLA Audit

| Inspection Item | Verification Method | Target Standard | Pass / Fail |
| :--- | :--- | :--- | :---: |
| **Physical Ground-Truth Visits** | KVK Pathologist visits 5 random plots per cluster (10 total). | 10 completed field audits | [ ] |
| **AI vs Pathologist Concordance** | Compare blinded field diagnosis against AI Top-3 predictions. | $\ge 85\%$ concordance | [ ] |
| **Expert Escalation SLA** | Review latency for cases marked `PENDING_EXPERT_REVIEW`. | Mean time $< 4$ hours | [ ] |
| **Chemical Safety Check** | Verify zero unapproved chemical prescriptions issued. | 0 off-label or banned inputs | [ ] |
| **Redis Rate Limit Metrics** | Review Redis server metrics for 429 false alarms on farmer traffic. | 0 false throttles on farmers | [ ] |

*Supervisor Sign-Off (Week 3):* _______________________  *Date:* ______________

---

## Week 4: Final Validation, Exit Interviews & Pilot Sign-Off

| Inspection Item | Verification Method | Target Standard | Pass / Fail |
| :--- | :--- | :--- | :---: |
| **Total Observation Quota** | Check total observations logged across 30 days per farmer. | $\ge 8$ per farmer (400+ total) | [ ] |
| **End-to-End Sync Completion** | Verify all local IndexedDB queues emptied to backend DB. | 100% sync rate | [ ] |
| **System Usability Scale (SUS)** | Administer 10-question standardized SUS survey to 50 farmers. | Cohort average score $\ge 75$ | [ ] |
| **Consent Revocation / Purge Check** | Confirm any participant withdrawal requests executed cleanly. | 100% compliant with DPDP | [ ] |
| **Joint KVK-ACREVIA Evaluation** | Convene final evaluation assembly with KVK Programme Coordinators. | Formal sign-off achieved | [ ] |

*Supervisor Sign-Off (Week 4):* _______________________  *Date:* ______________
