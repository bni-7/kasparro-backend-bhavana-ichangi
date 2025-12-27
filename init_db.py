"""Initialize database schema manually (optional).

This script creates all database tables.
Normally, tables are created automatically on first API startup.
Use this script if you need to initialize the database separately.
"""
import sys
import logging
import time
from core.database import init_db, check_db_connection
from core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Initialize database schema."""
    logger.info("Starting database initialization...")
    logger.info(f"Database URL: {settings.database_url.split('@')[-1]}")  # Hide credentials
    
    # Check connection with retries
    logger.info("Checking database connection...")
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(1, max_retries + 1):
        if check_db_connection():
            logger.info(f"Database connection successful on attempt {attempt}")
            break
        else:
            if attempt < max_retries:
                logger.warning(f"Connection attempt {attempt} failed, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to connect to database after all retries.")
                logger.error("Make sure PostgreSQL is running and accessible.")
                sys.exit(1)
    
    logger.info("✓ Database connection successful")
    
    # Initialize tables
    try:
        logger.info("Creating database tables...")
        init_db()
        logger.info("✓ Database tables created successfully")
        
        logger.info("\nCreated tables:")
        logger.info("  - raw_coinpaprika")
        logger.info("  - raw_coingecko")
        logger.info("  - raw_csv")
        logger.info("  - unified_crypto_data")
        logger.info("  - checkpoints")
        
        logger.info("\n✅ Database initialization complete!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
