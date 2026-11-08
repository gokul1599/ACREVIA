"""
ACREVIA - Geospatial & Farm Boundary Models (Pillar A: Acrevia Geo).
Stores validated WGS84 plot geometries, calculated areas, bounding boxes, and location permissions.
"""

import uuid
from typing import Optional
from sqlalchemy import String, Float, Boolean, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class PlotGeometry(Base, TimestampMixin):
    __tablename__ = "plot_geometries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    geometry_type: Mapped[str] = mapped_column(String(30), default="Polygon", nullable=False)
    coordinates_geojson: Mapped[str] = mapped_column(Text, nullable=False)
    
    centroid_lat: Mapped[float] = mapped_column(Float, nullable=False)
    centroid_lon: Mapped[float] = mapped_column(Float, nullable=False)
    
    calculated_area_hectares: Mapped[float] = mapped_column(Float, nullable=False)
    calculated_area_acres: Mapped[float] = mapped_column(Float, nullable=False)
    
    bbox_min_lon: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_min_lat: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_max_lon: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_max_lat: Mapped[float] = mapped_column(Float, nullable=False)
    
    properties_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot")

    __table_args__ = (
        Index("ix_plot_geometries_centroid", "centroid_lat", "centroid_lon"),
        Index("ix_plot_geometries_bbox", "bbox_min_lat", "bbox_max_lat", "bbox_min_lon", "bbox_max_lon"),
    )


class LocationPermission(Base, TimestampMixin):
    __tablename__ = "location_permissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    granularity: Mapped[str] = mapped_column(String(30), default="EXACT_BOUNDARY", nullable=False)  # EXACT_BOUNDARY, COARSE_VILLAGE, REVOKED
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm")
    user: Mapped["User"] = relationship("User")

    __table_args__ = (
        Index("ix_location_permissions_farm_user", "farm_id", "user_id"),
    )
