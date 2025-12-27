# System Architecture & Design Decisions

## 🏛️ Architecture Overview

This system implements a **production-grade ETL (Extract, Transform, Load) pipeline** with a RESTful API for querying cryptocurrency data. The architecture follows best practices for reliability, scalability, and maintainability.

## 🎯 Design Principles

### 1. Separation of Concerns
- **Data Sources** (`ingestion/sources/`) - External API/file interactions
- **Transformation** (`ingestion/transformer.py`) - Business logic
- **Storage** (`ingestion/loader.py`) - Database operations
- **API** (`api/`) - HTTP interface
- **Core** (`core/`) - Configuration and shared utilities

### 2. Idempotency
All operations are designed to be safely re-runnable:
- **Upsert logic** in database loader
- **Checkpoint tracking** prevents duplicate processing
- **Deterministic transformations** produce same output for same input

### 3. Fault Tolerance
- **Retry logic** with exponential backoff
- **Checkpoint system** for resume-on-failure
- **Error isolation** - one source failure doesn't block others
- **Graceful degradation** - system continues with partial data

### 4. Observability
- **Structured logging** with timestamps and context
- **Health endpoints** for monitoring
- **Statistics tracking** for each ETL run
- **Request tracing** with unique request IDs

## 📊 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      DATA SOURCES                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ CoinPaprika  │  │  CoinGecko   │  │   CSV File   │     │
│  │   REST API   │  │   REST API   │  │  sample.csv  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          │ Rate Limiting    │ Rate Limiting    │
          │ + Retries        │ + Retries        │ CSV Parse
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXTRACTION LAYER                          │
│                  (Pydantic Validation)                       │
├─────────────────────────────────────────────────────────────┤
│  RawCoinPaprika  │  RawCoinGecko   │   RawCSV              │
│     Schema       │     Schema      │    Schema              │
└─────────┬────────────────┬─────────────────┬────────────────┘
          │                │                  │
          │                │                  │
          ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   RAW DATA STORAGE                           │
│                    (PostgreSQL)                              │
├─────────────────────────────────────────────────────────────┤
│  raw_coinpaprika │  raw_coingecko  │   raw_csv             │
│  Full JSON logs  │  Full JSON logs │   CSV records         │
└─────────┬────────────────┬─────────────────┬────────────────┘
          │                │                  │
          │                │                  │
          ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                 TRANSFORMATION LAYER                         │
│            (DataTransformer + Validation)                    │
├─────────────────────────────────────────────────────────────┤
│  Transform to UnifiedCryptoDataSchema                       │
│  - Normalize field names                                    │
│  - Convert types                                            │
│  - Add source metadata                                      │
│  - Validate with Pydantic                                   │
└─────────┬───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                  UNIFIED DATA STORAGE                        │
│         (PostgreSQL with Upsert/Idempotent Writes)          │
├─────────────────────────────────────────────────────────────┤
│              unified_crypto_data table                       │
│  - coin_id, name, symbol                                    │
│  - price_usd, market_cap, volume_24h                        │
│  - source, ingested_at                                      │
│                                                              │
│  Indexes:                                                    │
│  - (coin_id, source, ingested_at) for upsert               │
│  - coin_id for lookups                                      │
│  - source for filtering                                     │
│  - ingested_at for time-based queries                       │
└─────────┬───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                      API LAYER                               │
│                    (FastAPI)                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  GET /api/v1/data                                           │
│  ├─ Pagination (page, page_size)                           │
│  ├─ Filtering (source, coin_id)                            │
│  ├─ Request tracking (request_id)                          │
│  └─ Latency measurement (api_latency_ms)                   │
│                                                              │
│  GET /api/v1/health                                         │
│  ├─ Database connectivity check                            │
│  └─ Last ETL run status                                    │
│                                                              │
│  GET /api/v1/stats                                          │
│  ├─ Records processed per source                           │
│  ├─ Duration per source                                    │
│  └─ Success/failure timestamps                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 ETL Checkpoint System

```
┌─────────────────────────────────────────────────────────────┐
│                  CHECKPOINT LIFECYCLE                        │
└─────────────────────────────────────────────────────────────┘

1. START RUN
   ├─ Check if source is already running
   │  └─ If yes: Skip (prevent concurrent runs)
   ├─ Create/Update checkpoint
   │  ├─ source: "coinpaprika"
   │  ├─ status: "running"
   │  └─ last_run_timestamp: NOW
   └─ Commit to database

2. EXECUTE ETL
   ├─ Extract data from source
   ├─ Validate with Pydantic
   ├─ Load raw data
   ├─ Transform to unified schema
   └─ Load unified data (upsert)

3. COMPLETE RUN (Success)
   ├─ Update checkpoint
   │  ├─ status: "success"
   │  ├─ records_processed: COUNT
   │  ├─ duration_seconds: ELAPSED
   │  └─ error_message: NULL
   └─ Commit to database

3. COMPLETE RUN (Failure)
   ├─ Update checkpoint
   │  ├─ status: "failure"
   │  ├─ records_processed: 0
   │  ├─ duration_seconds: ELAPSED
   │  └─ error_message: ERROR_DETAILS
   └─ Commit to database

4. RESUME FROM CHECKPOINT
   ├─ Query last successful run
   ├─ Determine what to re-process
   └─ Continue from last good state
```

## 🔐 Error Handling Strategy

### Retry Logic (Exponential Backoff)

```python
Attempt 1: Wait 1.0s    (initial_delay)
Attempt 2: Wait 2.0s    (delay * 2)
Attempt 3: Wait 4.0s    (delay * 2)
Attempt 4: Wait 8.0s    (delay * 2)
...
Max Wait:  60.0s        (max_delay cap)

Triggers:
- HTTP 429 (Rate Limit)
- HTTP 500, 502, 503, 504 (Server Errors)
- Connection Timeout
- Connection Refused
```

### Error Isolation

```
Source A fails → Checkpoint marked as "failure"
                ↓
Source B runs   → Independent execution
                ↓
Source C runs   → Independent execution
                ↓
API still works → Returns data from B and C
```

## 💾 Database Design Decisions

### Why Separate Raw and Unified Tables?

**Raw Tables:**
- **Preserve original data** for auditing
- **Debug data quality issues** at source
- **Re-transform** if business logic changes
- **Track API changes** over time

**Unified Table:**
- **Consistent schema** across all sources
- **Query performance** - single table for API
- **Business logic layer** - clean separation
- **Easy to extend** - add new sources without breaking API

### Why PostgreSQL?

1. **ACID Compliance** - Data integrity guarantees
2. **Advanced Features:**
   - `INSERT ... ON CONFLICT` for upserts
   - JSON column type for raw data storage
   - Partial indexes for performance
3. **Production Battle-Tested** - Proven at scale
4. **Rich Ecosystem** - Monitoring, backups, replication

### Indexing Strategy

```sql
-- Fast lookups by coin
CREATE INDEX idx_unified_coin_id ON unified_crypto_data(coin_id);

-- Filter by source
CREATE INDEX idx_unified_source ON unified_crypto_data(source);

-- Time-based queries
CREATE INDEX idx_unified_ingested ON unified_crypto_data(ingested_at);

-- Composite for upsert uniqueness
CREATE UNIQUE INDEX idx_unified_coin_source 
ON unified_crypto_data(coin_id, source, ingested_at);
```

## 🚦 Rate Limiting Implementation

### Two-Layer Protection

**1. Request Delay (Rate Limiting)**
```python
make_request()
sleep(0.5s)  # RATE_LIMIT_DELAY
```
Prevents overwhelming external APIs with requests.

**2. Exponential Backoff (Error Recovery)**
```python
try:
    make_request()
except RateLimitError:
    wait(delay)
    delay *= 2  # Exponential increase
    retry()
```
Handles 429 responses gracefully.

## 🔍 Observability & Monitoring

### Logging Strategy

```python
# Structured logging with context
logger.info(
    "Completed ETL run",
    extra={
        "source": "coinpaprika",
        "records": 100,
        "duration": 5.23,
        "status": "success"
    }
)
```

### Metrics Tracked

**Per ETL Run:**
- Records processed
- Duration (seconds)
- Success/failure status
- Error messages
- Timestamp

**Per API Request:**
- Request ID (UUID)
- Latency (milliseconds)
- Results count
- Filters applied

## 🐳 Docker Architecture

### Multi-Stage Build Benefits

**Stage 1: Builder**
- Installs build dependencies (gcc, etc.)
- Compiles Python packages
- Creates wheel files

**Stage 2: Runtime**
- Minimal base image
- Only runtime dependencies
- Smaller final image (security + performance)

**Result:**
- Build image: ~800MB
- Final image: ~300MB (60% reduction)

### Service Dependencies

```yaml
postgres:
  ↓ (health check: pg_isready)
api:
  ↓ (waits for postgres healthy)
  ├─ Run ETL pipeline
  └─ Start FastAPI server
```

## 📈 Scalability Considerations

### Current Design Supports:

1. **Horizontal Scaling**
   - Stateless API (multiple instances)
   - Read replicas for PostgreSQL
   - Load balancer in front

2. **Vertical Scaling**
   - Increase PostgreSQL resources
   - More API container memory
   - Larger connection pools

3. **Data Volume**
   - Partitioning by date (ingested_at)
   - Archiving old raw data
   - Materialized views for aggregations

### Future Enhancements:

- Task queue (Celery) for ETL scheduling
- Caching layer (Redis) for API responses
- Message queue (RabbitMQ) for real-time updates
- Data warehouse (Snowflake) for analytics

## 🧪 Testing Philosophy

### Test Pyramid

```
        ┌───────────┐
       ╱  Integration ╲      ← Few, test API + DB
      ┌─────────────────┐
     ╱   Component      ╲    ← Some, test ETL flow
    ┌───────────────────────┐
   ╱        Unit           ╲ ← Many, test transformations
  └─────────────────────────┘
```

**Unit Tests** - Fast, isolated, pure functions  
**Integration Tests** - API + test database  
**Recovery Tests** - Checkpoint logic, retry mechanisms  

## 🎓 Key Takeaways

✅ **Idempotency** - Safe to re-run at any time  
✅ **Fault Tolerance** - Graceful error handling  
✅ **Observability** - Logging, metrics, health checks  
✅ **Separation of Concerns** - Clear module boundaries  
✅ **Production-Ready** - Docker, tests, documentation  
✅ **Scalable Design** - Ready for growth  
✅ **Type Safety** - Pydantic validation everywhere  
✅ **Clean Code** - PEP 8, type hints, docstrings  

This architecture demonstrates enterprise-level software engineering practices suitable for production cryptocurrency data systems.
