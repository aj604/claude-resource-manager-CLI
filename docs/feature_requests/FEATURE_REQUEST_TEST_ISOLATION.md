# Feature Request: Implement Test Isolation for User Preferences in TUI Tests

## Summary

Tests in the TUI test suite are currently non-deterministic because they read from developers' actual user configuration files (`~/.config/claude-resources/settings.json`). This violates test isolation principles and causes tests to fail inconsistently across different development environments.

**Status**: Blocking 1 of 20 CI test failures
**Priority**: Medium (Developer Experience)
**Component**: Testing Infrastructure
**Affects**: `tests/unit/tui/test_advanced_ui.py` and all tests using `BrowserScreen`

---

## Problem Statement

### Current Behavior

The `BrowserScreen` class loads user preferences from the filesystem during initialization (line 112 in `browser_screen.py`):

```python
def __init__(self, catalog_loader=None, search_engine=None):
    # ... initialization code ...
    self._load_preferences()  # Reads from ~/.config/claude-resources/settings.json
```

The `_load_preferences()` method (lines 901-926) reads from the developer's actual home directory:

```python
def _load_preferences(self) -> None:
    """Load user preferences from config file."""
    try:
        config_path = Path.home() / ".config" / "claude-resources" / "settings.json"

        if config_path.exists():
            with open(config_path, "r") as f:
                prefs = json.load(f)

            # Load sort preferences
            self._sort_field = prefs.get("sort_field", "name")
            self._sort_reverse = not prefs.get("sort_ascending", True)
            # ... more preference loading ...
```

### Failing Test Case

**Test**: `tests/unit/tui/test_advanced_ui.py::TestSortingFeatures::test_WHEN_sort_by_name_THEN_orders_alphabetically`

**Test Code** (lines 337-377):
```python
@pytest.mark.asyncio
async def test_WHEN_sort_by_name_THEN_orders_alphabetically(self, sample_resources):
    """Sorting by name MUST order resources A-Z."""
    loader = AsyncMock()
    loader.load_resources.return_value = sample_resources

    app = AdvancedUITestApp(catalog_loader=loader)

    async with app.run_test() as pilot:
        await pilot.pause()
        browser = app.screen

        # This call fails if user's config already has sort_field="name"
        await browser.sort_by("name")

        # Expects ascending order
        names = [r.get("name", r.get("id", "")).lower() for r in browser.filtered_resources]
        assert names == sorted(names), "Resources not sorted alphabetically"
        assert getattr(browser, '_sort_reverse', False) == False, "Should be ascending by default"
```

### Root Cause Analysis

1. **Preferences loaded from user's home directory** during `BrowserScreen.__init__()` (line 112)
2. **If user previously sorted by "name"**, their config file contains: `{"sort_field": "name", "sort_ascending": true}`
3. **Test calls `browser.sort_by("name")`** expecting it to sort ascending
4. **Toggle logic activates** (lines 734-735 in `sort_by()` method):
   ```python
   if current_sort_field == field:
       self._sort_reverse = not current_sort_reverse  # Toggles to descending!
   ```
5. **Resources sorted in reverse order** (Z to A instead of A to Z)
6. **Test assertion fails**

### Debug Evidence

Console output showing the issue:
```
[DEBUG] Before sort: ['Zebra Agent', 'Alpha Agent', 'Beta MCP', 'Gamma Hook']
[DEBUG] _sort_reverse = True  # Should be False for first sort!
[DEBUG] After sort: ['Zebra Agent', 'Gamma Hook', 'Beta MCP', 'Alpha Agent']

AssertionError: Resources not sorted alphabetically:
['zebra agent', 'gamma hook', 'beta mcp', 'alpha agent'] !=
['alpha agent', 'beta mcp', 'gamma hook', 'zebra agent']
```

### Impact

**Severity**: Medium
- Tests are **non-deterministic** (pass/fail depends on invisible developer state)
- **Violates test isolation principle** (tests should not depend on external state)
- **Difficult to debug** (failure cause is not obvious from test code)
- **Wastes developer time** debugging environment-specific failures
- **Blocks CI/CD** if GitHub Actions runner has different state than local environment

**Scope**: Affects multiple test scenarios
- All tests that invoke `BrowserScreen.sort_by()`
- Tests that interact with preview pane visibility
- Tests that verify filter preferences
- Any test that instantiates `BrowserScreen` and expects clean state

---

## User Story

**As a** developer working on the claude-resource-manager-CLI project
**I want** tests to be isolated from my local user configuration
**So that** tests pass consistently regardless of my personal preferences
**And** I can trust that test failures indicate real bugs, not environment differences

### Acceptance Criteria

- [ ] All TUI tests use isolated configuration directories (not `~/.config/claude-resources/`)
- [ ] Tests do not read from or write to developers' actual user preferences
- [ ] Tests are deterministic and produce identical results across all development environments
- [ ] Test setup and teardown properly manage temporary configuration state
- [ ] Documentation explains the test isolation pattern for future test authors
- [ ] Existing tests pass consistently on all developer machines and CI runners

---

## Proposed Solutions

### Option 1: Mock Home Directory in Tests (Recommended)

**Approach**: Use `pytest` fixtures with `unittest.mock.patch` to redirect `Path.home()` to a temporary directory.

**Implementation**:

```python
import pytest
from unittest.mock import patch
from pathlib import Path

@pytest.fixture
def isolated_config(tmp_path):
    """Isolate user config to temporary directory for test."""
    with patch("pathlib.Path.home", return_value=tmp_path):
        yield tmp_path

@pytest.mark.asyncio
async def test_WHEN_sort_by_name_THEN_orders_alphabetically(
    self, sample_resources, isolated_config
):
    """Sorting by name MUST order resources A-Z."""
    loader = AsyncMock()
    loader.load_resources.return_value = sample_resources

    # BrowserScreen now reads from tmp_path instead of ~/
    app = AdvancedUITestApp(catalog_loader=loader)

    async with app.run_test() as pilot:
        await pilot.pause()
        browser = app.screen

        # Now guaranteed to start with clean state
        await browser.sort_by("name")

        names = [r.get("name", r.get("id", "")).lower() for r in browser.filtered_resources]
        assert names == sorted(names)
```

**Advantages**:
- Complete test isolation from user environment
- Works consistently across all machines and CI/CD systems
- No production code changes required
- Can be implemented as reusable pytest fixture
- Tests real preference loading logic (not mocked)

**Disadvantages**:
- Requires adding fixture to all affected tests
- Must patch at the right scope (module-level import might cache `Path.home()`)
- Slightly more complex test setup

**Estimated Effort**: 2-4 hours
- Create `isolated_config` fixture in `tests/conftest.py`
- Update affected tests to use fixture
- Verify all tests pass consistently

---

### Option 2: Reset State Before Assertions (Quick Fix)

**Approach**: Manually reset `BrowserScreen` internal state before calling methods under test.

**Implementation**:

```python
@pytest.mark.asyncio
async def test_WHEN_sort_by_name_THEN_orders_alphabetically(self, sample_resources):
    """Sorting by name MUST order resources A-Z."""
    loader = AsyncMock()
    loader.load_resources.return_value = sample_resources

    app = AdvancedUITestApp(catalog_loader=loader)

    async with app.run_test() as pilot:
        await pilot.pause()
        browser = app.screen

        # Reset state to ensure clean starting point
        browser._sort_field = None
        browser._sort_reverse = False

        await browser.sort_by("name")

        names = [r.get("name", r.get("id", "")).lower() for r in browser.filtered_resources]
        assert names == sorted(names)
```

**Advantages**:
- Simple, immediate fix
- No test infrastructure changes needed
- Minimal code changes per test

**Disadvantages**:
- Brittle (relies on knowing internal implementation details)
- Must be repeated in every test
- Easy to forget when writing new tests
- Doesn't solve the root problem (still reads from user config)
- Violates encapsulation (tests shouldn't manipulate private attributes)

**Estimated Effort**: 30 minutes
- Add state reset to failing test
- Document pattern for future tests

---

### Option 3: Dependency Injection for Preferences Loader (Architectural)

**Approach**: Refactor `BrowserScreen` to accept a preferences loader as a dependency, allowing tests to inject a mock.

**Implementation**:

```python
# New preferences loader abstraction
class PreferencesLoader:
    """Loads user preferences from filesystem."""

    def load(self) -> dict:
        """Load preferences from config file."""
        config_path = Path.home() / ".config" / "claude-resources" / "settings.json"

        if config_path.exists():
            with open(config_path, "r") as f:
                return json.load(f)

        return {}

class MockPreferencesLoader(PreferencesLoader):
    """Mock preferences loader for tests."""

    def load(self) -> dict:
        """Return empty preferences."""
        return {}

# Updated BrowserScreen
class BrowserScreen(Screen):
    def __init__(
        self,
        catalog_loader=None,
        search_engine=None,
        preferences_loader=None  # New parameter
    ):
        # ...
        self.preferences_loader = preferences_loader or PreferencesLoader()
        self._load_preferences()

    def _load_preferences(self) -> None:
        """Load user preferences."""
        prefs = self.preferences_loader.load()
        self._sort_field = prefs.get("sort_field", "name")
        # ... rest of preference loading

# Test usage
@pytest.mark.asyncio
async def test_WHEN_sort_by_name_THEN_orders_alphabetically(self, sample_resources):
    """Sorting by name MUST order resources A-Z."""
    loader = AsyncMock()
    loader.load_resources.return_value = sample_resources

    app = AdvancedUITestApp(
        catalog_loader=loader,
        preferences_loader=MockPreferencesLoader()  # Inject clean preferences
    )

    async with app.run_test() as pilot:
        await pilot.pause()
        browser = app.screen

        await browser.sort_by("name")

        names = [r.get("name", r.get("id", "")).lower() for r in browser.filtered_resources]
        assert names == sorted(names)
```

**Advantages**:
- Follows SOLID principles (Dependency Inversion)
- Makes preferences loading easily testable
- Enables future flexibility (e.g., different config sources)
- Clear separation of concerns
- Easy to understand and maintain

**Disadvantages**:
- Requires refactoring production code
- More complex change with wider impact
- Need to update `AdvancedUITestApp` and other test utilities
- Adds new classes and abstractions

**Estimated Effort**: 4-8 hours
- Design and implement `PreferencesLoader` abstraction
- Refactor `BrowserScreen` to accept dependency
- Update all tests and test utilities
- Verify backward compatibility

---

## Recommended Implementation Plan

### Phase 1: Immediate Fix (Unblock CI)
**Timeline**: Same day
**Approach**: Use Option 2 (Reset State)

1. Add state reset to failing test: `test_WHEN_sort_by_name_THEN_orders_alphabetically`
2. Verify test passes consistently
3. Document the workaround with `TODO` comment linking to this feature request

```python
# TODO: Replace with proper test isolation (see docs/feature_requests/FEATURE_REQUEST_TEST_ISOLATION.md)
browser._sort_field = None
browser._sort_reverse = False
```

### Phase 2: Proper Test Isolation (Short-term)
**Timeline**: Within 1 week
**Approach**: Use Option 1 (Mock Home Directory)

1. Create `isolated_config` fixture in `tests/conftest.py`:
   ```python
   @pytest.fixture
   def isolated_config(tmp_path):
       """Isolate user config to temporary directory."""
       with patch("pathlib.Path.home", return_value=tmp_path):
           yield tmp_path
   ```

2. Update affected test classes to use fixture:
   - `TestSortingFeatures`
   - `TestPreviewPane` (if exists)
   - `TestFilterPreferences` (if exists)

3. Add documentation to `tests/README.md` explaining the pattern

4. Run full test suite to verify consistency

### Phase 3: Architectural Improvement (Optional, Long-term)
**Timeline**: Future refactoring cycle
**Approach**: Option 3 (Dependency Injection)

Consider implementing during a larger refactoring effort when:
- Adding configuration features
- Implementing multi-profile support
- Refactoring for better testability across the codebase

---

## Testing Strategy

### Verification Steps

1. **Local Verification**:
   ```bash
   # Run test with fresh config
   rm -rf ~/.config/claude-resources/settings.json
   .venv/bin/pytest tests/unit/tui/test_advanced_ui.py::TestSortingFeatures::test_WHEN_sort_by_name_THEN_orders_alphabetically -v

   # Run test with existing config (sort_field="name")
   echo '{"sort_field": "name", "sort_ascending": true}' > ~/.config/claude-resources/settings.json
   .venv/bin/pytest tests/unit/tui/test_advanced_ui.py::TestSortingFeatures::test_WHEN_sort_by_name_THEN_orders_alphabetically -v

   # Both should pass
   ```

2. **CI Verification**:
   - Tests must pass in GitHub Actions
   - Add test matrix with different Python versions
   - Verify on different OS runners (Ubuntu, macOS, Windows)

3. **Regression Prevention**:
   - Add test that verifies isolation (e.g., create preferences file in tmp_path, verify it's used)
   - Add documentation for test authors about preference isolation pattern

### Success Metrics

- [ ] Test passes 100% of the time on all developer machines
- [ ] Test passes 100% of the time in CI/CD
- [ ] Test execution time not significantly impacted (< 5ms overhead)
- [ ] Zero flaky test reports related to preferences

---

## Related Issues

### Potential Related Tests

Other tests that may have similar issues (require investigation):

- `test_WHEN_sort_toggled_THEN_reverses_order` - Also tests sort behavior
- Any test using preview pane visibility
- Any test checking filter state persistence

### Technical Debt

This issue reveals a broader pattern that should be addressed:

1. **Filesystem dependencies in tests**: Tests should mock or isolate all filesystem access
2. **Test fixtures for state management**: Need shared fixtures for common test setup
3. **Documentation gaps**: Missing guidance on writing isolated tests

---

## References

### Files Involved

**Source Code**:
- `/Users/averyjones/Repos/claude/claude-resource-manager-CLI/src/claude_resource_manager/tui/screens/browser_screen.py`
  - Line 112: `self._load_preferences()` call in `__init__`
  - Lines 901-926: `_load_preferences()` implementation
  - Lines 710-771: `sort_by()` method with toggle logic

**Test Code**:
- `/Users/averyjones/Repos/claude/claude-resource-manager-CLI/tests/unit/tui/test_advanced_ui.py`
  - Lines 337-377: `test_WHEN_sort_by_name_THEN_orders_alphabetically`

**Configuration**:
- User preferences stored at: `~/.config/claude-resources/settings.json`

### Best Practices

- [pytest fixtures documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Test isolation principles](https://en.wikipedia.org/wiki/Test_isolation)

---

## Appendix: Debug Session Output

### Test Failure with User Preferences Present

```bash
$ cat ~/.config/claude-resources/settings.json
{"sort_field": "name", "sort_ascending": true}

$ .venv/bin/pytest tests/unit/tui/test_advanced_ui.py::TestSortingFeatures::test_WHEN_sort_by_name_THEN_orders_alphabetically -v

================================ test session starts =================================
tests/unit/tui/test_advanced_ui.py::TestSortingFeatures::test_WHEN_sort_by_name_THEN_orders_alphabetically FAILED

================================== FAILURES ==========================================
______ TestSortingFeatures.test_WHEN_sort_by_name_THEN_orders_alphabetically ________

[DEBUG] Before sort: ['Zebra Agent', 'Alpha Agent', 'Beta MCP', 'Gamma Hook']
[DEBUG] _sort_reverse = True
[DEBUG] After sort: ['Zebra Agent', 'Gamma Hook', 'Beta MCP', 'Alpha Agent']

    assert names == sorted(names), f"Resources not sorted alphabetically: {names} != {sorted(names)}"
E   AssertionError: Resources not sorted alphabetically:
E   ['zebra agent', 'gamma hook', 'beta mcp', 'alpha agent'] !=
E   ['alpha agent', 'beta mcp', 'gamma hook', 'zebra agent']
```

### Expected Behavior (Clean Environment)

```bash
$ rm ~/.config/claude-resources/settings.json

$ .venv/bin/pytest tests/unit/tui/test_advanced_ui.py::TestSortingFeatures::test_WHEN_sort_by_name_THEN_orders_alphabetically -v

================================ test session starts =================================
tests/unit/tui/test_advanced_ui.py::TestSortingFeatures::test_WHEN_sort_by_name_THEN_orders_alphabetically PASSED

[DEBUG] Before sort: ['Zebra Agent', 'Alpha Agent', 'Beta MCP', 'Gamma Hook']
[DEBUG] _sort_reverse = False
[DEBUG] After sort: ['Alpha Agent', 'Beta MCP', 'Gamma Hook', 'Zebra Agent']
```

---

## Questions and Answers

**Q: Why not just document that developers should delete their config before running tests?**
A: This violates the principle of test isolation and creates a poor developer experience. Tests should work regardless of local environment state. Requiring manual setup steps is error-prone and slows down development.

**Q: Could we use environment variables to control preference loading?**
A: Yes, but this is more complex than mocking `Path.home()` and still requires test-specific setup. Environment variables can leak between tests if not carefully managed.

**Q: Should we disable preference loading entirely in tests?**
A: No, we want to test that preference loading works correctly. We just need to control where preferences are loaded from (temporary directory instead of user's home).

**Q: Will this affect performance of the test suite?**
A: No, creating temporary directories and patching `Path.home()` has negligible overhead (< 1ms per test). The benefit of deterministic tests far outweighs any minimal performance impact.

---

**Priority**: Medium
**Component**: Testing Infrastructure
**Labels**: `testing`, `technical-debt`, `developer-experience`, `bug`
**Milestone**: Phase 2 - Test Suite Stability
