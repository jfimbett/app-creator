# RESPONSE — m1-05-capture-fixtures

- From: backend-engineer → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: 16adf1ad-34cd-498e-8ac9-baad1e7a8795 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T18:38:14.963Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
The capture worked: the script made one live run on 2026-11-03 with exactly 7 requests to SEC and saved authentic fixtures for Apple, Microsoft and Alphabet. The manifest test passes, `npm run verify` passes, and no email address appears in the fixtures or in any file I changed.

- **Capture script** (`scripts/capture_fixtures.py`): it uses the m1-04 SEC client and downloads everything into memory before writing any file. Files go to a temporary folder that replaces `fixtures/` only if all 7 requests succeed, so a blocked run leaves nothing half-written. The only thing it prints about the configured SEC_USER_AGENT is `SEC_USER_AGENT: set (value hidden)`. Before the live run I tested it once offline against fake SEC responses.
- **Fixtures**: the ticker file, three submissions files, three company-facts files, the manifest, `README.md` and `.gitattributes`. Each company has far more than the 5 required annual periods: Apple 20, Microsoft 19, Alphabet 13.
- **Known answers**, read by hand from the fixture files:

| Row | Value | Fact used |
|---|---|---|
| FX1 Apple revenue, year ending 2026-09-26 | 478,834,000,000 USD | `RevenueFromContractWithCustomerExcludingAssessedTax`, 10-K, filed 2026-11-03 |
| FX2 Apple net income, same year | 132,175,000,000 USD | `NetIncomeLoss`, same 10-K |
| FX3 Microsoft revenue, year ending 2026-06-30 | 331,839,000,000 USD | `RevenueFromContractWithCustomerExcludingAssessedTax`, 10-K, filed 2026-07-29 |
| FX4 Microsoft net income, same year | 133,749,000,000 USD | `NetIncomeLoss`, same 10-K |

Neither company has a `Revenues` fact for these years, so the second concept in the priority list is used. Microsoft's file also holds the same net-income figure from a later proxy statement (DEF 14A). The 10-K-only rule correctly leaves it out.

- **Fiscal year-end check** (now in the architecture decision log): Microsoft's and Alphabet's annual end dates all match their stated year-end. Apple's year ends on the last Saturday of September, so its end dates move between 09-24 and 09-30. Code must match years by start and end dates, never by the stated year-end.

Things later steps should know:
- **Extra Alphabet tickers.** SEC now lists four tickers for Alphabet: GOOGL, GOOG, GOOGM and GOOGN. All four are kept. The search step (m1-06) still has to return Alphabet only once for `goog`.
- **FX4 meaning.** The brief describes only three known answers, so I made FX4 Microsoft's net income.
- **Additions beyond the brief.** The script also writes the fixtures `README.md` and `.gitattributes`. The manifest has a few extra fields: which capture concepts each company lacks, period counts and how many filing rows were kept. The manifest test also fails if any email-like text appears under `fixtures/`.

## Handoff
Changes: `examples/sec-analytics/backend/scripts/capture_fixtures.py` (new); `examples/sec-analytics/fixtures/` (new: `company_tickers.json`, `submissions/CIK{0000320193,0000789019,0001652044}.json`, `companyfacts/` same three, `manifest.json`, `README.md`, `.gitattributes`); `examples/sec-analytics/backend/tests/synthetic/README.md`, `examples/sec-analytics/backend/tests/test_fixtures_manifest.py` (new); `milestones/acceptance.md` (fixture known-answer section FX1–FX4); `milestones/architecture.md` (decision-log row resolving the fiscal year-end `[verify against fixtures]`).
Verification evidence: manifest test before capture: 6 failed, 2 passed (expected); offline mocked dry run exit 0; `.venv/bin/python scripts/capture_fixtures.py` exit 0 ("Captured 7 files in 7 requests; snapshot 2026-11-03."); `pytest -q tests/test_fixtures_manifest.py` 8 passed; `ruff check .` exit 0; `pytest -q` 100 passed, exit 0; email-address grep over fixtures/ and all changed files: no matches (grep exit 1); `npm run verify` exit 0, "All checks passed." **live SEC: fixtures captured on 2026-11-03, 7 requests.**
Remaining findings: (1) Alphabet has four tickers (GOOGL, GOOG, GOOGM, GOOGN); m1-06 search must return one result per CIK. (2) FX4 = Microsoft net income (the brief names only three answers). (3) Apple's latest 10-K was filed on the capture day; a recapture will shift values. (4) `plan.md` progress log and `AI-USAGE.md` not updated (outside this step's file list; for m1-14). (5) Extra manifest fields: `concepts_absent`, period counts, `rows_kept`.
Next action: m1-07b-overview (backend-engineer): write `test_overview_fixtures.py` against FX1–FX4, then `logic/statements.py`.
<!-- VERBATIM:END -->
