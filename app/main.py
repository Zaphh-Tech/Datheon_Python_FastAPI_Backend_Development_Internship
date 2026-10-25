from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db import store
from app.db.database import init_db
from app.routers import auth, books, notes, notify


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    store.seed_books()
    yield


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.include_router(books.router)
app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(notify.router)


@app.get("/", tags=["Meta"])
def root():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION, "docs": "/docs"}
