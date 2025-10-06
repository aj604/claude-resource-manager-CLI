# VHS tape file - Help System Demo (20 seconds)
# Demonstrates help modal and keyboard shortcuts
# Duration: ~20 seconds
# Shows: Help modal, keyboard shortcuts, using shortcuts

# Configuration
Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 800
Set TypingSpeed 50ms
Set Theme "Dracula"

# Output
Output demo/output/help-system.gif

# Introduction
Type "# Help System Demo - Keyboard Shortcuts"
Enter
Sleep 1s

# Launch the TUI
Type "(source .venv/bin/activate 2>/dev/null || true) && crm browse"
Enter
Sleep 2s

# Open help modal
Type "?"  # Open help
Sleep 3s

# Navigate help (if scrollable)
Down  # Scroll down in help
Sleep 1s
Down
Sleep 1s
Up  # Scroll back up
Sleep 1s

# View all shortcuts
Sleep 2s

# Close help modal
Escape  # Close help
Sleep 1s

# Demonstrate a shortcut from help
Type "/"  # Search (as shown in help)
Sleep 500ms
Type "prompt"
Sleep 800ms
Enter  # Apply search
Sleep 1.5s

# Use another shortcut
Type "g"  # Go to top
Sleep 1s

Type "G"  # Go to bottom
Sleep 1s

# Show selection shortcut
Space  # Select
Sleep 800ms
Type "j"
Sleep 500ms
Space  # Select another
Sleep 800ms

# Clear selections
Type "c"  # Clear all
Sleep 1s

# Open help again briefly
Type "?"  # Show help is always available
Sleep 1.5s
Escape  # Close
Sleep 500ms

# Exit
Type "q"  # Quit
Sleep 500ms

# Summary
Type "# Press ? anytime for help with keyboard shortcuts!"
Enter
Sleep 1.5s