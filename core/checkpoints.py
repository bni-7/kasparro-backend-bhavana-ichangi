"""Checkpoint management for ETL pipeline."""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from core.database import Checkpoint
import logging

logger = logging.getLogger(__name__)


class CheckpointManager:
    """Manage ETL checkpoints for incremental ingestion."""
    
    def __init__(self, db: Session):
        """Initialize checkpoint manager."""
        self.db = db
    
    def get_checkpoint(self, source: str) -> Optional[Checkpoint]:
        """Get checkpoint for a source."""
        return self.db.query(Checkpoint).filter(
            Checkpoint.source == source
        ).first()
    
    def get_last_successful_run(self, source: str) -> Optional[datetime]:
        """Get timestamp of last successful run."""
        checkpoint = self.get_checkpoint(source)
        if checkpoint and checkpoint.status == "success":
            return checkpoint.last_run_timestamp
        return None
    
    def start_run(self, source: str) -> Checkpoint:
        """Mark start of ETL run."""
        checkpoint = self.get_checkpoint(source)
        
        if checkpoint:
            checkpoint.status = "running"
            checkpoint.last_run_timestamp = datetime.utcnow()
            checkpoint.error_message = None
        else:
            checkpoint = Checkpoint(
                source=source,
                last_run_timestamp=datetime.utcnow(),
                status="running",
                records_processed=0
            )
            self.db.add(checkpoint)
        
        self.db.commit()
        logger.info(f"Started ETL run for source: {source}")
        return checkpoint
    
    def complete_run(
        self,
        source: str,
        records_processed: int,
        duration_seconds: float,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> None:
        """Mark completion of ETL run."""
        checkpoint = self.get_checkpoint(source)
        
        if not checkpoint:
            logger.error(f"No checkpoint found for source: {source}")
            return
        
        checkpoint.status = "success" if success else "failure"
        checkpoint.records_processed = records_processed
        checkpoint.duration_seconds = duration_seconds
        checkpoint.error_message = error_message
        
        self.db.commit()
        
        status_msg = "successfully" if success else "with failure"
        logger.info(
            f"Completed ETL run for {source} {status_msg}. "
            f"Processed {records_processed} records in {duration_seconds:.2f}s"
        )
    
    def get_all_checkpoints(self) -> list[Checkpoint]:
        """Get all checkpoints."""
        return self.db.query(Checkpoint).all()
    
    def is_source_running(self, source: str) -> bool:
        """Check if source is currently running."""
        checkpoint = self.get_checkpoint(source)
        return checkpoint is not None and checkpoint.status == "running"
