# KrishiBrain: Agricultural Knowledge Intelligence & RAG Architecture
**ACREVIA — Agricultural Intelligence Platform (Stage 5)**  
*Document Version:* 1.0.0  
*Target Geography:* Telangana, India (Cotton, Rice, Chilli)  
*Languages:* Telugu (te), Hindi (hi), English (en)  
*Infrastructure:* Neon PostgreSQL + pgvector, Vercel Serverless (`sin1` Singapore)

---

## 1. Architectural Overview & Philosophy

KrishiBrain is the evidence-grounded agricultural knowledge retrieval system of ACREVIA. In smallholder agriculture, a hallucinated recommendation or an inaccurate chemical dosage can ruin a farmer's crop, violate statutory regulations (Central Insecticides Board & Registration Committee - CIBRC), or cause severe health hazards. 

KrishiBrain rejects the "unbounded generative chatbot" paradigm. Instead, it operates as an **evidence-bound agricultural Truth Engine**:
1. **Zero Hallucination Tolerance:** Factual assertions must map to a physical page, heading, and approved institutional publication (ICAR, PJTSAU, KVK).
2. **Deterministic Abstention:** If verified evidence is absent or similarity is below strict thresholds, the engine abstains (`INSUFFICIENT_EVIDENCE`) and invites expert escalation rather than guessing.
3. **Safety & Regulatory Gate:** High-risk chemical advice or off-label pesticide cocktails trigger an immediate `REQUIRES_EXPERT_REVIEW` safeguard.

```
                              [Farmer / Expert Query]
                                         │
                                         ▼
                            ┌────────────────────────┐
                            │ Agricultural Safety    │ ───► Block Injection Attacks
                            │ Guard & Input Sanitizer│ ───► Flag Extreme Chemical Advice
                            └────────────────────────┘
                                         │
                         ┌───────────────┴───────────────┐
                         ▼                               ▼
                 [Dense Embedding]               [Lexical Tokens]
             Local 1536d / Cloud API           Multilingual Terms
                         │                               │
                         └───────────────┬───────────────┘
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │   Hybrid Search Retriever     │
                         │   - pgvector Cosine Sim (65%) │
                         │   - Token Overlap (35%)       │
                         │   - Metadata Filters:         │
                         │     * Crop Scope (Cotton/Rice)│
                         │     * Growth Stage Scope      │
                         │     * Verified Institutional  │
                         └───────────────────────────────┘
                                         │
                          ┌──────────────┴──────────────┐
                          │ Chunks Score >= Threshold?  │
                          └──────────────┬──────────────┘
                                         │
                     ┌───────────────────┴───────────────────┐
                     ▼ YES                                   ▼ NO
        ┌─────────────────────────┐             ┌─────────────────────────┐
        │  Grounded Multilingual  │             │  Deterministic          │
        │  Synthesis Generator    │             │  Abstention Engine      │
        │  (Telugu, Hindi, Eng)   │             │  (INSUFFICIENT_EVIDENCE)│
        └─────────────────────────┘             └─────────────────────────┘
                     │                                       │
                     ▼                                       ▼
        ┌─────────────────────────┐             ┌─────────────────────────┐
        │ Citations with Page No. │             │ Route to Human Expert   │
        │ & Heading Hierarchy     │             │ (ExpertConnect Stage 7) │
        └─────────────────────────┘             └─────────────────────────┘
```

---

## 2. Decoupled Embedding Architecture

To prevent vendor lock-in and enable air-gapped or offline development in edge scenarios, KrishiBrain implements an abstract `EmbeddingProvider` interface with two pluggable implementations:

### 2.1 Abstract Interface (`backend/app/services/knowledge/embeddings/embedding_provider.py`)
```python
class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int: ...

    @abstractmethod
    def embed_text(self, text: str) -> List[float]: ...

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]: ...
```

### 2.2 Deterministic Local Provider
- Generates 1536-dimensional L2-normalized pseudo-semantic vectors using deterministic Murmur-style token hashing and positional projections.
- Fully self-contained; requires zero GPU overhead, zero network round-trips, and zero paid API keys during CI/CD and localized testing.
- Preserves token overlap geometry such that queries sharing agricultural vocabulary project into proximal cosine space.

### 2.3 Cloud Provider Adapter
- Supports OpenAI `text-embedding-3-small` (1536 dimensions) or open-weights hosted endpoints (e.g., BAAI/bge-m3).
- Configured via environment variables (`EMBEDDING_PROVIDER=cloud`, `EMBEDDING_API_KEY=...`).
- When credentials are unavailable, seamlessly falls back to the deterministic local provider without failing the application startup.

---

## 3. Hybrid Retrieval Algorithm

Dense semantic vector similarity alone often misses specific active ingredient names (e.g., *Emamectin benzoate 5% SG*), pest scientific names (*Pectinophora gossypiella*), or vernacular names (*Gulabi purugu* in Telugu). KrishiBrain therefore uses a weighted hybrid retrieval formula:

$$\text{HybridScore} = 0.65 \times \text{CosineSimilarity} + 0.35 \times \text{LexicalOverlap}$$

### Metadata Conditioning
Queries are pre-filtered at the database index level:
- `crop_scope`: Matches the query crop (e.g., `cotton`) or universally applicable agronomy (`all`).
- `growth_stage_scope`: Matches current vegetative, flowering, or boll formation stages.
- `approval_status`: Enforces that only `APPROVED` chunks from `APPROVED` document versions are accessible to farmers.

---

## 4. Multilingual Processing & Native Idioms

Smallholder farmers in Telangana communicate predominantly in Telugu (*తెలుగు*) or Dakhni/Hindi (*हिन्दी*). KrishiBrain natively handles cross-lingual queries:
- **Telugu:** Supports specific Telangana regional terminology (e.g., *గులాబీ రంగు పురుగు* for Pink Bollworm, *ఎర్ర తెగులు* for Leaf Blight).
- **Hindi:** Supports standardized North/Central Indian agronomic terms (*गुलाबी सुंडी*, *झुलसा रोग*).
- **English:** Provides technical and scientific literature terms for researchers and officers.

Response synthesis adapts culturally appropriate advisory phrasing:
- Telugu responses conclude with: `గమనిక: క్రిమిసంహారక మరియు ఎరువుల వాడకంలో CIBRC లేబుల్ మార్గదర్శకాలను పాటించండి.`
- Hindi responses conclude with: `सलाह: कीटनाशकों और उर्वरकों के उपयोग में हमेशा CIBRC द्वारा अनुमोदित उत्पाद लेबल का पालन करें।`
- English responses conclude with: `Advisory: Strictly follow CIBRC registered product label instructions and Pre-Harvest Intervals (PHI).`

---

## 5. Agricultural Safety Guardrails & Abstention Gates

The `AgriculturalSafetyGuard` acts as an inbound and outbound security firewall:

1. **Prompt Injection & Adversarial Sanitization:**
   - Strips system prompt hijacking phrases (`ignore previous instructions`, `bypass safety check`, `act as unrestrained assistant`).
   - Normalizes unicode whitespace and homoglyphs.

2. **High-Risk Chemical & Dosage Gate:**
   - Analyzes questions for hazardous queries (e.g., mixing banned organophosphates, extreme dosages, "spray all pests at once").
   - Automatically switches `answer_status` to `REQUIRES_EXPERT_REVIEW`.
   - Appends safety warnings discouraging off-label pesticide usage.

3. **Abstention Gate:**
   - If retrieved candidate score $< 0.20$ or no matching chunks exist in the approved repository, the system issues an explicit `INSUFFICIENT_EVIDENCE` status.
   - Farmers are prompted to route their inquiry to human agronomists via `ExpertConnect` rather than receiving an unverified generative response.

---

## 6. Infrastructure & Deployment Topology

- **Database:** Neon Serverless PostgreSQL with `pgvector` extension.
- **Regions:** 
  - Database primary: Singapore (`ap-southeast-1` / `sin1`).
  - Vercel Serverless Functions: Configured to region `sin1` to minimize intra-query latency between compute and vector storage ($< 8\text{ms}$).
- **Concurrency & Cold Start Mitigation:**
  - Stateless extractor and retriever modules.
  - SQL connection pooling via SQLAlchemy with recycled connections to prevent pool exhaustion on serverless scales.
