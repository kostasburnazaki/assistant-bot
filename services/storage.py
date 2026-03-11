import os
import pickle
from models.addressbook import AddressBook


def save_data(book: AddressBook, filename: str = "data/addressbook.pkl") -> None:
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename: str = "data/addressbook.pkl") -> AddressBook:
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        return AddressBook()
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except (EOFError, pickle.UnpicklingError):
        return AddressBook()
