# VHS tape file - Categories Demo (20 seconds)
# Demonstrates category filtering and navigation
# Duration: ~20 seconds
# Shows: Tab cycling, category filtering, navigation within categories

# Configuration
Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 800
Set TypingSpeed 50ms
Set Theme "Dracula"

# Output
Output demo/output/categories.gif

# Introduction
Type "# Categories Demo - Filter by Resource Type"
Enter
Sleep 1s

# Launch the TUI
Type "crm browse"
Enter
Sleep 2s

# Show current category (All)
Sleep 1s

# Cycle through categories
Tab  # Next category
Sleep 1.5s

Tab  # Next category
Sleep 1.5s

Tab  # Next category
Sleep 1.5s

Tab  # Next category
Sleep 1.5s

# Navigate within a category
Type "j"  # Move down
Sleep 500ms
Type "j"  # Move down
Sleep 500ms
Type "k"  # Move up
Sleep 500ms

# View details in current category
Enter  # Open details
Sleep 2s
Escape  # Close details
Sleep 800ms

# Continue cycling categories
Tab  # Next category
Sleep 1.5s

Tab  # Next category
Sleep 1.5s

# Return to "All" categories
Tab  # Should cycle back to All
Sleep 1.5s

# Show all resources again
Type "j"  # Navigate in full list
Sleep 500ms
Type "j"
Sleep 500ms

# Exit
Type "q"  # Quit
Sleep 500ms

# Summary
Type "# Categories help you find resources by type quickly!"
Enter
Sleep 1.5s