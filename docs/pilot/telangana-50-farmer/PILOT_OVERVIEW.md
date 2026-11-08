# ACREVIA 50-Farmer Telangana Field Pilot — Master Overview
## Controlled Pre-Production Operational Validation
**Programme:** ACREVIA Controlled Pilot Readiness Programme  
**Target Stage:** Stage 08 Operational Completion (`TASK-S08-01`)  
**Geographic Region:** Telangana State, India  
**Target Districts:** Warangal (Semi-arid / Black Cotton Soils) & Nalgonda (Red / Mixed Soils)  
**Target Cohort:** 50 Smallholder & Marginal Farmers (25 per district)  
**Target Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*)  
**Duration:** 30 Consecutive Days  
**Institutional Partners:** Krishi Vigyan Kendra (KVK) Malyal (Warangal) & KVK Kampasagar (Nalgonda), PJTSAU  

---

## 1. Executive Summary

The ACREVIA 50-Farmer Telangana Field Pilot is a controlled, human-governed operational study designed to evaluate the real-world field efficacy, user experience, and computational resilience of the ACREVIA Agricultural Intelligence Platform under rural operating conditions in Telangana.

While automated unit, integration, and synthetic E2E tests have certified the software platform (`COMPLETE_VERIFIED`), live agricultural intelligence requires field validation where intermittent network connectivity, ambient glare, low-cost Android hardware, vernacular literacy, and local crop agronomy interact.

This pilot validates four primary pillars:
1. **Offline-First PWA & Edge Usability:** Verifying IndexedDB persistence, background sync upon network resumption, and voice-assisted vernacular interaction.
2. **Computer Vision Inference Grounding:** Assessing field image capture quality, diagnostic calibration, out-of-distribution rejection, and farmer comprehension of uncertainty.
3. **KrishiBrain Agronomic Guidance:** Validating multilingual (Telugu/Hindi/English) knowledge retrieval grounded in PJTSAU package of practices, complete with human-in-the-loop expert escalation.
4. **Data Governance & Farmer Privacy:** Operationalizing the Digital Personal Data Protection (DPDP) Act 2023 with informed consent, coordinate dithering, and transparent rights management.

---

## 2. Cohort Distribution & District Topology

To capture diverse agricultural conditions, soil chemistries, and cropping patterns, the 50 participating farmers are partitioned across two agro-climatic clusters:

```
                                 TELANGANA STATE
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
       WARANGAL DISTRICT                             NALGONDA DISTRICT
   (KVK Malyal / Mahabubabad)                    (KVK Kampasagar / Miryalaguda)
   - 25 Participating Farmers                    - 25 Participating Farmers
   - Dominant Soil: Vertisols (Black Cotton)     - Dominant Soil: Alfisols (Red Sandy Loam)
   - Crop Focus:                                 - Crop Focus:
     * Cotton: 12 Farmers                          * Rice: 13 Farmers
     * Chilli: 8 Farmers                           * Cotton: 7 Farmers
     * Rice: 5 Farmers                             * Chilli: 5 Farmers
```

### Detailed Cohort Matrix:
| Parameter | Warangal Cluster | Nalgonda Cluster | Combined Total |
| :--- | :---: | :---: | :---: |
| **Partner KVK** | KVK Malyal | KVK Kampasagar | 2 KVKs |
| **Target Villages** | 3 Villages (Malyal, Kuravi, Kesamudram) | 3 Villages (Tripuraram, Miryalaguda, Nereducherla) | 6 Villages |
| **Total Farmers** | 25 | 25 | 50 |
| **Cotton Plots** | 12 | 7 | 19 |
| **Rice Plots** | 5 | 13 | 18 |
| **Chilli Plots** | 8 | 5 | 13 |
| **Avg Landholding** | 2.4 Acres | 2.1 Acres | 2.25 Acres |
| **Smartphones** | Android (OS 9.0–14.0) | Android (OS 9.0–14.0) | 100% Android |
| **Primary Language** | Telugu (100%) | Telugu (100%) | Telugu (Primary) |

---

## 3. Core Pilot Objectives

1. **Verify Field Offline Synchronization:**
   Demonstrate that 100% of observations and journal entries recorded in zero-connectivity field conditions are durably stored in client IndexedDB and reliably synchronized to the backend without data corruption upon reconnecting to 2G/3G/4G networks.

2. **Evaluate Computer Vision Model Diagnostic Utility:**
   Measure top-1 diagnostic accuracy across real-world smartphone photos of Cotton, Rice, and Chilli pathologies, benchmarked against simultaneous in-field expert diagnoses by KVK scientists.

3. **Validate Vernacular KrishiBrain Answers:**
   Confirm that all agronomic advice delivered in Telugu is grammatically natural, technically compliant with PJTSAU guidelines, includes mandatory safety precautions for any CIBRC-registered inputs, and transparently cites source publications.

4. **Safety & Zero-Harm Guarantee:**
   Enforce strict Human-in-the-Loop (HITL) review for high-risk chemical interventions and uncalibrated diagnoses, ensuring no toxic or banned chemical recommendation can reach a farmer without licensed agronomist sign-off.

---

## 4. Key Milestones & 30-Day Phasing

```
[Day -7 to -1]   --> Pre-Pilot Setup: KVK MoU, Institutional Sign-off, Device Verification
[Day 1 to 3]     --> Cohort Onboarding, Trilingual Informed Consent, App Installation
[Day 4 to 7]     --> Baseline Scouting & Initial Soil/Crop Profile Registration
[Day 8 to 21]    --> Active Operational Phase (Weekly Observations, Weather, AI Scouting)
[Day 22 to 27]   --> Mid-Season Expert Review & High-Risk Case Validation
[Day 28 to 30]   --> Pilot Closure, Exit Interviews, Data Purge Option & Final Sign-Off
```

---

## 5. Success Criteria & Exit Gates

The pilot will be deemed successful and qualify the platform for regional release if the following criteria are achieved:
- **Zero Critical Safety Incidents:** 0 incorrect chemical dosage recommendations; 0 unverified dangerous pesticide applications.
- **Offline Sync Integrity:** $\ge 99.0\%$ successful sync rate for queued offline records; 0 lost records due to storage eviction.
- **Farmer Usability Score:** System Usability Scale (SUS) score $\ge 75$ across the 50-farmer cohort.
- **Agronomist Concordance:** $\ge 85\%$ diagnostic agreement between ACREVIA AI top-3 predictions and KVK ground-truth pathologist assessments.
