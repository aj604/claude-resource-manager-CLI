# VHS tape file - Quick Start Demo (30 seconds)
# Comprehensive workflow demonstration of Claude Resource Manager CLI
# Duration: ~30 seconds
# Shows: Launch, Navigate, Search, Select, Install

# Configuration
Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 800
Set TypingSpeed 50ms
Set Theme "Dracula"

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
Type "crm browse"
Enter
Sleep 3s

# Navigate with arrow keys
Type "j"  # Move down
Sleep 500ms
Type "j"  # Move down again
Sleep 500ms
Type "k"  # Move up
Sleep 500ms

# View resource details
Enter  # Open details
Sleep 2s
Escape  # Close details
Sleep 1s

# Search for a resource
Type "/"  # Open search
Sleep 500ms
Type "model"  # Search term
Sleep 1s
Enter  # Apply search
Sleep 2s

# Clear search
Type "/"  # Open search again
Sleep 500ms
Ctrl+U  # Clear search field
Escape  # Close search
Sleep 1s

# Navigate categories
Tab  # Cycle category
Sleep 1s
Tab  # Next category
Sleep 1s
Tab  # Next category
Sleep 1s

# Select a resource
Type "j"  # Move to desired item
Sleep 500ms
Space  # Select item
Sleep 1s

# Multi-select another item
Type "j"  # Move down
Sleep 500ms
Space  # Select another item
Sleep 1s

# Install selected resources
Type "i"  # Install command
Sleep 2s

# Show success and exit
Type "q"  # Quit
Sleep 1s

# Summary
Type "# Demo complete! Selected resources have been installed."
Enter
Sleep 2s