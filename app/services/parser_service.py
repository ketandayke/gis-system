import fiona
import geopandas as gpd
from typing import List, Dict, Any

# Enable KML driver for Fiona
fiona.drvsupport.supported_drivers['KML'] = 'rw'
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'

class GISParserError(Exception):
    pass

import pandas as pd

def parse_file(file_path: str, file_type: str) -> Dict[str, Any]:
    """
    Parses a geospatial file (KML or Shapefile) and extracts features.
    Returns a dictionary with summary and feature list.
    """
    try:
        if file_type == "kml":
            gdf = gpd.read_file(file_path, driver='KML')
        elif file_type == "shapefile":
            gdf = gpd.read_file(file_path)
        else:
            raise GISParserError(f"Unsupported file type for parsing: {file_type}")
            
    except Exception as e:
        raise GISParserError(f"Failed to parse geospatial data: {e}")
        
    native_crs = str(gdf.crs) if gdf.crs else None
    
    features = []
    
    for idx, row in gdf.iterrows():
        geometry = row.geometry
        if geometry is None:
            continue
            
        geom_type = geometry.geom_type
        
        # Exclude geometry from properties
        properties = {col: row[col] for col in gdf.columns if col != 'geometry'}
        # Replace non-serializable items or NaNs
        for k, v in properties.items():
            if pd.isna(v):
                properties[k] = None
            elif type(v).__name__ == 'Timestamp':
                properties[k] = v.isoformat()
                
        features.append({
            "feature_index": idx,
            "geometry_type": geom_type,
            "geometry": geometry,
            "properties": properties
        })
        
    return {
        "feature_count": len(features),
        "native_crs": native_crs,
        "features": features
    }
