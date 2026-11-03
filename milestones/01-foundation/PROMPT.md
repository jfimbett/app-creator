# M1 Foundation: build brief

This is the exact implementation brief for SEC Analytics milestone 01. Give it, unchanged, to the assistant or agent
that implements the milestone. It is immutable once the `template-v1` checkpoint exists. Corrections that change
the implementation go into [FOLLOWUPS.md](FOLLOWUPS.md) before they are dispatched.

Paths are relative to the repository root unless stated. `fe/` means `examples/sec-analytics/frontend/` and `be/`
means `examples/sec-analytics/backend/`.

---

## 1. Starting ref

- **Start from tag `template-v1`.** It holds the generic App Creator toolkit, the planning documents in `milestones/`
  and these five prompts. It contains no SEC application.
- A student rebuilding this milestone, in a **clean checkout** (`git status` shows nothing to commit):

  ```bash
  git fetch origin --tags
  git switch -c exercise/build-m1 template-v1
  npm ci
  npm run setup
  ```

- Check the start before you change anything: `git describe --tags --exact-match HEAD` prints `template-v1`
  (or `git merge-base --is-ancestor template-v1 HEAD` exits 0 on a new branch with no commits yet), and
  `app-creator.config.json` has `"app": null`.
- The completed `m1` tag is **for inspection** (`git switch --detach m1`). Do not run this prompt on an `m1`
  checkout: that work is already done there. Replaying the prompt will not produce identical code; the `m1` tag is
  the reference version.

## 2. Context: what exists at `template-v1`

- **Generic toolkit.** `AGENTS.md`, `CLAUDE.md`, `.claude/skills/` (index: `.claude/skills/INDEX.md`),
  `.claude/agents/`, `.claude/settings.json`, `.clinerules/`, `docs/TOOLKIT.md` (conventions, root-command contract,
  Handoff block), `docs/research/` (SEC EDGAR, OpenRouter, stack versions), `runs/` (step records).
- **Root launchers** (`scripts/`, Node built-ins only), run from the repository root:
  `npm run setup | dev | demo | verify | create-app | check-toolkit`. They read `app-creator.config.json`. With
  `"app": null` they only check versions. `verify` runs the toolkit checks, then for the configured app: backend
  `ruff check .` and `pytest -q`, frontend `lint`, `typecheck`, `test` (Vitest), a production build into
  `.next-verify`, then backend and `next start` on spare ports with `demoEnv` applied and Playwright
  (`smokeSpec`, default `e2e`). Only `npm run dev` (and `setup`) pass the optional root `.env` to the processes they
  start, without printing it; `npm run verify` and `npm run demo` pass only the shell's environment plus `demoEnv`
  (docs/TOOLKIT.md §3), so tests and the demo never see local settings. The backend binds to 127.0.0.1.
- **Scaffold** (`scaffold/`): Next.js 16.4.2 App Router, React 19.3.1, TypeScript 6.0.3, Tailwind CSS 4.3.3,
  Vitest 5.0.5, Playwright 1.64.1 (`frontend/`); FastAPI 0.150.0, uvicorn, httpx 0.28.1, pydantic 2.14.1, pytest,
  ruff, respx (`backend/`, pinned in `requirements.lock`). `frontend/next.config.ts` rewrites `/api/*` to
  `BACKEND_URL` (same-origin calls; no `app/api` route handlers may exist, they would shadow the rewrite).
  `GET /api/health` returns `{status, app}`. A Playwright smoke spec takes screenshots at 1366×900 and 390×844.
- **`npm run create-app -- --dir <path> --name "<App name>"`** copies `scaffold/` to `<path>`, writes
  `<path>/docs/README.md`, replaces the name in `frontend/lib/site.ts` and `backend/app/main.py`, and sets `"app"` in
  `app-creator.config.json` (`frontendDir`, `backendDir`, `docsDir: <path>/docs`, `devEnv: {}`, `demoEnv: {}`). It
  refuses to overwrite.
- **Planning documents (agreed under delegation, 2026-11-03):** [GOAL.md](../../GOAL.md) (§4–§9),
  [docs/PRODUCT-DECISIONS.md](../../docs/PRODUCT-DECISIONS.md) (Q1–Q44, N1–N3),
  [milestones/product.md](../product.md), [milestones/architecture.md](../architecture.md),
  [milestones/acceptance.md](../acceptance.md), [milestones/plan.md](../plan.md) (slices 1.1–1.6),
  [docs/research/sec-edgar.md](../../docs/research/sec-edgar.md),
  [docs/research/stack-versions.md](../../docs/research/stack-versions.md).
- Nothing in `examples/` exists yet.

## 3. Goal and new work

Deliver a polished, offline SEC Analytics foundation (GOAL.md §5, row 01): a dark terminal shell; company search
by name, ticker or normalized CIK over the **demo universe** (Apple, Microsoft, Alphabet); a profile with the SEC
identifiers; a basic interactive dashboard built **only** from explicitly labelled, authentic recorded SEC data;
stable launch scripts; and a meaningful browser smoke test. M1 is **demo-only**: there is no live mode, no mode
selector and no SEC request from the running app.

Concretely:

1. **Example skeleton.** Run `npm run create-app -- --name "SEC Analytics" --dir examples/sec-analytics`. Then edit
   `app-creator.config.json` so `"app"` is:
   `{"name": "SEC Analytics", "frontendDir": "examples/sec-analytics/frontend", "backendDir":
   "examples/sec-analytics/backend", "docsDir": "milestones", "backendApp": "app.main:app", "healthPath":
   "/api/health", "ports": {"backend": 8000, "frontend": 3000}, "devEnv": {"DATA_MODE": "fixtures"}, "demoEnv":
   {"DATA_MODE": "fixtures"}, "smokeSpec": "e2e"}`. (`devEnv` becomes `{"DATA_MODE": "live"}` in M2, when live mode
   exists. At M1 both commands run fixtures.) Keep `$comment` unchanged. Delete the generated
   `examples/sec-analytics/docs/` folder: the docs of this example live in `milestones/` (PROGRESS.md D8). Run
   `npm run setup`.
2. **Authentic fixtures** for AAPL, MSFT and GOOGL, built by a reproducible script (section 6).
3. **Backend API** for meta, search, profile and overview (section 5), with one error envelope.
4. **Search:** `/` and Ctrl/Cmd-K focus the header search; typing shows matches; ↑/↓ move, Enter opens, Esc closes
   (accessible combobox). Name (case-insensitive substring), ticker (exact first, then prefix) and CIK (any
   zero-padding, 1–10 digits, normalized to 10) all work. Under the search, always visible on the home page:
   "Search covers the demo companies only: Apple, Microsoft, Alphabet". A miss shows "No match in the demo universe
   (3 companies)".
5. **Company page** `/companies/[cik]`: profile and identifiers exactly as in the fixture submissions file (name,
   tickers, exchanges, 10-digit CIK, SIC code and description, fiscal year-end as `MM-DD`, state of incorporation,
   former names with dates). Missing fields show "Not reported by SEC". No company description, logo, website
   blurb or price: none of these are in the data.
6. **Basic dashboard** on the company page: a key-figure strip with latest annual revenue and latest annual net
   income (reported values only), each with fiscal year-end, unit and a provenance tooltip; a line chart "Revenue
   and net income, USD, by fiscal year" with hover tooltips and series toggles (Revenue / Net income), a selector
   for "Last 5 years / All in snapshot", and a compact data table with the same values under the chart. Every panel
   carries `RECORDED SEC DEMO · snapshot <manifest snapshot_date>`. Hovering or focusing a value shows its concept,
   taxonomy, unit, period start–end, form, accession and filing date. The note "Values may reflect later
   restatements; not point-in-time." sits under the chart.
7. **States:** loading skeleton rows (not spinners on blank pages); empty search; no match; company not in the demo
   snapshot (404); invalid CIK (422 with "A CIK has up to 10 digits"); backend down ("Backend not reachable: start
   it with npm run demo", no stack trace); a value missing for a year (`MISSING · <reason>`).
8. **Example-specific rules and help for assistants:** `examples/sec-analytics/CLAUDE.md`, the nested skill
   `examples/sec-analytics/.claude/skills/sec-edgar-data/SKILL.md` and the example agent
   `.claude/agents/sec-data-specialist.md` (section 5).
9. **Browser smoke journey** and screenshots (section 9), replacing the scaffold's smoke spec.

SEC correctness that applies at M1 (GOAL.md §6), written out in section 7: backend-only SEC access (the capture
script only), declared User-Agent from the person's own configuration, allowlisted hosts and paths, conservative
throttle, CIK normalization, period identification by `start`/`end`, annual 10-K facts only, the deterministic
duplicate policy, provenance for every number, missing is null.

## 4. Design

The look is a modern, Bloomberg-inspired **dark navy terminal**: dense and calm, built for reading numbers.

- **Theme tokens** in `fe/app/globals.css` as CSS variables, used through Tailwind (`bg-[var(--panel)]` or
  `@theme` tokens). Defaults: background `#0A1020`, panel `#0F1A2E`, raised panel `#14223B`, border `#1F2E4A`, text
  `#DCE3EE`, muted text `#8C9AB3`, accent amber `#F2B33D` (focus rings, active tab, selected row), link `#6CB6FF`,
  positive `#3FB68B`, negative `#F0605D`, warning `#E8A33A`. Any change must keep text contrast at or above 4.5:1.
  Dark is the default and the done criterion. Light mode is secondary and **not** part of M1 (tokens make it cheap
  later).
- **Type:** system UI sans-serif for text and a system monospace stack for codes (CIK, accession). All numbers use
  `font-variant-numeric: tabular-nums` and are right-aligned. Base 14 px, table text 13 px, labels 11–12 px
  uppercase with letter spacing. **No web-font downloads** (`next/font/google` or CDN fonts would need the network).
- **Layout:** a compact header (wordmark "SEC ANALYTICS", search box with a `/` hint, the mode badge
  `RECORDED SEC DEMO`, backend status). No sidebar or menu items at M1: there are no other screens. Panels are
  bordered rectangles with a small uppercase title row and their source badge at the right; 8 px spacing grid; no
  decorative card grids, gradients, hero images or stock icons.
- **Tables:** dense rows (28–32 px), sticky header row, first column sticky when a table scrolls sideways, thin
  row separators, units in the column header ("USD millions"), negative numbers with a true minus sign (−).
- **Numbers:** money from the API is in whole currency units; the UI shows millions with thousands separators
  (`1,234,567` under "USD millions") and the exact value in the tooltip (`1,234,567,000,000 USD`). Missing values show
  `—` plus a text badge `MISSING · <reason>`, never 0 and never a blank cell without explanation.
- **Source badges** are text, never colour alone: `RECORDED SEC DEMO · snapshot <date>` (M1 has only this one and
  `MISSING · <reason>`). The header badge shows the mode for the whole app.
- **Charts** (Recharts 3.10.1, client components): line chart for trends, zero baseline always visible, negative
  values below it, a missing year is a gap (`connectNulls={false}`), never a zero. Axis labels state the unit.
  Tooltips show fiscal year label, period end date, value and unit. Colours: revenue `#6CB6FF`, net income
  `#F2B33D`; the series are also distinguished by name in the legend and tooltip.
- **Keyboard and accessibility:** visible focus ring (amber), every control reachable by Tab, combobox ARIA
  (`role="combobox"`, `aria-expanded`, `aria-controls`, `aria-activedescendant`, `role="listbox"`/`option`),
  tooltips also open on focus, `aria-live="polite"` for result counts and status changes.
- **Responsive:** check at 1440, 1366 and 390 px wide. At 390 px the page never scrolls sideways; wide tables
  scroll inside their own container; the header search stays usable (it may take the full width below the
  wordmark); the chart keeps readable axis labels.
- **Honesty rules:** no invented company descriptions, logos, prices or market data; no nonfunctional buttons; no
  navigation to features of later milestones (no "Filings", "Compare", "Analyst", no disabled placeholders).

## 5. Architecture and files

Follow [milestones/architecture.md](../architecture.md). Layers: UI (`fe/app/`, `fe/components/`) shows values it
receives; frontend helpers (`fe/lib/`) are a typed `/api` client and display formatting; API (`be/app/api/`)
validates and maps errors; logic (`be/app/logic/`) is pure (no files, network or clock: the current time is passed
in); data access (`be/app/data/`) reads fixtures; the SEC client (`be/app/clients/sec.py`) is used only by the
capture script at M1. The browser calls only same-origin `/api/*` (Next.js rewrite). No route handlers under
`fe/app/api/`.

**Files to create or change** (one line each; you may add small helper files inside the same folders):

| Path | Purpose |
|---|---|
| `app-creator.config.json` | `"app"` entry as in section 3 |
| `.env.example` (root) | add, commented with placeholders and one-line explanations: `DATA_MODE=fixtures`, `FIXTURES_DIR=` (empty means `examples/sec-analytics/fixtures`), `SEC_USER_AGENT=` with the comment "Your app name and your own contact email, e.g. `<app name> <your contact email>`. Needed only to capture fixtures (and for live mode from M2). Never commit it." No real or example address. |
| `examples/sec-analytics/README.md` | replace the copied scaffold README: what the example is, the demo universe, how to run (`npm run demo`), where fixtures come from, how to recapture them, milestone status M1 |
| `examples/sec-analytics/CLAUDE.md` | SEC/finance working rules for this folder (below) |
| `examples/sec-analytics/.claude/skills/sec-edgar-data/SKILL.md` | example-specific skill (below) |
| `.claude/agents/sec-data-specialist.md` | example-only agent (below). The only toolkit file this milestone may add; do not edit other `.claude/`, `scripts/`, `scaffold/` files, `AGENTS.md`, root `CLAUDE.md` or `docs/TOOLKIT.md` |
| `examples/sec-analytics/fixtures/` | recorded data, manifest, `README.md`, `.gitattributes` (section 6) |
| `be/app/main.py` | app factory: routers, error handlers, `APP_NAME = "SEC Analytics"`; keeps `GET /api/health` |
| `be/app/settings.py` | settings from the environment, validated with a pydantic model (no new package): `DATA_MODE` (`fixtures` only accepted at M1; anything else → startup error naming the setting), `FIXTURES_DIR` |
| `be/app/errors.py` | `AppError(code, message, status, details)`, handlers for `AppError`, `RequestValidationError` (→ 422 with a specific code) and unexpected exceptions (→ 500 `internal_error`, generic message, `reference` id; detail only in the log) |
| `be/app/models/common.py` | `SourceInfo`, `Provenance`, `MetricValue`, `ErrorEnvelope` exactly as in architecture.md "API" |
| `be/app/models/companies.py` | `MetaResponse`, `SearchResponse`, `CompanyProfile`, `OverviewResponse` |
| `be/app/api/meta.py`, `be/app/api/companies.py` | endpoints below |
| `be/app/logic/cik.py` | `normalize_cik(text) -> str` (strip, optional `CIK` prefix, 1–10 digits, zero-pad; else `InvalidCik`) |
| `be/app/logic/search.py` | `search(query, universe, limit) -> list[Match]` (ranking below) |
| `be/app/logic/concepts.py` | concept constants: the revenue priority list, `NetIncomeLoss`, and `CAPTURE_CONCEPTS` (section 6) |
| `be/app/logic/periods.py` | first version: annual-duration selection and the duplicate policy (section 7) |
| `be/app/logic/statements.py` | `overview(facts, profile, years) -> Overview`: key figures and chart rows for revenue and net income |
| `be/app/data/fixtures.py` | load `manifest.json` and the fixture files; build `SourceInfo`; refuse a manifest marked synthetic from being labelled as SEC data (label it `SYNTHETIC TEST DATA` instead) |
| `be/app/clients/sec.py` | minimal SEC client used by the capture script: allowlist, User-Agent, throttle, timeout, Retry-After, no retry on 403, manual redirects (section 7). Not imported by the running app at M1 |
| `be/scripts/capture_fixtures.py` | fixture builder (section 6) |
| `be/tests/...` | tests in section 9; `be/tests/synthetic/` for synthetic inputs |
| `fe/package.json`, `fe/package-lock.json` | add exact `recharts` 3.10.1 and `react-is` 19.3.1 (`npm install --save-exact` inside `fe/`) |
| `fe/app/layout.tsx`, `fe/app/globals.css` | shell, tokens, header |
| `fe/app/page.tsx` | home: search, demo-universe note, the three demo companies as a plain list of links (name · ticker · CIK) |
| `fe/app/companies/[cik]/page.tsx` | profile and dashboard (client component fetching `/api`) |
| `fe/app/not-found.tsx`, `fe/app/error.tsx` | friendly 404 and error states |
| `fe/components/` | `AppHeader`, `CompanySearch` (combobox), `SourceBadge`, `BackendStatus` (reuse `lib/health.ts`), `CompanyProfile`, `KeyFigures`, `RevenueIncomeChart`, `ProvenanceTip`, `StatePanel` (loading / empty / missing / error with a next step) |
| `fe/lib/api.ts`, `fe/lib/types.ts` | typed client and TypeScript mirrors of the pydantic models; one `ApiError` carrying the envelope |
| `fe/lib/format.ts` | display formatting of finished values (millions, minus sign, dates, `—`) |
| `fe/lib/combobox.ts`, `fe/lib/shortcuts.ts` | pure keyboard logic (testable with Vitest): active-index reducer, `/` and Ctrl/Cmd-K handling that ignores keystrokes while typing in other inputs |
| `fe/e2e/m1-foundation.spec.ts` | the M1 journey; delete `fe/e2e/smoke.spec.ts` (its health check moves into this spec) |
| `milestones/acceptance.md`, `milestones/plan.md`, `milestones/architecture.md` | statuses, progress log, fixture known-answer rows, decision-log rows only |
| `AI-USAGE.md` | one entry for this milestone's meaningful AI assistance |

**API at M1** (all under `/api`, JSON, error envelope `{"error": {"code", "message", "details", "reference"}}`):

| Method and path | Request | Response | Errors |
|---|---|---|---|
| `GET /api/health` | – | `{status: "ok", app: "SEC Analytics"}` | – |
| `GET /api/meta` | – | `{data_mode: "fixtures", live_available: false, live_configured: false, snapshot_date: date, demo_universe: [{cik, ticker, name}]}` | – |
| `GET /api/companies/search` | `q` (1–100 chars after trim), `limit` (1–20, default 10) | `{query, results: [{cik, ticker, name, match: "ticker"\|"name"\|"cik"}], universe_note: "Search covers the demo companies only: Apple, Microsoft, Alphabet", source: SourceInfo}` | 422 `invalid_query` |
| `GET /api/companies/{cik}` | `cik` 1–10 digits (optional `CIK` prefix), padded to 10 | `CompanyProfile {cik, name, tickers: [str], exchanges: [str], sic: str\|null, sic_description: str\|null, fiscal_year_end: "MMDD"\|null, state_of_incorporation: str\|null, former_names: [{name, from, to}], source: SourceInfo}` | 422 `invalid_cik` ("A CIK has up to 10 digits"), 404 `company_not_found` ("not in the demo snapshot") |
| `GET /api/companies/{cik}/overview` | `cik`; `years` (1–20, default: all in snapshot) | `{cik, key_figures: [MetricValue], chart: [{fiscal_year_label, period_end, revenue: MetricValue, net_income: MetricValue}], notes: [str], source: SourceInfo}` | as above |

`SourceInfo` in M1 is always `{mode: "demo", label: "RECORDED SEC DEMO · snapshot <date>", retrieved_at: null,
snapshot_date, source_urls: [the original SEC URLs of the fixture files used]}`. `MetricValue.kind` is `reported`
for every M1 value; `status` is `ok` or `missing` (with `reason`). Money values are whole currency units (USD), not
millions.

**`examples/sec-analytics/CLAUDE.md`** (short, imperative; loaded by Claude Code the first time it reads or edits a
file in this folder): data sources and hosts; never call SEC from the browser; the User-Agent comes only from
`SEC_USER_AGENT` in the person's own environment or ignored root `.env`, never invented, printed, logged or committed;
the throttle and allowlist; fixtures are authentic and only changed by `be/scripts/capture_fixtures.py`, synthetic
data only in `be/tests/synthetic/` marked `SYNTHETIC`; period rules (start/end, never group by `fy`, annual =
350–380 days, 10-K/10-K/A only, duplicate policy); missing is null never zero; reported vs derived with provenance;
no market prices, valuation metrics, currency conversion or invented descriptions; where the planning docs are
(`milestones/*.md`); the nested skill; and the note that **Cline does not load nested CLAUDE.md or nested skills
automatically**, so Cline users open these two files themselves.

**Nested skill `sec-edgar-data`** (`examples/sec-analytics/.claude/skills/sec-edgar-data/SKILL.md`): frontmatter
`name: sec-edgar-data` and a `description` that starts "SEC Analytics example only:" and says when to use it (SEC
fetches, fixtures, Company Facts mapping, periods, ratios, filing text in `examples/sec-analytics/`). Body in the
toolkit's shape: inputs, actions (how to add a concept, recapture fixtures, add a known-answer test), outputs,
verification, stop when (no `SEC_USER_AGENT`, SEC 403, a mapping that cannot be verified against fixtures), common
mistakes (grouping by `fy`, summing duplicates, zero for missing, YTD in annual). Record in the skill and in
`examples/sec-analytics/CLAUDE.md` that, per [docs/research/claude-code-and-cline.md](../../docs/research/claude-code-and-cline.md),
a `.claude/skills/` folder **below** the session's start directory is not loaded at startup; Claude Code loads it
the first time it reads or edits a file in that subfolder, and it is then addressed as
`examples/sec-analytics:sec-edgar-data`. Add a decision-log row to `milestones/architecture.md` saying the same.

**Example agent `sec-data-specialist`** (`.claude/agents/sec-data-specialist.md`): frontmatter `name:
sec-data-specialist`, a `description` beginning "For the SEC Analytics example only (examples/sec-analytics):"
covering SEC client, fixtures, concept mapping, periods and ratio logic; `tools: Read, Grep, Glob, Edit, Write,
Bash, Skill`; body: read `examples/sec-analytics/CLAUDE.md` and the nested skill first, never touch `.env`, end with
the Handoff block. It must pass `npm run check-toolkit` (name equals file name).

## 6. Fixtures and data

**Goal:** compact, authentic SEC snapshots for Apple (CIK 0000320193), Microsoft (0000789019) and Alphabet
(0001652044), with at least 5 annual periods each, and a manifest
(the script resolves the tickers AAPL, MSFT and GOOGL to CIKs from the downloaded `company_tickers.json` and stops
with an error if they differ from these expected values, instead of trusting this list) that lets anyone check where every file came
from. Never manufacture values. Never label synthetic data as SEC data.

**The builder** `be/scripts/capture_fixtures.py`, run from `be/` with the backend's own Python
(`.venv/bin/python scripts/capture_fixtures.py` on macOS/Linux, `.venv\Scripts\python.exe scripts\capture_fixtures.py`
on Windows):

- **User-Agent:** reads `SEC_USER_AGENT` from the process environment, or else from the repository-root `.env`
  (the script parses only that key, like the root launchers). The value must be a descriptive app or person name
  plus the person's own genuine contact email. It is configured by that person only. The script checks the shape
  (two or more words, one of which looks like an email address, no line breaks), prints only
  `SEC_USER_AGENT: set (value hidden)`, never writes it to any file, the manifest or a log, and never invents a
  fallback. If it is missing or malformed, the script exits with code 2 and a message naming the setting and
  `.env.example`. **You (the assistant) never read, print or edit `.env`**; you only run the script.
- **Requests** go through `app/clients/sec.py` (allowlist, ≤ 1 request per second, one in flight, 20 s timeout,
  Retry-After, no retry on 403). Exactly 7 requests: `https://www.sec.gov/files/company_tickers.json`, then
  `https://data.sec.gov/submissions/CIK##########.json` and
  `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` for each company. No bulk archives, no frames, no
  crawling, no older submissions pages at M1.
- **What is kept** (Q20). Values are never edited, rounded or reordered within a fact:
  - `fixtures/company_tickers.json`: the entries of the original object whose `cik_str` is one of the three CIKs
    (this includes both `GOOGL` and `GOOG` for Alphabet), with their original keys and fields.
  - `fixtures/submissions/CIK##########.json`: every top-level field except `filings` unchanged;
    `filings.recent` keeps only the rows whose `form` is `10-K`, `10-K/A`, `10-Q` or `10-Q/A`, with **all** columns
    kept and row-aligned; `filings.files` kept unchanged (the pages themselves are not downloaded; record that).
  - `fixtures/companyfacts/CIK##########.json`: `cik`, `entityName` and, under `facts.us-gaap`, only the concepts
    in `CAPTURE_CONCEPTS`, each with its `label`, `description` and complete `units` arrays (every fact for that
    concept, every form, unmodified). Concepts absent for a company are listed in the manifest, not invented.
  - `CAPTURE_CONCEPTS` (in `app/logic/concepts.py`, so M2 can map without recapturing): `Revenues`,
    `RevenueFromContractWithCustomerExcludingAssessedTax`, `SalesRevenueNet`,
    `RevenueFromContractWithCustomerIncludingAssessedTax`, `OperatingIncomeLoss`, `NetIncomeLoss`,
    `IncomeTaxExpenseBenefit`, `InterestExpense`, `InterestExpenseNonoperating`, `InterestExpenseDebt`,
    `DepreciationDepletionAndAmortization`, `DepreciationAndAmortization`, `DepreciationAmortizationAndAccretionNet`,
    `NetCashProvidedByUsedInOperatingActivities`, `PaymentsToAcquirePropertyPlantAndEquipment`, `Assets`,
    `AssetsCurrent`, `Liabilities`, `LiabilitiesCurrent`, `StockholdersEquity`, `LongTermDebtNoncurrent`,
    `LongTermDebtCurrent`, `CommercialPaper`, `ShortTermBorrowings`.
- JSON is written UTF-8 with `indent=1` and `ensure_ascii=False`. Add `fixtures/.gitattributes` with `* -text` so
  Git never rewrites line endings (the manifest hashes must match on Windows too).
- **`fixtures/manifest.json`:** `{schema_version: 1, label: "RECORDED SEC DEMO", synthetic: false, snapshot_date:
  "<UTC date of the run>", captured_with: "be/scripts/capture_fixtures.py", user_agent: "configured locally; not
  recorded", files: [...]}`. Each file entry: `path` (relative to `fixtures/`), `kind`
  (`company_tickers`/`submissions`/`companyfacts`), `cik` (when relevant), `source_url`, `retrieved_at` (UTC
  ISO 8601), `sha256` and `bytes` of the written file, `accessions` (distinct accession numbers in the kept data),
  `periods` (for companyfacts: the annual 10-K period end dates found for revenue and net income, earliest and
  latest; for submissions: earliest and latest `filingDate` kept), `scope` (one sentence: what was kept) and
  `trimmed` (one sentence: what was removed and why, e.g. "other forms' rows removed from filings.recent;
  filings.files pages not downloaded").
- `fixtures/README.md`: provenance in plain words, the snapshot date, how to recapture, and the warning that a
  recapture changes every number and needs new hand-worked known answers.
- **If retrieval is blocked** (no `SEC_USER_AGENT` in the environment, no network, SEC 403 or repeated 429/503):
  stop the capture, do not create partial fixtures that look complete, record the blocker (N2) with the exact
  command, exit code and message in the Handoff, and continue the work that does not depend on fixtures (logic
  with synthetic tests, the shell, the skill files). The milestone gate cannot pass without authentic fixtures;
  say so.
- **Synthetic test data** lives only in `be/tests/synthetic/`. Each file says `SYNTHETIC: invented for tests, not
  SEC data` (a `"_synthetic"` key in JSON, a comment elsewhere), and `be/tests/synthetic/README.md` explains this.
  The running app never reads that folder. A synthetic fixtures tree for API tests has a manifest with
  `"synthetic": true` and is labelled `SYNTHETIC TEST DATA` by `data/fixtures.py`.
- **Known answers from the fixtures:** after capture, open the fixture JSON yourself (not the app's output) and add
  rows `FX1`–`FX4` to `milestones/acceptance.md` under the calculations section: Apple's latest annual revenue and
  net income, and Microsoft's latest annual revenue, each quoting concept, unit, start, end, form, accession, filed
  date and `val`. Add them **before** writing the tests that use them.

## 7. SEC rules that apply at M1

- **Backend only.** The browser never calls `sec.gov` (data.sec.gov has no CORS support). At M1 even the backend
  makes no SEC request while serving: only the capture script does.
- **Allowlist** (`clients/sec.py`): `https://data.sec.gov` paths `^/submissions/CIK\d{10}\.json$`,
  `^/submissions/CIK\d{10}-submissions-\d{3}\.json$`, `^/api/xbrl/companyfacts/CIK\d{10}\.json$`;
  `https://www.sec.gov` paths `^/files/company_tickers\.json$` and
  `^/Archives/edgar/data/\d+/\d{18}/[A-Za-z0-9._-]+$`. HTTPS only, no userinfo, no non-default port, no query
  string. URLs are built from validated parts (normalized CIK), never taken from a caller. Redirects are not
  followed automatically: at most 3, each target checked against the allowlist before any request; otherwise
  `UpstreamNotAllowed`. This is not an arbitrary URL proxy.
- **Fair access:** declared User-Agent from configuration (above), plus `Accept-Encoding: gzip, deflate`. At most
  1 request per second per running process (`SEC_MAX_REQUESTS_PER_SECOND` arrives in M2; at M1 a constant), one
  request in flight, no prefetching. SEC's limit is 10 requests per second **for all machines together**, so a
  classroom on one public IP must use fixtures; put that note in `examples/sec-analytics/README.md`.
- **Failures:** 20 s timeout; on 429 or 503 wait for `Retry-After` (seconds or HTTP date, capped at 30 s; default
  backoff 2 s then 4 s) and retry at most twice; on 403 never retry and report "SEC refused the request (403)". Never
  disguise traffic, rotate agents or otherwise bypass a refusal.
- **CIK:** strip spaces and an optional `CIK` prefix; 1–10 digits; pad to 10 for data.sec.gov; reject anything else
  (`abc`, 11 digits, negative, empty).
- **Periods** (first version in `logic/periods.py`, used for the dashboard):
  - Identify a period by `start`/`end`. Never group facts by `fy` or `fp`: those describe the filing that reported
    the value, and later 10-Ks repeat earlier periods as comparatives.
  - Annual series use duration facts lasting 350–380 days inclusive (`end − start`), so 52/53-week years count;
    quarterly and year-to-date durations are excluded.
  - Only facts with `form` `10-K` or `10-K/A` feed annual series.
  - Duplicates: group by (concept, unit, start, end); keep the fact with the latest `filed`; on a tie the higher
    accession number; never sum. Keep the chosen fact as provenance.
  - Revenue: per period, the first concept present in the priority order `Revenues`,
    `RevenueFromContractWithCustomerExcludingAssessedTax`, `SalesRevenueNet`,
    `RevenueFromContractWithCustomerIncludingAssessedTax`; never summed across concepts; the concept used is in the
    provenance. Net income: `NetIncomeLoss`.
  - Unit: the reporting currency only (the ISO currency unit with the most annual revenue facts; `USD` for all
    three). No conversion; facts in other units are ignored, not mixed.
  - Fiscal year label `FY<year of the end date>`, always shown with the end date (`FY<year> (ends YYYY-MM-DD)`).
    `[verify against fixtures]`: confirm in the fixtures that each company's annual end dates match its
    `fiscalYearEnd`, and record the result in the architecture decision log.
  - Missing is `null` with `status: "missing"` and a reason, never 0.
- **Provenance** for every value: concept, taxonomy, unit, start, end, form, accession, filed, fy, fp and the source
  URL of the companyfacts file.

## 8. No-interview defaults

Do not interview the owner; decisions are in [docs/PRODUCT-DECISIONS.md](../../docs/PRODUCT-DECISIONS.md) and
`milestones/*.md`. Never re-decide what is recorded there. For unspecified, reversible details apply these defaults
and list them in the Handoff:

- Wording: use the exact strings in this prompt and in [acceptance.md](../acceptance.md); otherwise short, plain
  sentences that say what happened and what to do next.
- Code style: small functions with docstrings; type hints; no new dependency beyond `recharts` and `react-is`.
- Sorting: search results by match kind (ticker exact, CIK, ticker prefix, name), then name; one result per CIK.
- Chart default: all annual periods in the snapshot, both series on.
- Dates: ISO `YYYY-MM-DD`; timestamps in UTC with a `Z`.
- Anything the documents leave open and that does not change scope: choose the smallest option and add a row to
  the decision log in [architecture.md](../architecture.md) marked "routine technical choice under delegation".

If genuinely blocked (fixtures cannot be captured, a check fails twice after two different fixes, or a step would
need money, a secret, personal data or new scope): record the blocker with evidence in `milestones/plan.md`
"Known problems" and in the Handoff, and continue with the independent work. Do not ask anyone to paste a secret.

## 9. Tests and verification

Write the failing test first for logic, then the code. Keep tests offline: no test may reach the network
(use respx with no pass-through for HTTP code).

**pytest (`be/tests/`):**

- `test_cik.py`: `320193`, `0000320193`, `CIK320193`, ` 320193 ` → `0000320193`; `abc`, `12345678901`, `-1`, empty →
  `InvalidCik` (M1-E2).
- `test_search.py` (universe from the fixture tickers + submissions): `aapl` → Apple first with match `ticker`;
  `320193` and `0000320193` → Apple only (`cik`); `Microsoft` → Microsoft (`name`); `GOOGL` → Alphabet exactly once;
  `goog` → Alphabet once; `tesla` → empty (M1-AC3).
- `test_periods.py` with synthetic facts (`tests/synthetic/`): durations of 364, 371, 350 and 380 days are annual;
  349, 381, 91 and 273 are not; a 10-Q fact of annual length is ignored; the same (concept, unit, start, end) in a
  10-K filed 2024-11-01 (1,000) and a 10-K/A filed 2025-02-01 (1,010) gives 1,010 with the 10-K/A as provenance (not
  2,010); same filed date with accessions `…-24-000101` and `…-24-000099` keeps `…-24-000101` on every run; a FY2025
  10-K fact for the FY2023 period (`fy: 2025`) lands in FY2023; FY2023 only
  `RevenueFromContractWithCustomerExcludingAssessedTax` and FY2024 `Revenues` → each year uses its own concept, never a
  sum; a year with no revenue concept → `null`, `missing`, reason "no mapped revenue concept"; facts in `EUR` next to
  `USD` → only `USD` used.
- `test_overview_fixtures.py`: the overview for Apple and Microsoft equals the hand-worked `FX1`–`FX4` values,
  periods and accessions in acceptance.md; at least 5 annual periods per company.
- `test_api_m1.py` (FastAPI `TestClient`): `/api/health`; `/api/meta` (`data_mode` `fixtures`, snapshot date from
  the manifest, 3 companies); search (422 `invalid_query` for an empty or 101-character `q`); profile fields equal
  the fixture submissions file (M1-AC4); 422 `invalid_cik`, 404 `company_not_found`; every error uses the envelope;
  an unexpected exception returns 500 `internal_error` with a reference and no traceback text; every response's
  `source.label` starts with `RECORDED SEC DEMO · snapshot `.
- `test_fixtures_manifest.py` (M1-AC7): every file under `fixtures/` except `README.md`, `.gitattributes` and the
  manifest is listed; each entry has `source_url`, `retrieved_at`, `accessions`, `periods`, `scope` and `trimmed`;
  `sha256` matches; `synthetic` is false; no file under `fixtures/` contains the string `SYNTHETIC`; nothing under
  `be/tests/synthetic/` lacks the marker; companyfacts keeps only `CAPTURE_CONCEPTS`.
- `test_sec_client.py` (respx, fake clock and sleep, never real waiting): a non-allowlisted URL and a redirect to
  `https://example.com/` are refused before any request; a redirect to an allowlisted path is followed; a missing or
  malformed User-Agent refuses with a message naming `SEC_USER_AGENT`; 429 with `Retry-After: 5` then 200 waits ≥ 5 s
  and retries at most twice; 403 is not retried; two calls are ≥ 1 s apart. Build any fake User-Agent in the test
  from a reserved `.invalid` domain, never a real address.
- `test_no_network.py`: in fixture mode the app serves all M1 endpoints with respx active and no routes (any HTTP
  call fails the test).

**Vitest (`fe/`):** `lib/format.test.ts` (millions with separators, minus sign, `null` → `—`, dates);
`lib/combobox.test.ts` (↑/↓ wrap, Enter with no active item does nothing, Esc closes); `lib/shortcuts.test.ts` (`/`
and Ctrl/Cmd-K focus search, ignored while typing in an input); `components/SourceBadge.test.tsx` (text label
present for each kind).

**Playwright (`fe/e2e/m1-foundation.spec.ts`, fixture mode, run by `npm run verify`):**

1. Home: badge `RECORDED SEC DEMO`, the demo-universe note, backend status OK (M1-AC1).
2. Press `/`, type `aapl`, ↓, Enter → `/companies/0000320193`; Ctrl+K (Meta+K on macOS) also focuses the search
   (M1-AC2).
3. Company page: profile fields, key figures with fiscal year-end and unit, chart visible, the source label, hover a
   key figure → tooltip with concept and accession (M1-AC4, M1-AC5).
4. Search `tesla` → "No match in the demo universe (3 companies)".
5. Backend down (`page.route('/api/**', r => r.abort())`) → "Backend not reachable: start it with npm run demo"
   (M1-E1).
6. Throughout, record every request with `page.on('request')` and assert each URL is on `127.0.0.1` or
   `localhost` (no request leaves the machine, M1-AC1).
7. Screenshots of home and the Apple page at **1440×900, 1366×900 and 390×844** to
   `fe/test-results/m1-<screen>-<width>.png`, full page. At 390 px also assert
   `document.documentElement.scrollWidth <= 390`.

**Gate (all required, in this order):**

1. `npm run check-toolkit` exits 0.
2. `npm run verify` exits 0 from the repository root, with no network needed (record the summary line).
3. `npm run demo` starts with no `.env`, no keys and no network: open http://127.0.0.1:3000, do journeys 1–3, stop
   it with Ctrl+C. If you cannot drive a browser, check `curl -s http://127.0.0.1:8000/api/meta` and the home page
   HTML, and report the visual journey as not verified.
4. Open every screenshot from step 7 and look at it: dense dark layout, readable badges, no overlap, no sideways
   scrolling at 390 px. List the files you inspected and what you saw; fix what is wrong.
5. The fixture capture itself is the only live SEC contact at M1. Report it separately ("live SEC: fixtures
   captured on <date>, 7 requests" or "blocked: <reason>").

## 10. Acceptance criteria (from [acceptance.md](../acceptance.md))

- [ ] M1-AC1 `npm run demo` shows the dark shell, header search, `RECORDED SEC DEMO` badge and the demo-universe
  note; no request leaves the machine.
- [ ] M1-AC2 `/` (and Ctrl/Cmd-K) focus search; `aapl`, ↓, Enter opens "Apple Inc. · AAPL · CIK 0000320193".
- [ ] M1-AC3 `320193`, `0000320193`, `Microsoft`, `GOOGL` each find exactly their company; `tesla` gives "No match
  in the demo universe (3 companies)".
- [ ] M1-AC4 profile shows name, tickers, 10-digit CIK, exchange, SIC code and description, fiscal year-end and
  former names exactly as in the fixture; no invented description.
- [ ] M1-AC5 key figures and chart come from the fixture with fiscal year-end, unit and
  `RECORDED SEC DEMO · snapshot <date>`; hovering shows concept and accession.
- [ ] M1-AC6 `npm run verify` exits 0 offline, including backend lint and tests, frontend lint, typecheck, unit
  tests, build and the Playwright journey at 1440 and 390 px (this prompt adds 1366 px).
- [ ] M1-AC7 the manifest records source URL, retrieval date, accessions, periods and scope for every file;
  synthetic data only in `be/tests/synthetic/`, marked `SYNTHETIC`.
- [ ] M1-E1 backend down shows the plain message; M1-E2 invalid CIKs give 422 `invalid_cik`.
- [ ] V1–V3 screenshots at desktop and 390 px inspected; states explained in text, never colour alone.

Update each criterion's status in `milestones/acceptance.md` to `passing (test: <file::name>)`, `checked by hand on
<date> by <who>` or `blocked: <reason>`, and the slice rows and progress log in `milestones/plan.md`.

## 11. Out of scope

- Later milestones: live SEC lookup, the Live/Demo selector, the disk cache, full statements, ratios and the
  metric explorer (M2); filings, the filing reader and section search (M3); comparison and CSV export (M4); the AI
  analyst and OpenRouter (M5). Do not add their navigation, buttons or placeholders.
- Excluded everywhere (GOAL.md): accounts, payments, uploads, PostgreSQL or any database server, SQLite, a vector
  database, a Docker prerequisite, Streamlit, hosted or cloud deployment, SEC bulk archives, prefetching, an
  arbitrary URL proxy, non-SEC companies, market prices, valuation metrics, invented company descriptions, currency
  conversion, calendar alignment, light mode as a done criterion.
- Do not edit `milestones/*/PROMPT.md`, `milestones/*/FOLLOWUPS.md`, the toolkit (`.claude/` except the one new
  agent, `scripts/`, `scaffold/`, `AGENTS.md`, `CLAUDE.md`, `docs/TOOLKIT.md`), `GOAL.md`, `PROGRESS.md` or `runs/`.
  The milestone README's "Results" section is filled in by the owner after the checkpoint.

## 12. Handoff

Do not commit, tag, push or change Git configuration: the owner integrates, commits and creates the `m1`
checkpoint. Never read, create, print or commit `.env` files, keys or contact data.

End your final message with exactly this block (docs/TOOLKIT.md §7):

```
## Handoff
Changes: <files created or changed, grouped by folder>
Verification evidence: <each command with its exit code and summary line; screenshots looked at; live SEC capture result reported separately>
Remaining findings: <blockers, unverified items, defaults chosen, deviations from this prompt and why>
Next action: <one line>
```
