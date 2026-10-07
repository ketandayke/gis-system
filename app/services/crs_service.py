import math
from typing import Tuple, Optional
from pyproj import CRS, Transformer
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform
from app.core.logging import logger

def get_utm_epsg(longitude: float, latitude: float) -> int:
    """
    Calculate the EPSG code for the appropriate UTM zone based on longitude and latitude.
    """
    zone = math.floor((longitude + 180) / 6) + 1
    if latitude >= 0:
        return 32600 + zone
    else:
        return 32700 + zone

def is_geographic(crs_str: str) -> bool:
    """
    Check if a given CRS is geographic (uses degrees, e.g., EPSG:4326).
    """
    try:
        crs = CRS.from_user_input(crs_str)
        return crs.is_geographic
    except Exception as e:
        logger.warning(f"Could not parse CRS {crs_str}: {e}")
        return False

def transform_geometry(geometry: BaseGeometry, source_crs: str) -> Tuple[BaseGeometry, str]:
    """
    Transform geometry to a suitable projected CRS if it is geographic.
    Returns a tuple of (transformed_geometry, target_crs_str).
    """
    if not geometry or geometry.is_empty:
        return geometry, source_crs

    if not source_crs:
        # Fallback to WGS84 if none specified
        source_crs = "EPSG:4326"

    try:
        source = CRS.from_user_input(source_crs)
    except Exception as e:
        logger.warning(f"Invalid source CRS {source_crs}, defaulting to EPSG:4326. Error: {e}")
        source_crs = "EPSG:4326"
        source = CRS.from_user_input(source_crs)

    if not source.is_geographic:
        # Already projected
        return geometry, source_crs

    # Find a suitable UTM projection based on the centroid
    centroid = geometry.centroid
    longitude, latitude = centroid.x, centroid.y
    
    target_epsg = get_utm_epsg(longitude, latitude)
    target_crs = f"EPSG:{target_epsg}"
    
    try:
        target = CRS.from_user_input(target_crs)
        transformer = Transformer.from_crs(source, target, always_xy=True)
        projected_geom = transform(transformer.transform, geometry)
        return projected_geom, target_crs
    except Exception as e:
        logger.error(f"Failed to transform geometry from {source_crs} to {target_crs}: {e}")
        return geometry, source_crs
