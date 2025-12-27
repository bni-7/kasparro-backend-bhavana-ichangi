"""Run ETL pipeline on a schedule.

This script runs the ETL pipeline at regular intervals.
Useful for keeping data up-to-date automatically.

Usage:
    python run_etl_scheduled.py --interval 3600  # Run every hour
    python run_etl_scheduled.py --interval 900   # Run every 15 minutes
"""
import argparse
import time
import logging
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from core.database import SessionLocal
from etl_pipeline import ETLPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def run_etl_with_error_handling(db: Session) -> bool:
    """Run ETL pipeline with error handling."""
    try:
        logger.info("=" * 60)
        logger.info(f"Starting scheduled ETL run at {datetime.utcnow()}")
        logger.info("=" * 60)
        
        pipeline = ETLPipeline(db)
        pipeline.run_all()
        
        logger.info("=" * 60)
        logger.info(f"Completed scheduled ETL run at {datetime.utcnow()}")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"ETL pipeline failed: {str(e)}", exc_info=True)
        return False


def main():
    """Main entry point for scheduled ETL."""
    parser = argparse.ArgumentParser(description="Run ETL pipeline on a schedule")
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Interval in seconds between runs (default: 3600 = 1 hour)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (no scheduling)"
    )
    
    args = parser.parse_args()
    
    logger.info(f"ETL Scheduler starting...")
    if args.once:
        logger.info("Running ETL once (no scheduling)")
    else:
        logger.info(f"ETL will run every {args.interval} seconds ({args.interval/60:.1f} minutes)")
    
    run_count = 0
    
    while True:
        run_count += 1
        logger.info(f"\n{'=' * 60}")
        logger.info(f"ETL Run #{run_count}")
        logger.info(f"{'=' * 60}\n")
        
        db = SessionLocal()
        try:
            success = run_etl_with_error_handling(db)
            
            if success:
                logger.info("✅ ETL run completed successfully")
            else:
                logger.warning("⚠️ ETL run completed with errors")
                
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Received interrupt signal. Shutting down...")
            db.close()
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            
        finally:
            db.close()
        
        # Exit if running once
        if args.once:
            logger.info("\nRun completed. Exiting (--once mode).")
            break
        
        # Wait for next run
        logger.info(f"\n⏳ Waiting {args.interval} seconds until next run...")
        logger.info(f"Next run scheduled for: {datetime.utcnow().replace(microsecond=0)}")
        
        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Received interrupt signal. Shutting down...")
            sys.exit(0)


if __name__ == "__main__":
    main()
