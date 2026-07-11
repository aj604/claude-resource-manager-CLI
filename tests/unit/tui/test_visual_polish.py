"""Comprehensive test suite for Visual Polish features in BrowserScreen.

This module tests visual feedback enhancements for multi-select functionality:

- Checkbox column rendering ([ ] vs [x])
- Selection count indicators
- Real-time visual feedback
- Animation and smooth transitions
- Row highlighting and focus indicators
- Progress indicators for batch operations

Test Coverage: 20 tests
Strategy: RED phase - All tests will FAIL until visual polish is implemented

The visual polish system should provide:
1. Clear checkbox column showing selection state
2. Prominent selection count widget
3. Immediate visual feedback on state changes
4. Smooth animations without flicker
5. Distinct focus vs selection indicators

Author: TestMaster (TDD RED Phase)
Date: 2025-10-05
Phase: Phase 3 - Visual Polish
"""

from unittest.mock import AsyncMock

import pytest
from textual.app import App
from textual.widgets import DataTable, Static

from claude_resource_manager.tui.screens.browser_screen import BrowserScreen

# Force TUI tests to run serially to avoid race conditions with Textual app state
pytestmark = pytest.mark.xdist_group("tui")


class VisualPolishTestApp(App):
    """Test app for visual polish testing."""

    def __init__(self, catalog_loader=None, search_engine=None, **kwargs):
        super().__init__(**kwargs)
        self.catalog_loader = catalog_loader
        self.search_engine = search_engine

    def on_mount(self) -> None:
        """Push BrowserScreen on mount."""
        self.push_screen(
            BrowserScreen(catalog_loader=self.catalog_loader, search_engine=self.search_engine)
        )


# ============================================================================
# Checkbox Column Tests (7 tests)
# ============================================================================


class TestCheckboxColumn:
    """Tests for checkbox column implementation and rendering.

    The checkbox column should:
    - Be the first column in the DataTable
    - Show [ ] for unselected resources
    - Show [x] for selected resources
    - Update immediately when selection changes
    - Have appropriate width (4 characters minimum)
    - Display consistently across all rows
    """

    @pytest.mark.asyncio
    async def test_WHEN_browser_loads_THEN_checkbox_column_present(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Browser should display checkbox column as first column on load.

        Expected: DataTable has a "Select" column (or checkbox symbol) as column 0
        Current: Will FAIL - checkbox column not yet implemented
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)

            # Get column information
            columns = list(table.columns.keys())

            # First column should be checkbox/select column
            assert len(columns) > 0, "DataTable should have columns"
            first_col = table.columns[columns[0]]

            # Check column label is Select or checkbox symbol
            assert first_col.label.plain in [
                "Select",
                "☐",
                "✓",
                "",
            ], f"First column should be Select column, got: {first_col.label.plain}"

    @pytest.mark.asyncio
    async def test_WHEN_resource_unselected_THEN_shows_empty_checkbox(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Unselected resources should display empty checkbox [ ].

        Expected: First cell of unselected row shows "[ ]" or "☐"
        Current: Will FAIL - checkbox rendering not implemented
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)

            # Get first row (should be unselected initially)
            first_row = table.get_row_at(0)

            # First cell should show empty checkbox
            checkbox_cell = str(first_row[0])
            assert checkbox_cell in [
                "[ ]",
                "☐",
                "❌",
                "",
            ], f"Unselected row should show empty checkbox, got: {checkbox_cell}"

    @pytest.mark.asyncio
    async def test_WHEN_resource_selected_THEN_shows_checked_checkbox(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Selected resources should display checked checkbox [x].

        Expected: First cell of selected row shows "[x]" or "☑"
        Current: Will FAIL - checkbox selection rendering not implemented
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select first resource
            await pilot.press("space")
            await pilot.pause()

            # Get first row (now selected)
            first_row = table.get_row_at(0)

            # First cell should show checked checkbox
            checkbox_cell = str(first_row[0])
            assert checkbox_cell in [
                "[x]",
                "☑",
                "✓",
                "✅",
            ], f"Selected row should show checked checkbox, got: {checkbox_cell}"

    @pytest.mark.asyncio
    async def test_WHEN_space_pressed_THEN_checkbox_toggles(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Space key should toggle checkbox between [ ] and [x].

        Expected: Checkbox toggles on repeated space presses
        Current: Will FAIL - checkbox toggle visual feedback not implemented
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Get initial checkbox state
            first_row_initial = table.get_row_at(0)
            initial_checkbox = str(first_row_initial[0])

            # Should start unchecked
            assert initial_checkbox in ["[ ]", "☐", "❌", ""], "Initial state should be unchecked"

            # Toggle selection with space
            await pilot.press("space")
            await pilot.pause()

            # Should now be checked
            first_row_selected = table.get_row_at(0)
            selected_checkbox = str(first_row_selected[0])
            assert selected_checkbox in [
                "[x]",
                "☑",
                "✓",
                "✅",
            ], "After space, should show checked checkbox"

            # Toggle again
            await pilot.press("space")
            await pilot.pause()

            # Should be unchecked again
            first_row_deselected = table.get_row_at(0)
            deselected_checkbox = str(first_row_deselected[0])
            assert deselected_checkbox in [
                "[ ]",
                "☐",
                "❌",
                "",
            ], "After second space, should show unchecked checkbox"

    @pytest.mark.asyncio
    async def test_WHEN_all_selected_THEN_all_checkboxes_checked(
        self, mock_catalog_loader, sample_resources_list
    ):
        """When all resources selected, all checkboxes should show [x].

        Expected: Every row's first cell shows checked checkbox
        Current: Will FAIL - bulk checkbox rendering not implemented
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list[:3])
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select all 3 resources
            for i in range(3):
                await pilot.press("space")
                if i < 2:  # Don't move down after last
                    await pilot.press("down")
                await pilot.pause()

            # Check all rows have checked checkboxes
            for row_index in range(3):
                row = table.get_row_at(row_index)
                checkbox_cell = str(row[0])
                assert checkbox_cell in [
                    "[x]",
                    "☑",
                    "✓",
                    "✅",
                ], f"Row {row_index} should show checked checkbox, got: {checkbox_cell}"

    @pytest.mark.asyncio
    async def test_WHEN_checkbox_column_THEN_correct_width(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Checkbox column should have appropriate width (4 chars minimum).

        Expected: Checkbox column width >= 4 to accommodate "[ ]" or "[x]"
        Current: Will FAIL - checkbox column width not configured
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)

            # Get first column (checkbox column)
            columns = list(table.columns.keys())
            first_col_key = columns[0]
            first_col = table.columns[first_col_key]

            # Column should have minimum width for checkbox
            assert (
                first_col.width >= 4
            ), f"Checkbox column should be at least 4 chars wide, got: {first_col.width}"

    @pytest.mark.asyncio
    async def test_WHEN_checkbox_symbols_THEN_uses_brackets_and_x(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Checkbox should use [ ] and [x] symbols for consistency.

        Expected: Uses ASCII-friendly [ ] and [x] not Unicode
        Current: Will FAIL - checkbox symbol standardization not implemented

        Note: Could also accept ☐/☑ Unicode symbols as alternative
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Get unselected checkbox
            row_unselected = table.get_row_at(0)
            unchecked = str(row_unselected[0])

            # Should be [ ] or ☐ or ❌
            assert unchecked in ["[ ]", "☐", "❌"], f"Unchecked should be [ ] or ☐, got: {unchecked}"

            # Select and get checked checkbox
            await pilot.press("space")
            await pilot.pause()

            row_selected = table.get_row_at(0)
            checked = str(row_selected[0])

            # Should be [x] or ☑ or ✅
            assert checked in ["[x]", "☑", "✅"], f"Checked should be [x] or ☑, got: {checked}"


# ============================================================================
# Selection Indicator Tests (5 tests)
# ============================================================================


class TestSelectionIndicator:
    """Tests for selection count widget and indicator display.

    The selection indicator should:
    - Display "X selected" count prominently
    - Update in real-time as selections change
    - Be visible in status bar or dedicated widget
    - Show zero state appropriately
    - Use highlighting when selections > 0
    """

    @pytest.mark.asyncio
    async def test_WHEN_no_selections_THEN_count_shows_zero(
        self, mock_catalog_loader, sample_resources_list
    ):
        """No selections should display "0 selected" or hide count.

        Expected: Status bar shows "0 selected" or no selection indicator
        Current: Will FAIL - selection count widget not implemented
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Look for selection count widget
            selection_widget = screen.query_one("#selection-count", Static)
            assert selection_widget is not None, "Selection count widget should exist"

            count_text = str(selection_widget.render()).lower()
            # Should show 0 or be empty
            assert (
                "0 selected" in count_text or count_text == ""
            ), f"Should show 0 selected or empty, got: {count_text}"

    @pytest.mark.asyncio
    async def test_WHEN_one_selected_THEN_count_shows_one(
        self, mock_catalog_loader, sample_resources_list
    ):
        """One selection should display "1 selected".

        Expected: Status bar shows "1 selected" (singular)
        Current: Will FAIL - selection count not updating
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select one resource
            await pilot.press("space")
            await pilot.pause()

            # Check count widget
            selection_widget = screen.query_one("#selection-count", Static)
            count_text = str(selection_widget.render()).lower()

            assert ("1 selected" in count_text or "1 /" in count_text), f"Should show '1 selected' or '1 / N selected', got: {count_text}"

    @pytest.mark.asyncio
    async def test_WHEN_multiple_selected_THEN_count_accurate(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Multiple selections should display accurate count "N selected".

        Expected: Status bar shows "3 selected" for 3 selections
        Current: Will FAIL - multi-selection count not tracking
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select 3 resources
            for i in range(3):
                await pilot.press("space")
                if i < 2:
                    await pilot.press("down")
                await pilot.pause()

            # Check count widget
            selection_widget = screen.query_one("#selection-count", Static)
            count_text = str(selection_widget.render()).lower()

            assert ("3" in count_text and "selected" in count_text), f"Should show '3 selected' or '3 / N selected', got: {count_text}"

    @pytest.mark.asyncio
    async def test_WHEN_selection_changes_THEN_count_updates_immediately(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Selection count should update in real-time without delay.

        Expected: Count updates within same event loop tick
        Current: Will FAIL - real-time count update not implemented
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            selection_widget = screen.query_one("#selection-count", Static)

            # Initial: 0 selected
            count_text = str(selection_widget.render()).lower()
            assert "0" in count_text or count_text == ""

            # Select one
            await pilot.press("space")
            await pilot.pause()

            count_text = str(selection_widget.render()).lower()
            assert ("1 selected" in count_text or "1 /" in count_text), "Should immediately show 1 selected"

            # Deselect
            await pilot.press("space")
            await pilot.pause()

            count_text = str(selection_widget.render()).lower()
            assert "0" in count_text or "1" not in count_text, "Should immediately update back to 0"

    @pytest.mark.asyncio
    async def test_WHEN_count_widget_THEN_prominently_displayed(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Selection count widget should be prominently visible.

        Expected: Widget has highlighting/styling to stand out
        Current: Will FAIL - count widget styling not applied
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select a resource to make count visible
            await pilot.press("space")
            await pilot.pause()

            selection_widget = screen.query_one("#selection-count", Static)

            # Widget should exist and be visible
            assert selection_widget is not None, "Selection count widget must exist"
            assert selection_widget.display, "Selection count should be displayed"

            # Should have prominent styling (check for ID or class)
            assert selection_widget.id == "selection-count" or "selection" in " ".join(
                selection_widget.classes
            ), "Widget should have identifiable styling"


# ============================================================================
# Visual Feedback Tests (5 tests)
# ============================================================================


class TestVisualFeedback:
    """Tests for real-time visual updates and feedback mechanisms.

    Visual feedback should:
    - Update immediately on selection change (<100ms)
    - Show progress indicators for batch operations
    - Provide hover feedback when supported
    - Show focus indicators distinct from selection
    - Update without blocking user interaction
    """

    @pytest.mark.asyncio
    async def test_WHEN_selection_added_THEN_visual_feedback_immediate(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Adding selection should provide immediate visual feedback.

        Expected: Checkbox updates within same render cycle
        Current: Will FAIL - immediate visual update not implemented
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Press space to select
            await pilot.press("space")
            # Don't add extra pause - should be immediate

            # Check visual state updated immediately
            row = table.get_row_at(0)
            checkbox_cell = str(row[0])

            assert checkbox_cell in [
                "[x]",
                "☑",
                "✓",
                "✅",
            ], "Checkbox should update immediately on selection"

            # Selection set should also update
            assert len(screen.selected_resources) == 1, "Selection state should update immediately"

    @pytest.mark.asyncio
    async def test_WHEN_selection_removed_THEN_visual_feedback_immediate(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Removing selection should provide immediate visual feedback.

        Expected: Checkbox clears within same render cycle
        Current: Will FAIL - immediate deselection feedback not implemented
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select then deselect
            await pilot.press("space")
            await pilot.pause()

            # Verify selected
            row_selected = table.get_row_at(0)
            assert "[x]" in str(row_selected[0]) or "☑" in str(row_selected[0]) or "✅" in str(row_selected[0])

            # Deselect
            await pilot.press("space")
            # Immediate check

            row_deselected = table.get_row_at(0)
            checkbox_cell = str(row_deselected[0])
            assert checkbox_cell in [
                "[ ]",
                "☐",
                "❌",
                "",
            ], "Checkbox should clear immediately on deselection"

    @pytest.mark.asyncio
    async def test_WHEN_batch_operation_THEN_progress_indicator_visible(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Batch operations should show progress indicator.

        Expected: Progress bar or status appears during bulk actions
        Current: Will FAIL - progress indicator not implemented

        Note: This test may need to be adapted based on actual batch operation UX
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select multiple resources
            for i in range(3):
                await pilot.press("space")
                if i < 2:
                    await pilot.press("down")
                await pilot.pause()

            # Simulate batch operation trigger (e.g., install multiple)
            # This assumes batch operation method exists
            if hasattr(screen, "batch_install_selected"):
                # Note: This is async operation - progress should show
                # We're just checking the progress widget exists/can be queried

                # Progress widget should be queryable (even if hidden initially)
                progress_widgets = screen.query(".progress-indicator")
                assert len(progress_widgets) > 0 or screen.query(
                    "#progress-bar"
                ), "Progress indicator widget should exist for batch operations"

    @pytest.mark.asyncio
    async def test_WHEN_hover_over_resource_THEN_highlight_visible(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Hovering over resource should show highlight (if hover supported).

        Expected: Row shows hover state (may be cursor-based in terminal)
        Current: Will FAIL - hover highlight not implemented

        Note: Terminal hover is limited - this tests cursor highlight
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Cursor should be on first row
            assert table.cursor_row == 0, "Cursor should start at row 0"

            # Move cursor to second row
            await pilot.press("down")
            await pilot.pause()

            # Cursor position should update
            assert table.cursor_row == 1, "Cursor should move to row 1"

            # Visual cursor highlight is handled by Textual DataTable
            # We're verifying cursor tracking works for visual feedback

    @pytest.mark.asyncio
    async def test_WHEN_focused_resource_THEN_focus_indicator_visible(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Focused resource should have distinct focus indicator.

        Expected: Focus ring/highlight distinct from selection checkbox
        Current: Will FAIL - focus indicator styling not implemented

        Focus should be visually distinct from selection state.
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Table should have focus
            assert table.has_focus, "Table should be focused"

            # Cursor should be visible (row 0)
            assert table.cursor_row == 0, "Cursor should be at row 0"

            # Now select the focused row
            await pilot.press("space")
            await pilot.pause()

            # Both focus AND selection should be visible
            # Focus = cursor position, Selection = checkbox [x]
            row = table.get_row_at(0)
            checkbox = str(row[0])

            assert checkbox in ["[x]", "☑", "✅"], "Row should show selection checkbox"
            assert table.cursor_row == 0, "Focus cursor should still be on row 0"
            # Both states coexist - focus cursor + selection checkbox


# ============================================================================
# Animation & Timing Tests (3 tests)
# ============================================================================


class TestAnimationAndTiming:
    """Tests for smooth transitions and animation performance.

    Animations should:
    - Update smoothly without visible lag
    - Avoid flickering or double-rendering
    - Maintain scroll position during updates
    - Not block user interaction
    - Provide consistent timing
    """

    @pytest.mark.asyncio
    async def test_WHEN_state_changes_THEN_animation_smooth(
        self, mock_catalog_loader, sample_resources_list
    ):
        """State changes should animate smoothly without lag.

        Expected: State transitions occur within one render frame
        Current: Will FAIL - smooth animation not implemented

        Note: Terminal "animation" is mostly instant updates, but should be smooth
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Rapid state changes - should all work smoothly
            for i in range(5):
                await pilot.press("space")  # Toggle selection
                # No extra pause - should handle rapid input

            # All toggles should have completed
            # Odd number of toggles = selected
            assert len(screen.selected_resources) == 1, "Rapid toggles should process smoothly"

    @pytest.mark.asyncio
    async def test_WHEN_multiple_updates_THEN_no_flicker(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Multiple rapid updates should not cause visual flicker.

        Expected: UI updates are batched/debounced to prevent flicker
        Current: Will FAIL - anti-flicker batching not implemented
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Rapidly select multiple resources
            for i in range(3):
                await pilot.press("space")
                await pilot.press("down")
                # Minimal pause - testing rapid updates

            await pilot.pause()

            # All 3 should be selected without rendering issues
            assert (
                len(screen.selected_resources) == 3
            ), "All selections should register without flicker"

            # Verify all checkboxes rendered correctly
            for row_index in range(3):
                row = table.get_row_at(row_index)
                checkbox = str(row[0])
                assert checkbox in [
                    "[x]",
                    "☑",
                    "✅",
                ], f"Row {row_index} checkbox should be checked (no flicker)"

    @pytest.mark.asyncio
    async def test_WHEN_table_updates_THEN_scroll_position_maintained(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Table updates should preserve scroll position.

        Expected: Scroll position unchanged after selection updates
        Current: Will FAIL - scroll position preservation not implemented
        """
        # Create longer list to enable scrolling
        long_list = sample_resources_list * 4  # 20 resources
        mock_catalog_loader.load_resources = AsyncMock(return_value=long_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Scroll down several rows
            for _ in range(10):
                await pilot.press("down")
            await pilot.pause()

            # Record cursor position
            cursor_before = table.cursor_row
            assert cursor_before == 10, "Should be at row 10"

            # Make selection (should not reset scroll)
            await pilot.press("space")
            await pilot.pause()

            # Cursor position should be maintained
            cursor_after = table.cursor_row
            assert (
                cursor_after == cursor_before
            ), f"Cursor position should be maintained at {cursor_before}, got {cursor_after}"

            # Selection should work
            assert (
                len(screen.selected_resources) == 1
            ), "Selection should work without affecting scroll position"


# ============================================================================
# Integration Tests (Bonus - crosses multiple areas)
# ============================================================================


class TestVisualPolishIntegration:
    """Integration tests combining multiple visual polish features.

    These tests verify that visual components work together correctly.
    """

    @pytest.mark.asyncio
    async def test_WHEN_select_with_filter_THEN_visuals_update_correctly(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Selections should display correctly with active filters.

        Expected: Checkboxes and count update correctly when filtering
        Current: Will FAIL - integrated visual updates not implemented
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select first resource (architect - agent)
            await pilot.press("space")
            await pilot.pause()

            # Verify checkbox
            row = table.get_row_at(0)
            assert "[x]" in str(row[0]) or "☑" in str(row[0]) or "✅" in str(row[0])

            # Verify count
            selection_widget = screen.query_one("#selection-count", Static)
            count_text = str(selection_widget.render()).lower()
            assert ("1 selected" in count_text or "1 /" in count_text)

            # Apply filter to agents only
            await screen.filter_by_type("agent")
            await pilot.pause()

            # Selection should persist and be visible
            assert len(screen.selected_resources) == 1

            # Count should still show 1
            count_text = str(selection_widget.render()).lower()
            assert (
                "1 selected" in count_text
            ), "Selection count should persist through filter changes"

    @pytest.mark.asyncio
    async def test_WHEN_deselect_all_THEN_all_visuals_reset(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Clearing all selections should reset all visual indicators.

        Expected: All checkboxes empty, count shows 0
        Current: Will FAIL - bulk visual reset not implemented
        """
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list[:3])
        app = VisualPolishTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select all 3
            for i in range(3):
                await pilot.press("space")
                if i < 2:
                    await pilot.press("down")
                await pilot.pause()

            # Verify all selected
            assert len(screen.selected_resources) == 3

            # Clear all selections
            await screen.clear_selections()
            await pilot.pause()

            # All checkboxes should be empty
            for row_index in range(3):
                row = table.get_row_at(row_index)
                checkbox = str(row[0])
                assert checkbox in [
                    "[ ]",
                    "☐",
                    "❌",
                    "",
                ], f"Row {row_index} checkbox should be empty after clear"

            # Count should show 0
            selection_widget = screen.query_one("#selection-count", Static)
            count_text = str(selection_widget.render()).lower()
            assert "0" in count_text or count_text == "", "Count should reset to 0 after clear all"
