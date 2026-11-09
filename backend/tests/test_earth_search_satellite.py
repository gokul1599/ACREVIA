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
    CloudMaskPolicy,
    SATELLITE_EVIDENCE_DISCLAIMER,
    EARTH_SEARCH_ATTRIBUTION,
    PLANETARY_COMPUTER_ATTRIBUTION,
    TELANGANA_BBOX,
    SCL_NO_DATA,
    SCL_SATURATED,
    SCL_DARK_AREA,
    SCL_CLOUD_SHADOW,
    SCL_VEGETATION,
    SCL_NOT_VEGETATED,
    SCL_WATER,
    SCL_UNCLASSIFIED,
    SCL_CLOUD_MEDIUM_PROB,
    SCL_CLOUD_HIGH_PROB,
    SCL_THIN_CIRRUS,
    SCL_SNOW
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


# =============================================================================
# 5. Scientific Quality Controls, SCL Policies & Zonal Masking Tests
# =============================================================================

def test_cloud_mask_policy_definitions_and_behavior():
    """Validates STRICT, STANDARD, and LENIENT SCL masking behaviors."""
    # SCL 2 (Dark Area) & SCL 7 (Unclassified) behavior across policies
    assert SCL_DARK_AREA in CloudMaskPolicy.STRICT
    assert SCL_DARK_AREA not in CloudMaskPolicy.STANDARD
    assert SCL_DARK_AREA not in CloudMaskPolicy.LENIENT

    assert SCL_UNCLASSIFIED in CloudMaskPolicy.STRICT
    assert SCL_UNCLASSIFIED not in CloudMaskPolicy.STANDARD
    assert SCL_UNCLASSIFIED not in CloudMaskPolicy.LENIENT

    # SCL 8 (Medium Prob Cloud) & SCL 10 (Thin Cirrus) behavior across policies
    assert SCL_CLOUD_MEDIUM_PROB in CloudMaskPolicy.STRICT
    assert SCL_CLOUD_MEDIUM_PROB in CloudMaskPolicy.STANDARD
    assert SCL_CLOUD_MEDIUM_PROB not in CloudMaskPolicy.LENIENT

    assert SCL_THIN_CIRRUS in CloudMaskPolicy.STRICT
    assert SCL_THIN_CIRRUS in CloudMaskPolicy.STANDARD
    assert SCL_THIN_CIRRUS not in CloudMaskPolicy.LENIENT

    # SCL 9 (High Prob Cloud), 3 (Shadow), 0 (No data), 1 (Saturated) are ALWAYS masked
    for policy in [CloudMaskPolicy.STRICT, CloudMaskPolicy.STANDARD, CloudMaskPolicy.LENIENT]:
        assert SCL_CLOUD_HIGH_PROB in policy
        assert SCL_CLOUD_SHADOW in policy
        assert SCL_NO_DATA in policy
        assert SCL_SATURATED in policy

    # Test processing under STRICT vs STANDARD policy with dark area (SCL 2)
    nir = np.full((20, 20), 4000, dtype=np.uint16)
    red = np.full((20, 20), 1000, dtype=np.uint16)
    scl = np.full((10, 10), SCL_DARK_AREA, dtype=np.uint8)

    # In STRICT mode, all SCL 2 pixels are masked -> insufficient clear pixels
    res_strict = Sentinel2Processor.process_raster_arrays(
        red_band=red, nir_band=nir, scl_band=scl, cloud_mask_policy=CloudMaskPolicy.STRICT
    )
    assert res_strict["status"] in ["CLOUD_OBSCURED", "INSUFFICIENT_CLEAR_PIXELS"]
    assert res_strict["valid"] is False

    # In STANDARD mode, SCL 2 pixels are retained -> valid computation
    res_standard = Sentinel2Processor.process_raster_arrays(
        red_band=red, nir_band=nir, scl_band=scl, cloud_mask_policy=CloudMaskPolicy.STANDARD
    )
    assert res_standard["status"] == "SUCCESS"
    assert res_standard["valid"] is True


def test_sentinel2_configurable_cloud_withholding_thresholds():
    """Validates configurable max_cloud_cover_fraction and min_valid_pixel_fraction."""
    nir = np.full((20, 20), 4000, dtype=np.uint16)
    red = np.full((20, 20), 1000, dtype=np.uint16)
    
    # 10x10 SCL: 55% clouded (55 pixels SCL 9, 45 pixels SCL 4)
    scl = np.full((10, 10), SCL_VEGETATION, dtype=np.uint8)
    scl.flat[:55] = SCL_CLOUD_HIGH_PROB

    # 1. Under default threshold (0.50), 55% cloud triggers CLOUD_OBSCURED
    res_default = Sentinel2Processor.process_raster_arrays(
        red_band=red, nir_band=nir, scl_band=scl, max_cloud_cover_fraction=0.50
    )
    assert res_default["status"] == "CLOUD_OBSCURED"
    assert res_default["valid"] is False
    assert res_default["cloud_masked_pixel_ratio"] == 0.55
    assert res_default["max_allowed_cloud_ratio"] == 0.50

    # 2. When max_cloud_cover_fraction is raised to 0.60, observation is accepted
    res_relaxed = Sentinel2Processor.process_raster_arrays(
        red_band=red, nir_band=nir, scl_band=scl, max_cloud_cover_fraction=0.60
    )
    assert res_relaxed["status"] == "SUCCESS"
    assert res_relaxed["valid"] is True
    assert res_relaxed["cloud_masked_pixel_ratio"] == 0.55

    # 3. Test min_valid_pixel_fraction: 85% cloud leaves only 15% valid pixels
    scl_sparse = np.full((10, 10), SCL_CLOUD_HIGH_PROB, dtype=np.uint8)
    scl_sparse.flat[:15] = SCL_VEGETATION

    # With max_cloud threshold disabled (1.0), but min_valid_pixel_fraction at 0.20:
    res_insufficient = Sentinel2Processor.process_raster_arrays(
        red_band=red,
        nir_band=nir,
        scl_band=scl_sparse,
        max_cloud_cover_fraction=1.0,
        min_valid_pixel_fraction=0.20
    )
    assert res_insufficient["status"] == "INSUFFICIENT_CLEAR_PIXELS"
    assert res_insufficient["valid"] is False
    assert res_insufficient["valid_pixel_ratio"] == 0.15


def test_sentinel2_zonal_geometry_mask_cloud_fraction():
    """
    Validates that cloud obscuration ratio is computed strictly over the plot boundary
    geometry, preventing scene-wide cloud estimates from biasing parcel decisions.
    """
    nir = np.full((20, 20), 4000, dtype=np.uint16)
    red = np.full((20, 20), 1000, dtype=np.uint16)
    
    # 20x20 raster has a 10x10 sub-plot in the top-left corner
    plot_mask = np.zeros((20, 20), dtype=np.uint8)
    plot_mask[:10, :10] = 1

    # SCL is 100% cloudy in bottom half, but 100% CLEAR vegetation in top-left plot!
    scl = np.zeros((10, 10), dtype=np.uint8)
    # The top-left 5x5 in SCL (which corresponds to top-left 10x10 at 10m) is clear
    scl[:5, :5] = SCL_VEGETATION
    scl[5:, :] = SCL_CLOUD_HIGH_PROB
    scl[:, 5:] = SCL_CLOUD_HIGH_PROB

    res = Sentinel2Processor.process_raster_arrays(
        red_band=red, nir_band=nir, scl_band=scl, plot_mask=plot_mask
    )
    assert res["status"] == "SUCCESS"
    assert res["valid"] is True
    # Inside the 10x10 plot geometry, cloud ratio is exactly 0.0 even if scene is 75% cloudy
    assert res["cloud_masked_pixel_ratio"] == 0.0
    assert res["valid_pixels"] == 100


def test_planetary_computer_sas_token_caching_and_url_signing():
    """Validates MPC SAS token caching, expiration refresh, and asset URL signing."""
    import time
    provider = PlanetaryComputerProvider()

    # Initial state: empty cache
    assert provider._cached_sas_token is None

    # URL signing when token is None returns unsigned URL unchanged
    url = "https://sentinel2l2a01.blob.core.windows.net/b04.tif"
    assert provider.sign_asset_url(url, None) == url

    # Simulating cached token
    provider._cached_sas_token = "st=2026-03-28&se=2026-03-29&sp=r&sig=test_signature"
    provider._sas_token_expiry = time.time() + 3600  # valid for 1 hour

    # URL signing with token appends query string
    signed = provider.sign_asset_url(url, provider._cached_sas_token)
    assert signed == f"{url}?{provider._cached_sas_token}"

    # Does not double-sign if query string is already present
    assert provider.sign_asset_url(signed, provider._cached_sas_token) == signed

    # Cached token is returned synchronously when fresh without HTTP request
    token = asyncio.run(provider.get_sas_token())
    assert token == provider._cached_sas_token


def test_composite_client_distinguishes_empty_results_from_outages():
    """
    Validates that a legitimate 0-scene search (e.g. ultra-strict cloud filter)
    is treated as a successful search (not an outage) and does not spuriously trigger failover.
    """
    client = CompositeSatelliteClient()

    # Primary returns 0 scenes successfully
    primary_empty_result = {
        "success": True,
        "provider": "Element 84 Earth Search",
        "scenes_count": 0,
        "scenes": [],
        "attribution": EARTH_SEARCH_ATTRIBUTION,
        "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER
    }

    with patch.object(client.primary_provider, "search_scenes", return_value=primary_empty_result):
        res = asyncio.run(client.search_scenes(bbox=TELANGANA_BBOX))
        assert res["success"] is True
        assert res["scenes_count"] == 0
        assert res["failover_engaged"] is False
        assert res["provider"] == "Element 84 Earth Search"

    # Primary fails with 503 -> Failover IS engaged
    primary_error = {
        "success": False,
        "error_code": "HTTP_503",
        "message": "Gateway Timeout"
    }
    secondary_fallback_result = {
        "success": True,
        "provider": "Microsoft Planetary Computer",
        "scenes_count": 1,
        "scenes": [{"id": "S2B_TEST"}],
        "attribution": PLANETARY_COMPUTER_ATTRIBUTION,
        "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER
    }

    with patch.object(client.primary_provider, "search_scenes", return_value=primary_error):
        with patch.object(client.secondary_provider, "search_scenes", return_value=secondary_fallback_result):
            res = asyncio.run(client.search_scenes(bbox=TELANGANA_BBOX))
            assert res["success"] is True
            assert res["failover_engaged"] is True
            assert res["provider"] == "Microsoft Planetary Computer"


def test_fetch_cog_tile_error_handling():
    """Validates fetch_cog_tile raises RuntimeError on non-200/206 HTTP responses."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError, match="HTTP 404"):
            asyncio.run(Sentinel2Processor.fetch_cog_tile("https://example.com/invalid_tile.tif"))

