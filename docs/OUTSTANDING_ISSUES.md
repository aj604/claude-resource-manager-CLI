# Outstanding Issues - Phase 3 Accessibility Integration

**Document Version:** 1.0
**Last Updated:** 2025-10-05
**Current Status:** 21/36 tests passing (58% complete)
**Target:** 36/36 tests passing (100% WCAG 2.1 AA compliance)

---

## Executive Summary

The Phase 3 Accessibility Integration has successfully implemented core infrastructure including ARIA live regions, screen reader announcements, and WCAG-compliant color themes. **58% of tests are now passing (21/36)**, up from the initial 30% baseline.

**Critical blockers:** None. All infrastructure is in place.

**Remaining work:** Integration of existing accessibility components into screen workflows (15 failing tests, estimated 12-16 hours).

---

## Test Status Overview

| Category | Passing | Failing | Completion |
|----------|---------|---------|------------|
| **Helper Functions** | 11/11 | 0 | 100% ✅ |
| **Selection Announcements** | 2/2 | 0 | 100% ✅ |
| **Keyboard Navigation** | 4/6 | 2 | 67% 🟡 |
| **Color Contrast** | 4/7 | 3 | 57% 🟡 |
| **Screen Reader Events** | 0/6 | 6 | 0% 🔴 |
| **Error Recovery** | 0/4 | 4 | 0% 🔴 |
| **TOTAL** | **21/36** | **15** | **58%** |

---

## Outstanding Issues by Category

### 1. Screen Reader Announcements (6 failing tests)

**Status:** Infrastructure exists but not integrated into screen workflows

#### Issue 1.1: Search Result Announcements
- **Test:** `test_WHEN_search_updates_THEN_count_announced`
- **Impact:** High - Screen reader users don't know how many results match their search
- **Estimated Effort:** 1 hour
- **Root Cause:** `on_input_changed` in BrowserScreen doesn't call screen reader announcer
- **Fix:**
  ```python
  # File: src/claude_resource_manager/tui/screens/browser_screen.py
  # In: async def on_input_changed(self, event: Input.Changed)

  # After perform_search, add:
  if self.screen_reader and event.input.id == "search-input":
      count = len(self.filtered_resources)
      query = event.value
      if query.strip():
          self.screen_reader.announce(f"Found {count} resources matching '{query}'")
  ```

#### Issue 1.2: Category Filter Announcements
- **Test:** `test_WHEN_category_changed_THEN_category_announced`
- **Impact:** High - Users don't know when category filters are applied
- **Estimated Effort:** 1 hour
- **Root Cause:** `filter_by_type` method doesn't announce filter changes
- **Fix:**
  ```python
  # File: src/claude_resource_manager/tui/screens/browser_screen.py
  # In: async def filter_by_type(self, resource_type: str)

  # After updating filtered_resources, add:
  if self.screen_reader:
      count = len(self.filtered_resources)
      category_label = resource_type.capitalize() + "s" if resource_type != "all" else "All resources"
      self.screen_reader.announce(f"Filtered to: {category_label} ({count} items)")
  ```

#### Issue 1.3: Sort Order Announcements
- **Test:** `test_WHEN_sort_changed_THEN_sort_order_announced`
- **Impact:** Medium - Users can't tell which sort is active
- **Estimated Effort:** 1 hour
- **Root Cause:** `sort_by` method doesn't announce sort changes
- **Fix:**
  ```python
  # File: src/claude_resource_manager/tui/screens/browser_screen.py
  # In: async def sort_by(self, field: str)

  # After sorting, add:
  if self.screen_reader:
      direction = "descending" if self._sort_reverse else "ascending"
      self.screen_reader.announce(f"Sorted by {field}, {direction} order")
  ```

#### Issue 1.4: Error Announcements
- **Test:** `test_WHEN_error_occurs_THEN_error_announced`
- **Impact:** High - Errors are silent for screen reader users
- **Estimated Effort:** 2 hours
- **Root Cause:** Error handling doesn't use assertive ARIA announcements
- **Fix:**
  ```python
  # File: src/claude_resource_manager/tui/screens/browser_screen.py
  # In: async def on_mount(self) - exception handler

  # In except block, after showing error UI:
  if self.screen_reader:
      self.screen_reader.announce(f"Error: {str(e)}", assertive=True)
  ```

#### Issue 1.5: Batch Operation Progress
- **Test:** `test_WHEN_batch_install_starts_THEN_progress_announced`
- **Impact:** Medium - No feedback during batch operations
- **Estimated Effort:** 2 hours
- **Root Cause:** Batch install workflow not implemented with announcements
- **Fix:** Implement batch install handler with progress announcements (requires InstallPlanScreen integration)

#### Issue 1.6: Modal Open/Close Announcements
- **Test:** `test_WHEN_help_modal_opens_THEN_modal_announced`
- **Impact:** Medium - Screen reader users don't know when modals open/close
- **Estimated Effort:** 1 hour
- **Root Cause:** HelpScreen doesn't announce on mount
- **Fix:**
  ```python
  # File: src/claude_resource_manager/tui/screens/help_screen.py
  # In: def on_mount(self)

  # Add screen reader announcement:
  if hasattr(self.app, 'screen_reader') and self.app.screen_reader:
      self.app.screen_reader.announce("Help dialog opened. Press Escape to close.")
  ```

---

### 2. Color Contrast (3 failing tests)

**Status:** Theme file exists but not registered with Textual app

#### Issue 2.1: Light Theme Normal Text
- **Test:** `test_WHEN_light_theme_THEN_normal_text_contrast_4_5_to_1`
- **Impact:** High - WCAG AA compliance failure
- **Estimated Effort:** 3 hours
- **Root Cause:** ThemeManager.get_theme_colors() method doesn't exist in app.py
- **Current Code:**
  ```python
  # Line 203 in app.py:
  self.theme_manager = ThemeManager()
  self.color_scheme = self.theme_manager.detect_color_scheme()
  ```
  **Problem:** `ThemeManager` class is not defined in app.py
- **Fix:**
  ```python
  # Option 1: Define ThemeManager in app.py
  class ThemeManager:
      def detect_color_scheme(self) -> str:
          # Detect from environment or terminal
          return os.getenv("TERM_THEME", "dark")

      def get_theme_colors(self, theme_name: str) -> dict:
          from claude_resource_manager.tui.theme import get_theme
          theme = get_theme(theme_name)
          return theme.colors

  # Option 2: Import from theme.py and refactor
  from claude_resource_manager.tui.theme import get_theme, THEMES

  # Then in __init__:
  self.current_theme = get_theme(self.color_scheme)
  ```

#### Issue 2.2: Selected Item Contrast
- **Test:** `test_WHEN_selected_item_THEN_contrast_meets_wcag`
- **Impact:** High - Selection highlighting not accessible
- **Estimated Effort:** 1 hour (bundled with 2.1)
- **Root Cause:** Same as 2.1 - theme colors not applied to app
- **Fix:** After fixing 2.1, theme colors will automatically apply to selections

#### Issue 2.3: 100% Theme Compliance
- **Test:** `test_WHEN_all_themes_tested_THEN_100_percent_compliance`
- **Impact:** High - Overall WCAG certification blocked
- **Estimated Effort:** 0 hours (will pass when 2.1 and 2.2 fixed)
- **Root Cause:** Cascading failure from theme registration
- **Fix:** Automatically resolved by fixing issues 2.1 and 2.2

---

### 3. Keyboard Navigation (2 failing tests)

**Status:** Partial implementation - some handlers missing

#### Issue 3.1: ESC Key Search Clearing
- **Test:** `test_WHEN_search_active_THEN_esc_clears_and_exits`
- **Impact:** Medium - Minor UX issue, workaround exists (click elsewhere)
- **Estimated Effort:** 1 hour
- **Root Cause:** `action_clear_search` doesn't check focus before clearing
- **Current Behavior:** ESC clears search but doesn't check if search has focus
- **Expected Behavior:**
  1. If search input has focus AND has text → clear text, keep focus
  2. If search input has focus AND empty → blur focus, return to table
  3. If search input doesn't have focus → do nothing
- **Fix:**
  ```python
  # File: src/claude_resource_manager/tui/screens/browser_screen.py
  # Replace: async def action_clear_search(self)

  async def action_clear_search(self) -> None:
      """Clear search and handle focus appropriately."""
      search_input = self.query_one("#search-input", Input)

      # Only act if search has focus
      if not search_input.has_focus:
          return

      if search_input.value:
          # Clear text, keep focus
          search_input.value = ""
      else:
          # Already empty, blur and return to table
          table = self.query_one("#resource-table", DataTable)
          table.focus()
  ```

#### Issue 3.2: Tab Focus Order
- **Test:** `test_WHEN_tab_pressed_THEN_focus_moves_correctly`
- **Impact:** Low - Tab key currently works, just not tested
- **Estimated Effort:** 2 hours
- **Root Cause:** Focus order verification helper returns False (not implemented)
- **Expected Focus Order:**
  1. Search input (`#search-input`)
  2. Filter buttons container (`#filter-buttons`)
  3. Resource table (`#resource-table`)
  4. Install button (`#install-selected-button` when visible)
- **Fix:**
  ```python
  # File: tests/utils/accessibility_helpers.py
  # Update: verify_focus_order function

  def verify_focus_order(app, expected_order: list) -> bool:
      try:
          screen = app.screen if hasattr(app, 'screen') else app
          # Query all widgets with can_focus=True
          focusable = [w for w in screen.query("*") if w.can_focus]
          actual_ids = [w.id for w in focusable if w.id]

          # Check if expected widgets exist in order
          expected_indices = []
          for expected_id in expected_order:
              try:
                  idx = actual_ids.index(expected_id)
                  expected_indices.append(idx)
              except ValueError:
                  return False  # Expected widget not found

          # Verify indices are in ascending order
          return expected_indices == sorted(expected_indices)
      except Exception:
          return False
  ```

---

### 4. Error Recovery (4 failing tests)

**Status:** ErrorRecoveryModal exists but not integrated

#### Issue 4.1: User-Friendly Error Messages
- **Test:** `test_WHEN_network_error_THEN_user_friendly_message`
- **Impact:** Medium - Errors show technical details
- **Estimated Effort:** 2 hours
- **Root Cause:** BrowserScreen exception handlers show raw exception text
- **Fix:**
  ```python
  # File: src/claude_resource_manager/tui/screens/browser_screen.py
  # In: async def on_mount(self) - exception handler

  # Replace:
  error_display.update(f"Error loading resources: {str(e)}")

  # With:
  from claude_resource_manager.tui.modals.error_modal import ErrorRecoveryModal
  modal = ErrorRecoveryModal(e, "loading resources")
  result = await self.app.push_screen_wait(modal)

  if result == "retry":
      # Retry loading
      await self.on_mount()
  ```

#### Issue 4.2: Retry Option
- **Test:** `test_WHEN_error_THEN_retry_option_available`
- **Impact:** Medium - No way to retry failed operations
- **Estimated Effort:** 0 hours (bundled with 4.1)
- **Root Cause:** ErrorRecoveryModal not integrated
- **Fix:** Same as 4.1 - modal already has retry button

#### Issue 4.3: Skip Option (Batch Operations)
- **Test:** `test_WHEN_error_THEN_skip_option_available`
- **Impact:** Low - Batch operations not yet implemented
- **Estimated Effort:** 3 hours
- **Root Cause:** Batch install workflow doesn't exist
- **Fix:** Implement batch install handler with error recovery
  ```python
  # File: src/claude_resource_manager/tui/screens/browser_screen.py
  # Add new method:

  async def action_batch_install(self) -> None:
      """Install all selected resources with error recovery."""
      if not self.selected_resources:
          return

      for resource_id in self.selected_resources:
          try:
              # Install resource
              await self.installer.install(resource_id)
              if self.screen_reader:
                  self.screen_reader.announce(f"Installed {resource_id}")
          except Exception as e:
              # Show error recovery modal
              modal = ErrorRecoveryModal(e, f"installing {resource_id}")
              result = await self.app.push_screen_wait(modal)

              if result == "retry":
                  # Retry this resource
                  continue  # Loop will retry
              elif result == "skip":
                  continue  # Skip to next resource
              else:  # cancel
                  break  # Stop batch operation
  ```

#### Issue 4.4: Cancel Option
- **Test:** `test_WHEN_critical_error_THEN_cancel_option_available`
- **Impact:** Low - Already handled by modal
- **Estimated Effort:** 0 hours (bundled with 4.1)
- **Root Cause:** ErrorRecoveryModal not integrated
- **Fix:** Same as 4.1 - modal already has cancel button

---

## Prioritized Action Items

### P0 - Must Fix for WCAG AA Compliance (8 hours)

These issues block WCAG 2.1 AA certification:

- [ ] **Issue 2.1** - Register theme colors with app (3h)
  - Define or import ThemeManager in app.py
  - Apply theme colors via CSS variables
  - Verify all 3 themes load correctly

- [ ] **Issue 1.1** - Search result announcements (1h)
  - Add screen reader call to `on_input_changed`

- [ ] **Issue 1.2** - Category filter announcements (1h)
  - Add screen reader call to `filter_by_type`

- [ ] **Issue 1.4** - Error announcements (2h)
  - Add assertive announcements to exception handlers

- [ ] **Issue 1.6** - Modal announcements (1h)
  - Add announcements to HelpScreen mount/dismiss

**Estimated Total:** 8 hours

---

### P1 - Important for Usability (5 hours)

These improve user experience but don't block compliance:

- [ ] **Issue 1.3** - Sort order announcements (1h)
  - Add screen reader call to `sort_by`

- [ ] **Issue 3.1** - ESC key search behavior (1h)
  - Refactor `action_clear_search` with focus checks

- [ ] **Issue 4.1** - User-friendly error messages (2h)
  - Integrate ErrorRecoveryModal into exception handlers

- [ ] **Issue 3.2** - Tab focus order verification (1h)
  - Implement focus order helper in tests

**Estimated Total:** 5 hours

---

### P2 - Nice to Have (3 hours)

These are optional enhancements:

- [ ] **Issue 1.5** - Batch operation progress (2h)
  - Implement batch install workflow

- [ ] **Issue 4.3** - Skip option for batch errors (1h)
  - Add error recovery to batch operations

**Estimated Total:** 3 hours

---

## Known Workarounds

### Workaround 1: Theme Colors
**Issue:** Theme colors not applied
**Temporary Solution:** Tests can directly import theme:
```python
from claude_resource_manager.tui.theme import get_theme
theme = get_theme("dark")
colors = theme.colors
```

### Workaround 2: Screen Reader Testing
**Issue:** Some announcements not integrated
**Temporary Solution:** Manually verify announcements using test helper:
```python
from tests.utils.accessibility_helpers import get_aria_announcement
announcement = get_aria_announcement(app)
```

### Workaround 3: Error Recovery
**Issue:** ErrorRecoveryModal not shown
**Temporary Solution:** Users can restart operation manually

---

## Implementation Recommendations

### Recommended Order

**Week 1 - WCAG Compliance (8 hours)**
1. Fix theme registration (Issue 2.1) - 3h
2. Add search announcements (Issue 1.1) - 1h
3. Add category announcements (Issue 1.2) - 1h
4. Add error announcements (Issue 1.4) - 2h
5. Add modal announcements (Issue 1.6) - 1h

**Expected Result:** 30/36 tests passing (83% → WCAG AA compliant)

**Week 2 - UX Polish (5 hours)**
1. Add sort announcements (Issue 1.3) - 1h
2. Fix ESC search behavior (Issue 3.1) - 1h
3. Integrate error modal (Issue 4.1) - 2h
4. Fix focus order test (Issue 3.2) - 1h

**Expected Result:** 34/36 tests passing (94%)

**Week 3 - Optional Features (3 hours)**
1. Batch install workflow (Issue 1.5, 4.3) - 3h

**Expected Result:** 36/36 tests passing (100%)

---

## File Paths for Fixes

### Files to Modify

1. **`src/claude_resource_manager/tui/app.py`**
   - Add/import ThemeManager class
   - Register theme colors with Textual
   - Lines to modify: 203-204

2. **`src/claude_resource_manager/tui/screens/browser_screen.py`**
   - Add screen reader announcements (search, category, sort, errors)
   - Integrate ErrorRecoveryModal
   - Refactor ESC key handling
   - Lines to modify: 636-638 (search), 472-507 (filter), 736-791 (sort), 207-221 (errors)

3. **`src/claude_resource_manager/tui/screens/help_screen.py`**
   - Add modal announcements on mount/dismiss
   - Lines to modify: on_mount method (~line 50)

4. **`tests/utils/accessibility_helpers.py`**
   - Implement focus order verification
   - Lines to modify: 153-176 (verify_focus_order function)

### Files Already Complete

- ✅ `src/claude_resource_manager/tui/theme.py` - All 3 themes WCAG compliant
- ✅ `src/claude_resource_manager/tui/widgets/aria_live.py` - ARIA infrastructure ready
- ✅ `src/claude_resource_manager/tui/modals/error_modal.py` - Error UI ready
- ✅ `tests/utils/accessibility_helpers.py` - All contrast helpers working

---

## Dependencies

### Internal Dependencies
- **Theme Registration** (Issue 2.1) blocks Issues 2.2, 2.3
- **Error Modal Integration** (Issue 4.1) blocks Issues 4.2, 4.4
- **Batch Install** (Issue 1.5) blocks Issue 4.3

### External Dependencies
- None - all dependencies already installed in requirements

---

## Testing Strategy

### After Each Fix
```bash
# Run specific test
.venv/bin/pytest tests/unit/test_accessibility.py::TestClassName::test_name -v

# Run category
.venv/bin/pytest tests/unit/test_accessibility.py::TestColorContrast -v
```

### Before PR
```bash
# Run all accessibility tests
.venv/bin/pytest tests/unit/test_accessibility.py -v

# Expected output after P0 fixes:
# 30 passed, 6 failed (83%)

# Expected output after P1 fixes:
# 34 passed, 2 failed (94%)

# Expected output after P2 fixes:
# 36 passed (100%)
```

### Manual Testing Checklist
After implementing fixes, manually verify:

- [ ] Screen reader announces search results (VoiceOver/NVDA)
- [ ] Category changes are spoken aloud
- [ ] Errors are announced assertively
- [ ] ESC key clears search when focused
- [ ] Tab moves through widgets in logical order
- [ ] All themes display correct contrast ratios
- [ ] Error modal shows user-friendly messages

---

## Risk Assessment

### Low Risk (Can be done immediately)
- Issues 1.1, 1.2, 1.3, 1.6 - Simple method additions
- Issue 3.2 - Test helper implementation

### Medium Risk (Requires testing)
- Issue 2.1 - Theme integration (may affect CSS)
- Issue 3.1 - ESC key behavior (may break existing shortcuts)
- Issue 4.1 - Error modal integration (changes error flow)

### High Risk (Requires careful design)
- Issues 1.5, 4.3 - Batch install workflow (new feature)

---

## Success Metrics

### Current State
- Tests passing: 21/36 (58%)
- WCAG compliance: ~78% (estimated)
- Screen reader support: Partial (selection only)
- Error recovery: None

### Target State (After P0)
- Tests passing: 30/36 (83%)
- WCAG compliance: 100% ✅
- Screen reader support: Full
- Error recovery: Basic modal

### Stretch Goal (After P1+P2)
- Tests passing: 36/36 (100%)
- WCAG compliance: 100% ✅
- Screen reader support: Full with progress
- Error recovery: Full with retry/skip/cancel

---

## Questions / Blockers

### Open Questions
1. **Theme Integration:** Should we use CSS variables or Textual's built-in theme system?
2. **Batch Install:** Should this be a separate screen or inline in BrowserScreen?
3. **Error Announcements:** Should errors interrupt current speech (assertive) or queue (polite)?

### Current Blockers
None - all infrastructure is in place, just needs integration.

---

## References

- **WCAG 2.1 AA Standard:** https://www.w3.org/TR/WCAG21/
- **Implementation Summary:** `/docs/ACCESSIBILITY_IMPLEMENTATION_SUMMARY.md`
- **Test Summary:** `/docs/ACCESSIBILITY_TEST_SUMMARY.md`
- **Theme Implementation:** `/src/claude_resource_manager/tui/theme.py`
- **ARIA Widget:** `/src/claude_resource_manager/tui/widgets/aria_live.py`
- **Error Modal:** `/src/claude_resource_manager/tui/modals/error_modal.py`

---

## Document Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-05 | 1.0 | Initial document creation | Technical Writer |

---

**Next Review Date:** After P0 implementation (8 hours of work)
**Owner:** Development Team
**Stakeholders:** QA Team, Accessibility Specialist, Product Manager
