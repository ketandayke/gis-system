import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from app.db.base import Base

class FileRecord(Base):
    __tablename__ = "file_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    feature_count = Column(Integer, nullable=True)
    native_crs = Column(String, nullable=True)
    status = Column(String, default="PROCESSING") # PROCESSING, COMPLETED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)
