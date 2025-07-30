"""
Base API management class for the Raspberry Pi Dashboard.
"""

import requests
import time
from typing import Dict, Any, Optional
from core.cache import DataCache
from utils.constants import DEFAULT_UPDATE_INTERVAL


class BaseAPIManager:
    """Base class for API managers with common functionality."""
    
    def __init__(self, cache_key: str, update_interval: int = DEFAULT_UPDATE_INTERVAL):
        """
        Initialize base API manager.
        
        Args:
            cache_key: Key for caching this API's data
            update_interval: Update interval in seconds
        """
        self.cache_key = cache_key
        self.update_interval = update_interval
        self.cache = DataCache()
        self.session = requests.Session()
        self.session.timeout = 10
        self.last_error: Optional[str] = None
    
    def get_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get API data with caching.
        
        Args:
            force_refresh: Force refresh from API regardless of cache status
            
        Returns:
            API data dictionary with status information
        """
        # Check cache first unless forced refresh
        if not force_refresh:
            cached = self.cache.get(self.cache_key)
            if cached and not self.cache.is_expired(self.cache_key, self.update_interval):
                return cached
        
        # Fetch fresh data
        try:
            fresh_data = self._fetch_data()
            fresh_data['status'] = 'success'
            fresh_data['last_updated'] = time.time()
            
            # Cache the fresh data
            self.cache.set(self.cache_key, fresh_data)
            self.last_error = None
            
            return fresh_data
            
        except Exception as e:
            self.last_error = str(e)
            print(f"Error fetching {self.cache_key} data: {e}")
            
            # Return cached data if available
            cached = self.cache.get(self.cache_key)
            if cached:
                cached['status'] = 'cached'
                return cached
                
            # Return error state
            return {
                'status': 'error',
                'error': str(e),
                'last_updated': time.time()
            }
    
    def _fetch_data(self) -> Dict[str, Any]:
        """
        Fetch data from API. Must be implemented by subclasses.
        
        Returns:
            Raw API data dictionary
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _fetch_data method")
    
    def clear_cache(self) -> None:
        """Clear cached data for this API."""
        self.cache.clear(self.cache_key)
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get cache information for this API.
        
        Returns:
            Cache information dictionary
        """
        age = self.cache.get_age(self.cache_key)
        return {
            'cache_key': self.cache_key,
            'age_seconds': age,
            'is_expired': self.cache.is_expired(self.cache_key, self.update_interval),
            'last_error': self.last_error
        }
    
    def is_data_fresh(self) -> bool:
        """
        Check if cached data is fresh.
        
        Returns:
            True if data is fresh, False otherwise
        """
        return not self.cache.is_expired(self.cache_key, self.update_interval)
    
    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make HTTP request with error handling.
        
        Args:
            url: Request URL
            params: Request parameters
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: On request failure
        """
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response 