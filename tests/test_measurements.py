from shapely.geometry import Polygon, LineString, Point
from app.services.measurement_service import calculate_measurements

def test_polygon_area():
    # A 10x10 square
    poly = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    res = calculate_measurements(poly)
    assert res["status"] == "SUCCESS"
    assert res["measurements"]["area_sq_meters"] == 100
    assert res["measurements"]["area_hectares"] == 100 / 10000.0

def test_linestring_length():
    # A line of length 15
    line = LineString([(0, 0), (15, 0)])
    res = calculate_measurements(line)
    assert res["status"] == "SUCCESS"
    assert res["measurements"]["length_meters"] == 15
    assert res["measurements"]["length_kilometers"] == 15 / 1000.0

def test_point_not_applicable():
    point = Point(0, 0)
    res = calculate_measurements(point)
    assert res["status"] == "NOT_APPLICABLE"
