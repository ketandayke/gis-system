from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class MeasurementDict(BaseModel):
    area_sq_meters: Optional[float] = None
    area_hectares: Optional[float] = None
    length_meters: Optional[float] = None
    length_kilometers: Optional[float] = None

class FeatureRecordResponse(BaseModel):
    feature_index: int
    geometry_type: str
    projected_crs: Optional[str] = None
    status: str
    measurements: MeasurementDict
    properties: Dict[str, Any]

    class Config:
        from_attributes = True

class PaginatedMeasurements(BaseModel):
    file_id: str
    total_features: int
    features: List[FeatureRecordResponse]
