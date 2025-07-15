from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os # Import os to read environment variable
import logging
import asyncio
import google.genai.errors
from sqlalchemy import inspect
from datetime import datetime  # ← Thêm import này

from .database import engine, Base
# Import models to ensure they are registered with Base
from . import models # noqa
from .tasks import start_background_tasks

# Import middleware and exception handlers
from .middleware import (
    ErrorHandlerMiddleware,
    RateLimiter,
    request_validation_exception_handler,
    http_exception_handler,
    gemini_api_exception_handler
)

from app.routers import auth_router

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check if database tables exist and create missing ones
logger.info("Checking database tables...")
inspector = inspect(engine)
existing_tables = inspector.get_table_names()
logger.info(f"Found {len(existing_tables)} existing tables")

# Get all tables defined in SQLAlchemy models
metadata_tables = Base.metadata.tables.keys()
missing_tables = set(metadata_tables) - set(existing_tables)

if missing_tables:
    logger.info(f"Creating missing tables: {', '.join(missing_tables)}")
    # Create only the tables that don't exist yet
    Base.metadata.create_all(bind=engine)
    logger.info("Missing tables created successfully")
else:
    logger.info("No missing tables detected. All required tables exist.")

app = FastAPI(
    title="AI Math Chatbot API",
    description="API for the AI Math Chatbot application, managing chats and messages.",
    version="0.1.0"
)

# Register exception handlers
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(google.genai.errors.APIError, gemini_api_exception_handler)

# Add middleware
# Note: Middleware is executed in reverse order (last added, first executed)

# Add rate limiting middleware
app.add_middleware(RateLimiter)

# Add error handling middleware
app.add_middleware(ErrorHandlerMiddleware)

# CORS Configuration
# Read allowed origins from environment variable, default to "*" for development
# In production, set this to the specific frontend URL(s)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Log the allowed origins for debugging
logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins, # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods
    allow_headers=["*"], # Allow all headers
)

@app.get("/", tags=["Root"])
def read_root():
    """Provides a simple welcome message for the API root."""
    return {"message": "Welcome to the AI Math Chatbot API"}

from .routers import chat_router, message_router, file_router, streaming_router

app.include_router(chat_router.router)
app.include_router(message_router.router)
app.include_router(file_router.router)
app.include_router(streaming_router.router)
app.include_router(auth_router.router)

# Start background tasks when the application starts
@app.on_event("startup")
async def startup_event():
    """Start background tasks when the application starts."""
    # Start the background tasks in a separate task
    asyncio.create_task(start_background_tasks())
    logger.info("Background tasks started.")

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for Docker."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}