import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.file_record import FileRecord
from app.models.feature_record import FeatureRecord
from app.schemas.file import FileRecordResponse
from app.schemas.measurement import PaginatedMeasurements, FeatureRecordResponse, MeasurementDict
from app.services.file_extractor import save_upload_file_tmp, validate_and_extract
from app.services.parser_service import parse_file
from app.services.crs_service import transform_geometry, is_geographic
from app.services.measurement_service import calculate_measurements
from app.core.logging import logger

router = APIRouter()

@router.post("/", response_model=FileRecordResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Process synchronously for small files initially
    # 1. Save temp file
    tmp_path = await save_upload_file_tmp(file)
    
    try:
        # 2. Extract and Validate
        extracted_path, file_type, temp_dir_ref = validate_and_extract(tmp_path, file.filename)
        
        # 3. Create DB Record initially
        db_file = FileRecord(
            filename=file.filename,
            file_type=file_type,
            status="PROCESSING"
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        # 4. Parse
        parsed_data = parse_file(extracted_path, file_type)
        
        # Update DB File Record
        db_file.feature_count = parsed_data["feature_count"]
        db_file.native_crs = parsed_data["native_crs"]
        db_file.status = "COMPLETED"
        
        # 5. Process Features
        features = parsed_data["features"]
        for feat in features:
            geom = feat["geometry"]
            geom_type = feat["geometry_type"]
            props = feat["properties"]
            idx = feat["feature_index"]
            
            # CRS transform
            if db_file.native_crs and is_geographic(db_file.native_crs):
                proj_geom, target_crs = transform_geometry(geom, db_file.native_crs)
            else:
                proj_geom, target_crs = geom, db_file.native_crs
                
            # Measure
            measurements = calculate_measurements(proj_geom)
            status = measurements.get("status", "FAILED")
            
            meas_dict = measurements.get("measurements", {})
            area_sq_m = meas_dict.get("area_sq_meters")
            length_m = meas_dict.get("length_meters")
            
            db_feature = FeatureRecord(
                file_id=db_file.id,
                feature_index=idx,
                geometry_type=geom_type,
                projected_crs=target_crs,
                area_sq_m=area_sq_m,
                length_m=length_m,
                properties=props,
                status=status
            )
            db.add(db_feature)
            
        db.commit()
        db.refresh(db_file)
        
        return db_file
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Cleanup temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            
@router.get("/{file_id}/", response_model=FileRecordResponse)
def get_file_info(file_id: str, db: Session = Depends(get_db)):
    db_file = db.query(FileRecord).filter(FileRecord.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file

@router.get("/{file_id}/measurements/", response_model=PaginatedMeasurements)
def get_measurements(
    file_id: str, 
    limit: int = 50, 
    offset: int = 0, 
    db: Session = Depends(get_db)
):
    db_file = db.query(FileRecord).filter(FileRecord.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    features = db.query(FeatureRecord).filter(FeatureRecord.file_id == file_id).offset(offset).limit(limit).all()
    
    feature_responses = []
    for f in features:
        measurements = MeasurementDict()
        if f.area_sq_m is not None:
            measurements.area_sq_meters = f.area_sq_m
            measurements.area_hectares = f.area_sq_m / 10000.0
        if f.length_m is not None:
            measurements.length_meters = f.length_m
            measurements.length_kilometers = f.length_m / 1000.0
            
        feature_responses.append(FeatureRecordResponse(
            feature_index=f.feature_index,
            geometry_type=f.geometry_type,
            projected_crs=f.projected_crs,
            status=f.status,
            measurements=measurements,
            properties=f.properties or {}
        ))
        
    return PaginatedMeasurements(
        file_id=file_id,
        total_features=db_file.feature_count or 0,
        features=feature_responses
    )
