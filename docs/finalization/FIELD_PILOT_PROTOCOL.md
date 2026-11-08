# ACREVIA — REAL-WORLD AGRICULTURAL FIELD PILOT PROTOCOL
## Controlled Smallholder Evaluation Plan in Warangal & Khammam Districts, Telangana

**Document Version:** 1.0.0  
**Status:** Approved Operational Protocol  
**Target Duration:** 4 Consecutive Weeks (Active Cropping Season)  
**Target Cohort Size:** 15 Smallholder Farmers (5 Cotton, 5 Rice, 5 Chilli)  
**Field Coordinators:** 2 Certified Field Agronomists & 1 Local Extension Worker  

---

### 1. Geographic & Demographic Cohort Selection

* **Priority Districts:** Warangal (Georai / Atmakur mandals) and Khammam (Kalluru / Enkoor mandals).
* **Participant Distribution:**
  * Cotton (*Gossypium hirsutum*): 5 farmers (Rainfed & Supplemental Borewell, Vertisol soils).
  * Rice (*Oryza sativa*): 5 farmers (Canal & Tube Well Irrigated, Alluvial & Clay soils).
  * Chilli (*Capsicum annuum*): 5 farmers (Intensive Drip & Furrow, Red Sandy Loam / Alfisol soils).
* **Device & Connectivity Diversity:**
  * Low-end Android smartphones (Android 9–11, 2 GB–3 GB RAM).
  * Intermittent 2G/3G/4G rural field connectivity (testing offline PWA queue).
  * Vernacular literacy: Primary Telugu speakers (`te-IN`), with varying smartphone literacy.

---

### 2. The 15 Core Pilot Workflows to Validate

1. **Farmer Onboarding & Authentication:** Self-registration using phone number and OTP in Telugu.
2. **Farm Profile Setup:** Registering farm holding name, district, mandal, and village.
3. **Plot Boundary Mapping:** Walking plot boundary or defining GPS coordinates.
4. **Crop-Season Registration:** Selecting target crop (Cotton/Rice/Chilli), sowing date, and seed variety.
5. **Crop Observation Logging:** Creating routine weekly foliar inspection entries.
6. **Foliar Image Capture & Quality Gate:** Taking leaf photos; verifying blur and exposure rejection.
7. **Offline Field Scouting:** Capturing observations in remote fields with cellular data disabled.
8. **Reconnection Synchronization:** Verifying that `OfflineQueue` automatically flushes drafts upon returning to network.
9. **CropVision Automated Diagnosis:** Reviewing MobileNetV3 predictions, confidence scores, and Grad-CAM lesions.
10. **KrishiBrain Vernacular Q&A:** Asking agronomic questions via voice or text in Telugu with grounded citations.
11. **RiskCast Disease Alerts:** Receiving localized weather-driven epidemiological warnings.
12. **ExpertConnect Human Triage:** Escalating ambiguous foliar symptoms to university agronomists.
13. **Intervention Logging & PHI/REI Safety:** Recording pesticide/fertilizer applications and viewing safety countdowns.
14. **Harvest & Multi-Picking Records:** Logging yield pickings, moisture assays, and minting produce lots.
15. **Data Export & Privacy Review:** Reviewing data-sharing grants and verifying that public QR hides private PII.

---

### 3. Quantitative Acceptance Thresholds (Defined Prior to Trial)

| Evaluation Metric | Mathematical Definition | Minimum Acceptance Target |
|---|---|---|
| **Workflow Completion Rate** | $\frac{\text{Completed Workflows}}{\text{Attempted Workflows}} \times 100$ | $\ge 85.0\%$ |
| **Offline Sync Success Rate** | $\frac{\text{Successfully Flushed Drafts}}{\text{Queued Offline Drafts}} \times 100$ | $\ge 95.0\%$ |
| **Foliar Quality Gate Accuracy** | Agreement between OpenCV blur detector and human visual assessment | $\ge 90.0\%$ |
| **CropVision Top-1 Clinical Concordance** | Model prediction agreement with university agronomist in-situ diagnosis | $\ge 80.0\%$ |
| **KrishiBrain Grounded Citation Rate** | Percentage of answers with verifiable PJTSAU/ICAR citations | $\ge 98.0\%$ |
| **Vernacular Speech Recognition (WER)** | Word Error Rate on rural agricultural Telugu terms | $\le 18.0\%$ |
| **Zero Privacy Incidents** | Leakage of farmer PII or uncoarsened GPS coordinates | **0 Incidents (0.0%)** |
| **Zero Unauthorized Physical Actuation** | Inadvertent automated valve or equipment command | **0 Incidents (0.0%)** |

---

### 4. Informed Consent, Farmer Data Rights & Safety Protections

1. **Informed Consent in Vernacular:** Written and verbal consent administered in Telugu explaining exact data collection purpose.
2. **Granular Consent Options:** Participants choose whether photos are shared with researchers or kept strictly private.
3. **Unconditional Right of Withdrawal:** Farmers can withdraw participation and request complete data expungement at any point.
4. **Agrochemical Safety Guarantee:** If an automated recommendation appears hazardous or unapproved, the field coordinator immediately overrides the guidance and contacts PJTSAU extension.
