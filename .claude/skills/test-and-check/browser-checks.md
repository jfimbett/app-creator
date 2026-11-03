# Checking screens: tests, browser checks and visual inspection

Three different kinds of evidence. Report each one under its own name, never one as another.

| Kind | What it proves | What it cannot prove | Report it as |
|---|---|---|---|
| **Automated test** (test client, `AppTest`, unit test) | the server returns the right content, the shared layer computes the right values, permissions hold | that the page draws, that the chart is readable, that the layout fits a phone | `Tests: 42 passed` |
| **Browser check** (a script in a real headless browser) | the page loads and draws without JavaScript errors, the critical interactions work, no sideways scrolling, keyboard focus reaches controls, nothing loads from the internet | whether it looks right or is understandable | `Browser check: 0 problems at 1366 px and 390 px` |
| **Visual inspection** (someone looks at the screenshots or the live page) | layout, overlap, legibility, whether the chart tells the truth at a glance | anything not on the screenshot | `Looked at: 4 screenshots by Claude; student look pending` |

The assistant may inspect screenshots by opening the PNG files, if its model can read images. That counts as
visual inspection by the assistant, and it is still not the student's look. The student's own look at the running app is the final visual check: ask for it,
and record it in `docs/acceptance.md` as `checked by <name> on <date>`.

## A reproducible browser-check setup (no personal tools needed)

Use a browser tool that the **project itself installs**, so every team member and every reviewer gets the same
result. A browser tool that only one person has configured in their own assistant setup does not count as
the project's check: if one was used, say so in the change report.

Python stacks (paths A, B and C with a web page):

1. Add `playwright` to `app/requirements-dev.txt` (development-only dependencies; not needed to run the app).
   Check the current version on its official documentation or package index first.
2. Install inside the app's virtual environment, after the student agrees (the browser download is about
   150 MB, stored in the user's cache folder, outside the project):

   ```bash
   cd app
   .venv/bin/python -m pip install -r requirements-dev.txt
   .venv/bin/python -m playwright install chromium
   ```

   Windows: `.venv\Scripts\python` instead of `.venv/bin/python`.
3. Copy [browser_check.py](browser_check.py) to `app/checks/browser_check.py`. Fill its CONFIG section from
   `docs/acceptance.md`: the journey's pages, a ready selector (for Streamlit `[data-testid='stApp']`), and the
   critical interactions with what the user should then see.
4. Start the app in one terminal, then run the check in another:

   ```bash
   cd app
   .venv/bin/python checks/browser_check.py http://127.0.0.1:8000
   ```

   It exits with 1 if it finds problems, and writes screenshots to `app/.browser-checks/` (git-ignored).
5. Document both commands in `app/README.md` under "Checks".

JavaScript stacks (for example Next.js): use the official Playwright test runner as a development dependency
(`npm init playwright@latest`, after the student agrees) with the same pages, widths and checks.

If the student does not want the browser download, or it fails: use the framework's test client for content,
then give the student a numbered click-through (step, what to click, what they should see), and report the
screens as **not verified** until they confirm.

## What a browser check of a critical screen covers

- Each journey page at a laptop width (1366 px) and a phone width (390 px): loads, draws, full-page screenshot.
- The critical interactions from `docs/acceptance.md` (choose, submit, switch, filter), each followed by a check
  of what the user sees.
- Loading, empty and error states: open the page with no data, and with a failing data source (a test setting or
  a test fixture), and screenshot each.
  With debug mode on, many frameworks replace the app's own error pages (404, 500) with a developer page. The
  check then reports that page, not the app's: say so, and check the app's error pages with a test, or with
  debug mode off if the app can run that way locally.
- No JavaScript errors in the console; no requests to other hosts when the app is meant to work offline.
- Keyboard: Tab reaches the controls, the focus is visible on the screenshot.
- Charts: hover one point if the chart has tooltips, and screenshot it.

## Data used by checks

- Run checks against **test data**: a temporary or separate test database, or a fixture file. Do not fill the
  student's own local database with check users. If you had to, delete them afterwards and say so.
- Test accounts for checks are created by the check or a fixture, with throw-away passwords passed through
  environment variables in the terminal. Never real accounts, never values from `app/.env`.
- Do not script against an interactive shell's printed output (framework shells can print banners that break
  parsing). Use the framework's test client, a small script that prints JSON, or a management command.
- If port 8000 (or 8501) is busy, start the app on another port and pass that URL to the check.
