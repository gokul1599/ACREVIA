# ACREVIA — STAGE 07 DATABASE SCHEMA & REST API CONTRACTS
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 07 — Agricultural Risk Intelligence, ExpertConnect & Intervention Outcomes  
**Date:** 2026-11-08  
**Status:** SPECIFIED & TESTED (`PASS`)

---

## 1. Relational Database Schema Design (Neon PostgreSQL)

All Stage 07 tables are verified present under Alembic migration head `f4894a11c87d`.

### 1.1 RiskCast Schema Definition
```sql
CREATE TABLE risk_rules (
    id VARCHAR(36) PRIMARY KEY,
    rule_code VARCHAR(50) UNIQUE NOT NULL,
    crop VARCHAR(50) NOT NULL,
    disease_or_pest_name VARCHAR(150) NOT NULL,
    temp_min FLOAT,
    temp_max FLOAT,
    humidity_min FLOAT,
    leaf_wetness_hours_min FLOAT,
    rainfall_min_mm FLOAT,
    evidence_citations JSON NOT NULL,
    advisory_te TEXT NOT NULL,
    advisory_hi TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL
);
CREATE INDEX ix_risk_rules_crop ON risk_rules(crop);

CREATE TABLE plot_risk_assessments (
    id VARCHAR(36) PRIMARY KEY,
    plot_id VARCHAR(36) NOT NULL REFERENCES plots(id) ON DELETE CASCADE,
    weather_data_id VARCHAR(36) REFERENCES weather_data(id),
    overall_risk_level VARCHAR(20) NOT NULL,
    limiting_factors_json JSON,
    evaluation_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    limitations_notice TEXT NOT NULL
);
CREATE INDEX ix_plot_risk_assessments_plot_id ON plot_risk_assessments(plot_id);

CREATE TABLE risk_alerts (
    id VARCHAR(36) PRIMARY KEY,
    farm_id VARCHAR(36) NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    plot_id VARCHAR(36) REFERENCES plots(id) ON DELETE CASCADE,
    rule_code VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    deduplication_key VARCHAR(150) UNIQUE NOT NULL,
    is_acknowledged BOOLEAN DEFAULT FALSE NOT NULL,
    is_dismissed BOOLEAN DEFAULT FALSE NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX ix_risk_alerts_farm_plot ON risk_alerts(farm_id, plot_id);
```

---

### 1.2 ExpertConnect & Assessment Revisions Schema
```sql
CREATE TABLE expert_profiles (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    registration_number VARCHAR(100) UNIQUE NOT NULL,
    highest_degree VARCHAR(100) NOT NULL,
    institution VARCHAR(200) NOT NULL,
    specializations JSON NOT NULL,
    districts_covered JSON NOT NULL,
    verification_status VARCHAR(50) DEFAULT 'APPLICATION_SUBMITTED' NOT NULL,
    verified_by_user_id VARCHAR(36) REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    rejection_reason VARCHAR(500)
);

CREATE TABLE expert_cases (
    id VARCHAR(36) PRIMARY KEY,
    observation_id VARCHAR(36) UNIQUE NOT NULL REFERENCES observations(id) ON DELETE CASCADE,
    assigned_expert_id VARCHAR(36) REFERENCES expert_profiles(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'QUEUED' NOT NULL,
    priority VARCHAR(30) DEFAULT 'ROUTINE' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE TABLE expert_assessments (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) UNIQUE NOT NULL REFERENCES expert_cases(id) ON DELETE CASCADE,
    expert_id VARCHAR(36) NOT NULL REFERENCES expert_profiles(id),
    confirmed_crop VARCHAR(50) NOT NULL,
    primary_condition VARCHAR(200) NOT NULL,
    differential_diagnoses JSON NOT NULL,
    confidence_rating INTEGER NOT NULL,
    urgency_level VARCHAR(30) NOT NULL,
    management_plan TEXT NOT NULL,
    ipm_strategy TEXT NOT NULL,
    cibrc_advisories TEXT,
    revision_count INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE TABLE assessment_revisions (
    id VARCHAR(36) PRIMARY KEY,
    assessment_id VARCHAR(36) NOT NULL REFERENCES expert_assessments(id) ON DELETE CASCADE,
    revision_number INTEGER NOT NULL,
    revision_reason TEXT NOT NULL,
    previous_data_json JSON NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);
```

---

### 1.3 Intervention & Outcome Journal Schema
```sql
CREATE TABLE interventions (
    id VARCHAR(36) PRIMARY KEY,
    plot_id VARCHAR(36) NOT NULL REFERENCES plots(id) ON DELETE CASCADE,
    observation_id VARCHAR(36) REFERENCES observations(id) ON DELETE SET NULL,
    expert_assessment_id VARCHAR(36) REFERENCES expert_assessments(id) ON DELETE SET NULL,
    category VARCHAR(50) NOT NULL,
    trade_name VARCHAR(100) NOT NULL,
    active_ingredient VARCHAR(150),
    dosage FLOAT NOT NULL,
    unit VARCHAR(30) NOT NULL,
    application_method VARCHAR(50) DEFAULT 'FOLIAR_SPRAY' NOT NULL,
    application_date DATE NOT NULL,
    target_condition VARCHAR(150) NOT NULL,
    phi_days INTEGER,
    rei_hours INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE TABLE intervention_outcomes (
    id VARCHAR(36) PRIMARY KEY,
    intervention_id VARCHAR(36) NOT NULL REFERENCES interventions(id) ON DELETE CASCADE,
    follow_up_observation_id VARCHAR(36) NOT NULL REFERENCES observations(id) ON DELETE RESTRICT,
    evaluation_date DATE NOT NULL,
    observed_status VARCHAR(50) NOT NULL,
    days_post_intervention INTEGER NOT NULL,
    visual_change_notes TEXT,
    confounding_factors TEXT,
    farmer_assessment VARCHAR(100),
    confounding_variables_notice TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);
```

---

## 2. REST API Endpoint Contracts

### 2.1 RiskCast APIs
- `GET /api/v1/riskcast/rules?crop={crop}` $\to$ Returns active versioned rules and PJTSAU citations.
- `POST /api/v1/riskcast/evaluate/{plot_id}` $\to$ Evaluates plot environmental risk ($201\text{ Created}$).
- `GET /api/v1/riskcast/farms/{farm_id}/overview` $\to$ Returns plot risk matrix & weather.
- `GET /api/v1/riskcast/alerts?farm_id={farm_id}` $\to$ Returns active deduplicated alerts.
- `POST /api/v1/riskcast/alerts/{id}/acknowledge` $\to$ Marks alert acknowledged.
- `POST /api/v1/riskcast/alerts/{id}/dismiss` $\to$ Dismisses alert.

### 2.2 ExpertConnect APIs
- `POST /api/v1/expertconnect/apply` $\to$ Agronomist submits credentials ($201\text{ Created}$).
- `POST /api/v1/expertconnect/admin/verify/{id}` $\to$ Admin verifies/approves profile ($200\text{ OK}$, $403\text{ Forbidden}$ for non-admin).
- `POST /api/v1/expertconnect/cases/create-from-observation/{obs_id}` $\to$ Escalates observation to expert case.
- `GET /api/v1/expertconnect/cases` $\to$ Lists triage queue with priority filtering.
- `POST /api/v1/expertconnect/cases/{id}/claim` $\to$ Expert claims case ($status \to ASSIGNED$).
- `GET /api/v1/expertconnect/cases/{id}` $\to$ Returns comprehensive evidence dossier.
- `POST /api/v1/expertconnect/cases/{id}/assess` $\to$ Submits initial certified assessment.
- `PUT /api/v1/expertconnect/cases/{id}/assess` $\to$ Submits revision with rationale.
- `GET /api/v1/expertconnect/cases/{id}/revisions` $\to$ Returns immutable revision history.

### 2.3 Intervention Intelligence APIs
- `POST /api/v1/interventions/` $\to$ Logs executed intervention ($201\text{ Created}$).
- `GET /api/v1/interventions/plots/{plot_id}` $\to$ Lists plot interventions ($403\text{ Forbidden}$ cross-tenant).
- `POST /api/v1/interventions/{id}/outcomes` $\to$ Logs follow-up observation outcome ($201\text{ Created}$).
- `GET /api/v1/interventions/{id}/timeline` $\to$ Returns longitudinal timeline with causality notice.
