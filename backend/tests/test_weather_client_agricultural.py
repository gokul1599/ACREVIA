"""
ACREVIA - Unit & Offline Integration Tests for Open-Meteo Agricultural Extension.
Verifies soil moisture, soil temperature, FAO-56 Penman-Monteith ET0,
coordinate dithering for privacy, non-commercial caching, and PJTSAU fallback.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
import httpx

from backend.app.integrations.weather_client import (
    WeatherClient,
    dither_coordinates,
    OPEN_METEO_ATTRIBUTION,
    TELANGANA_DISTRICT_COORDS,
)


def test_coordinate_dithering_privacy():
    """Verifies that high-precision farm coordinates are dithered to 2 decimals (~1.1 km)."""
    lat, lon = 17.598642, 80.003719
    d_lat, d_lon = dither_coordinates(lat, lon, precision=2)
    assert d_lat == 17.60
    assert d_lon == 80.00

    # Ensure negative coordinates or edge coordinates format correctly
    d_lat2, d_lon2 = dither_coordinates(18.4386, 79.1288)
    assert d_lat2 == 18.44
    assert d_lon2 == 79.13


def test_get_agricultural_weather_success():
    """Verifies parsing of agricultural variables from mock Open-Meteo response."""
    client = WeatherClient(cache_ttl_seconds=60)

    mock_response_data = {
        "current": {
            "time": "2026-11-12T12:00:00Z",
            "temperature_2m": 31.4,
            "relative_humidity_2m": 72.0,
            "precipitation": 1.2,
            "wind_speed_10m": 9.5,
            "soil_moisture_0_to_1cm": 0.23,
            "soil_moisture_1_to_3cm": 0.25,
            "soil_moisture_3_to_9cm": 0.27,
            "soil_moisture_9_to_27cm": 0.28,
            "soil_moisture_27_to_81cm": 0.30,
            "soil_temperature_0cm": 32.5,
            "soil_temperature_6cm": 30.2,
            "soil_temperature_18cm": 28.9,
            "soil_temperature_54cm": 27.5,
            "et0_fao_evapotranspiration": 5.1,
            "shortwave_radiation_instant": 780.0,
        }
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response_data

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        result = asyncio.run(client.get_agricultural_weather(17.5986, 80.0037, dither=True))

        assert result["status"] == "CONFIGURED"
        assert result["latitude"] == 17.60
        assert result["longitude"] == 80.00
        assert result["is_dithered"] is True
        assert result["temperature"] == 31.4
        assert result["humidity"] == 72.0
        assert result["precipitation"] == 1.2
        assert result["wind_speed"] == 9.5
        assert result["soil_moisture"]["0_to_1cm"] == 0.23
        assert result["soil_moisture"]["3_to_9cm"] == 0.27
        assert result["soil_temperature"]["0cm"] == 32.5
        assert result["soil_temperature"]["18cm"] == 28.9
        assert result["et0_fao_evapotranspiration"] == 5.1
        assert result["shortwave_radiation_instant"] == 780.0
        assert result["attribution"] == OPEN_METEO_ATTRIBUTION
        assert result["data_nature"] == "MODEL_FORECAST_ESTIMATE"
        assert result["is_measured_in_situ"] is False
        assert result["is_cached"] is False

        # Verify second call hits cache
        cached_result = asyncio.run(client.get_agricultural_weather(17.5986, 80.0037, dither=True))
        assert cached_result["is_cached"] is True
        assert mock_get.call_count == 1


def test_get_agricultural_weather_http_error_fallback():
    """Verifies that an upstream 503 or server error gracefully falls back to PJTSAU normals."""
    client = WeatherClient(cache_ttl_seconds=60)

    mock_resp = MagicMock()
    mock_resp.status_code = 503

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        result = asyncio.run(client.get_agricultural_weather(17.1439, 79.6239, dither=True))

        assert result["status"] == "DEGRADED"
        assert "PJTSAU Historical Agro-Climatic Normal" in result["source"]
        assert result["data_nature"] == "HISTORICAL_CLIMATIC_NORMAL"
        assert result["is_measured_in_situ"] is False
        assert result["soil_moisture"]["0_to_1cm"] == 0.18
        assert result["soil_temperature"]["0cm"] == 29.5
        assert result["et0_fao_evapotranspiration"] == 4.5


def test_get_agricultural_weather_timeout_fallback():
    """Verifies that network timeout falls back gracefully with status UNAVAILABLE."""
    client = WeatherClient(cache_ttl_seconds=60)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.ConnectTimeout("Connection to api.open-meteo.com timed out")

        result = asyncio.run(client.get_agricultural_weather(17.9689, 79.5941, dither=True))

        assert result["status"] == "UNAVAILABLE"
        assert "PJTSAU" in result["source"]
        assert result["data_nature"] == "HISTORICAL_CLIMATIC_NORMAL"


def test_get_district_weather_backward_compatibility():
    """Verifies that get_district_weather returns all legacy fields and new agricultural fields."""
    client = WeatherClient(cache_ttl_seconds=60)

    mock_response_data = {
        "current": {
            "time": "2026-11-12T12:00:00Z",
            "temperature_2m": 30.0,
            "relative_humidity_2m": 65.0,
            "precipitation": 0.0,
            "wind_speed_10m": 7.0,
            "soil_moisture_0_to_1cm": 0.20,
            "soil_temperature_0cm": 30.5,
            "et0_fao_evapotranspiration": 4.8,
            "shortwave_radiation_instant": 700.0,
        }
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response_data

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        res = asyncio.run(client.get_district_weather("Mahabubabad"))
        assert res["district"] == "Mahabubabad"
        assert res["temperature"] == 30.0
        assert res["humidity"] == 65.0
        assert res["precipitation"] == 0.0
        assert res["wind_speed"] == 7.0
        assert "soil_moisture" in res
        assert "soil_temperature" in res
        assert "et0_fao_evapotranspiration" in res
        assert res["attribution"] == OPEN_METEO_ATTRIBUTION
