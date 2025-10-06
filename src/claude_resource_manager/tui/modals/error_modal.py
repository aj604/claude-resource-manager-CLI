"""Error recovery modal with WCAG compliant user-friendly messages.

Implements WCAG 2.1 Success Criteria:
- 3.3.1: Error Identification
- 3.3.3: Error Suggestion
- 3.3.4: Error Prevention
"""

from typing import Literal, Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ErrorRecoveryModal(ModalScreen):
    """Modal dialog for error recovery with user-friendly messages and suggestions.

    Provides:
    - Clear, non-technical error descriptions
    - Actionable recovery suggestions
    - Multiple recovery options (Retry, Skip, Cancel)
    - Keyboard navigation support
    - Screen reader announcements

    The modal translates technical errors into language users can understand
    and provides clear paths forward to recover from the error condition.
    """

    DEFAULT_CSS = """
    ErrorRecoveryModal {
        align: center middle;
    }

    ErrorRecoveryModal > Container {
        width: 60;
        height: auto;
        max-height: 80%;
        padding: 1 2;
        background: $surface;
        border: double $error;
    }

    .error-title {
        text-style: bold;
        color: $error;
        margin-bottom: 1;
    }

    .error-message {
        margin-bottom: 1;
    }

    .error-suggestion {
        color: $warning;
        margin-bottom: 2;
    }

    .error-details {
        color: $text-secondary;
        border: solid $border;
        padding: 1;
        margin-bottom: 2;
        max-height: 10;
        overflow-y: auto;
    }

    .error-actions {
        align: center middle;
        margin-top: 1;
        height: 3;
    }

    .error-actions Button {
        margin: 0 1;
        min-width: 12;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("r", "retry", "Retry"),
        ("s", "skip", "Skip"),
    ]

    def __init__(
        self,
        error: Exception,
        context: str,
        show_details: bool = True,
        id: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the error recovery modal.

        Args:
            error: The exception that occurred
            context: Description of what was being attempted
            show_details: Whether to show technical error details
            id: Optional ID for the modal
            **kwargs: Additional arguments for parent class
        """
        super().__init__(id=id, **kwargs)
        self.error = error
        self.context = context
        self.show_details = show_details
        self.result: Optional[Literal["retry", "skip", "cancel"]] = None
        self._previous_focus = None

    def compose(self) -> ComposeResult:
        """Compose the modal UI."""
        with Container():
            # Error title
            yield Static(f"Error: {self.context}", classes="error-title")

            # User-friendly error message
            yield Static(self._format_user_message(), classes="error-message")

            # Recovery suggestion
            suggestion = self._format_suggestion()
            if suggestion:
                yield Static(suggestion, classes="error-suggestion")

            # Technical details (collapsible)
            if self.show_details and str(self.error):
                yield Static(f"Technical details:\n{str(self.error)}", classes="error-details")

            # Action buttons
            with Horizontal(classes="error-actions"):
                yield Button("Retry", id="retry", variant="primary")
                yield Button("Skip", id="skip", variant="default")
                yield Button("Cancel", id="cancel", variant="error")

    def on_mount(self) -> None:
        """Handle mount event - save focus and announce."""
        # Save current focus for restoration
        if self.app.focused:
            self._previous_focus = self.app.focused

        # Announce error to screen readers

        if hasattr(self.app, "screen_reader"):
            self.app.screen_reader.announce_modal_open("Error")
            self.app.screen_reader.announce_error(self._format_user_message())

        # Focus on retry button by default
        self.query_one("#retry", Button).focus()

    def _format_user_message(self) -> str:
        """Convert technical error to user-friendly message.

        Returns:
            Human-readable error description
        """
        error_type = type(self.error).__name__
        error_str = str(self.error).lower()

        # Network/Connection errors
        if any(x in error_type.lower() for x in ["network", "connection", "timeout"]):
            return "Unable to connect to the internet. Please check your network connection and try again."
        elif "proxy" in error_str:
            return "Unable to connect through your proxy server. Please check your proxy settings."
        elif "dns" in error_str or "hostname" in error_str:
            return "Unable to reach the server. Please check your internet connection."

        # File/Permission errors
        elif isinstance(self.error, FileNotFoundError):
            filename = getattr(self.error, "filename", "the requested file")
            return f"Could not find {filename}. It may have been moved or deleted."
        elif isinstance(self.error, PermissionError):
            return (
                "You don't have permission to perform this action. Please check your access rights."
            )
        elif "permission" in error_str or "access denied" in error_str:
            return "Access denied. You may need administrator privileges for this operation."

        # Resource errors
        elif "not found" in error_str:
            return "The requested resource could not be found. It may have been removed or renamed."
        elif "already exists" in error_str:
            return "This item already exists. Please choose a different name or location."
        elif "disk space" in error_str or "no space" in error_str:
            return "Not enough disk space available. Please free up some space and try again."

        # Validation errors
        elif "invalid" in error_str:
            return "The provided information is not valid. Please check and correct your input."
        elif "format" in error_str:
            return "The file or data format is not supported. Please use a compatible format."

        # Installation errors
        elif "dependency" in error_str:
            return "Required components are missing. Some features may not work correctly."
        elif "version" in error_str:
            return "Version compatibility issue detected. An update may be required."

        # Generic fallback
        else:
            return f"An unexpected problem occurred: {str(self.error)[:100]}"

    def _format_suggestion(self) -> str:
        """Provide recovery suggestions based on error type.

        Returns:
            Actionable suggestion for error recovery
        """
        error_type = type(self.error).__name__
        error_str = str(self.error).lower()

        # Network suggestions
        if any(x in error_type.lower() for x in ["network", "connection", "timeout"]):
            return "Try: Check your Wi-Fi or ethernet connection, disable VPN if active, or restart your network."
        elif "proxy" in error_str:
            return "Try: Verify proxy settings in your system preferences or environment variables."

        # Permission suggestions
        elif isinstance(self.error, PermissionError) or "permission" in error_str:
            return "Try: Run with administrator/sudo privileges or check folder permissions."

        # File suggestions
        elif isinstance(self.error, FileNotFoundError):
            return "Try: Verify the file path, check if the file was moved, or restore from backup."

        # Space suggestions
        elif "disk space" in error_str or "no space" in error_str:
            return "Try: Delete temporary files, empty trash, or move to a drive with more space."

        # Format suggestions
        elif "format" in error_str or "invalid" in error_str:
            return "Try: Check the expected format in documentation or use a validation tool."

        # Installation suggestions
        elif "dependency" in error_str:
            return "Try: Update your package manager, install missing dependencies, or use '--skip-deps' flag."

        # Generic suggestion
        else:
            return "Try: Retry the operation, restart the application, or check the logs for more details."

    @on(Button.Pressed, "#retry")
    async def on_retry(self) -> None:
        """Handle retry button press."""
        self.result = "retry"
        await self._dismiss_with_result()

    @on(Button.Pressed, "#skip")
    async def on_skip(self) -> None:
        """Handle skip button press."""
        self.result = "skip"
        await self._dismiss_with_result()

    @on(Button.Pressed, "#cancel")
    async def on_cancel(self) -> None:
        """Handle cancel button press."""
        self.result = "cancel"
        await self._dismiss_with_result()

    def action_retry(self) -> None:
        """Keyboard shortcut for retry."""
        self.result = "retry"
        self.app.call_from_thread(self._dismiss_with_result)

    def action_skip(self) -> None:
        """Keyboard shortcut for skip."""
        self.result = "skip"
        self.app.call_from_thread(self._dismiss_with_result)

    def action_cancel(self) -> None:
        """Keyboard shortcut for cancel/escape."""
        self.result = "cancel"
        self.app.call_from_thread(self._dismiss_with_result)

    async def _dismiss_with_result(self) -> None:
        """Dismiss the modal and return result."""
        # Announce closing
        if hasattr(self.app, "screen_reader"):
            self.app.screen_reader.announce_modal_close("Error")

        # Restore focus
        if self._previous_focus:
            self._previous_focus.focus()

        # Dismiss with result
        self.dismiss(self.result)
