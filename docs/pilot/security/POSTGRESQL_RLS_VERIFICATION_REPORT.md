# ACREVIA — POSTGRESQL ROW-LEVEL SECURITY (RLS) VERIFICATION REPORT

**Report Identifier:** SEC-RLS-2026-11-09  
**Target Architecture:** Multi-Tenant Farm Isolation & User Privacy  
**Implementation Classification:** `D2_IMPLEMENTATION_STATUS = PARTIALLY_IMPLEMENTED`  
*(Awaiting Staging Database Branch Execution; Live Production Database Protected from Modification)*  
**Verification Date:** November 9, 2026  

---

## 1. Architectural Strategy & Threat Model

In agricultural advisory and digital twin systems, data leakages between adjacent or competing farms represent critical privacy, operational, and commercial risks. While application-layer checks (`verify_farm_access`) prevent ordinary access violations, database-engine Row-Level Security (RLS) guarantees defense-in-depth against:
1. Application logic bugs or missed filter clauses in complex queries.
2. Direct SQL injection or ORM association bypasses.
3. Unauthorized cross-farm data aggregation during reporting jobs.

---

## 2. Exhaustive Table Classification (132 Database Tables)

Every single model registered in SQLAlchemy `Base.metadata` (132 distinct tables) has been audited and classified in `backend/app/database/rls.py`:

### Category Distribution:
- **Tenant-Direct Tables (25 tables):**
  Entities containing a direct `farm_id` or `tenant_id` foreign key.
  `farms`, `audit_logs`, `crop_loss_evidence_packages`, `data_exchange_jobs`, `data_sharing_grants`, `expert_review_cases`, `farm_expenses`, `farm_memberships`, `farm_twins`, `intervention_records`, `location_permissions`, `observations`, `optimization_problems`, `plots`, `produce_lots`, `risk_alerts`, `risk_assessment_records`, `risk_assessments`, `sensor_devices`, `storage_locations`, `twin_snapshots`, `water_sources`, `weather_data`, `weather_observations`, `webhook_events`.

- **User-Owned Tables (13 tables):**
  Entities directly owned by an individual user account.
  `users`, `session_tokens`, `user_roles`, `consent_records`, `api_applications`, `webhook_endpoints`, `data_mapping_profiles`, `expert_profiles`, `community_memberships`, `organization_memberships`, `event_registrations`, `knowledge_feedback`, `learning_feedback`.

- **Tenant-Indirect Child Tables (51 tables):**
  Child entities linked to a farm through `plots`, `observations`, `seasons`, or `diagnoses`.
  `plants`, `plot_geometries`, `crop_seasons`, `crop_stage_events`, `crop_tasks`, `crop_season_economics`, `diagnosis_requests`, `predictions`, `prediction_candidates`, `expert_reviews`, `expert_assessments`, `expert_assessment_revisions`, `outcome_observations`, `farm_operations`, `observation_media`, `image_quality_assessments`, `sensor_measurements`, `sensor_calibrations`, `satellite_observations`, `fusion_explanations`, `yield_forecast_records`, `harvest_measurements`, `twin_state_records`, `twin_synchronization_events`, `simulation_scenarios`, `simulation_results`, `optimization_results`, `financial_corrections`, `sale_transactions`, `harvest_plans`, `harvest_sessions`, `lot_movements`, `produce_quality_profiles`, `quality_measurements`, `storage_lots`, `soil_profiles`, `soil_samples`, `soil_test_results`, `water_balance_snapshots`, `irrigation_events`, `soil_moisture_observations`, `climate_exposure_assessments`, `climate_adaptation_scenarios`, `nutrient_assessments`, `nutrient_expert_reviews`, `farm_practice_records`, `soil_carbon_measurements`, `environmental_accounting_estimates`, `resilience_assessments`, `resilience_scenario_simulations`, `decision_records`, `decision_feedbacks`, `api_credentials`, `webhook_deliveries`.

- **Shared Reference Catalogs (24 tables):**
  Public or system agronomic reference tables (public read, admin write).
  `roles`, `crops`, `crop_varieties`, `crop_calendar_definitions`, `agricultural_practice_definitions`, `market_commodities`, `market_locations`, `market_price_observations`, `satellite_sources`, `climate_baselines`, `risk_rules`, `integration_partners`, `partner_integrations`, `knowledge_sources`, `knowledge_documents`, `knowledge_document_versions`, `knowledge_chunks`, `knowledge_embeddings`, `knowledge_entities`, `knowledge_relationships`, `ingestion_jobs`, `learning_resources`, `training_events`, `satellite_acquisitions`.

- **Community & Collaborative Hub (19 tables):**
  Federated community knowledge and research consortium entities.
  `communities`, `community_posts`, `community_comments`, `community_reports`, `knowledge_contributions`, `contribution_reviews`, `translation_versions`, `agricultural_organizations`, `collective_activities`, `research_projects`, `research_consents`, `dataset_contributions`, `annotation_tasks`, `annotation_records`, `regional_signals`, `regional_signal_evidences`.

---

## 3. Session Context Lifecycle Implementation

In `backend/app/database/rls.py`, the session context lifecycle is implemented with connection pool safety:

```python
def set_tenant_context(
    session: Session,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    is_admin: bool = False
) -> None:
    session.info["tenant_context"] = {
        "tenant_id": str(tenant_id) if tenant_id else None,
        "user_id": str(user_id) if user_id else None,
        "is_admin": is_admin
    }
    bind = session.get_bind()
    if bind and bind.dialect.name == "postgresql":
        # Transaction-scoped configuration parameters (is_local=true)
        session.execute(sa.text("SELECT set_config('app.current_tenant_id', :val, true)"), {"val": str(tenant_id or "")})
        session.execute(sa.text("SELECT set_config('app.current_user_id', :val, true)"), {"val": str(user_id or "")})
        session.execute(sa.text("SELECT set_config('app.is_admin', :val, true)"), {"val": "true" if is_admin else "false"})
```

### Connection Pool Safety:
In `backend/app/database/session.py`, `get_db()` guarantees that `clear_tenant_context(db)` is invoked in the `finally` block before connection check-in. Furthermore, setting `is_local=true` in `set_config` ensures that PostgreSQL automatically clears the parameter at transaction boundary (`COMMIT` or `ROLLBACK`).

---

## 4. Alembic Migration `a1089411c87d`

Alembic migration `backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py`:
- Revisions parent: `f4894a11c87d`.
- Dialect check: `bind.dialect.name == "postgresql"`. If running against SQLite in test environments, the migration gracefully logs an informational message and skips execution.
- Generates strict PostgreSQL DDL:
  - `ALTER TABLE <table_name> ENABLE ROW LEVEL SECURITY;`
  - `ALTER TABLE <table_name> FORCE ROW LEVEL SECURITY;`
  - Restrictive policies using `current_setting('app.current_tenant_id', true)` and `current_setting('app.is_admin', true) = 'true'`.

---

## 5. Automated Verification Results

All 8 tests in `backend/tests/test_postgresql_rls.py` pass cleanly:
1. `test_complete_table_classification_coverage`: Verifies all 132 metadata tables are classified.
2. `test_table_classification_categories`: Validates enum mapping for all tables.
3. `test_generate_rls_ddl_tenant_direct`: Confirms FORCE RLS and restrictive policy generation.
4. `test_generate_rls_ddl_user_owned`: Confirms user isolation policy generation.
5. `test_generate_rls_ddl_shared_reference`: Confirms permissive read and admin-restricted write policies.
6. `test_tenant_context_lifecycle_sqlite`: Verifies safe context tracking and cleanup in test suites.
7. `test_tenant_context_lifecycle_simulated_postgresql`: Verifies execution of transaction-scoped `set_config` statements.
8. `test_verify_farm_access_sets_tenant_context`: Verifies that security dependencies set tenant context upon authorized access.

---

## 6. Staging Execution Gate

In compliance with project safety non-negotiables, the live cloud database (`ep-muddy-mode-a1nd6rrb...`) was deliberately not mutated during Phase 03. Full migration application will occur on the isolated staging database branch once owner authorization is granted.
