# RESPONSE — m1-06-backend-api

- From: backend-engineer → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: 607a20a3-2374-4b35-aa4b-2395c0f510a3 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T18:42:46.159Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
The backend for this step is in place: meta, search and profile endpoints, one error format, settings and fixture loading. `pytest -q` and `ruff check .` both exit 0, so the done condition is met, and the full root `npm run verify` also passed.

**What it does:**
- **Search** works over the three demo companies by ticker, CIK or name. Ticker and name matching ignore case, and a CIK can have any number of leading zeros or a `CIK` prefix. Each company appears once, so Alphabet's four tickers give one result. `tesla` returns an empty list (M1-AC3).
- **Profile** returns the fields exactly as in the recorded submissions file (M1-AC4). When SEC leaves a field empty, the API returns null rather than invented text.
- **Errors** all share the agreed shape:
  - a bad CIK gives 422 `invalid_cik` with "A CIK has up to 10 digits" (M1-E2);
  - a company outside the demo gives 404 `company_not_found`;
  - an empty, 101-character or missing `q`, or a `limit` outside 1–20, gives 422 `invalid_query`;
  - an unexpected crash gives 500 `internal_error` with a reference id, and the details go only to the server log.
- **Labels:** every response is labelled `RECORDED SEC DEMO · snapshot 2026-11-03`. If the fixtures are marked synthetic, the label becomes `SYNTHETIC TEST DATA` instead, whatever the manifest claims.
- **Settings:** the app refuses to start if `DATA_MODE` is anything other than `fixtures`, or if `FIXTURES_DIR` has no manifest; the message names the setting. Tests need no `.env`.
- **No network:** a test blocks all outgoing connections and confirms every M1 endpoint still answers.

**Choices I made (none change the contract):**
- **Which ticker a result shows:** an exact ticker match shows the ticker typed (`goog` → GOOG). A prefix match shows the first matching ticker (`goo` → GOOGL). Other matches show the primary ticker.
- **Name matching** uses the SEC company name only, not former names.
- **Raw SEC values are passed through unchanged.**
  - Former-name dates stay full timestamps (`2007-01-10T00:00:00.000Z`).
  - Alphabet's exchanges list repeats `Nasdaq` four times, once per ticker.

  The frontend will need to format the dates and may want to merge the repeated exchanges.
- **Relative `FIXTURES_DIR`:** a relative path is read from the repository root, which matches the wording in `.env.example`.
- **Extra files and test:** I added `api/deps.py` and the overview response models now so step m1-07b can use them. The synthetic-label test builds its data in a temporary folder, so nothing new goes into `tests/synthetic/`.

My models match the frontend's `types.ts` with no differences.

I didn't update `milestones/*.md`; only m1-05 and m1-14 edit those files. I propose these decision-log rows, each a routine technical choice under delegation:
1. Search ranking and which ticker a result shows, as above.
2. A relative `FIXTURES_DIR` is resolved from the repository root.
3. Former-name dates are passed through as raw SEC timestamps.
4. A validation error's code is chosen by parameter: `q` and `limit` give `invalid_query`, `cik` gives `invalid_cik`, anything else gives `invalid_request`.

## Handoff
Changes: created `be/app/settings.py`, `be/app/errors.py`, `be/app/models/{__init__,common,companies}.py`, `be/app/data/{__init__,fixtures}.py`, `be/app/logic/search.py`, `be/app/api/{__init__,deps,meta,companies}.py`, `be/tests/test_search.py`, `be/tests/test_api_m1.py`, `be/tests/test_no_network.py`; changed `be/app/main.py` (now built by a `create_app(settings)` function; `/api/health` unchanged). No other files touched.
Verification evidence: new tests failed first (3 collection errors, modules missing); then in the backend `.venv/bin/python -m pytest -q` → 162 passed, exit 0, and `.venv/bin/ruff check .` → "All checks passed!", exit 0; `DATA_MODE=live` import → `SettingsError` naming DATA_MODE; root `npm run verify` → exit 0, "All checks passed." (all 8 steps pass, Playwright still on the scaffold smoke spec). No live SEC calls.
Remaining findings: (1) Former-name dates are raw SEC timestamps and Alphabet's exchanges list repeats Nasdaq per ticker; the frontend should format and may merge them. (2) No differences between the pydantic models and `fe/lib/types.ts`. (3) The four proposed decision-log rows above are for m1-14 to record. (4) The overview endpoint, its `years` validation code and its cases in `test_api_m1.py` and `test_no_network.py` are left to m1-07b.
Next action: m1-07b-overview (backend-engineer) adds `logic/statements.py` and `GET /api/companies/{cik}/overview` using `FixtureStore` and `OverviewResponse`.
<!-- VERBATIM:END -->
