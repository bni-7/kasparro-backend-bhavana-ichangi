# PowerShell Commands for Windows Users
# Alternative to Makefile for Windows environments

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Available Commands:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  .\commands.ps1 up       - Start all services"
    Write-Host "  .\commands.ps1 down     - Stop all services"
    Write-Host "  .\commands.ps1 test     - Run tests"
    Write-Host "  .\commands.ps1 logs     - View logs"
    Write-Host "  .\commands.ps1 clean    - Stop and remove volumes"
    Write-Host "  .\commands.ps1 rebuild  - Rebuild and restart"
    Write-Host "  .\commands.ps1 etl      - Run ETL manually"
    Write-Host "  .\commands.ps1 health   - Check API health"
    Write-Host "  .\commands.ps1 stats    - Get ETL statistics"
    Write-Host "  .\commands.ps1 data     - Get sample data"
    Write-Host ""
}

switch ($Command) {
    "up" {
        Write-Host "Starting services..." -ForegroundColor Green
        docker compose up -d
        Write-Host "Services started. API available at http://localhost:8000" -ForegroundColor Green
        Write-Host "API docs at http://localhost:8000/docs" -ForegroundColor Yellow
    }
    
    "down" {
        Write-Host "Stopping services..." -ForegroundColor Yellow
        docker compose down
        Write-Host "Services stopped." -ForegroundColor Green
    }
    
    "test" {
        Write-Host "Running tests..." -ForegroundColor Green
        docker compose exec api pytest tests/ -v --cov=. --cov-report=term-missing
        Write-Host "Tests complete." -ForegroundColor Green
    }
    
    "logs" {
        Write-Host "Viewing logs (Ctrl+C to exit)..." -ForegroundColor Yellow
        docker compose logs -f
    }
    
    "clean" {
        Write-Host "Cleaning up..." -ForegroundColor Yellow
        docker compose down -v
        Write-Host "Cleanup complete." -ForegroundColor Green
    }
    
    "rebuild" {
        Write-Host "Rebuilding services..." -ForegroundColor Yellow
        docker compose down
        docker compose build --no-cache
        docker compose up -d
        Write-Host "Services rebuilt and started." -ForegroundColor Green
    }
    
    "etl" {
        Write-Host "Running ETL pipeline..." -ForegroundColor Green
        docker compose exec api python etl_pipeline.py
        Write-Host "ETL pipeline complete." -ForegroundColor Green
    }
    
    "health" {
        Write-Host "Checking API health..." -ForegroundColor Cyan
        curl http://localhost:8000/api/v1/health -UseBasicParsing | ConvertFrom-Json | ConvertTo-Json
    }
    
    "stats" {
        Write-Host "Fetching ETL stats..." -ForegroundColor Cyan
        curl http://localhost:8000/api/v1/stats -UseBasicParsing | ConvertFrom-Json | ConvertTo-Json
    }
    
    "data" {
        Write-Host "Fetching sample data..." -ForegroundColor Cyan
        curl "http://localhost:8000/api/v1/data?page=1&page_size=5" -UseBasicParsing | ConvertFrom-Json | ConvertTo-Json
    }
    
    default {
        Show-Help
    }
}
