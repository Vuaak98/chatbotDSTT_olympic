#!/usr/bin/env python

"""
Database migration script for the AI Math Chatbot.

This script provides a simpler interface to Alembic commands for common database migration tasks.

Usage:
    python migrate.py generate "Description of changes"  # Generate a new migration
    python migrate.py upgrade                            # Apply all migrations
    python migrate.py downgrade [steps]                  # Downgrade migrations (default: 1 step)
    python migrate.py history                            # Show migration history
    python migrate.py current                            # Show current revision
"""

import sys
import logging
import subprocess
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_alembic_command(command):
    """Run an Alembic command."""
    python_exe = os.path.join('..', '.venv', 'Scripts', 'python')
    #cmd = [python_exe, '-m', 'alembic'] + command
        # === THAY ĐỔI DUY NHẤT Ở ĐÂY ===
    # Thay vì đoán mò đường dẫn, chúng ta dùng `sys.executable`.
    # Biến này *luôn luôn* chứa đường dẫn đầy đủ đến file python.exe
    # hoặc trình thông dịch python đang chạy script này.
    # Đây là cách làm đúng để script có thể chạy trên mọi máy tính,
    # bất kể họ dùng venv, conda, hay cài Python ở đâu.
    cmd = [sys.executable, '-m', 'alembic'] + command
    
    try:
        logger.info(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running Alembic command: {e}")
        return False

def generate_migration(description):
    """Generate a new migration with autogenerate."""
    return run_alembic_command(['revision', '--autogenerate', '-m', description])

def upgrade_database():
    """Upgrade database to latest migration."""
    return run_alembic_command(['upgrade', 'head'])

def downgrade_database(steps=1):
    """Downgrade database by a number of steps."""
    return run_alembic_command(['downgrade', f'-{steps}'])

def show_history():
    """Show migration history."""
    return run_alembic_command(['history'])

def show_current():
    """Show current revision."""
    return run_alembic_command(['current'])

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'generate':
        if len(sys.argv) < 3:
            logger.error("Missing migration description")
            print("Usage: python migrate.py generate \"Description of changes\"")
            return
        description = sys.argv[2]
        generate_migration(description)
    
    elif command == 'upgrade':
        upgrade_database()
    
    elif command == 'downgrade':
        steps = 1
        if len(sys.argv) >= 3:
            try:
                steps = int(sys.argv[2])
            except ValueError:
                logger.error("Invalid number of steps")
                print("Usage: python migrate.py downgrade [steps]")
                return
        downgrade_database(steps)
    
    elif command == 'history':
        show_history()
    
    elif command == 'current':
        show_current()
    
    else:
        logger.error(f"Unknown command: {command}")
        print(__doc__)

if __name__ == "__main__":
    main() 