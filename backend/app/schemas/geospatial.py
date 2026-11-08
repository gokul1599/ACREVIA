"""
ACREVIA - Geospatial & Farm Boundary Pydantic Schemas.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class GeoPolygonInput(BaseModel):
    type: Literal["Polygon"] = "Polygon"
    coordinates: List[List[List[float]]] = Field(
        ...,
        description="GeoJSON polygon coordinate rings [[[lon, lat], ...]]"
    )


class CentroidCoord(BaseModel):
    latitude: float
    longitude: float


class PlotGeometryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    plot_id: str
    geometry_type: str = "Polygon"
    centroid: CentroidCoord
    calculated_area_hectares: float
    calculated_area_acres: float
    bbox: List[float] = Field(..., description="[min_lon, min_lat, max_lon, max_lat]")
    is_valid: bool = True
    properties: Optional[Dict[str, Any]] = None


class LocationPermissionUpdate(BaseModel):
    granularity: Literal["EXACT_BOUNDARY", "COARSE_VILLAGE", "REVOKED"] = "EXACT_BOUNDARY"
    notes: Optional[str] = None


class LocationPermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    farm_id: str
    user_id: str
    granularity: str
    is_active: bool
    notes: Optional[str] = None


class NearbyPlotItem(BaseModel):
    plot_id: str
    farm_id: str
    plot_name: str
    centroid_lat: float
    centroid_lon: float
    distance_km: float
    acreage: float
