# VHS tape file - Fuzzy Search Demo (20 seconds)
# Demonstrates fuzzy search capabilities with typo tolerance
# Duration: ~20 seconds
# Shows: Search with typos, fuzzy matching, result filtering

# Configuration
Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 800
Set TypingSpeed 65ms
Set Theme "Dracula"

# Output
Output demo/output/fuzzy-search.gif

# Introduction
Type "# Fuzzy Search Demo - Typo Tolerance"
Enter
Sleep 1s

# Launch the TUI
Type "(source .venv/bin/activate 2>/dev/null || true) && crm browse"
Enter
Sleep 2s

# Open search
Type "/"  # Open search dialog
Sleep 500ms

# Search with typos (intentional misspellings)
Type "comptr"  # Typo for "computer"
Sleep 1s

# Show fuzzy matching working
Enter  # Apply search
Sleep 2s

# Clear and try another fuzzy search
Type "/"  # Open search again
Sleep 500ms
Ctrl+U  # Clear current search
Sleep 300ms

# Another example with typos
Type "vison"  # Typo for "vision"
Sleep 1s
Enter  # Apply search
Sleep 2s

# Show exact match attempt
Type "/"  # Open search
Sleep 500ms
Ctrl+U  # Clear
Sleep 300ms
Type "model context"  # Multi-word search
Sleep 1s
Enter  # Apply search
Sleep 2s

# Clear search and show all resources
Type "/"  # Open search
Sleep 500ms
Ctrl+U  # Clear search completely
Escape  # Close search (shows all)
Sleep 1s

# Exit
Type "q"  # Quit
Sleep 500ms

# Summary
Type "# Fuzzy search handles typos and finds relevant matches!"
Enter
Sleep 1.5s