# Product: SEC Analytics (App Creator example)

Status: agreed on 2026-11-03 (delegated, see [docs/PRODUCT-DECISIONS.md](../docs/PRODUCT-DECISIONS.md))

`(assumption Q<n>)` marks a delegated assumption: a routine, reversible default that GOAL.md did not settle. Other
items are explicit instructor requirements (GOAL.md section given). This file is about the SEC example only.

## Problem and customers

- **Customer:** a business-school student inspecting a prepared version of the app in class. The instructor runs
  the demo. Rebuilding a milestone from its prompt is a secondary path (GOAL.md §1).
- **Problem today:** to find a company's annual figures, their periods and their sources, students read EDGAR filings
  and raw Company Facts JSON by hand. They also cannot see how an AI-assisted app is built, step by step
  (assumption Q2).
- **Success looks like:** the instructor checks out each milestone tag, runs `npm run demo` and finishes a
  three-minute demonstration offline with no errors. Every number shown has a visible source and period, and missing
  data is shown as missing (GOAL.md §4, §9).

## Main user journey (cumulative over the five milestones)

1. **M1.** The student presses `/`, types "apple", "AAPL" or "320193" and opens Apple Inc. They see the profile and
   identifiers, plus a small dashboard labelled `RECORDED SEC DEMO · snapshot <date>`. A note says search covers only
   the three demo companies.
2. **M2.** On the company page they see a key-figure strip, a revenue and net income chart, and income, balance and
   cash-flow summary tables for 5–10 fiscal years. They pick metrics in the explorer and hover any number to see its
   formula, SEC concept, period and filing. In `npm run dev` they can switch the header selector to Live.
3. **M3.** Under the company's Filings view they open the latest 10-K in the snapshot. The reader shows a section
   list and a search box, and links to the source document on sec.gov (assumption Q6).
4. **M4.** On Compare they add 2–4 companies, choose metrics, optionally index absolute values to 100, and export
   exactly the shown data as CSV (assumption Q7).
5. **M5.** They open the analyst panel, paste their own OpenRouter key (kept in memory), pick a model and ask "Why did
   net margin change?". The answer cites facts and filing passages by source id, with dates and periods
   (assumption Q8).

## Screens and visuals

Look: a dense dashboard in a modern Bloomberg-inspired **dark navy terminal** style: readable tables, tabular
numerals, restrained accents, compact navigation, no decorative card grids (GOAL.md §5). Used on a phone: the
layout must work at 390 px (assumption Q14). Theme: dark is required. Light mode is not a done criterion of any
milestone; it may come after all M5 criteria pass (assumption Q15). Visual reference: a financial terminal, dense but
calm.

| Screen | From | Purpose | The user sees first | Cards / charts / tables | The user can | States |
|---|---|---|---|---|---|---|
| Header (all screens) | M1 | navigation, mode | search box, mode badge (`RECORDED SEC DEMO` / `LIVE` / `CACHED`) | – | focus search with `/` or Ctrl/Cmd-K; switch Demo/Live in `npm run dev` from M2 (assumption Q13, Q22) | live not configured (message names the setting) |
| Home / search | M1 | find a company | search box, demo-universe note | results list (name, ticker, CIK) | type, arrow keys, Enter, Esc | no match, backend down |
| Company overview | M1, extended in M2 | key figures and statements | key-figure strip (assumption Q9, Q10) | strip: latest annual revenue, YoY revenue growth, net income, net margin, operating cash flow, FCF, debt-to-equity, each with fiscal year-end, unit, reported/derived badge; line chart "Revenue and net income, USD, by fiscal year"; statement tables | choose years (5–10), open provenance tooltips | loading, missing values (`MISSING · <reason>`), unavailable ratio with reason |
| Metric explorer | M2 | trend of chosen metrics | metric selector and line chart | line chart per metric, zero baseline visible, gaps for missing years (assumption Q11) | select metrics and years | metric unavailable for some years |
| Filings | M3 | find a report | latest 10-K and 10-Q (`Latest in snapshot (as of <date>)` in demo) | history table: form, amendment label, filing date, period, link | open a filing | history limited to the snapshot (labelled) |
| Filing reader | M3 | read a filing | section list and text | sanitized text, sections labelled "detected automatically; may be imperfect" | jump to a section, search the text, open the source on sec.gov | "Section boundaries not detected; showing full text" (assumption Q41) |
| Compare | M4 | compare 2–4 companies | company chips and metric selector | table and chart with each company's fiscal year-end and unit; grouped bars for one year, lines for trends | add/remove companies, choose metrics, toggle "Index = 100 at first common fiscal year", Export CSV (assumption Q32, Q33) | fewer than 2 / more than 4, currency mismatch warning |
| Analyst panel | M5 | grounded Q&A | context line, e.g. "Context: AAPL facts FY…–FY… + 10-K passages" | answer with numbered source chips | set key (memory), opt in to session storage, choose model, test connection, ask, cancel, clear key | AI not configured, key invalid, out of credits, rate limited, timeout, unsupported question |

Data-source labels are text badges, never colour alone: `LIVE · retrieved <time>`, `CACHED · retrieved <date>`,
`RECORDED SEC DEMO · snapshot <date>`, `MISSING · <reason>` (GOAL.md §4; wording assumption Q12). Navigation to a later
milestone's screen is left out entirely until that milestone (assumption Q18).

## MVP features (must have), per milestone

| Id | Feature (what the user can do) | Why | Criteria |
|---|---|---|---|
| M1-F1 | Use a polished dark shell with stable launch scripts | the classroom demo must start reliably | M1-AC1, M1-AC6 |
| M1-F2 | Search the demo universe by name, ticker or CIK (any zero-padding) | find a company quickly | M1-AC2, M1-AC3 |
| M1-F3 | See profile and identifiers | know which filer this is | M1-AC4 |
| M1-F4 | See a basic dashboard labelled as recorded SEC demo data | first look at real numbers, honestly labelled | M1-AC5 |
| M2-F1 | Look up any SEC filer live (backend adapters, explicit Live mode) | beyond the demo universe, still SEC only | M2-AC1, M2-AC2, M2-AC3, M2-AC9 |
| M2-F2 | Read annual income, balance and cash-flow summaries for 5–10 years | the core financial view | M2-AC4 |
| M2-F3 | Explore metrics in a chart | see trends | M2-AC5 |
| M2-F4 | See provenance and calculated ratios (formula tooltips) | trust and teaching | M2-AC6, M2-AC7, CALC1–CALC10 |
| M2-F5 | See missing data stated explicitly | never mistake missing for zero | M2-AC8, M2-E1–M2-E11 |
| M3-F1 | See the latest 10-K and 10-Q metadata and history with amendment labels | find the right report | M3-AC1, M3-AC2 |
| M3-F2 | Read the actual filing text, safely sanitized, with section navigation | read without raw HTML risks | M3-AC3, M3-AC4 |
| M3-F3 | Search the text and open the source | verify against sec.gov | M3-AC5, M3-AC6 |
| M3-F4 | See a documented fallback when sections are not detected | honest about extraction limits | M3-AC7 |
| M4-F1 | Compare 2–4 companies on selectable metrics | peer analysis | M4-AC1, M4-AC2 |
| M4-F2 | See fiscal dates, units and currencies, never silently aligned | comparability | M4-AC3, M4-AC4 |
| M4-F3 | Toggle clearly labelled indexing | compare growth paths | M4-AC5, CALC11 |
| M4-F4 | Export exactly the shown data as CSV | use it in a spreadsheet | M4-AC6, M4-AC7 |
| M5-F1 | Configure OpenRouter optionally (masked key, model list or manual id, test, clear) | the AI is opt-in and student-paid | M5-AC1, M5-AC2, M5-AC3 |
| M5-F2 | Ask grounded questions on company, filing and comparison screens | explanation with sources | M5-AC4, M5-AC5, M5-AC6 |
| M5-F3 | Have failures handled gracefully, with every non-AI feature working without a key | the class never breaks because of AI | M5-AC7, M5-AC8 |

Each milestone keeps all earlier behaviour and works as an independent checkout (GOAL.md §5).

## Explicitly not in the MVP

From GOAL.md §1, §4, §5, §6 and §7 (Q17, Q34), plus delegated exclusions:

- PostgreSQL or any database server, SQLite (not needed: assumption Q35), accounts, payments, uploads, a vector
  database, hosted services, a Docker prerequisite, Streamlit, cloud deployment.
- Market prices, valuation metrics (P/E, market cap), invented company descriptions.
- Currency conversion and calendar alignment across companies.
- SEC bulk archives, prefetching, an arbitrary URL proxy, non-SEC companies.
- 8-K and other forms in the filing history (assumption Q42); a fourth demo company (assumption Q19).
- Storing the OpenRouter key in localStorage, on the server or in any file; a hardcoded default model.
- Investment advice or price forecasts from the analyst (assumption Q43).
- Light mode as a done criterion (assumption Q15).

## Data and calculations

| Data | Source | Freshness | Offline demo data (fixtures) | Terms checked? |
|---|---|---|---|---|
| Ticker ↔ CIK map | `www.sec.gov/files/company_tickers.json` | live, cached 24 h (assumption Q35) | the 3 entries for AAPL, MSFT, GOOGL | SEC fair access: declared User-Agent, ≤ 10 req/s ([research](../docs/research/sec-edgar.md) §5) |
| Company metadata, filing list | `data.sec.gov/submissions/CIK##########.json` (+ older pages when needed) | live, cached 24 h | trimmed to 10-K/10-Q entries | same |
| Financial facts | `data.sec.gov/api/xbrl/companyfacts/CIK##########.json` | live, cached 24 h | trimmed to mapped concepts, values unmodified, ≥ 5 annual periods (assumption Q20) | same |
| Filing documents | `www.sec.gov/Archives/edgar/data/<cik>/<accession>/<document>` | immutable per accession, cached until deleted | excerpts of the latest 10-K and 10-Q primary documents, trimming recorded | same |
| AI answers | OpenRouter, the student's own key | per request, never stored | none: mocked in tests | OpenRouter docs ([research](../docs/research/openrouter.md)) |

Fixtures are authentic SEC snapshots with a manifest (source URL, retrieval date, accession, periods, scope). If they
cannot be fetched, the limitation is reported and no values are manufactured. Synthetic data appears only in tests,
isolated and marked (GOAL.md §4, Q21).

| Number the app shows | Formula | Units | Known-answer example |
|---|---|---|---|
| Revenue growth (YoY) | (current − prior) ÷ prior; n/m if prior ≤ 0 or missing | % | CALC1 |
| Operating, net, FCF margin | operating income, net income or FCF ÷ revenue; unavailable if revenue ≤ 0 or missing | % | CALC2, CALC3, CALC4 |
| FCF | operating cash flow − capex | reporting currency | CALC4 |
| EBIT, EBITDA (derived) | net income + income tax + interest expense; EBIT + D&A; never operating income | reporting currency | CALC5 |
| Working capital | current assets − current liabilities | reporting currency | CALC6 |
| Debt-to-equity | (noncurrent LTD + current LTD + short-term borrowings/commercial paper) ÷ equity | × (times) | CALC7 |
| ROE, ROA | net income ÷ average(beginning, ending) equity or assets; labelled ending-balance fallback | % | CALC8, CALC9, CALC10 |
| Index (M4) | value ÷ value at first common fiscal year × 100 | index points | CALC11 |

The rules (Q23–Q30, Q32) and the concept mapping are in [architecture.md](architecture.md#financial-data-rules), and
the worked examples are in [acceptance.md](acceptance.md#calculations-known-answers).

## Capabilities

| Capability | Needed? | Notes |
|---|---|---|
| Accounts / sign-in | no | GOAL.md §4 |
| Per-user saved data | no | only the OpenRouter key and model, in browser memory or opt-in sessionStorage (Q36) |
| File uploads | no | assumption Q34 |
| Payments | no | GOAL.md §4 |
| Background jobs / scheduled refresh | no | no prefetching (Q38) |
| Disk cache | yes, from M2 | git-ignored SEC response cache (Q35) |
| Works offline (`npm run demo`) | yes, every milestone | recorded SEC demo data, clearly labelled |
| Must be online for others | no | local teaching app; no cloud deployment (GOAL.md §1) |

## Team and constraints

- Mode: delegated by [GOAL.md](../GOAL.md) §1 and §8; decisions in [docs/PRODUCT-DECISIONS.md](../docs/PRODUCT-DECISIONS.md).
- Builders: AI agents dispatched as recorded steps (`runs/`), integrated by the owner session. Students read the result.
- Platforms: macOS and Windows; Node ≥ 22.13, Python 3.10–3.13 (Q39).
- Budget: zero. No paid service. OpenRouter is optional and paid by the student's own limited key; paid live AI
  validation is not delegable (N1).
- Rules: SEC fair access (declared contact User-Agent set by the owner locally, conservative throttling); never commit
  keys or contact data; finance rules stay with the example, not in the generic toolkit (docs/TOOLKIT.md §8).
