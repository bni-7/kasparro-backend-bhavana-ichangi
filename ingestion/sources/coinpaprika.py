"""CoinPaprika API data source with rate limiting and retries."""
import json
import time
import logging
from typing import List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from core.config import settings
from schemas.raw_data import RawCoinPaprikaSchema

logger = logging.getLogger(__name__)


class CoinPaprikaSource:
    """CoinPaprika API data source."""
    
    def __init__(self):
        """Initialize CoinPaprika source."""
        self.base_url = settings.coinpaprika_base_url
        self.api_key = settings.coinpaprika_api_key
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=settings.max_retries,
            backoff_factor=settings.initial_retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        if self.api_key:
            session.headers.update({"Authorization": self.api_key})
        
        return session
    
    def _make_request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make API request with exponential backoff."""
        url = f"{self.base_url}/{endpoint}"
        delay = settings.initial_retry_delay
        
        for attempt in range(settings.max_retries):
            try:
                logger.info(f"Requesting CoinPaprika: {endpoint} (attempt {attempt + 1})")
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 429:
                    logger.warning(f"Rate limited. Waiting {delay}s before retry...")
                    time.sleep(delay)
                    delay = min(delay * 2, settings.max_retry_delay)
                    continue
                
                response.raise_for_status()
                
                # Rate limiting between successful requests
                time.sleep(settings.rate_limit_delay)
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {str(e)}")
                
                if attempt == settings.max_retries - 1:
                    raise
                
                time.sleep(delay)
                delay = min(delay * 2, settings.max_retry_delay)
        
        raise Exception("Max retries exceeded")
    
    def fetch_ticker_data(self, coin_id: str = "btc-bitcoin") -> Optional[RawCoinPaprikaSchema]:
        """Fetch ticker data for a specific coin."""
        try:
            data = self._make_request(f"tickers/{coin_id}")
            
            return RawCoinPaprikaSchema(
                coin_id=data.get("id", coin_id),
                name=data.get("name"),
                symbol=data.get("symbol"),
                rank=data.get("rank"),
                price_usd=data.get("quotes", {}).get("USD", {}).get("price"),
                market_cap=data.get("quotes", {}).get("USD", {}).get("market_cap"),
                volume_24h=data.get("quotes", {}).get("USD", {}).get("volume_24h"),
                circulating_supply=data.get("circulating_supply"),
                total_supply=data.get("total_supply"),
                max_supply=data.get("max_supply"),
                percent_change_24h=data.get("quotes", {}).get("USD", {}).get("percent_change_24h"),
                raw_json=json.dumps(data)
            )
        except Exception as e:
            logger.error(f"Failed to fetch CoinPaprika data for {coin_id}: {str(e)}")
            return None
    
    def fetch_top_coins(self, limit: int = 10) -> List[RawCoinPaprikaSchema]:
        """Fetch top coins by market cap."""
        try:
            tickers = self._make_request("tickers", params={"limit": limit})
            
            results = []
            for ticker in tickers:
                try:
                    schema = RawCoinPaprikaSchema(
                        coin_id=ticker.get("id", ""),
                        name=ticker.get("name"),
                        symbol=ticker.get("symbol"),
                        rank=ticker.get("rank"),
                        price_usd=ticker.get("quotes", {}).get("USD", {}).get("price"),
                        market_cap=ticker.get("quotes", {}).get("USD", {}).get("market_cap"),
                        volume_24h=ticker.get("quotes", {}).get("USD", {}).get("volume_24h"),
                        circulating_supply=ticker.get("circulating_supply"),
                        total_supply=ticker.get("total_supply"),
                        max_supply=ticker.get("max_supply"),
                        percent_change_24h=ticker.get("quotes", {}).get("USD", {}).get("percent_change_24h"),
                        raw_json=json.dumps(ticker)
                    )
                    results.append(schema)
                except Exception as e:
                    logger.error(f"Failed to parse ticker: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(results)} coins from CoinPaprika")
            return results
            
        except Exception as e:
            logger.error(f"Failed to fetch CoinPaprika top coins: {str(e)}")
            return []
