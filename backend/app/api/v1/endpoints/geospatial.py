"""
ACREVIA - Geospatial & Farm Boundary REST API (Pillar A: Acrevia Geo).
"""

from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.geospatial import (
    GeoPolygonInput,
    PlotGeometryResponse,
    LocationPermissionUpdate,
    LocationPermissionResponse,
    NearbyPlotItem,
    CentroidCoord
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.geo_service import GeoSpatialService

router = APIRouter(prefix="/geospatial", tags=["Acrevia Geo"])


@router.post("/plots/{plot_id}/geometry", response_model=PlotGeometryResponse, status_code=status.HTTP_201_CREATED)
def save_plot_geometry(
    plot_id: str,
    payload: GeoPolygonInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validates and persists GeoJSON boundary polygon for a cultivation plot."""
    geom = GeoSpatialService.save_plot_geometry(
        db=db,
        plot_id=plot_id,
        coordinates=payload.coordinates
    )
    return PlotGeometryResponse(
        id=geom.id,
        plot_id=geom.plot_id,
        geometry_type=geom.geometry_type,
        centroid=CentroidCoord(latitude=geom.centroid_lat, longitude=geom.centroid_lon),
        calculated_area_hectares=geom.calculated_area_hectares,
        calculated_area_acres=geom.calculated_area_acres,
        bbox=[geom.bbox_min_lon, geom.bbox_min_lat, geom.bbox_max_lon, geom.bbox_max_lat],
        is_valid=True,
        properties=geom.properties_json
    )


@router.get("/plots/{plot_id}/geometry", response_model=PlotGeometryResponse)
def get_plot_geometry(
    plot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves plot geometry, centroid, and calculated acreage."""
    geom = GeoSpatialService.get_plot_geometry(db=db, plot_id=plot_id, user_id=current_user.id)
    return PlotGeometryResponse(
        id=geom.id,
        plot_id=geom.plot_id,
        geometry_type=geom.geometry_type,
        centroid=CentroidCoord(latitude=geom.centroid_lat, longitude=geom.centroid_lon),
        calculated_area_hectares=geom.calculated_area_hectares,
        calculated_area_acres=geom.calculated_area_acres,
        bbox=[geom.bbox_min_lon, geom.bbox_min_lat, geom.bbox_max_lon, geom.bbox_max_lat],
        is_valid=True,
        properties=geom.properties_json
    )


@router.post("/farms/{farm_id}/permissions", response_model=LocationPermissionResponse)
def set_location_permission(
    farm_id: str,
    payload: LocationPermissionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates location privacy tier (EXACT_BOUNDARY, COARSE_VILLAGE, REVOKED)."""
    perm = GeoSpatialService.update_location_permission(
        db=db,
        farm_id=farm_id,
        user_id=current_user.id,
        granularity=payload.granularity,
        notes=payload.notes
    )
    return perm


@router.get("/plots/nearby", response_model=List[NearbyPlotItem])
def find_nearby_plots(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    radius_km: float = Query(10.0, gt=0.0, le=100.0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Queries cultivation plots within proximity radius using haversine distance."""
    return GeoSpatialService.find_nearby_plots(
        db=db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km
    )
