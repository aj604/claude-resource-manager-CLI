# Before/After: Implementation-Specific vs Behavior-Focused Tests

## The Problem with Implementation-Specific Tests

When tests are tightly coupled to implementation details (keypresses, UI structure, internal state), they break every time the UX improves. This creates a disincentive to improve the user experience.

## Example 1: Basic Sorting

### ❌ BEFORE: Implementation-Specific (Brittle)
```python
def test_WHEN_s_then_1_THEN_sorts_by_name():
    """Test sorting via menu selection."""
    app.press("s")       # Open sort menu
    app.press("1")       # Select option 1 (name)
    
    # Check table rows directly
    assert app.table.rows[0].cells[1] < app.table.rows[1].cells[1]
```

**Problems:**
- Hardcoded to specific keypresses ("s", "1")
- Breaks if we change from menu to cycling
- Breaks if we change menu order
- Accessing internal table structure
- Unclear what "option 1" means
- Tests HOW, not WHAT

### ✅ AFTER: Behavior-Focused (Resilient)
```python
async def test_WHEN_sort_by_name_triggered_THEN_resources_alphabetically_ordered(
    self, sample_resources
):
    """Triggering name sort MUST result in alphabetically ordered resources."""
    # Arrange
    loader = AsyncMock()
    loader.load_resources.return_value = sample_resources
    app = AdvancedUITestApp(catalog_loader=loader)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Act - Abstract trigger (implementation-agnostic)
        await TUITestHelper.trigger_sort_by_name(pilot)
        await pilot.pause()

        # Assert - Observable outcome (behavior-focused)
        browser = app.screen
        TUITestHelper.assert_sorted_by_name(browser.filtered_resources)
```

**Benefits:**
- Tests WHAT (alphabetical ordering)
- Survives UX changes (menu → cycling → shortcuts)
- Clear intent from name
- Readable assertions
- No internal state access

**UX Changes This Test Survives:**
- ✅ Menu-based sorting
- ✅ One-key cycling (current)
- ✅ Multi-key shortcuts (Ctrl+Shift+S)
- ✅ Command palette ("Sort by name")
- ✅ Click column headers
- ✅ Drag-drop column reordering

## Example 2: Sort Reversal

### ❌ BEFORE: Implementation-Specific
```python
def test_WHEN_s_pressed_twice_THEN_reverses():
    """Test sort reversal."""
    app.press("s")       # Sort ascending
    app.press("s")       # Toggle to descending
    
    # Index-based assertion
    assert app.resources[-1].name < app.resources[0].name
```

**Problems:**
- Assumes "s" twice = reversal
- Breaks if reversal requires different key
- Index-based access is fragile
- Doesn't test the actual reversal, just end state
- No clear indication of what's being tested

### ✅ AFTER: Behavior-Focused
```python
async def test_WHEN_sort_reversed_THEN_order_inverted(self, sample_resources):
    """Reversing sort MUST invert the current order."""
    # Arrange
    loader = AsyncMock()
    loader.load_resources.return_value = sample_resources
    app = AdvancedUITestApp(catalog_loader=loader)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Act - Explicit state capture
        await TUITestHelper.trigger_sort_by_name(pilot)
        await pilot.pause()
        ascending_names = TUITestHelper.get_visible_resource_names(app)
        
        await TUITestHelper.trigger_reverse_sort(pilot)
        await pilot.pause()
        descending_names = TUITestHelper.get_visible_resource_names(app)

        # Assert - Explicit reversal check
        assert descending_names == list(reversed(ascending_names)), (
            "Sort reversal did not invert order"
        )
```

**Benefits:**
- Explicitly tests reversal behavior
- Captures before/after state
- Works with any reversal mechanism
- Clear error messages
- No assumptions about implementation

## Example 3: Sort + Filter Interaction

### ❌ BEFORE: Implementation-Specific
```python
def test_sort_with_filter():
    """Test sorting filtered results."""
    # Click specific UI element
    app.click("#filter-agent")
    
    # Hardcoded menu navigation
    app.press("s")
    app.press("1")
    
    # Internal state check
    assert app.screen._filtered_resources[0].type == "agent"
    assert app.screen._sort_field == "name"
```

**Problems:**
- Coupled to specific CSS selector (#filter-agent)
- Hardcoded keypresses
- Accessing private attributes (_filtered_resources)
- Doesn't verify the actual user-visible outcome
- Tests internal state, not behavior

### ✅ AFTER: Behavior-Focused
```python
async def test_WHEN_sort_applied_with_filter_THEN_only_filtered_resources_sorted(
    self, sample_resources
):
    """Sort MUST only affect visible (filtered) resources."""
    # Arrange
    loader = AsyncMock()
    loader.load_resources.return_value = sample_resources
    app = AdvancedUITestApp(catalog_loader=loader)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Act - Domain methods, not UI manipulation
        await app.screen.filter_by_type("agent")
        await pilot.pause()
        
        await TUITestHelper.trigger_sort_by_name(pilot)
        await pilot.pause()

        # Assert - Observable outcomes
        browser = app.screen
        types = TUITestHelper.get_visible_resource_types(app)
        assert all(t == "agent" for t in types), "Filter not applied"
        
        TUITestHelper.assert_sorted_by_name(browser.filtered_resources)
```

**Benefits:**
- Uses domain methods (filter_by_type)
- Tests both filter AND sort (interaction)
- Observable properties (what user sees)
- No private attribute access
- Clear, separate assertions

## Example 4: Sort Persistence

### ❌ BEFORE: Implementation-Specific
```python
def test_sort_persists():
    """Test sort state persistence."""
    app.press("s")
    app.press("2")  # Sort by type
    
    # Trigger search
    app.input("#search").value = "test"
    app.press("enter")
    
    # Check internal state
    assert app.screen._sort_field == "type"
```

**Problems:**
- Hardcoded menu navigation ("2" = type)
- Hardcoded CSS selector (#search)
- Simulating Enter keypress
- Checking private state
- Doesn't verify sort is actually applied

### ✅ AFTER: Behavior-Focused
```python
async def test_WHEN_sort_applied_THEN_state_persists_after_search_clear(
    self, sample_resources
):
    """Sort state MUST persist when search is cleared."""
    # Arrange
    loader = AsyncMock()
    loader.load_resources.return_value = sample_resources
    app = AdvancedUITestApp(catalog_loader=loader)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Act - Clear lifecycle: sort → search → clear
        await TUITestHelper.trigger_sort_by_type(pilot)
        await pilot.pause()
        
        await app.screen.perform_search("test")
        await pilot.pause()
        
        await app.screen.perform_search("")  # Clear search
        await pilot.pause()

        # Assert - Both indicator and actual state
        TUITestHelper.assert_sort_indicator_shows(app, "type")
        browser = app.screen
        TUITestHelper.assert_sorted_by_type(browser.filtered_resources)
```

**Benefits:**
- Tests complete lifecycle
- Domain methods (perform_search)
- Verifies both UI feedback and actual sorting
- No private state access
- Tests observable user experience

## Key Principles

### 1. Test WHAT, Not HOW
- ❌ "Press 's', then '1'"
- ✅ "Resources are alphabetically ordered"

### 2. Abstract Triggers
- ❌ `app.press("s"); app.press("1")`
- ✅ `TUITestHelper.trigger_sort_by_name(pilot)`

### 3. Abstract Assertions
- ❌ `assert app.table.rows[0].cells[1] < app.table.rows[1].cells[1]`
- ✅ `TUITestHelper.assert_sorted_by_name(resources)`

### 4. Use Domain Language
- ❌ `app.click("#filter-agent")`
- ✅ `app.screen.filter_by_type("agent")`

### 5. Test Observable Outcomes
- ❌ `assert app.screen._sort_field == "name"`
- ✅ `TUITestHelper.assert_sorted_by_name(browser.filtered_resources)`

### 6. Capture State Explicitly
- ❌ Implicit before/after comparison
- ✅ `before = get_names(); action(); after = get_names(); assert after == sorted(before)`

## Impact on Development

### With Implementation-Specific Tests
1. Improve UX (menu → cycling)
2. 15 tests break
3. Spend hours rewriting tests
4. Delay or skip UX improvement

**Result:** UX stagnates

### With Behavior-Focused Tests
1. Improve UX (menu → cycling)
2. Update 5 trigger helpers in `tui_helpers.py`
3. All 15 tests still pass
4. Ship UX improvement confidently

**Result:** Continuous UX improvement

## Migration Checklist

When refactoring tests from implementation-specific to behavior-focused:

- [ ] Remove hardcoded keypresses
- [ ] Remove CSS selector dependencies
- [ ] Remove private attribute access (_field, _state)
- [ ] Remove index-based assertions (rows[0])
- [ ] Create trigger helper for action
- [ ] Create assertion helper for outcome
- [ ] Use domain methods (filter_by_type, not click)
- [ ] Test observable properties (what user sees)
- [ ] Rename test to describe WHAT, not HOW
- [ ] Add docstring explaining behavior
- [ ] Capture before/after state explicitly
- [ ] Verify test would survive UX changes

## Conclusion

Behavior-focused tests:
- ✅ Survive UX improvements
- ✅ Serve as living documentation
- ✅ Focus on user outcomes
- ✅ Enable fearless refactoring
- ✅ Reduce test maintenance burden

Implementation-specific tests:
- ❌ Break on UX changes
- ❌ Obscure intent with mechanics
- ❌ Couple to internal structure
- ❌ Create fear of improving UX
- ❌ High maintenance burden

**Choose behavior-focused tests to enable continuous UX improvement.**
