"""
ACREVIA - Stage 13 Automated Test Suite.
Validates Soil Health Intelligence, Precision Water Management, Climate Resilience,
Nutrient Intelligence & Governance, Sustainable Agriculture, and Agricultural Resilience Engine.
"""

from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.farm import Farm, Plot
from backend.app.models.crop import Crop
from backend.app.models.user import User


@pytest.fixture
def test_plot(db_session: Session, farmer_user: User) -> Plot:
    """Fixture providing a verified plot for farmer_user."""
    farm = Farm(
        owner_id=farmer_user.id,
        name="Rameshwaram Farm",
        district="Warangal",
        mandal="Hanamkonda",
        village="Geesugonda",
        total_acreage=5.0,
    )
    db_session.add(farm)
    db_session.commit()
    db_session.refresh(farm)

    plot = Plot(
        farm_id=farm.id,
        name="North Cotton Field",
        acreage=3.5,
        soil_type="BLACK_COTTON",
        irrigation_source="DRIP",
    )
    db_session.add(plot)
    db_session.commit()
    db_session.refresh(plot)
    return plot


@pytest.fixture
def test_crop(db_session: Session) -> Crop:
    """Fixture providing Cotton crop."""
    crop = db_session.query(Crop).filter(Crop.name_en == "Cotton").first()
    if not crop:
        crop = Crop(
            name_en="Cotton",
            name_te="ప్రత్తి",
            name_hi="कपास",
            scientific_name="Gossypium hirsutum",
            category="FIBER",
        )
        db_session.add(crop)
        db_session.commit()
        db_session.refresh(crop)
    return crop


def test_scenario_a_soil_health_intelligence(
    client: TestClient,
    farmer_token: str,
    test_plot: Plot,
):
    """Scenario A: Soil profile, sampling with spatial warning, accredited lab result, and plot history."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Create Soil Profile
    prof_res = client.post(
        "/api/v1/soil/profiles",
        json={
            "plot_id": test_plot.id,
            "soil_order": "VERTISOL",
            "soil_series_name": "WARANGAL_DEEP_CLAY",
            "drainage_class": "MODERATELY_WELL_DRAINED",
            "bulk_density_g_cm3": 1.34,
            "effective_soil_depth_cm": 95.0,
            "texture_class": "CLAY",
        },
        headers=headers,
    )
    assert prof_res.status_code == 201
    profile = prof_res.json()
    assert profile["soil_order"] == "VERTISOL"

    # 2. Create Soil Sample with low core count on 3.5 acre plot -> triggers spatial coverage warning
    sample_res = client.post(
        "/api/v1/soil/samples",
        json={
            "plot_id": test_plot.id,
            "profile_id": profile["id"],
            "sample_code": "WAR-PLT1-2026-S1",
            "sampling_depth_min_cm": 0.0,
            "sampling_depth_max_cm": 15.0,
            "gps_latitude": 17.9689,
            "gps_longitude": 79.5941,
            "composite_cores_count": 3,  # < 5 cores on 3.5 acres
        },
        headers=headers,
    )
    assert sample_res.status_code == 201
    sample = sample_res.json()
    assert sample["spatial_coverage_warning"] == "INSUFFICIENT_SPATIAL_COVERAGE"
    assert sample["status"] == "COLLECTED"

    # 3. Ingest Accredited Lab Test Result
    lab_res = client.post(
        "/api/v1/soil/lab-results",
        json={
            "soil_sample_id": sample["id"],
            "laboratory_name": "PJTSAU Regional Soil Testing Laboratory, Warangal",
            "accreditation_number": "NABL-TC-8912",
            "ph": 7.5,
            "electrical_conductivity_ec": 0.55,
            "organic_carbon_percent": 0.62,
            "available_nitrogen_kg_ha": 235.0,  # Deficient (<280)
            "available_phosphorus_kg_ha": 18.0, # Deficient (<22)
            "available_potassium_kg_ha": 280.0, # Sufficient (140-330)
            "available_zinc_ppm": 0.48,          # Deficient (<0.60)
            "available_boron_ppm": 0.42,         # Deficient (<0.50)
            "provenance": {
                "method_n": "ALKALINE_PERMANGANATE",
                "method_p": "OLSEN_BICARBONATE",
                "method_k": "AMMONIUM_ACETATE",
                "analyst_id": "TECH_402",
            },
        },
        headers=headers,
    )
    assert lab_res.status_code == 201
    lab_data = lab_res.json()
    assert lab_data["ph"] == 7.5
    assert lab_data["available_nitrogen_kg_ha"] == 235.0

    # 4. Query Plot Soil History
    hist_res = client.get(f"/api/v1/soil/plot/{test_plot.id}/history", headers=headers)
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert history["samples_count"] >= 1
    assert history["latest_nitrogen_status"] == "DEFICIENT"
    assert history["latest_ph"] == 7.5


def test_scenario_b_precision_water_management(
    client: TestClient,
    farmer_token: str,
    test_plot: Plot,
):
    """Scenario B: Water source inventory, metered irrigation, telemetry, water balance, and scenario simulation."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Register Farm Water Source
    source_res = client.post(
        "/api/v1/water/sources",
        json={
            "farm_id": test_plot.farm_id,
            "source_type": "BOREWELL",
            "source_name": "East Field Borewell #1",
            "depth_meters": 115.0,
            "static_water_level_m": 38.0,
            "discharge_capacity_lps": 4.0,
            "salinity_ec_dsm": 0.72,
            "ph": 7.3,
            "sar": 1.8,
            "seasonal_availability": {"kharif": True, "rabi": True, "summer": False},
        },
        headers=headers,
    )
    assert source_res.status_code == 201
    source = source_res.json()
    assert source["source_type"] == "BOREWELL"

    # 2. List Water Sources for Farm
    list_res = client.get(f"/api/v1/water/sources?farm_id={test_plot.farm_id}", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 3. Record Metered Irrigation Event
    event_res = client.post(
        "/api/v1/water/irrigation-events",
        json={
            "plot_id": test_plot.id,
            "water_source_id": source["id"],
            "irrigation_method": "DRIP",
            "duration_hours": 3.0,
            "flow_meter_start_m3": 2100.0,
            "flow_meter_end_m3": 2145.0,  # 45 m3 applied
            "soil_moisture_before": 16.5,
            "soil_moisture_after": 26.8,
        },
        headers=headers,
    )
    assert event_res.status_code == 201
    event = event_res.json()
    assert event["calculated_volume_m3"] == 45.0
    assert event["equivalent_depth_mm"] > 0

    # 4. Record Soil Moisture Sensor Telemetry
    telem_res = client.post(
        "/api/v1/water/telemetry",
        json={
            "plot_id": test_plot.id,
            "sensor_id": "TEL-SMS-101",
            "depth_cm": 30,
            "volumetric_water_content": 26.8,
            "matric_potential_kpa": -33.0,
            "moisture_status": "FIELD_CAPACITY",
        },
        headers=headers,
    )
    assert telem_res.status_code == 201
    assert telem_res.json()["depth_cm"] == 30

    # 5. Query Plot Water Balance Snapshot
    balance_res = client.get(f"/api/v1/water/plot/{test_plot.id}/balance", headers=headers)
    assert balance_res.status_code == 200
    balance = balance_res.json()
    assert balance["accounting_status"] == "COMPLETED_WITH_VALIDATED_INPUTS"
    assert balance["management_allowed_depletion_percent"] == 45.0

    # 6. Compare Irrigation Scenarios
    scen_res = client.post(
        "/api/v1/water/scenarios/compare",
        json={
            "plot_id": test_plot.id,
            "baseline_method": "CONVENTIONAL_FLOOD",
            "proposed_method": "DRIP_FERTIGATION",
            "crop_name": "Cotton",
        },
        headers=headers,
    )
    assert scen_res.status_code == 200
    scen_data = scen_res.json()
    assert len(scen_data["scenarios"]) == 3
    drip_scen = next(s for s in scen_data["scenarios"] if s["method"] == "DRIP_FERTIGATION")
    assert drip_scen["water_saving_percent"] >= 35.0


def test_scenario_c_climate_resilience(
    client: TestClient,
    farmer_token: str,
    test_plot: Plot,
    test_crop: Crop,
):
    """Scenario C: 30-year climatological baselines, phenological vulnerability, and PJTSAU contingency intervention."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Get 30-Year Climatological Baselines for Warangal
    base_res = client.get("/api/v1/climate/baselines/TL_WARANGAL", headers=headers)
    assert base_res.status_code == 200
    baselines = base_res.json()
    assert len(baselines) == 12
    assert baselines[4]["month"] == 5  # May is month 5
    assert baselines[4]["normal_tmax_celsius"] >= 40.0

    # 2. Assess Climate Exposure during Reproductive Stage (Extended dry spell during flowering)
    assess_res = client.post(
        "/api/v1/climate/assess-exposure",
        json={
            "plot_id": test_plot.id,
            "crop_id": test_crop.id,
            "crop_stage": "FLOWERING_AND_BOLL_FORMATION",
            "forecast_tmax": 39.2,
            "forecast_rainfall_next_7_days": 0.0,
            "consecutive_rainless_days": 16,
        },
        headers=headers,
    )
    assert assess_res.status_code == 200
    exposure = assess_res.json()
    assert exposure["hazard_type"] == "DRY_SPELL"
    assert exposure["severity_level"] == "CRITICAL"
    assert exposure["vulnerability_score"] >= 0.75
    assert "KNO3" in exposure["recommended_adaptation"]
    assert "PJTSAU" in exposure["institutional_citation"]
    assert len(exposure["scenarios"]) >= 1


def test_scenario_d_nutrient_intelligence_and_safeguards(
    client: TestClient,
    farmer_token: str,
    test_plot: Plot,
    test_crop: Crop,
):
    """Scenario D: Soil-test prescription, split application schedules, and dosage safeguard rejection."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # Setup a sample and lab result for prescription
    s_res = client.post(
        "/api/v1/soil/samples",
        json={
            "plot_id": test_plot.id,
            "sample_code": "WAR-NUTRIENT-TEST-01",
            "composite_cores_count": 8,
        },
        headers=headers,
    )
    sample_id = s_res.json()["id"]

    lab_res = client.post(
        "/api/v1/soil/lab-results",
        json={
            "soil_sample_id": sample_id,
            "laboratory_name": "PJTSAU Soil Lab",
            "accreditation_number": "NABL-99",
            "ph": 7.2,
            "electrical_conductivity_ec": 0.60,
            "organic_carbon_percent": 0.52,
            "available_nitrogen_kg_ha": 210.0,  # Deficient
            "available_phosphorus_kg_ha": 15.0, # Deficient
            "available_potassium_kg_ha": 210.0, # Sufficient
            "available_zinc_ppm": 0.45,          # Deficient
            "available_boron_ppm": 0.40,         # Deficient
        },
        headers=headers,
    )
    soil_test_id = lab_res.json()["id"]

    # 1. Generate Valid Soil-Test-Based Prescription
    presc_res = client.post(
        "/api/v1/nutrient/prescribe",
        json={
            "soil_test_result_id": soil_test_id,
            "crop_id": test_crop.id,
            "yield_target_quintals_per_acre": 12.0,
        },
        headers=headers,
    )
    assert presc_res.status_code == 200
    presc = presc_res.json()
    assert presc["nitrogen_status"] == "DEFICIENT"
    assert presc["safeguard_checks_passed"] is True
    assert presc["recommended_n_kg_ha"] > 120.0  # Adjusted upward for deficiency
    assert "PJTSAU" in presc["institutional_citation"]

    # 2. Safeguard Check: Rejection of excessive unsupported nitrogen dosage (e.g. 300 kg/ha override)
    bad_res = client.post(
        "/api/v1/nutrient/prescribe",
        json={
            "soil_test_result_id": soil_test_id,
            "crop_id": test_crop.id,
            "override_n_kg_ha": 300.0,  # Exceeds safe 180 kg/ha limit
        },
        headers=headers,
    )
    assert bad_res.status_code == 422
    assert "UNACCEPTABLE_DOSAGE_OVERRIDE" in bad_res.json()["detail"]

    # 3. Submit Agronomist Review
    review_res = client.post(
        "/api/v1/nutrient/expert-review",
        json={
            "nutrient_assessment_id": presc["id"],
            "review_status": "APPROVED",
            "agronomist_notes": "Prescription validated. Advise farmer to avoid applying zinc sulphate with DAP simultaneously.",
        },
        headers=headers,
    )
    assert review_res.status_code == 200
    assert review_res.json()["review_status"] == "APPROVED"


def test_scenario_e_sustainable_practices_and_ghg_accounting(
    client: TestClient,
    farmer_token: str,
    test_plot: Plot,
):
    """Scenario E: Sustainable practice catalog, practice logging, empirical SOC, and research GHG accounting."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. List Canonical Sustainable Practices
    p_res = client.get("/api/v1/sustain/practices", headers=headers)
    assert p_res.status_code == 200
    practices = p_res.json()
    assert len(practices) >= 5
    green_manure = next(p for p in practices if p["code"] == "GREEN_MANURE")
    assert "Dhaincha" in green_manure["title_en"]

    # 2. Record Farm Practice Log
    rec_res = client.post(
        "/api/v1/sustain/records",
        json={
            "plot_id": test_plot.id,
            "practice_code": "GREEN_MANURE",
            "area_covered_acres": 3.5,
            "verification_method": "FARMER_LOG",
        },
        headers=headers,
    )
    assert rec_res.status_code == 201
    assert rec_res.json()["practice_code"] == "GREEN_MANURE"

    # 3. Record Empirical Soil Organic Carbon (Valid Method)
    soc_res = client.post(
        "/api/v1/sustain/carbon-measurement",
        json={
            "plot_id": test_plot.id,
            "depth_cm": 15.0,
            "soc_percent": 0.65,
            "bulk_density": 1.34,
            "method": "WALKLEY_BLACK",
            "lab_accreditation": "NABL-TC-8912",
        },
        headers=headers,
    )
    assert soc_res.status_code == 201
    assert soc_res.json()["soc_percent"] == 0.65

    # 4. Reject Satellite or Synthetic Approximation of SOC
    bad_soc_res = client.post(
        "/api/v1/sustain/carbon-measurement",
        json={
            "plot_id": test_plot.id,
            "soc_percent": 0.90,
            "method": "SATELLITE_NDVI_APPROXIMATION",
        },
        headers=headers,
    )
    assert bad_soc_res.status_code == 400

    # 5. Query Research-Grade Greenhouse Gas Emissions
    ghg_res = client.get(f"/api/v1/sustain/plot/{test_plot.id}/emissions?season=Kharif&year=2026", headers=headers)
    assert ghg_res.status_code == 200
    ghg = ghg_res.json()
    assert ghg["is_certified"] is False  # Mandatory non-certified research estimate
    assert "research-grade" in ghg["scientific_disclaimer"].lower()
    assert ghg["total_emissions_kg_co2e"] > 0

    # 6. Query Seasonal Sustainability Scorecard
    score_res = client.get(f"/api/v1/sustain/plot/{test_plot.id}/scorecard?season=Kharif&year=2026", headers=headers)
    assert score_res.status_code == 200
    scorecard = score_res.json()
    assert scorecard["sustainability_index"] > 50.0
    assert "GREEN_MANURE" in scorecard["verified_practices"]


def test_scenario_f_agricultural_resilience_engine(
    client: TestClient,
    farmer_token: str,
    test_plot: Plot,
):
    """Scenario F: Multi-dimensional resilience score, evidence completeness audit, and adaptation simulation."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Compute Resilience Assessment
    res_assess = client.post(
        "/api/v1/resilience/assess",
        json={"plot_id": test_plot.id},
        headers=headers,
    )
    assert res_assess.status_code == 200
    assessment = res_assess.json()
    assert 0.0 <= assessment["overall_resilience_score"] <= 100.0
    assert 0.0 <= assessment["evidence_quality_score"] <= 1.0
    assert assessment["confidence_category"] in [
        "HIGH_CONFIDENCE_EMPIRICAL",
        "MODERATE_CONFIDENCE_HYBRID",
        "LOW_CONFIDENCE_INSUFFICIENT_DATA",
    ]
    assert assessment["soil_score"] > 0
    assert assessment["water_score"] > 0

    # 2. Query Latest Resilience Assessment
    latest_res = client.get(f"/api/v1/resilience/plot/{test_plot.id}/latest", headers=headers)
    assert latest_res.status_code == 200
    assert latest_res.json()["id"] == assessment["id"]

    # 3. Simulate Climate Adaptation Package
    sim_res = client.post(
        "/api/v1/resilience/simulate-adaptation",
        json={
            "plot_id": test_plot.id,
            "package_name": "REGENERATIVE_INTEGRATED_PACKAGE",
        },
        headers=headers,
    )
    assert sim_res.status_code == 200
    sim = sim_res.json()
    assert sim["simulated_overall_score"] > assessment["overall_resilience_score"]
    assert sim["projected_water_saving_percent"] >= 30.0
    assert sim["yield_risk_reduction_percent"] >= 40.0


def test_scenario_g_security_and_privacy(
    client: TestClient,
    test_plot: Plot,
):
    """Scenario G: Unauthenticated requests and tenant privacy controls."""
    # 1. Unauthenticated requests rejected
    res_soil = client.get(f"/api/v1/soil/plot/{test_plot.id}/history")
    assert res_soil.status_code == 401

    res_water = client.get(f"/api/v1/water/plot/{test_plot.id}/balance")
    assert res_water.status_code == 401

    res_resilience = client.get(f"/api/v1/resilience/plot/{test_plot.id}/latest")
    assert res_resilience.status_code == 401
