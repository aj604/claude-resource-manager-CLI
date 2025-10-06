"""Accessibility enhancements for BrowserScreen.

This module contains mixins and patches to add WCAG 2.1 AA compliance
to the browser screen component.
"""

from typing import Optional

from textual import events
from textual.widgets import DataTable, Input

from claude_resource_manager.tui.modals.error_modal import ErrorRecoveryModal
from claude_resource_manager.tui.widgets.aria_live import AriaLiveRegion, ScreenReaderAnnouncer


class AccessibilityMixin:
    """Mixin to add accessibility features to BrowserScreen.

    Provides:
    - Screen reader announcements via ARIA live regions
    - Enhanced keyboard navigation with escape key support
    - Focus management for modals
    - User-friendly error messages with recovery options
    """

    def __init__(self, *args, **kwargs):
        """Initialize accessibility features."""
        super().__init__(*args, **kwargs)
        self.screen_reader: Optional[ScreenReaderAnnouncer] = None
        self._previous_focus = None
        self._modal_stack = []

    def setup_accessibility(self) -> None:
        """Set up accessibility components after mount."""
        # Find or create ARIA live region
        live_region = self.query_one("#aria-live-region", AriaLiveRegion)
        if live_region:
            self.screen_reader = ScreenReaderAnnouncer(live_region)
            # Also make it available app-wide
            if hasattr(self.app, "screen_reader") is False:
                self.app.screen_reader = self.screen_reader

    async def handle_accessible_key(self, event: events.Key) -> bool:
        """Handle keyboard events with accessibility enhancements.

        Args:
            event: The keyboard event

        Returns:
            True if event was handled, False otherwise
        """
        # ESC key handling
        if event.key == "escape":
            # If in search mode, clear search
            search_input = self.query_one("#search-input", Input)
            if search_input and search_input.has_focus:
                await self.action_clear_search()
                if self.screen_reader:
                    self.screen_reader.announce_search_results(len(self.filtered_resources), "")
                return True

            # If modal is open, close it
            if self._modal_stack:
                modal = self._modal_stack[-1]
                await modal.dismiss()
                return True

        # Space key for selection with announcement
        elif event.key == "space":
            table = self.query_one("#resource-table", DataTable)
            if table and table.has_focus:
                await self._toggle_selection_with_announcement()
                return True

        return False

    async def _toggle_selection_with_announcement(self) -> None:
        """Toggle resource selection with screen reader announcement."""
        if not self.selected_resource:
            return

        resource_id = self.selected_resource.id
        resource_name = self.selected_resource.name

        # Toggle selection
        if resource_id in self.selected_resources:
            self.selected_resources.remove(resource_id)
            selected = False
        else:
            self.selected_resources.add(resource_id)
            selected = True

        # Update UI
        await self._update_selection_ui()

        # Announce to screen reader
        if self.screen_reader:
            self.screen_reader.announce_selection(resource_name, selected)

    def announce_search_update(self, query: str, count: int) -> None:
        """Announce search results to screen readers.

        Args:
            query: The search query
            count: Number of results found
        """
        if self.screen_reader:
            self.screen_reader.announce_search_results(count, query)

    def announce_category_change(self, category: str) -> None:
        """Announce category filter change.

        Args:
            category: The selected category
        """
        if self.screen_reader:
            count = len(self.filtered_resources)
            self.screen_reader.announce_category_change(category, count)

    def announce_sort_change(self, field: str, order: str = "ascending") -> None:
        """Announce sort order change.

        Args:
            field: The sort field
            order: Sort direction
        """
        if self.screen_reader:
            self.screen_reader.announce_sort_change(field, order)

    async def show_error_with_recovery(self, error: Exception, context: str) -> Optional[str]:
        """Show error dialog with recovery options.

        Args:
            error: The exception that occurred
            context: What was being attempted

        Returns:
            User's choice: "retry", "skip", or "cancel"
        """
        # Create error modal
        modal = ErrorRecoveryModal(error, context)

        # Track modal in stack
        self._modal_stack.append(modal)

        # Show modal and wait for result
        result = await self.app.push_screen_wait(modal)

        # Remove from stack
        if modal in self._modal_stack:
            self._modal_stack.remove(modal)

        return result

    def announce_batch_operation(self, operation: str, count: int) -> None:
        """Announce batch operation start.

        Args:
            operation: Type of operation (e.g., "Installing")
            count: Number of items
        """
        if self.screen_reader:
            message = f"{operation} {count} resources"
            self.screen_reader.live_region.announce(message, assertive=True)

    def announce_navigation(self, resource_name: str, position: int, total: int) -> None:
        """Announce navigation to a resource.

        Args:
            resource_name: Name of the resource
            position: Position in list
            total: Total items in list
        """
        if self.screen_reader:
            self.screen_reader.announce_navigation(resource_name, position, total)

    def setup_focus_management(self) -> None:
        """Set up proper focus order for keyboard navigation."""
        # Define tab order
        focusable_elements = [
            "#search-input",
            "#filter-buttons",
            "#resource-table",
            "#preview-pane",
        ]

        # Set tab index for proper order
        for index, selector in enumerate(focusable_elements):
            element = self.query_one(selector)
            if element:
                element.can_focus = True

    async def on_modal_open(self, modal_type: str) -> None:
        """Handle modal opening with accessibility.

        Args:
            modal_type: Type of modal being opened
        """
        # Save current focus
        if self.app.focused:
            self._previous_focus = self.app.focused

        # Announce modal
        if self.screen_reader:
            self.screen_reader.announce_modal_open(modal_type)

    async def on_modal_close(self, modal_type: str) -> None:
        """Handle modal closing with accessibility.

        Args:
            modal_type: Type of modal being closed
        """
        # Restore focus
        if self._previous_focus:
            self._previous_focus.focus()
            self._previous_focus = None

        # Announce closing
        if self.screen_reader:
            self.screen_reader.announce_modal_close(modal_type)


def patch_browser_screen_for_accessibility(BrowserScreen):
    """Patch BrowserScreen class to add accessibility features.

    This function modifies the BrowserScreen class in-place to add:
    - ARIA live region to compose method
    - Accessibility setup in on_mount
    - Enhanced keyboard handling
    - Screen reader announcements

    Args:
        BrowserScreen: The BrowserScreen class to patch
    """
    # Store original methods
    original_compose = BrowserScreen.compose
    original_on_mount = BrowserScreen.on_mount
    original_on_key = getattr(BrowserScreen, "on_key", None)

    # Add compose with ARIA live region
    def compose_with_aria(self):
        """Compose UI with ARIA live region."""
        # Call original compose
        for widget in original_compose(self):
            yield widget

        # Add ARIA live region
        yield AriaLiveRegion(id="aria-live-region")

    # Add on_mount with accessibility setup
    async def on_mount_with_accessibility(self):
        """Set up accessibility on mount."""
        # Call original on_mount if it exists
        if original_on_mount:
            await original_on_mount(self)

        # Set up accessibility
        self.setup_accessibility()
        self.setup_focus_management()

    # Add enhanced keyboard handling
    async def on_key_with_accessibility(self, event: events.Key):
        """Handle keyboard events with accessibility."""
        # Try accessibility handling first
        if await self.handle_accessible_key(event):
            return

        # Call original handler if exists
        if original_on_key:
            await original_on_key(self, event)

    # Apply patches
    BrowserScreen.compose = compose_with_aria
    BrowserScreen.on_mount = on_mount_with_accessibility
    BrowserScreen.on_key = on_key_with_accessibility

    # Add mixin methods
    for method_name in dir(AccessibilityMixin):
        if not method_name.startswith("_"):
            method = getattr(AccessibilityMixin, method_name)
            setattr(BrowserScreen, method_name, method)

    return BrowserScreen
