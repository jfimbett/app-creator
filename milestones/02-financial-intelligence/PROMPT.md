# M2 Financial intelligence: build brief

This is the exact implementation brief for SEC Analytics milestone 02. Give it, unchanged, to the assistant or agent
that implements the milestone. It is immutable once the `template-v1` checkpoint exists. Corrections that change
the implementation go into [FOLLOWUPS.md](FOLLOWUPS.md) before they are dispatched.

Paths are relative to the repository root unless stated. `fe/` means `examples/sec-analytics/frontend/` and `be/`
means `examples/sec-analytics/backend/`.

---

## 1. Starting ref

- **Start from tag `m1`** (the verified M1 Foundation checkpoint).
- A student rebuilding this milestone, in a **clean checkout** (`git status` shows nothing to commit; stop any
  running `npm run dev` or `npm run demo` first):

  ```bash
  git fetch origin --tags
  git switch -c exercise/build-m2 m1
  npm ci
  npm run setup
  ```

- Check the start: `git merge-base --is-ancestor m1 HEAD` exits 0 and `git log --oneline m1..HEAD` is empty before
  you begin; `npm run verify` exits 0 on the untouched start (if it does not, record that as a finding before
  changing anything).
- The completed `m2` tag is **for inspection** (`git switch --detach m2`). Do not run this prompt on an `m2`
  checkout. Replaying the prompt will not produce identical code; the `m2` tag is the reference version.

## 2. Context: what exists at `m1`

Read the code before planning; if it differs from this summary, the code and the statuses in
`milestones/acceptance.md` win, and you record the difference as a finding.

- **Toolkit** as at `template-v1` (`AGENTS.md`, `.claude/skills/`, `.claude/agents/`, root launchers
  `npm run setup | dev | demo | verify`, `docs/TOOLKIT.md`), plus the example agent
  `.claude/agents/sec-data-specialist.md`.
- **Config:** `app-creator.config.json` points at `examples/sec-analytics/frontend` and `/backend`, `docsDir`
  `milestones`, `devEnv` and `demoEnv` both `{"DATA_MODE": "fixtures"}`.
- **Example rules:** `examples/sec-analytics/CLAUDE.md` (SEC/finance rules) and the nested skill
  `examples/sec-analytics/.claude/skills/sec-edgar-data/SKILL.md` (Claude Code loads it the first time a file in
  that folder is read or edited). Read both now.
- **Fixtures** (`examples/sec-analytics/fixtures/`): authentic snapshots for AAPL (CIK 0000320193), MSFT
  (0000789019) and GOOGL (0001652044): `company_tickers.json` (their entries), `submissions/` (10-K/10-Q rows),
  `companyfacts/` (the `CAPTURE_CONCEPTS` list, facts unmodified), `manifest.json` (source URL, retrieval date,
  sha256, accessions, periods, scope, trimmed), built by `be/scripts/capture_fixtures.py`. Hand-worked fixture
  values `FX1`–`FX4` are in `milestones/acceptance.md`.
- **Backend:** `app/main.py`, `settings.py` (`DATA_MODE`, `FIXTURES_DIR`), `errors.py` (envelope),
  `models/common.py` (`SourceInfo`, `Provenance`, `MetricValue`), `api/meta.py`, `api/companies.py`
  (`/api/health`, `/api/meta`, `/api/companies/search`, `/api/companies/{cik}`, `/api/companies/{cik}/overview`),
  `logic/cik.py`, `search.py`, `concepts.py`, `periods.py` (annual 350–380 days, 10-K/10-K/A, duplicate policy),
  `statements.py` (overview), `data/fixtures.py`, `clients/sec.py` (allowlist, User-Agent, throttle, Retry-After,
  no 403 retry; used only by the capture script), tests in `be/tests/` and `be/tests/synthetic/`.
- **Frontend:** dark navy terminal shell, header search combobox (`/`, Ctrl/Cmd-K, ↑/↓, Enter, Esc), home with the
  demo-universe note, `/companies/[cik]` with profile, key figures (latest revenue, net income), revenue/net income
  chart (Recharts) with provenance tooltips, `SourceBadge`, `StatePanel`, `lib/api.ts`, `lib/types.ts`,
  `lib/format.ts`; Playwright `e2e/m1-foundation.spec.ts` at 1440, 1366 and 390 px.
- **Settings in `.env.example`:** `DATA_MODE`, `FIXTURES_DIR`, `SEC_USER_AGENT` (names and placeholders only).
- **Planning:** [GOAL.md](../../GOAL.md) §4–§6, [docs/PRODUCT-DECISIONS.md](../../docs/PRODUCT-DECISIONS.md)
  (Q5, Q9–Q12, Q22–Q31, Q35, Q37, Q38), [milestones/architecture.md](../architecture.md) ("Data modes",
  "API", "Financial data rules", "External services"), [milestones/acceptance.md](../acceptance.md) (M2 rows,
  CALC1–CALC10, M2-E1–M2-E13), [milestones/plan.md](../plan.md) (slices 2.1–2.6),
  [docs/research/sec-edgar.md](../../docs/research/sec-edgar.md).

All M1 behaviour must keep working (M1-AC1–M1-AC7, M1-E1, M1-E2).

## 3. Goal and new work

GOAL.md §5, row 02: backend SEC adapters; live company lookup; annual income statement, balance sheet and
cash-flow summaries; 5–10 available years; a selectable metric explorer and charts; source provenance and
calculated ratios; explicit missing-data behaviour.

1. **Live mode, explicit and opt-in** (Q22). Set `devEnv` to `{"DATA_MODE": "live"}` in
   `app-creator.config.json` (`demoEnv` stays `fixtures`). Under `npm run dev` the header shows a **Demo / Live**
   selector that starts on Demo; under `npm run demo` there is no selector, only the `RECORDED SEC DEMO` badge. The
   chosen source travels with every data request as `source=demo|live` (and in the page URL as `?source=live`, so
   reloads keep it). The app never switches mode by itself: a failed live request shows the error and a
   **"Use recorded demo data"** button.
2. **SEC adapters** (`clients/sec.py` extended, `data/cache.py`, `data/source.py`): ticker map, submissions and
   Company Facts fetched by the backend only, with the full fair-access rules of section 7, a disk cache and
   request de-duplication.
3. **Live company lookup:** in Live, search covers the SEC ticker file (`company_tickers.json`) by ticker, name or
   CIK; a CIK that is not in the ticker file can still be opened. The note under the search reads "Live search
   covers SEC filers listed in the SEC ticker file; other filers can be opened by CIK." It never suggests non-SEC
   companies are supported. In Demo the M1 note and universe stay.
4. **Financial statements** on the company page: the M1 key-figure strip grows to latest annual revenue, YoY
   revenue growth, net income, net margin, operating cash flow, FCF and debt-to-equity (Q10), each with fiscal
   year-end, unit/currency, a `REPORTED` or `DERIVED` text badge and a provenance/formula tooltip. Below the M1
   chart: three summary tables, **Income statement (summary)**, **Balance sheet (summary)** and
   **Cash flow (summary)**, plus a **Ratios** table, one column per annual period, headed
   `FY<year> (ends YYYY-MM-DD)`, newest on the right. A years selector offers 5–10 (default 10; when fewer exist,
   "N annual periods available"). The tables are titled "normalized summary from SEC Company Facts, not the
   complete filed statement", and carry the note "Values may reflect later restatements; not point-in-time."
5. **Metric explorer** (a section of the company page, anchored `#explorer`; no new top-level route): pick 1–6
   metrics from `/api/metrics`, see one compact line chart per metric stacked in one panel with a shared fiscal
   year axis (so currency and percentage series never share an axis), visible zero baseline, gaps for missing
   years, provenance in the tooltip. A "Show data" toggle shows the same points as a table.
6. **Provenance and ratios:** every reported number carries its `Provenance`; every derived number carries its
   formula and its input `MetricValue`s. Ratios follow section 7 exactly.
7. **Missing data, stated explicitly:** `MISSING · <reason>` for absent facts, `unavailable` with a reason for
   ratios whose inputs are missing or whose denominator is zero, `n/m (negative equity)` or `n/m` with a reason
   where the number would mislead. Never 0, never a blank without a reason.
8. **Settings:** add `SEC_CACHE_DIR` (empty means `be/.cache/sec`) and `SEC_MAX_REQUESTS_PER_SECOND` (default `1`,
   values above 5 refused) to `.env.example` and `settings.py`; `DATA_MODE` now accepts `fixtures` or `live`.
9. **Live smoke script** `be/scripts/live_sec_smoke.py` (run by hand, never by `verify`): with `SEC_USER_AGENT`
   configured (process environment or root `.env`, parsed by the script, value never printed), it fetches the ticker
   map, Apple's submissions and Apple's Company Facts through the app's client (3 requests, 1 per second), checks
   the structure the app relies on, and prints PASS/FAIL per check.

## 4. Design

Keep the M1 look and extend it consistently.

- **Dark navy terminal** tokens from `fe/app/globals.css` (background `#0A1020`, panels `#0F1A2E`/`#14223B`, border
  `#1F2E4A`, text `#DCE3EE`, muted `#8C9AB3`, amber accent `#F2B33D`, link `#6CB6FF`, positive `#3FB68B`, negative
  `#F0605D`, warning `#E8A33A`; contrast ≥ 4.5:1). Dark is the done criterion; light mode stays out.
- **Dense tables** with tabular numerals, right-aligned numbers, sticky header and sticky first column, units in the
  header ("USD millions", "%", "×"), true minus signs. Percentages with 1 decimal, debt-to-equity with 2 decimals and
  `×`. Rows for derived lines are marked with the `DERIVED` badge; a thin rule separates statement groups.
- **Mode selector** (dev only): a two-option segmented control in the header, labelled "Data source", options
  "Demo" and "Live", with the current mode also in the header badge (`RECORDED SEC DEMO` or `LIVE`). Panels show
  their own badge: `RECORDED SEC DEMO · snapshot <date>`, `LIVE · retrieved <time>`, `CACHED · retrieved <date>`,
  `MISSING · <reason>`. Text, never colour alone.
- **Tooltips** (hover and keyboard focus): reported value → concept, taxonomy, unit, start–end, form, accession,
  filing date and a "Source" link to the companyfacts URL; derived value → formula, each input with its value and
  period, and the reason when unavailable.
- **States:** loading skeleton rows; "Live SEC data is not configured: set SEC_USER_AGENT (see .env.example and
  docs/SETUP.md)"; "SEC is unavailable right now" with "Use recorded demo data" and "Try again"; "SEC is limiting
  requests; try again in N s"; "SEC refused the request (403). The app does not retry refused requests."; "Not in
  the demo snapshot"; a statement column with no data. Each says what happened and what the user can do.
- **Charts** (Recharts): lines for trends, zero baseline always drawn, negative values below it, missing years as
  gaps (`connectNulls={false}`), axis titles with units, tooltips with the period end date.
- **Responsive** at 1440, 1366 and 390 px: no sideways page scroll; tables scroll inside their container; the key
  figures wrap into two columns at 390 px; the mode selector stays reachable.
- **Honesty:** no prices, market cap, P/E or other valuation figures; no invented descriptions; no navigation to
  later features (no Filings, Compare or Analyst links yet); no control that does nothing.

## 5. Architecture and files

Follow [milestones/architecture.md](../architecture.md). Logic stays pure (the current time is passed in), the API
layer only validates and maps errors, the data layer chooses fixture, cache or live per request and labels the
result, and only `clients/sec.py` talks to SEC.

| Path | Change |
|---|---|
| `app-creator.config.json` | `devEnv` → `{"DATA_MODE": "live"}` |
| `.env.example` | add `SEC_CACHE_DIR`, `SEC_MAX_REQUESTS_PER_SECOND`; update the `SEC_USER_AGENT` comment ("needed for live mode and fixture capture") |
| `be/app/settings.py` | new settings; `live_configured` = a well-formed `SEC_USER_AGENT` is present (the value is never exposed) |
| `be/app/clients/sec.py` | async client used by the app: allowlist and redirects, User-Agent, throttle, single flight, de-duplication, timeouts, Retry-After, 403 stop, typed errors (`SecNotConfigured`, `SecUnavailable`, `SecRateLimited(retry_after)`, `SecRefused`, `UpstreamNotAllowed`, `SecNotFound`); injectable clock and sleep for tests |
| `be/app/data/cache.py` | disk cache: file `<SEC_CACHE_DIR>/<sha256 of URL>.json` with `{url, retrieved_at, status, body}`; TTL 24 h for ticker map, submissions and Company Facts; written atomically (temp file + rename); a corrupt file is ignored and refetched |
| `be/app/data/source.py` | `get_ticker_map`, `get_submissions`, `get_companyfacts(cik, source, now)` → `(data, SourceInfo)`; demo → fixtures; live → cache or client; refuses live under `DATA_MODE=fixtures` (`409 live_disabled`) |
| `be/app/logic/concepts.py` | the verified concept mapping (section 7), each metric's id, label, unit kind, kind and concepts |
| `be/app/logic/periods.py` | complete: annual durations, instants matched to the period end, duplicate/restatement policy, unit filter, concept-change flag |
| `be/app/logic/statements.py` | statement lines per period (income, balance, cash flow) from the selected facts |
| `be/app/logic/metrics.py` | derived metrics and ratios (section 7), returning `MetricValue` with `status`, `reason`, `formula`, `inputs` |
| `be/app/models/financials.py` | `MetricsCatalog`, `FinancialsResponse`, `Line`, `MetricSeriesResponse` |
| `be/app/api/financials.py` | `GET /api/metrics`, `/api/companies/{cik}/financials`, `/api/companies/{cik}/metrics` |
| `be/app/api/companies.py`, `api/meta.py` | accept `source`; live search; `meta.data_mode`, `live_available` (`DATA_MODE=live`), `live_configured` |
| `be/app/errors.py` | new codes below |
| `be/scripts/live_sec_smoke.py` | manual live smoke check |
| `be/tests/...`, `be/tests/synthetic/...` | section 9 |
| `fe/lib/types.ts`, `fe/lib/api.ts` | new types and calls; every call passes `source` |
| `fe/lib/source.ts` | the selected source (React context + URL `?source=`), default `demo` |
| `fe/components/` | `ModeSelector`, `StatementTable`, `KeyFigures` (extended), `MetricExplorer`, `MetricChart`, `ProvenanceTip` (reported and derived), `ValueCell` (ok/missing/unavailable/n/m), `LiveErrorPanel` (with "Use recorded demo data") |
| `fe/app/companies/[cik]/page.tsx` | statements, ratios, explorer sections |
| `fe/e2e/m2-financials.spec.ts` | section 9 |
| `examples/sec-analytics/CLAUDE.md`, nested `sec-edgar-data` skill | the verified concept mapping, the formulas, the restatement policy, the cache and throttle |
| `examples/sec-analytics/README.md` | live mode, the setting, the classroom note, the smoke script |
| `milestones/acceptance.md`, `plan.md`, `architecture.md` | statuses, fixture-based calculation rows, progress log, decision-log rows (including any new error code) |

**API added or changed at M2** (shared shapes `SourceInfo`, `Provenance`, `MetricValue`, `FilingMeta` and the
error envelope as in architecture.md):

| Method and path | Request | Response | Errors |
|---|---|---|---|
| `GET /api/meta` | – | M1 fields; `data_mode` `fixtures`\|`live`, `live_available`, `live_configured` | – |
| `GET /api/companies/search` | `q`, `limit`, `source` (`demo` default) | M1 shape; `universe_note` per mode; `source` labelled `LIVE`/`CACHED`/`RECORDED SEC DEMO` | 422 `invalid_query`, 409 `live_disabled`, 503 `sec_contact_not_configured`, 502 `sec_unavailable`, 503 `sec_rate_limited` (`details.retry_after`), 502 `sec_refused`, 502 `upstream_not_allowed` |
| `GET /api/companies/{cik}`, `/overview` | + `source` | M1 shapes | + the SEC errors above |
| `GET /api/metrics` | – | `{metrics: [{id, label, unit_kind: "currency"\|"ratio"\|"percent", kind: "reported"\|"derived", formula: str\|null, concepts: [str]}]}` | – |
| `GET /api/companies/{cik}/financials` | `years` (5–10, default 10), `source` | `{cik, currency, fiscal_year_end: "MMDD", periods: [{fiscal_year_label, start, end}], statements: {income: [Line], balance: [Line], cash_flow: [Line]}, ratios: [Line], notes: [str], source}`; `Line {metric_id, label, kind, unit, values: [MetricValue]}` (one value per period, same order as `periods`) | 422 `invalid_years`, 422 `invalid_cik`, 404 `company_not_found`, 409, 503, 502 as above |
| `GET /api/companies/{cik}/metrics` | `ids` (comma list, 1–6, from `/api/metrics`), `years`, `source` | `{cik, series: [{metric_id, label, unit, kind, formula, points: [MetricValue]}], source}` | as above, 422 `unknown_metric` |

`sec_refused` (502, SEC answered 403) is new compared with architecture.md: add it to the API table there and to the
decision log. Live failures never fall back to fixtures silently; the frontend offers the button instead.
`notes` include the restatement note and, when it applies, "Revenue concept changes between years:
<FY>: <concept> → <FY>: <concept>".

## 6. Fixtures and data

- Use the M1 fixtures unchanged. Do **not** recapture: a recapture changes every number, the snapshot date and the
  hand-worked answers.
- Verify the concept mapping against the fixtures (`[verify against fixtures]` items in architecture.md): for each
  company and mapped concept, list which concepts actually appear in annual 10-K facts and over which years, and
  record the result in `examples/sec-analytics/CLAUDE.md` and the architecture decision log. Choose the
  interest-expense alternates and the D&A concept from what the fixtures contain, in a fixed priority order.
- If a needed concept is missing from `CAPTURE_CONCEPTS`, show the metric as unavailable and record a finding. Do
  not quietly recapture or edit fixtures; a recapture needs its own follow-up step.
- **Fixture-based known answers:** before writing the tests that use them, add rows `FX5` onward to the
  calculation section of `milestones/acceptance.md`: for Apple and Microsoft, latest fiscal year, the net margin,
  FCF, debt-to-equity and ROE, each with written hand working that quotes concept, unit, start/end, accession and
  `val` of every input taken from the fixture JSON (not from the app's output). Also record which inputs are
  unavailable (for example EBIT if `InterestExpense` is absent) and why.
- Synthetic inputs for CALC1–CALC10 and M2-E1–M2-E13 live in `be/tests/synthetic/`, each marked `SYNTHETIC`.
- The disk cache (`be/.cache/sec/`) is git-ignored (`.cache/` in the root `.gitignore`) and never committed.

## 7. SEC rules that apply at M2

**Client and fair access** (`clients/sec.py`):

- Backend only; the browser calls only `/api/*` on its own origin.
- Allowlisted HTTPS hosts and paths only (data.sec.gov `/submissions/CIK\d{10}.json`,
  `/submissions/CIK\d{10}-submissions-\d{3}.json`, `/api/xbrl/companyfacts/CIK\d{10}.json`; www.sec.gov
  `/files/company_tickers.json`, `/Archives/edgar/data/\d+/\d{18}/[A-Za-z0-9._-]+`). URLs are built from validated
  parts. Redirects are followed by hand, at most 3, each target checked first; otherwise `502
  upstream_not_allowed` and no request is made to it.
- `User-Agent` from `SEC_USER_AGENT` (descriptive name plus the person's own contact email, set by that person);
  missing or malformed → `503 sec_contact_not_configured` naming the setting. Never invented, logged or echoed.
- Throttle: at most `SEC_MAX_REQUESTS_PER_SECOND` (default 1) per running app, one request in flight, identical
  concurrent requests share one upstream call (single flight), and the cache answers repeats. No prefetching, no
  background refresh. SEC's limit is 10 requests per second for all machines together; a class on one public IP
  must default to fixtures and caches (say so in the README and in the "Live" option's help text).
- 20 s timeout. On 429/503: honour `Retry-After` (seconds or HTTP date), capped at 30 s, at most 2 retries with
  backoff (2 s, 4 s when no header); then `503 sec_rate_limited` with `details.retry_after`. On 403: no retry,
  `502 sec_refused`. Never bypass a refusal or disguise automated traffic. SEC 404 → `404 company_not_found`.
- Cache TTL 24 h; a response served from the cache is labelled `CACHED · retrieved <date>` (when a response
  combines several sources, the oldest `retrieved_at` is shown).

**Company Facts is not a ready-made statement.** Render labelled, normalized summaries, never a supposedly exact
reproduction. Rules (Q23–Q30):

- **Duration vs instant:** income-statement and cash-flow concepts are durations (`start` and `end`); balance-sheet
  concepts are instants (`end` only). Annual durations last 350–380 days inclusive, so 52/53-week years count;
  quarterly (about 91 days) and year-to-date durations are never mixed into annual series. An instant belongs to a
  period only if its `end` equals the period's `end` exactly (two days later is not used).
- **Never group by `fy` alone** (or `fp`): they describe the filing; a later 10-K repeats earlier periods.
- **Forms:** annual series use only facts with `form` `10-K` or `10-K/A`.
- **Duplicates and restatements** (deterministic, documented in `examples/sec-analytics/CLAUDE.md` and
  `logic/periods.py`): group by (concept, unit, start, end); keep the latest `filed`; tie → higher accession;
  never sum; keep the chosen fact as provenance. The view states "Values may reflect later restatements; not
  point-in-time."
- **Periods shown:** the annual periods are the distinct (start, end) pairs of the revenue and net income facts
  that pass the rules; when two pairs share an `end`, keep the one from the latest filed fact (tie: higher
  accession). Show the latest N (5–10). Label `FY<year of end>` with the end date.
- **Units:** one reporting currency per company (the ISO currency unit with most annual revenue facts). Other units
  are ignored, never converted. A ratio whose inputs have different units is `unavailable` ("units differ").
- **Reported vs derived:** `kind: "reported"` with full provenance (concept, taxonomy, unit, start, end, fiscal
  dates `fy`/`fp`, form, accession, filed, source URL) or `kind: "derived"` with `formula` and `inputs`.
- **Concept mapping** (priority order, the first present per period wins, alternates never summed; confirm against
  fixtures): revenue `Revenues` → `RevenueFromContractWithCustomerExcludingAssessedTax` → `SalesRevenueNet` →
  `RevenueFromContractWithCustomerIncludingAssessedTax` (concept shown; a change between years is flagged);
  operating income `OperatingIncomeLoss`; net income `NetIncomeLoss`; income tax `IncomeTaxExpenseBenefit`;
  interest expense `InterestExpense` then the alternates found in the fixtures; D&A
  `DepreciationDepletionAndAmortization` → `DepreciationAndAmortization` (→ the alternate found, if any); operating
  cash flow `NetCashProvidedByUsedInOperatingActivities`; capex `PaymentsToAcquirePropertyPlantAndEquipment`
  (a positive payment); assets `Assets`; current assets `AssetsCurrent`; liabilities `Liabilities` (never derived
  from other lines); current liabilities `LiabilitiesCurrent`; equity `StockholdersEquity`; debt components
  `LongTermDebtNoncurrent`, `LongTermDebtCurrent`, and short-term `CommercialPaper` if reported for that date,
  else `ShortTermBorrowings` (never both).
- **Formulas** (exact; `unavailable` when any input is missing, `null` value, reason stated):
  - Revenue growth = (current − prior) ÷ prior; prior missing → unavailable "prior year missing"; prior ≤ 0 →
    `not_meaningful` "n/m: prior value ≤ 0".
  - Operating, net and FCF margin = operating income, net income or FCF ÷ revenue; revenue missing → unavailable;
    revenue = 0 → unavailable "denominator is zero"; revenue < 0 → unavailable "revenue ≤ 0".
  - FCF = operating cash flow − capex (reporting currency).
  - EBIT = net income + income tax expense + interest expense; EBITDA = EBIT + D&A. Both `derived`, never replaced
    by operating income; unavailable if any input is missing.
  - Working capital = current assets − current liabilities at fiscal year-end; negative values shown as they are.
  - Debt = sum of the debt components reported at that date; if none is reported → unavailable "no debt concept
    reported" (never 0); the tooltip lists the components found and those not reported.
  - Debt-to-equity = debt ÷ equity; equity 0 → unavailable "denominator is zero"; equity < 0 → `not_meaningful`
    "n/m (negative equity)" with the raw inputs in the tooltip.
  - ROE = net income ÷ average(beginning, ending) equity; ROA = net income ÷ average(beginning, ending) total
    assets. Beginning = the prior annual period's ending balance. If the prior balance is missing, use the ending
    balance and label it "ending balance (prior year unavailable)". Unavailable if net income or the ending balance
    is missing, or the denominator is 0. Average equity < 0 → "n/m (negative equity)". Interpretation note in the
    tooltip and in CLAUDE.md: with negative equity, ROE and debt-to-equity do not measure return or leverage in
    the usual way, so they are not shown as numbers.
- **Not computed:** market valuation metrics (P/E, EV, market cap, dividend yield) because there is no market-price
  source; per-share metrics; any currency conversion or calendar alignment.
- **Missing is null**, never 0, in the API, the tables, the charts and the tooltips.

## 8. No-interview defaults

Do not interview the owner; decisions are in [docs/PRODUCT-DECISIONS.md](../../docs/PRODUCT-DECISIONS.md) and
`milestones/*.md`. Never re-decide what is recorded. Defaults for unspecified reversible details (list them in the
Handoff and, if they matter to others, in the architecture decision log as "routine technical choice under
delegation"):

- Metric ids: `revenue`, `revenue_growth`, `operating_income`, `operating_margin`, `net_income`, `net_margin`,
  `income_tax`, `interest_expense`, `ebit`, `ebitda`, `d_and_a`, `operating_cash_flow`, `capex`, `fcf`,
  `fcf_margin`, `assets`, `assets_current`, `liabilities`, `liabilities_current`, `equity`, `debt`,
  `working_capital`, `debt_to_equity`, `roe`, `roa`.
- Statement grouping: income (revenue, operating income, income tax, interest expense, net income, EBIT, EBITDA);
  balance (assets, current assets, liabilities, current liabilities, equity, debt components, debt, working
  capital); cash flow (operating cash flow, capex, FCF, D&A); ratios (growth, the three margins, debt-to-equity,
  ROE, ROA).
- Explorer default selection: revenue and net margin.
- Ratios are decimals in the API (0.25), shown as percentages or `×` by `lib/format.ts`.
- Exact strings: as in this prompt and [acceptance.md](../acceptance.md).
- A test or design choice the documents leave open: pick the smallest option that meets the criterion.

If genuinely blocked (the mapping cannot be verified, a check fails twice after two different fixes, or something
needs money, a secret, personal data or new scope): record it with evidence in `milestones/plan.md` "Known
problems" and in the Handoff, and continue the independent work.

## 9. Tests and verification

Failing test first for every logic change; expected values from [acceptance.md](../acceptance.md) (hand working),
never from the code's output. No test reaches the network (respx with no pass-through; fake clock and sleep).

**pytest:**

- `test_metrics_known_answers.py`: CALC1–CALC10 exactly (CALC9 ± 0.000001) from the `SYNTHETIC` Example Co inputs;
  EBIT 200 ≠ operating income 250; `FX5`+ fixture known answers for Apple and Microsoft.
- `test_periods_m2.py`: M2-E1 missing revenue tag (revenue `missing`, margins and growth `unavailable`, reason
  given); M2-E2 alternate revenue concepts (each year its own concept, never a sum, change flagged); M2-E3 10-K vs
  later 10-K/A (1,010, not 2,010; provenance the 10-K/A); M2-E4 same-date tie (higher accession, every run); M2-E5
  comparative period placed by `start`/`end`, not `fy`; M2-E6 durations 364/371/350/380 in, 349/381/91/273 out;
  M2-E7 `USD` and `EUR` facts (only the reporting currency; `USD` over `shares` → unavailable "units differ");
  M2-E11 instant two days after period end not used.
- `test_metrics_edges.py`: M2-E8 zero denominators (revenue 0, equity 0, average assets 0 → unavailable
  "denominator is zero", never ∞ or 0); M2-E9 negative equity (−100, debt 300, net income 150 → "n/m (negative
  equity)", inputs listed); M2-E10 growth with prior −20 or 0 (n/m, "prior value ≤ 0"); debt with no component →
  unavailable; ROE fallback label (CALC10).
- `test_sec_client_m2.py`: M2-AC9 five identical concurrent requests → one upstream call, calls ≥ 1 s apart, the
  next request served from the cache labelled `CACHED · retrieved <date>`; M2-E12 429 with `Retry-After: 5` then 200
  (waits ≥ 5 s, ≤ 2 retries); 403 → no retry, `sec_refused`; timeout → `sec_unavailable`; M2-E13 redirect to
  `https://example.com/` or a non-allowlisted SEC path → `upstream_not_allowed`, no request made; missing
  `SEC_USER_AGENT` → `sec_contact_not_configured`.
- `test_cache.py`: TTL expiry with an injected clock; corrupt file ignored; atomic write; key is the URL hash.
- `test_api_m2.py`: `/api/metrics` catalog; `/financials` for Apple in demo (≥ 5 periods, headings, notes, every
  value has provenance or formula, M2-AC4, M2-AC6); `/metrics` with `ids=net_margin,fcf` and 422
  `unknown_metric`; 422 `invalid_years` for 4 and 11; `source=live` under `DATA_MODE=fixtures` → 409
  `live_disabled`; live search for `NVDA` with a respx-mocked ticker file → `LIVE` label (M2-AC1); live without the
  setting → 503 naming `SEC_USER_AGENT` (M2-AC2); mocked SEC 503/timeout → 502 `sec_unavailable` and no silent
  demo data (M2-AC3); a synthetic period without revenue → `MISSING · no mapped revenue concept` and dependent
  ratios unavailable (M2-AC8).
- All M1 tests still pass.

**Vitest:** `lib/format.test.ts` (percent, `×`, `n/m`, unavailable text); `lib/source.test.ts` (default demo, URL
param kept); `components/ValueCell.test.tsx` (ok, missing, unavailable, not meaningful each render a text label).

**Playwright** (`fe/e2e/m2-financials.spec.ts`; fixture mode; `page.route` may mock `/api/*` responses for states
the fixture backend cannot produce, and such tests are named "(mocked backend)"):

1. Apple → statements show ≥ 5 columns headed `FY<year> (ends YYYY-MM-DD)` and the restatement note (M2-AC4).
2. Explorer: select net margin and FCF → both charts visible with a zero baseline; "Show data" lists a missing year
   as `MISSING`, not 0 (M2-AC5).
3. Hover and focus revenue for one year → tooltip with concept, taxonomy, unit, start–end, form, accession, filing
   date, source link; a derived value shows its formula and inputs (M2-AC6).
4. (mocked backend) `meta.live_available` true and live search returning `sec_contact_not_configured` → the exact
   "Live SEC data is not configured…" message; switching back to Demo works (M2-AC2).
5. (mocked backend) live company request returning `sec_unavailable` → error panel with "Use recorded demo data";
   the mode stays Live until the button is pressed (M2-AC3).
6. No request leaves `127.0.0.1`/`localhost`; screenshots of the Apple statements and explorer at 1440×900, 1366×900
   and 390×844 (`fe/test-results/m2-<screen>-<width>.png`); at 390 px no sideways page scroll.
7. The M1 journeys still pass.

**Gate:**

1. `npm run check-toolkit` exits 0.
2. `npm run verify` exits 0 offline.
3. `npm run demo` works with no `.env`, no keys, no network (no mode selector; demo badge; statements load).
4. Open and inspect every new screenshot; list them and what you checked.
5. **Live SEC smoke (separate, optional):** only if `SEC_USER_AGENT` is configured in the environment, run
   `be/.venv/bin/python be/scripts/live_sec_smoke.py` (Windows: `be\.venv\Scripts\python.exe`), and, if possible,
   `npm run dev` → Live → search `NVDA` → open it. Report "live SEC: passed/failed on <date>" or "live SEC: not run
   (SEC_USER_AGENT not configured)". It never replaces the offline gate.

## 10. Acceptance criteria (from [acceptance.md](../acceptance.md))

- [ ] M2-AC1 Live search for `NVDA` uses the SEC ticker map through the backend, labelled `LIVE · retrieved <time>`;
  the browser makes no request to sec.gov.
- [ ] M2-AC2 Without `SEC_USER_AGENT`, Live shows "Live SEC data is not configured: set SEC_USER_AGENT (see
  .env.example and docs/SETUP.md)"; Demo still works.
- [ ] M2-AC3 SEC 503/timeout → "SEC is unavailable" panel with "Use recorded demo data"; the mode never changes by
  itself.
- [ ] M2-AC4 Apple's income, balance and cash-flow summaries show ≥ 5 annual columns headed
  `FY<year> (ends YYYY-MM-DD)` with the restatement note.
- [ ] M2-AC5 The explorer shows net margin and FCF by fiscal year with a zero baseline; missing years are gaps.
- [ ] M2-AC6 Tooltips show full provenance for reported values and formula plus inputs for derived values.
- [ ] M2-AC7 Ratio functions return exactly CALC1–CALC10.
- [ ] M2-AC8 A period without a revenue concept shows `MISSING · no mapped revenue concept` and dependent ratios
  `unavailable`.
- [ ] M2-AC9 Five identical requests → one SEC call, ≥ 1 s spacing, cached repeat labelled `CACHED`.
- [ ] M2-E1–M2-E13 as listed in acceptance.md.
- [ ] All M1 criteria still pass; V1–V3 screenshots inspected.

Update the statuses in `milestones/acceptance.md` and the slices and progress log in `milestones/plan.md`.

## 11. Out of scope

- Later milestones: filing metadata and history, the filing reader, sanitization, section navigation and text
  search (M3); multi-company comparison, indexing and CSV export (M4); the AI analyst and any OpenRouter code (M5).
  No navigation or placeholders for them.
- Excluded everywhere (GOAL.md): accounts, payments, uploads, PostgreSQL or any database server, SQLite, a vector
  database, a Docker prerequisite, Streamlit, hosted deployment, SEC bulk archives (`companyfacts.zip`,
  `submissions.zip`), the frames API, prefetching or background refresh, an arbitrary URL proxy, non-SEC companies,
  market prices and valuation metrics, currency conversion, calendar alignment, invented descriptions, light mode as
  a done criterion.
- Do not edit `milestones/*/PROMPT.md`, `FOLLOWUPS.md`, the toolkit (`.claude/`, `scripts/`, `scaffold/`,
  `AGENTS.md`, `CLAUDE.md`, `docs/TOOLKIT.md`), `GOAL.md`, `PROGRESS.md`, `runs/` or the fixtures. The milestone
  README's "Results" section is filled in by the owner after the checkpoint.

## 12. Handoff

Do not commit, tag, push or change Git configuration: the owner integrates, commits and creates the `m2`
checkpoint. Never read, create, print or commit `.env` files, keys or contact data.

End your final message with exactly this block (docs/TOOLKIT.md §7):

```
## Handoff
Changes: <files created or changed, grouped by folder>
Verification evidence: <each command with its exit code and summary line; screenshots looked at; live SEC smoke reported separately>
Remaining findings: <blockers, unverified items, mapping results, defaults chosen, deviations and why>
Next action: <one line>
```
