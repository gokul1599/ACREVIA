"""
ACREVIA Backend - KrishiBrain Agricultural Knowledge, RAG & Citation Test Suite.
"""

from fastapi.testclient import TestClient
from backend.app.services.knowledge.evaluation.evaluation_runner import RAGEvaluationRunner
from backend.app.services.knowledge.evaluation.eval_dataset import KNOWLEDGE_EVALUATION_DATASET


def test_register_knowledge_source_rbac(client: TestClient, admin_token, farmer_token):
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_farmer = {"Authorization": f"Bearer {farmer_token}"}

    payload = {
        "publisher_name": "PJTSAU Agricultural University",
        "publisher_type": "UNIVERSITY",
        "official_domain": "pjtsau.edu.in",
        "authority_level": 1.0,
        "licensing_status": "GOVERNMENT_OPEN_ACCESS"
    }

    # 1. Admin can register source -> 201 Created
    admin_resp = client.post("/api/v1/knowledge/sources", json=payload, headers=headers_admin)
    assert admin_resp.status_code == 201
    source_data = admin_resp.json()
    assert source_data["publisher_name"] == "PJTSAU Agricultural University"
    assert source_data["approval_status"] == "APPROVED"

    # 2. Regular farmer cannot register source -> 403 Forbidden
    farmer_resp = client.post("/api/v1/knowledge/sources", json=payload, headers=headers_farmer)
    assert farmer_resp.status_code == 403


def test_ingest_document_and_query_citations(client: TestClient, admin_token, farmer_token):
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_farmer = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Register Source
    source_resp = client.post(
        "/api/v1/knowledge/sources",
        json={
            "publisher_name": "ICAR-CICR Cotton Institute",
            "publisher_type": "RESEARCH_COUNCIL",
            "official_domain": "cicr.org.in",
            "authority_level": 1.0,
            "licensing_status": "OPEN_ACCESS"
        },
        headers=headers_admin
    )
    assert source_resp.status_code == 201
    source_id = source_resp.json()["id"]

    # 2. Ingest Document
    sample_text = (
        "# Cotton Integrated Pest Management\n\n"
        "## Pink Bollworm Management\n"
        "Pink bollworm (Pectinophora gossypiella) is a major destructive pest of cotton in Telangana.\n"
        "Install 8 pheromone traps per hectare for pest monitoring and 20 traps per hectare for mass trapping.\n"
        "Collect and destroy rosette flowers in early season. Follow CIBRC approved bio-pesticide protocols.\n\n"
        "## Irrigation Schedule\n"
        "Cotton requires critical irrigation during flowering and boll formation stages in black cotton soils."
    )
    files = {
        "file": ("cotton_ipm_guide.md", sample_text.encode("utf-8"), "text/markdown")
    }
    form_data = {
        "source_id": source_id,
        "title": "Telangana Cotton IPM Package of Practices",
        "document_type": "MARKDOWN",
        "primary_language": "en",
        "crop_scope": "cotton",
        "region_scope": "Telangana"
    }

    ingest_resp = client.post(
        "/api/v1/knowledge/ingest",
        data=form_data,
        files=files,
        headers=headers_admin
    )
    assert ingest_resp.status_code == 202
    job_data = ingest_resp.json()
    assert job_data["status"] == "COMPLETED"
    assert job_data["progress_pct"] == 100

    # 3. Farmer Queries Grounded Knowledge
    query_payload = {
        "question": "How do I manage Pink Bollworm in cotton using pheromone traps?",
        "language": "en",
        "crop": "cotton"
    }
    query_resp = client.post("/api/v1/knowledge/query", json=query_payload, headers=headers_farmer)
    assert query_resp.status_code == 200
    q_data = query_resp.json()
    assert q_data["answer_status"] == "ANSWERED"
    assert "Pink bollworm" in q_data["answer"]
    assert len(q_data["citations"]) >= 1
    citation = q_data["citations"][0]
    assert citation["publisher"] == "ICAR-CICR Cotton Institute"
    assert "pink bollworm" in citation["content_snippet"].lower()


def test_knowledge_query_abstention_on_unsupported_topic(client: TestClient, farmer_token):
    headers = {"Authorization": f"Bearer {farmer_token}"}
    query_payload = {
        "question": "How do I cultivate cold-weather Arctic blueberries in the Sahara desert sands?",
        "language": "en",
        "crop": "cotton"
    }
    resp = client.post("/api/v1/knowledge/query", json=query_payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["answer_status"] == "INSUFFICIENT_EVIDENCE"
    assert data["evidence_strength"] == "INSUFFICIENT"
    assert len(data["citations"]) == 0
    assert "not available" in data["answer"].lower()


def test_knowledge_query_high_risk_advice_safety(client: TestClient, farmer_token):
    headers = {"Authorization": f"Bearer {farmer_token}"}
    query_payload = {
        "question": "What is the extreme chemical pesticide dose to spray all pests at once?",
        "language": "en",
        "crop": "cotton"
    }
    resp = client.post("/api/v1/knowledge/query", json=query_payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["requires_expert_review"] is True
    assert data["answer_status"] == "REQUIRES_EXPERT_REVIEW"


def test_multilingual_telugu_query(client: TestClient, admin_token, farmer_token):
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_farmer = {"Authorization": f"Bearer {farmer_token}"}

    # Ingest Telugu material
    source_resp = client.post(
        "/api/v1/knowledge/sources",
        json={
            "publisher_name": "PJTSAU వరంగల్ కృషి విజ్ఞాన కేంద్రం",
            "publisher_type": "KVK",
            "official_domain": "pjtsau.edu.in",
            "authority_level": 1.0,
            "licensing_status": "OPEN_ACCESS"
        },
        headers=headers_admin
    )
    source_id = source_resp.json()["id"]

    te_text = (
        "# పత్తి యాజమాన్య పద్ధతులు\n\n"
        "## గులాబీ రంగు కాయతొలుచు పురుగు\n"
        "పత్తిలో గులాబీ రంగు కాయతొలుచు పురుగు నివారణకు ఎకరానికి 8 లింగాకర్షక బుట్టలు అమర్చాలి.\n"
        "ఆరంభ దశలో రాలిపోయిన పూత మరియు గులాబీ రంగు పువ్వులను ఏరి నాశనం చేయాలి."
    )
    client.post(
        "/api/v1/knowledge/ingest",
        data={
            "source_id": source_id,
            "title": "పత్తి సమగ్ర సస్యరక్షణ మార్గదర్శకాలు",
            "document_type": "MARKDOWN",
            "primary_language": "te",
            "crop_scope": "cotton"
        },
        files={"file": ("cotton_te.md", te_text.encode("utf-8"), "text/markdown")},
        headers=headers_admin
    )

    # Query in Telugu
    resp = client.post(
        "/api/v1/knowledge/query",
        json={
            "question": "పత్తిలో గులాబీ రంగు పురుగు నివారణకు లింగాకర్షక బుట్టలు ఎలా వాడాలి?",
            "language": "te",
            "crop": "cotton"
        },
        headers=headers_farmer
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["language"] == "te"
    assert data["answer_status"] == "ANSWERED"
    assert "లింగాకర్షక బుట్టలు" in data["answer"]


def test_knowledge_feedback_workflow(client: TestClient, farmer_token):
    headers = {"Authorization": f"Bearer {farmer_token}"}
    feedback_payload = {
        "query_id": "test-query-uuid-12345",
        "issue_category": "MISSING_CITATION",
        "user_comments": "The answer mentions irrigation timing but page reference was missing."
    }
    resp = client.post("/api/v1/knowledge/feedback", json=feedback_payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["query_id"] == "test-query-uuid-12345"
    assert data["reviewer_status"] == "SUBMITTED"


def test_knowledge_query_tenant_isolation(client: TestClient, sample_farm, second_farmer_token):
    """
    SECURITY TEST: Farmer B tries to attach Farmer A's farm_id in knowledge query.
    verify_farm_access must reject with HTTP 403 Forbidden.
    """
    headers = {"Authorization": f"Bearer {second_farmer_token}"}
    payload = {
        "question": "What is the best fertilizer for cotton?",
        "farm_id": sample_farm.id  # Belongs to Farmer A
    }
    resp = client.post("/api/v1/knowledge/query", json=payload, headers=headers)
    assert resp.status_code == 403


def test_rag_evaluation_runner(db_session):
    """Smoke test for the 45 evaluation cases runner."""
    sample_cases = KNOWLEDGE_EVALUATION_DATASET[:6]
    report = RAGEvaluationRunner.evaluate(db=db_session, dataset=sample_cases)
    assert report["total_queries_evaluated"] == 6
    assert "mean_latency_ms" in report
    assert report["validation_status"] == "DRAFT_NOT_EXPERT_VALIDATED"
