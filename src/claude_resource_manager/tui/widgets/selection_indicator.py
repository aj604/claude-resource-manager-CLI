"""Selection indicator widget for displaying count of selected resources."""

from textual.reactive import reactive
from textual.widgets import Static


class SelectionIndicator(Static):
    """Widget displaying selection count in the TUI.

    Shows the number of selected resources and optionally the total count.
    Automatically hides when no resources are selected.
    """

    count = reactive(0)
    total = reactive(0)

    def __init__(self, **kwargs):
        """Initialize the selection indicator widget."""
        super().__init__("", id="selection-count", **kwargs)

    def watch_count(self, count: int) -> None:
        """Update display when count changes.

        Args:
            count: Number of selected resources
        """
        if count == 0:
            self.update("")  # Hide when nothing selected
        elif count == 1:
            self.update("[bold cyan]1[/] selected")
        else:
            if self.total > 0:
                self.update(f"[bold cyan]{count}[/] / {self.total} selected")
            else:
                self.update(f"[bold cyan]{count}[/] selected")

    def update_count(self, selected: int, total: int = 0) -> None:
        """Update both count and total.

        Args:
            selected: Number of selected resources
            total: Total number of available resources (optional)
        """
        self.total = total
        self.count = selected  # Setting count triggers watch_count
