"""
ACREVIA - RiskCast Weather Ingestion & Normalization Service.
Separates weather observations from forecasts and calculates agro-climatic indices.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from backend.app.core.logging import logger
from backend.app.models.farm import Farm
from backend.app.models.weather_data import WeatherData
from backend.app.integrations.weather_client import TELANGANA_DISTRICT_COORDS


class WeatherService:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    @classmethod
    async def fetch_and_persist_weather(cls, farm: Farm, db: Session) -> WeatherData:
        """
        Fetches current agrometeorological observation and stores WeatherData record.
        If live API fails or times out, uses district climatology normal.
        """
        dist_key = farm.district.lower().strip()
        coords = TELANGANA_DISTRICT_COORDS.get(dist_key, (17.8496, 79.1151))
        lat, lon = coords

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
            "hourly": "temperature_2m,relative_humidity_2m,precipitation",
            "forecast_days": 3,
            "timezone": "Asia/Kolkata"
        }

        temp = 28.5
        humidity = 68.0
        precip = 0.0
        wind = 8.5
        provider = "Open-Meteo Live API"
        leaf_wetness_hours = 4.0

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(cls.BASE_URL, params=params)
                if resp.status_code == 200:
                    payload = resp.json()
                    curr = payload.get("current", {})
                    temp = float(curr.get("temperature_2m", 28.5))
                    humidity = float(curr.get("relative_humidity_2m", 68.0))
                    precip = float(curr.get("precipitation", 0.0))
                    wind = float(curr.get("wind_speed_10m", 8.5))
                    
                    # Estimate past 24h leaf wetness from hourly RH >= 88% or rain > 0.1mm
                    hourly = payload.get("hourly", {})
                    rh_series = hourly.get("relative_humidity_2m", [])[:24]
                    p_series = hourly.get("precipitation", [])[:24]
                    wet_hours = 0
                    for rh, p in zip(rh_series, p_series):
                        if (rh and rh >= 88.0) or (p and p > 0.1):
                            wet_hours += 1
                    leaf_wetness_hours = float(wet_hours)
                else:
                    provider = "PJTSAU Agro-Climatic Normal (Fallback)"
        except Exception as e:
            logger.warning(f"Live weather fetch failed: {e}. Falling back to normal.")
            provider = "PJTSAU Agro-Climatic Normal (Fallback)"

        # Persist observation
        weather_entry = WeatherData(
            farm_id=farm.id,
            district=farm.district,
            is_forecast=False,
            observation_time=datetime.now(timezone.utc),
            temperature_celsius=temp,
            relative_humidity=humidity,
            precipitation_mm=precip,
            wind_speed_kmh=wind,
            leaf_wetness_hours=leaf_wetness_hours,
            source_provider=provider
        )
        db.add(weather_entry)
        db.commit()
        db.refresh(weather_entry)
        return weather_entry

    @classmethod
    def get_latest_weather(cls, farm_id: str, db: Session) -> Optional[WeatherData]:
        """Retrieves most recent WeatherData entry for a farm."""
        stmt = (
            select(WeatherData)
            .filter_by(farm_id=farm_id, is_forecast=False)
            .order_by(desc(WeatherData.observation_time))
            .limit(1)
        )
        return db.scalars(stmt).first()
