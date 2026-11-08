# ACREVIA — STAGE 4 BACKEND ARCHITECTURE SPECIFICATION
## Enterprise-Grade Modular FastAPI Architecture, Domain Boundaries, and Service Decoupling

---

## 1. Executive Summary & Canonical Identity

**ACREVIA** is a research-grade agricultural intelligence platform targeting smallholder farmers in Telangana, India. The initial crops supported are **Cotton**, **Rice**, and **Chilli** across **Telugu**, **English**, and **Hindi**.

Stage 4 establishes the enterprise backend foundation, replacing monolithic or ad-hoc scripts with a decoupled, modular, production-ready architecture designed for horizontal scalability, tenant isolation, strict data governance, and auditable agricultural workflows.

```
+---------------------------------------------------------------------------------------+
|                                    CLIENT LAYER                                       |
|                  Next.js Web / Mobile Progressive Web App (PWA)                       |
+---------------------------------------------------------------------------------------+
                                           |  HTTPS / JWT Bearer
                                           v
+---------------------------------------------------------------------------------------+
|                           ACREVIA BACKEND GATEWAY (:8000)                             |
|  - Request Correlation ID Middleware (X-Correlation-ID)                               |
|  - Structured Request Logger & Latency Timer (X-Response-Time-Ms)                     |
|  - CORS & Security Headers Middleware                                                 |
|  - Centralized Exception Handlers (AcreviaException, HTTPException, Validation)       |
+---------------------------------------------------------------------------------------+
       |                           |                            |
       v                           v                            v
+------------------+     +------------------+         +------------------+
|   Core Domain    |     | Farm & Agronomy  |         | Diagnostics & AI |
|     Services     |     |     Services     |         |     Services     |
| - AuthService    |     | - FarmService    |         | - ObservationSvc |
| - AuditService   |     | - CropSeasonSvc  |         | - DiagnosisSvc   |
| - ConsentService |     | - PlotPlantSvc   |         | - ExpertReviewSvc|
+------------------+     +------------------+         +------------------+
       |                           |                            |
       +---------------------------+----------------------------+
                                   |
                                   v
+---------------------------------------------------------------------------------------+
|                          INTEGRATION & PERSISTENCE ADAPTERS                           |
|  +-------------------------+  +--------------------------+  +----------------------+  |
|  |   PostgreSQL / SQLite   |  | Private Storage Provider |  | ML Inference Client  |  |
|  |  (SQLAlchemy 2.0 Pool)  |  | (Local / Private S3 Enc) |  |   (:8001 Microservice) |  |
|  +-------------------------+  +--------------------------+  +----------------------+  |
|  +---------------------------------------------------------------------------------+  |
|  | Open-Meteo Agrometeorological Weather Client (Telangana Agro-Climatic Centroids)|  |
|  +---------------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------+
```

---

## 2. Directory Structure & Layer Isolation

The backend codebase is organized under `backend/app/` following strict single-responsibility principles:

```text
backend/
├── Dockerfile                   # Multi-stage unprivileged container build (Python 3.11-slim)
├── alembic.ini                  # Migration orchestrator configuration
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py          # /api/v1/auth (Register, Login, Me)
│   │       │   ├── farms.py         # /api/v1/farms (Farm CRUD, Memberships)
│   │       │   ├── plots.py         # /api/v1/plots (Plot CRUD, Plant Tagging)
│   │       │   ├── seasons.py       # /api/v1/seasons (Crop Cycles, Phenological Stages)
│   │       │   ├── observations.py  # /api/v1/observations (Foliar Ingestion, Media Stream)
│   │       │   ├── diagnoses.py     # /api/v1/diagnoses (Pathology Requests, Predictions)
│   │       │   ├── expert_reviews.py# /api/v1/diagnoses/{id}/expert-review
│   │       │   ├── weather.py       # /api/v1/farms/{id}/weather (Agro-Risk Indices)
│   │       │   ├── consent.py       # /api/v1/consent (DPDP Consent Declarations)
│   │       │   └── system.py        # /api/v1/system (Info, Health & Integrations)
│   │       └── router.py            # Master API v1 Assembly Router
│   ├── core/
│   │   ├── config.py                # Pydantic BaseSettings with .env overrides
│   │   ├── exceptions.py            # Hierarchical Domain Exceptions (AcreviaException)
│   │   ├── logging.py               # JSON/Structured Logger with CorrelationIdFilter
│   │   └── security.py              # Bcrypt (rounds=12) & PyJWT (HS256) Encoders
│   ├── database/
│   │   ├── base.py                  # SQLAlchemy Declarative Base with TimestampMixin
│   │   ├── session.py               # Pooled Engine & Thread-Safe Session Generator
│   │   ├── init_db.py               # Baseline System Roles & Target Crops Seeder
│   │   └── migrations/              # Alembic Version History & Target Metadata
│   ├── integrations/
│   │   ├── ml_client.py             # HTTP Client to Stage 3 Inference Microservice (:8001)
│   │   ├── storage.py               # Abstract Storage Provider with Local/S3 Implementation
│   │   └── weather_client.py        # Open-Meteo Integration with Telangana Coordinates
│   ├── models/                      # 24 Relational Entities (SQLAlchemy 2.0 Mapped)
│   ├── schemas/                     # Pydantic v2 Request, Response, and Contract Schemas
│   ├── security/
│   │   ├── dependencies.py          # JWT Validation, RBAC & verify_farm_access
│   │   └── permissions.py           # SystemRole & FarmRole Enums
│   ├── services/                    # Encapsulated Business Logic Services
│   └── main.py                      # FastAPI App Gateway, Lifespan & Middlewares
└── tests/                           # 31 Comprehensive Pytest Integration Tests
```

---

## 3. Request Lifecycle & Middleware Pipeline

Every HTTP request traverses a standardized four-stage middleware pipeline before invoking endpoint handlers:

1. **Correlation ID Injection (`X-Correlation-ID`):**
   - Extracts incoming `X-Correlation-ID` from client header or mints a new UUID v4.
   - Binds the correlation identifier to `request.state.correlation_id` and the thread-local logger filter context.
2. **Execution Timing (`X-Response-Time-Ms`):**
   - High-precision wall-clock timer (`time.perf_counter`) captures request lifecycle duration.
   - Adds execution latency to the downstream response headers for client-side observability.
3. **Structured Request Logging:**
   - Emits standardized log entries: `METHOD /path - STATUS (LATENCYms) [CID: correlation_id]`.
4. **Domain Exception Handling:**
   - Traps all subclasses of `AcreviaException` and maps them into structured JSON error payloads containing `error_type`, `detail`, `details`, and `correlation_id`.
   - Traps unhandled exceptions, logs the traceback with correlation ID, and returns HTTP 500 without leaking stack traces or database connection strings to the client.

---

## 4. Multi-Tenant Authorization Invariants

ACREVIA enforces multi-tenancy at the **service and dependency layer**, rather than relying on error-prone client queries:

- **Ownership Rule:** A user owns a farm if `farm.owner_id == user.id`.
- **Collaborator Rule:** A user is authorized if an active `FarmMembership` record exists linking `(farm_id, user.id)`.
- **Superuser Override:** Users possessing the `ADMIN` system role have platform-wide read/write inspection rights.
- **Fail-Closed Security:** Any attempt by User B to query or mutate User A's farm, plot, observation, or private photograph triggers an immediate `HTTP 403 Forbidden` response. Client-supplied parameters such as `farm_id` in observation payloads are verified against the authenticated user token prior to database modification.

---

## 5. Decoupled ML Inference Architecture

To preserve backend responsiveness and avoid GIL contention from deep learning runtimes:
- The backend contains **zero PyTorch dependencies in production serving**.
- The backend delegates foliar classification to the **Stage 3 ML Inference Microservice** running as an independent daemon on `http://ml-inference:8001`.
- Communication occurs via non-blocking `httpx.AsyncClient` with a bounded 10.0-second timeout.
- In the event of microservice unavailability or network timeout, `DiagnosisService` automatically applies graceful degradation: sets diagnosis state to `NEEDS_REVIEW`, creates a suspected foliar anomaly candidate, and triggers an advisory notifying the farmer that an agronomist review has been queued.
