# Daily Notes - Ulauncher Extension

A Ulauncher 5 extension for managing a daily markdown journal in Joplin.

## Features

- **Quick Open**: Open the current week's note directly in Joplin
- **Quick Insert**: Insert notes without opening Joplin
- **Automatic Organization**: Creates weekly notes organized by year and ISO week number
- **Auto Date Headers**: Automatically adds markdown headers for each day

## Requirements

- Ulauncher 5+ (API v2)
- Python 3.7+
- Joplin desktop app with the Web Clipper server enabled

## Setup

1. In Joplin, go to **Tools → Options → Web Clipper** and enable the clipper service. Copy the API token.
2. Find the ID of the notebook you want notes written to: right-click the notebook → **Copy external link**, and extract the ID from that link.
3. In Ulauncher Preferences → Extensions → Daily Notes, fill in the token and notebook ID.

## Usage

### Open this week's note

1. Open Ulauncher
2. Type `dn` (or your configured keyword)
3. Select **Open Daily Notes** — the note opens in Joplin

### Insert a quick note

1. Open Ulauncher
2. Type `dn <your note text>`
   - Example: `dn Worked on issue ABC-123`
3. Press Enter

The note will be added as a bullet point under today's date header.

## Configuration

Preferences in Ulauncher Preferences → Extensions → Daily Notes:

| Setting | Default | Description |
|---|---|---|
| **Joplin API Token** | _(required)_ | Token from Joplin → Tools → Options → Web Clipper |
| **Joplin Folder ID** | _(required)_ | ID of the target Joplin notebook |
| **Joplin API URL** | `http://localhost:41184` | Joplin local REST API base URL |
| **Date Format** | `%A, %d %b` | Python strftime format for date headers |

Date format examples:
- `%A, %b %-d` → "Monday, Jan 6"
- `%A, %d %b` → "Monday, 06 Jan"
- `%Y-%m-%d` → "2026-01-06"

## Note Structure

Notes are organized as weekly Joplin notes titled `{year}.{week:02d}-daily-notes`, with each day prepended as a header:

```markdown
## Monday, 06 Jan

- Your note here
- Another note


## Sunday, 05 Jan

- Previous day's notes
```

## Troubleshooting

### "Joplin not reachable"
Make sure Joplin is running and the Web Clipper server is enabled (Tools → Options → Web Clipper).

### Notes going to the wrong notebook
Double-check the **Joplin Folder ID** preference — right-click the notebook in Joplin and choose **Copy notebook ID**.
