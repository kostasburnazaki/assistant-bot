from typing import Tuple, List
from models.addressbook import AddressBook
from models.record import Record
from services.storage import save_data
from services.birthdays import get_upcoming_birthdays
from cli.parser import parse_input
from rich.table import Table
from rich.console import Console


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
def delete_phone(args: List[str], book: AddressBook) -> str:

    name, phone = args

    record = book.find(name)

    record.remove_phone(phone)

    return "Телефон видалено."


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


@input_error
def remove_contact(args: List[str], book: AddressBook) -> str:

    name = args[0]

    book.delete(name)

    return f"Contact '{name}' removed."


def show_all(book: AddressBook):
    console = Console()

    if not book.data:
        console.print("[yellow]No contacts saved.[/yellow]")
        return

    table = Table(title="Contacts")

    table.add_column("Name", style="cyan")
    table.add_column("Phones", style="green")
    table.add_column("Email", style="magenta")
    table.add_column("Address", style="white")

    for record in book.data.values():

        phones = "; ".join(p.value for p in record.phones)

        email = record.email.value if record.email else "-"
        address = record.address.value if record.address else "-"

        table.add_row(
            record.name.value,
            phones,
            email,
            address
        )

    console.print(table)


@input_error
def add_birthday(args: Tuple[str, ...], book: AddressBook) -> str:
    if len(args) < 2:
        raise ValueError(
            "Запишіть імʼя і день народження у форматі DD.MM.YYYY.")
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
        return f"День народження не заданий для {name}."
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

    if not args:
        raise ValueError("Enter name or phone number to search.")

    query = args[0].strip().lower()

    results = []

    for record in book.data.values():

        if query in record.name.value.lower() or record.find_phone_part(query):
            results.append(str(record))

    if not results:
        return f"No contacts found for '{query}'."

    return "\n".join(results)


@input_error
def add_email(args: List[str], book: AddressBook) -> str:

    name, email = args

    record = book.find(name)

    record.add_email(email)

    return "Email added."


@input_error
def edit_email(args: List[str], book: AddressBook) -> str:

    name, new_email = args

    record = book.find(name)

    record.edit_email(new_email)

    return "Email updated."


@input_error
def add_address(args: List[str], book: AddressBook) -> str:

    name = args[0]
    address = " ".join(args[1:])  # щоб підтримувати багатослівні адреси

    record = book.find(name)

    record.add_address(address)

    return "Address added."


def show_help() -> str:
    return (
        "Доступні команди:\n"
        "- hello / help: Показати цю підказку\n"
        "- add [ім'я] [телефон]: Додати контакт або телефон\n"
        "- change [ім'я] [новий телефон]: Змінити телефон\n"
        "- phone [ім'я]: Показати телефони контакту\n"
        "- remove-phone [ім'я] [телефон]: Видалити телефон\n"
        "- remove-contact [ім'я]: Видалити контакт\n"
        "- all: Показати всі контакти\n"
        "- add-birthday [ім'я] [дата DD.MM.YYYY]: Додати день народження\n"
        "- show-birthday [ім'я]: Показати день народження\n"
        "- birthdays: Показати дні народження на наступному тижні\n"
        "- search [запит]: Пошук контакта за іменем чи номером телефону\n"
        "- close / exit: Вийти з програми"
    )
