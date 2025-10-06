"""Browser Screen for Claude Resource Manager TUI.

This module implements the main resource browsing interface with:
- Resource list display using DataTable
- Category filtering (All, Agent, Command, Hook, Template, MCP)
- Search functionality with fuzzy matching
- Preview pane showing resource details
- Multi-select support for batch operations
- Keyboard navigation and shortcuts
- Sorting by name, type, and date
- Responsive layout with breakpoints
- Help screen integration
"""

import json
from pathlib import Path
from typing import Any, Optional

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Static,
)

from claude_resource_manager.tui.widgets.selection_indicator import SelectionIndicator


class BrowserScreen(Screen):
    """Main resource browsing screen with search, filter, and preview capabilities.

    This screen provides the primary interface for browsing available resources
    in the Claude Resource Manager catalog. It features:

    - DataTable widget showing all resources with columns: Name, Type, Description, Version
    - Search input for filtering resources by name/description
    - Category filter buttons for each resource type
    - Preview pane showing detailed information about selected resource
    - Status bar displaying resource counts and selection state
    - Multi-select support for batch installation
    - Keyboard shortcuts for efficient navigation

    Attributes:
        catalog_loader: Service for loading resources from catalog
        search_engine: Service for searching and filtering resources
        resources: List of all loaded resources
        filtered_resources: Currently displayed (filtered) resources
        selected_resources: Set of resource IDs selected for batch operations
        selected_resource: Currently highlighted resource in the list
        current_filter: Active category filter (all, agent, command, etc.)
    """

    BINDINGS = [
        Binding("up", "cursor_up", "Move Up", show=False),
        Binding("down", "cursor_down", "Move Down", show=False),
        Binding("enter", "select_resource", "View Details", show=True),
        Binding("/", "focus_search", "Search", show=True),
        Binding("escape", "clear_search", "Clear Search", show=False),
        Binding("space", "toggle_select", "Toggle Select", show=True),
        Binding("tab", "focus_next", "Next Field", show=False),
        Binding("s", "open_sort_menu", "Sort", show=True),
        Binding("p", "toggle_preview", "Toggle Preview", show=True),
        Binding("question_mark", "show_help", "Help", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    # Responsive layout breakpoints
    NARROW_WIDTH = 80  # Hide preview pane below this width
    MIN_WIDTH = 40  # Minimum terminal width
    MIN_HEIGHT = 10  # Minimum terminal height

    def __init__(
        self, catalog_loader: Optional[Any] = None, search_engine: Optional[Any] = None, **kwargs
    ):
        """Initialize the browser screen.

        Args:
            catalog_loader: Service for loading resources from catalog
            search_engine: Service for searching and filtering resources
            **kwargs: Additional arguments passed to Screen
        """
        # Set the screen name before calling super().__init__
        if "name" not in kwargs:
            kwargs["name"] = "browser"

        super().__init__(**kwargs)

        self.catalog_loader = catalog_loader
        self.search_engine = search_engine

        self.resources: list[dict[str, Any]] = []
        self.filtered_resources: list[dict[str, Any]] = []
        self.selected_resources: set[str] = set()
        self.selected_resource: Optional[dict[str, Any]] = None
        self.current_filter: str = "all"

        # Sorting state
        self.current_sort: str = "name"  # Current sort field (name, type, updated)
        self._sort_ascending: bool = True  # Sort direction

        # Responsive state
        self._preview_visible: bool = True  # Preview pane visibility
        self._terminal_width: int = 100  # Current terminal width
        self._terminal_height: int = 30  # Current terminal height

        # Load saved preferences
        self._load_preferences()

    def compose(self) -> ComposeResult:
        """Compose the browser screen UI.

        Yields:
            Widget components for the browser screen
        """
        yield Header()

        # Size warning for terminals that are too small
        yield Static(
            f"⚠️ Terminal too small! Minimum size: {self.MIN_WIDTH}x{self.MIN_HEIGHT}\n"
            "Please resize your terminal window.",
            id="size-warning",
            classes="hidden error-message",
        )

        # Search input
        yield Input(placeholder="Search resources...", id="search-input")

        # Filter buttons container
        with Horizontal(id="filter-buttons"):
            yield Button("All", id="filter-all", classes="filter-button active")
            yield Button("Agent", id="filter-agent", classes="filter-button")
            yield Button("Command", id="filter-command", classes="filter-button")
            yield Button("Hook", id="filter-hook", classes="filter-button")
            yield Button("Template", id="filter-template", classes="filter-button")
            yield Button("MCP", id="filter-mcp", classes="filter-button")

        # Main content area with table and preview
        with Horizontal(id="main-content"):
            with Vertical(id="table-container"):
                # Loading indicator
                yield Static("Loading resources...", id="loading-indicator")

                # Empty message (hidden by default)
                yield Static("No resources found", id="empty-message", classes="hidden")

                # Error message (hidden by default)
                yield Static("", id="error-message", classes="hidden")

                # Search error (hidden by default)
                yield Static("", id="search-error", classes="hidden")

                # Resource list table
                yield DataTable(id="resource-table")

            # Preview pane
            yield Static("Select a resource to view details", id="preview-pane")

        # Status bar
        yield Static("0 resources", id="status-bar")

        # Install button (hidden by default)
        yield Button("Install Selected", id="install-selected-button", classes="hidden")

        # Selection count indicator
        yield SelectionIndicator()

        yield Footer()

    async def on_mount(self) -> None:
        """Load resources when screen is mounted.

        This method is called when the screen is first displayed. It:
        1. Shows loading indicator
        2. Loads resources from catalog
        3. Populates the resource list
        4. Hides loading indicator
        5. Handles any errors during loading
        """
        # Setup the DataTable columns (checkbox column first for multi-select)
        table = self.query_one(DataTable)
        table.add_column("", width=4)  # Fixed width checkbox column
        table.add_columns("Name", "Type", "Description", "Version")
        table.cursor_type = "row"

        # Show loading indicator
        loading = self.query_one("#loading-indicator", Static)
        loading.update("Loading resources...")
        loading.remove_class("hidden")

        # Hide error messages initially
        self.query_one("#error-message", Static).add_class("hidden")
        self.query_one("#search-error", Static).add_class("hidden")
        self.query_one("#empty-message", Static).add_class("hidden")

        try:
            # Load resources from catalog
            if self.catalog_loader:
                self.resources = await self.catalog_loader.load_resources()
                # Ensure we create a new list, not just a reference
                self.filtered_resources = list(self.resources)
                await self.populate_resource_list()
        except Exception as e:
            # Show error message
            error_display = self.query_one("#error-message", Static)
            error_display.update(f"Error loading resources: {str(e)}")
            error_display.remove_class("hidden")
        finally:
            # Hide loading indicator
            loading.add_class("hidden")

            # Update status bar
            await self.update_status_bar()
            self.update_selection_count()

            # Set initial scrollbar state based on terminal size
            try:
                terminal_height = self.app.size.height if self.app else 30
                if terminal_height < 20:
                    table.show_vertical_scrollbar = True
            except Exception:
                # Ignore if size not available
                pass

            # Set initial preview pane display state
            try:
                preview = self.query_one("#preview-pane", Static)
                if self._preview_visible:
                    preview.styles.display = "block"
                else:
                    preview.styles.display = "none"
            except Exception:
                # Ignore if preview not available
                pass

            # Set focus on table instead of search input
            # This allows keyboard shortcuts like "?" to work immediately
            table.focus()

    async def populate_resource_list(self) -> None:
        """Populate the DataTable with current filtered resources.

        This method:
        1. Clears the current table
        2. Adds rows for each resource in filtered_resources
        3. Handles resources with missing fields gracefully
        4. Shows empty message if no resources
        """
        table = self.query_one(DataTable)
        table.clear()

        empty_message = self.query_one("#empty-message", Static)

        if not self.filtered_resources:
            # Show empty message
            empty_message.remove_class("hidden")
            if self.current_filter != "all":
                empty_message.update("No matches found")
            else:
                empty_message.update("No resources found")
        else:
            # Hide empty message
            empty_message.add_class("hidden")

            # Add rows to table
            for resource in self.filtered_resources:
                try:
                    # Determine checkbox state
                    resource_id = resource.get("id", resource.get("name"))
                    checkbox = "[x]" if resource_id in self.selected_resources else "[ ]"

                    name = resource.get("name", resource.get("id", "Unknown"))
                    res_type = resource.get("type", "unknown")
                    description = resource.get("description", resource.get("summary", ""))
                    version = resource.get("version", "")

                    # Add score if present (for search results)
                    score = resource.get("score")
                    if score is not None:
                        description = f"{description} (Score: {score})"

                    table.add_row(checkbox, name, res_type, description, version)
                except Exception:
                    # Skip malformed resources
                    continue

        # Update status bar
        await self.update_status_bar()
        self.update_selection_count()

    async def action_cursor_down(self) -> None:
        """Move selection down in the resource list.

        Moves the cursor to the next resource in the table and updates
        the preview pane with the newly selected resource's details.
        """
        table = self.query_one(DataTable)
        if table.row_count > 0:
            current_row = table.cursor_row
            if current_row < table.row_count - 1:
                table.move_cursor(row=current_row + 1)
                await self.on_resource_selected(table.cursor_row)

    async def action_cursor_up(self) -> None:
        """Move selection up in the resource list.

        Moves the cursor to the previous resource in the table and updates
        the preview pane. Stops at the top (doesn't wrap).
        """
        table = self.query_one(DataTable)
        if table.row_count > 0:
            current_row = table.cursor_row
            if current_row > 0:
                table.move_cursor(row=current_row - 1)
                await self.on_resource_selected(table.cursor_row)

    async def action_select_resource(self) -> None:
        """Open detail screen for the currently selected resource.

        Pushes a DetailScreen onto the app stack showing full details
        of the currently highlighted resource.
        """
        if not self.selected_resource:
            return

        # Import here to avoid circular imports
        from claude_resource_manager.tui.screens.detail_screen import DetailScreen

        detail_screen = DetailScreen(resource=self.selected_resource)
        self.app.push_screen(detail_screen)

    async def action_focus_search(self) -> None:
        """Focus the search input box.

        Triggered by the '/' key, this action moves focus to the search
        input to allow the user to start typing a search query.
        """
        search_input = self.query_one(Input)
        search_input.focus()

    async def action_clear_search(self) -> None:
        """Clear the search input and return focus to the table.

        Triggered by the Escape key when in the search box. Clears
        the search query and shows all resources again.
        """
        search_input = self.query_one(Input)
        search_input.value = ""

        # Return focus to table
        table = self.query_one(DataTable)
        table.focus()

        # Show all resources
        await self.perform_search("")

    async def action_toggle_select(self) -> None:
        """Toggle multi-select for the current resource.

        Triggered by the Space key. Adds or removes the current resource
        from the selected_resources set for batch operations.
        """
        table = self.query_one(DataTable)
        if table.row_count > 0 and self.filtered_resources:
            current_row = table.cursor_row
            if 0 <= current_row < len(self.filtered_resources):
                resource = self.filtered_resources[current_row]
                resource_id = resource.get("id", resource.get("name"))

                if resource_id in self.selected_resources:
                    self.selected_resources.discard(resource_id)
                    new_checkbox = "[ ]"
                else:
                    # Check selection limit before adding
                    if not self._check_selection_limit():
                        return
                    self.selected_resources.add(resource_id)
                    new_checkbox = "[x]"

                # Update checkbox cell in the table (first column, index 0)
                row_key = table.get_row_at(current_row)
                table.update_cell_at((current_row, 0), new_checkbox)

                # Update status bar
                await self.update_status_bar()
                self.update_selection_count()

                # Show/hide install button
                install_button = self.query_one("#install-selected-button", Button)
                if self.selected_resources:
                    install_button.remove_class("hidden")
                else:
                    install_button.add_class("hidden")

    def update_selection_count(self) -> None:
        """Update the selection count widget.

        Updates the SelectionIndicator widget to show the current number
        of selected resources and the total available.
        """
        try:
            indicator = self.query_one("#selection-count", SelectionIndicator)
            total = len(self.filtered_resources) if hasattr(self, "filtered_resources") else 0
            indicator.update_count(len(self.selected_resources), total)
        except Exception:
            # Widget may not exist yet
            pass

    async def action_focus_next(self) -> None:
        """Cycle focus to the next interactive element.

        Triggered by the Tab key. Moves focus through: search -> table -> buttons
        """
        if self.focused is self.query_one(Input):
            self.query_one(DataTable).focus()
        else:
            self.query_one(Input).focus()

    async def perform_search(self, query: str) -> None:
        """Perform a search and update the resource list.

        Args:
            query: Search query string (case-insensitive)

        This method:
        1. Calls the search engine with the query
        2. Applies current category filter
        3. Updates filtered_resources
        4. Refreshes the table display
        5. Handles search errors gracefully
        """
        search_error = self.query_one("#search-error", Static)
        search_error.add_class("hidden")

        if not query.strip():
            # Empty query - show all resources (with filter applied)
            await self.filter_by_type(self.current_filter)
            return

        try:
            if self.search_engine:
                # Build filters
                filters = {}
                if self.current_filter != "all":
                    filters["type"] = self.current_filter

                # Perform search
                results = self.search_engine.search(query, limit=50, filters=filters)
                self.filtered_resources = results
            else:
                # Fallback: simple filtering
                self.filtered_resources = [
                    r
                    for r in self.resources
                    if query.lower() in r.get("name", "").lower()
                    or query.lower() in r.get("description", "").lower()
                ]

            await self.populate_resource_list()
        except Exception as e:
            # Show search error
            search_error.update(f"Search error: {str(e)}")
            search_error.remove_class("hidden")

    async def filter_by_type(self, resource_type: str) -> None:
        """Filter resources by category type.

        Args:
            resource_type: Type to filter by (all, agent, command, hook, template, mcp)

        This method:
        1. Updates current_filter
        2. Filters resources list
        3. Updates active button styling
        4. Refreshes the table display
        """
        self.current_filter = resource_type.lower()

        # Update button styling
        for button_type in ["all", "agent", "command", "hook", "template", "mcp"]:
            button = self.query_one(f"#filter-{button_type}", Button)
            if button_type == self.current_filter:
                button.add_class("active")
            else:
                button.remove_class("active")

        # Filter resources
        if self.current_filter == "all":
            self.filtered_resources = list(self.resources)
        else:
            self.filtered_resources = [
                r for r in self.resources if r.get("type", "").lower() == self.current_filter
            ]

        await self.populate_resource_list()

    async def on_resource_selected(self, row_index: int) -> None:
        """Handle resource selection change.

        Args:
            row_index: Index of the selected row in the table

        Updates the selected_resource and refreshes the preview pane.
        """
        if 0 <= row_index < len(self.filtered_resources):
            self.selected_resource = self.filtered_resources[row_index]
            await self.update_preview()

    async def update_preview(self) -> None:
        """Update the preview pane with selected resource details.

        Displays:
        - Resource name and description
        - Metadata (tools, model, tags)
        - Dependencies (required and recommended)
        - Version and author information
        """
        preview = self.query_one("#preview-pane", Static)

        if not self.selected_resource:
            preview.update("Select a resource to view details")
            return

        # Build preview text
        lines = []

        # Basic info
        name = self.selected_resource.get("name", "Unknown")
        description = self.selected_resource.get("description", "")
        lines.append(f"[bold]{name}[/bold]")
        if description:
            lines.append(f"\n{description}")

        # Metadata
        metadata = self.selected_resource.get("metadata", {})
        if metadata:
            lines.append("\n\n[bold]Metadata:[/bold]")
            if "tools" in metadata:
                tools = metadata["tools"]
                if isinstance(tools, list):
                    lines.append(f"Tools: {', '.join(tools)}")
                else:
                    lines.append(f"Tools: {tools}")
            if "model" in metadata:
                lines.append(f"Model: {metadata['model']}")
            if "tags" in metadata:
                tags = metadata["tags"]
                if isinstance(tags, list):
                    lines.append(f"Tags: {', '.join(tags)}")
                else:
                    lines.append(f"Tags: {tags}")

        # Dependencies
        dependencies = self.selected_resource.get("dependencies", {})
        if dependencies:
            if "required" in dependencies and dependencies["required"]:
                lines.append("\n[bold]Required Dependencies:[/bold]")
                for dep in dependencies["required"]:
                    lines.append(f"  • {dep}")
            if "recommended" in dependencies and dependencies["recommended"]:
                lines.append("\n[bold]Recommended Dependencies:[/bold]")
                for dep in dependencies["recommended"]:
                    lines.append(f"  • {dep}")

        # Author and version
        lines.append("\n")
        if "author" in self.selected_resource:
            lines.append(f"Author: {self.selected_resource['author']}")
        if "version" in self.selected_resource:
            lines.append(f"Version: {self.selected_resource['version']}")
        if "updated" in self.selected_resource:
            lines.append(f"Updated: {self.selected_resource['updated']}")

        preview.update("\n".join(lines))

    async def update_status_bar(self) -> None:
        """Update the status bar with current state information.

        Shows:
        - Total resources
        - Filtered resources (if filtering)
        - Selected resources count
        - Current sort order
        """
        status = self.query_one("#status-bar", Static)

        parts = []

        # Resource counts
        total = len(self.resources)
        filtered = len(self.filtered_resources)

        if self.current_filter != "all" or filtered != total:
            parts.append(f"{filtered}/{total} resources")
        else:
            parts.append(f"{total} resources")

        # Filter indicator
        if self.current_filter != "all":
            parts.append(f"Filter: {self.current_filter}")

        # Selected count
        if self.selected_resources:
            count = len(self.selected_resources)
            parts.append(f"{count} selected")

        # Sort indicator
        if self.current_sort:
            arrow = "↑" if self._sort_ascending else "↓"
            parts.append(f"Sort: {self.current_sort} {arrow}")

        status.update(" | ".join(parts))

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input change.

        Args:
            event: Input change event containing the new value

        Performs live search as the user types.
        """
        if event.input.id == "search-input":
            await self.perform_search(event.value)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: Button press event

        Routes button presses to appropriate handlers.
        """
        button_id = event.button.id

        if button_id and button_id.startswith("filter-"):
            # Extract filter type (e.g., "filter-agent" -> "agent")
            filter_type = button_id.replace("filter-", "")
            await self.filter_by_type(filter_type)
        elif button_id == "install-selected-button":
            # TODO: Implement batch installation
            self.notify(f"Installing {len(self.selected_resources)} resources...")

    async def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handle table row highlight change.

        Args:
            event: Row highlight event

        Updates the preview pane when a new row is highlighted.
        """
        if event.data_table.id == "resource-table":
            await self.on_resource_selected(event.cursor_row)

    @property
    def max_selections(self) -> Optional[int]:
        """Get the maximum number of allowed selections.

        Returns:
            Maximum selections limit or None if unlimited
        """
        return getattr(self, "_max_selections", None)

    @max_selections.setter
    def max_selections(self, value: Optional[int]) -> None:
        """Set the maximum number of allowed selections.

        Args:
            value: Maximum selections limit or None for unlimited
        """
        self._max_selections = value

    def _check_selection_limit(self) -> bool:
        """Check if adding another selection would exceed the limit.

        Returns:
            True if selection can be added, False if limit reached
        """
        max_sel = getattr(self, "_max_selections", None)
        if max_sel is not None and len(self.selected_resources) >= max_sel:
            self.notify(f"Maximum selections ({max_sel}) reached", severity="warning")
            return False
        return True

    async def select_all_visible(self) -> None:
        """Select all currently visible (filtered) resources.

        Adds all resources in filtered_resources to the selected_resources set.
        Respects max_selections limit if set.
        """
        max_sel = getattr(self, "_max_selections", None)

        for resource in self.filtered_resources:
            resource_id = resource.get("id", resource.get("name"))
            if resource_id not in self.selected_resources:
                # Check limit before adding
                if max_sel is not None and len(self.selected_resources) >= max_sel:
                    break
                self.selected_resources.add(resource_id)

        # Refresh table to show checkboxes
        await self.populate_resource_list()

        # Show install button if selections exist
        install_button = self.query_one("#install-selected-button", Button)
        if self.selected_resources:
            install_button.remove_class("hidden")
        else:
            install_button.add_class("hidden")

    async def refresh_table(self) -> None:
        """Refresh table display while preserving cursor position.

        Rebuilds the table content while maintaining the current cursor
        position and updating checkbox states.
        """
        table = self.query_one(DataTable)

        # Save current cursor position
        cursor_row = table.cursor_row if table.cursor_row is not None else 0

        # Clear and rebuild table
        table.clear()
        for resource in self.filtered_resources:
            resource_id = resource.get("id", resource.get("name"))
            checkbox = "[x]" if resource_id in self.selected_resources else "[ ]"
            name = resource.get("name", resource.get("id", "Unknown"))
            res_type = resource.get("type", "unknown")
            description = resource.get("description", resource.get("summary", ""))
            version = resource.get("version", "")

            # Add score if present (for search results)
            score = resource.get("score")
            if score is not None:
                description = f"{description} (Score: {score})"

            table.add_row(checkbox, name, res_type, description, version)

        # Restore cursor position
        if cursor_row < table.row_count:
            table.move_cursor(row=cursor_row)

    def clear_selections(self) -> None:
        """Clear all selections with visual update.

        Removes all resource IDs from the selected_resources set and updates UI.
        """
        self.selected_resources.clear()

        # Force table refresh to update checkboxes
        import asyncio

        asyncio.create_task(self.refresh_table())

        # Update selection count
        self.update_selection_count()

        # Refresh table to show cleared checkboxes
        table = self.query_one(DataTable)

        # Update all checkbox cells to unchecked state
        for row_idx in range(table.row_count):
            table.update_cell_at((row_idx, 0), "[ ]")

        # Hide install button
        install_button = self.query_one("#install-selected-button", Button)
        install_button.add_class("hidden")

        # Update status
        import asyncio

        asyncio.create_task(self.update_status_bar())

    async def sort_by(self, field: str) -> None:
        """Sort the resource list by specified field.

        Args:
            field: Field to sort by (name, type, updated)

        Toggles ascending/descending order when sorting by the same field.
        Updates the filtered_resources list and refreshes the table.
        """
        # Toggle direction if same field
        if field == self.current_sort:
            self._sort_ascending = not self._sort_ascending
        else:
            self.current_sort = field
            self._sort_ascending = True

        # Determine sort key function
        if field == "name":
            key_func = lambda r: r.get("name", "").lower()
        elif field == "type":
            key_func = lambda r: r.get("type", "").lower()
        elif field == "updated":
            key_func = lambda r: r.get("updated", "")
        else:
            # Fallback to name
            key_func = lambda r: r.get("name", "").lower()

        # Sort the filtered resources
        try:
            self.filtered_resources = sorted(
                self.filtered_resources, key=key_func, reverse=not self._sort_ascending
            )
        except Exception:
            # If sorting fails, keep original order
            pass

        # Refresh the table
        await self.populate_resource_list()

        # Update status bar
        await self.update_status_bar()

    def action_show_help(self) -> None:
        """Show the help screen.

        Pushes the help screen onto the app stack to display
        keyboard shortcuts and usage information.
        """
        # Import here to avoid circular imports
        from claude_resource_manager.tui.screens.help_screen import HelpScreen

        help_screen = HelpScreen()
        self.app.push_screen(help_screen)

    def action_open_sort_menu(self) -> None:
        """Open the sort menu.

        Displays a menu allowing the user to select the sort field.
        Triggered by the 's' key.
        """
        # Create a simple menu using notifications
        # In a more complete implementation, this could be a proper menu widget
        self.notify(
            "Sort by: [N]ame, [T]ype, [U]pdated date\n" "Press the corresponding key to sort",
            timeout=5,
            title="Sort Menu",
        )

        # Set up temporary key handlers
        def handle_sort_key(event: events.Key) -> None:
            if event.key == "n":
                import asyncio

                asyncio.create_task(self.sort_by("name"))
                self.notify("Sorting by name", timeout=2)
            elif event.key == "t":
                import asyncio

                asyncio.create_task(self.sort_by("type"))
                self.notify("Sorting by type", timeout=2)
            elif event.key == "u":
                import asyncio

                asyncio.create_task(self.sort_by("updated"))
                self.notify("Sorting by update date", timeout=2)

        # Note: In a real implementation, we'd need to properly manage
        # these temporary key handlers

    def action_toggle_preview(self) -> None:
        """Toggle the preview pane visibility.

        Triggered by the 'p' key. Hides or shows the preview pane
        to provide more space for the resource list when needed.
        """
        preview = self.query_one("#preview-pane", Static)

        if self._preview_visible:
            # Hide preview
            preview.styles.display = "none"
            self._preview_visible = False
            self.notify("Preview pane hidden", timeout=2)
        else:
            # Show preview
            preview.styles.display = "block"
            self._preview_visible = True
            self.notify("Preview pane shown", timeout=2)

        # Save preference
        self._save_preferences()

    def on_resize(self, event: events.Resize) -> None:
        """Handle terminal resize events.

        Args:
            event: Resize event with new terminal dimensions

        Adjusts UI layout based on terminal size:
        - Shows/hides preview pane on narrow terminals
        - Adjusts table column widths
        - Shows warnings for very small terminals
        """
        self._terminal_width = event.width
        self._terminal_height = event.height

        # Check minimum size
        warning = self.query_one("#size-warning", Static)
        if event.width < self.MIN_WIDTH or event.height < self.MIN_HEIGHT:
            warning.remove_class("hidden")
            return
        else:
            warning.add_class("hidden")

        # Responsive preview pane
        try:
            preview = self.query_one("#preview-pane", Static)
            if event.width < self.NARROW_WIDTH:
                # Hide preview on narrow terminals
                if self._preview_visible:
                    preview.styles.display = "none"
            else:
                # Auto-show preview on wider terminals (if user hasn't manually disabled it)
                if self._preview_visible:
                    preview.styles.display = "block"
        except Exception:
            # Preview pane may not exist yet
            pass

        # Adjust scrollbar visibility
        try:
            table = self.query_one(DataTable)
            if event.height < 20:
                table.show_vertical_scrollbar = True
            else:
                table.show_vertical_scrollbar = False
        except Exception:
            # Table may not exist yet
            pass

    def _load_preferences(self) -> None:
        """Load user preferences from disk.

        Loads saved preferences like:
        - Sort order
        - Preview pane visibility
        - Selected filter

        Preferences are stored in ~/.config/claude-resource-manager/preferences.json
        """
        try:
            pref_dir = Path.home() / ".config" / "claude-resource-manager"
            pref_file = pref_dir / "preferences.json"

            if pref_file.exists():
                with open(pref_file) as f:
                    prefs = json.load(f)

                # Apply preferences
                self.current_sort = prefs.get("sort_field", "name")
                self._sort_ascending = prefs.get("sort_ascending", True)
                self._preview_visible = prefs.get("preview_visible", True)
                self.current_filter = prefs.get("filter", "all")
        except Exception:
            # Use defaults if loading fails
            pass

    def _save_preferences(self) -> None:
        """Save user preferences to disk.

        Persists current preferences for the next session.
        """
        try:
            pref_dir = Path.home() / ".config" / "claude-resource-manager"
            pref_dir.mkdir(parents=True, exist_ok=True)
            pref_file = pref_dir / "preferences.json"

            prefs = {
                "sort_field": self.current_sort,
                "sort_ascending": self._sort_ascending,
                "preview_visible": self._preview_visible,
                "filter": self.current_filter,
            }

            with open(pref_file, "w") as f:
                json.dump(prefs, f, indent=2)
        except Exception:
            # Silently fail if we can't save preferences
            pass
