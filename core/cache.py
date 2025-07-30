"""
Thread-safe data caching for API responses and application data.
"""

import threading
import time
from typing import Dict, Any, Optional


class DataCache:
    """Thread-safe data cache for API responses and application data."""
    
    def __init__(self):
        """Initialize the data cache with thread-safe operations."""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached data.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found
        """
        with self._lock:
            cache_entry = self._cache.get(key)
            return cache_entry.get('data') if cache_entry else None
    
    def set(self, key: str, data: Dict[str, Any]) -> None:
        """
        Set cached data with timestamp.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        with self._lock:
            self._cache[key] = {
                'data': data,
                'timestamp': time.time()
            }
    
    def is_expired(self, key: str, max_age: int) -> bool:
        """
        Check if cached data is expired.
        
        Args:
            key: Cache key
            max_age: Maximum age in seconds
            
        Returns:
            True if expired or not found, False otherwise
        """
        with self._lock:
            if key not in self._cache:
                return True
            return time.time() - self._cache[key]['timestamp'] > max_age
    
    def clear(self, key: str = None) -> None:
        """
        Clear cached data.
        
        Args:
            key: Specific key to clear, or None to clear all
        """
        with self._lock:
            if key:
                self._cache.pop(key, None)
            else:
                self._cache.clear()
    
    def get_age(self, key: str) -> Optional[float]:
        """
        Get age of cached data in seconds.
        
        Args:
            key: Cache key
            
        Returns:
            Age in seconds or None if not found
        """
        with self._lock:
            if key not in self._cache:
                return None
            return time.time() - self._cache[key]['timestamp']
    
    def get_all_keys(self) -> list:
        """
        Get all cache keys.
        
        Returns:
            List of cache keys
        """
        with self._lock:
            return list(self._cache.keys())
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get cache statistics and information.
        
        Returns:
            Dictionary with cache information
        """
        with self._lock:
            current_time = time.time()
            info = {
                'total_entries': len(self._cache),
                'entries': {}
            }
            
            for key, entry in self._cache.items():
                info['entries'][key] = {
                    'age_seconds': current_time - entry['timestamp'],
                    'size_bytes': len(str(entry['data']))
                }
            
            return info 