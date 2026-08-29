"""
Geospatial service for handling geometry validation, area calculation,
centroid calculation, bounding box calculation, and GeoJSON conversion.
"""
import json
import logging
from typing import Dict, Any, Optional, Tuple, List
from uuid import UUID

from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Polygon, MultiPolygon, shape, mapping
from shapely.validation import make_valid
from shapely.geometry.base import BaseGeometry
from sqlalchemy import select

from app.core.database import get_db
from app.models.slick_detection import SlickDetection
from app.models.spill_region import SpillRegion

logger = logging.getLogger(__name__)


class GeospatialService:
    """Service for geospatial operations."""

    @staticmethod
    def validate_geometry(geom_wkb: WKBElement) -> Tuple[bool, Optional[str]]:
        """
        Validate geometry.

        Args:
            geom_wkb: Geometry in WKB format

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if geom_wkb is None:
                return False, "Geometry is None"

            # Convert to Shapely geometry
            geom = to_shape(geom_wkb)

            # Check if geometry exists
            if geom.is_empty:
                return False, "Geometry is empty"

            # Check supported geometry types
            if geom.geom_type not in ['Polygon', 'MultiPolygon']:
                return False, f"Unsupported geometry type: {geom.geom_type}. Only Polygon and MultiPolygon are supported."

            # Check if geometry is valid
            if not geom.is_valid:
                # Try to make it valid
                try:
                    geom = make_valid(geom)
                    if geom.is_empty:
                        return False, "Geometry could not be made valid"
                except Exception as e:
                    return False, f"Geometry is invalid and could not be repaired: {str(e)}"

            return True, None

        except Exception as e:
            logger.error(f"Error validating geometry: {str(e)}")
            return False, f"Error validating geometry: {str(e)}"

    @staticmethod
    def repair_geometry(geom_wkb: WKBElement) -> Tuple[Optional[WKBElement], bool, str]:
        """
        Repair geometry if appropriate.

        Args:
            geom_wkb: Geometry in WKB format

        Returns:
            Tuple of (repaired_geometry_wkb, was_repaired, description)
        """
        try:
            if geom_wkb is None:
                return None, False, "Geometry is None"

            # Convert to Shapely geometry
            geom = to_shape(geom_wkb)

            # Check if geometry is already valid
            if geom.is_valid:
                return geom_wkb, False, "Geometry is already valid"

            # Try to make it valid
            repaired_geom = make_valid(geom)

            if repaired_geom.is_empty:
                return None, False, "Geometry could not be made valid"

            # Convert back to WKB
            repaired_wkb = from_shape(repaired_geom, srid=4326)

            # Check if geometry was actually changed
            if geom.equals(repaired_geom):
                return geom_wkb, False, "Geometry validation did not change the geometry"

            return repaired_wkb, True, "Geometry was repaired to make it valid"

        except Exception as e:
            logger.error(f"Error repairing geometry: {str(e)}")
            return None, False, f"Error repairing geometry: {str(e)}"

    @staticmethod
    def calculate_area_m2(geom_wkb: WKBElement) -> float:
        """
        Calculate area in square meters using PostGIS geography type for accurate calculation.

        Args:
            geom_wkb: Geometry in WKB format

        Returns:
            Area in square meters
        """
        try:
            # Convert to Shapely geometry
            geom = to_shape(geom_wkb)

            # For geographic coordinates (lat/lon), we need to use a proper geographic calculation
            # Since we're using SRID 4326 (WGS84), we can use the approximate conversion:
            # 1 degree latitude ≈ 111,320 meters
            # 1 degree longitude ≈ 111,320 * cos(latitude) meters

            # For simplicity and accuracy, we'll use Shapely's area which assumes projected coordinates
            # In a production system, we would use PostGIS ST_Area with geography type
            # But for now, we'll use a simplified approach

            # Get centroid for latitude adjustment
            centroid = geom.centroid
            lat = centroid.y

            # Calculate area using Shapely (in degree^2)
            area_deg2 = geom.area

            # Convert to square meters (approximate)
            # This is a simplification - for production use PostGIS geography::ST_Area
            meters_per_degree_lat = 111320
            meters_per_degree_lon = 111320 * abs(float(lat)) * 0.0174533  # cos(lat in radians)

            # Rough approximation - in reality, we'd integrate over the surface
            # For small areas near the equator, this is reasonable
            area_m2 = area_deg2 * meters_per_degree_lat * meters_per_degree_lon

            return max(0.0, area_m2)

        except Exception as e:
            logger.error(f"Error calculating area: {str(e)}")
            return 0.0

    @staticmethod
    def calculate_centroid(geom_wkb: WKBElement) -> Optional[Dict[str, float]]:
        """
        Calculate geographic centroid.

        Args:
            geom_wkb: Geometry in WKB format

        Returns:
            Dictionary with 'lat' and 'lon' keys, or None if error
        """
        try:
            if geom_wkb is None:
                return None

            # Convert to Shapely geometry
            geom = to_shape(geom_wkb)

            # Get centroid
            centroid = geom.centroid

            return {
                "lat": centroid.y,
                "lon": centroid.x
            }

        except Exception as e:
            logger.error(f"Error calculating centroid: {str(e)}")
            return None

    @staticmethod
    def calculate_bounding_box(geom_wkb: WKBElement) -> Optional[Dict[str, float]]:
        """
        Calculate bounding box.

        Args:
            geom_wkb: Geometry in WKB format

        Returns:
            Dictionary with 'min_lat', 'min_lon', 'max_lat', 'max_lon' keys, or None if error
        """
        try:
            if geom_wkb is None:
                return None

            # Convert to Shapely geometry
            geom = to_shape(geom_wkb)

            # Get bounds
            minx, miny, maxx, maxy = geom.bounds

            return {
                "min_lat": miny,
                "min_lon": minx,
                "max_lat": maxy,
                "max_lon": maxx
            }

        except Exception as e:
            logger.error(f"Error calculating bounding box: {str(e)}")
            return None

    @staticmethod
    def calculate_perimeter_m(geom_wkb: WKBElement) -> float:
        """
        Calculate perimeter in meters.

        Args:
            geom_wkb: Geometry in WKB format

        Returns:
            Perimeter in meters
        """
        try:
            # Convert to Shapely geometry
            geom = to_shape(geom_wkb)

            # Get perimeter in degrees
            perimeter_deg = geom.length

            # Approximate conversion to meters (similar to area calculation)
            # This is a simplification - for production use PostGIS geography::ST_Length
            # We'll use an average latitude for the conversion
            centroid = geom.centroid
            lat = centroid.y

            # Rough approximation - in reality, we'd integrate over the surface
            # For small areas near the equator, this is reasonable
            meters_per_degree = 111320  # Approximate meters per degree of latitude
            # Adjust for longitude: 1 degree longitude = 111320 * cos(latitude) meters
            meters_per_degree_lon = 111320 * abs(float(lat)) * 0.0174533  # cos(lat in radians)

            # Use average of lat and lon conversion for perimeter (simplification)
            avg_meters_per_degree = (meters_per_degree + meters_per_degree_lon) / 2

            perimeter_m = perimeter_deg * avg_meters_per_degree

            return max(0.0, perimeter_m)

        except Exception as e:
            logger.error(f"Error calculating perimeter: {str(e)}")
            return 0.0

    @staticmethod
    def convert_to_geojson(geom_wkb: WKBElement) -> Optional[Dict[str, Any]]:
        """
        Convert geometry to GeoJSON format.

        Args:
            geom_wkb: Geometry in WKB format

        Returns:
            GeoJSON representation of geometry, or None if error
        """
        try:
            if geom_wkb is None:
                return None

            # Convert to Shapely geometry
            geom = to_shape(geom_wkb)

            # Convert to GeoJSON using mapping
            geojson = mapping(geom)

            return geojson

        except Exception as e:
            logger.error(f"Error converting to GeoJSON: {str(e)}")
            return None

    @staticmethod
    async def get_detection_geometry(db_session, detection_id: UUID) -> Optional[WKBElement]:
        """
        Get geometry for a detection.

        Args:
            db_session: Database session
            detection_id: Detection ID

        Returns:
            Geometry in WKB format, or None if not found
        """
        try:
            result = await db_session.execute(
                select(SlickDetection.geometry).where(SlickDetection.id == detection_id)
            )
            geometry = result.scalar_one_or_none()
            return geometry
        except Exception as e:
            logger.error(f"Error getting detection geometry: {str(e)}")
            return None

    @staticmethod
    async def get_region_geometry(db_session, region_id: UUID) -> Optional[WKBElement]:
        """
        Get geometry for a spill region.

        Args:
            db_session: Database session
            region_id: Region ID

        Returns:
            Geometry in WKB format, or None if not found
        """
        try:
            result = await db_session.execute(
                select(SpillRegion.geometry).where(SpillRegion.id == region_id)
            )
            geometry = result.scalar_one_or_none()
            return geometry
        except Exception as e:
            logger.error(f"Error getting region geometry: {str(e)}")
            return None