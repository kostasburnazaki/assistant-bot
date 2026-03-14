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

    def cmd_hello(args):
        if args:
            console.print("[bold red]Команда 'hello' не приймає аргументів[/bold red]")
        else:
            print(show_help())

    def cmd_help(args):
        if args:
            console.print("[bold red]Команда 'help' не приймає аргументів[/bold red]")
        else:
            print(show_help())

    def cmd_add(args):
        print(add_contact(args, book))

    def cmd_change(args):
        print(change_contact(args, book))

    def cmd_phone(args):
        print(show_phone(args, book))

    def cmd_remove_phone(args):
        print(delete_phone(args, book))

    def cmd_remove_contact(args):
        print(remove_contact(args, book))

    def cmd_all(args):
        print(show_all(book))

    def cmd_add_birthday(args):
        print(add_birthday(args, book))

    def cmd_show_birthday(args):
        print(show_birthday(args, book))

    def cmd_birthdays(args):
        print(birthdays(args, book))

    def cmd_search(args):
        print(search(args, book))

    def cmd_email(args):
        print(add_email(args, book))

    def cmd_edit_email(args):
        print(edit_email(args, book))

    def cmd_address(args):
        print(add_address(args, book))

    def cmd_note_add(args):
        print(note_add(tuple(args), notes_book))

    def cmd_note_edit(args):
        print(note_edit(tuple(args), notes_book))

    def cmd_note_delete(args):
        print(note_delete(tuple(args), notes_book))

    def cmd_note_search(args):
        print(note_search(tuple(args), notes_book))

    def cmd_note_tag(args):
        print(note_tag(tuple(args), notes_book))

    def cmd_note_list(args):
        print(note_list(tuple(args), notes_book))

    def cmd_exit(args):
        save_data(book)
        print("Вихід з програми.")
        exit()

    dispatch = {
        "hello": cmd_hello,
        "help": cmd_help,
        "add": cmd_add,
        "change": cmd_change,
        "phone": cmd_phone,
        "remove-phone": cmd_remove_phone,
        "remove-contact": cmd_remove_contact,
        "all": cmd_all,
        "add-birthday": cmd_add_birthday,
        "show-birthday": cmd_show_birthday,
        "birthdays": cmd_birthdays,
        "search": cmd_search,
        "email": cmd_email,
        "edit-email": cmd_edit_email,
        "address": cmd_address,
        "note-add": cmd_note_add,
        "note-edit": cmd_note_edit,
        "note-delete": cmd_note_delete,
        "note-search": cmd_note_search,
        "note-tag": cmd_note_tag,
        "note-list": cmd_note_list,
        "exit": cmd_exit,
        "close": cmd_exit,
    }

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

        func = dispatch.get(command)
        if func:
            func(args)
        else:
            suggestion = suggest_command(command, AVAILABLE_COMMANDS)
            if suggestion:
                console.print(f"[yellow]Unknown command '{command}'. Did you mean[/yellow] [bold]{suggestion}[/bold]?")
            else:
                console.print("[bold red]Invalid command.[/bold red]")
