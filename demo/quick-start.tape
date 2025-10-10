# VHS tape file - Quick Start Demo (30 seconds)
# Comprehensive workflow demonstration of Claude Resource Manager CLI
# Duration: ~30 seconds
# Shows: Launch, Navigate, Search, Select, Install

# Configuration
Set Shell "bash"
Set FontSize 14
Set Width 1000
Set Height 600
Set TypingSpeed 50ms
Set Theme "Dracula"
Set Framerate 12

# Output
Output demo/output/quick-start.gif

# Introduction
Type "# Claude Resource Manager - Quick Start Demo"
Enter
Sleep 1s

Type "# Launch the interactive browser"
Enter
Sleep 500ms

# Launch the TUI
Type ".venv/bin/crm browse"
Enter
Sleep 4s

# Navigate with arrow keys
Down  # Move down
Sleep 500ms
Down  # Move down again
Sleep 500ms
Up  # Move up
Sleep 500ms

# View resource details
Enter  # Open details
Sleep 2s
Escape  # Close details
Sleep 1s

# Search for a resource
Type "/"  # Open search
Sleep 500ms
Type "security"  # Search term
Sleep 1s
Enter  # Apply search
Sleep 2s
Escape  # Clear search text (first escape)
Sleep 500ms
Escape  # Return focus to table (second escape)
Sleep 1s

# Select a resource
Down  # Move to desired item
Sleep 500ms
Space  # Select item
Sleep 1s

# Multi-select another item
Down  # Move down
Sleep 500ms
Space  # Select another item
Sleep 1s

# Show selection status
Sleep 1.5s

# Install selected resources
Type "i"  # Trigger installation
Sleep 3s

# Exit to show completion
Type "q"  # Quit
Sleep 1s

# Summary
Type "# Demo complete! Resources installed successfully."
Enter
Sleep 2s