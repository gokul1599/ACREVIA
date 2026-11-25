# ACREVIA — PHASE 07: GLOBAL GUC & TENANT POLICY TRACEABILITY MATRIX

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** `MODE A ONLY` — Offline Source Inspection & Policy Traceability Analysis  
**Git Baseline:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Methodology:** Everything Claude Code (ECC) Security Assurance  
**Date:** November 23, 2026  
**Status:** `TECHNICAL_PREFLIGHT_BLOCKED_WITH_RECORDED_BLOCKERS`

---

## 1. Executive Summary & Traceability Scope

This matrix provides the exhaustive, source-verified security crosswalk across all **78 Tenant Tables** (25 Direct + 53 Indirect) and **13 User-Owned Tables** in ACREVIA. It traces:
1. Table classification and schema ownership columns.
2. Exact generated PostgreSQL RLS policy expressions.
3. Database privilege grants assigned to the runtime principal (`acrevia_staging_app`).
4. Session GUC consumption (`app.current_tenant_id` and `app.current_user_id`).
5. Presence or absence of independent database-layer membership checks.
6. Vulnerability classification under adversarial GUC spoofing.

---

## 2. Complete 78-Table Tenant Policy Matrix

### 2.1 Direct Tenant Tables (25 Tables)
All Direct Tenant Tables enforce RLS via `generate_rls_ddl(table_name, TableCategory.TENANT_DIRECT, column)`:
- **Permissive Base Policy:** `FOR ALL TO PUBLIC USING (true) WITH CHECK (true)`
- **Restrictive Isolation Policy:**
  $$\text{USING / WITH CHECK}\ (ADMIN\_BYPASS\_SQL \lor \{col\}::\text{text} = \text{current\_setting}('app.current\_tenant\_id', \text{true}))$$

| # | Table Name | Category | Scope Column | Independent Membership Check? | Database Privileges Granted (`acrevia_staging_app`) | GUC Spoof Vulnerability Classification |
|---|---|---|---|---|---|---|
| 1 | `audit_logs` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT` (Append-Only) | `DIRECT_GUC_DEPENDENCY` |
| 2 | `crop_loss_evidence_packages` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 3 | `data_exchange_jobs` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 4 | `data_sharing_grants` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 5 | `expert_review_cases` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 6 | `farm_expenses` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 7 | `farm_memberships` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 8 | `farm_twins` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 9 | `farms` | `TENANT_DIRECT` | `id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 10 | `intervention_records` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 11 | `location_permissions` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 12 | `observations` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 13 | `optimization_problems` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 14 | `plots` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 15 | `produce_lots` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 16 | `risk_alerts` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 17 | `risk_assessment_records` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 18 | `risk_assessments` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 19 | `sensor_devices` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 20 | `storage_locations` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 21 | `twin_snapshots` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 22 | `water_sources` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 23 | `weather_data` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 24 | `weather_observations` | `TENANT_DIRECT` | `farm_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |
| 25 | `webhook_events` | `TENANT_DIRECT` | `tenant_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `DIRECT_GUC_DEPENDENCY` |

---

### 2.2 Indirect Tenant Tables (53 Tables)
All Indirect Tenant Tables enforce RLS via `generate_rls_ddl(table_name, TableCategory.TENANT_INDIRECT)`:
- **Permissive Base Policy:** `FOR ALL TO PUBLIC USING (true) WITH CHECK (true)`
- **Restrictive Isolation Policy:**
  $$\text{USING / WITH CHECK}\ (ADMIN\_BYPASS\_SQL \lor \exists (\text{SELECT } 1 \text{ FROM } \{parent\} \dots \text{WHERE parent matches GUC}))$$

| # | Table Name | Parent Table | Foreign Key | Independent Membership Check? | Database Privileges Granted | GUC Spoof Vulnerability Classification |
|---|---|---|---|---|---|---|
| 1 | `api_credentials` | `api_applications` | `application_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 2 | `climate_adaptation_scenarios` | `climate_exposure_assessments` | `assessment_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 3 | `climate_exposure_assessments` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 4 | `crop_season_economics` | `crop_seasons` | `crop_season_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 5 | `crop_seasons` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 6 | `crop_stage_events` | `crop_seasons` | `crop_season_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 7 | `crop_tasks` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 8 | `decision_feedbacks` | `decision_records` | `decision_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 9 | `decision_records` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 10 | `diagnosis_requests` | `observations` | `observation_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 11 | `environmental_accounting_estimates` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 12 | `expert_assessment_revisions` | `expert_assessments` | `assessment_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 13 | `expert_assessments` | `expert_review_cases` | `case_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 14 | `expert_reviews` | `diagnosis_requests` | `diagnosis_request_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 15 | `farm_operations` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 16 | `farm_practice_records` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 17 | `financial_corrections` | `farm_expenses` | `expense_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 18 | `fusion_explanations` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 19 | `harvest_measurements` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 20 | `harvest_plans` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 21 | `harvest_sessions` | `harvest_plans` | `harvest_plan_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 22 | `image_quality_assessments` | `observation_media` | `media_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 23 | `irrigation_events` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 24 | `lot_movements` | `produce_lots` | `lot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 25 | `nutrient_assessments` | `soil_test_results` | `soil_test_result_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 26 | `nutrient_expert_reviews` | `nutrient_assessments` | `nutrient_assessment_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 27 | `observation_media` | `observations` | `observation_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 28 | `optimization_results` | `optimization_problems` | `problem_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 29 | `outcome_observations` | `intervention_records` | `intervention_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 30 | `plants` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 31 | `plot_geometries` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 32 | `prediction_candidates` | `predictions` | `prediction_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 33 | `predictions` | `diagnosis_requests` | `diagnosis_request_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 34 | `quality_measurements` | `produce_lots` | `lot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 35 | `resilience_assessments` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 36 | `resilience_scenario_simulations` | `resilience_assessments` | `assessment_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 37 | `sale_transactions` | `produce_lots` | `lot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 38 | `satellite_observations` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 39 | `sensor_calibrations` | `sensor_devices` | `device_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 40 | `sensor_measurements` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 41 | `simulation_results` | `simulation_scenarios` | `scenario_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 42 | `simulation_scenarios` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 43 | `soil_carbon_measurements` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 44 | `soil_moisture_observations` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 45 | `soil_profiles` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 46 | `soil_samples` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 47 | `soil_test_results` | `soil_samples` | `soil_sample_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 48 | `storage_lots` | `produce_lots` | `lot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 49 | `twin_state_records` | `twin_snapshots` | `snapshot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 50 | `twin_synchronization_events` | `farm_twins` | `twin_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 51 | `water_balance_snapshots` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 52 | `webhook_deliveries` | `webhook_endpoints` | `endpoint_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |
| 53 | `yield_forecast_records` | `plots` | `plot_id` | **NO** | `SELECT, INSERT, UPDATE, DELETE` | `INDIRECT_GUC_DEPENDENCY` |

---

## 3. Complete 13-Table User-Owned Security Matrix

All 13 User-Owned Tables enforce RLS via `generate_rls_ddl(table_name, TableCategory.USER_OWNED, column)`:
- **Permissive Base Policy:** `FOR ALL TO PUBLIC USING (true) WITH CHECK (true)`
- **Restrictive User Isolation Policy:**
  $$\text{USING / WITH CHECK}\ (ADMIN\_BYPASS\_SQL \lor \{col\}::\text{text} = \text{current\_setting}('app.current\_user\_id', \text{true}))$$

| # | Table Name | Owner Column | Primary Key | Foreign Key Cascades | Database Privileges Granted | Spoofing & Escalation Vulnerability | Remediation Mandate |
|---|---|---|---|---|---|---|---|
| 1 | `users` | `id` | `['id']` | Referenced by 12+ child tables | `SELECT, INSERT, UPDATE, DELETE` | Password overwrite, account takeover, cascading user deletion | Revoke runtime DELETE; soft-delete workflow |
| 2 | `session_tokens` | `user_id` | `['id']` | `user_id -> users.id (CASCADE)` | `SELECT, INSERT, UPDATE, DELETE` | Session hijacking/revocation; arbitrary session injection | Constrain session issuance to auth service |
| 3 | `user_roles` | `user_id` | `['user_id', 'role_id']` | `user_id -> users.id (CASCADE)`, `role_id -> roles.id (CASCADE)` | `SELECT, INSERT, UPDATE, DELETE` | **CRITICAL: Self-escalation to `ADMIN` (`RLS-ROLE-ASSIGNMENT-01`)** | Revoke runtime DML; deploy `register_default_user_role` gateway |
| 4 | `consent_records` | `user_id` | `['id']` | `user_id -> users.id (CASCADE)` | `SELECT, INSERT, UPDATE, DELETE` | Falsifying or revoking statutory DPDPA consent | Stored procedure for consent lifecycle; append-only audit |
| 5 | `api_applications` | `user_id` | `['id']` | `user_id -> users.id (CASCADE)` | `SELECT, INSERT, UPDATE, DELETE` | OAuth redirect URI hijacking | Restrict redirect URI modifications to verified partner admins |
| 6 | `webhook_endpoints` | `user_id` | `['id']` | `user_id -> users.id (CASCADE)` | `SELECT, INSERT, UPDATE, DELETE` | Event destination redirection to attacker host | URL validation and signing secret regeneration controls |
| 7 | `data_mapping_profiles` | `user_id` | `['id']` | `user_id -> users.id (CASCADE)` | `SELECT, INSERT, UPDATE, DELETE` | Tampering with data exchange ETL mappings | User ownership validation |
| 8 | `expert_profiles` | `user_id` | `['id']` | `user_id -> users.id (CASCADE)` | `SELECT, INSERT, UPDATE, DELETE` | Self-approval of agronomic verification status | Revoke direct UPDATE on `verification_status` and `verified_by` |
| 9 | `community_memberships` | `user_id` | `['id']` | `user_id -> users.id (CASCADE)` | `SELECT, INSERT, UPDATE, DELETE` | Self-promotion to community moderator | Restrict role field updates to community owners |
| 10 | `organization_memberships` | `user_id` | `['id']` | `user_id -> users.id (CASCADE)` | `SELECT, INSERT, UPDATE, DELETE` | Self-promotion to organization admin | Restrict `org_role` updates to existing organization admins |
| 11 | `event_registrations` | `user_id` | `['id']` | `user_id -> users.id (CASCADE)` | `SELECT, INSERT, UPDATE, DELETE` | Registration status manipulation | Low impact; user scoped |
| 12 | `knowledge_feedback` | `user_id` | `['id']` | `user_id -> users.id (SET NULL)` | `SELECT, INSERT, UPDATE, DELETE` | Resolution note tampering | Restrict resolution notes to expert/admin |
| 13 | `learning_feedback` | `user_id` | `['id']` | `user_id -> users.id (CASCADE)` | `SELECT, INSERT, UPDATE, DELETE` | Review tampering | User scoped |

---

## 4. Global Actor-GUC Consumer Matrix

| Table Name | Policy Scope | Actor GUC Used | Role Invariant Checked | Exploitation / Bypass Vector | Severity | Remediation |
|---|---|---|---|---|---|---|
| `regional_signals` | `author_write_policy` | `app.current_user_id` | `ur.role_id IN (ADMIN, EXPERT, RESEARCHER)` | Non-admin creates/promotes `OFFICIAL_ADVISORY` (`RLS-WRITE-AUTH-01`) | **HIGH** | Option D fail-closed policy (restrict official advisory to ADMIN) |
| `regional_signal_evidences` | `public_read_policy` | `app.current_user_id` | `ur.role_id IN (ADMIN, EXPERT, RESEARCHER)` | Role-global reading of evidence for sub-threshold signals (`RES-PULSE-READ-01`) | **HIGH** | District-scoped evidence visibility / case binding |
| `regional_signal_evidences` | `author_write_policy` | `app.current_user_id` | `ur.role_id IN (ADMIN, EXPERT, RESEARCHER)` | Arbitrary signal evidence injection | **HIGH** | Restrict to original signal author / admin |
| `community_posts` | `author_write_policy` | `app.current_user_id` | Author check or moderator | Author impersonation via GUC | **MEDIUM** | JWT subject validation in app layer |
| `community_comments` | `author_write_policy` | `app.current_user_id` | Author check | Author impersonation via GUC | **MEDIUM** | JWT subject validation in app layer |
| `agricultural_organizations`| `author_write_policy` | `app.current_user_id` | `om.org_role = 'ORGANIZATION_ADMIN'` | Organization profile tampering | **HIGH** | Independent membership check |
| `research_projects` | `author_write_policy` | `app.current_user_id` | `lead_researcher_id` match | Project tampering | **MEDIUM** | Verified researcher credential check |
| `research_consents` | `author_write_policy` | `app.current_user_id` | `farmer_id` match | Research consent forging | **HIGH** | Dual-signature verification |
| `annotation_tasks` | `author_write_policy` | `app.current_user_id` | Lead researcher match | Task reassignment | **MEDIUM** | Project lead validation |
| `annotation_records` | `author_write_policy` | `app.current_user_id` | `annotator_id` match | Annotation tampering | **MEDIUM** | Task assignment check |

---

## 5. Background Worker Dispatch & Database Principal Matrix

| Worker / Task Script | Execution Mode | Database Principal | Session Context Established | Dispatch Authorization Check | Database Privilege Threat | Status |
|---|---|---|---|---|---|---|
| `run_riskcast_batch.py` | Local Dev / Test | `acrevia_staging_app` | `tenant_id=farm_id, user_id="system:worker:riskcast", is_admin=False` | `DispatchVerifier.verify_target_authorization` | Holds full DML on `user_roles` and operational tables | **TEST ONLY** |
| `run_riskcast_batch.py` | Production / Staging | `acrevia_staging_app` | Fails closed before session creation | `ProductionDispatchBlockedError` (`WRK-DISP-01`) | N/A (Blocked in runtime) | **BLOCKED** |

---

## 6. Traceability and Cross-Reference Index

- **Associated Architecture Decision Record:** [`PHASE_07_TRUSTED_WRITER_ARCHITECTURE_DECISION_RECORD.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_TRUSTED_WRITER_ARCHITECTURE_DECISION_RECORD.md)
- **Associated Remediation Plan:** [`PHASE_07_GLOBAL_RLS_IDENTITY_REMEDIATION_AND_ROLE_MANAGEMENT_CONTAINMENT_PLAN.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GLOBAL_RLS_IDENTITY_REMEDIATION_AND_ROLE_MANAGEMENT_CONTAINMENT_PLAN.md)
- **Associated Audit Dossier:** [`PHASE_07_GLOBAL_ACTOR_GUC_TRUST_AND_ROLE_ASSIGNMENT_SECURITY_AUDIT.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_GLOBAL_ACTOR_GUC_TRUST_AND_ROLE_ASSIGNMENT_SECURITY_AUDIT.md)
