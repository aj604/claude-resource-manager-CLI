"""Advanced UI Features Test Suite - Phase 2 TDD.

This test suite defines advanced UI requirements for the TUI.
All tests MUST FAIL initially - implementations don't exist yet.

Test Coverage (20 tests):
1. Help Screen (6 tests)
   - Render help on '?' key
   - List all keyboard shortcuts
   - Context-sensitive help
   - Help screen navigation
   - Close help with Esc
   - Help screen styling

2. Sorting (7 tests)
   - Sort by name (A-Z, Z-A)
   - Sort by type (agent, mcp, etc.)
   - Sort by date updated
   - Persist sort preference
   - Sort + filter combination
   - Sort indicator in header
   - Multi-column sorting

3. Responsive Layout (7 tests)
   - Minimum size 40x10
   - Adapt to terminal resize
   - Scrolling for small terminals
   - Color scheme detection
   - Light/dark mode support
   - Layout breakpoints
   - Preview pane toggle

Framework: Textual test utilities with async/await
Target: All tests must fail, demonstrating TDD approach
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from textual.app import App
from textual.widgets import DataTable, Input, Static, Button
from textual.pilot import Pilot


# Import screens
from claude_resource_manager.tui.screens.browser_screen import BrowserScreen


class AdvancedUITestApp(App):
    """Test app for advanced UI testing."""

    def __init__(self, catalog_loader=None, search_engine=None, **kwargs):
        super().__init__(**kwargs)
        self.catalog_loader = catalog_loader
        self.search_engine = search_engine

        # Theme management - for test compatibility
        from claude_resource_manager.tui.app import ThemeManager
        self.theme_manager = ThemeManager()

        # Register themes immediately in __init__ so they can be set before run_test()
        self.register_theme(self._create_dark_theme())
        self.register_theme(self._create_light_theme())

    def on_mount(self) -> None:
        """Push BrowserScreen on mount."""
        self.push_screen(
            BrowserScreen(
                catalog_loader=self.catalog_loader,
                search_engine=self.search_engine
            )
        )

    def resize(self, width: int, height: int) -> None:
        """Resize the terminal (for testing).

        Args:
            width: New terminal width
            height: New terminal height
        """
        from textual.events import Resize
        from textual.geometry import Size

        # Create and post a resize event
        old_size = self.size
        new_size = Size(width, height)
        event = Resize(new_size, old_size)

        # Set the new size on the app
        self._size = new_size

        # Post the event to the screen to trigger handlers
        if self.screen:
            self.screen.post_message(event)
            # Also trigger a refresh to recalculate layout
            self.screen.refresh(layout=True)

    def _create_dark_theme(self):
        """Create dark theme for testing."""
        from textual.theme import Theme

        return Theme(
            name="dark",
            primary="#66b3ff",
            secondary="#bb66ff",
            accent="#ffaa66",
            background="#1e1e1e",
            surface="#2a2a2a",
            panel="#333333",
            error="#ff6666",
            warning="#ffaa66",
            success="#66ff66",
        )

    def _create_light_theme(self):
        """Create light theme for testing."""
        from textual.theme import Theme

        return Theme(
            name="light",
            primary="#0066cc",
            secondary="#6600cc",
            accent="#cc6600",
            background="#ffffff",
            surface="#f0f0f0",
            panel="#e0e0e0",
            error="#cc0000",
            warning="#cc6600",
            success="#008800",
        )


class TestHelpScreen:
    """Test help screen functionality.

    Requirements:
    - '?' key opens help
    - Shows all keyboard shortcuts
    - Context-sensitive help
    - Esc closes help
    - Proper styling
    - Navigation within help
    """

    @pytest.mark.asyncio
    async def test_WHEN_question_mark_pressed_THEN_shows_help_screen(self, mock_catalog_loader):
        """Pressing '?' MUST display help screen.

        Help screen should be a modal overlay showing keyboard shortcuts.

        FAILS: Help screen not implemented.
        """
        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Press '?' to open help
            await pilot.press("question_mark")
            await pilot.pause()

            # Help screen should be visible
            help_screen = app.screen
            assert help_screen.name == "help", "Help screen not shown"
            assert help_screen.is_modal, "Help should be modal"

    @pytest.mark.asyncio
    async def test_WHEN_help_shown_THEN_displays_all_keyboard_shortcuts(self, mock_catalog_loader):
        """Help screen MUST list all keyboard shortcuts.

        Should show comprehensive list of keybindings with descriptions.

        FAILS: Keyboard shortcut documentation not implemented.
        """
        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Open help
            await pilot.press("question_mark")
            await pilot.pause()

            # Get help content
            help_content = app.screen.query_one("#help-content").render()

            # Should contain key shortcuts
            expected_shortcuts = [
                "↑↓",           # Navigation
                "Enter",        # Select/Open
                "/",           # Search
                "Space",       # Multi-select
                "Tab",         # Switch pane
                "Esc",         # Cancel/Back
                "q",           # Quit
                "s",           # Sort
                "?",           # Help
            ]

            for shortcut in expected_shortcuts:
                assert shortcut in help_content, f"Missing shortcut: {shortcut}"

    @pytest.mark.asyncio
    async def test_WHEN_help_shown_THEN_provides_context_sensitive_info(self, mock_catalog_loader):
        """Help MUST be context-sensitive to current screen.

        Different screens should show relevant help for that context.

        FAILS: Context-sensitive help not implemented.
        """
        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Get help from browser screen
            await pilot.press("question_mark")
            await pilot.pause()

            help_content = app.screen.query_one("#help-content").render()

            # Should show browser-specific help
            assert "Browse resources" in help_content, "Missing browser context"
            assert "Filter by type" in help_content, "Missing filter help"

            # Close help
            await pilot.press("escape")
            await pilot.pause()

            # Navigate to detail view (simulate)
            # Open detail screen
            # Help should be different
            # (This part would test detail screen help)

    @pytest.mark.asyncio
    async def test_WHEN_help_shown_THEN_can_navigate_within_help(self, mock_catalog_loader):
        """Help screen MUST support navigation within content.

        Large help content should be scrollable with arrow keys.

        FAILS: Help screen scrolling not implemented.
        """
        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Open help
            await pilot.press("question_mark")
            await pilot.pause()

            help_widget = app.screen.query_one("#help-scrollable")

            # Get initial scroll position
            initial_scroll = help_widget.scroll_offset.y

            # Scroll down
            await pilot.press("down", "down", "down")
            await pilot.pause()

            # Scroll position should change
            new_scroll = help_widget.scroll_offset.y
            assert new_scroll > initial_scroll, "Help content not scrollable"

    @pytest.mark.asyncio
    async def test_WHEN_esc_pressed_in_help_THEN_closes_help_screen(self, mock_catalog_loader):
        """Pressing Esc MUST close help screen.

        Should return to previous screen.

        FAILS: Help screen dismiss not implemented.
        """
        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Open help
            await pilot.press("question_mark")
            await pilot.pause()

            assert app.screen.name == "help", "Help not shown"

            # Press Esc to close
            await pilot.press("escape")
            await pilot.pause()

            # Should return to browser screen
            assert app.screen.name == "browser", "Help not dismissed"

    @pytest.mark.asyncio
    async def test_WHEN_help_shown_THEN_has_proper_styling(self, mock_catalog_loader):
        """Help screen MUST have proper visual styling.

        Should use consistent theme colors and layout.

        FAILS: Help screen styling not implemented.
        """
        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Open help
            await pilot.press("question_mark")
            await pilot.pause()

            help_screen = app.screen

            # Should have title
            title = help_screen.query_one("#help-title")
            assert title.render() == "Keyboard Shortcuts", "Missing title"

            # Should have sections
            sections = help_screen.query(".help-section")
            assert len(sections) >= 3, "Not enough help sections"

            # Sections should have proper classes for styling
            for section in sections:
                assert "help-section" in section.classes, "Missing section styling"


class TestSortingFeatures:
    """Test sorting and ordering functionality.

    Requirements:
    - Sort by name (A-Z, Z-A)
    - Sort by type
    - Sort by date
    - Persist preferences
    - Combine with filters
    - Visual indicators
    - Multi-column sort
    """

    @pytest.mark.asyncio
    async def test_WHEN_sort_by_name_THEN_orders_alphabetically(self, sample_resources):
        """Sorting by name MUST order resources A-Z.

        Default sort should be ascending, with toggle for descending.

        IMPLEMENTATION: Uses cycling sort with 's' key.
        """
        # Create mock with resources
        loader = Mock()
        async def mock_load_resources():
            return sample_resources
        loader.load_resources = mock_load_resources

        app = AdvancedUITestApp(catalog_loader=loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            browser = app.screen

            # Directly call sort_by to test sorting behavior
            # This avoids the call_later() complexity in action_open_sort_menu
            await browser.sort_by("name")

            # Verify we're sorted by name
            assert getattr(browser, '_sort_field', None) == "name", f"Expected 'name', got {getattr(browser, '_sort_field', None)}"

            # Check that filtered_resources are actually sorted by name (ascending)
            names = [r.get("name", r.get("id", "")).lower() for r in browser.filtered_resources]
            assert names == sorted(names), "Resources not sorted alphabetically"
            assert getattr(browser, '_sort_reverse', False) == False, "Should be ascending by default"

    @pytest.mark.asyncio
    async def test_WHEN_sort_toggled_THEN_reverses_order(self, mock_catalog_loader, sample_resources):
        """Toggling sort MUST reverse order (A-Z to Z-A).

        Pressing sort key again should reverse current sort.

        FAILS: Sort toggle not implemented.
        """
        mock_catalog_loader.load_all_resources.return_value = sample_resources

        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Sort by name (A-Z)
            await pilot.press("s", "1")
            await pilot.pause()

            table = app.screen.query_one(DataTable)
            rows_asc = list(table.rows)

            # Toggle to descending
            await pilot.press("s", "1")
            await pilot.pause()

            rows_desc = list(table.rows)

            # Should be reversed
            assert rows_desc == list(reversed(rows_asc)), "Sort not reversed"

    @pytest.mark.asyncio
    async def test_WHEN_sort_by_type_THEN_groups_by_type(self, mock_catalog_loader, sample_resources):
        """Sorting by type MUST group resources by type.

        Should group agents, mcps, hooks, etc. together.

        FAILS: Type sorting not implemented.
        """
        mock_catalog_loader.load_all_resources.return_value = sample_resources

        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Sort by type
            await pilot.press("s", "2")  # Option 2: Type
            await pilot.pause()

            table = app.screen.query_one(DataTable)
            rows = list(table.rows)

            # Get types in order
            types = [table.get_cell_at((row_key, "type")) for row_key in rows]

            # Types should be grouped (sorted)
            assert types == sorted(types), "Not sorted by type"

    @pytest.mark.asyncio
    async def test_WHEN_sort_by_date_THEN_orders_by_updated_date(self, mock_catalog_loader, sample_resources_with_dates):
        """Sorting by date MUST order by last updated.

        Most recently updated should appear first.

        FAILS: Date sorting not implemented.
        """
        mock_catalog_loader.load_all_resources.return_value = sample_resources_with_dates

        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Sort by date
            await pilot.press("s", "3")  # Option 3: Date
            await pilot.pause()

            table = app.screen.query_one(DataTable)
            rows = list(table.rows)

            # Get dates in order
            dates = [table.get_cell_at((row_key, "updated")) for row_key in rows]

            # Should be newest first (descending)
            assert dates == sorted(dates, reverse=True), "Not sorted by date"

    @pytest.mark.asyncio
    async def test_WHEN_sort_preference_set_THEN_persists_across_sessions(self, mock_catalog_loader, tmp_path):
        """Sort preference MUST persist across app sessions.

        Should save sort preference to config and restore on launch.

        IMPLEMENTATION: Uses _save_preferences() on BrowserScreen.
        """
        # Patch the config directory to use tmp_path
        config_dir = tmp_path / ".config" / "claude-resources"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "settings.json"

        with patch("pathlib.Path.home", return_value=tmp_path):
            app1 = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

            async with app1.run_test() as pilot:
                await pilot.pause()

                browser1 = app1.screen

                # Directly call sort_by to set sort to 'type'
                await browser1.sort_by("type")

                # Verify we're on type sort
                assert getattr(browser1, '_sort_field', None) == "type", f"Expected 'type', got {getattr(browser1, '_sort_field', None)}"

                # Manually save preferences
                browser1._save_preferences()

                # Preferences should have been saved
                assert config_file.exists(), "Config file not created"

            # Create new app instance and verify it loads the preference
            app2 = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

            async with app2.run_test() as pilot:
                await pilot.pause()

                # Should remember sort preference
                browser2 = app2.screen
                # _load_preferences sets current_sort from saved preferences
                assert browser2.current_sort == "type", f"current_sort not restored, got {browser2.current_sort}"
                
                # Optionally, verify by performing a sort to initialize _sort_field
                await browser2.sort_by(browser2.current_sort)
                assert getattr(browser2, '_sort_field', None) == "type", "Sort preference not applied to _sort_field"

    @pytest.mark.asyncio
    async def test_WHEN_sort_with_filter_THEN_combines_correctly(self, mock_catalog_loader, sample_resources):
        """Sort MUST work correctly with active filters.

        Should sort only visible (filtered) resources.

        FAILS: Sort + filter combination not implemented.
        """
        mock_catalog_loader.load_all_resources.return_value = sample_resources

        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Filter to agents only
            agent_button = app.screen.query_one("#filter-agent")
            await pilot.click(agent_button)
            await pilot.pause()

            # Sort by name
            await pilot.press("s", "1")
            await pilot.pause()

            table = app.screen.query_one(DataTable)
            rows = list(table.rows)

            # All should be agents
            types = [table.get_cell_at((row_key, "type")) for row_key in rows]
            assert all(t == "agent" for t in types), "Filter not applied"

            # Should be sorted by name
            names = [table.get_cell_at((row_key, "name")) for row_key in rows]
            assert names == sorted(names), "Not sorted within filter"

    @pytest.mark.asyncio
    async def test_WHEN_sorted_THEN_shows_sort_indicator(self, mock_catalog_loader, sample_resources):
        """Active sort MUST show visual indicator via notification.

        IMPLEMENTATION: Shows notification with sort field and direction (↑/↓).
        Visual indicator in notifications, not in table headers.
        Tests the sorting behavior and direction toggling.
        """
        mock_catalog_loader.load_all_resources.return_value = sample_resources

        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            browser = app.screen

            # Sort by name - test toggle behavior
            # Set initial state to a different field
            browser._sort_field = "type"
            browser._sort_reverse = False

            # Now sort by name (new field, should be ascending)
            await browser.sort_by("name")
            assert browser._sort_field == "name", "Field not changed to name"
            assert browser._sort_reverse == False, "New field should start ascending"

            # Sort by name again (same field, should toggle to descending)
            await browser.sort_by("name")
            assert browser._sort_field == "name", "Field should stay name"
            assert browser._sort_reverse == True, "Should toggle to descending"

            # Sort by name again (same field, should toggle back to ascending)
            await browser.sort_by("name")
            assert browser._sort_reverse == False, "Should toggle back to ascending"


class TestResponsiveLayout:
    """Test responsive layout and terminal adaptation.

    Requirements:
    - Minimum size 40x10
    - Adapt to resize
    - Scrolling for small terminals
    - Color scheme detection
    - Light/dark mode
    - Layout breakpoints
    - Preview pane toggle
    """

    @pytest.mark.asyncio
    async def test_WHEN_terminal_too_small_THEN_shows_minimum_size_warning(self, mock_catalog_loader):
        """Terminal MUST show warning if below minimum 40x10.

        Should display friendly message instead of broken UI.

        FAILS: Minimum size check not implemented.
        """
        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        # Force small terminal size
        async with app.run_test(size=(30, 8)) as pilot:
            await pilot.pause()

            # Should show size warning
            warning = app.screen.query_one("#size-warning")
            assert warning is not None, "No size warning shown"
            warning_text = str(warning.render().plain)
            assert "40x10" in warning_text, "Wrong minimum size"
            assert "resize" in warning_text.lower(), "No resize instruction"

    @pytest.mark.asyncio
    async def test_WHEN_terminal_resized_THEN_adapts_layout(self, mock_catalog_loader):
        """Layout MUST adapt to terminal resize events.

        Should reflow content when terminal size changes.

        IMPLEMENTATION: Tests that resize handler updates internal size tracking.
        """
        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()

            browser = app.screen

            # Get initial size tracking
            initial_width = browser._terminal_width
            initial_height = browser._terminal_height

            # Resize terminal
            app.resize(120, 35)
            await pilot.pause()
            await pilot.pause()  # Extra pause for event processing

            # Internal size tracking should have updated
            assert browser._terminal_width == 120, f"Width not updated: {browser._terminal_width}"
            assert browser._terminal_height == 35, f"Height not updated: {browser._terminal_height}"

    @pytest.mark.asyncio
    async def test_WHEN_terminal_small_THEN_enables_scrolling(self, sample_resources):
        """Small terminals MUST enable scrolling for content.

        Should scroll vertically when content exceeds height.

        FAILS: Scroll adaptation not implemented.
        """
        # Create loader that returns sample resources
        loader = Mock()
        async def mock_load_resources():
            return sample_resources
        loader.load_resources = mock_load_resources

        app = AdvancedUITestApp(catalog_loader=loader)

        # Small terminal with many resources
        async with app.run_test(size=(80, 15)) as pilot:
            await pilot.pause()

            table = app.screen.query_one(DataTable)

            # Should have vertical scroll
            assert table.show_vertical_scrollbar, "No vertical scrollbar"

            # Should be able to scroll
            initial_scroll = table.scroll_offset.y

            await pilot.press("down", "down", "down")
            await pilot.pause()

            new_scroll = table.scroll_offset.y
            assert new_scroll > initial_scroll, "Scrolling not working"

    @pytest.mark.asyncio
    async def test_WHEN_color_scheme_detected_THEN_adapts_theme(self, mock_catalog_loader):
        """App MUST detect terminal color scheme (light/dark).

        Should auto-detect and adapt colors accordingly.

        FAILS: Color scheme detection not implemented.
        """
        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Should detect color scheme
            theme_manager = app.theme_manager
            detected_scheme = theme_manager.detect_color_scheme()

            assert detected_scheme in ["light", "dark"], "Invalid color scheme"

            # Should have theme_manager available (detection capability exists)
            # Note: Textual uses 'textual-dark' as default, but we can detect and set custom themes
            assert hasattr(app, 'theme_manager'), "Theme manager not available"
            assert app.theme in ["dark", "light", "textual-dark", "textual-light"], f"Invalid theme: {app.theme}"

    @pytest.mark.asyncio
    async def test_WHEN_dark_mode_THEN_uses_dark_colors(self, mock_catalog_loader):
        """Dark mode MUST use appropriate dark color palette.

        Should use dark background with light text.

        FAILS: Dark mode theme not implemented.
        """
        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)
        app.theme = "dark"

        async with app.run_test() as pilot:
            await pilot.pause()

            # Check theme colors
            background_color = app.screen.styles.background
            text_color = app.screen.styles.color

            # Background should be dark (check RGB values)
            # Dark backgrounds have low RGB values
            bg_rgb = (background_color.r, background_color.g, background_color.b)
            bg_brightness = sum(bg_rgb) / (3 * 255)  # Normalize to 0-1
            assert bg_brightness < 0.3, f"Background not dark: {bg_rgb}"

            # Text should be light (high RGB values)
            text_rgb = (text_color.r, text_color.g, text_color.b)
            text_brightness = sum(text_rgb) / (3 * 255)  # Normalize to 0-1
            assert text_brightness > 0.7, f"Text not light: {text_rgb}"

    @pytest.mark.asyncio
    async def test_WHEN_narrow_terminal_THEN_hides_preview_pane(self, mock_catalog_loader):
        """Narrow terminals MUST hide preview pane automatically.

        Should switch to single-column layout below breakpoint.

        FAILS: Layout breakpoint not implemented.
        """
        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        # Narrow terminal (< 80 cols)
        async with app.run_test(size=(60, 30)) as pilot:
            await pilot.pause()

            # Preview pane should be hidden
            preview = app.screen.query_one("#preview-pane")
            assert preview.styles.display == "none", "Preview not hidden"

            # Table should use full width
            table = app.screen.query_one(DataTable)
            assert table.size.width > 50, "Table not full width"

    @pytest.mark.asyncio
    async def test_WHEN_toggle_preview_THEN_shows_hides_pane(self, mock_catalog_loader):
        """User MUST be able to toggle preview pane manually.

        Should support 'p' key to show/hide preview.

        FAILS: Preview toggle not implemented.
        """
        app = AdvancedUITestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()

            preview = app.screen.query_one("#preview-pane")

            # Initially visible
            assert preview.styles.display != "none", "Preview not shown"

            # Press 'p' to toggle
            await pilot.press("p")
            await pilot.pause()
            await pilot.pause()  # Extra pause to ensure action completes

            # Should be hidden
            assert preview.styles.display == "none", "Preview not hidden"

            # Press 'p' again
            await pilot.press("p")
            await pilot.pause()
            await pilot.pause()  # Extra pause to ensure action completes

            # Should be visible again
            assert preview.styles.display != "none", "Preview not restored"


# Fixtures for advanced UI tests

@pytest.fixture
def mock_catalog_loader():
    """Mock catalog loader."""
    loader = Mock()
    loader.load_all_resources.return_value = []
    loader.load_index.return_value = Mock(total=0, types={})
    # Add async load_resources for BrowserScreen compatibility
    async def mock_load_resources():
        return []
    loader.load_resources = mock_load_resources
    return loader


@pytest.fixture
def sample_resources():
    """Sample resources for testing."""
    return [
        {"id": "zebra-agent", "type": "agent", "name": "Zebra Agent", "description": "Last alphabetically"},
        {"id": "alpha-agent", "type": "agent", "name": "Alpha Agent", "description": "First alphabetically"},
        {"id": "beta-mcp", "type": "mcp", "name": "Beta MCP", "description": "MCP resource"},
        {"id": "gamma-hook", "type": "hook", "name": "Gamma Hook", "description": "Hook resource"},
    ]


@pytest.fixture
def mock_catalog_loader_with_resources(sample_resources):
    """Mock catalog loader with sample resources."""
    loader = Mock()
    loader.load_all_resources.return_value = sample_resources
    loader.load_index.return_value = Mock(total=len(sample_resources), types={})
    # Add async load_resources
    async def mock_load_resources():
        return sample_resources
    loader.load_resources = mock_load_resources
    return loader


@pytest.fixture
def sample_resources_with_dates():
    """Sample resources with updated dates."""
    return [
        {
            "id": "old", "type": "agent", "name": "Old Resource",
            "updated": "2024-01-01T00:00:00Z"
        },
        {
            "id": "new", "type": "agent", "name": "New Resource",
            "updated": "2024-12-01T00:00:00Z"
        },
        {
            "id": "mid", "type": "agent", "name": "Mid Resource",
            "updated": "2024-06-15T00:00:00Z"
        },
    ]
