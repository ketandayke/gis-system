import os
import zipfile
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point

os.makedirs("sample_data", exist_ok=True)
temp_dir = "sample_data/temp_shp"
os.makedirs(temp_dir, exist_ok=True)

# Define sample features in EPSG:4326 (Bengaluru, India)
data = {
    "feature_id": [1, 2, 3],
    "name": ["Parcel Boundary", "Access Road", "Reference Marker"],
    "geometry": [
        # Polygon (~300,000 m²)
        Polygon([
            (77.600, 12.980),
            (77.605, 12.980),
            (77.605, 12.985),
            (77.600, 12.985),
            (77.600, 12.980)
        ]),
        # LineString
        LineString([(77.598, 12.978), (77.602, 12.982), (77.608, 12.986)]),
        # Point
        Point(77.6025, 12.9825)
    ]
}

# Note: Standard ESRI Shapefiles enforce a single geometry type per file.
# To test multiple geometry types or a clean polygon Shapefile:
gdf_poly = gpd.GeoDataFrame(
    {"id": [101, 102], "label": ["Site Area 1", "Site Area 2"]},
    geometry=[
        Polygon([(77.600, 12.980), (77.605, 12.980), (77.605, 12.985), (77.600, 12.985)]),
        Polygon([(77.610, 12.980), (77.615, 12.980), (77.615, 12.985), (77.610, 12.985)])
    ],
    crs="EPSG:4326"
)

shp_path = os.path.join(temp_dir, "survey_parcels.shp")
gdf_poly.to_file(shp_path)

# Package into survey_parcels.zip
zip_path = "sample_data/survey_parcels.zip"
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
        file_name = f"survey_parcels{ext}"
        full_path = os.path.join(temp_dir, file_name)
        if os.path.exists(full_path):
            zipf.write(full_path, arcname=file_name)
            os.remove(full_path)

os.rmdir(temp_dir)
print(f"Created valid Shapefile archive: {zip_path}")