# cli/bot.py
from cli.parser import parse_input
from cli.commands import (
    add_contact, change_contact, show_phone, show_all,
    add_birthday, show_birthday, birthdays, search, show_help
)
from services.storage import load_data, save_data

VALID_COMMANDS = [
    "hello", "help", "add", "change", "phone", "all",
    "add-birthday", "show-birthday", "birthdays", "close", "exit", "search"
]


def main():
    book = load_data()
    print("Бот-помічник запущено. Введіть команду або 'exit'/'close' для виходу. help для справки")
    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            print("Invalid command.")
            continue

        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Вихід з програми.")
            break

        elif command in ("hello", "help") and not args:
            print(show_help())

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        elif command == "search":
            print(search(args, book))

        else:
            print("Invalid command.")
