from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from .. import models, schemas

def get_file_metadata_by_id(db: Session, file_id: str) -> Optional[models.FileMetadata]:
    """Retrieve a single file metadata record by its ID."""
    return db.query(models.FileMetadata).filter(models.FileMetadata.id == file_id).first()

def create_file_metadata(
    db: Session, 
    file_id: str, 
    original_filename: str, 
    content_type: str, 
    size: int, 
    local_disk_path: str,
    processing_method: str
) -> models.FileMetadata:
    """Create a new file metadata record."""
    db_file_metadata = models.FileMetadata(
        id=file_id,
        original_filename=original_filename,
        content_type=content_type,
        size=size,
        local_disk_path=local_disk_path,
        processing_method=processing_method
    )
    db.add(db_file_metadata)
    db.commit()
    db.refresh(db_file_metadata)
    return db_file_metadata

def update_file_metadata_gemini_info(
    db: Session,
    file_id: str,
    gemini_api_file_id: str
) -> Optional[models.FileMetadata]:
    """Update a file metadata record with Gemini API file info."""
    db_file_metadata = get_file_metadata_by_id(db, file_id=file_id)
    if db_file_metadata:
        db_file_metadata.gemini_api_file_id = gemini_api_file_id
        db_file_metadata.gemini_api_upload_timestamp = datetime.utcnow()
        db_file_metadata.set_gemini_expiry()
        db.commit()
        db.refresh(db_file_metadata)
    return db_file_metadata

def get_expired_gemini_files(db: Session) -> List[models.FileMetadata]:
    """Retrieve all file metadata records where the Gemini file has expired."""
    now = datetime.utcnow()
    return db.query(models.FileMetadata).filter(
        models.FileMetadata.gemini_api_expiry_timestamp.isnot(None),
        models.FileMetadata.gemini_api_expiry_timestamp < now
    ).all()

def delete_file_metadata(db: Session, file_id: str) -> bool:
    """Delete a file metadata record."""
    db_file_metadata = get_file_metadata_by_id(db, file_id=file_id)
    if db_file_metadata:
        db.delete(db_file_metadata)
        db.commit()
        return True
    return False 