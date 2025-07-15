from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, CheckConstraint, Table, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta, timezone
from .database import Base

# Association Table for Message and FileMetadata
message_file_link_table = Table(
    'message_file_link',
    Base.metadata,
    Column('message_id', Integer, ForeignKey('messages.id'), primary_key=True),
    Column('file_metadata_id', String, ForeignKey('file_metadata.id'), primary_key=True)
)

class Chat(Base):
    __tablename__ = "chats"

    # Fix: Use explicit SQLite-compatible autoincrement
    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement="auto")
    title = Column(String, index=True, default="New Chat") # Default title
    create_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="chats")

    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

class FileMetadata(Base):
    __tablename__ = "file_metadata"
    id = Column(String, primary_key=True, index=True) # Our UUID file_id from /upload-file endpoint
    original_filename = Column(String, index=True)
    content_type = Column(String)
    size = Column(Integer)
    local_disk_path = Column(String, unique=True, nullable=False)
    upload_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    processing_method = Column(String, nullable=False) # "inline" or "files_api"
    
    # Fields for Gemini Files API specifics (merged from old GeminiFile model)
    gemini_api_file_id = Column(String, nullable=True, index=True) # Name from Gemini SDK, e.g., "files/xxxx"
    gemini_api_upload_timestamp = Column(DateTime, nullable=True)
    gemini_api_expiry_timestamp = Column(DateTime, nullable=True) # Calculated (upload + ~48h)

    # Relationship to link table
    messages = relationship(
        "Message",
        secondary=message_file_link_table,
        back_populates="files"
    )

    def set_gemini_expiry(self):
        if self.gemini_api_upload_timestamp:
            # Gemini Files API has a 48-hour TTL. Set expiry slightly less for safety.
            self.gemini_api_expiry_timestamp = self.gemini_api_upload_timestamp + timedelta(hours=47, minutes=55)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    role = Column(String, nullable=False, index=True)  # "user" or "model" or "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Add a CHECK constraint to ensure role is either 'user', 'model', or 'assistant'
    __table_args__ = (
        CheckConstraint("role IN ('user', 'model', 'assistant')", name="check_role"),
    )

    chat = relationship("Chat", back_populates="messages")
    
    # Relationship to FileMetadata via the association table
    files = relationship(
        "FileMetadata",
        secondary=message_file_link_table,
        back_populates="messages"
    )

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    chats = relationship("Chat", back_populates="user")