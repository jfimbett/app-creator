# RESPONSE — B03-research-sec-edgar

- From: default → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: a0c139b5-1417-4c95-919d-1721e0429a30 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T17:08:14.873Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
I wrote `docs/research/sec-edgar.md` as implementation notes. Every claim cites its source URL with the retrieval date 2026-11-03, and anything not in an official page is marked [unverified]. It is about 1,350 words, slightly over your 1,300 target. Nothing is committed and no other file was touched; `docs/TOOLKIT.md` and `runs/bootstrap/B06-agents/` are new untracked files I didn't create.

Points that matter for the build:

- **Field names aren't documented.** The API pages don't name `filings.recent`, `filings.files`, `accn`, `fy`, `fp`, `form`, `filed`, `frame`, `start`, `end`, `val` or `units`. I took them from live structure-only fetches of Apple's companyconcept and submissions JSON, and the notes label them as such. The page only describes submissions pagination in prose ("files will contain an array of additional JSON files…").
- **fy/fp are filing-level, but no official text says so.** The sample data shows it: a fact for the period ending 2011-09-24 carries `fy: 2012` from an 8-K filed in 2013, and some facts have `fy`/`fp` null. The notes recommend identifying a period by `start`/`end` or `frame`, never by `fy`/`fp`.
- **The 403 status is [unverified].** The policy pages only say the SEC reserves the right to block IP addresses that send excessive requests. Access resumes once the request rate has stayed below the limit for 10 minutes. None of them names an HTTP status.
- **CORS:** the API page says "data.sec.gov does not support Cross Origin Resource Scripting (CORS)" ("Scripting", not "Sharing"). All data.sec.gov calls should therefore go through the backend.
- **No caching guidance exists.** The TTLs in the notes are our own suggestion, labelled as such.

## Handoff
Changes: `docs/research/sec-edgar.md` (new; `docs/research/` created). No other files edited, nothing installed, nothing committed.
Verification evidence: all of these returned HTTP 200:
- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://www.sec.gov/page/edgar-application-programming-interfaces-old
- https://www.sec.gov/os/accessing-edgar-data
- https://www.sec.gov/about/developer-resources
- https://www.sec.gov/privacy.htm#security
- https://www.sec.gov/files/company_tickers.json (structure only; no 403 through the fetch tool)
- https://data.sec.gov/api/xbrl/companyconcept/CIK0000320193/us-gaap/AccountsPayableCurrent.json (structure only)
- https://data.sec.gov/submissions/CIK0000320193.json (structure only; the middle part was summarised by the fetch tool, so some `filings.recent` column names are marked [unverified])

There were no fetch failures. The sample User-Agent on the SEC page contains a placeholder email address, which is not reproduced.
Remaining findings:
- The developer-resources page doesn't mention User-Agent; only accessing-edgar-data does. Its sample has the form `<Company Name> <admin email>`, so the app needs a configurable contact value.
- `company_tickers*.json` is documented only on accessing-edgar-data, with "not guarantee accuracy or scope".
- The older-submissions URL `data.sec.gov/submissions/{files[].name}` is inferred, not documented.
- There are no contradictions with PROGRESS.md D5/D6: those are frontend and backend package pins and say nothing about SEC behaviour. httpx 0.28.1 in D6 can set the required User-Agent and is suitable for the backend proxy that the CORS restriction implies.

Next action: add a structure-only request per data.sec.gov endpoint to the backend integration tests, to confirm the [unverified] field names before relying on them.
<!-- VERBATIM:END -->
