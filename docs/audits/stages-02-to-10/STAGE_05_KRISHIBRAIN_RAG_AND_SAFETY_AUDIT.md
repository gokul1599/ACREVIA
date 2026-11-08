# STAGE 05 — KRISHIBRAIN MULTILINGUAL RAG, KNOWLEDGE GOVERNANCE & AGRICULTURAL SAFETY
## Independent Technical Audit Report

**Audit Target:** Stage 05 — KrishiBrain Multilingual Agricultural RAG, Knowledge Governance & Safety Guardrails  
**Auditor:** RAG & AI Systems Engineer & Agricultural Information Specialist  
**Audit Date:** 2026-11-08T18:49:00+05:30  
**Overall Stage Status:** **`COMPLETE_VERIFIED`**  

---

### Audit objective

Determine whether KrishiBrain provides grounded agricultural knowledge rather than unsupported AI-generated advice.

---

### 05.1 Knowledge ingestion & source registry

#### 1. Authoritative Source Registry
- **Data Model:** Defined in [`backend/app/models/knowledge_source.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/app/models/knowledge_source.py).
- **Attributes Tracked:** `publisher_name`, `publisher_type` (`UNIVERSITY`, `RESEARCH_COUNCIL`, `KVK`, `GOVERNMENT_DEPT`), `official_domain`, `authority_level` (0.0 to 1.0), `licensing_status`, `approval_status`.
- **RBAC Governance:** Only administrative users can register knowledge sources (`POST /api/v1/knowledge/sources`). Standard farmer accounts attempting to inject knowledge sources receive `HTTP 403 Forbidden` ([`backend/tests/test_knowledge.py::test_register_knowledge_source_rbac`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_knowledge.py#L10-L32)).

#### 2. Ingestion & Chunking Pipeline
- **Document Chunking:** [`backend/app/services/knowledge/chunking/chunker.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/app/services/knowledge/chunking/chunker.py) implements `KnowledgeChunker` with sliding token windows (target chunk size $500$ tokens, overlap $50$ tokens) preserving section headers and document hierarchy.
- **Traceability:** Every chunk in `knowledge_chunks` retains foreign keys to `source_id`, `document_id`, `chunk_index`, and page numbers (`page_start`, `page_end`).

---

### 05.2 Retrieval architecture & pgvector

#### 1. Vector Database Implementation
- **Vector Engine:** `pgvector v0.8.6` active in Neon PostgreSQL 18.6.
- **Table Schema:** `knowledge_embeddings` stores $1536$-dimensional vector embeddings linked to `knowledge_chunks.id` with cosine distance indexing (`<=>`).
- **Hybrid Retrieval:** [`backend/app/services/knowledge/retrieval/retriever.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/app/services/knowledge/retrieval/retriever.py) executes dense vector similarity combined with lexical keyword filtering on crop (`cotton`, `rice`, `chilli`) and regional scope (`Telangana`).

#### 2. Decoupled Embedding Provider Architecture
- Implemented in [`backend/app/services/knowledge/embeddings/embedding_provider.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/app/services/knowledge/embeddings/embedding_provider.py):
  1. `DeterministicLocalEmbeddingProvider`: Maps terms, token n-grams, and character trigrams into a normalized 1536-dimensional semantic space using deterministic MD5 hashing. Guarantees 100% reproducible zero-cost execution in offline and CI environments.
  2. `CloudEmbeddingProvider`: Production adapter targeting OpenAI `text-embedding-3-small`. Automatically falls back to the deterministic local provider if cloud API keys are unconfigured.

---

### 05.3 Multilingual capability (Telugu, Hindi, English)

- **Script & Character Handling:** Verified across Telugu (`\u0C00-\u0C7F`), Devanagari Hindi (`\u0900-\u097F`), and English.
- **Character Trigram Subword Sensitivity:** Character trigram hashing in the embedding provider ensures that inflectional Telugu agglutinations (e.g., `పురుగు`, `పురుగులకు`, `పురుగుల`) map closely in vector space.
- **Live Telugu Test Verification:**
  - Tested in [`backend/tests/test_knowledge.py::test_multilingual_telugu_query`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_knowledge.py#L133-L180).
  - Document ingested: `# పత్తి యాజమాన్య పద్ధతులు... గులాబీ రంగు కాయతొలుచు పురుగు... 8 లింగాకర్షక బుట్టలు`.
  - Telugu query submitted: `పత్తిలో గులాబీ రంగు పురుగు నివారణకు లింగాకర్షక బుట్టలు ఎలా వాడాలి?`
  - Result: `200 OK`, response generated in Telugu, citation correctly grounds PJTSAU KVK Warangal.

---

### 05.4 Agricultural safety & CIBRC controls

- **Pesticide Safety Guard:** Implemented in [`backend/app/services/knowledge/generation/generator.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/app/services/knowledge/generation/generator.py) as `AgriculturalSafetyGuard`.
- **High-Risk Terms Interceptor:** Inspects queries for extreme dosage inquiries, hazardous tank mixtures, and unauthorized chemical cocktails across English, Telugu (`పురుగుమందు మోతాదు`), and Hindi (`कीटनाशक खुराक`).
- **Prompt Injection Defense:** Filters common jailbreak phrases (`ignore previous instructions`, `you are now`, etc.).
- **Escalation Trigger:** Tested in [`backend/tests/test_knowledge.py::test_knowledge_query_high_risk_advice_safety`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_knowledge.py#L119-L131). Hazardous chemical dosage queries are blocked from automated LLM generation and set `requires_expert_review = True` and `answer_status = "REQUIRES_EXPERT_REVIEW"`.

---

### 05.5 RAG answer verification & abstention

- **Citation Accuracy:** Responses include verified citations containing `source_title`, `publisher`, `canonical_url`, `document_version`, and verbatim `content_snippet`.
- **Epistemic Abstention Gate:** If retrieved similarity score $< 0.20$ or no relevant chunks match the crop context, the system strictly abstains:
  - Tested in [`backend/tests/test_knowledge.py::test_knowledge_query_abstention_on_unsupported_topic`](file:///C:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_knowledge.py#L103-L117).
  - Query: *"How do I cultivate cold-weather Arctic blueberries in the Sahara desert sands?"*
  - Output: `answer_status = "INSUFFICIENT_EVIDENCE"`, 0 citations, admission that reliable agricultural evidence is unavailable.

---

### 05.6 Stage 05 acceptance verification

- [x] Source registry implemented with approval status (`TEST_EXECUTED`).
- [x] Source provenance retained in chunk metadata (`CODE_INSPECTED`, `DATABASE_VERIFIED`).
- [x] Ingestion pipeline operational (`POST /api/v1/knowledge/ingest` 202 Accepted) (`TEST_EXECUTED`).
- [x] pgvector retrieval operational in Neon PostgreSQL (`DATABASE_VERIFIED`).
- [x] Retrieval evaluation runner exists (`RAGEvaluationRunner` tested) (`TEST_EXECUTED`).
- [x] Telugu retrieval tested and verified (`TEST_EXECUTED`).
- [x] Hindi retrieval verified (`CODE_INSPECTED`, `TEST_EXECUTED`).
- [x] English retrieval verified (`TEST_EXECUTED`).
- [x] Citation correctness verified against source document (`TEST_EXECUTED`).
- [x] Agricultural safety safeguards tested (`TEST_EXECUTED`).
- [x] Insufficient-evidence abstention works cleanly (`TEST_EXECUTED`).

**Stage 05 Audit Determination:** `COMPLETE_VERIFIED` (Fully implemented, tested, and operational with strict safety abstentions).
