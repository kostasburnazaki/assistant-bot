from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .note import Note


DEFAULT_NOTES_DIR = Path.home() / ".assistant_bot"
DEFAULT_NOTES_FILE = DEFAULT_NOTES_DIR / "notes.json"


def _utc_now_iso() -> str:
    """Return current UTC time in ISO format for stable persistence."""
    return datetime.now(timezone.utc).isoformat()


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
