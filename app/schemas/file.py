from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FileRecordBase(BaseModel):
    filename: str
    file_type: str

class FileRecordCreate(FileRecordBase):
    pass

class FileRecordResponse(FileRecordBase):
    id: str
    feature_count: Optional[int] = None
    native_crs: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
