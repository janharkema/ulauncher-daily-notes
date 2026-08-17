import json
import locale
import logging
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import ItemEnterEvent, KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

logger = logging.getLogger(__name__)


class DailyNotesExtension(Extension):
    def __init__(self):
        super(DailyNotesExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    def get_joplin_url(self):
        return self.preferences.get("joplin_api_url", "http://localhost:41184").rstrip(
            "/"
        )

    def get_note_title(self):
        today = datetime.now()
        week_number = today.isocalendar()[1]
        return f"{today.year}.{week_number:02d}-daily-notes"

    def get_date_header(self):
        today = datetime.now()
        date_format = self.preferences.get("date_format", "%A, %d %b")
        locale_override = self.preferences.get("locale_override", "en_US.UTF-8").strip()
        if locale_override:
            saved = locale.setlocale(locale.LC_TIME)
            try:
                locale.setlocale(locale.LC_TIME, locale_override)
                return f"## {today.strftime(date_format)}"
            except locale.Error:
                logger.warning(
                    f"Locale '{locale_override}' not available, falling back to OS locale"
                )
            finally:
                locale.setlocale(locale.LC_TIME, saved)
        return f"## {today.strftime(date_format)}"

    def _joplin_request(self, method, path, data=None):
        token = self.preferences["joplin_token"]
        base_url = self.get_joplin_url()
        sep = "&" if "?" in path else "?"
        url = f"{base_url}{path}{sep}token={token}"
        body = json.dumps(data).encode() if data is not None else None
        headers = {"Content-Type": "application/json"} if body else {}
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())

    def _find_or_create_note(self, title, initial_body=""):
        """Return (note_id, body) for the note with this title in the configured folder."""
        folder_id = self.preferences["joplin_folder_id"]

        page = 1
        while True:
            result = self._joplin_request(
                "GET",
                f"/folders/{urllib.parse.quote(folder_id)}/notes?fields=id,title&limit=100&page={page}",
            )
            for note in result.get("items", []):
                if note["title"] == title:
                    note_data = self._joplin_request(
                        "GET", f"/notes/{note['id']}?fields=id,body"
                    )
                    return note_data["id"], note_data["body"]
            if not result.get("has_more", False):
                break
            page += 1

        new_note = self._joplin_request(
            "POST",
            "/notes",
            {
                "title": title,
                "body": initial_body,
                "parent_id": folder_id,
            },
        )
        return new_note["id"], initial_body

    def get_or_create_note(self):
        """Return (note_id, body) for this week's note, creating it if needed."""
        return self._find_or_create_note(self.get_note_title(), self.get_date_header() + "\n\n")

    def ensure_date_header(self, body):
        """Return body with today's date header prepended if absent."""
        date_header = self.get_date_header()
        if date_header not in body:
            return date_header + "\n\n" + body
        return body

    def insert_note(self, text):
        note_id, body = self.get_or_create_note()
        body = self.ensure_date_header(body)

        lines = body.split("\n")
        note_lines = [f"- {line}" for line in text.split("\n")]

        for i, note_line in enumerate(note_lines):
            lines.insert(2 + i, note_line)

        # Add blank line after notes if next line is a header
        if len(lines) > 2 + len(note_lines) and lines[2 + len(note_lines)].startswith(
            "##"
        ):
            lines.insert(2 + len(note_lines), "")

        self._joplin_request("PUT", f"/notes/{note_id}", {"body": "\n".join(lines)})
        return note_id

    def add_todo(self, text):
        note_id, body = self._find_or_create_note("TODO")
        new_body = body.rstrip("\n")
        new_body = f"{new_body}\n- [ ] {text}\n" if new_body else f"- [ ] {text}\n"
        self._joplin_request("PUT", f"/notes/{note_id}", {"body": new_body})
        return note_id


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or ""
        items = []

        if not query:
            items.append(
                ExtensionResultItem(
                    icon="images/icon.png",
                    name="Open Daily Notes",
                    description="Open this week's note in Joplin",
                    on_enter=ExtensionCustomAction({"action": "open"}),
                )
            )
            items.append(
                ExtensionResultItem(
                    icon="images/icon.png",
                    name="Insert Note",
                    description="Type your note to insert...",
                    on_enter=HideWindowAction(),
                )
            )
            items.append(
                ExtensionResultItem(
                    icon="images/icon.png",
                    name="Add TODO",
                    description="Type 'todo <text>' to add a checkbox item...",
                    on_enter=HideWindowAction(),
                )
            )
        elif query.split(" ", 1)[0].lower() == "todo":
            text = query.split(" ", 1)[1].strip() if " " in query else ""
            if text:
                items.append(
                    ExtensionResultItem(
                        icon="images/icon.png",
                        name=f"Add TODO: {text}",
                        description="Press Enter to add this checkbox item to your TODO note",
                        on_enter=ExtensionCustomAction({"action": "todo", "text": text}),
                    )
                )
        else:
            items.append(
                ExtensionResultItem(
                    icon="images/icon.png",
                    name=f"Insert: {query}",
                    description="Press Enter to add this note to your daily journal",
                    on_enter=ExtensionCustomAction({"action": "insert", "text": query}),
                )
            )

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        action = data.get("action")

        if action == "open":
            try:
                note_id, _ = extension.get_or_create_note()
                return OpenAction(f"joplin://x-callback-url/openNote?id={note_id}")
            except (urllib.error.URLError, KeyError) as e:
                logger.error(f"Joplin API error: {e}")
        elif action == "insert":
            text = data.get("text", "")
            if text:
                try:
                    extension.insert_note(text)
                except (urllib.error.URLError, KeyError) as e:
                    logger.error(f"Failed to insert note: {e}")
        elif action == "todo":
            text = data.get("text", "")
            if text:
                try:
                    extension.add_todo(text)
                except (urllib.error.URLError, KeyError) as e:
                    logger.error(f"Failed to add todo: {e}")

        return HideWindowAction()


if __name__ == "__main__":
    DailyNotesExtension().run()
