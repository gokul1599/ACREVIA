"""
ACREVIA - Weather & Agrometeorological Client Adapter.
Integrates Open-Meteo API for real-time temperature, humidity, and precipitation data.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import httpx

from backend.app.core.logging import logger

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
    Agrometeorological data adapter.
    """
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    @classmethod
    async def get_district_weather(cls, district: str) -> Dict[str, Any]:
        """
        Retrieves real-time agrometeorological indicators for a Telangana district.
        """
        dist_key = district.lower().strip()
        coords = TELANGANA_DISTRICT_COORDS.get(dist_key, (17.8496, 79.1151))  # Default Telangana centroid
        lat, lon = coords

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
            "timezone": "Asia/Kolkata"
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(cls.BASE_URL, params=params)
                if resp.status_code == 200:
                    data = resp.json().get("current", {})
                    return {
                        "status": "CONFIGURED",
                        "timestamp": data.get("time", datetime.now(timezone.utc).isoformat()),
                        "temperature": float(data.get("temperature_2m", 28.0)),
                        "humidity": float(data.get("relative_humidity_2m", 65.0)),
                        "precipitation": float(data.get("precipitation", 0.0)),
                        "wind_speed": float(data.get("wind_speed_10m", 8.0)),
                        "source": "Open-Meteo Historical & Forecast API",
                        "district": district
                    }
                else:
                    logger.warning(f"Weather API returned status {resp.status_code}")
                    return cls._fallback(district, status="DEGRADED")
        except Exception as e:
            logger.warning(f"Weather provider error: {e}")
            return cls._fallback(district, status="UNAVAILABLE")

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
            "district": district
        }


weather_client = WeatherClient()
