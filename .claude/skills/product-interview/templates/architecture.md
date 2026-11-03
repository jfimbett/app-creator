# Architecture

Status: draft | agreed on <YYYY-MM-DD>

## Path and stack

- **Path:** A dashboard | B customer-facing web app | C automation script
- **Stack:** <language, framework, storage, tests>
- **Why:** <two or three plain-language reasons tied to product.md>
- **Alternative considered:** <option, and why not now>

## Parts of the application

| Part | Folder / file | Responsibility | Must not |
|---|---|---|---|
| Interface | `app/...` | screens, inputs, display; charts draw values they receive | compute, round or fill in financial numbers |
| Logic (shared, tested) | `app/...` | calculations, rules, and the display-ready values for cards, charts and tables (units, periods, gaps with reasons) | read files or call APIs directly |
| Data access | `app/...` | files, database, external APIs | contain business rules |
| Tests | `app/tests/`, or the framework's convention (e.g. Django: `tests.py` or `tests/` in each app) | checks of logic, data access and the main journey | call live services |
| Browser check | `app/checks/browser_check.py` (if installed) | critical screens in a real browser, screenshots in `app/.browser-checks/` | replace tests or a person's look |

## Data model (if anything is stored)

| Table / file | Fields | Who can read / change it |
|---|---|---|
| | | |

## External services

| Service | Used for | Setting names (values live in `app/.env`, never committed) | Free tier / cost | Terms checked |
|---|---|---|---|---|
| | | | | |

## Security and privacy

- Personal data stored: <none | which fields, why>
- Who can see what: <rules; "single user" if path A>
- Secrets: listed in `app/.env.example`, values only in `app/.env` (git-ignored)

## Run, test, preview

- Python: <version> in `app/.venv` (chosen because <framework> supports it; others found: <list>)
- Settings: tests run without `app/.env`; the student creates it with `cp .env.example .env`
- Install: `<command>`
- Run: `<command>` then open `<URL>`
- Test: `<command>`
- Browser check: `<command>` (or "not installed")

## Decision log

| Date | Decision | Reason | Agreed by |
|---|---|---|---|
| | Scope and architecture agreed | | <student> |
