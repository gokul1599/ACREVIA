# ACREVIA — AI PROVIDER FALLBACK & RAG GROUNDING VERIFICATION REPORT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Module:** Groq AI Client & KrishiBrain Agronomic RAG Service  
**Execution Date:** November 9, 2026  
**Status:** `D4_STATUS = INDEPENDENTLY_VERIFIED_CODE_LEVEL`

---

## 1. Provider Classification & Architectural Boundaries

In accordance with Work Package 08, the AI model fallback mechanism is formally classified as:

```text
AI_RESILIENCE_CLASSIFICATION = SAME_PROVIDER_MULTI_MODEL_FALLBACK
PROVIDER_NAME = GroqCloud
MODELS_IN_CHAIN = [
    1. "qwen/qwen3.8-27b",          # Primary multilingual reasoning model
    2. "llama-3.3-70b-versatile",   # Secondary high-capacity fallback model
    3. "llama-3.1-8b-instant"       # Tertiary high-throughput emergency model
]
```

### Critical Architectural Honesty:
All three models are hosted on GroqCloud infrastructure. Therefore, this fallback architecture protects against individual model deprecations, model context errors, and model-specific rate limits, but does **NOT** provide independent multi-cloud provider redundancy if GroqCloud experiences a global platform outage or DNS failure.

---

## 2. Deterministic Agronomic Fallback (PJTSAU Vector RAG)

When GroqCloud is unreachable, times out (exceeding 3s), or all 3 models return HTTP 429, the system automatically and deterministically falls back to the local, offline-capable vector RAG advisory pipeline (`PJTSAU_GROUNDED_RAG`).

### Agronomic Corpus Verification:
- **Corpus Location:** `backend/app/database/init_db.py` and `backend/app/services/agronomic_advisory.py`.
- **Target Institution:** Professor Jayashankar Telangana State Agricultural University (PJTSAU), Rajendranagar, Hyderabad.
- **Audited Bulletins:**
  - *"PJTSAU Rice Diagnostic Bulletin (2022)"* (Rice Blast, Sheath Blight rules).
  - *"ICAR-IIRR Hyderabad Blast Surveillance"* (Epidemiological weather triggers).
  - *"PJTSAU Plant Pathology Compendium"* (Foliar cotton and chilli management).
  - *"ICAR-NRRI Cuttack Guidelines"* (Waterlogging and nutrient guidance).
- **Abstention Safeguards:**
  If an agricultural query is submitted for an unverified crop or outside Telangana agro-climatic zones, the system does NOT hallucinate advice. It returns a structured abstention response requesting expert consultation via ExpertConnect.

---

## 3. Resilience Test Results (5 Tests Passing)

All 5 tests in `backend/tests/test_groq_client_resilience.py` pass cleanly:
1. `test_unconfigured_client_returns_deterministic_fallback`: Unset API key triggers grounded RAG.
2. `test_primary_model_success`: Valid 200 OK inference with token metrics.
3. `test_primary_model_404_falls_back_to_secondary`: Automatic model rollover on 404/429/5xx.
4. `test_all_models_fail_returns_structured_rag_degradation`: Graceful fallback to PJTSAU RAG.
5. `test_health_check_detects_fallbacks_and_active_status`: Live model catalog inspection without secret leakage.
