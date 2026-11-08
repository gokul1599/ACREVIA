# KISANVISION — ARCHITECTURE DECISION RECORDS (ADR)

**Document Version:** 1.0.0  
**Status:** Approved for Stage 1 Baseline  
**Scope:** Key Structural, Algorithmic & Infrastructure Decisions for KisanVision  

---

## Index of Architecture Decisions

1. [ADR-001: Next.js App Router for Frontend Client Layer](#adr-001-nextjs-app-router-for-frontend-client-layer)
2. [ADR-002: FastAPI (Python 3.11 via `uv`) for Application API Gateway](#adr-002-fastapi-python-311-via-uv-for-application-api-gateway)
3. [ADR-003: PostgreSQL with `pgvector` for Relational & Vector Persistence](#adr-003-postgresql-with-pgvector-for-relational--vector-persistence)
4. [ADR-004: Tiered Hybrid Custom Vision Model vs. General Multimodal AI](#adr-004-tiered-hybrid-custom-vision-model-vs-general-multimodal-ai)
5. [ADR-005: Abstract Provider Adapter Architecture for Groq and Gemini](#adr-005-abstract-provider-adapter-architecture-for-groq-and-gemini)
6. [ADR-006: Local Sentence Transformers vs. Cloud Embedding APIs](#adr-006-local-sentence-transformers-vs-cloud-embedding-apis)
7. [ADR-007: FastAPI BackgroundTasks vs. Celery/Redis for Asynchronous Jobs](#adr-007-fastapi-backgroundtasks-vs-celeryredis-for-asynchronous-jobs)
8. [ADR-008: Private S3-Compatible Object Storage with Pre-signed URLs](#adr-008-private-s3-compatible-object-storage-with-pre-signed-urls)
9. [ADR-009: Phone Number OTP + Stateless JWT for Authentication](#adr-009-phone-number-otp--stateless-jwt-for-authentication)
10. [ADR-010: Service Worker PWA Caching Strategy for Rural Connectivity](#adr-010-service-worker-pwa-caching-strategy-for-rural-connectivity)

---

## ADR-001: Next.js App Router for Frontend Client Layer
- **Status:** **ACCEPTED**
- **Context:** KisanVision targets smallholder farmers in Telangana accessing the web via budget Android smartphones over intermittent 3G/4G networks, alongside desktop access for extension officers.
- **Options Considered:**
  1. *Next.js 14/15 App Router (TypeScript, React Server Components).*
  2. *Single Page Application (Vite + React).*
  3. *Cross-Platform Mobile App (Flutter or React Native).*
- **Decision:** Select **Next.js App Router with TypeScript**.
- **Reasoning:**
  - Next.js Server Components drastically reduce client JavaScript payload, delivering First Contentful Paint (FCP) < 1.2s on low-tier mobile hardware.
  - PWA packaging allows zero-install access via web link, bypassing Google Play Store installation friction and storage space concerns on budget phones.
  - Universal TypeScript data contracts can be shared with OpenAPI generated types.
- **Trade-offs:** Higher server-side compute requirement than static SPAs; requires handling hydration boundaries for interactive audio components.
- **Conditions that could change decision:** If rural user testing indicates farmers refuse browser-based workflows and insist on native Android APKs via sideloading/ShareChat.

---

## ADR-002: FastAPI (Python 3.11 via `uv`) for Application API Gateway
- **Status:** **ACCEPTED**
- **Context:** The backend must handle high-concurrency API requests, execute local ONNX computer vision models, interface with Python ML/scientific libraries (OpenCV, PyTorch, NumPy), and stream LLM responses. The audited host machine runs Python 3.14 (incompatible with PyTorch wheels), but has Astral `uv` installed.
- **Options Considered:**
  1. *FastAPI with CPython 3.11.16 pinned via `uv`.*
  2. *Django REST Framework (Python).*
  3. *Node.js / Express or NestJS.*
  4. *Go (Golang).*
- **Decision:** Select **FastAPI with CPython 3.11.16 managed by `uv`**.
- **Reasoning:**
  - Pinned CPython 3.11 guarantees pre-built wheel availability for PyTorch, torchvision, and OpenCV.
  - Native `asyncio` delivers high throughput for asynchronous external API orchestration (Groq, Gemini, Open-Meteo).
  - Pydantic v2 offers ultra-fast C-compiled schema validation and automatic OpenAPI 3.1 documentation.
- **Trade-offs:** Python consumes slightly more baseline memory than Go; mitigated by running lightweight async workers.
- **Conditions that could change decision:** If the microservices grow so large that ML inference is completely decoupled into a separate Triton inference cluster, at which point the API gateway could transition to Go.

---

## ADR-003: PostgreSQL with `pgvector` for Relational & Vector Persistence
- **Status:** **ACCEPTED**
- **Context:** KisanVision requires robust relational integrity (Farms, Plots, Seasons, Interventions) and high-dimensional semantic search for agricultural RAG. The host environment lacks local Docker or PostgreSQL, necessitating a managed cloud database.
- **Options Considered:**
  1. *Managed PostgreSQL (Supabase / Neon) with `pgvector` extension.*
  2. *Separate relational DB (PostgreSQL) + dedicated vector DB (Pinecone, Qdrant, Milvus).*
  3. *NoSQL Database (MongoDB Atlas).*
- **Decision:** Select **Managed PostgreSQL with `pgvector`**.
- **Reasoning:**
  - Unified ACID transactions: Can query a plot's disease history, soil type, and semantic knowledge chunks within a single SQL statement.
  - Zero dual-write inconsistency bugs (eliminates synchronizing two separate databases).
  - HNSW index in `pgvector` delivers sub-10ms vector similarity lookups for datasets under 1,000,000 vectors.
  - Supabase free tier provides 500 MB database and pre-installed `pgvector` hosted in Mumbai (`ap-south-1`).
- **Trade-offs:** Vector search consumes CPU/RAM on the database instance during heavy bulk indexing.
- **Conditions that could change decision:** If the knowledge base expands beyond 10 million vector chunks requiring distributed multi-node ANN clustering.

---

## ADR-004: Tiered Hybrid Custom Vision Model vs. General Multimodal AI
- **Status:** **ACCEPTED**
- **Context:** Farmers upload high-resolution leaf photographs. We must balance diagnostic accuracy, latency, inference cost, and offline resilience. General multimodal LLMs (GPT-4o, Gemini 1.5 Pro) are expensive ($0.002–$0.01 per image) and high latency (1.5–3.5s), while pure local edge models may struggle with complex rare co-infections.
- **Options Considered:**
  1. *Tiered Hybrid Strategy: Lightweight local ONNX vision model (Tier 1) + Multimodal LLM arbiter (Tier 2).*
  2. *Multimodal LLM only (Zero local vision model).*
  3. *Custom deep vision model only (Zero LLM vision fallback).*
- **Decision:** Select **Tiered Hybrid Architecture**.
- **Reasoning:**
  - 80%+ of common field infections (e.g., standard Rice Blast, Cotton Grey Mildew, Chilli Powdery Mildew) are classified cleanly by a fine-tuned MobileNetV3 / EfficientNet model running on local CPU in <100ms at $0.00 marginal cost.
  - Multimodal LLM (Gemini 1.5 Flash) is invoked only when entropy indicates high uncertainty ($< 0.85$ confidence) or multiple lesions are detected.
  - Optimizes operating costs by ~80% while retaining frontier reasoning for edge cases.
- **Trade-offs:** Requires maintaining both a computer vision training pipeline and an LLM prompt engineering pipeline.
- **Conditions that could change decision:** If cloud multimodal LLM pricing drops by 90% and latency falls below 200ms globally.

---

## ADR-005: Abstract Provider Adapter Architecture for Groq and Gemini
- **Status:** **ACCEPTED**
- **Context:** Cloud AI providers frequently adjust rate limits, deprecate model checkpoints, or change pricing tiers. Direct vendor lock-in poses an operational risk.
- **Options Considered:**
  1. *Abstract `ILLMProviderAdapter` interface with concrete adapters (`GroqAdapter`, `GeminiAdapter`).*
  2. *Direct integration using vendor-specific client libraries throughout services.*
  3. *Heavy third-party orchestration framework (e.g., LangChain ecosystem overhead).*
- **Decision:** Select **Clean Abstract Provider Adapter Interface**.
- **Reasoning:**
  - Complete decoupling: Switching from Groq to Gemini or self-hosted vLLM requires changing a single configuration key (`LLM_PROVIDER=gemini`).
  - Enables seamless runtime failover: If Groq returns HTTP 429 (Rate Limit Exceeded), the adapter automatically falls back to Gemini 1.5 Flash within 50ms.
  - Avoids framework bloat and hidden breaking changes associated with heavy abstractions.
- **Trade-offs:** Requires writing and maintaining ~150 lines of boilerplate adapter code.
- **Conditions that could change decision:** None; standard software engineering best practice.

---

## ADR-006: Local Sentence Transformers vs. Cloud Embedding APIs
- **Status:** **ACCEPTED**
- **Context:** Generating vector embeddings for agricultural knowledge documents (PJTSAU) and farmer search queries.
- **Options Considered:**
  1. *Local Sentence Transformers (`all-MiniLM-L6-v2` / `paraphrase-multilingual-MiniLM-L12-v2`).*
  2. *Cloud Embedding API (Google `text-embedding-004` or OpenAI `text-embedding-3-small`).*
- **Decision:** Select **Local Sentence Transformers**.
- **Reasoning:**
  - 100% offline development capability on host environment; zero external network dependency during RAG indexing.
  - Negligible CPU footprint on AMD Ryzen 5500U (~120ms for batch of 32 chunks).
  - Guarantees embedding dimension stability (384 dimensions) with zero per-token billing.
- **Trade-offs:** Smaller embedding dimensionality (384 vs. 768/1536) has slightly lower semantic capacity on cross-lingual nuances; mitigated by hybrid BM25 lexical keyword boosting.
- **Conditions that could change decision:** If multilingual Telugu retrieval benchmarks prove significantly superior on Google's native multilingual embeddings.

---

## ADR-007: FastAPI BackgroundTasks vs. Celery/Redis for Asynchronous Jobs
- **Status:** **ACCEPTED**
- **Context:** The system must process non-blocking asynchronous tasks (saving audit logs, generating image thumbnails, triggering notifications). The host environment has 5.86 GB RAM and no local Docker/Redis.
- **Options Considered:**
  1. *FastAPI native `BackgroundTasks` / Python `asyncio` worker queues.*
  2. *Celery + Redis message broker.*
  3. *Cloud-managed task queue (AWS SQS / Google Cloud Tasks).*
- **Decision:** Select **FastAPI native `BackgroundTasks` for Development & MVP (Phase 1)**, with an adapter design allowing Celery/Redis in Phase 3.
- **Reasoning:**
  - Saves 600 MB+ RAM on the constrained host machine during local development.
  - Eliminates external dependencies on Redis server processes on Windows.
  - Fully sufficient for MVP throughput of up to 50 concurrent requests.
- **Trade-offs:** Background tasks run in the same process memory space; tasks could be dropped if the server restarts mid-execution.
- **Conditions that could change decision:** Once KisanVision scales beyond 500 concurrent daily active farmers, requiring guaranteed task persistence.

---

## ADR-008: Private S3-Compatible Object Storage with Pre-signed URLs
- **Status:** **ACCEPTED**
- **Context:** Farmer leaf photographs must be stored securely, encrypted at rest, and served efficiently to mobile PWAs and expert portals.
- **Options Considered:**
  1. *Private S3-compatible object storage (Supabase Storage / Cloudflare R2 / AWS S3) with time-limited Pre-signed URLs.*
  2. *Storing binary image blobs directly inside PostgreSQL (`BYTEA`).*
  3. *Local filesystem storage.*
- **Decision:** Select **Private S3-Compatible Object Storage with Pre-signed URLs**.
- **Reasoning:**
  - Storing blobs in PostgreSQL degrades database performance, bloats backups, and exhausts RAM caches.
  - Pre-signed URLs (15-minute TTL) ensure that only authenticated farmers and assigned extension officers can view leaf imagery.
  - Storage is physically decoupled from application servers, allowing direct browser-to-bucket uploads.
- **Trade-offs:** Requires coordinating two-step uploads (request pre-signed URL -> upload blob -> commit metadata).
- **Conditions that could change decision:** None; standard industry pattern.

---

## ADR-009: Phone Number OTP + Stateless JWT for Authentication
- **Status:** **ACCEPTED**
- **Context:** Rural farmers in Telangana do not use email addresses or complex passwords. Mobile phone numbers and SMS OTPs are the universal standard for digital authentication in rural India.
- **Options Considered:**
  1. *Phone Number + SMS OTP issuing stateless HTTP-only signed JWTs.*
  2. *Email + Password authentication.*
  3. *OAuth2 Social Logins (Google / Truecaller).*
- **Decision:** Select **Phone Number + OTP with Signed JWT (HTTP-Only Cookies)**.
- **Reasoning:**
  - Zero password cognitive burden for smallholder farmers.
  - Aligns with standard Indian e-governance workflows (Rythu Bandhu, PM-Kisan).
  - Stateless JWTs allow seamless multi-server scaling without session database bottlenecks.
- **Trade-offs:** Costs incurred for SMS gateway delivery (e.g., Twilio / Fast2SMS); mitigated by fallback WhatsApp OTPs.
- **Conditions that could change decision:** None for farmers. Agronomists and administrators will use Email + Password + MFA.

---

## ADR-010: Service Worker PWA Caching Strategy for Rural Connectivity
- **Status:** **ACCEPTED**
- **Context:** Rural connectivity across agricultural mandals fluctuates between high-speed 4G, throttled 2G, and dead zones. Farmers must not encounter blank screens when internet drops while walking through fields.
- **Options Considered:**
  1. *Progressive Web App (PWA) with Workbox Service Worker employing a Stale-While-Revalidate caching strategy.*
  2. *Standard web application with no offline caching.*
  3. *Local SQLite database inside native mobile application.*
- **Decision:** Select **PWA with Stale-While-Revalidate & Cache-First Strategy**.
- **Reasoning:**
  - UI assets, fonts, icons, and static emergency crop guides are cached on first load.
  - Previous diagnostic reports and plot histories are persisted in IndexedDB on the client device.
  - If a photo is captured while offline, the service worker buffers the request in Background Sync and dispatches it automatically upon network restoration.
- **Trade-offs:** Cache invalidation complexity when deploying major frontend updates.
- **Conditions that could change decision:** If background sync reliability across low-end mobile browser variants proves inconsistent during field testing.
