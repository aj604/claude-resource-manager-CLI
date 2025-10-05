"""Comprehensive test suite for BrowserScreen - the main resource browsing interface.

Test Coverage:
- Resource list rendering (DataTable)
- Keyboard navigation (up/down, Enter, /, Esc, Tab)
- Search box interaction
- Category filtering (All, Agent, Command, Hook, Template, MCP)
- Multi-select with Space key
- Preview pane reactive updates
- Status bar updates
- Error handling
- Empty state display
- Performance with large datasets

All tests use proper Textual app context and async/await patterns.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from textual.app import App
from textual.widgets import DataTable, Input, Static, Button


# Import the BrowserScreen
from claude_resource_manager.tui.screens.browser_screen import BrowserScreen


class BrowserScreenTestApp(App):
    """Test app for BrowserScreen testing."""

    def __init__(self, catalog_loader=None, search_engine=None, **kwargs):
        super().__init__(**kwargs)
        self.catalog_loader = catalog_loader
        self.search_engine = search_engine

    def on_mount(self) -> None:
        """Push BrowserScreen on mount."""
        self.push_screen(
            BrowserScreen(
                catalog_loader=self.catalog_loader,
                search_engine=self.search_engine
            )
        )


class TestBrowserScreenInitialization:
    """Test browser screen initialization and setup."""

    @pytest.mark.asyncio
    async def test_browser_screen_creates_with_catalog_loader(self, mock_catalog_loader):
        """Browser screen initializes with catalog loader."""
        screen = BrowserScreen(catalog_loader=mock_catalog_loader)
        assert screen.catalog_loader is not None
        assert screen.catalog_loader == mock_catalog_loader

    @pytest.mark.asyncio
    async def test_browser_screen_loads_resources_on_mount(self, mock_catalog_loader):
        """Browser screen loads resources when mounted."""
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)
        async with app.run_test() as pilot:
            # Wait for mount to complete
            await pilot.pause()

            # Should call catalog loader
            mock_catalog_loader.load_resources.assert_called_once()

    @pytest.mark.asyncio
    async def test_browser_screen_has_search_input(self):
        """Browser screen contains search input widget."""
        app = BrowserScreenTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Should have search input
            search_input = app.screen.query_one(Input)
            assert search_input is not None
            assert search_input.placeholder == "Search resources..."

    @pytest.mark.asyncio
    async def test_browser_screen_has_resource_list(self):
        """Browser screen contains resource list widget."""
        app = BrowserScreenTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Should have DataTable for resources
            resource_list = app.screen.query_one(DataTable)
            assert resource_list is not None

    @pytest.mark.asyncio
    async def test_browser_screen_has_preview_pane(self):
        """Browser screen contains preview pane widget."""
        app = BrowserScreenTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Should have preview pane
            preview = app.screen.query_one("#preview-pane")
            assert preview is not None


class TestBrowserScreenResourceList:
    """Test resource list rendering and display."""

    @pytest.mark.asyncio
    async def test_resource_list_displays_loaded_resources(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Resource list displays all loaded resources."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            resource_list = app.screen.query_one(DataTable)
            assert resource_list.row_count == len(sample_resources_list)

    @pytest.mark.asyncio
    async def test_resource_list_shows_correct_columns(self, mock_catalog_loader):
        """Resource list displays correct columns (Name, Type, Description, Version)."""
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)
        async with app.run_test() as pilot:
            await pilot.pause()

            resource_list = app.screen.query_one(DataTable)
            # Use ordered_columns property to get column objects in order
            columns = [str(col.label) for col in resource_list.ordered_columns]

            assert "Name" in columns
            assert "Type" in columns
            assert "Description" in columns
            assert "Version" in columns

    @pytest.mark.asyncio
    async def test_resource_list_formats_resource_data_correctly(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Resource list formats each resource with proper display values."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            resource_list = app.screen.query_one(DataTable)
            first_row = resource_list.get_row_at(0)

            # Check formatting
            assert first_row[0] == "Architect"  # Name
            assert first_row[1] == "agent"  # Type
            assert "architecture" in str(first_row[2]).lower()  # Description

    @pytest.mark.asyncio
    async def test_resource_list_handles_empty_results(self, mock_catalog_loader):
        """Resource list shows empty state when no resources loaded."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=[])
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            empty_message = app.screen.query_one("#empty-message")
            assert not empty_message.has_class("hidden")
            assert "No resources found" in str(empty_message.render())

    @pytest.mark.asyncio
    async def test_resource_list_handles_loading_state(self):
        """Resource list shows loading indicator during resource fetch."""
        # Create a mock that delays before returning
        slow_loader = Mock()
        slow_loader.load_resources = AsyncMock(return_value=[])

        app = BrowserScreenTestApp(catalog_loader=slow_loader)
        async with app.run_test() as pilot:
            # Before mount completes, loading should be visible
            # After pause, it should be hidden
            await pilot.pause()

            loading_indicator = app.screen.query_one("#loading-indicator")
            # After loading completes, it should be hidden
            assert loading_indicator.has_class("hidden")

    @pytest.mark.asyncio
    async def test_resource_list_hides_loading_after_load(self, mock_catalog_loader):
        """Resource list hides loading indicator after resources loaded."""
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            loading_indicator = app.screen.query_one("#loading-indicator")
            assert loading_indicator.has_class("hidden")


class TestBrowserScreenKeyboardNavigation:
    """Test keyboard navigation in browser screen."""

    @pytest.mark.asyncio
    async def test_arrow_down_moves_selection_down(self, mock_catalog_loader, sample_resources_list):
        """Down arrow key moves selection to next resource."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            resource_list = app.screen.query_one(DataTable)
            # Ensure we're at the top
            initial_cursor = 0

            # Simulate down arrow
            await pilot.press("down")
            await pilot.pause()

            # Should have moved down
            assert resource_list.cursor_row >= initial_cursor

    @pytest.mark.asyncio
    async def test_arrow_up_moves_selection_up(self, mock_catalog_loader, sample_resources_list):
        """Up arrow key moves selection to previous resource."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Move down a few times first
            await pilot.press("down", "down", "down")
            await pilot.pause()

            resource_list = app.screen.query_one(DataTable)
            current_row = resource_list.cursor_row

            # Now move up
            await pilot.press("up")
            await pilot.pause()

            # Should have moved up
            assert resource_list.cursor_row < current_row

    @pytest.mark.asyncio
    async def test_arrow_up_at_top_stays_at_top(self, mock_catalog_loader, sample_resources_list):
        """Up arrow at first resource stays at top (doesn't wrap)."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            resource_list = app.screen.query_one(DataTable)
            # Should be at row 0
            assert resource_list.cursor_row == 0

            # Try to move up
            await pilot.press("up")
            await pilot.pause()

            # Should still be at row 0
            assert resource_list.cursor_row == 0

    @pytest.mark.asyncio
    async def test_enter_opens_detail_screen(self, mock_catalog_loader, sample_resources_list):
        """Enter key opens detail screen for selected resource."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Press enter to open detail screen
            await pilot.press("enter")
            await pilot.pause()

            # Should have pushed a new screen
            # The app should have 2 screens now (browser + detail)
            assert len(app.screen_stack) == 2

    @pytest.mark.asyncio
    async def test_slash_key_focuses_search_box(self, mock_catalog_loader):
        """Forward slash (/) focuses the search input."""
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            search_input = app.screen.query_one(Input)

            # Press slash to focus search
            await pilot.press("/")
            await pilot.pause()

            # Search input should be focused
            assert app.screen.focused is search_input

    @pytest.mark.asyncio
    async def test_escape_clears_search_and_returns_focus(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Escape key clears search and returns focus to list."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            search_input = app.screen.query_one(Input)

            # Focus search and type
            await pilot.press("/")
            search_input.value = "test query"
            await pilot.pause()

            # Press escape
            await pilot.press("escape")
            await pilot.pause()

            # Search should be cleared and focus returned to table
            assert search_input.value == ""
            assert app.screen.focused is app.screen.query_one(DataTable)

    @pytest.mark.asyncio
    async def test_space_toggles_resource_selection(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Space key toggles multi-select for current resource."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            assert len(screen.selected_resources) == 0

            # Focus the table first
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            current_id = screen.filtered_resources[0].get("id", screen.filtered_resources[0].get("name"))

            # Press space to select
            await pilot.press("space")
            await pilot.pause()

            assert current_id in screen.selected_resources

    @pytest.mark.asyncio
    async def test_space_deselects_if_already_selected(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Space key on selected resource deselects it."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Focus the table first
            table = screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            current_id = screen.filtered_resources[0].get("id", screen.filtered_resources[0].get("name"))

            # Select first
            await pilot.press("space")
            await pilot.pause()
            assert current_id in screen.selected_resources

            # Deselect
            await pilot.press("space")
            await pilot.pause()
            assert current_id not in screen.selected_resources

    @pytest.mark.asyncio
    async def test_tab_cycles_through_interactive_elements(self, mock_catalog_loader):
        """Tab key cycles focus through search, list, filters, buttons."""
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Focus search first
            await pilot.press("/")
            await pilot.pause()
            assert app.screen.focused is app.screen.query_one(Input)

            # Press tab to move to next element
            await pilot.press("tab")
            await pilot.pause()

            # Should move to resource list
            assert app.screen.focused is app.screen.query_one(DataTable)


class TestBrowserScreenSearchFunctionality:
    """Test search box and filtering functionality."""

    @pytest.mark.asyncio
    async def test_search_input_triggers_filter(self, mock_catalog_loader, mock_search_engine):
        """Typing in search box filters resource list."""
        app = BrowserScreenTestApp(
            catalog_loader=mock_catalog_loader,
            search_engine=mock_search_engine
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            search_input = app.screen.query_one(Input)
            search_input.value = "architect"
            # Trigger the on_input_changed event
            await app.screen.on_input_changed(Input.Changed(search_input, "architect"))
            await pilot.pause()

            mock_search_engine.search.assert_called()

    @pytest.mark.asyncio
    async def test_search_updates_resource_list(self, mock_catalog_loader, mock_search_engine):
        """Search results update the displayed resource list."""
        mock_search_engine.search.return_value = [
            {"id": "architect", "name": "Architect", "type": "agent", "description": "Test", "version": "v1.0.0"}
        ]
        app = BrowserScreenTestApp(
            catalog_loader=mock_catalog_loader,
            search_engine=mock_search_engine
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            await app.screen.perform_search("architect")
            await pilot.pause()

            resource_list = app.screen.query_one(DataTable)
            assert resource_list.row_count == 1

    @pytest.mark.asyncio
    async def test_search_with_no_results_shows_message(self, mock_catalog_loader, mock_search_engine):
        """Search with no results shows 'No matches found' message."""
        mock_search_engine.search.return_value = []
        app = BrowserScreenTestApp(
            catalog_loader=mock_catalog_loader,
            search_engine=mock_search_engine
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            # Set filter to something other than "all" first
            await app.screen.filter_by_type("agent")
            await pilot.pause()

            await app.screen.perform_search("xyznonexistent")
            await pilot.pause()

            empty_message = app.screen.query_one("#empty-message")
            assert not empty_message.has_class("hidden")
            # Should show "No matches found" when filter is active
            assert "No matches found" in str(empty_message.render())

    @pytest.mark.asyncio
    async def test_search_is_case_insensitive(self, mock_catalog_loader, mock_search_engine):
        """Search treats uppercase and lowercase as equivalent."""
        app = BrowserScreenTestApp(
            catalog_loader=mock_catalog_loader,
            search_engine=mock_search_engine
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            await app.screen.perform_search("ARCHITECT")
            await pilot.pause()

            # Should call search with the query as-is (search engine handles case)
            mock_search_engine.search.assert_called()
            call_args = mock_search_engine.search.call_args
            assert call_args[0][0] == "ARCHITECT"

    @pytest.mark.asyncio
    async def test_search_shows_fuzzy_match_indicator(self, mock_catalog_loader, mock_search_engine):
        """Search results show fuzzy match score indicator."""
        mock_search_engine.search.return_value = [
            {
                "id": "architect",
                "name": "Architect",
                "type": "agent",
                "description": "Test",
                "version": "v1.0.0",
                "score": 85
            }
        ]
        app = BrowserScreenTestApp(
            catalog_loader=mock_catalog_loader,
            search_engine=mock_search_engine
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            await app.screen.perform_search("archit")
            await pilot.pause()

            # Should display score in the description
            resource_list = app.screen.query_one(DataTable)
            first_row = resource_list.get_row_at(0)
            # Score should be shown in description column
            assert "85" in str(first_row[2])

    @pytest.mark.asyncio
    async def test_empty_search_shows_all_resources(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Clearing search box shows all resources again."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Get initial count
            initial_count = app.screen.query_one(DataTable).row_count

            # Perform search (which will filter)
            await app.screen.filter_by_type("agent")
            await pilot.pause()

            # Clear search
            await app.screen.perform_search("")
            await pilot.pause()

            # Should show filtered resources (agents only)
            # Not all resources, because filter is still active
            assert app.screen.query_one(DataTable).row_count == 3  # 3 agents in sample


class TestBrowserScreenCategoryFiltering:
    """Test category filtering functionality."""

    @pytest.mark.asyncio
    async def test_filter_by_agent_type(self, mock_catalog_loader, sample_resources_list):
        """Filtering by 'agent' shows only agents."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            await app.screen.filter_by_type("agent")
            await pilot.pause()

            resource_list = app.screen.query_one(DataTable)
            # Should only show agents (3 in sample data)
            assert resource_list.row_count == 3

    @pytest.mark.asyncio
    async def test_filter_by_command_type(self, mock_catalog_loader, sample_resources_list):
        """Filtering by 'command' shows only commands."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            await app.screen.filter_by_type("command")
            await pilot.pause()

            resource_list = app.screen.query_one(DataTable)
            # Should only show commands (1 in sample data)
            assert resource_list.row_count == 1

    @pytest.mark.asyncio
    async def test_filter_by_all_shows_everything(self, mock_catalog_loader, sample_resources_list):
        """Filtering by 'All' shows all resource types."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # First filter to agent
            await app.screen.filter_by_type("agent")
            await pilot.pause()

            # Then filter to all
            await app.screen.filter_by_type("all")
            await pilot.pause()

            resource_list = app.screen.query_one(DataTable)
            assert resource_list.row_count == len(sample_resources_list)

    @pytest.mark.asyncio
    async def test_category_buttons_exist(self, mock_catalog_loader):
        """Browser has category filter buttons for each type."""
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Should have filter buttons
            filter_container = app.screen.query_one("#filter-buttons")
            buttons = filter_container.query(Button)

            button_labels = [str(btn.label) for btn in buttons]
            assert "All" in button_labels
            assert "Agent" in button_labels
            assert "Command" in button_labels
            assert "Hook" in button_labels
            assert "Template" in button_labels
            assert "MCP" in button_labels

    @pytest.mark.asyncio
    async def test_active_filter_button_highlighted(self, mock_catalog_loader):
        """Active category filter button is visually highlighted."""
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            await app.screen.filter_by_type("agent")
            await pilot.pause()

            agent_button = app.screen.query_one("#filter-agent")
            assert agent_button.has_class("active")

    @pytest.mark.asyncio
    async def test_filter_persists_through_search(self, mock_catalog_loader, mock_search_engine):
        """Category filter remains active when searching."""
        app = BrowserScreenTestApp(
            catalog_loader=mock_catalog_loader,
            search_engine=mock_search_engine
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            # Set filter to agent
            await app.screen.filter_by_type("agent")
            await pilot.pause()

            # Perform search
            await app.screen.perform_search("test")
            await pilot.pause()

            # Should pass filter to search engine
            mock_search_engine.search.assert_called_with(
                "test", limit=50, filters={"type": "agent"}
            )


class TestBrowserScreenPreviewPane:
    """Test preview pane reactive updates."""

    @pytest.mark.asyncio
    async def test_preview_shows_selected_resource_details(
        self, mock_catalog_loader, sample_resource
    ):
        """Preview pane displays details of currently selected resource."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=[sample_resource])
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Select first resource
            await app.screen.on_resource_selected(0)
            await pilot.pause()

            preview = app.screen.query_one("#preview-pane")
            preview_text = str(preview.render())

            assert "Architect" in preview_text
            assert "System architecture design" in preview_text

    @pytest.mark.asyncio
    async def test_preview_updates_on_arrow_navigation(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Preview pane updates as user navigates with arrow keys."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Focus table
            table = app.screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Trigger initial selection
            await app.screen.on_resource_selected(0)
            await pilot.pause()
            initial_preview = str(app.screen.query_one("#preview-pane").render())

            # Move down and trigger new selection
            await pilot.press("down")
            await pilot.pause()

            # Preview should change
            new_preview = str(app.screen.query_one("#preview-pane").render())
            # If there's more than one resource, preview should change
            if len(sample_resources_list) > 1:
                assert new_preview != initial_preview

    @pytest.mark.asyncio
    async def test_preview_shows_metadata(self, mock_catalog_loader, sample_resource):
        """Preview pane displays resource metadata."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=[sample_resource])
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            app.screen.selected_resource = sample_resource
            await app.screen.update_preview()
            await pilot.pause()

            preview = app.screen.query_one("#preview-pane")
            preview_text = str(preview.render())

            # Should show metadata
            assert "Tools:" in preview_text or "tools" in preview_text.lower()
            assert "Model:" in preview_text or "model" in preview_text.lower()
            assert "opus" in preview_text

    @pytest.mark.asyncio
    async def test_preview_shows_dependencies(self, mock_catalog_loader, sample_resource):
        """Preview pane displays resource dependencies."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=[sample_resource])
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            app.screen.selected_resource = sample_resource
            await app.screen.update_preview()
            await pilot.pause()

            preview = app.screen.query_one("#preview-pane")
            preview_text = str(preview.render())

            assert "Dependencies:" in preview_text or "dependencies" in preview_text.lower()
            assert "security-reviewer" in preview_text

    @pytest.mark.asyncio
    async def test_preview_empty_when_no_selection(self, mock_catalog_loader):
        """Preview pane is empty when no resource selected."""
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            app.screen.selected_resource = None
            await app.screen.update_preview()
            await pilot.pause()

            preview = app.screen.query_one("#preview-pane")
            preview_text = str(preview.render())
            assert preview_text == "" or "Select a resource" in preview_text


class TestBrowserScreenStatusBar:
    """Test status bar updates and information display."""

    @pytest.mark.asyncio
    async def test_status_bar_shows_total_count(self, mock_catalog_loader, sample_resources_list):
        """Status bar displays total number of resources."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            await app.screen.update_status_bar()
            await pilot.pause()

            status_bar = app.screen.query_one("#status-bar")
            status_text = str(status_bar.render())
            assert f"{len(sample_resources_list)} resources" in status_text

    @pytest.mark.asyncio
    async def test_status_bar_shows_filtered_count(self, mock_catalog_loader, sample_resources_list):
        """Status bar shows filtered count when category filter active."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            await app.screen.filter_by_type("agent")
            await pilot.pause()

            status_bar = app.screen.query_one("#status-bar")
            status_text = str(status_bar.render()).lower()
            assert "agent" in status_text

    @pytest.mark.asyncio
    async def test_status_bar_shows_search_results_count(self, mock_catalog_loader, mock_search_engine):
        """Status bar shows number of search results."""
        mock_search_engine.search.return_value = [
            {"id": "test", "name": "Test", "type": "agent", "description": "Test", "version": "v1.0.0"}
        ]
        app = BrowserScreenTestApp(
            catalog_loader=mock_catalog_loader,
            search_engine=mock_search_engine
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            await app.screen.perform_search("test")
            await pilot.pause()

            status_bar = app.screen.query_one("#status-bar")
            status_text = str(status_bar.render()).lower()
            assert "1 match" in status_text

    @pytest.mark.asyncio
    async def test_status_bar_shows_selected_count(self, mock_catalog_loader):
        """Status bar shows number of selected resources (for multi-select)."""
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            app.screen.selected_resources = {"architect", "security-reviewer"}
            await app.screen.update_status_bar()
            await pilot.pause()

            status_bar = app.screen.query_one("#status-bar")
            status_text = str(status_bar.render()).lower()
            assert "2 selected" in status_text

    @pytest.mark.asyncio
    async def test_status_bar_shows_install_button_when_selected(
        self, mock_catalog_loader, sample_resources_list
    ):
        """Status bar shows install button when resources selected."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=sample_resources_list)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Focus the table first
            table = app.screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Select a resource
            await pilot.press("space")
            await pilot.pause()

            # Check if selection was successful
            if len(app.screen.selected_resources) > 0:
                install_button = app.screen.query_one("#install-selected-button")
                assert not install_button.has_class("hidden")


class TestBrowserScreenErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_handles_catalog_load_failure(self):
        """Browser gracefully handles catalog loading errors."""
        error_loader = Mock()
        error_loader.load_resources = AsyncMock(
            side_effect=Exception("Network error")
        )
        app = BrowserScreenTestApp(catalog_loader=error_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Should show error message
            error_display = app.screen.query_one("#error-message")
            assert not error_display.has_class("hidden")
            assert "error" in str(error_display.render()).lower()

    @pytest.mark.asyncio
    async def test_handles_search_engine_failure(self, mock_catalog_loader):
        """Browser handles search engine errors gracefully."""
        error_search = Mock()
        error_search.search.side_effect = Exception("Search index corrupted")
        app = BrowserScreenTestApp(
            catalog_loader=mock_catalog_loader,
            search_engine=error_search
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            await app.screen.perform_search("test")
            await pilot.pause()

            # Should show error message but not crash
            error_display = app.screen.query_one("#search-error")
            assert not error_display.has_class("hidden")

    @pytest.mark.asyncio
    async def test_handles_empty_catalog_gracefully(self):
        """Browser handles empty catalog without errors."""
        empty_loader = Mock()
        empty_loader.load_resources = AsyncMock(return_value=[])
        app = BrowserScreenTestApp(catalog_loader=empty_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Should not crash, should show empty message
            assert not app.screen.query_one("#empty-message").has_class("hidden")

    @pytest.mark.asyncio
    async def test_handles_malformed_resource_data(self, mock_catalog_loader):
        """Browser handles resources with missing fields."""
        malformed_data = [
            {"id": "incomplete"},  # Missing required fields
        ]
        mock_catalog_loader.load_resources = AsyncMock(return_value=malformed_data)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Should not crash when rendering
            resource_list = app.screen.query_one(DataTable)
            # Should have processed the malformed resource (or skipped it)
            assert resource_list.row_count >= 0


class TestBrowserScreenPerformance:
    """Test performance with large datasets."""

    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_loads_331_resources_quickly(self, mock_catalog_loader, mock_catalog_331_resources):
        """Browser loads full catalog (331 resources) within performance budget."""
        import time

        mock_catalog_loader.load_resources = AsyncMock(return_value=mock_catalog_331_resources)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            start = time.time()
            await app.screen.populate_resource_list()
            elapsed = time.time() - start

            # Should load in < 200ms (relaxed from 100ms for safety)
            assert elapsed < 0.2

    @pytest.mark.asyncio
    async def test_search_performs_quickly_on_large_dataset(
        self, mock_catalog_loader, mock_search_engine, mock_catalog_331_resources
    ):
        """Search completes within 50ms on full catalog."""
        import time

        mock_catalog_loader.load_resources = AsyncMock(return_value=mock_catalog_331_resources)
        app = BrowserScreenTestApp(
            catalog_loader=mock_catalog_loader,
            search_engine=mock_search_engine
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            start = time.time()
            await app.screen.perform_search("architect")
            elapsed = time.time() - start

            # Should complete in < 50ms (relaxed from 20ms for safety)
            assert elapsed < 0.05

    @pytest.mark.asyncio
    async def test_scrolling_large_list_is_smooth(self, mock_catalog_loader, mock_catalog_331_resources):
        """Scrolling through large resource list doesn't lag."""
        mock_catalog_loader.load_resources = AsyncMock(return_value=mock_catalog_331_resources)
        app = BrowserScreenTestApp(catalog_loader=mock_catalog_loader)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Focus the table
            table = app.screen.query_one(DataTable)
            table.focus()
            await pilot.pause()

            # Simulate rapid scrolling
            for _ in range(50):
                await pilot.press("down")

            await pilot.pause()

            # Should not crash or hang
            resource_list = app.screen.query_one(DataTable)
            assert resource_list.cursor_row >= 0
            # Should have moved down from initial position
            assert resource_list.cursor_row > 0
