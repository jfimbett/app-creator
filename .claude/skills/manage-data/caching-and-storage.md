# Caching and storage: practical patterns

Companion to [SKILL.md](SKILL.md). The SQLite code below was run with Python 3.10 and pytest 9.1 (4 tests passed,
`ruff check` clean with the scaffold's settings). The HTTP disk cache is part of the client in
[http-client-patterns.md](../integrate-api/http-client-patterns.md).

## Do you need a database?

| Situation | Use | Why |
|---|---|---|
| Fixed reference data (a list of countries, a sample dataset) | a file in `<backend>/data/`, loaded once at start-up | nothing changes at run time |
| External data that is slow, limited or costs per call | a disk cache with expiry (below) | the provider stays the source of truth |
| Results that take seconds to compute from data you have | an in-memory cache (`functools.lru_cache`) or the disk cache | recomputing is fine after a restart |
| Anything a user creates or changes (saved items, settings, accounts) | SQLite | must survive restarts, needs unique rules and queries |
| Several app servers, many concurrent writers, deployed for real users | PostgreSQL (or the host's managed database) | SQLite allows one writer at a time; ask before paying |

If the answer is "file" or "cache", say so in the decision log and do not add a database "for later".

## Disk cache layout

```text
<backend>/.cache/                  # git-ignored; safe to delete at any time
  http/<provider>/<sha256>.json    # one entry per request: {"data", "source", "retrieved_at", "stored_at"}
  computed/<name>-<version>.json   # derived results; bump <version> when the computation changes
```

Rules:

- **Expiry per kind of data**, written next to the client: for example statistics 24 h, a list of products 1 h,
  historical documents that never change: no expiry. Expired entries are fetched again; a damaged file counts as
  a miss.
- **Atomic writes:** write `name.json.tmp`, then `os.replace` it to `name.json`, so a crash never leaves half a file.
- **Keys** include everything that changes the answer (path, parameters, version, user if per user), hashed so
  file names are safe. Never a secret in a key or an entry.
- **Provenance:** entries keep `source` and `retrieved_at`; the app reports `mode: "cached"` and the age.
- **Size:** if the folder can grow without bound, delete entries older than N days at start-up.
- **Tests** point the cache at `tmp_path`; one test for hit, one for expiry (set `ttl_seconds=0` or change
  `stored_at`), one for a damaged file.
- **Stale on error (optional):** when the provider is down, serving an expired entry with a visible "data from
  <date>, the source is not answering" label is often better than an error. Decide it per feature in
  `<docs>/acceptance.md`.

## SQLite with numbered migrations

Setting: `DATABASE_PATH` (in `.env.example`, for example `data/app.db`, git-ignored). Tests never use it.

`<backend>/migrations/0001_favourites.sql`:

```sql
CREATE TABLE favourites (
    id       INTEGER PRIMARY KEY,
    item_id  TEXT NOT NULL UNIQUE,
    added_at TEXT NOT NULL          -- UTC, ISO 8601
);
```

`<backend>/app/db.py`:

```python
"""SQLite access: connection, numbered SQL migrations, and data-access functions."""

import sqlite3
from pathlib import Path

MIGRATIONS = Path(__file__).resolve().parent.parent / "migrations"


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # rows behave like dicts: row["item_id"]
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migrate(conn: sqlite3.Connection) -> list[str]:
    """Apply migrations/NNNN_name.sql files not applied yet, in order. Returns the names applied."""
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY, applied_at TEXT)")
    done = {row[0] for row in conn.execute("SELECT name FROM schema_migrations")}
    applied = []
    for file in sorted(MIGRATIONS.glob("[0-9][0-9][0-9][0-9]_*.sql")):
        if file.name in done:
            continue
        # One transaction per file: the schema change and its record, or neither.
        try:
            conn.executescript("BEGIN;\n" + file.read_text(encoding="utf-8"))
            conn.execute("INSERT INTO schema_migrations VALUES (?, datetime('now'))", (file.name,))
            conn.commit()
        except sqlite3.Error:
            conn.rollback()
            raise
        applied.append(file.name)
    return applied


def add_favourite(conn: sqlite3.Connection, item_id: str) -> None:
    with conn:
        conn.execute(
            "INSERT INTO favourites (item_id, added_at) VALUES (?, datetime('now'))"
            " ON CONFLICT(item_id) DO NOTHING",
            (item_id,),
        )


def list_favourites(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT item_id FROM favourites ORDER BY added_at, id")
    return [row["item_id"] for row in rows]
```

`<backend>/tests/test_db.py`:

```python
from app import db


def test_migrations_apply_on_an_empty_database_and_only_once(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    assert db.migrate(conn) == ["0001_favourites.sql"]
    assert db.migrate(conn) == []  # second run: nothing to do


def test_saving_the_same_item_twice_keeps_one_row(tmp_path):
    conn = db.connect(tmp_path / "test.db")
    db.migrate(conn)
    db.add_favourite(conn, "item-1")
    db.add_favourite(conn, "item-1")
    assert db.list_favourites(conn) == ["item-1"]


def test_data_survives_reconnecting(tmp_path):
    path = tmp_path / "test.db"
    conn = db.connect(path)
    db.migrate(conn)
    db.add_favourite(conn, "item-2")
    conn.close()
    assert db.list_favourites(db.connect(path)) == ["item-2"]


def test_a_broken_migration_changes_nothing(tmp_path, monkeypatch):
    folder = tmp_path / "migrations"
    folder.mkdir()
    (folder / "0001_ok.sql").write_text("CREATE TABLE a (x INTEGER);")
    (folder / "0002_broken.sql").write_text("CREATE TABLE b (y INTEGER);\nNOT VALID SQL;")
    monkeypatch.setattr(db, "MIGRATIONS", folder)
    conn = db.connect(tmp_path / "test.db")
    try:
        db.migrate(conn)
    except Exception:
        pass
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "a" in tables and "b" not in tables
    assert [r[0] for r in conn.execute("SELECT name FROM schema_migrations")] == ["0001_ok.sql"]
```

Use it from FastAPI: open the connection and run `migrate` in the app's lifespan (or one connection per request
through a dependency); routes call `db.add_favourite(...)`, never SQL directly. With `sqlite3`, pass
`check_same_thread=False` to `connect` if a connection is shared across FastAPI's worker threads, or open one per
request.

Migration rules:

- Never edit a migration that has been applied anywhere (committed). Add `0002_...sql` instead.
- To rename or drop a column on older SQLite, create the new table, copy the rows, drop the old table, rename:
  all in one migration file, after a backup (`cp data/app.db data/app.db.bak`).
- Describe what a migration does to existing rows in the change report.
- With SQLAlchemy, use Alembic instead (`alembic revision --autogenerate -m "..."`, then **read** the generated
  file before `alembic upgrade head`; autogenerate misses renames).

Data-type rules: money as integer minor units (`amount_cents INTEGER`) plus a `currency TEXT`; timestamps as UTC
ISO 8601 text; unknown values as `NULL` (a test checks that `NULL` comes back as `None`, not 0); booleans as
`INTEGER` 0/1 with a `CHECK (x IN (0, 1))`.

## Background jobs, kept simple

Start with the smallest thing that works, and move up only when it does not:

1. **Do it in the request** if it takes under about 2 seconds.
2. **FastAPI `BackgroundTasks`** for fire-and-forget work after the response (sending one email, warming a cache).
   It runs in the same process: lost if the server stops, so not for anything that must happen.
3. **A job table plus a worker loop** for work that must finish or takes minutes:

   ```sql
   CREATE TABLE jobs (
       id INTEGER PRIMARY KEY,
       kind TEXT NOT NULL,
       payload TEXT NOT NULL,                -- JSON
       status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','running','done','failed')),
       attempts INTEGER NOT NULL DEFAULT 0,
       last_error TEXT,                      -- short message, never secrets
       created_at TEXT NOT NULL,
       updated_at TEXT NOT NULL
   );
   ```

   The route inserts a `queued` row and returns its id (HTTP 202). A worker (a lifespan task or a separate
   `python -m app.worker` started by the person) takes one queued job, marks it `running`, does it, marks `done`
   or `failed` with `attempts + 1`, and gives up after 3 attempts. The page polls `GET /api/jobs/{id}` and shows
   the status, including failures.
4. **A scheduled refresh** (nightly data update): a script the person runs, or the host's scheduler. Document the
   command in the README.

Jobs must be **safe to run twice** (idempotent): check whether the work is already done before doing it. Do not
add Celery, Redis or a hosted queue without the owner's agreement; record the reason if you do.

## Checks before committing

- `git status` shows no `*.db`, `.cache/`, `uploads/` (the repository `.gitignore` covers them; check the app's
  folders too).
- Tests use `tmp_path`; nothing in `<backend>/data/` changed because of a test run.
