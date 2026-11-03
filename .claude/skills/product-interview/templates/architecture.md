# Architecture

Status: draft | agreed on <YYYY-MM-DD>

## Stack

- **Stack:** standard (Next.js + React + TypeScript + Tailwind CSS v4 + Recharts if charts are agreed; FastAPI +
  pydantic; storage: <none | files | SQLite>; pytest, Vitest, Playwright) | <other, with the reason>
- **Why:** <two or three plain-language reasons tied to product.md>
- **Alternative considered:** <option, and why not now>
- **Folders** (from `app-creator.config.json`): frontend `<frontendDir>`, backend `<backendDir>`, docs `<docsDir>`

## Parts of the application and their boundaries

| Part | Folder / file | Responsibility | Must not |
|---|---|---|---|
| Interface (UI) | `<frontend>/app/`, `<frontend>/components/` | screens, inputs, loading/empty/error states; draws values it receives | compute, round or fill in numbers; call third-party APIs; hold secrets |
| Frontend helpers | `<frontend>/lib/` | API client for `/api/*`, typed responses, formatting of already-computed values | business rules |
| API (routes) | `<backend>/app/main.py`, `<backend>/app/api/` | HTTP: parse and validate input (pydantic), call logic, return typed responses and the error envelope | contain calculations or SQL |
| Logic (shared, tested) | `<backend>/app/logic/` | calculations, rules, display-ready values (units, periods, gaps with reasons) | read files, call APIs or know about HTTP |
| Data access | `<backend>/app/data/` | files, database, external APIs, cache | contain business rules |
| Tests | `<backend>/tests/`, `<frontend>/**/*.test.ts(x)`, `<frontend>/e2e/` | logic and data access (pytest), frontend logic (Vitest), journeys (Playwright) | call live services |

## API

| Method and path | Purpose | Request | Response (model) | Errors |
|---|---|---|---|---|
| `GET /api/health` | backend is up | – | `{status, app}` | – |
| | | | | |

Error envelope: `{"error": {"code": "...", "message": "...", "details": ...}}` (see `plan-architecture`).

## Data and storage

- Storage: <none | files in `<backend>/data/` | SQLite at `<path>`>, because <reason>
- Schema changes: <how; see `manage-data`>

| Table / file | Fields | Who can read / change it |
|---|---|---|
| | | |

## External services

| Service | Used for | Setting names (values only in `.env`, never committed) | Offline / demo behaviour | Free tier / cost | Terms checked |
|---|---|---|---|---|---|
| | | | | | |

## Caching and background work

<none | what is cached, where, for how long, and how the user sees its age>

## Security and privacy

- Personal data stored: <none | which fields, why>
- Who can see what: <rules; "single user, local" if no accounts>
- Secrets: names in the root `.env.example`, values only in `.env` (git-ignored); read only by the backend

## Run, test, preview (root commands)

- Python: <version found by `npm run setup`> in `<backend>/.venv` (override: `APP_PYTHON`)
- Install: `npm ci` (once), then `npm run setup`
- Run: `npm run dev`, then open http://127.0.0.1:3000
- Offline demo: `npm run demo` (settings: <demoEnv>)
- Check everything: `npm run verify` (lint, tests, typecheck, build, Playwright smoke at 1366 and 390 px)
- Settings: tests and the demo run without `.env`; the owner creates it with `cp .env.example .env`

## Decision log

| Date | Decision | Reason | Basis (owner / delegated: `<brief>` §n / assumption D<n>) |
|---|---|---|---|
| | Scope and architecture agreed | | |
