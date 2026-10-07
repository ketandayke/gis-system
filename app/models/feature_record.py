import uuid
from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON
from app.db.base import Base

class FeatureRecord(Base):
    __tablename__ = "feature_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String, ForeignKey("file_records.id"), nullable=False)
    feature_index = Column(Integer, nullable=False)
    geometry_type = Column(String, nullable=False)
    projected_crs = Column(String, nullable=True)
    area_sq_m = Column(Float, nullable=True)
    length_m = Column(Float, nullable=True)
    properties = Column(JSON, nullable=True)
    status = Column(String, nullable=False) # SUCCESS, FAILED, NOT_APPLICABLE
    error_message = Column(String, nullable=True)
