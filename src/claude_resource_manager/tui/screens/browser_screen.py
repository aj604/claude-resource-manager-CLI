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
    MIN_WIDTH = 40     # Minimum terminal width
    MIN_HEIGHT = 10    # Minimum terminal height

    def __init__(
        self,
        catalog_loader: Optional[Any] = None,
        search_engine: Optional[Any] = None,
        **kwargs
    ):
        """Initialize the browser screen.

        Args:
            catalog_loader: Service for loading resources from catalog
            search_engine: Service for searching and filtering resources
            **kwargs: Additional arguments passed to Screen
        """
        # Set the screen name before calling super().__init__
        if 'name' not in kwargs:
            kwargs['name'] = 'browser'
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
            classes="hidden error-message"
        )

        # Search input
        yield Input(
            placeholder="Search resources...",
            id="search-input"
        )

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
        table.add_columns("", "Name", "Type", "Description", "Version")
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
                self.filtered_resources = self.resources.copy()
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

                # Show/hide install button
                install_button = self.query_one("#install-selected-button", Button)
                if self.selected_resources:
                    install_button.remove_class("hidden")
                else:
                    install_button.add_class("hidden")

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
                    r for r in self.resources
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
            self.filtered_resources = self.resources.copy()
        else:
            self.filtered_resources = [
                r for r in self.resources
                if r.get("type", "").lower() == self.current_filter
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

            if "model" in metadata:
                lines.append(f"Model: {metadata['model']}")

            if "tags" in metadata:
                tags = metadata["tags"]
                if isinstance(tags, list):
                    lines.append(f"Tags: {', '.join(tags)}")

        # Dependencies
        dependencies = self.selected_resource.get("dependencies", {})
        if dependencies:
            lines.append("\n\n[bold]Dependencies:[/bold]")

            required = dependencies.get("required", [])
            if required:
                if isinstance(required, list):
                    lines.append(f"Required: {', '.join(required)}")

            recommended = dependencies.get("recommended", [])
            if recommended:
                if isinstance(recommended, list):
                    lines.append(f"Recommended: {', '.join(recommended)}")

        # Version and author
        version = self.selected_resource.get("version", "")
        author = self.selected_resource.get("author", "")
        if version or author:
            lines.append("")
            if version:
                lines.append(f"Version: {version}")
            if author:
                lines.append(f"Author: {author}")

        preview.update("\n".join(lines))

    async def update_status_bar(self) -> None:
        """Update the status bar with current counts and selection state.

        Displays:
        - Total resource count or filtered count
        - Search result count
        - Number of selected resources
        - Current filter state
        """
        status_bar = self.query_one("#status-bar", Static)

        parts = []

        # Resource count
        total = len(self.resources)
        filtered = len(self.filtered_resources)

        if self.current_filter != "all":
            # Show filtered type
            parts.append(f"{filtered} {self.current_filter}s")
        elif filtered < total:
            # Show search results count
            if filtered == 1:
                parts.append("1 match")
            else:
                parts.append(f"{filtered} matches")
        else:
            # Show total count
            parts.append(f"{total} resources")

        # Selected count
        if self.selected_resources:
            count = len(self.selected_resources)
            parts.append(f"{count} selected")

        status_bar.update(" | ".join(parts))

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes.

        Args:
            event: Input change event containing the new value

        Triggers a search whenever the user types in the search box.
        """
        if event.input.id == "search-input":
            await self.perform_search(event.value)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button press event

        Handles filter button clicks and install button clicks.
        """
        button_id = event.button.id

        if button_id and button_id.startswith("filter-"):
            # Extract type from button ID
            resource_type = button_id.replace("filter-", "")
            await self.filter_by_type(resource_type)
        elif button_id == "install-selected-button":
            # Handle install (would push install screen)
            pass

    async def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handle table row highlighting.

        Args:
            event: Row highlighted event

        Updates the preview pane when a new row is highlighted.
        """
        await self.on_resource_selected(event.cursor_row)

    @property
    def max_selections(self) -> Optional[int]:
        """Get the maximum number of selections allowed.

        Returns:
            Maximum selections limit (None = unlimited)
        """
        return getattr(self, '_max_selections', None)

    @max_selections.setter
    def max_selections(self, value: Optional[int]) -> None:
        """Set the maximum number of selections allowed.

        Args:
            value: Maximum selections limit (None = unlimited)
        """
        self._max_selections = value

    def _check_selection_limit(self) -> bool:
        """Check if selection limit has been reached.

        Returns:
            True if selection can proceed, False if limit reached
        """
        max_sel = getattr(self, '_max_selections', None)
        if max_sel is not None and len(self.selected_resources) >= max_sel:
            self.notify(f"Maximum selections ({max_sel}) reached", severity="warning")
            return False
        return True

    async def select_all_visible(self) -> None:
        """Select all currently visible/filtered resources.

        Adds all resources in filtered_resources to the selected_resources set.
        Respects max_selections limit if set.
        """
        max_sel = getattr(self, '_max_selections', None)
        for resource in self.filtered_resources:
            resource_id = resource.get("id", resource.get("name"))
            if resource_id:
                # Check limit before adding
                if max_sel is not None and len(self.selected_resources) >= max_sel:
                    break
                self.selected_resources.add(resource_id)

        # Update UI
        await self.update_status_bar()

        # Show install button if selections exist
        install_button = self.query_one("#install-selected-button", Button)
        if self.selected_resources:
            install_button.remove_class("hidden")
        else:
            install_button.add_class("hidden")

    async def clear_selections(self) -> None:
        """Clear all selections.

        Removes all resource IDs from the selected_resources set and updates UI.
        """
        self.selected_resources.clear()

        # Update UI
        await self.update_status_bar()

        # Hide install button
        install_button = self.query_one("#install-selected-button", Button)
        install_button.add_class("hidden")

    async def sort_by(self, field: str) -> None:
        """Sort resources by specified field.

        Args:
            field: Field to sort by (name, type, updated, version)

        Sorts the filtered_resources list and refreshes the table.
        Preserves selections during sort.
        """
        # Valid sort fields
        valid_fields = ["name", "type", "updated", "version"]
        if field not in valid_fields:
            field = "name"

        # Get or initialize sort state
        current_sort_field = getattr(self, '_sort_field', None)
        current_sort_reverse = getattr(self, '_sort_reverse', False)

        # Toggle sort direction if same field, otherwise reset to ascending
        if current_sort_field == field:
            self._sort_reverse = not current_sort_reverse
        else:
            self._sort_reverse = False

        # Always set the field
        self._sort_field = field

        # Sort the filtered resources
        try:
            if field == "name":
                self.filtered_resources.sort(
                    key=lambda r: r.get("name", r.get("id", "")).lower(),
                    reverse=self._sort_reverse
                )
            elif field == "type":
                self.filtered_resources.sort(
                    key=lambda r: r.get("type", "").lower(),
                    reverse=self._sort_reverse
                )
            elif field == "updated":
                self.filtered_resources.sort(
                    key=lambda r: r.get("updated", ""),
                    reverse=self._sort_reverse
                )
            elif field == "version":
                self.filtered_resources.sort(
                    key=lambda r: r.get("version", ""),
                    reverse=self._sort_reverse
                )
        except Exception:
            # Fallback to name if sorting fails
            self.filtered_resources.sort(
                key=lambda r: r.get("name", r.get("id", "")).lower()
            )

        # Refresh the table
        await self.populate_resource_list()

    # ============================================================================
    # ADVANCED UI FEATURES - Phase 2
    # ============================================================================

    def action_show_help(self) -> None:
        """Show help screen with keyboard shortcuts.

        Opens a modal help screen displaying all available keyboard shortcuts
        and context-sensitive help for the current screen.
        """
        from claude_resource_manager.tui.screens.help_screen import HelpScreen

        help_screen = HelpScreen(context="browser")
        self.app.push_screen(help_screen)

    def action_open_sort_menu(self) -> None:
        """Open sort menu for resource ordering.

        Cycles through sort options: name -> type -> updated -> name
        Uses the existing sort_by method for consistent behavior.
        """
        # Map to use the existing sort_by method
        # Cycle through sort options
        sort_options = ["name", "type", "updated"]

        # Get current sort from existing state
        current_sort_field = getattr(self, '_sort_field', 'name')

        # Find next option
        try:
            current_index = sort_options.index(current_sort_field)
            next_index = (current_index + 1) % len(sort_options)
        except ValueError:
            next_index = 0

        next_field = sort_options[next_index]

        # Use existing sort_by method
        self.app.call_later(self.sort_by, next_field)

        # Save preference
        self.app.call_later(self._save_preferences)

        # Notify user
        direction = "↓" if getattr(self, '_sort_reverse', False) else "↑"
        self.notify(
            f"Sorted by {next_field} {direction}",
            title="Sort Applied",
            timeout=2
        )

    def action_toggle_preview(self) -> None:
        """Toggle preview pane visibility.

        Manually shows or hides the preview pane. User preference overrides
        automatic responsive hiding for narrow terminals.
        """
        preview = self.query_one("#preview-pane", Static)

        if self._preview_visible:
            # Hide preview
            preview.add_class("hidden")
            preview.styles.display = "none"
            self._preview_visible = False
            self.notify("Preview pane hidden", timeout=2)
        else:
            # Show preview
            preview.remove_class("hidden")
            preview.styles.display = "block"
            self._preview_visible = True
            self.notify("Preview pane shown", timeout=2)

        # Save preference
        self.app.call_later(self._save_preferences)

    def on_resize(self, event: events.Resize) -> None:
        """Handle terminal resize events.

        Adapts the layout to the new terminal size:
        - Shows size warning if terminal is too small
        - Hides preview pane on narrow terminals (< 80 cols)
        - Enables scrolling for small terminals
        - Updates internal size tracking

        Args:
            event: Resize event with new terminal dimensions
        """
        self._terminal_width = event.size.width
        self._terminal_height = event.size.height

        # Check minimum size
        size_warning = self.query_one("#size-warning", Static)
        if self._terminal_width < self.MIN_WIDTH or self._terminal_height < self.MIN_HEIGHT:
            # Show size warning
            size_warning.remove_class("hidden")
        else:
            # Hide size warning
            size_warning.add_class("hidden")

        # Responsive preview pane (only if preview is enabled by user)
        try:
            preview = self.query_one("#preview-pane", Static)
            if self._terminal_width < self.NARROW_WIDTH:
                # Auto-hide preview on narrow terminals
                if self._preview_visible:
                    preview.styles.display = "none"
            else:
                # Auto-show preview on wider terminals (if user hasn't manually disabled it)
                if self._preview_visible:
                    preview.styles.display = "block"
        except Exception:
            # Preview pane may not exist yet
            pass

        # Enable vertical scrolling for small terminals
        try:
            table = self.query_one(DataTable)
            if self._terminal_height < 20:
                table.show_vertical_scrollbar = True
            else:
                table.show_vertical_scrollbar = False
        except Exception:
            # Table may not exist yet
            pass

    def _load_preferences(self) -> None:
        """Load user preferences from config file.

        Loads saved preferences including:
        - Sort field and direction
        - Preview pane visibility
        - Filter preferences

        Preferences are stored in ~/.config/claude-resources/settings.json
        """
        try:
            config_path = Path.home() / ".config" / "claude-resources" / "settings.json"

            if config_path.exists():
                with open(config_path, "r") as f:
                    prefs = json.load(f)

                # Load sort preferences (use existing field names)
                self._sort_field = prefs.get("sort_field", "name")
                self._sort_reverse = not prefs.get("sort_ascending", True)  # Reverse ascending flag

                # Load current_sort for new code
                self.current_sort = prefs.get("sort_field", "name")
                self._sort_ascending = prefs.get("sort_ascending", True)

                self._preview_visible = prefs.get("preview_visible", True)
        except Exception:
            # Silently fail - use defaults
            pass

    def _save_preferences(self) -> None:
        """Save user preferences to config file.

        Persists preferences including:
        - Sort field and direction
        - Preview pane visibility
        - Filter preferences

        Preferences are stored in ~/.config/claude-resources/settings.json
        """
        try:
            config_dir = Path.home() / ".config" / "claude-resources"
            config_dir.mkdir(parents=True, exist_ok=True)

            config_path = config_dir / "settings.json"

            # Use existing _sort_field and _sort_reverse attributes
            sort_field = getattr(self, '_sort_field', 'name')
            sort_reverse = getattr(self, '_sort_reverse', False)

            prefs = {
                "sort_field": sort_field,
                "sort_ascending": not sort_reverse,  # Inverse of reverse
                "preview_visible": self._preview_visible,
            }

            with open(config_path, "w") as f:
                json.dump(prefs, f, indent=2)
        except Exception:
            # Silently fail - preferences won't persist
            pass
