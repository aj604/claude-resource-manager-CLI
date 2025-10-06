# VHS tape file - Multi-Select Demo (20 seconds)
# Demonstrates batch selection and installation
# Duration: ~20 seconds
# Shows: Space selection, checkboxes, batch operations

# Configuration
Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 800
Set TypingSpeed 50ms
Set Theme "Dracula"

# Output
Output demo/output/multi-select.gif

# Introduction
Type "# Multi-Select Demo - Batch Operations"
Enter
Sleep 1s

# Launch the TUI
Type "crm browse"
Enter
Sleep 2s

# Select first item
Space  # Select current item
Sleep 800ms

# Navigate and select more items
Type "j"  # Move down
Sleep 500ms
Type "j"  # Move down
Sleep 500ms
Space  # Select second item
Sleep 800ms

Type "j"  # Move down
Sleep 500ms
Type "j"  # Move down
Sleep 500ms
Space  # Select third item
Sleep 800ms

# Show selection count
Sleep 1.5s

# Deselect an item
Type "k"  # Move up
Sleep 500ms
Space  # Deselect (toggle)
Sleep 800ms

# Navigate to show selections are preserved
Type "j"  # Move down
Sleep 500ms
Type "j"  # Move down
Sleep 500ms
Type "j"  # Move down
Sleep 500ms

# Select one more
Space  # Select another item
Sleep 800ms

# Perform batch install
Type "i"  # Install selected
Sleep 2.5s

# Clear selections
Type "c"  # Clear all selections
Sleep 1s

# Exit
Type "q"  # Quit
Sleep 500ms

# Summary
Type "# Batch operations complete! Multiple resources installed at once."
Enter
Sleep 1.5s