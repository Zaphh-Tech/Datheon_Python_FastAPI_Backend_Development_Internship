# Datheon — Python + FastAPI Backend

A FastAPI backend with a books API, JWT authentication, a notes service backed by
SQLAlchemy, and background job dispatch with rate limiting. Interactive API docs
are served at `/docs`.

## Features

- **Books** — CRUD endpoints with Pydantic validation, query filtering and pagination (in-memory).
- **Auth** — register/login with JWT (OAuth2 password flow), bcrypt-hashed passwords, routes protected via `Depends(get_current_user)`.
- **Notes** — SQLAlchemy 2.0 async ORM on SQLite, with a `User → Notes` relationship. Each user only sees their own notes, and data persists across restarts.
- **Notify** — webhook and email dispatch handled in the background with `BackgroundTasks`, behind a per-client rate limiter.

## Running locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs.

## Docker

```bash
docker build -t datheon-api .
docker run --rm -p 8000:8000 -e SECRET_KEY=change-me datheon-api
```

## Auth usage

1. `POST /auth/register` with a username, email and password.
2. `POST /auth/login` to get an access token.
3. Send `Authorization: Bearer <token>` on protected routes (`/auth/me`, all `/notes`).

## Tests

```bash
pytest -q
```

## Configuration

Environment variables (all optional, with defaults for local dev):

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | `dev-only-change-me` | JWT signing key |
| `DATABASE_URL` | `sqlite+aiosqlite:///./datheon.db` | async database URL |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | token lifetime |
| `RATE_LIMIT_TIMES` / `RATE_LIMIT_WINDOW_SECONDS` | `5` / `60` | rate limit |

## Layout

```
app/
  main.py
  core/        config, security (bcrypt + jwt), rate limiter
  schemas/     pydantic models
  routers/     books, auth, notes, notify
  db/          async engine, models, in-memory book store
tests/
Dockerfile
```
