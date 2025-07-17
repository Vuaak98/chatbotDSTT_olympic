from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
# === THÊM IMPORT NÀY ===
from fastapi.openapi.utils import get_openapi
# ========================
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
import logging
import asyncio
import google.genai.errors
from sqlalchemy import inspect
from datetime import datetime

from .database import engine, Base
from . import models  # noqa
from .tasks import start_background_tasks
from .middleware import (
    ErrorHandlerMiddleware,
    RateLimiter,
    request_validation_exception_handler,
    http_exception_handler,
    gemini_api_exception_handler
)
from app.routers import auth_router

# ... (Phần logging và kiểm tra CSDL giữ nguyên) ...
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Checking database tables...")
inspector = inspect(engine)
existing_tables = inspector.get_table_names()
logger.info(f"Found {len(existing_tables)} existing tables")
metadata_tables = Base.metadata.tables.keys()
missing_tables = set(metadata_tables) - set(existing_tables)
if missing_tables:
    logger.info(f"Creating missing tables: {', '.join(missing_tables)}")
    Base.metadata.create_all(bind=engine)
    logger.info("Missing tables created successfully")
else:
    logger.info("No missing tables detected. All required tables exist.")


# --- KHỞI TẠO APP FASTAPI ---
app = FastAPI(
    title="AI Math Chatbot API",
    description="API for the AI Math Chatbot application, managing chats and messages.",
    version="0.1.0"
)


# --- THÊM CẤU HÌNH BẢO MẬT CHO SWAGGER UI (ĐÃ SỬA LỖI) ---
def custom_openapi():
    """
    Tùy chỉnh OpenAPI schema để thêm nút 'Authorize' cho JWT Bearer token.
    """
    if app.openapi_schema:
        return app.openapi_schema

    # === SỬA LẠI DÒNG NÀY ĐỂ TRÁNH ĐỆ QUY VÔ HẠN ===
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # ============================================
    
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    # Áp dụng security scheme cho các API cần xác thực
    api_router = {route.path: route for route in app.routes}
    for path, path_item in openapi_schema["paths"].items():
        if path.startswith("/auth/") or path == "/" or path == "/health":
            continue
        for method in path_item.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Gán hàm tùy chỉnh vào app
app.openapi = custom_openapi
# --- KẾT THÚC PHẦN CẤU HÌNH ---


# ... (Toàn bộ phần còn lại của file main.py giữ nguyên) ...

# Register exception handlers
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(google.genai.errors.APIError, gemini_api_exception_handler)

# Add middleware
app.add_middleware(RateLimiter)
app.add_middleware(ErrorHandlerMiddleware)

# CORS Configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
logger.info(f"CORS allowed origins: {allowed_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the AI Math Chatbot API"}

from .routers import chat_router, message_router, file_router, streaming_router

app.include_router(chat_router.router)
app.include_router(message_router.router)
app.include_router(file_router.router)
app.include_router(streaming_router.router)
app.include_router(auth_router.router)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_background_tasks())
    logger.info("Background tasks started.")

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}