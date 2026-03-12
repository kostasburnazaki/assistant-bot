# cli/bot.py
from cli.parser import parse_input, suggest_command
from cli.commands import (
    add_contact, change_contact, show_phone, show_all,
    add_birthday, show_birthday, birthdays, search, add_email, edit_email,
    add_address, show_help, delete_phone, remove_contact,
    note_add, note_edit, note_delete, note_search, note_tag, note_list,
)
from notes.notebook import NotesBook
from services.storage import load_data, save_data
from rich.console import Console


AVAILABLE_COMMANDS = [
    "hello",
    "help",
    "add",
    "change",
    "phone",
    "all",
    "add-birthday",
    "show-birthday",
    "birthdays",
    "search",
    "email",
    "edit-email",
    "address",
    "note-add",
    "note-edit",
    "note-delete",
    "note-search",
    "note-tag",
    "note-list",
    "remove-phone",
    "remove-contact",
    "exit",
    "close"
]


def main():
    book = load_data()
    notes_book = NotesBook()
    console = Console()
    console.print(
        "[bold green]Бот-помічник запущено. Введіть команду або 'exit'/'close' для виходу. help для справки[/bold green]")
    while True:
        console.print("[bold blue]Enter command:[/bold blue]", end=" ")
        user_input = input()
        if not user_input:
            console.print("[bold red]Invalid command.[/bold red]")
            continue

        try:
            command, args = parse_input(user_input)
        except ValueError as error:
            console.print(f"[bold red]{error}[/bold red]")
            continue

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

        elif command == "remove-phone":
            print(delete_phone(args, book))

        elif command == "remove-contact":
            print(remove_contact(args, book))

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

        elif command == "email":
            print(add_email(args, book))

        elif command == "edit-email":
            print(edit_email(args, book))

        elif command == "address":
            print(add_address(args, book))

        elif command == "note-add":
            print(note_add(tuple(args), notes_book))

        elif command == "note-edit":
            print(note_edit(tuple(args), notes_book))

        elif command == "note-delete":
            print(note_delete(tuple(args), notes_book))

        elif command == "note-search":
            print(note_search(tuple(args), notes_book))

        elif command == "note-tag":
            print(note_tag(tuple(args), notes_book))

        elif command == "note-list":
            print(note_list(tuple(args), notes_book))

        else:

            suggestion = suggest_command(command, AVAILABLE_COMMANDS)

            if suggestion:
                console.print(
                    f"[yellow]Unknown command '{command}'. Did you mean[/yellow] [bold]{suggestion}[/bold]?"
                )
            else:
                console.print("[bold red]Invalid command.[/bold red]")
