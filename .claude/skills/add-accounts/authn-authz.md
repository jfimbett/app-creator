# Authentication and authorization on the standard stack

Companion to [SKILL.md](SKILL.md). **Authentication** (authn) answers "who is this?"; **authorization** (authz)
answers "may this person do this?". Both happen on the FastAPI backend. Next.js only shows or hides things for
convenience.

The sign-in and authorization code here is a **sketch, not run** as written (the CSRF middleware was run: same
origin and same-origin `Referer` allowed; a look-alike host, another origin and no header refused): check the current documentation of FastAPI and of the hashing
library, pin the versions in `requirements.in`, regenerate `requirements.lock`, and let the tests prove it.

## Sessions or tokens

| | Server-side session in a cookie (default) | Bearer token (JWT) in a header |
|---|---|---|
| How | sign-in creates a random session id stored in the database; the browser keeps it in an `HttpOnly` cookie | sign-in returns a signed token; the client sends `Authorization: Bearer ...` |
| Fits | a browser app calling its own backend on the same origin (this stack) | mobile apps, other services calling your API |
| Sign-out | delete the session row: it stops working at once | the token stays valid until it expires (needs a deny list) |
| Risk to manage | CSRF (the browser sends the cookie automatically) | theft from `localStorage` by injected scripts |

Choose sessions unless the product has a non-browser client. Record the choice in `<docs>/architecture.md`.

## Password hashing

- Use a maintained library with Argon2id (for example `argon2-cffi` or `pwdlib[argon2]`) or bcrypt. Never
  `hashlib.sha256(password)`, never your own salt scheme, never reversible encryption.
- Store only the hash. Verify with the library's `verify` function (constant-time). Re-hash when the library says
  the parameters are outdated.
- Minimum length 8 (or more); no maximum below 64; no composition rules that annoy users. Optionally refuse the
  most common passwords.
- The same error for "no such user" and "wrong password": `Login or password is incorrect.` Slow down repeated
  failures (for example 5 per 15 minutes per account and per IP address, stored in the database).

## Tables

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    login TEXT NOT NULL UNIQUE COLLATE NOCASE,   -- the sign-in name; normalised (trimmed, lower case)
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at TEXT NOT NULL
);
CREATE TABLE sessions (
    id_hash TEXT PRIMARY KEY,                    -- SHA-256 of the cookie value, so a database leak is not a login
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at TEXT NOT NULL                     -- UTC; for example 7 days, renewed on use
);
```

## FastAPI sketch: sign-in, the user dependency, roles

```python
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Cookie, Depends, FastAPI, HTTPException, Response

COOKIE = "session"
app = FastAPI()


def _hash_id(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


@app.post("/api/auth/sign-in")
def sign_in(body: SignIn, response: Response) -> dict:
    user = users.find_by_login(body.login.strip().lower())
    if user is None or not hasher.verify(body.password, user.password_hash):  # library call
        raise HTTPException(401, "Login or password is incorrect.")
    raw = secrets.token_urlsafe(32)
    sessions.create(_hash_id(raw), user.id, datetime.now(timezone.utc) + timedelta(days=7))
    response.set_cookie(COOKIE, raw, httponly=True, samesite="lax",
                        secure=settings.cookie_secure, max_age=7 * 24 * 3600, path="/")
    return {"id": user.id, "role": user.role}


@app.post("/api/auth/sign-out")
def sign_out(response: Response, session: str | None = Cookie(default=None)) -> dict:
    if session:
        sessions.delete(_hash_id(session))
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


def current_user(session: str | None = Cookie(default=None)) -> User:
    found = sessions.find_valid(_hash_id(session)) if session else None
    if found is None:
        raise HTTPException(401, "Please sign in.")
    return found.user


def require_role(role: str):
    def check(user: User = Depends(current_user)) -> User:
        if user.role != role:
            raise HTTPException(403, "You do not have access to this page.")
        return user
    return check


@app.get("/api/notes/{note_id}")
def read_note(note_id: int, user: User = Depends(current_user)) -> dict:
    note = notes.get_for_owner(note_id, owner_id=user.id)  # WHERE id = ? AND owner_id = ?
    if note is None:
        raise HTTPException(404, "Note not found.")  # also for other users' notes: do not reveal they exist
    return note.as_dict()


@app.get("/api/admin/stats")
def admin_stats(_: User = Depends(require_role("admin"))) -> dict:
    return {"users": users.count()}
```

`SignIn`, `User`, `users`, `sessions`, `notes`, `hasher` and `settings` stand for your Pydantic models,
data-access functions (`manage-data`), hashing library object and settings. The cookie name is the parameter
name (`session`) in `Cookie(...)`.

Authorization rules of thumb:

- Every route that touches data has `Depends(current_user)` or `Depends(require_role(...))`. A test lists the
  app's routes (`app.routes`) and fails if a data route has neither, except an explicit public list.
- Filter in the query (`WHERE owner_id = ?`), not after loading.
- Never take `owner_id` or `role` from the request body.
- 401 = not signed in; 403 = signed in but not allowed (for pages and features, not individual records); 404 for
  records the user does not own.

## CSRF (cross-site request forgery)

With a session cookie, another website could make the browser send a `POST` to your app. Defenses, all cheap:

1. `SameSite=Lax` on the cookie (above): blocks cookies on most cross-site requests.
2. Never change data on `GET`.
3. For `POST`, `PUT`, `PATCH`, `DELETE`: refuse a request whose `Origin` header (or `Referer` if `Origin` is
   missing) is not the app's own origin, taken from a setting such as `APP_ORIGIN=http://127.0.0.1:3000`:

```python
from urllib.parse import urlsplit

from fastapi import Request
from fastapi.responses import JSONResponse

UNSAFE = {"POST", "PUT", "PATCH", "DELETE"}


def _origin_of(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}" if parts.scheme and parts.netloc else ""


@app.middleware("http")
async def same_origin_only(request: Request, call_next):
    if request.method in UNSAFE:
        sent = request.headers.get("origin") or _origin_of(request.headers.get("referer", ""))
        if sent != settings.app_origin:  # exact match: "startswith" would accept app.example.evil.net
            return JSONResponse({"detail": "Request refused."}, status_code=403)
    return await call_next(request)
```

Check in the running app that the Next.js rewrite forwards the browser's `Origin` header (it normally does); the
Playwright sign-in journey proves the happy path, a pytest test with `headers={"Origin": "https://evil.example"}`
proves the refusal.

## Frontend (Next.js)

- `fetch("/api/...", { credentials: "same-origin" })` (the default for same-origin) sends the cookie; no token
  handling in JavaScript.
- A small `useCurrentUser()` hook calls `GET /api/me`; on 401 redirect to `/sign-in?next=<path>` (only allow
  relative `next` values, to avoid open redirects).
- Forms show the server's message; never "user not found".

## One test per rule (pytest, FastAPI `TestClient`)

```python
def test_user_a_cannot_read_user_b_note(client, make_user, sign_in):
    a, b = make_user("a-test"), make_user("b-test")
    note_id = create_note(client, sign_in(b), "b's secret")
    response = client.get(f"/api/notes/{note_id}", cookies=sign_in(a))
    assert response.status_code == 404
    assert "secret" not in response.text
```

Fixtures `make_user` and `sign_in` create test users in a temporary database with throw-away passwords. Cover:
visitor 401, other user's record 404 (read, change, delete), normal user 403 on admin routes, wrong password 401
with the generic message, sign-out invalidates the session, expired session 401, CSRF refusal, and the
"every data route is protected" test.

## Before calling it done

- [ ] Permissions table in `<docs>/acceptance.md` has a test name per row, all passing.
- [ ] Session secret and `APP_ORIGIN` in `.env.example` with development values only; `Secure` cookies enabled
      outside local development.
- [ ] No password, session id or token in logs (search the log output of a test run).
- [ ] `security-reviewer` run (`review-changes`).
