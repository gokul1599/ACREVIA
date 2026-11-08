# ACREVIA — STAGE 5 READINESS AUDIT
## Pre-Implementation Dependency, Infrastructure, Architecture & Security Verification

---

## 1. Executive Summary & Audit Context

**Product:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana-first, India  
**Target Crops:** Cotton, Rice, Chilli  
**Languages:** Telugu, English, Hindi  
**Stage:** 05 — KrishiBrain: Agricultural Knowledge Intelligence, Multilingual RAG & Grounded AI  
**Infrastructure Target:** Neon PostgreSQL + pgvector + Vercel (`sin1` Singapore region alignment)  
**Audit Timestamp:** 2026-11-08

In accordance with the Stage 5 Entry Gate protocol, this audit inspects the current repository state before introducing any new code or database structures.

---

## 2. Dependency Readiness Verification Matrix

| Subsystem / Component | Current State | Status | Implementation Evidence | Missing Functionality / Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **Product Branding** | Canonical identity is ACREVIA | `READY` | Verified in `README.md`, `backend/app/main.py`, `backend/app/core/config.py` | None. Canonical naming maintained across all new components. |
| **Stage 2 ML Baseline** | Multicrop baseline architectures & dataset protocols | `READY` | `docs/research/STAGE_2_COMPLETION_REPORT.md`, `ml/configs/taxonomy/*.yaml` | Verified baseline entry gate. |
| **Stage 3 Inference Engine** | MobileNetV3 backbones, abstention, calibration, ONNX exporter | `READY` | `docs/research/STAGE_3_COMPLETION_REPORT.md`, `ml/inference_service/` (port 8001) | RAG must integrate with CropVision inference contracts. |
| **Stage 4 Enterprise Backend** | Modular FastAPI gateway with correlation tracking & middleware | `READY` | `backend/app/main.py`, `backend/app/api/v1/router.py`, `docs/architecture/STAGE_4_COMPLETION_REPORT.md` | Mount `/api/v1/knowledge` router into existing master router. |
| **Database Schema** | 24 relational tables mapped via SQLAlchemy 2.0 | `READY` | `backend/app/models/*.py`, verified in `backend/app/models/__init__.py` | Add Knowledge domain models: `KnowledgeSource`, `KnowledgeDocument`, `KnowledgeChunk`, `KnowledgeEmbedding`, etc. |
| **Database Engine & Neon Config** | Dual pooled/unpooled connection strategy | `PARTIALLY_READY` | `backend/app/core/config.py` supports `DATABASE_URL` and `DATABASE_URL_UNPOOLED` | Live hosted Neon instance is placeholder in `.env.example`; local testing uses SQLite with vector compatibility. |
| **Vector Extension (pgvector)** | PostgreSQL extension for vector similarity | `READY` | `pgvector==0.5.1` installed; SQLAlchemy Vector column verified | Implement pgvector extension migration script and cosine similarity queries. |
| **Authentication & RBAC** | Bcrypt (12 rounds) + JWT (HS256) | `READY` | `backend/app/core/security.py`, `backend/app/security/dependencies.py` | Reuse existing `require_roles(SystemRole.ADMIN, SystemRole.AGRICULTURAL_EXPERT)` for source ingestion and review. |
| **Tenant Farm Ownership** | Strict service-level isolation (`verify_farm_access`) | `READY` | `backend/app/security/dependencies.py`, `backend/tests/test_authorization.py` | Knowledge queries with optional `farm_id` must validate caller ownership to prevent cross-tenant leakage. |
| **Object Storage Abstraction** | Abstract `StorageProvider` with local and S3 adapters | `READY` | `backend/app/integrations/storage.py` | Store original uploaded PDF/DOCX source files in private storage. |
| **Document Extraction Libs** | PDF, DOCX, HTML, plain text extractors | `READY` | `pypdf==7.0.0`, `python-docx==1.2.0`, `beautifulsoup4==4.15.0`, `lxml==6.1.3` installed | Implement structure-aware chunking preserving headings and page boundaries. |
| **Embedding Providers** | External AI embedding models (OpenAI, Gemini, HuggingFace) | `PARTIALLY_READY` | Configuration schema in `backend/app/core/config.py` | API keys are not committed. Implement decoupled adapter with mock/deterministic provider for zero-cost offline testing. |
| **LLM Generation Providers** | Groq / Gemini / Sarvam AI | `PARTIALLY_READY` | Configuration schema in `backend/app/core/config.py` | Live keys are placeholders. Implement decoupled adapter with deterministic grounded response mode for testing. |
| **Automated Testing Suite** | Pytest harness with 96 existing tests (100% green) | `READY` | `tests/ml/`, `tests/api/`, `backend/tests/`, `ml/inference_service/tests/` | Add comprehensive Stage 5 knowledge unit, integration, and security tests. |
| **Vercel Deployment Topology** | Serverless Next.js + FastAPI integration | `PARTIALLY_READY` | `backend/Dockerfile`, Vercel config documentation | Long-running document ingestion must be designed as bounded CLI / job processor to respect serverless timeouts. |

---

## 3. Critical Blockers & Open Risks

1. **Third-Party AI Credentials Pending Provisioning:** In compliance with security directives, external API keys (`OPENAI_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `SARVAM_AI_API_KEY`) remain unconfigured placeholders in `.env.example`.
   - *Architecture Resolution:* KrishiBrain will implement an abstract `EmbeddingProvider` and `LLMProvider` architecture featuring a **deterministic local embedding/generation provider** alongside the cloud adapters, ensuring 100% of test suites and local development execute reproducibly without requiring live paid API credits.
2. **Neon Hosted Cloud Instance:** Cloud database URL is set to local fallback by default.
   - *Architecture Resolution:* The schema is architected to execute on native PostgreSQL + pgvector when deployed to Neon, while simultaneously supporting SQLite in-memory execution for testing via `pgvector.sqlalchemy.Vector`.

---

## 4. Stage 5 Implementation Boundaries

- **KrishiBrain** will act as the authoritative evidence and retrieval layer.
- **CropVision** diagnostic outputs will be consumed as contextual signals, but RAG retrieval will never override or invent disease classifications.
- **DPDP Act Compliance:** Public agricultural publications will remain strictly decoupled from private farmer field scouting records.
