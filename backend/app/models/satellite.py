"""
ACREVIA - Satellite Intelligence & Remote Sensing Models (Pillar B: Acrevia Earth).
Stores scene acquisitions, plot-level zonal vegetation indices (NDVI, EVI, NDMI),
and mandatory non-disease evidence disclaimers.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin

SATELLITE_EVIDENCE_DISCLAIMER = (
    "Satellite observations reflect broad canopy vigor and surface moisture; "
    "they do not diagnose specific plant diseases or pathogens."
)


class SatelliteSource(Base, TimestampMixin):
    __tablename__ = "satellite_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # SENTINEL_2, LANDSAT_9
    constellation: Mapped[str] = mapped_column(String(100), nullable=False)
    spatial_resolution_meters: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    acquisitions: Mapped[List["SatelliteAcquisition"]] = relationship("SatelliteAcquisition", back_populates="source")


class SatelliteAcquisition(Base, TimestampMixin):
    __tablename__ = "satellite_acquisitions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("satellite_sources.id"), index=True, nullable=False)
    scene_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    acquisition_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    cloud_coverage_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    raw_metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)

    # Relationships
    source: Mapped["SatelliteSource"] = relationship("SatelliteSource", back_populates="acquisitions")
    observations: Mapped[List["SatelliteObservation"]] = relationship("SatelliteObservation", back_populates="acquisition")


class SatelliteObservation(Base, TimestampMixin):
    __tablename__ = "satellite_observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    acquisition_id: Mapped[str] = mapped_column(String(36), ForeignKey("satellite_acquisitions.id", ondelete="CASCADE"), index=True, nullable=False)
    observation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    
    mean_ndvi: Mapped[float] = mapped_column(Float, nullable=False)
    min_ndvi: Mapped[float] = mapped_column(Float, nullable=False)
    max_ndvi: Mapped[float] = mapped_column(Float, nullable=False)
    std_ndvi: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    mean_evi: Mapped[float] = mapped_column(Float, nullable=False)
    mean_ndmi: Mapped[float] = mapped_column(Float, nullable=False)
    
    cloud_masked_pixel_ratio: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    trend_classification: Mapped[str] = mapped_column(String(50), default="STABLE", nullable=False)  # VIGOR_INCREASING, STABLE, DECLINING_STRESS, HARVEST_CLEARING
    
    evidence_disclaimer: Mapped[str] = mapped_column(Text, default=SATELLITE_EVIDENCE_DISCLAIMER, nullable=False)
    properties_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot")
    acquisition: Mapped["SatelliteAcquisition"] = relationship("SatelliteAcquisition", back_populates="observations")

    __table_args__ = (
        Index("ix_sat_obs_plot_date", "plot_id", "observation_date"),
    )
