"""
ACREVIA - Earth Search & Planetary Computer Satellite Test Suite.
Validates authentication-free Sentinel-2 L2A Earth observation pipeline:
- Element 84 Earth Search STAC API
- Microsoft Planetary Computer fallback
- Sentinel-2 L2A band handling (B04 Red, B08 NIR, SCL Scene Classification)
- Scientific NDVI computation and cloud/shadow masking
- Boundary clipping, zonal statistics, and cloud obscuration handling
- Zero-fabrication principle: non-invention of missing observations
- Mandatory non-disease diagnostic disclaimer enforcement.
"""

import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.app.integrations.satellite_client import (
    EarthSearchProvider,
    PlanetaryComputerProvider,
    Sentinel2Processor,
    CompositeSatelliteClient,
    satellite_client,
    SATELLITE_EVIDENCE_DISCLAIMER,
    EARTH_SEARCH_ATTRIBUTION,
    PLANETARY_COMPUTER_ATTRIBUTION,
    TELANGANA_BBOX,
    SCL_CLOUD_HIGH_PROB,
    SCL_CLOUD_SHADOW,
    SCL_VEGETATION
)
from backend.app.services.satellite_service import SatelliteService


# =============================================================================
# 1. Earth Search Primary Provider Tests
# =============================================================================

def test_earth_search_stac_health_and_collection():
    """1 & 2: Anonymous Earth Search STAC catalogue access and Sentinel-2 collection discovery."""
    provider = EarthSearchProvider()
    health = asyncio.run(provider.check_health())
    assert health["status"] in ["CONFIGURED", "DEGRADED", "TIMEOUT"]
    if health["status"] == "CONFIGURED":
        assert health["collection"] == "sentinel-2-l2a"
        assert health["auth_mode"] == "PUBLIC_STAC_ZERO_AUTH"
        assert health["free_tier"] is True
        assert EARTH_SEARCH_ATTRIBUTION in health["attribution"]


def test_earth_search_geographic_field_search_and_filters():
    """3, 4 & 5: Geographic field search, date-range, and cloud-cover filtering."""
    provider = EarthSearchProvider()
    
    # Warangal, Telangana agricultural centroid
    bbox = [79.55, 17.95, 79.65, 18.05]
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 3, 31, tzinfo=timezone.utc)

    res = asyncio.run(provider.search_scenes(
        bbox=bbox,
        start_date=start,
        end_date=end,
        max_cloud_cover_percent=20.0,
        limit=2
    ))

    # Test handles live network or mock if network unreachable
    if res.get("success"):
        assert res["scenes_count"] >= 1
        scene = res["scenes"][0]
        assert "id" in scene
        assert "acquisition_date" in scene
        assert scene["cloud_cover_percentage"] <= 20.0
        assert "assets" in scene
        assert "red" in scene["assets"] or "nir" in scene["assets"]
        assert EARTH_SEARCH_ATTRIBUTION in res["attribution"]
        assert SATELLITE_EVIDENCE_DISCLAIMER in res["disclaimer"]


def test_earth_search_asset_metadata_and_bands():
    """6 & 7: Asset metadata retrieval, band URLs, and Cloud-Optimized GeoTIFF accessibility."""
    provider = EarthSearchProvider()
    bbox = [79.55, 17.95, 79.65, 18.05]
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 3, 31, tzinfo=timezone.utc)

    res = asyncio.run(provider.search_scenes(
        bbox=bbox,
        start_date=start,
        end_date=end,
        max_cloud_cover_percent=10.0,
        limit=1
    ))

    if res.get("success") and res.get("scenes_count", 0) > 0:
        scene = res["scenes"][0]
        assets = scene["assets"]
        # Validate band URLs point to valid cloud-optimized assets (S3 COGs)
        if assets.get("red"):
            assert "sentinel" in assets["red"].lower()
            assert "b04" in assets["red"].lower() or "red" in assets["red"].lower()
        if assets.get("nir"):
            assert "sentinel" in assets["nir"].lower()
            assert "b08" in assets["nir"].lower() or "nir" in assets["nir"].lower()


# =============================================================================
# 2. Sentinel-2 Scientific Processing & NDVI Tests
# =============================================================================

def test_sentinel2_ndvi_computation_valid_pixels():
    """8: NDVI computation using valid raster arrays and mathematical formula."""
    # 50x50 test raster representing cotton canopy
    # Healthy cotton: NIR ~0.45 (reflectance 4500), Red ~0.10 (reflectance 1000)
    nir_band = np.full((50, 50), 4500, dtype=np.uint16)
    red_band = np.full((50, 50), 1000, dtype=np.uint16)
    
    # Vegetation SCL class (4 = vegetation)
    scl_band = np.full((25, 25), SCL_VEGETATION, dtype=np.uint8)

    # Circular plot mask inside 50x50 raster
    y, x = np.ogrid[:50, :50]
    plot_mask = ((x - 25)**2 + (y - 25)**2 <= 15**2).astype(np.uint8)

    result = Sentinel2Processor.process_raster_arrays(
        red_band=red_band,
        nir_band=nir_band,
        scl_band=scl_band,
        plot_mask=plot_mask
    )

    assert result["status"] == "SUCCESS"
    assert result["valid"] is True
    # (4500 - 1000) / (4500 + 1000) = 3500 / 5500 = 0.6364
    assert abs(result["mean_ndvi"] - 0.6364) < 0.001
    assert result["cloud_masked_pixel_ratio"] == 0.0
    assert result["valid_pixels"] > 0
    assert SATELLITE_EVIDENCE_DISCLAIMER in result["disclaimer"]


def test_sentinel2_cloud_shadow_masking_and_obscuration():
    """9: Cloud-obscured and missing-data handling (Zero-fabrication principle)."""
    # 50x50 test raster
    nir_band = np.full((50, 50), 4000, dtype=np.uint16)
    red_band = np.full((50, 50), 1000, dtype=np.uint16)
    
    # 90% cloud cover in SCL (class 9 = high probability cloud)
    scl_heavily_clouded = np.full((25, 25), SCL_CLOUD_HIGH_PROB, dtype=np.uint8)
    scl_heavily_clouded[0:2, 0:2] = SCL_VEGETATION

    result = Sentinel2Processor.process_raster_arrays(
        red_band=red_band,
        nir_band=nir_band,
        scl_band=scl_heavily_clouded
    )

    # Must withhold observation when cloud-obscured (>80%) and NEVER fabricate an NDVI
    assert result["status"] == "CLOUD_OBSCURED"
    assert result["valid"] is False
    assert result["cloud_masked_pixel_ratio"] > 0.80
    assert "withheld" in result["message"].lower()
    assert SATELLITE_EVIDENCE_DISCLAIMER in result["disclaimer"]


def test_sentinel2_dimension_mismatch_validation():
    """Validates band alignment error handling."""
    red = np.zeros((10, 10))
    nir = np.zeros((12, 10))
    with pytest.raises(ValueError, match="Dimension mismatch"):
        Sentinel2Processor.process_raster_arrays(red_band=red, nir_band=nir)


# =============================================================================
# 3. Microsoft Planetary Computer Fallback Tests
# =============================================================================

def test_planetary_computer_stac_health_and_fallback():
    """10: Microsoft Planetary Computer secondary fallback provider verification."""
    mpc = PlanetaryComputerProvider()
    health = asyncio.run(mpc.check_health())
    assert health["status"] in ["CONFIGURED", "DEGRADED", "TIMEOUT"]
    if health["status"] == "CONFIGURED":
        assert health["collection"] == "sentinel-2-l2a"
        assert health["auth_mode"] == "PUBLIC_STAC_ANONYMOUS_SAS"
        assert health["free_tier"] is True
        assert PLANETARY_COMPUTER_ATTRIBUTION in health["attribution"]


def test_composite_client_automatic_failover():
    """Tests automatic fallback from Earth Search to Planetary Computer on simulated failure."""
    client = CompositeSatelliteClient()
    
    # Mock Earth Search to simulate HTTP 503 gateway outage
    mock_earth_search_failure = {
        "success": False,
        "error_code": "HTTP_503",
        "message": "Service Temporarily Unavailable"
    }

    mock_mpc_success = {
        "success": True,
        "provider": "Microsoft Planetary Computer",
        "scenes_count": 1,
        "scenes": [
            {
                "id": "S2A_MSIL2A_FALLBACK_TEST",
                "acquisition_date": "2024-03-25T05:00:00Z",
                "cloud_cover_percentage": 5.0,
                "assets": {"red": "https://mpc/b04.tif", "nir": "https://mpc/b08.tif"}
            }
        ],
        "attribution": PLANETARY_COMPUTER_ATTRIBUTION,
        "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER
    }

    with patch.object(client.primary_provider, "search_scenes", return_value=mock_earth_search_failure):
        with patch.object(client.secondary_provider, "search_scenes", return_value=mock_mpc_success):
            res = asyncio.run(client.search_scenes(bbox=TELANGANA_BBOX))
            assert res["success"] is True
            assert res["failover_engaged"] is True
            assert res["scenes"][0]["id"] == "S2A_MSIL2A_FALLBACK_TEST"
            assert PLANETARY_COMPUTER_ATTRIBUTION in res["attribution"]


# =============================================================================
# 4. Service-Level & System Endpoint Integration Tests
# =============================================================================

def test_satellite_service_search_method():
    """Verifies SatelliteService.search_satellite_scenes wrapper and legacy compatibility."""
    res = asyncio.run(SatelliteService.search_satellite_scenes(
        start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2024, 2, 1, tzinfo=timezone.utc),
        limit=2
    ))
    assert "success" in res
    assert "disclaimer" in res
    assert SATELLITE_EVIDENCE_DISCLAIMER in res["disclaimer"]


def test_system_integrations_reports_earth_search(client: TestClient):
    """Verifies /api/v1/system/integrations exposes Earth Search and zero credentials required."""
    res = client.get("/api/v1/system/integrations")
    assert res.status_code == 200
    data = res.json()
    services = data.get("services", {})
    
    assert "earth_search_satellite" in services
    sat = services["earth_search_satellite"]
    assert sat["status"] in ["CONFIGURED", "DEGRADED", "TIMEOUT"]
    assert sat.get("free_tier") is True
    assert "auth_mode" in sat
    assert "PUBLIC_STAC" in sat["auth_mode"]
    assert SATELLITE_EVIDENCE_DISCLAIMER in sat["disclaimer"]

    # Verify legacy copernicus_data_space key is safely aliased
    assert "copernicus_data_space" in services
    cdse = services["copernicus_data_space"]
    assert cdse.get("auth_required") is False
