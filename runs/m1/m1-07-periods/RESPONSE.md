# RESPONSE — m1-07-periods

- From: backend-engineer → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: 9182bb5d-8780-4532-95ed-6f3f18023911 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T18:36:11.063Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
I added the annual-period rules to `backend/app/logic/periods.py`, along with 30 tests that use only made-up data. All 30 pass and `ruff check .` exits 0. I wrote the tests first and confirmed they failed before the module existed.

**What the tests cover (all brief §9 cases):**
- **Annual length:** durations of 364, 371, 350 and 380 days count as a year; 349, 381, 91 (a quarter) and 273 (year-to-date) do not.
- **Instant facts:** a balance on a single date (no start date) never counts as a yearly value. It only matches a year's exact end date.
- **Forms:** a 10-Q fact of annual length is ignored, even when it was filed after the 10-K.
- **Restatements:** a 10-K with 1,000 and a later 10-K/A with 1,010 give 1,010 (not 2,010), and the 10-K/A is kept as the source. On the same filing date the higher accession number (`…-24-000101` over `…-24-000099`) wins, in either input order and on repeated runs.
- **Not grouping by fiscal year:** a FY2025 10-K that repeats FY2023 lands in FY2023 and keeps its `fy: 2025` in the source details. Two periods filed with the same `fy` stay separate.
- **Revenue concept:** each year uses its own revenue concept and they are never added together. When two are present, the first in the priority list wins.
- **Missing values:** a year with no revenue concept gives no value, status "missing" and the reason "no mapped revenue concept". A genuinely reported 0 stays 0.
- **Currency:** facts in EUR next to USD are ignored, and only USD is used.

The made-up facts sit inside the test file under the `SYNTHETIC: invented for tests, not SEC data` marker. I did not create `tests/synthetic/`; the step brief allowed either place.

The full backend suite has 6 failures, all in `tests/test_fixtures_manifest.py`, which belongs to the parallel fixture-capture step. None come from this work.

## Handoff
Changes:
- `examples/sec-analytics/backend/app/logic/periods.py` (new): `Period`, `Fact`, `AnnualValue`, `parse_facts`, `is_instant`, `is_annual_duration`, `choose_fact`, `annual_facts`, `annual_periods`, `pick_first`, `reporting_currency`, `instant_at`, `fiscal_year_label`, `REVENUE_MISSING_REASON`. No files, network or clock.
- `examples/sec-analytics/backend/tests/test_periods.py` (new): 30 tests on synthetic facts.

Verification evidence:
- `.venv/bin/python -m pytest -q tests/test_periods.py` first failed with an ImportError (no module yet), then passed: 30 passed, exit 0.
- `.venv/bin/ruff check .` exit 0. An earlier run flagged 9 long lines in `scripts/capture_fixtures.py` (the parallel step's file, not touched by me); they were gone on the rerun.
- Full `pytest -q`: 94 passed, 6 failed, all in `tests/test_fixtures_manifest.py`.
- `npm run verify` not run; the milestone is still mid-way.

Remaining findings:
- Routine choices to add to the architecture decision log (I didn't touch `milestones/*.md`; outside this step's two files):
  - "Higher accession number" compares the accession's digits as one integer.
  - A currency tie (same number of annual revenue facts) goes to the alphabetically first currency.
  - Fact rows missing `end`, `val`, `form`, `accn` or `filed` are skipped, because they cannot carry a source.
  - Periods are keyed by exact (start, end).
- `statements.py` (step m1-07b) must give net income its own missing reason (e.g. "no NetIncomeLoss fact"); this module has no default for it.
- `plan.md` and `acceptance.md` statuses still need updating by whoever integrates the milestone.

Next action: m1-07b builds `statements.py` on top of `annual_facts`, `reporting_currency` and `pick_first`, once the fixtures and FX1–FX4 exist.
<!-- VERBATIM:END -->
