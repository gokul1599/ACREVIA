# Collaborative Research & Field Validation Proposal
## Deployment of ACREVIA Agricultural Intelligence Platform for Smallholder Field Evaluation
**Submitted To:**  
1. **The Programme Coordinator**, Krishi Vigyan Kendra (KVK) Malyal, Mahabubabad / Warangal, PJTSAU  
2. **The Programme Coordinator**, Krishi Vigyan Kendra (KVK) Kampasagar, Nalgonda, PJTSAU  

**From:** ACREVIA Engineering & Agricultural Intelligence Research Group  
**Academic Affiliation Focus:** Professor Jayashankar Telangana State Agricultural University (PJTSAU) Package of Practices  
**Target Duration:** 30 Calendar Days (Active Pilot) + 14 Days (Analysis & Joint Publication)  

---

## 1. Project Title & Context

**Project Title:** *Independent Field Validation, Ground-Truth Pathology Calibration, and Vernacular Usability Evaluation of the ACREVIA AI Platform in Smallholder Cotton, Rice, and Chilli Agro-Ecosystems of Telangana.*

Smallholder farmers in Telangana face recurring yield losses from complex pest complexes (e.g. Pink Bollworm and Spodoptera in Cotton, Brown Planthopper and Blast in Rice, Thrips, Mites, and Gemini Viruses in Chilli). While artificial intelligence offers rapid visual diagnosis on smartphones, ungrounded AI models risk hallucinations, inappropriate pesticide recommendations, and crop injury.

ACREVIA has developed an offline-first, vernacular (Telugu/English/Hindi) diagnostic system grounded in the official PJTSAU Package of Practices, fortified with human-in-the-loop agronomist oversight and DPDP 2023 compliance. 

This proposal requests an institutional partnership with KVK Malyal and KVK Kampasagar to validate this system under controlled field conditions.

---

## 2. Collaborative Objectives

1. **Independent Plant Pathology Ground-Truthing:**
   KVK plant pathologists and entomologists will conduct independent, blinded diagnostic evaluations of crop symptoms in 50 participating farmer fields, establishing the scientific ground truth against which ACREVIA's computer vision inference (shared MobileNetV3 28-class architecture) will be benchmarked.

2. **Package of Practices (PoP) Compliance Audit:**
   Audit KrishiBrain RAG advisory outputs to ensure all diagnostic explanations, threshold-based pest management (ETL) guidelines, and cultural/biological/chemical recommendations strictly adhere to PJTSAU and Central Insecticides Board & Registration Committee (CIBRC) standards.

3. **Expert Connect Workflow Validation:**
   Evaluate the bidirectional communication pipeline (`/api/v1/diagnoses/reviews`) between field farmers and KVK scientists, measuring agronomist review latency, ease of annotation, and resolution of ambiguous cases.

4. **Digital Literacy & Usability Evaluation:**
   Assess vernacular PWA adoption, offline IndexedDB synchronization in low-connectivity pockets, and farmer confidence in AI-assisted advisory.

---

## 3. Division of Responsibilities

```
+----------------------------------------------------+----------------------------------------------------+
| ACREVIA ENGINEERING & PLATFORM TEAM                | KRISHI VIGYAN KENDRA (KVK) SCIENTIFIC TEAM         |
+----------------------------------------------------+----------------------------------------------------+
| 1. Provide dedicated, pre-configured PWA           | 1. Facilitate village-level orientation sessions  |
|    instances with zero infrastructure cost to KVK.  |    at Rythu Vedikas in target mandals.             |
| 2. Deploy specialized KVK Expert Web Portal        | 2. Nominate 1 Pathologist and 1 Agronomist per     |
|    with annotation tools and case queues.          |    cluster for weekly blinded ground-truth visits. |
| 3. Conduct technical onboarding for 50 farmers     | 3. Review high-risk or ambiguous diagnostic cases   |
|    and supply trilingual user manuals.              |    escalated by the platform within 4 hours.       |
| 4. Maintain zero-data-loss offline sync engine     | 4. Co-evaluate farmer exit interviews and SUS      |
|    and cloud infrastructure on Vercel/Postgres.    |    usability scoring metrics.                      |
| 5. Provide institutional research stipend /        | 5. Co-author the peer-reviewed field validation    |
|    logistical transport support for field visits.  |    white paper and technical bulletin.             |
+----------------------------------------------------+----------------------------------------------------+
```

---

## 4. Scientific Protocol & Safety Governance

- **Blinded Evaluations:** During weekly field audits (20% random cohort sample), scientists will assess crop symptoms independently before viewing the AI inference results.
- **Human-Controlled Chemical Safeguards:** The platform will strictly withhold automated chemical pesticide advice for severe or uncalibrated cases, displaying a mandatory notification: *"Diagnosis pending verification by your local KVK scientist"*.
- **Data Protection:** All farmer personally identifiable information (PII) is encrypted. GPS coordinates are truncated to prevent precise farm boundary exposure, complying with the Digital Personal Data Protection (DPDP) Act 2023.

---

## 5. Expected Outcomes & Deliverables

1. **Joint Technical Bulletin:** A co-authored report detailing:
   - Diagnostic accuracy, sensitivity, and specificity across 28 pathology classes.
   - Out-of-Distribution (OOD) rejection rate under real sunlight and phone camera variations.
   - Offline synchronization reliability metrics in rural 2G/3G conditions.
2. **KVK Capacity Building:** Proven digital outreach tool enabling extension scientists to monitor pest outbreaks across the district in real time via geospatial disease heatmaps.
3. **Smallholder Empowerment:** 50 participating farmers equipped with permanent access to validated, vernacular agricultural intelligence.

---

## 6. Endorsement & Sign-Off

**For ACREVIA Platform:**  
Principal AI Architect: ___________________________  Date: ______________  
Agricultural Research Director: ___________________  Date: ______________  

**For Krishi Vigyan Kendra, PJTSAU:**  
Programme Coordinator, KVK Malyal: ________________ Date: ______________  
Programme Coordinator, KVK Kampasagar: ____________ Date: ______________  
