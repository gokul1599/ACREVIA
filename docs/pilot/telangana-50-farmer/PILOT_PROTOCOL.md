# ACREVIA 50-Farmer Telangana Field Pilot Protocol
## Standard Operating Procedures for Field Execution
**Target Stage:** Stage 08 Remediation (`TASK-S08-01`)  
**Scope:** Field Staff, KVK Extension Scientists, Platform Supervisors, Participating Farmers  
**Locations:** Warangal & Nalgonda Districts, Telangana  

---

## 1. Protocol Architecture & Operational Phases

The pilot follows a 4-phase sequential execution protocol over 30 days:

```
+-----------------------------------------------------------------------------------+
| PHASE 1: RECRUITMENT, CONSENT & ONBOARDING (Days 1–3)                             |
| - Village orientation sessions at Gram Panchayat / Rythu Vedika                   |
| - Device compatibility audit & PWA installation                                   |
| - Informed consent execution (Telugu/English/Hindi DPDP forms)                    |
| - Farm boundary, soil type & active crop profile registration                     |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| PHASE 2: BASELINE ESTABLISHMENT & FIRST SCOUTING CYCLE (Days 4–7)                 |
| - Baseline soil and crop phenology assessment                                     |
| - Guided first observation capture (leaf photograph + voice note)                 |
| - Offline mode trial (recording in field, syncing at village center)              |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| PHASE 3: ACTIVE SCOUTING & ADVISORY OPERATIONS (Days 8–24)                        |
| - Bi-weekly field scouting by farmers (Days 10, 14, 18, 22)                       |
| - Asynchronous AI diagnosis & KrishiBrain vernacular advisory                     |
| - Weekly KVK agronomist field audit & ground-truth validation                     |
| - High-risk pathology review and expert intervention triggers                     |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| PHASE 4: PILOT EVALUATION, CLOSURE & SIGNOFF (Days 25–30)                         |
| - Post-pilot System Usability Scale (SUS) survey administration                   |
| - Yield projection & intervention effectiveness interview                         |
| - Final data sync, consent confirmation / data deletion option                    |
| - Joint KVK-ACREVIA sign-off assembly                                            |
+-----------------------------------------------------------------------------------+
```

---

## 2. Phase 1: Onboarding Standard Operating Procedure (SOP-01)

### Step 1.1: Rythu Vedika Briefing
- Convene a 90-minute briefing at the local Rythu Vedika in each cluster.
- Conduct briefing in Telugu using the trilingual Farmer Information Sheet.
- Explain the platform purpose: agricultural decision support, pathology identification, and PJTSAU-aligned guidance.
- Explicitly state: ACREVIA does not replace certified agronomists; high-risk recommendations require human review.

### Step 1.2: Device Audit & Connectivity Test
- Confirm participant possesses an active Android smartphone running Android 9.0 or higher with Google Chrome or Chromium-based browser.
- Verify camera functionality and rear lens cleanliness.
- Test 4G cellular data and offline airplane-mode toggle.

### Step 1.3: Informed Consent & Identity Registration
- Read the Telugu DPDP Consent Form aloud to the participant.
- Obtain signed or thumb-printed consent along with verified phone number.
- Assign anonymized Pilot Participant ID (e.g. `PILOT-WAR-COT-001` to `PILOT-WAR-COT-012`).
- Issue authenticated credentials with role `farmer` and tenant `warangal-pilot` or `nalgonda-pilot`.

### Step 1.4: PWA Installation & Offline Verification
- Open Chrome, navigate to the production domain (`https://acrevia.app`).
- Tap "Add to Home screen" / "Install App".
- Switch device to Airplane Mode.
- Verify the PWA loads from the Cache API and displays the offline badge.
- Capture a dummy offline draft; confirm persistence in IndexedDB (`acrevia_offline_db_v2`).
- Switch Airplane Mode off; verify the draft synchronizes automatically to the backend.

---

## 3. Phase 2: Field Scouting & Image Capture Protocol (SOP-02)

To ensure diagnostic accuracy and avoid Out-of-Distribution (OOD) rejections, farmers are trained on the 5-point capture rule:

1. **Focus on Symptomatic Area:** Capture both healthy tissue and the disease lesion margin in the frame.
2. **Lighting:** Avoid harsh midday direct sunlight and deep shadows. Ideal capture times: 07:30–10:30 AM or 04:00–06:00 PM.
3. **Distance & Framing:** Maintain a distance of 15–30 cm from the leaf surface. The leaf must occupy $\ge 60\%$ of the image viewfinder.
4. **Clean Background:** Support the leaf with a hand or plain surface if necessary, avoiding complex weed or soil backgrounds.
5. **Multi-Angle Scouting:** For complex symptoms, capture 2 to 3 photos (upper leaf surface, lower leaf surface, whole branch).

---

## 4. Phase 3: Weekly KVK Validation & Ground-Truth Protocol (SOP-03)

- **Assigned Scientists:** 1 Senior Plant Pathologist and 1 Agronomist per KVK cluster.
- **Weekly Schedule:** Every Tuesday (Warangal) and Thursday (Nalgonda).
- **Physical Inspection:** Scientists visit a randomized 20% sample of participant plots weekly (5 farms per cluster per week).
- **Dual Diagnosis Record:**
  - Scientist records independent diagnosis on a standardized paper scoring sheet without viewing the AI output.
  - Scientist then opens the ACREVIA Expert Connect portal (`/expert/reviews`) and cross-examines the AI prediction.
  - Scientist records:
    * `AI Concordance`: Match, Partial Match, or Discordant.
    * `Confidence Calibration`: Appropriate, Overconfident, or Underconfident.
    * `Action Plan Approval`: Approved as-is, Modified, or Rejected.

---

## 5. Phase 4: Escalation & Adverse Event Handling (SOP-04)

- If an AI inference predicts a quarantined or highly destructive pathogen (e.g., Pink Bollworm in Cotton, Bacterial Leaf Blight in Rice, or Chilli Leaf Curl Virus at severe infestation levels):
  1. The system flags the observation with status `PENDING_EXPERT_VERIFICATION`.
  2. An automated SMS alert is dispatched to the cluster KVK agronomist.
  3. Chemical advisory is withheld from the farmer UI until the agronomist confirms the diagnosis or provides alternative cultural/biological controls.
  4. Response time target: $< 4$ hours during daylight hours (08:00–18:00).
