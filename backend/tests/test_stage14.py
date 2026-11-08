"""
ACREVIA - Stage 14 Automated Test Suite.
Validates Agricultural Interoperability, Open API Ecosystem, Consent-Driven Data Exchange,
Partner Integrations, Connector Framework, Webhooks Outbox, and Security Invariants.
"""

from datetime import datetime, timezone
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.farm import Farm, Plot
from backend.app.models.user import User
from backend.app.models.interoperability import (
    IntegrationPartner,
    PartnerIntegration,
    ApiApplication,
    ApiCredential,
    DataSharingGrant,
    WebhookEndpoint,
    WebhookEvent,
    WebhookDelivery,
)
from backend.app.models.exchange import DataExchangeJob, DataMappingProfile
from backend.app.services.canonical_standards import CanonicalStandardsService
from backend.app.services.connector_bridge import ConnectorBridgeManager
from backend.app.services.developer_service import DeveloperService
from backend.app.services.webhook_service import WebhookService, WebhookSecurityError


@pytest.fixture
def test_farm(db_session: Session, farmer_user: User) -> Farm:
    """Fixture providing a verified farm and plot for farmer_user."""
    farm = Farm(
        owner_id=farmer_user.id,
        name="Venkateshwara Krishi Kshetram",
        district="Warangal",
        mandal="Geesugonda",
        village="Dharmaram",
        total_acreage=6.5,
    )
    db_session.add(farm)
    db_session.commit()
    db_session.refresh(farm)

    plot = Plot(
        farm_id=farm.id,
        name="Main Cotton Plot",
        acreage=4.0,
        soil_type="BLACK_COTTON",
        irrigation_source="DRIP",
    )
    db_session.add(plot)
    db_session.commit()
    db_session.refresh(plot)
    return farm


# ============================================================================
# Scenario A: Canonical Standards & Unit Conversions
# ============================================================================

def test_canonical_unit_conversions(client: TestClient, farmer_token: str):
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Supported units registry
    res = client.get("/api/v1/standards/units", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "MASS" in data
    assert "AREA" in data
    assert "kg" in data["MASS"]
    assert "quintal" in data["MASS"]
    assert "acre" in data["AREA"]
    assert "gunta" in data["AREA"]

    # 2. Conversion: 100 kg -> 1 quintal
    res = client.post(
        "/api/v1/standards/convert-unit",
        headers=headers,
        json={"value": 100.0, "from_unit": "kg", "to_unit": "quintal", "category": "MASS"}
    )
    assert res.status_code == 200
    conv = res.json()
    assert conv["converted_value"] == 1.0
    assert conv["conversion_factor"] == 0.01

    # 3. Conversion: 40 gunta -> 1 acre (Telangana local standard)
    res = client.post(
        "/api/v1/standards/convert-unit",
        headers=headers,
        json={"value": 40.0, "from_unit": "gunta", "to_unit": "acre", "category": "AREA"}
    )
    assert res.status_code == 200
    conv = res.json()
    assert round(conv["converted_value"], 2) == 1.0

    # 4. Unknown unit rejection
    res = client.post(
        "/api/v1/standards/convert-unit",
        headers=headers,
        json={"value": 10.0, "from_unit": "fake_unit", "to_unit": "kg", "category": "MASS"}
    )
    assert res.status_code == 400


def test_canonical_crop_taxonomy(client: TestClient, farmer_token: str):
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # All crops taxonomy
    res = client.get("/api/v1/standards/taxonomy/crops", headers=headers)
    assert res.status_code == 200
    tax = res.json()
    assert "COTTON" in tax
    assert "RICE" in tax
    assert "CHILLI" in tax

    # Multi-language verification for Cotton
    cotton = tax["COTTON"]
    assert cotton["botanical_name"] == "Gossypium hirsutum"
    assert "ప్రత్తి" in cotton["names"]["te"]
    assert "कपास" in cotton["names"]["hi"]

    # Single crop code lookup
    res = client.get("/api/v1/standards/taxonomy/crops/CHILLI", headers=headers)
    assert res.status_code == 200
    chilli = res.json()
    assert chilli["botanical_name"] == "Capsicum annuum"
    assert "మిరప" in chilli["names"]["te"]


# ============================================================================
# Scenario B: Connector Framework (ACREVIA Bridge)
# ============================================================================

def test_connector_bridge_health_and_adapters(client: TestClient, farmer_token: str):
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # Health checks across all 5 connectors
    res = client.get("/api/v1/standards/health", headers=headers)
    assert res.status_code == 200
    checks = res.json()
    assert len(checks) >= 5
    connectors = [c["connector"] for c in checks]
    assert "SoilLabConnector" in connectors
    assert "MarketPriceConnector" in connectors
    assert "WeatherConnector" in connectors
    assert "SatelliteConnector" in connectors
    assert "IoTTelemetryConnector" in connectors

    for check in checks:
        assert check["status"] == "HEALTHY"
        assert check["latency_ms"] > 0

    # Test direct adapter normalization
    soil_conn = ConnectorBridgeManager.get_connector("SOIL_LAB")
    raw_soil = soil_conn.fetch_data({"sample_code": "TS-SL-TEST"})
    normalized_soil = soil_conn.normalize_data(raw_soil)
    assert len(normalized_soil) == 1
    assert normalized_soil[0]["sample_code"] == "TS-SL-TEST"
    assert normalized_soil[0]["ph"] == 7.4
    assert normalized_soil[0]["ec_ds_m"] == 0.85


# ============================================================================
# Scenario C: Partner Onboarding & Institutional Verification
# ============================================================================

def test_partner_registry_and_verification_lifecycle(client: TestClient, farmer_token: str):
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Register new partner application
    res = client.post(
        "/api/v1/partners/register",
        headers=headers,
        json={
            "name": "PJTSAU Regional Agricultural Research Station",
            "partner_type": "UNIVERSITY",
            "description": "Professor Jayashankar Telangana State Agricultural University research division",
            "website": "https://pjtsau.edu.in",
            "contact_email": "rars.warangal@pjtsau.edu.in",
            "legal_entity_number": "U-TS-PJTSAU-001"
        }
    )
    assert res.status_code == 201
    partner = res.json()
    partner_id = partner["id"]
    assert partner["verification_status"] == "APPLICATION_SUBMITTED"

    # 2. List partners with filtering
    res = client.get("/api/v1/partners?status=APPLICATION_SUBMITTED", headers=headers)
    assert res.status_code == 200
    partners = res.json()
    assert any(p["id"] == partner_id for p in partners)

    # 3. Verify partner (administrative review gate)
    res = client.post(
        f"/api/v1/partners/{partner_id}/verify",
        headers=headers,
        json={
            "verification_status": "VERIFIED",
            "verification_notes": "Official university credentials and ICAR accreditation verified"
        }
    )
    assert res.status_code == 200
    verified_partner = res.json()
    assert verified_partner["verification_status"] == "VERIFIED"
    assert verified_partner["verified_at"] is not None

    # 4. Register partner integration capability
    res = client.post(
        f"/api/v1/partners/{partner_id}/integrations",
        headers=headers,
        json={
            "connector_type": "KNOWLEDGE_BASE",
            "display_name": "PJTSAU Package of Practices Adapter",
            "capabilities": ["POP_RETRIEVAL", "VARIETY_RECOMMENDATIONS", "CLIMATE_ADVISORIES"],
            "adapter_config": {"protocol": "REST_V2", "rate_limit": 100}
        }
    )
    assert res.status_code == 201
    integration = res.json()
    assert integration["partner_id"] == partner_id
    assert integration["status"] == "ACTIVE"
    assert integration["health_status"] == "HEALTHY"


# ============================================================================
# Scenario D: Developer Applications & Scoped API Credentials
# ============================================================================

def test_developer_applications_and_scoped_credentials(
    client: TestClient, db_session: Session, farmer_user: User, farmer_token: str
):
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. Create developer sandbox application
    res = client.post(
        "/api/v1/developer/applications",
        headers=headers,
        json={
            "name": "Telangana Smart Ag IoT Client",
            "description": "Automated LoRa sensor data forwarder",
            "is_sandbox": True,
            "redirect_uris": ["https://oauth.iot-client.test/callback"]
        }
    )
    assert res.status_code == 201
    app_data = res.json()
    app_id = app_data["id"]
    assert app_data["is_sandbox"] is True
    assert app_data["is_active"] is True

    # 2. Generate scoped credential
    res = client.post(
        f"/api/v1/developer/applications/{app_id}/credentials",
        headers=headers,
        json={
            "scopes": ["crops:read", "diagnostics:read", "soil:read"],
            "rate_limit_per_minute": 120,
            "expires_in_days": 180
        }
    )
    assert res.status_code == 201
    cred_data = res.json()
    cred_id = cred_data["id"]
    client_id = cred_data["client_id"]
    client_secret = cred_data["client_secret"]

    # Verify prefix and secret returned ONCE
    assert client_id.startswith("ak_sand_")
    assert client_secret.startswith("sec_snd_")

    # Invariant: Secret must NOT be stored in plaintext in database!
    db_cred = db_session.get(ApiCredential, cred_id)
    assert db_cred.hashed_secret != client_secret
    assert len(db_cred.hashed_secret) == 64  # SHA-256 hex string

    # 3. Verify credential programmatically
    valid, verified_cred, err = DeveloperService.verify_credential(
        db=db_session,
        client_id=client_id,
        client_secret=client_secret,
        required_scope="crops:read"
    )
    assert valid is True
    assert err is None
    assert verified_cred.id == cred_id

    # 4. Verify scope failure
    valid_scope, _, err_scope = DeveloperService.verify_credential(
        db=db_session,
        client_id=client_id,
        client_secret=client_secret,
        required_scope="admin:superuser"
    )
    assert valid_scope is False
    assert "Insufficient scope" in err_scope

    # 5. Revoke credential
    res = client.delete(f"/api/v1/developer/credentials/{cred_id}", headers=headers)
    assert res.status_code == 200
    revoked = res.json()
    assert revoked["is_active"] is False

    # Verify revoked credential fails authentication
    valid_rev, _, err_rev = DeveloperService.verify_credential(
        db=db_session,
        client_id=client_id,
        client_secret=client_secret,
    )
    assert valid_rev is False
    assert "inactive or revoked" in err_rev


# ============================================================================
# Scenario E: Farmer Consent & Data Sharing Grants
# ============================================================================

def test_farmer_consent_grants_and_tenant_isolation(
    client: TestClient, db_session: Session, farmer_token: str, second_farmer_user: User
):
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # Register verified partner
    partner = IntegrationPartner(
        name="Khammam District FPO Federation",
        partner_type="FPO",
        contact_email="fpo.khammam@telangana.test",
        verification_status="VERIFIED",
    )
    db_session.add(partner)
    db_session.commit()
    db_session.refresh(partner)

    # 1. Farmer A grants explicit consent
    res = client.post(
        "/api/v1/consent/grants",
        headers=headers,
        json={
            "partner_id": partner.id,
            "data_categories": ["FARM_PROFILE", "SOIL_HEALTH", "OBSERVATIONS"],
            "purpose": "Collective Cotton Seed Procurement & Nitrogen Advisory",
            "anonymize_pii": True,
            "redact_exact_gps": True,
            "expires_in_days": 90
        }
    )
    assert res.status_code == 201
    grant = res.json()
    grant_id = grant["id"]
    assert grant["is_revoked"] is False
    assert grant["anonymize_pii"] is True
    assert grant["redact_exact_gps"] is True

    # 2. Farmer A lists grants
    res = client.get("/api/v1/consent/grants", headers=headers)
    assert res.status_code == 200
    grants = res.json()
    assert any(g["id"] == grant_id for g in grants)

    # 3. Tenant Isolation: Second farmer cannot revoke Farmer A's grant
    second_token = client.app.dependency_overrides  # We can craft token for second_farmer_user
    from backend.app.core.security import create_access_token
    second_bearer = create_access_token(subject=second_farmer_user.id, roles=["FARMER"])
    second_headers = {"Authorization": f"Bearer {second_bearer}"}

    res = client.post(
        f"/api/v1/consent/grants/{grant_id}/revoke",
        headers=second_headers,
        json={"reason": "Malicious unauthorized revocation attempt"}
    )
    assert res.status_code == 403

    # 4. Farmer A revokes own grant
    res = client.post(
        f"/api/v1/consent/grants/{grant_id}/revoke",
        headers=headers,
        json={"reason": "FPO season advisory cycle completed"}
    )
    assert res.status_code == 200
    revoked_grant = res.json()
    assert revoked_grant["is_revoked"] is True
    assert revoked_grant["revocation_reason"] == "FPO season advisory cycle completed"


# ============================================================================
# Scenario F: Data Exchange (Export & Import with Conflict Preservation)
# ============================================================================

def test_data_export_and_download_all_formats(client: TestClient, test_farm: Farm, farmer_token: str):
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. JSON Export
    res = client.post(
        "/api/v1/exchange/export",
        headers=headers,
        json={
            "farm_id": test_farm.id,
            "categories": ["ALL"],
            "format": "JSON",
            "redact_pii": True,
            "redact_gps": True
        }
    )
    assert res.status_code == 201
    job = res.json()
    assert job["status"] == "COMPLETED"
    assert job["checksum_sha256"] is not None
    json_job_id = job["id"]

    # Download JSON artifact
    res = client.get(f"/api/v1/exchange/download/{json_job_id}", headers=headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/json"
    exported_json = res.json()
    assert "schema_version" in exported_json
    assert "farms" in exported_json["entities"]

    # 2. ARCHIVE (ZIP with MANIFEST.json) Export
    res = client.post(
        "/api/v1/exchange/export",
        headers=headers,
        json={
            "farm_id": test_farm.id,
            "categories": ["FARM_PROFILE", "FINANCIAL_LEDGER"],
            "format": "ARCHIVE",
            "redact_pii": True,
            "redact_gps": True
        }
    )
    assert res.status_code == 201
    zip_job = res.json()
    assert zip_job["status"] == "COMPLETED"
    zip_job_id = zip_job["id"]

    # Download ZIP artifact
    res = client.get(f"/api/v1/exchange/download/{zip_job_id}", headers=headers)
    assert res.status_code == 200
    assert "application/zip" in res.headers["content-type"]
    assert len(res.content) > 100  # valid binary zip


def test_data_import_with_non_overwriting_conflict_preservation(
    client: TestClient, db_session: Session, test_farm: Farm, farmer_token: str
):
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # Pre-seed existing soil sample
    from backend.app.models.soil_health import SoilSample
    existing_sample = SoilSample(
        plot_id=test_farm.plots[0].id,
        sampled_by_user_id=test_farm.owner_id,
        sample_code="TS-WAR-2026-001",
        sampling_depth_min_cm=0.0,
        sampling_depth_max_cm=15.0,
        sampling_date=datetime.now(timezone.utc),
    )
    db_session.add(existing_sample)
    db_session.commit()

    # Import payload containing the exact same sample_code
    import_payload = json.dumps([
        {"sample_code": "TS-WAR-2026-001", "ph": 7.4, "ec_ds_m": 0.82, "organic_carbon_percent": 0.61},
        {"sample_code": "TS-WAR-2026-002", "ph": 6.8, "ec_ds_m": 0.45, "organic_carbon_percent": 0.50}
    ])

    res = client.post(
        "/api/v1/exchange/import",
        headers=headers,
        json={
            "farm_id": test_farm.id,
            "format": "JSON",
            "target_category": "SOIL_TESTS",
            "data_payload": import_payload,
            "preserve_conflicts": True
        }
    )
    assert res.status_code == 201
    job = res.json()
    assert job["status"] == "COMPLETED"
    assert job["records_processed"] == 2
    # Invariant: Must detect and preserve conflict, never silently overwrite!
    assert job["conflicts_detected"] == 1


# ============================================================================
# Scenario G: Webhooks, Transactional Outbox & SSRF Protection
# ============================================================================

def test_webhook_registration_hmac_and_ssrf_protection(
    client: TestClient, db_session: Session, farmer_token: str
):
    headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1. SSRF Protection: Loopback destination must be rejected
    res = client.post(
        "/api/v1/webhooks/endpoints",
        headers=headers,
        json={
            "url": "http://127.0.0.1:8080/internal/webhook",
            "event_types": ["crop.diagnosis.completed"]
        }
    )
    assert res.status_code == 400
    assert "SSRF" in res.json()["detail"] or "prohibited" in res.json()["detail"].lower()

    # 2. SSRF Protection: Localhost must be rejected
    res = client.post(
        "/api/v1/webhooks/endpoints",
        headers=headers,
        json={
            "url": "http://localhost:5000/webhook",
            "event_types": ["crop.diagnosis.completed"]
        }
    )
    assert res.status_code == 400

    # 3. SSRF Protection: Cloud metadata 169.254.169.254 must be rejected
    res = client.post(
        "/api/v1/webhooks/endpoints",
        headers=headers,
        json={
            "url": "http://169.254.169.254/latest/meta-data/",
            "event_types": ["crop.diagnosis.completed"]
        }
    )
    assert res.status_code == 400

    # 4. Valid HTTPS external endpoint registration
    res = client.post(
        "/api/v1/webhooks/endpoints",
        headers=headers,
        json={
            "url": "https://api.partner-agritech.org/events/acrevia",
            "event_types": ["crop.diagnosis.completed", "farm.risk.alert"]
        }
    )
    assert res.status_code == 201
    ep = res.json()
    endpoint_id = ep["id"]
    secret = ep["signing_secret"]
    assert secret.startswith("whsec_")

    # 5. HMAC Signature Verification Unit Test
    test_payload = '{"event": "crop.diagnosis.completed", "status": "CONFIRMED"}'
    ts_now = str(int(datetime.now(timezone.utc).timestamp()))
    sig = WebhookService.compute_hmac_signature(secret, ts_now, test_payload)
    assert sig.startswith("sha256=")

    # Verify fresh timestamp
    assert WebhookService.verify_incoming_signature(secret, sig, ts_now, test_payload) is True

    # Reject stale timestamp (> 300 seconds)
    stale_ts = str(int(datetime.now(timezone.utc).timestamp()) - 600)
    stale_sig = WebhookService.compute_hmac_signature(secret, stale_ts, test_payload)
    assert WebhookService.verify_incoming_signature(secret, stale_sig, stale_ts, test_payload) is False

    # 6. Outbox dispatch test
    res = client.post(
        "/api/v1/webhooks/test-dispatch?event_type=crop.diagnosis.completed",
        headers=headers,
    )
    assert res.status_code == 201
    event_data = res.json()
    assert event_data["status"] == "DELIVERED"

    # Verify delivery record was created
    res = client.get("/api/v1/webhooks/deliveries", headers=headers)
    assert res.status_code == 200
    deliveries = res.json()
    assert len(deliveries) >= 1
    assert deliveries[0]["status"] == "SUCCESS"
    assert deliveries[0]["response_status_code"] == 200
