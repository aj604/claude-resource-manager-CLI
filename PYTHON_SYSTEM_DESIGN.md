# Python-Based Claude Resource Manager CLI - System Architecture

**Document Type:** System Design & Architecture
**Date:** October 4, 2025
**Role:** BlueprintMaster - System Design Specialist
**Status:** Complete System Architecture

---

## Executive Summary

This document defines the complete system architecture for the Python-based Claude Resource Manager CLI, translating the Go-based design into Pythonic patterns while maintaining performance targets and user experience goals.

**Key Design Decisions:**
- **Python 3.11+** for performance improvements (10-15% faster than 3.9)
- **Textual framework** for rich TUI with CSS-like styling
- **AsyncIO** for concurrent operations (downloads, catalog loading)
- **Pydantic models** for data validation and serialization
- **Type hints** throughout for maintainability and IDE support
- **Lazy loading** and **caching** to meet performance targets

---

## 1. Python Package Structure

### 1.1 Module Organization

```
claude_resource_manager/
├── pyproject.toml                    # Modern Python packaging (PEP 621)
├── setup.cfg                         # Additional config (flake8, mypy)
├── README.md                         # Project documentation
├── LICENSE                           # MIT license
├── requirements.txt                  # Production dependencies
├── requirements-dev.txt              # Development dependencies
│
├── claude_resource_manager/          # Main package
│   ├── __init__.py                  # Package initialization
│   ├── __main__.py                  # Entry point for python -m
│   ├── __version__.py               # Version management
│   │
│   ├── cli/                         # CLI layer (thin)
│   │   ├── __init__.py
│   │   ├── app.py                   # Main CLI app (Click)
│   │   ├── commands/                # CLI commands
│   │   │   ├── __init__.py
│   │   │   ├── browse.py            # Browse command
│   │   │   ├── install.py           # Install command
│   │   │   ├── search.py            # Search command
│   │   │   └── deps.py              # Dependency command
│   │   └── config.py                # CLI configuration
│   │
│   ├── tui/                         # TUI layer (Textual)
│   │   ├── __init__.py
│   │   ├── app.py                   # Main TUI application
│   │   ├── screens/                 # TUI screens
│   │   │   ├── __init__.py
│   │   │   ├── browser.py           # Resource browser screen
│   │   │   ├── search.py            # Search screen
│   │   │   └── installer.py         # Installation progress screen
│   │   ├── widgets/                 # Custom widgets
│   │   │   ├── __init__.py
│   │   │   ├── resource_list.py     # Resource list widget
│   │   │   ├── preview_pane.py      # Preview pane widget
│   │   │   ├── category_tree.py     # Category tree widget
│   │   │   └── progress_bar.py      # Progress indicator
│   │   └── styles/                  # CSS styles
│   │       ├── __init__.py
│   │       └── theme.css            # TUI theme
│   │
│   ├── core/                        # Business logic
│   │   ├── __init__.py
│   │   ├── models.py                # Pydantic data models
│   │   ├── catalog_loader.py        # YAML catalog loading
│   │   ├── search_index.py          # Search functionality
│   │   ├── category_engine.py       # Category extraction
│   │   ├── dependency_resolver.py   # Dependency graph
│   │   ├── installer.py             # Installation logic
│   │   └── exceptions.py            # Custom exceptions
│   │
│   ├── data/                        # Data layer
│   │   ├── __init__.py
│   │   ├── cache.py                 # Caching layer
│   │   ├── registry.py              # Registry management
│   │   ├── downloader.py            # GitHub downloads
│   │   └── state.py                 # Installation state
│   │
│   ├── utils/                       # Utilities
│   │   ├── __init__.py
│   │   ├── async_helpers.py         # Async utilities
│   │   ├── performance.py           # Performance monitoring
│   │   ├── validators.py            # Path/data validation
│   │   └── logging_config.py        # Logging configuration
│   │
│   └── config/                      # Configuration
│       ├── __init__.py
│       ├── settings.py              # Application settings
│       └── constants.py             # Constants
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   ├── unit/                        # Unit tests (70%)
│   ├── integration/                 # Integration tests (25%)
│   ├── e2e/                         # End-to-end tests (5%)
│   └── fixtures/                    # Test data
│
└── docs/                            # Documentation
    ├── api/                         # API documentation
    ├── user_guide/                  # User documentation
    └── developer/                   # Developer docs
```

### 1.2 Separation of Concerns

```python
# Layer boundaries and responsibilities

# Presentation Layer (CLI + TUI)
# - User interaction
# - Command parsing
# - Display formatting
# - No business logic

# Business Layer (Core)
# - Resource management
# - Search algorithms
# - Dependency resolution
# - Category extraction
# - Installation orchestration

# Data Layer
# - YAML parsing
# - File I/O
# - HTTP downloads
# - Caching
# - State persistence

# Cross-cutting (Utils)
# - Logging
# - Performance monitoring
# - Validation
# - Error handling
```

### 1.3 Testability Considerations

```python
# Dependency Injection Pattern
class ResourceManager:
    def __init__(
        self,
        catalog_loader: CatalogLoader,
        search_index: SearchIndex,
        installer: Installer,
        cache: Optional[Cache] = None,
    ):
        self.catalog_loader = catalog_loader
        self.search_index = search_index
        self.installer = installer
        self.cache = cache or Cache()

# Easy to test with mocks
def test_resource_manager():
    mock_loader = Mock(spec=CatalogLoader)
    mock_index = Mock(spec=SearchIndex)
    mock_installer = Mock(spec=Installer)

    manager = ResourceManager(
        mock_loader,
        mock_index,
        mock_installer
    )
    # Test behavior, not implementation
```

---

## 2. Data Flow Design

### 2.1 Startup Sequence Optimization

```python
import asyncio
from typing import List, Dict
import time

class FastStartupManager:
    """Optimized startup sequence to meet <100ms target"""

    async def startup(self) -> None:
        """
        Startup sequence:
        1. Load minimal index (5-10ms)
        2. Initialize TUI framework (20-30ms)
        3. Background load full catalog (async)
        4. Show UI immediately with loading state
        """
        start = time.perf_counter()

        # Phase 1: Critical path (must complete)
        index = await self._load_minimal_index()  # 5-10ms

        # Phase 2: UI initialization (parallel)
        ui_task = asyncio.create_task(self._init_ui())  # 20-30ms

        # Phase 3: Background loading (non-blocking)
        asyncio.create_task(self._load_full_catalog())  # 50-100ms

        # Wait only for UI
        await ui_task

        elapsed = (time.perf_counter() - start) * 1000
        logger.debug(f"Startup completed in {elapsed:.1f}ms")

    async def _load_minimal_index(self) -> Dict:
        """Load just resource counts and types"""
        async with aiofiles.open('catalog/index.yaml', 'r') as f:
            content = await f.read()
            return yaml.safe_load(content)

    async def _load_full_catalog(self) -> None:
        """Load all resources in background"""
        tasks = [
            self._load_type_catalog('agents'),
            self._load_type_catalog('commands'),
            self._load_type_catalog('hooks'),
            self._load_type_catalog('templates'),
            self._load_type_catalog('mcps'),
        ]
        await asyncio.gather(*tasks)
```

### 2.2 Catalog Loading Strategy

```python
from pathlib import Path
import yaml
from pydantic import BaseModel
from typing import Optional, Dict, List
import aiofiles
import asyncio

class LazyLoadCatalog:
    """Lazy loading with progressive enhancement"""

    def __init__(self, catalog_path: Path):
        self.catalog_path = catalog_path
        self._index_cache: Optional[Dict] = None
        self._resource_cache: Dict[str, Resource] = {}
        self._loading_tasks: Dict[str, asyncio.Task] = {}

    async def get_index(self) -> Dict:
        """Get catalog index (cached)"""
        if self._index_cache is None:
            async with aiofiles.open(self.catalog_path / 'index.yaml') as f:
                content = await f.read()
                self._index_cache = yaml.safe_load(content)
        return self._index_cache

    async def get_resource(self, resource_id: str, resource_type: str) -> Resource:
        """Get single resource (lazy load)"""
        cache_key = f"{resource_type}/{resource_id}"

        # Check cache
        if cache_key in self._resource_cache:
            return self._resource_cache[cache_key]

        # Check if already loading
        if cache_key in self._loading_tasks:
            return await self._loading_tasks[cache_key]

        # Start loading
        task = asyncio.create_task(self._load_resource(resource_id, resource_type))
        self._loading_tasks[cache_key] = task

        try:
            resource = await task
            self._resource_cache[cache_key] = resource
            return resource
        finally:
            del self._loading_tasks[cache_key]

    async def _load_resource(self, resource_id: str, resource_type: str) -> Resource:
        """Load resource from disk"""
        path = self.catalog_path / resource_type / f"{resource_id}.yaml"
        async with aiofiles.open(path) as f:
            content = await f.read()
            data = yaml.safe_load(content)
            return Resource(**data)

    async def preload_visible(self, visible_ids: List[str], resource_type: str):
        """Preload resources that will be visible"""
        tasks = [
            self.get_resource(rid, resource_type)
            for rid in visible_ids
            if f"{resource_type}/{rid}" not in self._resource_cache
        ]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
```

### 2.3 Search Index Implementation

```python
from typing import List, Dict, Set, Optional
import re
from rapidfuzz import fuzz, process
from collections import defaultdict
import threading

class SearchIndex:
    """High-performance search index with multiple strategies"""

    def __init__(self):
        self._resources: Dict[str, Resource] = {}
        self._inverted_index: Dict[str, Set[str]] = defaultdict(set)
        self._prefix_tree: PrefixTree = PrefixTree()
        self._lock = threading.RLock()
        self._fuzzy_cache: Dict[str, List[tuple]] = {}

    def add_resource(self, resource: Resource) -> None:
        """Add resource to all indexes"""
        with self._lock:
            # Add to main index
            self._resources[resource.id] = resource

            # Add to inverted index (for word search)
            words = self._tokenize(resource.id, resource.name, resource.description)
            for word in words:
                self._inverted_index[word.lower()].add(resource.id)

            # Add to prefix tree (for prefix search)
            self._prefix_tree.insert(resource.id)

            # Clear fuzzy cache (invalidate)
            self._fuzzy_cache.clear()

    def search(self, query: str, mode: str = 'smart') -> List[Resource]:
        """
        Search with multiple strategies

        Modes:
        - exact: Exact ID match
        - prefix: Prefix matching
        - fuzzy: Fuzzy string matching
        - smart: Combines all strategies with ranking
        """
        query = query.lower().strip()

        if mode == 'exact':
            return self._exact_search(query)
        elif mode == 'prefix':
            return self._prefix_search(query)
        elif mode == 'fuzzy':
            return self._fuzzy_search(query)
        else:  # smart
            return self._smart_search(query)

    def _exact_search(self, query: str) -> List[Resource]:
        """O(1) exact match"""
        resource = self._resources.get(query)
        return [resource] if resource else []

    def _prefix_search(self, query: str) -> List[Resource]:
        """O(k) prefix search where k = query length"""
        matches = self._prefix_tree.find_prefix(query)
        return [self._resources[rid] for rid in matches]

    def _fuzzy_search(self, query: str, limit: int = 20) -> List[Resource]:
        """Fuzzy string matching with caching"""
        if query in self._fuzzy_cache:
            matches = self._fuzzy_cache[query]
        else:
            # Use rapidfuzz for fast fuzzy matching
            resource_ids = list(self._resources.keys())
            matches = process.extract(
                query,
                resource_ids,
                scorer=fuzz.WRatio,
                limit=limit
            )
            self._fuzzy_cache[query] = matches

        return [
            self._resources[match[0]]
            for match in matches
            if match[1] > 60  # Minimum score threshold
        ]

    def _smart_search(self, query: str) -> List[Resource]:
        """Combines multiple strategies with ranking"""
        results = []
        seen = set()

        # Priority 1: Exact matches
        exact = self._exact_search(query)
        for r in exact:
            if r.id not in seen:
                results.append((r, 100))  # Perfect score
                seen.add(r.id)

        # Priority 2: Prefix matches
        prefix = self._prefix_search(query)
        for r in prefix:
            if r.id not in seen:
                results.append((r, 90))  # High score
                seen.add(r.id)

        # Priority 3: Fuzzy matches
        fuzzy = self._fuzzy_search(query)
        for r in fuzzy:
            if r.id not in seen:
                # Calculate score based on fuzzy match quality
                score = fuzz.WRatio(query, r.id)
                results.append((r, score))
                seen.add(r.id)

        # Sort by score and return resources
        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results]

    def _tokenize(self, *texts: str) -> Set[str]:
        """Extract searchable tokens from text"""
        tokens = set()
        for text in texts:
            if text:
                # Split on non-alphanumeric
                words = re.findall(r'\w+', text.lower())
                tokens.update(words)
        return tokens

class PrefixTree:
    """Trie implementation for prefix search"""

    def __init__(self):
        self.root = {}

    def insert(self, word: str) -> None:
        """Insert word into trie"""
        node = self.root
        for char in word.lower():
            if char not in node:
                node[char] = {}
            node = node[char]
        node['$'] = word  # Store original word at leaf

    def find_prefix(self, prefix: str) -> List[str]:
        """Find all words with given prefix"""
        node = self.root
        for char in prefix.lower():
            if char not in node:
                return []
            node = node[char]

        # Collect all words from this node
        results = []
        self._collect_words(node, results)
        return results

    def _collect_words(self, node: Dict, results: List[str]) -> None:
        """Recursively collect all words from node"""
        if '$' in node:
            results.append(node['$'])
        for char, child in node.items():
            if char != '$':
                self._collect_words(child, results)
```

### 2.4 Installation Workflow

```python
import asyncio
from pathlib import Path
from typing import List, Optional, Set
import aiohttp
import aiofiles
from tqdm.asyncio import tqdm

class AsyncInstaller:
    """Asynchronous installation with progress tracking"""

    def __init__(self, base_path: Path = Path.home() / '.claude'):
        self.base_path = base_path
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(5)  # Max 5 concurrent downloads

    async def install_with_deps(self, resource: Resource) -> InstallResult:
        """Install resource with all dependencies"""
        # Resolve dependencies
        plan = await self._resolve_dependencies(resource)

        # Show plan to user
        if not await self._confirm_plan(plan):
            return InstallResult(cancelled=True)

        # Execute installation
        results = []
        async with aiohttp.ClientSession() as self.session:
            # Install in topological order
            for level in plan.installation_order:
                # Install level in parallel
                tasks = [
                    self._install_resource(r)
                    for r in level
                    if not self._is_installed(r)
                ]
                if tasks:
                    level_results = await tqdm.gather(*tasks, desc=f"Installing level")
                    results.extend(level_results)

        return InstallResult(
            installed=results,
            already_installed=plan.already_installed,
            success=all(r.success for r in results)
        )

    async def _install_resource(self, resource: Resource) -> ResourceInstallResult:
        """Install single resource"""
        async with self.semaphore:  # Rate limiting
            try:
                # Download content
                content = await self._download(resource.source.url)

                # Validate content
                if not self._validate_content(content, resource):
                    raise ValueError(f"Content validation failed for {resource.id}")

                # Write atomically
                target_path = self._get_install_path(resource)
                await self._atomic_write(target_path, content)

                # Update state
                await self._update_state(resource, 'installed')

                return ResourceInstallResult(
                    resource=resource,
                    success=True,
                    path=target_path
                )
            except Exception as e:
                logger.error(f"Failed to install {resource.id}: {e}")
                return ResourceInstallResult(
                    resource=resource,
                    success=False,
                    error=str(e)
                )

    async def _download(self, url: str) -> bytes:
        """Download with retry logic"""
        for attempt in range(3):
            try:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    return await response.read()
            except Exception as e:
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def _atomic_write(self, path: Path, content: bytes) -> None:
        """Atomic file write (temp + rename)"""
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix('.tmp')

        try:
            async with aiofiles.open(temp_path, 'wb') as f:
                await f.write(content)

            # Atomic rename
            temp_path.rename(path)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def _get_install_path(self, resource: Resource) -> Path:
        """Get installation path for resource"""
        type_dir = {
            'agent': 'agents',
            'command': 'commands',
            'hook': 'hooks',
            'template': 'templates',
            'mcp': 'mcps'
        }.get(resource.type, resource.type)

        filename = f"{resource.id}{resource.file_type}"
        return self.base_path / type_dir / filename
```

---

## 3. Python-Specific Design Patterns

### 3.1 Async/Await Usage Strategy

```python
# When to use async/await in the CLI

# YES - Network I/O (downloads, API calls)
async def download_resources(urls: List[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# YES - File I/O for large files
async def load_large_catalog():
    async with aiofiles.open('catalog.yaml') as f:
        content = await f.read()
        return yaml.safe_load(content)

# YES - Concurrent operations
async def search_multiple_indexes(query: str):
    results = await asyncio.gather(
        search_local(query),
        search_remote(query),
        search_fuzzy(query)
    )
    return merge_results(results)

# NO - CPU-bound operations (use threading/multiprocessing)
def build_search_index(resources: List[Resource]):
    # This is CPU-bound, don't use async
    index = SearchIndex()
    for resource in resources:
        index.add(resource)  # Synchronous
    return index

# NO - Simple, fast operations
def extract_category(resource_id: str) -> Category:
    # This is instant, no need for async
    parts = resource_id.split('-')
    return Category(primary=parts[0], secondary=parts[1] if len(parts) > 1 else None)
```

### 3.2 Type Hints Strategy

```python
from typing import (
    Dict, List, Optional, Union, Tuple, Set,
    TypeVar, Generic, Protocol, Literal, TypedDict,
    Callable, Awaitable, Any
)
from typing_extensions import NotRequired, Self
import mypy

# Use strict type hints throughout
T = TypeVar('T')
ResourceType = Literal['agent', 'command', 'hook', 'template', 'mcp']

# Protocol for duck typing
class Searchable(Protocol):
    """Protocol for searchable objects"""
    id: str
    name: str
    description: str

    def matches(self, query: str) -> bool:
        ...

# TypedDict for structured dicts
class CatalogIndex(TypedDict):
    total: int
    types: Dict[ResourceType, int]
    last_updated: str
    version: NotRequired[str]

# Generic types for reusability
class Cache(Generic[T]):
    def __init__(self, max_size: int = 100):
        self._cache: Dict[str, T] = {}
        self._max_size = max_size

    def get(self, key: str) -> Optional[T]:
        return self._cache.get(key)

    def set(self, key: str, value: T) -> None:
        if len(self._cache) >= self._max_size:
            # LRU eviction
            oldest = next(iter(self._cache))
            del self._cache[oldest]
        self._cache[key] = value

# Complex return types
async def search_with_stats(
    query: str
) -> Tuple[List[Resource], Dict[str, Any]]:
    """Returns resources and search statistics"""
    start = time.perf_counter()
    results = await search(query)
    stats = {
        'query': query,
        'count': len(results),
        'time_ms': (time.perf_counter() - start) * 1000,
        'strategy': 'fuzzy' if len(query) < 3 else 'exact'
    }
    return results, stats

# Mypy configuration in setup.cfg
"""
[mypy]
python_version = 3.11
strict = True
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
"""
```

### 3.3 Pydantic vs Dataclasses

```python
from pydantic import BaseModel, Field, validator, root_validator
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime

# PYDANTIC - For external data (YAML, JSON, API)
class Resource(BaseModel):
    """Resource model with validation"""
    id: str = Field(..., min_length=1, max_length=100)
    type: ResourceType
    name: str
    description: str = Field(..., max_length=1000)
    version: str = Field(default='v1.0.0', regex=r'^v\d+\.\d+\.\d+$')
    source: 'Source'
    metadata: Dict[str, Any] = Field(default_factory=dict)
    dependencies: Optional['Dependencies'] = None

    class Config:
        # Optimize for performance
        validate_assignment = True
        use_enum_values = True
        arbitrary_types_allowed = False

    @validator('id')
    def validate_id(cls, v: str) -> str:
        """Ensure ID follows naming convention"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError(f"Invalid ID format: {v}")
        return v.lower()

    @root_validator
    def check_dependencies(cls, values):
        """Validate dependency constraints"""
        deps = values.get('dependencies')
        if deps and deps.required:
            # Check for self-reference
            if values['id'] in deps.required:
                raise ValueError("Resource cannot depend on itself")
        return values

class Source(BaseModel):
    """Source information model"""
    repo: str
    path: str
    url: str = Field(..., regex=r'^https://.*')

# DATACLASSES - For internal state (performance-critical)
@dataclass
class SearchResult:
    """Internal search result (no validation needed)"""
    resource: Resource
    score: float
    match_type: Literal['exact', 'prefix', 'fuzzy']
    highlights: List[Tuple[int, int]] = field(default_factory=list)

    def __lt__(self, other: 'SearchResult') -> bool:
        """For sorting by score"""
        return self.score < other.score

@dataclass
class InstallState:
    """Internal installation state"""
    installed_resources: Set[str] = field(default_factory=set)
    install_history: List[Tuple[str, datetime]] = field(default_factory=list)
    failed_attempts: Dict[str, str] = field(default_factory=dict)

    def is_installed(self, resource_id: str) -> bool:
        return resource_id in self.installed_resources

    def mark_installed(self, resource_id: str) -> None:
        self.installed_resources.add(resource_id)
        self.install_history.append((resource_id, datetime.now()))

# Decision Matrix:
# Use Pydantic when:
# - Parsing external data (YAML, JSON)
# - Need validation
# - Serialization/deserialization
# - API boundaries

# Use Dataclasses when:
# - Internal data structures
# - Performance critical
# - No validation needed
# - Simple containers
```

### 3.4 Error Handling Patterns

```python
from typing import Optional, Union
from enum import Enum
import traceback

class ErrorSeverity(Enum):
    """Error severity levels"""
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ResourceManagerError(Exception):
    """Base exception for resource manager"""
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.ERROR):
        self.message = message
        self.severity = severity
        super().__init__(message)

class CatalogError(ResourceManagerError):
    """Catalog-related errors"""
    pass

class DependencyError(ResourceManagerError):
    """Dependency resolution errors"""
    pass

class InstallationError(ResourceManagerError):
    """Installation errors"""
    pass

class NetworkError(ResourceManagerError):
    """Network-related errors"""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after

# Error handling with context managers
from contextlib import contextmanager, asynccontextmanager

@contextmanager
def error_handler(operation: str, fallback=None):
    """Generic error handler with logging"""
    try:
        yield
    except CatalogError as e:
        logger.error(f"Catalog error during {operation}: {e.message}")
        if fallback is not None:
            return fallback
        raise
    except Exception as e:
        logger.error(f"Unexpected error during {operation}: {e}")
        logger.debug(traceback.format_exc())
        raise ResourceManagerError(f"Failed to {operation}: {str(e)}")

@asynccontextmanager
async def async_error_handler(operation: str):
    """Async error handler"""
    try:
        yield
    except asyncio.CancelledError:
        logger.info(f"Operation {operation} cancelled")
        raise
    except Exception as e:
        logger.error(f"Error in {operation}: {e}")
        raise

# Usage examples
def load_catalog(path: Path) -> Catalog:
    with error_handler("catalog loading"):
        return Catalog.from_yaml(path)

async def install_resource(resource: Resource) -> bool:
    async with async_error_handler(f"installing {resource.id}"):
        await download_and_install(resource)
        return True

# Result type pattern (like Rust's Result<T, E>)
from typing import TypeVar, Generic, Union

T = TypeVar('T')
E = TypeVar('E')

class Result(Generic[T, E]):
    """Result type for explicit error handling"""

    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        assert (value is None) != (error is None), "Must have either value or error"
        self._value = value
        self._error = error

    @property
    def is_ok(self) -> bool:
        return self._value is not None

    @property
    def is_err(self) -> bool:
        return self._error is not None

    def unwrap(self) -> T:
        if self._value is None:
            raise ValueError(f"Called unwrap on error: {self._error}")
        return self._value

    def unwrap_or(self, default: T) -> T:
        return self._value if self._value is not None else default

    @classmethod
    def ok(cls, value: T) -> 'Result[T, E]':
        return cls(value=value)

    @classmethod
    def err(cls, error: E) -> 'Result[T, E]':
        return cls(error=error)

# Usage
def parse_version(version_str: str) -> Result[tuple, str]:
    try:
        parts = version_str.strip('v').split('.')
        return Result.ok(tuple(map(int, parts)))
    except ValueError as e:
        return Result.err(f"Invalid version format: {version_str}")
```

---

## 4. Performance Optimizations

### 4.1 Lazy Loading Strategies

```python
from functools import cached_property, lru_cache
from typing import Optional, Dict, List
import weakref

class LazyResource:
    """Resource with lazy-loaded attributes"""

    def __init__(self, resource_id: str, catalog_path: Path):
        self.id = resource_id
        self._catalog_path = catalog_path
        self._metadata: Optional[Dict] = None
        self._full_content: Optional[str] = None

    @cached_property
    def metadata(self) -> Dict:
        """Load metadata only when accessed"""
        if self._metadata is None:
            path = self._catalog_path / f"{self.id}.yaml"
            with open(path) as f:
                data = yaml.safe_load(f)
                self._metadata = data.get('metadata', {})
        return self._metadata

    @cached_property
    def dependencies(self) -> List[str]:
        """Parse dependencies lazily"""
        deps = self.metadata.get('dependencies', {})
        return deps.get('required', [])

    async def get_full_content(self) -> str:
        """Async load full content"""
        if self._full_content is None:
            url = self.metadata['source']['url']
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    self._full_content = await response.text()
        return self._full_content

class LazyLoadRegistry:
    """Registry with progressive loading"""

    def __init__(self):
        self._index_loaded = False
        self._categories_loaded = False
        self._resources: Dict[str, weakref.ref] = {}
        self._lock = threading.Lock()

    @lru_cache(maxsize=1)
    def get_index(self) -> Dict:
        """Load index once and cache"""
        with self._lock:
            if not self._index_loaded:
                self._load_index()
                self._index_loaded = True
            return self._index

    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get resource with weak reference caching"""
        # Check weak reference cache
        ref = self._resources.get(resource_id)
        if ref:
            resource = ref()
            if resource:
                return resource

        # Load resource
        resource = self._load_resource(resource_id)
        if resource:
            # Store weak reference
            self._resources[resource_id] = weakref.ref(resource)

        return resource

    async def preload_batch(self, resource_ids: List[str]) -> None:
        """Preload multiple resources concurrently"""
        tasks = []
        for rid in resource_ids:
            if rid not in self._resources:
                tasks.append(self._async_load_resource(rid))

        if tasks:
            resources = await asyncio.gather(*tasks)
            for resource in resources:
                if resource:
                    self._resources[resource.id] = weakref.ref(resource)
```

### 4.2 Caching Approach

```python
from cachetools import TTLCache, LRUCache, cached
import pickle
import hashlib
from pathlib import Path

class MultiLevelCache:
    """Multi-level caching system"""

    def __init__(self, cache_dir: Path = Path.home() / '.claude' / 'cache'):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Level 1: In-memory caches
        self.index_cache = TTLCache(maxsize=1, ttl=300)  # 5 min TTL
        self.resource_cache = LRUCache(maxsize=50)  # 50 resources
        self.search_cache = TTLCache(maxsize=100, ttl=60)  # 1 min TTL

        # Level 2: Disk cache for expensive operations
        self.disk_cache_dir = cache_dir / 'disk'
        self.disk_cache_dir.mkdir(exist_ok=True)

    @cached(cache=lambda self: self.index_cache)
    def get_catalog_index(self) -> Dict:
        """Cached catalog index"""
        return self._load_catalog_index()

    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get resource with multi-level cache"""
        # L1: Memory cache
        if resource_id in self.resource_cache:
            return self.resource_cache[resource_id]

        # L2: Disk cache
        disk_path = self.disk_cache_dir / f"{resource_id}.pkl"
        if disk_path.exists():
            with open(disk_path, 'rb') as f:
                resource = pickle.load(f)
                self.resource_cache[resource_id] = resource
                return resource

        # L3: Load from source
        resource = self._load_resource_from_catalog(resource_id)
        if resource:
            # Update caches
            self.resource_cache[resource_id] = resource
            with open(disk_path, 'wb') as f:
                pickle.dump(resource, f)

        return resource

    def cache_search_results(self, query: str, results: List[Resource]) -> None:
        """Cache search results"""
        cache_key = hashlib.md5(query.encode()).hexdigest()
        self.search_cache[cache_key] = results

    def get_cached_search(self, query: str) -> Optional[List[Resource]]:
        """Get cached search results"""
        cache_key = hashlib.md5(query.encode()).hexdigest()
        return self.search_cache.get(cache_key)

    def invalidate_all(self) -> None:
        """Clear all caches"""
        self.index_cache.clear()
        self.resource_cache.clear()
        self.search_cache.clear()

        # Clear disk cache
        for file in self.disk_cache_dir.glob('*.pkl'):
            file.unlink()

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'index_cache': {
                'size': len(self.index_cache),
                'maxsize': self.index_cache.maxsize
            },
            'resource_cache': {
                'size': len(self.resource_cache),
                'maxsize': self.resource_cache.maxsize,
                'hit_rate': self.resource_cache.hit_rate if hasattr(self.resource_cache, 'hit_rate') else None
            },
            'search_cache': {
                'size': len(self.search_cache),
                'maxsize': self.search_cache.maxsize
            },
            'disk_cache': {
                'files': len(list(self.disk_cache_dir.glob('*.pkl'))),
                'size_mb': sum(f.stat().st_size for f in self.disk_cache_dir.glob('*.pkl')) / 1024 / 1024
            }
        }
```

### 4.3 Threading vs Async

```python
import asyncio
import concurrent.futures
from typing import List, Callable, Any

class HybridExecutor:
    """Hybrid async/threading for optimal performance"""

    def __init__(self):
        # Thread pool for CPU-bound tasks
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=4,
            thread_name_prefix='cpu_worker'
        )

        # Process pool for heavy CPU tasks
        self.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=2
        )

    async def run_io_bound(self, coros: List) -> List[Any]:
        """Run I/O bound tasks concurrently (async)"""
        return await asyncio.gather(*coros)

    async def run_cpu_bound(self, func: Callable, *args) -> Any:
        """Run CPU-bound task in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_pool, func, *args)

    async def run_heavy_cpu(self, func: Callable, *args) -> Any:
        """Run heavy CPU task in process pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.process_pool, func, *args)

    async def hybrid_search(self, query: str) -> List[Resource]:
        """Example: Hybrid search using both async and threads"""

        # I/O bound: Load resources (async)
        resources = await self.load_resources_async()

        # CPU bound: Build index (thread pool)
        index = await self.run_cpu_bound(build_search_index, resources)

        # CPU bound: Fuzzy matching (thread pool)
        matches = await self.run_cpu_bound(fuzzy_match, query, index)

        return matches

    def cleanup(self):
        """Cleanup pools"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)

# Decision matrix for async vs threading
"""
Use AsyncIO for:
- Network requests (HTTP downloads)
- File I/O (especially multiple files)
- Coordinating concurrent operations
- Waiting on external resources

Use Threading for:
- CPU-bound operations that release GIL
- Libraries that aren't async-aware
- Quick CPU tasks (<100ms)

Use Multiprocessing for:
- Heavy CPU-bound operations
- Parallel data processing
- Tasks that benefit from multiple cores

Avoid:
- Mixing async and blocking I/O
- CPU-heavy work in async functions
- Too many threads (>2x CPU cores)
"""
```

### 4.4 Memory Optimization

```python
import sys
from memory_profiler import profile
import gc
from typing import Iterator
import itertools

class MemoryOptimizedCatalog:
    """Memory-efficient catalog handling"""

    __slots__ = ['_path', '_index', '_resource_count']  # Reduce memory overhead

    def __init__(self, path: Path):
        self._path = path
        self._index = None
        self._resource_count = 0

    def iter_resources(self) -> Iterator[Resource]:
        """Iterate resources without loading all into memory"""
        for type_dir in self._path.iterdir():
            if type_dir.is_dir():
                for yaml_file in type_dir.glob('*.yaml'):
                    # Load one at a time
                    with open(yaml_file) as f:
                        data = yaml.safe_load(f)
                        yield Resource(**data)
                    # Explicitly free memory
                    del data

    def batch_process(self, batch_size: int = 100) -> Iterator[List[Resource]]:
        """Process resources in batches"""
        iterator = self.iter_resources()
        while True:
            batch = list(itertools.islice(iterator, batch_size))
            if not batch:
                break
            yield batch
            # Force garbage collection after each batch
            gc.collect()

    @profile  # Memory profiling decorator
    def build_index_memory_efficient(self) -> Dict:
        """Build index with minimal memory usage"""
        index = {
            'total': 0,
            'types': defaultdict(int)
        }

        # Process in batches to avoid loading all resources
        for batch in self.batch_process(batch_size=50):
            for resource in batch:
                index['total'] += 1
                index['types'][resource.type] += 1

            # Clear batch from memory
            del batch

        return index

    def get_memory_usage(self) -> Dict:
        """Get current memory usage stats"""
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024
        }

# String interning for repeated strings
class InternedResource:
    """Resource with string interning to save memory"""

    _interned_strings = {}

    def __init__(self, data: Dict):
        # Intern commonly repeated strings
        self.id = self._intern(data['id'])
        self.type = self._intern(data['type'])
        self.author = self._intern(data.get('author', ''))
        self.version = self._intern(data.get('version', 'v1.0.0'))

        # Don't intern unique strings
        self.description = data.get('description', '')
        self.content = data.get('content', '')

    @classmethod
    def _intern(cls, s: str) -> str:
        """Intern string to save memory"""
        if s not in cls._interned_strings:
            cls._interned_strings[s] = sys.intern(s)
        return cls._interned_strings[s]

# Memory-efficient data structures
from array import array
from collections import deque

class CompactSearchIndex:
    """Memory-efficient search index using compact data structures"""

    def __init__(self):
        # Use array for numeric data (more compact than list)
        self.resource_ids = []  # Still need list for strings
        self.scores = array('f')  # Float array for scores

        # Use deque for FIFO operations (more efficient than list)
        self.recent_searches = deque(maxlen=10)

        # Use bytes for fixed-size data
        self.hashes = {}  # resource_id -> hash bytes

    def add_resource(self, resource_id: str, score: float):
        """Add resource with compact storage"""
        self.resource_ids.append(sys.intern(resource_id))  # Intern string
        self.scores.append(score)

        # Store hash as bytes (more compact)
        hash_bytes = hashlib.md5(resource_id.encode()).digest()
        self.hashes[resource_id] = hash_bytes
```

---

## 5. Component Architecture

### 5.1 TUI Layer (Textual Framework)

```python
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, ListView, Input, Button
from textual.reactive import reactive
from textual.message import Message
from rich.syntax import Syntax
from rich.table import Table

class ResourceBrowserApp(App):
    """Main TUI application using Textual"""

    CSS = """
    ResourceBrowserApp {
        layout: grid;
        grid-size: 3 2;
        grid-columns: 1fr 2fr 2fr;
        grid-rows: 1fr auto;
    }

    #category-tree {
        border: solid $primary;
        overflow-y: scroll;
    }

    #resource-list {
        border: solid $secondary;
        overflow-y: scroll;
    }

    #preview-pane {
        border: solid $accent;
        overflow-y: scroll;
        padding: 1;
    }

    #search-bar {
        dock: top;
        height: 3;
    }

    .selected {
        background: $boost;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("/", "search", "Search"),
        Binding("i", "install", "Install"),
        Binding("d", "dependencies", "Show Dependencies"),
        Binding("?", "help", "Help"),
        Binding("ctrl+r", "refresh", "Refresh"),
    ]

    def __init__(self):
        super().__init__()
        self.catalog = LazyLoadCatalog()
        self.search_index = SearchIndex()
        self.selected_resources: Set[str] = set()
        self.current_filter = ""

    def compose(self) -> ComposeResult:
        """Create TUI layout"""
        yield Header()
        yield SearchBar(id="search-bar")
        yield CategoryTree(id="category-tree")
        yield ResourceList(id="resource-list")
        yield PreviewPane(id="preview-pane")
        yield Footer()

    async def on_mount(self):
        """Initialize on mount"""
        # Load catalog in background
        asyncio.create_task(self.load_catalog())

        # Set initial focus
        self.query_one("#resource-list").focus()

    async def load_catalog(self):
        """Load catalog progressively"""
        # Load index first
        index = await self.catalog.get_index()
        self.update_status(f"Loaded {index['total']} resources")

        # Build categories
        categories = await self.build_categories()
        self.query_one("#category-tree").update_categories(categories)

        # Load visible resources
        visible = self.query_one("#resource-list").get_visible_items()
        await self.catalog.preload_visible(visible)

    async def action_search(self):
        """Handle search action"""
        search_bar = self.query_one("#search-bar")
        search_bar.visible = True
        search_bar.focus()

    async def on_search_submitted(self, query: str):
        """Handle search query"""
        results = await self.search_index.search(query)
        self.query_one("#resource-list").update_resources(results)

        # Hide search bar
        self.query_one("#search-bar").visible = False

    async def action_install(self):
        """Handle install action"""
        selected = self.query_one("#resource-list").get_selected()
        if selected:
            # Show installation dialog
            await self.push_screen(InstallDialog(selected))

class CategoryTree(Widget):
    """Category tree widget"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.categories = {}
        self.expanded = set()

    def render(self) -> str:
        """Render category tree"""
        tree = Tree("Resources")

        for category, resources in self.categories.items():
            is_expanded = category in self.expanded
            icon = "▼" if is_expanded else "▶"

            branch = tree.add(f"{icon} {category} ({len(resources)})")

            if is_expanded:
                for resource in resources[:10]:  # Show first 10
                    branch.add(f"• {resource.name}")

        return tree

class ResourceList(ListView):
    """Resource list with virtual scrolling"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resources = []
        self.selected_index = 0

    def update_resources(self, resources: List[Resource]):
        """Update resource list"""
        self.resources = resources
        self.clear()

        # Add visible items only (virtual scrolling)
        visible_range = self.get_visible_range()
        for i in range(visible_range.start, visible_range.stop):
            if i < len(resources):
                self.append(ResourceItem(resources[i]))

    def get_visible_items(self) -> List[str]:
        """Get IDs of visible items"""
        visible_range = self.get_visible_range()
        return [
            self.resources[i].id
            for i in range(visible_range.start, visible_range.stop)
            if i < len(self.resources)
        ]

class PreviewPane(Static):
    """Resource preview pane with syntax highlighting"""

    current_resource = reactive(None)

    def watch_current_resource(self, resource: Optional[Resource]):
        """Update preview when resource changes"""
        if resource:
            self.update(self.format_resource(resource))
        else:
            self.update("Select a resource to preview")

    def format_resource(self, resource: Resource) -> str:
        """Format resource for display"""
        # Create rich table for metadata
        table = Table(title=resource.name, show_header=False)
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        table.add_row("ID", resource.id)
        table.add_row("Type", resource.type)
        table.add_row("Version", resource.version)
        table.add_row("Author", resource.author)

        # Add description
        desc = Text(resource.description, style="italic")

        # Add source info if available
        if hasattr(resource, 'source'):
            table.add_row("Source", resource.source.repo)
            table.add_row("Path", resource.source.path)

        return table
```

### 5.2 Business Logic Layer

```python
# core/models.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum

class ResourceType(str, Enum):
    AGENT = "agent"
    COMMAND = "command"
    HOOK = "hook"
    TEMPLATE = "template"
    MCP = "mcp"

class Dependencies(BaseModel):
    required: List[str] = Field(default_factory=list)
    recommended: List[str] = Field(default_factory=list)

    @validator('required', 'recommended', each_item=True)
    def validate_dependency_id(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError(f"Invalid dependency ID: {v}")
        return v

class Resource(BaseModel):
    id: str
    type: ResourceType
    name: str
    description: str
    summary: Optional[str] = None
    version: str = "v1.0.0"
    author: Optional[str] = None
    file_type: str = ".md"
    source: Optional[Dict[str, str]] = None
    install_path: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    dependencies: Optional[Dependencies] = None

    class Config:
        use_enum_values = True
```

### 5.3 Data Layer

```python
# data/downloader.py
import aiohttp
import asyncio
from typing import Optional, List
from pathlib import Path
import hashlib

class GitHubDownloader:
    """Async GitHub content downloader"""

    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def download(self, url: str) -> bytes:
        """Download content from URL"""
        async with self.semaphore:
            for attempt in range(3):
                try:
                    async with self.session.get(url) as response:
                        response.raise_for_status()
                        return await response.read()
                except aiohttp.ClientError as e:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(2 ** attempt)

    async def download_many(self, urls: List[str]) -> List[bytes]:
        """Download multiple URLs concurrently"""
        tasks = [self.download(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

    def verify_content(self, content: bytes, expected_hash: Optional[str]) -> bool:
        """Verify content hash if provided"""
        if not expected_hash:
            return True

        actual_hash = hashlib.sha256(content).hexdigest()
        return actual_hash == expected_hash
```

### 5.4 Integration Layer

```python
# Integration with GitHub API
class GitHubIntegration:
    """GitHub API integration for catalog updates"""

    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = "https://api.github.com"

    async def fetch_catalog_updates(self, repos: List[str]) -> Dict:
        """Check for catalog updates"""
        updates = {}

        async with aiohttp.ClientSession() as session:
            for repo in repos:
                # Get latest commit
                url = f"{self.base_url}/repos/{repo}/commits/main"
                headers = {"Authorization": f"token {self.token}"} if self.token else {}

                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        updates[repo] = {
                            'sha': data['sha'],
                            'date': data['commit']['committer']['date'],
                            'message': data['commit']['message']
                        }

        return updates
```

---

## 6. API Design

### 6.1 catalog_loader.py API

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, AsyncIterator
from pathlib import Path

class CatalogLoaderInterface(ABC):
    """Abstract interface for catalog loading"""

    @abstractmethod
    async def load_index(self) -> Dict:
        """Load catalog index"""
        pass

    @abstractmethod
    async def load_resource(self, resource_id: str, resource_type: str) -> Resource:
        """Load single resource"""
        pass

    @abstractmethod
    async def load_all_of_type(self, resource_type: str) -> List[Resource]:
        """Load all resources of given type"""
        pass

    @abstractmethod
    async def iter_resources(self) -> AsyncIterator[Resource]:
        """Iterate over all resources"""
        pass

class YamlCatalogLoader(CatalogLoaderInterface):
    """YAML-based catalog loader implementation"""

    def __init__(self, catalog_path: Path, cache: Optional[Cache] = None):
        self.catalog_path = catalog_path
        self.cache = cache or Cache()

    async def load_index(self) -> Dict:
        """Load and cache catalog index"""
        cache_key = "catalog:index"

        # Check cache
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Load from disk
        index_path = self.catalog_path / "index.yaml"
        async with aiofiles.open(index_path) as f:
            content = await f.read()
            index = yaml.safe_load(content)

        # Cache result
        self.cache.set(cache_key, index)
        return index

    # ... implementation of other methods
```

### 6.2 search_index.py API

```python
from typing import List, Optional, Protocol
from dataclasses import dataclass

class SearchStrategy(Protocol):
    """Protocol for search strategies"""

    def search(self, query: str, resources: List[Resource]) -> List[SearchResult]:
        ...

@dataclass
class SearchOptions:
    """Search configuration options"""
    limit: int = 20
    threshold: float = 0.6
    boost_exact: float = 2.0
    boost_prefix: float = 1.5
    fuzzy_enabled: bool = True

class SearchIndexInterface(ABC):
    """Abstract search index interface"""

    @abstractmethod
    def add(self, resource: Resource) -> None:
        """Add resource to index"""
        pass

    @abstractmethod
    def remove(self, resource_id: str) -> None:
        """Remove resource from index"""
        pass

    @abstractmethod
    def search(self, query: str, options: Optional[SearchOptions] = None) -> List[SearchResult]:
        """Search resources"""
        pass

    @abstractmethod
    def rebuild(self, resources: List[Resource]) -> None:
        """Rebuild entire index"""
        pass
```

### 6.3 dependency_resolver.py API

```python
from typing import List, Set, Dict, Optional, Tuple
from dataclasses import dataclass
import networkx as nx

@dataclass
class DependencyPlan:
    """Installation plan with dependencies"""
    to_install: List[List[Resource]]  # Levels for parallel install
    already_installed: Set[str]
    missing: Set[str]
    recommended: Set[str]
    install_order: List[str]

class DependencyResolverInterface(ABC):
    """Abstract dependency resolver interface"""

    @abstractmethod
    def resolve(self, resource: Resource) -> DependencyPlan:
        """Resolve dependencies for resource"""
        pass

    @abstractmethod
    def check_cycles(self, resource: Resource) -> Optional[List[str]]:
        """Check for circular dependencies"""
        pass

    @abstractmethod
    def get_dependents(self, resource_id: str) -> List[str]:
        """Get resources that depend on given resource"""
        pass

class NetworkXDependencyResolver(DependencyResolverInterface):
    """Dependency resolver using NetworkX"""

    def __init__(self, catalog: CatalogLoaderInterface):
        self.catalog = catalog
        self.graph = nx.DiGraph()
        self._build_graph()

    def resolve(self, resource: Resource) -> DependencyPlan:
        """Resolve dependencies using topological sort"""
        # Build subgraph of dependencies
        subgraph = self._get_dependency_subgraph(resource)

        # Check for cycles
        if not nx.is_directed_acyclic_graph(subgraph):
            cycles = list(nx.simple_cycles(subgraph))
            raise DependencyError(f"Circular dependency detected: {cycles[0]}")

        # Topological sort for installation order
        install_order = list(nx.topological_sort(subgraph))

        # Group by levels for parallel installation
        levels = self._group_by_levels(subgraph, install_order)

        return DependencyPlan(
            to_install=levels,
            already_installed=self._get_installed(),
            missing=self._find_missing(subgraph),
            recommended=self._get_recommended(resource),
            install_order=install_order
        )
```

### 6.4 installer.py API

```python
from typing import List, Optional, Callable, Awaitable
from dataclasses import dataclass
from pathlib import Path

@dataclass
class InstallOptions:
    """Installation options"""
    force: bool = False
    skip_dependencies: bool = False
    dry_run: bool = False
    parallel: bool = True
    verify_checksums: bool = True

@dataclass
class InstallResult:
    """Installation result"""
    resource_id: str
    success: bool
    path: Optional[Path] = None
    error: Optional[str] = None

class InstallerInterface(ABC):
    """Abstract installer interface"""

    @abstractmethod
    async def install(
        self,
        resource: Resource,
        options: Optional[InstallOptions] = None,
        progress_callback: Optional[Callable[[str, float], Awaitable[None]]] = None
    ) -> InstallResult:
        """Install single resource"""
        pass

    @abstractmethod
    async def install_many(
        self,
        resources: List[Resource],
        options: Optional[InstallOptions] = None
    ) -> List[InstallResult]:
        """Install multiple resources"""
        pass

    @abstractmethod
    async def uninstall(self, resource_id: str) -> bool:
        """Uninstall resource"""
        pass

    @abstractmethod
    def is_installed(self, resource_id: str) -> bool:
        """Check if resource is installed"""
        pass

class AsyncInstaller(InstallerInterface):
    """Asynchronous installer implementation"""

    def __init__(
        self,
        base_path: Path = Path.home() / '.claude',
        downloader: Optional[GitHubDownloader] = None
    ):
        self.base_path = base_path
        self.downloader = downloader or GitHubDownloader()
        self.state = InstallState()

    async def install(
        self,
        resource: Resource,
        options: Optional[InstallOptions] = None,
        progress_callback: Optional[Callable] = None
    ) -> InstallResult:
        """Install with progress tracking"""
        options = options or InstallOptions()

        try:
            # Check if already installed
            if not options.force and self.is_installed(resource.id):
                return InstallResult(
                    resource_id=resource.id,
                    success=True,
                    path=self._get_install_path(resource),
                    error="Already installed"
                )

            # Download content
            if progress_callback:
                await progress_callback(f"Downloading {resource.id}", 0.3)

            content = await self.downloader.download(resource.source['url'])

            # Verify if requested
            if options.verify_checksums:
                if progress_callback:
                    await progress_callback(f"Verifying {resource.id}", 0.6)
                # Verify logic here

            # Write to disk
            if progress_callback:
                await progress_callback(f"Installing {resource.id}", 0.9)

            if not options.dry_run:
                path = await self._write_resource(resource, content)
                self.state.mark_installed(resource.id)
            else:
                path = self._get_install_path(resource)

            if progress_callback:
                await progress_callback(f"Completed {resource.id}", 1.0)

            return InstallResult(
                resource_id=resource.id,
                success=True,
                path=path
            )

        except Exception as e:
            return InstallResult(
                resource_id=resource.id,
                success=False,
                error=str(e)
            )
```

---

## 7. Design Decisions & Rationale

### 7.1 Why Python Over Go

| Aspect | Python | Go | Decision |
|--------|--------|-----|----------|
| **Startup Time** | 100-200ms | 5-10ms | Python slower but acceptable with optimization |
| **Development Speed** | Fast | Medium | Python wins for rapid iteration |
| **TUI Framework** | Textual (excellent) | Bubble Tea (excellent) | Both strong, Textual more Pythonic |
| **Ecosystem** | Rich (ML, data) | Growing | Python has more libraries |
| **Type Safety** | Optional (type hints) | Built-in | Python sufficient with mypy |
| **Distribution** | Requires Python | Single binary | Go wins but Python acceptable |

**Decision: Python** - Development velocity and ecosystem outweigh startup time penalty.

### 7.2 Textual vs Other TUI Frameworks

| Framework | Pros | Cons | Decision |
|-----------|------|------|----------|
| **Textual** | Modern, CSS styling, async, reactive | Newer, smaller community | ✅ Selected |
| **Urwid** | Mature, stable | Older API, less modern | ❌ |
| **Rich** | Beautiful output | Not full TUI framework | ❌ |
| **Blessed** | Simple | Limited features | ❌ |

**Decision: Textual** - Modern architecture, CSS-like styling, excellent async support.

### 7.3 Pydantic vs Dataclasses vs Attrs

| Feature | Pydantic | Dataclasses | Attrs | Decision |
|---------|----------|-------------|-------|----------|
| **Validation** | Excellent | None | Good | Pydantic for external data |
| **Performance** | Good | Excellent | Good | Dataclasses for internal |
| **Serialization** | Built-in | Manual | Manual | Pydantic for YAML/JSON |
| **Type hints** | Full | Full | Full | All good |

**Decision: Hybrid** - Pydantic for external data, dataclasses for internal state.

### 7.4 Async Strategy

```python
# Decision tree for async usage

def should_use_async(operation):
    if operation.is_io_bound:
        if operation.involves_network:
            return True  # Always async for network
        if operation.involves_multiple_files:
            return True  # Async for concurrent file ops
        if operation.is_single_file and file.size < 1_mb:
            return False  # Sync is simpler for small files

    if operation.is_cpu_bound:
        if operation.can_release_gil:
            return "thread_pool"  # Use executor
        else:
            return False  # Sync or multiprocessing

    if operation.is_coordination:
        return True  # Async for orchestration

    return False  # Default to sync for simplicity
```

### 7.5 Performance Target Achievement Strategy

| Target | Challenge | Solution |
|--------|-----------|----------|
| **<100ms startup** | Python interpreter overhead | Lazy imports, minimal startup code, pre-compiled .pyc |
| **<1ms search** | Large dataset | In-memory index, trie for prefix, caching |
| **<50MB memory** | 331 resources | Lazy loading, weak references, string interning |
| **Cross-platform** | Path differences | pathlib, platform detection, CI testing |

---

## 8. Data Flow Diagrams

### 8.1 Search Flow

```
User Input → Search Query
    ↓
[Search Manager]
    ├→ Check Cache
    │   ├→ Hit: Return cached results
    │   └→ Miss: Continue
    ↓
[Strategy Selection]
    ├→ Length < 3: Prefix search
    ├→ Alphanumeric: Exact + Fuzzy
    └→ Special chars: Regex
    ↓
[Parallel Search]
    ├→ Exact Match (HashMap)
    ├→ Prefix Match (Trie)
    └→ Fuzzy Match (RapidFuzz)
    ↓
[Result Aggregation]
    ├→ Deduplication
    ├→ Scoring
    └→ Ranking
    ↓
[Cache Results]
    ↓
[Return to UI]
```

### 8.2 Installation Flow

```
User Selection → Resource(s)
    ↓
[Dependency Resolution]
    ├→ Build dependency graph
    ├→ Check for cycles
    └→ Topological sort
    ↓
[Installation Plan]
    ├→ Show plan to user
    └→ Get confirmation
    ↓
[Parallel Download]
    ├→ Level 1 deps (parallel)
    ├→ Level 2 deps (parallel)
    └→ Target resource
    ↓
[Verification]
    ├→ Checksum validation
    └→ Content validation
    ↓
[Atomic Write]
    ├→ Write to temp file
    └→ Atomic rename
    ↓
[State Update]
    ├→ Mark installed
    ├→ Update history
    └→ Clear cache
    ↓
[Report Success]
```

---

## 9. Component Interaction Diagrams

```
┌─────────────────────────────────────────────────────┐
│                    CLI Layer                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │ Browse  │  │ Install │  │ Search  │            │
│  └────┬────┘  └────┬────┘  └────┬────┘            │
│       └────────────┼────────────┘                  │
└───────────────────┼─────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────────┐
│                    TUI Layer (Textual)                │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Browser App  │  │ Search Screen│  │ Install UI │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘ │
│         └─────────────────┼─────────────────┘        │
└────────────────────────────┼──────────────────────────┘
                             ↓
┌────────────────────────────────────────────────────────┐
│                    Business Logic Layer                │
│  ┌────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │  Catalog   │  │ Search Index │  │  Dependency   │ │
│  │  Loader    │  │   Manager    │  │   Resolver    │ │
│  └─────┬──────┘  └──────┬───────┘  └───────┬───────┘ │
│        └────────────────┼───────────────────┘         │
└─────────────────────────┼──────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│                      Data Layer                          │
│  ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌────────┐│
│  │   Cache  │  │ YAML Parser│  │Downloader│  │ State  ││
│  └──────────┘  └────────────┘  └──────────┘  └────────┘│
└──────────────────────────────────────────────────────────┘
```

---

## 10. Key Design Patterns Summary

1. **Lazy Loading Pattern** - Load resources on-demand to minimize startup time
2. **Multi-level Caching** - Memory → Disk → Network hierarchy
3. **Strategy Pattern** - Multiple search strategies based on query type
4. **Repository Pattern** - Abstract data access behind interfaces
5. **Dependency Injection** - Testable components with clear boundaries
6. **Async/Await Pattern** - Concurrent I/O operations
7. **Observer Pattern** - Reactive UI updates with Textual
8. **Factory Pattern** - Resource creation from YAML data
9. **Command Pattern** - CLI commands as discrete operations
10. **Builder Pattern** - Complex object construction (InstallPlan)

---

## 11. Performance Benchmarks & Targets

| Operation | Target | Strategy | Validation |
|-----------|--------|----------|------------|
| **Cold start** | <100ms | Lazy imports, minimal init | `time python -m claude_resource_manager --version` |
| **Catalog load** | <50ms | Async parallel loading | Benchmark with 331 resources |
| **Search (exact)** | <1ms | HashMap O(1) lookup | Unit test with timing |
| **Search (fuzzy)** | <5ms | RapidFuzz with caching | Benchmark with complex queries |
| **Install (single)** | <500ms | Async download | Mock network, measure |
| **Memory usage** | <50MB | Lazy load, weak refs | Memory profiler |
| **TUI render** | 60 FPS | Virtual scrolling | Textual performance metrics |

---

## 12. Testing Strategy Summary

```python
# Test distribution following pyramid
UNIT_TESTS = 70  # Fast, isolated
INTEGRATION_TESTS = 25  # Component interaction
E2E_TESTS = 5  # Full workflows

# Test coverage targets
COVERAGE_TARGETS = {
    'core/': 95,  # Critical business logic
    'data/': 90,  # Data integrity critical
    'tui/': 75,   # UI harder to test
    'cli/': 85,   # User-facing must work
    'utils/': 80,  # Support code
    'overall': 85  # Project target
}
```

---

## Document Status

**Status:** ✅ Complete System Architecture
**Version:** 1.0.0
**Date:** October 4, 2025
**Next Steps:** Begin implementation following this design

This architecture provides:
- Clear module boundaries and responsibilities
- Performance optimization strategies
- Comprehensive API design
- Python-specific best practices
- Testing and validation approach

The design balances Python's development velocity with performance requirements through careful use of async patterns, caching, and lazy loading strategies.