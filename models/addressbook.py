from collections import UserDict
from typing import Optional, Dict
from .record import Record


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        return self.data.get(name.strip().capitalize())

    def delete(self, name: str) -> bool:
        name = name.strip().capitalize()
        if name in self.data:
            del self.data[name]
            return True
        return False

    def get_upcoming_birthdays(self, days_ahead: int = 7) -> Dict[str, int]:
        today = datetime.now().date()
        upcoming = {}
        for record in self.data.values():
            days = record.days_to_birthday()
            if days is not None and 0 <= days <= days_ahead:
                upcoming[record.name.value] = days
        return dict(sorted(upcoming.items(), key=lambda x: x[1]))
