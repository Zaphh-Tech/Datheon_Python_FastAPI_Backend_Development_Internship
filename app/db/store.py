from itertools import count
from threading import Lock

_books: dict[int, dict] = {}
_book_id = count(1)
_book_lock = Lock()


def seed_books() -> None:
    if _books:
        return
    samples = [
        {"title": "The Pragmatic Programmer", "author": "Andrew Hunt", "year": 1999, "genre": "Software"},
        {"title": "Clean Code", "author": "Robert C. Martin", "year": 2008, "genre": "Software"},
        {"title": "Dune", "author": "Frank Herbert", "year": 1965, "genre": "Sci-Fi"},
    ]
    for s in samples:
        bid = next(_book_id)
        _books[bid] = {"id": bid, **s}
