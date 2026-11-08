# ACREVIA — STAGE 04 TEST SUITE REPORT
## Complete Execution Telemetry, Pass Rates & Regression Coverage

**Document Reference:** `docs/finalization/stage-04/STAGE_04_TEST_REPORT.md`  
**Stage:** 04 — KrishiBrain Multilingual Multimodal Agricultural RAG Intelligence Engine  
**Execution Timestamp:** 2026-11-08T16:19:33+05:30  
**Test Harness:** `pytest 9.2.0` on CPython `3.11.16` (win32)  

---

### 1. Test Suite Execution Summary

| Test Suite Module | Target Scope | Total Items | Passed | Failed | Duration | Status |
|---|---|---|---|---|---|---|
| `backend/tests/test_knowledge.py` | KrishiBrain Endpoints, RBAC, Ingestion, Citations, Multilingual, Abstention, Tenant Isolation & Batch Evaluation | 8 | 8 | 0 | 33.23s | **100% PASS** |
| `tests/ml/` & `ml/inference_service/` | Stage 03 Computer Vision, Calibration, Abstention & Microservice Regression Suite | 56 | 56 | 0 | 41.49s | **100% PASS** |
| **Platform Total** | **Combined Verified Suites** | **64** | **64** | **0** | **74.72s** | **100% PASS** |

---

### 2. Itemized KrishiBrain Test Results

```text
============================= test session starts =============================
platform win32 -- Python 3.11.16, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\gokul\OneDrive\Documents\projects
plugins: anyio-4.16.0
collected 8 items

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

---

### 3. Detailed Verification Breakdown

1. **`test_register_knowledge_source_rbac`:** Confirmed that admins and agricultural experts can register publishers (HTTP 201), while unprivileged farmers are blocked (HTTP 403).
2. **`test_ingest_document_and_query_citations`:** Validated end-to-end markdown extraction, structure-aware chunking, vector embedding, and query retrieval with structured publisher and heading citations.
3. **`test_knowledge_query_abstention_on_unsupported_topic`:** Validated that querying topics outside indexed evidence triggers safe abstention (`INSUFFICIENT_EVIDENCE`) without hallucinated claims.
4. **`test_knowledge_query_high_risk_advice_safety`:** Confirmed that requests for lethal pesticide overdoses are intercepted by the safety guard, resulting in `answer_status: "REQUIRES_EXPERT_REVIEW"` and `requires_expert_review: True`.
5. **`test_multilingual_telugu_query`:** Validated that vernacular Telugu queries match native Telugu documents and emit verified Telugu citations and advice.
6. **`test_knowledge_feedback_workflow`:** Confirmed that farmer ratings, citation accuracy scores, and user comments are persisted in `knowledge_feedback`.
7. **`test_knowledge_query_tenant_isolation`:** Confirmed that attempting to query with an unauthorized farm ID belonging to another tenant is blocked with HTTP 403 Forbidden.
8. **`test_rag_evaluation_runner`:** Executed the full 45-case gold evaluation suite, asserting 100% safety compliance and generating empirical benchmark telemetry.
