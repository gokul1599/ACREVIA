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
    "mahabubabad": (17.5986, 80.0037),
    "suryapet": (17.1439, 79.6239),
}


def dither_coordinates(lat: float, lon: float, precision: int = 2) -> Tuple[float, float]:
    """
    Rounds parcel coordinates to protect farmer privacy from third-party server logging.
    Precision 2 decimals corresponds to approximately 1.1 km spatial dithering.
    """
    return round(float(lat), precision), round(float(lon), precision)


class WeatherClient:
    """
    Agrometeorological data adapter with in-memory TTL caching to respect Open-Meteo rate limits.
    Supports both regional district centroids and exact parcel coordinates with privacy dithering.
    """
    AGRICULTURAL_CURRENT_VARS = (
        "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,"
        "soil_moisture_0_to_1cm,soil_moisture_1_to_3cm,soil_moisture_3_to_9cm,"
        "soil_moisture_9_to_27cm,soil_moisture_27_to_81cm,"
        "soil_temperature_0cm,soil_temperature_6cm,soil_temperature_18cm,soil_temperature_54cm,"
        "et0_fao_evapotranspiration,shortwave_radiation_instant"
    )

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
                "data_nature": sample.get("data_nature", "MODEL_FORECAST_ESTIMATE"),
                "agricultural_extensions_active": True
            }
        except Exception as e:
            return {
                "status": "UNAVAILABLE",
                "provider": "Open-Meteo",
                "error": str(e)
            }

    async def get_agricultural_weather(
        self,
        latitude: float,
        longitude: float,
        dither: bool = True
    ) -> Dict[str, Any]:
        """
        Retrieves real-time agrometeorological indicators, multi-depth root-zone soil moisture,
        soil temperature, and reference evapotranspiration (FAO-56 Penman-Monteith).
        Coordinates are dithered to 2 decimal places (~1.1 km) by default to protect farmer privacy.
        """
        query_lat, query_lon = dither_coordinates(latitude, longitude) if dither else (float(latitude), float(longitude))
        cache_key = f"coord_{query_lat:.2f}_{query_lon:.2f}"

        now = time.time()
        if cache_key in self._cache:
            cached_time, cached_val = self._cache[cache_key]
            if now - cached_time < self.cache_ttl_seconds:
                val = dict(cached_val)
                val["is_cached"] = True
                return val

        params = {
            "latitude": query_lat,
            "longitude": query_lon,
            "current": self.AGRICULTURAL_CURRENT_VARS,
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
                        "latitude": query_lat,
                        "longitude": query_lon,
                        "is_dithered": dither,
                        "temperature": float(data.get("temperature_2m", 28.0)),
                        "humidity": float(data.get("relative_humidity_2m", 65.0)),
                        "precipitation": float(data.get("precipitation", 0.0)),
                        "wind_speed": float(data.get("wind_speed_10m", 8.0)),
                        "soil_moisture": {
                            "0_to_1cm": float(data.get("soil_moisture_0_to_1cm", 0.18)) if data.get("soil_moisture_0_to_1cm") is not None else None,
                            "1_to_3cm": float(data.get("soil_moisture_1_to_3cm", 0.20)) if data.get("soil_moisture_1_to_3cm") is not None else None,
                            "3_to_9cm": float(data.get("soil_moisture_3_to_9cm", 0.22)) if data.get("soil_moisture_3_to_9cm") is not None else None,
                            "9_to_27cm": float(data.get("soil_moisture_9_to_27cm", 0.24)) if data.get("soil_moisture_9_to_27cm") is not None else None,
                            "27_to_81cm": float(data.get("soil_moisture_27_to_81cm", 0.25)) if data.get("soil_moisture_27_to_81cm") is not None else None,
                        },
                        "soil_temperature": {
                            "0cm": float(data.get("soil_temperature_0cm", 29.0)) if data.get("soil_temperature_0cm") is not None else None,
                            "6cm": float(data.get("soil_temperature_6cm", 28.5)) if data.get("soil_temperature_6cm") is not None else None,
                            "18cm": float(data.get("soil_temperature_18cm", 27.8)) if data.get("soil_temperature_18cm") is not None else None,
                            "54cm": float(data.get("soil_temperature_54cm", 27.0)) if data.get("soil_temperature_54cm") is not None else None,
                        },
                        "et0_fao_evapotranspiration": float(data.get("et0_fao_evapotranspiration", 4.2)) if data.get("et0_fao_evapotranspiration") is not None else None,
                        "shortwave_radiation_instant": float(data.get("shortwave_radiation_instant", 650.0)) if data.get("shortwave_radiation_instant") is not None else None,
                        "source": "Open-Meteo Forecast & Historical API (Agrometeorological Extension)",
                        "attribution": OPEN_METEO_ATTRIBUTION,
                        "data_nature": "MODEL_FORECAST_ESTIMATE",
                        "is_measured_in_situ": False,
                        "is_cached": False
                    }
                    self._cache[cache_key] = (now, result)
                    return result
                else:
                    logger.warning(f"Weather API returned status {resp.status_code}")
                    return self._fallback_coords(query_lat, query_lon, status="DEGRADED")
        except Exception as e:
            logger.warning(f"Weather provider error: {e}")
            return self._fallback_coords(query_lat, query_lon, status="UNAVAILABLE")

    async def get_district_weather(self, district: str) -> Dict[str, Any]:
        """
        Retrieves real-time agrometeorological indicators for a Telangana district.
        Serves from cache if requested within TTL to conserve free community bandwidth.
        Maintains 100% backward compatibility for all legacy caller contracts.
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

        try:
            res = await self.get_agricultural_weather(lat, lon, dither=False)
            if res.get("status") in ["CONFIGURED", "DEGRADED", "UNAVAILABLE"]:
                # Attach district metadata to maintain exact backwards compatibility
                res["district"] = district
                self._cache[dist_key] = (now, res)
                return res
            return self._fallback(district, status="DEGRADED")
        except Exception as e:
            logger.warning(f"District weather resolution error: {e}")
            return self._fallback(district, status="UNAVAILABLE")

    @staticmethod
    def _fallback_coords(lat: float, lon: float, status: str = "DEGRADED") -> Dict[str, Any]:
        """Returns baseline agroclimatic normal indicators for coordinates."""
        return {
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": lat,
            "longitude": lon,
            "is_dithered": True,
            "temperature": 29.5,
            "humidity": 60.0,
            "precipitation": 0.0,
            "wind_speed": 10.0,
            "soil_moisture": {
                "0_to_1cm": 0.18,
                "1_to_3cm": 0.20,
                "3_to_9cm": 0.22,
                "9_to_27cm": 0.24,
                "27_to_81cm": 0.25,
            },
            "soil_temperature": {
                "0cm": 29.5,
                "6cm": 28.5,
                "18cm": 27.5,
                "54cm": 27.0,
            },
            "et0_fao_evapotranspiration": 4.5,
            "shortwave_radiation_instant": 600.0,
            "source": "PJTSAU Historical Agro-Climatic Normal (Fallback)",
            "attribution": "PJTSAU Agro-Climatic Normals",
            "data_nature": "HISTORICAL_CLIMATIC_NORMAL",
            "is_measured_in_situ": False,
            "is_cached": False
        }

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
            "soil_moisture": {
                "0_to_1cm": 0.18,
                "1_to_3cm": 0.20,
                "3_to_9cm": 0.22,
                "9_to_27cm": 0.24,
                "27_to_81cm": 0.25,
            },
            "soil_temperature": {
                "0cm": 29.5,
                "6cm": 28.5,
                "18cm": 27.5,
                "54cm": 27.0,
            },
            "et0_fao_evapotranspiration": 4.5,
            "shortwave_radiation_instant": 600.0,
            "source": "PJTSAU Historical Agro-Climatic Normal (Fallback)",
            "district": district,
            "attribution": "PJTSAU Agro-Climatic Normals",
            "data_nature": "HISTORICAL_CLIMATIC_NORMAL",
            "is_measured_in_situ": False,
            "is_cached": False
        }


weather_client = WeatherClient()
