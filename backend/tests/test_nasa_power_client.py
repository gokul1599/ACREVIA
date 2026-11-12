"""
ACREVIA - Unit & Offline Integration Tests for NASA POWER Agroclimatology Client.
Verifies solar radiation, precipitation, temperature, sentinel value filtering (-999.0),
coordinate privacy dithering, 30-day caching, and PJTSAU fallback.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from backend.app.integrations.nasa_power_client import (
    NASAPowerClient,
    NASA_POWER_ATTRIBUTION,
)
from backend.app.schemas.nasa_power import NASAPowerClimatologyBaseline


def _generate_mock_nasa_power_payload():
    """Generates synthetic NASA POWER JSON response."""
    return {
        "properties": {
            "parameter": {
                "ALLSKY_SFC_SW_DWN": {
                    "20261105": 19.45,
                    "20261106": 20.12,
                    "20261107": -999.0,  # Missing sentinel value to test filter
                },
                "T2M": {
                    "20261105": 27.8,
                    "20261106": 28.5,
                    "20261107": 28.1,
                },
                "RH2M": {
                    "20261105": 62.0,
                    "20261106": 58.5,
                    "20261107": 64.2,
                },
                "PRECTOTCORR": {
                    "20261105": 0.0,
                    "20261106": 1.4,
                    "20261107": 0.0,
                }
            }
        }
    }


def test_nasa_power_get_climatology_success_and_filtering():
    """Verifies that NASA POWER payload is parsed and -999.0 sentinels are normalized."""
    client = NASAPowerClient(cache_ttl_seconds=3600)
    mock_payload = _generate_mock_nasa_power_payload()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        baseline = asyncio.run(client.get_daily_climatology(17.5986, 80.0037, days=3, dither=True))

        assert isinstance(baseline, NASAPowerClimatologyBaseline)
        assert baseline.status == "CONFIGURED"
        assert baseline.latitude == 17.60
        assert baseline.longitude == 80.00
        assert baseline.is_dithered is True
        assert baseline.data_source == "NASA_POWER_AGROCLIMATOLOGY"
        assert baseline.epistemic_status == "CLIMATOLOGICAL_REMOTE_ESTIMATE"
        assert baseline.is_measured_in_situ is False
        assert baseline.non_override_guarantee is True
        assert baseline.attribution == NASA_POWER_ATTRIBUTION

        # Check records
        assert len(baseline.records) == 3
        # 20261107 had -999.0 sentinel for solar radiation, should be replaced with 18.5
        rec3 = baseline.records[2]
        assert rec3.date == "20261107"
        assert rec3.solar_radiation_allsky_sw == 18.5

        assert baseline.precipitation_total_period == 1.4
        assert baseline.solar_radiation_mean_daily > 18.0

        # Verify caching on second call
        cached = asyncio.run(client.get_daily_climatology(17.5986, 80.0037, days=3, dither=True))
        assert cached.is_cached is True
        assert mock_get.call_count == 1


def test_nasa_power_http_error_fallback():
    """Verifies that HTTP 500 error gracefully triggers PJTSAU agroclimatology fallback."""
    client = NASAPowerClient(cache_ttl_seconds=3600)

    mock_resp = MagicMock()
    mock_resp.status_code = 500

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        baseline = asyncio.run(client.get_daily_climatology(17.0575, 79.2684, days=5, dither=True))

        assert baseline.status == "DEGRADED"
        assert "PJTSAU_CLIMATOLOGY_NORMAL" in baseline.data_source
        assert baseline.epistemic_status == "HISTORICAL_CLIMATIC_NORMAL"
        assert len(baseline.records) == 5
        assert baseline.solar_radiation_mean_daily == 19.2


def test_nasa_power_timeout_fallback():
    """Verifies that network timeout falls back gracefully with status UNAVAILABLE."""
    client = NASAPowerClient(cache_ttl_seconds=3600)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.ConnectTimeout("NASA POWER timeout")

        baseline = asyncio.run(client.get_daily_climatology(17.9689, 79.5941, days=3, dither=True))

        assert baseline.status == "UNAVAILABLE"
        assert "PJTSAU" in baseline.data_source
        assert baseline.is_measured_in_situ is False


def test_nasa_power_health_probe():
    """Verifies health check probe returns expected provider metadata."""
    client = NASAPowerClient(cache_ttl_seconds=3600)
    mock_payload = _generate_mock_nasa_power_payload()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        health = asyncio.run(client.check_health())
        assert health["status"] == "CONFIGURED"
        assert health["provider"] == "NASA POWER Agroclimatology"
        assert health["auth_required"] is False
