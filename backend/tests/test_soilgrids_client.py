"""
ACREVIA - Unit & Offline Integration Tests for ISRIC SoilGrids v2.0 Client.
Verifies soil physical/chemical property extraction, conversion factor scaling,
decile uncertainty intervals (Q0.05, Q0.50, Q0.95), coordinate privacy dithering,
caching, and fallback invariants.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from backend.app.integrations.soilgrids_client import (
    SoilGridsClient,
    SOILGRIDS_ATTRIBUTION,
)
from backend.app.schemas.soilgrids import SoilGridsProfileResponse


def _generate_mock_soilgrids_payload():
    """Generates synthetic SoilGrids v2 GeoJSON response matching official schema."""
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [79.60, 17.60]},
        "properties": {
            "layers": [
                {
                    "name": "phh2o",
                    "unit_measure": {"target_units": "pH*10", "mapped_units": "pH*10"},
                    "depths": [
                        {
                            "label": "0-5cm",
                            "values": {"mean": 66, "Q0.05": 59, "Q0.5": 66, "Q0.95": 73}
                        }
                    ]
                },
                {
                    "name": "soc",
                    "unit_measure": {"target_units": "dg/kg", "mapped_units": "dg/kg"},
                    "depths": [
                        {
                            "label": "0-5cm",
                            "values": {"mean": 82, "Q0.05": 55, "Q0.5": 80, "Q0.95": 110}
                        }
                    ]
                },
                {
                    "name": "clay",
                    "unit_measure": {"target_units": "g/kg", "mapped_units": "g/kg"},
                    "depths": [
                        {
                            "label": "0-5cm",
                            "values": {"mean": 290, "Q0.05": 210, "Q0.5": 290, "Q0.95": 380}
                        }
                    ]
                },
                {
                    "name": "sand",
                    "unit_measure": {"target_units": "g/kg", "mapped_units": "g/kg"},
                    "depths": [
                        {
                            "label": "0-5cm",
                            "values": {"mean": 510, "Q0.05": 410, "Q0.5": 510, "Q0.95": 620}
                        }
                    ]
                },
                {
                    "name": "silt",
                    "unit_measure": {"target_units": "g/kg", "mapped_units": "g/kg"},
                    "depths": [
                        {
                            "label": "0-5cm",
                            "values": {"mean": 200, "Q0.05": 130, "Q0.5": 200, "Q0.95": 270}
                        }
                    ]
                },
                {
                    "name": "bdod",
                    "unit_measure": {"target_units": "cg/cm³", "mapped_units": "cg/cm³"},
                    "depths": [
                        {
                            "label": "0-5cm",
                            "values": {"mean": 134, "Q0.05": 121, "Q0.5": 134, "Q0.95": 147}
                        }
                    ]
                },
                {
                    "name": "cec",
                    "unit_measure": {"target_units": "mmol(c)/kg", "mapped_units": "mmol(c)/kg"},
                    "depths": [
                        {
                            "label": "0-5cm",
                            "values": {"mean": 225, "Q0.05": 160, "Q0.5": 220, "Q0.95": 290}
                        }
                    ]
                },
                {
                    "name": "nitrogen",
                    "unit_measure": {"target_units": "cg/kg", "mapped_units": "cg/kg"},
                    "depths": [
                        {
                            "label": "0-5cm",
                            "values": {"mean": 88, "Q0.05": 52, "Q0.5": 85, "Q0.95": 124}
                        }
                    ]
                }
            ]
        }
    }


def test_soilgrids_get_profile_success_and_scaling():
    """Verifies that SoilGrids response is parsed with correct unit conversions and uncertainty bounds."""
    client = SoilGridsClient(cache_ttl_seconds=3600)
    mock_payload = _generate_mock_soilgrids_payload()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        profile = asyncio.run(client.get_soil_profile(17.5986, 80.0037, dither=True))

        assert isinstance(profile, SoilGridsProfileResponse)
        assert profile.status == "CONFIGURED"
        assert profile.latitude == 17.60
        assert profile.longitude == 80.00
        assert profile.is_dithered is True
        assert profile.data_source == "ISRIC_SOILGRIDS_V2_250M"
        assert profile.epistemic_status == "REMOTE_STATISTICAL_MODEL_ESTIMATE"
        assert profile.is_measured_in_situ is False
        assert profile.non_override_guarantee is True
        assert profile.attribution == SOILGRIDS_ATTRIBUTION

        # Test chemical properties and conversions
        ph = profile.chemical.ph
        assert ph.mean == 6.6
        assert ph.median == 6.6
        assert ph.q05 == 5.9
        assert ph.q95 == 7.3
        assert ph.unit == "pH"
        assert ph.q05 <= ph.median <= ph.q95

        soc = profile.chemical.soil_organic_carbon
        assert soc.mean == 8.2
        assert soc.unit == "g/kg"
        assert soc.q05 <= soc.median <= soc.q95

        # Test physical properties and conversions
        clay = profile.physical.clay_percentage
        assert clay.mean == 29.0
        assert clay.unit == "%"

        sand = profile.physical.sand_percentage
        assert sand.mean == 51.0
        assert sand.unit == "%"

        silt = profile.physical.silt_percentage
        assert silt.mean == 20.0
        assert silt.unit == "%"

        # Texture fractions sum approximately to 100%
        assert round(clay.mean + sand.mean + silt.mean, 1) == 100.0

        bdod = profile.physical.bulk_density
        assert bdod is not None
        assert bdod.mean == 1.34
        assert bdod.unit == "g/cm³"

        # Verify caching on second call
        cached_profile = asyncio.run(client.get_soil_profile(17.5986, 80.0037, dither=True))
        assert cached_profile.is_cached is True
        assert mock_get.call_count == 1


def test_soilgrids_http_error_fallback():
    """Verifies that an upstream 502/503 gracefully falls back to PJTSAU agro-pedological normals."""
    client = SoilGridsClient(cache_ttl_seconds=3600)

    mock_resp = MagicMock()
    mock_resp.status_code = 502

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        profile = asyncio.run(client.get_soil_profile(17.1439, 79.6239, dither=True))

        assert profile.status == "DEGRADED"
        assert "PJTSAU_TELANGANA_SOIL_RESOURCE_NORMAL" in profile.data_source
        assert profile.epistemic_status == "REGIONAL_AGROCLIMATIC_PEDOLOGICAL_NORMAL"
        assert profile.is_measured_in_situ is False
        assert profile.chemical.ph.mean == 6.8
        assert profile.physical.clay_percentage.mean == 26.0


def test_soilgrids_timeout_fallback():
    """Verifies that network timeout falls back gracefully with status UNAVAILABLE."""
    client = SoilGridsClient(cache_ttl_seconds=3600)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.ConnectTimeout("SoilGrids connection timeout")

        profile = asyncio.run(client.get_soil_profile(17.9689, 79.5941, dither=True))

        assert profile.status == "UNAVAILABLE"
        assert "PJTSAU" in profile.data_source
        assert profile.is_measured_in_situ is False


def test_soilgrids_health_probe():
    """Verifies health check probe returns expected provider metadata."""
    client = SoilGridsClient(cache_ttl_seconds=3600)
    mock_payload = _generate_mock_soilgrids_payload()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        health = asyncio.run(client.check_health())
        assert health["status"] == "CONFIGURED"
        assert health["provider"] == "ISRIC SoilGrids v2.0"
        assert health["auth_required"] is False
        assert health["is_measured_in_situ"] is False
