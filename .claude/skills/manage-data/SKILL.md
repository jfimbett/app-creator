---
name: manage-data
description: Use when the app must save data between visits, cache slow or rate-limited data, add or change tables, fields or stored files, choose or connect a database, run a background job, or when stored data looks wrong, missing or duplicated.
---

# Persistent storage, caches and schema changes

Store only what the product needs, in a structure written down in `<docs>/architecture.md`, changed only through
recorded schema changes (migrations) that can be applied on any copy of the app.

Paths: `<backend>` and `<docs>` are `app.backendDir` and `app.docsDir` in `app-creator.config.json` (after
`npm run create-app`: `app/backend`, `app/docs`). Layouts, SQL and code: [caching-and-storage.md](caching-and-storage.md).

## Inputs

- `<docs>/product.md` (what is saved, for whom, how fresh), `<docs>/architecture.md` (storage choice, data model
  table).
- The current models, migrations and data-access code in `<backend>`.

## Actions

1. **Decide whether storage is needed at all** (guide, "Do you need a database?"). Read-only reference data can
   be files shipped with the app; slow external data usually needs only a disk cache; saved user input needs a
   database. Record the choice and the reason in the decision log of `<docs>/architecture.md`.
2. **Design the change** in the data model table of `<docs>/architecture.md`: tables or files, fields with types and
   units, required fields, unique keys, relations, who may read or change each record. Store money as integer minor
   units or decimals, never floats; store dates as ISO dates, timestamps in UTC; store the currency and the unit.
   A value that is not known is stored as `NULL`, never as 0.
3. **Choose the mechanism** for the standard stack (FastAPI backend):
   - files (JSON, CSV, Parquet) in `<backend>/data/` for read-only reference data;
   - a disk cache in a git-ignored folder (for example `<backend>/.cache/`) for external data with an expiry;
   - SQLite (Python's built-in `sqlite3`, or SQLAlchemy if the plan already uses it) for local saved data;
     PostgreSQL or similar only when a deployed multi-user app needs it, and only after the owner agrees (cost);
   - migrations: Alembic when SQLAlchemy is used; otherwise numbered SQL files in `<backend>/migrations/` applied
     in order by a small function at start-up (guide). Django or other stacks: their own migration tool.
4. **Write the change:** schema, migration, and data-access functions (create, read, update, delete as needed) in
   the data-access part (for example `<backend>/app/db.py` or `app/repositories/`). Keep SQL out of routes; use
   parameterised queries (`?` placeholders), never string formatting with user input.
5. **Existing data:** if records already exist, say what the migration does to them (new defaults, conversions).
   Back up a local database file before applying a destructive change, and ask before deleting data.
6. **Per-user data** (when accounts exist, `add-accounts`): every query that returns user data filters by the
   signed-in user or checks permission. Add a test that user A cannot read or change user B's records.
7. **Background work** only if a request would otherwise take too long: start with FastAPI `BackgroundTasks` or a
   scheduled script, keep job status in the database, make jobs safe to re-run (guide, "Background jobs").
8. **Tests** (`test-and-check`): use a temporary database file (`tmp_path`) or in-memory SQLite, never the real
   one. Test saving and reading back, required fields, unique rules, `NULL` stays `NULL`, cache expiry, and that
   migrations apply from an empty database.

## Outputs

Updated data model and decision in `<docs>/architecture.md`, schema and migration files, data-access functions,
tests, a change report that says how migrations are applied (automatically at start-up, or which command).

## Verification

- Migrations apply cleanly on an empty database (a test) and on the current local one.
- `npm run verify` passes using temporary databases and caches.
- The feature that uses the data works in the running app (`npm run dev`): save, reload the page, restart, see
  the data again.
- `git status` shows no database files, cache folders or uploads to be committed.

## Stop when

- The data survives a restart and the tests pass.
- **Stop and ask** before deleting or rewriting existing data, before storing new personal or sensitive data,
  before adding a hosted database or queue service that costs money, or when the provider's terms limit storage.

## Common mistakes

- Editing the database by hand so the migration files no longer describe it.
- Committing the local database file or the cache folder (keep `*.db`, `*.sqlite3`, `.cache/` git-ignored).
- Floats for money; amounts without currency; unknown values saved as 0.
- A database added "for later" when files or a cache would do.
- Background jobs with no status, no retry limit and no way to see that they failed.

## Example

"Users can save a list of favourite items between visits; no accounts yet." Decision: SQLite file
`<backend>/data/app.db` (git-ignored), path from setting `DATABASE_PATH`. Migration
`migrations/0001_favourites.sql` creates `favourites(id INTEGER PRIMARY KEY, item_id TEXT NOT NULL UNIQUE,
added_at TEXT NOT NULL)`. `db.py` has `add_favourite`, `list_favourites`, `remove_favourite` with `?`
placeholders. Tests use `tmp_path / "test.db"`: add, list, adding the same item twice keeps one row, migrations
apply on an empty file. Then: add a favourite in the browser, restart `npm run dev`, it is still there.
