# VHS tape file - Fuzzy Search Demo (15 seconds)
# Demonstrates fuzzy search capabilities with typo tolerance
# Duration: ~15 seconds
# Shows: Search with typos, fuzzy matching, result filtering

# Configuration
Set Shell "bash"
Set FontSize 14
Set Width 1000
Set Height 600
Set TypingSpeed 50ms
Set Theme "Dracula"
Set Framerate 12

# Output
Output demo/output/fuzzy-search.gif

# Introduction
Type "# Fuzzy Search Demo - Typo Tolerance"
Enter
Sleep 1s

# Launch the TUI
Type ".venv/bin/crm browse"
Enter
Sleep 4s

# Open search
Type "/"  # Open search dialog
Sleep 500ms

# Search with typos (intentional misspellings)
Type "architet"  # Typo for "architect"
Sleep 1s

# Show fuzzy matching working
Enter  # Apply search
Sleep 2s

# Navigate results to show matches found
Down
Sleep 700ms
Down
Sleep 700ms

# Clear and try another fuzzy search
Escape  # Clear search
Sleep 800ms
Type "/"  # Open search again
Sleep 500ms

# Another example with typos
Type "secrity"  # Typo for "security"
Sleep 1s
Enter  # Apply search
Sleep 2s

# Navigate to show search results
Down
Sleep 700ms

# Clear search and show all resources
Escape  # Close search (shows all)
Sleep 1s

# Exit
Type q  # Quit
Sleep 500ms

# Summary
Type "# Fuzzy search handles typos and finds relevant matches!"
Enter
Sleep 1.5s