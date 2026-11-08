# ACREVIA 30-Day Telangana Field Pilot: Final Evaluation Report
## Pre-Registered Scientific & Operational Evaluation Template
**Target Stage:** Stage 08 Remediation (`TASK-S08-01` / Evaluation Framework)  
**Study Period:** [Start Date: YYYY-MM-DD] to [End Date: YYYY-MM-DD]  
**Geographic Coverage:** Warangal and Nalgonda Districts, Telangana, India  
**Collaborating Institutions:** Krishi Vigyan Kendra (KVK) Malyal, KVK Kampasagar, PJTSAU & ACREVIA  
**Publication Status:** Pre-Registered Field Evaluation Report (Zero Fabricated Data)  

---

## 1. Executive Summary & Study Envelope

| Dimension | Planned Parameter | Actual Observed Result | Status |
| :--- | :--- | :--- | :---: |
| **Total Enrolled Farmers** | 50 Farmers (25 Warangal / 25 Nalgonda) | [_____] Farmers Completed | [ ] |
| **Total Field Observations** | $\ge 400$ Observations | [_____] Total Observations | [ ] |
| **Offline Sync Success Rate** | $\ge 99.0\%$ | [_____] % ($95\%\text{ CI: } [\_, \_]$) | [ ] |
| **Top-3 Diagnostic Concordance**| $\ge 85.0\%$ | [_____] % ($95\%\text{ CI: } [\_, \_]$) | [ ] |
| **System Usability Scale (SUS)**| Mean $\ge 75.0 / 100$ | Mean: [_____] $\pm$ [_____] | [ ] |
| **Critical Safety Incidents** | Exactly 0 incidents | [_____] Incidents | [ ] |
| **DPDP Privacy Breaches** | Exactly 0 breaches | 0 Breaches Recorded | [ ] |

---

## 2. Cohort Demographics & Baseline Characteristics

*Table 2.1: Enrolled Cohort Demographic Profile ($N = 50$)*

| Variable | Metric / Category | Warangal Cluster ($n=25$) | Nalgonda Cluster ($n=25$) | Combined Total ($N=50$) |
| :--- | :--- | :---: | :---: | :---: |
| **Mean Landholding** | Acres $\pm$ SD | [_____] $\pm$ [_____] | [_____] $\pm$ [_____] | [_____] $\pm$ [_____] |
| **Target Crop Enrolled** | Cotton (Bt) | [_____] | [_____] | [_____] |
| | Rice (Paddy) | [_____] | [_____] | [_____] |
| | Chilli (Capsicum) | [_____] | [_____] | [_____] |
| **Farmer Age Group** | $< 35$ Years | [_____] | [_____] | [_____] |
| | $35–50$ Years | [_____] | [_____] | [_____] |
| | $> 50$ Years | [_____] | [_____] | [_____] |
| **Literacy Profile** | Literate (Telugu reading) | [_____] | [_____] | [_____] |
| | Semi-literate (Family proxy) | [_____] | [_____] | [_____] |
| **Smartphone Android OS** | Android 9.0–11.0 | [_____] | [_____] | [_____] |
| | Android 12.0–14.0 | [_____] | [_____] | [_____] |

---

## 3. Systems Performance & Offline Resilience (Pillar 1)

*Table 3.1: Technical System & Sync Integrity Metrics*

| Metric ID | Description | Pre-Registered Target | Actual Realized Result | Gate Status |
| :--- | :--- | :---: | :---: | :---: |
| `M-TECH-01` | Offline Data Retention Rate (IndexedDB) | $100.0\%$ | [_____] % | [ ] PASS / [ ] FAIL |
| `M-TECH-02` | Synchronization Success Rate | $\ge 99.0\%$ | [_____] % | [ ] PASS / [ ] FAIL |
| `M-TECH-03` | PWA Crash-Free Sessions | $\ge 99.5\%$ | [_____] % | [ ] PASS / [ ] FAIL |
| `M-TECH-04` | Rate Limit False Positive Throttles | $< 0.1\%$ | [_____] % | [ ] PASS / [ ] FAIL |
| `M-TECH-05` | Median End-to-End API Latency | $< 500\text{ ms}$ | [_____] ms | [ ] PASS / [ ] FAIL |
| `M-TECH-06` | 95th Percentile API Latency | $< 1500\text{ ms}$ | [_____] ms | [ ] PASS / [ ] FAIL |

*Technical Narrative & Infrastructure Notes:*  
[Insert discussion of Redis rate limiter behavior, Vercel edge runtime observations, and cellular network transitions observed during field trials.]

---

## 4. Machine Learning & Pathology Diagnostic Accuracy (Pillar 2)

*Table 4.1: Computer Vision Model Performance vs Blinded KVK Ground Truth ($n = [\_]$)*

| Crop | Evaluated Samples | Top-1 Concordance (95% CI) | Top-3 Concordance (95% CI) | ECE (Calibration) |
| :--- | :---: | :---: | :---: | :---: |
| **Cotton** | [_____] | [_____]% ($[\_, \_]$) | [_____]% ($[\_, \_]$) | [_____] |
| **Rice** | [_____] | [_____]% ($[\_, \_]$) | [_____]% ($[\_, \_]$) | [_____] |
| **Chilli** | [_____] | [_____]% ($[\_, \_]$) | [_____]% ($[\_, \_]$) | [_____] |
| **Overall Model** | **[_____]** | **[_____]% ($[\_, \_]$)** | **[_____]% ($[\_, \_]$)** | **[_____]** |

*Table 4.2: Out-of-Distribution (OOD) Quality Filter Performance*
- Total Images Evaluated: `[_____]`
- True In-Distribution Captures Accepted: `[_____]`
- True OOD / Poor Quality Images Rejected: `[_____]`
- False Rejection Rate (Valid leaves rejected): `[_____]%` (Target $< 8.0\%$)
- False Acceptance Rate (Blur/dirt accepted): `[_____]%` (Target $< 2.0\%$)

---

## 5. KrishiBrain RAG & Agronomic Quality (Pillar 3)

*Table 5.1: RAG Evaluation Matrix ($n = 50$ Sampled Responses)*

| Dimension | Target Standard | Observed Metric | Outcome |
| :--- | :---: | :---: | :---: |
| **PJTSAU Alignment Score (1–5)** | $\ge 4.5 / 5.0$ | [_____] / 5.0 | [ ] MET |
| **Inter-Rater Reliability ($\kappa$)** | $\kappa \ge 0.75$ | $\kappa =$ [_____] | [ ] MET |
| **Citation Grounding Rate** | $100.0\%$ | [_____] % | [ ] MET |
| **Chemical Safety Violations** | Exactly 0 | [_____] Violations | [ ] MET |
| **Mandatory PPE Inclusions** | $100.0\%$ | [_____] % | [ ] MET |

---

## 6. Farmer Usability & Adoption Findings (Pillar 4)

*Table 6.1: System Usability Scale (SUS) Score Distribution*
- Mean Cohort SUS: `[_____]` $\pm$ `[_____]` (Target $\ge 75.0$)
- Median SUS: `[_____]` (IQR: `[_____] – [_____]`)
- One-Sample t-test ($H_0: \mu \le 68.0$): $t = [\_]$, $p = [\_]$

*Table 6.2: Behavioral Adoption Metrics*
- Total KrishiBrain Q&A Queries: `[_____]`
- Voice Input Modality Ratio: `[_____]%` (Target $\ge 40.0\%$)
- Independent Task Completion Rate: `[_____]%` (Target $\ge 85.0\%$)
- Self-Reported Perceived Loss Prevention: `[_____]%` of cohort (Target $\ge 75.0\%$)

---

## 7. Incident Log & Escalations

| Incident ID | Date | Severity | Description | Containment / Action Taken | Resolved (Y/N) |
| :--- | :---: | :---: | :--- | :--- | :---: |
| `INC-001` | [Date] | [SEV-X] | [Description of incident] | [Resolution actions] | [ ] |

---

## 8. Limitations & Recommendations for Scaled Deployment

### 8.1 Methodological Limitations
1. **Seasonal Duration:** 30 days covers a single crop phenological window rather than full seed-to-harvest lifecycle.
2. **Causal Attribution:** Yield outcomes are observational and self-reported; randomized multi-season trials are required for formal yield impact claims.
3. **Hardware Constraints:** Trial was conducted on Android smartphones; iOS performance was not evaluated.

### 8.2 Architectural & Engineering Recommendations
- [Detail any recommended updates to model quantization, cache TTLs, or vernacular prompts based on observed field friction.]

---

## 9. Final Sign-Off & Approvals

**Lead Agronomist, KVK Malyal:** __________________________________ Date: ______________  
**Lead Pathologist, KVK Kampasagar:** _____________________________ Date: ______________  
**Principal AI Architect, ACREVIA:** _______________________________ Date: ______________  
**Data Protection Officer, ACREVIA:** ______________________________ Date: ______________  
