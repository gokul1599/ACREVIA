# ACREVIA — PHASE 07: AUTHORITATIVE ORM TABLE & METADATA INVENTORY
## Complete 132-Entity Schema Reference, Model Crosswalk & RLS Categorization

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document ID:** `ACR-SEC-P07-ORM-INVENTORY`  
**Git Commit / HEAD:** `428812d99c8d4ac033b1ec9f8edac4a1dcccb973`  
**Generated Date:** November 10, 2026  
**Audit Status:** **`100% RECONCILED AGAINST SQLALCHEMY METADATA`**  

---

## 1. Executive Summary & Registry Set Reconciliation

This document establishes the authoritative, machine-extracted inventory of all 132 database entities registered in SQLAlchemy metadata (`Base.metadata.tables`).

### Dynamic Set Equality ($M = R$):
- **Registered SQLAlchemy Model Tables ($M$):** 132
- **RLS Classification Entries ($R$):** 132
- **Unclassified Model Tables ($M - R$):** $\emptyset$ (Zero unclassified tables)
- **Unknown RLS Tables ($R - M$):** $\emptyset$ (Zero phantom tables)
- **Matched Tables ($M \cap R$):** 132 ($100\%$ coverage)

### Discrepancy Resolution against Previous Colloquial Reports:
An audit of previous narrative reports identified discrepancies where colloquial or hypothetical names were cited in prose. This audit confirms the exact ground truth:
- `farm_memberships` is the **actual** table in `backend/app/models/farm.py` (prose report incorrectly cited `farm_members`).
- `crop_seasons` is the **actual** table in `backend/app/models/crop_planning.py` (prose report incorrectly cited `crop_cycles`).
- `farm_operations` is the **actual** table in `backend/app/models/operation.py` (prose report incorrectly cited `farm_machinery`).
- `livestock_profiles` and `drone_survey_missions` **do not exist** and have never existed in ACREVIA's SQLAlchemy registry.

---

## 2. Table-by-Table Authoritative Inventory (132 Tables)

| # | Table Name | SQLAlchemy Model | Source Module | Primary Key | Foreign Keys | RLS Category | FORCE RLS |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| 1 | `agricultural_organizations` | `AgriculturalOrganization` | `collective.py` | `id` | `None` | `community` | **YES** |
| 2 | `agricultural_practice_definitions` | `AgriculturalPracticeDefinition` | `sustainability.py` | `id` | `None` | `shared_reference` | **NO** |
| 3 | `annotation_records` | `AnnotationRecord` | `research_hub.py` | `id` | `annotator_id->users.id, task_id->annotation_tasks.id` | `community` | **YES** |
| 4 | `annotation_tasks` | `AnnotationTask` | `research_hub.py` | `id` | `project_id->research_projects.id, assigned_expert_id->users.id` | `community` | **YES** |
| 5 | `api_applications` | `ApiApplication` | `interoperability.py` | `id` | `partner_id->integration_partners.id, user_id->users.id` | `user_owned` | **YES** |
| 6 | `api_credentials` | `ApiCredential` | `interoperability.py` | `id` | `application_id->api_applications.id` | `tenant_indirect` | **YES** |
| 7 | `audit_logs` | `AuditLog` | `governance.py` | `id` | `None` | `tenant_direct` | **YES** |
| 8 | `climate_adaptation_scenarios` | `ClimateAdaptationScenario` | `climate_resilience.py` | `id` | `assessment_id->climate_exposure_assessments.id` | `tenant_indirect` | **YES** |
| 9 | `climate_baselines` | `ClimateBaseline` | `climate_resilience.py` | `id` | `None` | `shared_reference` | **NO** |
| 10 | `climate_exposure_assessments` | `ClimateExposureAssessment` | `climate_resilience.py` | `id` | `plot_id->plots.id, crop_id->crops.id` | `tenant_indirect` | **YES** |
| 11 | `collective_activities` | `CollectiveActivity` | `collective.py` | `id` | `organization_id->agricultural_organizations.id, created_by_user_id->users.id` | `community` | **YES** |
| 12 | `communities` | `Community` | `community.py` | `id` | `created_by_user_id->users.id` | `community` | **YES** |
| 13 | `community_comments` | `CommunityComment` | `community.py` | `id` | `author_id->users.id, post_id->community_posts.id` | `community` | **YES** |
| 14 | `community_memberships` | `CommunityMembership` | `community.py` | `id` | `user_id->users.id, community_id->communities.id` | `user_owned` | **YES** |
| 15 | `community_posts` | `CommunityPost` | `community.py` | `id` | `community_id->communities.id, author_id->users.id` | `community` | **YES** |
| 16 | `community_reports` | `CommunityReport` | `community.py` | `id` | `comment_id->community_comments.id, post_id->community_posts.id, reported_by_user_id->users.id` | `community` | **YES** |
| 17 | `consent_records` | `ConsentRecord` | `governance.py` | `id` | `user_id->users.id` | `user_owned` | **YES** |
| 18 | `contribution_reviews` | `ContributionReview` | `commons_contribution.py` | `id` | `contribution_id->knowledge_contributions.id, reviewer_id->users.id` | `community` | **YES** |
| 19 | `crop_calendar_definitions` | `CropCalendarDefinition` | `crop_planning.py` | `id` | `None` | `shared_reference` | **NO** |
| 20 | `crop_loss_evidence_packages` | `CropLossEvidencePackage` | `evidence_package.py` | `id` | `plot_id->plots.id, farm_id->farms.id, crop_season_id->crop_seasons.id` | `tenant_direct` | **YES** |
| 21 | `crop_season_economics` | `CropSeasonEconomics` | `crop_economics.py` | `id` | `crop_season_id->crop_seasons.id` | `tenant_indirect` | **YES** |
| 22 | `crop_seasons` | `CropSeason` | `crop.py` | `id` | `crop_id->crops.id, variety_id->crop_varieties.id, plot_id->plots.id` | `tenant_indirect` | **YES** |
| 23 | `crop_stage_events` | `CropStageEvent` | `crop.py` | `id` | `crop_season_id->crop_seasons.id` | `tenant_indirect` | **YES** |
| 24 | `crop_tasks` | `CropTask` | `crop_planning.py` | `id` | `plot_id->plots.id, crop_season_id->crop_seasons.id, calendar_def_id->crop_calendar_definitions.id` | `tenant_indirect` | **YES** |
| 25 | `crop_varieties` | `CropVariety` | `crop.py` | `id` | `crop_id->crops.id` | `shared_reference` | **NO** |
| 26 | `crops` | `Crop` | `crop.py` | `id` | `None` | `shared_reference` | **NO** |
| 27 | `data_exchange_jobs` | `DataExchangeJob` | `exchange.py` | `id` | `user_id->users.id, farm_id->farms.id` | `tenant_direct` | **YES** |
| 28 | `data_mapping_profiles` | `DataMappingProfile` | `exchange.py` | `id` | `user_id->users.id` | `user_owned` | **YES** |
| 29 | `data_sharing_grants` | `DataSharingGrant` | `interoperability.py` | `id` | `farm_id->farms.id, partner_id->integration_partners.id, user_id->users.id, plot_id->plots.id` | `tenant_direct` | **YES** |
| 30 | `dataset_contributions` | `DatasetContribution` | `research_hub.py` | `id` | `project_id->research_projects.id, contributor_id->users.id` | `community` | **YES** |
| 31 | `decision_feedbacks` | `DecisionFeedback` | `decision_intelligence.py` | `id` | `decision_id->decision_records.id` | `tenant_indirect` | **YES** |
| 32 | `decision_records` | `DecisionRecord` | `decision_intelligence.py` | `id` | `farmer_id->users.id, expert_escalation_case_id->expert_review_cases.id, plot_id->plots.id` | `tenant_indirect` | **YES** |
| 33 | `diagnosis_requests` | `DiagnosisRequest` | `diagnosis.py` | `id` | `media_id->observation_media.id, observation_id->observations.id` | `tenant_indirect` | **YES** |
| 34 | `environmental_accounting_estimates` | `EnvironmentalAccountingEstimate` | `sustainability.py` | `id` | `plot_id->plots.id` | `tenant_indirect` | **YES** |
| 35 | `event_registrations` | `EventRegistration` | `extension_learning.py` | `id` | `user_id->users.id, event_id->training_events.id` | `user_owned` | **YES** |
| 36 | `expert_assessment_revisions` | `ExpertAssessmentRevision` | `expert_assessment.py` | `id` | `assessment_id->expert_assessments.id, revised_by_user_id->users.id` | `tenant_indirect` | **YES** |
| 37 | `expert_assessments` | `ExpertAssessment` | `expert_assessment.py` | `id` | `case_id->expert_review_cases.id, expert_id->users.id` | `tenant_indirect` | **YES** |
| 38 | `expert_profiles` | `ExpertProfile` | `expert_profile.py` | `id` | `user_id->users.id, verified_by_user_id->users.id` | `user_owned` | **YES** |
| 39 | `expert_review_cases` | `ExpertReviewCase` | `expert_case.py` | `id` | `plot_id->plots.id, assigned_expert_id->users.id, farm_id->farms.id, observation_id->observations.id, diagnosis_request_id->diagnosis_requests.id` | `tenant_direct` | **YES** |
| 40 | `expert_reviews` | `ExpertReview` | `diagnosis.py` | `id` | `expert_id->users.id, diagnosis_request_id->diagnosis_requests.id` | `tenant_indirect` | **YES** |
| 41 | `farm_expenses` | `FarmExpense` | `financial_ledger.py` | `id` | `farm_id->farms.id, plot_id->plots.id, crop_season_id->crop_seasons.id` | `tenant_direct` | **YES** |
| 42 | `farm_memberships` | `FarmMembership` | `farm.py` | `id` | `farm_id->farms.id, user_id->users.id` | `tenant_direct` | **YES** |
| 43 | `farm_operations` | `FarmOperation` | `operation.py` | `id` | `plot_id->plots.id` | `tenant_indirect` | **YES** |
| 44 | `farm_practice_records` | `FarmPracticeRecord` | `sustainability.py` | `id` | `plot_id->plots.id` | `tenant_indirect` | **YES** |
| 45 | `farm_twins` | `FarmTwin` | `digital_twin.py` | `id` | `farm_id->farms.id` | `tenant_direct` | **YES** |
| 46 | `farms` | `Farm` | `farm.py` | `id` | `owner_id->users.id` | `tenant_direct` | **YES** |
| 47 | `financial_corrections` | `FinancialCorrection` | `financial_ledger.py` | `id` | `expense_id->farm_expenses.id` | `tenant_indirect` | **YES** |
| 48 | `fusion_explanations` | `FusionExplanation` | `evidence_fusion.py` | `id` | `plot_id->plots.id` | `tenant_indirect` | **YES** |
| 49 | `harvest_measurements` | `HarvestMeasurement` | `yield_research.py` | `id` | `plot_id->plots.id, season_id->crop_seasons.id` | `tenant_indirect` | **YES** |
| 50 | `harvest_plans` | `HarvestPlan` | `harvest_operations.py` | `id` | `crop_season_id->crop_seasons.id, plot_id->plots.id` | `tenant_indirect` | **YES** |
| 51 | `harvest_sessions` | `HarvestSession` | `harvest_operations.py` | `id` | `plot_id->plots.id, crop_season_id->crop_seasons.id, harvest_plan_id->harvest_plans.id` | `tenant_indirect` | **YES** |
| 52 | `image_quality_assessments` | `ImageQualityAssessment` | `observation.py` | `id` | `media_id->observation_media.id` | `tenant_indirect` | **YES** |
| 53 | `ingestion_jobs` | `IngestionJob` | `ingestion_job.py` | `id` | `document_id->knowledge_documents.id` | `shared_reference` | **YES** |
| 54 | `integration_partners` | `IntegrationPartner` | `interoperability.py` | `id` | `verified_by_user_id->users.id` | `shared_reference` | **YES** |
| 55 | `intervention_records` | `InterventionRecord` | `intervention.py` | `id` | `farm_id->farms.id, plot_id->plots.id, farmer_id->users.id` | `tenant_direct` | **YES** |
| 56 | `irrigation_events` | `IrrigationEvent` | `water_management.py` | `id` | `plot_id->plots.id, water_source_id->water_sources.id` | `tenant_indirect` | **YES** |
| 57 | `knowledge_chunks` | `KnowledgeChunk` | `knowledge_chunk.py` | `id` | `document_version_id->knowledge_document_versions.id` | `shared_reference` | **NO** |
| 58 | `knowledge_contributions` | `KnowledgeContribution` | `commons_contribution.py` | `id` | `contributor_id->users.id` | `community` | **YES** |
| 59 | `knowledge_document_versions` | `KnowledgeDocumentVersion` | `knowledge_document.py` | `id` | `document_id->knowledge_documents.id` | `shared_reference` | **NO** |
| 60 | `knowledge_documents` | `KnowledgeDocument` | `knowledge_document.py` | `id` | `source_id->knowledge_sources.id` | `shared_reference` | **NO** |
| 61 | `knowledge_embeddings` | `KnowledgeEmbedding` | `knowledge_embedding.py` | `id` | `chunk_id->knowledge_chunks.id` | `shared_reference` | **NO** |
| 62 | `knowledge_entities` | `KnowledgeEntity` | `knowledge_graph.py` | `id` | `None` | `shared_reference` | **NO** |
| 63 | `knowledge_feedback` | `KnowledgeFeedback` | `knowledge_feedback.py` | `id` | `user_id->users.id` | `user_owned` | **YES** |
| 64 | `knowledge_relationships` | `KnowledgeRelationship` | `knowledge_graph.py` | `id` | `source_entity_id->knowledge_entities.id, target_entity_id->knowledge_entities.id` | `shared_reference` | **NO** |
| 65 | `knowledge_sources` | `KnowledgeSource` | `knowledge_source.py` | `id` | `reviewer_id->users.id` | `shared_reference` | **NO** |
| 66 | `learning_feedback` | `LearningFeedback` | `extension_learning.py` | `id` | `resource_id->learning_resources.id, user_id->users.id` | `user_owned` | **YES** |
| 67 | `learning_resources` | `LearningResource` | `extension_learning.py` | `id` | `creator_user_id->users.id, creator_org_id->agricultural_organizations.id` | `shared_reference` | **NO** |
| 68 | `location_permissions` | `LocationPermission` | `geo_spatial.py` | `id` | `farm_id->farms.id, user_id->users.id` | `tenant_direct` | **YES** |
| 69 | `lot_movements` | `LotMovement` | `produce_traceability.py` | `id` | `lot_id->produce_lots.id` | `tenant_indirect` | **YES** |
| 70 | `market_commodities` | `MarketCommodity` | `market_intelligence.py` | `id` | `None` | `shared_reference` | **NO** |
| 71 | `market_locations` | `MarketLocation` | `market_intelligence.py` | `id` | `None` | `shared_reference` | **NO** |
| 72 | `market_price_observations` | `MarketPriceObservation` | `market_intelligence.py` | `id` | `commodity_id->market_commodities.id, market_id->market_locations.id` | `shared_reference` | **NO** |
| 73 | `nutrient_assessments` | `NutrientAssessment` | `nutrient_intelligence.py` | `id` | `soil_test_result_id->soil_test_results.id, crop_id->crops.id` | `tenant_indirect` | **YES** |
| 74 | `nutrient_expert_reviews` | `NutrientExpertReview` | `nutrient_intelligence.py` | `id` | `nutrient_assessment_id->nutrient_assessments.id, expert_user_id->users.id` | `tenant_indirect` | **YES** |
| 75 | `observation_media` | `ObservationMedia` | `observation.py` | `id` | `observation_id->observations.id` | `tenant_indirect` | **YES** |
| 76 | `observations` | `Observation` | `observation.py` | `id` | `plot_id->plots.id, observer_id->users.id, farm_id->farms.id, crop_season_id->crop_seasons.id` | `tenant_direct` | **YES** |
| 77 | `optimization_problems` | `OptimizationProblem` | `optimization.py` | `id` | `farm_id->farms.id, plot_id->plots.id` | `tenant_direct` | **YES** |
| 78 | `optimization_results` | `OptimizationResult` | `optimization.py` | `id` | `problem_id->optimization_problems.id` | `tenant_indirect` | **YES** |
| 79 | `organization_memberships` | `OrganizationMembership` | `collective.py` | `id` | `organization_id->agricultural_organizations.id, user_id->users.id` | `user_owned` | **YES** |
| 80 | `outcome_observations` | `OutcomeObservation` | `intervention.py` | `id` | `follow_up_observation_id->observations.id, intervention_id->intervention_records.id` | `tenant_indirect` | **YES** |
| 81 | `partner_integrations` | `PartnerIntegration` | `interoperability.py` | `id` | `partner_id->integration_partners.id` | `shared_reference` | **YES** |
| 82 | `plants` | `Plant` | `farm.py` | `id` | `plot_id->plots.id` | `tenant_indirect` | **YES** |
| 83 | `plot_geometries` | `PlotGeometry` | `geo_spatial.py` | `id` | `plot_id->plots.id` | `tenant_indirect` | **YES** |
| 84 | `plots` | `Plot` | `farm.py` | `id` | `farm_id->farms.id` | `tenant_direct` | **YES** |
| 85 | `prediction_candidates` | `PredictionCandidate` | `diagnosis.py` | `id` | `prediction_id->predictions.id` | `tenant_indirect` | **YES** |
| 86 | `predictions` | `Prediction` | `diagnosis.py` | `id` | `diagnosis_request_id->diagnosis_requests.id` | `tenant_indirect` | **YES** |
| 87 | `produce_lots` | `ProduceLot` | `produce_traceability.py` | `id` | `crop_season_id->crop_seasons.id, harvest_session_id->harvest_sessions.id, farm_id->farms.id, plot_id->plots.id` | `tenant_direct` | **YES** |
| 88 | `produce_quality_profiles` | `ProduceQualityProfile` | `post_harvest.py` | `id` | `None` | `shared_reference` | **NO** |
| 89 | `quality_measurements` | `QualityMeasurement` | `post_harvest.py` | `id` | `lot_id->produce_lots.id, session_id->harvest_sessions.id` | `tenant_indirect` | **YES** |
| 90 | `regional_signal_evidences` | `RegionalSignalEvidence` | `regional_pulse.py` | `id` | `signal_id->regional_signals.id` | `community` | **YES** |
| 91 | `regional_signals` | `RegionalSignal` | `regional_pulse.py` | `id` | `None` | `community` | **YES** |
| 92 | `research_consents` | `ResearchConsent` | `research_hub.py` | `id` | `farmer_id->users.id, project_id->research_projects.id` | `community` | **YES** |
| 93 | `research_projects` | `ResearchProject` | `research_hub.py` | `id` | `lead_researcher_id->users.id` | `community` | **YES** |
| 94 | `resilience_assessments` | `ResilienceAssessment` | `resilience_assessment.py` | `id` | `plot_id->plots.id` | `tenant_indirect` | **YES** |
| 95 | `resilience_scenario_simulations` | `ResilienceScenarioSimulation` | `resilience_assessment.py` | `id` | `assessment_id->resilience_assessments.id` | `tenant_indirect` | **YES** |
| 96 | `risk_alerts` | `RiskAlert` | `risk_alert.py` | `id` | `plot_id->plots.id, risk_assessment_id->risk_assessment_records.id, farm_id->farms.id` | `tenant_direct` | **YES** |
| 97 | `risk_assessment_records` | `RiskAssessmentRecord` | `risk_assessment.py` | `id` | `plot_id->plots.id, crop_season_id->crop_seasons.id, farm_id->farms.id, weather_data_id->weather_data.id` | `tenant_direct` | **YES** |
| 98 | `risk_assessments` | `RiskAssessment` | `operation.py` | `id` | `farm_id->farms.id, crop_season_id->crop_seasons.id` | `tenant_direct` | **YES** |
| 99 | `risk_rules` | `RiskRule` | `risk_rule.py` | `id` | `None` | `shared_reference` | **NO** |
| 100 | `roles` | `Role` | `user.py` | `id` | `None` | `shared_reference` | **NO** |
| 101 | `sale_transactions` | `SaleTransaction` | `financial_ledger.py` | `id` | `crop_season_id->crop_seasons.id` | `tenant_indirect` | **YES** |
| 102 | `satellite_acquisitions` | `SatelliteAcquisition` | `satellite.py` | `id` | `source_id->satellite_sources.id` | `shared_reference` | **NO** |
| 103 | `satellite_observations` | `SatelliteObservation` | `satellite.py` | `id` | `acquisition_id->satellite_acquisitions.id, plot_id->plots.id` | `tenant_indirect` | **YES** |
| 104 | `satellite_sources` | `SatelliteSource` | `satellite.py` | `id` | `None` | `shared_reference` | **NO** |
| 105 | `sensor_calibrations` | `SensorCalibration` | `sensor.py` | `id` | `device_id->sensor_devices.id` | `tenant_indirect` | **YES** |
| 106 | `sensor_devices` | `SensorDevice` | `sensor.py` | `id` | `farm_id->farms.id, plot_id->plots.id` | `tenant_direct` | **YES** |
| 107 | `sensor_measurements` | `SensorMeasurement` | `sensor.py` | `id` | `device_id->sensor_devices.id, plot_id->plots.id` | `tenant_indirect` | **YES** |
| 108 | `session_tokens` | `SessionToken` | `user.py` | `id` | `user_id->users.id` | `user_owned` | **YES** |
| 109 | `simulation_results` | `SimulationResult` | `simulation.py` | `id` | `scenario_id->simulation_scenarios.id` | `tenant_indirect` | **YES** |
| 110 | `simulation_scenarios` | `SimulationScenario` | `simulation.py` | `id` | `plot_id->plots.id, crop_season_id->crop_seasons.id, creator_id->users.id, baseline_snapshot_id->twin_snapshots.id` | `tenant_indirect` | **YES** |
| 111 | `soil_carbon_measurements` | `SoilCarbonMeasurement` | `sustainability.py` | `id` | `plot_id->plots.id` | `tenant_indirect` | **YES** |
| 112 | `soil_moisture_observations` | `SoilMoistureObservation` | `water_management.py` | `id` | `plot_id->plots.id` | `tenant_indirect` | **YES** |
| 113 | `soil_profiles` | `SoilProfile` | `soil_health.py` | `id` | `plot_id->plots.id` | `tenant_indirect` | **YES** |
| 114 | `soil_samples` | `SoilSample` | `soil_health.py` | `id` | `profile_id->soil_profiles.id, plot_id->plots.id, sampled_by_user_id->users.id` | `tenant_indirect` | **YES** |
| 115 | `soil_test_results` | `SoilTestResult` | `soil_health.py` | `id` | `soil_sample_id->soil_samples.id` | `tenant_indirect` | **YES** |
| 116 | `storage_locations` | `StorageLocation` | `post_harvest.py` | `id` | `farm_id->farms.id` | `tenant_direct` | **YES** |
| 117 | `storage_lots` | `StorageLot` | `post_harvest.py` | `id` | `lot_id->produce_lots.id, storage_location_id->storage_locations.id` | `tenant_indirect` | **YES** |
| 118 | `training_events` | `TrainingEvent` | `extension_learning.py` | `id` | `organizer_org_id->agricultural_organizations.id` | `shared_reference` | **NO** |
| 119 | `translation_versions` | `TranslationVersion` | `commons_contribution.py` | `id` | `contribution_id->knowledge_contributions.id` | `community` | **YES** |
| 120 | `twin_snapshots` | `TwinSnapshot` | `digital_twin.py` | `id` | `twin_id->farm_twins.id, created_by->users.id, crop_season_id->crop_seasons.id, plot_id->plots.id, farm_id->farms.id` | `tenant_direct` | **YES** |
| 121 | `twin_state_records` | `TwinStateRecord` | `digital_twin.py` | `id` | `snapshot_id->twin_snapshots.id` | `tenant_indirect` | **YES** |
| 122 | `twin_synchronization_events` | `TwinSynchronizationEvent` | `digital_twin.py` | `id` | `twin_id->farm_twins.id` | `tenant_indirect` | **YES** |
| 123 | `user_roles` | `UserRole` | `user.py` | `user_id, role_id` | `user_id->users.id, role_id->roles.id` | `user_owned` | **YES** |
| 124 | `users` | `User` | `user.py` | `id` | `None` | `user_owned` | **YES** |
| 125 | `water_balance_snapshots` | `WaterBalanceSnapshot` | `water_management.py` | `id` | `plot_id->plots.id` | `tenant_indirect` | **YES** |
| 126 | `water_sources` | `WaterSource` | `water_management.py` | `id` | `farm_id->farms.id` | `tenant_direct` | **YES** |
| 127 | `weather_data` | `WeatherData` | `weather_data.py` | `id` | `farm_id->farms.id` | `tenant_direct` | **YES** |
| 128 | `weather_observations` | `WeatherObservation` | `operation.py` | `id` | `farm_id->farms.id` | `tenant_direct` | **YES** |
| 129 | `webhook_deliveries` | `WebhookDelivery` | `interoperability.py` | `id` | `endpoint_id->webhook_endpoints.id, event_id->webhook_events.id` | `tenant_indirect` | **YES** |
| 130 | `webhook_endpoints` | `WebhookEndpoint` | `interoperability.py` | `id` | `partner_id->integration_partners.id, user_id->users.id` | `user_owned` | **YES** |
| 131 | `webhook_events` | `WebhookEvent` | `interoperability.py` | `id` | `None` | `tenant_direct` | **YES** |
| 132 | `yield_forecast_records` | `YieldForecastRecord` | `yield_research.py` | `id` | `season_id->crop_seasons.id, plot_id->plots.id` | `tenant_indirect` | **YES** |

---

## 3. Detailed Column Specification by Table

### agricultural_organizations (`AgriculturalOrganization`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\collective.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `name` (VARCHAR(150)) &mdash; NOT NULL
  - `org_type` (VARCHAR(50)) &mdash; NOT NULL
  - `registration_number` (VARCHAR(100)) &mdash; NULL
  - `state` (VARCHAR(100)) &mdash; NOT NULL
  - `district` (VARCHAR(100)) &mdash; NOT NULL
  - `description` (TEXT) &mdash; NULL
  - `contact_email` (VARCHAR(100)) &mdash; NULL
  - `contact_phone` (VARCHAR(20)) &mdash; NULL
  - `verification_status` (VARCHAR(50)) &mdash; NOT NULL
  - `verified_by_user_id` (VARCHAR(36)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### agricultural_practice_definitions (`AgriculturalPracticeDefinition`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\sustainability.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `code` (VARCHAR(50)) &mdash; NOT NULL
  - `category` (VARCHAR(50)) &mdash; NOT NULL
  - `title_en` (VARCHAR(150)) &mdash; NOT NULL
  - `title_te` (VARCHAR(150)) &mdash; NOT NULL
  - `title_hi` (VARCHAR(150)) &mdash; NOT NULL
  - `description_en` (TEXT) &mdash; NOT NULL
  - `specification_json` (TEXT) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### annotation_records (`AnnotationRecord`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\research_hub.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `task_id` (VARCHAR(36)) &mdash; NOT NULL
  - `annotator_id` (VARCHAR(36)) &mdash; NOT NULL
  - `label_taxonomy_version` (VARCHAR(50)) &mdash; NOT NULL
  - `label_assigned` (VARCHAR(100)) &mdash; NOT NULL
  - `confidence_score` (NUMERIC(5, 4)) &mdash; NOT NULL
  - `disagreement_flag` (BOOLEAN) &mdash; NOT NULL
  - `notes` (TEXT) &mdash; NULL
  - `submitted_at` (DATETIME) &mdash; NOT NULL

### annotation_tasks (`AnnotationTask`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\research_hub.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `project_id` (VARCHAR(36)) &mdash; NOT NULL
  - `assigned_expert_id` (VARCHAR(36)) &mdash; NULL
  - `task_type` (VARCHAR(50)) &mdash; NOT NULL
  - `entity_reference_id` (VARCHAR(100)) &mdash; NOT NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL

### api_applications (`ApiApplication`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\interoperability.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `partner_id` (VARCHAR(36)) &mdash; NULL
  - `name` (VARCHAR(120)) &mdash; NOT NULL
  - `description` (TEXT) &mdash; NULL
  - `is_sandbox` (BOOLEAN) &mdash; NOT NULL
  - `is_active` (BOOLEAN) &mdash; NOT NULL
  - `redirect_uris_json` (TEXT) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### api_credentials (`ApiCredential`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\interoperability.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `application_id` (VARCHAR(36)) &mdash; NOT NULL
  - `client_id` (VARCHAR(80)) &mdash; NOT NULL
  - `hashed_secret` (VARCHAR(128)) &mdash; NOT NULL
  - `secret_prefix` (VARCHAR(16)) &mdash; NOT NULL
  - `scopes_json` (TEXT) &mdash; NOT NULL
  - `rate_limit_per_minute` (INTEGER) &mdash; NOT NULL
  - `is_active` (BOOLEAN) &mdash; NOT NULL
  - `expires_at` (DATETIME) &mdash; NULL
  - `last_used_at` (DATETIME) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL

### audit_logs (`AuditLog`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\governance.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NULL
  - `farm_id` (VARCHAR(36)) &mdash; NULL
  - `action` (VARCHAR(100)) &mdash; NOT NULL
  - `resource_type` (VARCHAR(50)) &mdash; NOT NULL
  - `resource_id` (VARCHAR(36)) &mdash; NULL
  - `ip_address` (VARCHAR(45)) &mdash; NULL
  - `timestamp` (DATETIME) &mdash; NOT NULL
  - `metadata_json` (VARCHAR(2000)) &mdash; NULL

### climate_adaptation_scenarios (`ClimateAdaptationScenario`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\climate_resilience.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `assessment_id` (VARCHAR(36)) &mdash; NOT NULL
  - `title` (VARCHAR(150)) &mdash; NOT NULL
  - `description` (TEXT) &mdash; NOT NULL
  - `projected_loss_reduction_percent` (FLOAT) &mdash; NOT NULL
  - `cost_delta_inr` (FLOAT) &mdash; NOT NULL
  - `intervention_actions_json` (TEXT) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### climate_baselines (`ClimateBaseline`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\climate_resilience.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `district_code` (VARCHAR(50)) &mdash; NOT NULL
  - `month` (INTEGER) &mdash; NOT NULL
  - `normal_rainfall_mm` (FLOAT) &mdash; NOT NULL
  - `normal_tmax_celsius` (FLOAT) &mdash; NOT NULL
  - `normal_tmin_celsius` (FLOAT) &mdash; NOT NULL
  - `extreme_heat_days_p90` (FLOAT) &mdash; NOT NULL
  - `dry_spell_frequency` (FLOAT) &mdash; NOT NULL
  - `heavy_rain_days_count` (FLOAT) &mdash; NOT NULL
  - `baseline_period` (VARCHAR(20)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### climate_exposure_assessments (`ClimateExposureAssessment`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\climate_resilience.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `crop_id` (VARCHAR(36)) &mdash; NULL
  - `hazard_type` (VARCHAR(50)) &mdash; NOT NULL
  - `severity_level` (VARCHAR(30)) &mdash; NOT NULL
  - `crop_stage` (VARCHAR(100)) &mdash; NOT NULL
  - `vulnerability_score` (FLOAT) &mdash; NOT NULL
  - `forecast_tmax` (FLOAT) &mdash; NULL
  - `forecast_rainfall_next_7_days` (FLOAT) &mdash; NULL
  - `consecutive_rainless_days` (INTEGER) &mdash; NULL
  - `recommended_adaptation` (TEXT) &mdash; NOT NULL
  - `institutional_citation` (VARCHAR(200)) &mdash; NOT NULL
  - `assessed_at` (DATETIME) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### collective_activities (`CollectiveActivity`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\collective.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `organization_id` (VARCHAR(36)) &mdash; NOT NULL
  - `created_by_user_id` (VARCHAR(36)) &mdash; NULL
  - `activity_type` (VARCHAR(50)) &mdash; NOT NULL
  - `title` (VARCHAR(200)) &mdash; NOT NULL
  - `description` (TEXT) &mdash; NOT NULL
  - `target_date` (DATE) &mdash; NOT NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### communities (`Community`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\community.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `name` (VARCHAR(100)) &mdash; NOT NULL
  - `slug` (VARCHAR(100)) &mdash; NOT NULL
  - `description` (TEXT) &mdash; NOT NULL
  - `category` (VARCHAR(50)) &mdash; NOT NULL
  - `crop_id` (VARCHAR(50)) &mdash; NULL
  - `district` (VARCHAR(100)) &mdash; NULL
  - `is_moderated` (BOOLEAN) &mdash; NOT NULL
  - `created_by_user_id` (VARCHAR(36)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### community_comments (`CommunityComment`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\community.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `post_id` (VARCHAR(36)) &mdash; NOT NULL
  - `author_id` (VARCHAR(36)) &mdash; NOT NULL
  - `content` (TEXT) &mdash; NOT NULL
  - `is_expert_reply` (BOOLEAN) &mdash; NOT NULL
  - `is_helpful` (BOOLEAN) &mdash; NOT NULL
  - `moderation_status` (VARCHAR(30)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL

### community_memberships (`CommunityMembership`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\community.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `community_id` (VARCHAR(36)) &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `role` (VARCHAR(50)) &mdash; NOT NULL
  - `joined_at` (DATETIME) &mdash; NOT NULL

### community_posts (`CommunityPost`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\community.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `community_id` (VARCHAR(36)) &mdash; NOT NULL
  - `author_id` (VARCHAR(36)) &mdash; NOT NULL
  - `post_type` (VARCHAR(50)) &mdash; NOT NULL
  - `title` (VARCHAR(200)) &mdash; NOT NULL
  - `content` (TEXT) &mdash; NOT NULL
  - `language` (VARCHAR(10)) &mdash; NOT NULL
  - `crop_id` (VARCHAR(50)) &mdash; NULL
  - `growth_stage` (VARCHAR(50)) &mdash; NULL
  - `visibility` (VARCHAR(30)) &mdash; NOT NULL
  - `moderation_status` (VARCHAR(30)) &mdash; NOT NULL
  - `is_expert_reviewed` (BOOLEAN) &mdash; NOT NULL
  - `helpful_count` (INTEGER) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### community_reports (`CommunityReport`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\community.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `post_id` (VARCHAR(36)) &mdash; NULL
  - `comment_id` (VARCHAR(36)) &mdash; NULL
  - `reported_by_user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `reason_category` (VARCHAR(50)) &mdash; NOT NULL
  - `details` (TEXT) &mdash; NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `reviewed_by_user_id` (VARCHAR(36)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL

### consent_records (`ConsentRecord`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\governance.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `consent_type` (VARCHAR(50)) &mdash; NOT NULL
  - `is_granted` (BOOLEAN) &mdash; NOT NULL
  - `policy_version` (VARCHAR(20)) &mdash; NOT NULL
  - `granted_at` (DATETIME) &mdash; NOT NULL
  - `revoked_at` (DATETIME) &mdash; NULL

### contribution_reviews (`ContributionReview`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\commons_contribution.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `contribution_id` (VARCHAR(36)) &mdash; NOT NULL
  - `reviewer_id` (VARCHAR(36)) &mdash; NOT NULL
  - `reviewer_role` (VARCHAR(50)) &mdash; NOT NULL
  - `decision` (VARCHAR(30)) &mdash; NOT NULL
  - `comments` (TEXT) &mdash; NOT NULL
  - `scientific_rating` (INTEGER) &mdash; NOT NULL
  - `safety_assessment` (TEXT) &mdash; NULL
  - `reviewed_at` (DATETIME) &mdash; NOT NULL

### crop_calendar_definitions (`CropCalendarDefinition`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\crop_planning.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `crop_id` (VARCHAR(50)) &mdash; NOT NULL
  - `variety_id` (VARCHAR(100)) &mdash; NULL
  - `agro_climatic_zone` (VARCHAR(100)) &mdash; NOT NULL
  - `growth_stage` (VARCHAR(100)) &mdash; NOT NULL
  - `typical_duration_days` (INTEGER) &mdash; NOT NULL
  - `recommended_tasks_json` (JSON) &mdash; NOT NULL
  - `source_citation` (TEXT) &mdash; NOT NULL
  - `version` (VARCHAR(20)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### crop_loss_evidence_packages (`CropLossEvidencePackage`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\evidence_package.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `crop_season_id` (VARCHAR(36)) &mdash; NOT NULL
  - `incident_date` (DATE) &mdash; NOT NULL
  - `incident_type` (VARCHAR(50)) &mdash; NOT NULL
  - `package_payload_json` (TEXT) &mdash; NOT NULL
  - `package_hash` (VARCHAR(64)) &mdash; NOT NULL
  - `generated_at` (DATETIME) &mdash; NOT NULL

### crop_season_economics (`CropSeasonEconomics`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\crop_economics.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `crop_season_id` (VARCHAR(36)) &mdash; NOT NULL
  - `total_expenses` (NUMERIC(12, 2)) &mdash; NOT NULL
  - `gross_revenue` (NUMERIC(12, 2)) &mdash; NOT NULL
  - `net_realization` (NUMERIC(12, 2)) &mdash; NOT NULL
  - `total_harvest_quantity` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `total_sold_quantity` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `unit` (VARCHAR(20)) &mdash; NOT NULL
  - `cost_per_unit` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `net_margin_per_unit` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `data_completeness_pct` (NUMERIC(5, 2)) &mdash; NOT NULL
  - `calculated_at` (DATETIME) &mdash; NOT NULL

### crop_seasons (`CropSeason`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\crop.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `crop_id` (VARCHAR(50)) &mdash; NOT NULL
  - `variety_id` (VARCHAR(36)) &mdash; NULL
  - `season_type` (VARCHAR(20)) &mdash; NOT NULL
  - `sowing_date` (DATE) &mdash; NOT NULL
  - `current_stage` (VARCHAR(50)) &mdash; NOT NULL
  - `status` (VARCHAR(20)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### crop_stage_events (`CropStageEvent`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\crop.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `crop_season_id` (VARCHAR(36)) &mdash; NOT NULL
  - `stage_name` (VARCHAR(50)) &mdash; NOT NULL
  - `event_date` (DATE) &mdash; NOT NULL
  - `notes` (VARCHAR(500)) &mdash; NULL

### crop_tasks (`CropTask`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\crop_planning.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `crop_season_id` (VARCHAR(36)) &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `calendar_def_id` (VARCHAR(36)) &mdash; NULL
  - `task_name` (VARCHAR(150)) &mdash; NOT NULL
  - `task_category` (VARCHAR(50)) &mdash; NOT NULL
  - `due_date` (DATE) &mdash; NOT NULL
  - `completed_date` (DATE) &mdash; NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `weather_conflict_flag` (BOOLEAN) &mdash; NOT NULL
  - `conflict_reason` (VARCHAR(255)) &mdash; NULL
  - `execution_details_json` (JSON) &mdash; NOT NULL
  - `notes` (TEXT) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### crop_varieties (`CropVariety`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\crop.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `crop_id` (VARCHAR(50)) &mdash; NOT NULL
  - `name` (VARCHAR(100)) &mdash; NOT NULL
  - `duration_days` (INTEGER) &mdash; NOT NULL
  - `resistance_traits` (VARCHAR(255)) &mdash; NULL

### crops (`Crop`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\crop.py`
  - `id` (VARCHAR(50)) [PK] &mdash; NOT NULL
  - `name_en` (VARCHAR(100)) &mdash; NOT NULL
  - `name_te` (VARCHAR(100)) &mdash; NOT NULL
  - `name_hi` (VARCHAR(100)) &mdash; NOT NULL
  - `scientific_name` (VARCHAR(100)) &mdash; NOT NULL

### data_exchange_jobs (`DataExchangeJob`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\exchange.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NULL
  - `job_type` (VARCHAR(20)) &mdash; NOT NULL
  - `format` (VARCHAR(20)) &mdash; NOT NULL
  - `categories_json` (TEXT) &mdash; NOT NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `records_processed` (INTEGER) &mdash; NOT NULL
  - `records_failed` (INTEGER) &mdash; NOT NULL
  - `conflicts_detected` (INTEGER) &mdash; NOT NULL
  - `manifest_json` (TEXT) &mdash; NOT NULL
  - `storage_path` (VARCHAR(500)) &mdash; NULL
  - `checksum_sha256` (VARCHAR(64)) &mdash; NULL
  - `redact_pii` (BOOLEAN) &mdash; NOT NULL
  - `preserve_conflicts` (BOOLEAN) &mdash; NOT NULL
  - `error_message` (TEXT) &mdash; NULL
  - `expires_at` (DATETIME) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### data_mapping_profiles (`DataMappingProfile`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\exchange.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `name` (VARCHAR(150)) &mdash; NOT NULL
  - `source_format` (VARCHAR(50)) &mdash; NOT NULL
  - `target_entity` (VARCHAR(50)) &mdash; NOT NULL
  - `mapping_rules_json` (TEXT) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL

### data_sharing_grants (`DataSharingGrant`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\interoperability.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `partner_id` (VARCHAR(36)) &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NULL
  - `plot_id` (VARCHAR(36)) &mdash; NULL
  - `data_categories_json` (TEXT) &mdash; NOT NULL
  - `purpose` (VARCHAR(255)) &mdash; NOT NULL
  - `anonymize_pii` (BOOLEAN) &mdash; NOT NULL
  - `redact_exact_gps` (BOOLEAN) &mdash; NOT NULL
  - `is_revoked` (BOOLEAN) &mdash; NOT NULL
  - `granted_at` (DATETIME) &mdash; NOT NULL
  - `expires_at` (DATETIME) &mdash; NULL
  - `revoked_at` (DATETIME) &mdash; NULL
  - `revocation_reason` (TEXT) &mdash; NULL

### dataset_contributions (`DatasetContribution`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\research_hub.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `project_id` (VARCHAR(36)) &mdash; NOT NULL
  - `contributor_id` (VARCHAR(36)) &mdash; NOT NULL
  - `dataset_name` (VARCHAR(150)) &mdash; NOT NULL
  - `crop_id` (VARCHAR(50)) &mdash; NOT NULL
  - `sample_count` (INTEGER) &mdash; NOT NULL
  - `data_type` (VARCHAR(50)) &mdash; NOT NULL
  - `split_type` (VARCHAR(20)) &mdash; NOT NULL
  - `storage_uri` (VARCHAR(500)) &mdash; NOT NULL
  - `license` (VARCHAR(50)) &mdash; NOT NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### decision_feedbacks (`DecisionFeedback`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\decision_intelligence.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `decision_id` (VARCHAR(36)) &mdash; NOT NULL
  - `farmer_action_taken` (VARCHAR(50)) &mdash; NOT NULL
  - `farmer_rating` (INTEGER) &mdash; NULL
  - `feedback_notes` (TEXT) &mdash; NULL
  - `observed_outcome` (TEXT) &mdash; NULL
  - `recorded_at` (DATETIME) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### decision_records (`DecisionRecord`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\decision_intelligence.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `farmer_id` (VARCHAR(36)) &mdash; NOT NULL
  - `query_text` (TEXT) &mdash; NOT NULL
  - `decision_category` (VARCHAR(50)) &mdash; NOT NULL
  - `recommendation_state` (VARCHAR(50)) &mdash; NOT NULL
  - `evidence_sources_json` (JSON) &mdash; NOT NULL
  - `grounded_explanation_en` (TEXT) &mdash; NOT NULL
  - `grounded_explanation_te` (TEXT) &mdash; NOT NULL
  - `grounded_explanation_hi` (TEXT) &mdash; NOT NULL
  - `uncertainty_disclosures_json` (JSON) &mdash; NOT NULL
  - `expert_escalation_case_id` (VARCHAR(36)) &mdash; NULL
  - `evaluated_at` (DATETIME) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### diagnosis_requests (`DiagnosisRequest`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\diagnosis.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `observation_id` (VARCHAR(36)) &mdash; NOT NULL
  - `media_id` (VARCHAR(36)) &mdash; NULL
  - `status` (VARCHAR(50)) &mdash; NOT NULL
  - `requested_at` (DATETIME) &mdash; NOT NULL
  - `completed_at` (DATETIME) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### environmental_accounting_estimates (`EnvironmentalAccountingEstimate`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\sustainability.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `season` (VARCHAR(30)) &mdash; NOT NULL
  - `year` (INTEGER) &mdash; NOT NULL
  - `fertilizer_n2o_kg_co2e` (FLOAT) &mdash; NOT NULL
  - `paddy_ch4_kg_co2e` (FLOAT) &mdash; NOT NULL
  - `fuel_combustion_kg_co2e` (FLOAT) &mdash; NOT NULL
  - `total_emissions_kg_co2e` (FLOAT) &mdash; NOT NULL
  - `emission_intensity_kg_co2e_per_kg` (FLOAT) &mdash; NULL
  - `is_certified` (BOOLEAN) &mdash; NOT NULL
  - `scientific_disclaimer` (TEXT) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### event_registrations (`EventRegistration`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\extension_learning.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `event_id` (VARCHAR(36)) &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `attendance_status` (VARCHAR(30)) &mdash; NOT NULL
  - `registered_at` (DATETIME) &mdash; NOT NULL

### expert_assessment_revisions (`ExpertAssessmentRevision`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\expert_assessment.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `assessment_id` (VARCHAR(36)) &mdash; NOT NULL
  - `revision_number` (INTEGER) &mdash; NOT NULL
  - `previous_assessment_json` (TEXT) &mdash; NOT NULL
  - `revision_reason` (TEXT) &mdash; NOT NULL
  - `revised_by_user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `revised_at` (DATETIME) &mdash; NOT NULL

### expert_assessments (`ExpertAssessment`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\expert_assessment.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `case_id` (VARCHAR(36)) &mdash; NOT NULL
  - `expert_id` (VARCHAR(36)) &mdash; NOT NULL
  - `confirmed_crop` (VARCHAR(50)) &mdash; NOT NULL
  - `primary_condition` (VARCHAR(100)) &mdash; NOT NULL
  - `differential_diagnoses_json` (TEXT) &mdash; NULL
  - `confidence_rating` (INTEGER) &mdash; NOT NULL
  - `urgency_level` (VARCHAR(20)) &mdash; NOT NULL
  - `management_plan` (TEXT) &mdash; NOT NULL
  - `ipm_strategy` (TEXT) &mdash; NOT NULL
  - `cibrc_advisories` (TEXT) &mdash; NOT NULL
  - `revision_count` (INTEGER) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### expert_profiles (`ExpertProfile`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\expert_profile.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `registration_number` (VARCHAR(100)) &mdash; NULL
  - `highest_degree` (VARCHAR(100)) &mdash; NOT NULL
  - `institution` (VARCHAR(150)) &mdash; NOT NULL
  - `specializations_json` (VARCHAR(500)) &mdash; NOT NULL
  - `districts_covered_json` (VARCHAR(500)) &mdash; NOT NULL
  - `verification_status` (VARCHAR(50)) &mdash; NOT NULL
  - `verified_by_user_id` (VARCHAR(36)) &mdash; NULL
  - `verified_at` (DATETIME) &mdash; NULL
  - `rejection_reason` (TEXT) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### expert_review_cases (`ExpertReviewCase`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\expert_case.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `diagnosis_request_id` (VARCHAR(36)) &mdash; NULL
  - `observation_id` (VARCHAR(36)) &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NULL
  - `crop_id` (VARCHAR(50)) &mdash; NOT NULL
  - `priority` (VARCHAR(20)) &mdash; NOT NULL
  - `status` (VARCHAR(50)) &mdash; NOT NULL
  - `assigned_expert_id` (VARCHAR(36)) &mdash; NULL
  - `assigned_at` (DATETIME) &mdash; NULL
  - `completed_at` (DATETIME) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### expert_reviews (`ExpertReview`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\diagnosis.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `diagnosis_request_id` (VARCHAR(36)) &mdash; NOT NULL
  - `expert_id` (VARCHAR(36)) &mdash; NOT NULL
  - `status` (VARCHAR(50)) &mdash; NOT NULL
  - `verified_class_id` (VARCHAR(100)) &mdash; NULL
  - `expert_notes` (VARCHAR(1000)) &mdash; NULL
  - `reviewed_at` (DATETIME) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### farm_expenses (`FarmExpense`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\financial_ledger.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NULL
  - `crop_season_id` (VARCHAR(36)) &mdash; NULL
  - `category` (VARCHAR(50)) &mdash; NOT NULL
  - `description` (TEXT) &mdash; NOT NULL
  - `amount` (NUMERIC(12, 2)) &mdash; NOT NULL
  - `currency` (VARCHAR(10)) &mdash; NOT NULL
  - `quantity` (NUMERIC(10, 2)) &mdash; NULL
  - `unit` (VARCHAR(20)) &mdash; NULL
  - `transaction_date` (DATE) &mdash; NOT NULL
  - `payment_status` (VARCHAR(20)) &mdash; NOT NULL
  - `payment_method` (VARCHAR(30)) &mdash; NULL
  - `vendor_name` (VARCHAR(100)) &mdash; NULL
  - `receipt_url` (VARCHAR(500)) &mdash; NULL
  - `created_by_user_id` (VARCHAR(36)) &mdash; NULL
  - `verification_state` (VARCHAR(30)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### farm_memberships (`FarmMembership`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\farm.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `role_in_farm` (VARCHAR(50)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### farm_operations (`FarmOperation`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\operation.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `operation_type` (VARCHAR(50)) &mdash; NOT NULL
  - `execution_date` (DATE) &mdash; NOT NULL
  - `details_json` (VARCHAR(1000)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### farm_practice_records (`FarmPracticeRecord`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\sustainability.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `practice_code` (VARCHAR(50)) &mdash; NOT NULL
  - `implementation_date` (DATETIME) &mdash; NOT NULL
  - `area_covered_acres` (FLOAT) &mdash; NOT NULL
  - `verification_method` (VARCHAR(50)) &mdash; NOT NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### farm_twins (`FarmTwin`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\digital_twin.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `twin_version` (INTEGER) &mdash; NOT NULL
  - `state_status` (VARCHAR(50)) &mdash; NOT NULL
  - `last_synchronized_at` (DATETIME) &mdash; NOT NULL
  - `completeness_score` (FLOAT) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### farms (`Farm`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\farm.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `owner_id` (VARCHAR(36)) &mdash; NOT NULL
  - `name` (VARCHAR(100)) &mdash; NOT NULL
  - `state` (VARCHAR(50)) &mdash; NOT NULL
  - `district` (VARCHAR(50)) &mdash; NOT NULL
  - `mandal` (VARCHAR(50)) &mdash; NOT NULL
  - `village` (VARCHAR(50)) &mdash; NOT NULL
  - `total_acreage` (FLOAT) &mdash; NOT NULL
  - `is_archived` (BOOLEAN) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### financial_corrections (`FinancialCorrection`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\financial_ledger.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `expense_id` (VARCHAR(36)) &mdash; NOT NULL
  - `previous_amount` (NUMERIC(12, 2)) &mdash; NOT NULL
  - `new_amount` (NUMERIC(12, 2)) &mdash; NOT NULL
  - `reason` (TEXT) &mdash; NOT NULL
  - `corrected_by_user_id` (VARCHAR(36)) &mdash; NULL
  - `corrected_at` (DATETIME) &mdash; NOT NULL

### fusion_explanations (`FusionExplanation`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\evidence_fusion.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `evaluation_timestamp` (DATETIME) &mdash; NOT NULL
  - `overall_vigor_status` (VARCHAR(50)) &mdash; NOT NULL
  - `primary_stress_driver` (VARCHAR(50)) &mdash; NOT NULL
  - `evidence_sources_json` (JSON) &mdash; NOT NULL
  - `contradictions_detected_json` (JSON) &mdash; NOT NULL
  - `farmer_explanation_en` (TEXT) &mdash; NOT NULL
  - `farmer_explanation_te` (TEXT) &mdash; NOT NULL
  - `farmer_explanation_hi` (TEXT) &mdash; NOT NULL
  - `epistemic_qualifications_json` (JSON) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### harvest_measurements (`HarvestMeasurement`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\yield_research.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `season_id` (VARCHAR(36)) &mdash; NOT NULL
  - `harvest_date` (DATETIME) &mdash; NOT NULL
  - `yield_quintals_per_acre` (FLOAT) &mdash; NOT NULL
  - `total_harvest_kg` (FLOAT) &mdash; NOT NULL
  - `provenance_tier` (VARCHAR(50)) &mdash; NOT NULL
  - `verification_document_url` (VARCHAR(500)) &mdash; NULL
  - `notes` (TEXT) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### harvest_plans (`HarvestPlan`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\harvest_operations.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `crop_season_id` (VARCHAR(36)) &mdash; NOT NULL
  - `planned_start_date` (DATE) &mdash; NOT NULL
  - `planned_end_date` (DATE) &mdash; NOT NULL
  - `estimated_quantity_quintals` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `harvest_method` (VARCHAR(50)) &mdash; NOT NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### harvest_sessions (`HarvestSession`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\harvest_operations.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `crop_season_id` (VARCHAR(36)) &mdash; NOT NULL
  - `harvest_plan_id` (VARCHAR(36)) &mdash; NULL
  - `picking_number` (INTEGER) &mdash; NOT NULL
  - `harvest_date` (DATE) &mdash; NOT NULL
  - `harvested_quantity` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `unit` (VARCHAR(20)) &mdash; NOT NULL
  - `quantity_type` (VARCHAR(30)) &mdash; NOT NULL
  - `loss_quantity` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `notes` (TEXT) &mdash; NULL
  - `recorded_by_user_id` (VARCHAR(36)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### image_quality_assessments (`ImageQualityAssessment`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\observation.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `media_id` (VARCHAR(36)) &mdash; NOT NULL
  - `status` (VARCHAR(50)) &mdash; NOT NULL
  - `sharpness_score` (FLOAT) &mdash; NOT NULL
  - `exposure_status` (VARCHAR(50)) &mdash; NOT NULL
  - `reasons_json` (VARCHAR(1000)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### ingestion_jobs (`IngestionJob`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\ingestion_job.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `document_id` (VARCHAR(36)) &mdash; NOT NULL
  - `document_version_id` (VARCHAR(36)) &mdash; NULL
  - `status` (VARCHAR(50)) &mdash; NOT NULL
  - `stage` (VARCHAR(50)) &mdash; NOT NULL
  - `progress_pct` (INTEGER) &mdash; NOT NULL
  - `error_message` (TEXT) &mdash; NULL
  - `attempt_count` (INTEGER) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### integration_partners (`IntegrationPartner`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\interoperability.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `name` (VARCHAR(150)) &mdash; NOT NULL
  - `partner_type` (VARCHAR(50)) &mdash; NOT NULL
  - `description` (TEXT) &mdash; NULL
  - `website` (VARCHAR(255)) &mdash; NULL
  - `contact_email` (VARCHAR(100)) &mdash; NOT NULL
  - `contact_phone` (VARCHAR(30)) &mdash; NULL
  - `legal_entity_number` (VARCHAR(100)) &mdash; NULL
  - `verification_status` (VARCHAR(30)) &mdash; NOT NULL
  - `verification_notes` (TEXT) &mdash; NULL
  - `verified_at` (DATETIME) &mdash; NULL
  - `verified_by_user_id` (VARCHAR(36)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### intervention_records (`InterventionRecord`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\intervention.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `farmer_id` (VARCHAR(36)) &mdash; NOT NULL
  - `category` (VARCHAR(50)) &mdash; NOT NULL
  - `trade_name` (VARCHAR(150)) &mdash; NOT NULL
  - `active_ingredient` (VARCHAR(150)) &mdash; NULL
  - `dosage` (FLOAT) &mdash; NOT NULL
  - `unit` (VARCHAR(30)) &mdash; NOT NULL
  - `application_method` (VARCHAR(100)) &mdash; NOT NULL
  - `application_date` (DATE) &mdash; NOT NULL
  - `target_condition` (VARCHAR(100)) &mdash; NULL
  - `phi_days` (INTEGER) &mdash; NOT NULL
  - `rei_hours` (INTEGER) &mdash; NOT NULL
  - `notes` (TEXT) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### irrigation_events (`IrrigationEvent`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\water_management.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `water_source_id` (VARCHAR(36)) &mdash; NULL
  - `event_date` (DATETIME) &mdash; NOT NULL
  - `irrigation_method` (VARCHAR(50)) &mdash; NOT NULL
  - `duration_hours` (FLOAT) &mdash; NOT NULL
  - `flow_meter_start_m3` (FLOAT) &mdash; NULL
  - `flow_meter_end_m3` (FLOAT) &mdash; NULL
  - `calculated_volume_m3` (FLOAT) &mdash; NOT NULL
  - `equivalent_depth_mm` (FLOAT) &mdash; NOT NULL
  - `soil_moisture_before` (FLOAT) &mdash; NULL
  - `soil_moisture_after` (FLOAT) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### knowledge_chunks (`KnowledgeChunk`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\knowledge_chunk.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `document_version_id` (VARCHAR(36)) &mdash; NOT NULL
  - `chunk_index` (INTEGER) &mdash; NOT NULL
  - `parent_section` (VARCHAR(200)) &mdash; NULL
  - `heading_path` (VARCHAR(500)) &mdash; NULL
  - `content` (TEXT) &mdash; NOT NULL
  - `language` (VARCHAR(10)) &mdash; NOT NULL
  - `crop_scope` (VARCHAR(50)) &mdash; NOT NULL
  - `region_scope` (VARCHAR(50)) &mdash; NOT NULL
  - `growth_stage_scope` (VARCHAR(50)) &mdash; NOT NULL
  - `page_start` (INTEGER) &mdash; NULL
  - `page_end` (INTEGER) &mdash; NULL
  - `token_count` (INTEGER) &mdash; NOT NULL
  - `content_hash` (VARCHAR(64)) &mdash; NOT NULL
  - `approval_status` (VARCHAR(50)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### knowledge_contributions (`KnowledgeContribution`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\commons_contribution.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `contributor_id` (VARCHAR(36)) &mdash; NOT NULL
  - `contribution_type` (VARCHAR(50)) &mdash; NOT NULL
  - `title` (VARCHAR(200)) &mdash; NOT NULL
  - `description` (TEXT) &mdash; NOT NULL
  - `original_language` (VARCHAR(10)) &mdash; NOT NULL
  - `crop_id` (VARCHAR(50)) &mdash; NULL
  - `geographic_scope` (VARCHAR(100)) &mdash; NOT NULL
  - `growth_stage` (VARCHAR(50)) &mdash; NULL
  - `evidence_references_json` (TEXT) &mdash; NOT NULL
  - `usage_permission` (VARCHAR(50)) &mdash; NOT NULL
  - `status` (VARCHAR(50)) &mdash; NOT NULL
  - `assigned_expert_id` (VARCHAR(36)) &mdash; NULL
  - `approved_by_user_id` (VARCHAR(36)) &mdash; NULL
  - `krishi_brain_ingested` (BOOLEAN) &mdash; NOT NULL
  - `krishi_brain_doc_id` (VARCHAR(36)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### knowledge_document_versions (`KnowledgeDocumentVersion`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\knowledge_document.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `document_id` (VARCHAR(36)) &mdash; NOT NULL
  - `version_number` (INTEGER) &mdash; NOT NULL
  - `content_hash` (VARCHAR(64)) &mdash; NOT NULL
  - `original_file_path` (VARCHAR(500)) &mdash; NULL
  - `publication_date` (DATE) &mdash; NULL
  - `extraction_status` (VARCHAR(50)) &mdash; NOT NULL
  - `review_status` (VARCHAR(50)) &mdash; NOT NULL
  - `supersedes_version_id` (VARCHAR(36)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### knowledge_documents (`KnowledgeDocument`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\knowledge_document.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `source_id` (VARCHAR(36)) &mdash; NOT NULL
  - `title` (VARCHAR(255)) &mdash; NOT NULL
  - `canonical_url` (VARCHAR(500)) &mdash; NULL
  - `document_type` (VARCHAR(20)) &mdash; NOT NULL
  - `primary_language` (VARCHAR(10)) &mdash; NOT NULL
  - `crop_scope` (VARCHAR(50)) &mdash; NOT NULL
  - `region_scope` (VARCHAR(50)) &mdash; NOT NULL
  - `topic_scope` (VARCHAR(100)) &mdash; NULL
  - `current_version_id` (VARCHAR(36)) &mdash; NULL
  - `status` (VARCHAR(50)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### knowledge_embeddings (`KnowledgeEmbedding`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\knowledge_embedding.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `chunk_id` (VARCHAR(36)) &mdash; NOT NULL
  - `embedding_profile_id` (VARCHAR(100)) &mdash; NOT NULL
  - `embedding` (VECTOR(1536)) &mdash; NOT NULL
  - `model_name` (VARCHAR(100)) &mdash; NOT NULL
  - `model_version` (VARCHAR(50)) &mdash; NOT NULL
  - `dimensions` (INTEGER) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL

### knowledge_entities (`KnowledgeEntity`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\knowledge_graph.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `entity_type` (VARCHAR(50)) &mdash; NOT NULL
  - `canonical_name` (VARCHAR(150)) &mdash; NOT NULL
  - `local_name_te` (VARCHAR(150)) &mdash; NULL
  - `local_name_hi` (VARCHAR(150)) &mdash; NULL
  - `scientific_name` (VARCHAR(150)) &mdash; NULL
  - `properties_json` (JSON) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### knowledge_feedback (`KnowledgeFeedback`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\knowledge_feedback.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `query_id` (VARCHAR(64)) &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NULL
  - `issue_category` (VARCHAR(50)) &mdash; NOT NULL
  - `user_comments` (TEXT) &mdash; NULL
  - `reviewer_status` (VARCHAR(50)) &mdash; NOT NULL
  - `resolution_notes` (TEXT) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### knowledge_relationships (`KnowledgeRelationship`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\knowledge_graph.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `source_entity_id` (VARCHAR(36)) &mdash; NOT NULL
  - `target_entity_id` (VARCHAR(36)) &mdash; NOT NULL
  - `relationship_type` (VARCHAR(50)) &mdash; NOT NULL
  - `confidence_weight` (FLOAT) &mdash; NOT NULL
  - `evidence_source` (VARCHAR(200)) &mdash; NOT NULL
  - `properties_json` (JSON) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### knowledge_sources (`KnowledgeSource`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\knowledge_source.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `publisher_name` (VARCHAR(150)) &mdash; NOT NULL
  - `publisher_type` (VARCHAR(50)) &mdash; NOT NULL
  - `official_domain` (VARCHAR(100)) &mdash; NOT NULL
  - `authority_level` (FLOAT) &mdash; NOT NULL
  - `licensing_status` (VARCHAR(50)) &mdash; NOT NULL
  - `approval_status` (VARCHAR(50)) &mdash; NOT NULL
  - `reviewer_id` (VARCHAR(36)) &mdash; NULL
  - `approved_at` (DATETIME) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### learning_feedback (`LearningFeedback`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\extension_learning.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `resource_id` (VARCHAR(36)) &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `feedback_type` (VARCHAR(50)) &mdash; NOT NULL
  - `comments` (TEXT) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL

### learning_resources (`LearningResource`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\extension_learning.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `title` (VARCHAR(200)) &mdash; NOT NULL
  - `content_body` (TEXT) &mdash; NOT NULL
  - `resource_type` (VARCHAR(50)) &mdash; NOT NULL
  - `creator_org_id` (VARCHAR(36)) &mdash; NULL
  - `creator_user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `crop_id` (VARCHAR(50)) &mdash; NULL
  - `language` (VARCHAR(10)) &mdash; NOT NULL
  - `review_status` (VARCHAR(30)) &mdash; NOT NULL
  - `view_count` (INTEGER) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### location_permissions (`LocationPermission`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\geo_spatial.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `granularity` (VARCHAR(30)) &mdash; NOT NULL
  - `is_active` (BOOLEAN) &mdash; NOT NULL
  - `notes` (VARCHAR(255)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### lot_movements (`LotMovement`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\produce_traceability.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `lot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `movement_type` (VARCHAR(30)) &mdash; NOT NULL
  - `source_location` (VARCHAR(100)) &mdash; NOT NULL
  - `destination_location` (VARCHAR(100)) &mdash; NOT NULL
  - `quantity_transferred` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `unit` (VARCHAR(20)) &mdash; NOT NULL
  - `actor_name` (VARCHAR(100)) &mdash; NOT NULL
  - `movement_timestamp` (DATETIME) &mdash; NOT NULL
  - `notes` (TEXT) &mdash; NULL

### market_commodities (`MarketCommodity`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\market_intelligence.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `commodity_name` (VARCHAR(100)) &mdash; NOT NULL
  - `canonical_crop_id` (VARCHAR(50)) &mdash; NOT NULL
  - `variety_name` (VARCHAR(100)) &mdash; NULL
  - `grade` (VARCHAR(50)) &mdash; NULL

### market_locations (`MarketLocation`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\market_intelligence.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `market_code` (VARCHAR(50)) &mdash; NOT NULL
  - `market_name` (VARCHAR(100)) &mdash; NOT NULL
  - `district` (VARCHAR(100)) &mdash; NOT NULL
  - `state` (VARCHAR(100)) &mdash; NOT NULL
  - `latitude` (NUMERIC(9, 6)) &mdash; NOT NULL
  - `longitude` (NUMERIC(9, 6)) &mdash; NOT NULL
  - `is_active` (BOOLEAN) &mdash; NOT NULL

### market_price_observations (`MarketPriceObservation`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\market_intelligence.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `market_id` (VARCHAR(36)) &mdash; NOT NULL
  - `commodity_id` (VARCHAR(36)) &mdash; NOT NULL
  - `min_price` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `max_price` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `modal_price` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `price_unit` (VARCHAR(30)) &mdash; NOT NULL
  - `arrival_quantity_quintals` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `observation_date` (DATE) &mdash; NOT NULL
  - `source_provider` (VARCHAR(50)) &mdash; NOT NULL
  - `retrieved_at` (DATETIME) &mdash; NOT NULL

### nutrient_assessments (`NutrientAssessment`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\nutrient_intelligence.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `soil_test_result_id` (VARCHAR(36)) &mdash; NOT NULL
  - `crop_id` (VARCHAR(36)) &mdash; NOT NULL
  - `nitrogen_status` (VARCHAR(30)) &mdash; NOT NULL
  - `phosphorus_status` (VARCHAR(30)) &mdash; NOT NULL
  - `potassium_status` (VARCHAR(30)) &mdash; NOT NULL
  - `zinc_status` (VARCHAR(30)) &mdash; NOT NULL
  - `boron_status` (VARCHAR(30)) &mdash; NOT NULL
  - `recommended_n_kg_ha` (FLOAT) &mdash; NOT NULL
  - `recommended_p2o5_kg_ha` (FLOAT) &mdash; NOT NULL
  - `recommended_k2o_kg_ha` (FLOAT) &mdash; NOT NULL
  - `split_application_schedule_json` (TEXT) &mdash; NOT NULL
  - `micronutrient_recommendations_json` (TEXT) &mdash; NOT NULL
  - `safeguard_checks_passed` (BOOLEAN) &mdash; NOT NULL
  - `institutional_citation` (VARCHAR(200)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### nutrient_expert_reviews (`NutrientExpertReview`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\nutrient_intelligence.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `nutrient_assessment_id` (VARCHAR(36)) &mdash; NOT NULL
  - `expert_user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `review_status` (VARCHAR(30)) &mdash; NOT NULL
  - `agronomist_notes` (TEXT) &mdash; NOT NULL
  - `revised_prescription_json` (TEXT) &mdash; NULL
  - `reviewed_at` (DATETIME) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### observation_media (`ObservationMedia`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\observation.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `observation_id` (VARCHAR(36)) &mdash; NOT NULL
  - `storage_path` (VARCHAR(500)) &mdash; NOT NULL
  - `file_size_bytes` (INTEGER) &mdash; NOT NULL
  - `mime_type` (VARCHAR(50)) &mdash; NOT NULL
  - `sha256_hash` (VARCHAR(64)) &mdash; NOT NULL
  - `is_primary` (BOOLEAN) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### observations (`Observation`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\observation.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NULL
  - `crop_season_id` (VARCHAR(36)) &mdash; NULL
  - `observer_id` (VARCHAR(36)) &mdash; NOT NULL
  - `notes` (VARCHAR(1000)) &mdash; NULL
  - `symptom_tags` (VARCHAR(255)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### optimization_problems (`OptimizationProblem`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\optimization.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NULL
  - `problem_type` (VARCHAR(50)) &mdash; NOT NULL
  - `objective_type` (VARCHAR(50)) &mdash; NOT NULL
  - `decision_variables_json` (JSON) &mdash; NOT NULL
  - `hard_constraints_json` (JSON) &mdash; NOT NULL
  - `soft_constraints_json` (JSON) &mdash; NOT NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### optimization_results (`OptimizationResult`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\optimization.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `problem_id` (VARCHAR(36)) &mdash; NOT NULL
  - `feasibility_status` (VARCHAR(30)) &mdash; NOT NULL
  - `selected_solution_json` (JSON) &mdash; NOT NULL
  - `alternative_solutions_json` (JSON) &mdash; NOT NULL
  - `conflicting_constraints_json` (JSON) &mdash; NOT NULL
  - `trade_off_analysis_json` (JSON) &mdash; NOT NULL
  - `solver_name` (VARCHAR(100)) &mdash; NOT NULL
  - `solved_at` (DATETIME) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### organization_memberships (`OrganizationMembership`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\collective.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `organization_id` (VARCHAR(36)) &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `org_role` (VARCHAR(50)) &mdash; NOT NULL
  - `is_active` (BOOLEAN) &mdash; NOT NULL
  - `joined_at` (DATETIME) &mdash; NOT NULL

### outcome_observations (`OutcomeObservation`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\intervention.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `intervention_id` (VARCHAR(36)) &mdash; NOT NULL
  - `follow_up_observation_id` (VARCHAR(36)) &mdash; NOT NULL
  - `evaluation_date` (DATE) &mdash; NOT NULL
  - `observed_status` (VARCHAR(50)) &mdash; NOT NULL
  - `visual_change_notes` (TEXT) &mdash; NOT NULL
  - `confounding_factors` (TEXT) &mdash; NOT NULL
  - `farmer_assessment` (TEXT) &mdash; NULL
  - `days_post_intervention` (INTEGER) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### partner_integrations (`PartnerIntegration`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\interoperability.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `partner_id` (VARCHAR(36)) &mdash; NOT NULL
  - `connector_type` (VARCHAR(50)) &mdash; NOT NULL
  - `display_name` (VARCHAR(150)) &mdash; NOT NULL
  - `capabilities_json` (TEXT) &mdash; NOT NULL
  - `adapter_config_json` (TEXT) &mdash; NOT NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `last_health_check_at` (DATETIME) &mdash; NULL
  - `health_status` (VARCHAR(30)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### plants (`Plant`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\farm.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `tag_code` (VARCHAR(50)) &mdash; NOT NULL
  - `crop_id` (VARCHAR(50)) &mdash; NOT NULL
  - `notes` (VARCHAR(500)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### plot_geometries (`PlotGeometry`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\geo_spatial.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `geometry_type` (VARCHAR(30)) &mdash; NOT NULL
  - `coordinates_geojson` (TEXT) &mdash; NOT NULL
  - `centroid_lat` (FLOAT) &mdash; NOT NULL
  - `centroid_lon` (FLOAT) &mdash; NOT NULL
  - `calculated_area_hectares` (FLOAT) &mdash; NOT NULL
  - `calculated_area_acres` (FLOAT) &mdash; NOT NULL
  - `bbox_min_lon` (FLOAT) &mdash; NOT NULL
  - `bbox_min_lat` (FLOAT) &mdash; NOT NULL
  - `bbox_max_lon` (FLOAT) &mdash; NOT NULL
  - `bbox_max_lat` (FLOAT) &mdash; NOT NULL
  - `properties_json` (JSON) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### plots (`Plot`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\farm.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `name` (VARCHAR(100)) &mdash; NOT NULL
  - `soil_type` (VARCHAR(50)) &mdash; NOT NULL
  - `irrigation_source` (VARCHAR(50)) &mdash; NOT NULL
  - `acreage` (FLOAT) &mdash; NOT NULL
  - `boundary_geojson` (VARCHAR(2000)) &mdash; NULL
  - `is_archived` (BOOLEAN) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### prediction_candidates (`PredictionCandidate`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\diagnosis.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `prediction_id` (VARCHAR(36)) &mdash; NOT NULL
  - `rank` (INTEGER) &mdash; NOT NULL
  - `class_id` (VARCHAR(100)) &mdash; NOT NULL
  - `display_name_en` (VARCHAR(100)) &mdash; NOT NULL
  - `display_name_te` (VARCHAR(100)) &mdash; NOT NULL
  - `display_name_hi` (VARCHAR(100)) &mdash; NOT NULL
  - `pathogen_or_cause` (VARCHAR(150)) &mdash; NULL
  - `calibrated_prob` (FLOAT) &mdash; NOT NULL

### predictions (`Prediction`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\diagnosis.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `diagnosis_request_id` (VARCHAR(36)) &mdash; NOT NULL
  - `model_version` (VARCHAR(100)) &mdash; NOT NULL
  - `decision_state` (VARCHAR(50)) &mdash; NOT NULL
  - `top_confidence` (FLOAT) &mdash; NOT NULL
  - `normalized_entropy` (FLOAT) &mdash; NULL
  - `prediction_margin` (FLOAT) &mdash; NULL
  - `cibrc_advisory` (VARCHAR(1000)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### produce_lots (`ProduceLot`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\produce_traceability.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `lot_code` (VARCHAR(60)) &mdash; NOT NULL
  - `qr_token` (VARCHAR(100)) &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `crop_season_id` (VARCHAR(36)) &mdash; NOT NULL
  - `harvest_session_id` (VARCHAR(36)) &mdash; NULL
  - `crop_id` (VARCHAR(50)) &mdash; NOT NULL
  - `variety_name` (VARCHAR(100)) &mdash; NULL
  - `harvest_date` (DATE) &mdash; NOT NULL
  - `initial_quantity` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `remaining_quantity` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `unit` (VARCHAR(20)) &mdash; NOT NULL
  - `current_status` (VARCHAR(30)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### produce_quality_profiles (`ProduceQualityProfile`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\post_harvest.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `crop_id` (VARCHAR(50)) &mdash; NOT NULL
  - `standard_name` (VARCHAR(100)) &mdash; NOT NULL
  - `grade_definitions_json` (TEXT) &mdash; NOT NULL

### quality_measurements (`QualityMeasurement`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\post_harvest.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `session_id` (VARCHAR(36)) &mdash; NULL
  - `lot_id` (VARCHAR(36)) &mdash; NULL
  - `parameter_name` (VARCHAR(50)) &mdash; NOT NULL
  - `measured_value` (NUMERIC(8, 2)) &mdash; NOT NULL
  - `unit` (VARCHAR(20)) &mdash; NOT NULL
  - `measurement_method` (VARCHAR(50)) &mdash; NOT NULL
  - `instrument_details` (VARCHAR(100)) &mdash; NULL
  - `measured_at` (DATETIME) &mdash; NOT NULL

### regional_signal_evidences (`RegionalSignalEvidence`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\regional_pulse.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `signal_id` (VARCHAR(36)) &mdash; NOT NULL
  - `evidence_type` (VARCHAR(50)) &mdash; NOT NULL
  - `evidence_reference_id` (VARCHAR(100)) &mdash; NOT NULL
  - `evidence_notes` (TEXT) &mdash; NULL
  - `added_at` (DATETIME) &mdash; NOT NULL

### regional_signals (`RegionalSignal`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\regional_pulse.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `district` (VARCHAR(100)) &mdash; NOT NULL
  - `state` (VARCHAR(100)) &mdash; NOT NULL
  - `crop_id` (VARCHAR(50)) &mdash; NOT NULL
  - `signal_category` (VARCHAR(50)) &mdash; NOT NULL
  - `signal_title` (VARCHAR(200)) &mdash; NOT NULL
  - `signal_summary` (TEXT) &mdash; NOT NULL
  - `confidence_tier` (VARCHAR(50)) &mdash; NOT NULL
  - `source_observation_count` (INTEGER) &mdash; NOT NULL
  - `distinct_farms_count` (INTEGER) &mdash; NOT NULL
  - `is_outbreak_claim_suppressed` (BOOLEAN) &mdash; NOT NULL
  - `validation_status` (VARCHAR(50)) &mdash; NOT NULL
  - `recommended_action` (TEXT) &mdash; NOT NULL
  - `observed_start_date` (DATE) &mdash; NOT NULL
  - `observed_end_date` (DATE) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### research_consents (`ResearchConsent`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\research_hub.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `project_id` (VARCHAR(36)) &mdash; NOT NULL
  - `farmer_id` (VARCHAR(36)) &mdash; NOT NULL
  - `consent_scope` (VARCHAR(50)) &mdash; NOT NULL
  - `is_active` (BOOLEAN) &mdash; NOT NULL
  - `consent_version` (VARCHAR(20)) &mdash; NOT NULL
  - `granted_at` (DATETIME) &mdash; NOT NULL
  - `revoked_at` (DATETIME) &mdash; NULL

### research_projects (`ResearchProject`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\research_hub.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `title` (VARCHAR(200)) &mdash; NOT NULL
  - `lead_researcher_id` (VARCHAR(36)) &mdash; NOT NULL
  - `institution_name` (VARCHAR(150)) &mdash; NOT NULL
  - `research_objectives` (TEXT) &mdash; NOT NULL
  - `supported_crops_json` (TEXT) &mdash; NOT NULL
  - `geographic_scope` (VARCHAR(100)) &mdash; NOT NULL
  - `project_status` (VARCHAR(30)) &mdash; NOT NULL
  - `publication_references_json` (TEXT) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### resilience_assessments (`ResilienceAssessment`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\resilience_assessment.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `overall_resilience_score` (FLOAT) &mdash; NOT NULL
  - `soil_score` (FLOAT) &mdash; NOT NULL
  - `water_score` (FLOAT) &mdash; NOT NULL
  - `climate_score` (FLOAT) &mdash; NOT NULL
  - `nutrient_score` (FLOAT) &mdash; NOT NULL
  - `practice_score` (FLOAT) &mdash; NOT NULL
  - `evidence_quality_score` (FLOAT) &mdash; NOT NULL
  - `confidence_category` (VARCHAR(50)) &mdash; NOT NULL
  - `top_vulnerabilities_json` (TEXT) &mdash; NOT NULL
  - `adaptation_recommendations_json` (TEXT) &mdash; NOT NULL
  - `evaluated_at` (DATETIME) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### resilience_scenario_simulations (`ResilienceScenarioSimulation`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\resilience_assessment.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `assessment_id` (VARCHAR(36)) &mdash; NOT NULL
  - `package_name` (VARCHAR(100)) &mdash; NOT NULL
  - `simulated_overall_score` (FLOAT) &mdash; NOT NULL
  - `projected_water_saving_percent` (FLOAT) &mdash; NOT NULL
  - `cost_delta_inr` (FLOAT) &mdash; NOT NULL
  - `yield_risk_reduction_percent` (FLOAT) &mdash; NOT NULL
  - `simulated_at` (DATETIME) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### risk_alerts (`RiskAlert`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\risk_alert.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `risk_assessment_id` (VARCHAR(36)) &mdash; NOT NULL
  - `alert_level` (VARCHAR(20)) &mdash; NOT NULL
  - `title` (VARCHAR(150)) &mdash; NOT NULL
  - `message_en` (TEXT) &mdash; NOT NULL
  - `message_te` (TEXT) &mdash; NOT NULL
  - `message_hi` (TEXT) &mdash; NOT NULL
  - `recommended_actions_json` (TEXT) &mdash; NOT NULL
  - `is_acknowledged` (BOOLEAN) &mdash; NOT NULL
  - `acknowledged_at` (DATETIME) &mdash; NULL
  - `is_dismissed` (BOOLEAN) &mdash; NOT NULL
  - `dismissed_at` (DATETIME) &mdash; NULL
  - `deduplication_key` (VARCHAR(128)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL

### risk_assessment_records (`RiskAssessmentRecord`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\risk_assessment.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `crop_season_id` (VARCHAR(36)) &mdash; NULL
  - `evaluation_timestamp` (DATETIME) &mdash; NOT NULL
  - `overall_risk_level` (VARCHAR(20)) &mdash; NOT NULL
  - `weather_data_id` (VARCHAR(36)) &mdash; NULL
  - `rules_triggered_json` (TEXT) &mdash; NOT NULL
  - `advisory_en` (TEXT) &mdash; NOT NULL
  - `advisory_te` (TEXT) &mdash; NOT NULL
  - `advisory_hi` (TEXT) &mdash; NOT NULL
  - `limitations_notice` (TEXT) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### risk_assessments (`RiskAssessment`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\operation.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `crop_season_id` (VARCHAR(36)) &mdash; NULL
  - `assessment_date` (DATE) &mdash; NOT NULL
  - `pest_risk_level` (VARCHAR(20)) &mdash; NOT NULL
  - `weather_risk_level` (VARCHAR(20)) &mdash; NOT NULL
  - `advisory` (VARCHAR(1000)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### risk_rules (`RiskRule`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\risk_rule.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `rule_code` (VARCHAR(50)) &mdash; NOT NULL
  - `crop` (VARCHAR(50)) &mdash; NOT NULL
  - `target_threat` (VARCHAR(100)) &mdash; NOT NULL
  - `applicable_growth_stages` (VARCHAR(255)) &mdash; NOT NULL
  - `min_temp` (FLOAT) &mdash; NULL
  - `max_temp` (FLOAT) &mdash; NULL
  - `min_humidity` (FLOAT) &mdash; NULL
  - `min_leaf_wetness_hours` (FLOAT) &mdash; NULL
  - `min_consecutive_wet_days` (INTEGER) &mdash; NULL
  - `severity_level` (VARCHAR(20)) &mdash; NOT NULL
  - `advisory_en` (TEXT) &mdash; NOT NULL
  - `advisory_te` (TEXT) &mdash; NOT NULL
  - `advisory_hi` (TEXT) &mdash; NOT NULL
  - `evidence_citations_json` (TEXT) &mdash; NOT NULL
  - `version` (VARCHAR(20)) &mdash; NOT NULL
  - `is_active` (BOOLEAN) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### roles (`Role`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\user.py`
  - `id` (VARCHAR(50)) [PK] &mdash; NOT NULL
  - `description` (VARCHAR(255)) &mdash; NULL

### sale_transactions (`SaleTransaction`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\financial_ledger.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `crop_season_id` (VARCHAR(36)) &mdash; NOT NULL
  - `lot_id` (VARCHAR(36)) &mdash; NULL
  - `buyer_name` (VARCHAR(100)) &mdash; NOT NULL
  - `buyer_type` (VARCHAR(50)) &mdash; NOT NULL
  - `quantity_sold` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `unit` (VARCHAR(20)) &mdash; NOT NULL
  - `price_per_unit` (NUMERIC(12, 2)) &mdash; NOT NULL
  - `gross_amount` (NUMERIC(12, 2)) &mdash; NOT NULL
  - `deductions_amount` (NUMERIC(12, 2)) &mdash; NOT NULL
  - `net_amount` (NUMERIC(12, 2)) &mdash; NOT NULL
  - `sale_date` (DATE) &mdash; NOT NULL
  - `payment_status` (VARCHAR(20)) &mdash; NOT NULL
  - `notes` (TEXT) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### satellite_acquisitions (`SatelliteAcquisition`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\satellite.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `source_id` (VARCHAR(36)) &mdash; NOT NULL
  - `scene_id` (VARCHAR(100)) &mdash; NOT NULL
  - `acquisition_date` (DATETIME) &mdash; NOT NULL
  - `cloud_coverage_percentage` (FLOAT) &mdash; NOT NULL
  - `raw_metadata_json` (JSON) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### satellite_observations (`SatelliteObservation`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\satellite.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `acquisition_id` (VARCHAR(36)) &mdash; NOT NULL
  - `observation_date` (DATETIME) &mdash; NOT NULL
  - `mean_ndvi` (FLOAT) &mdash; NOT NULL
  - `min_ndvi` (FLOAT) &mdash; NOT NULL
  - `max_ndvi` (FLOAT) &mdash; NOT NULL
  - `std_ndvi` (FLOAT) &mdash; NOT NULL
  - `mean_evi` (FLOAT) &mdash; NOT NULL
  - `mean_ndmi` (FLOAT) &mdash; NOT NULL
  - `cloud_masked_pixel_ratio` (FLOAT) &mdash; NOT NULL
  - `trend_classification` (VARCHAR(50)) &mdash; NOT NULL
  - `evidence_disclaimer` (TEXT) &mdash; NOT NULL
  - `properties_json` (JSON) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### satellite_sources (`SatelliteSource`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\satellite.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `name` (VARCHAR(50)) &mdash; NOT NULL
  - `constellation` (VARCHAR(100)) &mdash; NOT NULL
  - `spatial_resolution_meters` (FLOAT) &mdash; NOT NULL
  - `description` (VARCHAR(255)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### sensor_calibrations (`SensorCalibration`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\sensor.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `device_id` (VARCHAR(36)) &mdash; NOT NULL
  - `calibrated_at` (DATETIME) &mdash; NOT NULL
  - `valid_until` (DATETIME) &mdash; NOT NULL
  - `calibrated_by` (VARCHAR(100)) &mdash; NOT NULL
  - `calibration_coefficients_json` (JSON) &mdash; NULL
  - `is_valid` (BOOLEAN) &mdash; NOT NULL
  - `notes` (VARCHAR(255)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### sensor_devices (`SensorDevice`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\sensor.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NULL
  - `device_serial_number` (VARCHAR(100)) &mdash; NOT NULL
  - `device_category` (VARCHAR(50)) &mdash; NOT NULL
  - `auth_token_hash` (VARCHAR(128)) &mdash; NOT NULL
  - `firmware_version` (VARCHAR(50)) &mdash; NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `last_heartbeat_at` (DATETIME) &mdash; NULL
  - `properties_json` (JSON) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### sensor_measurements (`SensorMeasurement`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\sensor.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `device_id` (VARCHAR(36)) &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `timestamp` (DATETIME) &mdash; NOT NULL
  - `soil_moisture_pct` (FLOAT) &mdash; NULL
  - `soil_temperature_c` (FLOAT) &mdash; NULL
  - `ambient_temperature_c` (FLOAT) &mdash; NULL
  - `relative_humidity_pct` (FLOAT) &mdash; NULL
  - `leaf_wetness_pct` (FLOAT) &mdash; NULL
  - `solar_radiation_w_m2` (FLOAT) &mdash; NULL
  - `battery_pct` (FLOAT) &mdash; NULL
  - `signal_rssi` (INTEGER) &mdash; NULL
  - `data_quality_flag` (VARCHAR(50)) &mdash; NOT NULL
  - `quality_notes` (VARCHAR(255)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### session_tokens (`SessionToken`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\user.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `refresh_token_hash` (VARCHAR(255)) &mdash; NOT NULL
  - `expires_at` (DATETIME) &mdash; NOT NULL
  - `revoked` (BOOLEAN) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL

### simulation_results (`SimulationResult`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\simulation.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `scenario_id` (VARCHAR(36)) &mdash; NOT NULL
  - `model_name` (VARCHAR(100)) &mdash; NOT NULL
  - `model_version` (VARCHAR(50)) &mdash; NOT NULL
  - `outputs_json` (JSON) &mdash; NOT NULL
  - `uncertainty_metadata_json` (JSON) &mdash; NOT NULL
  - `evidence_sources_json` (JSON) &mdash; NOT NULL
  - `execution_duration_ms` (FLOAT) &mdash; NOT NULL
  - `completed_at` (DATETIME) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### simulation_scenarios (`SimulationScenario`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\simulation.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `crop_season_id` (VARCHAR(36)) &mdash; NULL
  - `creator_id` (VARCHAR(36)) &mdash; NOT NULL
  - `scenario_type` (VARCHAR(50)) &mdash; NOT NULL
  - `scenario_name` (VARCHAR(150)) &mdash; NOT NULL
  - `baseline_snapshot_id` (VARCHAR(36)) &mdash; NULL
  - `input_parameters_json` (JSON) &mdash; NOT NULL
  - `farmer_assumptions_json` (JSON) &mdash; NOT NULL
  - `constraints_json` (JSON) &mdash; NOT NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### soil_carbon_measurements (`SoilCarbonMeasurement`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\sustainability.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `sample_date` (DATETIME) &mdash; NOT NULL
  - `depth_cm` (FLOAT) &mdash; NOT NULL
  - `soc_percent` (FLOAT) &mdash; NOT NULL
  - `bulk_density` (FLOAT) &mdash; NULL
  - `method` (VARCHAR(50)) &mdash; NOT NULL
  - `lab_accreditation` (VARCHAR(100)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### soil_moisture_observations (`SoilMoistureObservation`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\water_management.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `sensor_id` (VARCHAR(64)) &mdash; NOT NULL
  - `depth_cm` (INTEGER) &mdash; NOT NULL
  - `volumetric_water_content` (FLOAT) &mdash; NOT NULL
  - `matric_potential_kpa` (FLOAT) &mdash; NULL
  - `moisture_status` (VARCHAR(50)) &mdash; NOT NULL
  - `observed_at` (DATETIME) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### soil_profiles (`SoilProfile`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\soil_health.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `soil_order` (VARCHAR(50)) &mdash; NOT NULL
  - `soil_series_name` (VARCHAR(100)) &mdash; NULL
  - `drainage_class` (VARCHAR(50)) &mdash; NOT NULL
  - `bulk_density_g_cm3` (FLOAT) &mdash; NULL
  - `effective_soil_depth_cm` (FLOAT) &mdash; NULL
  - `texture_class` (VARCHAR(50)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### soil_samples (`SoilSample`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\soil_health.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `profile_id` (VARCHAR(36)) &mdash; NULL
  - `sampled_by_user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `sample_code` (VARCHAR(64)) &mdash; NOT NULL
  - `sampling_date` (DATETIME) &mdash; NOT NULL
  - `sampling_depth_min_cm` (FLOAT) &mdash; NOT NULL
  - `sampling_depth_max_cm` (FLOAT) &mdash; NOT NULL
  - `gps_latitude` (FLOAT) &mdash; NULL
  - `gps_longitude` (FLOAT) &mdash; NULL
  - `composite_cores_count` (INTEGER) &mdash; NOT NULL
  - `spatial_coverage_warning` (VARCHAR(100)) &mdash; NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### soil_test_results (`SoilTestResult`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\soil_health.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `soil_sample_id` (VARCHAR(36)) &mdash; NOT NULL
  - `laboratory_name` (VARCHAR(150)) &mdash; NOT NULL
  - `accreditation_number` (VARCHAR(100)) &mdash; NOT NULL
  - `ph` (FLOAT) &mdash; NOT NULL
  - `electrical_conductivity_ec` (FLOAT) &mdash; NOT NULL
  - `organic_carbon_percent` (FLOAT) &mdash; NOT NULL
  - `available_nitrogen_kg_ha` (FLOAT) &mdash; NOT NULL
  - `available_phosphorus_kg_ha` (FLOAT) &mdash; NOT NULL
  - `available_potassium_kg_ha` (FLOAT) &mdash; NOT NULL
  - `available_sulphur_ppm` (FLOAT) &mdash; NULL
  - `available_zinc_ppm` (FLOAT) &mdash; NULL
  - `available_iron_ppm` (FLOAT) &mdash; NULL
  - `available_boron_ppm` (FLOAT) &mdash; NULL
  - `provenance_json` (TEXT) &mdash; NOT NULL
  - `verified_at` (DATETIME) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### storage_locations (`StorageLocation`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\post_harvest.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `name` (VARCHAR(100)) &mdash; NOT NULL
  - `storage_type` (VARCHAR(50)) &mdash; NOT NULL
  - `capacity_quintals` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `district` (VARCHAR(100)) &mdash; NOT NULL
  - `is_temperature_controlled` (BOOLEAN) &mdash; NOT NULL

### storage_lots (`StorageLot`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\post_harvest.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `lot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `storage_location_id` (VARCHAR(36)) &mdash; NOT NULL
  - `quantity_stored` (NUMERIC(10, 2)) &mdash; NOT NULL
  - `unit` (VARCHAR(20)) &mdash; NOT NULL
  - `entry_date` (DATE) &mdash; NOT NULL
  - `exit_date` (DATE) &mdash; NULL
  - `current_status` (VARCHAR(30)) &mdash; NOT NULL

### training_events (`TrainingEvent`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\extension_learning.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `organizer_org_id` (VARCHAR(36)) &mdash; NULL
  - `title` (VARCHAR(200)) &mdash; NOT NULL
  - `description` (TEXT) &mdash; NOT NULL
  - `event_type` (VARCHAR(50)) &mdash; NOT NULL
  - `target_crop_id` (VARCHAR(50)) &mdash; NULL
  - `district` (VARCHAR(100)) &mdash; NOT NULL
  - `scheduled_start` (DATETIME) &mdash; NOT NULL
  - `scheduled_end` (DATETIME) &mdash; NOT NULL
  - `is_online` (BOOLEAN) &mdash; NOT NULL
  - `meeting_link` (VARCHAR(500)) &mdash; NULL
  - `max_capacity` (INTEGER) &mdash; NOT NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### translation_versions (`TranslationVersion`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\commons_contribution.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `contribution_id` (VARCHAR(36)) &mdash; NOT NULL
  - `target_language` (VARCHAR(10)) &mdash; NOT NULL
  - `translated_title` (VARCHAR(200)) &mdash; NOT NULL
  - `translated_content` (TEXT) &mdash; NOT NULL
  - `is_native_reviewed` (BOOLEAN) &mdash; NOT NULL
  - `reviewer_id` (VARCHAR(36)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL

### twin_snapshots (`TwinSnapshot`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\digital_twin.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `twin_id` (VARCHAR(36)) &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NULL
  - `crop_season_id` (VARCHAR(36)) &mdash; NULL
  - `snapshot_version` (INTEGER) &mdash; NOT NULL
  - `state_payload_json` (JSON) &mdash; NOT NULL
  - `source_manifest_json` (JSON) &mdash; NOT NULL
  - `data_completeness_pct` (FLOAT) &mdash; NOT NULL
  - `payload_hash` (VARCHAR(64)) &mdash; NOT NULL
  - `generated_at` (DATETIME) &mdash; NOT NULL
  - `created_by` (VARCHAR(36)) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### twin_state_records (`TwinStateRecord`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\digital_twin.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `snapshot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `entity_type` (VARCHAR(50)) &mdash; NOT NULL
  - `entity_id` (VARCHAR(36)) &mdash; NOT NULL
  - `property_name` (VARCHAR(100)) &mdash; NOT NULL
  - `property_value_json` (JSON) &mdash; NOT NULL
  - `unit` (VARCHAR(30)) &mdash; NULL
  - `provenance_type` (VARCHAR(50)) &mdash; NOT NULL
  - `source_reference` (VARCHAR(255)) &mdash; NULL
  - `observed_at` (DATETIME) &mdash; NOT NULL
  - `quality_status` (VARCHAR(30)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### twin_synchronization_events (`TwinSynchronizationEvent`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\digital_twin.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `twin_id` (VARCHAR(36)) &mdash; NOT NULL
  - `event_type` (VARCHAR(100)) &mdash; NOT NULL
  - `event_hash` (VARCHAR(64)) &mdash; NOT NULL
  - `payload_json` (JSON) &mdash; NOT NULL
  - `processed_at` (DATETIME) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### user_roles (`UserRole`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\user.py`
  - `user_id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `role_id` (VARCHAR(50)) [PK] &mdash; NOT NULL

### users (`User`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\user.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `phone` (VARCHAR(20)) &mdash; NOT NULL
  - `email` (VARCHAR(255)) &mdash; NULL
  - `hashed_password` (VARCHAR(255)) &mdash; NOT NULL
  - `full_name` (VARCHAR(100)) &mdash; NOT NULL
  - `language_preference` (VARCHAR(10)) &mdash; NOT NULL
  - `is_active` (BOOLEAN) &mdash; NOT NULL
  - `is_verified` (BOOLEAN) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### water_balance_snapshots (`WaterBalanceSnapshot`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\water_management.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `snapshot_date` (DATETIME) &mdash; NOT NULL
  - `effective_precipitation_mm` (FLOAT) &mdash; NOT NULL
  - `irrigation_applied_mm` (FLOAT) &mdash; NOT NULL
  - `crop_evapotranspiration_mm` (FLOAT) &mdash; NOT NULL
  - `deep_percolation_mm` (FLOAT) &mdash; NOT NULL
  - `runoff_mm` (FLOAT) &mdash; NOT NULL
  - `storage_change_mm` (FLOAT) &mdash; NOT NULL
  - `accounting_status` (VARCHAR(50)) &mdash; NOT NULL
  - `management_allowed_depletion_percent` (FLOAT) &mdash; NOT NULL
  - `current_depletion_percent` (FLOAT) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### water_sources (`WaterSource`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\water_management.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `source_type` (VARCHAR(50)) &mdash; NOT NULL
  - `source_name` (VARCHAR(100)) &mdash; NOT NULL
  - `depth_meters` (FLOAT) &mdash; NULL
  - `static_water_level_m` (FLOAT) &mdash; NULL
  - `discharge_capacity_lps` (FLOAT) &mdash; NULL
  - `salinity_ec_dsm` (FLOAT) &mdash; NULL
  - `ph` (FLOAT) &mdash; NULL
  - `sar` (FLOAT) &mdash; NULL
  - `seasonal_availability_json` (TEXT) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### weather_data (`WeatherData`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\weather_data.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `district` (VARCHAR(50)) &mdash; NOT NULL
  - `is_forecast` (BOOLEAN) &mdash; NOT NULL
  - `observation_time` (DATETIME) &mdash; NOT NULL
  - `forecast_target_time` (DATETIME) &mdash; NULL
  - `temperature_celsius` (FLOAT) &mdash; NOT NULL
  - `relative_humidity` (FLOAT) &mdash; NOT NULL
  - `precipitation_mm` (FLOAT) &mdash; NOT NULL
  - `wind_speed_kmh` (FLOAT) &mdash; NOT NULL
  - `leaf_wetness_hours` (FLOAT) &mdash; NOT NULL
  - `source_provider` (VARCHAR(50)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL

### weather_observations (`WeatherObservation`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\operation.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `farm_id` (VARCHAR(36)) &mdash; NOT NULL
  - `timestamp` (DATETIME) &mdash; NOT NULL
  - `temperature` (FLOAT) &mdash; NOT NULL
  - `humidity` (FLOAT) &mdash; NOT NULL
  - `precipitation` (FLOAT) &mdash; NOT NULL
  - `wind_speed` (FLOAT) &mdash; NOT NULL
  - `source` (VARCHAR(50)) &mdash; NOT NULL

### webhook_deliveries (`WebhookDelivery`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\interoperability.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `endpoint_id` (VARCHAR(36)) &mdash; NOT NULL
  - `event_id` (VARCHAR(36)) &mdash; NOT NULL
  - `attempt_number` (INTEGER) &mdash; NOT NULL
  - `response_status_code` (INTEGER) &mdash; NULL
  - `response_body_snippet` (VARCHAR(500)) &mdash; NULL
  - `duration_ms` (INTEGER) &mdash; NOT NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `delivered_at` (DATETIME) &mdash; NOT NULL

### webhook_endpoints (`WebhookEndpoint`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\interoperability.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `user_id` (VARCHAR(36)) &mdash; NOT NULL
  - `partner_id` (VARCHAR(36)) &mdash; NULL
  - `url` (VARCHAR(500)) &mdash; NOT NULL
  - `secret_hash` (VARCHAR(128)) &mdash; NOT NULL
  - `event_types_json` (TEXT) &mdash; NOT NULL
  - `is_active` (BOOLEAN) &mdash; NOT NULL
  - `failure_count` (INTEGER) &mdash; NOT NULL
  - `last_delivery_at` (DATETIME) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL

### webhook_events (`WebhookEvent`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\interoperability.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `event_type` (VARCHAR(100)) &mdash; NOT NULL
  - `event_version` (VARCHAR(20)) &mdash; NOT NULL
  - `tenant_id` (VARCHAR(36)) &mdash; NOT NULL
  - `entity_type` (VARCHAR(50)) &mdash; NOT NULL
  - `entity_id` (VARCHAR(36)) &mdash; NOT NULL
  - `payload_json` (TEXT) &mdash; NOT NULL
  - `status` (VARCHAR(30)) &mdash; NOT NULL
  - `created_at` (DATETIME) &mdash; NOT NULL

### yield_forecast_records (`YieldForecastRecord`)
- **Source File:** `C:\Users\gokul\OneDrive\Documents\projects\backend\app\models\yield_research.py`
  - `id` (VARCHAR(36)) [PK] &mdash; NOT NULL
  - `plot_id` (VARCHAR(36)) &mdash; NOT NULL
  - `season_id` (VARCHAR(36)) &mdash; NOT NULL
  - `model_version` (VARCHAR(50)) &mdash; NOT NULL
  - `status` (VARCHAR(50)) &mdash; NOT NULL
  - `predicted_yield_min` (FLOAT) &mdash; NULL
  - `predicted_yield_max` (FLOAT) &mdash; NULL
  - `confidence_score` (FLOAT) &mdash; NULL
  - `withholding_reason` (TEXT) &mdash; NULL
  - `features_snapshot_json` (JSON) &mdash; NULL
  - `created_at` (DATETIME) &mdash; NOT NULL
  - `updated_at` (DATETIME) &mdash; NOT NULL
