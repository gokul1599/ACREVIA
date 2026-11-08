# ACREVIA — Stage 7 Entry Gate Readiness Audit
## RiskCast, ExpertConnect & Intervention Outcome Tracking

---

## 1. Executive Summary

- **Product:** ACREVIA — Agricultural Intelligence Platform.
- **Stage:** 07 (Weeks 13–14).
- **Audit Date:** 2026-11-08.
- **Auditor:** Agricultural Systems Architecture & Backend Engineering Team.
- **Target Geography:** Telangana, India (Warangal, Karimnagar, Khammam, Nalgonda, Adilabad, Mahabubnagar).
- **Target Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*).
- **Core Languages:** Telugu (తెలుగు), English, Hindi (हिन्दी).
- **Entry Gate Status:** **PASSED / READY FOR STAGE 7 EXECUTION**.

---

## 2. Upstream Dependency Verification

| Upstream Dependency | Verification Scope | Status | Notes |
|:---|:---|:---|:---|
| **Stage 1 & 2 Taxonomy** | Cotton, Rice, Chilli condition classes & phenology | **VERIFIED** | 18 condition classes defined; phenological growth stages catalogued. |
| **Stage 3 Computer Vision** | Calibrated inference, uncertainty metrics, ONNX export | **VERIFIED** | MobileNetV3 backbones calibrated with temperature scaling; 8 agricultural decision states implemented. |
| **Stage 4 Backend Foundation** | FastAPI app, JWT authentication, Farm/Plot multi-tenant RBAC | **VERIFIED** | Database schema in PostgreSQL/SQLite; `verify_farm_access` protects all tenant data boundaries. |
| **Stage 5 KrishiBrain RAG** | Ingestion pipeline, pgvector / local embeddings, CIBRC guardrails | **VERIFIED** | 45-case gold evaluation suite passed; evidence chunking & citation retrieval operational. |
| **Stage 6 Farmer PWA** | Next.js 16 App Router, offline queue, Web Speech voice adapter | **VERIFIED** | 11 statically compiled routes; full Telugu/English/Hindi translations; responsive mobile-first UI. |

---

## 3. Stage 7 Architectural Scope & Boundary Enforcement

### 3.1 Pillar A: RiskCast (Climate & Crop Risk Intelligence)
1. **Weather Observations vs. Forecasts:**
   - Observations reflect measured ground/satellite agrometeorological conditions up to the current hour.
   - Forecasts represent forward-looking probability projections across 1 to 7 day horizons.
   - The system must explicitly label observation timestamps versus forecast target horizons.
2. **Predisposition vs. Disease Outbreak Safeguard:**
   - Under no circumstances shall high humidity, ambient temperature, or rainfall be reported as a "confirmed disease outbreak".
   - RiskCast outputs qualified environmental risk indicators: `LOW`, `MODERATE`, `HIGH`, or `INSUFFICIENT_DATA`.
   - Every assessment carries an explicit scientific disclaimer: *"High environmental risk denotes favorable climatic conditions for pathogen proliferation, not confirmed biological infection. Physical scouting required."*

### 3.2 Pillar B: ExpertConnect (Agricultural Expert Review Network)
1. **Expert Governance & Credentialing:**
   - Agricultural experts must undergo formal verification: `APPLICATION_SUBMITTED` -> `UNDER_REVIEW` -> `APPROVED` -> `SUSPENDED` -> `REVOKED`.
   - Admin approval is mandatory before any user can claim cases or issue certified agronomist opinions.
2. **Review Case Dossier:**
   - Cases link CropPulse observations, foliar images, AI vision predictions (with entropy and calibrated probabilities), and KrishiBrain knowledge citations.
   - Expert assessments are immutable once committed; subsequent revisions require a structured revision record (`ExpertAssessmentRevision`) documenting the rationale and author.
3. **AI Decoupling:**
   - AI outputs are strictly decision-support aids for the human expert.
   - Expert assessments are stored separately and do not automatically mutate ML model weights without an audited clinical validation cycle.

### 3.3 Pillar C: Intervention Intelligence & Outcome Tracking
1. **Actionable Farm Journal:**
   - Structured logs for biological, chemical, cultural, irrigation, and fertilizer actions.
   - Strict tracking of Pre-Harvest Intervals (PHI) and Re-Entry Intervals (REI) aligned with CIBRC pesticide standards.
2. **Outcome Observation & Causality Protection:**
   - Subsequent CropPulse observations evaluate status changes: `IMPROVING`, `STABLE`, `WORSENING`, `INCONCLUSIVE`.
   - The platform strictly enforces that visual changes do not constitute proof of causal cure, recording confounding factors (rainfall, thermal stress, untracked soil dynamics).

---

## 4. Technical Environment & Regional Alignment

- **Database:** Neon Serverless PostgreSQL with `pgvector` extension; SQLite fallback for isolated unit testing.
- **Compute:** FastAPI backend running on Python 3.11; Next.js frontend deployed on Vercel Singapore (`sin1`) for minimal latency to Telangana users.
- **Test Baseline:** 97 backend/ML tests and 9 frontend tests passing prior to Stage 7 execution.
- **Security Protocols:** JWT authentication, role-based authorization (`FARMER`, `AGRICULTURAL_EXPERT`, `RESEARCHER`, `ADMIN`), cryptographic media hashing (SHA-256).

---

## 5. Entry Gate Conclusion

All prerequisites for ACREVIA Stage 7 are satisfied. The engineering team has established strict domain boundaries, safety disclaimers, and data isolation controls to proceed with implementing RiskCast, ExpertConnect, and Intervention Intelligence.
