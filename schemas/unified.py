"""Pydantic schemas for unified data."""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class UnifiedCryptoDataSchema(BaseModel):
    """Schema for unified cryptocurrency data."""
    
    coin_id: str = Field(..., description="Unique coin identifier")
    name: str = Field(..., description="Coin name")
    symbol: str = Field(..., description="Coin symbol")
    price_usd: Optional[float] = Field(None, description="Price in USD")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    volume_24h: Optional[float] = Field(None, description="24h trading volume")
    source: Literal["coinpaprika", "coingecko", "csv"] = Field(
        ..., description="Data source"
    )
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class UnifiedCryptoDataResponse(BaseModel):
    """Response schema for unified cryptocurrency data."""
    
    id: int
    coin_id: str
    name: str
    symbol: str
    price_usd: Optional[float]
    market_cap: Optional[float]
    volume_24h: Optional[float]
    source: str
    ingested_at: datetime
    
    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    
    data: list[UnifiedCryptoDataResponse]
    total: int
    page: int
    page_size: int
    request_id: str
    api_latency_ms: float
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    database_connected: bool
    etl_last_run: Optional[dict]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatsResponse(BaseModel):
    """ETL statistics response."""
    
    source: str
    records_processed: int
    duration_seconds: Optional[float]
    last_success_timestamp: Optional[datetime]
    last_failure_timestamp: Optional[datetime]
    status: str
    
    class Config:
        from_attributes = True


class ETLStatsResponse(BaseModel):
    """Complete ETL statistics response."""
    
    sources: list[StatsResponse]
    total_records: int
    request_id: str
    api_latency_ms: float
