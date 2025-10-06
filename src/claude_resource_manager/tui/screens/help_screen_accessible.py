"""Accessible help screen with proper focus management and announcements."""

from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from claude_resource_manager.tui.widgets.aria_live import AriaLiveRegion, ScreenReaderAnnouncer


class AccessibleHelpScreen(ModalScreen):
    """Enhanced help screen with WCAG 2.1 AA compliant accessibility features.

    Improvements over base HelpScreen:
    - Saves and restores focus when modal opens/closes
    - Announces modal state to screen readers
    - ESC key properly closes modal without trapping
    - Tab navigation cycles within modal
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close Help", show=True),
        Binding("q", "dismiss", "Close Help", show=False),
        Binding("tab", "focus_next", "Next Element", show=False),
        Binding("shift+tab", "focus_previous", "Previous Element", show=False),
    ]

    DEFAULT_CSS = """
    AccessibleHelpScreen {
        align: center middle;
    }

    #help-dialog {
        width: 80%;
        max-width: 100;
        height: 80%;
        max-height: 40;
        padding: 1 2;
        background: $surface;
        border: double $primary;
    }

    #help-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    #help-content {
        height: 1fr;
        margin-bottom: 1;
        padding: 0 1;
    }

    #help-footer {
        text-align: center;
        color: $text-secondary;
        margin-top: 1;
    }

    .help-section {
        margin-bottom: 1;
    }

    .help-section-title {
        text-style: bold;
        color: $secondary;
        margin-bottom: 0;
    }

    .help-shortcut {
        margin-left: 2;
    }

    .help-key {
        color: $primary;
        text-style: bold;
    }
    """

    def __init__(self, context: str = "browser", **kwargs):
        """Initialize the accessible help screen.

        Args:
            context: The current screen context for relevant help
            **kwargs: Additional arguments for parent class
        """
        super().__init__(**kwargs)
        self.context = context
        self._previous_focus = None
        self.screen_reader: Optional[ScreenReaderAnnouncer] = None

    def compose(self) -> ComposeResult:
        """Compose the help screen UI with accessibility features."""
        with Container(id="help-dialog"):
            # Title
            yield Static("Help - Keyboard Shortcuts", id="help-title")

            # Scrollable content
            with ScrollableContainer(id="help-content"):
                yield Static(self._get_help_content(), classes="help-text")

            # Footer with close button
            yield Button("Close (ESC)", id="help-close", variant="primary")

        # Hidden ARIA live region
        yield AriaLiveRegion(id="help-aria-live")

    def on_mount(self) -> None:
        """Handle mount event - save focus and announce opening."""
        # Save current focus
        if self.app.focused:
            self._previous_focus = self.app.focused

        # Set up screen reader
        live_region = self.query_one("#help-aria-live", AriaLiveRegion)
        self.screen_reader = ScreenReaderAnnouncer(live_region)

        # Announce modal opening
        self.screen_reader.announce_modal_open("Help")
        self.screen_reader.live_region.announce(
            "Help dialog opened. Press Escape to close.", assertive=False
        )

        # Focus on close button for keyboard users
        self.query_one("#help-close", Button).focus()

    @on(Button.Pressed, "#help-close")
    def on_close_pressed(self) -> None:
        """Handle close button press."""
        self.action_dismiss()

    def action_dismiss(self) -> None:
        """Close the help screen with proper cleanup."""
        # Announce closing
        if self.screen_reader:
            self.screen_reader.announce_modal_close("Help")

        # Restore previous focus
        if self._previous_focus:
            # Schedule focus restoration after dismiss
            self.app.call_after_refresh(self._restore_focus)

        # Dismiss the modal
        self.app.pop_screen()

    def _restore_focus(self) -> None:
        """Restore focus to the previous element."""
        if self._previous_focus and self._previous_focus.can_focus:
            self._previous_focus.focus()

    def action_focus_next(self) -> None:
        """Move focus to next element within modal."""
        self.focus_next()

    def action_focus_previous(self) -> None:
        """Move focus to previous element within modal."""
        self.focus_previous()

    def _get_help_content(self) -> str:
        """Generate help content based on context.

        Returns:
            Formatted help text with keyboard shortcuts
        """
        lines = []

        # Navigation section
        lines.extend(
            [
                "[bold]Navigation[/bold]",
                "  [cyan]↑/↓[/cyan]         - Navigate list",
                "  [cyan]Page Up/Down[/cyan] - Navigate by page",
                "  [cyan]Home/End[/cyan]     - Jump to first/last item",
                "  [cyan]Tab[/cyan]          - Move between UI elements",
                "",
            ]
        )

        # Selection section
        lines.extend(
            [
                "[bold]Selection[/bold]",
                "  [cyan]Enter[/cyan]        - View resource details",
                "  [cyan]Space[/cyan]        - Toggle selection for batch operations",
                "  [cyan]Ctrl+A[/cyan]       - Select all visible resources",
                "  [cyan]Ctrl+D[/cyan]       - Deselect all",
                "",
            ]
        )

        # Search and Filter section
        lines.extend(
            [
                "[bold]Search & Filter[/bold]",
                "  [cyan]/[/cyan]            - Focus search field",
                "  [cyan]Escape[/cyan]       - Clear search (when in search field)",
                "  [cyan]1-6[/cyan]          - Quick filter by category",
                "  [cyan]s[/cyan]            - Open sort menu",
                "",
            ]
        )

        # Actions section
        lines.extend(
            [
                "[bold]Actions[/bold]",
                "  [cyan]i[/cyan]            - Install selected resources",
                "  [cyan]p[/cyan]            - Toggle preview pane",
                "  [cyan]r[/cyan]            - Refresh resource list",
                "  [cyan]?[/cyan]            - Show this help",
                "  [cyan]q[/cyan]            - Quit application",
                "",
            ]
        )

        # Accessibility section
        lines.extend(
            [
                "[bold]Accessibility[/bold]",
                "  [cyan]Escape[/cyan]       - Close dialogs/cancel operations",
                "  [cyan]Tab[/cyan]          - Navigate forward through controls",
                "  [cyan]Shift+Tab[/cyan]    - Navigate backward through controls",
                "  • Screen reader announcements for all state changes",
                "  • WCAG AA compliant color contrast",
                "  • Keyboard shortcuts for all actions",
                "",
            ]
        )

        # Tips section
        lines.extend(
            [
                "[bold]Tips[/bold]",
                "  • Use fuzzy search for flexible matching",
                "  • Multi-select resources for batch installation",
                "  • Sort by any column for better organization",
                "  • Preview pane shows full resource details",
            ]
        )

        return "\n".join(lines)
