from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Union

# --- File Metadata Schemas ---
class FileMetadataInfo(BaseModel):
    id: str # The UUID of the file metadata entry
    original_filename: str
    content_type: str
    size: int # in bytes
    processing_method: str # "inline" or "files_api"
    gemini_api_file_id: Optional[str] = None # Gemini API identifier, if applicable

    class Config:
        from_attributes = True

# Schema for the response from /upload-file endpoint
class FileUploadResponse(BaseModel):
    file_id: str
    filename: str # original filename
    content_type: str
    size: int
    # path: str # Removed, not sending local server path to frontend
    processing_method: str

# --- Message Schemas ---
class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    # This schema is simple. If files are involved, their file_ids (UUIDs)
    # will be passed as a separate parameter to the endpoint/service, not in this body.
    pass

# The old MessageFile and MessageFileCreate are no longer needed
# as we link Messages to FileMetadata via file_ids.

class Message(MessageBase):
    id: int
    chat_id: int
    timestamp: datetime
    files: List[FileMetadataInfo] = [] # List of associated file metadata

    class Config:
        from_attributes = True

# --- Chat Schemas ---
class ChatBase(BaseModel):
    title: Optional[str] = "New Chat"

class ChatCreate(ChatBase):
    # Used by API when client explicitly wants to create a new chat session, 
    # even if an unnamed one might exist.
    forceCreate: Optional[bool] = False

class ChatUpdate(BaseModel):
    title: Optional[str] = None

class Chat(ChatBase):
    id: int
    create_time: datetime
    messages: List[Message] = []

    class Config:
        from_attributes = True

# --- User Message Input for Streaming Endpoint ---
class UserMessageInput(BaseModel):
    """Schema for user message input with optional file references for streaming endpoint."""
    content: str
    file_ids: Optional[List[str]] = None # List of FileMetadata UUIDs

# The old GeminiFile schemas are obsolete as this functionality is part of FileMetadata.

# --- File Processing Schemas ---
class FileProcessingResult(BaseModel):
    file_id: str
    filename: str
    content_type: Optional[str] = None
    size: int
    path: Optional[str] = None # Local server path, consider if this should be exposed
    processing_type: str
    processing_method: str
    char_count: Optional[int] = None
    preview: Optional[str] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True # If it ever needs to be created from a model instance

# --- Streaming Schemas ---
class InterruptRequest(BaseModel):
    generation_id: Optional[str] = None

class InterruptResponse(BaseModel):
    status: str
    message: str