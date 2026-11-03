# Architecture: SEC Analytics (App Creator example)

Status: agreed on 2026-11-03 (delegated, see [docs/PRODUCT-DECISIONS.md](../docs/PRODUCT-DECISIONS.md))

`(assumption Q<n>)` points to a delegated decision. Rows marked **routine technical choice** were made here under
the delegation (GOAL.md §1) and are listed in the decision log. Anything marked `[verify against fixtures]` must be
confirmed against the recorded SEC data before the slice that uses it is called done.

## Stack

- **Stack:** standard App Creator stack (docs/TOOLKIT.md §2): Next.js App Router + React + TypeScript + Tailwind CSS v4,
  shadcn/ui-style components where they help, and Recharts; FastAPI + pydantic + httpx (+ BeautifulSoup for filing
  text); storage is fixture files plus a disk cache, with no database; pytest (respx for HTTP mocks), Vitest and
  project-local Playwright.
- **Why:** GOAL.md §4 requires this stack. The root commands already support it. SEC data must be fetched
  server-side, because data.sec.gov has no CORS ([research](../docs/research/sec-edgar.md) §6).
- **Alternative considered:** SQLite for the cache. Rejected for now, because plain files keyed by URL are enough
  (assumption Q35).
- **Folders** (in `app-creator.config.json` on the milestone branches; the template branch keeps `"app": null`):
  - frontend `examples/sec-analytics/frontend`
  - backend `examples/sec-analytics/backend`
  - docs `milestones` (PROGRESS.md D8)
  - recorded data `examples/sec-analytics/fixtures`
  - `demoEnv` `{"DATA_MODE": "fixtures"}`, `devEnv` `{"DATA_MODE": "live"}` (live is only allowed: the UI still
    starts in Demo)
  - SEC-specific working rules: `examples/sec-analytics/CLAUDE.md` (written in M1)

## Parts of the application and their boundaries

```text
browser ──same-origin /api/*──▶ Next.js (rewrite) ──▶ FastAPI on 127.0.0.1
                                                      ├─ logic/ (pure)
                                                      ├─ data/  fixtures ◀ examples/sec-analytics/fixtures
                                                      │         cache    ◀ <backend>/.cache/sec (git-ignored)
                                                      └─ clients/ sec.py ──▶ data.sec.gov, www.sec.gov (allowlist)
                                                                  openrouter.py ──▶ openrouter.ai/api/v1 (user key, per request)
```

| Part | Folder / file | Responsibility | Must not |
|---|---|---|---|
| UI | `frontend/app/` (routes `/`, `/companies/[cik]`, `/companies/[cik]/filings`, `/companies/[cik]/filings/[accession]`, `/compare`), `frontend/components/` | screens, inputs, keyboard search, source badges, loading/empty/missing/error states; draws values it receives | compute ratios, round or fill numbers, call SEC or OpenRouter, render raw filing HTML (`dangerouslySetInnerHTML` is forbidden) |
| Frontend helpers | `frontend/lib/api.ts`, `lib/types.ts` (mirror of the pydantic models), `lib/format.ts`, `lib/ai-key.ts` | typed `/api/*` client, display formatting of finished values, the key holder (memory, opt-in sessionStorage) | business rules; localStorage for the key |
| API | `backend/app/main.py`, `backend/app/api/{meta,companies,financials,filings,compare,ai}.py` | parse and validate (pydantic, `Query`/`Path`), choose the data source, call logic, map errors to the envelope | calculations, HTTP calls, file reads |
| Models | `backend/app/models/` | pydantic request/response models (shared shapes below) | logic |
| Logic | `backend/app/logic/`: `cik.py`, `search.py`, `concepts.py`, `periods.py`, `statements.py`, `metrics.py`, `compare.py`, `csv_export.py`, `sanitize.py`, `sections.py`, `retrieval.py`, `scope.py`, `prompting.py`, `citations.py` | pure functions: CIK normalization, annual-period selection, dedupe and restatement, ratios, indexing, CSV, HTML → text, section detection, passage retrieval, source ids, citation validation | network, files, clock (the current time is passed in) |
| Data access | `backend/app/data/fixtures.py`, `data/cache.py`, `data/source.py` | read fixtures and the manifest, read/write the disk cache, decide fixture vs cache vs live per request and label the result | business rules |
| External clients | `backend/app/clients/sec.py`, `clients/openrouter.py` | allowlisted SEC fetches (User-Agent, throttle, timeout, backoff, Retry-After); one OpenRouter call per request with the user's key | store or log keys; follow non-allowlisted redirects |
| Settings | `backend/app/settings.py` (pydantic `BaseSettings`) | read the setting names below | hold defaults that enable network in tests |
| Tests | `backend/tests/` (pytest; synthetic data in `tests/synthetic/`, marked `SYNTHETIC`), `frontend/**/*.test.ts(x)` (Vitest), `frontend/e2e/` (Playwright, fixture mode) | logic, data access with mocked HTTP, journeys | call SEC or OpenRouter (live smoke checks are separate scripts, run by hand) |

## Data modes and their labels

| Mode | When | Network | Label on every data panel | Header badge |
|---|---|---|---|---|
| **Demo (fixtures)** | always under `npm run demo` (`DATA_MODE=fixtures`); the default selection under `npm run dev` (assumption Q22, Q38) | none | `RECORDED SEC DEMO · snapshot <manifest retrieval date>`; filings: `Latest in snapshot (as of <date>)`, never just "Latest" | `RECORDED SEC DEMO` |
| **Live** | user picks Live in the header selector (`DATA_MODE=live`, from M2); needs `SEC_USER_AGENT` | SEC via backend | `LIVE · retrieved <time>` | `LIVE` |
| **Cached** | live mode, and the response came from the disk cache within its TTL | none for that response | `CACHED · retrieved <date>` | `LIVE` (panel shows CACHED) |
| **Missing** | a value or section is absent | – | `MISSING · <reason>` (e.g. "no mapped revenue concept for FY2021") | – |

The app never switches modes by itself. If a live request fails, the panel shows the error and a "Use recorded demo
data" button (GOAL.md §4, Q22). M1 is demo-only. The source chosen travels with the request (`source=demo|live`). Under
`DATA_MODE=fixtures` the server refuses `source=live` with `409 live_disabled`.

## API

All paths are same-origin under `/api/`. Shared shapes (pydantic, mirrored in `lib/types.ts`):

- `SourceInfo {mode: "demo"|"live"|"cached", label: str, retrieved_at: datetime|null, snapshot_date: date|null, source_urls: [str]}`
- `Provenance {concept: str, taxonomy: str, unit: str, start: date|null, end: date, form: str, accession: str, filed: date, fy: int|null, fp: str|null, source_url: str}`
- `MetricValue {metric_id: str, period_start: date|null, period_end: date, fiscal_year_label: str, value: float|null, unit: str, kind: "reported"|"derived", status: "ok"|"missing"|"unavailable"|"not_meaningful", reason: str|null, formula: str|null, inputs: [MetricValue], provenance: Provenance|null, note: str|null}`. Money is in the reporting currency's units (for example USD, not millions); ratios are decimals (0.25 = 25 %); the UI scales and formats.
- `FilingMeta {accession: str, form: str, is_amendment: bool, filing_date: date, report_date: date|null, primary_document: str, document_url: str, index_url: str}`
- Error envelope: `{"error": {"code": str, "message": str, "details": object|null, "reference": str|null}}`

| M | Method and path | Request | Response | Errors |
|---|---|---|---|---|
| M1 | `GET /api/health` | – | `{status: "ok", app: str}` | – |
| M1 | `GET /api/meta` | – | `{data_mode: "fixtures"\|"live", live_available: bool, live_configured: bool, snapshot_date: date, demo_universe: [{cik, ticker, name}]}` | – |
| M1 | `GET /api/companies/search` | `q` (1–100 chars), `limit` (1–20, default 10), `source` (M2+) | `{query, results: [{cik, ticker, name, match: "ticker"\|"name"\|"cik"}], universe_note: str, source: SourceInfo}` | 422 `invalid_query` |
| M1 | `GET /api/companies/{cik}` | `cik`: 1–10 digits, padded to 10 | `CompanyProfile {cik, name, tickers: [str], exchanges: [str], sic: str\|null, sic_description: str\|null, fiscal_year_end: "MMDD"\|null, state_of_incorporation: str\|null, former_names: [{name, from, to}], source: SourceInfo}` | 422 `invalid_cik`, 404 `company_not_found` (demo: "not in the demo snapshot") |
| M1 | `GET /api/companies/{cik}/overview` | `cik` | `{cik, key_figures: [MetricValue], chart: [{fiscal_year_label, period_end, revenue: MetricValue, net_income: MetricValue}], source: SourceInfo}` | as above |
| M2 | `GET /api/metrics` | – | `{metrics: [{id, label, unit_kind: "currency"\|"ratio"\|"percent", kind, formula: str\|null, concepts: [str]}]}` | – |
| M2 | `GET /api/companies/{cik}/financials` | `years` (5–10, default 10), `source` | `{cik, currency: str, fiscal_year_end: "MMDD", periods: [{fiscal_year_label, start, end}], statements: {income: [Line], balance: [Line], cash_flow: [Line]}, ratios: [Line], notes: [str], source: SourceInfo}` with `Line {metric_id, label, kind, unit, values: [MetricValue]}` | 422, 404, 409 `live_disabled`, 503 `sec_contact_not_configured`, 502 `sec_unavailable`, 503 `sec_rate_limited` (`details.retry_after`) |
| M2 | `GET /api/companies/{cik}/metrics` | `ids` (comma list, 1–6, from `/api/metrics`), `years`, `source` | `{cik, series: [{metric_id, label, unit, kind, formula, points: [MetricValue]}], source}` | as above, 422 `unknown_metric` |
| M3 | `GET /api/companies/{cik}/filings` | `forms` (subset of `10-K,10-K/A,10-Q,10-Q/A`), `years` (1–10, default 10), `source` | `{cik, latest: {annual: FilingMeta\|null, quarterly: FilingMeta\|null, label: str}, history: [FilingMeta], coverage: {from: date, to: date, complete: bool, note: str\|null}, source}` | as above |
| M3 | `GET /api/companies/{cik}/filings/{accession}` | `accession` `\d{10}-\d{2}-\d{6}`, `source` | `{meta: FilingMeta, section_status: "detected"\|"not_detected", note: str, sections: [{id, item: str, title: str, block_start: int}], blocks: [{id: int, section_id: str\|null, text: str}], source_link: str, source}` | 422 `invalid_accession`, 404 `filing_not_found`, 413 `document_too_large` |
| M4 | `GET /api/compare` | `ciks` (2–4, comma list), `metrics` (1–6), `years` (5–10), `index` (`none`\|`first_common_year`), `source` | `{companies: [{cik, ticker, name, fiscal_year_end, currency}], metrics: [str], rows: [CompareRow], index_base: {fiscal_year_by_cik: {cik: str}}\|null, warnings: [{code, message}], source}` with `CompareRow {cik, metric_id, fiscal_year_label, period_start, period_end, value: float\|null, unit, kind, indexed: bool, source_concept: str\|null, accession: str\|null, data_source: str}` | 422 `too_few_companies` / `too_many_companies` / `duplicate_company`, others as above |
| M4 | `GET /api/compare.csv` | same as `/api/compare` | `text/csv` attachment built from the same result (columns in [acceptance](acceptance.md) M4-AC6) | same |
| M5 | `GET /api/ai/models` | header `X-OpenRouter-Key` | `{models: [{id, name, context_length: int\|null, prompt_usd_per_million: str\|null, completion_usd_per_million: str\|null, expiration_date: date\|null}], fetched_at}` | 400 `ai_key_missing`, 401 `ai_key_invalid`, 502 `ai_unavailable`, 504 `ai_timeout` |
| M5 | `POST /api/ai/test-connection` | header key | `{ok: bool, label: str\|null, limit_remaining_usd: float\|null, message: str}` (calls `GET /api/v1/key`; the UI warns it may incur a small charge) | as above |
| M5 | `POST /api/ai/chat` | header key; body `{model: str (required, no default), scope: {kind: "company"\|"filing"\|"comparison", cik?, accession?, ciks?, metrics?}, question: str (1–2,000 chars), source}`; body ≤ 64 KB | `{answer: str, citations: [{source_id, valid: bool, kind: "fact"\|"passage", label, period, date, link}], invalid_references: [str], refusal: {code, message}\|null, context: {facts: int, passages: int, chars: int}, model: str, usage: {prompt_tokens, completion_tokens, cost}\|null, notice: "Source links are checked; the claims themselves may still be wrong."}` | 400 `ai_key_missing`, 401 `ai_key_invalid`, 402 `ai_insufficient_credits`, 403 `ai_forbidden`, 404 `ai_model_not_found`, 409 `ai_busy`, 413 `request_too_large`, 429 `ai_rate_limited`, 502 `ai_unavailable`, 504 `ai_timeout` |

Unexpected errors return 500 with a generic message and a `reference` id. Detail goes to the log only, never a
stack trace or a key.

## Financial data rules

These rules are the outline that M2's tests pin down (Q23–Q30). The full version, with the verified concept list, goes
into `examples/sec-analytics/CLAUDE.md` and `backend/app/logic/concepts.py`.

**Periods.** A period is identified by `start`/`end`, never by `fy`/`fp`: those describe the filing that reported
the value ([research](../docs/research/sec-edgar.md) §2).
- Annual duration facts last 350–380 days inclusive, so 52/53-week years are included. Quarterly and
  year-to-date facts are excluded from annual series (Q25).
- Instant facts (balance sheet) are matched to the annual period's `end` date exactly.
- Only facts whose `form` is `10-K` or `10-K/A` feed annual series (Q24).
- Fiscal year label: `FY<year of end date>`, shown with the exact end date (routine technical choice
  `[verify against fixtures]`).

**Duplicates and restatements** (Q24):
- Group facts by (concept, unit, start, end).
- Keep the fact with the latest `filed` date. If two share a date, keep the higher accession number.
- Duplicates are never summed, and the facts used are kept as provenance.
- Every statement view carries the note "Values may reflect later restatements; not point-in-time."

**Units.** A series uses one unit, the company's reporting currency (for example `USD`).
- Facts in other units are not mixed in.
- A ratio whose inputs have different units is `unavailable` ("units differ").
- No currency conversion (GOAL.md §6).

**Concept mapping** (proposed; `[verify against fixtures]`):

| Metric | US-GAAP concepts (priority order; the first present per period wins; alternates never summed) | Kind |
|---|---|---|
| revenue | `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`, `SalesRevenueNet`, `RevenueFromContractWithCustomerIncludingAssessedTax` (Q23) | reported; concept shown, change between years flagged |
| operating_income | `OperatingIncomeLoss` | reported |
| net_income | `NetIncomeLoss` | reported |
| income_tax | `IncomeTaxExpenseBenefit` | reported (EBIT input) |
| interest_expense | `InterestExpense` (alternates to be chosen from fixtures) | reported (EBIT input) |
| d_and_a | `DepreciationDepletionAndAmortization`, `DepreciationAndAmortization` | reported (EBITDA input) |
| operating_cash_flow | `NetCashProvidedByUsedInOperatingActivities` | reported |
| capex | `PaymentsToAcquirePropertyPlantAndEquipment` (a positive payment) | reported |
| assets, assets_current, liabilities, liabilities_current, equity | `Assets`, `AssetsCurrent`, `Liabilities`, `LiabilitiesCurrent`, `StockholdersEquity` | reported (instant) |
| debt components | `LongTermDebtNoncurrent` + `LongTermDebtCurrent` + (`CommercialPaper` or `ShortTermBorrowings`), each counted once (Q29) | reported inputs to derived debt |

**Derived metrics** (formulas in [acceptance](acceptance.md#calculations-known-answers)):
- revenue growth, margins, FCF, EBIT, EBITDA, working capital, debt-to-equity, ROE and ROA (Q26–Q30).
- A missing input makes the result `unavailable`, never 0. A zero denominator is `unavailable`.
- Negative equity gives `not_meaningful`, shown as "n/m (negative equity)", with the inputs in the tooltip.
- EBIT is never replaced by operating income.

**Comparison** (Q32): each company keeps its own fiscal year-ends and currency.
- Indexing is "Index = 100 at first common fiscal year label", computed per company.
- Absolute values in different currencies are never drawn on one axis; a warning is shown instead.

## Data and storage

- Storage: **fixture files** (read-only) and a **disk cache** (from M2). No database (Q35).

| File / folder | Contents | Who reads / changes it |
|---|---|---|
| `examples/sec-analytics/fixtures/manifest.json` | per file: source URL, retrieval date, accession(s), periods, trimming scope | backend reads; changed only by the documented fixture-capture script |
| `fixtures/company_tickers.json` | the 3 ticker-map entries | backend reads |
| `fixtures/submissions/CIK##########.json` | submissions trimmed to 10-K/10-Q entries | backend reads |
| `fixtures/companyfacts/CIK##########.json` | Company Facts trimmed to mapped concepts, original structure, values unmodified | backend reads |
| `fixtures/filings/<cik>/<accession>/<document>` | latest 10-K and 10-Q primary-document excerpts | backend reads |
| `<backend>/.cache/sec/<sha256 of URL>.json` (`SEC_CACHE_DIR`) | `{url, retrieved_at, status, body}` | backend reads/writes; git-ignored (`.cache/`) |

Fixture capture is a one-off script, `backend/scripts/capture_fixtures.py` (M1). It uses the live client, so it
needs `SEC_USER_AGENT`. If capture is blocked, the step is reported as blocked (N2).

## External services

| Service | Used for | Setting names (values only in `.env`) | Offline / demo behaviour | Cost | Terms checked |
|---|---|---|---|---|---|
| SEC EDGAR (`data.sec.gov`, `www.sec.gov`) | ticker map, submissions, Company Facts, filing documents | `SEC_USER_AGENT` (an app name plus the owner's contact, set by the owner only) | fixtures; no network | free | fair access: ≤ 10 req/s for all machines together, declared User-Agent, no CORS ([research](../docs/research/sec-edgar.md) §5–6) |
| OpenRouter | M5 analyst | none on the server: the student's key travels per request | AI panel shows "AI not configured"; tests mock the client | paid per token by the student's limited key | [research](../docs/research/openrouter.md) §1–7 |

**SEC client rules** (`clients/sec.py`):
- **Allowlist:** `https://data.sec.gov` paths `/submissions/CIK\d{10}.json`, `/submissions/CIK\d{10}-submissions-\d{3}.json`
  and `/api/xbrl/companyfacts/CIK\d{10}.json`; `https://www.sec.gov` paths `/files/company_tickers.json` and
  `/Archives/edgar/data/\d+/\d{18}/[A-Za-z0-9._-]+`.
- **Redirects:** followed manually, at most 3, and only to allowlisted URLs. URLs are built from validated parts,
  never taken from the client.
- **User-Agent:** from `SEC_USER_AGENT`. Missing means `503 sec_contact_not_configured`, naming the setting (Q37).
- **Throttle:** at most 1 request per second per running app (`SEC_MAX_REQUESTS_PER_SECOND`, default 1), one request
  in flight, identical concurrent requests deduplicated, no prefetching (Q38).
- **Timeouts and retries:**
  - Timeout of 20 s.
  - On 429/503, honour `Retry-After` (capped at 30 s) and retry at most 2 times with backoff.
  - On 403, never retry: show a message saying SEC refused the request.

**OpenRouter boundary** (`clients/openrouter.py`, GOAL.md §7):
- **The key's path:** the browser keeps the key in memory. sessionStorage is used only after an explicit opt-in with a
  warning that page scripts can read it, and never localStorage (Q36). The browser sends the key in the
  `X-OpenRouter-Key` header to its own backend. The backend uses it for that one upstream call
  (`Authorization: Bearer`) and drops it. The key is never saved, logged or echoed in an error.
- **Redaction:** a logging filter redacts that header, `Authorization` and request bodies.
- **Network boundary:** the backend binds to 127.0.0.1. CORS is not enabled. `/api/ai/*` rejects requests whose
  `Origin` is not the app's own origin.
- **Limits:**
  - Request body ≤ 64 KB.
  - Context of at most 60 facts and 8 passages (about 24,000 characters).
  - `max_completion_tokens` 800.
  - Concurrency: 2 on the backend, 1 per browser.
  - 60 s upstream timeout.
  - No automatic retries.
  - The UI has a cancel button, which aborts the fetch; the backend then cancels the upstream call (Q44).
- **Models:** the list comes live from `GET /api/v1/models`, showing IDs and price per million tokens. A manual ID is
  allowed. There is no default model.
- **Errors:** handled for 401, 402, 403, 404 (retired model), 429 and timeout. The backend checks `body.error` even
  on a 200 ([research](../docs/research/openrouter.md) §5).
- **Grounding:**
  - `logic/retrieval.py` picks facts (from the computed metrics) and passages (filing blocks ranked by
    deterministic term overlap with the question).
  - Server-assigned ids are `F1…` for facts and `P1…` for passages.
  - Filing text goes in a delimited data block in the user message, never in the system message. The system
    message says the passages are data, not instructions.
  - Numbers are computed by the app.
  - `logic/scope.py` runs a deterministic pre-check that refuses clearly out-of-scope questions (price forecasts,
    buy/sell advice, companies that are not loaded) without calling the model (Q43). Other refusals come from the
    model and are shown as they are.
  - `logic/citations.py` keeps only references to supplied ids. Any others are listed as `invalid_references` and
    shown with a warning.

## Caching and background work

- A disk cache of SEC responses, from M2:
  - ticker map, submissions and Company Facts are stale after 24 h;
  - archive documents are kept until deleted (an accession does not change).
- The age is shown as `CACHED · retrieved <date>`.
- No background jobs, no scheduled refresh, no prefetching.

## Security and privacy

- **Personal data stored:** none. The SEC contact is the owner's local setting, never committed or logged (N2).
- **Who can see what:** single user, local. There are no accounts.
- **Secrets:** the app needs no server secret. The OpenRouter key is user-supplied and transient (above). Nothing goes
  in `NEXT_PUBLIC_*`.
- **Filing content is untrusted:**
  - it is converted to text with scripts, styles, iframes, forms and event attributes removed;
  - it is rendered as text only;
  - source links are preserved;
  - section detection skips repeated table-of-contents headings and labels its uncertainty (Q41).
- **CSV export** neutralises cells starting with `=`, `+`, `-` or `@` (Q33).

## Settings (names only; placeholders in `.env.example`, added by the slice that first reads them)

| Name | Read by | Default (safe) | From |
|---|---|---|---|
| `DATA_MODE` | backend | `fixtures` | M1 |
| `FIXTURES_DIR` | backend | `examples/sec-analytics/fixtures` | M1 |
| `SEC_USER_AGENT` | backend (live only) | empty: live refused | M2 (and the M1 capture script) |
| `SEC_CACHE_DIR` | backend | `<backend>/.cache/sec` | M2 |
| `SEC_MAX_REQUESTS_PER_SECOND` | backend | `1` | M2 |
| `BACKEND_PORT`, `FRONTEND_PORT`, `APP_PYTHON` | root launchers | 8000, 3000, auto | existing |

Tests and `npm run demo` need no `.env`.

## Run, test, preview (root commands)

- Python 3.10–3.13 in `examples/sec-analytics/backend/.venv` (override: `APP_PYTHON`).
- Install: `npm ci` (once), then `npm run setup`.
- Offline demo: `npm run demo` (`DATA_MODE=fixtures`). Development: `npm run dev`, then open http://127.0.0.1:3000.
- Check everything: `npm run verify`. It runs the toolkit checks, backend lint and pytest, frontend lint, typecheck,
  Vitest, the production build and a Playwright smoke test in fixture mode at 1440 and 390 px, with no network
  (Q40, Q14).
- Live checks: SEC live smoke and OpenRouter live are separate, run by hand, and reported separately from `verify`.

## Decision log

| Date | Decision | Reason | Basis |
|---|---|---|---|
| 2026-11-03 | Scope and architecture agreed for M1–M5 | delegated interview complete | agreed under delegation (GOAL.md §1, §8); decisions Q1–Q44 in docs/PRODUCT-DECISIONS.md. Open blockers: N1 (paid live AI validation), N2 (SEC contact in the owner's environment) |
| 2026-11-03 | Planning documents in `milestones/`; app in `examples/sec-analytics/` | template must hold prompts, not the app | PROGRESS.md D8; GOAL.md §3 |
| 2026-11-03 | Fixture files + disk cache, no SQLite | read-only snapshots and URL-keyed responses need no queries | assumption Q35; GOAL.md §4 |
| 2026-11-03 | Data source chosen per request (`source=demo\|live`), live refused under `DATA_MODE=fixtures` | explicit mode choice, deterministic demo | GOAL.md §4; assumption Q22 |
| 2026-11-03 | SEC allowlist, 1 req/s, one in flight, Retry-After, no retry on 403 | fair access, shared classroom IP | GOAL.md §6; assumption Q38 |
| 2026-11-03 | Annual = 350–380 days, 10-K/10-K/A only, latest filed wins, tie → higher accession | 52/53-week years; deterministic restatement policy | GOAL.md §6; assumptions Q24, Q25 |
| 2026-11-03 | Fiscal year label `FY<year of end date>` with the end date shown | readable and unambiguous with the date beside it | routine technical choice under delegation; `[verify against fixtures]` |
| 2026-11-03 | OpenRouter key in `X-OpenRouter-Key` header per request, never stored server-side | transient key, redaction-friendly | GOAL.md §7; assumption Q36, Q44 |
| 2026-11-03 | Filing text search runs in the browser over the returned blocks; no search endpoint | the text is already loaded; less API surface | routine technical choice under delegation |
| 2026-11-03 | Rejected: SQLite cache, vector database, server-side key storage, 8-K history | not needed / forbidden / new scope | GOAL.md §4, §7; assumption Q42 |
