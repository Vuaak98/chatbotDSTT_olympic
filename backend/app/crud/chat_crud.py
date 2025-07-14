from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from .. import models, schemas
from . import file_crud

logger = logging.getLogger(__name__)

# CRUD operations for Chat

def get_chat(db: Session, chat_id: int) -> Optional[models.Chat]:
    """Lấy một cuộc trò chuyện duy nhất bằng ID của nó."""
    return db.query(models.Chat).filter(models.Chat.id == chat_id).first()

def get_chats(db: Session, skip: int = 0, limit: int = 100) -> List[models.Chat]:
    """Lấy danh sách các cuộc trò chuyện, được sắp xếp theo thời gian gần nhất."""
    return db.query(models.Chat).order_by(models.Chat.create_time.desc()).offset(skip).limit(limit).all()

def create_chat(db: Session, chat: schemas.ChatCreate) -> models.Chat:
    """Tạo một cuộc trò chuyện mới."""
    try:
        # Create chat with provided title or default
        db_chat = models.Chat(title=chat.title)
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        
        # Additional validation to ensure ID was generated
        if not db_chat.id:
            db.rollback()
            raise ValueError("Database did not generate a valid ID for the chat")
        
        # Log successful creation
        logger.info(f"Successfully created chat with ID: {db_chat.id}")
        return db_chat
    except Exception as e:
        # Rollback the transaction on error
        db.rollback()
        logger.error(f"Error creating chat: {str(e)}")
        raise

def update_chat(db: Session, chat_id: int, chat_update: schemas.ChatUpdate) -> Optional[models.Chat]:
    """Update a chat's title."""
    db_chat = get_chat(db, chat_id)
    if db_chat:
        if chat_update.title is not None:
            db_chat.title = chat_update.title
            db.commit()
            db.refresh(db_chat)
    return db_chat

def delete_chat(db: Session, chat_id: int) -> Optional[models.Chat]:
    """Delete a chat by its ID."""
    db_chat = get_chat(db, chat_id)
    if db_chat:
        # File cleanup logic needs to be re-evaluated based on FileMetadata
        # For now, focus on chat and message deletion. Physical file cleanup is a separate concern
        # (handled by background tasks in file_router or a dedicated service)
        db.delete(db_chat) # Cascade will delete messages, and relationship to message_file_link_table
        db.commit()
        logger.info(f"Deleted chat ID {chat_id} and all its messages and file links")
    return db_chat

# CRUD operations for Message

def get_messages_for_chat(db: Session, chat_id: int, skip: int = 0, limit: int = 1000, exclude_message_id: Optional[int] = None) -> List[models.Message]:
    """Retrieve messages for a specific chat, ordered by timestamp.
    Can optionally exclude a specific message ID (e.g., the current user message being processed).
    """
    query = db.query(models.Message)\
              .filter(models.Message.chat_id == chat_id)
    
    if exclude_message_id is not None:
        query = query.filter(models.Message.id != exclude_message_id)
        
    return query.order_by(models.Message.timestamp)\
              .offset(skip)\
              .limit(limit)\
              .all()

# This will be the primary way to create messages, including those with files.
def create_chat_message(
    db: Session, 
    chat_id: int, 
    role: str, 
    content: str, 
    file_ids: Optional[List[str]] = None
) -> models.Message:
    """Create a new message, and if file_ids are provided, link them.
       Assumes file_ids refer to existing FileMetadata entries.
    """ 
    db_message = models.Message(chat_id=chat_id, role=role, content=content)
    db.add(db_message)
    
    if file_ids:
        for file_id in file_ids:
            file_metadata = file_crud.get_file_metadata_by_id(db, file_id=file_id)
            if file_metadata:
                db_message.files.append(file_metadata) # Append to the relationship list
            else:
                # Handle error: file_id provided but not found in FileMetadata
                logger.warning(f"FileMetadata with id {file_id} not found. Cannot link to message.")
    
    db.commit()
    db.refresh(db_message)
    return db_message

def create_chat_message_with_files(
    db: Session, 
    message_data: schemas.MessageCreate, 
    chat_id: int, 
    file_metadatas: Optional[List[dict]] = None
) -> models.Message:
    """
    Create a new message and link it to file metadata entries.
    
    Args:
        db: Database session
        message_data: Message data schema
        chat_id: ID of the chat to add the message to
        file_metadatas: List of dicts with file metadata, each containing an 'id' key
        
    Returns:
        The created message with files linked
    """
    # Create the message
    db_message = models.Message(
        chat_id=chat_id,
        role=message_data.role,
        content=message_data.content
    )
    db.add(db_message)
    
    # Link files if provided
    if file_metadatas:
        for file_meta in file_metadatas:
            file_id = file_meta.get('id')
            if file_id:
                file_metadata = file_crud.get_file_metadata_by_id(db, file_id=file_id)
                if file_metadata:
                    db_message.files.append(file_metadata)
                else:
                    logger.warning(f"FileMetadata with id {file_id} not found. Cannot link to message.")
    
    db.commit()
    db.refresh(db_message)
    return db_message

# CRUD operations for GeminiFile

def get_expired_gemini_files_from_metadata(db: Session) -> List[models.FileMetadata]:
    """Retrieve all FileMetadata records where the Gemini file has expired."""
    now = datetime.utcnow()
    # Query FileMetadata where gemini_api_expiry_timestamp is not null and is in the past
    return db.query(models.FileMetadata).filter(
        models.FileMetadata.gemini_api_expiry_timestamp.isnot(None),
        models.FileMetadata.gemini_api_expiry_timestamp < now
    ).all() 