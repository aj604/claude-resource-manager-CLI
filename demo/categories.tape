# VHS tape file - Category Filtering Demo (18 seconds)
# Demonstrates category filtering with keyboard shortcuts
# Duration: ~18 seconds
# Shows: Category cycling with 'n' key, filtered resource lists

# Configuration
Set Shell "bash"
Set FontSize 14
Set Width 1000
Set Height 600
Set TypingSpeed 50ms
Set Theme "Dracula"
Set Framerate 12

# Output
Output demo/output/categories.gif

# Introduction
Type "# Category Filtering Demo - Press 'n' to cycle categories"
Enter
Sleep 1s

# Launch the TUI
Type ".venv/bin/crm browse"
Enter
Sleep 4s

# Show All category (default)
Sleep 1s

# Cycle to Agent category
Type "n"  # Next category → Agent
Sleep 1.8s

# Navigate within Agent category
Down
Sleep 700ms
Down
Sleep 700ms

# Cycle to Command category
Type "n"  # Next category → Command
Sleep 1.8s

# Navigate within Command category
Down
Sleep 700ms

# Cycle to Hook category
Type "n"  # Next category → Hook
Sleep 1.8s

# Cycle to Template category
Type "n"  # Next category → Template
Sleep 1.8s

# Cycle to MCP category
Type "n"  # Next category → MCP
Sleep 1.8s

# Cycle back to All
Type "n"  # Next category → All (cycles back)
Sleep 1.8s

# Navigate in full list
Down
Sleep 700ms
Down
Sleep 700ms

# Exit
Type "q"  # Quit
Sleep 500ms

# Summary
Type "# Press 'n' to cycle categories, 'N' (Shift+n) to go backwards!"
Enter
Sleep 1.5s