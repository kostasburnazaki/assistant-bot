from __future__ import annotations

import json
import shlex
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Tuple


DEFAULT_NOTES_DIR = Path.home() / ".assistant_bot"
DEFAULT_NOTES_FILE = DEFAULT_NOTES_DIR / "notes.json"


def _utc_now_iso() -> str:
    """Return current UTC time in ISO format for stable persistence."""
    return datetime.now(timezone.utc).isoformat()


def parse_tags(raw_tags: str) -> List[str]:
    """Normalize comma-separated tags to lowercase unique values."""
    tags: List[str] = []
    seen = set()

    for part in raw_tags.split(","):
        tag = part.strip().lstrip("#").lower()
        if not tag or tag in seen:
            continue
        tags.append(tag)
        seen.add(tag)

    return tags


@dataclass
class Note:
    """Entity that stores note data."""

    note_id: int
    text: str
    tags: List[str]
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "note_id": self.note_id,
            "text": self.text,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "Note":
        raw_note_id = data["note_id"]
        if not isinstance(raw_note_id, (int, str)):
            raise TypeError("Invalid note ID format.")

        raw_tags = data.get("tags", [])
        if not isinstance(raw_tags, list):
            raise TypeError("Invalid note tags format.")

        return cls(
            note_id=int(raw_note_id),
            text=str(data["text"]),
            tags=[str(tag) for tag in raw_tags],
            created_at=str(data["created_at"]),
            updated_at=str(data["updated_at"]),
        )


class NotesBook:
    """Storage and business logic layer for text notes."""

    def __init__(self, storage_file: Path = DEFAULT_NOTES_FILE):
        self.storage_file = storage_file
        self.notes: Dict[int, Note] = {}
        self._next_id = 1
        self.load()

    def load(self) -> None:
        """Load notes from disk. Invalid file falls back to empty store."""
        if not self.storage_file.exists():
            return

        try:
            payload = json.loads(self.storage_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return

        loaded_notes: Dict[int, Note] = {}
        highest_id = 0

        for raw_note in payload.get("notes", []):
            try:
                note = Note.from_dict(raw_note)
            except (KeyError, TypeError, ValueError):
                continue

            loaded_notes[note.note_id] = note
            highest_id = max(highest_id, note.note_id)

        self.notes = loaded_notes
        self._next_id = highest_id + 1

    def save(self) -> None:
        """Persist notes to disk in user home directory."""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {"notes": [note.to_dict() for note in self.notes.values()]}
        self.storage_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_note(self, text: str, tags: Optional[List[str]] = None) -> Note:
        """Create and save a new note."""
        clean_text = self._validate_note_text(text)
        clean_tags = self._validate_tags(tags or [])
        timestamp = _utc_now_iso()

        note = Note(
            note_id=self._next_id,
            text=clean_text,
            tags=clean_tags,
            created_at=timestamp,
            updated_at=timestamp,
        )
        self.notes[note.note_id] = note
        self._next_id += 1
        self.save()
        return note

    def edit_note(
        self,
        note_id: int,
        new_text: Optional[str] = None,
        new_tags: Optional[List[str]] = None,
    ) -> Note:
        """Update note text and/or tags, then persist changes."""
        note = self._get_existing_note(note_id)

        if new_text is None and new_tags is None:
            raise ValueError("Provide at least one value to update.")

        if new_text is not None:
            note.text = self._validate_note_text(new_text)

        if new_tags is not None:
            note.tags = self._validate_tags(new_tags)

        note.updated_at = _utc_now_iso()
        self.save()
        return note

    def delete_note(self, note_id: int) -> None:
        """Delete note by ID."""
        self._get_existing_note(note_id)
        del self.notes[note_id]
        self.save()

    def search_notes(self, query: str) -> List[Note]:
        """Case-insensitive search by note text."""
        clean_query = query.strip().lower()
        if not clean_query:
            raise ValueError("Search query cannot be empty.")

        return [
            note
            for note in self.notes.values()
            if clean_query in note.text.lower()
        ]

    def search_by_tag(self, tag: str) -> List[Note]:
        """Case-insensitive search by a single tag value."""
        clean_tag = tag.strip().lstrip("#").lower()
        if not clean_tag:
            raise ValueError("Tag cannot be empty.")

        return [
            note
            for note in self.notes.values()
            if clean_tag in (stored_tag.lower() for stored_tag in note.tags)
        ]

    def list_notes(self) -> List[Note]:
        """Return all notes sorted by note ID."""
        return sorted(self.notes.values(), key=lambda note: note.note_id)

    @staticmethod
    def _validate_note_text(text: str) -> str:
        clean_text = text.strip()
        if not clean_text:
            raise ValueError("Note text cannot be empty.")
        if len(clean_text) > 2000:
            raise ValueError("Note text is too long (max 2000 characters).")
        return clean_text

    @staticmethod
    def _validate_tags(tags: List[str]) -> List[str]:
        normalized: List[str] = []
        seen = set()

        for raw_tag in tags:
            clean_tag = str(raw_tag).strip().lstrip("#").lower()
            if not clean_tag:
                continue
            if " " in clean_tag:
                raise ValueError("Tags cannot contain spaces.")
            if len(clean_tag) > 30:
                raise ValueError("Tag is too long (max 30 characters).")
            if clean_tag in seen:
                continue
            seen.add(clean_tag)
            normalized.append(clean_tag)

        return normalized

    def _get_existing_note(self, note_id: int) -> Note:
        note = self.notes.get(note_id)
        if note is None:
            raise KeyError("Note not found.")
        return note


def _parse_note_id(raw_value: str) -> int:
    """Validate note ID from CLI input."""
    try:
        note_id = int(raw_value)
    except ValueError as error:
        raise ValueError("Note ID must be an integer.") from error

    if note_id <= 0:
        raise ValueError("Note ID must be positive.")
    return note_id


def format_note(note: Note) -> str:
    tags_value = ", ".join(f"#{tag}" for tag in note.tags) if note.tags else "-"
    return (
        f"[{note.note_id}] {note.text}\n"
        f"  Tags: {tags_value}\n"
        f"  Created: {note.created_at}\n"
        f"  Updated: {note.updated_at}"
    )


def format_notes(notes: List[Note]) -> str:
    if not notes:
        return "No notes found."
    return "\n\n".join(format_note(note) for note in notes)


def parse_note_command(user_input: str) -> Tuple[str, List[str]]:
    """Parse command with support for quoted text values and clear validation."""
    try:
        parts = shlex.split(user_input.strip())
    except ValueError as error:
        raise ValueError("Invalid command format. Check quotes in your input.") from error

    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


def handle_note_command(command: str, args: List[str], notes_book: NotesBook) -> str:
    """
    Command router for note features.

    Expected commands:
    - note-add "text" [tag1,tag2]
    - note-edit <id> ["new text"] [tag1,tag2]
    - note-delete <id>
    - note-search "query"
    - note-tag <tag>
    - note-list
    - note-help
    """
    try:
        if command == "note-add":
            if not args:
                return "Usage: note-add \"text\" [tag1,tag2]"
            text = args[0]
            tags = parse_tags(args[1]) if len(args) > 1 else []
            note = notes_book.add_note(text, tags)
            return f"Note created with ID {note.note_id}."

        if command == "note-edit":
            if len(args) < 2:
                return "Usage: note-edit <id> \"new text\" [tag1,tag2]"
            note_id = _parse_note_id(args[0])
            new_text = args[1]
            new_tags = parse_tags(args[2]) if len(args) > 2 else None
            note = notes_book.edit_note(note_id, new_text=new_text, new_tags=new_tags)
            return f"Note {note.note_id} updated."

        if command == "note-delete":
            if len(args) != 1:
                return "Usage: note-delete <id>"
            note_id = _parse_note_id(args[0])
            notes_book.delete_note(note_id)
            return f"Note {note_id} deleted."

        if command == "note-search":
            if len(args) != 1:
                return "Usage: note-search \"query\""
            results = notes_book.search_notes(args[0])
            return format_notes(results)

        if command == "note-tag":
            if len(args) != 1:
                return "Usage: note-tag <tag>"
            results = notes_book.search_by_tag(args[0])
            return format_notes(results)

        if command == "note-list":
            return format_notes(notes_book.list_notes())

        if command == "note-help":
            return (
                "Available note commands:\n"
                "  note-add \"text\" [tag1,tag2]\n"
                "  note-edit <id> \"new text\" [tag1,tag2]\n"
                "  note-delete <id>\n"
                "  note-search \"query\"\n"
                "  note-tag <tag>\n"
                "  note-list\n"
                "  note-help"
            )

        return "Unknown note command. Type: note-help"

    except (ValueError, KeyError) as error:
        return str(error)


def run_notes_cli() -> None:
    """Standalone CLI for quick manual testing of notes feature."""
    notes_book = NotesBook()
    print("Notes CLI is running. Type 'note-help' for commands, 'exit' to stop.")

    while True:
        try:
            raw_input_value = input("notes> ").strip()
            if raw_input_value.lower() in {"exit", "close"}:
                print("Good bye!")
                break

            command, args = parse_note_command(raw_input_value)
            if not command:
                print("Please enter a command.")
                continue

            print(handle_note_command(command, args, notes_book))
        except ValueError as error:
            print(str(error))


if __name__ == "__main__":
    run_notes_cli()


