# SEC Analytics (example app)

SEC Analytics is the worked example of App Creator: a dark, terminal-style web app for reading public company data
from the SEC (U.S. Securities and Exchange Commission). It runs on recorded SEC data offline, and on live SEC data when you choose.

- Code: `frontend/` (Next.js) and `backend/` (FastAPI).
- Planning documents: `milestones/` at the repository root (product, architecture, acceptance, plan).
- Rules for working in this folder: [CLAUDE.md](CLAUDE.md).

## What it does

Search by name, ticker or CIK; a company profile; key figures; an annual revenue and net income chart; **normalized annual
summaries** of the income statement, balance sheet and cash flow; ratios; and a metric explorer. Hovering or focusing a value
shows the SEC fact it came from, or its formula and inputs. A value that is not available says so and why; it is never 0.

**Filings** (M3): the latest 10-K and 10-Q, a 10-year filing history with amendment labels, and a reader with the filing's own
text, detected sections, search and links to sec.gov. **Compare** (M4, header link): 2–4 companies side by side by their own
fiscal years, with an optional "Index = 100 at first common fiscal year" for amounts, line and bar charts, and Export CSV. The
comparison state is in the URL, so a link shows the same comparison.

These summaries are built from SEC Company Facts. They are not the complete filed statements. Metric ids, concepts and
formulas are in `backend/app/logic/concepts.py` and `metrics.py`; the selection policy is in `logic/periods.py`.

**Demo and Live.** `npm run demo` is offline, on Apple, Microsoft and Alphabet only: any other company gives "No match in the
demo universe (3 companies)". `npm run dev` adds a Demo / Live selector that starts on Demo. Live search covers SEC filers
listed in the SEC ticker file, and other filers can be opened by CIK. It does not cover non-SEC companies. Setup, your contact
setting and the smoke check are in [docs/SETUP.md](../../docs/SETUP.md).

## Run it (from the repository root)

```bash
npm ci           # once: the launcher's lockfile
npm run setup    # once: backend and frontend packages, project-local browser
npm run demo     # offline demo on recorded data: http://127.0.0.1:3000
npm run dev      # the same, with the Demo / Live selector
npm run verify   # every check, no network needed
```

Ports 3000 and 8000 are refused if something else uses them. Choose others, for example
`FRONTEND_PORT=3200 BACKEND_PORT=8200 npm run demo`, then open http://127.0.0.1:3200.

## Where the data comes from

[`fixtures/`](fixtures/README.md) holds trimmed but unmodified SEC data retrieved on 2026-11-03. Its `manifest.json`
records each file's source URL, retrieval time, hash, accession numbers, periods and scope. Values may reflect later
restatements; they are not point-in-time. The data is a snapshot: never read it as the current latest filing.

**Recapturing** changes every number, so the known answers in `milestones/acceptance.md` must be worked by hand again.
It needs your own `SEC_USER_AGENT` (a descriptive name plus your own contact email; see the root `.env.example`):

```bash
cd examples/sec-analytics/backend
.venv/bin/python scripts/capture_fixtures.py   # Windows: .venv\Scripts\python scripts\capture_fixtures.py
```

**Classroom note.** SEC's fair-access limit applies across everyone sharing one public address, so a class uses Demo by
default. Do not have every student recapture or use Live at once.
