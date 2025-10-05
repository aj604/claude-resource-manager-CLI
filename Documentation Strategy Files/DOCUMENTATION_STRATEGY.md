# Documentation Strategy - Claude Resource Manager CLI

**Role:** DocuMentor - Documentation Architecture Specialist
**Project:** Claude Resource Manager CLI (Python Implementation)
**Date:** 2025-10-04
**Status:** Ready for Implementation Phase

---

## Executive Summary

This document defines the **comprehensive inline documentation strategy** for the Claude Resource Manager CLI Python implementation. As code is developed following TDD principles, documentation will be added **concurrently** to ensure 100% coverage of all public APIs.

**Documentation Principles:**
1. **Security-First**: All security-critical code MUST have explanatory comments
2. **Type-Safe**: All functions MUST have Google-style docstrings with type hints
3. **Example-Rich**: Complex functions MUST include usage examples
4. **Living Docs**: Documentation evolves with code, validated by tests

---

## Documentation Requirements

### 1. Module-Level Documentation

Every Python module MUST have a module-level docstring:

```python
"""Module for loading and validating YAML catalog files.

This module provides SECURITY CRITICAL functionality for safely loading
YAML catalog files. All YAML loading MUST use yaml.safe_load() to prevent
code execution attacks (CWE-502).

Key Security Controls:
    - YAML safe_load only (no yaml.load)
    - File size limits (max 1MB)
    - Parse timeout (5 seconds)
    - Path traversal prevention

Typical usage example:

    from pathlib import Path
    from claude_resource_manager.core.catalog_loader import CatalogLoader

    loader = CatalogLoader(Path.home() / '.claude' / 'catalog')
    catalog = loader.load_index()
    print(f"Loaded {catalog.total} resources")

Security Note:
    This module handles untrusted YAML input. All validation must be
    strict and defensive. See tests/unit/test_security_yaml_loading.py
    for security test cases.
"""
```

### 2. Class Documentation

Every class MUST have a comprehensive docstring with Attributes section:

```python
class CatalogLoader:
    """Loads and validates YAML catalog files with security controls.

    This class provides safe YAML loading with multiple security layers:
    - File size validation (max 1MB)
    - YAML safe_load only (prevents code execution)
    - Timeout protection (prevents YAML bombs)
    - Path validation (prevents directory traversal)

    Attributes:
        catalog_path: Path to the catalog directory containing YAML files
        timeout: Maximum seconds allowed for YAML parsing (default: 5)
        max_file_size: Maximum file size in bytes (default: 1MB)
        use_cache: Whether to cache loaded resources (default: True)
        _index_cache: Internal cache for catalog index (Optional[Dict])
        _resource_cache: Internal cache for loaded resources (Dict[str, Resource])

    Example:
        >>> from pathlib import Path
        >>> loader = CatalogLoader(Path('/path/to/catalog'))
        >>> index = loader.load_index()
        >>> print(index.total)
        331

    Security:
        This class is SECURITY CRITICAL. All YAML loading uses yaml.safe_load
        to prevent arbitrary code execution. File size limits prevent DoS
        attacks. Path validation prevents directory traversal (CWE-22).

    Raises:
        FileNotFoundError: If catalog directory or index.yaml doesn't exist
        ValidationError: If YAML content fails Pydantic validation
        ValueError: If file size exceeds max_file_size
        yaml.YAMLError: If YAML is malformed
        TimeoutError: If parsing exceeds timeout
    """
```

### 3. Function/Method Documentation

Every function MUST have Google-style docstring with Args, Returns, Raises:

```python
def load_resource(self, resource_id: str, resource_type: str) -> Resource:
    """Load a single resource from the catalog.

    Loads and validates a resource YAML file, returning a validated
    Resource model. Uses caching to avoid redundant file I/O.

    Args:
        resource_id: The unique identifier of the resource (e.g., 'architect')
        resource_type: The type of resource ('agent', 'command', 'hook', etc.)

    Returns:
        A validated Resource model with all fields populated

    Raises:
        FileNotFoundError: If resource YAML file doesn't exist
        ValidationError: If YAML content fails Resource model validation
        ValueError: If file size exceeds max_file_size
        yaml.YAMLError: If YAML is malformed

    Example:
        >>> loader = CatalogLoader(catalog_path)
        >>> resource = loader.load_resource('architect', 'agent')
        >>> print(resource.name)
        'architect'

    Performance:
        Uses O(1) dict lookup if resource is cached. First load requires
        file I/O (~1-5ms). Cached lookups are <1ms.

    Security:
        Validates resource_id and resource_type to prevent path traversal.
        All paths are resolved and checked against catalog_path base directory.
    """
    # Implementation here
```

### 4. Security-Critical Code Comments

All security-critical code MUST have explanatory comments:

```python
def validate_path(self, user_path: str, base_dir: Path) -> Path:
    """Validate that a user-provided path is safe and within base directory.

    This is a SECURITY CRITICAL function that prevents path traversal
    attacks (CWE-22). It ensures user-provided paths cannot escape the
    base directory using techniques like '../../../etc/passwd'.

    Args:
        user_path: The user-provided path to validate (untrusted input)
        base_dir: The base directory that user_path must be relative to

    Returns:
        The validated absolute Path object, guaranteed to be within base_dir

    Raises:
        SecurityError: If path traversal attempt detected or path outside base_dir

    Example:
        >>> validate_path("agents/architect.md", Path.home() / ".claude")
        PosixPath('/home/user/.claude/agents/architect.md')

        >>> validate_path("../../../etc/passwd", Path.home() / ".claude")
        SecurityError: Path traversal attempt detected

    Security:
        1. Resolves user_path to absolute path
        2. Resolves base_dir to absolute path
        3. Checks if user_path starts with base_dir
        4. Validates no symlinks escape base_dir
    """
    # SECURITY: Resolve to absolute paths to detect traversal
    abs_user_path = Path(user_path).resolve()
    abs_base_dir = base_dir.resolve()

    # SECURITY: Check if resolved path is within base directory
    try:
        abs_user_path.relative_to(abs_base_dir)
    except ValueError:
        raise SecurityError(
            f"Path traversal attempt detected: {user_path} "
            f"is outside {base_dir}"
        )

    # SECURITY: Ensure no symlinks escape the base directory
    if abs_user_path.is_symlink():
        link_target = abs_user_path.readlink()
        if not link_target.is_relative_to(abs_base_dir):
            raise SecurityError(
                f"Symlink escapes base directory: {user_path} -> {link_target}"
            )

    return abs_user_path
```

### 5. Complex Algorithm Documentation

Complex algorithms MUST have step-by-step comments:

```python
def smart_search(self, query: str) -> List[SearchResult]:
    """Multi-strategy search combining exact, prefix, and fuzzy matching.

    Implements a cascading search strategy that tries multiple approaches
    and combines results with intelligent scoring.

    Args:
        query: The search query string

    Returns:
        List of SearchResult objects sorted by relevance score (highest first)

    Algorithm:
        1. Exact match: O(1) hash lookup, score = 100
        2. Prefix match: O(k) trie search where k = query length, score = 90
        3. Fuzzy match: O(n) fuzzy string matching, score = similarity * 100
        4. Combine and deduplicate results
        5. Sort by score descending

    Performance:
        - Exact match: <1ms (hash lookup)
        - Prefix match: <5ms (trie traversal)
        - Fuzzy match: <20ms (RapidFuzz with 331 resources)
        - Total: <25ms for worst case

    Example:
        >>> results = search_index.smart_search('arch')
        >>> results[0].resource.id
        'architect'
        >>> results[0].score
        90.0  # Prefix match
    """
    results: Dict[str, SearchResult] = {}
    query_lower = query.lower().strip()

    # Step 1: Try exact match (highest priority)
    # O(1) hash lookup for instant exact matches
    if exact_resource := self._resources.get(query_lower):
        results[exact_resource.id] = SearchResult(
            resource=exact_resource,
            score=100.0,  # Perfect score for exact match
            match_type='exact'
        )

    # Step 2: Try prefix match (high priority)
    # Uses trie for efficient prefix searching
    prefix_matches = self._prefix_tree.find_prefix(query_lower)
    for resource_id in prefix_matches:
        if resource_id not in results:  # Don't override exact matches
            results[resource_id] = SearchResult(
                resource=self._resources[resource_id],
                score=90.0,  # High score for prefix match
                match_type='prefix'
            )

    # Step 3: Try fuzzy match (fallback for typos)
    # Uses RapidFuzz for fast approximate string matching
    fuzzy_matches = self._fuzzy_search(query_lower, limit=20)
    for resource, score in fuzzy_matches:
        if resource.id not in results:  # Don't override better matches
            results[resource.id] = SearchResult(
                resource=resource,
                score=score,
                match_type='fuzzy'
            )

    # Step 4: Sort by score descending and return
    return sorted(results.values(), key=lambda r: r.score, reverse=True)
```

---

## Documentation Coverage Requirements

### Coverage Targets by Module

| Module | Classes | Functions | Coverage Target | Priority |
|--------|---------|-----------|-----------------|----------|
| `models/` | 5 | 15 | 100% | Critical |
| `core/catalog_loader.py` | 1 | 8 | 100% | Critical |
| `core/search_engine.py` | 1 | 12 | 100% | Critical |
| `core/installer.py` | 1 | 10 | 100% | Critical |
| `core/dependency_resolver.py` | 1 | 6 | 100% | Critical |
| `utils/validators.py` | 0 | 8 | 100% | Critical (Security) |
| `utils/security.py` | 0 | 5 | 100% | Critical (Security) |
| `tui/app.py` | 1 | 15 | 90% | High |
| `tui/widgets/` | 5 | 20 | 85% | Medium |
| `cli/commands/` | 0 | 8 | 90% | High |

**Overall Target: 95% documentation coverage**

### What MUST Be Documented

**Required Documentation:**
- ✅ All public classes
- ✅ All public functions/methods
- ✅ All class attributes (in class docstring)
- ✅ All function parameters (Args section)
- ✅ All return values (Returns section)
- ✅ All raised exceptions (Raises section)
- ✅ All security-critical code paths
- ✅ All complex algorithms
- ✅ All module-level exports

**Optional Documentation:**
- Private methods (if complex)
- Internal helper functions (if non-obvious)
- Type aliases (if not self-documenting)

---

## Documentation Templates

### Template 1: Pydantic Model

```python
"""Pydantic models for resource data validation."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

class Resource(BaseModel):
    """Represents a Claude resource with validation.

    A Resource is any reusable component (agent, command, hook, template, or MCP)
    that can be installed and used in Claude projects. This model provides
    type-safe validation of resource data loaded from YAML files.

    Attributes:
        id: Unique identifier for the resource (lowercase, alphanumeric + hyphens)
        type: Resource type ('agent', 'command', 'hook', 'template', 'mcp')
        name: Human-readable display name
        description: Detailed description of resource functionality
        version: Semantic version string (e.g., 'v1.0.0')
        author: Optional author name or organization
        file_type: File extension for the resource (default: '.md')
        source: Source information for downloading the resource
        install_path: Optional custom installation path
        metadata: Additional metadata as key-value pairs
        dependencies: Optional dependency information

    Example:
        >>> resource = Resource(
        ...     id='architect',
        ...     type='agent',
        ...     name='Architect Agent',
        ...     description='System architecture design specialist',
        ...     version='v1.0.0'
        ... )
        >>> resource.id
        'architect'

    Validation:
        - ID must be lowercase, alphanumeric with hyphens only
        - Type must be one of the valid resource types
        - Version must follow semantic versioning pattern
        - Source URL must use HTTPS (security requirement)
        - Cannot have circular dependencies (self-reference)

    Security:
        Resource data comes from YAML files (untrusted input). All fields
        are validated against strict schemas. IDs are validated to prevent
        path traversal attacks.
    """

    id: str = Field(..., min_length=1, max_length=100)
    type: str  # Will be validated as Literal type
    name: str
    description: str = Field(..., max_length=1000)
    version: str = Field(default='v1.0.0')
    author: Optional[str] = None
    file_type: str = '.md'
    source: Optional[Dict[str, str]] = None
    install_path: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    dependencies: Optional['Dependency'] = None

    @validator('id')
    def validate_id(cls, v: str) -> str:
        """Validate ID format to prevent security issues.

        IDs must be lowercase, alphanumeric with hyphens only. This prevents
        path traversal attacks and ensures consistent naming.

        Args:
            v: The ID value to validate

        Returns:
            The validated lowercase ID

        Raises:
            ValueError: If ID contains invalid characters

        Security:
            This validation prevents path traversal attacks by rejecting
            IDs like '../../../etc/passwd' or 'agent/../secret'.
        """
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError(f"Invalid ID format: {v}")
        return v.lower()

    class Config:
        """Pydantic model configuration."""
        validate_assignment = True
        use_enum_values = True
```

### Template 2: Core Business Logic

```python
"""Search index implementation with multiple search strategies."""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass
import threading
from rapidfuzz import fuzz, process

@dataclass
class SearchResult:
    """A single search result with scoring information.

    Attributes:
        resource: The matched Resource object
        score: Relevance score (0-100, higher is better)
        match_type: Type of match ('exact', 'prefix', 'fuzzy')
    """
    resource: 'Resource'
    score: float
    match_type: str

class SearchIndex:
    """High-performance search index with multiple strategies.

    Provides three search strategies with intelligent ranking:
    1. Exact match: O(1) hash lookup
    2. Prefix match: O(k) trie search where k = query length
    3. Fuzzy match: O(n) fuzzy string matching

    Results are ranked by match quality and presented in order of relevance.

    Attributes:
        _resources: Dict mapping resource IDs to Resource objects
        _inverted_index: Dict mapping words to sets of resource IDs
        _prefix_tree: Trie structure for efficient prefix search
        _lock: Thread lock for concurrent access safety
        _fuzzy_cache: LRU cache for fuzzy search results

    Thread Safety:
        All public methods are thread-safe using internal locks.
        Safe for concurrent access from multiple TUI components.

    Performance:
        - Exact search: <1ms (hash lookup)
        - Prefix search: <5ms (trie traversal)
        - Fuzzy search: <20ms (cached with RapidFuzz)
        - Memory: ~10MB for 331 resources

    Example:
        >>> index = SearchIndex()
        >>> index.add_resource(resource)
        >>> results = index.search('arch', mode='smart')
        >>> results[0].resource.id
        'architect'
        >>> results[0].score
        90.0
    """
```

### Template 3: Security-Critical Function

```python
def safe_yaml_load(file_path: Path, max_size: int = 1024 * 1024) -> Dict:
    """Safely load YAML file with security controls.

    This is a SECURITY CRITICAL function that loads YAML files with
    multiple protection layers against common attacks:
    - File size limit (prevents DoS)
    - yaml.safe_load only (prevents code execution - CWE-502)
    - Timeout protection (prevents YAML bombs)
    - UTF-8 validation (prevents encoding attacks)

    Args:
        file_path: Path to the YAML file to load
        max_size: Maximum file size in bytes (default: 1MB)

    Returns:
        Parsed YAML content as a dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file size exceeds max_size
        yaml.YAMLError: If YAML is malformed
        TimeoutError: If parsing takes >5 seconds
        UnicodeDecodeError: If file is not valid UTF-8

    Example:
        >>> data = safe_yaml_load(Path('catalog/index.yaml'))
        >>> data['total']
        331

    Security:
        NEVER use yaml.load() - it can execute arbitrary code!
        This function uses yaml.safe_load() which only constructs
        simple Python objects (dict, list, str, int, float, bool, None).

        File size check prevents billion laughs attack (YAML bomb).
        Timeout prevents algorithmic complexity attacks.

    See Also:
        - CWE-502: Deserialization of Untrusted Data
        - tests/unit/test_security_yaml_loading.py for security tests
    """
    # SECURITY: Check file size before reading
    file_size = file_path.stat().st_size
    if file_size > max_size:
        raise ValueError(
            f"File size {file_size} exceeds maximum {max_size} bytes"
        )

    # SECURITY: Read with UTF-8 validation
    try:
        content = file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError as e:
        raise ValueError(f"Invalid UTF-8 in {file_path}: {e}")

    # SECURITY: Use safe_load ONLY (never yaml.load)
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in {file_path}: {e}")

    return data
```

### Template 4: Async Function

```python
async def download_resource(self, url: str, verify_ssl: bool = True) -> bytes:
    """Download resource content from URL with retry logic.

    Downloads resource content asynchronously with automatic retries
    on network failures. Uses exponential backoff for retry delays.

    Args:
        url: HTTPS URL to download from (HTTP not allowed for security)
        verify_ssl: Whether to verify SSL certificates (default: True)

    Returns:
        Downloaded content as bytes

    Raises:
        ValueError: If URL is not HTTPS
        SecurityError: If SSL verification fails
        httpx.HTTPError: If download fails after all retries

    Example:
        >>> content = await downloader.download_resource(
        ...     'https://raw.githubusercontent.com/org/repo/main/agent.md'
        ... )
        >>> len(content)
        1234

    Performance:
        Uses httpx async client with connection pooling.
        Typical download: 200-500ms depending on network and file size.
        Retries use exponential backoff: 1s, 2s, 4s delays.

    Security:
        - HTTPS only (prevents MITM attacks)
        - SSL verification enabled by default
        - Content-Length header checked (prevents DoS)

    Concurrency:
        Uses semaphore to limit concurrent downloads (max 5).
        Safe to call from multiple coroutines.
    """
    # SECURITY: Enforce HTTPS only
    if not url.startswith('https://'):
        raise ValueError(f"URL must use HTTPS: {url}")

    async with self.semaphore:  # Limit concurrency
        for attempt in range(3):  # 3 attempts with exponential backoff
            try:
                async with self.session.get(url, verify=verify_ssl) as response:
                    response.raise_for_status()
                    return await response.read()
            except httpx.HTTPError as e:
                if attempt == 2:  # Last attempt
                    raise
                # Exponential backoff: 1s, 2s, 4s
                await asyncio.sleep(2 ** attempt)
```

---

## Documentation Validation

### Automated Checks

```python
# scripts/validate_docs.py
"""Validate documentation coverage and quality."""

import ast
import inspect
from pathlib import Path
from typing import List, Tuple

def check_docstring_coverage(module_path: Path) -> Tuple[int, int, List[str]]:
    """Check docstring coverage for a Python module.

    Args:
        module_path: Path to Python module to check

    Returns:
        Tuple of (documented, total, missing) where:
        - documented: Number of items with docstrings
        - total: Total number of items that should have docstrings
        - missing: List of item names missing docstrings
    """
    with open(module_path) as f:
        tree = ast.parse(f.read())

    documented = 0
    total = 0
    missing = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            total += 1
            docstring = ast.get_docstring(node)
            if docstring:
                documented += 1
            else:
                missing.append(f"{node.__class__.__name__}: {node.name}")

    return documented, total, missing

def validate_docstring_format(docstring: str, item_type: str) -> List[str]:
    """Validate docstring follows Google style guide.

    Args:
        docstring: The docstring text to validate
        item_type: Type of item ('function', 'class', 'module')

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if item_type == 'function':
        if 'Args:' not in docstring and 'Returns:' not in docstring:
            errors.append("Missing Args or Returns section")

        if 'Example:' not in docstring and len(docstring) > 200:
            errors.append("Complex function missing Example section")

    elif item_type == 'class':
        if 'Attributes:' not in docstring:
            errors.append("Class missing Attributes section")

    return errors
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
# Validate documentation before commit

echo "Validating documentation coverage..."

python scripts/validate_docs.py

if [ $? -ne 0 ]; then
    echo "❌ Documentation validation failed"
    echo "Please add docstrings to all public classes and functions"
    exit 1
fi

echo "✅ Documentation validation passed"
```

---

## Documentation Workflow

### During Implementation

1. **Write Test First** (TDD)
   ```python
   # tests/unit/core/test_catalog_loader.py
   def test_load_resource_by_id():
       """Test loading resource by ID."""
       # Test implementation
   ```

2. **Implement Function WITH Docstring**
   ```python
   # src/claude_resource_manager/core/catalog_loader.py
   def load_resource(self, resource_id: str) -> Resource:
       """Load a single resource by ID.

       Args:
           resource_id: Unique identifier of the resource

       Returns:
           Validated Resource model

       Raises:
           FileNotFoundError: If resource doesn't exist
       """
       # Implementation
   ```

3. **Add Security Comments If Applicable**
   ```python
   # SECURITY: Validate path to prevent traversal
   safe_path = self.validate_path(resource_id)
   ```

4. **Run Documentation Validation**
   ```bash
   python scripts/validate_docs.py src/claude_resource_manager/core/catalog_loader.py
   ```

5. **Update Module Docstring**
   ```python
   """Catalog loading with security controls.

   Updated: 2025-10-04
   Coverage: 100%
   Security Tests: tests/unit/test_security_yaml_loading.py
   """
   ```

---

## Documentation Report Template

### Weekly Documentation Report

```markdown
# Documentation Coverage Report
**Week:** 1
**Date:** 2025-10-04
**Phase:** Core Implementation

## Coverage Summary

| Module | Functions | Documented | Coverage | Status |
|--------|-----------|------------|----------|--------|
| models/resource.py | 5 | 5 | 100% | ✅ |
| core/catalog_loader.py | 8 | 8 | 100% | ✅ |
| core/search_engine.py | 12 | 10 | 83% | 🟡 |
| utils/validators.py | 8 | 8 | 100% | ✅ |

**Overall Coverage:** 93% (38/41 items documented)

## Missing Documentation

### core/search_engine.py
- `_build_inverted_index()` - Private method, add docstring
- `_fuzzy_cache_key()` - Private helper, add docstring

## Security Documentation Status

All security-critical functions documented: ✅
- `safe_yaml_load()` - Full security comments
- `validate_path()` - Path traversal prevention documented
- `verify_https()` - SSL verification documented

## Action Items

- [ ] Add docstrings to private methods in search_engine.py
- [ ] Add performance notes to search functions
- [ ] Update module-level docstring with examples

## Next Week Goals

- Document TUI layer (15 functions)
- Document CLI commands (8 functions)
- Reach 95% overall coverage
```

---

## Final Documentation Checklist

Before marking implementation complete, verify:

### Module Level
- [ ] Module docstring with purpose and usage example
- [ ] Security note if module handles untrusted input
- [ ] Import statements documented if complex

### Class Level
- [ ] Class docstring with purpose
- [ ] Attributes section listing ALL attributes with types
- [ ] Usage example showing common use case
- [ ] Thread safety notes if applicable
- [ ] Performance characteristics documented

### Function Level
- [ ] One-line summary (first line)
- [ ] Detailed description (optional, if complex)
- [ ] Args section with types and descriptions
- [ ] Returns section with type and description
- [ ] Raises section listing all exceptions
- [ ] Example section for complex functions
- [ ] Performance notes for critical paths
- [ ] Security notes for critical functions

### Security Critical Code
- [ ] SECURITY comment explaining the risk
- [ ] Reference to CWE if applicable
- [ ] Link to security tests
- [ ] Explanation of mitigation

### Complex Algorithms
- [ ] Step-by-step comments
- [ ] Big-O complexity noted
- [ ] Performance measurements if available

---

## Success Metrics

**Documentation Quality Metrics:**
- ✅ 95%+ docstring coverage
- ✅ 100% security-critical code documented
- ✅ 100% public API documented
- ✅ All complex algorithms explained
- ✅ All examples are tested and work
- ✅ mypy strict mode passes
- ✅ Passes automated doc validation

**Maintainability Metrics:**
- New developers can understand code from docs alone
- Security reviewers can validate security controls
- AI assistants can suggest accurate completions
- Documentation builds without warnings
- Examples in docstrings are runnable

---

## Conclusion

This documentation strategy ensures that **as code is written, it is documented**. The TDD approach means tests define behavior, implementation follows tests, and documentation explains both.

**Key Principles:**
1. Document DURING implementation, not after
2. Security-first: all critical code explained
3. Examples tested: all examples must work
4. Living docs: update with code changes

**Next Steps:**
1. Implement first module (models/resource.py)
2. Add comprehensive docstrings following templates
3. Validate with `python scripts/validate_docs.py`
4. Generate weekly coverage report
5. Repeat for each module

By following this strategy, we'll achieve **95%+ documentation coverage** and create a codebase that is both secure and maintainable.
