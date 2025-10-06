"""Search screen for the Textual TUI.

This module provides a dedicated search interface for the Claude Resource Manager TUI.
It offers real-time search with fuzzy matching, result highlighting, and keyboard navigation.

Features:
- Real-time search as user types
- Fuzzy matching with score indicators
- Result highlighting
- Keyboard navigation (↑↓, Enter, Esc)
- Search history tracking
- Debounced input to avoid excessive searches
- Clear/reset functionality
- No results messaging with tips
- Performance optimized for rapid typing
"""

import asyncio
from typing import Any, Optional

from textual import on
from textual.binding import Binding
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Input, Label, ListItem, ListView, Static


class SearchScreen(Screen):
    """Dedicated search screen with real-time filtering.

    This screen provides a focused search experience with:
    - Search input with placeholder
    - Results list with scores
    - Help text and no-results messaging
    - Search history tracking
    - Keyboard shortcuts for navigation and selection

    Bindings:
        - Escape: Close search without selection
        - Enter: Select highlighted result
        - ↑/↓: Navigate through results
        - Ctrl+L: Clear search
        - Ctrl+P: Previous search from history

    Attributes:
        search_engine: SearchEngine instance for performing searches
        current_query: Current search query string
        displayed_results: List of currently displayed search results
        search_history: List of previous search queries (max 10)
        _debounce_task: Asyncio task for debouncing input
        _pending_searches: Counter for pending searches
    """

    BINDINGS = [
        Binding("escape", "cancel", "Close", show=True),
        Binding("enter", "select_result", "Select", show=True),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("ctrl+l", "clear", "Clear", show=True),
        Binding("ctrl+p", "history_previous", "History", show=False),
    ]

    CSS = """
    SearchScreen {
        align: center middle;
        background: $surface;
    }

    #search-container {
        width: 80;
        height: 30;
        border: solid $primary;
        background: $panel;
        padding: 1;
    }

    #search-input {
        margin-bottom: 1;
    }

    #results-container {
        height: 20;
        border: solid $accent;
    }

    #search-help {
        color: $text-muted;
        text-align: center;
        margin: 1;
    }

    #no-results-message {
        color: $warning;
        text-align: center;
        margin: 1;
    }

    #search-error {
        color: $error;
        text-align: center;
        margin: 1;
    }

    ListView {
        height: 100%;
    }

    ListItem {
        padding: 0 1;
    }
    """

    def __init__(
        self,
        search_engine: Optional[Any] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ):
        """Initialize search screen.

        Args:
            search_engine: SearchEngine instance for performing searches
            name: Name of the screen
            id: ID of the screen
            classes: CSS classes for the screen
        """
        super().__init__(name=name, id=id, classes=classes)
        self.search_engine = search_engine
        self.current_query = ""
        self.displayed_results: list[dict[str, Any]] = []
        self.search_history: list[str] = []
        self._debounce_task: Optional[asyncio.Task] = None
        self._pending_searches = 0
        self._history_index = -1

    def compose(self):
        """Create child widgets.

        Yields:
            Widget: Child widgets for the search screen
        """
        with Container(id="search-container"):
            yield Input(placeholder="Type to search...", id="search-input")
            yield Static(
                "Type to search resources. Use ↑/↓ to navigate, Enter to select, Esc to cancel.",
                id="search-help",
            )
            yield Static("", id="no-results-message")
            yield Static("", id="search-error")
            with Container(id="results-container"):
                yield ListView(id="search-results")

    async def on_mount(self) -> None:
        """Handle screen mount event.

        Sets focus to the search input when the screen is mounted.
        """
        search_input = self.query_one(Input)
        search_input.focus()

        # Hide messages initially
        self.query_one("#no-results-message").visible = False
        self.query_one("#search-error").visible = False

    @on(Input.Changed)
    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input change event.

        Performs debounced search as user types. Enforces minimum query length
        and trims whitespace.

        Args:
            event: Input change event (can also be called with string value)
        """
        # Handle both event object and direct string input
        if isinstance(event, str):
            value = event
        else:
            value = event.value

        # Trim whitespace
        query = value.strip()
        self.current_query = query

        # Clear results if empty
        if not query:
            self.clear_results()
            self.query_one("#search-help").visible = True
            self.query_one("#no-results-message").visible = False
            self.query_one("#search-error").visible = False
            return

        # Minimum query length
        if len(query) < 2:
            return

        # Hide help text
        self.query_one("#search-help").visible = False

        # Cancel previous debounce task
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()

        # Create new debounced search task
        self._debounce_task = asyncio.create_task(self._debounced_search(query))

    async def _debounced_search(self, query: str) -> None:
        """Perform debounced search.

        Waits 200ms before executing search to avoid excessive searches
        during rapid typing.

        Args:
            query: Search query string
        """
        try:
            # Wait for debounce period
            await asyncio.sleep(0.2)

            # Perform search
            await self._perform_search(query)
        except asyncio.CancelledError:
            # Task was cancelled, ignore
            pass

    async def _perform_search(self, query: str) -> None:
        """Perform actual search and display results.

        Args:
            query: Search query string
        """
        if not self.search_engine:
            return

        try:
            # Hide error message
            self.query_one("#search-error").visible = False

            # Increment pending searches
            self._pending_searches += 1

            # Perform search
            results = self.search_engine.search_smart(query, limit=50)

            # Decrement pending searches
            self._pending_searches -= 1

            # Add to history if results found
            if results:
                self.add_to_history(query)

            # Display results
            if results:
                self.display_results(results)
                self.query_one("#no-results-message").visible = False
            else:
                self.display_no_results(query)

        except Exception as e:
            # Handle search errors gracefully
            self._pending_searches = max(0, self._pending_searches - 1)
            error_msg = self.query_one("#search-error")
            error_msg.update(f"Search error: {str(e)}")
            error_msg.visible = True
            self.clear_results()

    def display_results(self, results: list[dict[str, Any]]) -> None:
        """Display search results in the list view.

        Results are sorted by score (highest first) and displayed with
        name, type, score, and description preview.

        Args:
            results: List of search result dictionaries with score field
        """
        # Sort by score (highest first)
        sorted_results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)
        self.displayed_results = sorted_results

        # Clear and populate results list
        results_list = self.query_one(ListView)
        results_list.clear()

        for result in sorted_results:
            # Format result item
            item_text = self._format_result_item(result)
            results_list.append(ListItem(Label(item_text)))

        # Hide no-results message
        self.query_one("#no-results-message").visible = False

    def _format_result_item(self, result: dict[str, Any]) -> str:
        """Format a result item for display.

        Includes name, type, score indicator, and description preview.
        Highlights matching text from the query.

        Args:
            result: Result dictionary

        Returns:
            Formatted string with Rich markup
        """
        name = result.get("name", result.get("id", "Unknown"))
        resource_type = result.get("type", "unknown")
        score = result.get("score", 0)
        description = result.get("description", "")

        # Create score stars
        stars = "★" * int(score / 20)  # 0-5 stars

        # Truncate description
        desc_preview = description[:50] + "..." if len(description) > 50 else description

        # Highlight matching text
        highlighted_name = self._highlight_match(name, self.current_query)
        highlighted_desc = self._highlight_match(desc_preview, self.current_query)

        # Format: Name (type) ★★★ score - description
        return f"{highlighted_name} [dim]({resource_type})[/dim] [yellow]{stars}[/yellow] [dim]{score}[/dim] - [italic]{highlighted_desc}[/italic]"

    def _highlight_match(self, text: str, query: str) -> str:
        """Highlight matching text in result.

        Args:
            text: Text to highlight
            query: Query to match

        Returns:
            Text with Rich markup for highlighting
        """
        if not query or not text:
            return text

        # Simple case-insensitive highlight
        text_lower = text.lower()
        query_lower = query.lower()

        if query_lower in text_lower:
            # Find position and highlight
            start = text_lower.index(query_lower)
            end = start + len(query)
            return f"{text[:start]}[bold yellow]{text[start:end]}[/bold yellow]{text[end:]}"

        return text

    def display_no_results(self, query: str) -> None:
        """Display no results message with search tips.

        Args:
            query: Search query that returned no results
        """
        self.clear_results()

        no_results_msg = self.query_one("#no-results-message")
        no_results_msg.update(
            f"No matches found for '{query}'.\n"
            "Try different keywords, check spelling, or use fewer keywords."
        )
        no_results_msg.visible = True

    def clear_results(self) -> None:
        """Clear the results list."""
        results_list = self.query_one(ListView)
        results_list.clear()
        self.displayed_results = []

    def add_to_history(self, query: str) -> None:
        """Add query to search history.

        Avoids duplicates and limits history to 10 items.

        Args:
            query: Query to add to history
        """
        # Remove if already exists (move to end)
        if query in self.search_history:
            self.search_history.remove(query)

        # Add to end
        self.search_history.append(query)

        # Limit to 10 items
        if len(self.search_history) > 10:
            self.search_history = self.search_history[-10:]

        # Reset history index
        self._history_index = -1

    async def action_cursor_down(self) -> None:
        """Navigate down through results."""
        results_list = self.query_one(ListView)
        if results_list.children:
            # Move focus to results if not already
            results_list.focus()
            current_index = results_list.index or 0
            if current_index < len(results_list.children) - 1:
                results_list.index = current_index + 1

    async def action_cursor_up(self) -> None:
        """Navigate up through results."""
        results_list = self.query_one(ListView)
        if results_list.children:
            results_list.focus()
            current_index = results_list.index or 0
            if current_index > 0:
                results_list.index = current_index - 1

    async def action_select_result(self) -> None:
        """Select the highlighted result and close search.

        Returns the selected result via dismiss().
        """
        results_list = self.query_one(ListView)
        if results_list.children and self.displayed_results:
            index = results_list.index or 0
            if 0 <= index < len(self.displayed_results):
                selected = self.displayed_results[index]
                self.dismiss(selected)

    async def action_cancel(self) -> None:
        """Close search without selecting.

        Returns None via dismiss().
        """
        self.dismiss(None)

    async def on_result_clicked(self, index: int) -> None:
        """Handle result click event.

        Args:
            index: Index of clicked result
        """
        if 0 <= index < len(self.displayed_results):
            selected = self.displayed_results[index]
            self.dismiss(selected)

    async def action_clear(self) -> None:
        """Clear search input and results, then refocus input."""
        search_input = self.query_one(Input)
        search_input.value = ""
        self.current_query = ""
        self.clear_results()
        self.query_one("#search-help").visible = True
        self.query_one("#no-results-message").visible = False
        self.query_one("#search-error").visible = False
        search_input.focus()

    async def action_history_previous(self) -> None:
        """Load previous search from history.

        Cycles through search history when up arrow is pressed in empty input.
        """
        if not self.search_history:
            return

        search_input = self.query_one(Input)

        # Only activate if input is empty or we're already cycling
        if search_input.value == "" or self._history_index >= 0:
            # Move to previous in history
            if self._history_index < 0:
                self._history_index = len(self.search_history) - 1
            elif self._history_index > 0:
                self._history_index -= 1

            # Set input value
            if 0 <= self._history_index < len(self.search_history):
                search_input.value = self.search_history[self._history_index]

    async def wait_for_pending_searches(self) -> None:
        """Wait for all pending searches to complete.

        Used in tests to ensure all debounced searches have finished.
        """
        # Wait for debounce task
        if self._debounce_task and not self._debounce_task.done():
            try:
                await self._debounce_task
            except asyncio.CancelledError:
                pass

        # Wait for pending searches counter to reach zero
        max_wait = 1.0  # 1 second max
        elapsed = 0.0
        interval = 0.05

        while self._pending_searches > 0 and elapsed < max_wait:
            await asyncio.sleep(interval)
            elapsed += interval
