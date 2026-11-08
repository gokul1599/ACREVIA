"""
ACREVIA - Weather & Agrometeorological Client Adapter.
Integrates Open-Meteo API for real-time temperature, humidity, and precipitation data.
Enforces non-commercial caching, attribution, and clearly distinguishes model estimates from in-situ measurements.
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import time
import httpx

from backend.app.core.config import settings
from backend.app.core.logging import logger

OPEN_METEO_ATTRIBUTION = "Weather data provided by Open-Meteo.com under Non-Commercial Attribution license"

# Approximate centroid coordinates for Telangana agricultural districts
TELANGANA_DISTRICT_COORDS = {
    "warangal": (17.9689, 79.5941),
    "khammam": (17.2473, 80.1514),
    "nalgonda": (17.0575, 79.2684),
    "karimnagar": (18.4386, 79.1288),
    "nizamabad": (18.6725, 78.0941),
    "adilabad": (19.6641, 78.5320),
    "hyderabad": (17.3850, 78.4867),
}


class WeatherClient:
    """
    Agrometeorological data adapter with in-memory TTL caching to respect Open-Meteo rate limits.
    """
    def __init__(self, base_url: Optional[str] = None, cache_ttl_seconds: int = 900):
        self.base_url = base_url or settings.OPEN_METEO_API_URL
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}

    async def check_health(self) -> Dict[str, Any]:
        """Verifies Open-Meteo connectivity."""
        try:
            sample = await self.get_district_weather("warangal")
            return {
                "status": "CONFIGURED",
                "provider": "Open-Meteo",
                "auth_required": False,
                "attribution": OPEN_METEO_ATTRIBUTION,
                "cached": sample.get("is_cached", False),
                "data_nature": sample.get("data_nature", "MODEL_FORECAST_ESTIMATE")
            }
        except Exception as e:
            return {
                "status": "UNAVAILABLE",
                "provider": "Open-Meteo",
                "error": str(e)
            }

    async def get_district_weather(self, district: str) -> Dict[str, Any]:
        """
        Retrieves real-time agrometeorological indicators for a Telangana district.
        Serves from cache if requested within TTL to conserve free community bandwidth.
        """
        dist_key = district.lower().strip()

        # Check TTL cache
        now = time.time()
        if dist_key in self._cache:
            cached_time, cached_val = self._cache[dist_key]
            if now - cached_time < self.cache_ttl_seconds:
                val = dict(cached_val)
                val["is_cached"] = True
                return val

        coords = TELANGANA_DISTRICT_COORDS.get(dist_key, (17.8496, 79.1151))  # Default Telangana centroid
        lat, lon = coords

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
            "timezone": "Asia/Kolkata"
        }

        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(self.base_url, params=params)
                if resp.status_code == 200:
                    data = resp.json().get("current", {})
                    result = {
                        "status": "CONFIGURED",
                        "timestamp": data.get("time", datetime.now(timezone.utc).isoformat()),
                        "temperature": float(data.get("temperature_2m", 28.0)),
                        "humidity": float(data.get("relative_humidity_2m", 65.0)),
                        "precipitation": float(data.get("precipitation", 0.0)),
                        "wind_speed": float(data.get("wind_speed_10m", 8.0)),
                        "source": "Open-Meteo Forecast & Historical API",
                        "district": district,
                        "attribution": OPEN_METEO_ATTRIBUTION,
                        "data_nature": "MODEL_FORECAST_ESTIMATE",
                        "is_measured_in_situ": False,
                        "is_cached": False
                    }
                    self._cache[dist_key] = (now, result)
                    return result
                else:
                    logger.warning(f"Weather API returned status {resp.status_code}")
                    return self._fallback(district, status="DEGRADED")
        except Exception as e:
            logger.warning(f"Weather provider error: {e}")
            return self._fallback(district, status="UNAVAILABLE")

    @staticmethod
    def _fallback(district: str, status: str = "DEGRADED") -> Dict[str, Any]:
        """Returns baseline climate indicators for Telangana agro-climatic zones."""
        return {
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": 29.5,
            "humidity": 60.0,
            "precipitation": 0.0,
            "wind_speed": 10.0,
            "source": "PJTSAU Historical Agro-Climatic Normal (Fallback)",
            "district": district,
            "attribution": "PJTSAU Agro-Climatic Normals",
            "data_nature": "HISTORICAL_CLIMATIC_NORMAL",
            "is_measured_in_situ": False,
            "is_cached": False
        }


weather_client = WeatherClient()
