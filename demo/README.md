# VHS Demo Generation

This directory contains VHS tape files for generating animated GIF demonstrations of the Claude Resource Manager CLI.

## Prerequisites

Install VHS (by Charm):

### macOS
```bash
brew install vhs
```

### Linux
```bash
# Download latest release from GitHub
curl -LO https://github.com/charmbracelet/vhs/releases/latest/download/vhs_Linux_x86_64.tar.gz
tar -xzf vhs_Linux_x86_64.tar.gz
sudo mv vhs /usr/local/bin/
```

### Windows
```powershell
scoop install vhs
```

## Generating Demos

### All Demos
```bash
make demos
```

### Individual Demos
```bash
make demo-quick-start
make demo-fuzzy-search
make demo-multi-select
make demo-categories
make demo-help-system
```

### Clean Output
```bash
make demo-clean
```

## Tape Files

- `quick-start.tape` - 30-second comprehensive workflow demo
- `fuzzy-search.tape` - Fuzzy search with typo tolerance
- `multi-select.tape` - Batch selection and installation
- `categories.tape` - Category filtering demonstration
- `help-system.tape` - Help modal and keyboard shortcuts

## Output

Generated GIFs are saved to `demo/output/`:
- `quick-start.gif` (< 2MB, 1200x800px)
- `fuzzy-search.gif` (< 2MB, 1200x800px)
- `multi-select.gif` (< 2MB, 1200x800px)
- `categories.gif` (< 2MB, 1200x800px)
- `help-system.gif` (< 2MB, 1200x800px)

## Troubleshooting

### VHS Not Found
Ensure VHS is installed and in your PATH:
```bash
which vhs
```

### Demo Too Long
Edit the .tape file and reduce Sleep durations or remove steps.

### GIF Too Large
Use gifsicle to optimize:
```bash
gifsicle --lossy=80 -O3 input.gif -o output.gif
```

## Customization

Edit .tape files to:
- Change terminal theme (Set Theme "...")
- Adjust typing speed (Set TypingSpeed ...)
- Modify dimensions (Set Width/Height)
- Update demo workflow

## VHS Tape File Syntax

VHS uses a simple DSL for recording terminal sessions:

### Basic Commands
- `Type "text"` - Types text character by character
- `Enter` - Presses Enter key
- `Sleep <duration>` - Pauses for specified time (e.g., `Sleep 2s`, `Sleep 500ms`)
- `Ctrl+<key>` - Sends control key combination
- `Escape` - Sends ESC key
- `Space` - Sends space key
- `Tab` - Sends tab key
- `Down`, `Up`, `Left`, `Right` - Arrow keys

### Configuration
- `Set Shell "bash"` - Sets shell to use
- `Set FontSize <size>` - Font size in pixels
- `Set Width <pixels>` - Terminal width
- `Set Height <pixels>` - Terminal height
- `Set TypingSpeed <duration>` - Speed between keystrokes
- `Set Theme "<name>"` - Terminal color theme
- `Output <path>` - Output file path

## Demo Scripts Overview

### Quick Start (30s)
Comprehensive workflow showing:
1. Launch browser with `crm browse`
2. Navigate through resources with arrow keys
3. View details with Enter
4. Search for a resource
5. Select and install

### Fuzzy Search (20s)
Search capabilities:
1. Launch browser
2. Press `/` to search
3. Type with intentional typos
4. Show fuzzy matching results
5. Clear search and return

### Multi-Select (20s)
Batch operations:
1. Launch browser
2. Select multiple items with Space
3. Show selection indicators
4. Batch install with `i`
5. Confirm success

### Categories (20s)
Category filtering:
1. Launch browser
2. Press Tab to cycle categories
3. Show filtered results
4. Navigate within category
5. Return to "All" categories

### Help System (20s)
Help and shortcuts:
1. Launch browser
2. Press `?` for help
3. View keyboard shortcuts
4. Close with ESC
5. Use a demonstrated shortcut