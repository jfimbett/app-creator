# SEC Analytics example: rules for this folder

These rules add to the root [AGENTS.md](../../AGENTS.md); they never relax it. They apply to everything under
`examples/sec-analytics/` (`backend/`, `frontend/`, `fixtures/`). Paths below are relative to this folder.

**How this file loads.** Claude Code loads this file, and the nested skill
[`sec-edgar-data`](.claude/skills/sec-edgar-data/SKILL.md), the first time it reads or edits a file in this folder;
they are not loaded when a session starts at the repository root. Once loaded, the skill is addressed as
`examples/sec-analytics:sec-edgar-data` ([research](../../docs/research/claude-code-and-cline.md) §1 and §4).
**Cline does not load nested `CLAUDE.md` files or nested skills automatically**: Cline users open this file and the
skill's `SKILL.md` themselves before working here.

## Where the decisions are

The planning documents of this example live in `milestones/`, not in a `docs/` folder here:
[product.md](../../milestones/product.md), [architecture.md](../../milestones/architecture.md) (API contract,
financial data rules, decision log), [acceptance.md](../../milestones/acceptance.md) (criteria and the hand-worked
known answers `FX…`), [plan.md](../../milestones/plan.md) (slices, progress, known problems). SEC facts:
[docs/research/sec-edgar.md](../../docs/research/sec-edgar.md). Read them before acting; do not re-decide them.

## Data sources and access

1. Only SEC EDGAR, through two hosts: `https://data.sec.gov` (submissions, company facts) and `https://www.sec.gov`
   (`/files/company_tickers.json`, `/Archives/edgar/data/...` filing documents). No other data provider.
2. **Never call SEC from the browser.** data.sec.gov has no CORS support, and the frontend only calls same-origin
   `/api/*`. All SEC traffic goes through `backend/app/clients/sec.py`. The running app uses it only when a request
   says `source=live`, through `backend/app/data/source.py`, which also holds the disk cache (24 h) and single flight.
   A live failure is an error shown to the person, never replaced by fixtures.
3. **Allowlist.** HTTPS only, the two hosts above, the path patterns in `clients/sec.py` (milestone brief §7), no
   query string, no userinfo, no non-default port. URLs are built from validated parts (a normalized CIK), never
   taken from a caller. Redirects are followed by hand, at most 3, each target checked against the allowlist first.
   This is not a URL proxy: never add an endpoint that fetches a caller-supplied URL.
4. **User-Agent.** It comes only from `SEC_USER_AGENT` in the person's own environment or their git-ignored root
   `.env` (name in the root `.env.example`). It is an app or person name plus that person's own contact email.
   Never invent, hard-code, guess or default it; never print, log, store or commit it; never put it in fixtures,
   the manifest, tests, docs or `runs/`. Tests build fake values from a reserved `.invalid` domain. You never read
   `.env`; if the setting is missing, stop and tell the person to set it themselves.
5. **Fair access.** At most 1 request per second per process, one request in flight, no prefetching, no crawling,
   no bulk archives. 20 s timeout. On 429 or 503 wait for `Retry-After` (capped at 30 s), retry at most twice. On
   403 never retry: report "SEC refused the request (403)". Never disguise traffic or rotate agents. SEC's limit
   (10 requests per second) is for all machines together, so a classroom on one IP uses fixtures.
6. **CIK.** Strip spaces and an optional `CIK` prefix; 1–10 digits; pad to 10. Reject anything else.

## Fixtures and test data

1. `fixtures/` holds **authentic** recorded SEC data and its `manifest.json` (source URL, retrieval time, sha256,
   accessions, periods, scope, what was trimmed). It changes **only** by running `backend/scripts/capture_fixtures.py`.
   Never hand-edit, round, reorder or "fix" a value in it, and never create partial fixtures that look complete.
2. A recapture changes every number: the known answers in `milestones/acceptance.md` must be worked by hand again
   from the new JSON before the tests that use them change.
3. **Synthetic data** lives only in `backend/tests/synthetic/`, each file marked `SYNTHETIC: invented for tests,
   not SEC data` (a `"_synthetic"` key in JSON). The running app never reads it. Anything synthetic shown on a
   screen is labelled `SYNTHETIC TEST DATA`, never `RECORDED SEC DEMO`.
4. Tests are offline: HTTP is mocked with `respx` with no pass-through.

## Financial data rules

1. **Periods** are identified by `start`/`end`. Never group by `fy` or `fp`: they describe the filing, and later
   10-Ks repeat earlier periods as comparatives.
2. **Annual** = a duration of 350–380 days inclusive (52/53-week years count); quarterly and year-to-date facts never
   enter an annual series. Instant (balance) facts match the annual period's `end` exactly.
3. **Forms:** only `10-K` and `10-K/A` facts feed annual series.
4. **Duplicates:** group by (concept, unit, start, end); keep the latest `filed`, on a tie the higher accession
   number. Never sum duplicates or alternative concepts. Keep the chosen fact as provenance.
5. **Concepts:** every list in `backend/app/logic/concepts.py` is a priority order for one period: the first present
   wins, and alternates are never summed. Revenue: `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`,
   `SalesRevenueNet`, `RevenueFromContractWithCustomerIncludingAssessedTax`. Interest: `InterestExpense`,
   `InterestExpenseNonoperating`, `InterestExpenseDebt`. D&A: `DepreciationDepletionAndAmortization`,
   `DepreciationAndAmortization`, `DepreciationAmortizationAndAccretionNet`. Capex:
   `PaymentsToAcquirePropertyPlantAndEquipment`, `PaymentsToAcquireProductiveAssets`. Short-term debt: `CommercialPaper`,
   else `ShortTermBorrowings`. A new mapping is verified against the fixtures or a named live filing before use.
   **Checked 2026-11-04:** Microsoft and Alphabet report none of the D&A concepts, and Apple has no interest concept after
   FY2023, so those lines show as missing and EBITDA or EBIT as unavailable. `PaymentsToAcquireProductiveAssets` was checked on
   live NVIDIA data and is outside `CAPTURE_CONCEPTS`, so the fixtures do not contain it.
6. **Units:** the reporting currency only; facts in other units are ignored, never mixed or converted.
7. **Missing is `null`** with `status: "missing"` and a reason, never 0 and never a blank without explanation.
8. **Reported vs derived.** Every value says whether it is `reported` (one SEC fact) or `derived` (a formula over
   reported values, from M2). Every value carries provenance: concept, taxonomy, unit, start, end, form, accession,
   filed, fy, fp and the companyfacts source URL. A derived value lists its formula and inputs; a missing input
   makes it `unavailable`, never 0.
9. Labels: `FY<year of end date>`, always shown with the end date. Statement views carry "Values may reflect later
   restatements; not point-in-time." and are titled as a normalized summary, not the complete filed statement.
10. **Formulas** are in `backend/app/logic/metrics.py`, and a value that would mislead is not computed. A prior year counts
    only if it ended about a year earlier. **Debt** sums the components reported at that date and is `unavailable` when no
    long-term component is reported, because a short-term line alone would understate debt, possibly as zero. **Negative
    equity:** ROE and debt-to-equity do not measure return or leverage in the usual way, so they show
    `n/m (negative equity)` with the inputs in the tooltip. EBIT is never replaced by operating income.
11. **Key figures** use the latest period, or say why not; only revenue and net income fall back to the latest reported
    value, dated. An old value next to the latest figures would look current.

## Never

- Market prices, market capitalisation, valuation metrics (P/E, EV/EBITDA and the like), currency conversion or
  calendar alignment.
- Invented company descriptions, logos, websites or any value not in the SEC data.
- Navigation, buttons or placeholders for features of later milestones.

## Help

- Skill: [sec-edgar-data](.claude/skills/sec-edgar-data/SKILL.md) (adding a concept, recapturing fixtures, adding a
  known-answer test).
- Agent: `sec-data-specialist` ([.claude/agents/sec-data-specialist.md](../../.claude/agents/sec-data-specialist.md))
  for SEC client, fixture, concept-mapping, period and ratio work in this folder.
