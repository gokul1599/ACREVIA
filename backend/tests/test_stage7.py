"""
ACREVIA Backend - Stage 7 Test Suite.
Verifies RiskCast, ExpertConnect, and Intervention Intelligence & Outcome Tracking.
"""

from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.farm import Farm, Plot
from backend.app.models.crop import CropSeason
from backend.app.models.observation import Observation


# ==============================================================================
# 1. RISKCAST TESTS
# ==============================================================================

def test_riskcast_seeded_rules_and_query(client: TestClient, farmer_token):
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Query all rules
    resp = client.get("/api/v1/riskcast/rules", headers=headers)
    assert resp.status_code == 200
    rules = resp.json()
    assert len(rules) >= 6
    rule_codes = [r["rule_code"] for r in rules]
    assert "RIC-BLST-01" in rule_codes
    assert "COT-CLSP-01" in rule_codes
    assert "CHL-ANTH-01" in rule_codes

    # 2. Filter by crop
    resp_rice = client.get("/api/v1/riskcast/rules?crop=rice", headers=headers)
    assert resp_rice.status_code == 200
    rice_rules = resp_rice.json()
    assert all(r["crop"] == "rice" for r in rice_rules)
    assert any(r["rule_code"] == "RIC-BLST-01" for r in rice_rules)

    # 3. Verify PJTSAU citation and multilingual content
    blast_rule = next(r for r in rice_rules if r["rule_code"] == "RIC-BLST-01")
    assert "PJTSAU" in str(blast_rule["evidence_citations"])
    assert blast_rule["advisory_te"] != ""
    assert blast_rule["advisory_hi"] != ""


def test_riskcast_plot_evaluation_and_alerts(client: TestClient, farmer_token, sample_farm: Farm, sample_plot: Plot, sample_season: CropSeason):
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Evaluate Plot Risk
    eval_resp = client.post(f"/api/v1/riskcast/evaluate/{sample_plot.id}", headers=headers)
    assert eval_resp.status_code == 201
    eval_data = eval_resp.json()
    assert eval_data["plot_id"] == sample_plot.id
    assert eval_data["overall_risk_level"] in ("LOW", "MODERATE", "HIGH")
    assert "NOT confirmed disease outbreak" in eval_data["limitations_notice"]

    # 2. Query Farm Overview
    overview_resp = client.get(f"/api/v1/riskcast/farms/{sample_farm.id}/overview", headers=headers)
    assert overview_resp.status_code == 200
    overview_data = overview_resp.json()
    assert overview_data["farm_id"] == sample_farm.id
    assert len(overview_data["plots_risk_summary"]) >= 1
    assert overview_data["current_weather"] is not None

    # 3. List Alerts
    alerts_resp = client.get(f"/api/v1/riskcast/alerts?farm_id={sample_farm.id}", headers=headers)
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()

    # If an alert was generated, test acknowledge and dismiss
    if alerts:
        first_alert = alerts[0]
        alert_id = first_alert["id"]

        # Acknowledge
        ack_resp = client.post(f"/api/v1/riskcast/alerts/{alert_id}/acknowledge", headers=headers)
        assert ack_resp.status_code == 200
        assert ack_resp.json()["is_acknowledged"] is True

        # Dismiss
        dsm_resp = client.post(f"/api/v1/riskcast/alerts/{alert_id}/dismiss", headers=headers)
        assert dsm_resp.status_code == 200
        assert dsm_resp.json()["is_dismissed"] is True


def test_riskcast_deduplication(client: TestClient, farmer_token, sample_farm: Farm, sample_plot: Plot, sample_season: CropSeason):
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # First evaluation
    client.post(f"/api/v1/riskcast/evaluate/{sample_plot.id}", headers=headers)
    alerts_first = client.get(f"/api/v1/riskcast/alerts?farm_id={sample_farm.id}", headers=headers).json()

    # Immediate second evaluation on same day
    client.post(f"/api/v1/riskcast/evaluate/{sample_plot.id}", headers=headers)
    alerts_second = client.get(f"/api/v1/riskcast/alerts?farm_id={sample_farm.id}", headers=headers).json()

    # Alert count should not increase due to deduplication key
    assert len(alerts_second) == len(alerts_first)


# ==============================================================================
# 2. EXPERTCONNECT TESTS
# ==============================================================================

def test_expertconnect_application_and_admin_verification(client: TestClient, farmer_token, admin_token):
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    app_payload = {
        "registration_number": "PJTSAU-AGRO-2026-089",
        "highest_degree": "Ph.D. in Plant Pathology",
        "institution": "Professor Jayashankar Telangana State Agricultural University",
        "specializations": ["COTTON", "CHILLI"],
        "districts_covered": ["Warangal", "Khammam", "Karimnagar"]
    }

    # 1. User applies
    apply_resp = client.post("/api/v1/expertconnect/apply", json=app_payload, headers=farmer_headers)
    assert apply_resp.status_code == 201
    profile = apply_resp.json()
    assert profile["verification_status"] == "APPLICATION_SUBMITTED"
    profile_id = profile["id"]

    # 2. Candidate checks profile
    me_resp = client.get("/api/v1/expertconnect/profile/me", headers=farmer_headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["id"] == profile_id

    # 3. Regular user cannot access admin verification -> 403 Forbidden
    unauth_resp = client.post(
        f"/api/v1/expertconnect/admin/verify/{profile_id}",
        json={"decision": "APPROVED"},
        headers=farmer_headers
    )
    assert unauth_resp.status_code == 403

    # 4. Admin verifies and approves
    admin_resp = client.post(
        f"/api/v1/expertconnect/admin/verify/{profile_id}",
        json={"decision": "APPROVED"},
        headers=admin_headers
    )
    assert admin_resp.status_code == 200
    assert admin_resp.json()["verification_status"] == "APPROVED"
    assert admin_resp.json()["verified_at"] is not None


def test_expertconnect_case_workflow_and_revisions(
    client: TestClient,
    farmer_token,
    expert_token,
    sample_farm: Farm,
    sample_plot: Plot,
    sample_season: CropSeason
):
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
    expert_headers = {"Authorization": f"Bearer {expert_token}"}

    # 1. Farmer creates observation
    obs_resp = client.post(
        "/api/v1/observations/",
        json={
            "farm_id": sample_farm.id,
            "plot_id": sample_plot.id,
            "notes": "Spotted circular lesions on lower cotton leaves.",
            "symptom_tags": "leaf_spots,chlorosis"
        },
        headers=farmer_headers
    )
    assert obs_resp.status_code == 201
    obs_id = obs_resp.json()["id"]

    # 2. Escalate observation to Expert Review Case
    case_resp = client.post(
        f"/api/v1/expertconnect/cases/create-from-observation/{obs_id}?priority=URGENT",
        headers=farmer_headers
    )
    assert case_resp.status_code == 201
    case_data = case_resp.json()
    case_id = case_data["id"]
    assert case_data["status"] == "QUEUED"
    assert case_data["priority"] == "URGENT"

    # 3. Expert views triage queue
    queue_resp = client.get("/api/v1/expertconnect/cases?priority=URGENT", headers=expert_headers)
    assert queue_resp.status_code == 200
    queue_cases = queue_resp.json()
    assert any(c["id"] == case_id for c in queue_cases)

    # 4. Expert claims the case
    claim_resp = client.post(f"/api/v1/expertconnect/cases/{case_id}/claim", headers=expert_headers)
    assert claim_resp.status_code == 200
    assert claim_resp.json()["status"] == "ASSIGNED"

    # 5. Expert inspects evidence dossier
    dossier_resp = client.get(f"/api/v1/expertconnect/cases/{case_id}", headers=expert_headers)
    assert dossier_resp.status_code == 200
    dossier = dossier_resp.json()
    assert dossier["case_id"] == case_id
    assert dossier["district"] == sample_farm.district
    assert "farmer_notes" in dossier

    # 6. Expert submits initial certified assessment
    assess_payload = {
        "confirmed_crop": "cotton",
        "primary_condition": "Cercospora Leaf Spot (Cercospora gossypina)",
        "differential_diagnoses": ["Alternaria Leaf Spot", "Bacterial Blight"],
        "confidence_rating": 4,
        "urgency_level": "ROUTINE",
        "management_plan": "Improve drainage, remove heavily infected lower leaves, and spray Copper Oxychloride 50% WP if progression exceeds 5% leaf area.",
        "ipm_strategy": "Cultural sanitation first. Clear crop residues and maintain proper plant spacing for aeration.",
        "cibrc_advisories": "Copper Oxychloride 50% WP @ 2.5-3.0 g/litre of water. Pre-Harvest Interval (PHI): 14 days."
    }
    submit_resp = client.post(f"/api/v1/expertconnect/cases/{case_id}/assess", json=assess_payload, headers=expert_headers)
    assert submit_resp.status_code == 201
    assess_data = submit_resp.json()
    assert assess_data["primary_condition"] == "Cercospora Leaf Spot (Cercospora gossypina)"
    assert assess_data["revision_count"] == 0

    # 7. Expert submits a revision with rationale
    revision_payload = {
        **assess_payload,
        "primary_condition": "Cercospora Leaf Spot + Secondary Potassium Deficiency",
        "confidence_rating": 5,
        "revision_reason": "Follow-up foliar inspection confirmed marginal chlorosis consistent with potassium deficiency alongside fungal spots."
    }
    rev_resp = client.put(f"/api/v1/expertconnect/cases/{case_id}/assess", json=revision_payload, headers=expert_headers)
    assert rev_resp.status_code == 200
    rev_data = rev_resp.json()
    assert rev_data["revision_count"] == 1
    assert "Potassium Deficiency" in rev_data["primary_condition"]

    # 8. Verify immutable revision history
    history_resp = client.get(f"/api/v1/expertconnect/cases/{case_id}/revisions", headers=expert_headers)
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert len(history) == 1
    assert history[0]["revision_number"] == 1
    assert "marginal chlorosis" in history[0]["revision_reason"]
    assert history[0]["previous_assessment"]["primary_condition"] == "Cercospora Leaf Spot (Cercospora gossypina)"


# ==============================================================================
# 3. INTERVENTION INTELLIGENCE TESTS
# ==============================================================================

def test_interventions_lifecycle_and_outcomes(
    client: TestClient,
    farmer_token,
    second_farmer_token,
    sample_farm: Farm,
    sample_plot: Plot
):
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
    second_farmer_headers = {"Authorization": f"Bearer {second_farmer_token}"}

    # 1. Farmer logs an intervention
    interv_payload = {
        "plot_id": sample_plot.id,
        "category": "BIOLOGICAL",
        "trade_name": "Neem Baan 1500 ppm",
        "active_ingredient": "Azadirachtin 0.15% EC",
        "dosage": 500.0,
        "unit": "ml/acre",
        "application_method": "FOLIAR_SPRAY",
        "application_date": date.today().isoformat(),
        "target_condition": "Sucking pests (Whitefly)",
        "phi_days": 3,
        "rei_hours": 12,
        "notes": "Applied early morning foliar spray with knapsack sprayer."
    }
    create_resp = client.post("/api/v1/interventions/", json=interv_payload, headers=farmer_headers)
    assert create_resp.status_code == 201
    interv_data = create_resp.json()
    interv_id = interv_data["id"]
    assert interv_data["trade_name"] == "Neem Baan 1500 ppm"

    # 2. Second farmer cannot access first farmer's interventions (multi-tenant boundary)
    cross_tenant_resp = client.get(f"/api/v1/interventions/plots/{sample_plot.id}", headers=second_farmer_headers)
    assert cross_tenant_resp.status_code == 403

    # 3. Create follow-up observation on this plot
    obs_resp = client.post(
        "/api/v1/observations/",
        json={
            "farm_id": sample_farm.id,
            "plot_id": sample_plot.id,
            "notes": "Follow-up scout 5 days post Neem oil spray. Lower whitefly nymph counts.",
            "symptom_tags": "recovering,reduced_pests"
        },
        headers=farmer_headers
    )
    assert obs_resp.status_code == 201
    follow_obs_id = obs_resp.json()["id"]

    # 4. Record Outcome Observation
    outcome_payload = {
        "follow_up_observation_id": follow_obs_id,
        "evaluation_date": date.today().isoformat(),
        "observed_status": "IMPROVING",
        "visual_change_notes": "Whitefly counts reduced from 8/leaf to 2/leaf; no phytotoxicity symptoms.",
        "confounding_factors": "Light intermittent shower 2 days ago; beneficial predator ladybird beetles spotted.",
        "farmer_assessment": "Satisfied with organic bio-repellent outcome."
    }
    outcome_resp = client.post(f"/api/v1/interventions/{interv_id}/outcomes", json=outcome_payload, headers=farmer_headers)
    assert outcome_resp.status_code == 201
    outcome_data = outcome_resp.json()
    assert outcome_data["observed_status"] == "IMPROVING"
    assert outcome_data["days_post_intervention"] >= 0

    # 5. Retrieve Timeline & verify causality disclaimer
    timeline_resp = client.get(f"/api/v1/interventions/{interv_id}/timeline", headers=farmer_headers)
    assert timeline_resp.status_code == 200
    timeline = timeline_resp.json()
    assert timeline["intervention"]["id"] == interv_id
    assert len(timeline["outcomes"]) >= 1
    assert "not proven single-cause cure" in timeline["confounding_variables_notice"]
