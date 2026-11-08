"""
ACREVIA - Stage 10 Automated Test Suite.
Validates Pillar A (Twin), Pillar B (Simulate), Pillar C (Optimize),
Pillar D (Plan), and Pillar E (Decision Intelligence & Security).
"""

from datetime import date, datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.farm import Farm, Plot
from backend.app.models.crop import CropSeason
from backend.app.models.weather_data import WeatherData
from backend.app.models.operation import FarmOperation
from backend.app.models.risk_alert import RiskAlert
from backend.app.models.risk_assessment import RiskAssessmentRecord
from backend.app.models.digital_twin import FarmTwin, TwinSnapshot
from backend.app.services.twin_service import TwinService
from backend.app.services.crop_planning_service import CropPlanningService


def test_scenario_a_digital_twin_lifecycle(
    client: TestClient,
    sample_farm: Farm,
    sample_plot: Plot,
    sample_season: CropSeason,
    farmer_token: str,
):
    """Scenario A: Farm digital twin state aggregation, completeness, and snapshot reconciliation."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Get initial farm digital twin
    res = client.get(f"/api/v1/twin/farms/{sample_farm.id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["farm_id"] == sample_farm.id
    assert data["twin_version"] >= 1
    assert data["state_status"] == "SYNCHRONIZED"
    assert data["active_plots_count"] >= 1

    # 2. Check data completeness vector
    comp_res = client.get(f"/api/v1/twin/farms/{sample_farm.id}/completeness", headers=headers)
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert "overall_score" in comp_data
    assert "dimensions" in comp_data
    assert comp_data["dimensions"]["cadastral_boundary"] == 100.0
    assert comp_data["dimensions"]["crop_season_active"] == 100.0

    # 3. Trigger reconciliation
    rec_res = client.post(f"/api/v1/twin/farms/{sample_farm.id}/reconcile", headers=headers)
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert rec_data["current_version"] > rec_data["previous_version"]
    assert rec_data["status"] == "SYNCHRONIZED"

    # 4. List snapshots
    snap_res = client.get(f"/api/v1/twin/farms/{sample_farm.id}/snapshots", headers=headers)
    assert snap_res.status_code == 200
    snaps = snap_res.json()
    assert len(snaps) >= 1
    latest_snap_id = snaps[0]["id"]
    assert len(snaps[0]["payload_hash"]) == 64  # SHA-256 hash length

    # 5. Get snapshot detail with state records & 8-tier provenance
    detail_res = client.get(f"/api/v1/twin/snapshots/{latest_snap_id}", headers=headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert "records" in detail
    assert len(detail["records"]) > 0
    # Verify provenance tag is from the strict hierarchy
    for rec in detail["records"]:
        assert rec["provenance_type"] in [
            "MEASURED",
            "FARMER_REPORTED",
            "EXPERT_REVIEWED",
            "AI_ESTIMATED",
            "PROVIDER_OBSERVATION",
            "SIMULATED",
            "INFERRED",
            "UNKNOWN",
        ]


def test_scenario_b_simulation_fao56_and_compare(
    client: TestClient,
    sample_plot: Plot,
    sample_season: CropSeason,
    farmer_token: str,
):
    """Scenario B: Agricultural simulation (FAO-56 water balance) and scenario comparison."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Run baseline scenario: 30mm irrigation on Day 0
    payload_1 = {
        "plot_id": sample_plot.id,
        "crop_season_id": sample_season.id,
        "scenario_name": "Immediate Furrow Irrigation 30mm",
        "scenario_type": "IRRIGATION_WATER_BALANCE",
        "input_parameters": {
            "irrigation_depth_mm": 30.0,
            "days_offset": 0,
            "horizon_days": 14,
        },
        "farmer_assumptions": {
            "weather_condition": "NORMAL",
        },
    }
    res_1 = client.post("/api/v1/simulations/", headers=headers, json=payload_1)
    assert res_1.status_code == 201
    data_1 = res_1.json()
    assert data_1["status"] == "COMPLETED"
    assert data_1["result"] is not None
    assert data_1["result"]["model_name"] == "FAO-56_DUAL_KC"
    outputs_1 = data_1["result"]["outputs"]
    assert "root_zone_depletion_mm" in outputs_1
    assert "water_stress_index" in outputs_1
    assert "depletion_trajectory_days" in outputs_1
    assert len(outputs_1["depletion_trajectory_days"]) == 14
    assert data_1["result"]["execution_duration_ms"] < 200.0  # Serverless latency budget check

    # 2. Run counterfactual scenario: Delayed irrigation (Day 6)
    payload_2 = {
        "plot_id": sample_plot.id,
        "crop_season_id": sample_season.id,
        "scenario_name": "Delayed Irrigation Day 6",
        "scenario_type": "IRRIGATION_WATER_BALANCE",
        "input_parameters": {
            "irrigation_depth_mm": 30.0,
            "days_offset": 6,
            "horizon_days": 14,
        },
        "farmer_assumptions": {
            "weather_condition": "HEAT_WAVE",
        },
    }
    res_2 = client.post("/api/v1/simulations/", headers=headers, json=payload_2)
    assert res_2.status_code == 201
    data_2 = res_2.json()

    # 3. Compare scenarios side-by-side
    compare_res = client.post(
        "/api/v1/simulations/compare",
        headers=headers,
        json={"scenario_ids": [data_1["id"], data_2["id"]]},
    )
    assert compare_res.status_code == 200
    comp_data = compare_res.json()
    assert len(comp_data["scenarios"]) == 2
    assert "comparison_summary" in comp_data


def test_scenario_b_simulation_thermal_gdd_and_waterlogging(
    client: TestClient,
    sample_plot: Plot,
    sample_season: CropSeason,
    farmer_token: str,
):
    """Scenario B: GDD thermal progression and waterlogging stress evaluation."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Thermal GDD simulation
    gdd_res = client.post(
        "/api/v1/simulations/",
        headers=headers,
        json={
            "plot_id": sample_plot.id,
            "crop_season_id": sample_season.id,
            "scenario_name": "Summer Thermal GDD Horizon",
            "scenario_type": "THERMAL_GDD_STAGE",
            "input_parameters": {"horizon_days": 14},
            "farmer_assumptions": {"avg_max_temp_c": 35.0, "avg_min_temp_c": 23.0},
        },
    )
    assert gdd_res.status_code == 201
    gdd_data = gdd_res.json()
    assert gdd_data["result"]["outputs"]["accumulated_gdd_horizon"] > 0

    # 2. Waterlogging stress simulation
    wl_res = client.post(
        "/api/v1/simulations/",
        headers=headers,
        json={
            "plot_id": sample_plot.id,
            "scenario_name": "Monsoon Surge 90mm in 12h",
            "scenario_type": "WATERLOGGING_STRESS",
            "input_parameters": {"intense_rainfall_mm": 90.0, "duration_hours": 12.0},
            "farmer_assumptions": {},
        },
    )
    assert wl_res.status_code == 201
    wl_data = wl_res.json()
    assert "surface_ponding_depth_mm" in wl_data["result"]["outputs"]
    assert "estimated_drainage_hours" in wl_data["result"]["outputs"]


def test_scenario_c_optimization_water_allocation(
    client: TestClient,
    sample_farm: Farm,
    sample_plot: Plot,
    farmer_token: str,
):
    """Scenario C: Multi-plot water allocation with feasible solution."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    payload = {
        "farm_id": sample_farm.id,
        "problem_type": "WATER_ALLOCATION",
        "objective_type": "MAXIMIZE_WATER_PRODUCTIVITY",
        "decision_variables": {"plots": [sample_plot.id]},
        "hard_constraints": {
            "max_water_volume_m3": 150.0,
            "pump_hours_available": 8.0,
            "flow_rate_lps": 4.5,
        },
        "soft_constraints": {},
    }

    res = client.post("/api/v1/optimization/problems", headers=headers, json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "SOLVED"
    assert data["result"]["feasibility_status"] == "FEASIBLE"
    assert "allocated_depths_mm" in data["result"]["selected_solution"]
    assert data["result"]["selected_solution"]["total_water_used_m3"] > 0
    assert data["result"]["selected_solution"]["pump_hours_required"] <= 8.0


def test_scenario_c_optimization_infeasible_bottleneck(
    client: TestClient,
    sample_farm: Farm,
    sample_plot: Plot,
    farmer_token: str,
):
    """Scenario C: Explicit infeasibility detection and conflicting bottleneck diagnosis."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # Extremely constrained pump hours (0.5 hour cannot satisfy 2-acre plot)
    payload = {
        "farm_id": sample_farm.id,
        "problem_type": "WATER_ALLOCATION",
        "objective_type": "MAXIMIZE_WATER_PRODUCTIVITY",
        "decision_variables": {"plots": [sample_plot.id]},
        "hard_constraints": {
            "max_water_volume_m3": 5.0,  # Far below minimum 15mm threshold
            "pump_hours_available": 0.2,
            "flow_rate_lps": 2.0,
        },
        "soft_constraints": {},
    }

    res = client.post("/api/v1/optimization/problems", headers=headers, json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "INFEASIBLE"
    assert data["result"]["feasibility_status"] == "INFEASIBLE"
    assert len(data["result"]["conflicting_constraints"]) > 0
    assert "cannot satisfy" in data["result"]["conflicting_constraints"][0].lower()


def test_scenario_d_crop_planning_and_weather_conflict(
    client: TestClient,
    sample_farm: Farm,
    sample_plot: Plot,
    sample_season: CropSeason,
    farmer_token: str,
    db_session: Session,
):
    """Scenario D: Crop task scheduling, weather conflict detection, and lifecycle completion."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. List PJTSAU crop calendars
    cal_res = client.get("/api/v1/planning/calendars?crop_name=COTTON", headers=headers)
    assert cal_res.status_code == 200
    calendars = cal_res.json()
    assert len(calendars) >= 1
    cal_id = calendars[0]["id"]

    # 2. Simulate high rain in weather table to trigger weather conflict
    task_due = date.today() + timedelta(days=2)
    weather = WeatherData(
        farm_id=sample_farm.id,
        district=sample_farm.district,
        observation_time=datetime.combine(task_due, datetime.min.time(), tzinfo=timezone.utc),
        temperature_celsius=28.5,
        relative_humidity=85.0,
        precipitation_mm=35.0,  # High rain > 15mm
        wind_speed_kmh=12.0,
        source_provider="Open-Meteo",
    )
    db_session.add(weather)
    db_session.commit()

    # 3. Create plant protection spray task on that day
    task_res = client.post(
        "/api/v1/planning/tasks",
        headers=headers,
        json={
            "crop_season_id": sample_season.id,
            "plot_id": sample_plot.id,
            "calendar_def_id": cal_id,
            "task_name": "Foliar Spray against Leaf Reddening",
            "task_category": "PLANT_PROTECTION",
            "due_date": task_due.isoformat(),
            "notes": "1% MgSO4 foliar spray",
        },
    )
    assert task_res.status_code == 201
    task = task_res.json()
    assert task["weather_conflict_flag"] is True
    assert "wash-off" in task["conflict_reason"].lower()

    # 4. Complete task and verify FarmOperation is logged
    comp_res = client.post(
        f"/api/v1/planning/tasks/{task['id']}/complete",
        headers=headers,
        json={
            "actual_date": date.today().isoformat(),
            "labor_hours": 3.0,
            "materials_used": [{"item": "MgSO4", "quantity_kg": 2.5}],
            "observations": "Applied with battery backpack sprayer.",
        },
    )
    assert comp_res.status_code == 200
    comp_task = comp_res.json()
    assert comp_task["status"] == "COMPLETED"

    # Verify immutable FarmOperation audit log exists in DB
    op = db_session.query(FarmOperation).filter(FarmOperation.plot_id == sample_plot.id).first()
    assert op is not None
    assert op.operation_type == "PLANT_PROTECTION"


def test_scenario_e_decision_intelligence_grounding_and_safety(
    client: TestClient,
    sample_plot: Plot,
    sample_season: CropSeason,
    farmer_token: str,
):
    """Scenario E: Explainable decision support, regulatory filters, and feedback."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Grounded operational query
    query_payload = {
        "plot_id": sample_plot.id,
        "query_text": "Should I apply second split Urea top dressing this week?",
        "decision_category": "FERTILIZER_APPLICATION",
    }
    res = client.post("/api/v1/decisions/analyze", headers=headers, json=query_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["recommendation_state"] in ["EVIDENCE_SUPPORTED", "REQUIRES_MORE_INFORMATION"]
    assert len(data["grounded_explanation_en"]) > 20
    assert len(data["grounded_explanation_te"]) > 20
    assert len(data["grounded_explanation_hi"]) > 20

    # 2. Banned agrochemical query (monocrotophos)
    banned_payload = {
        "plot_id": sample_plot.id,
        "query_text": "Can I spray monocrotophos for quick pest knockdown?",
        "decision_category": "PEST_MANAGEMENT",
    }
    banned_res = client.post("/api/v1/decisions/analyze", headers=headers, json=banned_payload)
    assert banned_res.status_code == 200
    banned_data = banned_res.json()
    assert banned_data["recommendation_state"] == "NOT_SUPPORTED"
    assert "banned or restricted" in banned_data["grounded_explanation_en"].lower()

    # 3. Farmer feedback recording
    feedback_res = client.post(
        f"/api/v1/decisions/{data['id']}/feedback",
        headers=headers,
        json={
            "farmer_action_taken": "ADOPTED",
            "farmer_rating": 5,
            "feedback_notes": "Followed top-dressing timing, good crop vigor.",
        },
    )
    assert feedback_res.status_code == 201
    feedback_data = feedback_res.json()
    assert feedback_data["farmer_action_taken"] == "ADOPTED"
    assert feedback_data["farmer_rating"] == 5


def test_scenario_f_security_and_tenant_isolation(
    client: TestClient,
    sample_farm: Farm,
    sample_plot: Plot,
    second_farmer_token: str,
):
    """Scenario F: Multi-tenant boundary enforcement blocking unauthorized cross-farm access."""
    unauthorized_headers = {"Authorization": f"Bearer {second_farmer_token}"}

    # Attempt to access User A's twin with User B's credentials
    res = client.get(f"/api/v1/twin/farms/{sample_farm.id}", headers=unauthorized_headers)
    assert res.status_code == 403

    # Attempt to run simulation on User A's plot
    sim_res = client.post(
        "/api/v1/simulations/",
        headers=unauthorized_headers,
        json={
            "plot_id": sample_plot.id,
            "scenario_name": "Unauthorized Intrusion Simulation",
            "scenario_type": "IRRIGATION_WATER_BALANCE",
        },
    )
    assert sim_res.status_code == 403

    # Attempt to solve optimization on User A's farm
    opt_res = client.post(
        "/api/v1/optimization/problems",
        headers=unauthorized_headers,
        json={
            "farm_id": sample_farm.id,
            "problem_type": "WATER_ALLOCATION",
        },
    )
    assert opt_res.status_code == 403
