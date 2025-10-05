# Claude Resource Manager CLI - Python Testing Strategy

**Document Version:** 1.0.0
**Date:** October 4, 2025
**Status:** PLANNING ONLY - No Implementation
**Language:** Python 3.11+

---

## Executive Summary

Comprehensive QA framework for Python-based Claude Resource Manager CLI, leveraging pytest and Textual's testing utilities.

**Key Challenges:** TUI interaction testing, dependency graph edge cases, cross-platform file operations, async/await coverage, performance benchmarking

**Strategic Approach:**
- pytest framework (70% unit / 25% integration / 5% E2E)
- Target: 550-650 tests, 85%+ overall coverage
- Textual test harness for TUI validation
- Hypothesis for property-based testing

---

## 1. Test Pyramid

```
         /\
        /  \  5%     E2E Tests (27-32 tests)
       /----\
      / 25%  \      Integration Tests (138-163 tests)
    /----------\
   /   70%      \   Unit Tests (385-455 tests)
 /----------------\
```

**Coverage Targets:**
- Critical Components (>90%): dependency_resolver.py, installer.py, catalog_loader.py
- High-Priority (>85%): category_engine.py, search_engine.py
- TUI Components (>75%): browser.py, widgets.py
- Overall: >85%

---

## 2. Python Testing Ecosystem

### 2.1 Core Tools

```yaml
pytest-cov: Coverage reporting
pytest-asyncio: Async/await testing
pytest-mock: Mocking utilities
pytest-benchmark: Performance testing
pytest-xdist: Parallel execution
hypothesis: Property-based testing
```

### 2.2 Quick Examples

**pytest fixture:**
```python
def test_load_valid_yaml(catalog_loader):
    result = catalog_loader.load("test.yaml")
    assert len(result) == 331
```

**Textual TUI testing:**
```python
@pytest.mark.asyncio
async def test_browser_navigation():
    app = BrowserApp()
    async with app.run_test() as pilot:
        await pilot.press("down", "down", "enter")
        assert app.selected_index == 2
```

**Property-based:**
```python
@given(st.lists(st.text(min_size=1), max_size=1000))
def test_resolver_never_crashes(resource_list):
    resolver = DependencyResolver()
    try:
        result = resolver.resolve(resource_list)
        assert isinstance(result, list)
    except (CyclicDependencyError, MissingDependencyError):
        pass
```

---

## 3. Project Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # 70%
├── integration/             # 25%
├── e2e/                     # 5%
├── fixtures/
└── benchmarks/
```

---

## 4. Test Scenarios

### 4.1 Catalog Loader (85-105 tests)

**Happy Path:**
- Load 331 resources from index.yaml
- Parse all resource types (agent, command, hook, template, mcp)
- Build O(1) lookup index

**Error Handling:**
- File not found, malformed YAML, missing required fields
- Invalid resource types, duplicate IDs
- Permission denied, empty catalog

**Edge Cases:**
- Unicode handling, 10k+ resources, deep nesting
- Mixed line endings, trailing whitespace
- Symlinked directories, relative/absolute paths

**Benchmarks:**
- Load index: <10ms
- Load 331 resources: <200ms cold, <50ms warm
- ID lookup: <1ms

### 4.2 Dependency Resolver (110-130 tests)

**Core Algorithm:**
- No dependencies, linear chains, diamond patterns
- Topological sorting, parallel installation levels

**Cycle Detection:**
- Simple cycles (A→B→A)
- Deep cycles (A→B→C→D→B)
- Self-references

**Edge Cases:**
- 100+ levels deep
- Missing dependencies
- Property-based fuzzing

### 4.3 Category Engine (65-85 tests)

**Prefix Extraction:**
- Single category: "database-postgres" → "database"
- Multi-level: "test-integration-api" → "test"/"integration"

**Tree Building:**
- 30+ categories from 331 resources
- Orphan handling

### 4.4 Installer (85-105 tests)

**Basic Operations:**
- Install single resource
- Install with dependencies
- Atomic writes with rollback

**Error Handling:**
- Network failures
- Disk full
- Permission errors
- Checksum mismatches

**Concurrency:**
- Parallel downloads
- Race condition prevention

### 4.5 TUI Components (70-90 tests)

**Browser App:**
- Load catalog (331 resources)
- Keyboard navigation
- Search filtering
- Selection and installation

**Widgets:**
- ResourceTable rendering
- PreviewPane markdown
- CategoryTree expansion

### 4.6 Search Engine (65-85 tests)

**Exact Search:**
- O(1) hash lookup
- Case-insensitive matching

**Fuzzy Search:**
- Typo handling
- Ranking algorithm
- <20ms for 331 resources

---

## 5. Integration Tests (138-163 tests)

**Key Flows:**
- Catalog → Installer
- TUI → Business Logic
- Dependency Resolver → Installer
- Search Engine → Browser

---

## 6. E2E Tests (27-32 tests)

**Critical User Journeys:**
- Browse → Search → Install
- Install with dependency resolution
- Multi-select batch installation
- Error recovery workflows

---

## 7. Performance Benchmarks

**Targets:**
- Cold start: <100ms
- Catalog load: <200ms (331 resources)
- Exact search: <10ms
- Fuzzy search: <20ms
- Memory: <100MB
- Scale test: 10k resources in <2s

---

## 8. CI/CD Integration

**GitHub Actions Matrix:**
```yaml
os: [ubuntu, macos, windows]
python: ['3.9', '3.10', '3.11', '3.12']
```

**tox Configuration:**
```ini
envlist = py39,py310,py311,py312,lint,type
```

**Commands:**
```bash
# Development
pytest tests/unit/ -v
pytest --cov=src/crm

# Parallel
pytest -n auto

# Benchmarks
pytest -m benchmark --benchmark-only

# Pre-commit
pytest -x && ruff check && mypy src/
```

---

## 9. Quality Gates

**Required Before Merge:**
- [ ] All tests pass (550+ tests)
- [ ] Coverage ≥85% overall
- [ ] Critical components ≥90%
- [ ] mypy strict mode passes
- [ ] All benchmarks meet targets

**Performance Gates:**
- [ ] Cold start <100ms
- [ ] Exact search <10ms
- [ ] Fuzzy search <20ms
- [ ] Memory <100MB

---

## Document Status

**Status:** ✅ Complete
**Test Count:** 550-650 tests
**Coverage Target:** 85%+
**Ready for:** Implementation phase
