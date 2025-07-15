from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from .. import crud, models, schemas
from ..database import get_db
from app.auth_service import get_current_user
from app.models import User

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Chat, status_code=status.HTTP_201_CREATED)
def create_new_chat(
    chat: schemas.ChatCreate = schemas.ChatCreate(title="New Chat"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a new chat session."""
    try:
        # Get existing chats for this user
        existing_chats = crud.get_chats(db, user_id=current_user.id, limit=1)
        # If no chat object provided, use default (empty title)
        if chat is None:
            if existing_chats:
                logger.info(f"Returning existing chat instead of creating new one: {existing_chats[0].id}")
                return existing_chats[0]
            chat = schemas.ChatCreate(title="New Chat")
        elif not getattr(chat, 'forceCreate', False) and existing_chats:
            logger.info(f"forceCreate not set, returning existing chat: {existing_chats[0].id}")
            return existing_chats[0]
        logger.info(f"Attempting to create new chat with title: {chat.title}")
        db_chat = crud.create_chat(db=db, chat=chat, user_id=current_user.id)
        if not db_chat or not db_chat.id:
            logger.error("Chat created, but no valid ID was assigned")
            raise ValueError("Failed to generate valid chat ID")
        logger.info(f"Created new chat with ID: {db_chat.id}")
        return db_chat
    except Exception as e:
        logger.error(f"Error creating chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating chat: {str(e)}"
        )

@router.get("/", response_model=List[schemas.Chat])
def read_all_chats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieves a list of all chat sessions for the current user."""
    chats = crud.get_chats(db, user_id=current_user.id, skip=skip, limit=limit)
    return chats

@router.get("/{chat_id}", response_model=schemas.Chat)
def read_single_chat(chat_id: int, db: Session = Depends(get_db)):
    """Retrieves a specific chat session by its ID, including its messages."""
    db_chat = crud.get_chat(db, chat_id=chat_id)
    if db_chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return db_chat

@router.put("/{chat_id}", response_model=schemas.Chat)
def update_existing_chat(chat_id: int, chat_update: schemas.ChatUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Updates the title of an existing chat session."""
    db_chat = crud.update_chat(db=db, chat_id=chat_id, chat_update=chat_update, user_id=current_user.id)
    if db_chat is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed or chat not found")
    return db_chat

@router.patch("/{chat_id}", response_model=schemas.Chat)
def rename_chat(chat_id: int, chat_update: schemas.ChatUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Renames a chat session (PATCH alternative to PUT)."""
    db_chat = crud.update_chat(db=db, chat_id=chat_id, chat_update=chat_update, user_id=current_user.id)
    if db_chat is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed or chat not found")
    return db_chat

@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_chat(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Deletes a chat session and all its associated messages."""
    db_chat = crud.delete_chat(db=db, chat_id=chat_id, user_id=current_user.id)
    if db_chat is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed or chat not found")
    return None # Return None for 204 No Content