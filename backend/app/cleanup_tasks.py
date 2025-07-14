import os
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, delete # Ensure select and delete are imported

from . import models, crud # Assuming crud contains file_crud
from .models import FileMetadata, message_file_link # Ensure models are imported
from .config import get_settings # For potential cleanup settings
from .database import SessionLocal # For creating a DB session if run standalone

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Gemini Client if needed for API deletions (optional)
# from .services import client # Assuming client is accessible; handle potential None

DEFAULT_ORPHAN_FILE_AGE_DAYS = 7 # Example: Files unlinked for 7 days
DEFAULT_EXPIRED_GEMINI_GRACE_DAYS = 2 # Example: Delete local 2 days after Gemini expiry

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def perform_physical_file_cleanup(db: Session):
    logger.info("Starting physical file cleanup task...")
    settings = get_settings()
    
    files_deleted_count = 0
    metadata_deleted_count = 0

    # 1. Cleanup based on Expired Gemini Files API uploads
    # Policy: Delete local files whose Gemini API counterparts have expired some time ago.
    # Gemini itself handles deletion from their cloud storage after TTL (48h).
    # This is more about cleaning up local copies if they are no longer considered useful.
    try:
        expired_grace_period = timedelta(days=settings.cleanup_expired_gemini_grace_days if hasattr(settings, 'cleanup_expired_gemini_grace_days') else DEFAULT_EXPIRED_GEMINI_GRACE_DAYS)
        # Query for files whose Gemini API versions have expired AND are past the grace period
        # Check for gemini_api_expiry_timestamp < (now - grace_period)
        # This means the Gemini file *should* have been gone for at least `expired_grace_period`
        query_expired_gemini = (
            select(FileMetadata)
            .where(FileMetadata.gemini_api_file_id.isnot(None))
            .where(FileMetadata.gemini_api_expiry_timestamp.isnot(None))
            .where(FileMetadata.gemini_api_expiry_timestamp < (datetime.utcnow() - expired_grace_period))
        )
        expired_gemini_files = db.scalars(query_expired_gemini).all()

        for fm in expired_gemini_files:
            logger.info(f"FileMetadata ID {fm.id} ({fm.original_filename}) has an expired Gemini API file past grace period. Considering for local deletion.")
            # Optional: Check if linked to any messages before deleting local copy
            # For now, we assume if Gemini part expired, local can go too if this policy is active.
            if fm.local_disk_path and os.path.exists(fm.local_disk_path):
                try:
                    os.remove(fm.local_disk_path)
                    logger.info(f"Deleted local file: {fm.local_disk_path}")
                    files_deleted_count += 1
                    # Optionally, clear gemini specific fields if we keep the metadata
                    # fm.gemini_api_file_id = None
                    # fm.gemini_api_upload_timestamp = None
                    # fm.gemini_api_expiry_timestamp = None
                    # db.commit()
                    # Or delete the metadata record entirely if the local file was its primary reason for existence
                    # For now, let's assume we might delete the metadata later if also unlinked.
                except OSError as e:
                    logger.error(f"Error deleting local file {fm.local_disk_path}: {e}")
            # Consider deleting the FileMetadata record itself if no longer useful
            # This might be better handled by the unlinked files logic below

    except Exception as e:
        logger.error(f"Error during expired Gemini files cleanup: {e}", exc_info=True)


    # 2. Cleanup Unlinked Local Files (Orphaned FileMetadata records)
    # Policy: Delete FileMetadata records and their corresponding local files if the metadata
    # is old and not linked to any message in message_file_link.
    try:
        orphan_file_age_threshold = datetime.utcnow() - timedelta(days=settings.cleanup_orphan_file_age_days if hasattr(settings, 'cleanup_orphan_file_age_days') else DEFAULT_ORPHAN_FILE_AGE_DAYS)
        
        # Subquery to find all file_metadata_ids that ARE linked to messages
        linked_fm_ids_subquery = select(message_file_link.c.file_metadata_id).distinct()

        # Query for FileMetadata records that are old AND not in the set of linked_fm_ids
        query_unlinked_old = (
            select(FileMetadata)
            .where(FileMetadata.upload_timestamp < orphan_file_age_threshold)
            .where(FileMetadata.id.notin_(linked_fm_ids_subquery))
        )
        unlinked_files_metadata = db.scalars(query_unlinked_old).all()

        for fm in unlinked_files_metadata:
            logger.info(f"FileMetadata ID {fm.id} ({fm.original_filename}) is old, unlinked, and will be deleted.")
            if fm.local_disk_path and os.path.exists(fm.local_disk_path):
                try:
                    os.remove(fm.local_disk_path)
                    logger.info(f"Deleted associated local file: {fm.local_disk_path}")
                    files_deleted_count += 1
                except OSError as e:
                    logger.error(f"Error deleting local file {fm.local_disk_path} for unlinked metadata {fm.id}: {e}")
            
            try:
                # Delete the FileMetadata record itself
                # Using file_crud if it has a delete method, or direct delete
                if hasattr(crud, 'file_crud') and hasattr(crud.file_crud, 'delete_file_metadata_by_id'):
                    crud.file_crud.delete_file_metadata_by_id(db, file_id=fm.id)
                else: # Fallback to direct delete if CRUD method not found
                    db.delete(fm)
                    db.commit() # Commit after each delete or batch commits
                logger.info(f"Deleted FileMetadata record for ID: {fm.id}")
                metadata_deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting FileMetadata record {fm.id}: {e}", exc_info=True)
                db.rollback() # Rollback if delete fails
        
        if unlinked_files_metadata: # Commit any batched deletes if not committed individually
            try:
                db.commit()
            except: pass # If individual commits were used, this might do nothing or error harmlessly

    except Exception as e:
        logger.error(f"Error during unlinked files cleanup: {e}", exc_info=True)

    logger.info(f"Physical file cleanup task completed. Local files deleted: {files_deleted_count}. Metadata records deleted: {metadata_deleted_count}.")

# Example of how this might be run (e.g., from a scheduled script or admin endpoint)
if __name__ == "__main__":
    # This is for standalone testing/execution.
    # In a FastAPI app, you'd integrate this with a scheduler or background task runner.
    print("Running cleanup task directly...")
    db_gen = get_db_session()
    db_session = next(db_gen)
    try:
        perform_physical_file_cleanup(db_session)
    finally:
        next(db_gen, None) # Close session
    print("Cleanup task finished.") 