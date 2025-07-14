import asyncio
import logging
from datetime import datetime, timedelta
import os
from sqlalchemy.orm import Session

from . import crud, models
from .database import get_db
from .crud import file_crud

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def cleanup_expired_gemini_files(db: Session):
    """
    Clean up expired Gemini Files API uploads.
    
    This task should be run periodically to clean up expired files from both
    the local filesystem and the database.
    
    The Gemini Files API has a 48-hour TTL, so files uploaded via the API
    will expire after that time. This task removes the local files and database
    records for expired files.
    """
    try:
        # Get all expired Gemini file records
        expired_files = file_crud.get_expired_gemini_files(db)
        
        if not expired_files:
            logger.info("No expired Gemini Files API uploads found.")
            return
        
        logger.info(f"Found {len(expired_files)} expired Gemini Files API uploads to clean up.")
        
        # Clean up each expired file
        for file_record in expired_files:
            try:
                # Delete the local file if it exists
                if os.path.exists(file_record.local_disk_path):
                    os.unlink(file_record.local_disk_path)
                    logger.info(f"Deleted expired local file: {file_record.local_disk_path}")
                
                # Delete the database record
                file_crud.delete_file_metadata(db, file_record.id)
                logger.info(f"Deleted expired Gemini file record for file ID: {file_record.id}")
                
            except Exception as e:
                logger.error(f"Error cleaning up expired Gemini file {file_record.id}: {e}")
                # Continue with the next file even if there's an error
                continue
        
        logger.info(f"Completed cleanup of expired Gemini Files API uploads.")
        
    except Exception as e:
        logger.error(f"Error in cleanup_expired_gemini_files task: {e}")

async def cleanup_old_chat_data(db: Session):
    """Clean up old chat data to maintain database performance.
    
    This function:
    1. Deletes messages older than 60 days
    2. Removes orphaned files
    """
    try:
        # Calculate cutoff date (60 days ago)
        cutoff_date = datetime.utcnow() - timedelta(days=60)
        
        # Delete old messages
        result = db.query(models.Message).filter(
            models.Message.timestamp < cutoff_date
        ).delete()
        
        logger.info(f"Deleted {result} messages older than 60 days")
        
        # Clean up orphaned files
        file_records = db.query(models.FileMetadata).all()
        for file_record in file_records:
            # Check if the local file exists but is not referenced by any message
            if file_record.local_disk_path and os.path.exists(file_record.local_disk_path):
                message_references = db.query(models.Message).filter(
                    models.Message.files.any(models.FileMetadata.id == file_record.id)
                ).count()
                
                if message_references == 0:
                    # Delete the orphaned file
                    try:
                        os.remove(file_record.local_disk_path)
                        db.delete(file_record)
                        logger.info(f"Deleted orphaned file: {file_record.local_disk_path}")
                    except Exception as e:
                        logger.error(f"Error deleting orphaned file: {e}")
        
        # Commit changes
        db.commit()
        
    except Exception as e:
        logger.error(f"Error cleaning up old chat data: {e}")
        db.rollback()

async def start_background_tasks():
    """
    Start background tasks for the application.
    
    This function should be called when the application starts.
    It starts periodic tasks like cleaning up expired Gemini Files API uploads.
    """
    while True:
        try:
            # Get a database session
            db = next(get_db())
            
            # Run the cleanup tasks
            await cleanup_expired_gemini_files(db)
            await cleanup_old_chat_data(db)
            
            # Close the database session
            db.close()
            
            # Wait for 6 hours before running again
            await asyncio.sleep(21600)  # 6 hours in seconds
            
        except Exception as e:
            logger.error(f"Error in background tasks: {e}")
            # Wait a bit before trying again
            await asyncio.sleep(60)  # 1 minute in seconds