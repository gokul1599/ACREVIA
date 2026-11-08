# KISANVISION — PRODUCT REQUIREMENTS DOCUMENT (PRD)

**Document Version:** 1.0.0  
**Status:** Approved for Stage 1 Baseline  
**Target Region:** Telangana, India (Initial), with scalable Indian agro-climatic zone support  
**Target Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*)  
**Target Languages:** Telugu (తెలుగు), English, Hindi (हिन्दी)  
**Author:** Principal Software Architect, Senior AI/ML Research Engineer, Agricultural Technology Researcher, Product Manager  

---

## 1. Executive Summary & Vision

KisanVision is a research-grade, evidence-based agricultural intelligence platform engineered to bridge the critical gap between frontier multimodal artificial intelligence and smallholder farm operations in Telangana, India. Unlike simplistic consumer chatbot wrappers, KisanVision combines:
1. **Calibrated Computer Vision:** Dual-stage edge/cloud computer vision models trained specifically on localized field pathology (including leaf background noise, direct sunlight, and multi-symptom co-infections).
2. **Context-Grounded RAG (KrishiBrain):** Grounded agricultural retrieval against certified agronomical packages of practices (PJTSAU, ICAR-IIRR, ICAR-CICR) and chemical label guidelines (CIBRC).
3. **Multilingual Voice-First Interaction (KisanSaathi):** Native Telugu, Hindi, and English voice interaction tuned to agricultural vernacular and local crop stage terminology.
4. **Human-in-the-Loop Expert Escalation (ExpertConnect):** A safety-critical verification workflow routing ambiguous or severe anomalies to accredited agronomists.

---

## 2. Target User Groups & Personas

### 2.1 Persona 1: Smallholder & Tenant Farmer (Primary End-User)
- **Profile:** Cultivates 1.5 to 5 acres of cotton, paddy (rice), or chilli in districts like Warangal, Khammam, Nalgonda, or Karimnagar.
- **Literacy & Technical Profile:** High comfort with smartphone touch interfaces and voice notes (WhatsApp/YouTube); moderate to low literacy in formal English or complex technical Telugu; prefers spoken Telugu or vernacular terminology (e.g., *Gulaabi purugu* for pink bollworm, *Aggi tegulu* for blast, *Nalla thaamara* for black thrips).
- **Core Needs:** Rapid leaf diagnosis, exact chemical/organic remedies with verified dosages per acre/tank (*pichikari can*), local weather warnings before spraying, audio explanations.

### 2.2 Persona 2: Agricultural Extension Officer / KVK Scientist / Agronomist (Expert Reviewer)
- **Profile:** Officers at Rythu Vedika, Krishi Vigyan Kendra (KVK), or state agricultural departments overseeing hundreds of village clusters.
- **Technical Profile:** Uses desktop or tablet; requires rapid triage queues, high-resolution original image inspection, symptom heatmaps, confidence score breakdowns, and one-click feedback/advisory issuance.
- **Core Needs:** Filter unconfirmed or high-risk AI predictions, review field telemetry, prevent localized pest epidemics (e.g., *Thrips parvispinus* outbreaks), and dispatch broadcast advisories.

### 2.3 Persona 3: Agricultural Research Engineer & Data Scientist (Internal/Partner)
- **Profile:** Agronomic and ML researchers tracking crop pathology, climate correlations, model drift, and dataset quality.
- **Technical Profile:** Technical dashboard user requiring access to model metrics (Macro F1, confusion matrices, calibration curves, OOD flags), confusion logs, dataset provenance, and annotation exports.
- **Core Needs:** Audit model performance across varieties, download de-identified field image splits, and benchmark new quantized backbones.

### 2.4 Persona 4: Platform Administrator & Security Officer (Operations)
- **Profile:** DevOps and compliance engineers maintaining system availability, tenant isolation, DPDPA 2023 compliance, API rate budgets, and audit logging.
- **Core Needs:** Role-based access control (RBAC), API quota monitoring (Groq, Gemini, Sarvam AI), database backup status, and security audit log inspection.

---

## 3. Core Real-World User Problems Solved

1. **Diagnostic Latency & Misdiagnosis:** Smallholders rely on local agri-input retailers who frequently misidentify viral vs. fungal infections (e.g., mistaking invasive *Thrips parvispinus* rasping damage for chilli leaf curl virus) and sell unnecessary, expensive, and ineffective broad-spectrum chemicals.
2. **Indiscriminate Chemical Overuse & Pest Resistance:** Spraying incorrect dosages or unapproved chemical cocktails (*tank mixtures*) destroys beneficial natural predators, accelerates pesticide resistance (e.g., pink bollworm in Bt cotton), causes chemical leaf burn, and drives farmers into debt cycles.
3. **Climate-Triggered Disease Surges:** Rapid micro-climatic shifts (e.g., sudden cyclonic unseasonal rains during Telangana's Kharif season) cause instant sporulation of rice blast or cotton root rot. Farmers lack predictive risk indicators synchronized with their specific sowing dates.
4. **Language & Dialect Barriers:** High-quality research papers and university bulletins published in formal technical English or high academic Telugu fail to reach rural farmers who require conversational audio in their local dialect.
5. **Absence of Longitudinal Plot History:** Farmers cannot track disease recurrence across seasons, soil test history, or which variety proved resistant in their specific soil type, leading to repetitive management failures.
6. **Severe Agronomist-to-Farmer Deficit:** With over 6 million operational farm holdings in Telangana and an extension ratio exceeding 1:1,500, physical access to university scientists during peak pest surges is impossible.

---

## 4. Comprehensive Product Modules (15 Modules)

### Module 1: CropVision — Plant Image Intelligence
- **Objective:** Ingest field photographs of cotton, rice, and chilli foliage, validate visual quality, and predict primary and secondary pathologies with calibrated uncertainty.
- **Target User:** Farmers, Agricultural Extension Officers.
- **Inputs:** Raw smartphone camera image or gallery upload (JPEG/PNG/WebP, up to 15 MB), crop type (or auto-detected), plant organ (leaf, stem, fruit, boll).
- **Processing:**
  1. Quality Guard: Blur detection (Laplacian variance), illumination range check (HSV histogram), background dominance check (OpenCV GrabCut/contouring).
  2. Crop & Organ Verification: Validates that the subject is cotton/rice/chilli foliage.
  3. Multi-head Inference: Dual-head ONNX classifier (primary condition + symptom severity index).
  4. Uncertainty & Calibration: Softmax entropy + temperature scaling. Flags Out-Of-Distribution (OOD) when top-class probability < 0.70 or entropy > threshold.
  5. Multimodal Fallback: When confidence is ambiguous, triggers Gemini 1.5 Flash visual reasoning pipeline with structured JSON schema.
- **Outputs:** Primary condition name (vernacular + scientific), confidence level (High/Medium/Low), visual bounding box/heat-map of necrotic lesions, image quality score, OOD flag.
- **Dependencies:** OpenCV, ONNX Runtime (CPU), Gemini 1.5 Flash API (cloud fallback), PyTorch/torchvision (model training/export).
- **Error States:** `BLURRY_IMAGE`, `INSUFFICIENT_LIGHTING`, `NON_CROP_DETECTED`, `UNSUPPORTED_ORGAN`, `SERVER_OVERLOAD`.
- **Privacy Requirements:** Strip EXIF metadata (except creation timestamp and optional farm-linked GPS if consented); isolate raw files in private object storage.
- **Acceptance Criteria:**
  - Image quality assessment completes in <100ms.
  - End-to-end CPU inference on host environment completes in <350ms.
  - Zero crashes when given non-plant images (must cleanly trigger `NON_CROP_DETECTED`).
- **MVP Priority:** **P0**

---

### Module 2: AgroContext — Farm & Crop Context
- **Objective:** Collect and manage spatial, temporal, and varietal context for every farm plot to condition all diagnostic and risk algorithms.
- **Target User:** Farmers, Extension Officers.
- **Inputs:** Farm location (Mandal, District, Geo-coordinates), plot acreage, soil type (Black cotton soil / Regur, Red chalka, Sandy loam), crop variety (e.g., Bt-II Cotton hybrid, BPT-5204 Samba Mahsuri Rice, Teja Chilli), sowing/transplanting date, irrigation source (Borewell, Canal, Drip, Rainfed).
- **Processing:** Calculates Current Crop Growth Stage (e.g., Rice: Tillering, Panicle Initiation, Flowering, Grain Filling) based on thermal time / Growing Degree Days (GDD) and calendar delta from sowing date.
- **Outputs:** Context payload: `{mandal_id, crop_stage_enum, soil_type, irrigation_type, days_after_sowing}`.
- **Dependencies:** Database (PostgreSQL).
- **Error States:** `INVALID_COORDINATES`, `FUTURE_SOWING_DATE`, `UNKNOWN_VARIETY`.
- **Privacy Requirements:** Strict multi-tenant isolation; precise GPS coordinates masked to 1 km² mandal centroid unless farmer explicitly consents to geo-referenced survey mapping.
- **Acceptance Criteria:** Sowing date calculation accurately maps to PJTSAU growth stages across Kharif and Rabi calendars.
- **MVP Priority:** **P0**

---

### Module 3: KrishiBrain — Agricultural Knowledge & RAG Engine
- **Objective:** Deliver evidence-grounded, peer-reviewed agronomic management recommendations dynamically retrieved from verified university literature.
- **Target User:** Farmers, Agronomists.
- **Inputs:** Query vector (from diagnostic result + user question + crop context), user language (Telugu/English/Hindi).
- **Processing:**
  1. Dense semantic retrieval from `pgvector` knowledge base (PJTSAU Vyavasaya Panchangam, ICAR manuals).
  2. Sparse keyword re-ranking (BM25) for chemical active ingredients and vernacular pest names.
  3. CIBRC Chemical Safety Guardrail: Filters recommendations through an in-memory SQL rules table of approved chemical formulations and dosage limits.
  4. Context-stuffed LLM prompt passed to Groq (Llama 3.3 70B) or Gemini 1.5 Flash.
- **Outputs:** Structured advisory: Cultural control, biological remedy, verified chemical formulation with exact per-acre water/chemical dosage (*e.g., Chlorantraniliprole 18.5% SC @ 60 ml/acre in 200 L water*), spray precautions, safety intervals (waiting period before harvest), and authoritative document citations.
- **Dependencies:** PostgreSQL + `pgvector`, Groq API / Gemini API, CIBRC Formulary Database.
- **Error States:** `RETRIEVAL_NO_MATCH`, `UNAPPROVED_CHEMICAL_ATTEMPT`, `LLM_TIMEOUT`.
- **Privacy Requirements:** No farmer personal identifiers passed in external LLM prompts.
- **Acceptance Criteria:** Every chemical recommendation includes exact citation to a PJTSAU/CIBRC source document; 0% hallucinated chemical names.
- **MVP Priority:** **P0**

---

### Module 4: RiskCast — Weather & Contextual Risk Indicators
- **Objective:** Continuously evaluate micro-climatic parameters to predict upcoming disease outbreaks and calculate optimal spraying windows.
- **Target User:** Farmers, Extension Officers.
- **Inputs:** Mandal centroid coordinates, 7-day hourly forecast from Open-Meteo (Relative Humidity, Ambient Temp, Wind Speed, Precipitation probability, Leaf wetness duration).
- **Processing:**
  - Evaluates epidemiological rule models (e.g., Rice Blast: RH > 90% + Temp 20–26°C for >12 consecutive hours; Chilli Anthracnose: Rain splash + RH > 80% + Temp > 28°C).
  - Evaluates Spray Window Safety: Wind speed < 15 km/h, rain probability < 20% in next 6 hours, no peak midday sun (>35°C).
- **Outputs:** Outbreak Risk Score (Low/Moderate/Severe) for top 3 diseases, Spray Advisory Badge (Safe to Spray / Do Not Spray / Rain Risk in 3h).
- **Dependencies:** Open-Meteo API, AgroContext module.
- **Error States:** `WEATHER_API_UNAVAILABLE`, `LOCATION_OUT_OF_BOUNDS`.
- **Privacy Requirements:** Weather calls use district/mandal centroids; no private user metadata shared.
- **Acceptance Criteria:** Weather data cached with 3-hour TTL; spray safety index updates hourly.
- **MVP Priority:** **P1**

---

### Module 5: KisanSaathi — Multilingual Voice AI Assistant
- **Objective:** Provide a frictionless, conversational voice and text assistant in Telugu, Hindi, and English to answer farmer inquiries regarding farm operations and diagnoses.
- **Target User:** Farmers.
- **Inputs:** Recorded farmer voice note (WAV/MP3/Opus), text prompt, session history, active diagnostic report ID.
- **Processing:**
  1. Speech-to-Text: Sarvam AI `saaras:v1` (Telugu/Hindi audio to text).
  2. Query Orchestration: Intent classification via FastAPI -> routes to KrishiBrain RAG or weather service.
  3. Synthesis: Generates natural language response constrained to agricultural facts.
  4. Text-to-Speech: Sarvam AI `bulbul:v1` (Telugu/Hindi natural audio generation).
- **Outputs:** Spoken audio stream (Telugu voice output) + readable vernacular transcript with formatted bullet points.
- **Dependencies:** Sarvam AI API, Groq / Gemini API, KrishiBrain module.
- **Error States:** `AUDIO_UNINTELLIGIBLE`, `LANGUAGE_UNSUPPORTED`, `STT_SERVICE_DOWN`.
- **Privacy Requirements:** Audio recordings retained only upon explicit consent; zero training without consent.
- **Acceptance Criteria:** Round-trip latency (audio in -> audio out) < 2.5 seconds on 4G network.
- **MVP Priority:** **P0**

---

### Module 6: ExpertConnect — Expert Review System
- **Objective:** Provide an asynchronous human-in-the-loop review pipeline where university scientists and extension officers validate, correct, or refine AI predictions.
- **Target User:** Agricultural Extension Officers, Scientists, Farmers.
- **Inputs:** Triage-flagged diagnosis requests (OOD cases, low-confidence scores, rare symptoms, farmer dispute requests).
- **Processing:**
  - Worklist queuing with priority weighting (severe epidemic risk prioritized).
  - Web-based review interface with zoomable multi-spectral/RGB imagery, crop context, and AI diagnostic proposal.
  - One-click confirmation, diagnostic override, or custom voice/text advisory attachment.
  - Automated notification dispatch back to the farmer.
- **Outputs:** Certified Expert Review Record, farmer notification (SMS/Push/In-app), verified dataset candidate record for future model fine-tuning.
- **Dependencies:** Supabase Database, Storage, Notification service.
- **Error States:** `EXPERT_TIMEOUT_EXCEEDED`, `IMAGE_CORRUPTED`.
- **Privacy Requirements:** Farmer personal contact hidden from general reviewer list; visible only to authorized local Mandal extension officers.
- **Acceptance Criteria:** Review queue updates in real-time; farmer receives alert immediately upon expert submission.
- **MVP Priority:** **P1**

---

### Module 7: CropPulse — Plant Health Timeline
- **Objective:** Provide a longitudinal visual health ledger for every registered farm plot across the seasonal crop cycle.
- **Target User:** Farmers, Extension Officers, Researchers.
- **Inputs:** Sequential photo observations, logged interventions (sprays/fertilizers), weather events.
- **Processing:** Aggregates health trajectory, visualizes recovery progression post-intervention, and computes recovery index.
- **Outputs:** Interactive visual timeline card showing chronological photo cards, severity progression graph (e.g., 60% necrosis -> 15% necrosis post-spray), and milestone flags.
- **Dependencies:** Database (Observations, Plots, Interventions).
- **Error States:** `NO_OBSERVATIONS_LOGGED`, `SEASON_EXPIRED`.
- **Privacy Requirements:** Bound to farmer account and plot authorization.
- **Acceptance Criteria:** Renders responsive chronological scroll of plot history with smooth thumbnail loading.
- **MVP Priority:** **P1**

---

### Module 8: Farm Intelligence Dashboard
- **Objective:** Aggregated executive overview for farmers and regional administrators displaying real-time farm condition, pending actions, and localized threat bulletins.
- **Target User:** Farmers, Village Panchayat Heads, Extension Officers.
- **Inputs:** User farm records, regional outbreak alerts, current weather feed.
- **Processing:** Consolidates active plot statuses, next scheduled spray/irrigation task, and regional threat radar into a unified card view.
- **Outputs:** Responsive dashboard overview with KPI cards: Active Plots, Current Health Status, Today's Spray Safety Window, Regional Alerts.
- **Dependencies:** AgroContext, RiskCast, CropPulse.
- **Error States:** `DATA_SYNC_FAILED`.
- **Privacy Requirements:** Role-based data aggregation; village-level views show de-identified counts only.
- **Acceptance Criteria:** First Contentful Paint (FCP) < 1.2s on mobile connections.
- **MVP Priority:** **P1**

---

### Module 9: Crop Lifecycle & Season Management
- **Objective:** Structured tracking of seasonal timelines (Kharif, Rabi, Zaid) from land preparation to harvest.
- **Target User:** Farmers.
- **Inputs:** Season start date, crop variety, seed treatment details, target harvest window.
- **Processing:** Automated calculation of seasonal milestones according to standard PJTSAU crop development schedules.
- **Outputs:** Calendar milestones: Basal fertilizer application date, weeding schedule, critical irrigation stages (e.g., rice panicle initiation), harvest maturity countdown.
- **Dependencies:** AgroContext.
- **Error States:** `SEASON_OVERLAP_CONFLICT`.
- **Privacy Requirements:** Standard tenant isolation.
- **Acceptance Criteria:** Generates accurate agronomical milestones upon crop registration.
- **MVP Priority:** **P0**

---

### Module 10: Soil & Irrigation Records
- **Objective:** Record soil health card parameters and water management schedules to tailor fertilizer and disease vulnerability assessments.
- **Target User:** Farmers, Extension Officers.
- **Inputs:** Soil test values (pH, Electrical Conductivity, Organic Carbon, Available Nitrogen, Phosphorus, Potassium, Zinc, Boron), irrigation type, salinity observations.
- **Processing:** Generates soil health score; flags nutrient deficiencies that mimic foliar diseases (e.g., Nitrogen deficiency vs. general chlorosis; Potassium deficiency vs. leaf edge scorching).
- **Outputs:** Visual soil health card, customized basal and top-dressing fertilizer advisory (Urea, DAP, MOP dosages per acre).
- **Dependencies:** Database.
- **Error States:** `INVALID_NUTRIENT_RANGE`.
- **Privacy Requirements:** Plot-level encryption.
- **Acceptance Criteria:** Correctly alerts user when symptoms indicate nutritional deficiency rather than pathogen infection.
- **MVP Priority:** **P2**

---

### Module 11: Farm Operations & Intervention Tracking
- **Objective:** Enable farmers to record and verify every action taken in the field (pesticide spray, fertilizer application, weeding, irrigation, pruning).
- **Target User:** Farmers.
- **Inputs:** Action type, product brand/chemical name, quantity used, water volume, date, application method.
- **Processing:** Validates intervention against previous diagnostic recommendations; checks compliance with pre-harvest intervals (PHI).
- **Outputs:** Digital farm ledger entry, automated follow-up reminder (*"Check leaf status 5 days after spray"*).
- **Dependencies:** Database, KrishiBrain.
- **Error States:** `INVALID_DATE`, `UNKNOWN_PRODUCT`.
- **Privacy Requirements:** Standard tenant isolation.
- **Acceptance Criteria:** 1-tap logging via quick-select buttons optimized for mobile touch.
- **MVP Priority:** **P1**

---

### Module 12: Harvest & Post-Harvest Records
- **Objective:** Track crop yield, grade quality, post-harvest losses, and storage conditions.
- **Target User:** Farmers, Researchers.
- **Inputs:** Harvest date, total quintals harvested per acre, moisture percentage, grading notes (e.g., cotton staple length/trash content, chilli color grade).
- **Processing:** Computes yield-per-acre productivity index against regional PJTSAU district benchmarks.
- **Outputs:** Yield summary card, seasonal profitability input, storage preservation advisory.
- **Dependencies:** Database.
- **Error States:** `UNREALISTIC_YIELD_VALUE`.
- **Privacy Requirements:** Private financial/production data.
- **Acceptance Criteria:** Accurately calculates quintals/acre and highlights delta vs. district average.
- **MVP Priority:** **P2**

---

### Module 13: Market Intelligence
- **Objective:** Real-time commodity price tracking and mandi arrivals across Telangana Agricultural Market Committees (e.g., Warangal Cotton & Chilli Mandi, Khammam, Suryapet).
- **Target User:** Farmers.
- **Inputs:** Commodity filter (Cotton, Paddy Common, Paddy Grade A, Chilli Teja), district selection.
- **Processing:** Ingestion and normalization of public agricultural market committee feeds (e-NAM / Agmarknet).
- **Outputs:** Modal price, minimum/maximum price per quintal, 7-day price trend chart, nearest major mandi distance.
- **Dependencies:** External market data adapter (e-NAM / open scraper).
- **Error States:** `MANDI_FEED_STALE`, `COMMODITY_NOT_LISTED`.
- **Privacy Requirements:** None (public commodity data).
- **Acceptance Criteria:** Displays verified modal mandi prices updated within 24 hours.
- **MVP Priority:** **P2**

---

### Module 14: Agricultural Learning Centre
- **Objective:** Curated multimedia knowledge repository providing step-by-step guides, pest life cycles, beneficial insect identification, and water management in Telugu and English.
- **Target User:** Farmers, Students, Extension Agents.
- **Inputs:** Search query, topic taxonomy filter (Crops, Diseases, Organic Practices, Government Schemes like Rythu Bharosa).
- **Processing:** Fast full-text search against PJTSAU extension bulletins and illustrated guides.
- **Outputs:** Interactive cards with high-definition diagrams, symptom comparison carousels, audio summaries, and downloadable PDF bulletins.
- **Dependencies:** Private object storage, CDN.
- **Error States:** `CONTENT_NOT_FOUND`.
- **Privacy Requirements:** Public educational content.
- **Acceptance Criteria:** Content viewable offline via PWA caching.
- **MVP Priority:** **P2**

---

### Module 15: AI Research & Model Evaluation Dashboard
- **Objective:** Internal operational console for researchers and ML engineers to evaluate model drift, confusion patterns, calibration error, and annotation pipelines.
- **Target User:** ML Researchers, System Administrators.
- **Inputs:** Diagnostic prediction logs, ground-truth expert review feedback, image quality statistics.
- **Processing:** Computes real-time Macro F1, class-wise Precision/Recall, Expected Calibration Error (ECE), and OOD rejection frequency.
- **Outputs:** Confusion matrices, drift alerts, low-confidence symptom clusters, download link for expert-verified benchmark sets.
- **Dependencies:** Database, MLflow, Analytics service.
- **Error States:** `INSUFFICIENT_EVALUATION_DATA`.
- **Privacy Requirements:** Strict RBAC (Researcher role only); all farmer metadata stripped from images and logs.
- **Acceptance Criteria:** Generates updated confusion matrix across all 3 crops upon new expert validations.
- **MVP Priority:** **P1**

---

## 5. Release Phasing Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RELEASE PHASING MATRIX                             │
├──────────────────────────┬──────────────────────────┬───────────────────────┤
│   PHASE 1: CORE MVP      │  PHASE 2: ENHANCED MVP   │ PHASE 3: SCALE EXPANSION
│     (Weeks 1 - 12)       │     (Weeks 13 - 16)      │     (Post-16 Weeks)   │
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ • Module 1: CropVision   │ • Module 4: RiskCast     │ • Module 10: Soil &   │
│   (P0 - Core Pathology)  │   (P1 - Weather Risks)   │   Irrigation Records  │
│ • Module 2: AgroContext  │ • Module 6: ExpertConnect│ • Module 12: Harvest  │
│   (P0 - Plot & Stages)   │   (P1 - Agronomist Queue)│   & Post-Harvest      │
│ • Module 3: KrishiBrain  │ • Module 7: CropPulse    │ • Module 13: Market   │
│   (P0 - Verified RAG)    │   (P1 - Plot Timeline)   │   Intelligence (eNAM) │
│ • Module 5: KisanSaathi  │ • Module 8: Farm Intel   │ • Module 14: Learning │
│   (P0 - Telugu Voice AI) │   (P1 - Summary Deck)    │   Centre Library      │
│ • Module 9: Lifecycle    │ • Module 11: Operations  │ • Satellite Integration│
│   (P0 - Season Setup)    │   (P1 - Spray Tracking)  │   (Copernicus NDVI)   │
│                          │ • Module 15: AI Eval     │                       │
│                          │   (P1 - ML Diagnostics)  │                       │
└──────────────────────────┴──────────────────────────┴───────────────────────┘
```
