# Daily Notes - Ulauncher Extension

A Ulauncher 5 extension for managing a daily markdown journal.

## Features

- **Quick Open**: Open the current week's daily notes file
- **Quick Insert**: Insert notes without opening the file
- **Automatic Organization**: Creates weekly markdown files organized by year and week number
- **Auto Date Headers**: Automatically adds markdown headers for each day
- **Configurable**: Choose your notes directory, date format, and preferred editor

## Usage

### Open Daily Notes

1. Open Ulauncher
2. Type `dn` (or your configured keyword)
3. Select "Open Daily Notes" and press Enter

### Insert a Quick Note

1. Open Ulauncher
2. Type `dn <your note text>`
   - Example: `dn Remember to call the dentist`
3. Press Enter to insert the note

The note will be added as a bullet point under today's date header.

## Configuration

Access preferences in Ulauncher Preferences > Extensions > Daily Notes:

- **Notes Directory**: Where to store your daily notes (default: `~/daily-notes`)
- **Date Format**: Python strftime format for date headers (default: `%A, %d %b`)
  - Examples:
    - `%A, %d %b` → "Monday, 06 Jan"
    - `%Y-%m-%d` → "2026-01-06"
    - `%B %d, %Y` → "January 06, 2026"
- **Text Editor**: Command to open notes (default: `xdg-open`)
  - Examples: `gedit`, `code`, `kate`, `vim`, `subl`

## File Organization

Notes are organized as weekly markdown files:

```
~/daily-notes/
├── 2026.01-daily-notes.md
├── 2026.02-daily-notes.md
└── ...
```

Each file contains date headers for each day:

```markdown
## Monday, 06 Jan

- Your note here
- Another note


## Sunday, 05 Jan

- Previous day's notes
```

## How It Works

The extension:
1. Creates a new weekly file if it doesn't exist
2. Automatically prepends today's date header if not present
3. Inserts notes as bullet points after the date header
4. Uses the ISO week number for file naming

## Requirements

- Ulauncher 5+ (API v2)
- Python 3.7+

## Troubleshooting

### Notes directory doesn't exist
The extension will automatically create the directory when you first use it.

### Editor doesn't open
Make sure your configured editor command is installed and in your PATH. Try using `xdg-open` for the system default application.

### Icon not showing
The icon will default to the SVG if PNG conversion fails. This doesn't affect functionality.
