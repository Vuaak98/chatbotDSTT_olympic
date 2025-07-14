#!/usr/bin/env python

"""
Database management script for the AI Math Chatbot.

Usage:
    python db_manager.py init     # Initialize the database
    python db_manager.py seed     # Seed the database with test data
    python db_manager.py reset    # Reset the database (drop and recreate)
    python db_manager.py show     # Show tables and their columns
    python db_manager.py backup   # Backup the database
    python db_manager.py clean    # Clean up expired files and old messages
    python db_manager.py check    # Check database for integrity issues
"""

import sys
import os
import logging
import shutil
import datetime
from sqlalchemy import inspect
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import the app package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app import models  # Import models to ensure they are registered with Base
from app.config import get_settings

def init_db():
    """Initialize the database by creating all tables."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")
    return True

def reset_db():
    """Reset the database by dropping all tables and recreating them."""
    logger.info("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Tables dropped successfully.")
    return init_db()

def show_tables():
    """Show all tables in the database."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info("Tables in the database:")
    for table in tables:
        logger.info(f"- {table}")
        columns = inspector.get_columns(table)
        for column in columns:
            logger.info(f"  - {column['name']}: {column['type']}")
    return tables

def seed_db():
    """Seed the database with test data."""
    # Import here to avoid circular imports
    from app.seed_db import seed_db as _seed_db
    _seed_db()
    logger.info("Database seeded successfully.")
    return True

def backup_db():
    """Create a backup of the database."""
    settings = get_settings()
    db_url = settings.database_url
    
    # Only handle SQLite databases for now
    if not db_url.startswith("sqlite:///"):
        logger.error("Backup only supports SQLite databases.")
        return False
    
    # Extract the database path from the URL
    db_path = db_url.replace("sqlite:///", "")
    if db_path.startswith("./"):
        db_path = db_path[2:]
    
    # Create a timestamped backup file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.{timestamp}.backup"
    
    try:
        # Make sure the database exists
        if not os.path.exists(db_path):
            logger.error(f"Database file not found: {db_path}")
            return False
        
        # Copy the database file
        shutil.copy2(db_path, backup_path)
        logger.info(f"Database backed up to: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Error backing up database: {e}")
        return False

def clean_db():
    """Clean up expired files and old messages."""
    from app.tasks import cleanup_expired_gemini_files, cleanup_old_chat_data
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Run cleanup tasks synchronously
        loop = asyncio.get_event_loop()
        loop.run_until_complete(cleanup_expired_gemini_files(db))
        loop.run_until_complete(cleanup_old_chat_data(db))
        
        logger.info("Database cleanup completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Error cleaning database: {e}")
        return False
    finally:
        db.close()

def check_db():
    """Check database for integrity issues."""
    db = SessionLocal()
    
    try:
        # Check that tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        required_tables = ["chats", "messages", "file_metadata"]
        
        missing_tables = [table for table in required_tables if table not in tables]
        if missing_tables:
            logger.error(f"Missing tables: {', '.join(missing_tables)}")
            return False
        
        # Check for orphaned messages (messages with no chat)
        from app.models import Message, Chat
        orphaned_count = db.query(Message).filter(
            ~Message.chat_id.in_(db.query(Chat.id))
        ).count()
        
        if orphaned_count > 0:
            logger.warning(f"Found {orphaned_count} orphaned messages. Consider running a database repair.")
        
        logger.info("Database integrity check completed.")
        return True
    except Exception as e:
        logger.error(f"Error checking database: {e}")
        return False
    finally:
        db.close()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    if command == "init":
        init_db()
    elif command == "seed":
        seed_db()
    elif command == "reset":
        reset_db()
        seed_db()
    elif command == "show":
        show_tables()
    elif command == "backup":
        backup_db()
    elif command == "clean":
        clean_db()
    elif command == "check":
        check_db()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()