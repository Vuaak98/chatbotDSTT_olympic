from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aichatbot.db")

# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

# For SQLite, connect_args is needed to allow multithreading
engine_args = {}
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

# engine = create_engine(
#     DATABASE_URL, **engine_args
# )
# THAY THẾ BẰNG CODE NÀY

# Đối với PostgreSQL, chúng ta không cần engine_args đặc biệt nữa
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Bật tính năng kiểm tra kết nối
    pool_recycle=1800        # Tái sử dụng kết nối sau mỗi 30 phút (1800 giây)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Add SQLite specific configurations to ensure proper auto-increment behavior
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception: # Catch any exception to trigger a rollback
        db.rollback()
        raise # Re-raise the exception to be handled by FastAPI
    finally:
        db.close()