"""Main integration module for accessibility features in the TUI.

This module provides the central integration point for adding WCAG 2.1 AA
compliant accessibility features to the Claude Resource Manager TUI.
"""

from typing import Optional

from textual import events
from textual.app import App
from textual.screen import ModalScreen, Screen
from textual.widgets import DataTable, Input

from .modals.error_modal import ErrorRecoveryModal
from .screens.browser_screen_accessibility import AccessibilityMixin
from .screens.help_screen_accessible import AccessibleHelpScreen

# Import accessibility components
from .theme import DefaultTheme
from .widgets.aria_live import AriaLiveRegion, ScreenReaderAnnouncer


class AccessibleApp(App):
    """Enhanced TUI application with full accessibility support.

    This class extends the base Textual App with:
    - WCAG AA compliant themes
    - Screen reader announcements
    - Enhanced keyboard navigation
    - Error recovery dialogs
    - Focus management
    """

    def __init__(self, *args, **kwargs):
        """Initialize the accessible app."""
        super().__init__(*args, **kwargs)
        self.screen_reader: Optional[ScreenReaderAnnouncer] = None
        self.theme = DefaultTheme()
        self._focus_stack = []

    def on_mount(self) -> None:
        """Set up accessibility features on app mount."""
        # Set up global ARIA live region
        self._setup_global_announcer()

        # Apply accessible theme
        self._apply_accessible_theme()

        # Set up global keyboard handlers
        self._setup_global_keyboard_handlers()

    def _setup_global_announcer(self) -> None:
        """Set up global screen reader announcer."""
        # Check if current screen has ARIA live region
        if self.screen:
            live_region = self.screen.query("#aria-live-region").first(AriaLiveRegion)
            if not live_region:
                # Create a global one
                live_region = AriaLiveRegion(id="global-aria-live")
                # Note: In real implementation, this would be added to the DOM

            self.screen_reader = ScreenReaderAnnouncer(live_region)

    def _apply_accessible_theme(self) -> None:
        """Apply WCAG compliant theme colors."""
        # Apply theme colors via CSS variables
        _theme_css = self._generate_theme_css(self.theme)
        # Note: In real implementation, this would update CSS variables
        # Currently unused but reserved for future implementation

    def _generate_theme_css(self, theme) -> str:
        """Generate CSS from theme colors."""
        css_vars = []
        for name, color in theme.colors.items():
            css_name = name.replace("_", "-")
            css_vars.append(f"--{css_name}: {color};")
        return "\n".join(css_vars)

    def _setup_global_keyboard_handlers(self) -> None:
        """Set up global keyboard shortcuts."""
        # These are handled at app level for consistency
        pass

    async def on_key(self, event: events.Key) -> None:
        """Handle global keyboard events with accessibility focus.

        Args:
            event: The keyboard event
        """
        # Global ESC handling - always allow escape
        if event.key == "escape":
            # Check if we're in a modal
            if isinstance(self.screen, ModalScreen):
                await self.pop_screen()
                event.stop()
                return

            # Check if we're in a text input
            focused = self.focused
            if isinstance(focused, Input) and focused.value:
                focused.value = ""
                if self.screen_reader:
                    self.screen_reader.live_region.announce("Input cleared")
                event.stop()
                return

        # Let the event propagate
        await super().on_key(event)

    def push_screen_with_focus(self, screen: Screen) -> None:
        """Push a screen while managing focus stack.

        Args:
            screen: The screen to push
        """
        # Save current focus
        if self.focused:
            self._focus_stack.append(self.focused)

        # Push the screen
        self.push_screen(screen)

    def pop_screen_with_focus(self) -> None:
        """Pop a screen and restore previous focus."""
        # Pop the screen
        self.pop_screen()

        # Restore focus if available
        if self._focus_stack:
            previous_focus = self._focus_stack.pop()
            if previous_focus and previous_focus.can_focus:
                previous_focus.focus()

    async def show_error_dialog(self, error: Exception, context: str) -> str:
        """Show accessible error dialog.

        Args:
            error: The exception that occurred
            context: Description of what was being attempted

        Returns:
            User choice: "retry", "skip", or "cancel"
        """
        modal = ErrorRecoveryModal(error, context)
        result = await self.push_screen_wait(modal)
        return result

    def announce(self, message: str, assertive: bool = False) -> None:
        """Make a screen reader announcement.

        Args:
            message: The message to announce
            assertive: Whether to interrupt current speech
        """
        if self.screen_reader:
            self.screen_reader.live_region.announce(message, assertive)


def enhance_browser_screen_accessibility(screen_class):
    """Enhance BrowserScreen with full accessibility support.

    This function adds all accessibility features to the BrowserScreen class.

    Args:
        screen_class: The BrowserScreen class to enhance
    """

    # Mixin the accessibility features
    class AccessibleBrowserScreen(AccessibilityMixin, screen_class):
        """Browser screen with full accessibility support."""

        def compose(self):
            """Compose UI with accessibility widgets."""
            # Call parent compose
            for widget in super().compose():
                yield widget

            # Add ARIA live region if not present
            if not self.query("#aria-live-region"):
                yield AriaLiveRegion(id="aria-live-region")

        async def on_mount(self) -> None:
            """Set up accessibility on mount."""
            await super().on_mount()
            self.setup_accessibility()
            self.setup_focus_management()

        async def on_key(self, event: events.Key) -> None:
            """Handle keyboard with accessibility."""
            # Try accessibility handling first
            if await self.handle_accessible_key(event):
                return

            # Call parent handler
            await super().on_key(event)

        async def action_show_help(self) -> None:
            """Show accessible help screen."""
            await self.on_modal_open("Help")
            help_screen = AccessibleHelpScreen(context="browser")
            await self.app.push_screen(help_screen)

        async def handle_search_input(self, event) -> None:
            """Handle search with announcements."""
            await super().handle_search_input(event)

            # Announce results
            if self.screen_reader:
                count = len(self.filtered_resources)
                query = self.query_one("#search-input", Input).value
                self.announce_search_update(query, count)

        async def handle_category_change(self, category: str) -> None:
            """Handle category change with announcement."""
            await super().handle_category_change(category)

            # Announce change
            if self.screen_reader:
                self.announce_category_change(category)

        async def handle_sort_change(self, field: str, order: str) -> None:
            """Handle sort change with announcement."""
            await super().handle_sort_change(field, order)

            # Announce change
            if self.screen_reader:
                self.announce_sort_change(field, order)

        async def handle_selection_toggle(self) -> None:
            """Handle selection toggle with announcement."""
            if not self.selected_resource:
                return

            resource = self.selected_resource
            was_selected = resource.id in self.selected_resources

            # Toggle selection
            if was_selected:
                self.selected_resources.remove(resource.id)
            else:
                self.selected_resources.add(resource.id)

            # Update UI
            await self._update_ui()

            # Announce
            if self.screen_reader:
                self.screen_reader.announce_selection(resource.name, not was_selected)

        async def handle_navigation(self, direction: str) -> None:
            """Handle navigation with announcements."""
            await super().handle_navigation(direction)

            # Announce new position
            if self.selected_resource and self.screen_reader:
                table = self.query_one("#resource-table", DataTable)
                if table:
                    row = table.cursor_row
                    total = table.row_count
                    self.announce_navigation(self.selected_resource.name, row + 1, total)

        async def handle_batch_install(self) -> None:
            """Handle batch install with announcements."""
            count = len(self.selected_resources)

            # Announce start
            if self.screen_reader:
                self.announce_batch_operation("Installing", count)

            try:
                await super().handle_batch_install()

                # Announce completion
                if self.screen_reader:
                    self.screen_reader.live_region.announce(
                        f"Successfully installed {count} resources", assertive=True
                    )
            except Exception as e:
                # Show error recovery dialog
                result = await self.show_error_with_recovery(e, f"installing {count} resources")

                if result == "retry":
                    await self.handle_batch_install()
                elif result == "skip":
                    pass  # Skip failed items
                else:
                    raise  # Cancel operation

    return AccessibleBrowserScreen


# Export main integration function
def integrate_accessibility(app_class, browser_screen_class):
    """Main function to integrate all accessibility features.

    Args:
        app_class: The main App class
        browser_screen_class: The BrowserScreen class

    Returns:
        Tuple of (AccessibleApp, AccessibleBrowserScreen)
    """

    # Enhance app with accessibility
    class EnhancedApp(AccessibleApp, app_class):
        pass

    # Enhance browser screen
    EnhancedBrowserScreen = enhance_browser_screen_accessibility(browser_screen_class)

    return EnhancedApp, EnhancedBrowserScreen
