from fastapi import APIRouter, UploadFile, File, HTTPException, status, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import os
import shutil
from pathlib import Path
import uuid
import mimetypes
import logging
from sqlalchemy.orm import Session

from .. import config, services, schemas
from ..database import get_db
from ..utils import sanitize_filename, validate_mime_type
from ..crud import file_crud

# Configure logging
logger = logging.getLogger(__name__)

# Define allowed file types and size limits
ALLOWED_MIME_TYPES = [
    'text/plain',                      # .txt
    'application/pdf',                 # .pdf
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
    'image/jpeg',                      # .jpg, .jpeg
    'image/png',                       # .png
    'image/gif',                       # .gif
    'image/webp',                      # .webp
    'image/heic',                      # .heic
    'image/heif',                      # .heif
]

# Define file extensions to MIME type mapping for special cases
EXTENSION_TO_MIME = {
    '.heic': 'image/heic',
    '.heif': 'image/heif',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}

# Get max file size from config
MAX_INLINE_SIZE = config.get_settings().max_file_size  # 20MB for inline processing
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB - maximum for Gemini Files API

# Create a temporary directory for file uploads if it doesn't exist
UPLOAD_DIR = Path(config.get_settings().upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(
    prefix="/files",
    tags=["Files"],
    responses={404: {"description": "Not found"}},
)

@router.post("/upload", response_model=schemas.FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file_to_server(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
) -> schemas.FileUploadResponse:
    """
    Upload a file, store its metadata in DB, and save file to disk.
    Returns file metadata including a unique file_id.
    """
    original_filename = sanitize_filename(file.filename or "")
    if not original_filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")
    
    file_extension_original = os.path.splitext(original_filename)[1].lower()
    content_type = file.content_type
    if file_extension_original in EXTENSION_TO_MIME:
        content_type = EXTENSION_TO_MIME[file_extension_original]
    
    if not content_type or not validate_mime_type(content_type, ALLOWED_MIME_TYPES):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type {content_type or 'unknown'} not supported."
        )
    
    file_id = str(uuid.uuid4())
    file_storage_extension = mimetypes.guess_extension(content_type) or file_extension_original or ''
    local_disk_path = UPLOAD_DIR / f"{file_id}{file_storage_extension}"
    
    file_size = 0
    try:
        with open(local_disk_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    buffer.close()
                    os.unlink(local_disk_path)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File size exceeds {MAX_FILE_SIZE // (1024*1024)}MB"
                    )
                buffer.write(chunk)
    except Exception as e:
        if os.path.exists(local_disk_path):
            os.unlink(local_disk_path)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not save file: {str(e)}")

    if content_type == 'text/plain':
        try:
            with open(local_disk_path, 'r', encoding='utf-8', errors='replace') as f: f.read(1024)
        except Exception as e:
            os.unlink(local_disk_path); raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid text file: {str(e)}")
    elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        try:
            text_c = services.extract_text_from_docx(str(local_disk_path))
            if not text_c or text_c.startswith('[Error'): 
                os.unlink(local_disk_path); raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid/corrupt DOCX")
        except Exception as e:
            os.unlink(local_disk_path); raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error processing DOCX: {str(e)}")

    processing_method = "inline" if file_size <= MAX_INLINE_SIZE else "files_api"
    
    db_file_metadata = file_crud.create_file_metadata(
        db=db, 
        file_id=file_id, 
        original_filename=original_filename, 
        content_type=content_type, 
        size=file_size, 
        local_disk_path=str(local_disk_path),
        processing_method=processing_method
    )

    logger.info(f"File metadata saved: {original_filename} (ID: {file_id}, Size: {file_size}, Type: {content_type}, Method: {processing_method})")
    
    return schemas.FileUploadResponse(
        file_id=db_file_metadata.id,
        filename=db_file_metadata.original_filename,
        content_type=db_file_metadata.content_type,
        size=db_file_metadata.size,
        processing_method=db_file_metadata.processing_method
    )

@router.get("/{file_id}/info", response_model=schemas.FileMetadataInfo)
async def get_file_metadata_info(
    file_id: str,
    db: Session = Depends(get_db)
) -> schemas.FileMetadataInfo:
    """Get metadata for a specific file from the database."""
    db_file_metadata = file_crud.get_file_metadata_by_id(db, file_id=file_id)
    if not db_file_metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File metadata not found")
    return db_file_metadata

@router.post("/process-file/{file_id}", response_model=schemas.FileProcessingResult, status_code=status.HTTP_200_OK)
async def process_file_for_chat(file_id: str) -> schemas.FileProcessingResult:
    """
    Process a file for use in a chat message.
    
    This endpoint takes a file ID, processes the file according to its type,
    and returns information about how it was processed.
    
    Supports both inline processing and Gemini Files API for large files.
    """
    # Look for files with the given ID in the upload directory
    matching_files = list(UPLOAD_DIR.glob(f"{file_id}*"))
    
    if not matching_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID {file_id} not found"
        )
    
    file_path = matching_files[0]
    file_size = file_path.stat().st_size
    file_extension = file_path.suffix.lower()
    mime_type, _ = mimetypes.guess_type(str(file_path))
    
    # Determine processing method based on file size
    processing_method = "inline" if file_size <= MAX_INLINE_SIZE else "files_api"
    
    # Process the file based on its type
    processing_result = {
        "file_id": file_id,
        "filename": file_path.name,
        "content_type": mime_type,
        "size": file_size,
        "path": str(file_path),
        "processing_type": "unknown",
        "processing_method": processing_method
    }
    
    try:
        # For text files
        if mime_type == 'text/plain' or file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                text_content = f.read()
                char_count = len(text_content)
                processing_result.update({
                    "processing_type": "text_extraction",
                    "char_count": char_count,
                    "preview": text_content[:200] + "..." if len(text_content) > 200 else text_content
                })
        
        # For DOCX files
        elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or file_extension == '.docx':
            text_content = services.extract_text_from_docx(str(file_path))
            char_count = len(text_content)
            processing_result.update({
                "processing_type": "docx_extraction",
                "char_count": char_count,
                "preview": text_content[:200] + "..." if len(text_content) > 200 else text_content
            })
        
        # For PDF and image files
        elif mime_type.startswith('image/') or mime_type == 'application/pdf':
            if processing_method == "inline":
                processing_result.update({
                    "processing_type": "binary_inline",
                    "preview": f"[Binary {mime_type} file - will be processed directly by Gemini API]"
                })
            else:
                processing_result.update({
                    "processing_type": "binary_files_api",
                    "preview": f"[Large {mime_type} file ({file_size/(1024*1024):.1f} MB) - will be processed using Gemini Files API]"
                })
        
        # For unsupported file types
        else:
            processing_result.update({
                "processing_type": "unsupported",
                "preview": f"[Unsupported file type: {mime_type}]"
            })
    
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
        # Ensure all fields of FileProcessingResult are potentially met even in error
        processing_result.update({
            "processing_type": "error",
            "error": str(e),
            # Fill in other required fields with sensible defaults or None if optional
            "filename": processing_result.get("filename", file_path.name if 'file_path' in locals() and file_path else file_id),
            "content_type": processing_result.get("content_type", mime_type if 'mime_type' in locals() else None),
            "size": processing_result.get("size", file_size if 'file_size' in locals() else -1),
            "processing_method": processing_result.get("processing_method", "unknown")
        })
    
    return schemas.FileProcessingResult(**processing_result)