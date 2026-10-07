from shapely.geometry.base import BaseGeometry
from shapely.validation import make_valid
from typing import Dict, Any, Union

def validate_geometry(geometry: BaseGeometry) -> BaseGeometry:
    """
    Validates a geometry and attempts to repair it if invalid.
    """
    if not geometry.is_valid:
        geometry = make_valid(geometry)
    return geometry

def calculate_measurements(geometry: BaseGeometry) -> Dict[str, Any]:
    """
    Calculates measurements for a given geometry.
    Assumes the geometry is already in an appropriate projected CRS (meters).
    """
    geometry = validate_geometry(geometry)
    
    geom_type = geometry.geom_type
    
    if geom_type in ["Point", "MultiPoint"]:
        return {
            "status": "NOT_APPLICABLE"
        }
        
    elif geom_type in ["Polygon", "MultiPolygon"]:
        area_sq_m = geometry.area
        return {
            "status": "SUCCESS",
            "measurements": {
                "area_sq_meters": area_sq_m,
                "area_hectares": area_sq_m / 10000.0
            }
        }
        
    elif geom_type in ["LineString", "MultiLineString"]:
        length_m = geometry.length
        return {
            "status": "SUCCESS",
            "measurements": {
                "length_meters": length_m,
                "length_kilometers": length_m / 1000.0
            }
        }
        
    return {
        "status": "NOT_APPLICABLE"
    }
