# ACREVIA — STAGE 4 DATABASE IMPLEMENTATION SPECIFICATION
## Relational Data Modeling, 24-Entity Schema, Multi-Tenant Indexing, and pgvector Readiness

---

## 1. Relational Database Strategy

ACREVIA employs **PostgreSQL 16** as its canonical relational data store, accessed via **SQLAlchemy 2.0** mapped classes and managed through **Alembic** migrations. For local isolated unit/integration testing, the system provides zero-dependency **SQLite in-memory** execution (`sqlite:///:memory:`) using standard ANSI SQL datatypes and UUID string representations.

### Key Database Conventions:
- **Primary Keys:** UUID v4 represented as fixed-length strings (`String(36)`), guaranteeing uniform compatibility between PostgreSQL `uuid` and SQLite `varchar(36)`.
- **Timestamps:** Standardized UTC timestamps using `TimestampMixin` with `created_at` and `updated_at` tracking `DateTime(timezone=True)`.
- **Connection Management:** Pooled `QueuePool` with 10 connections (`max_overflow=20`) and connection recycling after 1800 seconds to eliminate stale cloud proxies.

---

## 2. 24-Entity Domain Schema Catalog

```
+---------------------------------------------------------------------------------------------------+
|                                 ACREVIA ENTITY-RELATIONSHIP SCHEMA                                |
+---------------------------------------------------------------------------------------------------+
  User (1) <==== owned_farms ====> (M) Farm (1) <==== plots ====> (M) Plot
     |                                   |                           |
     +--- (M) FarmMembership (M) --------+                           +--- (M) Plant
     |                                   |                           |
     +--- (M) ConsentRecord              +--- (M) Observation        +--- (M) CropSeason
     |                                             |                      |
     +--- (M) AuditLog                             +--- (M) Media         +--- (M) StageEvent
                                                   |         |
                                                   |         +--- (1) QualityAssessment
                                                   v
                                            DiagnosisRequest (1)
                                            ├── (1) Prediction (1) <==== candidates ====> (M) Candidate
                                            └── (1) ExpertReview (User role: AGRICULTURAL_EXPERT)
```

### 2.1 Identity & Access Domain
1. **`users`:** Core user account containing `id`, `phone` (unique E.164 index), `email` (unique index), `hashed_password` (bcrypt), `full_name`, `language_preference` (`te`, `en`, `hi`), `is_active`, `is_verified`.
2. **`roles`:** System-wide roles (`FARMER`, `AGRICULTURAL_EXPERT`, `RESEARCHER`, `ADMIN`).
3. **`user_roles`:** Join table enforcing many-to-many relationship between users and system roles.
4. **`session_tokens`:** Secure session storage tracking refresh tokens, device user-agents, IP addresses, and expiration timestamps.

### 2.2 Farm & Agronomic Hierarchy Domain
5. **`farms`:** Multi-tenant root entity with `owner_id` (FK to `users`), `name`, `state` ("Telangana"), `district`, `mandal`, `village`, `total_acreage`, `is_archived`.
6. **`farm_memberships`:** Multi-user collaboration join table linking `(farm_id, user_id)` with `role_in_farm` (`OWNER`, `MANAGER`, `WORKER`, `AGRONOMIST_ADVISOR`).
7. **`plots`:** Physical cultivation plot with `farm_id` (FK to `farms`), `name`, `soil_type` (`BLACK_COTTON`, `RED_CHALKA`, `ALLUVIAL`), `irrigation_source` (`BOREWELL`, `DRIP`, `CANAL`, `RAINFED`), `acreage`, `boundary_geojson`.
8. **`plants`:** Specific tagged perennial plant or quadrant with `plot_id` (FK to `plots`), `tag_code`, `crop_id`, `notes`.

### 2.3 Crops & Phenology Domain
9. **`crops`:** Supported crop catalogue (`cotton`, `rice`, `chilli`) with multilingual names (`name_en`, `name_te`, `name_hi`) and `scientific_name`.
10. **`crop_varieties`:** Commercial and research cultivars with `crop_id`, `name`, `duration_days`, `resistance_traits`.
11. **`crop_seasons`:** Cultivation cycle with `plot_id`, `crop_id`, `variety_id`, `season_type` (`KHARIF`, `RABI`, `SUMMER`), `sowing_date`, `current_stage`, `status` (`ACTIVE`, `HARVESTED`).
12. **`crop_stage_events`:** Historical phenological transitions with `crop_season_id`, `stage_name` (`VEGETATIVE`, `FLOWERING`, `BOLL_FORMATION`), `event_date`, `notes`.

### 2.4 Observations & Foliar Media Domain
13. **`observations`:** Agricultural field scouting record with `farm_id`, `plot_id`, `crop_season_id`, `observer_id`, `notes`, `symptom_tags`.
14. **`observation_media`:** Foliar photograph asset with `observation_id`, `storage_path`, `file_size_bytes`, `mime_type`, `sha256_hash` (indexed for deduplication), `is_primary`.
15. **`image_quality_assessments`:** Automated quality evaluation record with `media_id` (unique FK), `status` (`ACCEPTED`, `RETAKE_OR_REVIEW`, `QUARANTINED`), `sharpness_score`, `exposure_status`, `reasons_json`.

### 2.5 Diagnostics & Clinical Agronomy Domain
16. **`diagnosis_requests`:** State machine orchestrator with `observation_id`, `media_id`, `status` (`CREATED`, `PROCESSING`, `COMPLETED`, `NEEDS_REVIEW`, `FAILED`), `requested_at`, `completed_at`.
17. **`predictions`:** AI model prediction payload with `diagnosis_request_id` (unique FK), `model_version`, `decision_state` (1 of 8 agricultural states), `top_confidence`, `normalized_entropy`, `prediction_margin`, `cibrc_advisory`.
18. **`prediction_candidates`:** Ranked differential diagnosis candidates with `prediction_id`, `rank`, `class_id`, `display_name_en`, `display_name_te`, `display_name_hi`, `pathogen_or_cause`, `calibrated_prob`.
19. **`expert_reviews`:** Human agronomist clinical validation with `diagnosis_request_id` (unique FK), `expert_id` (FK to `users`), `status` (`CONFIRMED`, `OVERRIDDEN`), `verified_class_id`, `expert_notes`, `reviewed_at`.

### 2.6 Operations & Agrometeorology Domain
20. **`farm_operations`:** Farm activity journal (spraying, weeding, fertilizer application) with `farm_id`, `plot_id`, `operation_type`, `performed_at`, `inputs_applied_json`.
21. **`weather_observations`:** Ingested weather indicators with `farm_id`, `timestamp`, `temperature`, `humidity`, `precipitation`, `wind_speed`, `source`.
22. **`risk_assessments`:** Agro-climatic disease risk evaluation with `farm_id`, `crop_season_id`, `assessment_date`, `pest_risk_level`, `weather_risk_level`, `advisory`.

### 2.7 Governance & Compliance Domain
23. **`consent_records`:** Digital Personal Data Protection (DPDP) Act compliance log with `user_id`, `consent_type` (`CORE_SERVICE`, `EXPERT_REVIEW`, `RESEARCH_PARTICIPATION`, `MODEL_TRAINING`), `is_granted`, `policy_version`, `granted_at`, `revoked_at`.
24. **`audit_logs`:** Append-only cryptographic audit trail with `user_id`, `farm_id`, `action`, `resource_type`, `resource_id`, `ip_address`, `timestamp`, `metadata_json`.

---

## 3. Foreign Key Cascading & Indexing Strategies

### Cascading Rules:
- **`CASCADE` Delete:** Deleting a `Farm` safely removes related `Plot`, `FarmMembership`, and `Observation` records to prevent tenant data ghosting. Deleting an `Observation` automatically purges attached `ObservationMedia`, `ImageQualityAssessment`, and `DiagnosisRequest`.
- **`RESTRICT` Delete:** Attempting to delete a `User` who is a primary farm owner or has recorded active audit logs is strictly blocked by foreign key constraints, preserving regulatory auditability.
- **`SET NULL`:** Deleting an optional plot or crop season sets foreign key references in historical observations to `NULL` without destroying the underlying foliar evidence.

### Multi-Tenant Query Acceleration Indexes:
1. `ix_farms_district_mandal`: Composite index on `(district, mandal)` for spatial agro-climatic aggregation.
2. `uq_farm_user_membership`: Unique compound constraint on `(farm_id, user_id)` preventing duplicate user memberships in the same farm.
3. `ix_observation_media_sha256`: Cryptographic checksum index for zero-storage duplicate image deduplication.
4. `ix_audit_logs_user_farm`: Multi-column index on `(user_id, farm_id)` for high-speed security audit filtering.

---

## 4. pgvector Readiness (Stage 5 RAG Foundation)

The schema design incorporates pgvector extension compatibility for upcoming Stage 5 KrishiBrain knowledge retrieval:
- In PostgreSQL deployments, the extension is activated via `CREATE EXTENSION IF NOT EXISTS vector;`.
- Agronomic knowledge chunks and disease monographs will store embedding representations using `VECTOR(1536)` (OpenAI/Gemini compatible) with HNSW (Hierarchical Navigable Small World) cosine indexing (`vector_cosine_ops`) for sub-millisecond retrieval.
