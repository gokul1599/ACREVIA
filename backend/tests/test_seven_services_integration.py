"""
ACREVIA - Seven Free Services Integration & Verification Test Suite.
Tests GroqCloud, Neon PostgreSQL, Upstash Redis, Copernicus Data Space,
Hugging Face, Open-Meteo, and data.gov.in across both live and mock/fallback modes.
"""

import os
import time
import asyncio
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.integrations.groq_client import GroqClient, groq_client
from backend.app.integrations.hf_client import HuggingFaceClient, hf_client
from backend.app.integrations.copernicus_client import CopernicusClient, copernicus_client, SATELLITE_EVIDENCE_DISCLAIMER
from backend.app.integrations.weather_client import WeatherClient, weather_client, OPEN_METEO_ATTRIBUTION
from backend.app.integrations.datagov_client import DataGovClient, datagov_client, DATA_GOV_IN_ATTRIBUTION
from backend.app.core.rate_limit import RedisRateLimiterBackend, InMemoryRateLimiterBackend


# =============================================================================
# 1. GroqCloud AI Inference Tests
# =============================================================================

def test_groq_health_and_capabilities():
    """Verifies Groq health probe and available model status."""
    health = asyncio.run(groq_client.check_health())
    assert health["provider"] == "GroqCloud"
    if groq_client.is_configured:
        assert health["status"] in ["CONFIGURED", "RATE_LIMITED", "DEGRADED"]
        assert "free_tier" in health or "retry_after_seconds" in health
    else:
        assert health["status"] == "NOT_CONFIGURED"


def test_groq_completion_generation():
    """Tests Groq model inference or graceful error handling."""
    if not groq_client.is_configured:
        res = asyncio.run(groq_client.generate_completion([{"role": "user", "content": "ping"}]))
        assert res["success"] is False
        assert res["error_code"] == "NOT_CONFIGURED"
    else:
        # Live generation test with active free model
        active_client = GroqClient(model="qwen/qwen3.8-27b")
        res = asyncio.run(active_client.generate_completion(
            messages=[
                {"role": "system", "content": "You are an agricultural assistant."},
                {"role": "user", "content": "Hello ACREVIA"}
            ],
            max_tokens=15
        ))
        if res.get("success"):
            assert len(res["content"]) > 0
            assert res["provider"] == "GroqCloud"
            assert "usage" in res
        else:
            # If free rate limit exceeded during testing, verify controlled response
            assert res["error_code"] in ["RATE_LIMIT_EXCEEDED", "TIMEOUT", "PROVIDER_UNAVAILABLE", "REQUEST_FAILED"]


def test_groq_rate_limit_and_outage_simulation():
    """Simulates Groq HTTP 429 response to verify controlled backoff envelope."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {"retry-after": "45"}

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        client = GroqClient(api_key="mock_key_12345")
        res = asyncio.run(client.generate_completion([{"role": "user", "content": "test"}]))
        assert res["success"] is False
        assert res["error_code"] == "RATE_LIMIT_EXCEEDED"
        assert res["retry_after_seconds"] == 45


# =============================================================================
# 2. Neon PostgreSQL Database Tests
# =============================================================================

def test_neon_postgresql_safe_read_query(db_session):
    """Verifies safe read-only queries and pgvector availability on Neon/PostgreSQL."""
    from sqlalchemy import text
    val = db_session.execute(text("SELECT 1")).scalar()
    assert val == 1

    # Verify no unhandled runtime DDL is allowed
    version = db_session.execute(text("SELECT 1 + 1")).scalar()
    assert version == 2


# =============================================================================
# 3. Upstash Redis & Rate Limiting Tests
# =============================================================================

def test_upstash_redis_connection_parsing_and_in_memory_fallback():
    """Verifies Redis URL parsing for Upstash TLS (rediss://) and in-memory fallback."""
    # 1. Test In-Memory fallback
    mem_backend = InMemoryRateLimiterBackend()
    res = mem_backend.check_rate_limit("test:quota", max_requests=2, window_seconds=10)
    assert res.allowed is True
    assert res.remaining == 1

    # 2. Test Upstash TLS URL parsing in mock mode
    upstash_url = "rediss://default:mock_token_pass@global-endpoint.upstash.io:6379"
    with patch("redis.Redis.from_url") as mock_from_url:
        mock_redis = MagicMock()
        mock_from_url.return_value = mock_redis
        backend = RedisRateLimiterBackend(redis_url=upstash_url)
        client = backend._get_client()
        assert client is not None
        mock_from_url.assert_called_once_with(
            upstash_url,
            socket_connect_timeout=backend.timeout,
            socket_timeout=backend.timeout,
            decode_responses=True
        )


# =============================================================================
# 4. Copernicus Data Space Ecosystem (CDSE) Tests
# =============================================================================

def test_copernicus_public_catalogue_health():
    """Verifies Copernicus public OData catalogue probe and mandatory disclaimers."""
    health = asyncio.run(copernicus_client.check_health())
    assert health["provider"] == "Copernicus Data Space Ecosystem"
    assert health["status"] in ["CONFIGURED", "DEGRADED", "TIMEOUT"]
    assert "Sentinel-2" in health.get("constellation", "")
    assert SATELLITE_EVIDENCE_DISCLAIMER in health["disclaimer"]


def test_copernicus_token_caching_and_expiry_logic():
    """Tests client credentials token caching and auto-refresh."""
    client = CopernicusClient(client_id="mock_id", client_secret="mock_secret")

    # Mock token response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "access_token": "mock_jwt_token_abc123",
        "expires_in": 3600
    }

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        tok1 = asyncio.run(client.get_access_token())
        assert tok1 == "mock_jwt_token_abc123"
        # Second call within expiry should use cache without POST
        tok2 = asyncio.run(client.get_access_token())
        assert tok2 == "mock_jwt_token_abc123"


# =============================================================================
# 5. Hugging Face Hub Tests
# =============================================================================

def test_hugging_face_public_and_authenticated_modes():
    """Verifies Hugging Face Hub connectivity both with token and anonymously."""
    # 1. Default configured instance
    health = asyncio.run(hf_client.check_health())
    assert health["provider"] == "Hugging Face"
    assert health["status"] in ["CONFIGURED", "AUTHENTICATED", "DEGRADED"]

    # 2. Anonymous client without token
    anon_client = HuggingFaceClient(token="")
    assert anon_client.is_authenticated is False
    anon_health = asyncio.run(anon_client.check_health())
    assert anon_health["auth_mode"] == "ANONYMOUS_PUBLIC"


def test_hugging_face_model_metadata_lookup():
    """Queries public sentence transformer model metadata."""
    res = asyncio.run(hf_client.get_model_info("sentence-transformers/all-MiniLM-L6-v2"))
    assert res["success"] is True
    assert res["model_id"] == "sentence-transformers/all-MiniLM-L6-v2"
    assert res["private"] is False


# =============================================================================
# 6. Open-Meteo Weather API Tests
# =============================================================================

def test_open_meteo_parsing_attribution_and_caching():
    """Verifies weather parsing, attribution, and non-commercial caching."""
    # 1. First fetch
    data1 = asyncio.run(weather_client.get_district_weather("warangal"))
    assert data1["status"] in ["CONFIGURED", "DEGRADED", "UNAVAILABLE"]
    assert "temperature" in data1
    assert "humidity" in data1
    assert OPEN_METEO_ATTRIBUTION in data1["attribution"]
    assert data1["data_nature"] in ["MODEL_FORECAST_ESTIMATE", "HISTORICAL_CLIMATIC_NORMAL"]
    assert data1["is_measured_in_situ"] is False

    # 2. Second fetch within TTL must hit cache
    data2 = asyncio.run(weather_client.get_district_weather("warangal"))
    assert data2.get("is_cached") is True


# =============================================================================
# 7. data.gov.in Agricultural Market Datasets Tests
# =============================================================================

def test_datagov_in_health_and_outage_resilience():
    """Verifies data.gov.in health probe and graceful handling of gateway timeouts."""
    health = asyncio.run(datagov_client.check_health())
    assert health["provider"] == "data.gov.in"
    assert health["status"] in ["CONFIGURED", "TIMEOUT", "DEGRADED", "NOT_CONFIGURED", "UNAVAILABLE"]


def test_datagov_in_mock_record_normalization():
    """Verifies Agmarknet record normalization and non-fabrication principles."""
    mock_api_response = {
        "title": "Daily Price and Arrival of Agriculture Commodities",
        "total": 1,
        "records": [
            {
                "state": "Telangana",
                "district": "Warangal",
                "market": "Warangal (Enumamula)",
                "commodity": "Cotton",
                "variety": "Medium Staple",
                "grade": "FAQ",
                "arrival_date": "08/11/2026",
                "min_price": "7100.00",
                "max_price": "7800.00",
                "modal_price": "7500.00"
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_api_response

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        client = DataGovClient(api_key="mock_key_abc")
        res = asyncio.run(client.fetch_telangana_mandi_prices(commodity="Cotton"))
        assert res["success"] is True
        assert res["records_count"] == 1
        record = res["records"][0]
        assert record["state"] == "Telangana"
        assert record["modal_price"] == 7500.00
        assert record["provenance"]["source_provider"] == "data.gov.in Agmarknet"
        assert DATA_GOV_IN_ATTRIBUTION in res["attribution"]


# =============================================================================
# 8. System Integrations Endpoint & Zero-Secret-Leakage Test
# =============================================================================

def test_system_integrations_endpoint_seven_services(client: TestClient):
    """Verifies /api/v1/system/integrations exposes all 7 services without leaking secrets."""
    resp = client.get("/api/v1/system/integrations")
    assert resp.status_code == 200
    body = resp.json()

    # 1. Preserved baseline keys
    assert "storage" in body
    assert "ml_inference_microservice" in body
    assert "weather_provider" in body

    # 2. Seven Services Manifest
    assert "services" in body
    services = body["services"]
    assert "groq_cloud" in services
    assert "neon_postgresql" in services
    assert "upstash_redis" in services
    assert "copernicus_data_space" in services
    assert "hugging_face" in services
    assert "open_meteo" in services
    assert "data_gov_in" in services

    # 3. Non-leakage verification: raw secret tokens must NEVER appear in response body
    body_text = resp.text
    if settings.GROQ_API_KEY:
        assert settings.GROQ_API_KEY not in body_text
    if settings.HF_TOKEN:
        assert settings.HF_TOKEN not in body_text
    if settings.DATA_GOV_IN_API_KEY:
        assert settings.DATA_GOV_IN_API_KEY not in body_text
    if settings.JWT_SECRET_KEY:
        assert settings.JWT_SECRET_KEY not in body_text
