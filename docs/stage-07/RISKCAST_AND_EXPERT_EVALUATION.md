# ACREVIA — RiskCast & Expert Evaluation Report
## Empirical Validation of Agrometeorological Rules & Expert Review Governance

---

## 1. RiskCast Agrometeorological Rule Engine Evaluation

To evaluate RiskCast's accuracy in predicting biotic disease predisposition without generating false alarms, the rule engine was tested against calibrated environmental profiles representing Telangana agro-climatic extremes.

### 1.1 Test Scenario Matrix & Results

| Scenario ID | Target Crop | Environmental Profile | Injected Conditions | Expected RiskCast Output | Observed RiskCast Output | Evaluation Status |
|:---|:---|:---|:---|:---|:---|:---|
| `SCEN-01` | **Rice** (Panicle Initiation) | Saturated Humid Monsoon (Warangal) | Temp 24°C, RH 92%, Leaf Wetness 11h, 3 wet days | `HIGH` (Rice Blast: `RIC-BLST-01`) | `HIGH` (Rice Blast: `RIC-BLST-01`) | **PASSED** (Spindle lesion advisory triggered) |
| `SCEN-02` | **Cotton** (Vegetative) | Humid Cloudy Spell (Khammam) | Temp 28°C, RH 84%, Leaf Wetness 7h, 2 wet days | `HIGH` (Cercospora Leaf Spot: `COT-CLSP-01`) | `HIGH` (Cercospora Leaf Spot: `COT-CLSP-01`) | **PASSED** (Lower canopy scouting alert emitted) |
| `SCEN-03` | **Chilli** (Vegetative) | Dry Sunny Heatwave (Nalgonda) | Temp 34°C, RH 42%, Leaf Wetness 0h, 0 wet days | `HIGH` (Thrips & Murda: `CHL-THRP-01`) | `HIGH` (Thrips & Murda: `CHL-THRP-01`) | **PASSED** (Blue sticky trap & Neem oil advisory) |
| `SCEN-04` | **Rice** (Tillering) | Normal Clear Winter Day (Karimnagar) | Temp 27°C, RH 55%, Leaf Wetness 1h, 0 wet days | `LOW` (Routine Monitoring) | `LOW` (Routine Monitoring) | **PASSED** (No false alarms generated) |

### 1.2 Deduplication Efficiency
- In scenario testing with 10 repeated daily evaluations under identical continuous rainfall, the SHA-256 deduplication key (`farm_id:plot_id:threat:date:severity`) achieved **100% suppression of redundant alert records**, keeping the farmer's alert drawer uncluttered.

---

## 2. ExpertConnect Clinical Workflow Evaluation

The human-in-the-loop consultation pipeline was evaluated across three core operational metrics:

1. **RBAC Isolation:**
   - 10 unauthorized claim attempts by unverified farmers were simulated: **10/10 blocked with HTTP 403 Forbidden**.
2. **Clinical Dossier Integrity:**
   - Dossier retrieval assembled all 5 required multimodal artifacts:
     - High-resolution foliar image.
     - CropVision AI decision state, confidence, and entropy.
     - 3 relevant KrishiBrain literature citations.
     - Real-time weather observation metrics.
     - Farm/plot phenological context.
3. **Assessment Immutability & Revision Tracking:**
   - When an assessment was updated, the system successfully created an `ExpertAssessmentRevision` record.
   - 100% of previous assessment content was preserved in the immutable JSON snapshot.

---

## 3. Intervention Outcome Causality Protection

The Intervention Intelligence system was audited to ensure strict adherence to scientific causality principles:
- The system was tested across 15 post-intervention observation scenarios (e.g., biological sprays followed by weather changes).
- In 100% of responses, the platform displayed the explicit notice:
  > *"Observed visual changes reflect open-field biological progression and ambient conditions, not singular product causality."*
- Confounding variables (rainfall events, thermal stress, untracked soil dynamics) were recorded in 100% of outcome observations.
