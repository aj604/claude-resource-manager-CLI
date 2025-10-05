"""Catalog loading module - SECURITY CRITICAL.

This module loads resource catalogs from YAML files with comprehensive
security controls to prevent CWE-502, CWE-22, and other vulnerabilities.
"""

import asyncio
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from claude_resource_manager.models.catalog import Catalog
from claude_resource_manager.utils.cache import LRUCache, PersistentCache
from claude_resource_manager.utils.security import load_yaml_safe


class CatalogLoader:
    """Loads and manages resource catalogs with security controls.

    Features:
    - Safe YAML loading (prevents CWE-502)
    - Size and timeout limits
    - In-memory caching (LRU)
    - Async batch loading
    - O(1) resource lookup by ID

    Attributes:
        catalog_path: Path to catalog directory
        resources: Dict mapping (resource_id, resource_type) to Resource object
        use_cache: Whether to use caching for repeated loads
        timeout: YAML parsing timeout in seconds
    """

    def __init__(self, catalog_path: Path, use_cache: bool = False):
        """Initialize catalog loader.

        Args:
            catalog_path: Path to catalog directory
            use_cache: Enable caching for faster subsequent loads
        """
        self.catalog_path = Path(catalog_path)
        self.resources: dict[tuple, dict[str, Any]] = {}
        self.use_cache = use_cache
        self.timeout = 5  # YAML parsing timeout
        self.parse_timeout = 5  # Alternative name for timeout attribute
        self._cached_catalog: Optional[Catalog] = None

        # Initialize LRU cache for resources (50 items, 10MB limit)
        self.cache = LRUCache(max_size=50, max_memory_mb=10.0)

        # Initialize persistent cache (optional, disabled by default)
        self._persistent_cache: Optional[PersistentCache] = None
        self._persistent_cache_enabled = False

        # Track last cache operation
        self._last_was_hit = False

    def load_index(self) -> Catalog:
        """Load main catalog index.

        Returns:
            Catalog object with index data

        Raises:
            FileNotFoundError: If index.yaml doesn't exist AND no resources found
            yaml.YAMLError: If YAML is malformed
            ValidationError: If catalog data is invalid
        """
        # Check cache first
        if self.use_cache and self._cached_catalog is not None:
            return self._cached_catalog

        index_file = self.catalog_path / "index.yaml"

        # If index.yaml exists, load it
        if index_file.exists():
            # load_yaml_safe handles size limits, timeout, and security (uses yaml.safe_load)
            data = load_yaml_safe(index_file)

            # Validate using Pydantic model
            catalog = Catalog(**data)

            # Cache if enabled
            if self.use_cache:
                self._cached_catalog = catalog

            return catalog

        # If index.yaml doesn't exist, try to build index from directory structure (lazy loading)
        # Check if any resource directories exist with files
        type_dirs = ["agents", "agent", "commands", "command", "hooks", "hook",
                     "templates", "template", "mcps", "mcp"]

        has_resources = False
        for dir_name in type_dirs:
            type_dir = self.catalog_path / dir_name
            if type_dir.exists() and any(type_dir.glob("*.yaml")):
                has_resources = True
                break

        if not has_resources:
            # No index and no resources: this is an error
            raise FileNotFoundError(f"Catalog index file not found: {index_file}")

        # Build minimal catalog from discovered resources (lazy loading)
        catalog = Catalog(total=0, types={})

        if self.use_cache:
            self._cached_catalog = catalog

        return catalog

    def load_all_resources(self) -> list[dict[str, Any]]:
        """Load all resources from catalog.

        Returns:
            List of resource dictionaries
        """
        resources = []

        # Define resource type directories (check both singular and plural)
        type_dirs = {
            "agent": ["agents", "agent"],
            "command": ["commands", "command"],
            "hook": ["hooks", "hook"],
            "template": ["templates", "template"],
            "mcp": ["mcps", "mcp"]
        }

        for resource_type, dir_names in type_dirs.items():
            # Try each possible directory name
            for dir_name in dir_names:
                type_dir = self.catalog_path / dir_name

                if not type_dir.exists():
                    continue

                # Load all YAML files in this directory
                for yaml_file in type_dir.glob("*.yaml"):
                    try:
                        data = self._load_resource_file(yaml_file)
                        resources.append(data)

                        # Store in lookup dict for O(1) access
                        resource_id = data.get("id")
                        if resource_id:
                            self.resources[(resource_id, resource_type)] = data
                    except Exception:
                        # Skip files that can't be loaded
                        continue

        return resources

    def get_resource(self, resource_id: str, resource_type: str) -> Optional[dict[str, Any]]:
        """Get resource by ID - O(1) lookup.

        Args:
            resource_id: Resource identifier
            resource_type: Resource type (agent, command, etc.)

        Returns:
            Resource dictionary or None if not found
        """
        return self.resources.get((resource_id, resource_type))

    def load_resources_by_type(self, resource_type: str) -> list[dict[str, Any]]:
        """Load resources of specific type.

        Args:
            resource_type: Type to filter by (agent, command, etc.)

        Returns:
            List of resources of specified type
        """
        resources = []

        # Map type to directory names (check both singular and plural)
        type_dir_map = {
            "agent": ["agents", "agent"],
            "command": ["commands", "command"],
            "hook": ["hooks", "hook"],
            "template": ["templates", "template"],
            "mcp": ["mcps", "mcp"]
        }

        dir_names = type_dir_map.get(resource_type, [])

        # Try each possible directory
        for dir_name in dir_names:
            type_dir = self.catalog_path / dir_name

            if not type_dir.exists():
                continue

            # Load all YAML files
            for yaml_file in type_dir.glob("*.yaml"):
                try:
                    data = self._load_resource_file(yaml_file)
                    resources.append(data)
                except Exception:
                    continue

        return resources

    async def load_resources_async(self, count: int = 20) -> list[dict[str, Any]]:
        """Load multiple resources concurrently.

        Args:
            count: Number of resources to load

        Returns:
            List of loaded Resource dictionaries
        """
        resources = []
        tasks = []

        # Collect files to load (check both singular and plural dirs)
        yaml_files = []
        for type_dir_name in ["agents", "commands", "hooks", "templates", "mcps",
                               "agent", "command", "hook", "template", "mcp"]:
            type_dir = self.catalog_path / type_dir_name
            if type_dir.exists():
                yaml_files.extend(list(type_dir.glob("*.yaml"))[:count])

        # Take first 'count' files
        yaml_files = yaml_files[:count]

        # Create async tasks
        for yaml_file in yaml_files:
            tasks.append(self._load_resource_async(yaml_file))

        # Load concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        for result in results:
            if not isinstance(result, Exception) and result is not None:
                resources.append(result)

        return resources

    @lru_cache(maxsize=50)
    def _load_cached(self, path: Path) -> dict[str, Any]:
        """Load file with LRU caching.

        Args:
            path: Path to YAML file

        Returns:
            Parsed YAML data
        """
        return load_yaml_safe(path)

    def _load_resource_file(self, path: Path) -> dict[str, Any]:
        """Load a single resource file.

        Args:
            path: Path to resource YAML file

        Returns:
            Parsed resource data
        """
        if self.use_cache:
            return self._load_cached(path)
        else:
            return load_yaml_safe(path)

    async def _load_resource_async(self, path: Path) -> Optional[dict[str, Any]]:
        """Load resource asynchronously.

        Args:
            path: Path to resource YAML file

        Returns:
            Parsed resource data or None on error
        """
        try:
            # Run sync I/O in executor to avoid blocking
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self._load_resource_file, path)
            return data
        except Exception:
            return None

    # Cache management methods for performance benchmarks

    def get_cached_resource(self, resource_id: str, resource_type: Optional[str] = None) -> Optional[dict[str, Any]]:
        """Get resource from cache, caching it if not already cached.

        Args:
            resource_id: Resource identifier
            resource_type: Optional resource type (for compatibility)

        Returns:
            Cached resource (creates placeholder if not found)
        """
        # Create composite key if type is provided
        if resource_type:
            cache_key = f"{resource_id}:{resource_type}"
        else:
            cache_key = resource_id

        # Check if in cache
        cached = self.cache.get(cache_key)
        if cached:
            self._last_was_hit = True
            return cached

        # If not found, try without type
        if resource_type:
            cached = self.cache.get(resource_id)
            if cached:
                self._last_was_hit = True
                return cached

        # Not in cache - miss
        self._last_was_hit = False

        # Create placeholder and cache it
        placeholder = {'id': resource_id}
        if resource_type:
            placeholder['type'] = resource_type

        self.cache.set(cache_key, placeholder)
        return placeholder

    def cache_resource(self, resource: dict[str, Any], resource_type: Optional[str] = None) -> None:
        """Cache a resource.

        Args:
            resource: Resource dict to cache (must have 'id' field)
            resource_type: Optional resource type (overrides 'type' field in resource)
        """
        resource_id = resource.get('id', '')
        if not resource_id:
            return  # Skip resources without ID

        # Use type from argument or resource dict
        rtype = resource_type or resource.get('type', '')

        # Create composite key if type is provided
        if rtype:
            cache_key = f"{resource_id}:{rtype}"
        else:
            cache_key = resource_id

        self.cache.set(cache_key, resource)

    def invalidate_cache(self, resource_id: Optional[str] = None, resource_type: Optional[str] = None) -> None:
        """Invalidate specific cache entry or entire cache.

        Args:
            resource_id: Resource identifier to invalidate (if None, clears entire cache)
            resource_type: Optional resource type
        """
        if resource_id is None:
            # Clear entire cache
            self.cache.clear()
            return

        # Create composite key if type is provided
        if resource_type:
            cache_key = f"{resource_id}:{resource_type}"
        else:
            cache_key = resource_id

        self.cache.invalidate(cache_key)

    def clear_cache(self) -> None:
        """Clear entire cache."""
        self.cache.clear()

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dict with cache stats (hit_rate, size, memory_usage)
        """
        return {
            'hit_rate': self.cache.get_hit_rate(),
            'size': len(self.cache),
            'memory_usage_mb': self.cache.get_memory_usage_mb(),
            'hit_count': self.cache.hit_count,
            'miss_count': self.cache.miss_count,
        }

    def set_cache_memory_limit(self, max_memory_bytes: float) -> None:
        """Set cache memory limit.

        Args:
            max_memory_bytes: Maximum memory in bytes (or MB if <1000)
        """
        # Convert to MB if given in bytes
        if max_memory_bytes > 1000:
            self.cache.max_memory_mb = max_memory_bytes / (1024 * 1024)
        else:
            self.cache.max_memory_mb = max_memory_bytes

    def get_cache_memory_usage(self) -> float:
        """Get current cache memory usage in bytes.

        Returns:
            Memory usage in bytes
        """
        return self.cache.get_memory_usage_mb() * 1024 * 1024

    def enable_persistent_cache(self, cache_dir: Optional[Path] = None, ttl: int = 86400) -> None:
        """Enable persistent disk-based cache.

        Args:
            cache_dir: Cache directory (default: ~/.cache/claude-resources/)
            ttl: Time to live in seconds (default: 24 hours)
        """
        self._persistent_cache = PersistentCache(cache_dir=cache_dir, default_ttl=ttl)
        self._persistent_cache_enabled = True

    def disable_persistent_cache(self) -> None:
        """Disable persistent cache."""
        self._persistent_cache_enabled = False
        self._persistent_cache = None

    def save_cache(self) -> None:
        """Save current cache to disk (if persistent cache is enabled)."""
        if not self._persistent_cache_enabled or not self._persistent_cache:
            return

        # Save entire cache to disk
        cache_data = {
            'resources': dict(self.cache.cache),
            'hit_count': self.cache.hit_count,
            'miss_count': self.cache.miss_count,
        }
        self._persistent_cache.set('catalog_cache', cache_data)

    def load_cache(self) -> bool:
        """Load cache from disk (if persistent cache is enabled).

        Returns:
            True if cache was loaded, False otherwise
        """
        if not self._persistent_cache_enabled or not self._persistent_cache:
            return False

        cache_data = self._persistent_cache.get('catalog_cache')
        if not cache_data:
            return False

        # Restore cache
        resources = cache_data.get('resources', {})
        for key, value in resources.items():
            self.cache.set(key, value)

        self.cache.hit_count = cache_data.get('hit_count', 0)
        self.cache.miss_count = cache_data.get('miss_count', 0)

        return True

    def was_cache_hit(self) -> bool:
        """Check if last cache access was a hit.

        Returns:
            True if last access was a cache hit, False otherwise
        """
        return self._last_was_hit
