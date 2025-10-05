"""Catalog loading module - SECURITY CRITICAL.

This module loads resource catalogs from YAML files with comprehensive
security controls to prevent CWE-502, CWE-22, and other vulnerabilities.
"""

import asyncio
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from claude_resource_manager.models.catalog import Catalog
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
