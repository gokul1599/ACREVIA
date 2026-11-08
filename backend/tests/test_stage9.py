"""
ACREVIA - Stage 9 Automated Test Suite.
Validates Pillar A (Geo), Pillar B (Earth), Pillar C (Sense), Pillar D (Fusion),
Pillar E (Predict), and Agricultural Knowledge Graph traversal.
"""

import json
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.farm import Farm, Plot
from backend.app.models.crop import CropSeason
from backend.app.models.operation import FarmOperation
from backend.app.services.satellite_service import SatelliteService
from backend.app.services.predict_service import PredictService


def test_scenario_a_geospatial_valid_polygon(client: TestClient, sample_plot: Plot, farmer_token: str):
    """Scenario A: Valid GeoJSON polygon upload with acreage calculation."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # Valid closed ring around Geesugonda, Warangal
    coords = [
        [
            [79.6200, 17.9800],
            [79.6250, 17.9800],
            [79.6250, 17.9750],
            [79.6200, 17.9750],
            [79.6200, 17.9800]
        ]
    ]

    res = client.post(
        f"/api/v1/geospatial/plots/{sample_plot.id}/geometry",
        headers=headers,
        json={"type": "Polygon", "coordinates": coords}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["plot_id"] == sample_plot.id
    assert data["is_valid"] is True
    assert data["calculated_area_hectares"] > 0.0
    assert data["calculated_area_acres"] > 0.0
    assert "centroid" in data
    assert 17.97 <= data["centroid"]["latitude"] <= 17.99
    assert 79.61 <= data["centroid"]["longitude"] <= 79.63

    # Proximity query
    prox_res = client.get(
        "/api/v1/geospatial/plots/nearby?latitude=17.978&longitude=79.622&radius_km=5.0",
        headers=headers
    )
    assert prox_res.status_code == 200
    plots = prox_res.json()
    assert len(plots) >= 1
    assert any(p["plot_id"] == sample_plot.id for p in plots)


def test_scenario_b_geospatial_invalid_polygon_rejection(client: TestClient, sample_plot: Plot, farmer_token: str):
    """Scenario B: Invalid GeoJSON polygon rejection."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Unclosed ring (first != last)
    unclosed = [
        [
            [79.6200, 17.9800],
            [79.6250, 17.9800],
            [79.6250, 17.9750],
            [79.6200, 17.9750]  # Missing closed point
        ]
    ]
    res1 = client.post(
        f"/api/v1/geospatial/plots/{sample_plot.id}/geometry",
        headers=headers,
        json={"type": "Polygon", "coordinates": unclosed}
    )
    assert res1.status_code == 400

    # 2. Out of bounds coordinates (lat > 90)
    out_of_bounds = [
        [
            [79.6200, 117.9800],
            [79.6250, 117.9800],
            [79.6250, 117.9750],
            [79.6200, 117.9800]
        ]
    ]
    res2 = client.post(
        f"/api/v1/geospatial/plots/{sample_plot.id}/geometry",
        headers=headers,
        json={"type": "Polygon", "coordinates": out_of_bounds}
    )
    assert res2.status_code == 400


def test_scenario_c_satellite_vegetation_indices_and_disclaimer(client: TestClient, sample_plot: Plot, farmer_token: str):
    """Scenario C: Satellite optical indices & non-disease disclaimer enforcement."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # Mathematical index formula checks
    ndvi = SatelliteService.calculate_ndvi(nir=0.75, red=0.15)
    assert ndvi == 0.6667
    evi = SatelliteService.calculate_evi(nir=0.75, red=0.15, blue=0.08)
    assert 0.4 <= evi <= 0.9
    ndmi = SatelliteService.calculate_ndmi(nir=0.75, swir=0.35)
    assert 0.2 <= ndmi <= 0.5

    # Record two observations
    now = datetime.now(timezone.utc)
    client.post(
        f"/api/v1/satellite/plots/{sample_plot.id}/observations",
        headers=headers,
        json={
            "observation_date": (now - timedelta(days=20)).isoformat(),
            "mean_ndvi": 0.55,
            "min_ndvi": 0.40,
            "max_ndvi": 0.65,
            "cloud_masked_pixel_ratio": 0.05
        }
    )
    client.post(
        f"/api/v1/satellite/plots/{sample_plot.id}/observations",
        headers=headers,
        json={
            "observation_date": now.isoformat(),
            "mean_ndvi": 0.68,
            "min_ndvi": 0.50,
            "max_ndvi": 0.78,
            "cloud_masked_pixel_ratio": 0.02
        }
    )

    # Retrieve time series
    res = client.get(f"/api/v1/satellite/plots/{sample_plot.id}/time-series", headers=headers)
    assert res.status_code == 200
    ts_data = res.json()
    assert ts_data["observations_count"] == 2
    assert ts_data["trend_summary"] == "VIGOR_INCREASING"

    # Mandatory Evidence Disclaimer Check
    assert "evidence_disclaimer" in ts_data
    assert "not diagnose specific plant diseases" in ts_data["evidence_disclaimer"].lower()


def test_scenario_d_sensor_device_auth_and_quality_control(
    client: TestClient, sample_farm: Farm, sample_plot: Plot, farmer_token: str
):
    """Scenario D: IoT device registration, token authentication, stuck and uncalibrated detection."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Register device
    reg_res = client.post(
        f"/api/v1/sense/farms/{sample_farm.id}/devices",
        headers=headers,
        json={
            "device_serial_number": "SENS-WAR-9901",
            "device_category": "SOIL_PROBE",
            "plot_id": sample_plot.id
        }
    )
    assert reg_res.status_code == 201
    dev_data = reg_res.json()
    device_id = dev_data["id"]
    device_token = dev_data["auth_token"]
    assert device_token.startswith("dev_sec_")

    # 2. Ingest telemetry before calibration -> UNCALIBRATED flag
    now = datetime.now(timezone.utc)
    push_res = client.post(
        "/api/v1/sense/telemetry",
        headers={"Authorization": f"Bearer {device_token}"},
        json={
            "device_id": device_id,
            "plot_id": sample_plot.id,
            "timestamp": now.isoformat(),
            "measurements": {
                "soil_moisture_pct": 28.5,
                "soil_temperature_c": 26.2,
                "ambient_temperature_c": 30.1,
                "relative_humidity_pct": 72.0
            }
        }
    )
    assert push_res.status_code == 201
    assert push_res.json()["data_quality_flag"] == "UNCALIBRATED"
    assert push_res.json()["calibration_valid"] is False

    # 3. Add valid calibration
    cal_res = client.post(
        f"/api/v1/sense/devices/{device_id}/calibration",
        headers=headers,
        json={
            "calibrated_by": "KVK Agronomy Lab",
            "valid_days": 180,
            "coefficients": {"slope": 1.02, "offset": -0.5}
        }
    )
    assert cal_res.status_code == 201
    assert cal_res.json()["is_valid"] is True

    # 4. Ingest again -> VALID flag
    push_res2 = client.post(
        "/api/v1/sense/telemetry",
        headers={"Authorization": f"Bearer {device_token}"},
        json={
            "device_id": device_id,
            "plot_id": sample_plot.id,
            "timestamp": (now + timedelta(minutes=15)).isoformat(),
            "measurements": {
                "soil_moisture_pct": 29.1,
                "soil_temperature_c": 26.4
            }
        }
    )
    assert push_res2.status_code == 201
    assert push_res2.json()["data_quality_flag"] == "VALID"
    assert push_res2.json()["calibration_valid"] is True


def test_scenario_e_evidence_fusion_conflict_resolution(
    client: TestClient, db_session: Session, sample_plot: Plot, farmer_token: str
):
    """Scenario E: Evidence fusion conflict resolution (NDVI drop + recent harvest log)."""
    headers = {"Authorization": f"Bearer {farmer_token}"}
    now = datetime.now(timezone.utc)

    # 1. Record declining satellite observation
    SatelliteService.record_observation(
        db=db_session,
        plot_id=sample_plot.id,
        observation_date=now,
        mean_ndvi=0.38,  # Low/declining
        min_ndvi=0.25,
        max_ndvi=0.45
    )

    # 2. Record recent farmer harvest operation in CropPulse
    op = FarmOperation(
        plot_id=sample_plot.id,
        operation_type="HARVEST",
        execution_date=(now - timedelta(days=2)).date(),
        details_json=json.dumps({"notes": "First picking of cotton bolls completed."})
    )
    db_session.add(op)
    db_session.commit()

    # 3. Evaluate fusion
    res = client.get(f"/api/v1/fusion/plots/{sample_plot.id}/assessment", headers=headers)
    assert res.status_code == 200
    data = res.json()

    # Verify contradiction detected and resolved
    assert data["primary_stress_driver"] == "OPERATIONAL_CLEARING"
    assert data["overall_vigor_status"] == "VEGETATIVE_CLEARING"
    assert len(data["contradictions_detected"]) >= 1
    assert data["contradictions_detected"][0]["conflict_type"] == "CANOPY_DROP_VS_MANAGEMENT_ACTION"

    # Verify multilingual explanations
    assert "harvesting or pruning" in data["farmer_explanation"]["en"].lower()
    assert "కోత లేదా కత్తిరింపు" in data["farmer_explanation"]["te"]
    assert "कटाई या छंटाई" in data["farmer_explanation"]["hi"]


def test_scenario_f_yield_forecasting_withholding_gate(
    client: TestClient, db_session: Session, sample_plot: Plot, sample_season: CropSeason, farmer_token: str
):
    """Scenario F: Yield prediction withholding gate when historical sample count < 50."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # Record 1 harvest measurement (insufficient sample size < 50)
    harvest = PredictService.record_harvest(
        db=db_session,
        plot_id=sample_plot.id,
        season_id=sample_season.id,
        harvest_date=datetime.now(timezone.utc),
        yield_quintals_per_acre=7.5,
        total_harvest_kg=1500.0,
        provenance_tier="TIER_1_VERIFIED_WEIGHBRIDGE"
    )
    assert harvest.id is not None

    # Request forecast
    res = client.get(f"/api/v1/predict/plots/{sample_plot.id}/forecast", headers=headers)
    assert res.status_code == 200
    fc = res.json()

    # Strict Withholding Verification
    assert fc["is_forecast_available"] is False
    assert fc["forecast_status"] == "WITHHELD_INSUFFICIENT_DATA"
    assert fc["predicted_yield_min"] is None
    assert fc["predicted_yield_max"] is None
    assert fc["sample_count_available"] == 1
    assert fc["minimum_sample_threshold_required"] == 50
    assert "below the minimum statistical power threshold" in fc["withholding_reason"]


def test_scenario_g_knowledge_graph_multihop_traversal(client: TestClient, farmer_token: str):
    """Scenario G: Knowledge graph multi-hop relational traversal."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # Query traversal for seeded Rice Blast
    res = client.get("/api/v1/knowledge-graph/traverse?entity=Rice Blast", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["root_entity"]["canonical_name"] == "Rice Blast"
    assert data["root_entity"]["scientific_name"] == "Magnaporthe oryzae"
    assert len(data["hops"]) >= 3

    # Check relation types
    rel_types = [h["relationship_type"] for h in data["hops"]]
    assert "AFFECTS_CROP" in rel_types
    assert "FAVORED_BY_CONDITION" in rel_types
    assert "SUPPRESSED_BY_PRACTICE" in rel_types

    # Check that PJTSAU evidence source is cited
    assert all("PJTSAU" in h["evidence_source"] for h in data["hops"])
