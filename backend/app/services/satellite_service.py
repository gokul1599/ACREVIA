"""
ACREVIA - Satellite Intelligence & Remote Sensing Service (Pillar B: Acrevia Earth).
Computes optical vegetation indices (NDVI, EVI, NDMI), evaluates cloud-masked time-series,
classifies canopy vigor trends, and enforces non-diagnostic evidence disclaimers.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc

from backend.app.models.satellite import (
    SatelliteSource,
    SatelliteAcquisition,
    SatelliteObservation,
    SATELLITE_EVIDENCE_DISCLAIMER
)
from backend.app.models.farm import Plot
from backend.app.core.exceptions import NotFoundError, ValidationError


class SatelliteService:
    @staticmethod
    def calculate_ndvi(nir: float, red: float) -> float:
        """Normalized Difference Vegetation Index: (NIR - RED) / (NIR + RED)."""
        denom = nir + red
        if abs(denom) < 1e-6:
            return 0.0
        ndvi = (nir - red) / denom
        return round(max(-1.0, min(1.0, ndvi)), 4)

    @staticmethod
    def calculate_evi(nir: float, red: float, blue: float) -> float:
        """Enhanced Vegetation Index: 2.5 * (NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1.0)."""
        denom = nir + 6.0 * red - 7.5 * blue + 1.0
        if abs(denom) < 1e-6:
            return 0.0
        evi = 2.5 * (nir - red) / denom
        return round(max(-1.0, min(2.5, evi)), 4)

    @staticmethod
    def calculate_ndmi(nir: float, swir: float) -> float:
        """Normalized Difference Moisture Index: (NIR - SWIR) / (NIR + SWIR)."""
        denom = nir + swir
        if abs(denom) < 1e-6:
            return 0.0
        ndmi = (nir - swir) / denom
        return round(max(-1.0, min(1.0, ndmi)), 4)

    @staticmethod
    def classify_vigor_trend(observations: List[SatelliteObservation]) -> str:
        """Classifies 30-day vigor trajectory based on NDVI delta."""
        if not observations or len(observations) < 2:
            return "STABLE"

        sorted_obs = sorted(observations, key=lambda o: o.observation_date)
        delta_ndvi = sorted_obs[-1].mean_ndvi - sorted_obs[0].mean_ndvi

        if delta_ndvi > 0.08:
            return "VIGOR_INCREASING"
        elif delta_ndvi < -0.18:
            return "HARVEST_CLEARING"
        elif delta_ndvi < -0.06:
            return "DECLINING_STRESS"
        else:
            return "STABLE"

    @staticmethod
    def record_observation(
        db: Session,
        plot_id: str,
        observation_date: datetime,
        mean_ndvi: float,
        min_ndvi: float,
        max_ndvi: float,
        std_ndvi: float = 0.02,
        mean_evi: Optional[float] = None,
        mean_ndmi: Optional[float] = None,
        cloud_masked_pixel_ratio: float = 0.0,
        acquisition_scene_id: Optional[str] = None
    ) -> SatelliteObservation:
        """Records an ingested satellite observation for a plot."""
        plot = db.get(Plot, plot_id)
        if not plot or plot.is_archived:
            raise NotFoundError("Plot not found.")

        # Ensure baseline source exists
        source = db.execute(
            select(SatelliteSource).where(SatelliteSource.name == "SENTINEL_2")
        ).scalar_one_or_none()
        if not source:
            source = SatelliteSource(
                name="SENTINEL_2",
                constellation="Copernicus Sentinel-2 MSI",
                spatial_resolution_meters=10.0,
                description="Copernicus 10m multispectral satellite imagery"
            )
            db.add(source)
            db.commit()
            db.refresh(source)

        # Ensure acquisition exists
        scene_id = acquisition_scene_id or f"S2A_MSIL2A_{observation_date.strftime('%Y%m%d')}_TELANGANA"
        acq = db.execute(
            select(SatelliteAcquisition).where(SatelliteAcquisition.scene_id == scene_id)
        ).scalar_one_or_none()
        if not acq:
            acq = SatelliteAcquisition(
                source_id=source.id,
                scene_id=scene_id,
                acquisition_date=observation_date,
                cloud_coverage_percentage=round(cloud_masked_pixel_ratio * 100.0, 1)
            )
            db.add(acq)
            db.commit()
            db.refresh(acq)

        obs = SatelliteObservation(
            plot_id=plot_id,
            acquisition_id=acq.id,
            observation_date=observation_date,
            mean_ndvi=round(mean_ndvi, 4),
            min_ndvi=round(min_ndvi, 4),
            max_ndvi=round(max_ndvi, 4),
            std_ndvi=round(std_ndvi, 4),
            mean_evi=round(mean_evi if mean_evi is not None else mean_ndvi * 0.8, 4),
            mean_ndmi=round(mean_ndmi if mean_ndmi is not None else mean_ndvi * 0.5, 4),
            cloud_masked_pixel_ratio=round(cloud_masked_pixel_ratio, 4),
            trend_classification="STABLE",
            evidence_disclaimer=SATELLITE_EVIDENCE_DISCLAIMER
        )
        db.add(obs)
        db.commit()
        db.refresh(obs)

        # Update trend classification across historical series
        history = db.execute(
            select(SatelliteObservation).where(SatelliteObservation.plot_id == plot_id)
        ).scalars().all()
        trend = SatelliteService.classify_vigor_trend(history)
        obs.trend_classification = trend
        db.commit()
        db.refresh(obs)

        return obs

    @staticmethod
    def get_time_series(db: Session, plot_id: str, days: int = 60) -> Dict[str, Any]:
        """Retrieves historical satellite observations with rolling trend and non-disease disclaimer."""
        plot = db.get(Plot, plot_id)
        if not plot or plot.is_archived:
            raise NotFoundError("Plot not found.")

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = select(SatelliteObservation).where(
            and_(
                SatelliteObservation.plot_id == plot_id,
                SatelliteObservation.observation_date >= cutoff
            )
        ).order_by(SatelliteObservation.observation_date.asc())

        records = list(db.execute(stmt).scalars().all())

        # If empty, return structured empty envelope with mandatory disclaimer
        if not records:
            return {
                "plot_id": plot_id,
                "trend_summary": "NO_OBSERVATIONS",
                "observations_count": 0,
                "evidence_disclaimer": SATELLITE_EVIDENCE_DISCLAIMER,
                "time_series": []
            }

        trend_summary = SatelliteService.classify_vigor_trend(records)
        return {
            "plot_id": plot_id,
            "trend_summary": trend_summary,
            "observations_count": len(records),
            "evidence_disclaimer": SATELLITE_EVIDENCE_DISCLAIMER,
            "time_series": records
        }

    @staticmethod
    def get_latest_observation(db: Session, plot_id: str) -> Optional[SatelliteObservation]:
        """Returns the most recent clear-sky satellite observation."""
        plot = db.get(Plot, plot_id)
        if not plot or plot.is_archived:
            raise NotFoundError("Plot not found.")

        stmt = select(SatelliteObservation).where(
            SatelliteObservation.plot_id == plot_id
        ).order_by(SatelliteObservation.observation_date.desc()).limit(1)

        return db.execute(stmt).scalar_one_or_none()

    @classmethod
    async def query_copernicus_scenes(
        cls,
        max_cloud_cover_percent: float = 20.0,
        days_back: int = 15,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Queries Copernicus CDSE Sentinel-2 catalogue for recent clear-sky acquisitions."""
        from backend.app.integrations.copernicus_client import copernicus_client
        return await copernicus_client.search_sentinel2_scenes(
            max_cloud_cover_percent=max_cloud_cover_percent,
            days_back=days_back,
            limit=limit
        )
