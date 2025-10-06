"""
TUI Application Entry Point

This module provides the main entry point for the TUI (Text User Interface).
It initializes the Textual app, loads the catalog, and manages screen navigation.
Includes theme management and color scheme detection for accessibility.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from textual.app import App, ComposeResult
from textual.binding import Binding

from claude_resource_manager.core.catalog_loader import CatalogLoader
from claude_resource_manager.core.search_engine import SearchEngine
from claude_resource_manager.tui.screens.browser_screen import BrowserScreen
from claude_resource_manager.tui.theme import get_theme

console = Console()


class ThemeManager:
    """Manages color scheme detection and theme colors for the TUI."""

    def detect_color_scheme(self) -> str:
        """Detect color scheme from environment or terminal.

        Returns:
            "dark" or "light" based on environment
        """
        # Check TERM_THEME environment variable
        term_theme = os.getenv("TERM_THEME", "").lower()
        if term_theme in ("dark", "light"):
            return term_theme

        # Check COLORFGBG environment variable (used by some terminals)
        colorfgbg = os.getenv("COLORFGBG", "")
        if colorfgbg:
            # Format is "foreground;background"
            parts = colorfgbg.split(";")
            if len(parts) >= 2:
                try:
                    bg_color = int(parts[-1])
                    # Light background colors are typically 7 or 15
                    if bg_color in (7, 15):
                        return "light"
                except ValueError:
                    pass

        # Default to dark theme
        return "dark"

    def get_theme_colors(self, theme_name: str) -> dict:
        """Get theme colors for the specified theme.

        Args:
            theme_name: Name of the theme (dark, light, default)

        Returns:
            Dictionary of theme colors
        """
        theme = get_theme(theme_name)
        return theme.colors


class ResourceManagerApp(App):
    """Main TUI application for Claude Resource Manager.

    This is the root application class that manages the overall TUI experience.
    It handles screen navigation, keyboard shortcuts, and integrates all the
    core services (CatalogLoader, SearchEngine).

    Features:
    - Browser screen for resource listing and filtering
    - Search screen for fuzzy resource search
    - Detail screen for resource information
    - Install plan screen for installation workflow
    - Global keyboard shortcuts (q to quit, ? for help)
    - Rich styling with consistent theme

    Attributes:
        catalog_loader: Service for loading resources from catalog
        search_engine: Service for searching and filtering resources
        resource_type: Optional initial resource type filter
        category: Optional initial category filter
        verbose: Enable verbose error output
    """

    # App metadata
    TITLE = "Claude Resource Manager"
    SUB_TITLE = "Browse and install Claude resources"

    # Global key bindings
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("question_mark", "help", "Help", show=True),
        Binding("ctrl+c", "quit", "Quit", show=False),
    ]

    # CSS styling for consistent theme
    CSS = """
    Screen {
        background: $surface;
    }

    Header {
        background: $primary;
        color: $text;
    }

    Footer {
        background: $panel;
    }

    .title {
        text-align: center;
        padding: 1;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    .section {
        margin: 1;
        padding: 1;
        border: solid $accent;
    }

    .section-title {
        text-style: bold;
        color: $primary;
    }

    .hidden {
        display: none;
    }

    .filter-button {
        margin-right: 1;
    }

    .filter-button.active {
        background: $primary;
        color: $text;
    }

    #main-content {
        height: 100%;
    }

    #table-container {
        width: 60%;
        height: 100%;
    }

    #preview-pane {
        width: 40%;
        height: 100%;
        padding: 1;
        border-left: solid $accent;
    }

    #status-bar {
        dock: bottom;
        height: 1;
        background: $panel;
        color: $text-muted;
        padding-left: 1;
    }

    #resource-table {
        height: 100%;
    }

    #filter-buttons {
        height: auto;
        padding: 1;
    }

    #search-input {
        margin: 1;
    }

    .loading-message {
        color: $warning;
        text-align: center;
    }

    .error-message {
        color: $error;
        text-align: center;
    }

    .info-message {
        color: $text-muted;
        text-align: center;
    }

    DataTable {
        height: 100%;
    }

    DataTable > .datatable--cursor {
        background: $primary;
        color: $text;
    }

    Button {
        margin: 0 1;
    }

    Button.-primary {
        background: $primary;
        color: $text;
    }
    """

    def __init__(
        self,
        catalog_loader: CatalogLoader,
        search_engine: SearchEngine,
        resource_type: Optional[str] = None,
        category: Optional[str] = None,
        verbose: bool = False,
    ):
        """Initialize the TUI application.

        Args:
            catalog_loader: Service for loading resources from catalog
            search_engine: Service for searching and filtering resources
            resource_type: Optional resource type filter (agent, command, etc.)
            category: Optional category filter
            verbose: Enable verbose error output
        """
        super().__init__()
        self.catalog_loader = catalog_loader
        self.search_engine = search_engine
        self.resource_type = resource_type
        self.category = category
        self.verbose = verbose

        # Theme management - detect color scheme
        self.theme_manager = ThemeManager()
        self.color_scheme = self.theme_manager.detect_color_scheme()  # "dark" or "light"

    def compose(self) -> ComposeResult:
        """Compose the application UI.

        The main app only needs to yield the initial screen.
        Additional screens are pushed/popped as needed.

        Yields:
            Widget components for the app
        """
        # Header and Footer are automatically added by Textual
        # We don't need to yield them here
        # Return empty generator
        yield from []

    def on_mount(self) -> None:
        """Handle app mount - push initial browser screen.

        This is called when the app first starts. It pushes the
        BrowserScreen as the initial screen.
        """
        # Push the browser screen as the initial screen
        browser_screen = BrowserScreen(
            catalog_loader=self.catalog_loader,
            search_engine=self.search_engine,
        )
        self.push_screen(browser_screen)

    def action_help(self) -> None:
        """Show help message.

        Displays keyboard shortcuts and usage information via HelpScreen.
        """
        from claude_resource_manager.tui.screens.help_screen import HelpScreen

        # Push help screen with app context
        help_screen = HelpScreen(context="app")
        self.push_screen(help_screen)

    def action_quit(self) -> None:
        """Exit the application.

        Cleanly exits the TUI and returns to terminal.
        """
        self.exit()


def launch_tui(
    catalog_path: Path,
    resource_type: Optional[str] = None,
    category: Optional[str] = None,
    verbose: bool = False,
) -> None:
    """
    Launch the TUI browser.

    This is the main entry point for the TUI. It:
    1. Initializes the CatalogLoader
    2. Loads resources from the catalog
    3. Builds the SearchEngine index
    4. Creates and runs the ResourceManagerApp
    5. Handles errors gracefully

    Args:
        catalog_path: Path to the catalog directory
        resource_type: Optional resource type filter (agent, command, etc.)
        category: Optional category filter
        verbose: Enable verbose output

    Raises:
        FileNotFoundError: If catalog path doesn't exist
        Exception: Any other errors during initialization or runtime

    Example:
        >>> from pathlib import Path
        >>> launch_tui(Path.home() / '.claude' / 'registry' / 'catalog')
    """
    try:
        # Validate catalog path
        if not catalog_path.exists():
            console.print(f"[red]Error:[/red] Catalog not found at {catalog_path}", style="bold")
            console.print("[yellow]Hint:[/yellow] Run 'claude-resources sync' to download catalog")
            sys.exit(1)

        # Initialize catalog loader
        if verbose:
            console.print("[cyan]Loading catalog...[/cyan]")

        catalog_loader = CatalogLoader(catalog_path, use_cache=True)

        # Load all resources
        # We use asyncio.run to load resources asynchronously
        async def load_resources():
            """Async helper to load resources."""
            return catalog_loader.load_all_resources()

        resources = asyncio.run(load_resources())

        if verbose:
            console.print(f"[green]Loaded {len(resources)} resources[/green]")

        # Build search engine index
        if verbose:
            console.print("[cyan]Building search index...[/cyan]")

        search_engine = SearchEngine(use_cache=True)
        for resource in resources:
            search_engine.index_resource(resource)

        if verbose:
            console.print("[green]Search index ready[/green]")
            console.print("[cyan]Launching TUI...[/cyan]")

        # Create and run the app
        app = ResourceManagerApp(
            catalog_loader=catalog_loader,
            search_engine=search_engine,
            resource_type=resource_type,
            category=category,
            verbose=verbose,
        )

        # Run the app
        app.run()

    except FileNotFoundError:
        console.print(f"[red]Error:[/red] Catalog not found at {catalog_path}", style="bold")
        console.print("[yellow]Hint:[/yellow] Run 'claude-resources sync' to download catalog")
        if verbose:
            console.print_exception()
        sys.exit(1)

    except KeyboardInterrupt:
        # Clean exit on Ctrl+C
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)

    except Exception as e:
        console.print("[red]Error:[/red] Failed to launch TUI", style="bold")
        console.print(f"[red]{str(e)}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


