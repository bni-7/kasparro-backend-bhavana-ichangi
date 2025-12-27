# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# (Optional) Edit .env to add your CoinPaprika API key
# The system works without an API key, but may have stricter rate limits
```

### 2. Start the System
```bash
# Start all services with Docker Compose
make up

# Or without Make:
docker-compose up -d
```

### 3. Test the API
```bash
# Check health
curl http://localhost:8000/api/v1/health

# View interactive docs
open http://localhost:8000/docs

# Get cryptocurrency data
curl "http://localhost:8000/api/v1/data?page=1&page_size=5"

# Get ETL statistics
curl http://localhost:8000/api/v1/stats
```

## 📖 What Happens on Startup

1. **PostgreSQL** starts and creates database
2. **API container** waits for database to be ready
3. **ETL pipeline** runs automatically:
   - Fetches data from CoinPaprika (top 10 coins)
   - Fetches data from CoinGecko (top 10 coins)
   - Reads data from sample CSV file
   - Stores raw data in respective tables
   - Transforms and loads into unified table
4. **FastAPI server** starts on port 8000

Total startup time: ~30-40 seconds

## 🔍 Verify Everything Works

```bash
# Check all services are running
docker-compose ps

# View logs
docker-compose logs -f

# Check health endpoint
make health

# Get sample data
make data

# View statistics
make stats
```

## 🛠️ Common Commands

```bash
make up        # Start services
make down      # Stop services
make logs      # View logs
make test      # Run tests
make etl       # Run ETL manually
make clean     # Clean everything
make help      # Show all commands
```

## 📊 What Data is Available

After successful startup, you'll have:
- ~10 records from CoinPaprika
- ~10 records from CoinGecko  
- ~10 records from CSV file
- Total: ~30 cryptocurrency records

All accessible via `/api/v1/data` endpoint with:
- Pagination
- Filtering by source
- Filtering by coin_id

## 🐛 Troubleshooting

**Services won't start?**
```bash
# Check Docker is running
docker ps

# View detailed logs
docker-compose logs
```

**Port 8000 already in use?**
```bash
# Edit docker-compose.yml and change port mapping:
# From: "8000:8000"
# To:   "8001:8000"
```

**Database connection errors?**
```bash
# Restart services
make down
make up
```

## 📚 Next Steps

- Read the full [README.md](README.md) for architecture details
- Explore API docs at http://localhost:8000/docs
- Add your CoinPaprika API key to `.env` for higher rate limits
- Customize CSV file at `data/sample.csv`
- Run tests with `make test`
- Add new data sources (see README.md)

## 🎯 Key Features Demonstrated

✅ Production-grade ETL pipeline  
✅ Rate limiting & retry logic with exponential backoff  
✅ Incremental ingestion with checkpoints  
✅ Idempotent writes (safe re-runs)  
✅ Resume-on-failure capability  
✅ RESTful API with pagination  
✅ Comprehensive error handling  
✅ Docker containerization  
✅ Automated testing  
✅ Structured logging  
✅ Health monitoring  

Enjoy exploring the system! 🎉
