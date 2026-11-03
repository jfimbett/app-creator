---
name: manage-data
description: Use when the application must save data between visits, when adding or changing tables, fields or stored files, when choosing or connecting a database, or when stored data looks wrong, missing or duplicated.
---

# Persistent storage and schema changes

Store only what the product needs, in a structure written down in `docs/architecture.md`, changed only through
recorded schema changes (migrations) that can be applied on any copy of the app.

## Inputs

- `docs/product.md` (what is saved, for whom), `docs/architecture.md` (storage choice, data model table).
- The current models, migrations and data-access code in `app/`.

## Actions

1. **Design the change** in the data model table of `docs/architecture.md`: tables or files, fields with types and
   units, required fields, unique keys, relations, who may read or change each record. Store money as integer minor
   units or decimals, never floats; store dates as ISO dates; store the currency.
2. **Choose the mechanism** to match the stack:
   - files (CSV, Parquet, JSON) for read-only reference data;
   - SQLite for local saved data; PostgreSQL (or similar) when deployed for several users;
   - the framework's migration tool when it has one (Django `makemigrations` / `migrate`; Alembic with
     SQLAlchemy); otherwise numbered SQL files in `app/migrations/` applied in order by a small script.
3. **Write the change:** model or schema, migration, and data-access functions (create, read, update, delete as
   needed) in the data-access part. Keep SQL out of interface code; use parameterised queries, never string
   concatenation.
4. **Existing data:** if records already exist, say what the migration does to them (new defaults, conversions).
   Back up a local database file before applying a destructive change, and ask before deleting data.
5. **Per-user data** (when accounts exist): every query that returns user data filters by the signed-in user or
   checks permission. Add a test that user A cannot read or change user B's records.
6. **Tests** (`test-and-check`): use a temporary or in-memory database, never the real one. Test saving and reading
   back, required fields, unique rules, and that migrations apply from an empty database.

## Outputs

Updated data model in `docs/architecture.md`, models and migration files, data-access functions, tests, a change
report that says which commands apply the migration.

## Verification

- Migrations apply cleanly on an empty database and on the current local one.
- Tests pass using a temporary database.
- The feature that uses the data works in the running app: save, reload the page or restart, see the data again.

## Stop when

- The data survives a restart and the tests pass.
- **Stop and ask** before deleting or rewriting existing data, before storing new personal or sensitive data, or
  before adding a hosted database that costs money.

## Common mistakes

- Editing the database by hand so the migration files no longer describe it.
- Committing the local database file with test or personal data (keep `*.db`/`*.sqlite3` git-ignored).
- Floats for money; amounts without currency.
