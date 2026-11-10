# ACREVIA — PHASE 07 RLS 132-ENTITY COVERAGE MATRIX

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document Code:** `PHASE_07_RLS_132_ENTITY_COVERAGE_MATRIX.md`  
**Execution Date:** November 10, 2026  
**Auditor Status:** FULLY AUDITED & RECONCILED (132/132 ENTITIES)  
**Machine-Readable Inventory:** [`docs/pilot/security/PHASE_07_RLS_132_ENTITY_INVENTORY.json`](./PHASE_07_RLS_132_ENTITY_INVENTORY.json)  

---

## 1. Classification Summary

Every single entity in SQLAlchemy `Base.metadata.tables` (132 tables) is audited and mapped to its true data-ownership structure:

| Category | Reconciled Entity Count | Policy Model | FORCE RLS | Operational Semantics |
|---|---:|---|:---:|---|
| **`TENANT_DIRECT`** | 25 | Restrictive (`farm_id` / `tenant_id`) | **YES** | Strict tenant isolation. Queries filtered by `app.current_tenant_id`. |
| **`USER_OWNED`** | 13 | Restrictive (`user_id` / `id`) | **YES** | User identity isolation. Queries filtered by `app.current_user_id`. |
| **`TENANT_INDIRECT`** | 53 | Restrictive (Parent FK traversal) | **YES** | Child table isolation verified through verified parent foreign key. |
| **`SHARED_REFERENCE`** | 25 | Permissive Select + Admin Restrictive | NO | Public catalog read-only; writes restricted to verified admin role. |
| **`COMMUNITY_COLLABORATIVE`**| 16 | Permissive Select + Author Restrictive | NO | Community public reading; writes restricted to authenticated author. |
| **Total Database Entities** | **132** | — | **91 Tables** | **100% Comprehensive Coverage** |

---

## 2. Table-by-Table Classification Register

### Category 1: TENANT_DIRECT (25 Tables)
*Direct ownership column: `farm_id` (or `id` for `farms`, `tenant_id` for `webhook_events`).*

1. `farms` (id / owner_id)
2. `audit_logs` (farm_id)
3. `crop_loss_evidence_packages` (farm_id)
4. `data_exchange_jobs` (farm_id)
5. `data_sharing_grants` (farm_id)
6. `expert_review_cases` (farm_id)
7. `farm_expenses` (farm_id)
8. `farm_memberships` (farm_id)
9. `farm_twins` (farm_id)
10. `intervention_records` (farm_id)
11. `location_permissions` (farm_id)
12. `observations` (farm_id)
13. `optimization_problems` (farm_id)
14. `plots` (farm_id)
15. `produce_lots` (farm_id)
16. `risk_alerts` (farm_id)
17. `risk_assessment_records` (farm_id)
18. `risk_assessments` (farm_id)
19. `sensor_devices` (farm_id)
20. `storage_locations` (farm_id)
21. `twin_snapshots` (farm_id)
22. `water_sources` (farm_id)
23. `weather_data` (farm_id)
24. `weather_observations` (farm_id)
25. `webhook_events` (tenant_id)

### Category 2: USER_OWNED (13 Tables)
*Direct ownership column: `user_id` (or `id` for `users`).*

1. `users` (id)
2. `session_tokens` (user_id)
3. `user_roles` (user_id)
4. `consent_records` (user_id)
5. `api_applications` (user_id)
6. `webhook_endpoints` (user_id)
7. `data_mapping_profiles` (user_id)
8. `expert_profiles` (user_id)
9. `community_memberships` (user_id)
10. `organization_memberships` (user_id)
11. `event_registrations` (user_id)
12. `knowledge_feedback` (user_id)
13. `learning_feedback` (user_id)

### Category 3: TENANT_INDIRECT (53 Tables)
*Child entities traversing foreign key relationships to tenant/user roots.*

1. `plants` &rarr; `plots` (`fk: plot_id`)
2. `plot_geometries` &rarr; `plots` (`fk: plot_id`)
3. `crop_seasons` &rarr; `plots` (`fk: plot_id`)
4. `crop_stage_events` &rarr; `crop_seasons` (`fk: crop_season_id`)
5. `crop_tasks` &rarr; `plots` (`fk: plot_id`)
6. `crop_season_economics` &rarr; `crop_seasons` (`fk: crop_season_id`)
7. `diagnosis_requests` &rarr; `observations` (`fk: observation_id`)
8. `predictions` &rarr; `diagnosis_requests` (`fk: diagnosis_request_id`)
9. `prediction_candidates` &rarr; `predictions` (`fk: prediction_id`)
10. `expert_reviews` &rarr; `diagnosis_requests` (`fk: diagnosis_request_id`)
11. `expert_assessments` &rarr; `expert_review_cases` (`fk: case_id`)
12. `expert_assessment_revisions` &rarr; `expert_assessments` (`fk: assessment_id`)
13. `outcome_observations` &rarr; `intervention_records` (`fk: intervention_id`)
14. `farm_operations` &rarr; `plots` (`fk: plot_id`)
15. `observation_media` &rarr; `observations` (`fk: observation_id`)
16. `image_quality_assessments` &rarr; `observation_media` (`fk: media_id`)
17. `sensor_measurements` &rarr; `plots` (`fk: plot_id`)
18. `sensor_calibrations` &rarr; `sensor_devices` (`fk: device_id`)
19. `satellite_observations` &rarr; `plots` (`fk: plot_id`)
20. `fusion_explanations` &rarr; `plots` (`fk: plot_id`)
21. `yield_forecast_records` &rarr; `plots` (`fk: plot_id`)
22. `harvest_measurements` &rarr; `plots` (`fk: plot_id`)
23. `twin_state_records` &rarr; `twin_snapshots` (`fk: snapshot_id`)
24. `twin_synchronization_events` &rarr; `farm_twins` (`fk: twin_id`)
25. `simulation_scenarios` &rarr; `plots` (`fk: plot_id`)
26. `simulation_results` &rarr; `simulation_scenarios` (`fk: scenario_id`)
27. `optimization_results` &rarr; `optimization_problems` (`fk: problem_id`)
28. `financial_corrections` &rarr; `farm_expenses` (`fk: expense_id`)
29. `sale_transactions` &rarr; `produce_lots` (`fk: lot_id`)
30. `harvest_plans` &rarr; `plots` (`fk: plot_id`)
31. `harvest_sessions` &rarr; `harvest_plans` (`fk: harvest_plan_id`)
32. `lot_movements` &rarr; `produce_lots` (`fk: lot_id`)
33. `quality_measurements` &rarr; `produce_lots` (`fk: lot_id`)
34. `storage_lots` &rarr; `produce_lots` (`fk: lot_id`)
35. `soil_profiles` &rarr; `plots` (`fk: plot_id`)
36. `soil_samples` &rarr; `plots` (`fk: plot_id`)
37. `soil_test_results` &rarr; `soil_samples` (`fk: soil_sample_id`)
38. `water_balance_snapshots` &rarr; `plots` (`fk: plot_id`)
39. `irrigation_events` &rarr; `plots` (`fk: plot_id`)
40. `soil_moisture_observations` &rarr; `plots` (`fk: plot_id`)
41. `climate_exposure_assessments` &rarr; `plots` (`fk: plot_id`)
42. `climate_adaptation_scenarios` &rarr; `climate_exposure_assessments` (`fk: assessment_id`)
43. `nutrient_assessments` &rarr; `soil_test_results` (`fk: soil_test_result_id`)
44. `nutrient_expert_reviews` &rarr; `nutrient_assessments` (`fk: nutrient_assessment_id`)
45. `farm_practice_records` &rarr; `plots` (`fk: plot_id`)
46. `soil_carbon_measurements` &rarr; `plots` (`fk: plot_id`)
47. `environmental_accounting_estimates` &rarr; `plots` (`fk: plot_id`)
48. `resilience_assessments` &rarr; `plots` (`fk: plot_id`)
49. `resilience_scenario_simulations` &rarr; `resilience_assessments` (`fk: assessment_id`)
50. `decision_records` &rarr; `plots` (`fk: plot_id`)
51. `decision_feedbacks` &rarr; `decision_records` (`fk: decision_id`)
52. `api_credentials` &rarr; `api_applications` (`fk: application_id`)
53. `webhook_deliveries` &rarr; `webhook_endpoints` (`fk: endpoint_id`)

### Category 4: SHARED_REFERENCE (25 Tables)
*Public lookup catalogs, agronomic definitions, university research references.*

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
25. `produce_quality_profiles` (AGMARK crop grading standards)

### Category 5: COMMUNITY_COLLABORATIVE (16 Tables)
*Public collaborative knowledge exchange, collective farming initiatives, anonymous signal sharing.*

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

## 3. Verification Artifact Parity

- **Total Metadata Entities:** 132
- **Mapped Entities:** 132
- **Unmapped Entities:** 0
- **Missing Foreign Keys:** 0
- **Machine-Readable JSON Validated:** Yes (`PHASE_07_RLS_132_ENTITY_INVENTORY.json`).
