# ACREVIA 50-Farmer Telangana Pilot: Eligibility & Recruitment Framework
## Participant Selection Criteria & Cohort Stratification
**Target Stage:** Stage 08 Remediation (`TASK-S08-01`)  
**Geographic Coverage:** Warangal and Nalgonda Districts, Telangana  
**Target Sample Size:** $N = 50$ Smallholder Farmers  

---

## 1. Eligibility Criteria

To ensure scientifically valid results that reflect representative smallholder conditions while ensuring safe field execution, the following criteria govern participant recruitment:

### 1.1 Inclusion Criteria
1. **Landholding Classification:** Small and marginal farmers operating between **1.0 acre and 5.0 acres** of total cultivated agricultural land.
2. **Target Crops:** Actively cultivating at least one of the three core ACREVIA crops:
   - **Cotton** (*Gossypium hirsutum* — Bt hybrid or desi cotton)
   - **Rice** (*Oryza sativa* — irrigated puddle or dry direct-seeded)
   - **Chilli** (*Capsicum annuum* — commercial red or green chilli)
3. **Geographic Proximity:** Farm plots situated within the operational jurisdiction of:
   - KVK Malyal (Warangal cluster: Malyal, Kuravi, Kesamudram mandals)
   - KVK Kampasagar (Nalgonda cluster: Tripuraram, Miryalaguda, Nereducherla mandals)
4. **Hardware & Connectivity:**
   - Personal ownership or household dedicated access to an Android smartphone running **Android 9.0 (Pie) or higher**.
   - Functional autofocus rear camera ($\ge 8\text{ MP}$ recommended).
   - Active SIM card with 2G/3G/4G cellular data plan.
5. **Language & Literacy:** Ability to understand spoken and written **Telugu** (or family proxy assistance for reading if semi-literate).
6. **Commitment:** Willingness to participate in a 30-day observational routine (2 observations per week), attend onboarding, and participate in exit interviews.

### 1.2 Exclusion Criteria
1. **Commercial Agribusinesses:** Large-scale commercial holdings ($> 10\text{ acres}$) or contract corporate farming ventures.
2. **Total Network Blackouts:** Farms located in deep signal dead zones with zero cell service reachable within a 5 km radius.
3. **Conflicting Chemical Trials:** Farms currently enrolled in active agrochemical pesticide registration trials where proprietary treatments would confound observational data.
4. **Transient Sharecroppers:** Farmers with insecure short-term verbal leases that may terminate before the 30-day pilot conclusion.

---

## 2. Cohort Stratification Matrix

Recruitment targets a balanced 50-farmer distribution across districts, crop types, and soil profiles:

| District | Target Mandal / KVK | Crop Allocation | Target Farmers | Soil Profile | Irrigation Source |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **Warangal** | Malyal / Kuravi / Kesamudram | Cotton (Bt) | 12 | Vertisols (Deep Black) | Borewell / Rainfed |
| | | Chilli (Red) | 8 | Vertisols / Mixed | Drip / Furrow |
| | | Rice | 5 | Heavy Clay / Vertic | Canal / Borewell |
| **Nalgonda** | Tripuraram / Miryalaguda | Rice (Paddy) | 13 | Clay Loam / Alluvial | NSP Canal / Borewell |
| | | Cotton | 7 | Alfisols (Red Sandy) | Rainfed / Borewell |
| | | Chilli | 5 | Red Sandy Loam | Drip / Micro-irrigation |
| **Total** | **6 Mandals / 2 KVKs** | **3 Crops** | **50** | **Diverse Telangana Soils** | **Representative Mix** |

---

## 3. Recruitment & Mobilization Process

```
Step 1: Institutional Engagement
└── Coordination with KVK Senior Scientists & District Agricultural Officers (DAOs).

Step 2: Rythu Vedika Village Meetings
└── Public announcements via Gram Panchayat & Rythu Bandhu Samithi coordinators.
└── 2 Open orientation meetings per cluster.

Step 3: Preliminary Screening & Field Audit
└── Extension officers verify farm boundaries, active crops, and smartphone compatibility.
└── Document baseline demographic survey.

Step 4: Formal Registration & Participant ID Issuance
└── Execution of trilingual informed consent.
└── System onboarding with anonymized ID allocation:
    - Warangal: `PILOT-WAR-001` through `PILOT-WAR-025`
    - Nalgonda: `PILOT-NAL-026` through `PILOT-NAL-050`
```

---

## 4. Demographic & Farm Baseline Record Template

Each recruited participant will have the following baseline record filed:

| Attribute | Collection Format | Validation Range |
| :--- | :--- | :--- |
| **Participant ID** | Alphanumeric | `PILOT-[WAR/NAL]-[001-050]` |
| **Farmer Name** | Text (Encrypted) | DPDP Private Storage |
| **Phone Number** | E.164 (+91) | Verified via OTP |
| **District & Mandal** | Categorical | Warangal / Nalgonda mandals |
| **Farm Latitude / Longitude** | WGS84 Decimal Degrees | Dithered to 2 decimal places ($\pm 1\text{ km}$) for privacy |
| **Total Landholding** | Numeric (Acres) | $1.0 \le \text{Acres} \le 5.0$ |
| **Target Crop & Variety** | Categorical / Text | e.g. Cotton (Bollgard II), Rice (BPT 5204 / RNR 15048), Chilli (Teja / Wonder Hot) |
| **Sowing / Transplanting Date** | ISO 8601 Date | Valid within current agricultural season |
| **Smartphone Model & OS** | Text | Model name, Android version, RAM |
