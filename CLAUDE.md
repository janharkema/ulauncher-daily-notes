# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **Ulauncher 5 extension** (API v2) that provides quick access to a daily markdown journal stored in Joplin. Users can open the current week's note in Joplin, insert bullet-point notes, or add checkbox TODO items, directly from the Ulauncher launcher bar. Notes are written directly to Joplin via its local REST API.

## Development Setup

This extension has no build system or test suite. To develop and test:

1. Symlink or copy the repo into Ulauncher's extensions directory:
   ```
   ln -s /home/jan/projects/ulauncher-daily-notes ~/.local/share/ulauncher/extensions/ulauncher-daily-notes
   ```
2. Restart Ulauncher (or reload extensions from preferences)
3. Logs appear via `journalctl --user -f` or in Ulauncher's own logs

There are no lint, test, or build commands — changes take effect after Ulauncher reloads the extension.

## Architecture

All logic lives in [main.py](main.py). The extension follows Ulauncher's event-listener pattern:

- **`DailyNotesExtension`** — main class, subscribes to events, holds all file/date logic
- **`KeywordQueryEventListener`** — handles the search bar input. With no query, shows "Open" / "Insert" / "Add TODO" hint items. Typing plain text shows an insert-preview item; typing `todo <text>` shows a TODO-preview item instead.
- **`ItemEnterEventListener`** — handles item selection; dispatches to open, insert, or todo logic

**Note title:** `{year}.{ISO_week:02d}-daily-notes` in the configured Joplin notebook

**Note insertion flow:** `get_or_create_note()` calls the `_find_or_create_note()` helper, then `ensure_date_header()` runs, then a bullet is inserted at line index 2 (right after the `## Date` header and blank line), prepending newer entries above older ones, then the result is PUT back to Joplin.

**TODO flow:** typing `todo <text>` after the keyword calls `add_todo()`, which uses the same `_find_or_create_note()` helper to fetch/create a fixed note titled `TODO` in the same notebook, and appends `- [ ] <text>` to the end of its body.

**Open flow:** fetches/creates the note, then opens it via the `joplin://x-callback-url/openNote?id=<id>` URL scheme.

## Key Files

- [main.py](main.py) — entire extension logic
- [manifest.json](manifest.json) — extension metadata and user preferences (keyword, joplin_token, joplin_folder_id, date_format)
- [versions.json](versions.json) — Ulauncher extension registry version history

## Preferences

Configured in `manifest.json` and read via `self.preferences[...]` in the extension:

| ID | Default | Description |
|----|---------|-------------|
| `keyword` | `dn` | Trigger keyword |
| `joplin_token` | _(required)_ | Joplin Web Clipper API token |
| `joplin_folder_id` | _(required)_ | ID of the target Joplin notebook |
| `joplin_api_url` | `http://localhost:41184` | Joplin local REST API base URL |
| `date_format` | `%A, %d %b` | Python strftime format for `## Date` headers |
| `locale_override` | `en_US.UTF-8` | Locale for day/month names (e.g. `nl_NL.UTF-8`); empty = OS locale |
