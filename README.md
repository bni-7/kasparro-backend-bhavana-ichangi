# Crypto ETL System

A production-grade ETL (Extract, Transform, Load) system with REST API for cryptocurrency data ingestion and querying, built with Python FastAPI and PostgreSQL.

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────┐
│   Data Sources  │
│  ┌───────────┐  │
│  │CoinPaprika│  │
│  │ CoinGecko │  │
│  │    CSV    │  │
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ETL Pipeline   │
│  ┌───────────┐  │
│  │ Extractor │  │
│  │Transformer│  │
│  │  Loader   │  │
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│  ┌───────────┐  │
│  │  Raw Data │  │
│  │  Unified  │  │
│  │Checkpoints│  │
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI REST   │
│  ┌───────────┐  │
│  │ /data     │  │
│  │ /health   │  │
│  │ /stats    │  │
│  └───────────┘  │
└─────────────────┘
```

### Database Schema

**Raw Tables:**
- `raw_coinpaprika` - Raw data from CoinPaprika API
- `raw_coingecko` - Raw data from CoinGecko API
- `raw_csv` - Raw data from CSV files

**Unified Table:**
- `unified_crypto_data` - Normalized cryptocurrency data with fields:
  - `coin_id`, `name`, `symbol`
  - `price_usd`, `market_cap`, `volume_24h`
  - `source` (coinpaprika, coingecko, csv)
  - `ingested_at` (timestamp)

**Checkpoints:**
- `checkpoints` - ETL execution tracking for resume-on-failure

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Make (optional, for convenience commands)

### Setup and Run

1. **Clone and navigate to the project:**
   ```bash
   cd kasparro
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env and add your COINPAPRIKA_API_KEY if available
   ```

3. **Start the system:**
   ```bash
   make up
   ```
   
   Or without Make:
   ```bash
   docker-compose up -d
   ```

4. **Access the API:**
   - API Base: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/v1/health

### Available Make Commands

```bash
make help      # Show all available commands
make up        # Start all services
make down      # Stop all services
make logs      # View logs
make test      # Run tests
make etl       # Run ETL pipeline manually
make health    # Check service health
make stats     # Get ETL statistics
make data      # Get sample data
make clean     # Remove all containers and volumes
```

## 📡 API Endpoints

### GET /api/v1/data

Get cryptocurrency data with pagination and filtering.

**Query Parameters:**
- `page` (default: 1) - Page number
- `page_size` (default: 100, max: 1000) - Items per page
- `source` (optional) - Filter by source (coinpaprika, coingecko, csv)
- `coin_id` (optional) - Filter by coin ID

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "coin_id": "btc-bitcoin",
      "name": "Bitcoin",
      "symbol": "BTC",
      "price_usd": 45000.0,
      "market_cap": 850000000000.0,
      "volume_24h": 25000000000.0,
      "source": "coinpaprika",
      "ingested_at": "2025-12-27T10:30:00"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 100,
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "api_latency_ms": 45.23
}
```

**Examples:**
```bash
# Get first page
curl "http://localhost:8000/api/v1/data?page=1&page_size=10"

# Filter by source
curl "http://localhost:8000/api/v1/data?source=coinpaprika"

# Filter by coin
curl "http://localhost:8000/api/v1/data?coin_id=btc-bitcoin"
```

### GET /api/v1/health

Health check endpoint showing database connectivity and ETL status.

**Response:**
```json
{
  "status": "healthy",
  "database_connected": true,
  "etl_last_run": {
    "source": "coinpaprika",
    "timestamp": "2025-12-27T10:30:00",
    "status": "success",
    "records_processed": 10
  },
  "timestamp": "2025-12-27T10:35:00"
}
```

### GET /api/v1/stats

ETL statistics including records processed, duration, and timestamps.

**Response:**
```json
{
  "sources": [
    {
      "source": "coinpaprika",
      "records_processed": 10,
      "duration_seconds": 5.23,
      "last_success_timestamp": "2025-12-27T10:30:00",
      "last_failure_timestamp": null,
      "status": "success"
    },
    {
      "source": "coingecko",
      "records_processed": 10,
      "duration_seconds": 4.87,
      "last_success_timestamp": "2025-12-27T10:30:05",
      "last_failure_timestamp": null,
      "status": "success"
    }
  ],
  "total_records": 30,
  "request_id": "650e8400-e29b-41d4-a716-446655440001",
  "api_latency_ms": 12.45
}
```

## 🔧 Configuration

### Environment Variables

All configuration is managed via environment variables (see `.env.example`):

**Database:**
- `DATABASE_URL` - PostgreSQL connection string
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` - PostgreSQL credentials

**API Keys:**
- `COINPAPRIKA_API_KEY` - CoinPaprika API key (optional)

**API Configuration:**
- `API_HOST` - API host (default: 0.0.0.0)
- `API_PORT` - API port (default: 8000)

**ETL Configuration:**
- `CSV_FILE_PATH` - Path to CSV file (default: data/sample.csv)
- `MAX_RETRIES` - Maximum retry attempts (default: 3)
- `INITIAL_RETRY_DELAY` - Initial retry delay in seconds (default: 1.0)
- `MAX_RETRY_DELAY` - Maximum retry delay (default: 60.0)
- `RATE_LIMIT_DELAY` - Delay between requests (default: 0.5)

**Logging:**
- `LOG_LEVEL` - Logging level (default: INFO)

## 🔄 ETL Pipeline Features

### Incremental Ingestion

The system implements **incremental ingestion** with checkpoint tracking:

1. **Checkpoint Table** tracks each source's last run:
   - Timestamp of last successful run
   - Records processed
   - Duration
   - Status (success/failure/running)
   - Error messages on failure

2. **Idempotent Writes** using PostgreSQL `INSERT ... ON CONFLICT`:
   - Prevents duplicate data
   - Safe for re-runs
   - Handles network failures gracefully

3. **Resume-on-Failure**:
   - Pipeline can resume from last successful checkpoint
   - Failed runs are logged with error details
   - No reprocessing of successfully ingested data

### Rate Limiting & Retry Logic

**Exponential Backoff:**
- Initial delay: 1 second
- Doubles on each retry (1s → 2s → 4s → 8s...)
- Maximum delay: 60 seconds
- Handles 429 (rate limit) and 5xx errors

**Request Throttling:**
- 0.5s delay between successful requests
- Prevents overwhelming external APIs
- Configurable via `RATE_LIMIT_DELAY`

### Data Validation

All data is validated using **Pydantic schemas**:
- Type checking (int, float, str, datetime)
- Required vs. optional fields
- Enum validation for source types
- Automatic timestamp generation

## 🧪 Testing

### Run All Tests

```bash
make test
```

Or manually:
```bash
docker-compose exec api pytest tests/ -v --cov=. --cov-report=term-missing
```

### Test Coverage

**Test Suites:**
1. **test_etl.py** - Data transformation and validation
2. **test_api.py** - API endpoints with mock data
3. **test_recovery.py** - Failure recovery and edge cases

**Coverage Areas:**
- ETL transformations (CoinPaprika, CoinGecko, CSV)
- API pagination, filtering, and error handling
- Checkpoint management and resume logic
- Rate limiting and retry mechanisms
- Schema validation and mismatch handling
- CSV parsing with invalid rows

## 🏭 Production Deployment

### Docker Multi-Stage Build

The Dockerfile uses **multi-stage builds** for optimization:

**Stage 1 (Builder):**
- Installs dependencies with build tools
- Creates isolated Python package directory

**Stage 2 (Production):**
- Minimal runtime image
- Only copies compiled dependencies
- No build tools (smaller image)
- Runs as non-root for security

### Health Checks

Docker Compose includes health checks:
- Database: `pg_isready` check every 10s
- API: HTTP health endpoint check every 30s
- Startup grace period: 40s

### Auto-Start Behavior

The API container:
1. Waits for PostgreSQL to be healthy
2. Runs ETL pipeline to populate initial data
3. Starts FastAPI server on port 8000
4. Restarts automatically on failure (`restart: unless-stopped`)

## 📊 Design Decisions

### Why PostgreSQL?

- **ACID compliance** for data integrity
- **ON CONFLICT** for idempotent upserts
- **Indexing** on coin_id, source, and timestamps
- **Production-ready** with proven scalability

### Why Pydantic?

- **Runtime validation** catches errors early
- **Type hints** improve code quality
- **Automatic documentation** for OpenAPI/Swagger
- **Settings management** from environment variables

### Why Separate Raw and Unified Tables?

- **Raw tables** preserve original API responses
- **Unified table** provides consistent schema across sources
- **Data lineage** for debugging and auditing
- **Flexibility** to add new sources without schema changes

### Why Checkpoint-Based Ingestion?

- **Fault tolerance** - Resume from last successful point
- **Monitoring** - Track ETL health and performance
- **Idempotency** - Safe to re-run without duplicates
- **Scalability** - Each source runs independently

## 🔍 Monitoring & Observability

### Structured Logging

All components use structured logging with:
- Timestamps
- Log levels (INFO, WARNING, ERROR)
- Source identification
- Error context and stack traces

### Metrics Available

Via `/api/v1/stats`:
- Records processed per source
- Execution duration
- Success/failure timestamps
- Current status

### Health Monitoring

Via `/api/v1/health`:
- Database connectivity
- Last ETL run status
- System timestamp

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps

# View PostgreSQL logs
docker-compose logs postgres

# Test connection manually
docker-compose exec postgres psql -U crypto_user -d crypto_etl
```

### ETL Pipeline Failures

```bash
# View API logs
docker-compose logs api

# Run ETL manually with verbose output
docker-compose exec api python etl_pipeline.py

# Check checkpoint status
curl http://localhost:8000/api/v1/stats
```

### API Not Responding

```bash
# Check API health
curl http://localhost:8000/api/v1/health

# View API logs
docker-compose logs -f api

# Restart API container
docker-compose restart api
```

## 📝 Development

### Local Development Setup

```bash
# Install dependencies locally
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start only PostgreSQL
docker-compose up -d postgres

# Run API locally
python -m uvicorn api.main:app --reload

# Run ETL locally
python etl_pipeline.py
```

### Adding New Data Sources

1. Create new source in `ingestion/sources/your_source.py`
2. Implement rate limiting and retry logic
3. Add raw table in `core/database.py`
4. Create Pydantic schema in `schemas/raw_data.py`
5. Add transformer method in `ingestion/transformer.py`
6. Add to ETL pipeline in `etl_pipeline.py`
7. Write tests in `tests/`

## 📄 License

This project is a demonstration of production-grade ETL architecture.

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type hints
- **CoinPaprika & CoinGecko** - Cryptocurrency data APIs
