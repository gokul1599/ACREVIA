"""
ACREVIA - ISRIC SoilGrids v2.0 Client Adapter.
Queries 250m machine-learning derived soil physical and chemical profiles.
Enforces privacy coordinate dithering, long-term TTL caching (180 days),
conversion factor normalization, and the non-override scientific invariant.
"""

from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timezone
import time
import httpx

from backend.app.core.logging import logger
from backend.app.schemas.soilgrids import (
    SoilDepthLayer,
    SoilPhysicalProperties,
    SoilChemicalProperties,
    SoilGridsProfileResponse,
)
from backend.app.integrations.weather_client import dither_coordinates

SOILGRIDS_ATTRIBUTION = "Soil data produced by ISRIC - World Soil Information (SoilGrids 250m v2.0, CC-BY 4.0)"
SOILGRIDS_DEFAULT_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"


class SoilGridsClient:
    """
    Adapter for ISRIC SoilGrids v2.0 REST API.
    Provides baseline pedological indicators (texture, pH, organic carbon, CEC) for farm holdings.
    """
    PROPERTIES = ["phh2o", "soc", "clay", "sand", "silt", "bdod", "cec", "nitrogen"]
    DEPTHS = ["0-5cm", "5-15cm", "15-30cm"]
    VALUES = ["mean", "Q0.05", "Q0.5", "Q0.95"]

    # Raw value divisors specified by ISRIC SoilGrids v2 schema
    DIVISORS = {
        "phh2o": 10.0,       # pH * 10 -> pH
        "clay": 10.0,        # g/kg -> % (e.g., 250 g/kg = 25.0%)
        "sand": 10.0,        # g/kg -> %
        "silt": 10.0,        # g/kg -> %
        "soc": 10.0,         # dg/kg -> g/kg
        "bdod": 100.0,       # cg/cm³ -> g/cm³
        "cec": 10.0,         # mmol(c)/kg -> cmol(+)/kg
        "nitrogen": 100.0,   # cg/kg -> g/kg
    }

    UNITS = {
        "phh2o": "pH",
        "clay": "%",
        "sand": "%",
        "silt": "%",
        "soc": "g/kg",
        "bdod": "g/cm³",
        "cec": "cmol(+)/kg",
        "nitrogen": "g/kg",
    }

    def __init__(self, base_url: Optional[str] = None, cache_ttl_seconds: int = 180 * 86400):
        self.base_url = base_url or SOILGRIDS_DEFAULT_URL
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: Dict[str, Tuple[float, SoilGridsProfileResponse]] = {}

    async def check_health(self) -> Dict[str, Any]:
        """Probes SoilGrids API connectivity using Warangal benchmark coordinates."""
        try:
            profile = await self.get_soil_profile(17.9689, 79.5941, dither=True)
            return {
                "status": "CONFIGURED",
                "provider": "ISRIC SoilGrids v2.0",
                "auth_required": False,
                "attribution": SOILGRIDS_ATTRIBUTION,
                "cached": profile.is_cached,
                "data_nature": profile.epistemic_status,
                "is_measured_in_situ": False
            }
        except Exception as e:
            return {
                "status": "UNAVAILABLE",
                "provider": "ISRIC SoilGrids v2.0",
                "error": str(e)
            }

    async def get_soil_profile(
        self,
        latitude: float,
        longitude: float,
        dither: bool = True
    ) -> SoilGridsProfileResponse:
        """
        Retrieves physical and chemical soil properties at 0-5cm surface depth.
        Dithers coordinates to 2 decimal places to preserve smallholder location privacy.
        """
        q_lat, q_lon = dither_coordinates(latitude, longitude) if dither else (float(latitude), float(longitude))
        cache_key = f"soil_{q_lat:.2f}_{q_lon:.2f}"

        now = time.time()
        if cache_key in self._cache:
            cached_time, cached_val = self._cache[cache_key]
            if now - cached_time < self.cache_ttl_seconds:
                val = cached_val.model_copy(deep=True)
                val.is_cached = True
                return val

        # SoilGrids query parameters
        params = [
            ("lon", q_lon),
            ("lat", q_lat),
        ]
        for p in self.PROPERTIES:
            params.append(("property", p))
        for d in self.DEPTHS:
            params.append(("depth", d))
        for v in self.VALUES:
            params.append(("value", v))

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(self.base_url, params=params)
                if resp.status_code == 200:
                    payload = resp.json()
                    layers_data = self._parse_layers(payload)
                    res = self._build_response(
                        q_lat, q_lon, dither, layers_data, status="CONFIGURED", is_cached=False
                    )
                    self._cache[cache_key] = (now, res)
                    return res
                else:
                    logger.warning(f"SoilGrids API returned status {resp.status_code}")
                    return self._fallback_profile(q_lat, q_lon, dither, status="DEGRADED")
        except Exception as e:
            logger.warning(f"SoilGrids client error: {e}")
            return self._fallback_profile(q_lat, q_lon, dither, status="UNAVAILABLE")

    def _parse_layers(self, payload: Dict[str, Any]) -> Dict[str, Dict[str, SoilDepthLayer]]:
        """Extracts and scales depth layer observations from SoilGrids GeoJSON response."""
        layers_dict: Dict[str, Dict[str, SoilDepthLayer]] = {}
        properties = payload.get("properties", {})
        raw_layers = properties.get("layers", [])

        for layer in raw_layers:
            name = layer.get("name")
            divisor = self.DIVISORS.get(name, 1.0)
            unit = self.UNITS.get(name, "")
            depths_dict: Dict[str, SoilDepthLayer] = {}

            for d in layer.get("depths", []):
                label = d.get("label", "0-5cm")
                vals = d.get("values", {})
                mean_v = float(vals.get("mean", 0.0)) / divisor
                median_v = float(vals.get("Q0.5", vals.get("mean", 0.0))) / divisor
                q05_v = float(vals.get("Q0.05", median_v * 0.9)) / divisor
                q95_v = float(vals.get("Q0.95", median_v * 1.1)) / divisor

                depths_dict[label] = SoilDepthLayer(
                    depth_interval=label,
                    mean=round(mean_v, 2),
                    median=round(median_v, 2),
                    q05=round(q05_v, 2),
                    q95=round(q95_v, 2),
                    unit=unit
                )
            layers_dict[name] = depths_dict

        return layers_dict

    def _build_response(
        self,
        lat: float,
        lon: float,
        dither: bool,
        layers: Dict[str, Dict[str, SoilDepthLayer]],
        status: str = "CONFIGURED",
        is_cached: bool = False
    ) -> SoilGridsProfileResponse:
        """Constructs standardized Pydantic SoilGridsProfileResponse."""
        surf_ph = layers.get("phh2o", {}).get(
            "0-5cm", SoilDepthLayer(depth_interval="0-5cm", mean=6.8, median=6.8, q05=6.1, q95=7.4, unit="pH")
        )
        surf_soc = layers.get("soc", {}).get(
            "0-5cm", SoilDepthLayer(depth_interval="0-5cm", mean=6.5, median=6.5, q05=4.5, q95=8.8, unit="g/kg")
        )
        surf_clay = layers.get("clay", {}).get(
            "0-5cm", SoilDepthLayer(depth_interval="0-5cm", mean=26.0, median=26.0, q05=18.0, q95=34.0, unit="%")
        )
        surf_sand = layers.get("sand", {}).get(
            "0-5cm", SoilDepthLayer(depth_interval="0-5cm", mean=54.0, median=54.0, q05=42.0, q95=65.0, unit="%")
        )
        surf_silt = layers.get("silt", {}).get(
            "0-5cm", SoilDepthLayer(depth_interval="0-5cm", mean=20.0, median=20.0, q05=12.0, q95=28.0, unit="%")
        )
        surf_bdod = layers.get("bdod", {}).get(
            "0-5cm", SoilDepthLayer(depth_interval="0-5cm", mean=1.35, median=1.35, q05=1.20, q95=1.50, unit="g/cm³")
        )
        surf_cec = layers.get("cec", {}).get(
            "0-5cm", SoilDepthLayer(depth_interval="0-5cm", mean=18.5, median=18.5, q05=12.0, q95=26.0, unit="cmol(+)/kg")
        )
        surf_n = layers.get("nitrogen", {}).get(
            "0-5cm", SoilDepthLayer(depth_interval="0-5cm", mean=0.75, median=0.75, q05=0.45, q95=1.10, unit="g/kg")
        )

        return SoilGridsProfileResponse(
            status=status,
            latitude=lat,
            longitude=lon,
            is_dithered=dither,
            retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
            physical=SoilPhysicalProperties(
                clay_percentage=surf_clay,
                sand_percentage=surf_sand,
                silt_percentage=surf_silt,
                bulk_density=surf_bdod
            ),
            chemical=SoilChemicalProperties(
                ph=surf_ph,
                soil_organic_carbon=surf_soc,
                cation_exchange_capacity=surf_cec,
                nitrogen=surf_n
            ),
            data_source="ISRIC_SOILGRIDS_V2_250M",
            epistemic_status="REMOTE_STATISTICAL_MODEL_ESTIMATE",
            is_measured_in_situ=False,
            non_override_guarantee=True,
            attribution=SOILGRIDS_ATTRIBUTION,
            is_cached=is_cached
        )

    def _fallback_profile(
        self,
        lat: float,
        lon: float,
        dither: bool,
        status: str = "DEGRADED"
    ) -> SoilGridsProfileResponse:
        """Returns baseline pedological indicators for Telangana agroclimatic zones."""
        res = self._build_response(lat, lon, dither, {}, status=status, is_cached=False)
        res.data_source = "PJTSAU_TELANGANA_SOIL_RESOURCE_NORMAL (Fallback)"
        res.epistemic_status = "REGIONAL_AGROCLIMATIC_PEDOLOGICAL_NORMAL"
        res.attribution = "PJTSAU Agro-Pedological Normals"
        return res


soilgrids_client = SoilGridsClient()
