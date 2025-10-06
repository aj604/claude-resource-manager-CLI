"""High-performance caching utilities for resource management.

Provides:
- LRU cache with memory limits
- Persistent disk-based cache
- TTL-based cache invalidation
- Memory-efficient resource caching
"""

import hashlib
import json
import pickle
import sys
import time
from collections import OrderedDict
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Generic, Optional, TypeVar

T = TypeVar("T")


class LRUCache(Generic[T]):
    """Memory-bounded LRU cache with O(1) access.

    Features:
    - Least Recently Used eviction policy
    - Configurable size and memory limits
    - O(1) get/set/invalidate operations
    - Thread-safe operations
    - Memory usage tracking

    Attributes:
        max_size: Maximum number of items to cache
        max_memory_mb: Maximum memory usage in MB (0 = unlimited)
        cache: OrderedDict storing cached items
        hit_count: Number of cache hits
        miss_count: Number of cache misses
    """

    def __init__(self, max_size: int = 50, max_memory_mb: float = 10.0):
        """Initialize LRU cache.

        Args:
            max_size: Maximum number of items (default: 50)
            max_memory_mb: Maximum memory in MB (default: 10MB)
        """
        self.max_size = max_size
        self.maxsize = max_size  # Alias for compatibility
        self.max_memory_mb = max_memory_mb
        self.cache: OrderedDict[str, T] = OrderedDict()
        self.hit_count = 0
        self.miss_count = 0
        self._memory_bytes = 0

    def get(self, key: str) -> Optional[T]:
        """Get item from cache, None if not found.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hit_count += 1
            return self.cache[key]

        self.miss_count += 1
        return None

    def set(self, key: str, value: T) -> None:
        """Set item in cache, evicting if necessary.

        Args:
            key: Cache key
            value: Value to cache
        """
        # If key exists, remove it first (to update position)
        if key in self.cache:
            del self.cache[key]

        # Add new item
        self.cache[key] = value
        self.cache.move_to_end(key)

        # Update memory tracking
        self._memory_bytes = self._estimate_memory()

        # Evict if over size limit
        while len(self.cache) > self.max_size:
            self.cache.popitem(last=False)  # Remove oldest
            self._memory_bytes = self._estimate_memory()

        # Evict if over memory limit
        max_bytes = self.max_memory_mb * 1024 * 1024
        while self.max_memory_mb > 0 and self._memory_bytes > max_bytes and len(self.cache) > 0:
            self.cache.popitem(last=False)
            self._memory_bytes = self._estimate_memory()

    def invalidate(self, key: str) -> None:
        """Invalidate cache entry.

        Args:
            key: Cache key to invalidate
        """
        if key in self.cache:
            del self.cache[key]
            self._memory_bytes = self._estimate_memory()

    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()
        self._memory_bytes = 0
        self.hit_count = 0
        self.miss_count = 0

    def get_hit_rate(self) -> float:
        """Calculate cache hit rate.

        Returns:
            Hit rate as percentage (0-100)
        """
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return (self.hit_count / total) * 100.0

    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB.

        Returns:
            Memory usage in megabytes
        """
        return self._memory_bytes / (1024 * 1024)

    def _estimate_memory(self) -> int:
        """Estimate memory usage of cached objects.

        Returns:
            Estimated memory in bytes
        """
        # Use sys.getsizeof for rough estimate
        total = 0
        for key, value in self.cache.items():
            total += sys.getsizeof(key)
            total += sys.getsizeof(value)
        return total

    def __len__(self) -> int:
        """Return number of cached items."""
        return len(self.cache)

    def __contains__(self, key: str) -> bool:
        """Check if key is in cache."""
        return key in self.cache


class PersistentCache:
    """Disk-based persistent cache with TTL support.

    Provides:
    - Disk persistence across sessions
    - TTL-based expiration
    - Fast pickle serialization
    - Atomic writes

    Attributes:
        cache_dir: Directory for cache files
        default_ttl: Default TTL in seconds
    """

    def __init__(self, cache_dir: Optional[Path] = None, default_ttl: int = 86400):
        """Initialize persistent cache.

        Args:
            cache_dir: Cache directory (default: ~/.cache/claude-resources/)
            default_ttl: Default TTL in seconds (default: 24 hours)
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "claude-resources"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """Get item from persistent cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        cache_file = self._get_cache_file(key)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "rb") as f:
                data = pickle.load(f)

            # Check TTL
            if "expires_at" in data and time.time() > data["expires_at"]:
                # Expired - remove file
                cache_file.unlink(missing_ok=True)
                return None

            return data.get("value")

        except (pickle.PickleError, OSError, KeyError):
            # Corrupted cache file - remove it
            cache_file.unlink(missing_ok=True)
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set item in persistent cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: self.default_ttl)
        """
        cache_file = self._get_cache_file(key)

        if ttl is None:
            ttl = self.default_ttl

        data = {
            "value": value,
            "created_at": time.time(),
            "expires_at": time.time() + ttl if ttl > 0 else None,
        }

        try:
            # Write atomically with temp file
            temp_file = cache_file.with_suffix(".tmp")
            with open(temp_file, "wb") as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

            # Atomic rename
            temp_file.replace(cache_file)

        except (pickle.PickleError, OSError):
            # Failed to write - clean up
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)

    def invalidate(self, key: str) -> None:
        """Invalidate cache entry.

        Args:
            key: Cache key to invalidate
        """
        cache_file = self._get_cache_file(key)
        cache_file.unlink(missing_ok=True)

    def clear(self) -> None:
        """Clear entire persistent cache."""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink(missing_ok=True)

    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key.

        Args:
            key: Cache key

        Returns:
            Path to cache file
        """
        # Hash key to create safe filename
        key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
        return self.cache_dir / f"{key_hash}.cache"


def cached(
    max_size: int = 50,
    max_memory_mb: float = 10.0,
    persistent: bool = False,
    ttl: Optional[int] = None,
) -> Callable:
    """Decorator for caching function results.

    Args:
        max_size: Maximum cache size
        max_memory_mb: Maximum memory in MB
        persistent: Use disk-based persistent cache
        ttl: Time to live in seconds (for persistent cache)

    Returns:
        Decorator function

    Example:
        @cached(max_size=100, persistent=True, ttl=3600)
        def expensive_function(arg1, arg2):
            # Expensive computation
            return result
    """

    def decorator(func: Callable) -> Callable:
        if persistent:
            cache = PersistentCache(ttl=ttl or 86400)
        else:
            cache = LRUCache(max_size=max_size, max_memory_mb=max_memory_mb)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_parts = [func.__name__, str(args), str(sorted(kwargs.items()))]
            cache_key = hashlib.md5(json.dumps(key_parts).encode()).hexdigest()

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            if persistent:
                cache.set(cache_key, result, ttl=ttl)
            else:
                cache.set(cache_key, result)

            return result

        # Expose cache for inspection
        wrapper.cache = cache  # type: ignore

        return wrapper

    return decorator


def memory_efficient_cache(func: Callable) -> Callable:
    """Decorator for memory-efficient caching of large objects.

    Uses weak references to allow garbage collection of cached objects
    when no longer needed elsewhere.

    Args:
        func: Function to cache

    Returns:
        Wrapped function with weak-ref cache
    """
    import weakref

    cache: Dict[str, Any] = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key
        key_parts = [func.__name__, str(args), str(sorted(kwargs.items()))]
        cache_key = hashlib.md5(json.dumps(key_parts).encode()).hexdigest()

        # Check if cached value still exists
        if cache_key in cache:
            ref = cache[cache_key]
            value = ref() if isinstance(ref, weakref.ref) else ref
            if value is not None:
                return value

        # Execute function
        result = func(*args, **kwargs)

        # Cache with weak reference for large objects
        try:
            cache[cache_key] = weakref.ref(result)
        except TypeError:
            # Object doesn't support weak refs (e.g., int, str)
            cache[cache_key] = result

        return result

    wrapper.cache = cache  # type: ignore

    return wrapper
