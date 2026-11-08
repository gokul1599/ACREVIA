# KrishiBrain Knowledge API Specifications & Contracts
**ACREVIA — Agricultural Intelligence Platform (Stage 5)**  
*Document Version:* 1.0.0  
*Base URL Path:* `/api/v1/knowledge`  
*Auth Protocol:* Bearer JWT (`Authorization: Bearer <token>`)  
*Content-Type:* `application/json` (or `multipart/form-data` for ingestion)

---

## 1. Overview & RBAC Permissions Matrix

All knowledge endpoints enforce strict Role-Based Access Control (RBAC):

| Endpoint | HTTP Method | Role Required | Description |
| :--- | :---: | :---: | :--- |
| `/api/v1/knowledge/sources` | `POST` | `ADMIN` | Register a new institutional knowledge source |
| `/api/v1/knowledge/sources` | `GET` | Authenticated | List all verified knowledge publishers |
| `/api/v1/knowledge/ingest` | `POST` | `ADMIN`, `RESEARCHER` | Upload and trigger asynchronous document ingestion |
| `/api/v1/knowledge/jobs/{job_id}` | `GET` | `ADMIN`, `RESEARCHER` | Poll progress and status of an ingestion job |
| `/api/v1/knowledge/query` | `POST` | `FARMER`, `EXPERT`, `ADMIN` | Query evidence-grounded knowledge with citations |
| `/api/v1/knowledge/feedback` | `POST` | `FARMER`, `EXPERT`, `ADMIN` | Submit quality and citation feedback on an answer |
| `/api/v1/knowledge/evaluation/run` | `POST` | `ADMIN`, `RESEARCHER` | Execute the 45-case automated benchmark suite |

---

## 2. Endpoint Specifications

### 2.1 Register Knowledge Source
`POST /api/v1/knowledge/sources`

#### Request Headers
```http
Authorization: Bearer <admin_jwt>
Content-Type: application/json
```

#### Request Body (`KnowledgeSourceCreate`)
```json
{
  "publisher_name": "PJTSAU Regional Agricultural Research Station",
  "publisher_type": "STATE_AGRICULTURAL_UNIVERSITY",
  "official_domain": "pjtsau.edu.in",
  "authority_level": 1.0,
  "licensing_status": "OPEN_ACCESS"
}
```

#### Response (`201 Created`)
```json
{
  "id": "73b1c028-7a58-4273-bcda-cfc4e191ad98",
  "publisher_name": "PJTSAU Regional Agricultural Research Station",
  "publisher_type": "STATE_AGRICULTURAL_UNIVERSITY",
  "official_domain": "pjtsau.edu.in",
  "authority_level": 1.0,
  "licensing_status": "OPEN_ACCESS",
  "is_approved": true,
  "created_at": "2026-11-08T03:15:33Z"
}
```

---

### 2.2 Upload & Ingest Publication
`POST /api/v1/knowledge/ingest`

#### Request Headers
```http
Authorization: Bearer <admin_or_researcher_jwt>
Content-Type: multipart/form-data
```

#### Form Parameters
- `source_id` (string, UUID, required): ID of registered knowledge source.
- `title` (string, required): Title of publication.
- `document_type` (string, required): `PDF` | `DOCX` | `HTML` | `MARKDOWN` | `TEXT`.
- `primary_language` (string, required): `en` | `te` | `hi`.
- `crop_scope` (string, required): `cotton` | `rice` | `chilli` | `all`.
- `region_scope` (string, optional, default: `Telangana`).
- `file` (binary, required): Document file payload.

#### Response (`202 Accepted`)
```json
{
  "id": "7a5f5cd4-eac7-4236-b777-0ca46d8143f9",
  "document_id": "0c47f4f1-6d45-40b1-a86d-46b1bdaa2895",
  "status": "COMPLETED",
  "progress_pct": 100,
  "error_message": null,
  "retry_count": 0,
  "created_at": "2026-11-08T03:15:33Z",
  "completed_at": "2026-11-08T03:15:33Z"
}
```

---

### 2.3 Query Grounded Knowledge
`POST /api/v1/knowledge/query`

#### Request Headers
```http
Authorization: Bearer <user_jwt>
Content-Type: application/json
```

#### Request Body (`KnowledgeQueryRequest`)
```json
{
  "question": "వరి పంటలో సుడి దోమ నివారణకు ఎలాంటి చర్యలు తీసుకోవాలి?",
  "language": "te",
  "crop": "rice",
  "growth_stage": "TILLERING",
  "max_citations": 3
}
```

#### Response (`200 OK - Answered State`)
```json
{
  "query_id": "ca3215f1-df9c-40e0-9341-5c53c3e9c838",
  "answer_status": "ANSWERED",
  "language": "te",
  "answer": "అధికారిక ఆధారాలు (PJTSAU - Telangana Rice Package of Practices):\n\nవరిలో సుడి దోమ (Brown Planthopper) నివారణకు పొలంలో నీటిని ఎప్పటికప్పుడు తీసివేసి ఆరబెట్టాలి. ప్రతి 2 మీటర్ల దూరంలో 20 సెం.మీ వెడల్పు గల కాలిబాటలు తీయాలి. నత్రజని ఎరువులను అధికంగా వాడకూడదు.\n\nగమనిక: క్రిమిసంహారక మరియు ఎరువుల వాడకంలో CIBRC లేబుల్ మార్గదర్శకాలను పాటించండి.",
  "evidence_strength": "STRONG",
  "citations": [
    {
      "source_title": "Telangana Rice Package of Practices",
      "publisher": "PJTSAU Regional Agricultural Research Station",
      "canonical_url": "https://pjtsau.edu.in/publications/rice_pop.pdf",
      "document_version": 1,
      "page_start": 42,
      "page_end": 43,
      "heading_path": "Rice > Pest Management > Brown Planthopper",
      "content_snippet": "వరిలో సుడి దోమ (Brown Planthopper) నివారణకు పొలంలో నీటిని ఎప్పటికప్పుడు తీసివేసి ఆరబెట్టాలి...",
      "relevance_score": 0.884
    }
  ],
  "limitations": [
    "క్షేత్రస్థాయి పంట దశ మరియు వాతావరణ పరిస్థితులపై ఆధారపడి ఫలితాలు మారవచ్చు."
  ],
  "follow_up_questions": [
    "పంట ప్రస్తుత దశ ఏమిటి?",
    "పొలంలో నీటి పారుదల సౌకర్యం ఉందా?"
  ],
  "requires_expert_review": false,
  "execution_time_ms": 32.4
}
```

#### Response (`200 OK - Abstention State`)
```json
{
  "query_id": "9d1b7a21-7b19-4a9f-a2e1-4c5512d78901",
  "answer_status": "INSUFFICIENT_EVIDENCE",
  "language": "en",
  "answer": "Sufficient evidence-backed agricultural documentation is not available in the verified registry for this question. Please consult your local Krishi Vigyan Kendra (KVK) agronomist.",
  "evidence_strength": "INSUFFICIENT",
  "citations": [],
  "limitations": [
    "No approved source in the knowledge registry satisfies the query constraints."
  ],
  "follow_up_questions": [
    "Would you like to request an expert review via ExpertConnect?"
  ],
  "requires_expert_review": true,
  "execution_time_ms": 11.2
}
```

---

### 2.4 Submit Knowledge Feedback
`POST /api/v1/knowledge/feedback`

#### Request Body (`KnowledgeFeedbackCreate`)
```json
{
  "query_id": "ca3215f1-df9c-40e0-9341-5c53c3e9c838",
  "rating": 5,
  "is_helpful": true,
  "citation_accuracy_score": 1.0,
  "comments": "Exact match with university recommendations for Khammam district."
}
```

#### Response (`201 Created`)
```json
{
  "id": "e89c0901-b214-419b-a010-891040182741",
  "query_id": "ca3215f1-df9c-40e0-9341-5c53c3e9c838",
  "rating": 5,
  "is_helpful": true,
  "citation_accuracy_score": 1.0,
  "comments": "Exact match with university recommendations for Khammam district.",
  "created_at": "2026-11-08T03:15:35Z"
}
```
