---
name: debug-issue
description: Use when something is broken or wrong (an error, a crash, a wrong number, a blank chart, a page that does not load, a failing test or verify step, behaviour that differs from acceptance.md), or before refactoring code that works.
---

# Debug: reproduce, locate, fix, verify

Find the cause before changing code. A fix that is not proven by a failing-then-passing check is a guess.
Cleaning up working code is a different job with its own rules: [refactoring.md](refactoring.md).

Paths: `<backend>`, `<frontend>`, `<docs>` come from `app-creator.config.json` (`app.backendDir`,
`app.frontendDir`, `app.docsDir`).

## Inputs

- The person's description: what they did, what they expected, what happened (the exact error text or a
  screenshot description). Ask for any of these that are missing, at most three questions.
- The code, logs and tests in `<backend>` and `<frontend>`; `<docs>/acceptance.md` for the expected behaviour;
  the output of `npm run verify` or `npm run dev` if the problem shows there.

## Where to look first (standard stack)

| Symptom | First places to look |
|---|---|
| `npm run setup` / `dev` / `verify` fails | the launcher's message (it names the failing step), then that step's log; Node and Python versions; a busy port (`dev` refuses it: set `BACKEND_PORT` / `FRONTEND_PORT`) |
| Page shows "Error" or a blank area | browser DevTools → Console and Network: which `/api/...` call failed and its status |
| `/api` call returns 500 | the backend terminal (FastAPI traceback, read from the bottom up) |
| `/api` call returns 404 | the route path in FastAPI versus the frontend's `fetch` path; the Next.js rewrite of `/api/*` |
| `/api` call returns 422 | FastAPI's response body names the field that failed validation |
| Wrong number | follow one value from the source (fixture, database, API) through each function to the screen; check units, missing-vs-zero, period alignment |
| Works in `dev`, fails in `verify` | `verify` uses the production build and `demoEnv` (fixture mode): check server/client component boundaries, environment variables, fixture data |
| Playwright fails | `<frontend>/test-results/`: the screenshot and `trace.zip` (`npx playwright show-trace ...`) |
| External API fails | [http-client-patterns.md](../integrate-api/http-client-patterns.md), "Debugging an integration" |

## Actions

1. **Reproduce.** Run the exact steps, command or test and see the failure yourself. Write down the smallest set of
   steps that shows it. If you cannot reproduce it, say what you tried and ask for more detail; do not fix blind.
2. **Capture it in a test** that fails for the reason the person sees (`test-and-check`): pytest for backend
   logic and endpoints, Vitest for frontend logic, a Playwright journey for a screen flow. If a test is not
   practical (pure layout), write the manual reproduction steps in the report instead.
3. **Locate the cause.** Read the error from the bottom up; follow the data from the input to where it goes wrong;
   check recent changes (`git diff`, `git log -p -- <file>`); add temporary prints or logging if needed (remove
   them afterwards, and never print settings or secrets). State the cause in one sentence, with the file and line.
4. **Fix the cause, not the symptom.** The smallest change that makes the failing test pass. Do not change the
   expected value of a test to make it pass. Do not wrap errors in `try`/`except` (or `catch`) to hide them.
5. **Verify:** the new test passes, `npm run verify` passes, and the original reproduction steps now behave
   correctly in the running app.
6. **Look for siblings:** search for the same mistake elsewhere (same function, same pattern, `grep`) and list
   them; fix them only with the owner's agreement (or within a recorded delegation, `docs/TOOLKIT.md` §4).
7. **Record:** progress log in `<docs>/plan.md`; a line in `AI-USAGE.md` if the AI found or fixed it; change
   report; proposed commit (`fix: ...`). If cleanup is tempting, do it afterwards as a separate refactoring
   commit ([refactoring.md](refactoring.md)), never mixed into the fix.

## Outputs

Reproduction steps, the cause (file:line, one sentence), the fix, a regression test, check results, a change report.

## Verification

- The regression test failed before the fix and passes after.
- `npm run verify` exits 0.
- The original steps were re-run against the fixed app.

## Stop when

- The cause is identified, fixed and verified.
- **Stop and ask** after two different fix attempts fail, when the cause is outside the app (a service outage, a
  machine set-up problem, a data error at the source), or when the "bug" is really a missing or unclear business
  rule. Report what is known, what was ruled out and the options.

## Common mistakes

- Rewriting a whole file when one line was wrong.
- "Fixing" by catching the exception and returning an empty result (or 0).
- Declaring it fixed because the error message disappeared.
- Mixing a refactor into a bug fix, so nobody can see which line fixed it.
- Debugging against the owner's real data or `.env` instead of fixtures.

## Example

Report: "the chart shows a drop to zero in March". Reproduce: `npm run demo`, open the chart, March is 0.
Test: `test_month_without_data_is_none` in `<backend>/tests/test_series.py` fails (returns 0). Cause:
`app/logic/series.py:42` uses `totals.get(month, 0)`. Fix: `totals.get(month)` and the chart draws a gap for
`null`. Verify: test passes, `npm run verify` exit 0, March shows a gap in the screenshot at both widths.
Siblings: the same `.get(..., 0)` in `summary.py:17` listed for the owner. Commit `fix: show missing months as
gaps, not zero`.
