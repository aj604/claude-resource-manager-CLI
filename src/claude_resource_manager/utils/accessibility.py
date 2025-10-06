"""Accessibility utilities for WCAG 2.1 AA compliance.

Provides helper functions for:
- Color contrast calculation
- WCAG compliance checking
- Theme validation
- Accessibility testing utilities
"""

from typing import Dict, List, Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color string to RGB tuple.

    Args:
        hex_color: Color in hex format (#RRGGBB or RRGGBB)

    Returns:
        Tuple of (red, green, blue) values (0-255)
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")

    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def calculate_relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate relative luminance of an RGB color per WCAG formula.

    Args:
        rgb: Tuple of (red, green, blue) values (0-255)

    Returns:
        Relative luminance value (0.0 to 1.0)
    """

    def channel_luminance(value: int) -> float:
        """Calculate luminance for a single color channel."""
        value = value / 255.0
        if value <= 0.03928:
            return value / 12.92
        else:
            return ((value + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return (
        0.2126 * channel_luminance(r)
        + 0.7152 * channel_luminance(g)
        + 0.0722 * channel_luminance(b)
    )


def calculate_contrast_ratio(fg: str, bg: str) -> float:
    """Calculate WCAG contrast ratio between two colors.

    Args:
        fg: Foreground color in hex format
        bg: Background color in hex format

    Returns:
        Contrast ratio from 1:1 to 21:1
    """
    fg_rgb = hex_to_rgb(fg)
    bg_rgb = hex_to_rgb(bg)

    fg_lum = calculate_relative_luminance(fg_rgb)
    bg_lum = calculate_relative_luminance(bg_rgb)

    # Ensure lighter color is in numerator
    lighter = max(fg_lum, bg_lum)
    darker = min(fg_lum, bg_lum)

    return (lighter + 0.05) / (darker + 0.05)


def wcag_aa_passes(fg: str, bg: str, large_text: bool = False) -> bool:
    """Check if color combination meets WCAG AA standards.

    Args:
        fg: Foreground color in hex format
        bg: Background color in hex format
        large_text: Whether text is large (18pt+ or 14pt+ bold)

    Returns:
        True if contrast ratio meets WCAG AA requirements
    """
    ratio = calculate_contrast_ratio(fg, bg)
    required_ratio = 3.0 if large_text else 4.5
    return ratio >= required_ratio


def wcag_aaa_passes(fg: str, bg: str, large_text: bool = False) -> bool:
    """Check if color combination meets WCAG AAA standards.

    Args:
        fg: Foreground color in hex format
        bg: Background color in hex format
        large_text: Whether text is large (18pt+ or 14pt+ bold)

    Returns:
        True if contrast ratio meets WCAG AAA requirements
    """
    ratio = calculate_contrast_ratio(fg, bg)
    required_ratio = 4.5 if large_text else 7.0
    return ratio >= required_ratio


def validate_theme_accessibility(theme_colors: Dict[str, str]) -> Dict[str, List[str]]:
    """Validate a theme's color combinations for WCAG compliance.

    Args:
        theme_colors: Dictionary of color values

    Returns:
        Dictionary with compliance results and any failures
    """
    results = {
        "passes_aa": True,
        "passes_aaa": False,
        "failures": [],
        "warnings": [],
        "contrast_ratios": {},
    }

    # Define color combinations to test
    combinations = [
        # Normal text on backgrounds
        ("text_primary", "background", False),
        ("text_secondary", "background", False),
        ("text_disabled", "background", False),
        ("text_primary", "surface", False),
        # UI elements
        ("primary", "background", False),
        ("success", "background", False),
        ("warning", "background", False),
        ("error", "background", False),
        ("info", "background", False),
        # Selected items
        ("selected_fg", "selected_bg", False),
        # Large text (assumed for headers)
        ("text_primary", "background", True),
    ]

    for fg_key, bg_key, large in combinations:
        if fg_key not in theme_colors or bg_key not in theme_colors:
            continue

        fg = theme_colors[fg_key]
        bg = theme_colors[bg_key]
        ratio = calculate_contrast_ratio(fg, bg)

        combo_name = f"{fg_key} on {bg_key}"
        results["contrast_ratios"][combo_name] = ratio

        # Check AA compliance
        if not wcag_aa_passes(fg, bg, large):
            results["passes_aa"] = False
            results["failures"].append(
                f"{combo_name}: {ratio:.2f}:1 (needs {3.0 if large else 4.5}:1)"
            )
        elif ratio < 7.0 and not large:
            # Warning for combinations that pass AA but not AAA
            results["warnings"].append(f"{combo_name}: {ratio:.2f}:1 (AAA needs 7.0:1)")

    # Check if theme passes AAA
    results["passes_aaa"] = all(
        ratio >= (4.5 if "large" in name else 7.0)
        for name, ratio in results["contrast_ratios"].items()
    )

    return results


def generate_accessible_color(bg: str, min_contrast: float = 4.5) -> str:
    """Generate a foreground color with sufficient contrast against background.

    Args:
        bg: Background color in hex format
        min_contrast: Minimum contrast ratio required

    Returns:
        Hex color that meets contrast requirement
    """
    bg_rgb = hex_to_rgb(bg)
    bg_lum = calculate_relative_luminance(bg_rgb)

    # Determine if we need a light or dark color
    if bg_lum > 0.5:
        # Dark background, use light text
        # Start with white and darken if needed
        for gray_value in range(255, 0, -5):
            fg = f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"
            if calculate_contrast_ratio(fg, bg) >= min_contrast:
                return fg
    else:
        # Light background, use dark text
        # Start with black and lighten if needed
        for gray_value in range(0, 256, 5):
            fg = f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"
            if calculate_contrast_ratio(fg, bg) >= min_contrast:
                return fg

    # Fallback to black or white
    return "#000000" if bg_lum > 0.5 else "#ffffff"


class AccessibilityChecker:
    """Helper class for checking accessibility compliance in tests."""

    def __init__(self):
        """Initialize the accessibility checker."""
        self.violations = []
        self.warnings = []
        self.passes = []

    def check_contrast(self, fg: str, bg: str, element_name: str, large_text: bool = False) -> bool:
        """Check contrast ratio for an element.

        Args:
            fg: Foreground color
            bg: Background color
            element_name: Name of the element being checked
            large_text: Whether this is large text

        Returns:
            True if check passes
        """
        ratio = calculate_contrast_ratio(fg, bg)
        required = 3.0 if large_text else 4.5

        if ratio < required:
            self.violations.append(f"{element_name}: Contrast {ratio:.2f}:1 (needs {required}:1)")
            return False
        else:
            self.passes.append(f"{element_name}: Contrast {ratio:.2f}:1 (✓)")
            return True

    def check_keyboard_navigation(
        self, element_name: str, can_focus: bool, has_keyboard_handler: bool
    ) -> bool:
        """Check keyboard accessibility for an element.

        Args:
            element_name: Name of the element
            can_focus: Whether element can receive focus
            has_keyboard_handler: Whether element handles keyboard events

        Returns:
            True if check passes
        """
        if not can_focus and has_keyboard_handler:
            self.violations.append(f"{element_name}: Has keyboard handler but cannot receive focus")
            return False

        if can_focus and not has_keyboard_handler:
            self.warnings.append(f"{element_name}: Can focus but no keyboard handler")

        self.passes.append(f"{element_name}: Keyboard navigation OK")
        return True

    def get_report(self) -> Dict[str, any]:
        """Get accessibility check report.

        Returns:
            Dictionary with check results
        """
        return {
            "passes": len(self.passes),
            "violations": len(self.violations),
            "warnings": len(self.warnings),
            "compliance_percentage": (
                len(self.passes) / (len(self.passes) + len(self.violations)) * 100
                if self.passes or self.violations
                else 100
            ),
            "details": {
                "passes": self.passes,
                "violations": self.violations,
                "warnings": self.warnings,
            },
        }
