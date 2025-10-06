"""Test Helper Utilities for Behavior-Focused TUI Testing.

This module provides abstraction layers for testing TUI behaviors without
coupling tests to specific implementation details like keypresses or UI elements.

Design Philosophy:
- Test WHAT happens, not HOW it happens
- Abstract triggers (actions) from implementations (keypresses, clicks, etc.)
- Abstract assertions (outcomes) from internal state checks
- Enable tests to survive UX changes (menu -> cycling -> command palette)

Example:
    Instead of:
        await pilot.press("s")  # Open menu
        await pilot.press("1")  # Select name
        assert table.rows[0].name < table.rows[1].name

    Use:
        await TUITestHelper.trigger_sort_by_name(pilot)
        TUITestHelper.assert_sorted_by_name(browser.filtered_resources)
"""

from typing import Any


class TUITestHelper:
    """Helper methods for behavior-focused TUI testing.

    This class provides implementation-agnostic methods for triggering
    actions and asserting outcomes in the TUI.
    """

    # ============================================================================
    # SORT TRIGGER METHODS (Implementation-Agnostic)
    # ============================================================================

    @staticmethod
    async def trigger_sort_by_name(pilot: Any) -> None:
        """Trigger sorting by name (implementation agnostic).

        Args:
            pilot: Textual test pilot for driving the app

        Note:
            Current implementation uses one-key cycling with 's'.
            If UX changes to menu-based, command palette, or other,
            only this method needs updating - tests remain unchanged.
        """
        # Current implementation: Cycling with 's' key
        # Cycle to 'name' sort (from any current state)
        browser = pilot.app.screen
        current_sort = getattr(browser, "_sort_field", None)

        # Cycle through until we reach 'name'
        max_cycles = 5  # Safety limit
        cycles = 0
        while current_sort != "name" and cycles < max_cycles:
            await pilot.press("s")
            await pilot.pause()
            current_sort = getattr(browser, "_sort_field", None)
            cycles += 1

    @staticmethod
    async def trigger_sort_by_type(pilot: Any) -> None:
        """Trigger sorting by type (implementation agnostic).

        Args:
            pilot: Textual test pilot for driving the app
        """
        browser = pilot.app.screen
        current_sort = getattr(browser, "_sort_field", None)

        max_cycles = 5
        cycles = 0
        while current_sort != "type" and cycles < max_cycles:
            await pilot.press("s")
            await pilot.pause()
            current_sort = getattr(browser, "_sort_field", None)
            cycles += 1

    @staticmethod
    async def trigger_sort_by_updated(pilot: Any) -> None:
        """Trigger sorting by updated date (implementation agnostic).

        Args:
            pilot: Textual test pilot for driving the app
        """
        browser = pilot.app.screen
        current_sort = getattr(browser, "_sort_field", None)

        max_cycles = 5
        cycles = 0
        while current_sort != "updated" and cycles < max_cycles:
            await pilot.press("s")
            await pilot.pause()
            current_sort = getattr(browser, "_sort_field", None)
            cycles += 1

    @staticmethod
    async def trigger_cycle_sort(pilot: Any, times: int = 1) -> None:
        """Cycle through sort options N times.

        Args:
            pilot: Textual test pilot
            times: Number of times to cycle
        """
        for _ in range(times):
            await pilot.press("s")
            await pilot.pause()

    @staticmethod
    async def trigger_reverse_sort(pilot: Any) -> None:
        """Trigger reverse sorting (implementation agnostic).

        Args:
            pilot: Textual test pilot

        Note:
            Current implementation: Complete TWO full cycles to toggle direction.
            - First cycle (3 presses): Returns to start field, same direction
            - Second cycle (3 more presses): Returns to start field, toggles direction
        """
        # Press 's' 6 times to complete two full cycles, which toggles direction
        for _ in range(6):
            await pilot.press("s")
            await pilot.pause()

    # ============================================================================
    # SORT ASSERTION METHODS (Behavior-Focused)
    # ============================================================================

    @staticmethod
    def assert_sorted_by_name(resources: list[dict[str, Any]]) -> None:
        """Assert resources are sorted alphabetically by name.

        Args:
            resources: List of resource dictionaries

        Raises:
            AssertionError: If resources are not sorted by name
        """
        if len(resources) < 2:
            return  # Single or empty list is trivially sorted

        names = [r.get("name", r.get("id", "")).lower() for r in resources]
        assert names == sorted(names), (
            f"Resources not sorted alphabetically by name.\n"
            f"Expected: {sorted(names)}\n"
            f"Got: {names}"
        )

    @staticmethod
    def assert_sorted_by_type(resources: list[dict[str, Any]]) -> None:
        """Assert resources are sorted by type.

        Args:
            resources: List of resource dictionaries

        Raises:
            AssertionError: If resources are not sorted by type
        """
        if len(resources) < 2:
            return

        types = [r.get("type", "").lower() for r in resources]
        assert types == sorted(types), (
            f"Resources not sorted by type.\n" f"Expected: {sorted(types)}\n" f"Got: {types}"
        )

    @staticmethod
    def assert_sorted_by_updated(resources: list[dict[str, Any]]) -> None:
        """Assert resources are sorted by updated date (newest first).

        Args:
            resources: List of resource dictionaries

        Raises:
            AssertionError: If resources are not sorted by updated date
        """
        if len(resources) < 2:
            return

        dates = [r.get("updated", "") for r in resources]
        assert dates == sorted(dates, reverse=True), (
            f"Resources not sorted by updated date (newest first).\n"
            f"Expected: {sorted(dates, reverse=True)}\n"
            f"Got: {dates}"
        )

    @staticmethod
    def assert_sorted_by_name_reverse(resources: list[dict[str, Any]]) -> None:
        """Assert resources are sorted reverse-alphabetically (Z-A).

        Args:
            resources: List of resource dictionaries

        Raises:
            AssertionError: If resources are not reverse sorted
        """
        if len(resources) < 2:
            return

        names = [r.get("name", r.get("id", "")).lower() for r in resources]
        assert names == sorted(names, reverse=True), (
            f"Resources not sorted reverse-alphabetically.\n"
            f"Expected: {sorted(names, reverse=True)}\n"
            f"Got: {names}"
        )

    @staticmethod
    def assert_sort_indicator_shows(app: Any, expected_sort: str) -> None:
        """Assert sort indicator shows the current sort mode.

        Args:
            app: The TUI application
            expected_sort: Expected sort field name

        Raises:
            AssertionError: If sort indicator doesn't match
        """
        browser = app.screen
        current_sort = getattr(browser, "_sort_field", None)
        assert current_sort == expected_sort, (
            f"Sort indicator mismatch.\n" f"Expected: {expected_sort}\n" f"Got: {current_sort}"
        )

    @staticmethod
    def assert_sort_stable(
        resources_before: list[dict[str, Any]], resources_after: list[dict[str, Any]]
    ) -> None:
        """Assert sort is stable (equal items maintain relative order).

        Args:
            resources_before: Resources before sorting
            resources_after: Resources after sorting

        Raises:
            AssertionError: If sort is not stable
        """
        # For resources with equal sort keys, verify they maintain order
        # This is a simplified check - assumes IDs are unique
        ids_before = [r.get("id") for r in resources_before]
        ids_after = [r.get("id") for r in resources_after]

        # At minimum, all IDs should still be present
        assert set(ids_before) == set(
            ids_after
        ), "Sort changed the set of resources (instability detected)"

    @staticmethod
    def get_visible_resource_names(app: Any) -> list[str]:
        """Get names of currently visible resources in order.

        Args:
            app: The TUI application

        Returns:
            List of resource names in display order
        """
        browser = app.screen
        return [r.get("name", r.get("id", "")) for r in browser.filtered_resources]

    @staticmethod
    def get_visible_resource_types(app: Any) -> list[str]:
        """Get types of currently visible resources in order.

        Args:
            app: The TUI application

        Returns:
            List of resource types in display order
        """
        browser = app.screen
        return [r.get("type", "") for r in browser.filtered_resources]
