"""
ACREVIA - Geospatial & Farm Boundary Service (Pillar A: Acrevia Geo).
Handles WGS84 polygon validation, area computation (Shoelace geodesic),
bounding box indexing, proximity search, and privacy-aware location permissions.
"""

import json
import math
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from backend.app.models.geo_spatial import PlotGeometry, LocationPermission
from backend.app.models.farm import Plot, Farm
from backend.app.core.exceptions import ValidationError, NotFoundError, PermissionDeniedError

EARTH_RADIUS_METERS = 6371008.8  # Mean Earth radius in meters
EARTH_RADIUS_KM = 6371.0


class GeoSpatialService:
    @staticmethod
    def validate_polygon_coordinates(coords: List[List[float]]) -> None:
        """Validates a linear ring of [longitude, latitude] coordinates."""
        if not coords or len(coords) < 4:
            raise ValidationError("Polygon ring must contain at least 4 coordinate pairs (triangle + closed point).")

        # Check closure
        if coords[0] != coords[-1]:
            raise ValidationError(
                f"Polygon ring is not closed: first coordinate {coords[0]} != last coordinate {coords[-1]}"
            )

        # Coordinate ranges
        for i, pt in enumerate(coords):
            if len(pt) < 2:
                raise ValidationError(f"Invalid coordinate at index {i}: must have [longitude, latitude]")
            lon, lat = pt[0], pt[1]
            if not (-180.0 <= lon <= 180.0):
                raise ValidationError(f"Longitude {lon} at index {i} out of valid bounds [-180, 180].")
            if not (-90.0 <= lat <= 90.0):
                raise ValidationError(f"Latitude {lat} at index {i} out of valid bounds [-90, 90].")

        # Planar self-intersection test
        GeoSpatialService._check_self_intersection(coords)

    @staticmethod
    def _check_self_intersection(coords: List[List[float]]) -> None:
        """Checks if any non-adjacent line segments intersect."""
        n = len(coords) - 1  # Number of segments
        for i in range(n):
            p1, p2 = coords[i], coords[i + 1]
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue  # First and last segments meet at vertex 0
                p3, p4 = coords[j], coords[j + 1]
                if GeoSpatialService._segments_intersect(p1, p2, p3, p4):
                    raise ValidationError(f"Polygon self-intersects between segments {i} and {j}.")

    @staticmethod
    def _segments_intersect(p1: List[float], p2: List[float], p3: List[float], p4: List[float]) -> bool:
        """Checks if segment p1-p2 intersects segment p3-p4 using cross products."""
        def ccw(a, b, c):
            return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

        return (ccw(p1, p3, p4) != ccw(p2, p3, p4)) and (ccw(p1, p2, p3) != ccw(p1, p2, p4))

    @staticmethod
    def calculate_centroid(coords: List[List[float]]) -> Tuple[float, float]:
        """Calculates arithmetic centroid (latitude, longitude) of the ring."""
        # Exclude the duplicated last point for the mean
        pts = coords[:-1]
        mean_lon = sum(pt[0] for pt in pts) / len(pts)
        mean_lat = sum(pt[1] for pt in pts) / len(pts)
        return round(mean_lat, 6), round(mean_lon, 6)

    @staticmethod
    def calculate_bounding_box(coords: List[List[float]]) -> Tuple[float, float, float, float]:
        """Returns (min_lon, min_lat, max_lon, max_lat)."""
        lons = [pt[0] for pt in coords]
        lats = [pt[1] for pt in coords]
        return min(lons), min(lats), max(lons), max(lats)

    @staticmethod
    def calculate_spherical_area_hectares(coords: List[List[float]]) -> Tuple[float, float]:
        """
        Calculates surface area in hectares and acres using spherical polygon formula.
        Returns: (hectares, acres)
        """
        if len(coords) < 4:
            return 0.0, 0.0

        area_sq_meters = 0.0
        n = len(coords) - 1

        for i in range(n):
            p1 = coords[i]
            p2 = coords[i + 1]
            lon1, lat1 = math.radians(p1[0]), math.radians(p1[1])
            lon2, lat2 = math.radians(p2[0]), math.radians(p2[1])
            area_sq_meters += (lon2 - lon1) * (2.0 + math.sin(lat1) + math.sin(lat2))

        area_sq_meters = abs(area_sq_meters * (EARTH_RADIUS_METERS ** 2) / 2.0)
        hectares = area_sq_meters / 10000.0
        acres = hectares * 2.47105

        return round(hectares, 4), round(acres, 4)

    @staticmethod
    def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Computes Great Circle distance between two coordinates in kilometers."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(EARTH_RADIUS_KM * c, 3)

    @staticmethod
    def save_plot_geometry(
        db: Session,
        plot_id: str,
        coordinates: List[List[List[float]]],
        properties: Optional[Dict[str, Any]] = None
    ) -> PlotGeometry:
        """Validates and persists GeoJSON polygon for a plot."""
        plot = db.get(Plot, plot_id)
        if not plot or plot.is_archived:
            raise NotFoundError("Plot not found.")

        if not coordinates or not isinstance(coordinates, list):
            raise ValidationError("Invalid coordinates format: must be list of coordinate rings.")

        outer_ring = coordinates[0]
        GeoSpatialService.validate_polygon_coordinates(outer_ring)

        centroid_lat, centroid_lon = GeoSpatialService.calculate_centroid(outer_ring)
        min_lon, min_lat, max_lon, max_lat = GeoSpatialService.calculate_bounding_box(outer_ring)
        hectares, acres = GeoSpatialService.calculate_spherical_area_hectares(outer_ring)

        if hectares < 0.01:
            raise ValidationError(f"Calculated plot area ({hectares:.4f} ha) is below minimum threshold (0.01 ha).")
        if hectares > 1000.0:
            raise ValidationError(f"Calculated plot area ({hectares:.4f} ha) exceeds maximum realistic farm boundary (1000 ha).")

        existing_geom = db.execute(
            select(PlotGeometry).where(PlotGeometry.plot_id == plot_id)
        ).scalar_one_or_none()

        coords_str = json.dumps(coordinates)

        if existing_geom:
            existing_geom.coordinates_geojson = coords_str
            existing_geom.centroid_lat = centroid_lat
            existing_geom.centroid_lon = centroid_lon
            existing_geom.calculated_area_hectares = hectares
            existing_geom.calculated_area_acres = acres
            existing_geom.bbox_min_lon = min_lon
            existing_geom.bbox_min_lat = min_lat
            existing_geom.bbox_max_lon = max_lon
            existing_geom.bbox_max_lat = max_lat
            existing_geom.properties_json = properties or {}
            geom = existing_geom
        else:
            geom = PlotGeometry(
                plot_id=plot_id,
                geometry_type="Polygon",
                coordinates_geojson=coords_str,
                centroid_lat=centroid_lat,
                centroid_lon=centroid_lon,
                calculated_area_hectares=hectares,
                calculated_area_acres=acres,
                bbox_min_lon=min_lon,
                bbox_min_lat=min_lat,
                bbox_max_lon=max_lon,
                bbox_max_lat=max_lat,
                properties_json=properties or {}
            )
            db.add(geom)

        # Update plot acreage if variance is small
        plot.boundary_geojson = coords_str
        db.commit()
        db.refresh(geom)
        return geom

    @staticmethod
    def get_plot_geometry(db: Session, plot_id: str, user_id: Optional[str] = None) -> PlotGeometry:
        """Retrieves plot geometry with location permission check."""
        plot = db.get(Plot, plot_id)
        if not plot or plot.is_archived:
            raise NotFoundError("Plot not found.")

        geom = db.execute(
            select(PlotGeometry).where(PlotGeometry.plot_id == plot_id)
        ).scalar_one_or_none()

        if not geom:
            raise NotFoundError(f"No geometry registered for plot {plot_id}.")

        # Check permission if user_id is provided
        if user_id:
            perm = db.execute(
                select(LocationPermission).where(
                    and_(
                        LocationPermission.farm_id == plot.farm_id,
                        LocationPermission.user_id == user_id,
                        LocationPermission.is_active == True
                    )
                )
            ).scalar_one_or_none()

            if perm and perm.granularity == "REVOKED":
                raise PermissionDeniedError("Location tracking permission has been revoked for this farm.")

        return geom

    @staticmethod
    def update_location_permission(
        db: Session,
        farm_id: str,
        user_id: str,
        granularity: str,
        notes: Optional[str] = None
    ) -> LocationPermission:
        """Sets or updates privacy granularity tier."""
        farm = db.get(Farm, farm_id)
        if not farm or farm.is_archived:
            raise NotFoundError("Farm not found.")

        perm = db.execute(
            select(LocationPermission).where(
                and_(
                    LocationPermission.farm_id == farm_id,
                    LocationPermission.user_id == user_id
                )
            )
        ).scalar_one_or_none()

        if perm:
            perm.granularity = granularity
            perm.is_active = (granularity != "REVOKED")
            perm.notes = notes
        else:
            perm = LocationPermission(
                farm_id=farm_id,
                user_id=user_id,
                granularity=granularity,
                is_active=(granularity != "REVOKED"),
                notes=notes
            )
            db.add(perm)

        db.commit()
        db.refresh(perm)
        return perm

    @staticmethod
    def find_nearby_plots(
        db: Session,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0
    ) -> List[Dict[str, Any]]:
        """Returns plots within radius_km using haversine distance."""
        # Simple bounding box pre-filter (~1 degree lat ~= 111 km)
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * math.cos(math.radians(latitude)))

        stmt = select(PlotGeometry, Plot).join(Plot, PlotGeometry.plot_id == Plot.id).where(
            and_(
                Plot.is_archived == False,
                PlotGeometry.centroid_lat.between(latitude - lat_delta, latitude + lat_delta),
                PlotGeometry.centroid_lon.between(longitude - lon_delta, longitude + lon_delta)
            )
        )

        results = []
        for geom, plot in db.execute(stmt).all():
            dist = GeoSpatialService.haversine_distance_km(latitude, longitude, geom.centroid_lat, geom.centroid_lon)
            if dist <= radius_km:
                results.append({
                    "plot_id": plot.id,
                    "farm_id": plot.farm_id,
                    "plot_name": plot.name,
                    "centroid_lat": geom.centroid_lat,
                    "centroid_lon": geom.centroid_lon,
                    "distance_km": dist,
                    "acreage": geom.calculated_area_acres
                })

        results.sort(key=lambda x: x["distance_km"])
        return results
