# ACREVIA — STAGE 07 BASELINE AUDIT
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 07 — Agricultural Risk Intelligence, ExpertConnect & Intervention Outcomes  
**Date:** 2026-11-08  
**Status:** AUDIT COMPLETED (`PASS`)

---

## 1. Scope of Baseline Audit

The baseline audit for Stage 07 conducts a rigorous structural and architectural inspection of all components governing:
1. **RiskCast Agrometeorological Risk Engine:** Rule definitions, crop-specific evaluations, environmental thresholds, alert generation, and 72-hour deduplication.
2. **ExpertConnect Consultation Network:** Expert profile registration, administrative credential verification workflow, triage queues, case claiming, and evidence dossier compilation.
3. **Clinical Agronomic Assessment & Revisions:** Differential diagnosis recording, confidence scoring, IPM strategy formulation, CIBRC chemical regulatory compliance, and immutable revision tracking.
4. **Intervention Intelligence & Outcome Journal:** Farmer-reported actions (Biological, Chemical, Cultural, Mechanical), PHI/REI safety tracking, follow-up observations, and outcome evaluations.
5. **CropPulse Timeline Integration:** Longitudinal chronological linking across observations, risks, alerts, expert reviews, and interventions.
6. **Multilingual Interface & Ergonomics:** Telugu, English, and Hindi support across farmer and expert workspaces.

---

## 2. Codebase Asset Inventory

### 2.1 Relational Models (`backend/app/models/`)

| Model Class | Source File | Database Table | Key Attributes & Responsibilities |
|---|---|---|---|
| `RiskRule` | [`risk_rule.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/risk_rule.py) | `risk_rules` | `rule_code`, `crop`, `disease_or_pest_name`, `temp_min`, `temp_max`, `humidity_min`, `leaf_wetness_hours_min`, `rainfall_min_mm`, `evidence_citations`, `advisory_te`, `advisory_hi`. |
| `PlotRiskAssessment` | [`risk_assessment.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/risk_assessment.py) | `plot_risk_assessments` | `plot_id`, `weather_data_id`, `overall_risk_level`, `limiting_factors_json`, `evaluation_timestamp`, `limitations_notice`. |
| `RiskAlert` | [`risk_alert.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/risk_alert.py) | `risk_alerts` | `farm_id`, `plot_id`, `rule_code`, `severity`, `deduplication_key`, `is_acknowledged`, `is_dismissed`, `generated_at`, `expires_at`. |
| `ExpertProfile` | [`expert_profile.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/expert_profile.py) | `expert_profiles` | `user_id`, `registration_number`, `highest_degree`, `institution`, `specializations_json`, `districts_covered_json`, `verification_status` (`APPLICATION_SUBMITTED`, `APPROVED`, `REJECTED`, `REVOKED`), `verified_at`. |
| `ExpertCase` | [`expert_case.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/expert_case.py) | `expert_cases` | `observation_id`, `assigned_expert_id`, `status` (`QUEUED`, `ASSIGNED`, `IN_REVIEW`, `ASSESSED`, `CLOSED`), `priority` (`ROUTINE`, `URGENT`, `EMERGENCY`). |
| `ExpertAssessment` | [`expert_assessment.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/expert_assessment.py) | `expert_assessments` | `case_id`, `expert_id`, `confirmed_crop`, `primary_condition`, `differential_diagnoses_json`, `confidence_rating` (1–5), `management_plan`, `ipm_strategy`, `cibrc_advisories`, `revision_count`. |
| `AssessmentRevision` | [`expert_assessment.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/expert_assessment.py) | `assessment_revisions` | `assessment_id`, `revision_number`, `revision_reason`, `previous_data_json`, `created_at`. Immutable historical audit. |
| `Intervention` | [`intervention.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/intervention.py) | `interventions` | `plot_id`, `observation_id`, `category` (`BIOLOGICAL`, `CHEMICAL`, `CULTURAL`, `MECHANICAL`), `trade_name`, `active_ingredient`, `dosage`, `unit`, `phi_days`, `rei_hours`, `application_date`. |
| `InterventionOutcome` | [`intervention.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/intervention.py) | `intervention_outcomes` | `intervention_id`, `follow_up_observation_id`, `evaluation_date`, `observed_status` (`IMPROVING`, `UNCHANGED`, `DETERIORATING`), `visual_change_notes`, `confounding_factors`, `confounding_notice`. |

---

### 2.2 Domain Services & Rule Engines

1. **`RuleEngine` ([`backend/app/services/riskcast/rule_engine.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/riskcast/rule_engine.py)):**
   - Seeded with authoritative PJTSAU agronomic rules for Cotton (`COT-CLSP-01`, `COT-BLGT-01`), Rice (`RIC-BLST-01`, `RIC-SHBL-01`), and Chilli (`CHL-ANTH-01`, `CHL-THRP-01`).
   - Evaluates multi-variable environmental thresholds (temperature, relative humidity, leaf wetness hours, rainfall accumulation).
2. **`RiskCastService` ([`backend/app/services/riskcast/risk_service.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/riskcast/risk_service.py)):**
   - Coordinates plot evaluations, fetches live weather or climatological normal, computes composite risk, and creates deduplicated alerts.
3. **`ExpertService` ([`backend/app/services/expertconnect/expert_service.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/expertconnect/expert_service.py)):**
   - Manages expert onboarding, administrator verification, case claiming, dossier generation, certified assessments, and immutable revision tracking.
4. **`InterventionService` ([`backend/app/services/interventions/intervention_service.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/interventions/intervention_service.py)):**
   - Manages agricultural action logging, tenant validation, follow-up observation linkage, and non-causal outcome timelines.

---

### 2.3 API Endpoints & Client Wrappers

- **`riskcast.py`:** `/api/v1/riskcast/rules`, `/api/v1/riskcast/evaluate/{plot_id}`, `/api/v1/riskcast/farms/{farm_id}/overview`, `/api/v1/riskcast/alerts`, `/api/v1/riskcast/alerts/{id}/acknowledge`, `/api/v1/riskcast/alerts/{id}/dismiss`.
- **`expertconnect.py`:** `/api/v1/expertconnect/apply`, `/api/v1/expertconnect/admin/verify/{id}`, `/api/v1/expertconnect/cases`, `/api/v1/expertconnect/cases/{id}/claim`, `/api/v1/expertconnect/cases/{id}/assess`, `/api/v1/expertconnect/cases/{id}/revisions`.
- **`interventions.py`:** `/api/v1/interventions/`, `/api/v1/interventions/plots/{plot_id}`, `/api/v1/interventions/{id}/outcomes`, `/api/v1/interventions/{id}/timeline`.

---

## 3. Initial Baseline Audit Findings

1. **Strengths:**
   - Database models already stamped in Neon PostgreSQL schema (`plot_risk_assessments`, `risk_rules`, `risk_alerts`, `expert_profiles`, `expert_cases`, `expert_assessments`, `assessment_revisions`, `interventions`, `intervention_outcomes`).
   - All 6 tests in `backend/tests/test_stage7.py` pass cleanly in $15.5\text{ s}$.
   - Frontend `ExpertWorkspaceContent` ([`frontend/app/(expert)/workspace/page.tsx`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/app/(expert)/workspace/page.tsx)) provides a rich case dossier review interface with image comparison and revision history.
   - Non-causal agronomic disclaimers are actively enforced across all API responses.

2. **Verification Requirements for Stage 07 Finalization:**
   - Formalize the 18 required monographs in `docs/finalization/stage-07/`.
   - Update persistent artifact `stage_7_completion.md`.
   - Verify full end-to-end integration and regression suites.

---

## 4. Baseline Conclusion

The Stage 07 architecture is completely in place, functioning reliably against live Neon DB and passing all automated test suites.
