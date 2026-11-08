# ACREVIA — SYSTEM ARCHITECTURE VERIFICATION
## End-to-End Architectural Inspection, Boundaries, Data Ownership & Contract Verification

**System:** ACREVIA — Agricultural Intelligence Platform  
**Architecture Style:** Modular Clean Architecture (Layered Domain Services + FastAPI + Next.js PWA + Neon pgvector)  
**Verification Date:** November 2026  
**Status:** VERIFIED & HARDENED  

---

## 1. Verified High-Level System Architecture

The implemented ACREVIA production architecture connects a mobile-first multilingual frontend with an enterprise FastAPI gateway, backed by Neon PostgreSQL, an optimized PyTorch/ONNX ML microservice, and a hybrid vector search engine.

```text
               +-------------------------------------------------------+
               |                  ACREVIA FARMER PWA                   |
               |       Next.js 14 App Router (Telugu / English / Hindi) |
               |     Service Worker Shell + IndexedDB Offline Queue    |
               +---------------------------+---------------------------+
                                           |  HTTPS / TLS 1.3
                                           |  Bearer JWT Authentication
                                           v
               +-------------------------------------------------------+
               |                 FASTAPI API GATEWAY                   |
               |   Correlation Tracking | OWASP Headers | Rate Limiter  |
               +---------------------------+---------------------------+
                                           |
         +-----------------+---------------+-----------------+-----------------+
         |                 |                                 |                 |
         v                 v                                 v                 v
+-----------------+ +-------------------------------+ +-------------+ +-----------------+
|   FARM & CROP   | |     CROPVISION CV SERVICE     | |  RISKCAST   | |  EXPERTCONNECT  |
|     SERVICE     | | MobileNetV3 Large/Small Heads | | WEATHER &   | | Clinical Triage |
| Plots, Seasons, | | OOD Detection (Mahalanobis)   | | RULE ENGINE | | Multimodal      |
| Phenology, Auth | | Quality Gate (Blur/Exposure)  | | Open-Meteo  | | Dossiers        |
| Multi-tenant DB | | Abstention / Uncertainty Gate | | PJTSAU Norms| | Revisions Audit |
+--------+--------+ +---------------+---------------+ +------+------+ +--------+--------+
         |                          |                      |                   |
         |                          v                      |                   |
         |         +--------------------------------+      |                   |
         |         |         KRISHIBRAIN            |      |                   |
         |         |  pgvector Hybrid Search (1536d)|      |                   |
         |         |  PJTSAU/ICAR Grounded Citations|      |                   |
         |         +----------------+---------------+      |                   |
         |                          |                      |                   |
         v                          v                      v                   v
+--------------------------------------------------------------------------------------+
|                                NEON POSTGRESQL + PGVECTOR                            |
|             32 Relational Entities | Connection Pooling (10+20) | Pre-ping           |
+--------------------------------------------------------------------------------------+
```

---

## 2. Integration Boundary Verification

### 2.1 Frontend to Backend Authorized Boundary
- **Communication Protocol:** JSON over HTTPS with strict CORS origins (`http://localhost:3000`, `http://localhost:8000`, and authorized production domains).
- **Security Headers:** Injected by FastAPI middleware and verified by Next.js `next.config.mjs`:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: camera=(self), microphone=(self), geolocation=()`
- **Identity & Session Propagation:** All requests outside public registration/login require `Authorization: Bearer <jwt_token>` carrying user UUID, phone number, and assigned roles (`FARMER`, `AGRICULTURAL_EXPERT`, `ADMIN`).
- **Telemetry & Tracing:** Gateway injects unique `X-Correlation-ID` and logs response latency in `X-Response-Time-Ms`.

### 2.2 CropVision Inference Boundary
- **Contract Schema:** `POST /api/v1/diagnoses/` takes `observation_id`, `media_id`, `crop_type`, and `language`.
- **Pre-inference Gate:** Image is validated for format (JPEG/PNG/WebP), size ($\le 10$ MB), blurriness (Laplacian variance $\ge 100$), and exposure ($30 \le \text{mean luminance} \le 225$).
- **Inference Execution:** High-res image is resized to $224 \times 224$, normalized with ImageNet stats, and evaluated through the crop-specific classification head.
- **Uncertainty Gate:** If top-1 confidence is $< 0.65$ or top-2 margin is $\le 0.15$, the diagnosis status is flagged as `NEEDS_REVIEW` and routed to the ExpertConnect triage queue with an explanation.

### 2.3 KrishiBrain Knowledge Retrieval Boundary
- **Embedding Alignment:** 1536-dimensional cosine distance vector embeddings stored in Neon pgvector.
- **Query Processing:** Incoming questions in Telugu, English, or Hindi are parsed; the detected language is matched with agricultural taxonomy keywords, filtering out chunks belonging to other crops.
- **Grounded Attribution:** Output answers include explicit citations referencing the registered publication source, publisher name, section title, and verbatim excerpt.

### 2.4 RiskCast Agrometeorological Boundary
- **Provider Isolation:** Weather data is consumed via `weather_service.py` from Open-Meteo, separating measured historical observations from forward-looking forecast horizons.
- **Fallback Guarantee:** When external APIs fail or timeout, the engine automatically draws on 30-year district climate normals published by PJTSAU with an explicit data source annotation.
- **Non-Causal Disclaimer:** All risk assessments and alerts must include the mandatory agronomic disclaimer: *"High environmental risk denotes favorable climatic conditions for pathogen proliferation, NOT confirmed disease outbreak. Physical scouting required."*

### 2.5 ExpertConnect Governance Boundary
- **RBAC Enforcement:** Expert review cases can only be claimed, reviewed, and finalized by users holding the `AGRICULTURAL_EXPERT` role who have an `APPROVED` `ExpertProfile`.
- **Dossier Completeness:** Agronomists inspect comprehensive clinical packages consisting of foliar photographs, CropVision ML confidence scores, KrishiBrain reference documents, and micro-climate history.
- **Immutability Contract:** Submitted assessments are locked against in-place overwrites. Modifications must be committed as `ExpertAssessmentRevision` records with prior state snapshots and clinical justification.

### 2.6 Intervention & CropPulse Tracking Boundary
- **Intervention Recording:** Logs farm interventions across 5 categories (`BIOLOGICAL`, `CHEMICAL`, `CULTURAL`, `IRRIGATION`, `FERTILIZER`) with trade names, dosages, application dates, PHI, and REI.
- **Observation Linkage:** Follow-up CropPulse observations evaluate condition progression (`IMPROVING`, `STABLE`, `WORSENING`, `INCONCLUSIVE`).
- **Causality Protection:** Emits the mandatory confounding factors notice stating that open-field environmental dynamics, rainfall, and unmonitored pest reservoirs prevent attributing visual changes to single-cause interventions.

---

## 3. Database Schema & Data Ownership Integrity

All 32 database models preserve foreign-key relational integrity, multi-tenant isolation, and cascade policies:

| Parent Entity | Child Entity | Relationship Type | Cascading Behavior | Multi-Tenant Enforcement |
|---|---|---|---|---|
| `User` | `FarmMembership` | One-to-Many | CASCADE on User delete | User must be OWNER or MEMBER |
| `Farm` | `Plot` | One-to-Many | CASCADE on Farm delete | Plot queries enforce `farm.owner_id == user.id` |
| `Plot` | `CropSeason` | One-to-Many | CASCADE on Plot delete | Verified via Plot & Farm ownership chain |
| `Plot` | `Observation` | One-to-Many | SET NULL on Plot delete | Observation access requires Farm membership |
| `Observation` | `ObservationMedia` | One-to-Many | CASCADE on Observation delete | Files stored privately with SHA-256 hash |
| `Observation` | `DiagnosisRequest` | One-to-One | CASCADE on Observation delete | Tied to requesting farmer |
| `DiagnosisRequest` | `Prediction` | One-to-One | CASCADE on Diagnosis delete | Immutable inference snapshot |
| `DiagnosisRequest` | `PredictionCandidate`| One-to-Many | CASCADE on Prediction delete | Top-K candidate distribution |
| `Observation` | `ExpertReviewCase` | One-to-One | RESTRICT on Observation delete | Case lifecycle tracked independently |
| `ExpertReviewCase` | `ExpertAssessment` | One-to-One | RESTRICT on Case delete | Certified permanent finding |
| `ExpertAssessment` | `ExpertAssessmentRevision`| One-to-Many| RESTRICT on Assessment delete | Versioned audit log of all clinical edits |
| `Plot` | `InterventionRecord` | One-to-Many | CASCADE on Plot delete | Tied to plot crop cycle |
| `InterventionRecord`| `OutcomeObservation`| One-to-Many | CASCADE on Intervention delete| Links follow-up observation with status |

---

## 4. Architectural Verification Summary

The architectural verification confirms that:
1. No unauthenticated API routes expose private farmer data.
2. No ML inferences are forced when image quality or confidence is inadequate.
3. No agricultural advice is generated without grounded publication citations.
4. No weather risks are presented as confirmed biological disease outbreaks.
5. All 32 database tables adhere to 3rd Normal Form with proper foreign keys and indexes.

**Architecture Verification Verdict:** **VERIFIED — PRODUCTION GRADE & SECURE.**
