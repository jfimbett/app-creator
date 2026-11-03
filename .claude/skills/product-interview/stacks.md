# The stack and how the root commands set it up

A stack is the set of tools an app is built with: a language, an interface framework, a way to store data and a
way to test. App Creator supports **one standard stack** with ready-made root commands. Recommend it unless the
product clearly needs something else, and explain the choice in plain language.

Before adding a library or service, check its current official documentation (versions, free tiers and terms
change). Never sign the owner up for anything, and never choose a paid service without their explicit agreement.

## The standard stack

| Part | Tool | Why |
|---|---|---|
| Interface | Next.js (App Router) + React + TypeScript | pages, components and type checks; one project for all screens |
| Styling | Tailwind CSS v4, theme colours in CSS variables; shadcn/ui-style components where they help | consistent design without a heavy UI library (`design-interface`) |
| Charts (only if agreed) | Recharts | React-native charts that draw prepared values |
| Backend | Python FastAPI, models with pydantic | typed API, automatic validation, easy tests |
| Storage | nothing, files, or SQLite, only when needed (`manage-data`) | no database server to install |
| Tests | pytest (backend), Vitest (pure frontend logic), Playwright (browser journeys, project-local) | all run by `npm run verify` |

How the parts talk: the browser only calls `/api/*` on its own site. In development Next.js forwards (rewrites)
those requests to FastAPI on 127.0.0.1 (`<frontend>/next.config.ts`, setting `BACKEND_URL`). Browsers never call
third-party APIs directly and never hold server secrets.

The walking skeleton in `scaffold/` already contains all of this: a page with a **Backend status** panel,
`GET /api/health`, one pytest test, Vitest tests and a Playwright smoke test at 1366 and 390 px.

## When to deviate

| If the product... | Then |
|---|---|
| shows data, tables, charts, forms, what-if inputs, downloads (most course projects) | standard stack |
| has users who sign in and keep their own data | standard stack plus `add-accounts`; consider a hosted identity provider |
| takes money | standard stack plus `add-payments` (hosted checkout, test mode) |
| has no screen at all (a scheduled report or export) | a plain Python script with pytest; the launchers expect a frontend, so adapt `verify` first (`prepare-deploy`) |
| the team already knows another framework well (Django, Streamlit, plain React) | possible, but the root commands must be adapted first (`prepare-deploy`); say so plainly and record it in the decision log |

When in doubt, use the standard stack without accounts or storage: it proves the idea fastest, and calculation
code in the backend's logic layer can be reused later.

## How to explain the choice (example)

"I recommend the standard stack: a Next.js website with a Python FastAPI backend. You get one command to install
everything (`npm run setup`), one to run it (`npm run dev`) and one to check it (`npm run verify`). The weekly
table and the 'most improved' card can be on screen in the second slice. The cost is two languages, TypeScript
for the screens and Python for the calculations, but each stays small. We save runs in SQLite, a database that
is a single file, so nothing else needs installing. Alternative: a Streamlit app, all in Python, but the root
commands would need rewriting and the layout is harder to control."

## Root commands (run from the repository root)

| Command | What it does | What you should see |
|---|---|---|
| `npm ci` | once, after cloning: prepares the launchers (no runtime dependencies) | `added 0 packages` or similar, exit 0 |
| `npm run create-app -- --name "<App name>"` | copies `scaffold/` to `app/` and points `app-creator.config.json` at it; refuses to overwrite | the files it created and the next steps |
| `npm run setup` | checks Node ≥ 22.13, finds Python 3.10–3.13, creates `<backend>/.venv`, installs `requirements.lock`, runs `npm ci` in `<frontend>`, installs Chromium into `.cache/ms-playwright`. Skips steps whose lockfile has not changed | `Node: …`, `Python: 3.x (…)`, then each step done or skipped |
| `npm run dev` | starts backend (127.0.0.1:8000) and frontend (http://127.0.0.1:3000); refuses busy ports; Ctrl+C stops both | both URLs printed |
| `npm run demo` | like `dev` with the config's `demoEnv` (for example offline fixture mode, no keys) | same, with the demo settings named |
| `npm run verify` | toolkit checks, backend lint + pytest, frontend lint, typecheck, Vitest, production build, then a Playwright smoke test on spare ports | a summary; exit code 0 only if everything passed |

Ports: `BACKEND_PORT` and `FRONTEND_PORT` (in the terminal or the root `.env`) override the defaults.

## How `npm run setup` finds Python

Several Pythons are often installed, and the first one on the PATH may be too old (macOS `/usr/bin/python3` can
be 3.9) or a shared base installation (Anaconda). Setup searches in this order and uses the **first supported**
one (3.10–3.13):

1. `APP_PYTHON`, if set (in the terminal or the root `.env`). If it does not run or is unsupported, setup stops
   with a message instead of guessing.
2. Windows only: the `py` launcher, newest first (`py -3.13` … `py -3.10`).
3. `python3.13` … `python3.10`, then `python3`, then `python` on the PATH.
4. macOS/Linux: `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin` (`python3.13` … `python3.10`).
5. Anaconda, Miniconda and Miniforge in the usual places (`~/anaconda3`, `~/opt/anaconda3`, `~/miniconda3`,
   `~/miniforge3`, `/opt/anaconda3`, `/opt/miniconda3`, `C:\ProgramData\anaconda3`, …).

It prints which one it chose (`Python: 3.12.4 (python3.12)`) and any it skipped. A virtual environment created
*from* Anaconda's Python is still separate; what is forbidden is installing packages into the base installation
itself. Setup never does that.

### If setup picks the wrong Python or finds none

See what is installed:

```bash
# macOS / Linux
for p in python3.13 python3.12 python3.11 python3.10 python3 python; do command -v $p >/dev/null && echo "$p: $($p --version 2>&1)"; done
for d in /opt/anaconda3 ~/anaconda3 ~/opt/anaconda3 /opt/miniconda3 ~/miniconda3 ~/opt/miniconda3 ~/miniforge3; do [ -x "$d/bin/python" ] && echo "$d/bin/python: $("$d/bin/python" --version 2>&1)"; done
# Windows (PowerShell)
py -0p
Get-ChildItem "$env:USERPROFILE\anaconda3\python.exe","$env:USERPROFILE\miniconda3\python.exe","$env:LOCALAPPDATA\anaconda3\python.exe","C:\ProgramData\anaconda3\python.exe" -ErrorAction SilentlyContinue | ForEach-Object { "$($_.FullName): $(& $_.FullName --version)" }
```

Then tell setup exactly which one to use:

```bash
# macOS / Linux, one run
APP_PYTHON=/opt/homebrew/bin/python3.12 npm run setup
# Windows (cmd)
set APP_PYTHON=C:\Users\you\AppData\Local\Programs\Python\Python312\python.exe
npm run setup
# Windows (PowerShell)
$env:APP_PYTHON = "$env:USERPROFILE\anaconda3\python.exe"; npm run setup
```

To make it permanent, the owner puts `APP_PYTHON=...` in the root `.env` (created from `.env.example`). The
assistant never writes that file.

If no supported Python is installed, stop and tell the owner how to get one (python.org, `brew install
python@3.12`, or `conda create -n app python=3.12`), then open a new terminal. Do not install it yourself. If the
owner has Anaconda but none of the checks finds it, ask where it is (Anaconda Navigator, or `conda info --base` in
the Anaconda Prompt) before suggesting a new installation.

After setup, the backend's Python is `<backend>/.venv/bin/python` (Windows `<backend>\.venv\Scripts\python.exe`).
The launchers use it; activation (`source .venv/bin/activate`) is never needed.

## Dependencies

- Backend: add the exact version to `<backend>/requirements.in`, regenerate `requirements.lock` with the steps in
  its header (a temporary venv, `pip install -r requirements.in`, `pip freeze`), then `npm run setup`. Never `pip install` into a global Python.
- Frontend: `npm install --save-exact <package>` inside `<frontend>` (`.npmrc` keeps versions exact), commit
  `package.json` and `package-lock.json`. Never `npm install -g`.
- Add a library only when a slice needs it, and record why in the decision log.

## Permissions for the chosen stack (Claude Code)

Propose narrow allow rules for routine checks, and add them to `.claude/settings.json` only with the owner's
agreement, for example `Bash(npm run verify)` and `Bash(npm run setup)`. Never propose rules that allow any
command of a kind: no `Bash(*)`, `Bash(python *)`, `Bash(npm *)`, `Bash(npx *)` or `Bash(pip install *)`.
Installing new packages, starting servers and deleting files keep asking. Cline has no per-command allow list:
tell the owner which commands are routine checks, so they know what they are approving.
