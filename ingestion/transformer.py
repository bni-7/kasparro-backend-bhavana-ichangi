"""Data transformation from raw to unified schema."""
import logging
from typing import List
from schemas.raw_data import RawCoinPaprikaSchema, RawCoinGeckoSchema, RawCSVSchema
from schemas.unified import UnifiedCryptoDataSchema

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transform raw data to unified schema."""
    
    @staticmethod
    def transform_coinpaprika(raw_data: RawCoinPaprikaSchema) -> UnifiedCryptoDataSchema:
        """Transform CoinPaprika data to unified schema."""
        return UnifiedCryptoDataSchema(
            coin_id=raw_data.coin_id,
            name=raw_data.name or "",
            symbol=raw_data.symbol or "",
            price_usd=raw_data.price_usd,
            market_cap=raw_data.market_cap,
            volume_24h=raw_data.volume_24h,
            source="coinpaprika",
            ingested_at=raw_data.ingested_at
        )
    
    @staticmethod
    def transform_coingecko(raw_data: RawCoinGeckoSchema) -> UnifiedCryptoDataSchema:
        """Transform CoinGecko data to unified schema."""
        return UnifiedCryptoDataSchema(
            coin_id=raw_data.coin_id,
            name=raw_data.name or "",
            symbol=raw_data.symbol or "",
            price_usd=raw_data.current_price,
            market_cap=raw_data.market_cap,
            volume_24h=raw_data.total_volume,
            source="coingecko",
            ingested_at=raw_data.ingested_at
        )
    
    @staticmethod
    def transform_csv(raw_data: RawCSVSchema) -> UnifiedCryptoDataSchema:
        """Transform CSV data to unified schema."""
        return UnifiedCryptoDataSchema(
            coin_id=raw_data.coin_id,
            name=raw_data.name,
            symbol=raw_data.symbol,
            price_usd=raw_data.price_usd,
            market_cap=raw_data.market_cap,
            volume_24h=raw_data.volume_24h,
            source="csv",
            ingested_at=raw_data.ingested_at
        )
    
    @staticmethod
    def transform_batch_coinpaprika(
        raw_data_list: List[RawCoinPaprikaSchema]
    ) -> List[UnifiedCryptoDataSchema]:
        """Transform batch of CoinPaprika data."""
        results = []
        for raw_data in raw_data_list:
            try:
                unified = DataTransformer.transform_coinpaprika(raw_data)
                results.append(unified)
            except Exception as e:
                logger.error(f"Failed to transform CoinPaprika data: {str(e)}")
        return results
    
    @staticmethod
    def transform_batch_coingecko(
        raw_data_list: List[RawCoinGeckoSchema]
    ) -> List[UnifiedCryptoDataSchema]:
        """Transform batch of CoinGecko data."""
        results = []
        for raw_data in raw_data_list:
            try:
                unified = DataTransformer.transform_coingecko(raw_data)
                results.append(unified)
            except Exception as e:
                logger.error(f"Failed to transform CoinGecko data: {str(e)}")
        return results
    
    @staticmethod
    def transform_batch_csv(
        raw_data_list: List[RawCSVSchema]
    ) -> List[UnifiedCryptoDataSchema]:
        """Transform batch of CSV data."""
        results = []
        for raw_data in raw_data_list:
            try:
                unified = DataTransformer.transform_csv(raw_data)
                results.append(unified)
            except Exception as e:
                logger.error(f"Failed to transform CSV data: {str(e)}")
        return results
