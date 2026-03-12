from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping


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
