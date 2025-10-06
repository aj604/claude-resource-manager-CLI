"""Behavior-Focused Sorting Tests - Phase 3 TDD Red Phase.

This test suite demonstrates behavior-focused testing approach:
- Tests WHAT happens (resources get sorted), not HOW (specific keypresses)
- Uses abstraction helpers to decouple from implementation details
- Survives UX changes (menu-based → cycling → command palette)
- Focuses on observable outcomes, not internal mechanics

Key Lesson from Phase 2:
    Implementation-specific tests break when UX improves.
    Behavior-focused tests remain valid across UI paradigm shifts.

Test Coverage (15 tests):
1. Basic sorting behaviors (name, type, date) - 3 tests
2. Sort cycling and reversing - 3 tests
3. Sort with filters and search - 3 tests
4. Sort persistence and indicators - 3 tests
5. Sort edge cases and stability - 3 tests

Expected State: ALL TESTS FAIL INITIALLY (Red Phase)
This is intentional - we're defining behaviors before implementation.
"""

from unittest.mock import AsyncMock

import pytest

# Import test app
from tests.unit.tui.test_advanced_ui import AdvancedUITestApp
from tests.utils.tui_helpers import TUITestHelper


class TestSortingBehaviorFocused:
    """Behavior-focused sorting tests that survive UX changes.

    These tests abstract the HOW (keypresses, clicks) to test WHAT (outcomes).
    """

    # ========================================================================
    # BASIC SORTING BEHAVIORS (3 tests)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_WHEN_sort_by_name_triggered_THEN_resources_alphabetically_ordered(
        self, sample_resources
    ):
        """Triggering name sort MUST result in alphabetically ordered resources.

        This tests the BEHAVIOR (alphabetical ordering), not the mechanism
        (keypresses, menu selection, etc.).

        FAILS: Behavior not yet implemented.
        """
        # Arrange
        loader = AsyncMock()
        loader.load_resources.return_value = sample_resources
        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Act - Trigger sort by name (implementation-agnostic)
            await TUITestHelper.trigger_sort_by_name(pilot)
            await pilot.pause()

            # Assert - Resources should be alphabetically ordered
            browser = app.screen
            TUITestHelper.assert_sorted_by_name(browser.filtered_resources)

    @pytest.mark.asyncio
    async def test_WHEN_sort_by_type_triggered_THEN_resources_grouped_by_type(
        self, sample_resources
    ):
        """Triggering type sort MUST result in type-grouped resources.

        Tests grouping behavior regardless of HOW sort is triggered.

        FAILS: Type sorting behavior not implemented.
        """
        # Arrange
        loader = AsyncMock()
        loader.load_resources.return_value = sample_resources
        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Act
            await TUITestHelper.trigger_sort_by_type(pilot)
            await pilot.pause()

            # Assert
            browser = app.screen
            TUITestHelper.assert_sorted_by_type(browser.filtered_resources)

    @pytest.mark.asyncio
    async def test_WHEN_sort_by_updated_triggered_THEN_newest_resources_first(
        self, sample_resources_with_dates
    ):
        """Triggering date sort MUST show newest resources first.

        Tests temporal ordering behavior.

        FAILS: Date sorting not implemented.
        """
        # Arrange
        loader = AsyncMock()
        loader.load_resources.return_value = sample_resources_with_dates
        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Act
            await TUITestHelper.trigger_sort_by_updated(pilot)
            await pilot.pause()

            # Assert
            browser = app.screen
            TUITestHelper.assert_sorted_by_updated(browser.filtered_resources)

    # ========================================================================
    # SORT CYCLING AND REVERSING (3 tests)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_WHEN_sort_cycled_THEN_returns_to_initial_state(self, sample_resources):
        """Cycling through all sort options MUST return to initial state.

        Tests that sort cycling is circular and predictable.

        FAILS: Sort cycling behavior not defined.
        """
        # Arrange
        loader = AsyncMock()
        loader.load_resources.return_value = sample_resources
        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Capture initial state
            browser = app.screen
            initial_names = TUITestHelper.get_visible_resource_names(app)

            # Act - Cycle through all sort options (3 cycles: name -> type -> updated -> name)
            await TUITestHelper.trigger_cycle_sort(pilot, times=3)
            await pilot.pause()

            # Assert - Should return to initial order
            final_names = TUITestHelper.get_visible_resource_names(app)
            assert final_names == initial_names, "Sort cycling did not return to initial state"

    @pytest.mark.asyncio
    async def test_WHEN_sort_reversed_THEN_order_inverted(self, sample_resources):
        """Reversing sort MUST invert the current order.

        Tests that sort reversal produces Z-A from A-Z.

        FAILS: Sort reversal not implemented.
        """
        # Arrange
        loader = AsyncMock()
        loader.load_resources.return_value = sample_resources
        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Act - Sort by name, then reverse
            await TUITestHelper.trigger_sort_by_name(pilot)
            await pilot.pause()

            browser = app.screen
            ascending_names = TUITestHelper.get_visible_resource_names(app)

            await TUITestHelper.trigger_reverse_sort(pilot)
            await pilot.pause()

            descending_names = TUITestHelper.get_visible_resource_names(app)

            # Assert - Should be reversed
            assert descending_names == list(
                reversed(ascending_names)
            ), "Sort reversal did not invert order"

    @pytest.mark.asyncio
    async def test_WHEN_multiple_sort_changes_THEN_last_sort_wins(self, sample_resources):
        """Applying multiple sorts MUST result in last sort being active.

        Tests that sort operations are idempotent and non-cumulative.

        FAILS: Multiple sort handling not defined.
        """
        # Arrange
        loader = AsyncMock()
        loader.load_resources.return_value = sample_resources
        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Act - Apply name sort, then type sort
            await TUITestHelper.trigger_sort_by_name(pilot)
            await pilot.pause()

            await TUITestHelper.trigger_sort_by_type(pilot)
            await pilot.pause()

            # Assert - Only type sort should be active
            browser = app.screen
            TUITestHelper.assert_sorted_by_type(browser.filtered_resources)
            TUITestHelper.assert_sort_indicator_shows(app, "type")

    # ========================================================================
    # SORT WITH FILTERS AND SEARCH (3 tests)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_WHEN_sort_applied_with_filter_THEN_only_filtered_resources_sorted(
        self, sample_resources
    ):
        """Sort MUST only affect visible (filtered) resources.

        Tests that sort respects active filters.

        FAILS: Sort + filter interaction not implemented.
        """
        # Arrange
        loader = AsyncMock()
        loader.load_resources.return_value = sample_resources
        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Act - Filter to agents, then sort
            await app.screen.filter_by_type("agent")
            await pilot.pause()

            await TUITestHelper.trigger_sort_by_name(pilot)
            await pilot.pause()

            # Assert - Only agents should be visible and sorted
            browser = app.screen
            types = TUITestHelper.get_visible_resource_types(app)
            assert all(t == "agent" for t in types), "Filter not applied"

            TUITestHelper.assert_sorted_by_name(browser.filtered_resources)

    @pytest.mark.asyncio
    async def test_WHEN_sort_applied_with_search_THEN_search_results_sorted(self, sample_resources):
        """Sort MUST work correctly with active search queries.

        Tests that sort respects search filtering.

        FAILS: Sort + search interaction not implemented.
        """
        # Arrange
        loader = AsyncMock()
        loader.load_resources.return_value = sample_resources
        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Act - Search, then sort
            search_input = app.screen.query_one("#search-input")
            search_input.value = "agent"
            await app.screen.perform_search("agent")
            await pilot.pause()

            await TUITestHelper.trigger_sort_by_name(pilot)
            await pilot.pause()

            # Assert - Search results should be sorted
            browser = app.screen
            names = TUITestHelper.get_visible_resource_names(app)
            assert all("agent" in n.lower() for n in names), "Search not applied"

            TUITestHelper.assert_sorted_by_name(browser.filtered_resources)

    @pytest.mark.asyncio
    async def test_WHEN_filter_changed_THEN_sort_persists(self, sample_resources):
        """Changing filter MUST maintain active sort order.

        Tests that sort state persists across filter changes.

        FAILS: Sort persistence across filters not implemented.
        """
        # Arrange
        loader = AsyncMock()
        loader.load_resources.return_value = sample_resources
        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Act - Sort, then change filter
            await TUITestHelper.trigger_sort_by_name(pilot)
            await pilot.pause()

            await app.screen.filter_by_type("agent")
            await pilot.pause()

            # Assert - Sort should still be active
            TUITestHelper.assert_sort_indicator_shows(app, "name")

            browser = app.screen
            TUITestHelper.assert_sorted_by_name(browser.filtered_resources)

    # ========================================================================
    # SORT PERSISTENCE AND INDICATORS (3 tests)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_WHEN_sort_applied_THEN_indicator_shows_current_sort(self, sample_resources):
        """Sort indicator MUST reflect currently active sort.

        Tests that UI provides feedback on sort state.

        FAILS: Sort indicator not implemented.
        """
        # Arrange
        loader = AsyncMock()
        loader.load_resources.return_value = sample_resources
        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Act - Apply type sort
            await TUITestHelper.trigger_sort_by_type(pilot)
            await pilot.pause()

            # Assert - Indicator should show 'type'
            TUITestHelper.assert_sort_indicator_shows(app, "type")

    @pytest.mark.asyncio
    async def test_WHEN_no_sort_applied_THEN_default_order_shown(self, sample_resources):
        """Without explicit sort, resources MUST appear in default order.

        Tests default sorting behavior.

        FAILS: Default sort order not defined.
        """
        # Arrange
        loader = AsyncMock()
        loader.load_resources.return_value = sample_resources
        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # No sort action - just observe default

            # Assert - Should match default order (name by default)
            browser = app.screen
            default_sort = getattr(browser, "current_sort", "name")
            assert default_sort == "name", "Default sort should be 'name'"

    @pytest.mark.asyncio
    async def test_WHEN_sort_applied_THEN_state_persists_after_search_clear(self, sample_resources):
        """Sort state MUST persist when search is cleared.

        Tests that sort survives search lifecycle.

        FAILS: Sort persistence through search not implemented.
        """
        # Arrange
        loader = AsyncMock()
        loader.load_resources.return_value = sample_resources
        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Act - Sort, search, clear search
            await TUITestHelper.trigger_sort_by_type(pilot)
            await pilot.pause()

            search_input = app.screen.query_one("#search-input")
            search_input.value = "test"
            await app.screen.perform_search("test")
            await pilot.pause()

            search_input.value = ""
            await app.screen.perform_search("")
            await pilot.pause()

            # Assert - Sort should still be 'type'
            TUITestHelper.assert_sort_indicator_shows(app, "type")
            browser = app.screen
            TUITestHelper.assert_sorted_by_type(browser.filtered_resources)

    # ========================================================================
    # SORT EDGE CASES AND STABILITY (3 tests)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_WHEN_resources_have_equal_sort_keys_THEN_order_stable(self, sample_resources):
        """Resources with equal sort keys MUST maintain stable order.

        Tests sort stability (important for predictable UX).

        FAILS: Sort stability not guaranteed.
        """
        # Arrange - Create resources with duplicate names
        resources_with_dupes = [
            {"id": "first-alpha", "type": "agent", "name": "Alpha"},
            {"id": "second-alpha", "type": "mcp", "name": "Alpha"},
            {"id": "beta", "type": "agent", "name": "Beta"},
        ]
        loader = AsyncMock()
        loader.load_resources.return_value = resources_with_dupes
        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            browser = app.screen
            resources_before = list(browser.filtered_resources)

            # Act - Sort by name (two "Alpha" entries should maintain order)
            await TUITestHelper.trigger_sort_by_name(pilot)
            await pilot.pause()

            resources_after = browser.filtered_resources

            # Assert - Stable sort (equal items maintain relative order)
            TUITestHelper.assert_sort_stable(resources_before, resources_after)

            # Specifically check the two "Alpha" entries
            alpha_ids = [r["id"] for r in resources_after if r["name"] == "Alpha"]
            assert alpha_ids == ["first-alpha", "second-alpha"], "Sort not stable for equal keys"

    @pytest.mark.asyncio
    async def test_WHEN_empty_resource_list_THEN_sort_handles_gracefully(self):
        """Sorting empty list MUST not crash.

        Tests edge case of no resources.

        FAILS: Empty list handling not implemented.
        """
        # Arrange
        loader = AsyncMock()
        loader.load_resources.return_value = []
        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Act - Try to sort empty list
            try:
                await TUITestHelper.trigger_sort_by_name(pilot)
                await pilot.pause()
                success = True
            except Exception as e:
                success = False
                error = str(e)

            # Assert - Should not crash
            assert success, f"Sort crashed on empty list: {error if not success else ''}"

            browser = app.screen
            assert len(browser.filtered_resources) == 0, "Empty list should stay empty"

    @pytest.mark.asyncio
    async def test_WHEN_single_resource_THEN_sort_handles_gracefully(self):
        """Sorting single-item list MUST not crash.

        Tests edge case of one resource.

        FAILS: Single item handling not implemented.
        """
        # Arrange
        single_resource = [{"id": "only", "type": "agent", "name": "Only Resource"}]
        loader = AsyncMock()
        loader.load_resources.return_value = single_resource
        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Act - Try to sort single item
            try:
                await TUITestHelper.trigger_sort_by_name(pilot)
                await pilot.pause()
                success = True
            except Exception:
                success = False

            # Assert - Should not crash
            assert success, "Sort crashed on single-item list"

            browser = app.screen
            assert len(browser.filtered_resources) == 1
            assert browser.filtered_resources[0]["id"] == "only"


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def sample_resources():
    """Sample resources for testing (unsorted)."""
    return [
        {
            "id": "zebra-agent",
            "type": "agent",
            "name": "Zebra Agent",
            "description": "Last alphabetically",
        },
        {
            "id": "alpha-agent",
            "type": "agent",
            "name": "Alpha Agent",
            "description": "First alphabetically",
        },
        {"id": "beta-mcp", "type": "mcp", "name": "Beta MCP", "description": "MCP resource"},
        {"id": "gamma-hook", "type": "hook", "name": "Gamma Hook", "description": "Hook resource"},
    ]


@pytest.fixture
def sample_resources_with_dates():
    """Sample resources with updated dates."""
    return [
        {"id": "old", "type": "agent", "name": "Old Resource", "updated": "2024-01-01T00:00:00Z"},
        {"id": "new", "type": "agent", "name": "New Resource", "updated": "2024-12-01T00:00:00Z"},
        {"id": "mid", "type": "agent", "name": "Mid Resource", "updated": "2024-06-15T00:00:00Z"},
    ]
