from app.services.crs_service import get_utm_epsg, is_geographic, transform_geometry
from shapely.geometry import Point

def test_utm_epsg():
    # NY: ~-74, 40 -> zone 18, Northern hemisphere -> 32618
    epsg = get_utm_epsg(-74, 40)
    assert epsg == 32618
    
    # Sydney: ~151, -33 -> zone 56, Southern hemisphere -> 32756
    epsg = get_utm_epsg(151, -33)
    assert epsg == 32756

def test_is_geographic():
    assert is_geographic("EPSG:4326") is True
    assert is_geographic("EPSG:32618") is False

def test_transform_geometry():
    point = Point(-74, 40)
    proj_geom, target_crs = transform_geometry(point, "EPSG:4326")
    
    assert target_crs == "EPSG:32618"
    assert proj_geom.x > 0
    assert proj_geom.y > 0
