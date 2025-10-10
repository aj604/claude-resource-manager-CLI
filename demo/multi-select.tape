# VHS tape file - Multi-Select Demo (20 seconds)
# Demonstrates batch selection and installation
# Duration: ~20 seconds
# Shows: Space selection, checkboxes, batch operations

# Configuration
Set Shell "bash"
Set FontSize 14
Set Width 1000
Set Height 600
Set TypingSpeed 50ms
Set Theme "Dracula"
Set Framerate 12

# Output
Output demo/output/multi-select.gif

# Introduction
Type "# Multi-Select Demo - Batch Operations"
Enter
Sleep 1s

# Launch the TUI
Type ".venv/bin/crm browse"
Enter
Sleep 4s

# Select first item
Space  # Select current item
Sleep 1.2s

# Navigate and select more items
Down  # Move down
Sleep 500ms
Down  # Move down
Sleep 500ms
Space  # Select second item
Sleep 1.2s

Down  # Move down
Sleep 500ms
Down  # Move down
Sleep 500ms
Space  # Select third item
Sleep 1.2s

# Show selection count
Sleep 2s

# Deselect an item
Up  # Move up
Sleep 500ms
Space  # Deselect (toggle)
Sleep 1.2s

# Navigate to show selections are preserved
Down  # Move down
Sleep 500ms
Down  # Move down
Sleep 500ms
Down  # Move down
Sleep 500ms

# Select one more
Space  # Select another item
Sleep 1.2s

# Show final selection count
Sleep 2.5s

# Exit
Type q  # Quit
Sleep 500ms

# Summary
Type "# Batch operations complete! Multi-select demonstrated with Space."
Enter
Sleep 1.5s