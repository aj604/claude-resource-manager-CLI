# VHS tape file - Help System Demo (15 seconds)
# Demonstrates help modal and keyboard shortcuts
# Duration: ~15 seconds
# Shows: Help modal, keyboard shortcuts, using shortcuts

# Configuration
Set Shell "bash"
Set FontSize 14
Set Width 1000
Set Height 600
Set TypingSpeed 50ms
Set Theme "Dracula"
Set Framerate 12

# Output
Output demo/output/help-system.gif

# Introduction
Type "# Help System Demo - Keyboard Shortcuts"
Enter
Sleep 1s

# Launch the TUI
Type ".venv/bin/crm browse"
Enter
Sleep 4s

# Open help modal
Type "?"  # Open help
Sleep 4s

# Close help modal
Escape  # Close help
Sleep 800ms

# Demonstrate search shortcut from help
Type "/"  # Search (as shown in help)
Sleep 500ms
Type "agent"
Sleep 1s
Enter  # Apply search
Sleep 1.5s

# Clear search
Escape  # Clear search
Sleep 800ms

# Show selection shortcut
Space  # Select
Sleep 1.2s
Down
Sleep 700ms
Space  # Select another
Sleep 1.2s

# Navigate with selections
Down
Sleep 600ms
Up
Sleep 600ms

# Open help again briefly
Type "?"  # Show help is always available
Sleep 2.5s
Escape  # Close
Sleep 500ms

# Exit
Type "q"  # Quit
Sleep 500ms

# Summary
Type "# Press ? anytime for help with keyboard shortcuts!"
Enter
Sleep 1.5s