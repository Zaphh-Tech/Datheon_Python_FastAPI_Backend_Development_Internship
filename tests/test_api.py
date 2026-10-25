import os
import tempfile

_TEST_DB = os.path.join(tempfile.gettempdir(), "datheon_test.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_TEST_DB}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.rate_limit import RateLimiter  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _auth_header(client, username):
    client.post(
        "/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "supersecret1"},
    )
    token = client.post(
        "/auth/login", data={"username": username, "password": "supersecret1"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    assert client.get("/").json()["status"] == "ok"


def test_books_crud_cycle(client):
    assert len(client.get("/books").json()) >= 3

    bid = client.post("/books", json={"title": "TDD", "author": "Kent Beck", "year": 2002}).json()["id"]
    assert client.get(f"/books/{bid}").status_code == 200
    assert client.put(f"/books/{bid}", json={"year": 2003}).json()["year"] == 2003
    assert any(b["id"] == bid for b in client.get("/books", params={"author": "beck"}).json())
    assert client.delete(f"/books/{bid}").status_code == 204
    assert client.get(f"/books/{bid}").status_code == 404


def test_books_validation(client):
    assert client.post("/books", json={"title": "x", "author": "y", "year": 9999}).status_code == 422


def test_auth_flow(client):
    assert client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "supersecret1"},
    ).status_code == 201

    assert client.get("/auth/me").status_code == 401

    token = client.post("/auth/login", data={"username": "alice", "password": "supersecret1"}).json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200 and me.json()["username"] == "alice"


def test_login_wrong_password(client):
    _auth_header(client, "bob")
    assert client.post("/auth/login", data={"username": "bob", "password": "wrongpass1"}).status_code == 401


def test_notes_crud(client):
    hdr = _auth_header(client, "carol")
    nid = client.post("/notes", json={"title": "n1", "content": "hello"}, headers=hdr).json()["id"]
    assert len(client.get("/notes", headers=hdr).json()) == 1
    assert client.put(f"/notes/{nid}", json={"content": "edited"}, headers=hdr).json()["content"] == "edited"
    assert client.delete(f"/notes/{nid}", headers=hdr).status_code == 204


def test_notes_owner_isolation(client):
    hdr_a = _auth_header(client, "dave")
    hdr_b = _auth_header(client, "erin")
    nid = client.post("/notes", json={"title": "secret"}, headers=hdr_a).json()["id"]
    assert client.get(f"/notes/{nid}", headers=hdr_b).status_code == 404
    assert all(n["id"] != nid for n in client.get("/notes", headers=hdr_b).json())


def test_notes_require_auth(client):
    assert client.get("/notes").status_code == 401


def test_webhook_accepted(client):
    r = client.post("/notify/webhook", json={"url": "http://127.0.0.1:9/hook", "message": "hi"})
    assert r.status_code == 202 and r.json()["status"] == "accepted"


def test_email_accepted(client):
    assert client.post("/notify/email", json={"to": "x@example.com", "subject": "s", "body": "b"}).status_code == 202


def test_rate_limiter():
    import types

    limiter = RateLimiter(times=2, window_seconds=60)
    req = types.SimpleNamespace(client=types.SimpleNamespace(host="9.9.9.9"))
    limiter(req)
    limiter(req)
    with pytest.raises(Exception) as exc:
        limiter(req)
    assert "429" in str(exc.value) or "Rate limit" in str(exc.value)
