# RESPONSE — m1-04-sec-client

- From: backend-engineer → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: a752008b-7ae5-49b7-b7aa-7b9037df2c4d (local Claude Code transcript; not committed)
- Finished: 2026-11-03T18:32:34.009Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
I finished the SEC client, the CIK rule and the concept lists, and both test files pass. Root `npm run verify` still fails, but only at the frontend unit tests: two tests in `fe/lib/api.test.ts`, which belongs to the frontend-lib step running in parallel. Everything before that passed, including backend lint and tests, so the browser check did not run.

- **CIK rule:** a CIK is the SEC's ID number for a company. Inputs like `320193`, `CIK320193` or ` 320193 ` all become `0000320193`. Anything else, such as `abc`, 11 digits or `-1`, is rejected with "A CIK has up to 10 digits".
- **SEC client:** it only fetches addresses that match the brief's fixed list of SEC URLs, and checks every redirect against that list before following it, at most 3. It refuses to send anything unless `SEC_USER_AGENT` is set and well formed; the error names the setting but never shows its value. It makes at most one request per second, one at a time, with a 20 s timeout. On a 429 or 503 it waits as SEC asks, up to 30 s, and retries at most twice. A 403 is never retried and reports "SEC refused the request (403)".
- **Concept lists:** the revenue priority list, `NetIncomeLoss`, and the 24 concepts the fixture capture keeps.

The tests were run first and failed because the modules didn't exist. All HTTP in them is mocked and the clock is fake, so nothing waits or reaches the network. The fake contact address is assembled in the test from a reserved `.invalid` domain, so no address is written out.

The client defines its own error classes rather than using the app's `errors.py`, which another step owns. I made a few small choices the brief didn't spell out (listed in the handoff); the capture step or the integration should check them.

## Handoff
Changes: created `examples/sec-analytics/backend/app/clients/__init__.py`, `app/clients/sec.py`, `app/logic/__init__.py`, `app/logic/cik.py`, `app/logic/concepts.py`, `tests/test_cik.py`, `tests/test_sec_client.py`. No other files touched.
Verification evidence: tests run first and failed (`ModuleNotFoundError: No module named 'app.clients'`, 2 collection errors). Then, in `be/`: `.venv/bin/pytest -q tests/test_cik.py tests/test_sec_client.py` → 60 passed, exit 0; `.venv/bin/pytest -q` → 62 passed, exit 0; `.venv/bin/ruff check .` → "All checks passed!", exit 0. Root `npm run verify` → exit 1: toolkit checks, ruff, pytest, frontend lint and typecheck pass; frontend unit tests fail in `fe/lib/api.test.ts` (2 tests, owned by the parallel m1-09 step). Build and Playwright did not run. No live SEC calls.
Remaining findings: (1) The `fe/lib/api.test.ts` failure must be fixed by m1-09 before verify can pass. (2) Defaults I chose: timeouts and network errors are not retried; the CIK prefix is case-insensitive; 404 becomes `SecNotFound`; the throttle measures the gap between request starts; the client takes the User-Agent value as an argument (reading `SEC_USER_AGENT` from the environment or `.env` is the capture script's job, m1-05) and checks its shape only at the first request. Proposed decision-log row: "SEC client errors are their own `SecError` classes with stable codes (`sec_contact_not_configured`, `upstream_not_allowed`, `sec_refused`, `sec_not_found`, `sec_unavailable`); the API layer maps them in M2. Routine technical choice under delegation." (3) The client's API, for m1-05: `SecClient(user_agent).get_json(url)`, `COMPANY_TICKERS_URL`, `submissions_url(cik)`, `companyfacts_url(cik)`. (4) No response-size cap; not required at M1.
Next action: m1-05-capture-fixtures builds `scripts/capture_fixtures.py` on `SecClient` with `CAPTURE_CONCEPTS`, once m1-09 fixes `fe/lib/api.test.ts`.
<!-- VERBATIM:END -->
