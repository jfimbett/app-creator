# SEC Analytics (example app)

SEC Analytics is the worked example of App Creator: a dark, terminal-style web app for reading public company data
from the SEC (U.S. Securities and Exchange Commission). At milestone M1 it runs offline only, on recorded SEC data.

- Code: `frontend/` (Next.js) and `backend/` (FastAPI).
- Planning documents: `milestones/` at the repository root (product, architecture, acceptance, plan).
- Rules for working in this folder: [CLAUDE.md](CLAUDE.md).

## What M1 does

Search by name, ticker or CIK, a company profile, key figures, and an annual revenue and net income chart with a
data table. Hovering a value shows the SEC filing it came from.

**Demo universe.** Search covers Apple, Microsoft and Alphabet only, the companies in the recorded snapshot. Any other
company gives "No match in the demo universe (3 companies)". There is no live SEC lookup at M1.

## Run it (from the repository root)

```bash
npm ci           # once: the launcher's lockfile
npm run setup    # once: backend and frontend packages, project-local browser
npm run demo     # offline demo on recorded data: http://127.0.0.1:3000
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

**Classroom note.** SEC's fair-access limit applies across everyone sharing one public address, so a class uses the
recorded data. Do not have every student recapture.
