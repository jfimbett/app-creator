# RESPONSE — m1-07b-overview

- From: backend-engineer → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: 6d05834f-1378-4d17-b17c-5febb579df79 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T18:45:30.755Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
The overview endpoint is built. Apple's and Microsoft's latest annual revenue and net income match the hand-worked rows FX1–FX4 exactly, and Apple has 20 annual periods, Microsoft 19 and Alphabet 13. All checks pass: backend `pytest -q` (196 passed), `ruff check .`, and `npm run verify` from the root.

**What the endpoint returns.** `GET /api/companies/{cik}/overview` gives:
- **Key figures:** the latest reported annual revenue and net income, in whole USD rather than millions.
- **Chart rows:** one per fiscal year, earliest first, labelled `FY<year>` with the end date.
- **Notes:** the line "Values may reflect later restatements; not point-in-time."
- **Source:** the `RECORDED SEC DEMO · snapshot 2026-11-03` label and the original SEC URL of the company-facts file.

Every value names the SEC filing it came from (concept, form, accession number, filing date). A value that is absent is `null` with a reason, never 0. Revenue uses "no mapped revenue concept" and net income has its own reason, "no NetIncomeLoss fact", as m1-07 asked.

**How the tests check it.**
- Expected values, periods and accession numbers are copied from FX1–FX4 and the period counts in `acceptance.md`, not taken from the app's output. One test confirms FX4 keeps the 10-K and ignores a later proxy-statement (DEF 14A) copy of the same figure.
- A few edge cases use small made-up inputs marked `SYNTHETIC`: a missing year, a reported loss staying negative, and no revenue at all.
- One of my first made-up cases was wrong and I fixed the test, not the code. The reporting currency is defined by revenue facts, so a company with no revenue at all gets an empty chart and a note.

**Where I differed from the brief or the listed files:**
1. **Two extra files.** I added a small company-facts accessor to `app/data/fixtures.py`, because the store did not load those files yet. It reads them at startup (about 1.8 MB) and they count towards the existing "is this synthetic?" check. I also added three overview requests to `tests/test_no_network.py`, as its docstring asked.
2. **Function inputs.** The brief names the function `overview(facts, profile, years)`. Mine takes the company-facts data, its SEC URL and the year count, because the profile isn't needed and the URL is needed for provenance.
3. **Key-figure rule.** A key figure is the latest year that actually has a value. If the newest year is missing, it falls back to an earlier year, never a zero.
4. **`years` errors.** A bad `years` value gets the generic code `invalid_request` with `{"parameters": ["years"]}`, because I didn't add a new code to `errors.py`.

`npm run verify` still runs the scaffold's old smoke test; the M1 browser journey belongs to the frontend steps. The criteria statuses in `acceptance.md` and the decision-log rows for points 2–4 are not updated yet; they are outside this step's files.

## Handoff
Changes:
- `examples/sec-analytics/backend/app/logic/statements.py` (new)
- `examples/sec-analytics/backend/app/api/companies.py` (overview endpoint, shared 404 helper)
- `examples/sec-analytics/backend/app/data/fixtures.py` (company-facts accessor; outside the listed files, but needed)
- `examples/sec-analytics/backend/tests/test_overview_fixtures.py` (new, 21 tests)
- `examples/sec-analytics/backend/tests/test_api_m1.py` (overview cases)
- `examples/sec-analytics/backend/tests/test_no_network.py` (overview requests)

Verification evidence:
- Tests were written first: collection error with no module, then 14 API/offline failures before the endpoint existed.
- `.venv/bin/python -m pytest -q` (backend): 196 passed, exit 0.
- `.venv/bin/ruff check .`: exit 0.
- `npm run verify` (root): exit 0, "All checks passed." (Playwright is still the scaffold smoke spec).
- No live calls.

Remaining findings:
- Decision-log rows still needed for: the function inputs, the key-figure fallback, `years` errors using `invalid_request`, and no revenue meaning no currency (empty chart plus a note).
- FX1–FX4 and M1-AC5 (API part) can now be marked passing (`test_overview_fixtures.py`) in `milestones/acceptance.md`; I did not edit milestone docs.

Next action: Frontend step builds `KeyFigures` and `RevenueIncomeChart` on `/api/companies/{cik}/overview`. The integrator updates `acceptance.md`, `plan.md` and the decision log.
<!-- VERBATIM:END -->
