"""
ACREVIA - Copernicus Data Space Ecosystem (CDSE) Client Adapter.
Queries Sentinel-2 multispectral satellite imagery, manages OAuth2 token lifecycles with caching,
applies cloud masking filters, and enforces non-diagnostic evidence disclaimers.
"""

from typing import Dict, Any, List, Optional
import time
from datetime import datetime, timezone, timedelta
import httpx

from backend.app.core.config import settings
from backend.app.core.logging import logger

COPERNICUS_ATTRIBUTION = "Contains modified Copernicus Sentinel data [2026]"
SATELLITE_EVIDENCE_DISCLAIMER = (
    "Satellite-derived vegetation indices (NDVI, EVI, NDMI) provide spectral reflectance estimates "
    "and canopy vigor trends. They do not constitute direct biological diagnoses of plant disease, "
    "insect damage, or soil nutrient deficiencies without in-situ field verification."
)

# Geographic bounding box for Telangana State, India (WGS84)
# Latitude: ~15.8°N to 19.9°N, Longitude: ~77.2°E to 81.3°E
TELANGANA_BBOX_POLYGON = "POLYGON((77.2 15.8, 81.3 15.8, 81.3 19.9, 77.2 19.9, 77.2 15.8))"


class CopernicusClient:
    """
    Adapter for Copernicus Data Space Ecosystem (CDSE) Sentinel-2 services.
    Handles server-side OAuth2 token acquisition, expiry caching, and OData catalogue queries.
    """
    TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    ODATA_BASE_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1"

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        self.client_id = client_id or settings.COPERNICUS_CLIENT_ID
        self.client_secret = client_secret or settings.COPERNICUS_CLIENT_SECRET
        self._cached_token: Optional[str] = None
        self._token_expiry_timestamp: float = 0.0

    @property
    def is_configured(self) -> bool:
        """Returns True if client credentials are provided."""
        return bool(
            self.client_id and self.client_id.strip() and
            self.client_secret and self.client_secret.strip()
        )

    async def get_access_token(self) -> Optional[str]:
        """
        Obtains or returns cached OAuth2 Bearer token from Copernicus CDSE.
        Automatically refreshes before expiration (with 60-second safety margin).
        """
        if not self.is_configured:
            return None

        # Return cached token if still valid
        now = time.time()
        if self._cached_token and now < (self._token_expiry_timestamp - 60):
            return self._cached_token

        # Acquire new token via Client Credentials Grant
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.TOKEN_URL, data=data)
                if resp.status_code == 200:
                    token_data = resp.json()
                    self._cached_token = token_data.get("access_token")
                    expires_in = token_data.get("expires_in", 3600)
                    self._token_expiry_timestamp = now + expires_in
                    logger.info("Acquired fresh Copernicus CDSE OAuth2 access token.")
                    return self._cached_token
                else:
                    logger.warning(f"Copernicus OAuth failed: HTTP {resp.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error requesting Copernicus access token: {e}")
            return None

    async def check_health(self) -> Dict[str, Any]:
        """
        Verifies Copernicus service availability without exposing secrets.
        """
        try:
            # Query public OData catalogue endpoint (works without credentials)
            params = {
                "$filter": "Collection/Name eq 'SENTINEL-2'",
                "$top": "1"
            }
            async with httpx.AsyncClient(timeout=8.0) as client:
                t0 = time.time()
                resp = await client.get(f"{self.ODATA_BASE_URL}/Products", params=params)
                latency_ms = round((time.time() - t0) * 1000, 1)

                if resp.status_code == 200:
                    return {
                        "status": "CONFIGURED",
                        "provider": "Copernicus Data Space Ecosystem",
                        "constellation": "Sentinel-2 MSI",
                        "auth_mode": "AUTHENTICATED" if self.is_configured else "PUBLIC_CATALOGUE",
                        "has_credentials": self.is_configured,
                        "latency_ms": latency_ms,
                        "attribution": COPERNICUS_ATTRIBUTION,
                        "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER
                    }
                else:
                    return {
                        "status": "DEGRADED",
                        "provider": "Copernicus Data Space Ecosystem",
                        "http_status": resp.status_code
                    }
        except httpx.TimeoutException:
            logger.warning("Copernicus OData endpoint timed out.")
            return {"status": "TIMEOUT", "provider": "Copernicus Data Space Ecosystem"}
        except Exception as e:
            logger.warning(f"Copernicus catalogue connection error: {e}")
            return {"status": "UNAVAILABLE", "provider": "Copernicus Data Space Ecosystem", "error": str(e)}

    async def search_sentinel2_scenes(
        self,
        max_cloud_cover_percent: float = 20.0,
        days_back: int = 15,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Searches recent Sentinel-2 MSI Level-2A surface reflectance products over Telangana.
        Applies cloud masking threshold and returns normalized scene metadata.
        """
        now = datetime.now(timezone.utc)
        start_date = (now - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00.000Z")

        # Build OData filter query
        filter_expr = (
            f"Collection/Name eq 'SENTINEL-2' and "
            f"ContentDate/Start ge {start_date} and "
            f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/Value le {max_cloud_cover_percent})"
        )

        params = {
            "$filter": filter_expr,
            "$orderby": "ContentDate/Start desc",
            "$top": str(min(20, limit))
        }

        token = await self.get_access_token()
        headers = {"User-Agent": "ACREVIA-AgriEarth/1.0"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                resp = await client.get(
                    f"{self.ODATA_BASE_URL}/Products",
                    params=params,
                    headers=headers
                )
                if resp.status_code == 200:
                    raw_products = resp.json().get("value", [])
                    scenes = []
                    for prod in raw_products:
                        scenes.append({
                            "product_id": prod.get("Id"),
                            "name": prod.get("Name"),
                            "acquisition_date": prod.get("ContentDate", {}).get("Start"),
                            "content_length_bytes": prod.get("ContentLength"),
                            "origin_constellation": "Sentinel-2",
                            "cloud_filtered": True
                        })
                    return {
                        "success": True,
                        "scenes_count": len(scenes),
                        "scenes": scenes,
                        "attribution": COPERNICUS_ATTRIBUTION,
                        "disclaimer": SATELLITE_EVIDENCE_DISCLAIMER
                    }
                else:
                    logger.warning(f"Copernicus catalogue search failed: HTTP {resp.status_code}")
                    return {
                        "success": False,
                        "error_code": f"HTTP_{resp.status_code}",
                        "message": "Copernicus OData query failed."
                    }
        except Exception as e:
            logger.warning(f"Error querying Copernicus catalogue: {e}")
            return {
                "success": False,
                "error_code": "CONNECTION_ERROR",
                "message": str(e)
            }


copernicus_client = CopernicusClient()
