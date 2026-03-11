import re
from datetime import datetime


class Field:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value: str):
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value.strip().capitalize())


class Phone(Field):
    def __init__(self, value: str):
        value = value.strip()
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError("Phone must be exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value: str):
        try:
            date_obj = datetime.strptime(value.strip(), "%d.%m.%Y")
            # Перевірка 29 лютого
            if date_obj.day == 29 and date_obj.month == 2:
                year = date_obj.year
                if not (year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)):
                    raise ValueError("Year is not leap, 29.02 invalid date.")
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError("Invalid date format. Use DD.MM.YYYY")
            else:
                raise
        super().__init__(date_obj)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Email(Field):
    """Validate email format."""

    def __init__(self, value: str):
        value = value.strip()

        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(pattern, value):
            raise ValueError("Invalid email format.")

        super().__init__(value)


class Address(Field):
    """Simple text address."""

    def __init__(self, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Address cannot be empty.")

        super().__init__(value)
