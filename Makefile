.PHONY: help up down logs clean test etl install

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start all services (postgres + api)
	@echo "Starting services..."
	docker compose up -d
	@echo "Services started. API available at http://localhost:8000"
	@echo "API docs at http://localhost:8000/docs"

down: ## Stop all services
	@echo "Stopping services..."
	docker compose down
	@echo "Services stopped."

logs: ## View logs from all services
	docker compose logs -f

clean: ## Stop services and remove volumes
	@echo "Cleaning up..."
	docker compose down -v
	@echo "Cleanup complete."

rebuild: ## Rebuild and restart services
	@echo "Rebuilding services..."
	docker compose down
	docker compose build --no-cache
	docker compose up -d
	@echo "Services rebuilt and started."

test: ## Run tests
	@echo "Running tests..."
	docker compose exec api pytest tests/ -v --cov=. --cov-report=term-missing
	@echo "Tests complete."

etl: ## Run ETL pipeline manually
	@echo "Running ETL pipeline..."
	docker compose exec api python etl_pipeline.py
	@echo "ETL pipeline complete."

install: ## Install dependencies locally
	pip install -r requirements.txt

shell: ## Open shell in api container
	docker compose exec api /bin/sh

db-shell: ## Open PostgreSQL shell
	docker compose exec postgres psql -U crypto_user -d crypto_etl

health: ## Check service health
	@echo "Checking API health..."
	@curl -s http://localhost:8000/api/v1/health | python -m json.tool

stats: ## Get ETL statistics
	@echo "Fetching ETL stats..."
	@curl -s http://localhost:8000/api/v1/stats | python -m json.tool

data: ## Get sample data
	@echo "Fetching sample data..."
	@curl -s "http://localhost:8000/api/v1/data?page=1&page_size=5" | python -m json.tool
