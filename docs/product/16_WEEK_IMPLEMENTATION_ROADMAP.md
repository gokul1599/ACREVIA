# KISANVISION — 16-WEEK IMPLEMENTATION ROADMAP

**Document Version:** 1.0.0  
**Status:** Approved for Stage 1 Baseline  
**Project Horizon:** 16 Weeks (4 Sprints of 4 Weeks each)  
**Methodology:** Spec-Driven Development (SDD) with strict quality, security, and agricultural verification gates  

---

## 1. Master Milestone Overview

```mermaid
gantt
    title KisanVision 16-Week Implementation Roadmap
    dateFormat  YYYY-MM-DD
    section S1: Foundation & ML
    W1-2: Research & Foundation         :done, m1, 2026-11-09, 14d
    W3-4: Dataset Prep & Baseline ML   :active, m2, after m1, 14d
    W5-6: Model Eval & Inference API   :m3, after m2, 14d
    section S2: Platform Core
    W7-8: Auth, Database & Storage    :m4, after m3, 14d
    W9-10: RAG Ingestion & Citations   :m5, after m4, 14d
    section S3: User Experience
    W11-12: PWA & Multilingual Voice   :m6, after m5, 14d
    W13-14: CropPulse & ExpertConnect  :m7, after m6, 14d
    section S4: Hardening & Launch
    W15-16: Validation, Security & Prod:m8, after m7, 14d
```

---

## 2. Detailed Milestone Specifications

### Milestone 1 (Weeks 1–2): Research, Governance & Foundation Scaffolding
- **Objective:** Establish the technical workspace, legal compliance guardrails, research registers, and repository foundations.
- **Tasks:**
  1. Scaffold `kisanvision` monorepo (`apps/web`, `apps/api`, `packages/ml`, `packages/rag`, `packages/database`).
  2. Pin CPython 3.11.16 virtual environment via Astral `uv` to overcome Python 3.14 wheel limitations.
  3. Formulate the official Cotton, Rice, and Chilli agricultural pathology register with PJTSAU citations.
  4. Build CIBRC chemical formulary baseline table with approved active ingredients and per-acre dosage limits.
  5. Provision Supabase project on AWS Mumbai (`ap-south-1`) with `pgvector` enabled.
- **Deliverables:** Verified monorepo structure, `.env.example`, initialized Git repo, base database migration scripts.
- **Dependencies:** Stage 1 Environment Audit & PRD approval.
- **Risks:** Delays in obtaining cloud API trial tokens; OneDrive file locking.
- **Acceptance Criteria:** `uv run pytest` executes cleanly; Supabase connection verified via SSL test script.
- **Exit Conditions:** All Stage 1 action items executed; development environment fully operational.

---

### Milestone 2 (Weeks 3–4): Dataset Ingestion & Baseline Machine Learning
- **Objective:** Curate, filter, and preprocess candidate datasets for Cotton, Rice, and Chilli; build baseline vision pipelines.
- **Tasks:**
  1. Ingest and deduplicate PlantVillage and PlantDoc image subsets for target crops.
  2. Implement OpenCV client-side quality filter (Laplacian blur detector, exposure check, leaf contour crop).
  3. Implement Albumentations pipeline simulating real-field conditions (direct tropical sunlight, shadows, blur, dust).
  4. Build PyTorch Dataset and DataLoader with Group-Stratified splitting to prevent farm-level data leakage.
  5. Train baseline MobileNetV3-Large classifier on cloud GPU (Google Colab / Kaggle).
- **Deliverables:** Versioned dataset manifests (DVC/JSON), image preprocessing module, initial trained PyTorch weights.
- **Dependencies:** Milestone 1 repo scaffolding.
- **Risks:** Imbalanced class distributions (e.g., thousands of healthy leaves vs. few rare false smut samples).
- **Acceptance Criteria:** Data loader verifies 0% overlap of farm IDs across train, val, and test splits.
- **Exit Conditions:** Baseline MobileNetV3 model converges without memory leaks.

---

### Milestone 3 (Weeks 5–6): Model Comparison, Quantization & Inference Engine
- **Objective:** Train and compare candidate vision architectures, quantize best models to INT8 ONNX, and build local inference engine.
- **Tasks:**
  1. Benchmark EfficientNet-B0 vs. MobileNetV3 vs. ResNet-18 across Macro F1, calibration (ECE), and parameter size.
  2. Implement Post-Training Dynamic INT8 Quantization using ONNX Runtime.
  3. Implement Softmax Entropy and Temperature Scaling for calibrated uncertainty estimation.
  4. Build Out-of-Distribution (OOD) detector to reject non-plant images.
  5. Build FastAPI `/api/v1/vision/predict` endpoint serving ONNX models on local AMD Ryzen CPU.
- **Deliverables:** Quantized ONNX model files (<15 MB), model evaluation report with confusion matrices, local inference service.
- **Dependencies:** Milestone 2 dataset preparation.
- **Risks:** Quantization causing excessive accuracy drop (>2% Macro F1 drop).
- **Acceptance Criteria:** Local CPU inference latency strictly under 200ms per image on host machine.
- **Exit Conditions:** Model Evaluation Dashboard displays validated metrics for production candidate.

---

### Milestone 4 (Weeks 7–8): Authentication, Database, Backend & Storage
- **Objective:** Deploy production PostgreSQL relational schema, object storage integration, and role-based authentication.
- **Tasks:**
  1. Execute SQLAlchemy / Alembic migrations for all 32 core database entities.
  2. Implement phone-based OTP authentication for farmers and email/MFA for agronomists/admins.
  3. Implement S3-compatible private object storage client for encrypted leaf photographs.
  4. Implement Farm, Plot, and Crop Season CRUD APIs with strict tenant isolation.
  5. Implement append-only Audit Logging and DPDPA consent tracking middleware.
- **Deliverables:** Production REST API (`/api/v1/auth`, `/api/v1/farms`, `/api/v1/plots`), automated database migrations.
- **Dependencies:** Milestone 3 inference service.
- **Risks:** Misconfigured RLS leaking cross-tenant farm records.
- **Acceptance Criteria:** 100% of farm endpoints enforce tenant boundaries; unauthenticated requests rejected with 401.
- **Exit Conditions:** Automated security integration tests pass with zero authorization bypasses.

---

### Milestone 5 (Weeks 9–10): KrishiBrain RAG Ingestion, Retrieval & Citations
- **Objective:** Implement grounded agricultural retrieval system with CIBRC safety guardrails and multi-provider LLM abstraction.
- **Tasks:**
  1. Ingest PJTSAU Vyavasaya Panchangam and ICAR handbooks; chunk into semantic markdown passages (500 tokens).
  2. Generate 384-dimensional dense embeddings using local Sentence Transformers; index into `pgvector` with HNSW.
  3. Build hybrid retrieval engine combining vector similarity (cosine) with BM25 keyword matching for Telugu terms.
  4. Build the CIBRC Chemical Safety Filter: strictly enforce approved pesticide dosages and statutory pre-harvest intervals.
  5. Integrate Groq (Llama 3.3 70B) and Google Gemini 1.5 Flash behind the `ILLMProviderAdapter`.
- **Deliverables:** KrishiBrain RAG service, CIBRC verification engine, populated vector knowledge base.
- **Dependencies:** Milestone 4 database and storage setup.
- **Risks:** LLM hallucinating unapproved tank mixtures; mitigation via strict regex and SQL validation.
- **Acceptance Criteria:** 100% of generated chemical advisories cite verified PJTSAU/CIBRC documents; 0 unapproved chemicals output.
- **Exit Conditions:** RAG retrieval returns grounded context with latency < 1.5 seconds.

---

### Milestone 6 (Weeks 11–12): Farmer Frontend, PWA & Multilingual Voice Experience
- **Objective:** Build responsive Next.js Progressive Web App with Telugu, Hindi, and English support and native voice AI.
- **Tasks:**
  1. Build mobile-first PWA UI using Next.js 14/15 App Router, Tailwind CSS, and shadcn/ui.
  2. Implement camera capture interface with real-time blur and lighting guidance overlays.
  3. Integrate Sarvam AI for Telugu/Hindi Speech-to-Text (`saaras`) and Text-to-Speech (`bulbul`).
  4. Implement offline Service Worker caching for historical diagnosis cards and emergency agronomy guides.
  5. Implement vernacular terminology toggle (Telugu, Hindi, English).
- **Deliverables:** Complete Next.js PWA web app, service worker offline bundle, voice interaction module.
- **Dependencies:** Milestones 3, 4, and 5 APIs.
- **Risks:** Slow audio synthesis over 3G rural mobile networks; mitigation via client audio streaming.
- **Acceptance Criteria:** First Contentful Paint (FCP) < 1.2s; voice query round-trip < 2.5s on 4G.
- **Exit Conditions:** Farmers can complete full photo capture, voice query, and hear spoken Telugu advice end-to-end.

---

### Milestone 7 (Weeks 13–14): CropPulse, Weather Context & ExpertConnect
- **Objective:** Implement longitudinal plant health tracking, micro-climate risk indicators, and human-in-the-loop expert review.
- **Tasks:**
  1. Build Open-Meteo weather adapter; compute 7-day hourly spray safety index and disease risk scores.
  2. Implement CropPulse plot timeline visualizing sequential photo observations and recovery post-spray.
  3. Build ExpertConnect web review portal for agricultural extension officers with zoomable leaf viewer and triage queue.
  4. Implement automated notification dispatch (SMS/Push) alerting farmers when experts review their diagnostic records.
  5. Build Farm Intelligence Dashboard aggregating plot health, weather warnings, and operations.
- **Deliverables:** CropPulse visual timeline, RiskCast weather service, ExpertConnect agronomist portal.
- **Dependencies:** Milestone 6 frontend and Milestone 4 database.
- **Risks:** Expert review queue backlog during peak pest seasons; mitigation via urgency prioritization algorithms.
- **Acceptance Criteria:** Weather risk index updates hourly; expert override updates farmer diagnosis immediately.
- **Exit Conditions:** Asynchronous escalation workflow operates reliably end-to-end.

---

### Milestone 8 (Weeks 15–16): Hardening, Security, Field Validation & Deployment
- **Objective:** Conduct security audits, agronomic validation trials with local extension agents, load testing, and production deployment.
- **Tasks:**
  1. Perform penetration testing, OWASP Top 10 API audit, and DPDPA data privacy compliance review.
  2. Conduct stress and load testing on FastAPI endpoints under simulated multi-user traffic.
  3. Execute double-blind agronomic validation trial on 300 real Telangana field photographs with university agronomists.
  4. Finalize production Docker packaging and CI/CD pipelines with automated smoke testing.
  5. Conduct user acceptance testing (UAT) with real farmers in Warangal and Nalgonda districts.
- **Deliverables:** Production deployment bundle, Stage 1 to Stage 4 verification audit reports, user manuals in Telugu and English.
- **Dependencies:** All previous milestones completed.
- **Risks:** High false-positive rate on emerging local pest strains; handled via expert review fallback.
- **Acceptance Criteria:** Zero critical vulnerabilities; 99.5% uptime SLA during simulated load tests.
- **Exit Conditions:** Formal sign-off by agricultural and engineering leads for general availability.
