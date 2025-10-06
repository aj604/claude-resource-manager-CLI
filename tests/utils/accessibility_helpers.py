"""Accessibility testing utilities for WCAG 2.1 AA compliance.

This module provides helper functions for testing accessibility features:
- Color contrast ratio calculation (WCAG 2.1 criterion 1.4.3)
- ARIA announcement verification
- Keyboard navigation testing
- Focus management validation

All calculations follow W3C WCAG 2.1 specifications.
"""

from typing import Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., "#ffffff" or "ffffff")

    Returns:
        RGB tuple (r, g, b) with values 0-255

    Example:
        >>> hex_to_rgb("#ffffff")
        (255, 255, 255)
    """
    # Remove leading '#' if present
    hex_color = hex_color.lstrip("#")

    # Convert to RGB
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def calculate_relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate relative luminance per WCAG 2.1 formula.

    Formula from: https://www.w3.org/TR/WCAG21/#dfn-relative-luminance

    For the sRGB colorspace, the relative luminance of a color is defined as:
    L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    where R, G and B are defined as:
    - if RsRGB <= 0.03928 then R = RsRGB/12.92
    - else R = ((RsRGB+0.055)/1.055) ^ 2.4

    Args:
        rgb: RGB tuple with values 0-255

    Returns:
        Relative luminance value (0.0 to 1.0)
    """
    # Convert to 0-1 range
    r, g, b = [val / 255.0 for val in rgb]

    # Apply sRGB gamma correction
    def adjust_channel(val: float) -> float:
        if val <= 0.03928:
            return val / 12.92
        return ((val + 0.055) / 1.055) ** 2.4

    r = adjust_channel(r)
    g = adjust_channel(g)
    b = adjust_channel(b)

    # Calculate relative luminance
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def calculate_contrast_ratio(color1: str, color2: str) -> float:
    """Calculate WCAG contrast ratio between two colors.

    Formula from: https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio

    Contrast ratio = (L1 + 0.05) / (L2 + 0.05)
    where L1 is the relative luminance of the lighter color
    and L2 is the relative luminance of the darker color.

    WCAG 2.1 AA Requirements:
    - Normal text: >= 4.5:1
    - Large text (18pt+ or 14pt+ bold): >= 3:1

    Args:
        color1: First color (hex format, e.g., "#ffffff")
        color2: Second color (hex format, e.g., "#000000")

    Returns:
        Contrast ratio (1.0 to 21.0, where 21.0 is black on white)

    Example:
        >>> calculate_contrast_ratio("#ffffff", "#000000")
        21.0
        >>> calculate_contrast_ratio("#ffffff", "#767676")
        4.54  # Passes WCAG AA for normal text
    """
    # Convert to RGB
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)

    # Calculate luminance
    lum1 = calculate_relative_luminance(rgb1)
    lum2 = calculate_relative_luminance(rgb2)

    # Ensure L1 is the lighter color
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)

    # Calculate contrast ratio
    ratio = (lighter + 0.05) / (darker + 0.05)

    return round(ratio, 2)


def get_aria_announcement(app) -> str:
    """Get current ARIA live region text from app.

    This function queries the app for the ARIA live region and returns
    its current announcement text. Uses announcement history to retrieve
    the most recent announcement, regardless of whether the timer has cleared it.

    Args:
        app: Textual App instance

    Returns:
        Most recent announcement text, or empty string if no announcement
    """
    try:
        # Query for ARIA live region from the current screen
        # (not app root, since live region is on the screen)
        screen = app.screen if hasattr(app, 'screen') else app
        live_region = screen.query_one("#aria-live-region")

        # Use new test helper method (immune to timer clearing)
        if hasattr(live_region, "get_last_announcement"):
            return live_region.get_last_announcement()

        # Fallback: check announcement attribute (reactive property)
        if hasattr(live_region, "announcement"):
            return str(live_region.announcement)

        # Fallback: check renderable
        if hasattr(live_region, "renderable"):
            text = str(live_region.renderable)
            if text and text.strip():
                return text

        # Last resort: convert widget to string
        return str(live_region)
    except Exception:
        # No live region found
        return ""


def verify_focus_order(app, expected_order: list) -> bool:
    """Verify that tab navigation follows expected focus order.

    Tests WCAG 2.1 criterion 2.4.3 - Focus Order.

    Args:
        app: Textual App instance
        expected_order: List of widget IDs in expected focus order

    Returns:
        True if focus order matches expected, False otherwise
    """
    try:
        screen = app.screen if hasattr(app, 'screen') else app
        # Query all widgets with can_focus=True
        focusable = [w for w in screen.query("*") if w.can_focus]
        actual_ids = [w.id for w in focusable if w.id]

        # Check if expected widgets exist in order
        expected_indices = []
        for expected_id in expected_order:
            try:
                idx = actual_ids.index(expected_id)
                expected_indices.append(idx)
            except ValueError:
                return False  # Expected widget not found

        # Verify indices are in ascending order
        return expected_indices == sorted(expected_indices)
    except Exception:
        return False


def check_keyboard_trap(app, modal_id: str) -> bool:
    """Check if user can escape from a modal/component (no keyboard trap).

    Tests WCAG 2.1 criterion 2.1.2 - No Keyboard Trap.

    Args:
        app: Textual App instance
        modal_id: ID of the modal/component to test

    Returns:
        True if user can escape, False if keyboard trap exists

    Note:
        This will FAIL until keyboard trap prevention is implemented.
    """
    try:
        # Check if ESC key handler exists on modal
        modal = app.query_one(f"#{modal_id}")
        return hasattr(modal, "action_close") or hasattr(modal, "action_dismiss")
    except Exception:
        # Modal not found or no escape mechanism - expected to fail
        return False


def wcag_aa_passes(contrast_ratio: float, is_large_text: bool = False) -> bool:
    """Check if contrast ratio passes WCAG 2.1 AA.

    WCAG 2.1 AA Requirements (criterion 1.4.3):
    - Normal text: >= 4.5:1
    - Large text: >= 3:1

    Large text is defined as:
    - 18pt (24px) or larger
    - 14pt (18.66px) or larger if bold

    Args:
        contrast_ratio: Calculated contrast ratio
        is_large_text: True if text is large (18pt+ or 14pt+ bold)

    Returns:
        True if passes WCAG AA, False otherwise
    """
    if is_large_text:
        return contrast_ratio >= 3.0
    return contrast_ratio >= 4.5


def wcag_aaa_passes(contrast_ratio: float, is_large_text: bool = False) -> bool:
    """Check if contrast ratio passes WCAG 2.1 AAA.

    WCAG 2.1 AAA Requirements (criterion 1.4.6):
    - Normal text: >= 7:1
    - Large text: >= 4.5:1

    Args:
        contrast_ratio: Calculated contrast ratio
        is_large_text: True if text is large (18pt+ or 14pt+ bold)

    Returns:
        True if passes WCAG AAA, False otherwise
    """
    if is_large_text:
        return contrast_ratio >= 4.5
    return contrast_ratio >= 7.0
