# Geospatial File Measurement API

A production-ready REST API built with **FastAPI** that accepts geospatial vector files (KML and Zipped Shapefiles), extracts their features, safely handles coordinate reference systems (CRS), and computes accurate measurements (area for polygons, length for lines).

## 1. Problem Statement
The goal is to build an API capable of ingesting geospatial files, extracting features securely, and applying geometric calculations. Due to the planar nature of accurate geometric calculations, geographic coordinate systems (like `EPSG:4326`) must be correctly transformed into projected planar coordinate systems prior to calculation to prevent heavily distorted distance/area outcomes.

## 2. Features
- **Accepts `.kml` and `.zip` (ESRI Shapefile) files**.
- **Security-First Zip Extraction**: Prevents zip-slip path traversal and validates archive structures.
- **Robust Geospatial Validation**: Fixes invalid and self-intersecting geometries automatically using Shapely.
- **Dynamic CRS Transformation**: Identifies geographic CRS and automatically calculates the appropriate local UTM zone to project geometries into.
- **Automated Measurements**: Area for polygons/multipolygons and Length for linestrings/multilinestrings.
- **Persistent Storage**: Stores extracted features and measurements securely in a PostgreSQL database.

## 3. Architecture
The application follows a clean separation-of-concerns pattern to isolate API handling, GIS operations, and database persistence.

```
Client -> FastAPI Endpoint -> File Extractor -> GIS Parser -> CRS Service -> Measurement Service -> Database
```

## 4. Technology Choices
- **FastAPI**: Asynchronous web framework for high-performance API endpoints.
- **GeoPandas & Fiona**: Feature extraction and GIS vector data manipulation.
- **Shapely**: Fast geometry validation and geometric area/length calculations.
- **PyProj**: Mathematical CRS transformation engine.
- **PostgreSQL & SQLAlchemy 2.0**: Relational data persistence and ORM.
- **Docker & Docker Compose**: Unified, reproducible execution environment with OS-level C++ GIS dependencies baked in.

## 5. Setup & 6. Docker Usage
Local installation of GIS binaries (GDAL, GEOS) can be tricky on Windows. Docker is highly recommended to run this repository.

1. Clone the repository.
2. Run the application:
```bash
docker-compose up --build
```
This single command spins up both the FastAPI application and the PostgreSQL database. The API will be available at `http://localhost:8000`.

## 7. Local Development
To run locally without Docker:
1. Ensure GDAL and GEOS binaries are installed on your OS.
2. `python -m venv venv`
3. `venv\Scripts\activate` (Windows)
4. `pip install -r requirements.txt`
5. Have a local PostgreSQL running and copy `.env.example` to `.env` with correct credentials.
6. `uvicorn app.main:app --reload`

## 8. API Endpoints
- `GET /health/`: Health check.
- `POST /api/v1/files/`: Upload a file (Form-Data: `file`). Returns File processing summary.
- `GET /api/v1/files/{file_id}/`: Retrieves the status and feature count of an uploaded file.
- `GET /api/v1/files/{file_id}/measurements/?limit=50&offset=0`: Retrieves paginated measurements for features belonging to the file.

## 9. Example Requests/Responses

**Upload File:**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/files/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@sample_survey.kml'
```
*Response:*
```json
{
  "filename": "sample_survey.kml",
  "file_type": "kml",
  "id": "e00fb...",
  "feature_count": 3,
  "native_crs": "EPSG:4326",
  "status": "COMPLETED",
  "created_at": "2026-10-07T21:40:00"
}
```

## 10. File Processing Flow
1. Extension and size limits validated.
2. Saved to secure `/tmp/`. Extracted safely if `.zip`.
3. Processed by `GeoPandas` (yielding native geometry and properties).
4. Features mapped asynchronously.

## 11. CRS Strategy
If the native CRS is Geographic (e.g. WGS84 / `EPSG:4326` using latitude/longitude degrees), calculating square meters directly yields absurd results. 
The **CRS Service** extracts the centroid of the geometry and mathematically determines the appropriate **Universal Transverse Mercator (UTM)** zone, converting the feature to a heavily optimized local planar projection prior to calculations.

## 12. Measurement Strategy
Measurements are exclusively ran against planar projections:
- `Polygon`: Area returned in $m^2$ and Hectares.
- `LineString`: Length returned in meters and kilometers.
- `Point`: Handled gracefully as `NOT_APPLICABLE`.

## 13. Error Handling
The application returns proper HTTP Exception codes:
- `400 Bad Request` for ZipSlip attacks, missing `.shx` shapes, or oversized files.
- `404 Not Found` for missing database IDs.
- Invalid geometries (like self-intersecting bow-ties) do not throw 500s; they are cleanly repaired using Shapely's `make_valid()` algorithm without dropping the feature.

## 14. Testing
Tests cover unit operations and API endpoints. 
Run tests within the Docker container:
```bash
docker-compose exec api pytest tests/
```

## 15. Design Decisions/Trade-offs
- Processed files sequentially in a single API loop rather than async Celery queues. This reduces architecture complexity for a V1 while keeping the service boundaries clean so Celery can be added seamlessly later.

## 16. Limitations
- Does not currently support complex Raster data processing.
- Multi-GB Shapefiles might cause memory starvation since we read using standard GeoPandas instead of chunked streaming.

## 17. Learning
Learned to bridge complex Python C-bindings (like GDAL/Pyogrio) with lightweight asynchronous web engines (FastAPI) while prioritizing robust file security.

## 18. Future Scope
- **Celery + Redis**: Offloading measurements of 100k+ row datasets into a background queue.
- **Cloud Storage**: Connecting the File Extractor interface to AWS S3.
- **Authentication**: Implementing JWT endpoints to scope uploaded files to tenants/users.
