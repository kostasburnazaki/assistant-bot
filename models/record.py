from typing import List, Optional
from .fields import Name, Phone, Birthday, Address, Email
from datetime import datetime


class Record:
    def __init__(self, name: str):
        self.name = Name(name)

        self.phones: List[Phone] = []

        self.email: Optional[Email] = None
        self.address: Optional[Address] = None
        self.birthday: Optional[Birthday] = None

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        phone = phone.strip()

        for i, p in enumerate(self.phones):

            if p.value == phone:
                self.phones.pop(i)
                return

        raise ValueError("Phone not found.")

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        old_phone = old_phone.strip()

        for i, p in enumerate(self.phones):

            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return

        raise ValueError("Old phone not found.")

    def add_birthday(self, birthday_str: str):
        self.birthday = Birthday(birthday_str)

    def days_to_birthday(self) -> Optional[int]:
        if not self.birthday:
            return None
        today = datetime.now().date()
        bday = self.birthday.value.date()
        year = today.year

        # Привітання 29.02 тільки у високосні роки
        if bday.month == 2 and bday.day == 29:
            if not (year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)):
                next_year = year + 1
                while not (next_year % 400 == 0 or (next_year % 4 == 0 and next_year % 100 != 0)):
                    next_year += 1
                next_birthday = bday.replace(year=next_year)
            else:
                next_birthday = bday.replace(year=year)
        else:
            next_birthday = bday.replace(year=year)

        if next_birthday < today:
            if bday.month == 2 and bday.day == 29:
                next_year = year + 1
                while not (next_year % 400 == 0 or (next_year % 4 == 0 and next_year % 100 != 0)):
                    next_year += 1
                next_birthday = bday.replace(year=next_year)
            else:
                next_birthday = bday.replace(year=year + 1)

        return (next_birthday - today).days

    def __str__(self):
        phones_str = "; ".join(
            p.value for p in self.phones) if self.phones else "No phones"
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"
