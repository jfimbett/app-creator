# M4 Comparative analysis: build brief

This is the exact implementation brief for SEC Analytics milestone 04. Give it, unchanged, to the assistant or agent
that implements the milestone. It is immutable once the `template-v1` checkpoint exists. Corrections that change
the implementation go into [FOLLOWUPS.md](FOLLOWUPS.md) before they are dispatched.

Paths are relative to the repository root unless stated. `fe/` means `examples/sec-analytics/frontend/` and `be/`
means `examples/sec-analytics/backend/`.

---

## 1. Starting ref

- **Start from tag `m3`** (the verified M3 Filing intelligence checkpoint).
- A student rebuilding this milestone, in a **clean checkout** (`git status` clean; stop any running
  `npm run dev`/`demo` first):

  ```bash
  git fetch origin --tags
  git switch -c exercise/build-m4 m3
  npm ci
  npm run setup
  ```

- Check the start: `git merge-base --is-ancestor m3 HEAD` exits 0, `git log --oneline m3..HEAD` is empty, and
  `npm run verify` exits 0 before you change anything (otherwise record it as a finding first).
- The completed `m4` tag is **for inspection** (`git switch --detach m4`). Do not run this prompt on an `m4`
  checkout. Replaying the prompt will not produce identical code; the `m4` tag is the reference version.

## 2. Context: what exists at `m3`

Read the code before planning; where it differs from this summary, the code and the statuses in
`milestones/acceptance.md` win, and you record the difference.

- **Toolkit** as at `template-v1`, plus `.claude/agents/sec-data-specialist.md`.
- **Config:** app in `examples/sec-analytics/`, `docsDir` `milestones`, `devEnv` `{"DATA_MODE": "live"}`, `demoEnv`
  `{"DATA_MODE": "fixtures"}`.
- **Example rules:** `examples/sec-analytics/CLAUDE.md` and the nested skill
  `examples/sec-analytics/.claude/skills/sec-edgar-data/SKILL.md`. Read both now.
- **Fixtures:** authentic AAPL, MSFT, GOOGL snapshots: ticker entries, trimmed submissions (and any older page),
  Company Facts for the captured concepts, the latest 10-K and 10-Q primary documents (gzip), `manifest.json`.
- **Backend:** SEC client (allowlist, manual redirects, User-Agent, 1 req/s, single flight, timeouts, Retry-After,
  no 403 retry), disk cache, `data/source.py` (`source=demo|live`); logic `cik`, `search`, `concepts`, `periods`
  (annual 350–380 days, instants at period end, 10-K/10-K/A, duplicate policy, single reporting currency),
  `statements`, `metrics` (growth, margins, FCF, EBIT/EBITDA, working capital, debt, debt-to-equity, ROE/ROA with
  status and reasons), `filings`, `archive`, `sanitize`, `sections`; endpoints `/api/health`, `/api/meta`,
  `/api/companies/search`, `/api/companies/{cik}`, `/overview`, `/api/metrics`, `/financials`, `/metrics`,
  `/filings`, `/filings/{accession}`.
- **Frontend:** dark navy terminal shell, keyboard search, Demo/Live selector (dev only), source badges, company
  page with tabs Overview (profile, key figures, chart, statements, ratios, metric explorer, provenance tooltips) and
  Filings (latest with `Latest in snapshot (as of <date>)`, history with `AMENDMENT` labels, sanitized reader with
  sections, search and Source link); Playwright specs for M1–M3 at 1440, 1366 and 390 px.
- **Planning:** [GOAL.md](../../GOAL.md) §5–§6, [docs/PRODUCT-DECISIONS.md](../../docs/PRODUCT-DECISIONS.md)
  (Q7, Q11, Q19, Q32, Q33), [milestones/architecture.md](../architecture.md) ("Comparison", API rows M4),
  [milestones/acceptance.md](../acceptance.md) (M4 rows, CALC11, M4-E1–M4-E3), [milestones/plan.md](../plan.md)
  (slices 4.1–4.3).

All M1–M3 behaviour must keep working.

## 3. Goal and new work

GOAL.md §5, row 04: compare 2–4 companies; selectable revenue, growth, margin, leverage and cash-flow metrics;
comparable tables and charts with fiscal dates and units; clearly labelled indexing or normalization; CSV export.

1. **Compare screen** at `/compare`, reached from a new header link **Compare** (the only new navigation). The state
   lives in the URL: `/compare?ciks=0000320193,0000789019&metrics=revenue,net_margin&years=10&index=none&source=demo`,
   so a reload or a shared link shows the same comparison.
2. **Company chips** (Q7): a search box (the same combobox as the header, scoped to the current source: the demo
   universe in Demo, the SEC ticker file in Live) adds a company as a chip; each chip has a remove button. The rule
   is 2–4 companies: adding a fifth is refused with "Compare 2–4 companies"; adding a company already present is
   ignored with "Already in the comparison"; with fewer than 2, no table or chart is drawn and the screen says
   "Add at least 2 companies to compare". Offline the demo universe has 3 companies, so the 4-company limit is shown
   by tests and in Live (Q19).
3. **Metric selector:** 1–6 metrics from this comparison set: `revenue`, `revenue_growth`, `operating_margin`,
   `net_margin`, `operating_cash_flow`, `fcf`, `fcf_margin`, `debt_to_equity`. Default: `revenue`, `net_margin`.
   Years 5–10 (default 10).
4. **Table:** one row per company × metric, one column per fiscal year label, with each cell showing the value and,
   beneath or in its tooltip, that company's own period end date; columns are labelled by fiscal year label, not by
   calendar year. A header line under the title states each company's fiscal year-end (for example "Apple: FY ends
   <MM-DD> · Microsoft: FY ends <MM-DD>", filled from the data), and the legend states **"Fiscal years are not
   aligned"** whenever the companies' year-end dates differ. Units in every row (`USD millions`, `%`, `×`). Missing
   and unavailable values show their reason as in M2.
5. **Charts** (Q11): for the metric chosen in a metric tab row, a line chart of each company over fiscal year labels
   (trends) and a grouped bar chart for one selected fiscal year label (default: the latest label all companies
   share). Zero baseline visible, negative values below it, missing values are gaps or absent bars, never zero.
   Tooltips show company, fiscal year label, period start–end, value, unit and whether the value is reported or
   derived.
6. **Indexing** (Q32): a toggle **"Index = 100 at first common fiscal year"** for absolute currency metrics
   (`revenue`, `operating_cash_flow`, `fcf`). Each company is indexed on its own fiscal years:
   value ÷ value at the base year × 100, where the base year is the first fiscal year label in the selected window
   for which every selected company has a value. The label lists each company's fiscal year-end and base period end
   date. Ratios and percentages are never indexed and are shown as they are (the table says "not indexed:
   ratio"). No common label → the toggle is disabled with "No common fiscal year to index from". A base value ≤ 0
   or missing for a company → that company's indexed values are unavailable with the reason.
7. **Currencies:** each company keeps its reporting currency; nothing is converted. If an absolute currency metric
   has different currencies across the selected companies, no shared axis is drawn for it and the warning
   "Different reporting currencies (USD, EUR): not converted" appears (listing the actual currencies); the table
   still shows each value with its own unit; ratios are still compared.
8. **Export CSV** (Q33): a button "Export CSV" downloads `/api/compare.csv` with the same parameters, built on the
   server from the same comparison result the table shows, so the file holds exactly the shown data points in the
   same order.

## 4. Design

Keep the M1–M3 look and extend it.

- **Dark navy terminal** tokens (background `#0A1020`, panels `#0F1A2E`/`#14223B`, border `#1F2E4A`, text
  `#DCE3EE`, muted `#8C9AB3`, amber accent `#F2B33D`, link `#6CB6FF`, warning `#E8A33A`; contrast ≥ 4.5:1). Dark is
  the done criterion; light mode stays out.
- **Compare layout:** a toolbar row (company chips + add box, metric multi-select, years, index toggle, Export CSV),
  then the warnings line, then the table, then the chart panel with metric tabs and a "Trend / One year" switch.
  Dense, aligned, tabular numerals; no card grid.
- **Company series colours:** four fixed, distinguishable colours (`#6CB6FF`, `#F2B33D`, `#3FB68B`, `#C792EA`),
  always paired with the ticker in the legend, the tooltip and the table row, so colour is never the only cue.
- **Labels and badges:** source badge per panel (`RECORDED SEC DEMO · snapshot <date>`, `LIVE · retrieved <time>`,
  `CACHED · retrieved <date>`); `INDEXED` text badge on indexed rows and on the chart title ("Revenue, index = 100
  at FY<year> (Apple ends <date>; Microsoft ends <date>)", dates taken from the data); "Fiscal years are not aligned"; currency warning
  in the warning colour with an icon and text.
- **States:** fewer than 2 companies; a fifth refused; duplicate ignored; a company with no data for a metric; live
  errors with "Use recorded demo data"; export in progress / failed.
- **Responsive** at 1440, 1366 and 390 px: at 390 px the toolbar stacks, chips wrap, the table scrolls inside its
  container with a sticky first column, the chart keeps legible labels; no sideways page scroll.
- **Honesty:** no calendar alignment, no conversion, no prices or valuation metrics, no navigation to the Analyst
  (M5), no control that does nothing.

## 5. Architecture and files

Follow [milestones/architecture.md](../architecture.md): comparison and CSV logic are pure functions; the API
validates and calls them; the frontend draws what it receives.

| Path | Change |
|---|---|
| `be/app/logic/compare.py` | `compare(companies, metric_series, years, index)`: rows in a fixed order, fiscal-year-end and currency warnings, index base per company, indexed values with status and reason |
| `be/app/logic/csv_export.py` | `to_csv(result) -> str` with the exact header, formula-injection guard, empty cells for null |
| `be/app/models/compare.py` | `CompareResponse`, `CompareRow`, `CompareWarning` |
| `be/app/api/compare.py` | `GET /api/compare`, `GET /api/compare.csv` (one shared function builds the result) |
| `be/tests/...`, `be/tests/synthetic/...` | section 9 |
| `fe/app/compare/page.tsx` | the Compare screen |
| `fe/components/` | `AppHeader` (Compare link), `CompanyChips`, `MetricPicker`, `CompareTable`, `CompareChart` (lines and grouped bars), `IndexToggle`, `ExportCsvButton`, `CompareWarnings` |
| `fe/lib/compare-state.ts` | parse and serialise the URL state; the 2–4 and duplicate rules for the UI (Vitest) |
| `fe/lib/types.ts`, `fe/lib/api.ts` | new types and calls (the CSV download uses the same query string) |
| `fe/e2e/m4-compare.spec.ts` | section 9 |
| `examples/sec-analytics/CLAUDE.md`, nested skill, `examples/sec-analytics/README.md` | comparability, indexing and CSV rules |
| `milestones/acceptance.md`, `plan.md`, `architecture.md` | statuses, progress log, decision-log rows |

**API added at M4** (as in architecture.md; error envelope unchanged):

| Method and path | Request | Response | Errors |
|---|---|---|---|
| `GET /api/compare` | `ciks` (comma list, 2–4, each normalized), `metrics` (1–6 from the comparison set), `years` (5–10, default 10), `index` (`none`\|`first_common_year`, default `none`), `source` | `{companies: [{cik, ticker, name, fiscal_year_end, currency}], metrics: [str], rows: [CompareRow], index_base: {fiscal_year_by_cik: {cik: str}, period_end_by_cik: {cik: date}}\|null, warnings: [{code, message}], source}`; `CompareRow {cik, metric_id, fiscal_year_label, period_start, period_end, value: float\|null, unit, kind, status, reason, indexed: bool, source_concept: str\|null, accession: str\|null, data_source: str}` | 422 `too_few_companies`, 422 `too_many_companies`, 422 `duplicate_company`, 422 `invalid_cik`, 422 `unknown_metric`, 422 `invalid_years`, 404 `company_not_found`, 409 `live_disabled`, SEC errors as in M2 |
| `GET /api/compare.csv` | same as `/api/compare` | `text/csv; charset=utf-8`, `Content-Disposition: attachment; filename="sec-analytics-compare-<tickers>-<YYYY-MM-DD>.csv"` | same, as the JSON error envelope |

`status` and `reason` on `CompareRow` (and `period_end_by_cik` in `index_base`) extend the architecture.md shape so
missing and unavailable values keep their reason; add them to the API table and the decision log. Warning codes:
`fiscal_years_not_aligned`, `currencies_differ`, `no_common_fiscal_year`, `index_base_unavailable`. Row order (the
table and the CSV both use it): companies in the order given in `ciks`, then metrics in the order given in
`metrics`, then fiscal year ascending.

**CSV format** (M4-AC6, Q33): header exactly
`company,ticker,cik,fiscal_year_label,fiscal_year_end,period_start,period_end,metric,value,unit,kind,indexed,source_concept,accession,data_source`;
one line per `CompareRow`, in row order; `value` is the full-precision number from the API in whole currency
units, index points or a decimal ratio (never the scaled display value), and an **empty cell** when null; `unit`
says which (`USD`, `index`, `ratio`); `indexed` is `true`/`false`; written with Python's `csv` module (RFC 4180
quoting, UTF-8, `\r\n`). The **formula-injection guard** prefixes text cells that start with `=`, `+`, `-`, `@`,
tab or carriage return with a single quote `'`; numeric `value` cells are never prefixed, so negative numbers stay
numbers.

## 6. Fixtures and data

- No new fixtures. Use the M1–M3 fixtures unchanged; do not recapture.
- Fiscal year-ends for M4-AC3 are expected to differ (Apple late September, Microsoft 30 June,
  `[verify against fixtures]`): confirm from the fixture period end dates and record the result in the architecture
  decision log.
- Synthetic inputs in `be/tests/synthetic/` (each marked `SYNTHETIC`): the CALC11 "Example Co" (revenue 800 → 1,000)
  and "Sample Ltd" (revenue 50 → 40) series; a company reporting in `EUR`; a set with no common fiscal year label;
  a company whose name starts with `=` for the CSV guard; a fourth and fifth company for the 2–4 rule.
- Add a fixture-based known answer before its test: in the calculation section of `milestones/acceptance.md`, a
  row `FX` (next free number) indexing Apple's and Microsoft's revenue to the first common fiscal year label in the
  fixtures, with hand working from the fixture values already recorded (concept, accession, period, `val`).

## 7. SEC and comparability rules that apply at M4

- All data comes from the M2 pipeline: periods by `start`/`end`, annual 350–380 days, 10-K/10-K/A only, the
  duplicate/restatement policy, one reporting currency per company, reported vs derived with provenance, missing is
  null. The comparison never recomputes these in the frontend.
- **No calendar alignment:** companies are compared by their own fiscal year labels (`FY<year of end date>`), and
  each value shows its own period end. "Fiscal years are not aligned" whenever the end dates differ.
- **No currency conversion:** different reporting currencies → no shared absolute axis, the warning, values in
  their own units; ratios still compared.
- **Indexing** only for absolute currency metrics, per company, labelled with the base year and each company's
  period end; ratios are not indexed.
- **Ratios** keep M2's definitions and their `unavailable` / `n/m` statuses and reasons.
- **Live mode:** each company costs up to two SEC requests (submissions, Company Facts), throttled to 1 per second
  and cached for 24 h; a 4-company live comparison therefore takes several seconds the first time; show a progress
  state, never fire requests in parallel past the throttle, and never fall back to demo data silently.
- **CSV** contains provenance (`source_concept`, `accession`, `data_source`) and the guard above.
- No market prices or valuation metrics.

## 8. No-interview defaults

Do not interview the owner; decisions are in [docs/PRODUCT-DECISIONS.md](../../docs/PRODUCT-DECISIONS.md) and
`milestones/*.md`. Never re-decide what is recorded. Defaults for unspecified reversible details (list them in the
Handoff; record important ones in the architecture decision log as "routine technical choice under delegation"):

- `company` column = the SEC entity name as given; `ticker` = the first ticker in the submissions file;
  `fiscal_year_end` column = the row's period end date (`YYYY-MM-DD`); `data_source` = the panel label text
  (e.g. `RECORDED SEC DEMO · snapshot 2026-11-03`).
- Chart default: the first selected metric, trend view.
- Grouped-bar default year: the latest fiscal year label that every selected company has.
- Opening Compare with no `ciks` in the URL shows an empty comparison with the add box focused; it never
  auto-adds companies.
- Exact strings: as in this prompt and [acceptance.md](../acceptance.md).

If genuinely blocked (a check fails twice after two different fixes, or something needs money, a secret, personal
data or new scope): record it with evidence in `milestones/plan.md` "Known problems" and the Handoff, and continue
the independent work.

## 9. Tests and verification

Failing test first; expected values from hand working in [acceptance.md](../acceptance.md), never from the code's
output; no test reaches the network.

**pytest:**

- `test_compare.py`: CALC11 and M4-AC5 (Example Co 100.0 and 125.0, Sample Ltd 100.0 and 80.0, ± 0.05) with each
  company's own base period; ratios not indexed; M4-E1 no common fiscal year → `no_common_fiscal_year`, no indexed
  rows; base ≤ 0 → `index_base_unavailable` with reason; M4-AC3 different year-ends → `fiscal_years_not_aligned` and
  each row's own `period_end`; M4-AC4 USD and EUR → `currencies_differ` with both codes in the message, values kept
  in their own units, ratios present; row order exactly companies → metrics → fiscal year; the fixture-based `FX`
  index known answer.
- `test_csv_export.py`: M4-AC6 exact header and one line per row in the same order; M4-AC7 a null value → empty
  `value` cell, row present; M4-E2 a company name starting with `=`, `+`, `-` or `@` → prefixed with `'`; a negative
  numeric value not prefixed; quoting of commas and quotes; round trip through `csv.reader` equals the rows.
- `test_api_m4.py`: `/api/compare` for AAPL, MSFT, GOOGL in demo (M4-AC1); 422 `too_few_companies` (1),
  `too_many_companies` (5, synthetic CIKs), `duplicate_company` (M4-E3), `unknown_metric`, `invalid_years`;
  `/api/compare.csv` returns `text/csv`, the attachment header and exactly the JSON result's rows; live with
  respx-mocked SEC (throttled, cached, labelled); `source=live` under fixtures → 409.
- All M1–M3 tests still pass.

**Vitest:** `lib/compare-state.test.ts` (URL round trip; adding a fifth refused with "Compare 2–4 companies";
duplicate ignored; removing down to one clears the comparison).

**Playwright** (`fe/e2e/m4-compare.spec.ts`, fixture mode):

1. Header → Compare; add AAPL, MSFT and GOOGL; select revenue and net margin → the table and chart show each
   company's values by fiscal year (M4-AC1).
2. The legend says "Fiscal years are not aligned" and a cell tooltip shows that company's own period end (M4-AC3).
3. Remove companies down to one → no table or chart and "Add at least 2 companies to compare" (M4-AC2, UI part).
4. Toggle "Index = 100 at first common fiscal year" on revenue → `INDEXED` badge and the label listing each
   company's fiscal year-end; net margin rows say "not indexed: ratio" (M4-AC5, UI part).
5. Export CSV: `page.waitForEvent('download')`, read the file, check the exact header and that the number of data
   lines equals the number of displayed data points (M4-AC6).
6. Reload the page: the URL state restores the same comparison.
7. No request leaves `127.0.0.1`/`localhost`; screenshots of Compare (table, trend chart, indexed view) at 1440×900,
   1366×900 and 390×844 (`fe/test-results/m4-<screen>-<width>.png`); at 390 px no sideways page scroll.
8. The M1–M3 journeys still pass.

**Gate:**

1. `npm run check-toolkit` exits 0.
2. `npm run verify` exits 0 offline.
3. `npm run demo` works with no `.env`, no keys, no network: Compare AAPL, MSFT, GOOGL → index → Export CSV and open
   the file.
4. Open and inspect every new screenshot; list what you checked (chart legibility at 390 px, warnings readable).
5. **Live SEC (separate, optional):** only with `SEC_USER_AGENT` configured: `npm run dev` → Live → compare four
   companies (for example AAPL, MSFT, GOOGL, NVDA). Report "live SEC: passed/failed on <date>" or "not run
   (SEC_USER_AGENT not configured)".

## 10. Acceptance criteria (from [acceptance.md](../acceptance.md))

- [ ] M4-AC1 AAPL, MSFT and GOOGL with revenue and net margin → table and chart by fiscal year.
- [ ] M4-AC2 A fifth company is refused with "Compare 2–4 companies"; with one company no comparison is drawn; the
  API returns 422 `too_many_companies` / `too_few_companies`.
- [ ] M4-AC3 Each company's own period end is shown; the legend says "Fiscal years are not aligned".
- [ ] M4-AC4 Different currencies → no shared absolute axis, "Different reporting currencies (USD, EUR): not
  converted", ratios still shown.
- [ ] M4-AC5 Indexing gives 100.0/125.0 and 100.0/80.0 for the CALC11 inputs; the label lists fiscal year-ends.
- [ ] M4-AC6 The CSV has the exact header and exactly the shown rows in the same order.
- [ ] M4-AC7 A missing value is an empty `value` cell, never `0`, and the row is kept.
- [ ] M4-E1–M4-E3 as listed in acceptance.md.
- [ ] All M1–M3 criteria still pass; V1–V3 screenshots inspected.

Update the statuses in `milestones/acceptance.md` and the slices and progress log in `milestones/plan.md`.

## 11. Out of scope

- Later milestone: the AI analyst, OpenRouter settings and any OpenRouter code (M5). No Analyst navigation or
  placeholder.
- Also out: a fourth demo company or new fixtures (Q19); peer suggestions; saved comparisons; Excel files; charts
  of quarterly data; calendar alignment; currency conversion.
- Excluded everywhere (GOAL.md): accounts, payments, uploads, PostgreSQL or any database server, SQLite, a vector
  database, a Docker prerequisite, Streamlit, hosted deployment, SEC bulk archives, prefetching, an arbitrary URL
  proxy, non-SEC companies, market prices and valuation metrics, invented descriptions, light mode as a done
  criterion.
- Do not edit `milestones/*/PROMPT.md`, `FOLLOWUPS.md`, the toolkit (`.claude/`, `scripts/`, `scaffold/`,
  `AGENTS.md`, `CLAUDE.md`, `docs/TOOLKIT.md`), `GOAL.md`, `PROGRESS.md`, `runs/` or the fixtures. The milestone
  README's "Results" section is filled in by the owner after the checkpoint.

## 12. Handoff

Do not commit, tag, push or change Git configuration: the owner integrates, commits and creates the `m4`
checkpoint. Never read, create, print or commit `.env` files, keys or contact data.

End your final message with exactly this block (docs/TOOLKIT.md §7):

```
## Handoff
Changes: <files created or changed, grouped by folder>
Verification evidence: <each command with its exit code and summary line; screenshots looked at; live SEC reported separately>
Remaining findings: <blockers, unverified items, defaults chosen, deviations and why>
Next action: <one line>
```
