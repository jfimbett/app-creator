---
name: plan-architecture
description: Use when writing or changing architecture.md, before a slice adds an API endpoint, stored data, an external service, a setting or secret, caching or a background job, or when code mixes UI, logic and data access, or errors and validation are inconsistent.
---

# Plan the architecture

Decide where each kind of code lives, how the frontend and backend talk, what is stored, how errors and settings
work, and write it down in `<docs>/architecture.md` so every slice follows the same rules. Keep it as small as
the product allows: no database, cache or job queue until a feature needs one.

**Paths.** `<docs>`, `<frontend>`, `<backend>` come from `app-creator.config.json` (`app.docsDir`,
`app.frontendDir`, `app.backendDir`). Stack and root commands: [docs/TOOLKIT.md](../../../docs/TOOLKIT.md) §2–3.

## Inputs

- `<docs>/product.md` (journey, features, data, capabilities) and `<docs>/acceptance.md` (criteria, calculations).
- The current `<docs>/architecture.md` (draft from [the template](../product-interview/templates/architecture.md))
  and its decision log; in delegated mode also the decisions file.
- The code that exists: `<backend>/app/`, `<frontend>/app/`, `<frontend>/lib/`, `<frontend>/next.config.ts`.
- Guides: [api-and-contracts.md](api-and-contracts.md), [errors-and-validation.md](errors-and-validation.md),
  [caching-and-jobs.md](caching-and-jobs.md).

## Actions

1. **Draw the boundaries.** Fill "Parts of the application" with four layers and what each must not do:

   | Layer | Where (standard stack) | Does | Never |
   |---|---|---|---|
   | UI | `<frontend>/app/`, `components/` | screens, inputs, states; formats values it receives | calculations, third-party calls, secrets |
   | API | `<backend>/app/main.py` or `app/api/<resource>.py` | parse, validate (pydantic), call logic, map errors | business rules, SQL |
   | Logic | `<backend>/app/logic/` | pure functions: calculations, rules, display-ready values | I/O (files, network, database, clock) |
   | Data access / external services | `<backend>/app/data/`, `app/clients/` | files, SQLite, external APIs, cache | business rules |

   Rule of thumb: logic functions take plain values and return plain values, so pytest can test them with no
   server, file or network. The browser talks only to `/api/*` on its own site (Next.js rewrites it to FastAPI).

2. **Design the API** with [api-and-contracts.md](api-and-contracts.md): list each endpoint in the API table
   (method, path, request, response model, errors). Plural nouns for resources, typed pydantic response models
   mirrored by TypeScript types, pagination for lists that can grow, one error envelope, `/api/` prefix without
   a version number until there is a second client.

3. **Decide storage** (record the reason in the decision log):

   | The app... | Choose |
   |---|---|
   | only shows data computed from inputs or fetched live | **nothing stored** |
   | reads fixed or recorded data (demo fixtures, a downloaded sample) | **files** in `<backend>/data/` (JSON/CSV), read-only, with source and date recorded next to them |
   | caches slow external responses | **a disk cache** (files keyed by request) — see [caching-and-jobs.md](caching-and-jobs.md) |
   | saves what users enter, needs queries, updates or uniqueness | **SQLite** (one file, in the standard library) |
   | has many simultaneous writers or runs on several servers | a database server: a later decision, not the MVP |

   Schema, migrations, backups and test data: hand over to [manage-data](../manage-data/SKILL.md).

4. **Plan validation and errors** with [errors-and-validation.md](errors-and-validation.md): the server validates
   every input (pydantic models and `Query`/`Path` constraints); the client validates only to help the user
   type; every expected failure has a code and a plain message; unexpected ones are logged with detail and
   shown to the user as a generic message with a reference id, never a stack trace.

5. **Caching and background work** only when a criterion needs it (a slow or rate-limited source, a refresh on
   a schedule). Choose the simplest option in [caching-and-jobs.md](caching-and-jobs.md) and write down how the
   user sees how old the data is.

6. **Settings and secrets layout.**
   - Every setting name goes in the root `.env.example` with a placeholder or safe development value and a
     comment; real values only in `.env`, which the owner creates and the assistant never reads or prints.
   - Only the backend reads secrets (`os.environ` or a pydantic `BaseSettings` class in `<backend>/app/settings.py`).
     Nothing secret goes in `NEXT_PUBLIC_*` variables: those are copied into the browser bundle.
   - Defaults are safe: debug off, live external calls off in tests, demo mode needing no key.
   - Mode settings for `npm run dev` and `npm run demo` go in `devEnv` / `demoEnv` in `app-creator.config.json`
     (non-secret values only).
   - Missing optional key → the feature shows "not configured" and the rest of the app works.

7. **Write the decision log.** One row per decision: date, decision, reason, and basis (owner, or under
   delegation the brief section or `assumption D<n>`). Record rejected alternatives in one line. In delegated
   mode, routine technical choices are delegated; scope, money, publication, personal data and secrets are not
   (TOOLKIT §4).

8. **Check the plan against the code** when code exists: each layer's folder exists or the first slice that
   creates it is named in `<docs>/plan.md`. List any disagreement and ask which is right.

## Outputs

An updated `<docs>/architecture.md` (parts and boundaries, API table, storage, external services, caching,
security, settings, root commands, decision log); new setting names in `.env.example`; slices added to
`<docs>/plan.md` for any new layer or storage.

## Verification

- Every MVP feature can be traced to a screen, an endpoint (or "frontend only") and a logic function.
- Every endpoint in the table has a response model and its error codes.
- No layer's responsibility overlaps another's ("Must not" column filled).
- Every setting the code reads is listed in `.env.example`; tests run without `.env`
  (`npm run verify` exits 0 on a clean clone).
- Storage and caching choices each have a reason tied to a criterion.

## Stop when

- The architecture is agreed (interactive) or recorded under delegation, and the next slice can start.
- **Stop and ask** if a need requires a paid service, a hosted database, personal data, accounts or a secret
  not yet agreed; if two criteria imply contradictory designs; or if the code contradicts the documented
  architecture and it is unclear which is right.

## Common mistakes

- Calculations in React components or in route handlers, so they are tested only through the browser.
- The browser calling a third-party API directly (CORS problems, exposed keys, no caching).
- A database "for later" when files or nothing would do.
- Different error shapes per endpoint, or returning `200` with `{"error": ...}`.
- Validating only in the form; the API accepts anything.
- A secret in `NEXT_PUBLIC_API_KEY`, in a test, or in `app-creator.config.json`.
- `/api/v1/` everywhere from day one, with no second client to justify it.

## Example

Feature F2 "weekly totals per member" in the running-club app:

- UI: `<frontend>/app/weekly/page.tsx` shows the table; `<frontend>/lib/api.ts` has `getWeeklyTotals(week)`.
- API: `GET /api/weekly-totals?week=2026-W12` → `WeeklyTotalsResponse { week, rows: [{member_id, name,
  total_km, change_km, change_note}] }`; `422 invalid_week` for a bad week string.
- Logic: `app/logic/totals.py::weekly_totals(runs, week) -> list[WeeklyRow]` (pure; CALC1 tests it).
- Data: `app/data/runs.py::list_runs(week)` reads SQLite.
- Decision log: "2026-03-02 · SQLite for runs · the coach edits runs between visits · owner".
