# ACREVIA 30-Day Telangana Field Pilot Operational Calendar
## Day-by-Day Field Protocol, Milestone Gates & Operational Schedule
**Target Stage:** Stage 08 Remediation (`TASK-S08-01` / Evaluation Framework)  
**Locations:** Warangal (Cluster A) & Nalgonda (Cluster B)  
**Cohort Size:** 50 Smallholder Farmers (25 per cluster)  

---

## 1. Calendar Overview & Operational Phases

```
[Day 1–3]   ==> Phase 1: Onboarding, Consent, PWA Installation & Baseline Profile
[Day 4–7]   ==> Phase 2: First Field Scouting Cycle & Offline Sync Trial
[Day 8–14]  ==> Phase 3: Week 2 Scouting & First Blinded KVK Ground-Truth Audit
[Day 15–21] ==> Phase 4: Week 3 Scouting, Mid-Pilot Review & Disease Hotspot Mapping
[Day 22–27] ==> Phase 5: Week 4 Scouting & High-Risk Case Validation
[Day 28–30] ==> Phase 6: Exit Survey (SUS), Data Reconciliation & Institutional Sign-Off
```

---

## 2. Daily Operational Breakdown

### Phase 1: Orientation, Informed Consent & Onboarding (Days 1–3)
- **Day 1 (Warangal Orientation):**
  - 09:30–12:30: Rythu Vedika meeting at Malyal. Trilingual Farmer Information Sheet distributed.
  - 14:00–17:00: Device audit, informed consent execution (`CONSENT_FORM_TE.md`), PWA installation for 25 Warangal farmers.
- **Day 2 (Nalgonda Orientation):**
  - 09:30–12:30: Rythu Vedika meeting at Tripuraram. Trilingual Farmer Information Sheet distributed.
  - 14:00–17:00: Device audit, informed consent execution, PWA installation for 25 Nalgonda farmers.
- **Day 3 (Baseline Profile Registration):**
  - Field assistants register 50 farm profiles (acreage, crop varieties, sowing dates, soil types).
  - Dry-run offline test: farmers record dummy photo offline; verify sync on reconnection.
  - **Milestone Gate 1:** 50/50 farmers onboarded with signed consent and verified PWA installs.

---

### Phase 2: Baseline Scouting & Offline Trial (Days 4–7)
- **Day 4–5 (First Scouting Wave):**
  - All 50 farmers conduct their first official in-field crop inspection (Cotton, Rice, Chilli).
  - Field assistants observe capture technique; reinforce 5-point leaf photography rule.
- **Day 6 (Offline Sync Verification):**
  - Technical engineering audit of `sync_metadata` in PostgreSQL.
  - Verify 100% of offline IndexedDB drafts were successfully committed to backend.
- **Day 7 (Weekly Synthesis 1):**
  - Operations team standup: review initial image quality distributions and OOD rejection rates.

---

### Phase 3: Week 2 Operations & First KVK Ground-Truth Audit (Days 8–14)
- **Day 8–9 (Routine Scouting Cycle 2):**
  - Farmers log second wave of observations (minimum 2 entries per farmer).
- **Day 10 (Warangal Blinded Field Audit 1):**
  - KVK Malyal Pathologist visits 5 random plots (3 Cotton, 1 Chilli, 1 Rice).
  - Pathologist completes blinded diagnostic score sheet before viewing AI output.
- **Day 11 (Nalgonda Blinded Field Audit 1):**
  - KVK Kampasagar Pathologist visits 5 random plots (3 Rice, 1 Cotton, 1 Chilli).
  - Blinded ground-truth scoring recorded.
- **Day 12–13 (Routine Scouting Cycle 3):**
  - Farmers log third scouting cycle.
- **Day 14 (Weekly Synthesis 2 & Concordance Check):**
  - Calculate Week 2 concordance rate between AI Top-3 predictions and KVK diagnoses.
  - **Milestone Gate 2:** Concordance exceeds 80% baseline threshold; zero safety incidents.

---

### Phase 4: Week 3 Operations & Mid-Pilot Review (Days 15–21)
- **Day 15–16 (Scouting Cycle 4 & Voice Q&A Promotion):**
  - Farmers encouraged to ask KrishiBrain questions via voice microphone in Telugu.
- **Day 17 (Warangal Blinded Field Audit 2):**
  - KVK Malyal Pathologist visits second 5-plot random sample.
- **Day 18 (Nalgonda Blinded Field Audit 2):**
  - KVK Kampasagar Pathologist visits second 5-plot random sample.
- **Day 19–20 (Scouting Cycle 5):**
  - High-incidence scouting for emerging sucking pests in Cotton and Chilli.
- **Day 21 (Mid-Pilot Operational Milestone):**
  - Comprehensive database health check: total observations $> 250$.
  - Rate limiting audit: verify zero false 429 throttles experienced by farmers.

---

### Phase 5: Week 4 Operations & High-Risk Case Validation (Days 22–27)
- **Day 22–23 (Scouting Cycle 6):**
  - Focus on reproductive stage symptoms (bollworm in cotton, neck blast in rice).
- **Day 24 (Warangal Blinded Field Audit 3):**
  - KVK Malyal Pathologist visits third 5-plot sample (cumulative sample = 15 Warangal plots).
- **Day 25 (Nalgonda Blinded Field Audit 3):**
  - KVK Kampasagar Pathologist visits third 5-plot sample (cumulative sample = 15 Nalgonda plots).
- **Day 26–27 (Final Scouting Cycle 7):**
  - Farmers log final observations. Total cumulative observations per farmer $\ge 8$.

---

### Phase 6: Exit Evaluation, Data Reconciliation & Institutional Sign-Off (Days 28–30)
- **Day 28 (System Usability Scale Administration):**
  - Field assistants administer the standardized 10-question SUS survey in Telugu to all 50 farmers.
  - Conduct structured qualitative exit interviews on perceived crop loss avoidance.
- **Day 29 (Data Reconciliation & Privacy Confirmation):**
  - Verify all client IndexedDB queues are 100% drained and synchronized to backend.
  - Review consent renewal / withdrawal register; execute any requested data erasures within SLA.
  - Generate automated evaluation metrics report across all 4 pillars.
- **Day 30 (Joint Institutional Sign-Off Assembly):**
  - Joint conference at PJTSAU / KVK with Programme Coordinators, Pathologists, and ACREVIA Leadership.
  - Formal execution of `PILOT_COMPLETION_AND_SIGNOFF_TEMPLATE.md`.
  - **Milestone Gate 3:** Formal pilot completion and regional deployment recommendation signed.
