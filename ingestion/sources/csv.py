"""CSV data source for cryptocurrency data."""
import csv
import logging
from pathlib import Path
from typing import List
from schemas.raw_data import RawCSVSchema

logger = logging.getLogger(__name__)


class CSVSource:
    """CSV file data source."""
    
    def __init__(self, file_path: str):
        """Initialize CSV source."""
        self.file_path = Path(file_path)
    
    def fetch_data(self) -> List[RawCSVSchema]:
        """Read and parse CSV file."""
        if not self.file_path.exists():
            logger.error(f"CSV file not found: {self.file_path}")
            return []
        
        results = []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        schema = RawCSVSchema(
                            coin_id=row.get("coin_id", "").strip(),
                            name=row.get("name", "").strip(),
                            symbol=row.get("symbol", "").strip(),
                            price_usd=float(row["price_usd"]) if row.get("price_usd") else None,
                            market_cap=float(row["market_cap"]) if row.get("market_cap") else None,
                            volume_24h=float(row["volume_24h"]) if row.get("volume_24h") else None,
                        )
                        results.append(schema)
                    except Exception as e:
                        logger.error(f"Failed to parse CSV row {row_num}: {str(e)}")
                        continue
            
            logger.info(f"Fetched {len(results)} records from CSV: {self.file_path}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to read CSV file {self.file_path}: {str(e)}")
            return []
