"""
Startup check to verify database connection
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
if Path("/app").exists() and Path("/app/database").exists():
    project_root = Path("/app")
else:
    project_root = Path(__file__).parent.parent

sys.path.insert(0, str(project_root))

from database.base import get_session
from config.settings import settings
import logging
import time

logger = logging.getLogger(__name__)

def check_database_connection(max_retries=30, retry_delay=2):
    """Check database connection with retries"""
    logger.info(f"Checking database connection to: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'unknown'}")
    
    for attempt in range(max_retries):
        try:
            from sqlalchemy import text
            with get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database connection successful!")
            return True
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                return False
    
    return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = check_database_connection()
    sys.exit(0 if success else 1)

