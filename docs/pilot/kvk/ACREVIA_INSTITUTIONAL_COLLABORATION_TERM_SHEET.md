# ACREVIA — INSTITUTIONAL COLLABORATION TERM SHEET
## NON-BINDING RESEARCH COLLABORATION, SCIENTIFIC GOVERNANCE & DATA RIGHTS OUTLINE

> [!IMPORTANT]
> **LEGAL & INSTITUTIONAL DISCLAIMER:**  
> **PROPOSED WORKING DRAFT — SUBJECT TO INSTITUTIONAL AND LEGAL REVIEW**  
> This document is an internal preparatory term sheet outline for research collaboration between the ACREVIA initiative and participating agricultural institutions (KVK Malyal, KVK Kampasagar, and PJTSAU). It does **NOT** constitute an executed legal contract, binding agreement, or formal Memorandum of Understanding (MoU). All provisions remain subject to formal review and institutional negotiation.

---

### Term Sheet Summary

| Parameter | Provisional Research Term |
|---|---|
| **Nature of Collaboration** | Non-commercial academic technology evaluation & supervised field research |
| **Proposed Institutions** | Krishi Vigyan Kendra (KVK) Malyal; KVK Kampasagar; PJTSAU Directorate of Extension |
| **Provisional Cohort** | 20–30 Smallholder Farmers per KVK (1 Village Cluster per KVK) |
| **Provisional Duration** | 30 Calendar Days (Supervised Feasibility & Workflow Evaluation) |
| **Participation Fee Model** | No-participation-fee model for KVKs and participating farmers |
| **Data Protection Standard** | Digital Personal Data Protection (DPDP) Act, 2023 alignment |
| **Regulatory Compliance** | CIBRC statutory label compliance; human agronomist override |

---

## 1. Non-Commercial Academic Research Positioning

ACREVIA is positioned strictly as an open-access, zero-cost agricultural intelligence research and decision-support platform. 
- The collaboration is designed to assess the feasibility, usability, and workflow integration of deep computer vision diagnostics ([CropVision](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/integrations/ml_client.py)), multilingual retrieval-augmented generation ([KrishiBrain RAG](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/knowledge.py)), and microclimate risk forecasting ([RiskCast](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/riskcast.py)) under frontline extension conditions.
- The platform will **NOT** be commercialized, marketed, or used for commercial input sales, credit scoring, or advertising during or following the pilot.

---

## 2. Financial Model & Transparent Cost Allocation

ACREVIA proposes a **no-participation-fee model** for the agreed pilot:
- **No Fees for KVKs or Farmers:** No financial charges, subscription fees, or license costs will be levied on participating KVKs, university scientists, or smallholder farmers.
- **Infrastructure Cost Responsibility:** ACREVIA provides cloud hosting, compute, vector database storage, and AI inference capacity using verified free-tier architectures.
- **Operating & Field Expenses:** The parties must explicitly document and mutually agree upon the allocation of any local operating expenses (e.g., travel for field training, specialized physical soil/leaf sampling kits, cellular connectivity recharge) prior to field deployment. No financial obligation will be imposed on a participating KVK or farmer without prior written agreement.
- **Future Sustainability Note:** Permanent zero-cost operation cannot be unconditionally guaranteed beyond the trial period; future sustainability will depend on grant funding, open research support, or public university hosting.

---

## 3. Provisional Study Scope & Feasibility Designation

The proposed field trial is formally designated as:
**"30-Day Supervised Agricultural Technology Feasibility and Workflow Evaluation"**

- **Cohort Scale:** Provisioally planned for **20 to 30 smallholder farmers per KVK**, selected across one representative village cluster in Mahabubabad (Cotton/Chilli) and Nalgonda (Rice/Cotton).
- **Feasibility Focus:** This 30-day evaluation is designed to evaluate technical feasibility, mobile usability in low-bandwidth rural networks, image capture quality, offline synchronization reliability, and scientist review workload. It is **NOT** powered or claimed as a definitive clinical validation of disease-detection accuracy.

---

## 4. Scientist-in-the-Loop Supervision & Clinical Adjudication

To ensure complete agricultural safety:
1. **Decision Hierarchy:** KVK Subject Matter Specialists (Plant Protection, Agronomy) retain ultimate authority over all diagnostic and advisory outputs.
2. **Clear Output Categorization:** All user interfaces strictly distinguish between:
   - *Automated Model Prediction:* An AI estimate accompanied by class confidence scores, Grad-CAM visual heatmaps, and explicit uncertainty notices.
   - *Expert-Reviewed Diagnosis:* A human agronomist assessment verified through the [ExpertConnect portal](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/expertconnect.py).
   - *Confirmed Ground Truth:* A lab-verified or on-station confirmed pathological finding.
3. **Escalation Triggers:** Low model confidence ($< 0.60$), out-of-distribution non-plant imagery, narrow prediction margins between multiple diseases, or suspected high-risk quarantine pests automatically trigger mandatory expert review.

---

## 5. Comprehensive Data Rights & Permissions Matrix

To prevent ambiguity, data rights, ownership, and permitted processing purposes are partitioned across ten distinct asset classes:

```
+====================================================================================================================================================+
| ACREVIA DATA RIGHTS, PERMISSIONS & GOVERNANCE MATRIX                                                                                               |
+----+----------------------------+-----------------------+-----------------------+--------------------------+--------------------+------------------+
| #  | Data Category              | Data Originator       | Controller / Processor| Permitted Purpose        | Access Rights      | Retention Policy |
+----+----------------------------+-----------------------+-----------------------+--------------------------+--------------------+------------------+
| 01 | Farmer Personal Identity   | Participating Farmer  | ACREVIA (Fiduciary)   | Account auth & contact   | Farmer & ACREVIA   | Purged upon exit |
|    | (Name, Phone, Village)     |                       |                       |                          | (Encrypted TLS/DB) | (within 48h opt) |
+----+----------------------------+-----------------------+-----------------------+--------------------------+--------------------+------------------+
| 02 | Farm Geospatial Boundary   | Participating Farmer  | ACREVIA (Storage)     | Satellite pixel window   | Farmer & Agronomist| Purged on exit;  |
|    | (Polygon Coordinates)      | & Extension Officer   |                       | extraction only          | (Never published)  | Never monetized  |
+----+----------------------------+-----------------------+-----------------------+--------------------------+--------------------+------------------+
| 03 | Leaf & Crop Images         | Participating Farmer  | ACREVIA & KVK Experts | Diagnostic inference     | Farmer, KVK, &     | De-identified    |
|    | (Camera Photos)            |                       |                       | & model refinement       | Research Archive   | academic archive |
+----+----------------------------+-----------------------+-----------------------+--------------------------+--------------------+------------------+
| 04 | Crop Observation Notes     | Participating Farmer  | ACREVIA & KVK Experts | Agronomic context        | Farmer & KVK       | Crop Season      |
|    | (Symptoms, Crop Age)       |                       |                       |                          | (Confidential)     | (120 days)       |
+----+----------------------------+-----------------------+-----------------------+--------------------------+--------------------+------------------+
| 05 | AI Diagnostic Predictions  | ACREVIA CropVision    | ACREVIA Engine        | Farmer decision support  | Farmer & KVK       | Audit log        |
|    | (Probabilities, Heatmaps)  |                       |                       | & verification           | (Transparent)      | (Encrypted)      |
+----+----------------------------+-----------------------+-----------------------+--------------------------+--------------------+------------------+
| 06 | Expert Clinical Notes      | KVK Agronomist        | KVK & ACREVIA         | Verified advice & ground | Farmer, KVK,       | Joint Research   |
|    | (Diagnosis, Recommendations|                       |                       | truth calibration        | & ACREVIA          | Record           |
+----+----------------------------+-----------------------+-----------------------+--------------------------+--------------------+------------------+
| 07 | Derived Spatial Analytics  | ACREVIA Engine        | ACREVIA Engine        | Macro-level risk rules   | Aggregated         | Indefinite       |
|    | (Zonal NDVI, Risk Indices) |                       |                       | (RiskCast)               | (Anonymized)       | (De-identified)  |
+----+----------------------------+-----------------------+-----------------------+--------------------------+--------------------+------------------+
| 08 | De-Identified Dataset      | Joint Research        | Jointly Governed      | Academic publication     | Open Agricultural  | Indefinite       |
|    | (Anonymized Benchmarks)    | Collaboration         | (PJTSAU / ACREVIA)    | & benchmark refinement   | Science Archive    | (Public Good)    |
+----+----------------------------+-----------------------+-----------------------+--------------------------+--------------------+------------------+
| 09 | Software & Model IP        | ACREVIA Engineering   | ACREVIA Initiative    | Platform operation       | ACREVIA Initiative | Proprietary/Open |
|    | (Codebase, Weights)        |                       |                       |                          |                    | Research         |
+----+----------------------------+-----------------------+-----------------------+--------------------------+--------------------+------------------+
| 10 | Institutional Research IP  | KVK / PJTSAU          | PJTSAU University     | Frontline extension      | PJTSAU / KVK       | University       |
|    | (Package of Practices)     |                       |                       | & academic reporting     |                    | Statutory Rights |
+----+----------------------------+-----------------------+-----------------------+--------------------------+--------------------+------------------+
```

---

## 6. Qualified 48-Hour Right-to-Erasure Protocol

- **Operational Target:** ACREVIA establishes an operational target of executing verified personal data deletion requests within **48 hours** of receiving participant withdrawal.
- **Qualified Limitations:** Complete erasure applies to live operational PostgreSQL records, active session tokens, and primary object storage. Residual log fragments and point-in-time database backups (PITR) roll off according to their automated 7-day lifecycle. Data shared with approved third-party model processors (GroqCloud transient inference) is stateless and not retained upstream.
- **Non-Personal Data Retention:** De-identified, anonymized agronomic imagery containing zero personal metadata or farm coordinates may be retained in public research datasets for agricultural science advancement, subject to participant consent.

---

## 7. Contribution-Based Academic Authorship & Intellectual Property

- **Scientific Authorship:** Authorship on all resulting scientific whitepapers, conference papers, and validation reports will be determined strictly in accordance with **International Committee of Medical Journal Editors (ICMJE) / ICAR academic contribution guidelines**.
- **Equal Partnership:** KVK scientists who contribute to study design, ground-truthing, clinical adjudication, and data analysis will hold full joint co-authorship. Institutional participation alone does not automatically guarantee authorship without scientific contribution.
- **Negative Results Disclosure:** Both parties commit to the transparent publication of all findings, including diagnostic failure modes, model abstention rates, and technical limitations.
- **Pre-Existing IP:** Neither party acquires any right, title, or interest in the pre-existing intellectual property, models, or institutional publications of the other.

---

## 8. Chemical Safety & CIBRC Regulatory Compliance

- **Label Claim Adherence:** All crop protection recommendations must strictly comply with the Central Insecticide Board & Registration Committee (CIBRC) approved label claims and the PJTSAU *Vyavasaya Panchangam*.
- **Automated Abstention:** Inquiries involving off-label uses, unapproved tank mixtures, or highly hazardous chemicals (WHO Class Ia/Ib) automatically trigger the `REQUIRES_EXPERT_REVIEW` abstention gate, blocking automated guidance and alerting KVK scientists.

---

## 9. Participant Withdrawal vs. Institutional MoU Termination

A critical distinction is established between individual participant withdrawal and institutional contract termination:

1. **Individual Farmer Withdrawal (Immediate):**
   - Any participating farmer may withdraw from the pilot at any time, for any reason, without penalty or loss of extension services.
   - Withdrawal takes effect immediately upon verbal or in-app notice, triggering data access revocation and initiating the 48-hour erasure process.
2. **Institutional Collaboration Termination (30-Day Notice):**
   - Either participating KVK, PJTSAU, or ACREVIA may terminate the research collaboration agreement by providing **30 calendar days' written notice** to the other parties.
   - Termination of the institutional MoU does not retroactively compromise published research data or require immediate destruction of de-identified academic findings.
3. **Immediate Safety Suspension:**
   - Either party may immediately suspend field activities without notice if a critical agronomic safety hazard, severe ethical breach, or significant data vulnerability is identified.

---

## 10. Regulatory & Scientific Disclaimers

> [!CAUTION]
> **ACREVIA IS PROPOSED AS A RESEARCH DECISION-SUPPORT TOOL.**  
> It does not constitute a certified statutory agricultural diagnostic authority, an official seed/fertilizer testing laboratory, or an infallible advisory service. Recommendations generated by the platform do not replace qualified agronomist inspection or official state agricultural advisories. Neither ACREVIA nor the participating KVKs guarantee specific crop yields, pest eradication, or financial outcomes.

---

## 11. Qualified Legal & Institutional Review Requirements

This term sheet outline requires review and formal approval by:
1. Legal Counsel / Data Protection Officer (verifying DPDP Act 2023 compliance).
2. Directorate of Extension, PJTSAU (verifying university research protocols).
3. Project Leadership / Platform Owner (executing formal collaboration charter).
