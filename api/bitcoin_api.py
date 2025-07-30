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
        Fetch comprehensive Bitcoin data from mempool.space and fallback sources.
        
        Returns:
            Dictionary containing Bitcoin price, fees, hashrate, difficulty, and mempool info
            
        Raises:
            Exception: On API failure
        """
        data = {}
        
        try:
            # Fetch Bitcoin price from mempool.space
            price_response = self._make_request(API_ENDPOINTS['mempool_price'])
            price_data = price_response.json()
            
            data['price'] = price_data.get('USD', 0)
            data['price_formatted'] = f"${price_data.get('USD', 0):,.2f}"
            
        except Exception as e:
            print(f"Error fetching mempool price, using fallback: {e}")
            try:
                # Fallback to CoinGecko
                price_response = self._make_request(API_ENDPOINTS['bitcoin_price'])
                price_data = price_response.json()
                data['price'] = price_data['bitcoin']['usd']
                data['price_formatted'] = f"${price_data['bitcoin']['usd']:,.2f}"
            except Exception:
                data['price'] = 0
                data['price_formatted'] = '$0.00'
        
        try:
            # Fetch fee recommendations
            fees_response = self._make_request(API_ENDPOINTS['mempool_fees'])
            fees_data = fees_response.json()
            
            data['fees'] = {
                'fastest': fees_data.get('fastestFee', 0),
                'half_hour': fees_data.get('halfHourFee', 0),
                'hour': fees_data.get('hourFee', 0),
                'economy': fees_data.get('economyFee', 0),
                'minimum': fees_data.get('minimumFee', 0)
            }
        except Exception as e:
            print(f"Error fetching fees: {e}")
            data['fees'] = {'fastest': 0, 'half_hour': 0, 'hour': 0, 'economy': 0, 'minimum': 0}
        
        try:
            # Fetch difficulty adjustment info
            difficulty_response = self._make_request(API_ENDPOINTS['mempool_difficulty'])
            difficulty_data = difficulty_response.json()
            
            data['difficulty'] = {
                'current': difficulty_data.get('difficulty', 0),
                'change': difficulty_data.get('difficultyChange', 0),
                'estimated_retarget': difficulty_data.get('estimatedRetargetDate', 0),
                'blocks_until_retarget': difficulty_data.get('remainingBlocks', 0),
                'time_until_retarget': difficulty_data.get('timeAvg', 0)
            }
        except Exception as e:
            print(f"Error fetching difficulty: {e}")
            data['difficulty'] = {'current': 0, 'change': 0, 'estimated_retarget': 0, 'blocks_until_retarget': 0, 'time_until_retarget': 0}
        
        try:
            # Fetch hashrate info
            hashrate_response = self._make_request(API_ENDPOINTS['mempool_hashrate'])
            hashrate_data = hashrate_response.json()
            
            if hashrate_data and isinstance(hashrate_data, list) and len(hashrate_data) > 0:
                latest_hashrate = hashrate_data[-1]  # Get most recent data point
                data['hashrate'] = {
                    'current': latest_hashrate.get('avgHashrate', 0),
                    'formatted': self._format_hashrate(latest_hashrate.get('avgHashrate', 0))
                }
            else:
                data['hashrate'] = {'current': 0, 'formatted': '0 EH/s'}
        except Exception as e:
            print(f"Error fetching hashrate: {e}")
            data['hashrate'] = {'current': 0, 'formatted': '0 EH/s'}
        
        try:
            # Fetch recent blocks info
            blocks_response = self._make_request(API_ENDPOINTS['mempool_blocks'])
            blocks_data = blocks_response.json()
            
            if blocks_data and isinstance(blocks_data, list) and len(blocks_data) > 0:
                latest_block = blocks_data[0]
                data['block_height'] = latest_block.get('height', 0)
                data['block_hash'] = latest_block.get('id', '')
                data['block_hash_short'] = latest_block.get('id', '')[:16] + '...'
                data['block_time'] = latest_block.get('timestamp', 0)
                data['block_size'] = latest_block.get('size', 0)
                data['block_tx_count'] = latest_block.get('tx_count', 0)
            else:
                # Fallback to blockchain.info
                blockchain_response = self._make_request(API_ENDPOINTS['blockchain_info'])
                blockchain_data = blockchain_response.json()
                data['block_height'] = blockchain_data.get('height', 0)
                data['block_hash'] = blockchain_data.get('hash', '')
                data['block_hash_short'] = blockchain_data.get('hash', '')[:16] + '...'
                data['block_time'] = blockchain_data.get('time', 0)
                data['block_size'] = 0
                data['block_tx_count'] = 0
        except Exception as e:
            print(f"Error fetching blocks: {e}")
            data.update({
                'block_height': 0,
                'block_hash': '',
                'block_hash_short': 'N/A',
                'block_time': 0,
                'block_size': 0,
                'block_tx_count': 0
            })
        
        try:
            # Fetch mempool info
            mempool_response = self._make_request(API_ENDPOINTS['mempool_mempool'])
            mempool_data = mempool_response.json()
            
            data['mempool'] = {
                'count': mempool_data.get('count', 0),
                'vsize': mempool_data.get('vsize', 0),
                'total_fee': mempool_data.get('total_fee', 0),
                'fee_histogram': mempool_data.get('fee_histogram', [])
            }
        except Exception as e:
            print(f"Error fetching mempool: {e}")
            data['mempool'] = {'count': 0, 'vsize': 0, 'total_fee': 0, 'fee_histogram': []}
        
        return data
    
    def _format_hashrate(self, hashrate_per_second: float) -> str:
        """
        Format hashrate for display.
        
        Args:
            hashrate_per_second: Hashrate in H/s
            
        Returns:
            Formatted hashrate string
        """
        if hashrate_per_second >= 1e18:  # EH/s
            return f"{hashrate_per_second / 1e18:.1f} EH/s"
        elif hashrate_per_second >= 1e15:  # PH/s
            return f"{hashrate_per_second / 1e15:.1f} PH/s"
        elif hashrate_per_second >= 1e12:  # TH/s
            return f"{hashrate_per_second / 1e12:.1f} TH/s"
        else:
            return f"{hashrate_per_second:.0f} H/s"
    
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