# VHS Demo Documentation

This document explains the VHS demo system for the Claude Resource Manager CLI.

## Overview

We use [VHS](https://github.com/charmbracelet/vhs) to generate animated GIF demonstrations of the CLI in action. These demos:
- Showcase key features visually
- Help users understand the tool before installing
- Serve as regression tests (if demo fails, feature broke)
- Auto-update via CI/CD when code changes

## Demo Files

### quick-start.tape (30 seconds)
**Purpose:** Comprehensive workflow from start to finish

**Shows:**
- Launching the browser
- Navigating resources
- Searching
- Viewing details
- Selecting and installing

**Target Audience:** New users, README visitors

### fuzzy-search.tape (20 seconds)
**Purpose:** Demonstrate typo tolerance in search

**Shows:**
- Typing search query with typos
- Real-time filtering
- Match highlighting
- Clearing search

**Target Audience:** Users evaluating search capabilities

### multi-select.tape (20 seconds)
**Purpose:** Show batch operations

**Shows:**
- Selecting multiple resources with SPACE
- Visual selection indicators ([x])
- Selection count display
- Batch install workflow

**Target Audience:** Power users, efficiency-focused users

### categories.tape (20 seconds)
**Purpose:** Demonstrate organization system

**Shows:**
- TAB to cycle categories
- Filtered views (agents, commands, etc.)
- Category resource counts
- Returning to "All"

**Target Audience:** Users browsing large catalogs

### help-system.tape (20 seconds)
**Purpose:** Show built-in documentation

**Shows:**
- Pressing `?` to open help
- Keyboard shortcut list
- Modal navigation
- Closing with ESC

**Target Audience:** Users learning keyboard shortcuts

## Tape File Structure

Each `.tape` file follows this structure:

```tape
# Configuration
Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 800
Set TypingSpeed 50ms
Set Theme "Dracula"

# Output
Output demo/output/<name>.gif

# Demo actions
Type "crm browse"
Sleep 500ms
Enter
Sleep 2s
# ... more actions ...
```

### Best Practices

1. **Timing**: Natural pauses (1-2s after actions)
2. **Typing Speed**: 50-65ms realistic typing
3. **File Size**: Optimize to stay under 2MB
4. **Dimensions**: Always 1200x800px (GitHub optimal)
5. **Theme**: Dracula for consistency and readability

## Generating Demos

### Local Generation

```bash
# Install VHS
brew install vhs  # macOS
# OR
curl -LO https://github.com/charmbracelet/vhs/releases/latest/download/vhs_Linux_x86_64.tar.gz
tar -xzf vhs_Linux_x86_64.tar.gz && sudo mv vhs /usr/local/bin/  # Linux

# Generate all demos
make demos

# Generate specific demo
vhs demo/quick-start.tape

# Clean output
make demo-clean
```

### CI/CD Generation

Demos auto-generate on:
- Push to `main` (commits GIFs back)
- Pull requests (artifacts + comment)
- Manual workflow dispatch

See [.github/workflows/vhs-demos.yml](../.github/workflows/vhs-demos.yml)

## Editing Demos

To update a demo:

1. **Edit .tape file** in `demo/`
2. **Test locally**: `vhs demo/<name>.tape`
3. **Review GIF**: Open `demo/output/<name>.gif`
4. **Adjust timing** if needed (Sleep commands)
5. **Commit changes** - CI will regenerate

### Common Edits

**Speed up demo:**
```tape
# Reduce sleep times
Sleep 1s  # was 2s
```

**Add new action:**
```tape
Type "additional command"
Sleep 500ms
Enter
```

**Change appearance:**
```tape
Set Theme "GitHub Dark"  # or other theme
Set FontSize 18          # larger text
```

## Troubleshooting

### GIF Too Large

```bash
# Use gifsicle to optimize
gifsicle --lossy=80 -O3 input.gif -o output.gif
```

### Demo Timing Feels Off

Edit Sleep commands:
- Too fast: Increase Sleep values
- Too slow: Decrease Sleep values
- Typical: 500ms-2s between actions

### VHS Fails in CI

Check:
- Terminal dimensions (1200x800)
- VHS version (v0.7.2 pinned)
- Headless display (Xvfb) running
- ttyd installed

## File Size Guidelines

| Demo | Target Size | Max Size | Typical Size |
|------|-------------|----------|--------------|
| quick-start.gif | < 2MB | 2MB | 1.5-1.8MB |
| fuzzy-search.gif | < 2MB | 2MB | 0.8-1.2MB |
| multi-select.gif | < 2MB | 2MB | 0.9-1.3MB |
| categories.gif | < 2MB | 2MB | 0.8-1.2MB |
| help-system.gif | < 2MB | 2MB | 0.7-1.0MB |
| **Total** | < 10MB | 10MB | 6-7MB |

## Maintenance

### Regular Updates

Update demos when:
- Major UI changes occur
- New features added
- Keyboard shortcuts change
- Theme or styling updates

### Quality Checks

Before committing demos:
- [ ] File sizes acceptable
- [ ] Dimensions correct (1200x800)
- [ ] Animations smooth (no flicker)
- [ ] Timing feels natural
- [ ] All actions complete successfully
- [ ] Text readable

## Integration with Documentation

### README.md

Demos embedded at the top (above-the-fold):
```markdown
## What Does It Look Like?

![Quick Start Demo](demo/output/quick-start.gif)
```

### Feature Docs

Demos embedded within feature sections:
```markdown
## Fuzzy Search

![Fuzzy Search in Action](../demo/output/fuzzy-search.gif)
```

### Best Practices for Embedding

1. **Position**: Place demos early in documents
2. **Context**: Add descriptive captions
3. **Links**: Provide direct links to GIFs
4. **Fallback**: Use alt text for accessibility
5. **Size**: Ensure GIFs load quickly (< 2MB)

## VHS Tape File Reference

### Configuration Commands

```tape
Set Shell "bash"              # Shell to use
Set FontSize 16               # Font size in px
Set Width 1200                # Terminal width in px
Set Height 800                # Terminal height in px
Set TypingSpeed 50ms          # Typing speed per character
Set Theme "Dracula"           # Color theme
Set Padding 20                # Terminal padding
Set Framerate 30              # Output frame rate
Output demo/output/demo.gif   # Output file path
```

### Action Commands

```tape
Type "text"                   # Type text
Enter                         # Press Enter
Escape                        # Press Escape
Space                         # Press Space
Tab                           # Press Tab
Backspace                     # Press Backspace
Up/Down/Left/Right            # Arrow keys
Ctrl+<key>                    # Control key combo
Sleep 1s                      # Pause (s/ms units)
Hide                          # Hide following commands
Show                          # Show following commands
```

### Demo Flow Pattern

```tape
# 1. Setup
Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 800

# 2. Configure
Set TypingSpeed 50ms
Set Theme "Dracula"
Output demo/output/example.gif

# 3. Execute
Type "command"
Sleep 500ms
Enter
Sleep 2s

# 4. Interact
Down
Down
Space
Enter
Sleep 1s

# 5. Complete
Type "q"
Sleep 500ms
```

## Advanced Techniques

### Loop Demonstrations

For continuous demos:
```tape
# Not supported in VHS
# Create appearance of loop by repeating actions
```

### Highlighting Specific Areas

VHS doesn't support overlays, so use:
- Cursor movement to draw attention
- Pauses at important moments
- Strategic Sleep timings

### Multi-Step Workflows

Break complex workflows into segments:
```tape
# Step 1: Launch
Type "crm browse"
Enter
Sleep 2s

# Step 2: Search
Type "/"
Sleep 500ms
Type "architect"
Sleep 1s

# Step 3: Select
Down
Space
Sleep 500ms

# Step 4: Install
Type "i"
Sleep 2s
```

## Testing Strategy

### Manual Testing

1. Generate demo: `vhs demo/test.tape`
2. Open GIF in browser
3. Check for:
   - Smooth animations
   - Readable text
   - Correct timing
   - Expected actions

### Automated Testing

```bash
# VHS integration tests
.venv/bin/pytest tests/integration/test_vhs_integration.py -v

# Validates:
# - All .tape files exist
# - Required commands present
# - Output paths correct
# - File sizes within limits
```

### CI/CD Testing

GitHub Actions validates:
- VHS installation successful
- All demos generate without errors
- File sizes within limits
- GIFs committed to repository

## Performance Optimization

### Reduce File Size

1. **Lower frame rate**: `Set Framerate 24` (default 30)
2. **Reduce duration**: Cut unnecessary pauses
3. **Smaller dimensions**: `Set Width 1000` (from 1200)
4. **Post-process**: Use gifsicle optimization

### Maintain Quality

Balance file size with quality:
- Don't go below 20 FPS
- Keep width ≥ 1000px for readability
- Maintain 50ms typing speed for realism

## Future Enhancements

Potential future additions:
- [ ] Interactive HTML demos (asciinema)
- [ ] Video tutorials (MP4 format)
- [ ] Error scenario demos
- [ ] Advanced workflow demos
- [ ] Mobile-responsive demos
- [ ] Internationalized demos

## Resources

### Official Documentation
- [VHS GitHub](https://github.com/charmbracelet/vhs)
- [VHS Documentation](https://github.com/charmbracelet/vhs/blob/main/README.md)

### Related Tools
- [ttyd](https://github.com/tsl0922/ttyd) - Terminal sharing
- [asciinema](https://asciinema.org/) - Terminal session recorder
- [gifsicle](https://www.lcdf.org/gifsicle/) - GIF optimizer

### Themes
- [Dracula](https://draculatheme.com/)
- [GitHub Dark](https://github.com/settings/appearance)
- [Monokai](https://monokai.pro/)

---

**Last Updated:** December 2024
**Maintainer:** Claude Resource Manager Team
**Version:** 1.0.0
