from models.addressbook import AddressBook


def get_upcoming_birthdays(book: AddressBook, days_ahead: int = 7):
    return book.get_upcoming_birthdays(days_ahead)
