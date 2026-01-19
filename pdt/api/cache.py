"""
Caching Layer - Redis/Memcached for frequent queries.
"""

from typing import Optional, Any, Dict
import hashlib
import json
import pickle


class SimpleCache:
    """Simple in-memory cache (can be replaced with Redis)."""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum cache size
        """
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
    
    def _hash_key(self, key: Any) -> str:
        """Hash key for caching."""
        if isinstance(key, (dict, list)):
            key_str = json.dumps(key, sort_keys=True)
        else:
            key_str = str(key)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: Any) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        cache_key = self._hash_key(key)
        return self.cache.get(cache_key)
    
    def set(self, key: Any, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live (not implemented in simple cache)
        """
        if len(self.cache) >= self.max_size:
            # Remove oldest (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        cache_key = self._hash_key(key)
        self.cache[cache_key] = value
    
    def clear(self):
        """Clear cache."""
        self.cache.clear()


# Global cache instance
cache = SimpleCache()

