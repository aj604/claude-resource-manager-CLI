"""Comprehensive test suite for multi-select functionality in BrowserScreen.

This module tests the multi-select feature that allows users to select multiple
resources for batch operations. Tests cover:

- Selection state management (toggle, add, remove)
- Keyboard interaction (Space key)
- UI updates (checkboxes, visual feedback)
- Selection persistence during filtering/search
- Edge cases (empty selections, max limits)

Test Coverage: 20 tests
Strategy: RED phase - All tests will FAIL until multi-select is implemented

Author: TestMaster (TDD Phase)
"""

from unittest.mock import AsyncMock

import pytest
from textual.app import App
from textual.widgets import DataTable

from claude_resource_manager.tui.screens.browser_screen import BrowserScreen


class MultiSelectTestApp(App):
    """Test app for multi-select testing."""

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
# Selection State Management Tests (8 tests)
# ============================================================================


class TestSelectionStateManagement:
    """Test multi-select state tracking and management."""

    @pytest.mark.asyncio
    async def test_WHEN_space_pressed_THEN_toggles_selection(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Space key should toggle resource selection state."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Initially no selections
            assert len(screen.selected_resources) == 0

            # Press space to select first resource
            await pilot.press("space")
            await pilot.pause()

            # First resource should be selected
            assert len(screen.selected_resources) == 1
            first_id = screen.filtered_resources[0].get(
                "id", screen.filtered_resources[0].get("name")
            )
            assert first_id in screen.selected_resources

    @pytest.mark.asyncio
    async def test_WHEN_select_multiple_THEN_all_tracked(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Selecting multiple resources should track all of them."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select first 3 resources
            for i in range(3):
                await pilot.press("space")  # Select
                await pilot.press("down")  # Move to next
                await pilot.pause()

            # Should have 3 resources selected
            assert len(screen.selected_resources) == 3

    @pytest.mark.asyncio
    async def test_WHEN_deselect_resource_THEN_removes_from_set(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Pressing space on selected resource should deselect it."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select first resource
            await pilot.press("space")
            await pilot.pause()
            assert len(screen.selected_resources) == 1

            # Press space again to deselect
            await pilot.press("space")
            await pilot.pause()

            # Should be deselected
            assert len(screen.selected_resources) == 0

    @pytest.mark.asyncio
    async def test_WHEN_select_all_in_category_THEN_batch_selects(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Select-all action should select all visible resources."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            # Filter to agents only
            await screen.filter_by_type("agent")
            await pilot.pause()

            # Call select_all method (needs to be implemented)
            await screen.select_all_visible()
            await pilot.pause()

            # Should have selected all agents (5 in sample data)
            assert len(screen.selected_resources) == 5

    @pytest.mark.asyncio
    async def test_WHEN_clear_selections_THEN_empties_set(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Clear selections action should remove all selections."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select multiple resources
            for _ in range(3):
                await pilot.press("space")
                await pilot.press("down")
                await pilot.pause()

            assert len(screen.selected_resources) > 0

            # Clear all selections
            await screen.clear_selections()
            await pilot.pause()

            # Should be empty
            assert len(screen.selected_resources) == 0

    @pytest.mark.asyncio
    async def test_WHEN_filter_active_THEN_selections_persist(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Selections should persist when switching filters."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select first resource (architect - agent)
            await pilot.press("space")
            await pilot.pause()
            first_id = screen.filtered_resources[0].get("id")
            assert first_id in screen.selected_resources

            # Change filter to command
            await screen.filter_by_type("command")
            await pilot.pause()

            # Selection should still exist
            assert first_id in screen.selected_resources

            # Change back to all
            await screen.filter_by_type("all")
            await pilot.pause()

            # Selection should still be there
            assert first_id in screen.selected_resources

    @pytest.mark.asyncio
    async def test_WHEN_search_active_THEN_selections_persist(
        self, mock_catalog_loader, mock_search_engine, sample_resources_list
    ):
        """Selections should persist during search operations."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        mock_search_engine.search.return_value = [sample_resources_list[0]]
        app = MultiSelectTestApp(
            catalog_loader=mock_catalog_loader, search_engine=mock_search_engine
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select first resource
            await pilot.press("space")
            await pilot.pause()
            selected_id = screen.filtered_resources[0].get("id")
            assert selected_id in screen.selected_resources

            # Perform search
            await screen.perform_search("architect")
            await pilot.pause()

            # Selection should persist
            assert selected_id in screen.selected_resources

    @pytest.mark.asyncio
    async def test_WHEN_resource_id_unique_THEN_no_duplicates(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Selecting same resource twice should not create duplicates."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select first resource
            await pilot.press("space")
            await pilot.pause()
            initial_count = len(screen.selected_resources)

            # Deselect
            await pilot.press("space")
            await pilot.pause()

            # Select again
            await pilot.press("space")
            await pilot.pause()

            # Should still have same count (no duplicates)
            assert len(screen.selected_resources) == initial_count


# ============================================================================
# UI Updates Tests (6 tests)
# ============================================================================


class TestUIUpdates:
    """Test visual feedback and UI updates for multi-select."""

    @pytest.mark.asyncio
    async def test_WHEN_selected_THEN_shows_checkbox(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Selected resources should display checkbox indicator [x]."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select first resource
            await pilot.press("space")
            await pilot.pause()

            # Check if checkbox column exists and shows [x]
            first_row = table.get_row_at(0)
            # Checkbox should be first column
            assert "[x]" in str(first_row[0]) or "✓" in str(first_row[0])

    @pytest.mark.asyncio
    async def test_WHEN_not_selected_THEN_shows_empty_checkbox(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Unselected resources should display empty checkbox [ ]."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)

            # Check first row (not selected)
            first_row = table.get_row_at(0)
            # Should show empty checkbox
            assert "[ ]" in str(first_row[0]) or "☐" in str(first_row[0])

    @pytest.mark.asyncio
    async def test_WHEN_selections_change_THEN_counter_updates(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Selection counter should update in real-time."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Initially no counter
            status_bar = screen.query_one("#status-bar")
            status_text = str(status_bar.render()).lower()
            assert "selected" not in status_text or "0 selected" in status_text

            # Select one
            await pilot.press("space")
            await pilot.pause()

            status_text = str(status_bar.render()).lower()
            assert "1 selected" in status_text

            # Select another
            await pilot.press("down")
            await pilot.press("space")
            await pilot.pause()

            status_text = str(status_bar.render()).lower()
            assert "2 selected" in status_text

    @pytest.mark.asyncio
    async def test_WHEN_selected_THEN_row_highlighted(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Selected rows should have visual highlighting."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select first resource
            await pilot.press("space")
            await pilot.pause()

            # Row should have selected class or style
            # This is implementation-specific, but we expect some visual indicator
            # For now, we check that the selection state is tracked
            first_id = screen.filtered_resources[0].get("id")
            assert first_id in screen.selected_resources
            # Visual feedback will be tested in integration tests

    @pytest.mark.asyncio
    async def test_WHEN_navigate_with_selections_THEN_keyboard_works(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Keyboard navigation should work normally with selections active."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select first
            await pilot.press("space")
            await pilot.pause()

            # Navigate down
            await pilot.press("down")
            await pilot.pause()

            # Cursor should have moved
            assert table.cursor_row == 1

            # Select second
            await pilot.press("space")
            await pilot.pause()

            # Should have 2 selections
            assert len(screen.selected_resources) == 2

    @pytest.mark.asyncio
    async def test_WHEN_toggle_selection_THEN_instant_feedback(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Selection toggle should provide instant visual feedback."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Toggle selection
            await pilot.press("space")
            await pilot.pause()

            # Should update immediately (no delay)
            assert len(screen.selected_resources) == 1

            # Toggle off
            await pilot.press("space")
            await pilot.pause()

            # Should deselect immediately
            assert len(screen.selected_resources) == 0


# ============================================================================
# Edge Cases Tests (6 tests)
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions for multi-select."""

    @pytest.mark.asyncio
    async def test_WHEN_max_selections_reached_THEN_prevents_more(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Optional: Enforce maximum selection limit."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Set max limit
            screen.max_selections = 2

            # Select 2 resources
            await pilot.press("space")
            await pilot.press("down")
            await pilot.press("space")
            await pilot.pause()

            assert len(screen.selected_resources) == 2

            # Try to select third
            await pilot.press("down")
            await pilot.press("space")
            await pilot.pause()

            # Should still be 2 (max enforced)
            assert len(screen.selected_resources) == 2

    @pytest.mark.asyncio
    async def test_WHEN_select_during_filter_THEN_only_visible(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Selecting during filter should only affect visible resources."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            # Filter to agents
            await screen.filter_by_type("agent")
            await pilot.pause()

            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select first visible (agent)
            await pilot.press("space")
            await pilot.pause()

            selected_id = screen.filtered_resources[0].get("id")
            # Should be an agent
            assert screen.filtered_resources[0].get("type") == "agent"
            assert selected_id in screen.selected_resources

    @pytest.mark.asyncio
    async def test_WHEN_deselect_during_filter_THEN_updates_correctly(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Deselecting during filter should work correctly."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select in "all" view
            await pilot.press("space")
            await pilot.pause()
            selected_id = screen.filtered_resources[0].get("id")
            assert selected_id in screen.selected_resources

            # Filter to agents
            await screen.filter_by_type("agent")
            await pilot.pause()

            # Deselect if visible
            if selected_id == screen.filtered_resources[0].get("id"):
                await pilot.press("space")
                await pilot.pause()

                # Should be deselected
                assert selected_id not in screen.selected_resources

    @pytest.mark.asyncio
    async def test_WHEN_sort_active_THEN_selections_maintained(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Selections should persist after sorting."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select first and third resources
            await pilot.press("space")  # Select first
            await pilot.press("down")
            await pilot.press("down")
            await pilot.press("space")  # Select third
            await pilot.pause()

            selected_before = screen.selected_resources.copy()
            assert len(selected_before) == 2

            # Sort by name (if sorting is implemented)
            await screen.sort_by("name")
            await pilot.pause()

            # Selections should remain
            assert screen.selected_resources == selected_before

    @pytest.mark.asyncio
    async def test_WHEN_empty_list_THEN_no_selection_errors(self, mock_catalog_loader):
        """Empty resource list should not cause selection errors."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=[])
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Try to select in empty list
            await pilot.press("space")
            await pilot.pause()

            # Should not error, no selections
            assert len(screen.selected_resources) == 0

    @pytest.mark.asyncio
    async def test_WHEN_select_with_no_id_THEN_handles_gracefully(self, mock_catalog_loader):
        """Resources without ID should be handled gracefully."""
        resources_no_id = [{"type": "agent", "name": "Test Agent", "description": "No ID"}]
        mock_catalog_loader.load_resources = AsyncMock(return_value=resources_no_id)
        app = MultiSelectTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Try to select
            await pilot.press("space")
            await pilot.pause()

            # Should use name as fallback for ID
            assert "Test Agent" in screen.selected_resources or len(screen.selected_resources) == 1
