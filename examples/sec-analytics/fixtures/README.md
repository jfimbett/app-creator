# Recorded SEC fixtures (RECORDED SEC DEMO)

Authentic data from SEC EDGAR, recorded on **2026-11-03** (UTC) for the demo universe: Apple
(CIK 0000320193), Microsoft (0000789019) and Alphabet (0001652044). The app serves these files
offline in fixture mode and labels them `RECORDED SEC DEMO · snapshot 2026-11-03`.

- `company_tickers.json`: the three companies' entries from
  https://www.sec.gov/files/company_tickers.json.
- `submissions/CIK##########.json`: https://data.sec.gov/submissions/, with `filings.recent` cut
  down to 10-K, 10-K/A, 10-Q and 10-Q/A rows.
- `companyfacts/CIK##########.json`: https://data.sec.gov/api/xbrl/companyfacts/, only the us-gaap
  concepts in `backend/app/logic/concepts.py` `CAPTURE_CONCEPTS`.
- `manifest.json`: for every file the source URL, retrieval time, sha256, size, accession numbers,
  periods, what was kept and what was trimmed. No value was edited, rounded or reordered.

The User-Agent used for the capture was configured locally by the person who ran it and is not
recorded.

## Recapture

These files change only by running the capture script; never edit them by hand. With your own
`SEC_USER_AGENT` set (see the root `.env.example`), from `examples/sec-analytics/backend/`:

    .venv/bin/python scripts/capture_fixtures.py

(Windows: `.venv\Scripts\python.exe scripts\capture_fixtures.py`). It makes 7 requests, at
most one per second, and replaces this whole folder.

**Warning:** a recapture changes every number. The hand-worked known answers (`FX…` rows in
`milestones/acceptance.md`) must be worked out again from the new files before the tests that use
them are updated.
