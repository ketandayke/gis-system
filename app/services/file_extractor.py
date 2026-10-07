import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Tuple, Optional, List
from fastapi import UploadFile
from app.core.logging import logger

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

class FileExtractionError(Exception):
    pass

def is_safe_path(basedir: str, path: str) -> bool:
    """Prevent zip slip / path traversal."""
    matchpath = os.path.abspath(path)
    return basedir == os.path.commonpath((basedir, matchpath))

async def save_upload_file_tmp(upload_file: UploadFile) -> str:
    """Save the uploaded file to a temporary file."""
    try:
        suffix = Path(upload_file.filename).suffix.lower()
        fd, path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, 'wb') as f:
            while chunk := await upload_file.read(8192):
                f.write(chunk)
        return path
    except Exception as e:
        logger.error(f"Error saving upload file: {e}")
        raise FileExtractionError("Could not save uploaded file")

def validate_and_extract(file_path: str, filename: str) -> Tuple[str, str, Optional[tempfile.TemporaryDirectory]]:
    """
    Validate and extract the file if it's a zip.
    Returns:
        (path_to_process, file_type, temp_dir_reference)
    The temp_dir_reference should be kept alive and cleaned up after processing.
    """
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise FileExtractionError(f"File exceeds maximum size of {MAX_FILE_SIZE} bytes.")
        
    ext = Path(filename).suffix.lower()
    
    if ext == ".kml":
        return file_path, "kml", None
        
    elif ext == ".zip":
        temp_dir = tempfile.TemporaryDirectory()
        extract_path = temp_dir.name
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                # Security checks
                for info in zf.infolist():
                    extracted_path = os.path.join(extract_path, info.filename)
                    if not is_safe_path(extract_path, extracted_path):
                        raise FileExtractionError("Unsafe zip extraction path detected")
                    if info.file_size > MAX_FILE_SIZE:
                        raise FileExtractionError("Uncompressed file exceeds size limit")
                
                zf.extractall(extract_path)
        except zipfile.BadZipFile:
            raise FileExtractionError("Invalid ZIP file")
            
        # Find the .shp file
        shp_files = list(Path(extract_path).rglob("*.shp"))
        if not shp_files:
            raise FileExtractionError("No .shp file found in the ZIP archive")
            
        target_shp = shp_files[0]
        
        # Check required components
        req_exts = [".shx", ".dbf"]
        for rext in req_exts:
            req_path = target_shp.with_suffix(rext)
            if not req_path.exists():
                raise FileExtractionError(f"Missing required file {rext} for shapefile")
                
        return str(target_shp), "shapefile", temp_dir
        
    else:
        raise FileExtractionError(f"Unsupported file extension: {ext}")
