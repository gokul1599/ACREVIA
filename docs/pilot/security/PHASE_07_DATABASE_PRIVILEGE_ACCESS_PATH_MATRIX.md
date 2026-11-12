# ACREVIA — PHASE 07: DATABASE PRIVILEGE & ACCESS PATH AUDIT MATRIX (132-TABLE CROSSWALK)

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation  
**Document ID:** `ACR-SEC-P07-DB-PRIV-MATRIX`  
**Classification:** RESTRICTED — PILOT DATABASE SECURITY AUDIT  
**Operating Mode:** **`MODE A ONLY`** (Local Source Inspection & Offline Verification)  
**Audit Determination:** **`PARTIALLY_RESOLVED`**  
- `LOCAL_PRIVILEGE_SPECIFICATION`: **`RESOLVED_LOCALLY_AND_TESTED`**  
- `LIVE_DATABASE_ACL_ENFORCEMENT`: **`BLOCKED_PENDING_LIVE_POSTGRESQL`** (Requires Gate 02/04 on live staging)  
**Associated Baseline Tests:** `backend/tests/test_worker_security_and_privacy.py` (`test_database_privileges_truncate_and_views_audit`, `test_132_tables_exact_crosswalk_set_equality`, `test_132_tables_privilege_crosswalk_exact_counts_and_no_blanket_dml`, `test_idempotent_privilege_grants_ddl_explicit_revokes` — 55 tests in suite, 102 across Phase 07)  

---

## 1. Executive Summary & Core PostgreSQL Rule

> [!CRITICAL]
> **A locally specified GRANT is not a live database ACL.**  
> In PostgreSQL, Row-Level Security (RLS) policies apply **only** to standard row-level DML operations (`SELECT`, `INSERT`, `UPDATE`, `DELETE`).  
> RLS does **not** protect against:
> 1. **`TRUNCATE`**: Bypasses all row-level filters and clears the entire table regardless of active RLS policies.
> 2. **`REFERENCES`**: In PostgreSQL, the `REFERENCES` privilege permits a role to create foreign-key constraints referencing a target table or columns. Denying it prevents unprivileged runtime roles from creating unauthorized schema-level foreign keys, creating lock contention side-channels, and existence-probing rows across tenant boundaries.
> 3. **`TRIGGER`**: Allows creation of triggers that execute arbitrary code with elevated owner permissions.
>
> Furthermore, in SQL **omission is not revocation**. If a runtime role previously acquired direct or inherited privileges, omitting `UPDATE` and `DELETE` from a `GRANT` statement leaves pre-existing privileges active! Therefore, `generate_privilege_grants_ddl()` generates fully idempotent SQL emitting explicit `REVOKE` statements for disallowed DML prior to granting permitted DML.  
> Across all 132 database entities:
> - **SELECT**: Granted on all **132** tables.
> - **INSERT**: Granted on **108** tables (91 tenant + 16 community + 1 shared reference `ingestion_jobs`); Denied on **24** shared reference tables.
> - **UPDATE**: Granted on **107** tables (90 tenant + 16 community + 1 shared reference `ingestion_jobs`); Denied on **24** shared reference tables and **1** append-only table (`audit_logs`).
> - **DELETE**: Granted on **90** tenant tables; Strictly **DENIED** on all **16** community tables, all **25** shared reference tables, and **1** append-only table (`audit_logs`).
> - **TRUNCATE**: Strictly **DENIED (0 tables)**.
> - **REFERENCES**: Strictly **DENIED (0 tables)**.
> - **TRIGGER**: Strictly **DENIED (0 tables)**.

---

## 2. Category Reconciliation & Authoritative Distribution

Earlier preliminary summaries reported differing category counts (e.g. 24 direct, 51 indirect, 20 community) due to privilege-oriented groupings. The authoritative metadata distribution in `TABLE_CLASSIFICATION` ([`backend/app/database/rls.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py)) across all 132 tables in `Base.metadata` is reconciled below:

| Authoritative RLS Category | Exact Entity Count | FORCE RLS Enforced | ENABLE RLS Enforced | Privilege Group Identifier | Core Isolation Mechanism |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **`tenant_direct`** | **25** | **25** (YES) | **25** (YES) | `TENANT_DIRECT_DML` | Direct `farm_id` / `tenant_id` RESTRICTIVE policy guard. |
| **`user_owned`** | **13** | **13** (YES) | **13** (YES) | `USER_OWNED_DML` | Direct `user_id` RESTRICTIVE policy guard. |
| **`tenant_indirect`** | **53** | **53** (YES) | **53** (YES) | `TENANT_INDIRECT_DML` | Child table linked via foreign key to plot/season/observation. |
| **`shared_reference`** | **25** | **3** (YES) / **22** (NO) | **25** (YES) | `PUBLIC_SHARED_REF` / `ADMIN_INTEGRATION_REF` | 22 public reference tables (read-only); 3 private/admin tables. |
| **`community`** | **16** | **16** (YES) | **16** (YES) | `COMMUNITY_COLLABORATIVE_DML` | Collaborative posts/signals with author/expert scoping. |
| **Total Reconciled** | **`132`** | **`110`** | **`132`** | — | **100% of Base.metadata accounted for (0 missing, 0 phantom).** |

---


---

## 2.1. Programmatic Privilege Crosswalk & Mathematical Reconciliation

The least-privilege matrix is programmatically defined in `backend/app/database/rls.py` as `PRIVILEGE_CROSSWALK`:

```python
# Programmatic least-privilege derivation in backend/app/database/rls.py
PRIVILEGE_CROSSWALK: Dict[str, Dict[str, Any]]
```

### 1. Mathematical Privilege Distribution
| Privilege Name | Granted Tables | Denied Tables | Scope & Category Justification |
| :--- | :---: | :---: | :--- |
| **`SELECT`** | **132** | **0** | Baseline read visibility required across all application entities. |
| **`INSERT`** | **108** | **24** | Allowed for tenant tables, community contributions, and `ingestion_jobs`. Denied for static reference tables. |
| **`UPDATE`** | **107** | **25** | Allowed for mutable entities; denied for read-only agricultural reference catalogs (24) and append-only audit trail `audit_logs` (1). |
| **`DELETE`** | **90** | **42** | **Strictly denied on all 16 community tables**, all 25 reference tables, and append-only audit trail `audit_logs` (1). Allowed only on mutable tenant entities. |
| **`TRUNCATE`** | **0** | **132** | **0 tables authorized.** Prevents whole-table wipeout bypassing RLS. |
| **`REFERENCES`** | **0** | **132** | **0 tables authorized.** Prevents unauthorized schema-level foreign-key creation and cross-tenant existence probing. |
| **`TRIGGER`** | **0** | **132** | **0 tables authorized.** Prevents unprivileged trigger injection. |

### 2. Evidence Classification Taxonomy
Every assertion in this matrix carries one of four explicit evidence classifications:
- **`LOCALLY_SPECIFIED`**: The privilege configuration is fully specified in local source code (`PRIVILEGE_CROSSWALK`, `TABLE_CLASSIFICATION`, `generate_privilege_grants_ddl`).
- **`PROPOSED_FOR_FUTURE_PROVISIONING`**: The role creation DDL for `acrevia_staging_app` and `acrevia_admin` is authored and tested offline, pending Project Owner approval.
- **`NOT_LIVE_INSTALLED`**: The SQL `GRANT` and `REVOKE` statements have not been applied to the live Neon PostgreSQL database.
- **`NOT_PROVEN_LIVE`**: Database kernel catalog reflection (`information_schema.table_privileges`, `pg_class`, `pg_roles`) has not been queried against physical cloud infrastructure in Mode A.


### 3. Idempotent DDL Generation: Omission is Not Revocation
In PostgreSQL privilege management, issuing `GRANT SELECT, INSERT ON TABLE audit_logs TO role;` does NOT revoke pre-existing `UPDATE` or `DELETE` grants. To achieve genuine idempotency, `generate_privilege_grants_ddl()` explicitly revokes disallowed permissions:
```sql
-- Explicit defensive revocation guarantees clean slate regardless of prior grants
REVOKE UPDATE, DELETE ON TABLE audit_logs FROM acrevia_staging_app;
GRANT SELECT, INSERT ON TABLE audit_logs TO acrevia_staging_app;
REVOKE TRUNCATE, REFERENCES, TRIGGER ON TABLE audit_logs FROM acrevia_staging_app;
```
Verified via unit test `test_idempotent_privilege_grants_ddl_explicit_revokes`:
- Emits explicit `REVOKE UPDATE, DELETE ON TABLE audit_logs`.
- Emits explicit `REVOKE DELETE ON TABLE agricultural_organizations`.
- Emits explicit `REVOKE INSERT, UPDATE, DELETE ON TABLE crops`.
- Emits explicit `REVOKE TRUNCATE, REFERENCES, TRIGGER` on all 132 tables.

## 4. Authoritative 132-Table Privilege & RLS Crosswalk

The table below provides the single authoritative, complete, table-by-table crosswalk for every entity in ACREVIA:

| # | SQL Table Name | ORM Model Class | RLS Category | Privilege Group | ENABLE RLS | FORCE RLS | SELECT | INSERT | UPDATE | DELETE | TRUNCATE | REFERENCES | TRIGGER | PROPOSED_TABLE_OWNER (NOT_LIVE_VERIFIED) | Notes |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| 1 | `agricultural_organizations` | `AgriculturalOrganization` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 2 | `agricultural_practice_definitions` | `AgriculturalPracticeDefinition` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 3 | `annotation_records` | `AnnotationRecord` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 4 | `annotation_tasks` | `AnnotationTask` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 5 | `api_applications` | `ApiApplication` | `user_owned` | `USER_OWNED_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by user_id RESTRICTIVE |
| 6 | `api_credentials` | `ApiCredential` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of api_applications via application_id |
| 7 | `audit_logs` | `AuditLog` | `tenant_direct` | `TENANT_DIRECT_APPEND_ONLY` | **YES** | **YES** | Granted | Granted | **Denied** | **Denied** | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE; strictly append-only under ACREVIA audit-integrity architectural specification (UPDATE & DELETE denied) |
| 8 | `climate_adaptation_scenarios` | `ClimateAdaptationScenario` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of climate_exposure_assessments via assessment_id |
| 9 | `climate_baselines` | `ClimateBaseline` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 10 | `climate_exposure_assessments` | `ClimateExposureAssessment` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 11 | `collective_activities` | `CollectiveActivity` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 12 | `communities` | `Community` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 13 | `community_comments` | `CommunityComment` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 14 | `community_memberships` | `CommunityMembership` | `user_owned` | `USER_OWNED_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by user_id RESTRICTIVE |
| 15 | `community_posts` | `CommunityPost` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 16 | `community_reports` | `CommunityReport` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 17 | `consent_records` | `ConsentRecord` | `user_owned` | `USER_OWNED_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by user_id RESTRICTIVE |
| 18 | `contribution_reviews` | `ContributionReview` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 19 | `crop_calendar_definitions` | `CropCalendarDefinition` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 20 | `crop_loss_evidence_packages` | `CropLossEvidencePackage` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 21 | `crop_season_economics` | `CropSeasonEconomics` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of crop_seasons via crop_season_id |
| 22 | `crop_seasons` | `CropSeason` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 23 | `crop_stage_events` | `CropStageEvent` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of crop_seasons via crop_season_id |
| 24 | `crop_tasks` | `CropTask` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 25 | `crop_varieties` | `CropVariety` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 26 | `crops` | `Crop` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 27 | `data_exchange_jobs` | `DataExchangeJob` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 28 | `data_mapping_profiles` | `DataMappingProfile` | `user_owned` | `USER_OWNED_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by user_id RESTRICTIVE |
| 29 | `data_sharing_grants` | `DataSharingGrant` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 30 | `dataset_contributions` | `DatasetContribution` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 31 | `decision_feedbacks` | `DecisionFeedback` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of decision_records via decision_id |
| 32 | `decision_records` | `DecisionRecord` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 33 | `diagnosis_requests` | `DiagnosisRequest` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of observations via observation_id |
| 34 | `environmental_accounting_estimates` | `EnvironmentalAccountingEstimate` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 35 | `event_registrations` | `EventRegistration` | `user_owned` | `USER_OWNED_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by user_id RESTRICTIVE |
| 36 | `expert_assessment_revisions` | `ExpertAssessmentRevision` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of expert_assessments via assessment_id |
| 37 | `expert_assessments` | `ExpertAssessment` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of expert_review_cases via case_id |
| 38 | `expert_profiles` | `ExpertProfile` | `user_owned` | `USER_OWNED_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by user_id RESTRICTIVE |
| 39 | `expert_review_cases` | `ExpertReviewCase` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 40 | `expert_reviews` | `ExpertReview` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of diagnosis_requests via diagnosis_request_id |
| 41 | `farm_expenses` | `FarmExpense` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 42 | `farm_memberships` | `FarmMembership` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 43 | `farm_operations` | `FarmOperation` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 44 | `farm_practice_records` | `FarmPracticeRecord` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 45 | `farm_twins` | `FarmTwin` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 46 | `farms` | `Farm` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by id RESTRICTIVE |
| 47 | `financial_corrections` | `FinancialCorrection` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of farm_expenses via expense_id |
| 48 | `fusion_explanations` | `FusionExplanation` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 49 | `harvest_measurements` | `HarvestMeasurement` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 50 | `harvest_plans` | `HarvestPlan` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 51 | `harvest_sessions` | `HarvestSession` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of harvest_plans via harvest_plan_id |
| 52 | `image_quality_assessments` | `ImageQualityAssessment` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of observation_media via media_id |
| 53 | `ingestion_jobs` | `IngestionJob` | `shared_reference` | `PRIVATE_OPERATIONAL_REF` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Agronomist/Expert/Admin worker scoped |
| 54 | `integration_partners` | `IntegrationPartner` | `shared_reference` | `ADMIN_INTEGRATION_REF` | **YES** | **YES** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Administrative integration reference |
| 55 | `intervention_records` | `InterventionRecord` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 56 | `irrigation_events` | `IrrigationEvent` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 57 | `knowledge_chunks` | `KnowledgeChunk` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 58 | `knowledge_contributions` | `KnowledgeContribution` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 59 | `knowledge_document_versions` | `KnowledgeDocumentVersion` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 60 | `knowledge_documents` | `KnowledgeDocument` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 61 | `knowledge_embeddings` | `KnowledgeEmbedding` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 62 | `knowledge_entities` | `KnowledgeEntity` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 63 | `knowledge_feedback` | `KnowledgeFeedback` | `user_owned` | `USER_OWNED_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by user_id RESTRICTIVE |
| 64 | `knowledge_relationships` | `KnowledgeRelationship` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 65 | `knowledge_sources` | `KnowledgeSource` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 66 | `learning_feedback` | `LearningFeedback` | `user_owned` | `USER_OWNED_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by user_id RESTRICTIVE |
| 67 | `learning_resources` | `LearningResource` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 68 | `location_permissions` | `LocationPermission` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 69 | `lot_movements` | `LotMovement` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of produce_lots via lot_id |
| 70 | `market_commodities` | `MarketCommodity` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 71 | `market_locations` | `MarketLocation` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 72 | `market_price_observations` | `MarketPriceObservation` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 73 | `nutrient_assessments` | `NutrientAssessment` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of soil_test_results via soil_test_result_id |
| 74 | `nutrient_expert_reviews` | `NutrientExpertReview` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of nutrient_assessments via nutrient_assessment_id |
| 75 | `observation_media` | `ObservationMedia` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of observations via observation_id |
| 76 | `observations` | `Observation` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 77 | `optimization_problems` | `OptimizationProblem` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 78 | `optimization_results` | `OptimizationResult` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of optimization_problems via problem_id |
| 79 | `organization_memberships` | `OrganizationMembership` | `user_owned` | `USER_OWNED_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by user_id RESTRICTIVE |
| 80 | `outcome_observations` | `OutcomeObservation` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of intervention_records via intervention_id |
| 81 | `partner_integrations` | `PartnerIntegration` | `shared_reference` | `ADMIN_INTEGRATION_REF` | **YES** | **YES** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Administrative integration reference |
| 82 | `plants` | `Plant` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 83 | `plot_geometries` | `PlotGeometry` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 84 | `plots` | `Plot` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 85 | `prediction_candidates` | `PredictionCandidate` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of predictions via prediction_id |
| 86 | `predictions` | `Prediction` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of diagnosis_requests via diagnosis_request_id |
| 87 | `produce_lots` | `ProduceLot` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 88 | `produce_quality_profiles` | `ProduceQualityProfile` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 89 | `quality_measurements` | `QualityMeasurement` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of produce_lots via lot_id |
| 90 | `regional_signal_evidences` | `RegionalSignalEvidence` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 91 | `regional_signals` | `RegionalSignal` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 92 | `research_consents` | `ResearchConsent` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 93 | `research_projects` | `ResearchProject` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 94 | `resilience_assessments` | `ResilienceAssessment` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 95 | `resilience_scenario_simulations` | `ResilienceScenarioSimulation` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of resilience_assessments via assessment_id |
| 96 | `risk_alerts` | `RiskAlert` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 97 | `risk_assessment_records` | `RiskAssessmentRecord` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 98 | `risk_assessments` | `RiskAssessment` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 99 | `risk_rules` | `RiskRule` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 100 | `roles` | `Role` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 101 | `sale_transactions` | `SaleTransaction` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of produce_lots via lot_id |
| 102 | `satellite_acquisitions` | `SatelliteAcquisition` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 103 | `satellite_observations` | `SatelliteObservation` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 104 | `satellite_sources` | `SatelliteSource` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 105 | `sensor_calibrations` | `SensorCalibration` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of sensor_devices via device_id |
| 106 | `sensor_devices` | `SensorDevice` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 107 | `sensor_measurements` | `SensorMeasurement` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 108 | `session_tokens` | `SessionToken` | `user_owned` | `USER_OWNED_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by user_id RESTRICTIVE |
| 109 | `simulation_results` | `SimulationResult` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of simulation_scenarios via scenario_id |
| 110 | `simulation_scenarios` | `SimulationScenario` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 111 | `soil_carbon_measurements` | `SoilCarbonMeasurement` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 112 | `soil_moisture_observations` | `SoilMoistureObservation` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 113 | `soil_profiles` | `SoilProfile` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 114 | `soil_samples` | `SoilSample` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 115 | `soil_test_results` | `SoilTestResult` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of soil_samples via soil_sample_id |
| 116 | `storage_locations` | `StorageLocation` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 117 | `storage_lots` | `StorageLot` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of produce_lots via lot_id |
| 118 | `training_events` | `TrainingEvent` | `shared_reference` | `PUBLIC_SHARED_REF` | **YES** | **NO** | Granted | Denied | Denied | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Public/Authenticated read-only reference |
| 119 | `translation_versions` | `TranslationVersion` | `community` | `COMMUNITY_COLLABORATIVE_DML` | **YES** | **YES** | Granted | Granted | Granted | Denied | **Denied** | **Denied** | **Denied** | `neondb_owner` | Author/Expert collaborative isolation |
| 120 | `twin_snapshots` | `TwinSnapshot` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 121 | `twin_state_records` | `TwinStateRecord` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of twin_snapshots via snapshot_id |
| 122 | `twin_synchronization_events` | `TwinSynchronizationEvent` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of farm_twins via twin_id |
| 123 | `user_roles` | `UserRole` | `user_owned` | `USER_OWNED_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by user_id RESTRICTIVE |
| 124 | `users` | `User` | `user_owned` | `USER_OWNED_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by id RESTRICTIVE |
| 125 | `water_balance_snapshots` | `WaterBalanceSnapshot` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |
| 126 | `water_sources` | `WaterSource` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 127 | `weather_data` | `WeatherData` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 128 | `weather_observations` | `WeatherObservation` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by farm_id RESTRICTIVE |
| 129 | `webhook_deliveries` | `WebhookDelivery` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of webhook_endpoints via endpoint_id |
| 130 | `webhook_endpoints` | `WebhookEndpoint` | `user_owned` | `USER_OWNED_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by user_id RESTRICTIVE |
| 131 | `webhook_events` | `WebhookEvent` | `tenant_direct` | `TENANT_DIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Scoped by tenant_id RESTRICTIVE |
| 132 | `yield_forecast_records` | `YieldForecastRecord` | `tenant_indirect` | `TENANT_INDIRECT_DML` | **YES** | **YES** | Granted | Granted | Granted | Granted | **Denied** | **Denied** | **Denied** | `neondb_owner` | Child of plots via plot_id |

---

## 4. Verification of Actual GRANT and REVOKE Source

### 1. Local Provisioning Specification (`scripts/neon_staging_branch_spec.py`)
Inspection of `get_staging_branch_specification()` confirms that the runtime role specification for `acrevia_staging_app` explicitly records:
- `is_superuser`: **`False`**
- `bypass_rls`: **`False`**
- `can_create_db`: **`False`**
- `can_create_role`: **`False`**
- `can_truncate`: **`False`** (Non-negotiable invariant)
- `can_references`: **`False`** (Non-negotiable invariant)
- `can_trigger`: **`False`**
- `admin_role_membership`: **`False`**

### 2. Distinction: Local Specification vs. Live ACL State
- **Locally Specified:** The engineering harness and role generators define least-privilege DML (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) and ban `TRUNCATE` and `REFERENCES`.
- **Live Database ACL State:** Until Decision Gate 02 is authorized and executed on the live Neon staging branch via PostgreSQL commands (`REVOKE ALL ON ALL TABLES IN SCHEMA public FROM acrevia_staging_app; GRANT SELECT, INSERT, UPDATE, DELETE...`), the live ACL state remains **uninstalled and unverified**.
- **Governance Classification:** `LOCAL_PRIVILEGE_SPECIFICATION = RESOLVED_LOCALLY_AND_TESTED`; `LIVE_DATABASE_ACL_ENFORCEMENT = BLOCKED_PENDING_LIVE_POSTGRESQL`.

---

## 5. Non-Table SQL Privileges Inventory & Evidence Tagging

Every SQL-level permission beyond standard table DML is classified below with its rigorous evidence taxonomy tag:

| Non-Table SQL Privilege / Capability | Runtime Role (`acrevia_staging_app`) | Admin Role (`acrevia_admin`) | Migration Owner (`neondb_owner`) | Evidence Classification Status | Security Rationale & Specification |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **Schema `USAGE` on `public`** | **Allowed** | **Allowed** | **Allowed** | `LOCALLY_SPECIFIED` / `PROPOSED_FOR_FUTURE_PROVISIONING` / `NOT_LIVE_INSTALLED` / `NOT_PROVEN_LIVE` | Required for namespace resolution of public tables. |
| **Schema `CREATE` on `public`** | **DENIED** | **DENIED** | **Allowed** | `LOCALLY_SPECIFIED` / `PROPOSED_FOR_FUTURE_PROVISIONING` / `NOT_LIVE_INSTALLED` / `NOT_PROVEN_LIVE` | Prevents runtime role from creating untracked tables or spoofing functions. |
| **Sequence `USAGE`, `SELECT`** | **Allowed** | **Allowed** | **Allowed** | `LOCALLY_SPECIFIED` / `PROPOSED_FOR_FUTURE_PROVISIONING` / `NOT_LIVE_INSTALLED` / `NOT_PROVEN_LIVE` | Required for auto-incrementing surrogate primary keys (`bigserial`/`identity`). |
| **Sequence `UPDATE`** | **DENIED** | **DENIED** | **Allowed** | `LOCALLY_SPECIFIED` / `PROPOSED_FOR_FUTURE_PROVISIONING` / `NOT_LIVE_INSTALLED` / `NOT_PROVEN_LIVE` | Prevents out-of-order sequence exhaustion or primary-key collisions. |
| **Table `TRUNCATE`** | **DENIED** | **DENIED** | **Allowed** | `LOCALLY_SPECIFIED` / `PROPOSED_FOR_FUTURE_PROVISIONING` / `NOT_LIVE_INSTALLED` / `NOT_PROVEN_LIVE` | RLS bypass mitigation: whole-table truncation strictly denied. |
| **Table `REFERENCES`** | **DENIED** | **DENIED** | **Allowed** | `LOCALLY_SPECIFIED` / `PROPOSED_FOR_FUTURE_PROVISIONING` / `NOT_LIVE_INSTALLED` / `NOT_PROVEN_LIVE` | Prevents unauthorized schema-level foreign key creation, cross-table locking side-channels, and unexpected dependency chains. |
| **Table `TRIGGER`** | **DENIED** | **DENIED** | **Allowed** | `LOCALLY_SPECIFIED` / `PROPOSED_FOR_FUTURE_PROVISIONING` / `NOT_LIVE_INSTALLED` / `NOT_PROVEN_LIVE` | Prevents unauthorized trigger creation or event manipulation. |
| **Default Privileges (`ALTER DEFAULT...`)** | **Restricted** | **Restricted** | **Configured** | `LOCALLY_SPECIFIED` / `PROPOSED_FOR_FUTURE_PROVISIONING` / `NOT_LIVE_INSTALLED` / `NOT_PROVEN_LIVE` | Default table creation privileges automatically inherit least-privilege DML. |
| **Role Attribute: `NOINHERIT`** | **NOINHERIT** | **NOINHERIT** | **INHERIT** | `LOCALLY_SPECIFIED` / `PROPOSED_FOR_FUTURE_PROVISIONING` / `NOT_LIVE_INSTALLED` / `NOT_PROVEN_LIVE` | Prevents ambient role grant inheritance. Note: NOINHERIT alone does not prevent switching roles if explicit SET ROLE is authorized. |
| **Database `CONNECT`** | **Allowed** | **Allowed** | **Allowed** | `LOCALLY_SPECIFIED` / `PROPOSED_FOR_FUTURE_PROVISIONING` / `NOT_LIVE_INSTALLED` / `NOT_PROVEN_LIVE` | Baseline connection requirement for connection pool checkouts. |
| **Database `TEMPORARY`** | **DENIED** | **DENIED** | **Allowed** | `LOCALLY_SPECIFIED` / `PROPOSED_FOR_FUTURE_PROVISIONING` / `NOT_LIVE_INSTALLED` / `NOT_PROVEN_LIVE` | Prevents temporary table search-path poisoning attacks. |

---

## 6. Correct PostgreSQL Object Inventory Claims

Separating source inspection proof from live database catalog inspection:

### Local Source Inspection Findings:
- **`NO_VIEW_DEFINITIONS_FOUND_IN_INSPECTED_LOCAL_SOURCE`:** An exhaustive scan of `backend/app/models/` and all Alembic migration revisions confirms that zero standard SQL views (`CREATE VIEW`) or materialized views (`CREATE MATERIALIZED VIEW`) exist in the repository. All 132 entities in `Base.metadata` are mapped base tables.
- **`NO_USER_DEFINED_SECURITY_DEFINER_FUNCTIONS_FOUND_IN_INSPECTED_LOCAL_SOURCE`:** An exhaustive scan across migrations and SQL generators confirms that zero user-defined `SECURITY DEFINER` functions exist in the codebase.

### Live PostgreSQL Catalog Status:
- **`LIVE_RELKIND_NOT_VERIFIED`:** Because remote database connections are strictly prohibited in Mode A, live catalog inspection via `pg_class.relkind = 'r'` has not been executed against PostgreSQL.
- **`LIVE_PG_PROC_NOT_VERIFIED`:** Live inspection of `pg_proc.prosecdef` has not been executed against PostgreSQL.
- **Requirement:** Catalog verification will execute via `scripts/verify_staging_rls.py` upon authorization of GATE-04 in Mode B.

### 5. Sensitive Column Exposure & Row vs Column Confidentiality Audit
An adversarial audit of all 132 database entities identified **21 tables** containing sensitive columns (passwords, phone numbers, email addresses, API secrets, tokens, village identifiers, traceback logs):
- `users`: `phone`, `email`, `hashed_password`
- `farms`: `village`
- `expert_profiles`: `registration_number`
- `agricultural_organizations`: `registration_number`, `contact_email`, `contact_phone`
- `integration_partners`: `contact_email`, `contact_phone`
- `api_credentials`: `hashed_secret`, `secret_prefix`
- `sensor_devices`: `auth_token_hash`
- `session_tokens`: `refresh_token_hash`
- `webhook_endpoints`: `secret_hash`
- `knowledge_documents` / `chunks` / `embeddings`: `token_count`, `content_hash`, `embedding`
- `audit_logs`: `details`, `client_ip`, `user_id`

#### Architectural Finding & Threat Classification:
1. **Row-Level Security Boundary:** RLS filters *which rows* are visible under the query (`USING` clause). RLS does **not** filter or mask columns. Once a row satisfies the tenant policy, `SELECT *` returns all columns including sensitive fields.
2. **Application DTO Projections:** Confidentiality of sensitive fields currently relies on FastAPI/Pydantic response models (`UserResponse`, `AgriculturalOrganizationResponse`) which mask or omit fields before sending HTTP responses.
3. **Database-Level Risk:** If `acrevia_staging_app` executes unprojected `SELECT *`, it sees all columns of accessible rows.
4. **Offline Proof:** Verified by unit test `test_adversarial_sensitive_columns_unrestricted_select_crosswalk`.
