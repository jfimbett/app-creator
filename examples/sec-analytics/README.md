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

**Landing page, themes and video** (M6): `/` is a landing page that explains the product (its testimonials, pricing and
company story are fictional or illustrative and say so on the page; there are no accounts or payments). The app itself is at
`/app`. Every header has a sun/moon button that switches between the dark and light themes; the choice is remembered in this
browser (`localStorage`, key `sec-analytics.theme`, display preference only). A 22-second launch video made with the
`/brag` skill is in [brag-output/brag.mp4](brag-output/brag.mp4), with its plan and share text.

## Run it (from the repository root)

```bash
npm ci           # once: the launcher's lockfile
npm run setup    # once: backend and frontend packages, project-local browser
npm run demo     # offline demo on recorded data: http://127.0.0.1:3000 (landing), /app (the app)
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

## Optional AI analyst (M5)

The company page, the filing reader and Compare have an **Analyst** button. It answers questions about the data on screen
using a model you choose on [OpenRouter](https://openrouter.ai), and cites its sources as numbered chips. Everything else
in the app works without it.

**Your own key.** Open Analyst → **AI settings** and paste your own OpenRouter key. Use a key with a **credit limit**; your
instructor may give you a limited key for your group. This is separate from any model your coding assistant (Claude Code
or Cline) uses: nothing here reads or changes their settings, and their settings do not give this app a key.

**Where the key is kept.** By default only in the page's memory: a reload forgets it. If you tick "Remember for this tab
(sessionStorage)", it stays until you close the tab. Scripts on this page can read browser storage, so this is **not
secure storage**. The key is never written to localStorage, cookies, the URL or any file, and the backend never stores
or logs it: it forwards it for that one request.

**Costs.** Questions are paid from your key's credit at the model's price, shown per million tokens in the model list.
"Test connection" asks OpenRouter about your key and may incur a small charge. The app never retries a failed call, so a
failure does not cost twice. There is no default model: you choose one.

**What the answer is.** The model sees only the app's own numbers (the latest five fiscal years) and passages of the
filing, with ids like `[F2]` and `[P1]`. The app checks that every cited id was really supplied. **A valid source chip
means the source exists, not that the sentence is true**: read the source. The analyst refuses price forecasts,
valuations, investment advice and companies that are not open.

**For instructors: one limited key per student or group.** In the OpenRouter dashboard, create a key per student or group
with a credit limit and an expiry; or create them with the management API (`POST /api/v1/keys` with `limit`,
`limit_reset` and `expires_at`, using a separate management key, which cannot call models). Never hand out one
unrestricted shared key. Extra keys do not raise the rate limits of free models.

**Local only.** The AI endpoints accept requests only from this app's own pages on 127.0.0.1 or localhost. This is a local
teaching app, not a public AI proxy: do not expose the backend to a network.
