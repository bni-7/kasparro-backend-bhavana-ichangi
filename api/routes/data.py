"""API routes for cryptocurrency data."""
import time
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import get_db, UnifiedCryptoData, check_db_connection
from core.checkpoints import CheckpointManager
from schemas.unified import (
    PaginatedResponse,
    UnifiedCryptoDataResponse,
    HealthResponse,
    StatsResponse,
    ETLStatsResponse
)
from core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/data", response_model=PaginatedResponse)
async def get_data(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Items per page"),
    source: Optional[str] = Query(None, description="Filter by source"),
    coin_id: Optional[str] = Query(None, description="Filter by coin ID"),
    db: Session = Depends(get_db)
):
    """
    Get cryptocurrency data with pagination and filtering.
    
    Returns:
        - data: List of cryptocurrency records
        - total: Total number of records
        - page: Current page number
        - page_size: Items per page
        - request_id: Unique request identifier
        - api_latency_ms: API response time in milliseconds
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        # Build query
        query = db.query(UnifiedCryptoData)
        
        # Apply filters
        if source:
            query = query.filter(UnifiedCryptoData.source == source)
        
        if coin_id:
            query = query.filter(UnifiedCryptoData.coin_id == coin_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        data = query.order_by(
            UnifiedCryptoData.ingested_at.desc()
        ).offset(offset).limit(page_size).all()
        
        # Convert to response schema
        data_response = [
            UnifiedCryptoDataResponse(
                id=item.id,
                coin_id=item.coin_id,
                name=item.name,
                symbol=item.symbol,
                price_usd=item.price_usd,
                market_cap=item.market_cap,
                volume_24h=item.volume_24h,
                source=item.source,
                ingested_at=item.ingested_at
            )
            for item in data
        ]
        
        latency_ms = (time.time() - start_time) * 1000
        
        return PaginatedResponse(
            data=data_response,
            total=total,
            page=page,
            page_size=page_size,
            request_id=request_id,
            api_latency_ms=round(latency_ms, 2)
        )
        
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    
    Returns:
        - status: Overall health status
        - database_connected: Database connectivity status
        - etl_last_run: Information about last ETL run
    """
    try:
        # Check database connectivity
        db_connected = check_db_connection()
        
        # Get last ETL run info
        checkpoint_manager = CheckpointManager(db)
        checkpoints = checkpoint_manager.get_all_checkpoints()
        
        etl_last_run = None
        if checkpoints:
            latest = max(checkpoints, key=lambda x: x.last_run_timestamp)
            etl_last_run = {
                "source": latest.source,
                "timestamp": latest.last_run_timestamp.isoformat(),
                "status": latest.status,
                "records_processed": latest.records_processed
            }
        
        status = "healthy" if db_connected else "unhealthy"
        
        return HealthResponse(
            status=status,
            database_connected=db_connected,
            etl_last_run=etl_last_run
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            database_connected=False,
            etl_last_run=None
        )


@router.get("/stats", response_model=ETLStatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """
    Get ETL statistics.
    
    Returns:
        - sources: List of source statistics
        - total_records: Total records across all sources
        - request_id: Unique request identifier
        - api_latency_ms: API response time in milliseconds
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        checkpoint_manager = CheckpointManager(db)
        checkpoints = checkpoint_manager.get_all_checkpoints()
        
        # Get success/failure timestamps per source
        stats_list = []
        total_records = 0
        
        for checkpoint in checkpoints:
            # Determine last success and failure timestamps
            last_success = None
            last_failure = None
            
            if checkpoint.status == "success":
                last_success = checkpoint.last_run_timestamp
            elif checkpoint.status == "failure":
                last_failure = checkpoint.last_run_timestamp
            
            stats_list.append(
                StatsResponse(
                    source=checkpoint.source,
                    records_processed=checkpoint.records_processed,
                    duration_seconds=checkpoint.duration_seconds,
                    last_success_timestamp=last_success,
                    last_failure_timestamp=last_failure,
                    status=checkpoint.status
                )
            )
            
            total_records += checkpoint.records_processed
        
        latency_ms = (time.time() - start_time) * 1000
        
        return ETLStatsResponse(
            sources=stats_list,
            total_records=total_records,
            request_id=request_id,
            api_latency_ms=round(latency_ms, 2)
        )
        
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
