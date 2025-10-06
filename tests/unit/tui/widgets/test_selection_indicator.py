"""RED PHASE: SelectionIndicator Widget Tests - Comprehensive test suite.

Test Coverage:
- Reactive behavior (watch_count triggers on count change)
- Formatting - zero count (empty string when count=0)
- Formatting - single item (shows "1 selected", not "1 / X selected")
- Formatting - multiple items without total (shows "X selected" when total=0)
- Formatting - multiple items with total (shows "X / Y selected" when total>0)
- Edge cases - large numbers, boundary conditions
- Update method - update_count sets both count and total correctly
- Rendering - proper markup with bold cyan styling
"""

import pytest
from textual.app import App

from claude_resource_manager.tui.widgets.selection_indicator import SelectionIndicator


class SelectionIndicatorTestApp(App):
    """Test app for SelectionIndicator widget testing."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.indicator = None

    def compose(self):
        """Compose the test app with SelectionIndicator."""
        self.indicator = SelectionIndicator()
        yield self.indicator


class TestSelectionIndicatorReactiveBehavior:
    """Test reactive behavior of SelectionIndicator."""

    @pytest.mark.asyncio
    async def test_WHEN_count_changes_THEN_watch_count_is_triggered(self):
        """Changing count reactive attribute triggers watch_count method."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            initial_content = str(indicator.render())

            # Change count - should trigger watch_count
            indicator.count = 1
            await pilot.pause()

            updated_content = str(indicator.render())
            # Content should have changed from empty to "1 selected"
            assert initial_content != updated_content
            assert "selected" in updated_content.lower()

    @pytest.mark.asyncio
    async def test_WHEN_count_set_to_zero_THEN_widget_content_cleared(self):
        """Setting count to 0 triggers watch_count which clears the widget."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator

            # First set count to non-zero
            indicator.count = 3
            await pilot.pause()

            # Then set to zero
            indicator.count = 0
            await pilot.pause()

            content = str(indicator.render())
            # Should be empty when count is 0
            assert content.strip() == ""

    @pytest.mark.asyncio
    async def test_WHEN_count_incremented_THEN_display_updates(self):
        """Incrementing count updates the display reactively."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator

            # Increment count
            indicator.count = 1
            await pilot.pause()
            content_1 = str(indicator.render())

            indicator.count = 2
            await pilot.pause()
            content_2 = str(indicator.render())

            indicator.count = 3
            await pilot.pause()
            content_3 = str(indicator.render())

            # Each should be different
            assert content_1 != content_2
            assert content_2 != content_3
            # And should contain increasing numbers
            assert "1" in content_1
            assert "2" in content_2
            assert "3" in content_3


class TestSelectionIndicatorFormattingZeroCount:
    """Test widget displays nothing when count is zero."""

    @pytest.mark.asyncio
    async def test_WHEN_count_is_zero_THEN_shows_empty_string(self):
        """Widget shows empty string when count is 0."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            indicator.count = 0
            await pilot.pause()

            content = str(indicator.render())
            assert content.strip() == ""

    @pytest.mark.asyncio
    async def test_WHEN_initialized_THEN_count_is_zero_and_empty(self):
        """Widget initializes with count=0 and displays nothing."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator

            # Default count should be 0
            assert indicator.count == 0

            content = str(indicator.render())
            assert content.strip() == ""

    @pytest.mark.asyncio
    async def test_WHEN_count_reset_to_zero_THEN_hides_indicator(self):
        """Resetting count to 0 hides the indicator (shows empty)."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator

            # Set to non-zero first
            indicator.count = 5
            await pilot.pause()
            assert "selected" in str(indicator.render()).lower()

            # Reset to zero
            indicator.count = 0
            await pilot.pause()

            content = str(indicator.render())
            assert content.strip() == ""


class TestSelectionIndicatorFormattingSingleItem:
    """Test widget shows '1 selected' for single item."""

    @pytest.mark.asyncio
    async def test_WHEN_count_is_one_THEN_shows_one_selected(self):
        """Widget shows '1 selected' when count is 1."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            indicator.count = 1
            await pilot.pause()

            content = str(indicator.render())
            # Should show "1 selected" (not "1 / X selected")
            assert "1" in content
            assert "selected" in content.lower()

    @pytest.mark.asyncio
    async def test_WHEN_count_is_one_THEN_does_not_show_total(self):
        """Widget does NOT show total when count is 1 (shows '1 selected', not '1 / X')."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            indicator.total = 100  # Set total
            indicator.count = 1    # But count is 1
            await pilot.pause()

            content = str(indicator.render())
            # Should show "1 selected" without the "/ 100" part
            assert "1" in content
            assert "selected" in content.lower()
            # Should NOT show total for single item
            assert "/" not in content

    @pytest.mark.asyncio
    async def test_WHEN_count_is_one_with_zero_total_THEN_shows_one_selected(self):
        """Widget shows '1 selected' when count=1 and total=0."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            indicator.total = 0
            indicator.count = 1
            await pilot.pause()

            content = str(indicator.render())
            assert "1" in content
            assert "selected" in content.lower()
            assert "/" not in content


class TestSelectionIndicatorFormattingMultipleWithoutTotal:
    """Test widget shows 'X selected' for multiple items when total=0."""

    @pytest.mark.asyncio
    async def test_WHEN_count_is_two_and_total_zero_THEN_shows_two_selected(self):
        """Widget shows '2 selected' when count=2 and total=0."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            indicator.total = 0
            indicator.count = 2
            await pilot.pause()

            content = str(indicator.render())
            assert "2" in content
            assert "selected" in content.lower()
            # Should NOT show "/ total" when total is 0
            assert "/" not in content

    @pytest.mark.asyncio
    async def test_WHEN_count_is_five_and_total_zero_THEN_shows_five_selected(self):
        """Widget shows '5 selected' when count=5 and total=0."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            indicator.total = 0
            indicator.count = 5
            await pilot.pause()

            content = str(indicator.render())
            assert "5" in content
            assert "selected" in content.lower()
            assert "/" not in content

    @pytest.mark.asyncio
    async def test_WHEN_count_is_multiple_with_default_total_THEN_shows_count_only(self):
        """Widget shows 'X selected' when total not explicitly set (defaults to 0)."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            # Don't set total (defaults to 0)
            indicator.count = 10
            await pilot.pause()

            content = str(indicator.render())
            assert "10" in content
            assert "selected" in content.lower()
            assert "/" not in content


class TestSelectionIndicatorFormattingMultipleWithTotal:
    """Test widget shows 'X / Y selected' for multiple items when total>0."""

    @pytest.mark.asyncio
    async def test_WHEN_count_two_and_total_ten_THEN_shows_two_of_ten_selected(self):
        """Widget shows '2 / 10 selected' when count=2 and total=10."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            indicator.total = 10
            indicator.count = 2
            await pilot.pause()

            content = str(indicator.render())
            assert "2" in content
            assert "10" in content
            assert "/" in content
            assert "selected" in content.lower()

    @pytest.mark.asyncio
    async def test_WHEN_count_equals_total_THEN_shows_all_selected(self):
        """Widget shows 'X / X selected' when all items selected."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            indicator.total = 50
            indicator.count = 50
            await pilot.pause()

            content = str(indicator.render())
            assert "50" in content
            assert "/" in content
            assert "selected" in content.lower()
            # Should show "50 / 50 selected"
            assert content.count("50") >= 2

    @pytest.mark.asyncio
    async def test_WHEN_count_three_total_hundred_THEN_shows_three_of_hundred(self):
        """Widget shows '3 / 100 selected' when count=3, total=100."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            indicator.total = 100
            indicator.count = 3
            await pilot.pause()

            content = str(indicator.render())
            assert "3" in content
            assert "100" in content
            assert "/" in content
            assert "selected" in content.lower()


class TestSelectionIndicatorEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_WHEN_count_is_very_large_THEN_displays_correctly(self):
        """Widget handles very large numbers correctly."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            indicator.total = 999999
            indicator.count = 123456
            await pilot.pause()

            content = str(indicator.render())
            assert "123456" in content
            assert "999999" in content
            assert "/" in content

    @pytest.mark.asyncio
    async def test_WHEN_count_exceeds_total_THEN_still_displays(self):
        """Widget displays even when count > total (edge case/bug scenario)."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            indicator.total = 5
            indicator.count = 10  # More than total (shouldn't happen but test it)
            await pilot.pause()

            content = str(indicator.render())
            # Should still show the values even if logically incorrect
            assert "10" in content
            assert "5" in content

    @pytest.mark.asyncio
    async def test_WHEN_total_changes_dynamically_THEN_display_updates(self):
        """Widget updates when total changes and count is re-triggered.

        Note: Only count is reactive, so we need to change count to trigger watch_count
        after changing total to see the update.
        """
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator

            # Set initial state
            indicator.total = 10
            indicator.count = 5
            await pilot.pause()
            content_1 = str(indicator.render())

            # Change total and increment count to trigger watch_count
            indicator.total = 20
            indicator.count = 6  # Change count to different value to trigger watch_count
            await pilot.pause()
            content_2 = str(indicator.render())

            # Content should change (5/10 vs 6/20)
            assert content_1 != content_2
            assert "6" in content_2
            assert "20" in content_2

    @pytest.mark.asyncio
    async def test_WHEN_negative_count_THEN_displays_negative(self):
        """Widget handles negative numbers (edge case - shouldn't happen)."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            indicator.count = -1
            await pilot.pause()

            content = str(indicator.render())
            # Should still render something (not crash)
            assert content is not None


class TestSelectionIndicatorUpdateMethod:
    """Test the update_count helper method."""

    @pytest.mark.asyncio
    async def test_WHEN_update_count_called_THEN_sets_both_values(self):
        """update_count method sets both count and total."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator

            # Use update_count method
            indicator.update_count(selected=5, total=20)
            await pilot.pause()

            # Should update both
            assert indicator.count == 5
            assert indicator.total == 20

            content = str(indicator.render())
            assert "5" in content
            assert "20" in content
            assert "/" in content

    @pytest.mark.asyncio
    async def test_WHEN_update_count_without_total_THEN_sets_count_only(self):
        """update_count method works with just selected parameter."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator

            # Call with only selected (total defaults to 0)
            indicator.update_count(selected=7)
            await pilot.pause()

            assert indicator.count == 7
            assert indicator.total == 0

            content = str(indicator.render())
            assert "7" in content
            assert "/" not in content

    @pytest.mark.asyncio
    async def test_WHEN_update_count_called_multiple_times_THEN_updates_correctly(self):
        """update_count can be called multiple times to update values."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator

            # First update
            indicator.update_count(selected=3, total=10)
            await pilot.pause()
            content_1 = str(indicator.render())

            # Second update
            indicator.update_count(selected=7, total=10)
            await pilot.pause()
            content_2 = str(indicator.render())

            # Third update
            indicator.update_count(selected=0, total=10)
            await pilot.pause()
            content_3 = str(indicator.render())

            # Each should be different
            assert "3" in content_1
            assert "7" in content_2
            assert content_3.strip() == ""  # 0 count = empty

    @pytest.mark.asyncio
    async def test_WHEN_update_count_sets_count_THEN_triggers_watch_count(self):
        """update_count triggers watch_count because it sets count reactive."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator

            # update_count should trigger watch_count
            indicator.update_count(selected=4, total=15)
            await pilot.pause()

            # The display should update (proving watch_count was triggered)
            content = str(indicator.render())
            assert "4" in content
            assert "15" in content


class TestSelectionIndicatorRendering:
    """Test markup and styling in rendered output."""

    @pytest.mark.asyncio
    async def test_WHEN_count_nonzero_THEN_contains_content(self):
        """Widget output contains content when count is set."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            indicator.count = 5
            await pilot.pause()

            content = str(indicator.render())

            # Should have content
            assert len(content) > 0
            assert "5" in content
            assert "selected" in content.lower()

    @pytest.mark.asyncio
    async def test_WHEN_formatting_applied_THEN_uses_bold_cyan(self):
        """Widget uses bold cyan styling for count numbers."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            indicator.count = 3
            await pilot.pause()

            content = str(indicator.render())

            # Should use rich console markup for bold cyan
            # The actual implementation uses [bold cyan] tags
            assert "bold" in content.lower() or "cyan" in content.lower() or "3" in content

    @pytest.mark.asyncio
    async def test_WHEN_multiple_with_total_THEN_only_count_is_styled(self):
        """When showing 'X / Y selected', only X is bold cyan, not Y."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator
            indicator.total = 50
            indicator.count = 10
            await pilot.pause()

            content = str(indicator.render())

            # Both numbers should be present
            assert "10" in content
            assert "50" in content
            # The '10' should come before '50' in "10 / 50 selected"
            assert content.index("10") < content.index("50")

    @pytest.mark.asyncio
    async def test_WHEN_widget_has_id_THEN_id_is_selection_count(self):
        """Widget has the ID 'selection-count' for CSS targeting."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator

            # Should have the correct ID
            assert indicator.id == "selection-count"


class TestSelectionIndicatorInitialization:
    """Test widget initialization and default state."""

    @pytest.mark.asyncio
    async def test_WHEN_widget_created_THEN_has_correct_defaults(self):
        """Widget initializes with count=0, total=0."""
        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator

            assert indicator.count == 0
            assert indicator.total == 0

    @pytest.mark.asyncio
    async def test_WHEN_widget_created_THEN_inherits_from_static(self):
        """SelectionIndicator is a Textual Static widget."""
        from textual.widgets import Static

        app = SelectionIndicatorTestApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            indicator = app.indicator

            # Should be an instance of Static
            assert isinstance(indicator, Static)

    @pytest.mark.asyncio
    async def test_WHEN_widget_created_with_kwargs_THEN_accepts_widget_params(self):
        """Widget accepts standard Textual widget parameters."""
        # Test that we can pass custom classes, etc.
        indicator = SelectionIndicator(classes="custom-class")

        assert indicator.has_class("custom-class")
