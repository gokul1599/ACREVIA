"""
ACREVIA - Stage 8 Comprehensive End-to-End System Validation Suite.
Validates Workflows A through H across full domain integrations, security boundaries, and telemetry.
"""

from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.farm import Farm, Plot
from backend.app.models.crop import CropSeason


# =========================================================================
# WORKFLOW A: Full Farmer Onboarding Lifecycle
# =========================================================================
def test_workflow_a_farmer_onboarding(client: TestClient, db_session: Session):
    """
    Workflow A:
    1. Farmer registers new account (Telugu language preference).
    2. Logs in to obtain JWT bearer token.
    3. Creates a farm in Telangana (Warangal district).
    4. Creates a plot with Black Cotton Soil.
    5. Creates a Kharif Cotton crop season.
    """
    # 1. Register
    reg_payload = {
        "phone": "+919848012345",
        "full_name": "K. Venkatesh",
        "password": "AcreviaSecurePass2026!",
        "language_preference": "te"
    }
    res_reg = client.post("/api/v1/auth/register", json=reg_payload)
    assert res_reg.status_code == 201

    # 2. Login
    login_payload = {
        "phone": "+919848012345",
        "password": "AcreviaSecurePass2026!"
    }
    res_login = client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Farm
    farm_payload = {
        "name": "Venkatesh Cotton Estate",
        "state": "Telangana",
        "district": "Warangal",
        "mandal": "Geesugonda",
        "village": "Dharmaram",
        "total_acreage": 4.5
    }
    res_farm = client.post("/api/v1/farms/", json=farm_payload, headers=headers)
    assert res_farm.status_code == 201
    farm_id = res_farm.json()["id"]
    assert res_farm.json()["district"] == "Warangal"

    # 4. Create Plot
    plot_payload = {
        "name": "North Field - Plot 1",
        "soil_type": "BLACK_COTTON",
        "irrigation_source": "BOREWELL",
        "acreage": 2.5
    }
    res_plot = client.post(f"/api/v1/farms/{farm_id}/plots", json=plot_payload, headers=headers)
    assert res_plot.status_code == 201
    plot_id = res_plot.json()["id"]

    # 5. Create Crop Season
    season_payload = {
        "plot_id": plot_id,
        "crop_id": "cotton",
        "season_type": "KHARIF",
        "sowing_date": "2026-06-15",
        "current_stage": "VEGETATIVE"
    }
    res_season = client.post(f"/api/v1/plots/{plot_id}/seasons", json=season_payload, headers=headers)
    assert res_season.status_code == 201
    assert res_season.json()["crop_id"] == "cotton"
    assert res_season.json()["status"] == "ACTIVE"


# =========================================================================
# WORKFLOW B: Crop Diagnosis & Image Quality Gate
# =========================================================================
def test_workflow_b_crop_diagnosis_and_evidence(
    client: TestClient,
    farmer_token: str,
    sample_farm: Farm,
    sample_plot: Plot,
    sample_season: CropSeason,
    sample_image_bytes: bytes,
    db_session: Session
):
    """
    Workflow B:
    1. Upload foliar image observation with crop context.
    2. Verify image quality assessment and hash integrity.
    3. Execute crop diagnosis with evidence and uncertainty handling.
    """
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Create Observation
    obs_payload = {
        "farm_id": sample_farm.id,
        "plot_id": sample_plot.id,
        "crop_season_id": sample_season.id,
        "notes": "Water soaked angular lesions on lower leaves"
    }
    obs_res = client.post("/api/v1/observations/", json=obs_payload, headers=headers)
    assert obs_res.status_code == 201
    obs_id = obs_res.json()["id"]

    # 2. Upload Observation Media
    files = {"file": ("foliar_leaf.jpg", sample_image_bytes, "image/jpeg")}
    media_res = client.post(
        f"/api/v1/observations/{obs_id}/media",
        files=files,
        data={"is_primary": "true"},
        headers=headers
    )
    assert media_res.status_code == 201
    media_id = media_res.json()["id"]
    assert len(media_res.json()["sha256_hash"]) == 64

    # 3. Trigger Diagnosis
    diag_payload = {
        "observation_id": obs_id,
        "media_id": media_id,
        "crop_type": "cotton",
        "language": "te"
    }
    res_diag = client.post("/api/v1/diagnoses/", json=diag_payload, headers=headers)
    assert res_diag.status_code in [200, 201]
    diag_res = res_diag.json()
    assert "id" in diag_res
    assert diag_res["status"] in ["COMPLETED", "NEEDS_REVIEW"]


# =========================================================================
# WORKFLOW C: Multilingual KrishiBrain RAG Retrieval
# =========================================================================
def test_workflow_c_krishi_brain_multilingual_rag(
    client: TestClient,
    admin_token: str,
    farmer_token: str,
    db_session: Session
):
    """
    Workflow C:
    Verify KrishiBrain semantic and evidence retrieval across Telugu, English, and Hindi.
    """
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_farmer = {"Authorization": f"Bearer {farmer_token}"}

    # Seed Knowledge Document
    src_res = client.post(
        "/api/v1/knowledge/sources",
        json={
            "publisher_name": "PJTSAU Regional Center",
            "publisher_type": "UNIVERSITY",
            "official_domain": "pjtsau.edu.in",
            "authority_level": 1.0,
            "licensing_status": "OPEN_ACCESS"
        },
        headers=headers_admin
    )
    assert src_res.status_code in (201, 409)

    # Ingest document
    sample_text = (
        "# Telangana Agricultural Guide\n\n"
        "## Rice Blast Management\n"
        "Rice blast caused by Magnaporthe oryzae can be controlled with Tricyclazole 75 WP at 0.6g/L.\n"
        "Avoid excess nitrogen application in early tillering.\n\n"
        "## Cotton Pink Bollworm\n"
        "Use pheromone traps at 8 traps per hectare for monitoring.\n"
    )
    files = {"file": ("guide.md", sample_text.encode("utf-8"), "text/markdown")}
    client.post(
        "/api/v1/knowledge/ingest",
        data={
            "source_id": src_res.json()["id"] if src_res.status_code == 201 else "PJTSAU",
            "title": "Telangana Agricultural Guide",
            "document_type": "MARKDOWN",
            "primary_language": "en",
            "crop_scope": "rice",
            "region_scope": "Telangana"
        },
        files=files,
        headers=headers_admin
    )

    # 1. Query in Telugu
    query_te = {
        "question": "వరిలో అగ్గి తెగులు నివారణ ఏమిటి?",
        "language": "te",
        "crop": "rice"
    }
    res_te = client.post("/api/v1/knowledge/query", json=query_te, headers=headers_farmer)
    assert res_te.status_code == 200
    assert "answer" in res_te.json()

    # 2. Query in English
    query_en = {
        "question": "How do I manage Rice Blast disease using Tricyclazole?",
        "language": "en",
        "crop": "rice"
    }
    res_en = client.post("/api/v1/knowledge/query", json=query_en, headers=headers_farmer)
    assert res_en.status_code == 200
    assert "answer" in res_en.json()

    # 3. Query in Hindi
    query_hi = {
        "question": "धान में झुलसा रोग की रोकथाम कैसे करें?",
        "language": "hi",
        "crop": "rice"
    }
    res_hi = client.post("/api/v1/knowledge/query", json=query_hi, headers=headers_farmer)
    assert res_hi.status_code == 200
    assert "answer" in res_hi.json()


# =========================================================================
# WORKFLOW D: CropPulse Longitudinal Monitoring
# =========================================================================
def test_workflow_d_croppulse_plant_monitoring(
    client: TestClient,
    farmer_token: str,
    sample_farm: Farm,
    sample_plot: Plot,
    sample_image_bytes: bytes
):
    """
    Workflow D:
    Upload initial and subsequent observation for a plant to test longitudinal tracking.
    """
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # Initial Observation
    obs1_payload = {
        "farm_id": sample_farm.id,
        "plot_id": sample_plot.id,
        "notes": "First symptom spot visible"
    }
    obs1_res = client.post("/api/v1/observations/", json=obs1_payload, headers=headers)
    assert obs1_res.status_code == 201
    obs1_id = obs1_res.json()["id"]

    # Follow-up Observation (Day 7)
    obs2_payload = {
        "farm_id": sample_farm.id,
        "plot_id": sample_plot.id,
        "notes": "Symptom spot unchanged"
    }
    obs2_res = client.post("/api/v1/observations/", json=obs2_payload, headers=headers)
    assert obs2_res.status_code == 201
    obs2_id = obs2_res.json()["id"]

    assert obs1_id != obs2_id


# =========================================================================
# WORKFLOW E: RiskCast Agrometeorological Intelligence & Non-Causal Safeguard
# =========================================================================
def test_workflow_e_riskcast_intelligence(
    client: TestClient,
    farmer_token: str,
    sample_farm: Farm,
    sample_plot: Plot,
    sample_season: CropSeason
):
    """
    Workflow E:
    1. Evaluate plot agrometeorological risk.
    2. Verify non-causal disclaimer preservation: "NOT confirmed disease outbreak".
    3. Fetch farm risk overview.
    """
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # Evaluate plot risk
    res_eval = client.post(f"/api/v1/riskcast/evaluate/{sample_plot.id}", headers=headers)
    assert res_eval.status_code == 201
    eval_json = res_eval.json()
    assert "limitations_notice" in eval_json
    assert "NOT confirmed disease outbreak" in eval_json["limitations_notice"]

    # Farm Overview
    res_overview = client.get(f"/api/v1/riskcast/farms/{sample_farm.id}/overview", headers=headers)
    assert res_overview.status_code == 200
    overview_json = res_overview.json()
    assert overview_json["farm_id"] == sample_farm.id
    assert "current_weather" in overview_json


# =========================================================================
# WORKFLOW F: ExpertConnect Agronomist Review Lifecycle
# =========================================================================
def test_workflow_f_expertconnect_lifecycle(
    client: TestClient,
    farmer_token: str,
    admin_token: str,
    expert_token: str,
    sample_farm: Farm,
    sample_plot: Plot,
    sample_season: CropSeason,
    sample_image_bytes: bytes,
    db_session: Session
):
    """
    Workflow F:
    1. Farmer submits observation and creates expert review case.
    2. Agronomist applies for expert status; Admin verifies credentials.
    3. Agronomist claims case, inspects multimodal dossier, and submits certified assessment.
    4. Agronomist creates an immutable revision with revision audit history.
    """
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    expert_headers = {"Authorization": f"Bearer {expert_token}"}

    # 1. Observation & Media
    obs_res = client.post(
        "/api/v1/observations/",
        json={"farm_id": sample_farm.id, "plot_id": sample_plot.id, "crop_season_id": sample_season.id},
        headers=farmer_headers
    )
    assert obs_res.status_code == 201
    obs_id = obs_res.json()["id"]

    client.post(
        f"/api/v1/observations/{obs_id}/media",
        files={"file": ("foliar_case.jpg", sample_image_bytes, "image/jpeg")},
        headers=farmer_headers
    )

    # 2. Case Creation
    case_res = client.post(
        f"/api/v1/expertconnect/cases/create-from-observation/{obs_id}?farmer_notes=Severe+yellowing+in+lower+canopy&priority=URGENT",
        headers=farmer_headers
    )
    assert case_res.status_code == 201
    case_id = case_res.json()["id"]

    # 3. Expert Profile Setup & Admin Verification
    apply_payload = {
        "registration_number": "PJTSAU-AGRO-2026-999",
        "highest_degree": "Ph.D. in Plant Pathology",
        "institution": "PJTSAU College of Agriculture, Rajendranagar",
        "specializations": ["COTTON", "CHILLI"],
        "districts_covered": ["Warangal", "Karimnagar", "Khammam"]
    }
    apply_res = client.post("/api/v1/expertconnect/apply", json=apply_payload, headers=expert_headers)
    assert apply_res.status_code in [201, 200]
    profile_id = apply_res.json()["id"]

    verify_res = client.post(
        f"/api/v1/expertconnect/admin/verify/{profile_id}",
        json={"decision": "APPROVED", "notes": "Credentials verified against PJTSAU Registry"},
        headers=admin_headers
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["verification_status"] == "APPROVED"

    # 4. Claim Case & Inspect Dossier
    claim_res = client.post(f"/api/v1/expertconnect/cases/{case_id}/claim", headers=expert_headers)
    assert claim_res.status_code == 200

    dossier_res = client.get(f"/api/v1/expertconnect/cases/{case_id}", headers=expert_headers)
    assert dossier_res.status_code == 200
    dossier = dossier_res.json()
    assert dossier["case_id"] == case_id
    assert "farmer_notes" in dossier

    # 5. Submit Certified Assessment
    assess_payload = {
        "confirmed_crop": "cotton",
        "primary_condition": "Cercospora Leaf Spot (Cercospora gossypina)",
        "differential_diagnoses": ["Alternaria Leaf Spot", "Bacterial Blight"],
        "confidence_rating": 4,
        "urgency_level": "ROUTINE",
        "management_plan": "Improve drainage, remove heavily infected lower leaves.",
        "ipm_strategy": "Cultural sanitation first. Clear crop residues.",
        "cibrc_advisories": "Copper Oxychloride 50% WP @ 2.5g/L. PHI: 14 days."
    }
    assess_res = client.post(
        f"/api/v1/expertconnect/cases/{case_id}/assess",
        json=assess_payload,
        headers=expert_headers
    )
    assert assess_res.status_code == 201
    assess_data = assess_res.json()
    assert assess_data["primary_condition"] == "Cercospora Leaf Spot (Cercospora gossypina)"

    # 6. Submit Assessment Revision
    revision_payload = {
        **assess_payload,
        "primary_condition": "Cercospora Leaf Spot + Secondary Potassium Deficiency",
        "confidence_rating": 5,
        "revision_reason": "Follow-up scouting confirmed marginal chlorosis consistent with potassium deficiency."
    }
    rev_res = client.put(
        f"/api/v1/expertconnect/cases/{case_id}/assess",
        json=revision_payload,
        headers=expert_headers
    )
    assert rev_res.status_code == 200
    assert rev_res.json()["revision_count"] == 1


# =========================================================================
# WORKFLOW G: Intervention Tracking & Correlation vs. Causation Guard
# =========================================================================
def test_workflow_g_intervention_and_outcomes(
    client: TestClient,
    farmer_token: str,
    sample_farm: Farm,
    sample_plot: Plot,
    sample_season: CropSeason,
    sample_image_bytes: bytes
):
    """
    Workflow G:
    1. Log chemical/biological intervention with PHI and REI safety metrics.
    2. Link follow-up outcome observation.
    3. Verify timeline and correlation vs. causation disclaimer.
    """
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Log Intervention
    action_payload = {
        "plot_id": sample_plot.id,
        "category": "CHEMICAL",
        "trade_name": "Tilt 25 EC",
        "active_ingredient": "Propiconazole 25% EC",
        "dosage": 250.0,
        "unit": "ml/acre",
        "application_method": "FOLIAR_SPRAY",
        "application_date": "2026-11-01",
        "target_condition": "Cercospora Leaf Spot",
        "phi_days": 30,
        "rei_hours": 24,
        "notes": "Applied using knapsack sprayer with cone nozzle"
    }
    res_act = client.post("/api/v1/interventions/", json=action_payload, headers=headers)
    assert res_act.status_code == 201
    intervention_id = res_act.json()["id"]

    # 2. Create Follow-up Observation
    obs_res = client.post(
        "/api/v1/observations/",
        json={"farm_id": sample_farm.id, "plot_id": sample_plot.id, "crop_season_id": sample_season.id},
        headers=headers
    )
    follow_up_obs_id = obs_res.json()["id"]

    # 3. Record Outcome Observation
    outcome_payload = {
        "follow_up_observation_id": follow_up_obs_id,
        "evaluation_date": "2026-11-08",
        "observed_status": "IMPROVING",
        "visual_change_notes": "Lesion borders arrested; no new chlorotic halos observed.",
        "confounding_factors": "Temperatures dropped by 3C; reduced canopy humidity.",
        "farmer_assessment": "Leaf spotting has stabilized."
    }
    outcome_res = client.post(
        f"/api/v1/interventions/{intervention_id}/outcomes",
        json=outcome_payload,
        headers=headers
    )
    assert outcome_res.status_code == 201
    assert outcome_res.json()["observed_status"] == "IMPROVING"

    # 4. Check Timeline & Causation Disclaimer
    timeline_res = client.get(f"/api/v1/interventions/{intervention_id}/timeline", headers=headers)
    assert timeline_res.status_code == 200
    tl = timeline_res.json()
    assert "confounding_variables_notice" in tl
    assert "not proven single-cause cure" in tl["confounding_variables_notice"]


# =========================================================================
# WORKFLOW H: Security, Multi-Tenant Boundary Isolation & Observability
# =========================================================================
def test_workflow_h_security_tenant_isolation_and_observability(
    client: TestClient,
    farmer_token: str,
    second_farmer_token: str,
    sample_farm: Farm,
    sample_plot: Plot
):
    """
    Workflow H:
    1. Multi-tenant isolation: Farmer B cannot access Farmer A's farm or plot (403 Forbidden).
    2. OWASP Security Headers verified on API responses.
    3. Production Observability and Telemetry endpoints verified.
    """
    farmer_a_headers = {"Authorization": f"Bearer {farmer_token}"}
    farmer_b_headers = {"Authorization": f"Bearer {second_farmer_token}"}

    # 1. Multi-Tenant Isolation
    # Farmer B attempts to access Farmer A's farm
    res_cross_farm = client.get(f"/api/v1/farms/{sample_farm.id}", headers=farmer_b_headers)
    assert res_cross_farm.status_code == 403

    # Farmer B attempts to access Farmer A's plot
    res_cross_plot = client.get(f"/api/v1/plots/{sample_plot.id}", headers=farmer_b_headers)
    assert res_cross_plot.status_code == 403

    # Farmer A can access own farm
    res_own_farm = client.get(f"/api/v1/farms/{sample_farm.id}", headers=farmer_a_headers)
    assert res_own_farm.status_code == 200

    # 2. OWASP Security Headers Verification
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.headers.get("X-Content-Type-Options") == "nosniff"
    assert res_health.headers.get("X-Frame-Options") == "DENY"
    assert res_health.headers.get("X-XSS-Protection") == "1; mode=block"
    assert res_health.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "X-Correlation-ID" in res_health.headers
    assert "X-Response-Time-Ms" in res_health.headers

    # 3. Observability & System Info
    res_obs = client.get("/api/v1/system/observability")
    assert res_obs.status_code == 200
    obs_data = res_obs.json()
    assert obs_data["version"] == "1.0.0"
    assert obs_data["status"] == "HEALTHY"
    assert "database_pool" in obs_data
    assert "cotton" in obs_data["supported_crops"]
