# Documentation Quick Reference Card

**Quick guide for documenting Python code in this project**

---

## 🎯 Documentation Standards

### Required for ALL public APIs
- ✅ Module docstring
- ✅ Class docstring with Attributes
- ✅ Function docstring with Args/Returns/Raises
- ✅ Security notes for critical code
- ✅ Examples for complex functions

---

## 📝 Templates

### Module Docstring (First thing in file)

```python
"""Brief description of module purpose.

Detailed explanation including:
- What the module does
- Security considerations if applicable
- Performance characteristics
- Typical usage patterns

Typical usage example:

    from module import Class

    obj = Class()
    result = obj.method()

Security Note:
    Add if module handles untrusted input or is security-critical.

See Also:
    - related_module.py
    - tests/unit/test_this_module.py
"""
```

### Class Docstring

```python
class ClassName:
    """One-line summary of class purpose.

    Detailed explanation of what the class does, when to use it,
    and any important design decisions or patterns.

    Attributes:
        attr1: Description of attribute including type
        attr2: Description of attribute including type
        _private: Private attributes can be documented too

    Example:
        >>> obj = ClassName(param=value)
        >>> result = obj.method()
        >>> print(result)
        'expected output'

    Thread Safety:
        Add if class is used concurrently

    Performance:
        Add key performance characteristics if important
    """
```

### Function/Method Docstring

```python
def function_name(arg1: str, arg2: int = 0) -> bool:
    """One-line summary of function purpose.

    Detailed explanation if needed. Keep concise but complete.

    Args:
        arg1: Description of arg1 parameter
        arg2: Description of arg2 with default (default: 0)

    Returns:
        Description of return value and its type

    Raises:
        ValueError: When and why this is raised
        TypeError: When and why this is raised

    Example:
        >>> result = function_name('test', 5)
        >>> result
        True

    Performance:
        Add if performance-critical (e.g., "O(n) complexity")

    Security:
        Add if function validates input or handles sensitive data
    """
```

### Security-Critical Function

```python
def validate_input(user_input: str) -> str:
    """Validate and sanitize user input.

    This is a SECURITY CRITICAL function that prevents [specific attack].

    Args:
        user_input: Untrusted input from user

    Returns:
        Sanitized and validated input

    Raises:
        SecurityError: If validation fails or attack detected

    Example:
        >>> safe = validate_input("normal input")
        >>> safe
        'normal input'

    Security:
        - Prevents [specific attack] (CWE-XXX if applicable)
        - Validates [specific thing]
        - See tests/unit/test_security_*.py
    """
    # SECURITY: Comment explaining the specific check
    if dangerous_pattern in user_input:
        raise SecurityError("Attack detected")

    # SECURITY: Comment explaining sanitization
    return sanitized_input
```

---

## 🔒 Security Documentation

### When to add security notes:

- Any function that validates input
- Any function that handles files/paths
- Any function that processes YAML/JSON
- Any function that makes network requests
- Any function with authentication/authorization

### Security comment template:

```python
# SECURITY: [What attack this prevents]
# Validates [what] to prevent [attack type]
# See CWE-XXX: [attack name]
```

### Examples:

```python
# SECURITY: Validate path to prevent directory traversal (CWE-22)
safe_path = path.resolve().relative_to(base_path)

# SECURITY: Use safe_load ONLY to prevent code execution (CWE-502)
data = yaml.safe_load(content)

# SECURITY: Enforce HTTPS to prevent MITM attacks
if not url.startswith('https://'):
    raise ValueError("HTTPS required")
```

---

## 📊 Performance Documentation

### When to add performance notes:

- Functions with complexity > O(n)
- Functions that do I/O
- Functions that cache results
- Functions used in hot paths

### Performance note template:

```python
"""Function description.

Performance:
    - Complexity: O(n log n)
    - Typical: ~5ms for 1000 items
    - Worst case: ~50ms for 10000 items
    - Cached: <1ms (if applicable)
"""
```

---

## 💡 Examples Section

### When to add examples:

- Complex functions (>10 lines)
- Functions with multiple parameters
- Functions with non-obvious behavior
- Public API functions

### Example formats:

**Simple example:**
```python
Example:
    >>> result = function(arg)
    >>> result
    42
```

**Multi-step example:**
```python
Example:
    >>> obj = MyClass()
    >>> obj.configure(setting=True)
    >>> result = obj.process(data)
    >>> print(result)
    'processed'
```

**Multiple examples:**
```python
Examples:
    Basic usage:
        >>> simple = function('input')

    Advanced usage:
        >>> advanced = function('input', option=True)
        >>> advanced.validate()
        True
```

---

## ✅ Validation Checklist

Before committing, check:

- [ ] Module has docstring with example
- [ ] All classes have docstring with Attributes
- [ ] All public functions have Args/Returns/Raises
- [ ] Security-critical code has SECURITY comments
- [ ] Complex functions have examples
- [ ] Run `python scripts/validate_docs.py`

---

## 🚫 Common Mistakes

### ❌ Don't do this:

```python
def load(p):
    """Load file."""
    # No Args, Returns, or Raises
    # Parameter name 'p' is unclear
    # No example
```

```python
class Thing:
    """A thing."""
    # No Attributes section
    # No examples
    # Too vague
```

```python
# Security check
if bad: raise Error()
# No explanation of WHAT security check
```

### ✅ Do this instead:

```python
def load_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse YAML file.

    Args:
        file_path: Path to YAML file to load

    Returns:
        Parsed YAML content as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML is malformed

    Example:
        >>> data = load_file(Path('config.yaml'))
        >>> data['version']
        '1.0.0'
    """
```

```python
class CatalogLoader:
    """Loads YAML catalog files with validation.

    Attributes:
        catalog_path: Path to catalog directory
        use_cache: Whether to cache loaded files
        _cache: Internal cache dictionary

    Example:
        >>> loader = CatalogLoader(Path('/catalog'))
        >>> data = loader.load()
    """
```

```python
# SECURITY: Validate path to prevent directory traversal (CWE-22)
# Ensures resolved path is within allowed base directory
if not safe_path.is_relative_to(base_path):
    raise SecurityError("Path traversal detected")
```

---

## 🛠️ Tools

### Validate documentation:
```bash
# Single file
python scripts/validate_docs.py src/module.py

# Entire project
python scripts/validate_docs.py

# With details
python scripts/validate_docs.py --verbose
```

### Check with mypy:
```bash
mypy --strict src/claude_resource_manager
```

### Format code:
```bash
black src/claude_resource_manager
ruff check src/claude_resource_manager
```

---

## 📈 Coverage Goals

| Category | Target |
|----------|--------|
| Overall | 95% |
| Security-critical | 100% |
| Public APIs | 100% |
| Private methods | 80% |
| Examples | 50%+ |

---

## 🔗 Resources

- **Full Strategy:** [DOCUMENTATION_STRATEGY.md](DOCUMENTATION_STRATEGY.md)
- **Full Example:** [DOCUMENTATION_EXAMPLE.md](DOCUMENTATION_EXAMPLE.md)
- **Python Guide:** [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- **Security:** [CWE Top 25](https://cwe.mitre.org/top25/)

---

## Quick Copy-Paste Templates

### Minimal function:
```python
def func(arg: str) -> bool:
    """Brief description.

    Args:
        arg: Description

    Returns:
        Description
    """
```

### Security function:
```python
def secure_func(untrusted: str) -> str:
    """Brief description - SECURITY CRITICAL.

    Args:
        untrusted: Untrusted input

    Returns:
        Validated output

    Raises:
        SecurityError: If validation fails

    Security:
        Prevents [attack] (CWE-XXX)
    """
    # SECURITY: Explanation
```

### Async function:
```python
async def async_func(arg: str) -> List[str]:
    """Brief description.

    Args:
        arg: Description

    Returns:
        Description

    Example:
        >>> results = await async_func('test')
        >>> len(results)
        5

    Concurrency:
        Thread-safe / Safe for concurrent calls
    """
```

---

**Remember:** Document WHILE coding, not after! 🚀
