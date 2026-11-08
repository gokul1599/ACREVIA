# ACREVIA — EXPERTCONNECT VALIDATION REPORT
## Clinical Workflow, Multimodal Dossiers, Certified Agronomist Reviews & Revision Audit

**Platform Identity:** ACREVIA — Agricultural Intelligence Platform  
**Subsystem:** ExpertConnect Certified Agronomist Review Network  
**Target User Persona:** Agricultural Extension Officers (KVKs), University Plant Pathologists (PJTSAU), Field Agronomists  
**Evaluation Date:** November 2026  
**Auditor:** Principal Human-in-the-Loop AI Architect & Systems Governance Specialist  
**Validation Status:** WORKFLOW VERIFIED / PANEL ENROLLMENT PENDING  

---

## 1. Executive Summary & Clinical Governance

ExpertConnect is ACREVIA's human-in-the-loop clinical tele-agronomy network. It allows certified agricultural scientists and extension specialists to inspect ambiguous, high-severity, or model-abstained crop disease cases and deliver certified IPM management plans to farmers.

### Architectural Governance Principles
1. **No Self-Declared Agronomists:** Public registration cannot grant `AGRICULTURAL_EXPERT` privileges. Candidate accounts undergo formal administrative verification.
2. **Immutable Clinical Findings:** Certified assessments cannot be silently overwritten or modified in-place; all edits generate versioned revision records.
3. **Training Set Isolation:** Expert-submitted diagnoses are strictly quarantined from active ML model weights to prevent unvalidated self-reinforcing bias loops.

---

## 2. Expert Credentialing & Onboarding Lifecycle

Expert accounts follow a strict 5-stage verification state machine:

```text
[ APPLICATION_SUBMITTED ]
           |
           v (Admin Reviews Academic Degrees & Registration)
    [ UNDER_REVIEW ]
      /           \
     v             v
[ APPROVED ]   [ REJECTED ]
     |
     v (Disciplinary or License Invalidation)
[ SUSPENDED / REVOKED ]
```

### 2.1 Verification Gate Audit
- Candidates submit academic credentials (B.Sc., M.Sc., Ph.D. in Agriculture / Pathology / Entomology), university/institute affiliation (e.g., PJTSAU, ICAR, KVK), state council registration numbers, and assigned district jurisdictions.
- Admin reviews application details via `/api/v1/expertconnect/admin/verify/{profile_id}`.
- Upon approval, the user's role is elevated to `AGRICULTURAL_EXPERT` and audit-logged in `audit_logs`.
- Verified in `test_authorization.py`, `test_stage7.py`, and `test_stage8_e2e.py`.

---

## 3. Clinical Case Triage & Multimodal Evidence Dossiers

When a farmer's observation requires human expertise (either requested directly or escalated automatically due to CropVision abstention $< 0.65$ confidence):

### 3.1 Triage Queue Lifecycle
Cases transition through: `QUEUED` &rarr; `ASSIGNED` (claimed by an authorized agronomist) &rarr; `IN_REVIEW` &rarr; `COMPLETED`.

### 3.2 Multimodal Dossier Components
Agronomists inspect a comprehensive evidence package assembled dynamically by `expert_service.py`:
1. **Foliar Visual Evidence:** High-resolution photographs with quality metrics (Laplacian blur score, luminance).
2. **CropVision AI Analysis:** Model version, top-3 differential diagnosis candidates with calibrated probability distributions, and Grad-CAM saliency heatmaps highlighting suspected necrotic regions.
3. **KrishiBrain Grounded Citations:** University reference chapters and CIBRC chemical tables relevant to the crop.
4. **Agrometeorological Context:** 7-day ambient temperature, relative humidity, precipitation, and Leaf Wetness Hours ($LWH$).
5. **Crop Metadata:** Farm name, mandal/village, sowing date, phenological stage (e.g., Vegetative, Flowering, Boll formation), and irrigation source.

---

## 4. Assessment Submission & Immutable Revision History

### 4.1 Certified Assessment Structure
Upon completing review, the agronomist authors an authoritative finding:
- **Confirmed Crop & Primary Pathology:** Scientific classification (e.g., *Cercospora gossypina*).
- **Differential Diagnoses:** Ruled-out conditions (e.g., *Alternaria macrospora*, Bacterial Blight).
- **Clinical Severity & Confidence:** Severity (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`), Confidence ($1$–$5$ scale).
- **Comprehensive IPM Strategy:**
  - *Cultural Controls:* Canopy thinning, sanitation, drainage, aeration.
  - *Biological Controls:* Bio-agents (e.g., *Trichoderma viride*, *Pseudomonas fluorescens*).
  - *Approved Chemical Controls:* Exact CIBRC registered fungicides/insecticides, dilution dosages, Pre-Harvest Interval (PHI) in days, and Re-Entry Interval (REI) in hours.

### 4.2 Revision Auditability
If new field scouting data emerges or a diagnosis is updated:
- The agronomist submits a PUT request with `revision_reason`.
- The prior assessment state is serialized into JSON and stored in `expert_assessment_revisions`.
- The `revision_count` is incremented.
- The prior history remains accessible to administrative audit logs, preserving scientific integrity.

---

## 5. Machine Learning Quarantining & Data Governance

A common vulnerability in agricultural AI platforms is immediately feeding human expert corrections into retraining datasets without independent laboratory validation.
- ExpertConnect assessments are stored in the application database (`expert_assessments`).
- They do **not** automatically alter model weights or re-index vector collections.
- Promotion of field cases to future model training sets requires explicit farmer research consent, dual-expert validation, and formal inclusion in a versioned dataset datasheet.

---

## 6. Real Expert Engagement Status

To maintain uncompromising truthfulness:
- **Platform Capability:** Fully implemented, end-to-end tested, and operationally verified with realistic agronomist test fixtures.
- **Field Expert Panel:** While the technical portal and workflow are complete, a permanent full-time cadre of KVK / PJTSAU extension officers has not yet been onboarded for 24/7 commercial operations.
- **Operational Status:** **`PLATFORM_VERIFIED_READY` / `FORMAL_FIELD_PANEL_ENROLLMENT_PENDING`**.

**ExpertConnect Validation Verdict:** **PASSED — SYSTEM READY FOR CONTROLLED FIELD PILOT DEPLOYMENT.**
