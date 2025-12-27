"""Tests for ETL transformations and incremental ingestion."""
import pytest
from datetime import datetime
from schemas.raw_data import RawCoinPaprikaSchema, RawCoinGeckoSchema, RawCSVSchema
from schemas.unified import UnifiedCryptoDataSchema
from ingestion.transformer import DataTransformer


class TestDataTransformer:
    """Test data transformation logic."""
    
    def test_transform_coinpaprika(self):
        """Test CoinPaprika transformation."""
        raw_data = RawCoinPaprikaSchema(
            coin_id="btc-bitcoin",
            name="Bitcoin",
            symbol="BTC",
            rank=1,
            price_usd=45000.0,
            market_cap=850000000000.0,
            volume_24h=25000000000.0,
            ingested_at=datetime.utcnow()
        )
        
        unified = DataTransformer.transform_coinpaprika(raw_data)
        
        assert unified.coin_id == "btc-bitcoin"
        assert unified.name == "Bitcoin"
        assert unified.symbol == "BTC"
        assert unified.price_usd == 45000.0
        assert unified.source == "coinpaprika"
    
    def test_transform_coingecko(self):
        """Test CoinGecko transformation."""
        raw_data = RawCoinGeckoSchema(
            coin_id="bitcoin",
            name="Bitcoin",
            symbol="btc",
            current_price=45000.0,
            market_cap=850000000000.0,
            total_volume=25000000000.0,
            ingested_at=datetime.utcnow()
        )
        
        unified = DataTransformer.transform_coingecko(raw_data)
        
        assert unified.coin_id == "bitcoin"
        assert unified.name == "Bitcoin"
        assert unified.symbol == "btc"
        assert unified.price_usd == 45000.0
        assert unified.source == "coingecko"
    
    def test_transform_csv(self):
        """Test CSV transformation."""
        raw_data = RawCSVSchema(
            coin_id="btc-bitcoin",
            name="Bitcoin",
            symbol="BTC",
            price_usd=45000.0,
            market_cap=850000000000.0,
            volume_24h=25000000000.0,
            ingested_at=datetime.utcnow()
        )
        
        unified = DataTransformer.transform_csv(raw_data)
        
        assert unified.coin_id == "btc-bitcoin"
        assert unified.name == "Bitcoin"
        assert unified.symbol == "BTC"
        assert unified.price_usd == 45000.0
        assert unified.source == "csv"
    
    def test_transform_batch_coinpaprika(self):
        """Test batch transformation for CoinPaprika."""
        raw_data_list = [
            RawCoinPaprikaSchema(
                coin_id=f"coin-{i}",
                name=f"Coin {i}",
                symbol=f"C{i}",
                price_usd=float(i * 1000),
                ingested_at=datetime.utcnow()
            )
            for i in range(3)
        ]
        
        unified_list = DataTransformer.transform_batch_coinpaprika(raw_data_list)
        
        assert len(unified_list) == 3
        assert all(u.source == "coinpaprika" for u in unified_list)
        assert unified_list[0].coin_id == "coin-0"
        assert unified_list[2].price_usd == 2000.0
    
    def test_transform_with_missing_data(self):
        """Test transformation with missing optional fields."""
        raw_data = RawCoinPaprikaSchema(
            coin_id="test-coin",
            name="Test",
            symbol="TST",
            price_usd=None,
            market_cap=None,
            volume_24h=None,
            ingested_at=datetime.utcnow()
        )
        
        unified = DataTransformer.transform_coinpaprika(raw_data)
        
        assert unified.coin_id == "test-coin"
        assert unified.price_usd is None
        assert unified.market_cap is None
        assert unified.volume_24h is None


class TestIncrementalIngestion:
    """Test incremental ingestion logic."""
    
    def test_schema_validation(self):
        """Test Pydantic schema validation."""
        # Valid data
        valid_data = UnifiedCryptoDataSchema(
            coin_id="btc",
            name="Bitcoin",
            symbol="BTC",
            price_usd=45000.0,
            source="coinpaprika"
        )
        assert valid_data.coin_id == "btc"
        
        # Invalid source
        with pytest.raises(Exception):
            UnifiedCryptoDataSchema(
                coin_id="btc",
                name="Bitcoin",
                symbol="BTC",
                source="invalid_source"
            )
    
    def test_timestamp_generation(self):
        """Test automatic timestamp generation."""
        data = UnifiedCryptoDataSchema(
            coin_id="btc",
            name="Bitcoin",
            symbol="BTC",
            source="csv"
        )
        
        assert data.ingested_at is not None
        assert isinstance(data.ingested_at, datetime)
