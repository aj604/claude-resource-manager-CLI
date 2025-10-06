"""ARIA live region widget for screen reader announcements.

Implements WCAG 2.1 Success Criterion 4.1.3: Status Messages
Provides non-visual feedback for screen reader users about application state changes.
"""

import time
from typing import Any, Dict, List, Optional

from textual.reactive import reactive
from textual.widgets import Static


class AriaLiveRegion(Static):
    """Widget that announces status messages to screen readers.

    WCAG 4.1.3 Compliance:
    - Provides programmatic notification of status messages
    - Supports polite and assertive announcement modes
    - Does not change keyboard focus when announcing

    The widget simulates ARIA live regions for terminal applications,
    making dynamic content changes accessible to screen reader users.

    Attributes:
        announcement: Current message being announced
        politeness: Either "polite" (waits for pause) or "assertive" (interrupts)
    """

    DEFAULT_CSS = """
    AriaLiveRegion {
        display: none;  /* Hidden visually but accessible to screen readers */
    }
    """

    announcement = reactive("", init=False)

    def __init__(
        self,
        politeness: str = "polite",
        id: Optional[str] = "aria-live-region",
        max_history: int = 10,
        **kwargs
    ):
        """Initialize the ARIA live region.

        Args:
            politeness: Announcement mode - "polite" or "assertive"
            id: Widget ID for querying
            max_history: Maximum number of announcements to keep in history
            **kwargs: Additional arguments for parent class
        """
        super().__init__("", id=id, **kwargs)
        self.politeness = politeness
        self._announcement_queue = []
        self._is_announcing = False
        self._announcement_history: List[Dict[str, Any]] = []
        self._max_history = max_history

    def announce(self, message: str, assertive: bool = False) -> None:
        """Announce a message to screen readers.

        Args:
            message: The message to announce
            assertive: If True, use assertive mode (interrupts current speech)
        """
        if not message:
            return

        # Update politeness mode if needed
        if assertive:
            self.politeness = "assertive"
        else:
            self.politeness = "polite"

        # Update the announcement
        self.announcement = message
        self.update(message)

        # Store in history for testing and debugging
        self._announcement_history.append({
            'message': message,
            'timestamp': time.time(),
            'assertive': assertive,
            'politeness': self.politeness
        })

        # Limit history size to prevent memory leak
        if len(self._announcement_history) > self._max_history:
            self._announcement_history.pop(0)

        # Clear after a delay to prepare for next announcement
        self.set_timer(2.0, self._clear_announcement)

        # Log for debugging (helps verify announcements in testing)
        self.log(f"[ARIA-{self.politeness.upper()}] {message}")

    def _clear_announcement(self) -> None:
        """Clear the current announcement."""
        self.update("")
        self.announcement = ""

    def announce_queued(self, message: str, assertive: bool = False) -> None:
        """Queue a message for announcement.

        Useful for multiple rapid state changes to avoid overwhelming users.

        Args:
            message: The message to queue
            assertive: Priority of the message
        """
        self._announcement_queue.append((message, assertive))
        if not self._is_announcing:
            self._process_queue()

    def _process_queue(self) -> None:
        """Process queued announcements."""
        if not self._announcement_queue:
            self._is_announcing = False
            return

        self._is_announcing = True
        message, assertive = self._announcement_queue.pop(0)
        self.announce(message, assertive)

        # Process next item after a delay
        self.set_timer(2.5, self._process_queue)

    def get_last_announcement(self) -> str:
        """Get the most recent announcement.

        Test helper method that retrieves the last announcement
        regardless of whether it has been cleared.

        Returns:
            Most recent announcement message, or empty string if none
        """
        if self._announcement_history:
            return self._announcement_history[-1]['message']
        return ""

    def get_announcement_history(self, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent announcement history.

        Useful for testing sequences of announcements.

        Args:
            count: Number of recent announcements to retrieve (default: all)

        Returns:
            List of announcement dictionaries
        """
        if count is None:
            return list(self._announcement_history)
        return list(self._announcement_history[-count:])

    def clear_history(self) -> None:
        """Clear announcement history.

        Useful for test isolation between test cases.
        """
        self._announcement_history.clear()


class ScreenReaderAnnouncer:
    """Helper class for managing screen reader announcements across the app.

    Provides a centralized way to make announcements with consistent formatting
    and appropriate politeness levels for different types of messages.
    """

    def __init__(self, live_region: AriaLiveRegion):
        """Initialize with a live region widget.

        Args:
            live_region: The AriaLiveRegion widget to use for announcements
        """
        self.live_region = live_region

    def announce(self, message: str, assertive: bool = False) -> None:
        """Make a generic announcement.

        Args:
            message: The message to announce
            assertive: If True, interrupt current announcements (for errors)
        """
        self.live_region.announce(message, assertive=assertive)

    def announce_selection(self, resource_name: str, selected: bool) -> None:
        """Announce resource selection or deselection.

        Args:
            resource_name: Name of the resource
            selected: True if selected, False if deselected
        """
        action = "selected" if selected else "deselected"
        self.live_region.announce(f"Resource {action}: {resource_name}")

    def announce_search_results(self, count: int, query: str = "") -> None:
        """Announce search result count.

        Args:
            count: Number of results found
            query: Optional search query
        """
        if query:
            message = f"{count} resources found for '{query}'"
        else:
            message = f"{count} resources found"
        self.live_region.announce(message)

    def announce_category_change(self, category: str, count: int) -> None:
        """Announce category filter change.

        Args:
            category: The selected category
            count: Number of resources in category
        """
        message = f"Category: {category}, {count} resources"
        self.live_region.announce(message)

    def announce_sort_change(self, sort_field: str, order: str = "ascending") -> None:
        """Announce sort order change.

        Args:
            sort_field: The field being sorted by
            order: Sort order (ascending/descending)
        """
        message = f"Sorted by {sort_field}, {order}"
        self.live_region.announce(message)

    def announce_error(self, error_message: str) -> None:
        """Announce an error message.

        Args:
            error_message: The error to announce
        """
        self.live_region.announce(f"Error: {error_message}", assertive=True)

    def announce_progress(self, action: str, current: int, total: int) -> None:
        """Announce progress updates.

        Args:
            action: The action being performed (e.g., "Installing")
            current: Current progress value
            total: Total items
        """
        percentage = (current / total * 100) if total > 0 else 0
        message = f"{action}: {current} of {total} ({percentage:.0f}%)"
        self.live_region.announce(message)

    def announce_modal_open(self, modal_type: str) -> None:
        """Announce modal dialog opening.

        Args:
            modal_type: Type of modal (e.g., "Help", "Error")
        """
        self.live_region.announce(f"{modal_type} dialog opened", assertive=True)

    def announce_modal_close(self, modal_type: str) -> None:
        """Announce modal dialog closing.

        Args:
            modal_type: Type of modal that closed
        """
        self.live_region.announce(f"{modal_type} dialog closed")

    def announce_navigation(
        self, element: str, position: Optional[int] = None, total: Optional[int] = None
    ) -> None:
        """Announce navigation to a new element.

        Args:
            element: Description of the element
            position: Optional position in list
            total: Optional total items
        """
        if position is not None and total is not None:
            message = f"{element}, item {position} of {total}"
        else:
            message = element
        self.live_region.announce(message)
