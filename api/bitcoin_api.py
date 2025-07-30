"""
Bitcoin API management for price and blockchain data.
"""

from typing import Dict, Any
from api.base_api import BaseAPIManager
from utils.constants import API_ENDPOINTS


class BitcoinAPIManager(BaseAPIManager):
    """Manages Bitcoin price and blockchain data from multiple APIs."""
    
    def __init__(self):
        """Initialize Bitcoin API manager."""
        super().__init__(cache_key='bitcoin')
    
    def _fetch_data(self) -> Dict[str, Any]:
        """
        Fetch Bitcoin price and blockchain data.
        
        Returns:
            Dictionary containing Bitcoin price and blockchain info
            
        Raises:
            Exception: On API failure
        """
        # Fetch Bitcoin price from CoinGecko
        price_response = self._make_request(API_ENDPOINTS['bitcoin_price'])
        price_data = price_response.json()
        
        # Fetch blockchain info
        blockchain_response = self._make_request(API_ENDPOINTS['blockchain_info'])
        blockchain_data = blockchain_response.json()
        
        return {
            'price': price_data['bitcoin']['usd'],
            'price_formatted': f"${price_data['bitcoin']['usd']:,.2f}",
            'block_height': blockchain_data['height'],
            'block_hash': blockchain_data['hash'],
            'block_hash_short': blockchain_data['hash'][:16] + '...',  # Truncated for display
            'block_time': blockchain_data.get('time', 0)
        }
    
    def get_price(self) -> float:
        """
        Get current Bitcoin price.
        
        Returns:
            Bitcoin price in USD or 0 if unavailable
        """
        data = self.get_data()
        return data.get('price', 0)
    
    def get_block_height(self) -> int:
        """
        Get current block height.
        
        Returns:
            Current block height or 0 if unavailable
        """
        data = self.get_data()
        return data.get('block_height', 0)
    
    def get_formatted_price(self) -> str:
        """
        Get formatted Bitcoin price string.
        
        Returns:
            Formatted price string
        """
        data = self.get_data()
        return data.get('price_formatted', '$0.00')
    
    def get_status(self) -> str:
        """
        Get API status.
        
        Returns:
            Status string ('success', 'cached', 'error')
        """
        data = self.get_data()
        return data.get('status', 'unknown') 