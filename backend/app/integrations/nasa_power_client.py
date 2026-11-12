"""
ACREVIA - NASA POWER Agroclimatology Client Adapter.
Queries daily solar irradiance (ALLSKY_SFC_SW_DWN), precipitation (PRECTOTCORR),
and temperature/humidity baselines for water resilience and drought stress profiling.
Enforces privacy dithering, 30-day caching, and PJTSAU baseline fallback.
"""

from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timezone, timedelta
import time
import httpx

from backend.app.core.logging import logger
from backend.app.schemas.nasa_power import (
    NASAPowerDailyPoint,
    NASAPowerClimatologyBaseline,
)
from backend.app.integrations.weather_client import dither_coordinates

NASA_POWER_ATTRIBUTION = "Data obtained from NASA Langley Research Center POWER Project (Agroclimatology Community)"
NASA_POWER_DEFAULT_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


class NASAPowerClient:
    """
    Adapter for NASA POWER Agroclimatology REST API.
    Provides regional solar radiation and historical water-balance indicators.
    """
    PARAMETERS = "ALLSKY_SFC_SW_DWN,T2M,RH2M,PRECTOTCORR"

    def __init__(self, base_url: Optional[str] = None, cache_ttl_seconds: int = 30 * 86400):
        self.base_url = base_url or NASA_POWER_DEFAULT_URL
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: Dict[str, Tuple[float, NASAPowerClimatologyBaseline]] = {}

    async def check_health(self) -> Dict[str, Any]:
        """Probes NASA POWER Agroclimatology API with Warangal coordinates."""
        try:
            baseline = await self.get_daily_climatology(
                17.9689, 79.5941, days=3, dither=True
            )
            return {
                "status": "CONFIGURED",
                "provider": "NASA POWER Agroclimatology",
                "auth_required": False,
                "attribution": NASA_POWER_ATTRIBUTION,
                "cached": baseline.is_cached,
                "data_nature": baseline.epistemic_status,
                "is_measured_in_situ": False
            }
        except Exception as e:
            return {
                "status": "UNAVAILABLE",
                "provider": "NASA POWER Agroclimatology",
                "error": str(e)
            }

    async def get_daily_climatology(
        self,
        latitude: float,
        longitude: float,
        days: int = 7,
        dither: bool = True
    ) -> NASAPowerClimatologyBaseline:
        """
        Retrieves daily solar radiation and agroclimatological indicators for a recent window.
        Coordinates are dithered to 2 decimal places to preserve smallholder privacy.
        """
        q_lat, q_lon = dither_coordinates(latitude, longitude) if dither else (float(latitude), float(longitude))
        cache_key = f"nasa_power_{q_lat:.2f}_{q_lon:.2f}_{days}d"

        now = time.time()
        if cache_key in self._cache:
            cached_time, cached_val = self._cache[cache_key]
            if now - cached_time < self.cache_ttl_seconds:
                val = cached_val.model_copy(deep=True)
                val.is_cached = True
                return val

        # Calculate date range with 3-day safety lag for NASA POWER data processing
        end_dt = datetime.now(timezone.utc) - timedelta(days=3)
        start_dt = end_dt - timedelta(days=days - 1)
        start_str = start_dt.strftime("%Y%m%d")
        end_str = end_dt.strftime("%Y%m%d")

        params = {
            "parameters": self.PARAMETERS,
            "community": "AG",
            "longitude": q_lon,
            "latitude": q_lat,
            "start": start_str,
            "end": end_str,
            "format": "JSON"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self.base_url, params=params)
                if resp.status_code == 200:
                    payload = resp.json()
                    res = self._parse_payload(q_lat, q_lon, dither, payload, status="CONFIGURED")
                    self._cache[cache_key] = (now, res)
                    return res
                else:
                    logger.warning(f"NASA POWER API returned status {resp.status_code}")
                    return self._fallback_baseline(q_lat, q_lon, dither, days=days, status="DEGRADED")
        except Exception as e:
            logger.warning(f"NASA POWER client error: {e}")
            return self._fallback_baseline(q_lat, q_lon, dither, days=days, status="UNAVAILABLE")

    def _parse_payload(
        self,
        lat: float,
        lon: float,
        dither: bool,
        payload: Dict[str, Any],
        status: str = "CONFIGURED"
    ) -> NASAPowerClimatologyBaseline:
        """Parses NASA POWER JSON payload into typed NASAPowerClimatologyBaseline."""
        properties = payload.get("properties", {}).get("parameter", {})
        sw_dict = properties.get("ALLSKY_SFC_SW_DWN", {})
        t2m_dict = properties.get("T2M", {})
        rh_dict = properties.get("RH2M", {})
        precip_dict = properties.get("PRECTOTCORR", {})

        records: List[NASAPowerDailyPoint] = []
        all_dates = sorted(sw_dict.keys())

        total_sw = 0.0
        total_precip = 0.0
        total_temp = 0.0
        count = 0

        for d_str in all_dates:
            sw_val = float(sw_dict.get(d_str, 0.0))
            t_val = float(t2m_dict.get(d_str, 28.0))
            rh_val = float(rh_dict.get(d_str, 60.0))
            p_val = float(precip_dict.get(d_str, 0.0))

            # Filter missing/sentinel values (-999.0 in NASA POWER)
            if sw_val < 0.0:
                sw_val = 18.5  # Telangana normal solar irradiance MJ/m²/day
            if t_val < -50.0:
                t_val = 28.0
            if rh_val < 0.0:
                rh_val = 60.0
            if p_val < 0.0:
                p_val = 0.0

            total_sw += sw_val
            total_precip += p_val
            total_temp += t_val
            count += 1

            records.append(
                NASAPowerDailyPoint(
                    date=d_str,
                    solar_radiation_allsky_sw=round(sw_val, 2),
                    temperature_2m=round(t_val, 2),
                    relative_humidity_2m=round(rh_val, 2),
                    precipitation_corrected=round(p_val, 2)
                )
            )

        mean_sw = round(total_sw / max(count, 1), 2) if count > 0 else 18.5
        mean_t = round(total_temp / max(count, 1), 2) if count > 0 else 28.0

        return NASAPowerClimatologyBaseline(
            status=status,
            latitude=lat,
            longitude=lon,
            is_dithered=dither,
            retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
            solar_radiation_mean_daily=mean_sw,
            precipitation_total_period=round(total_precip, 2),
            temperature_mean_period=mean_t,
            records=records,
            data_source="NASA_POWER_AGROCLIMATOLOGY",
            epistemic_status="CLIMATOLOGICAL_REMOTE_ESTIMATE",
            is_measured_in_situ=False,
            non_override_guarantee=True,
            attribution=NASA_POWER_ATTRIBUTION,
            is_cached=False
        )

    def _fallback_baseline(
        self,
        lat: float,
        lon: float,
        dither: bool,
        days: int = 7,
        status: str = "DEGRADED"
    ) -> NASAPowerClimatologyBaseline:
        """Returns 30-year climatological normal baseline for Telangana."""
        records: List[NASAPowerDailyPoint] = []
        today = datetime.now(timezone.utc).date()
        for i in range(days):
            d = today - timedelta(days=i + 3)
            records.append(
                NASAPowerDailyPoint(
                    date=d.strftime("%Y%m%d"),
                    solar_radiation_allsky_sw=19.2,
                    temperature_2m=28.5,
                    relative_humidity_2m=62.0,
                    precipitation_corrected=0.5
                )
            )

        return NASAPowerClimatologyBaseline(
            status=status,
            latitude=lat,
            longitude=lon,
            is_dithered=dither,
            retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
            solar_radiation_mean_daily=19.2,
            precipitation_total_period=round(0.5 * days, 2),
            temperature_mean_period=28.5,
            records=records,
            data_source="PJTSAU_CLIMATOLOGY_NORMAL (Fallback)",
            epistemic_status="HISTORICAL_CLIMATIC_NORMAL",
            is_measured_in_situ=False,
            non_override_guarantee=True,
            attribution="PJTSAU 30-Year Agro-Climatology Normals",
            is_cached=False
        )


nasa_power_client = NASAPowerClient()
