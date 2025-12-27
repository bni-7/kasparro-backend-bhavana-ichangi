"""Data loader with incremental ingestion and upsert logic."""
import logging
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from core.database import (
    RawCoinPaprika,
    RawCoinGecko,
    RawCSV,
    UnifiedCryptoData
)
from schemas.raw_data import RawCoinPaprikaSchema, RawCoinGeckoSchema, RawCSVSchema
from schemas.unified import UnifiedCryptoDataSchema

logger = logging.getLogger(__name__)


class DataLoader:
    """Load data into database with upsert logic."""
    
    def __init__(self, db: Session):
        """Initialize data loader."""
        self.db = db
    
    def load_raw_coinpaprika(
        self,
        data_list: List[RawCoinPaprikaSchema]
    ) -> int:
        """Load raw CoinPaprika data with upsert."""
        if not data_list:
            return 0
        
        try:
            records = [
                RawCoinPaprika(
                    coin_id=data.coin_id,
                    name=data.name,
                    symbol=data.symbol,
                    rank=data.rank,
                    price_usd=data.price_usd,
                    market_cap=data.market_cap,
                    volume_24h=data.volume_24h,
                    circulating_supply=data.circulating_supply,
                    total_supply=data.total_supply,
                    max_supply=data.max_supply,
                    percent_change_24h=data.percent_change_24h,
                    raw_json=data.raw_json,
                    ingested_at=data.ingested_at
                )
                for data in data_list
            ]
            
            self.db.bulk_save_objects(records)
            self.db.commit()
            
            logger.info(f"Loaded {len(records)} raw CoinPaprika records")
            return len(records)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to load raw CoinPaprika data: {str(e)}")
            raise
    
    def load_raw_coingecko(
        self,
        data_list: List[RawCoinGeckoSchema]
    ) -> int:
        """Load raw CoinGecko data."""
        if not data_list:
            return 0
        
        try:
            records = [
                RawCoinGecko(
                    coin_id=data.coin_id,
                    name=data.name,
                    symbol=data.symbol,
                    current_price=data.current_price,
                    market_cap=data.market_cap,
                    total_volume=data.total_volume,
                    price_change_24h=data.price_change_24h,
                    price_change_percentage_24h=data.price_change_percentage_24h,
                    market_cap_rank=data.market_cap_rank,
                    raw_json=data.raw_json,
                    ingested_at=data.ingested_at
                )
                for data in data_list
            ]
            
            self.db.bulk_save_objects(records)
            self.db.commit()
            
            logger.info(f"Loaded {len(records)} raw CoinGecko records")
            return len(records)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to load raw CoinGecko data: {str(e)}")
            raise
    
    def load_raw_csv(
        self,
        data_list: List[RawCSVSchema]
    ) -> int:
        """Load raw CSV data."""
        if not data_list:
            return 0
        
        try:
            records = [
                RawCSV(
                    coin_id=data.coin_id,
                    name=data.name,
                    symbol=data.symbol,
                    price_usd=data.price_usd,
                    market_cap=data.market_cap,
                    volume_24h=data.volume_24h,
                    ingested_at=data.ingested_at
                )
                for data in data_list
            ]
            
            self.db.bulk_save_objects(records)
            self.db.commit()
            
            logger.info(f"Loaded {len(records)} raw CSV records")
            return len(records)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to load raw CSV data: {str(e)}")
            raise
    
    def load_unified_data(
        self,
        data_list: List[UnifiedCryptoDataSchema]
    ) -> int:
        """Load unified data with upsert logic (idempotent)."""
        if not data_list:
            return 0
        
        try:
            # Use PostgreSQL INSERT ... ON CONFLICT for upsert
            for data in data_list:
                stmt = insert(UnifiedCryptoData).values(
                    coin_id=data.coin_id,
                    name=data.name,
                    symbol=data.symbol,
                    price_usd=data.price_usd,
                    market_cap=data.market_cap,
                    volume_24h=data.volume_24h,
                    source=data.source,
                    ingested_at=data.ingested_at
                )
                
                # On conflict, update the record (idempotent upsert)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['coin_id', 'source', 'ingested_at'],
                    set_=dict(
                        name=stmt.excluded.name,
                        symbol=stmt.excluded.symbol,
                        price_usd=stmt.excluded.price_usd,
                        market_cap=stmt.excluded.market_cap,
                        volume_24h=stmt.excluded.volume_24h,
                    )
                )
                
                self.db.execute(stmt)
            
            self.db.commit()
            
            logger.info(f"Loaded {len(data_list)} unified records")
            return len(data_list)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to load unified data: {str(e)}")
            raise
    
    def get_last_ingestion_time(self, source: str) -> datetime:
        """Get timestamp of last successful ingestion for a source."""
        try:
            result = self.db.query(UnifiedCryptoData.ingested_at).filter(
                UnifiedCryptoData.source == source
            ).order_by(UnifiedCryptoData.ingested_at.desc()).first()
            
            if result:
                return result[0]
            
            # Return epoch if no previous ingestion
            return datetime(1970, 1, 1)
            
        except Exception as e:
            logger.error(f"Failed to get last ingestion time: {str(e)}")
            return datetime(1970, 1, 1)
