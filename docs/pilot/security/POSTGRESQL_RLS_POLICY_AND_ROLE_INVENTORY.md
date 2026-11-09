# ACREVIA — POSTGRESQL RLS POLICY & ROLE INVENTORY
## Complete Entity Classification, Policy Composition, and Role Mapping (132 Tables)

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document Code:** `POSTGRESQL_RLS_POLICY_AND_ROLE_INVENTORY.md`  
**Execution Date:** November 9, 2026  
**Audited Baseline:** 132 Tables in `Base.metadata`  

---

## 1. Summary of Database Schema Classification

Every single registered table in `Base.metadata` is strictly classified into one of five functional categories:

| Category | Table Count | Policy Strategy | Primary Isolation Key |
|---|---:|---|---|
| **TENANT_DIRECT** | 25 | Permissive Base + Restrictive Isolation | `farm_id` or `tenant_id` |
| **USER_OWNED** | 13 | Permissive Base + Restrictive Isolation | `user_id` or `id` |
| **TENANT_INDIRECT** | 54 | Permissive Base + Restrictive Subquery | Parent FK (`plot_id`, `observation_id`, etc.) |
| **SHARED_REFERENCE** | 24 | Permissive Read + Restrictive Admin Write | Public read; Admin write via `ADMIN_BYPASS_SQL` |
| **COMMUNITY_COLLABORATIVE** | 16 | Permissive Read + Restrictive Author Write | Public read; Authenticated `user_id` write |
| **Total Database Entities** | **132** | — | — |

---

## 2. Policy Composition Architecture

In PostgreSQL Row-Level Security:
1. **Permissive Policies (`AS PERMISSIVE`):** Combined using Boolean `OR`. At least one permissive policy must evaluate to `TRUE` for an operation to be permitted.
2. **Restrictive Policies (`AS RESTRICTIVE`):** Combined using Boolean `AND`. Must evaluate to `TRUE` in addition to any permissive policy, acting as an unbypassable boundary.

### Hardened Administrative Bypass Clause
Applied uniformly across all restrictive policies:
```sql
ADMIN_BYPASS_SQL = (
    CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
    AND current_setting('app.is_admin', true) = 'true'
)
```

---

## 3. Entity Classification Detail (132 Tables)

### Category 1: Direct Tenant Tables (25 Tables)
*Policies:* `{table}_base_access_policy` (PERMISSIVE, `true`), `{table}_tenant_isolation_policy` (RESTRICTIVE, `ADMIN_BYPASS_SQL OR {col}::text = current_setting('app.current_tenant_id', true)`).  
*FORCE ROW LEVEL SECURITY:* YES.

1. `farms` (col: `id`)
2. `audit_logs` (col: `farm_id`)
3. `crop_loss_evidence_packages` (col: `farm_id`)
4. `data_exchange_jobs` (col: `farm_id`)
5. `data_sharing_grants` (col: `farm_id`)
6. `expert_review_cases` (col: `farm_id`)
7. `farm_expenses` (col: `farm_id`)
8. `farm_memberships` (col: `farm_id`)
9. `farm_twins` (col: `farm_id`)
10. `intervention_records` (col: `farm_id`)
11. `location_permissions` (col: `farm_id`)
12. `observations` (col: `farm_id`)
13. `optimization_problems` (col: `farm_id`)
14. `plots` (col: `farm_id`)
15. `produce_lots` (col: `farm_id`)
16. `risk_alerts` (col: `farm_id`)
17. `risk_assessment_records` (col: `farm_id`)
18. `risk_assessments` (col: `farm_id`)
19. `sensor_devices` (col: `farm_id`)
20. `storage_locations` (col: `farm_id`)
21. `twin_snapshots` (col: `farm_id`)
22. `water_sources` (col: `farm_id`)
23. `weather_data` (col: `farm_id`)
24. `weather_observations` (col: `farm_id`)
25. `webhook_events` (col: `tenant_id`)

### Category 2: User-Owned Tables (13 Tables)
*Policies:* `{table}_base_access_policy` (PERMISSIVE, `true`), `{table}_user_isolation_policy` (RESTRICTIVE, `ADMIN_BYPASS_SQL OR {col}::text = current_setting('app.current_user_id', true)`).  
*FORCE ROW LEVEL SECURITY:* YES.

1. `users` (col: `id`)
2. `session_tokens` (col: `user_id`)
3. `user_roles` (col: `user_id`)
4. `consent_records` (col: `user_id`)
5. `api_applications` (col: `user_id`)
6. `webhook_endpoints` (col: `user_id`)
7. `data_mapping_profiles` (col: `user_id`)
8. `expert_profiles` (col: `user_id`)
9. `community_memberships` (col: `user_id`)
10. `organization_memberships` (col: `user_id`)
11. `event_registrations` (col: `user_id`)
12. `knowledge_feedback` (col: `user_id`)
13. `learning_feedback` (col: `user_id`)

### Category 3: Indirect Tenant Tables (54 Tables)
*Policies:* `{table}_base_access_policy` (PERMISSIVE, `true`), `{table}_child_isolation_policy` (RESTRICTIVE, parent subquery check).  
*FORCE ROW LEVEL SECURITY:* YES.

1. `plants` (parent: `plots`, fk: `plot_id`)
2. `plot_geometries` (parent: `plots`, fk: `plot_id`)
3. `crop_seasons` (parent: `plots`, fk: `plot_id`)
4. `crop_stage_events` (parent: `crop_seasons`, fk: `crop_season_id`)
5. `crop_tasks` (parent: `plots`, fk: `plot_id`)
6. `crop_season_economics` (parent: `crop_seasons`, fk: `crop_season_id`)
7. `diagnosis_requests` (parent: `observations`, fk: `observation_id`)
8. `predictions` (parent: `diagnosis_requests`, fk: `diagnosis_request_id`)
9. `prediction_candidates` (parent: `predictions`, fk: `prediction_id`)
10. `expert_reviews` (parent: `predictions`, fk: `prediction_id`)
11. `expert_assessments` (parent: `expert_review_cases`, fk: `case_id`)
12. `expert_assessment_revisions` (parent: `expert_assessments`, fk: `assessment_id`)
13. `outcome_observations` (parent: `intervention_records`, fk: `intervention_id`)
14. `farm_operations` (parent: `plots`, fk: `plot_id`)
15. `observation_media` (parent: `observations`, fk: `observation_id`)
16. `image_quality_assessments` (parent: `observation_media`, fk: `media_id`)
17. `sensor_measurements` (parent: `plots`, fk: `plot_id`)
18. `sensor_calibrations` (parent: `sensor_devices`, fk: `device_id`)
19. `satellite_observations` (parent: `plots`, fk: `plot_id`)
20. `fusion_explanations` (parent: `observations`, fk: `observation_id`)
21. `yield_forecast_records` (parent: `plots`, fk: `plot_id`)
22. `harvest_measurements` (parent: `plots`, fk: `plot_id`)
23. `twin_state_records` (parent: `twin_snapshots`, fk: `snapshot_id`)
24. `twin_synchronization_events` (parent: `farm_twins`, fk: `twin_id`)
25. `simulation_scenarios` (parent: `plots`, fk: `plot_id`)
26. `simulation_results` (parent: `simulation_scenarios`, fk: `scenario_id`)
27. `optimization_results` (parent: `optimization_problems`, fk: `problem_id`)
28. `financial_corrections` (parent: `farm_expenses`, fk: `expense_id`)
29. `sale_transactions` (parent: `produce_lots`, fk: `lot_id`)
30. `harvest_plans` (parent: `plots`, fk: `plot_id`)
31. `harvest_sessions` (parent: `harvest_plans`, fk: `plan_id`)
32. `lot_movements` (parent: `produce_lots`, fk: `lot_id`)
33. `produce_quality_profiles` (parent: `produce_lots`, fk: `lot_id`)
34. `quality_measurements` (parent: `produce_quality_profiles`, fk: `profile_id`)
35. `storage_lots` (parent: `produce_lots`, fk: `lot_id`)
36. `soil_profiles` (parent: `plots`, fk: `plot_id`)
37. `soil_samples` (parent: `plots`, fk: `plot_id`)
38. `soil_test_results` (parent: `soil_samples`, fk: `soil_sample_id`)
39. `water_balance_snapshots` (parent: `plots`, fk: `plot_id`)
40. `irrigation_events` (parent: `plots`, fk: `plot_id`)
41. `soil_moisture_observations` (parent: `plots`, fk: `plot_id`)
42. `climate_exposure_assessments` (parent: `plots`, fk: `plot_id`)
43. `climate_adaptation_scenarios` (parent: `climate_exposure_assessments`, fk: `assessment_id`)
44. `nutrient_assessments` (parent: `plots`, fk: `plot_id`)
45. `nutrient_expert_reviews` (parent: `nutrient_assessments`, fk: `assessment_id`)
46. `farm_practice_records` (parent: `plots`, fk: `plot_id`)
47. `soil_carbon_measurements` (parent: `plots`, fk: `plot_id`)
48. `environmental_accounting_estimates` (parent: `plots`, fk: `plot_id`)
49. `resilience_assessments` (parent: `plots`, fk: `plot_id`)
50. `resilience_scenario_simulations` (parent: `resilience_assessments`, fk: `resilience_assessment_id`)
51. `decision_records` (parent: `plots`, fk: `plot_id`)
52. `decision_feedbacks` (parent: `decision_records`, fk: `decision_record_id`)
53. `api_credentials` (parent: `api_applications`, fk: `application_id`)
54. `webhook_deliveries` (parent: `webhook_endpoints`, fk: `endpoint_id`)

### Category 4: Shared Reference Catalogs (24 Tables)
*Policies:* `{table}_shared_read_policy` (PERMISSIVE, `SELECT TO PUBLIC USING (true)`), `{table}_admin_write_policy` (RESTRICTIVE, `ADMIN_BYPASS_SQL`).  
*FORCE ROW LEVEL SECURITY:* NO (Enables efficient lookup caching).

1. `roles`
2. `crops`
3. `crop_varieties`
4. `crop_calendar_definitions`
5. `agricultural_practice_definitions`
6. `market_commodities`
7. `market_locations`
8. `market_price_observations`
9. `satellite_sources`
10. `climate_baselines`
11. `risk_rules`
12. `integration_partners`
13. `partner_integrations`
14. `knowledge_sources`
15. `knowledge_documents`
16. `knowledge_document_versions`
17. `knowledge_chunks`
18. `knowledge_embeddings`
19. `knowledge_entities`
20. `knowledge_relationships`
21. `ingestion_jobs`
22. `learning_resources`
23. `training_events`
24. `satellite_acquisitions`

### Category 5: Community & Collaborative Hub (16 Tables)
*Policies:* `{table}_public_read_policy` (PERMISSIVE, `SELECT TO PUBLIC USING (true)`), `{table}_author_write_policy` (RESTRICTIVE, `ADMIN_BYPASS_SQL OR current_setting('app.current_user_id', true) != ''`).  
*FORCE ROW LEVEL SECURITY:* NO.

1. `communities`
2. `community_posts`
3. `community_comments`
4. `community_reports`
5. `knowledge_contributions`
6. `contribution_reviews`
7. `translation_versions`
8. `agricultural_organizations`
9. `collective_activities`
10. `research_projects`
11. `research_consents`
12. `dataset_contributions`
13. `annotation_tasks`
14. `annotation_records`
15. `regional_signals`
16. `regional_signal_evidences`

---

## 4. Role Mapping & Permissions

| Role Name | Superuser | Bypass RLS | Create DB | Create Role | Permitted Actions |
|---|---|---|---|---|---|
| `neondb_owner` | NO | YES (implicit via owner) | YES | YES | DDL execution, Alembic migrations |
| `acrevia_staging_app` | NO | NO | NO | NO | DML (`SELECT, INSERT, UPDATE, DELETE`) under RLS |
| `acrevia_admin` | NO | NO | NO | NO | Privileged administration via `ADMIN_BYPASS_SQL` |
