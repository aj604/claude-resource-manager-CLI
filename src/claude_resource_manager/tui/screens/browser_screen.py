"""Browser Screen for Claude Resource Manager TUI.

This module implements the main resource browsing interface with:
- Resource list display using DataTable
- Category filtering (All, Agent, Command, Hook, Template, MCP)
- Search functionality with fuzzy matching
- Preview pane showing resource details
- Multi-select support for batch operations
- Keyboard navigation and shortcuts
"""

from typing import Any, Optional

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
        Binding("q", "quit", "Quit", show=True),
    ]

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
        super().__init__(**kwargs)
        self.catalog_loader = catalog_loader
        self.search_engine = search_engine
        self.resources: list[dict[str, Any]] = []
        self.filtered_resources: list[dict[str, Any]] = []
        self.selected_resources: set[str] = set()
        self.selected_resource: Optional[dict[str, Any]] = None
        self.current_filter: str = "all"

    def compose(self) -> ComposeResult:
        """Compose the browser screen UI.

        Yields:
            Widget components for the browser screen
        """
        yield Header()

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
        # Setup the DataTable columns
        table = self.query_one(DataTable)
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
                    name = resource.get("name", resource.get("id", "Unknown"))
                    res_type = resource.get("type", "unknown")
                    description = resource.get("description", resource.get("summary", ""))
                    version = resource.get("version", "")

                    # Add score if present (for search results)
                    score = resource.get("score")
                    if score is not None:
                        description = f"{description} (Score: {score})"

                    table.add_row(name, res_type, description, version)
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
                else:
                    self.selected_resources.add(resource_id)

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
