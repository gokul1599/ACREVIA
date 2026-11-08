# STAGE 02 — ANNOTATION QUALITY & LABEL GOVERNANCE SPECIFICATION
## Double-Blind Review Protocols, Agronomist Validation & Diagnostic Certainty States

**Stage:** 02 — Agricultural Dataset Engineering & Taxonomy Validation  
**Core Modules:** [`annotation_schema.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/annotations/annotation_schema.py), [`expert_review.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/annotations/expert_review.py)  
**Status:** Approved Label Governance Specification  

---

### 1. The 7 Canonical Annotation Lifecycle States

Labels assigned to agricultural photographs progress through an explicit governance lifecycle:

```
[Raw Image Ingestion]
         │
         ▼
    UNREVIEWED ───────────────► Fails Quality Gate ──────────► REJECTED_QUALITY
         │
         ▼
     ANNOTATED (Preliminary source or field-collector label)
         │
         ▼
  REVIEW_PENDING (Assigned to certified university agronomist)
         │
         ├───► Agrees with High Certainty ──────────────────► EXPERT_VERIFIED (Admitted to Training)
         │
         ├───► Diagnostic Ambiguity / Conflicting Evidence ──► DISPUTED (Escalated to Senior Panel)
         │
         └───► Foliar Symptoms Insufficient ────────────────► INSUFFICIENT_EVIDENCE (Quarantined)
```

---

### 2. Multi-Tier Diagnostic Certainty Levels

Agronomists reviewing candidate foliar images must record an explicit certainty rating:

1. **`CERTAIN`:** Diagnostic lesions are classic, unambiguous, and corroborated by secondary symptoms (e.g. concentric target rings in Alternaria spot, or distinct acervuli in Chilli Anthracnose). Microscope verification noted if laboratory assay was performed.
2. **`PROBABLE`:** Symptoms are consistent with the pathology but slight chlorosis or atypical foliar positioning introduces mild ambiguity. Admissible to training with lower sample weight.
3. **`INCONCLUSIVE`:** Foliar symptoms exhibit mixed patterns (e.g. nutritional deficit co-occurring with sap-sucking pest damage). Excluded from single-label classification training; archived for multi-pathology research.

---

### 3. Reviewer Audit Trail & Anonymization

To preserve data integrity while protecting expert privacy:
* Every review record ([`ExpertReviewRecord`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/annotations/annotation_schema.py)) archives the expert's institutional affiliation and anonymized hash (`expert_id_hash`).
* Mandatory revision entries ([`LabelRevisionEntry`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/annotations/annotation_schema.py)) record the previous label, new label, role, botanical rationale, and timestamp.
* Labels cannot be modified without generating an immutable audit entry.
