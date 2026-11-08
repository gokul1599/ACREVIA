# STAGE 07 — RISKCAST, EXPERTCONNECT, DIFFERENTIAL DIAGNOSIS & INTERVENTION TRACKING
## Independent Technical Audit Report

**Audit Target:** Stage 07 — Agricultural Risk Intelligence, Expert Review Network & Intervention Outcome Tracking  
**Auditor:** Agricultural Risk Modelling Scientist & Agronomic Operations Lead  
**Audit Date:** 2026-11-08T18:51:00+05:30  
**Overall Stage Status:** **`COMPLETE_VERIFIED`**  

---

### Audit objective

Determine whether ACREVIA can manage agricultural risk, expert review and intervention history without fabricating diagnoses or treatment effectiveness.

---

### 07.1 RiskCast epidemiological engine

#### 1. Rule Architecture & Grounding
- **Data Models:** [`RiskRule`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/app/models/risk_rule.py), [`RiskAlert`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/app/models/risk_alert.py), [`RiskAssessmentRecord`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/app/models/risk_assessment.py).
- **PJTSAU Grounded Rules:** 6 standard epidemiological disease rules seeded in database:
  - `RIC-BLST-01`: Rice Blast (*Magnaporthe oryzae*) triggered by night temp $< 20^\circ\text{C}$ and $RH > 90\%$.
  - `COT-CLSP-01`: Cotton Bacterial Blight (*Xanthomonas*) triggered by high temp and overcast humidity.
  - `CHL-ANTH-01`: Chilli Anthracnose Fruit Rot (*Colletotrichum*) triggered by rain splash and high humidity.
- **Trilingual Advisories:** Every rule stores verified advisory text across `advisory_en`, `advisory_te` (Telugu), and `advisory_hi` (Hindi).
- **Epistemic Limitation Disclaimer:** Every plot evaluation includes a mandatory limitations notice: *"This assessment represents an epidemiological risk indicator based on weather and crop stage; it is NOT a confirmed biological disease outbreak."*
- **Alert Deduplication:** Active alerts are deduplicated by `(rule_code, plot_id, is_active)` to prevent redundant notification blasts.
- **Test Evidence:** [`backend/tests/test_stage7.py::test_riskcast_seeded_rules_and_query`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_stage7.py#L20-L46) and `test_riskcast_plot_evaluation_and_alerts`.

---

### 07.2 ExpertConnect consultation network

#### 1. Expert Registry & Credential Governance
- **Data Models:** [`ExpertProfile`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/app/models/expert_profile.py), [`ExpertReviewCase`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/app/models/expert_case.py), [`ExpertAssessment`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/app/models/expert_assessment.py).
- **Verification Workflow:** Agronomists register credentials (`institution`, `qualification_degree`, `specialization`, `license_number`). Only admins can approve (`verification_status = "VERIFIED"`).
- **RBAC Authorization:** Regular farmer accounts attempting to submit expert diagnostic reviews receive `HTTP 403 Forbidden` ([`backend/tests/test_diagnoses.py::test_farmer_cannot_submit_expert_review`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_diagnoses.py#L90-L105)).
- **Case State Machine:** `PENDING_REVIEW` $\to$ `ASSIGNED` $\to$ `IN_PROGRESS` $\to$ `COMPLETED` / `REJECTED`. Revisions preserve complete audit trails.
- **Test Evidence:** [`backend/tests/test_stage7.py::test_expertconnect_application_and_admin_verification`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_stage7.py#L95-L135).

---

### 07.3 Differential diagnosis & human escalation

- **Candidate Evaluation:** When computer vision inference exhibits ambiguity (top confidence $< 0.85$ or normalized entropy $> 0.65$), the system generates a ranked differential diagnosis list with candidate causes, confidence scores, and missing observation requests.
- **Human-in-the-Loop Hand-off:** An `ExpertReviewCase` is created automatically, packaging the image, EXIF metadata, crop stage, and telemetry for agronomist review.

---

### 07.4 Intervention journal & product provenance

- **Data Model:** [`InterventionRecord`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/app/models/intervention.py).
- **Attributes Captured:** `intervention_type` (`CHEMICAL_PESTICIDE`, `BIO_CONTROL`, `FERTILIZER`, `IRRIGATION`, `CULTURAL`), `chemical_name`, `active_ingredient`, `brand_name`, `dosage`, `unit`, `water_volume_liters`, `application_method`, `cost_inr`, `source_of_instruction`.
- **Integrity:** Records are linked to the specific plot and crop season, establishing an immutable field journal.

---

### 07.5 Food safety: Pre-Harvest (PHI) & Re-Entry Intervals (REI)

- **PHI Tracking:** Pre-Harvest Interval (in days) stored on every chemical intervention. A harvest operation scheduled within an unexpired PHI is automatically flagged with an active safety violation.
- **REI Tracking:** Restricted-Entry Interval (in hours) stored on interventions. Farm labor tasks within the REI window require personal protective equipment (PPE) warnings.

---

### 07.6 Outcome tracking & scientific non-causality disclaimer

- **Data Model:** [`OutcomeObservation`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/app/models/intervention.py#L65-L100).
- **Provenance Disaggregation:** Explicitly distinguishes `provenance` (`FARMER_REPORTED`, `EXPERT_VERIFIED`, `MEASURED`).
- **Effectiveness Categories:** `HIGHLY_EFFECTIVE`, `MODERATELY_EFFECTIVE`, `NO_APPARENT_EFFECT`, `ADVERSE_PHYTOTOXICITY`.
- **Correlation vs Causation Disclaimer:** Verified present in all responses: *"Reported recovery represents field correlation; treatment effectiveness cannot be scientifically inferred from an uncontrolled before/after observation without controlled trials."*

---

### 07.7 Stage 07 acceptance verification

- [x] RiskCast implementation verified with 6 PJTSAU rules (`TEST_EXECUTED`).
- [x] Risk provenance retained with limitations disclaimer (`TEST_EXECUTED`).
- [x] Alerts and deduplication tested (`TEST_EXECUTED`).
- [x] Expert registry verified with admin approval workflow (`TEST_EXECUTED`).
- [x] Credentials verified; unauthorized farmer review submissions blocked (`TEST_EXECUTED`).
- [x] Differential diagnosis and case escalation tested (`TEST_EXECUTED`).
- [x] Human review workflow functional (`TEST_EXECUTED`).
- [x] Intervention journal functional with dosage and cost tracking (`TEST_EXECUTED`).
- [x] PHI/REI safeguards verified (`TEST_EXECUTED`).
- [x] Outcome provenance retained (`TEST_EXECUTED`).
- [x] CropPulse timeline integration functional (`TEST_EXECUTED`).

**Stage 07 Audit Determination:** `COMPLETE_VERIFIED` (Fully implemented, tested, and operational).
