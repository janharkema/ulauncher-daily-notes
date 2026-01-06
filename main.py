import os
import logging
from datetime import datetime
from pathlib import Path
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

logger = logging.getLogger(__name__)


class DailyNotesExtension(Extension):

    def __init__(self):
        super(DailyNotesExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    def get_notes_directory(self):
        notes_dir = self.preferences['notes_directory']
        return os.path.expanduser(notes_dir)

    def get_file_path(self):
        today = datetime.now()
        year = today.year
        week_number = self.get_week_number(today)
        notes_dir = self.get_notes_directory()
        filename = f"{year}.{week_number:02d}-daily-notes.md"
        return os.path.join(notes_dir, filename)

    def get_week_number(self, date):
        return date.isocalendar()[1]

    def get_date_header(self):
        today = datetime.now()
        date_format = self.preferences.get('date_format', '%A, %d %b')
        return f"## {today.strftime(date_format)}\n\n\n"

    def ensure_file_exists(self):
        file_path = self.get_file_path()
        notes_dir = self.get_notes_directory()

        # Create directory if it doesn't exist
        Path(notes_dir).mkdir(parents=True, exist_ok=True)

        # Create file with date header if it doesn't exist
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(self.get_date_header())
            return file_path

        # Check if we need to prepend today's date header
        with open(file_path, 'r') as f:
            content = f.read()

        lines = content.split('\n')
        first_line = lines[0].strip() if lines else ''
        date_header = self.get_date_header().strip()

        if first_line != date_header.split('\n')[0]:
            # Prepend date header
            with open(file_path, 'w') as f:
                f.write(date_header + '\n' + content)

        return file_path

    def insert_note(self, text):
        file_path = self.ensure_file_exists()

        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Insert note at line 2 (after the header)
        note_lines = [f"- {line}\n" for line in text.split('\n')]
        lines[2:2] = note_lines

        with open(file_path, 'w') as f:
            f.writelines(lines)

        return file_path


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        query = event.get_argument() or ''

        items = []

        if not query:
            # Show default options
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name='Open Daily Notes',
                description='Open today\'s daily notes file',
                on_enter=ExtensionCustomAction({'action': 'open'})
            ))
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name='Insert Note',
                description='Type your note to insert...',
                on_enter=HideWindowAction()
            ))
        else:
            # User is typing a note to insert
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name=f'Insert: {query}',
                description='Press Enter to add this note to your daily journal',
                on_enter=ExtensionCustomAction({'action': 'insert', 'text': query})
            ))

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):
        data = event.get_data()
        action = data.get('action')

        if action == 'open':
            file_path = extension.ensure_file_exists()
            editor = extension.preferences.get('editor', 'xdg-open')
            return RunScriptAction(f'{editor} "{file_path}"', [])

        elif action == 'insert':
            text = data.get('text', '')
            if text:
                extension.insert_note(text)
            return HideWindowAction()

        return HideWindowAction()


if __name__ == '__main__':
    DailyNotesExtension().run()
