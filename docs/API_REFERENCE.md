# API Reference - Phase 2

**Developer-Facing API Documentation**

This reference documents all public APIs introduced or enhanced in Phase 2 of the Claude Resource Manager.

---

## Table of Contents

1. [Category Engine](#category-engine)
2. [Search Engine](#search-engine)
3. [Async Installer](#async-installer)
4. [Cache Utilities](#cache-utilities)
5. [TUI Components](#tui-components)

---

## Category Engine

**Module**: `claude_resource_manager.core.category_engine`

The CategoryEngine provides automatic resource categorization based on ID prefixes, with hierarchical tree building and efficient filtering.

### Classes

#### Category

Extracted category information from a resource ID.

```python
from claude_resource_manager.core.category_engine import Category

class Category(BaseModel):
    """Category extracted from resource ID prefix."""
    primary: str              # Primary category (e.g., "mcp")
    secondary: Optional[str]  # Subcategory (e.g., "dev-team")
    resource_name: str        # Final resource name
    full_path: list[str]      # Complete hierarchy path
```

**Example**:

```python
Category(
    primary="mcp",
    secondary="dev-team",
    resource_name="architect",
    full_path=["mcp", "dev-team", "architect"]
)
```

#### CategoryNode

Node in the category tree hierarchy.

```python
class CategoryNode:
    """Represents a category in the tree."""

    def __init__(self, name: str, parent: Optional[CategoryNode] = None):
        """Initialize category node.

        Args:
            name: Category name
            parent: Parent node (None for root)
        """
        self.name = name
        self.parent = parent
        self.children: dict[str, CategoryNode] = {}
        self.resources: list[dict[str, Any]] = []
```

**Methods**:

##### `add_child(name: str) -> CategoryNode`

Add or get child category node.

```python
node = CategoryNode("mcp")
dev_team = node.add_child("dev-team")
# Returns existing child if already present
```

**Parameters**:
- `name`: Child category name

**Returns**: Child CategoryNode instance

**Complexity**: O(1)

##### `add_resource(resource: dict[str, Any]) -> None`

Add resource to this category node.

```python
node.add_resource({
    "id": "mcp-dev-team-architect",
    "type": "agent",
    "name": "Architect"
})
```

**Parameters**:
- `resource`: Resource dictionary

**Complexity**: O(1)

##### `get_all_resources() -> list[dict[str, Any]]`

Get all resources in this category and subcategories recursively.

```python
resources = node.get_all_resources()
# Returns resources from this node and all descendants
```

**Returns**: List of all resources recursively

**Complexity**: O(n) where n = total resources in subtree

##### `count_resources() -> int`

Count total resources in this category and subcategories.

```python
count = node.count_resources()
# Returns total count including descendants
```

**Returns**: Total resource count

**Complexity**: O(k) where k = number of nodes in subtree

---

#### CategoryTree

Hierarchical category tree with filtering and statistics.

```python
class CategoryTree:
    """Hierarchical category tree."""

    def __init__(self) -> None:
        """Initialize empty category tree."""
        self.root = CategoryNode("root")
        self.categories: list[CategoryNode] = []
        self.max_depth: int = 1
        self._category_map: dict[str, CategoryNode] = {}
```

**Methods**:

##### `add_resource(category: Category, resource: dict[str, Any]) -> None`

Add resource to tree based on its category.

```python
tree = CategoryTree()
category = Category(
    primary="mcp",
    secondary="dev-team",
    resource_name="architect",
    full_path=["mcp", "dev-team", "architect"]
)
tree.add_resource(category, resource)
```

**Parameters**:
- `category`: Extracted category information
- `resource`: Resource dictionary to add

**Complexity**: O(d) where d = category depth (typically 1-3)

##### `filter_by_category(name: str) -> list[dict[str, Any]]`

Filter resources by primary category.

```python
mcp_resources = tree.filter_by_category("mcp")
# Returns all resources in "mcp" category and subcategories
```

**Parameters**:
- `name`: Category name

**Returns**: List of resources in that category

**Complexity**: O(n) where n = resources in category

**Example**:

```python
# Get all MCP servers
mcp_servers = tree.filter_by_category("mcp")
print(f"Found {len(mcp_servers)} MCP servers")

# Get all agents
agents = tree.filter_by_category("agent")
```

##### `filter_by_path(path: list[str]) -> list[dict[str, Any]]`

Filter resources by category path.

```python
# Get resources in mcp/dev-team subcategory
dev_team_resources = tree.filter_by_path(["mcp", "dev-team"])
```

**Parameters**:
- `path`: Category path (e.g., `["mcp", "dev-team"]`)

**Returns**: List of resources matching path

**Complexity**: O(n) where n = resources in path

##### `filter_by_category_and_type(category: str, resource_type: str) -> list[dict[str, Any]]`

Filter resources by category and type.

```python
# Get all agents in MCP category
mcp_agents = tree.filter_by_category_and_type("mcp", "agent")
```

**Parameters**:
- `category`: Category name
- `resource_type`: Resource type (agent, mcp, hook, etc.)

**Returns**: List of resources matching both criteria

**Complexity**: O(n) where n = resources in category

##### `get_statistics() -> CategoryStatistics`

Get category statistics.

```python
stats = tree.get_statistics()
print(f"Total resources: {stats.total_resources}")
print(f"Total categories: {stats.total_categories}")
print(f"MCP servers: {stats.category_counts['mcp']} ({stats.category_percentages['mcp']:.1f}%)")
```

**Returns**: CategoryStatistics with counts and percentages

**Example Output**:

```python
CategoryStatistics(
    total_resources=331,
    total_categories=5,
    category_counts={
        "mcp": 52,
        "agent": 181,
        "hook": 64,
        "command": 18,
        "template": 16
    },
    category_percentages={
        "mcp": 15.7,
        "agent": 54.7,
        "hook": 19.3,
        "command": 5.4,
        "template": 4.8
    }
)
```

##### `get_sorted_categories() -> list[CategoryNode]`

Get categories sorted alphabetically.

```python
sorted_cats = tree.get_sorted_categories()
for cat in sorted_cats:
    print(f"{cat.name}: {cat.count_resources()} resources")
```

**Returns**: Alphabetically sorted list of category nodes

**Complexity**: O(k log k) where k = number of categories

---

#### CategoryEngine

Engine for extracting categories and building hierarchical trees.

```python
class CategoryEngine:
    """Engine for category extraction and tree building."""

    def __init__(self, lazy_load: bool = False):
        """Initialize category engine.

        Args:
            lazy_load: Enable lazy loading of categories (default: False)
        """
        self.lazy_load = lazy_load
        self._cached_tree: Optional[CategoryTree] = None
        self._cache_key: Optional[int] = None
```

**Methods**:

##### `extract_category(resource_id: str) -> Category`

Extract category from resource ID.

Parses hyphenated resource IDs into hierarchical categories using intelligent heuristics.

```python
engine = CategoryEngine()

# Single word -> general category
cat = engine.extract_category("architect")
# Category(primary="general", resource_name="architect")

# Two parts -> simple category-name
cat = engine.extract_category("mcp-architect")
# Category(primary="mcp", resource_name="architect")

# Three+ parts -> hierarchical
cat = engine.extract_category("mcp-dev-team-architect")
# Category(primary="mcp", secondary="dev-team", resource_name="architect")
```

**Parameters**:
- `resource_id`: Resource identifier to parse

**Returns**: Category object with extracted hierarchy

**Complexity**: O(k) where k = number of hyphens in ID

**Heuristics**:

1. **Single word**: `primary="general"`, no secondary
2. **Two parts**: `primary=part1`, `resource_name=part2`
3. **Three parts**: `primary=part1`, `secondary=part2`, `resource_name=part3`
4. **Four+ parts**: Uses length heuristic:
   - If `part2` ≤ 6 chars: Group middle parts as secondary
   - If `part2` > 6 chars: Keep part2 single, combine rest as resource name

**Examples**:

```python
# Heuristic examples
extract_category("ai-specialists-prompt-engineer")
# primary="ai", secondary="specialists", resource_name="prompt-engineer"
# (part2 "specialists" > 6 chars, so keep single and combine rest)

extract_category("mcp-dev-team-architect")
# primary="mcp", secondary="dev-team", resource_name="architect"
# (part2 "dev" ≤ 6 chars, so group "dev-team" as secondary)
```

##### `build_tree(resources: list[dict[str, Any]]) -> CategoryTree`

Build category tree from resources.

Uses caching to avoid rebuilding for identical resource lists.

```python
engine = CategoryEngine()
resources = load_resources()  # 331 resources

tree = engine.build_tree(resources)
# First call: Builds tree (~0.77ms)

tree2 = engine.build_tree(resources)
# Second call: Returns cached tree (~0.01ms, 77x faster)
```

**Parameters**:
- `resources`: List of resource dictionaries

**Returns**: CategoryTree with all resources organized

**Performance**:
- First build: <1ms for 331 resources
- Cached build: <0.01ms (cache hit)

**Complexity**: O(n) where n = number of resources

**Caching**:
The engine caches the last built tree using object identity (`id(resources)`). Cache is invalidated if resource list changes.

##### `invalidate_cache() -> None`

Invalidate cached category tree.

Forces next `build_tree()` call to create a fresh tree.

```python
engine.invalidate_cache()
tree = engine.build_tree(resources)  # Rebuilds from scratch
```

---

### Performance Characteristics

| Operation | Complexity | Phase 2 Benchmark |
|-----------|------------|-------------------|
| Extract category | O(k) | <0.01ms |
| Build tree (331) | O(n) | 0.77ms |
| Build tree (cached) | O(1) | 0.01ms |
| Filter by category | O(m) | <0.5ms (m=52) |
| Get statistics | O(k) | <0.1ms (k=5) |

**Memory**: <5MB for full tree (331 resources)

---

## Search Engine

**Module**: `claude_resource_manager.core.search_engine`

The SearchEngine provides fast multi-strategy search with exact, prefix, and fuzzy matching.

### Classes

#### TrieNode

Node in prefix trie for fast prefix search.

```python
class TrieNode:
    """Node in prefix trie."""

    def __init__(self):
        """Initialize trie node."""
        self.children: dict[str, TrieNode] = {}
        self.resource_ids: list[str] = []
```

Internal class used by SearchEngine. Not typically used directly.

---

#### SearchEngine

Fast search engine with exact, prefix, and fuzzy matching.

```python
class SearchEngine:
    """Multi-strategy search engine."""

    def __init__(self, use_cache: bool = False, index_fields: Optional[list[str]] = None):
        """Initialize search engine.

        Args:
            use_cache: Enable LRU caching for search results (default: False)
            index_fields: Fields to index (default: ["id", "name", "description"])
        """
        self.resources: dict[str, dict[str, Any]] = {}
        self.trie_root = TrieNode()
        self.use_cache = use_cache
        self.index_fields = index_fields or ["id", "name", "description"]
```

**Methods**:

##### `index_resource(resource: dict[str, Any]) -> None`

Add or update a resource in the search index.

Builds trie for prefix search and creates searchable text for fuzzy matching.

```python
engine = SearchEngine()

engine.index_resource({
    "id": "architect",
    "type": "agent",
    "name": "System Architect",
    "description": "Designs system architecture and patterns"
})

# Resource is now searchable by:
# - ID: "architect"
# - Name: "system", "architect"
# - Description: "designs", "system", "architecture", etc.
```

**Parameters**:
- `resource`: Resource dictionary to index (must have "id" field)

**Complexity**: O(k) where k = total characters in indexed fields

**Indexed Fields**:
By default, indexes: `id`, `name`, `description`

Custom indexing:
```python
engine = SearchEngine(index_fields=["id", "name", "tags"])
```

##### `remove_resource(resource_id: str) -> None`

Remove a resource from the search index.

Rebuilds the entire trie for simplicity (efficient for small catalogs).

```python
engine.remove_resource("architect")
# Resource no longer searchable
```

**Parameters**:
- `resource_id`: ID of resource to remove

**Complexity**: O(n*k) where n = resources, k = avg chars per resource

**Note**: Rebuilds trie from scratch. For production with frequent deletions, a more efficient deletion algorithm should be used.

##### `search_exact(query: str) -> list[dict[str, Any]]`

Exact match search - O(1) dictionary lookup.

```python
results = engine.search_exact("architect")
# Returns [resource] if exact ID match, else []
```

**Parameters**:
- `query`: Exact ID to search for

**Returns**: List containing matching resource, or empty list

**Performance**: <1ms (O(1) hash lookup)

##### `search_prefix(prefix: str) -> list[dict[str, Any]]`

Prefix search using trie - O(k) where k is prefix length.

```python
results = engine.search_prefix("arch")
# Returns all resources with IDs or indexed fields starting with "arch"
# e.g., "architect", "architecture-expert", "archival-system"
```

**Parameters**:
- `prefix`: Prefix to search for

**Returns**: List of resources matching prefix

**Performance**: <2ms for 331 resources

**Complexity**: O(k + m) where k = prefix length, m = matching resources

##### `search_fuzzy(query: str, limit: int = 50) -> list[dict[str, Any]]`

Fuzzy search using RapidFuzz - O(n) with typo tolerance.

Uses token_set_ratio for multi-word matching and handles typos.

```python
# Typo tolerance
results = engine.search_fuzzy("architet", limit=10)
# Finds "architect" despite missing 'c'

# Multi-word
results = engine.search_fuzzy("system design", limit=10)
# Finds resources with both "system" and "design"
```

**Parameters**:
- `query`: Query string (may contain typos)
- `limit`: Maximum number of results (default: 50)

**Returns**: List of resources ranked by fuzzy match score

**Performance**: <20ms for 331 resources

**Scoring**:
- Uses RapidFuzz WRatio (Weighted Ratio) scorer
- Score range: 0-100
- Adaptive threshold based on query characteristics:
  - Normal queries: 35 (permissive)
  - Queries with numbers + letters: 60 (stricter, avoids spurious matches)

**Example**:

```python
# Adaptive threshold in action
results = engine.search_fuzzy("architect")
# Uses score_cutoff=35, finds many matches

results = engine.search_fuzzy("xyznonexistent123")
# Uses score_cutoff=60, returns [] (likely noise)
```

##### `search_smart(query: str, limit: int = 50) -> list[dict[str, Any]]`

Smart search with weighted scoring for result ranking.

**New in Phase 2**: This is the recommended search method.

Combines exact, prefix, and fuzzy matching with field-based scoring to rank results.

**Scoring Strategy**:
- Exact match (ID == query): score = 100
- ID/name match: base fuzzy score + 20 point boost
- Description-only match: base fuzzy score (no boost)
- Multi-field match: combined scores from all fields

```python
results = engine.search_smart("security", limit=10)

# Results ranked by score:
# [
#   {"id": "security-expert", "score": 100, ...},           # Exact match
#   {"id": "security-code-reviewer", "score": 95, ...},     # ID match + high fuzzy
#   {"id": "code-reviewer", "score": 68, ...}               # Description match
# ]
```

**Parameters**:
- `query`: Search query
- `limit`: Maximum results to return (default: 50)

**Returns**: List of resources with 'score' field, ranked by relevance

**Performance**: <0.3ms for 331 resources

**Scoring Details**:

1. **Exact Match** (score = 100):
   ```python
   query = "architect"
   resource["id"] = "architect"
   # score = 100
   ```

2. **ID/Name Match** (score = base + 20):
   ```python
   query = "security"
   resource["id"] = "security-expert"
   # base_score = 85 (fuzzy match)
   # final_score = min(99, 85 + 20) = 99
   ```

3. **Description-Only Match** (score = base):
   ```python
   query = "security"
   resource["id"] = "code-reviewer"
   resource["description"] = "Reviews code for security issues"
   # base_score = 68 (fuzzy match on description)
   # final_score = 68 (no boost)
   ```

**Example**:

```python
engine = SearchEngine()

# Index resources
engine.index_resource({
    "id": "security-expert",
    "name": "Security Expert",
    "description": "Security specialist"
})
engine.index_resource({
    "id": "code-reviewer",
    "name": "Code Reviewer",
    "description": "Reviews code for security issues and best practices"
})

# Smart search with scoring
results = engine.search_smart("security", limit=10)

print(f"Found {len(results)} results:")
for r in results:
    print(f"  {r['id']:20} score={r['score']}")

# Output:
# Found 2 results:
#   security-expert      score=100
#   code-reviewer        score=68
```

##### `search(query: str, limit: int = 50, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]`

**Legacy method**: Combines exact, prefix, and fuzzy search without scoring.

**Recommendation**: Use `search_smart()` instead for better ranking.

```python
results = engine.search("architect", limit=10, filters={"type": "agent"})
```

**Parameters**:
- `query`: Search query
- `limit`: Maximum results
- `filters`: Optional filters (e.g., `{"type": "agent"}`)

**Returns**: List of matching resources (unscored)

**Strategy**:
1. Try exact match → return if found
2. Try prefix match → collect results
3. Try fuzzy match → collect results
4. Combine and deduplicate
5. Apply filters
6. Limit results

##### `search_async(query: str, limit: int = 50, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]`

Async version of search for concurrent operations.

```python
async def search_multiple():
    tasks = [
        engine.search_async("architect", limit=5),
        engine.search_async("security", limit=5),
        engine.search_async("test", limit=5)
    ]
    results = await asyncio.gather(*tasks)
    return results

# Results: [[arch results], [security results], [test results]]
```

**Parameters**:
- `query`: Search query
- `limit`: Maximum results
- `filters`: Optional filters

**Returns**: List of matching resources

**Performance**: Runs sync search in executor to avoid blocking event loop

---

### Performance Characteristics

| Operation | Complexity | Phase 2 Benchmark | Phase 1 Target |
|-----------|------------|-------------------|----------------|
| Exact match | O(1) | <1ms | <1ms |
| Prefix match | O(k+m) | <2ms | <2ms |
| Fuzzy match | O(n) | 0.29ms | <20ms |
| Smart search | O(n) | 0.32ms | <5ms |

**Memory**: ~2MB for search index (331 resources)

---

### Usage Examples

#### Basic Search

```python
from claude_resource_manager.core.search_engine import SearchEngine

engine = SearchEngine()

# Index resources
for resource in load_resources():
    engine.index_resource(resource)

# Search with typo tolerance
results = engine.search_smart("architet", limit=10)

for r in results:
    print(f"{r['id']:30} score={r['score']}")
```

#### Cached Search

```python
# Enable caching for repeated queries
engine = SearchEngine(use_cache=True)

# First search (uncached)
results1 = engine.search("architect", limit=10)  # ~0.32ms

# Second search (cached)
results2 = engine.search("architect", limit=10)  # ~0.01ms (32x faster)
```

#### Custom Indexing

```python
# Index only specific fields
engine = SearchEngine(index_fields=["id", "tags"])

engine.index_resource({
    "id": "security-expert",
    "tags": ["security", "audit", "compliance"],
    "description": "This won't be indexed"
})

# Search only matches ID and tags
results = engine.search_fuzzy("audit", limit=10)
# Finds "security-expert" via tags
```

#### Filtered Search

```python
# Search with type filter
results = engine.search(
    "architect",
    limit=10,
    filters={"type": "agent"}
)
# Returns only agents matching "architect"

# Multiple filters
results = engine.search(
    "mcp",
    limit=10,
    filters={"type": "mcp", "version": "v1.0"}
)
```

---

## Async Installer

**Module**: `claude_resource_manager.core.installer`

The AsyncInstaller provides secure resource installation with atomic writes, retry logic, and batch operations.

### Classes

#### InstallResult

Result of an installation operation.

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class InstallResult:
    """Result of installation operation."""
    success: bool                  # Installation succeeded
    path: Optional[Path] = None    # Installed file path (if success)
    error: Optional[str] = None    # Error message (if failed)
    message: str = ""              # Status message
    skipped: bool = False          # Already installed (skipped)
```

**Example**:

```python
# Success
InstallResult(
    success=True,
    path=Path("~/.claude/agents/architect.md"),
    message="Installation successful"
)

# Skipped (already installed)
InstallResult(
    success=True,
    path=Path("~/.claude/agents/architect.md"),
    message="Already installed",
    skipped=True
)

# Failed
InstallResult(
    success=False,
    error="Download failed: 404 Not Found"
)
```

---

#### AsyncInstaller

Async resource installer with atomic writes and retry logic.

**Features**:
- HTTPS-only downloads (CWE-319 prevention)
- Atomic file writes (temp file + rename)
- Automatic retry with exponential backoff
- Checksum verification (optional)
- Path traversal prevention (CWE-22)
- Progress callbacks
- Concurrent installation support
- Batch operations with dependency resolution

```python
class AsyncInstaller:
    """Async resource installer."""

    def __init__(
        self,
        base_path: Path,
        max_retries: int = 3,
        timeout: float = 30.0,
    ):
        """Initialize installer.

        Args:
            base_path: Base directory for installations
            max_retries: Max download retry attempts
            timeout: Download timeout in seconds
        """
        self.base_path = Path(base_path)
        self.max_retries = max_retries
        self.timeout = timeout
```

**Methods**:

##### `install(resource: dict[str, Any], force: bool = False, progress_callback: Optional[Callable] = None) -> InstallResult`

**New in Phase 2**: Enhanced with progress callbacks and better error handling.

Install a resource with atomic write and retry logic.

```python
installer = AsyncInstaller(base_path=Path("~/.claude"))

resource = {
    "id": "architect",
    "type": "agent",
    "source": {
        "url": "https://raw.githubusercontent.com/.../architect.md",
        "sha256": "abc123..."  # Optional checksum
    },
    "install_path": "agents/architect.md"
}

# Simple install
result = await installer.install(resource)

if result.success:
    print(f"Installed to: {result.path}")
else:
    print(f"Failed: {result.error}")
```

**Parameters**:
- `resource`: Resource dictionary to install
- `force`: If True, overwrite existing file (default: False)
- `progress_callback`: Optional callback(status: str, percent: float)

**Returns**: InstallResult with success status

**Process**:
1. Validate URL (HTTPS-only)
2. Validate install path (no traversal)
3. Check if already installed (skip if not forced)
4. Download with retry
5. Verify checksum (if provided)
6. Atomic write (temp file + rename)

**Progress Callbacks**:

```python
async def progress(status: str, percent: float):
    print(f"[{percent*100:3.0f}%] {status}")

result = await installer.install(resource, progress_callback=progress)

# Output:
# [  0%] Starting installation
# [ 30%] Downloading
# [ 70%] Verifying
# [ 90%] Writing file
# [100%] Complete
```

**Error Handling**:

```python
# Timeout
InstallResult(success=False, error="Download timeout: ...")

# HTTP error
InstallResult(success=False, error="Download failed: 404 Not Found")

# Disk full
InstallResult(success=False, error="Disk full: No space left on device")

# Checksum mismatch
InstallResult(success=False, error="Checksum mismatch. Expected: abc123, Got: def456")

# Security error
InstallResult(success=False, error="URL must use HTTPS")
InstallResult(success=False, error="Path traversal detected: ../../etc/passwd")
```

**Atomic Writes**:

The installer uses atomic file writes to prevent partial writes:

1. Write to temp file: `.tmp_XXXXXX.download`
2. Verify write succeeded
3. Atomic rename to target path
4. Clean up temp file on error

This ensures installations are all-or-nothing (never partial files).

##### `install_with_dependencies(resource: dict[str, Any], force: bool = False) -> list[InstallResult]`

Install resource with dependencies in topological order.

```python
resource = {
    "id": "web-server",
    "type": "agent",
    "dependencies": {
        "required": ["config-loader", "auth-handler"]
    },
    ...
}

# Installs dependencies first, then web-server
results = await installer.install_with_dependencies(resource)

# Results in topological order:
# [
#   InstallResult(success=True, path=".../config-loader.md"),
#   InstallResult(success=True, path=".../auth-handler.md"),
#   InstallResult(success=True, path=".../web-server.md")
# ]
```

**Parameters**:
- `resource`: Resource to install with dependencies
- `force`: If True, reinstall even if already installed

**Returns**: List of InstallResult in dependency order

**Dependency Resolution**:
- Recursively installs required dependencies first
- Detects circular dependencies
- Uses topological sort for correct order

**Example with Circular Dependency**:

```python
# Circular: web-server → api-client → auth → web-server
results = await installer.install_with_dependencies(resource)

# Returns error:
# [InstallResult(
#   success=False,
#   error="Circular dependency detected involving: web-server"
# )]
```

##### `batch_install(resources: list[dict[str, Any]], progress_callback: Optional[Callable] = None, parallel: bool = True, rollback_on_error: bool = False, skip_installed: bool = False) -> list[InstallResult]`

**New in Phase 2**: Install multiple resources with progress tracking.

```python
resources = [
    {"id": "architect", ...},
    {"id": "security-expert", ...},
    {"id": "test-generator", ...}
]

# Progress callback
async def progress(resource_id: str, current: int, total: int, status: str):
    print(f"[{current}/{total}] {resource_id}: {status}")

results = await installer.batch_install(
    resources,
    progress_callback=progress,
    parallel=True,
    skip_installed=True
)

# Output:
# [1/3] architect: Installing
# [2/3] security-expert: Installing
# [3/3] test-generator: Installing
```

**Parameters**:
- `resources`: List of resources to install
- `progress_callback`: Optional callback(resource_id, current, total, status)
- `parallel`: Use parallel downloads (faster) - default: True
- `rollback_on_error`: Rollback all on any failure - default: False
- `skip_installed`: Skip already installed resources - default: False

**Returns**: List of InstallResult for each resource

**Features**:
- Automatic deduplication by resource ID
- Dependency resolution for each resource
- Circular dependency detection
- Progress tracking
- Optional rollback on error

**Deduplication**:

```python
resources = [
    {"id": "architect", ...},
    {"id": "architect", ...},  # Duplicate - skipped
    {"id": "security", ...}
]

results = await installer.batch_install(resources)
# Installs only 2 unique resources
```

**Circular Dependency Handling**:

```python
resources = [
    {"id": "a", "dependencies": {"required": ["b"]}},
    {"id": "b", "dependencies": {"required": ["c"]}},
    {"id": "c", "dependencies": {"required": ["a"]}}  # Circular!
]

results = await installer.batch_install(resources)
# Returns error for all:
# [InstallResult(success=False, error="Circular dependency..."), ...]
```

##### `batch_install_with_summary(resources: list[dict[str, Any]], **kwargs) -> dict[str, Any]`

**New in Phase 2**: Install batch and return summary dictionary.

```python
summary = await installer.batch_install_with_summary(resources)

print(f"Total: {summary['total']}")
print(f"Succeeded: {summary['succeeded']}")
print(f"Failed: {summary['failed']}")
print(f"Skipped: {summary['skipped']}")
print(f"Duration: {summary['duration']:.2f}s")

# Output:
# Total: 5
# Succeeded: 4
# Failed: 0
# Skipped: 1
# Duration: 2.45s
```

**Parameters**:
- `resources`: List of resources to install
- `**kwargs`: Additional arguments passed to batch_install()

**Returns**: Dictionary with summary statistics:

```python
{
    "total": int,              # Total resources processed
    "succeeded": int,          # Successfully installed
    "failed": int,             # Failed installations
    "skipped": int,            # Skipped (already installed)
    "duration": float,         # Total time in seconds
    "results": list[InstallResult]  # Individual results
}
```

##### `rollback_batch(results: list[InstallResult]) -> None`

**New in Phase 2**: Rollback installed resources from batch.

Deletes all successfully installed files (useful if batch partially failed).

```python
results = await installer.batch_install(resources)

if any(not r.success for r in results):
    # Partial failure - rollback all
    await installer.rollback_batch(results)
    print("Batch failed, all changes rolled back")
```

**Parameters**:
- `results`: List of install results to rollback

**Behavior**:
- Deletes files for all successful results
- Ignores errors during rollback
- Does not affect skipped results

**Example**:

```python
# Install batch
results = [
    InstallResult(success=True, path=Path("~/.claude/agents/a.md")),
    InstallResult(success=True, path=Path("~/.claude/agents/b.md")),
    InstallResult(success=False, error="Download failed"),
]

# Rollback
await installer.rollback_batch(results)
# Deletes: a.md, b.md
# Leaves: (nothing, c.md was never installed)
```

---

### Performance Characteristics

| Operation | Duration | Notes |
|-----------|----------|-------|
| Single install | 0.5-2s | Depends on download size/speed |
| Batch install (5) | 2-5s | Parallel downloads |
| Batch install (5) sequential | 5-10s | Serial downloads |
| Rollback | <100ms | Fast file deletion |

---

### Usage Examples

#### Simple Installation

```python
from claude_resource_manager.core.installer import AsyncInstaller
from pathlib import Path

installer = AsyncInstaller(base_path=Path("~/.claude"))

resource = {
    "id": "architect",
    "type": "agent",
    "source": {
        "url": "https://raw.githubusercontent.com/.../architect.md"
    },
    "install_path": "agents/architect.md"
}

result = await installer.install(resource)

if result.success:
    print(f"✓ Installed: {result.path}")
else:
    print(f"✗ Failed: {result.error}")
```

#### Batch Installation with Progress

```python
resources = load_selected_resources()  # User's selection

async def progress(resource_id: str, current: int, total: int, status: str):
    print(f"[{current}/{total}] {resource_id}: {status}")

summary = await installer.batch_install_with_summary(
    resources,
    progress_callback=progress,
    skip_installed=True
)

print(f"\nInstallation complete:")
print(f"  Succeeded: {summary['succeeded']}")
print(f"  Failed: {summary['failed']}")
print(f"  Skipped: {summary['skipped']}")
print(f"  Duration: {summary['duration']:.2f}s")
```

#### Installation with Rollback

```python
results = await installer.batch_install(
    resources,
    rollback_on_error=False  # Manual rollback control
)

failed = [r for r in results if not r.success]

if failed:
    print(f"⚠ {len(failed)} installations failed:")
    for r in failed:
        print(f"  - {r.error}")

    # Ask user if they want to rollback
    if input("Rollback all changes? (y/n): ").lower() == 'y':
        await installer.rollback_batch(results)
        print("All changes rolled back")
```

---

## Cache Utilities

**Module**: `claude_resource_manager.utils.cache` *(hypothetical - not in codebase)*

**Note**: Phase 2 uses Python's built-in `functools.lru_cache` for search caching. This section documents the conceptual cache utilities mentioned in Phase 2 requirements.

### LRU Cache

```python
from functools import lru_cache

class SearchEngine:
    def __init__(self, use_cache: bool = False):
        if use_cache:
            # Wrap search method with LRU cache
            self.search = lru_cache(maxsize=100)(self._search_impl)
        else:
            self.search = self._search_impl
```

**Configuration**:
- `maxsize=100`: Cache up to 100 unique queries
- Eviction policy: Least Recently Used (LRU)
- Hit rate: ~64% (realistic workload)

**Usage**:

```python
engine = SearchEngine(use_cache=True)

# First query (cache miss)
results = engine.search("architect", limit=10)  # ~0.32ms

# Repeat query (cache hit)
results = engine.search("architect", limit=10)  # ~0.01ms (32x faster)

# Clear cache
engine.search.cache_clear()
```

---

## TUI Components

**Module**: `claude_resource_manager.tui.screens`

### HelpScreen

**New in Phase 2**: Modal help screen with keyboard shortcuts.

**Module**: `claude_resource_manager.tui.screens.help_screen`

```python
from claude_resource_manager.tui.screens.help_screen import HelpScreen

class HelpScreen(ModalScreen):
    """Modal help screen displaying keyboard shortcuts."""

    def __init__(self, context: Optional[str] = None, **kwargs):
        """Initialize help screen.

        Args:
            context: Optional context for context-sensitive help
                    ('browser', 'detail', 'search')
        """
```

**Usage**:

```python
# In your TUI app
from textual.app import App

class MyApp(App):
    def action_show_help(self):
        """Show help screen (bound to '?' key)."""
        self.push_screen(HelpScreen(context="browser"))
```

**Features**:
- Context-sensitive help based on current screen
- Scrollable content
- Rich markup formatting
- Keyboard shortcuts organized by category

**Bindings**:
- `?`: Show help (global)
- `Escape` or `q`: Close help

---

### BrowserScreen (Multi-Select)

**Enhanced in Phase 2**: Multi-select functionality.

**New Attributes**:

```python
class BrowserScreen(Screen):
    """Browser screen with multi-select support."""

    def __init__(self, ...):
        self.selected_resources: set[str] = set()  # Selected resource IDs
        self.max_selections: Optional[int] = None  # Max selection limit
```

**New Methods**:

##### `toggle_selection() -> None`

Toggle selection for current resource.

```python
# Bound to Space key
# Press Space on any resource to toggle selection
```

##### `select_all_visible() -> None`

Select all visible resources (respects current filter).

```python
# Bound to 'a' key
# Selects all resources currently displayed
```

##### `clear_selections() -> None`

Clear all selections.

```python
# Bound to 'c' key
# Clears selection set
```

##### `install_selected() -> None`

Install all selected resources.

```python
# Bound to 'i' key
# Batch installs all selected resources with progress
```

**Visual Indicators**:

```text
DataTable with checkbox column:

[ ] architect              # Not selected
[x] security-expert        # Selected
[ ] test-generator         # Not selected
[x] code-reviewer          # Selected

Status bar: "2 resources selected"
```

---

## Summary

Phase 2 APIs provide:

- **CategoryEngine**: Automatic hierarchical categorization (0.77ms for 331 resources)
- **SearchEngine**: Multi-strategy search with fuzzy matching (0.32ms average)
- **AsyncInstaller**: Batch installation with dependencies (2-5s for 5 resources)
- **HelpScreen**: Context-sensitive help system
- **Multi-Select**: Batch operations in BrowserScreen

All APIs follow:
- Type hints (mypy strict compliant)
- Google-style docstrings
- Comprehensive error handling
- Performance-first design
- Security best practices

See [PHASE_2_FEATURES.md](PHASE_2_FEATURES.md) for user-facing documentation and [ARCHITECTURE_PHASE2.md](ARCHITECTURE_PHASE2.md) for technical design details.
