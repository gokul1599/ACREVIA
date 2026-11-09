"""
ACREVIA - Provider-Independent Satellite Earth Observation Integration.
Replaces Copernicus CDSE OAuth2 dependency with Element 84 Earth Search STAC API
and Microsoft Planetary Computer fallback for 100% authentication-free Sentinel-2 L2A data.

Pillar B: Acrevia Earth.
Adheres strictly to scientific safeguards:
- Non-diagnostic evidence disclaimers
- Non-fabrication of missing satellite observations
- Explicit distinction between cloud-obscured, estimated, and verified data.
"""

import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
import httpx
import numpy as np

from backend.app.core.config import settings
from backend.app.core.logging import logger

# Scientific Disclaimers & Attributions
SATELLITE_EVIDENCE_DISCLAIMER = (
    "Satellite observations reflect broad canopy vigor and surface moisture; "
    "they do not diagnose specific plant diseases or pathogens."
)

EARTH_SEARCH_ATTRIBUTION = (
    "Contains modified Copernicus Sentinel data [2026] processed via AWS Open Data / Element 84 Earth Search"
)

PLANETARY_COMPUTER_ATTRIBUTION = (
    "Contains modified Copernicus Sentinel data [2026] processed via Microsoft Planetary Computer"
)

# Standard bounding box for Telangana State, India (WGS84: min_lon, min_lat, max_lon, max_lat)
TELANGANA_BBOX = [77.2, 15.8, 81.3, 19.9]

# SCL (Scene Classification Layer) Cloud & Shadow Class Identifiers (Sentinel-2 L2A)
SCL_NO_DATA = 0
SCL_SATURATED = 1
SCL_DARK_AREA = 2
SCL_CLOUD_SHADOW = 3
SCL_VEGETATION = 4
SCL_NOT_VEGETATED = 5
SCL_WATER = 6
SCL_UNCLASSIFIED = 7
SCL_CLOUD_MEDIUM_PROB = 8
SCL_CLOUD_HIGH_PROB = 9
SCL_THIN_CIRRUS = 10
SCL_SNOW = 11

class CloudMaskPolicy:
    """
    Configurable Scene Classification Layer (SCL) quality policies for Sentinel-2 L2A.
    Explicit treatment of uncertain & shadow pixels:
    - SCL 0 (NO_DATA): Always masked (sensor margin or missing tile).
    - SCL 1 (SATURATED_OR_DEFECTIVE): Always masked (sensor saturation or optical defect).
    - SCL 2 (DARK_AREA): Topographic shadow, deeply wet soil, or burnt fields.
      * In STRICT: masked.
      * In STANDARD & LENIENT: kept as valid ground observations to prevent falsely discarding wet paddy soils.
    - SCL 3 (CLOUD_SHADOW): Always masked (cloud shadows severely suppress reflectance, corrupting NDVI).
    - SCL 4 (VEGETATION): Kept (primary target).
    - SCL 5 (NOT_VEGETATED): Kept (bare agricultural soil).
    - SCL 6 (WATER): Kept (useful for irrigated rice/paddy flooding assessment).
    - SCL 7 (UNCLASSIFIED): Ambiguous or mixed pixels.
      * In STRICT: masked.
      * In STANDARD & LENIENT: kept with uncertainty tagging.
    - SCL 8 (CLOUD_MEDIUM_PROB): Masked in STRICT & STANDARD; permitted only in LENIENT.
    - SCL 9 (CLOUD_HIGH_PROB): Always masked (thick opaque cloud).
    - SCL 10 (THIN_CIRRUS): Semi-transparent clouds. Masked in STRICT & STANDARD; permitted in LENIENT.
    - SCL 11 (SNOW_OR_ICE): Always masked (irrelevant in tropical Telangana, prevents false high-reflectance spikes).
    """
    STRICT = {SCL_NO_DATA, SCL_SATURATED, SCL_DARK_AREA, SCL_CLOUD_SHADOW, SCL_UNCLASSIFIED, SCL_CLOUD_MEDIUM_PROB, SCL_CLOUD_HIGH_PROB, SCL_THIN_CIRRUS, SCL_SNOW}
    STANDARD = {SCL_NO_DATA, SCL_SATURATED, SCL_CLOUD_SHADOW, SCL_CLOUD_MEDIUM_PROB, SCL_CLOUD_HIGH_PROB, SCL_THIN_CIRRUS, SCL_SNOW}
    LENIENT = {SCL_NO_DATA, SCL_SATURATED, SCL_CLOUD_SHADOW, SCL_CLOUD_HIGH_PROB, SCL_SNOW}


# Default SCL classes treated as cloud or shadow in standard operations
SCL_CLOUD_SHADOW_CLASSES = CloudMaskPolicy.STANDARD


class SatelliteProvider(ABC):
    """Abstract interface for STAC-compliant satellite Earth observation providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the satellite provider."""
        pass

    @property
    @abstractmethod
    def attribution(self) -> str:
        """Legal attribution required by provider terms."""
        pass

    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """Probes catalogue availability and responsiveness."""
        pass

    @abstractmethod
    async def search_scenes(
        self,
        bbox: Optional[List[float]] = None,
        geometry: Optional[Dict[str, Any]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_cloud_cover_percent: float = 20.0,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """Searches Sentinel-2 L2A scenes matching spatial, temporal, and cloud-cover filters."""
        pass


class EarthSearchProvider(SatelliteProvider):
    """
    Primary Provider: Element 84 Earth Search STAC API.
    Provides free, public, authentication-free access to AWS Open Data Sentinel-2 L2A COGs.
    Endpoint: https://earth-search.aws.element84.com/v1
    """

    def __init__(self, base_url: Optional[str] = None, timeout: float = 12.0) -> None:
        self.base_url = (base_url or getattr(settings, "EARTH_SEARCH_STAC_URL", "https://earth-search.aws.element84.com/v1")).rstrip("/")
        self.timeout = timeout
        self.collection = "sentinel-2-l2a"
        self.headers = {"User-Agent": "AcreviaPlatform/1.0 (Telangana Agricultural Earth Intelligence)"}

    @property
    def provider_name(self) -> str:
        return "Element 84 Earth Search (AWS Open Data)"

    @property
    def attribution(self) -> str:
        return EARTH_SEARCH_ATTRIBUTION

    async def check_health(self) -> Dict[str, Any]:
        """Probes Earth Search STAC API and verifies Sentinel-2 L2A collection availability."""
        url = f"{self.base_url}/collections/{self.collection}"
        t0 = time.time()
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                resp = await client.get(url)
                latency_ms = round((time.time() - t0) * 1000, 1)
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "status": "CONFIGURED",
                        "provider": self.provider_name,
                        "collection": self.collection,
                        "title": data.get("title", "Sentinel-2 L2A"),
                        "auth_mode": "PUBLIC_STAC_ZERO_AUTH",
                        "free_tier": True,
                        "latency_ms": latency_ms,
                        "attribution": self.attribution,
                        "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER,
                    }
                else:
                    return {
                        "status": "DEGRADED",
                        "provider": self.provider_name,
                        "http_status": resp.status_code,
                    }
        except httpx.TimeoutException:
            return {"status": "TIMEOUT", "provider": self.provider_name, "timeout_seconds": self.timeout}
        except Exception as e:
            return {"status": "UNAVAILABLE", "provider": self.provider_name, "error": str(e)}

    async def search_scenes(
        self,
        bbox: Optional[List[float]] = None,
        geometry: Optional[Dict[str, Any]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_cloud_cover_percent: float = 20.0,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """
        Executes a STAC Search on Earth Search.
        Supports both Bounding Box and GeoJSON Polygon geometries.
        """
        url = f"{self.base_url}/search"
        now = datetime.now(timezone.utc)
        end = end_date or now
        start = start_date or (end - timedelta(days=30))

        datetime_interval = f"{start.strftime('%Y-%m-%dT%H:%M:%SZ')}/{end.strftime('%Y-%m-%dT%H:%M:%SZ')}"

        payload: Dict[str, Any] = {
            "collections": [self.collection],
            "datetime": datetime_interval,
            "query": {
                "eo:cloud_cover": {"lte": max_cloud_cover_percent}
            },
            "limit": min(max(1, limit), 20),
        }

        if geometry:
            payload["intersects"] = geometry
        else:
            payload["bbox"] = bbox or TELANGANA_BBOX

        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                t0 = time.time()
                resp = await client.post(url, json=payload)
                latency_ms = round((time.time() - t0) * 1000, 1)

                if resp.status_code == 200:
                    data = resp.json()
                    features = data.get("features", [])
                    scenes = []
                    for f in features:
                        props = f.get("properties", {})
                        assets = f.get("assets", {})
                        
                        # Canonical band URL mapping for Earth Search COGs
                        red_asset = assets.get("red") or assets.get("B04") or {}
                        nir_asset = assets.get("nir") or assets.get("B08") or {}
                        scl_asset = assets.get("scl") or assets.get("SCL") or {}
                        thumb_asset = assets.get("thumbnail") or {}

                        scenes.append({
                            "id": f.get("id"),
                            "provider": self.provider_name,
                            "acquisition_date": props.get("datetime"),
                            "cloud_cover_percentage": props.get("eo:cloud_cover", 0.0),
                            "platform": props.get("platform", "sentinel-2"),
                            "constellation": "Sentinel-2 MSI L2A",
                            "bbox": f.get("bbox"),
                            "geometry": f.get("geometry"),
                            "available_bands": list(assets.keys()),
                            "assets": {
                                "red": red_asset.get("href"),
                                "nir": nir_asset.get("href"),
                                "scl": scl_asset.get("href"),
                                "thumbnail": thumb_asset.get("href"),
                            },
                            "provenance": {
                                "source": "Earth Search v1",
                                "collection": self.collection,
                                "stac_item_id": f.get("id"),
                            }
                        })

                    return {
                        "success": True,
                        "provider": self.provider_name,
                        "scenes_count": len(scenes),
                        "scenes": scenes,
                        "latency_ms": latency_ms,
                        "attribution": self.attribution,
                        "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER,
                    }
                elif resp.status_code == 429:
                    return {
                        "success": False,
                        "error_code": "RATE_LIMITED",
                        "message": "Earth Search rate limit exceeded.",
                    }
                else:
                    return {
                        "success": False,
                        "error_code": f"HTTP_{resp.status_code}",
                        "message": f"Earth Search STAC query failed: {resp.text[:100]}",
                    }
        except httpx.TimeoutException:
            return {"success": False, "error_code": "TIMEOUT", "message": "Earth Search request timed out."}
        except Exception as e:
            return {"success": False, "error_code": "CONNECTION_ERROR", "message": str(e)}


class PlanetaryComputerProvider(SatelliteProvider):
    """
    Secondary Fallback Provider: Microsoft Planetary Computer STAC API.
    Provides free, public catalogue search with optional SAS token signing for assets.
    Endpoint: https://planetarycomputer.microsoft.com/api/stac/v1
    """

    def __init__(self, base_url: Optional[str] = None, timeout: float = 12.0) -> None:
        self.base_url = (base_url or getattr(settings, "PLANETARY_COMPUTER_STAC_URL", "https://planetarycomputer.microsoft.com/api/stac/v1")).rstrip("/")
        self.sas_url = "https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel-2-l2a"
        self.timeout = timeout
        self.collection = "sentinel-2-l2a"
        self.headers = {"User-Agent": "AcreviaPlatform/1.0 (Telangana Agricultural Earth Intelligence)"}
        self._cached_sas_token: Optional[str] = None
        self._sas_token_expiry: float = 0.0

    @property
    def provider_name(self) -> str:
        return "Microsoft Planetary Computer"

    @property
    def attribution(self) -> str:
        return PLANETARY_COMPUTER_ATTRIBUTION

    async def check_health(self) -> Dict[str, Any]:
        """Probes Microsoft Planetary Computer STAC API."""
        url = f"{self.base_url}/collections/{self.collection}"
        t0 = time.time()
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                resp = await client.get(url)
                latency_ms = round((time.time() - t0) * 1000, 1)
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "status": "CONFIGURED",
                        "provider": self.provider_name,
                        "collection": self.collection,
                        "title": data.get("title", "Sentinel-2 Level-2A"),
                        "auth_mode": "PUBLIC_STAC_ANONYMOUS_SAS",
                        "free_tier": True,
                        "latency_ms": latency_ms,
                        "attribution": self.attribution,
                        "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER,
                    }
                else:
                    return {
                        "status": "DEGRADED",
                        "provider": self.provider_name,
                        "http_status": resp.status_code,
                    }
        except httpx.TimeoutException:
            return {"status": "TIMEOUT", "provider": self.provider_name, "timeout_seconds": self.timeout}
        except Exception as e:
            return {"status": "UNAVAILABLE", "provider": self.provider_name, "error": str(e)}

    async def get_sas_token(self) -> Optional[str]:
        """Obtains or returns cached free anonymous SAS token with automatic refresh."""
        now = time.time()
        if self._cached_sas_token and now < (self._sas_token_expiry - 60):
            return self._cached_sas_token
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                r = await client.get(self.sas_url)
                if r.status_code == 200:
                    data = r.json()
                    self._cached_sas_token = data.get("token")
                    expiry_iso = data.get("msft:expiry")
                    if expiry_iso:
                        try:
                            exp_dt = datetime.fromisoformat(expiry_iso.replace("Z", "+00:00"))
                            self._sas_token_expiry = exp_dt.timestamp()
                        except Exception:
                            self._sas_token_expiry = now + 3600
                    else:
                        self._sas_token_expiry = now + 3600
                    return self._cached_sas_token
        except Exception as e:
            logger.warning(f"Could not retrieve MPC SAS token: {e}")
        return None

    def sign_asset_url(self, url: str, sas_token: Optional[str]) -> str:
        """Appends SAS token query string to Microsoft Planetary Computer asset URLs."""
        if not sas_token or not url or "?" in url:
            return url
        return f"{url}?{sas_token}"

    async def search_scenes(
        self,
        bbox: Optional[List[float]] = None,
        geometry: Optional[Dict[str, Any]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_cloud_cover_percent: float = 20.0,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """Executes a STAC Search on Microsoft Planetary Computer."""
        url = f"{self.base_url}/search"
        now = datetime.now(timezone.utc)
        end = end_date or now
        start = start_date or (end - timedelta(days=30))

        datetime_interval = f"{start.strftime('%Y-%m-%dT%H:%M:%SZ')}/{end.strftime('%Y-%m-%dT%H:%M:%SZ')}"

        payload: Dict[str, Any] = {
            "collections": [self.collection],
            "datetime": datetime_interval,
            "query": {
                "eo:cloud_cover": {"lte": max_cloud_cover_percent}
            },
            "limit": min(max(1, limit), 20),
        }

        if geometry:
            payload["intersects"] = geometry
        else:
            payload["bbox"] = bbox or TELANGANA_BBOX

        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                t0 = time.time()
                resp = await client.post(url, json=payload)
                latency_ms = round((time.time() - t0) * 1000, 1)

                if resp.status_code == 200:
                    data = resp.json()
                    features = data.get("features", [])
                    scenes = []
                    for f in features:
                        props = f.get("properties", {})
                        assets = f.get("assets", {})
                        
                        # In Planetary Computer, bands are named B04, B08, SCL
                        red_asset = assets.get("B04") or assets.get("red") or {}
                        nir_asset = assets.get("B08") or assets.get("nir") or {}
                        scl_asset = assets.get("SCL") or assets.get("scl") or {}
                        rendered_thumb = assets.get("rendered_preview") or assets.get("thumbnail") or {}

                        scenes.append({
                            "id": f.get("id"),
                            "provider": self.provider_name,
                            "acquisition_date": props.get("datetime"),
                            "cloud_cover_percentage": props.get("eo:cloud_cover", 0.0),
                            "platform": props.get("platform", "sentinel-2"),
                            "constellation": "Sentinel-2 MSI L2A",
                            "bbox": f.get("bbox"),
                            "geometry": f.get("geometry"),
                            "available_bands": list(assets.keys()),
                            "assets": {
                                "red": red_asset.get("href"),
                                "nir": nir_asset.get("href"),
                                "scl": scl_asset.get("href"),
                                "thumbnail": rendered_thumb.get("href"),
                            },
                            "provenance": {
                                "source": "Microsoft Planetary Computer",
                                "collection": self.collection,
                                "stac_item_id": f.get("id"),
                            }
                        })

                    return {
                        "success": True,
                        "provider": self.provider_name,
                        "scenes_count": len(scenes),
                        "scenes": scenes,
                        "latency_ms": latency_ms,
                        "attribution": self.attribution,
                        "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER,
                    }
                else:
                    return {
                        "success": False,
                        "error_code": f"HTTP_{resp.status_code}",
                        "message": f"Planetary Computer STAC query failed: {resp.text[:100]}",
                    }
        except httpx.TimeoutException:
            return {"success": False, "error_code": "TIMEOUT", "message": "Planetary Computer request timed out."}
        except Exception as e:
            return {"success": False, "error_code": "CONNECTION_ERROR", "message": str(e)}


class Sentinel2Processor:
    """
    Scientific Sentinel-2 L2A optical vegetation processing engine.
    Computes NDVI, performs cloud/shadow masking via SCL, and computes zonal statistics.
    Enforces non-fabrication: Never invents observations for obscured or missing pixels.
    """

    @staticmethod
    def calculate_ndvi_scalar(nir: float, red: float) -> float:
        """Scalar NDVI: (NIR - RED) / (NIR + RED)."""
        denom = nir + red
        if abs(denom) < 1e-6:
            return 0.0
        return round(float(np.clip((nir - red) / denom, -1.0, 1.0)), 4)

    @staticmethod
    def calculate_evi_scalar(nir: float, red: float, blue: float) -> float:
        """Scalar EVI: 2.5 * (NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1.0)."""
        denom = nir + 6.0 * red - 7.5 * blue + 1.0
        if abs(denom) < 1e-6:
            return 0.0
        evi = 2.5 * (nir - red) / denom
        return round(float(np.clip(evi, -1.0, 2.5)), 4)

    @staticmethod
    def calculate_ndmi_scalar(nir: float, swir: float) -> float:
        """Scalar NDMI: (NIR - SWIR) / (NIR + SWIR)."""
        denom = nir + swir
        if abs(denom) < 1e-6:
            return 0.0
        return round(float(np.clip((nir - swir) / denom, -1.0, 1.0)), 4)

    @classmethod
    def process_raster_arrays(
        cls,
        red_band: np.ndarray,
        nir_band: np.ndarray,
        scl_band: Optional[np.ndarray] = None,
        plot_mask: Optional[np.ndarray] = None,
        max_cloud_cover_fraction: float = 0.50,
        min_valid_pixel_fraction: float = 0.20,
        cloud_mask_policy: Optional[set] = None,
    ) -> Dict[str, Any]:
        """
        Processes 2D numpy arrays of Sentinel-2 L2A surface reflectance.
        - Validates dimensions and spatial alignment.
        - Resamples 20m SCL to match 10m B04/B08 resolution.
        - Applies configurable SCL cloud and shadow quality policy.
        - Calculates zonal NDVI statistics across the plot mask geometry.
        - Enforces scientific withholding if plot cloud fraction > max_cloud_cover_fraction (default 50%)
          or valid clear ground pixels < min_valid_pixel_fraction (default 20%).
        """
        if red_band.shape != nir_band.shape:
            raise ValueError(
                f"Dimension mismatch between Red ({red_band.shape}) and NIR ({nir_band.shape}) bands."
            )

        target_h, target_w = red_band.shape
        active_policy = cloud_mask_policy if cloud_mask_policy is not None else CloudMaskPolicy.STANDARD

        # Handle SCL resolution alignment (20m native -> 10m target)
        aligned_scl = None
        if scl_band is not None:
            if scl_band.shape != (target_h, target_w):
                # Integer scale factor expansion (typically 2x)
                scale_y = target_h // scl_band.shape[0]
                scale_x = target_w // scl_band.shape[1]
                if scale_y >= 1 and scale_x >= 1:
                    aligned_scl = np.repeat(np.repeat(scl_band, scale_y, axis=0), scale_x, axis=1)
                    # Trim or pad if fractional
                    aligned_scl = aligned_scl[:target_h, :target_w]
                else:
                    aligned_scl = scl_band
            else:
                aligned_scl = scl_band

        # Build cloud and valid ground mask
        total_pixels = target_h * target_w
        if plot_mask is not None:
            effective_plot_pixels = int(np.sum(plot_mask > 0))
        else:
            effective_plot_pixels = total_pixels

        if effective_plot_pixels == 0:
            return {
                "status": "EMPTY_PLOT_BOUNDARY",
                "valid": False,
                "message": "Plot boundary contains 0 pixels within scene extent.",
                "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER,
            }

        # Identify cloud & shadow pixels using active policy
        if aligned_scl is not None:
            cloud_shadow_mask = np.isin(aligned_scl, list(active_policy))
            nodata_mask = np.isin(aligned_scl, [SCL_NO_DATA, SCL_SATURATED])
            valid_clear_mask = (~cloud_shadow_mask) & (~nodata_mask)
            
            if plot_mask is not None:
                cloud_pixels_in_plot = int(np.sum(cloud_shadow_mask & (plot_mask > 0)))
                cloud_ratio = round(cloud_pixels_in_plot / effective_plot_pixels, 4)
            else:
                cloud_ratio = round(float(np.mean(cloud_shadow_mask)), 4)
        else:
            valid_clear_mask = np.ones((target_h, target_w), dtype=bool)
            cloud_ratio = 0.0

        # Check if plot is cloud-obscured beyond configured threshold
        if cloud_ratio > max_cloud_cover_fraction:
            return {
                "status": "CLOUD_OBSCURED",
                "valid": False,
                "cloud_masked_pixel_ratio": cloud_ratio,
                "max_allowed_cloud_ratio": max_cloud_cover_fraction,
                "message": (
                    f"Observation withheld: plot is {round(cloud_ratio * 100, 1)}% obscured by clouds or cloud shadows "
                    f"(exceeds maximum allowed threshold of {round(max_cloud_cover_fraction * 100, 1)}%). "
                    "Non-fabrication principle enforced."
                ),
                "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER,
            }

        # Apply plot polygon mask
        if plot_mask is not None:
            active_mask = valid_clear_mask & (plot_mask > 0)
        else:
            active_mask = valid_clear_mask

        # Numerical stability & reflection bounds
        red_f = red_band.astype(np.float32)
        nir_f = nir_band.astype(np.float32)
        denom = nir_f + red_f

        valid_data_mask = active_mask & (denom > 1e-4) & (nir_f >= 0) & (red_f >= 0)
        valid_pixel_count = int(np.sum(valid_data_mask))
        valid_pixel_ratio = round(valid_pixel_count / effective_plot_pixels, 4)

        if valid_pixel_ratio < min_valid_pixel_fraction or valid_pixel_count < 1:
            return {
                "status": "INSUFFICIENT_CLEAR_PIXELS",
                "valid": False,
                "cloud_masked_pixel_ratio": cloud_ratio,
                "valid_pixel_ratio": valid_pixel_ratio,
                "min_required_valid_ratio": min_valid_pixel_fraction,
                "message": (
                    f"Observation withheld: only {round(valid_pixel_ratio * 100, 1)}% valid clear reflectance pixels remain "
                    f"(requires minimum of {round(min_valid_pixel_fraction * 100, 1)}% valid pixels across plot geometry)."
                ),
                "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER,
            }

        ndvi_raster = np.where(valid_data_mask, (nir_f - red_f) / denom, np.nan)
        ndvi_values = ndvi_raster[valid_data_mask]
        clipped_ndvi = np.clip(ndvi_values, -1.0, 1.0)

        mean_ndvi = round(float(np.mean(clipped_ndvi)), 4)
        min_ndvi = round(float(np.min(clipped_ndvi)), 4)
        max_ndvi = round(float(np.max(clipped_ndvi)), 4)
        std_ndvi = round(float(np.std(clipped_ndvi)), 4)

        return {
            "status": "SUCCESS",
            "valid": True,
            "mean_ndvi": mean_ndvi,
            "min_ndvi": min_ndvi,
            "max_ndvi": max_ndvi,
            "std_ndvi": std_ndvi,
            "cloud_masked_pixel_ratio": cloud_ratio,
            "valid_pixels": valid_pixel_count,
            "valid_pixel_ratio": valid_pixel_ratio,
            "total_plot_pixels": effective_plot_pixels,
            "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER,
        }

    @classmethod
    async def fetch_cog_tile(
        cls,
        cog_url: str,
        tile_index: int = 0,
        timeout: float = 15.0
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Reads a single tile window from a remote Cloud-Optimized GeoTIFF using HTTP Range requests.
        Eliminates downloading large 200MB+ images over the network.
        Uses pure-Python tifffile for robust streaming header parsing and tile decompression.
        """
        import io
        import tifffile
        
        headers = {"Range": "bytes=0-1048575", "User-Agent": "AcreviaPlatform/1.0"}
        async with httpx.AsyncClient(timeout=timeout) as client:
            hdr_resp = await client.get(cog_url, headers=headers)
            if hdr_resp.status_code not in [200, 206]:
                raise RuntimeError(f"Failed to fetch COG header: HTTP {hdr_resp.status_code}")

            with tifffile.TiffFile(io.BytesIO(hdr_resp.content)) as tif:
                p0 = tif.pages[0]
                total_tiles = len(p0.dataoffsets)
                idx = min(tile_index, total_tiles - 1)
                offset = p0.dataoffsets[idx]
                count = p0.databytecounts[idx]
                meta = {
                    "image_shape": p0.shape,
                    "tile_shape": p0.tile,
                    "dtype": str(p0.dtype),
                    "total_tiles": total_tiles,
                    "geotags": p0.geotiff_tags if hasattr(p0, "geotiff_tags") else {}
                }

            tile_headers = {"Range": f"bytes={offset}-{offset + count - 1}", "User-Agent": "AcreviaPlatform/1.0"}
            tile_resp = await client.get(cog_url, headers=tile_headers)
            if tile_resp.status_code not in [200, 206]:
                raise RuntimeError(f"Failed to fetch COG tile bytes: HTTP {tile_resp.status_code}")

            with tifffile.TiffFile(io.BytesIO(hdr_resp.content)) as tif:
                tile_arr = tif.pages[0].decode(tile_resp.content, idx)[0].squeeze()
                return tile_arr, meta


class CompositeSatelliteClient:
    """
    Composite Satellite Client managing primary Earth Search integration
    with automatic failover to Microsoft Planetary Computer.
    Ensures zero reliance on CDSE OAuth client credentials while maintaining 100% free operation.
    """

    def __init__(self) -> None:
        self.primary_provider = EarthSearchProvider()
        self.secondary_provider = PlanetaryComputerProvider()
        self.processor = Sentinel2Processor()

    async def check_health(self) -> Dict[str, Any]:
        """
        Probes satellite providers in order.
        Returns composite status ensuring seamless operational continuity.
        """
        primary_res = await self.primary_provider.check_health()
        if primary_res.get("status") == "CONFIGURED":
            return {
                "status": "CONFIGURED",
                "primary_provider": self.primary_provider.provider_name,
                "fallback_available": True,
                "fallback_provider": self.secondary_provider.provider_name,
                "auth_mode": "PUBLIC_STAC_ZERO_AUTH",
                "free_tier": True,
                "latency_ms": primary_res.get("latency_ms"),
                "attribution": self.primary_provider.attribution,
                "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER,
                "details": primary_res,
            }

        logger.warning(
            f"Primary satellite provider {self.primary_provider.provider_name} degraded. "
            "Probing fallback Microsoft Planetary Computer..."
        )
        fallback_res = await self.secondary_provider.check_health()
        if fallback_res.get("status") == "CONFIGURED":
            return {
                "status": "CONFIGURED",
                "primary_provider": self.secondary_provider.provider_name,
                "fallback_active": True,
                "auth_mode": "PUBLIC_STAC_ANONYMOUS_SAS",
                "free_tier": True,
                "latency_ms": fallback_res.get("latency_ms"),
                "attribution": self.secondary_provider.attribution,
                "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER,
                "details": fallback_res,
            }

        return {
            "status": "DEGRADED",
            "primary_error": primary_res,
            "fallback_error": fallback_res,
            "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER,
        }

    async def search_scenes(
        self,
        bbox: Optional[List[float]] = None,
        geometry: Optional[Dict[str, Any]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_cloud_cover_percent: float = 20.0,
        limit: int = 5,
        fallback_on_empty: bool = False,
    ) -> Dict[str, Any]:
        """
        Executes scene search using Earth Search with automated fallback to Planetary Computer.
        - By default (fallback_on_empty=False), legitimate 0-scene searches (e.g. strict cloud threshold)
          are treated as valid observations without spuriously engaging failover.
        - Automated failover engages when primary encounters outages, HTTP 429/5xx, timeouts, or connection errors.
        - Provenance metadata tracks primary provider, effective provider, and failover reasons.
        """
        # 1. Attempt Primary Provider (Earth Search)
        res = await self.primary_provider.search_scenes(
            bbox=bbox,
            geometry=geometry,
            start_date=start_date,
            end_date=end_date,
            max_cloud_cover_percent=max_cloud_cover_percent,
            limit=limit,
        )

        if res.get("success"):
            has_scenes = res.get("scenes_count", 0) > 0
            if has_scenes or not fallback_on_empty:
                res["failover_engaged"] = False
                res["primary_provider"] = self.primary_provider.provider_name
                res["effective_provider"] = self.primary_provider.provider_name
                return res

        # 2. Automated Failover to Secondary Provider (Planetary Computer)
        failover_reason = "PRIMARY_EMPTY" if res.get("success") else (res.get("message") or res.get("error_code") or "OUTAGE")
        logger.info(
            f"Primary Earth Search returned {res.get('scenes_count', 0)} scenes or error: {failover_reason}. "
            "Failing over to Microsoft Planetary Computer..."
        )
        fb_res = await self.secondary_provider.search_scenes(
            bbox=bbox,
            geometry=geometry,
            start_date=start_date,
            end_date=end_date,
            max_cloud_cover_percent=max_cloud_cover_percent,
            limit=limit,
        )

        if fb_res.get("success"):
            fb_res["failover_engaged"] = True
            fb_res["primary_provider"] = self.primary_provider.provider_name
            fb_res["effective_provider"] = self.secondary_provider.provider_name
            fb_res["failover_reason"] = failover_reason
            return fb_res

        # If both failed, return structured error with provenance
        return {
            "success": False,
            "error_code": "ALL_PROVIDERS_FAILED",
            "message": f"Earth Search failed ({res.get('message')}) and Planetary Computer failed ({fb_res.get('message')}).",
            "primary_provider": self.primary_provider.provider_name,
            "fallback_provider": self.secondary_provider.provider_name,
            "failover_engaged": True,
            "failover_reason": failover_reason,
            "attribution": EARTH_SEARCH_ATTRIBUTION,
            "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER,
        }


# Global singleton instance
satellite_client = CompositeSatelliteClient()
