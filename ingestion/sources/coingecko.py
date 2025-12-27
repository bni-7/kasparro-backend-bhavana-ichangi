"""CoinGecko API data source with rate limiting and retries."""
import json
import time
import logging
from typing import List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from core.config import settings
from schemas.raw_data import RawCoinGeckoSchema

logger = logging.getLogger(__name__)


class CoinGeckoSource:
    """CoinGecko API data source."""
    
    def __init__(self):
        """Initialize CoinGecko source."""
        self.base_url = settings.coingecko_base_url
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
        
        return session
    
    def _make_request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make API request with exponential backoff."""
        url = f"{self.base_url}/{endpoint}"
        delay = settings.initial_retry_delay
        
        for attempt in range(settings.max_retries):
            try:
                logger.info(f"Requesting CoinGecko: {endpoint} (attempt {attempt + 1})")
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
    
    def fetch_markets_data(
        self,
        vs_currency: str = "usd",
        per_page: int = 10,
        page: int = 1
    ) -> List[RawCoinGeckoSchema]:
        """Fetch market data for cryptocurrencies."""
        try:
            params = {
                "vs_currency": vs_currency,
                "per_page": per_page,
                "page": page,
                "order": "market_cap_desc"
            }
            
            data = self._make_request("coins/markets", params=params)
            
            results = []
            for coin in data:
                try:
                    schema = RawCoinGeckoSchema(
                        coin_id=coin.get("id", ""),
                        name=coin.get("name"),
                        symbol=coin.get("symbol"),
                        current_price=coin.get("current_price"),
                        market_cap=coin.get("market_cap"),
                        total_volume=coin.get("total_volume"),
                        price_change_24h=coin.get("price_change_24h"),
                        price_change_percentage_24h=coin.get("price_change_percentage_24h"),
                        market_cap_rank=coin.get("market_cap_rank"),
                        raw_json=json.dumps(coin)
                    )
                    results.append(schema)
                except Exception as e:
                    logger.error(f"Failed to parse coin data: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(results)} coins from CoinGecko")
            return results
            
        except Exception as e:
            logger.error(f"Failed to fetch CoinGecko market data: {str(e)}")
            return []
    
    def fetch_coin_data(self, coin_id: str = "bitcoin") -> Optional[RawCoinGeckoSchema]:
        """Fetch data for a specific coin."""
        try:
            data = self._make_request(f"coins/{coin_id}")
            
            market_data = data.get("market_data", {})
            
            return RawCoinGeckoSchema(
                coin_id=data.get("id", coin_id),
                name=data.get("name"),
                symbol=data.get("symbol"),
                current_price=market_data.get("current_price", {}).get("usd"),
                market_cap=market_data.get("market_cap", {}).get("usd"),
                total_volume=market_data.get("total_volume", {}).get("usd"),
                price_change_24h=market_data.get("price_change_24h"),
                price_change_percentage_24h=market_data.get("price_change_percentage_24h"),
                market_cap_rank=data.get("market_cap_rank"),
                raw_json=json.dumps(data)
            )
        except Exception as e:
            logger.error(f"Failed to fetch CoinGecko data for {coin_id}: {str(e)}")
            return None
