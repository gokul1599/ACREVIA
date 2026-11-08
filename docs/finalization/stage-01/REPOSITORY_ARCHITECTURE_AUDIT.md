# STAGE 01 — REPOSITORY ARCHITECTURE & MODULE AUDIT
## Monorepo Layout, Boundary Separation & Import Integrity Audit

**Stage:** 01 — Research Foundation, Environment & Reproducibility  
**Audit Timestamp:** 2026-11-08T15:24:00+05:30  
**Verification Target:** Directory Structure, Module Boundaries, Configuration Integrity  
**Status:** `COMPLETE_VERIFIED`  

---

### 1. Monorepo Structural Inventory

The repository is cleanly partitioned into four primary directories, ensuring separation of concerns:

```
ACREVIA Repository Root/
├── backend/                  # FastAPI Asynchronous Application Gateway
│   ├── alembic/              # Alembic configuration & migrations
│   ├── app/
│   │   ├── api/              # Versioned API routes (/api/v1)
│   │   ├── core/             # Security, configuration, logging, exceptions
│   │   ├── database/         # Session lifecycle, base ORM, seed scripts
│   │   ├── middleware/       # Correlation tracking, rate limiting
│   │   ├── models/           # 132 SQLAlchemy domain entities
│   │   ├── rag/              # KrishiBrain knowledge chunking, CIBRC safety
│   │   └── services/         # Domain business logic (Twin, Simulate, Market, etc.)
│   └── tests/                # 97 Automated Pytest backend integration tests
│
├── frontend/                 # Next.js 16 App Router PWA (TypeScript)
│   ├── public/               # PWA manifests, icons, service worker (sw.js)
│   ├── src/
│   │   ├── app/              # 13 Prerendered static pages (Turbopack)
│   │   ├── components/       # Vernacular UI widgets, high-contrast controls
│   │   └── lib/              # OfflineQueue (IndexedDB), speech.ts, i18n
│   └── tests/                # 36 Node.js native test runner unit tests
│
├── ml/                       # Machine Learning Research & Inference Pipelines
│   ├── inference_service/    # Dedicated FastAPI microservice (port 8001)
│   │   ├── app/              # Model loaders, validators, schemas
│   │   └── tests/            # 7 Microservice automated tests
│   └── src/                  # PyTorch MobileNetV3 models, calibration, splits
│
└── docs/                     # Architectural Specifications, Runbooks & Audits
    ├── finalization/         # Production readiness monographs & stage audits
    └── stage-01 .. 14/       # Historical stage-by-stage documentation packages
```

---

### 2. Module Boundary & Import Integrity Verification

Both primary application gateways were inspected for circular imports, missing packages, and broken imports:

* **Backend Entrypoint:** `backend.app.main:app`
  * Command: `from backend.app.main import app`
  * Result: **Verified.** Loads cleanly as `ACREVIA API (1.0.0)`.
* **ML Microservice Entrypoint:** `ml.inference_service.app.main:app`
  * Command: `from ml.inference_service.app.main import app`
  * Result: **Verified.** Loads taxonomies for Cotton, Rice, Chilli cleanly as `KisanVision Dedicated ML Inference Service`.
* **Zero Cross-Layer Coupling:** The frontend communicates with the backend solely via REST contracts (`/api/v1`); it contains zero direct database dependencies.
