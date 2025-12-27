"""Simple CLI tool to view data from the database.

Usage:
    python view_data.py --source coinpaprika --limit 5
    python view_data.py --coin btc-bitcoin
    python view_data.py --stats
"""
import argparse
from sqlalchemy.orm import Session
from core.database import SessionLocal, UnifiedCryptoData, Checkpoint
from core.checkpoints import CheckpointManager
from tabulate import tabulate
import sys


def view_data(db: Session, source: str = None, coin_id: str = None, limit: int = 10):
    """View unified crypto data."""
    query = db.query(UnifiedCryptoData)
    
    if source:
        query = query.filter(UnifiedCryptoData.source == source)
    
    if coin_id:
        query = query.filter(UnifiedCryptoData.coin_id == coin_id)
    
    results = query.order_by(
        UnifiedCryptoData.ingested_at.desc()
    ).limit(limit).all()
    
    if not results:
        print("No data found.")
        return
    
    # Prepare table data
    headers = ["ID", "Coin ID", "Name", "Symbol", "Price USD", "Market Cap", "Volume 24h", "Source", "Ingested At"]
    rows = []
    
    for r in results:
        rows.append([
            r.id,
            r.coin_id,
            r.name,
            r.symbol,
            f"${r.price_usd:,.2f}" if r.price_usd else "N/A",
            f"${r.market_cap:,.0f}" if r.market_cap else "N/A",
            f"${r.volume_24h:,.0f}" if r.volume_24h else "N/A",
            r.source,
            r.ingested_at.strftime("%Y-%m-%d %H:%M:%S")
        ])
    
    print("\n" + "=" * 120)
    print(f"Cryptocurrency Data (showing {len(results)} records)")
    print("=" * 120)
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print()


def view_stats(db: Session):
    """View ETL statistics."""
    manager = CheckpointManager(db)
    checkpoints = manager.get_all_checkpoints()
    
    if not checkpoints:
        print("No ETL runs recorded yet.")
        return
    
    headers = ["Source", "Status", "Records", "Duration (s)", "Last Run", "Error"]
    rows = []
    
    total_records = 0
    
    for cp in checkpoints:
        rows.append([
            cp.source,
            cp.status,
            cp.records_processed,
            f"{cp.duration_seconds:.2f}" if cp.duration_seconds else "N/A",
            cp.last_run_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            cp.error_message[:50] + "..." if cp.error_message and len(cp.error_message) > 50 else (cp.error_message or "")
        ])
        total_records += cp.records_processed
    
    print("\n" + "=" * 120)
    print("ETL Statistics")
    print("=" * 120)
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print(f"\nTotal records processed: {total_records}")
    print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="View cryptocurrency data from database")
    parser.add_argument("--source", help="Filter by source (coinpaprika, coingecko, csv)")
    parser.add_argument("--coin", help="Filter by coin ID")
    parser.add_argument("--limit", type=int, default=10, help="Number of records to show (default: 10)")
    parser.add_argument("--stats", action="store_true", help="Show ETL statistics")
    
    args = parser.parse_args()
    
    db = SessionLocal()
    
    try:
        if args.stats:
            view_stats(db)
        else:
            view_data(db, source=args.source, coin_id=args.coin, limit=args.limit)
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
