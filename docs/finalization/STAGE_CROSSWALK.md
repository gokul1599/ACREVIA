# ACREVIA — HISTORICAL ROADMAP & 14-STAGE CROSSWALK
## Reconciliation of Evolutionary Architecture, Stage Mappings & System Continuity

**Document Version:** 1.0.0  
**Status:** Approved Architectural Crosswalk  
**Scope:** Reconciles the historical 13-stage roadmap with the definitive 14-stage enterprise monograph.

---

### 1. Evolutionary Stage Mapping Matrix

The ACREVIA architecture evolved from an initial 13-stage progression into an expanded 14-stage enterprise agricultural platform. Below is the exact mapping of historical capabilities to their current production modules:

| Historical Stage & Title | Definitive 14-Stage Alignment | Core Implementation Modules | Database Tables | Automated Verification |
|---|---|---|---|---|
| **Stage 1:** Research Foundation & Environment | **Stage 01:** Research Baseline & Antigravity Setup | Root configuration, monorepo layout, agronomic references | N/A (Environment) | `docs/STAGE_1_ENVIRONMENT_AUDIT.md` |
| **Stage 2:** Agronomic Dataset Engineering | **Stage 02:** Agricultural Dataset Engineering & Taxonomy | `ml/src/dataset/stratified_split.py`, `ml/src/dataset/image_quality.py` | N/A (Preprocessing) | 18 unit tests in `tests/ml/` |
| **Stage 3:** Computer Vision & Calibration | **Stage 03:** Computer Vision, Calibration & Inference Microservice | `ml/src/models/multicrop_classifier.py`, `ml/inference_service/app.py` | N/A (ML Runtime) | `test_inference_service.py` (7 passed) |
| **Stage 4:** KrishiBrain Multimodal RAG | **Stage 04:** KrishiBrain Multilingual Multimodal RAG Subsystem | `backend/app/rag/`, `backend/app/services/knowledge_service.py` | `knowledge_sources`, `knowledge_documents`, `knowledge_chunks`, `knowledge_feedback` | `test_knowledge.py` (8 passed) |
| **Stage 5:** Farm Journal & Weather | **Stage 05:** Farm Action Journal, Observations & Weather | `backend/app/models/observation.py`, `backend/app/services/weather_service.py` | `observations`, `observation_images`, `weather_snapshots` | `test_observations.py`, `test_system_weather.py` |
| **Stage 6:** Vernacular PWA & Voice | **Stage 06:** Vernacular PWA, Offline Queue & Speech Interaction | `frontend/src/app/`, `frontend/src/lib/offlineQueue.ts`, `frontend/src/lib/speech.ts` | IndexedDB (Client side) | `frontend test` (36 passed) |
| **Stage 7:** RiskCast & ExpertConnect | **Stage 07:** RiskCast, ExpertConnect & Intervention Tracking | `backend/app/services/riskcast_service.py`, `backend/app/services/expert_service.py` | `risk_rules`, `risk_alerts`, `expert_profiles`, `expert_reviews`, `interventions` | `test_stage7.py` (6 passed) |
| **Stage 8:** Production Hardening & E2E | **Stage 08:** Production Hardening, Observability & E2E Validation | `backend/app/middleware/`, `backend/app/core/security.py` | System-wide audit logs | `test_stage8_e2e.py` (8 workflows passed) |
| **Stage 9:** Precision Ag & IoT Fusion | **Stage 09:** Precision Ag, Satellite Intelligence & IoT Integration | `backend/app/models/precision_ag.py`, `backend/app/services/earth_service.py` | `geospatial_plots`, `satellite_scenes`, `iot_devices`, `sensor_telemetry`, `evidence_fusions` | `test_stage9.py` (7 passed) |
| **Stage 10:** Digital Twin & Decision AI | **Stage 10:** Intelligent Digital Twin, Simulation & Decision Support | `backend/app/models/digital_twin.py`, `backend/app/services/twin_service.py` | `digital_twins`, `twin_snapshots`, `simulations`, `optimizations`, `recommendations` | `test_stage10.py` (8 passed) |
| **Stage 11:** Economics & Traceability | **Stage 11:** Agricultural Economics, Mandi Realization & Traceability | `backend/app/models/financial_ledger.py`, `backend/app/models/harvest_traceability.py` | `farm_expenses`, `financial_corrections`, `market_prices`, `harvest_sessions`, `produce_lots` | `test_stage11.py` (7 passed) |
| **Stage 12:** Collectives & Commons | **Stage 12:** Agricultural Collaboration, FPO Workspaces & Regional Pulse | `backend/app/models/collaboration.py`, `backend/app/services/community_service.py` | `community_posts`, `commons_contributions`, `fpo_collectives`, `research_projects` | `test_stage12.py` (6 passed) |
| **Stage 13:** Soil, Water & Climate | **Stage 13:** Soil Health Intelligence, Precision Water & Climate Resilience | `backend/app/models/soil_health.py`, `backend/app/models/sustainability.py` | `soil_samples`, `soil_test_results`, `water_assets`, `irrigation_events`, `climate_normals` | `test_stage13.py` (7 passed) |
| **Stage 14:** Open APIs & Interoperability | **Stage 14:** Open API Ecosystem, Partner Integrations & Data Exchange | `backend/app/models/interoperability.py`, `backend/app/services/exchange_service.py` | `integration_partners`, `api_applications`, `api_credentials`, `webhook_events`, `data_exchange_jobs` | `test_stage14.py` (9 passed) |

---

### 2. Historical Core Gateway & Security Verification

All architectural requirements originally specified for the foundational backend have been verified as fully implemented and actively protected:

1. **FastAPI Modular Gateway:** Implemented in `backend/app/main.py` with OpenAPI specifications exposed at `/docs` and `/redoc`, equipped with versioned router aggregation (`/api/v1`).
2. **Cryptographic Authentication:** JWT tokens signed with HS256 (`PyJWT`), password hashing via 12-round salted `bcrypt` (`backend/app/core/security.py`).
3. **Session Management & Refresh Cycles:** Access tokens expire in 60 minutes; refresh tokens persist for 30 days with revocable state tracking in database.
4. **Role-Based Access Control (RBAC):** Strict role hierarchy (`FARMER`, `AGRICULTURAL_EXPERT`, `RESEARCHER`, `ADMIN`) enforced via FastAPI dependency `require_roles`.
5. **Farm Membership & Multi-Tenant Isolation:** Farm ownership and multi-farmer access verified via `verify_farm_access` (`backend/app/api/deps.py`), preventing cross-tenant data leakage (IDOR protection).
6. **Object Storage Abstraction:** Generic storage interface supporting local filesystem storage with SHA-256 deduplication and tokenized access URLs (`backend/app/core/storage.py`), with S3 compatibility configured for cloud deployment.
7. **Observability & Request Correlation:** Correlation ID middleware (`CorrelationIdMiddleware`) injecting `X-Correlation-ID` headers across all inbound and outbound requests, paired with structured JSON logging and Prometheus counter instrumentation.
8. **Disambiguation of 'Connect':**
   - **ACREVIA Connect (Stage 12):** Farmer community forum, peer discussion, and verified agronomist replies (`/api/v1/community`).
   - **ACREVIA Developer Connect (Stage 14):** External developer API platform, scoped application credentials (`ak_live_...`), and partner integrations (`/api/v1/developer`).
