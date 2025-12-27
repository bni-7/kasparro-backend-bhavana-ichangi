"""ETL pipeline orchestrator."""
import logging
import time
from datetime import datetime
from sqlalchemy.orm import Session
from core.database import SessionLocal
from core.checkpoints import CheckpointManager
from core.config import settings
from ingestion.sources.coinpaprika import CoinPaprikaSource
from ingestion.sources.coingecko import CoinGeckoSource
from ingestion.sources.csv import CSVSource
from ingestion.transformer import DataTransformer
from ingestion.loader import DataLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class ETLPipeline:
    """ETL pipeline orchestrator."""
    
    def __init__(self, db: Session):
        """Initialize ETL pipeline."""
        self.db = db
        self.checkpoint_manager = CheckpointManager(db)
        self.loader = DataLoader(db)
        self.transformer = DataTransformer()
    
    def run_coinpaprika(self) -> None:
        """Run CoinPaprika ETL pipeline."""
        source_name = "coinpaprika"
        start_time = time.time()
        
        try:
            logger.info(f"Starting {source_name} ETL pipeline...")
            
            # Check if already running
            if self.checkpoint_manager.is_source_running(source_name):
                logger.warning(f"{source_name} is already running. Skipping.")
                return
            
            # Start checkpoint
            self.checkpoint_manager.start_run(source_name)
            
            # Extract
            source = CoinPaprikaSource()
            raw_data = source.fetch_top_coins(limit=10)
            
            if not raw_data:
                logger.warning(f"No data fetched from {source_name}")
                duration = time.time() - start_time
                self.checkpoint_manager.complete_run(
                    source_name, 0, duration, success=True
                )
                return
            
            # Load raw data
            raw_count = self.loader.load_raw_coinpaprika(raw_data)
            
            # Transform
            unified_data = self.transformer.transform_batch_coinpaprika(raw_data)
            
            # Load unified data
            unified_count = self.loader.load_unified_data(unified_data)
            
            # Complete checkpoint
            duration = time.time() - start_time
            self.checkpoint_manager.complete_run(
                source_name, unified_count, duration, success=True
            )
            
            logger.info(
                f"Completed {source_name} ETL: {unified_count} records in {duration:.2f}s"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Failed {source_name} ETL: {error_msg}")
            
            self.checkpoint_manager.complete_run(
                source_name, 0, duration, success=False, error_message=error_msg
            )
    
    def run_coingecko(self) -> None:
        """Run CoinGecko ETL pipeline."""
        source_name = "coingecko"
        start_time = time.time()
        
        try:
            logger.info(f"Starting {source_name} ETL pipeline...")
            
            # Check if already running
            if self.checkpoint_manager.is_source_running(source_name):
                logger.warning(f"{source_name} is already running. Skipping.")
                return
            
            # Start checkpoint
            self.checkpoint_manager.start_run(source_name)
            
            # Extract
            source = CoinGeckoSource()
            raw_data = source.fetch_markets_data(per_page=10)
            
            if not raw_data:
                logger.warning(f"No data fetched from {source_name}")
                duration = time.time() - start_time
                self.checkpoint_manager.complete_run(
                    source_name, 0, duration, success=True
                )
                return
            
            # Load raw data
            raw_count = self.loader.load_raw_coingecko(raw_data)
            
            # Transform
            unified_data = self.transformer.transform_batch_coingecko(raw_data)
            
            # Load unified data
            unified_count = self.loader.load_unified_data(unified_data)
            
            # Complete checkpoint
            duration = time.time() - start_time
            self.checkpoint_manager.complete_run(
                source_name, unified_count, duration, success=True
            )
            
            logger.info(
                f"Completed {source_name} ETL: {unified_count} records in {duration:.2f}s"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Failed {source_name} ETL: {error_msg}")
            
            self.checkpoint_manager.complete_run(
                source_name, 0, duration, success=False, error_message=error_msg
            )
    
    def run_csv(self) -> None:
        """Run CSV ETL pipeline."""
        source_name = "csv"
        start_time = time.time()
        
        try:
            logger.info(f"Starting {source_name} ETL pipeline...")
            
            # Check if already running
            if self.checkpoint_manager.is_source_running(source_name):
                logger.warning(f"{source_name} is already running. Skipping.")
                return
            
            # Start checkpoint
            self.checkpoint_manager.start_run(source_name)
            
            # Extract
            source = CSVSource(settings.csv_file_path)
            raw_data = source.fetch_data()
            
            if not raw_data:
                logger.warning(f"No data fetched from {source_name}")
                duration = time.time() - start_time
                self.checkpoint_manager.complete_run(
                    source_name, 0, duration, success=True
                )
                return
            
            # Load raw data
            raw_count = self.loader.load_raw_csv(raw_data)
            
            # Transform
            unified_data = self.transformer.transform_batch_csv(raw_data)
            
            # Load unified data
            unified_count = self.loader.load_unified_data(unified_data)
            
            # Complete checkpoint
            duration = time.time() - start_time
            self.checkpoint_manager.complete_run(
                source_name, unified_count, duration, success=True
            )
            
            logger.info(
                f"Completed {source_name} ETL: {unified_count} records in {duration:.2f}s"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Failed {source_name} ETL: {error_msg}")
            
            self.checkpoint_manager.complete_run(
                source_name, 0, duration, success=False, error_message=error_msg
            )
    
    def run_all(self) -> None:
        """Run all ETL pipelines."""
        logger.info("Starting all ETL pipelines...")
        
        self.run_coinpaprika()
        self.run_coingecko()
        self.run_csv()
        
        logger.info("Completed all ETL pipelines")


def main():
    """Main ETL entry point."""
    logger.info("ETL Pipeline starting...")
    
    db = SessionLocal()
    
    try:
        pipeline = ETLPipeline(db)
        pipeline.run_all()
    except Exception as e:
        logger.error(f"ETL pipeline failed: {str(e)}")
        raise
    finally:
        db.close()
    
    logger.info("ETL Pipeline completed")


if __name__ == "__main__":
    main()
