from typing import Tuple
from models.addressbook import AddressBook
from models.record import Record
from services.storage import save_data
from services.birthdays import get_upcoming_birthdays
from cli.parser import parse_input


def input_error(handler):
    def wrapper(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except KeyError:
            return "Enter user name."
        except ValueError as e:
            return str(e) if str(e) else "Invalid input."
        except IndexError:
            return "Enter user name."
    return wrapper


@input_error
def add_contact(args: Tuple[str, ...], book: AddressBook) -> str:
    if len(args) < 2:
        raise ValueError("Додайте імʼя та номер телефону")
    name, phone, *_ = args
    name = name.strip().capitalize()
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = f"Контакт {name} додано."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args: Tuple[str, ...], book: AddressBook) -> str:
    if len(args) < 2:
        raise ValueError("Назвіть імʼя та новий номер телефону")
    name, new_phone, *_ = args
    name = name.strip().capitalize()
    record = book.find(name)
    if record is None:
        raise KeyError
    if record.phones:
        record.edit_phone(record.phones[0].value, new_phone)
    else:
        record.add_phone(new_phone)
    return f"Телефон для {name} оновлено."


@input_error
def show_phone(args: Tuple[str, ...], book: AddressBook) -> str:
    if len(args) < 1:
        raise ValueError("Введіть імʼя")
    name = args[0].strip().capitalize()
    record = book.find(name)
    if record is None:
        raise KeyError
    if not record.phones:
        return f"У контакту {name} немає номерів."
    phones_str = "; ".join(p.value for p in record.phones)
    return f"{name}: {phones_str}"


def show_all(book: AddressBook) -> str:
    if not book.data:
        return "Книга контактів порожня."
    result = "Контакти:\n"
    for record in book.data.values():
        result += f"{record}\n"
    return result.strip()


@input_error
def add_birthday(args: Tuple[str, ...], book: AddressBook) -> str:
    if len(args) < 2:
        raise ValueError("Запишіть імʼя і день народження у форматі DD.MM.YYYY.")
    name, birthday_str, *_ = args
    name = name.strip().capitalize()
    record = book.find(name)
    if record is None:
        raise KeyError
    record.add_birthday(birthday_str)
    return f"Birthday for {name} added/updated."


@input_error
def show_birthday(args: Tuple[str, ...], book: AddressBook) -> str:
    if len(args) < 1:
        raise ValueError("Введіть імʼя.")
    name = args[0].strip().capitalize()
    record = book.find(name)
    if record is None:
        raise KeyError
    if not record.birthday:
        return f"No birthday set for {name}."
    return f"{name}'s birthday is {record.birthday}"


@input_error
def birthdays(args: Tuple[str, ...], book: AddressBook) -> str:
    upcoming = get_upcoming_birthdays(book)
    if not upcoming:
        return "No birthdays in the next 7 days."
    result_lines = ["Upcoming birthdays:"]
    for name, days in upcoming.items():
        day_text = "today" if days == 0 else f"in {days} day{'s' if days > 1 else ''}"
        result_lines.append(f"{name} - {day_text}")
    return "\n".join(result_lines)


@input_error
def search(args: Tuple[str, ...], book: AddressBook) -> str:
    if len(args) < 1:
        raise ValueError("Введіть ім'я або частину імені для пошуку.")
    query = args[0].strip().capitalize()
    results = []
    for record in book.data.values():
        if query in record.name.value:
            results.append(str(record))
    if not results:
        return f"Контакт з ім'ям, що містить '{query}', не знайдено."
    return "\n".join(results)


def show_help() -> str:
    return (
        "Доступні команди:\n"
        "- hello / help: Показати цю підказку\n"
        "- add [ім'я] [телефон]: Додати контакт або телефон\n"
        "- change [ім'я] [новий телефон]: Змінити телефон\n"
        "- phone [ім'я]: Показати телефони контакту\n"
        "- all: Показати всі контакти\n"
        "- add-birthday [ім'я] [дата DD.MM.YYYY]: Додати день народження\n"
        "- show-birthday [ім'я]: Показати день народження\n"
        "- birthdays: Показати дні народження на наступному тижні\n"
        "- close / exit: Вийти з програми"
    )
