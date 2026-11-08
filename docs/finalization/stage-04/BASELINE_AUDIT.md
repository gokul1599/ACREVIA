# ACREVIA — STAGE 04 BASELINE AUDIT REPORT
## Codebase Inventory, Historical 48-Document Claim Audit & Live Neon DB State

**Document Reference:** `docs/finalization/stage-04/BASELINE_AUDIT.md`  
**Stage:** 04 — KrishiBrain Multilingual Multimodal Agricultural RAG Intelligence Engine  
**Audit Date:** 2026-11-08  
**Auditing Authority:** ACREVIA Principal AI Architect & Data Engineering Specialist  

---

### 1. Codebase Asset Inventory

The KrishiBrain subsystem is structured across backend services, database models, API routes, and a Next.js 16 frontend interface:

| Subsystem Component | File Path | Functional Responsibility |
|---|---|---|
| **API Endpoints** | [`backend/app/api/v1/endpoints/knowledge.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/knowledge.py) | Query dispatch (`/query`), source registration (`/sources`), ingestion (`/ingest`), job polling (`/jobs/{id}`), feedback (`/feedback`) |
| **Data Models** | `backend/app/models/knowledge_*.py` | SQLAlchemy 2.x models for sources, documents, document versions, chunks, embeddings, feedback, and knowledge graph |
| **Ingestion Pipeline** | [`backend/app/services/knowledge/ingestion/ingestion_service.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/knowledge/ingestion/ingestion_service.py) | Orchestrates extraction, chunking, embedding generation, version tracking, and audit logging |
| **Document Extractors** | [`backend/app/services/knowledge/extraction/extractors.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/knowledge/extraction/extractors.py) | Format extractors for PDF (`pypdf`), DOCX (`python-docx`), HTML (`BeautifulSoup`), Markdown, and plain text |
| **Chunking Engine** | [`backend/app/services/knowledge/chunking/chunker.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/knowledge/chunking/chunker.py) | Structure-aware chunking preserving headings, token bounds (250 tokens target, 40 overlap), and page metadata |
| **Embedding Provider** | [`backend/app/services/knowledge/embeddings/embedding_provider.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/knowledge/embeddings/embedding_provider.py) | 1536-dimensional embedding provider: `DeterministicLocalEmbeddingProvider` and `CloudEmbeddingProvider` |
| **Hybrid Retriever** | [`backend/app/services/knowledge/retrieval/retriever.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/knowledge/retrieval/retriever.py) | Dense pgvector cosine search + lexical token overlap + crop boosting (65/35 ratio) |
| **Grounded Generator** | [`backend/app/services/knowledge/generation/generator.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/knowledge/generation/generator.py) | Evidence grounding, CIBRC agrochemical safety guardrails, citation assembly, and multilingual response synthesis |
| **Evaluation Suite** | `backend/app/services/knowledge/evaluation/` | 45 structured gold test cases across Cotton, Rice, Chilli (`eval_dataset.py`) and batch evaluation runner (`evaluation_runner.py`) |
| **Farmer Interface** | [`frontend/app/(farmer)/knowledge/page.tsx`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/app/(farmer)/knowledge/page.tsx) | Next.js 16 App Router UI with voice recording, audio playback (TTS), crop toggles, citations drawer, and feedback buttons |

---

### 2. Historical 48-Document Claim Audit

Earlier development summaries reported:
> *"KrishiBrain is powered by 48 PJTSAU/ICAR agricultural guides, structure-aware chunking, and 1536-dimensional embeddings in pgvector."*

#### Empirical Finding
An independent database query executed against the live Neon Serverless PostgreSQL instance revealed that **the live production database initially contained 0 sources, 0 documents, and 0 chunks**.

The "48 documents" figure represents a **conceptual roadmap catalog** compiled during initial planning, but no automated migration had actually persisted those 48 documents into the database. Previous tests had verified RAG purely via dynamic in-memory test fixtures created during test setup.

#### Resolution & Seed Deployment
To establish genuine, evidence-backed knowledge in Neon PostgreSQL, an institutional seed was created and executed during this finalization session, yielding:
- **Registered Sources:** 4 verified institutions (`PJTSAU`, `ICAR-CICR`, `ICAR-IIRR`, `CIBRC`).
- **Ingested Documents:** 7 foundational agricultural documents across English, Telugu, and Hindi.
- **Indexed Chunks:** 19 structure-aware chunks with heading hierarchies and page references.
- **Embedded Vectors:** 19 1536-dimensional dense vectors stored in Neon `pgvector`.

---

### 3. Embedding Architecture & Vector Storage Baseline

- **Model Dimension:** Strictly 1536 dimensions, mapping to OpenAI `text-embedding-3-small` specification.
- **Vector Extension:** Neon PostgreSQL 16 + `pgvector` v0.8.6.
- **Table Definition:** `knowledge_embeddings` with `embedding Vector(1536)` and indexed profile ID.
- **Provider Abstraction:** Decoupled factory (`get_embedding_provider()`) allowing zero-cost local deterministic execution during development and seamless cloud provider switching in production.

---

### 4. Integration Test Baseline

Running the backend knowledge test suite confirms an unbroken baseline:

```text
backend/tests/test_knowledge.py::test_register_knowledge_source_rbac PASSED             [ 12%]
backend/tests/test_knowledge.py::test_ingest_document_and_query_citations PASSED       [ 25%]
backend/tests/test_knowledge.py::test_knowledge_query_abstention_on_unsupported_topic PASSED [ 37%]
backend/tests/test_knowledge.py::test_knowledge_query_high_risk_advice_safety PASSED   [ 50%]
backend/tests/test_knowledge.py::test_multilingual_telugu_query PASSED                 [ 62%]
backend/tests/test_knowledge.py::test_knowledge_feedback_workflow PASSED               [ 75%]
backend/tests/test_knowledge.py::test_knowledge_query_tenant_isolation PASSED          [ 87%]
backend/tests/test_knowledge.py::test_rag_evaluation_runner PASSED                     [100%]

======================== 8 passed, 1 warning in 33.23s ========================
```
All 8 integration tests pass with 100% green coverage.
