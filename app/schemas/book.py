from pydantic import BaseModel, Field


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=120)
    year: int = Field(..., ge=0, le=2100)
    genre: str | None = Field(None, max_length=60)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    author: str | None = Field(None, min_length=1, max_length=120)
    year: int | None = Field(None, ge=0, le=2100)
    genre: str | None = Field(None, max_length=60)


class Book(BookBase):
    id: int
