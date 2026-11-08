# ACREVIA — AGRICULTURAL FIELD PILOT PROTOCOL
## Controlled On-Farm Validation Methodology, Usability Metrics & Clinical Safety Framework

**Platform Identity:** ACREVIA — Agricultural Intelligence Platform  
**Target Region:** Telangana, India (Warangal, Khammam, Karimnagar)  
**Target Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*)  
**Languages:** Telugu (`te`), English (`en`), Hindi (`hi`)  
**Target Cohort Size:** 15–20 Smallholder Farmers + 2 Certified Agronomists  
**Protocol Version:** 1.0.0-PROD  
**Author:** Principal Agricultural AI Architect & Field Research Coordinator  

---

## 1. Study Rationale & Research Objectives

While laboratory and computational benchmarks (e.g., test split accuracies, synthetic RAG evaluations) establish theoretical capability, real agricultural deployments face severe field challenges:
- High ambient sunlight and foliar shadows.
- Intermittent 2G/3G connectivity or complete rural signal blackouts.
- Varied Android smartphone cameras (sub-\$100 devices with noisy optical sensors).
- Distinct rural dialectal nuances in Telugu.
- Complex pest complexes (e.g., simultaneous Thrips and Anthracnose on Chilli).

The primary objectives of this controlled field pilot are:
1. Evaluate end-to-end task completion for smallholder farmers using the ACREVIA PWA.
2. Measure CropVision diagnostic reliability and abstention frequency on real field foliage.
3. Validate farmer comprehension of probabilistic AI uncertainty and RiskCast weather predisposition disclaimers.
4. Assess ExpertConnect clinical triage ergonomics and response turnaround time with KVK agronomists.
5. Verify offline draft synchronization under intermittent network connectivity.

---

## 2. Participant Eligibility & Selection Criteria

### 2.1 Farmer Participant Criteria
- **Inclusion Criteria:**
  - Actively cultivating at least one of the three target crops (Cotton, Rice, Chilli) in Telangana.
  - Landholding between 1.0 and 10.0 acres (representative smallholder to medium farmer).
  - Owns an Android smartphone (Android 8.0 or newer) with a functional camera.
  - Ability to communicate in Telugu, English, or Hindi.
  - Willingness to participate in a 4-week crop monitoring period with weekly check-ins.
- **Exclusion Criteria:**
  - Corporate contract farming entities with automated greenhouse or precision irrigation sensor arrays.
  - Unwillingness to sign informed consent or share crop leaf photographs for research validation.

### 2.2 Agricultural Expert Criteria
- Minimum Master of Science (M.Sc.) or Ph.D. in Plant Pathology, Agricultural Entomology, or Agronomy.
- Minimum 3 years of field diagnostic experience in Telangana agro-climatic zones.
- Formal affiliation with a recognized institution (PJTSAU, ICAR, or District KVK).

---

## 3. Ethical Governance & Informed Consent Protocol

### 3.1 Informed Consent Lifecycle
1. **Vernacular Plain-Language Briefing:** Explaining study scope, voluntary nature, and privacy protections in Telugu (or Hindi/English).
2. **Specific Purpose Limitation:** Explicitly separating permission to use the software from optional consent to include anonymized foliar photos in future open research datasets.
3. **Unconditional Withdrawal Right:** Participants may withdraw at any time without penalty or loss of standard agricultural extension support.
4. **Data Minimization:** No Aadhaar numbers, national identity cards, or exact survey cadastral maps are collected. Locations are generalized to village and mandal centroids.

### 3.2 Participant Safety & Advisory Disclaimer
> [!IMPORTANT]
> **Safety Guarantee to Farmers:**  
> ACREVIA is an assistive diagnostic decision-support tool. It does **not** replace certified agronomist recommendations. In any high-severity ambiguity, the system routes the case to a qualified human expert. Farmers are explicitly instructed never to purchase or spray toxic agrochemicals based solely on an automated smartphone prediction.

---

## 4. Structured Field Tasks & Evaluation Scenarios

Each farmer participant executes 8 standardized field scenarios over the 4-week trial:

| Scenario Code | Field Activity | Primary Subsystem | Evaluation Metric |
|---|---|---|---|
| **SC-01** | Farmer Registration & Plot Setup | Auth & Farm Management | Onboarding duration ($< 5$ mins target), form error rate |
| **SC-02** | Foliar Image Capture in Full Sunlight | CropVision & Quality Gate | Exposure rejection rate, blur detection frequency |
| **SC-03** | Crop Disease Diagnosis & Advisory | CropVision & KrishiBrain | Diagnosis comprehension, farmer trust rating (1–5) |
| **SC-04** | Multilingual Vernacular Voice Q&A | KrishiBrain Multilingual | Speech-to-text accuracy, citation readability |
| **SC-05** | Weather Predisposition Alert Review | RiskCast Intelligence | Understanding that alert $\ne$ active disease (Yes/No) |
| **SC-06** | Escalation to Agricultural Expert | ExpertConnect Network | Ease of case submission, satisfaction with response |
| **SC-07** | Recording Farm Intervention & PHI | Intervention Tracking | Comprehension of Pre-Harvest Interval (PHI) warnings |
| **SC-08** | Offline Photo Capture & Resync | PWA Offline Queue | Successful draft recovery upon reconnecting to 4G/WiFi |

---

## 5. Quantitative Usability & Agronomic Rubrics

### 5.1 Usability Metrics (SUS & Task Success)
- **Task Completion Rate:** Percentage of farmers completing plot setup, image upload, and advisory review without facilitator assistance.
- **System Usability Scale (SUS):** Standardized 10-item questionnaire adapted into vernacular Telugu (Target score: $\ge 75/100$).
- **Time on Critical Path:** Duration from application launch to viewing diagnosis results.

### 5.2 Agronomic Diagnostic Validation Rubric (Expert Evaluation)
For every field image submitted by a farmer, a dual-blind review is performed by two independent agronomists:
- **Diagnostic Agreement Score:** Concordance between CropVision's top-1 prediction and independent expert laboratory diagnosis.
- **Abstention Appropriateness:** Percentage of ambiguous or low-quality images where CropVision appropriately absteined rather than hallucinating an incorrect disease.
- **Treatment Safety Score:** Expert rating on the appropriateness and CIBRC compliance of KrishiBrain IPM advice.

---

## 6. Pilot Risk Mitigation & Incident Response

- **Crop Hazard Safeguard:** If a farmer submits an image exhibiting rapid foliar necrosis or suspected quarantine pest (e.g., Fall Armyworm in sweet corn or invasive viral strains), the platform triggers an automatic `URGENT` notification to the district KVK nodal officer.
- **Device Support:** Facilitators carry backup power banks and hotspot routers to assist farmers with legacy battery or firmware configurations.
