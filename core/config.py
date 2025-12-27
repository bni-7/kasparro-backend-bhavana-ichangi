"""Configuration management using Pydantic settings."""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    
    # PostgreSQL Configuration (for Docker Compose)
    postgres_user: Optional[str] = Field(None, env="POSTGRES_USER")
    postgres_password: Optional[str] = Field(None, env="POSTGRES_PASSWORD")
    postgres_db: Optional[str] = Field(None, env="POSTGRES_DB")
    
    # API Keys
    coinpaprika_api_key: Optional[str] = Field(None, env="COINPAPRIKA_API_KEY")
    
    # API Configuration
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    
    # ETL Configuration
    coinpaprika_base_url: str = Field(
        "https://api.coinpaprika.com/v1",
        env="COINPAPRIKA_BASE_URL"
    )
    coingecko_base_url: str = Field(
        "https://api.coingecko.com/api/v3",
        env="COINGECKO_BASE_URL"
    )
    csv_file_path: str = Field("data/sample.csv", env="CSV_FILE_PATH")
    
    # Rate Limiting
    max_retries: int = Field(3, env="MAX_RETRIES")
    initial_retry_delay: float = Field(1.0, env="INITIAL_RETRY_DELAY")
    max_retry_delay: float = Field(60.0, env="MAX_RETRY_DELAY")
    rate_limit_delay: float = Field(0.5, env="RATE_LIMIT_DELAY")
    
    # Pagination
    default_page_size: int = Field(100, env="DEFAULT_PAGE_SIZE")
    max_page_size: int = Field(1000, env="MAX_PAGE_SIZE")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()
