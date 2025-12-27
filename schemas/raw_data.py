"""Pydantic schemas for raw data sources."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RawCoinPaprikaSchema(BaseModel):
    """Schema for raw CoinPaprika data."""
    
    coin_id: str = Field(..., description="Unique coin identifier")
    name: Optional[str] = Field(None, description="Coin name")
    symbol: Optional[str] = Field(None, description="Coin symbol")
    rank: Optional[int] = Field(None, description="Market rank")
    price_usd: Optional[float] = Field(None, description="Price in USD")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    volume_24h: Optional[float] = Field(None, description="24h trading volume")
    circulating_supply: Optional[float] = Field(None, description="Circulating supply")
    total_supply: Optional[float] = Field(None, description="Total supply")
    max_supply: Optional[float] = Field(None, description="Maximum supply")
    percent_change_24h: Optional[float] = Field(None, description="24h price change %")
    raw_json: Optional[str] = Field(None, description="Raw JSON response")
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class RawCoinGeckoSchema(BaseModel):
    """Schema for raw CoinGecko data."""
    
    coin_id: str = Field(..., description="Unique coin identifier")
    name: Optional[str] = Field(None, description="Coin name")
    symbol: Optional[str] = Field(None, description="Coin symbol")
    current_price: Optional[float] = Field(None, description="Current price")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    total_volume: Optional[float] = Field(None, description="Total volume")
    price_change_24h: Optional[float] = Field(None, description="24h price change")
    price_change_percentage_24h: Optional[float] = Field(None, description="24h change %")
    market_cap_rank: Optional[int] = Field(None, description="Market cap rank")
    raw_json: Optional[str] = Field(None, description="Raw JSON response")
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class RawCSVSchema(BaseModel):
    """Schema for raw CSV data."""
    
    coin_id: str = Field(..., description="Unique coin identifier")
    name: str = Field(..., description="Coin name")
    symbol: str = Field(..., description="Coin symbol")
    price_usd: Optional[float] = Field(None, description="Price in USD")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    volume_24h: Optional[float] = Field(None, description="24h trading volume")
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True
