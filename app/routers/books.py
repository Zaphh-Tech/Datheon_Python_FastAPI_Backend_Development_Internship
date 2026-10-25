from fastapi import APIRouter, HTTPException, Query, status

from app.db import store
from app.schemas.book import Book, BookCreate, BookUpdate

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=list[Book])
def list_books(
    author: str | None = Query(None),
    genre: str | None = Query(None),
    year: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    results = list(store._books.values())
    if author:
        results = [b for b in results if author.lower() in b["author"].lower()]
    if genre:
        results = [b for b in results if b["genre"] and b["genre"].lower() == genre.lower()]
    if year is not None:
        results = [b for b in results if b["year"] == year]
    return results[skip : skip + limit]


@router.get("/{book_id}", response_model=Book)
def get_book(book_id: int):
    book = store._books.get(book_id)
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Book {book_id} not found")
    return book


@router.post("", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate):
    with store._book_lock:
        book_id = next(store._book_id)
        book = {"id": book_id, **payload.model_dump()}
        store._books[book_id] = book
    return book


@router.put("/{book_id}", response_model=Book)
def update_book(book_id: int, payload: BookUpdate):
    book = store._books.get(book_id)
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Book {book_id} not found")
    book.update(payload.model_dump(exclude_unset=True))
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    with store._book_lock:
        if book_id not in store._books:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Book {book_id} not found")
        del store._books[book_id]
    return None
