# PROMPT — B03-research-sec-edgar

- Sender: owner (top-level Claude Code session)
- Receiver: default Claude Code agent (`--agent default`; the toolkit's agents do not exist yet — orchestrator B01 risk 4)
- Starting commit: 10e8c6f
- Skills: none; instruction paths: GOAL.md, PROGRESS.md
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B03-research-sec-edgar --agent default --mode bypassPermissions --milestone bootstrap`
- Plan reference: runs/bootstrap/B01-orchestrator-bootstrap-plan/RESPONSE.md

<!-- DISPATCH:BEGIN -->
Research task for the App Creator build (see GOAL.md §6). Topic: SEC EDGAR APIs and fair access. Fetch the official pages: https://www.sec.gov/search-filings/edgar-application-programming-interfaces (EDGAR APIs), https://www.sec.gov/os/accessing-edgar-data and https://www.sec.gov/about/developer-resources (fair access, User-Agent, rate limit), https://www.sec.gov/files/company_tickers.json (format only — do a single request with a User-Agent of the form "App Creator research contact-not-included" ONLY if needed; better: describe from documentation). Answer precisely: endpoints for submissions (CIK##########.json), the "filings.files" older-submissions pagination, companyfacts, companyconcept, frames; field names (accn, fy, fp, form, filed, frame, start, end, val, units); the ticker file(s) (company_tickers.json, company_tickers_exchange.json) and where documented; EDGAR archive URL structure (Archives/edgar/data/<cik>/<accession-no-dashes>/<primaryDocument>, index.json); the hosts (www.sec.gov, data.sec.gov); required User-Agent declaration format; the 10 requests/second limit and what happens when exceeded (403 / temporary block); CORS (data.sec.gov does not support browser calls?) and caching guidance; how frequently submissions/companyfacts update. Also note what "frame" means and why fy/fp are filing-level not period-level (cite the API page text if present).
Rules: use only official documentation (fetch the pages; do not answer from memory), cite every claim with its URL and the retrieval date 2026-11-03, and mark anything you could not fetch as [unverified]. Write ONLY the one file named below (create docs/research/ if needed); do not edit any other file, do not install anything, do not commit. Keep the file under about 1300 words, as practical implementation notes. Never print or write secrets or email addresses. End your final message with:
## Handoff
Changes: <file written>
Verification evidence: <pages fetched (URLs) and any failures>
Remaining findings: <surprises, contradictions with the notes in PROGRESS.md decisions D5/D6>
Next action: <one line>
File: docs/research/sec-edgar.md

<!-- DISPATCH:END -->
