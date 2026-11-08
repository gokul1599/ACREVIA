"""
ACREVIA - Stage 11 Automated Test Suite.
Validates Agricultural Economics, Farm Financial Ledger, Market Analytics,
Harvest Operations, Post-Harvest Quality Assays, Produce Traceability, and PMFBY Loss Bundles.
"""

from datetime import date
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.farm import Farm, Plot
from backend.app.models.crop import CropSeason
from backend.app.models.financial_ledger import FarmExpense, SaleTransaction
from backend.app.models.produce_traceability import ProduceLot


def test_scenario_a_farm_financial_ledger(
    client: TestClient,
    sample_farm: Farm,
    sample_plot: Plot,
    sample_season: CropSeason,
    farmer_token: str,
):
    """Scenario A: Farm expense recording, receipt metadata, corrections audit, and sales."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Record an initial expense (Seeds)
    seed_payload = {
        "farm_id": sample_farm.id,
        "plot_id": sample_plot.id,
        "crop_season_id": sample_season.id,
        "category": "SEEDS",
        "description": "3 packets RCH-659 BG II Hybrid Cotton Seeds",
        "amount": "2580.00",
        "currency": "INR",
        "quantity": 3.0,
        "unit": "BAGS",
        "transaction_date": "2026-06-18",
        "payment_status": "PAID",
        "payment_method": "UPI",
        "vendor_name": "Warangal Agro Seeds Agency",
        "receipt_url": "https://storage.acrevia.ag/receipts/rec_seeds_01.jpg",
    }
    res = client.post("/api/v1/ledger/expenses", json=seed_payload, headers=headers)
    assert res.status_code == 201
    expense_data = res.json()
    expense_id = expense_data["id"]
    assert expense_data["category"] == "SEEDS"
    assert expense_data["amount"] == "2580.00"
    assert expense_data["verification_state"] == "PENDING_REVIEW"

    # 2. Record a second expense (Fertilizer)
    fert_payload = {
        "farm_id": sample_farm.id,
        "plot_id": sample_plot.id,
        "crop_season_id": sample_season.id,
        "category": "FERTILIZERS",
        "description": "4 bags Urea 45kg from Geesugonda PACS",
        "amount": "1066.00",
        "currency": "INR",
        "quantity": 4.0,
        "unit": "BAGS",
        "transaction_date": "2026-07-10",
        "payment_status": "PAID",
        "payment_method": "CASH",
        "vendor_name": "Geesugonda PACS",
    }
    res_fert = client.post("/api/v1/ledger/expenses", json=fert_payload, headers=headers)
    assert res_fert.status_code == 201
    assert res_fert.json()["verification_state"] == "UNVERIFIED"

    # 3. List expenses
    list_res = client.get(f"/api/v1/ledger/expenses?farm_id={sample_farm.id}", headers=headers)
    assert list_res.status_code == 200
    expenses = list_res.json()
    assert len(expenses) == 2

    # 4. Correct expense with audit trail
    corr_payload = {
        "new_amount": "2430.00",
        "reason": "Corrected for ₹150 state seed subsidy discount on final invoice receipt.",
    }
    corr_res = client.post(f"/api/v1/ledger/expenses/{expense_id}/correct", json=corr_payload, headers=headers)
    assert corr_res.status_code == 200
    updated_exp = corr_res.json()
    assert updated_exp["amount"] == "2430.00"
    assert len(updated_exp["corrections"]) == 1
    assert updated_exp["corrections"][0]["previous_amount"] == "2580.00"
    assert updated_exp["corrections"][0]["new_amount"] == "2430.00"

    # 5. Record a crop sale transaction
    sale_payload = {
        "crop_season_id": sample_season.id,
        "buyer_name": "Enumamula Cotton Traders",
        "buyer_type": "MANDI_TRADER",
        "quantity_sold": "20.00",
        "unit": "QUINTAL",
        "price_per_unit": "7400.00",
        "gross_amount": "148000.00",
        "deductions_amount": "1800.00",
        "sale_date": "2026-10-25",
        "payment_status": "PAID",
        "notes": "Moisture docked 1.0%",
    }
    sale_res = client.post("/api/v1/ledger/sales", json=sale_payload, headers=headers)
    assert sale_res.status_code == 201
    sale_data = sale_res.json()
    assert sale_data["gross_amount"] == "148000.00"
    assert sale_data["deductions_amount"] == "1800.00"
    assert sale_data["net_amount"] == "146200.00"

    # 6. List sales
    sales_list = client.get(f"/api/v1/ledger/sales?crop_season_id={sample_season.id}", headers=headers)
    assert sales_list.status_code == 200
    assert len(sales_list.json()) == 1


def test_scenario_b_market_intelligence_and_comparison(
    client: TestClient,
    sample_plot: Plot,
    farmer_token: str,
):
    """Scenario B: Mandi price board queries and distance-adjusted net realization."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Query market prices for Cotton
    prices_res = client.get("/api/v1/market/prices?crop_id=cotton")
    assert prices_res.status_code == 200
    prices = prices_res.json()
    assert len(prices) >= 1
    assert any("Enumamula" in p["market"]["market_name"] or "Warangal" in p["market"]["market_name"] for p in prices)

    # 2. Compare market realizations for 25 quintals of cotton
    comp_res = client.get(
        f"/api/v1/market/compare?crop_id=cotton&quantity_quintals=25.0&plot_id={sample_plot.id}",
        headers=headers,
    )
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["canonical_crop_id"] == "cotton"
    assert float(comp_data["quantity_quintals"]) == 25.0
    assert len(comp_data["comparisons"]) >= 1

    top_mandi = comp_data["comparisons"][0]
    assert "market_name" in top_mandi
    assert "distance_km" in top_mandi
    assert float(top_mandi["estimated_net_realization"]) > 0
    assert float(top_mandi["effective_rate_per_quintal"]) > 0
    assert "disclaimer" in top_mandi


def test_scenario_c_harvest_operations(
    client: TestClient,
    sample_plot: Plot,
    sample_season: CropSeason,
    farmer_token: str,
):
    """Scenario C: Harvest planning, picking sessions, loss tracking, and produce lot minting."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Create a Harvest Plan
    plan_payload = {
        "plot_id": sample_plot.id,
        "crop_season_id": sample_season.id,
        "planned_start_date": "2026-10-15",
        "planned_end_date": "2026-11-30",
        "estimated_quantity_quintals": "30.00",
        "harvest_method": "MANUAL",
    }
    plan_res = client.post("/api/v1/harvest/plans", json=plan_payload, headers=headers)
    assert plan_res.status_code == 201
    plan_data = plan_res.json()
    plan_id = plan_data["id"]

    # 2. Record 1st picking session (automatically mints ProduceLot)
    session_payload = {
        "plot_id": sample_plot.id,
        "crop_season_id": sample_season.id,
        "harvest_plan_id": plan_id,
        "picking_number": 1,
        "harvest_date": "2026-10-20",
        "harvested_quantity": "14.50",
        "unit": "QUINTAL",
        "quantity_type": "MEASURED",
        "loss_quantity": "0.40",
        "notes": "1st picking - clean bolls, minimal trash",
    }
    session_res = client.post("/api/v1/harvest/sessions", json=session_payload, headers=headers)
    assert session_res.status_code == 201
    session_data = session_res.json()
    assert session_data["picking_number"] == 1
    assert session_data["harvested_quantity"] == "14.50"
    assert session_data["produce_lot_id"] is not None
    assert session_data["lot_code"].startswith("ACR-")

    # 3. List harvest plans and sessions
    sessions_list = client.get(f"/api/v1/harvest/sessions?crop_season_id={sample_season.id}", headers=headers)
    assert sessions_list.status_code == 200
    assert len(sessions_list.json()) == 1


def test_scenario_d_post_harvest_quality_and_storage(
    client: TestClient,
    sample_farm: Farm,
    sample_plot: Plot,
    sample_season: CropSeason,
    farmer_token: str,
):
    """Scenario D: Moisture provenance, quality assays, and storage lot assignments."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Harvest a lot first
    session_payload = {
        "plot_id": sample_plot.id,
        "crop_season_id": sample_season.id,
        "picking_number": 1,
        "harvest_date": "2026-10-22",
        "harvested_quantity": "16.00",
        "unit": "QUINTAL",
        "quantity_type": "MEASURED",
    }
    session_res = client.post("/api/v1/harvest/sessions", json=session_payload, headers=headers)
    produce_lot_id = session_res.json()["produce_lot_id"]

    # 2. Record moisture measurement
    moisture_payload = {
        "lot_id": produce_lot_id,
        "parameter_name": "MOISTURE_PCT",
        "measured_value": "8.40",
        "unit": "%",
        "measurement_method": "MEASURED_DIGITAL_SENSOR",
        "instrument_details": "AgroSens Pin Moisture Meter Pro",
    }
    m_res = client.post("/api/v1/quality/measurements", json=moisture_payload, headers=headers)
    assert m_res.status_code == 201
    assert m_res.json()["measured_value"] == "8.40"

    # 3. Record staple length measurement
    staple_payload = {
        "lot_id": produce_lot_id,
        "parameter_name": "STAPLE_LENGTH_MM",
        "measured_value": "29.50",
        "unit": "mm",
        "measurement_method": "VERIFIED_LAB_ASSAY",
        "instrument_details": "Warangal APMC Grading Lab",
    }
    s_res = client.post("/api/v1/quality/measurements", json=staple_payload, headers=headers)
    assert s_res.status_code == 201

    # 4. Create a storage location
    storage_loc_payload = {
        "farm_id": sample_farm.id,
        "name": "Warangal Cold Storage Unit 4",
        "storage_type": "COMMERCIAL_COLD_STORAGE",
        "capacity_quintals": "500.00",
        "district": "Warangal",
        "is_temperature_controlled": True,
    }
    loc_res = client.post("/api/v1/quality/storage/locations", json=storage_loc_payload, headers=headers)
    assert loc_res.status_code == 201
    storage_loc_id = loc_res.json()["id"]

    # 5. Assign produce lot to storage
    storage_lot_payload = {
        "lot_id": produce_lot_id,
        "storage_location_id": storage_loc_id,
        "quantity_stored": "10.00",
        "unit": "QUINTAL",
        "entry_date": "2026-10-23",
    }
    store_res = client.post("/api/v1/quality/storage/lots", json=storage_lot_payload, headers=headers)
    assert store_res.status_code == 201
    assert store_res.json()["current_status"] == "STORED"


def test_scenario_e_produce_traceability_and_privacy_redaction(
    client: TestClient,
    sample_plot: Plot,
    sample_season: CropSeason,
    farmer_token: str,
):
    """Scenario E: Chain of custody, quantity conservation balance, and public QR privacy redaction."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Harvest a lot
    session_payload = {
        "plot_id": sample_plot.id,
        "crop_season_id": sample_season.id,
        "picking_number": 1,
        "harvest_date": "2026-10-25",
        "harvested_quantity": "20.00",
        "unit": "QUINTAL",
        "quantity_type": "MEASURED",
    }
    session_res = client.post("/api/v1/harvest/sessions", json=session_payload, headers=headers)
    produce_lot_id = session_res.json()["produce_lot_id"]

    # 2. Add a quality assay to test public summary
    client.post(
        "/api/v1/quality/measurements",
        json={
            "lot_id": produce_lot_id,
            "parameter_name": "MOISTURE_PCT",
            "measured_value": "8.80",
            "unit": "%",
            "measurement_method": "MEASURED_DIGITAL_SENSOR",
        },
        headers=headers,
    )

    # 3. Retrieve internal lot detail
    lot_res = client.get(f"/api/v1/trace/lots/{produce_lot_id}", headers=headers)
    assert lot_res.status_code == 200
    lot_data = lot_res.json()
    qr_token = lot_data["qr_token"]
    assert lot_data["initial_quantity"] == "20.00"
    assert lot_data["remaining_quantity"] == "20.00"
    assert len(lot_data["movements"]) >= 1

    # 4. Test quantity conservation law: transferring 25 quintals when only 20 remain must fail
    overdraft_payload = {
        "movement_type": "SALE",
        "source_location": "Farm Yard",
        "destination_location": "Trader Truck",
        "quantity_transferred": "25.00",
        "unit": "QUINTAL",
        "actor_name": "Trader Agent",
    }
    od_res = client.post(f"/api/v1/trace/lots/{produce_lot_id}/movements", json=overdraft_payload, headers=headers)
    assert od_res.status_code == 400
    assert "remains in this lot" in od_res.json()["detail"]

    # 5. Valid movement of 12 quintals
    valid_movement = {
        "movement_type": "SALE",
        "source_location": "Farm Yard",
        "destination_location": "Warangal APMC",
        "quantity_transferred": "12.00",
        "unit": "QUINTAL",
        "actor_name": "Warangal APMC Trader",
    }
    vm_res = client.post(f"/api/v1/trace/lots/{produce_lot_id}/movements", json=valid_movement, headers=headers)
    assert vm_res.status_code == 201

    # Verify updated balance
    lot_updated = client.get(f"/api/v1/trace/lots/{produce_lot_id}", headers=headers).json()
    assert lot_updated["remaining_quantity"] == "8.00"
    assert lot_updated["current_status"] == "PARTIALLY_SOLD"

    # 6. Public QR verification endpoint (Open access, no bearer token)
    public_res = client.get(f"/api/v1/trace/public/{qr_token}")
    assert public_res.status_code == 200
    pub_data = public_res.json()
    assert pub_data["lot_code"] == lot_data["lot_code"]
    assert "Cotton" in pub_data["crop_name"]
    assert pub_data["district"] == "Warangal"
    assert pub_data["state"] == "Telangana"
    assert pub_data["origin_verification"] == "VERIFIED_ACREVIA_FARM"
    assert len(pub_data["quality_parameters"]) >= 1
    assert "overall_grade" in pub_data

    # Strict Privacy Redaction: ensure farmer PII and exact GPS coordinates are not leaked
    assert "farmer_name" not in pub_data
    assert "phone" not in pub_data
    assert "latitude" not in pub_data
    assert "longitude" not in pub_data
    assert "receipt_url" not in pub_data


def test_scenario_f_crop_season_economics_and_loss_evidence(
    client: TestClient,
    sample_farm: Farm,
    sample_plot: Plot,
    sample_season: CropSeason,
    farmer_token: str,
):
    """Scenario F: Cost of cultivation, gross revenue, net margins, and PMFBY evidence package."""
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Query season economics
    econ_res = client.get(f"/api/v1/economics/seasons/{sample_season.id}", headers=headers)
    assert econ_res.status_code == 200
    econ_data = econ_res.json()
    assert econ_data["crop_season_id"] == sample_season.id
    assert "total_expenses" in econ_data
    assert "gross_revenue" in econ_data
    assert "net_realization" in econ_data
    assert "completeness_badge" in econ_data
    assert len(econ_data["economic_disclaimers"]) >= 1

    # 2. Generate PMFBY Crop Loss Evidence Package
    evidence_payload = {
        "farm_id": sample_farm.id,
        "plot_id": sample_plot.id,
        "crop_season_id": sample_season.id,
        "incident_date": "2026-10-18",
        "incident_type": "EXCESS_RAINFALL",
        "notes": "Unseasonal October rain causing boll rotting in lower branches.",
    }
    ev_res = client.post("/api/v1/economics/evidence-package", json=evidence_payload, headers=headers)
    assert ev_res.status_code == 201
    ev_data = ev_res.json()
    assert ev_data["incident_type"] == "EXCESS_RAINFALL"
    assert "package_hash" in ev_data
    assert len(ev_data["package_hash"]) == 64  # Valid SHA-256 hex digest
    assert ev_data["package_payload"]["farm"]["name"] == sample_farm.name
    assert ev_data["package_payload"]["attestation"]["compliance_standard"] == "PMFBY_GOI_DISASTER_RELIEF_EVIDENCE"


def test_security_and_tenant_isolation(
    client: TestClient,
    sample_farm: Farm,
    farmer_token: str,
    second_farmer_token: str,
):
    """Security: Cross-farm tenant isolation and input validation."""
    farmer_b_headers = {"Authorization": f"Bearer {second_farmer_token}"}

    # 1. Cross-farm expense listing rejection (Farmer B tries to access Farmer A's farm expenses)
    cross_res = client.get(f"/api/v1/ledger/expenses?farm_id={sample_farm.id}", headers=farmer_b_headers)
    assert cross_res.status_code == 403

    # 2. Negative expense amount rejection
    farmer_a_headers = {"Authorization": f"Bearer {farmer_token}"}
    neg_payload = {
        "farm_id": sample_farm.id,
        "category": "PESTICIDES",
        "description": "Invalid test negative amount",
        "amount": "-500.00",
        "transaction_date": "2026-07-01",
    }
    neg_res = client.post("/api/v1/ledger/expenses", json=neg_payload, headers=farmer_a_headers)
    assert neg_res.status_code == 400

    # 3. Non-existent QR token public query returns 404
    bad_qr_res = client.get("/api/v1/trace/public/non-existent-qr-token-12345")
    assert bad_qr_res.status_code == 404
