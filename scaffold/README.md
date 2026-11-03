# Walking skeleton (scaffold)

The smallest app that works end to end on the standard App Creator stack. It is a starting point to grow,
not a product. `npm run create-app` (at the repository root) copies this folder to `app/` and points
`app-creator.config.json` at the copy. Do not build your app inside `scaffold/` itself: `npm run verify`
checks this folder as the template.

| Part | What | Main files |
|---|---|---|
| `frontend/` | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4 | `app/page.tsx`, `components/HealthStatus.tsx`, `lib/health.ts` |
| `backend/` | Python FastAPI | `app/main.py` (`GET /api/health`) |

The page shows the app name and a **Backend status** panel. The browser calls `/api/health` on the same site;
Next.js forwards `/api/*` to the backend (`frontend/next.config.ts`, setting `BACKEND_URL`). The panel shows
"Checking…", then **OK** or an **Error** message if the backend is not reachable. Dark mode is the default; a
light theme follows the system setting.

## Commands (run them at the repository root)

| Command | What it does |
|---|---|
| `npm ci` | once: prepares the root launcher (it has no dependencies of its own) |
| `npm run create-app` | copies this scaffold to `app/` (`-- --dir <path> --name "<App name>"`; `-- --dry-run` only shows what it would do) |
| `npm run setup` | creates `backend/.venv` and installs `requirements.lock`, runs `npm ci` in `frontend/`, installs the test browser into `.cache/ms-playwright` |
| `npm run dev` | starts the backend on http://127.0.0.1:8000 and the site on http://127.0.0.1:3000 (Ctrl+C stops both) |
| `npm run verify` | backend lint (ruff) and tests (pytest); frontend lint, typecheck, unit tests (Vitest), production build; then a Playwright browser test with screenshots in `frontend/test-results/` |

## Tests

- `backend/tests/test_health.py`: the health endpoint (pytest, FastAPI `TestClient`).
- `frontend/lib/health.test.ts` and `frontend/components/HealthStatus.test.tsx`: the status logic and panel (Vitest).
- `frontend/e2e/smoke.spec.ts`: the page in a real browser at 1366×900 and 390×844 (Playwright).

## Versions

Exact versions are pinned: `frontend/package.json` plus `package-lock.json` (`.npmrc` keeps new installs exact)
and `backend/requirements.lock` (generated from `backend/requirements.in`; its header says how). Supported:
Node 22.13 or newer, Python 3.10–3.13.

Known, accepted issue: `npm ci` in `frontend/` prints an `ERESOLVE overriding peer dependency` warning, because
`eslint-plugin-import` (pulled in by `eslint-config-next`) does not yet declare support for ESLint 10. It is a
warning, not an error: lint passes in `npm run verify`. Remove this note once an upgrade of `eslint-config-next`
makes the warning disappear.
