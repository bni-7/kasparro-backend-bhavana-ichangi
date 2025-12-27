"""Database models and connection management."""
from datetime import datetime
from typing import Generator
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    DateTime,
    Integer,
    Text,
    Index,
    text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from core.config import settings

Base = declarative_base()


class RawCoinPaprika(Base):
    """Raw data from CoinPaprika API."""
    
    __tablename__ = "raw_coinpaprika"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(String(100), nullable=False)
    name = Column(String(255))
    symbol = Column(String(50))
    rank = Column(Integer)
    price_usd = Column(Float)
    market_cap = Column(Float)
    volume_24h = Column(Float)
    circulating_supply = Column(Float)
    total_supply = Column(Float)
    max_supply = Column(Float)
    percent_change_24h = Column(Float)
    raw_json = Column(Text)
    ingested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("idx_coinpaprika_coin_id", "coin_id"),
        Index("idx_coinpaprika_ingested", "ingested_at"),
    )


class RawCoinGecko(Base):
    """Raw data from CoinGecko API."""
    
    __tablename__ = "raw_coingecko"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(String(100), nullable=False)
    name = Column(String(255))
    symbol = Column(String(50))
    current_price = Column(Float)
    market_cap = Column(Float)
    total_volume = Column(Float)
    price_change_24h = Column(Float)
    price_change_percentage_24h = Column(Float)
    market_cap_rank = Column(Integer)
    raw_json = Column(Text)
    ingested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("idx_coingecko_coin_id", "coin_id"),
        Index("idx_coingecko_ingested", "ingested_at"),
    )


class RawCSV(Base):
    """Raw data from CSV file."""
    
    __tablename__ = "raw_csv"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(String(100), nullable=False)
    name = Column(String(255))
    symbol = Column(String(50))
    price_usd = Column(Float)
    market_cap = Column(Float)
    volume_24h = Column(Float)
    ingested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("idx_csv_coin_id", "coin_id"),
        Index("idx_csv_ingested", "ingested_at"),
    )


class UnifiedCryptoData(Base):
    """Unified normalized cryptocurrency data."""
    
    __tablename__ = "unified_crypto_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    symbol = Column(String(50), nullable=False)
    price_usd = Column(Float)
    market_cap = Column(Float)
    volume_24h = Column(Float)
    source = Column(String(50), nullable=False)
    ingested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("idx_unified_coin_id", "coin_id"),
        Index("idx_unified_source", "source"),
        Index("idx_unified_ingested", "ingested_at"),
        Index("idx_unified_coin_source", "coin_id", "source", "ingested_at"),
        UniqueConstraint("coin_id", "source", "ingested_at", name="uq_coin_source_time"),
    )


class Checkpoint(Base):
    """ETL checkpoint tracking."""
    
    __tablename__ = "checkpoints"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False, unique=True)
    last_run_timestamp = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)  # success, failure, running
    records_processed = Column(Integer, default=0)
    duration_seconds = Column(Float)
    error_message = Column(Text)
    
    __table_args__ = (
        Index("idx_checkpoint_source", "source"),
    )


# Database engine and session
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Check database connectivity."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Database connection failed: {e}")
        return False
