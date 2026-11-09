# ACREVIA — POSTGRESQL RLS DATABASE EXECUTION & POLICY AUDIT REPORT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Architecture:** Multi-Tenant Isolation & Hierarchical Access  
**Audited Migration:** `a1089411c87d_enable_postgresql_rls_tenant_isolation.py`  
**Execution Date:** November 9, 2026  
**Status:** `PARTIALLY_IMPLEMENTED` (Code and Migration Complete; Awaiting Remote Staging Branch Execution)

---

## 1. Exhaustive Entity Classification Reconciliation (132 Tables)

All 132 models in `Base.metadata` have been cataloged into 5 architectural isolation categories:

| Category | Count | Primary Ownership Link | Key Representative Tables |
| :--- | :---: | :--- | :--- |
| **`TENANT_DIRECT`** | 25 | `farm_id` / `tenant_id` | `farms`, `plots`, `crop_loss_evidence_packages`, `farm_expenses`, `observations`, `risk_alerts`, `sensor_devices`, `storage_locations`, `twin_snapshots`, `water_sources` |
| **`USER_OWNED`** | 13 | `user_id` / `owner_id` | `users`, `session_tokens`, `consent_records`, `api_applications`, `webhook_endpoints`, `data_mapping_profiles`, `community_memberships`, `event_registrations` |
| **`TENANT_INDIRECT`** | 54 | Foreign Key to Parent | `plants`, `crop_seasons`, `diagnosis_requests`, `predictions`, `expert_assessments`, `satellite_observations`, `yield_forecast_records`, `harvest_plans`, `soil_profiles`, `irrigation_events` |
| **`SHARED_REFERENCE`**| 24 | Public / Taxonomy | `roles`, `crops`, `crop_varieties`, `crop_calendar_definitions`, `market_commodities`, `knowledge_documents`, `knowledge_chunks`, `learning_resources` |
| **`COMMUNITY_COLLABORATIVE`** | 16 | Community Authorship | `communities`, `community_posts`, `community_comments`, `community_reports`, `knowledge_contributions`, `research_projects`, `dataset_contributions` |
| **Total** | **132** | **100% Accounted For** | **Zero unmapped tables** |

### Historical Mismatch Reconciliation:
In the Phase 03 markdown report (`POSTGRESQL_RLS_VERIFICATION_REPORT.md`), the section headers stated "(51 tables)" for indirect and "(19 tables)" for collaborative, but the lists beneath them contained exactly 54 and 16 tables respectively. The 54 and 16 table counts represent the actual physical database models.

---

## 2. Policy Composition Architecture Fix

### The PostgreSQL RLS Policy Composition Rule:
In PostgreSQL engine architecture:
- `PERMISSIVE` policies combine via `OR`.
- `RESTRICTIVE` policies combine via `AND`.
- **If a table has ONLY restrictive policies and no permissive policy, PostgreSQL denies all operations because the default permissive state evaluates to false.**

### Remediation Applied in `backend/app/database/rls.py`:
In Phase 05, `generate_rls_ddl()` was upgraded to generate a base `PERMISSIVE` policy (`_base_access_policy`) that permits processing, layered with a `RESTRICTIVE` policy (`_tenant_isolation_policy`) enforcing tenant boundaries:

```sql
-- Direct Tenant Example:
ALTER TABLE plots ENABLE ROW LEVEL SECURITY;
ALTER TABLE plots FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS plots_base_access_policy ON plots;
CREATE POLICY plots_base_access_policy ON plots
    AS PERMISSIVE FOR ALL TO PUBLIC USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS plots_tenant_isolation_policy ON plots;
CREATE POLICY plots_tenant_isolation_policy ON plots
    AS RESTRICTIVE FOR ALL TO PUBLIC
    USING (
        current_setting('app.is_admin', true) = 'true'
        OR farm_id::text = current_setting('app.current_tenant_id', true)
    )
    WITH CHECK (
        current_setting('app.is_admin', true) = 'true'
        OR farm_id::text = current_setting('app.current_tenant_id', true)
    );
```

### Hierarchical Child Policy (`TENANT_INDIRECT`):
Subqueries now evaluate the parent's actual ownership column (`farm_id`, `id`, or `user_id`):
```sql
CREATE POLICY plants_child_isolation_policy ON plants
    AS RESTRICTIVE FOR ALL TO PUBLIC
    USING (
        current_setting('app.is_admin', true) = 'true'
        OR EXISTS (
            SELECT 1 FROM plots
            WHERE plots.id = plants.plot_id
              AND (
                  plots.farm_id::text = current_setting('app.current_tenant_id', true)
                  OR plots.id::text = current_setting('app.current_tenant_id', true)
              )
        )
    );
```

---

## 3. Automated Test Evidence (23 Tests Passing)

All 23 isolation tests in `backend/tests/test_postgresql_rls.py` passed:
1. `test_complete_table_classification_coverage`: 132/132 tables mapped.
2. `test_table_classification_categories`: Valid enum bindings.
3. `test_generate_rls_ddl_tenant_direct`: Base permissive and restrictive isolation policies verified.
4. `test_generate_rls_ddl_user_owned`: User-scoped isolation verified.
5. `test_generate_rls_ddl_shared_reference`: Public read, admin write verified.
6. `test_generate_rls_ddl_tenant_indirect`: Hierarchical EXISTS subquery verified.
7. `test_generate_rls_ddl_community_collaborative`: Author write, public read verified.
8. `test_tenant_context_lifecycle_sqlite`: Session dictionary lifecycle verified.
9. `test_tenant_context_lifecycle_simulated_postgresql`: Transaction-scoped `set_config` verified.
10–23: Validation of all 16 isolation criteria (cross-tenant read/update/delete/insert denial, unauthenticated denial, parent-child cascade, connection pool reuse, transaction rollback, and admin bypass).
