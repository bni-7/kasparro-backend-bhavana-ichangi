"""System validation script - checks if everything is set up correctly.

Run this to verify your installation before starting the services.
"""
import os
import sys
from pathlib import Path


def check_file(filepath: str, description: str) -> bool:
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ MISSING {description}: {filepath}")
        return False


def check_directory(dirpath: str, description: str) -> bool:
    """Check if a directory exists."""
    if Path(dirpath).is_dir():
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ MISSING {description}: {dirpath}")
        return False


def main():
    """Run validation checks."""
    print("=" * 70)
    print("CRYPTO ETL SYSTEM - VALIDATION CHECK")
    print("=" * 70)
    print()
    
    checks_passed = 0
    checks_total = 0
    
    # Core files
    print("📁 Core Application Files:")
    checks = [
        ("api/main.py", "FastAPI main"),
        ("api/routes/data.py", "API routes"),
        ("core/config.py", "Configuration"),
        ("core/database.py", "Database models"),
        ("core/checkpoints.py", "Checkpoint manager"),
        ("etl_pipeline.py", "ETL pipeline"),
    ]
    
    for filepath, desc in checks:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    print()
    
    # Data sources
    print("📡 Data Sources:")
    checks = [
        ("ingestion/sources/coinpaprika.py", "CoinPaprika source"),
        ("ingestion/sources/coingecko.py", "CoinGecko source"),
        ("ingestion/sources/csv.py", "CSV source"),
        ("ingestion/transformer.py", "Data transformer"),
        ("ingestion/loader.py", "Data loader"),
    ]
    
    for filepath, desc in checks:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    print()
    
    # Schemas
    print("📋 Pydantic Schemas:")
    checks = [
        ("schemas/raw_data.py", "Raw data schemas"),
        ("schemas/unified.py", "Unified schemas"),
    ]
    
    for filepath, desc in checks:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    print()
    
    # Tests
    print("🧪 Test Files:")
    checks = [
        ("tests/test_etl.py", "ETL tests"),
        ("tests/test_api.py", "API tests"),
        ("tests/test_recovery.py", "Recovery tests"),
        ("tests/conftest.py", "Test config"),
    ]
    
    for filepath, desc in checks:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    print()
    
    # Docker files
    print("🐳 Docker Files:")
    checks = [
        ("Dockerfile", "Dockerfile"),
        ("docker-compose.yml", "Docker Compose"),
    ]
    
    for filepath, desc in checks:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    print()
    
    # Configuration
    print("⚙️ Configuration Files:")
    checks = [
        ("requirements.txt", "Python dependencies"),
        (".env.example", "Environment template"),
        ("pytest.ini", "Pytest config"),
        ("Makefile", "Makefile"),
    ]
    
    for filepath, desc in checks:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    print()
    
    # Data
    print("📊 Data Files:")
    checks = [
        ("data/sample.csv", "Sample CSV data"),
    ]
    
    for filepath, desc in checks:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    print()
    
    # Documentation
    print("📖 Documentation:")
    checks = [
        ("README.md", "Main README"),
        ("QUICKSTART.md", "Quick start guide"),
        ("ARCHITECTURE.md", "Architecture docs"),
        ("PROJECT_STRUCTURE.md", "Structure guide"),
        ("BUILD_COMPLETE.md", "Build summary"),
    ]
    
    for filepath, desc in checks:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    print()
    
    # Environment check
    print("🔧 Environment Check:")
    if Path(".env").exists():
        print("✅ .env file exists")
        checks_passed += 1
    else:
        print("⚠️  .env file not found (copy from .env.example)")
    checks_total += 1
    
    print()
    print("=" * 70)
    print(f"VALIDATION RESULT: {checks_passed}/{checks_total} checks passed")
    print("=" * 70)
    print()
    
    if checks_passed == checks_total:
        print("🎉 SUCCESS! All files present. You're ready to start!")
        print()
        print("Next steps:")
        print("  1. Review/edit .env file (add API keys if needed)")
        print("  2. Run: make up")
        print("  3. Access: http://localhost:8000/docs")
        print()
        return 0
    elif checks_passed >= checks_total - 1:
        print("⚠️  Almost there! Create .env file:")
        print("     cp .env.example .env")
        print()
        return 0
    else:
        print("❌ FAILED! Some files are missing.")
        print("   Please ensure all files were created correctly.")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
