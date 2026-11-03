# Choosing a stack

Pick the **simplest path that delivers the main user journey**. Recommend one option, name one alternative,
and explain the tradeoff in plain language. A stack is a set of tools that work well together: a language,
a framework for the interface, a way to store data, and a way to test.

Before recommending a specific library or service, check its current official documentation (versions, free
tiers and terms change). Never sign the student up for anything, and never choose a paid service without
their explicit agreement.

## Decide the path first

| If the product... | Path |
|---|---|
| is used by the team itself or a few known people, shows data, charts, tables, what-if inputs, downloads | **A. Dashboard** |
| has outside customers who sign in, keep their own saved data, upload files, or pay | **B. Customer-facing web app** |
| has no screen at all: it produces a report, a spreadsheet or an email on a schedule | **C. Automation script** (a small variant of A without the interface) |

When in doubt, start with A: it proves the idea faster, and its data and calculation code can be reused in B
later. Moving from A to B is a planned slice, not a rewrite, if calculations live outside the interface code.

## Path A: dashboard (default for data and analysis products)

| Part | Recommended | Alternatives |
|---|---|---|
| Language | Python 3.11+ | – |
| Interface | Streamlit (pages, widgets, charts in plain Python) | Dash, Panel, Gradio |
| Charts | Plotly or Altair | matplotlib |
| Data | pandas | polars |
| Storage | files the app reads; SQLite (built into Python) when something must be saved | – |
| Tests | pytest; Streamlit's `AppTest` to run the app without a browser; the project's browser check for critical screens | – |
| Sharing | run on a laptop for the demo; a hosted Python app platform if others must use it | – |

Strengths: fastest to a working screen, everything in Python, few files. Limits: one shared app for all
users, limited control over layout, sign-in and per-user data are possible but not its strength.

## Path B: customer-facing web app

| Part | Recommended | Alternatives |
|---|---|---|
| Language | Python 3.11+ | TypeScript (Next.js) if the team already knows JavaScript |
| Framework | **Django**: accounts, permissions, database models, migrations, admin pages, forms and CSRF protection are built in | FastAPI or Flask (more freedom, more pieces to choose and secure yourself) |
| Interface | Django templates (server-rendered HTML) with a small CSS framework | a separate JavaScript front end (only if the team knows it) |
| Charts (only if agreed) | one charting library chosen with the student, kept as a local file (no CDN by default); the server prepares all values | none: tables only |
| Storage | SQLite on the laptop; PostgreSQL when deployed | – |
| Accounts | Django's built-in authentication | a hosted identity provider (sign-in with Google etc.) when required |
| Payments | a payment provider's **hosted checkout page** in test mode, with webhook verification (skill `add-payments`) | – |
| Tests | Django's test client or pytest-django (tests where the framework expects them, e.g. per-app `tests.py` or `tests/`); the project's browser check for critical screens | – |
| Deployment | a platform that runs Python web apps with a managed PostgreSQL database | – |

Strengths: real accounts and per-user data with safe defaults, schema changes tracked as migrations, an admin
screen for free. Limits: more files and concepts than path A; deployment needs a database and secrets set on the
host.

## Path C: automation script

Python + pandas, output to Excel (openpyxl) or PDF/HTML, run from the command line, tests with pytest. Add a
schedule only at deployment time.

## Capabilities: add only what the product needs

| Need | Add it with | Default |
|---|---|---|
| External data or API | `integrate-api` | as needed |
| Saved data, schema changes | `manage-data` | files or SQLite |
| Sign-in, per-user data, roles | `add-accounts` | **off** |
| Taking money | `add-payments` | **off**; test mode only during the course |

## How to explain the choice (example)

"I recommend a dashboard in Python with Streamlit. You can show the comparison table and the chart on one page
within the first session, and you never have to write HTML. The cost is that every visitor sees the same app:
there are no personal accounts. If you later need customers to sign in and save portfolios, we move the
calculation code we already tested into a Django app. Alternative: Django from the start, which takes about two
more slices before the first useful screen."

## Setting up the environment (Python stacks)

1. **Find the installed versions.** Several Pythons are often installed, and the first one on the PATH may be old
   (macOS's `/usr/bin/python3` can be 3.9) or a shared base installation (Anaconda).

   ```bash
   # macOS / Linux
   for p in python3.14 python3.13 python3.12 python3.11 python3 python; do command -v $p >/dev/null && echo "$p: $($p --version 2>&1)"; done
   # Windows (PowerShell or cmd)
   py -0p
   ```

   **Then look for Anaconda or Miniconda**, which most students in this course have: it is often not on the PATH
   of the terminal you run in, so the list above can miss it.

   ```bash
   # macOS / Linux
   for d in /opt/anaconda3 ~/anaconda3 ~/opt/anaconda3 /opt/miniconda3 ~/miniconda3 ~/opt/miniconda3 ~/miniforge3; do [ -x "$d/bin/python" ] && echo "$d/bin/python: $("$d/bin/python" --version 2>&1)"; done; command -v conda >/dev/null && echo "conda base: $(conda info --base)"
   # Windows (PowerShell)
   Get-ChildItem "$env:USERPROFILE\anaconda3\python.exe","$env:USERPROFILE\miniconda3\python.exe","$env:LOCALAPPDATA\anaconda3\python.exe","C:\ProgramData\anaconda3\python.exe" -ErrorAction SilentlyContinue | ForEach-Object { "$($_.FullName): $(& $_.FullName --version)" }
   ```

   If you find one, use its **full path** in step 3 (for example `/opt/anaconda3/bin/python -m venv .venv`, or
   `& "$env:USERPROFILE\anaconda3\python.exe" -m venv .venv` on Windows). If none of the checks finds a Python 3.11+,
   ask the student where their Anaconda is (Anaconda Navigator, or `conda info --base` in the Anaconda Prompt)
   before telling them to install anything.

2. **Choose** the newest version that the chosen framework's official documentation supports (check it; do
   not assume). Any installation can be the source of the environment, including Anaconda's: a virtual
   environment created from it is still separate. What is forbidden is installing packages into the base
   installation itself. If none is installed, stop and tell the student how to install one (python.org, or their package
   manager); do not install it yourself.
3. **Create the isolated environment** with that exact interpreter, inside `app/`:

   ```bash
   cd app
   python3.12 -m venv .venv            # Windows: py -3.12 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt     # Windows: .venv\Scripts\python -m pip ...
   ```

4. From then on, run everything with `.venv/bin/python` (Windows `.venv\Scripts\python`), written out in full in
   `app/README.md` and in `AGENTS.md`'s "This project". Activation (`source .venv/bin/activate`) is optional for
   the student and never needed by the assistant. `app/.venv/` is git-ignored.

Development-only tools (the browser check, linters) go in `app/requirements-dev.txt`, so the app's own dependency
file stays minimal.

## Permissions for the chosen stack

`.claude/settings.json` already allows the test and check commands of the Python paths when run with the
project's environment from `app/` (for example `cd app && .venv/bin/python -m pytest`,
`.venv/bin/python manage.py test`, `.venv/bin/python checks/browser_check.py <url>`). For another stack, propose
the matching narrow rules and add them only with the student's agreement:

| Stack | Rules to propose |
|---|---|
| Next.js / Node | `Bash(npm test *)`, `Bash(npm run test *)`, `Bash(npm run lint *)`, `Bash(npx playwright test *)` |
| Windows, Python | the same commands with the Windows path; copy the exact command text from a permission prompt the student saw (for example `.venv\Scripts\python -m pytest`), and add `Bash(<that text> *)` |

Never propose rules that allow any command of a kind: no `Bash(*)`, `Bash(python *)`, `Bash(.venv/bin/python *)`,
`Bash(npm *)`, `Bash(npx *)` or `Bash(pip install *)`. Those would let any script or package run without the
student seeing it. Installing packages, starting servers and deleting files keep asking.
