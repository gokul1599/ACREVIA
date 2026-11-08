# Document Ingestion Architecture & Pipeline Specification
**ACREVIA — Agricultural Intelligence Platform (Stage 5)**  
*Document Version:* 1.0.0  
*Target Formats:* PDF, DOCX, HTML, Markdown, Plain Text  
*Component Scope:* Document Parsers, Structure-Aware Chunker, Ingestion Service & Job Tracker

---

## 1. Document Ingestion Objectives

Agricultural knowledge publications from agricultural universities (PJTSAU), national research bodies (ICAR-CICR, ICAR-IIRR), and state agricultural departments vary drastically in structure and format:
- Comprehensive 100+ page PDF packages of practices (POP).
- Extension brochures in DOCX/Word format.
- Web-based agricultural advisories and bulletins in HTML.
- Internal curated clinical guides in Markdown.

The KrishiBrain ingestion engine transforms these raw multi-format publications into structured, traceable, citation-ready knowledge units while guaranteeing cryptographic provenance and idempotency.

---

## 2. Ingestion Pipeline & State Machine

Every document ingestion undergoes a six-stage transactional state machine tracked via the `ingestion_jobs` table:

```
    [Upload Document]
           │
           ▼
    ┌──────────────┐
    │   PENDING    │ ───► Validate Role (ADMIN / RESEARCHER), Source & Content
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  EXTRACTING  │ ───► Format Detection (PDF / DOCX / HTML / MD) & Metadata Extraction
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   CHUNKING   │ ───► Structure-Aware Hierarchy & Physical Page Tracking
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  EMBEDDING   │ ───► 1536d Vector Generation & Database Persistence
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  COMPLETED   │ ───► Chunks & Version Marked APPROVED; Audit Log Recorded
    └──────────────┘
           │
       (On Error)
           ▼
    ┌──────────────┐
    │    FAILED    │ ───► Error Message Stored, Retry Counter Incremented
    └──────────────┘
```

---

## 3. Format Extractors (`DocumentExtractor`)

The extraction layer decouples file-specific binary decoding from downstream text processing:

### 3.1 PDF Extraction (`pypdf`)
- Iterates over physical pages sequentially.
- Extracts raw text per page while maintaining exact physical page numbers (`page_num = idx + 1`).
- Identifies bold or uppercase heading lines as section delineators.

### 3.2 DOCX Extraction (`python-docx`)
- Traverses document paragraphs and table blocks in document order.
- Utilizes paragraph styles (`Heading 1`, `Heading 2`, `Heading 3`, `Title`) to construct hierarchical document trees.
- Estimates physical page intervals based on character density (approx. 450 words per page).

### 3.3 HTML Extraction (`beautifulsoup4` + `lxml`)
- Strips non-content boilerplate: `<script>`, `<style>`, `<nav>`, `<footer>`, `<aside>`.
- Preserves `<h1>` through `<h6>` tags as semantic heading boundaries.
- Formats `<table>` data into clean pipe-delimited text representations.

### 3.4 Markdown & Plain Text Extraction
- Directly parses ATX heading tokens (`#`, `##`, `###`).
- Preserves bulleted lists, diagnostic tables, and chemical dosage summaries.

---

## 4. Structure-Aware Chunker (`StructureAwareChunker`)

Naive fixed-window chunking destroys agricultural context (e.g., splitting a pesticide name from its recommended dosage). KrishiBrain employs a **structure-aware, hierarchy-preserving chunker**:

### 4.1 Hierarchy Preservation
- Chunks track their ancestral heading path (e.g., `Cotton > Integrated Pest Management > Pink Bollworm > Trap Setup`).
- This heading path is indexed and returned with every citation, allowing farmers and agronomists to instantly understand the diagnostic context.

### 4.2 Bounding Constraints
- **Target Size:** 300 to 500 tokens (or ~1200 to 2000 characters).
- **Maximum Bounding:** 800 tokens.
- **Sliding Overlap:** 50 tokens between contiguous chunks within the same section to preserve boundary semantics.
- **Section Integrity:** Headings trigger new chunk boundaries; content is never merged across unrelated agronomic topics.

### 4.3 Page Coordinate Retention
- Every chunk records `page_start` and `page_end`.
- When an agronomist reviews a recommendation, KrishiBrain cites the exact physical page of the official publication for instant verification.

---

## 5. Cryptographic Hashing, Provenance & Deduplication

To prevent duplicate processing and guarantee data integrity:

1. **Document-Level SHA-256:**
   - On ingest, `sha256(raw_bytes)` is calculated.
   - If an existing version of the document has identical hash, the ingestion completes idempotently without re-embedding.

2. **Chunk-Level SHA-256:**
   - Each chunk computes:  
     $$\text{content\_hash} = \text{SHA256}(\text{heading\_path} + "::" + \text{content})$$
   - Prevents duplicate chunks from accumulating in the vector index.

3. **Immutable Versioning:**
   - Modifying a document creates a new `KnowledgeDocumentVersion` record (`version_number = N + 1`).
   - Prior versions, chunks, and citations remain immutable in the historical archive.

---

## 6. Access Control & Governance

- **Source Registration:** Restricted to users with the `ADMIN` role.
- **Document Ingestion:** Restricted to `ADMIN` and `RESEARCHER` roles.
- **Direct Queries:** Accessible to authenticated `FARMER`, `EXPERT`, and `ADMIN` roles.
- **Audit Logging:** Every ingestion attempt, state transition, and error is logged in the `AuditLog` table with user and correlation IDs.
