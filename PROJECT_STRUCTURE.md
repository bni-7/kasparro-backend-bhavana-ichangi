# Project Structure

```
kasparro/
│
├── api/                          # FastAPI application
│   ├── __init__.py
│   ├── main.py                   # FastAPI app initialization
│   └── routes/
│       ├── __init__.py
│       └── data.py               # API endpoints (/data, /health, /stats)
│
├── core/                         # Core configuration and database
│   ├── __init__.py
│   ├── config.py                 # Settings with Pydantic
│   ├── database.py               # SQLAlchemy models and connection
│   └── checkpoints.py            # Checkpoint management for ETL
│
├── ingestion/                    # ETL components
│   ├── __init__.py
│   ├── transformer.py            # Data transformation logic
│   ├── loader.py                 # Data loading with upsert
│   └── sources/                  # Data source implementations
│       ├── __init__.py
│       ├── coinpaprika.py        # CoinPaprika API client
│       ├── coingecko.py          # CoinGecko API client
│       └── csv.py                # CSV file reader
│
├── schemas/                      # Pydantic schemas
│   ├── __init__.py
│   ├── raw_data.py               # Raw data schemas
│   └── unified.py                # Unified data and API response schemas
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   ├── test_etl.py               # ETL transformation tests
│   ├── test_api.py               # API endpoint tests
│   └── test_recovery.py          # Failure recovery tests
│
├── data/                         # Data files
│   └── sample.csv                # Sample cryptocurrency data
│
├── etl_pipeline.py               # ETL orchestrator (main entry point)
│
├── Dockerfile                    # Multi-stage Docker build
├── docker-compose.yml            # Service orchestration
├── Makefile                      # Convenient commands
├── requirements.txt              # Python dependencies
├── pytest.ini                    # Pytest configuration
│
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
│
├── README.md                     # Comprehensive documentation
└── QUICKSTART.md                 # Quick start guide
```

## Key Files Explained

### Application Entry Points

- **`api/main.py`** - FastAPI application with CORS, lifespan management
- **`etl_pipeline.py`** - ETL orchestrator that runs all data sources

### Database Models (`core/database.py`)

- `RawCoinPaprika` - Raw CoinPaprika data
- `RawCoinGecko` - Raw CoinGecko data
- `RawCSV` - Raw CSV data
- `UnifiedCryptoData` - Normalized unified data
- `Checkpoint` - ETL execution tracking

### API Routes (`api/routes/data.py`)

- `GET /api/v1/data` - Query cryptocurrency data
- `GET /api/v1/health` - Health check
- `GET /api/v1/stats` - ETL statistics

### Data Sources (`ingestion/sources/`)

Each source implements:
- Rate limiting
- Retry logic with exponential backoff
- Error handling
- Data validation

### Schemas (`schemas/`)

- **Raw schemas** - One per data source
- **Unified schema** - Common format for all sources
- **API response schemas** - For REST endpoints

### Configuration (`core/config.py`)

Uses Pydantic Settings for:
- Database URLs
- API keys
- Rate limiting parameters
- Pagination settings
- Logging configuration

## Data Flow

```
1. Extract:
   CoinPaprika/CoinGecko/CSV → Raw Data (validated with Pydantic)
   
2. Load Raw:
   Raw Data → PostgreSQL (raw_* tables)
   
3. Transform:
   Raw Data → Unified Schema (standardized format)
   
4. Load Unified:
   Unified Data → PostgreSQL (unified_crypto_data table)
   WITH upsert logic (idempotent)
   
5. Checkpoint:
   Record execution status, duration, records processed
   
6. API Query:
   HTTP Request → FastAPI → PostgreSQL → JSON Response
```

## Testing Strategy

- **Unit tests** - Transform functions, schemas
- **Integration tests** - API endpoints with test database
- **Recovery tests** - Checkpoint management, retry logic
- **Edge case tests** - Invalid data, missing fields, rate limits

## Docker Services

```yaml
postgres:  # PostgreSQL 15
  - Port: 5432
  - Volume: postgres_data
  - Health check: pg_isready

api:       # Python FastAPI
  - Port: 8000
  - Depends on: postgres
  - Auto-runs: ETL then API
  - Health check: HTTP /api/v1/health
```

## Environment Variables

See `.env.example` for all available configuration options:
- Database connection
- API keys
- Rate limiting
- Pagination
- Logging
