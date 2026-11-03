# RESPONSE — B10-interview-questions

- From: product-architect → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: eaf6e927-8844-4a3f-a7df-fe9736eeced9 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T17:38:06.620Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
I used the product-interview skill (Delegated mode). I read GOAL.md in full, plus `docs/TOOLKIT.md`, `app-creator.config.json` (`"app"` is still `null`, so this is template mode), the two research notes and the decisions template. `docs/PRODUCT-DECISIONS.md` doesn't exist yet, so no answers are recorded. Below are 44 questions for `delegated-product-owner`, grouped by the skill's seven rounds plus one SEC-specific round. Some ask about things GOAL.md already covers, as the brief told me to, so each answer gets an explicit citation.

## Interview questions for the delegated product owner

**Round 1 — Customers and problem**
- Q1. Who is the main user of SEC Analytics: business-school students looking at prepared versions in class, the instructor running the demo, or students rebuilding each milestone with its prompt?
- Q2. What painful task does SEC Analytics replace for that user today (for example, reading raw EDGAR pages or Company Facts JSON by hand)?
- Q3. What visible result in class shows the product helped (for example, an instructor finishes a three-minute demo per milestone offline, without errors)?

**Round 2 — Main user journey per milestone**
- Q4. In M1 (Foundation), what is the one visit from opening the app to the result: search a demo company, open its profile and identifiers, then see the labelled fixture dashboard?
- Q5. In M2 (Financial intelligence), what does the user enter and take away: a company, a choice of metric and 5–10 years, then statements, charts, ratios and where each number came from?
- Q6. In M3 (Filing intelligence), does the journey start from the company page (latest 10-K/10-Q, then filing history, then a readable filing with section navigation and search), or from a separate filings screen?
- Q7. In M4 (Comparative analysis), how does the user pick 2–4 companies and metrics, and is CSV export the end of the journey?
- Q8. In M5 (AI analyst), where does chat live (on the company, filing and comparison screens, or one analyst panel that keeps track of which of those the user is on), and what does a good answer look like to the user?

**Round 3 — Screens and visuals**
- Q9. On the company screen, should the first view be a dense dashboard (key figures with fiscal year-end and units, plus a revenue/net income chart) or a statement table, given "dense readable tables" and "useful charts" in §5?
- Q10. Which summary figures belong in the M2 dashboard header (for example: latest annual revenue, revenue growth, net margin, FCF, debt-to-equity), each shown with fiscal period, unit and whether it is reported or derived?
- Q11. Which chart types fit the metric explorer and the comparison (for example, a line chart for trends over time and grouped bars for one year across companies), and how should negative values and gaps be drawn?
- Q12. How should data-source labels look (live, cached, recorded SEC demo data, missing), and where should the as-of or snapshot date appear on each screen?
- Q13. How does keyboard-friendly search work (for example, a "/" or Ctrl/Cmd-K shortcut to focus it, arrow-key results, Enter to open)?
- Q14. Which narrow width must the layout support (phone around 390 px, or only a narrow laptop window), given that dark mode is required and light mode is secondary?
- Q15. Should light mode be part of any milestone's done criteria, or stay explicitly after the core features (and, if so, after which milestone)?

**Round 4 — MVP features and exclusions per milestone**
- Q16. For each milestone, what are the three to five must-have features, taken from the §5 table?
- Q17. What is explicitly not in the MVP across all milestones (for example: accounts, payments, database server, vector database, Docker, cloud hosting, market prices or valuation metrics, currency conversion, bulk archive downloads, non-SEC companies)?
- Q18. How should a navigation item for a later milestone be handled in an earlier version: left out entirely, or shown clearly disabled with a "coming in M3" note?

**Round 5 — Data and calculations**
- Q19. Is the demo universe exactly AAPL, MSFT and GOOGL, or should a fourth company be added so the M4 four-company comparison can be shown offline?
- Q20. What is the fixture scope per company: how many annual periods (at least 5?), which filing excerpts (latest 10-K and 10-Q sections?), and should fixtures be trimmed Company Facts or full responses?
- Q21. If live SEC access to fetch the real fixtures is blocked, what should happen: stop that milestone and report it, or continue with clearly marked synthetic test data only, never shown as SEC data?
- Q22. How is the user switched between modes: an explicit demo or live toggle in the interface, the `npm run demo` versus `npm run dev` launch command, or both?
- Q23. Which concept mapping, with alternates in priority order, defines revenue (for example `Revenues`, then `RevenueFromContractWithCustomerExcludingAssessedTax`, then `SalesRevenueNet`), and is the concept actually used shown to the user?
- Q24. What is the restatement and duplicate rule: for each concept, unit and exact start/end period, keep the value from the most recently filed annual report (10-K or 10-K/A), with a deterministic tie-break, and show a "may include later restatements" note?
- Q25. What range of days counts as an annual period (for example 350–380 days, to allow 52/53-week years), and are 10-K facts with other lengths excluded from annual series?
- Q26. Is EBIT defined as net income + income tax expense + interest expense (shown as unavailable if any input is missing), and EBITDA as EBIT + depreciation and amortization, both labelled as derived and never replaced by operating income?
- Q27. Is FCF defined as operating cash flow − capital expenditures (`PaymentsToAcquirePropertyPlantAndEquipment`), in the reporting currency, unavailable if either input is missing?
- Q28. Are ROE = net income / average of beginning and ending equity, and ROA = net income / average of beginning and ending total assets? Should they show "unavailable" when the earlier year is missing, or fall back to the ending balance with a label?
- Q29. Is debt-to-equity = (long-term debt + current debt) / total equity, and how is it shown when equity is zero (unavailable) or negative (value shown with a "negative equity: not meaningful" note)?
- Q30. How are margins (operating, net, FCF), year-over-year growth and working capital (current assets − current liabilities) defined, and what is shown when the previous-year value is zero or negative?
- Q31. Which known-answer check sets the expected values for these formulas: hand working from the recorded fixture facts (quoting accession and period), or numbers cited from the company's 10-K?
- Q32. In M4, what does "indexing or normalization" mean: rebase each company's series to 100 at its first common fiscal year, or show percentages and ratios only? How is it labelled, given that currencies and fiscal year-ends are never aligned silently?
- Q33. What must the M4 CSV contain (company, CIK, fiscal year-end, period start/end, metric, value, unit, reported or derived, source concept, accession, data-source label), and are missing values written as empty cells?

**Round 6 — Accounts, saved data, uploads, payments**
- Q34. Is it confirmed that there are no accounts, no uploads and no payments in any milestone?
- Q35. What is saved between visits: only a local disk cache of SEC responses (or SQLite, and if so, which and from which milestone), and how long is the cache kept before it is treated as stale?
- Q36. For the OpenRouter key, is the default memory-only, with an explicit opt-in to session storage (sessionStorage, cleared when the tab closes) and a warning that page scripts can read it? Should model choice also be remembered, and where?

**Round 7 — Team, constraints and launch**
- Q37. How should a student who runs live mode without the SEC User-Agent contact setting be treated: block live requests with a clear message naming the setting, while demo mode keeps working?
- Q38. What request budget fits a classroom on one public IP: a global backend limit well below SEC's limit (for example ≤ 2 requests per second per running app), with fixtures and cache as the default and no prefetching?
- Q39. Which Node and Python versions must `setup` support on macOS and Windows, and which ports do `dev` and `demo` use by default (for example 3000 frontend, 8000 backend), with the ports configurable by setting name?
- Q40. In each milestone, what must `npm run verify` include: lint and type checks, pytest, the production frontend build, and a Playwright smoke journey on fixtures, with no network needed?

**Product-specific — filings and AI analyst**
- Q41. When section extraction cannot reliably find an Item (for example Item 1A or Item 7), what should happen: show the full cleaned text with search plus a note "section boundaries not detected", or show the best-guess section marked "approximate"?
- Q42. Which filing types count in M3's history (10-K, 10-Q and their /A amendments only, or also 8-K), and how many years of history are shown, including older submissions pages?
- Q43. What may the M5 analyst answer: questions about the current company's financial data, its filings and the current comparison only, refusing anything else (price forecasts, investment advice, companies not loaded) with a clear message?
- Q44. What limits apply to the analyst (for example: at most N facts and M passages per request, a cap on output tokens, one request at a time per browser, a timeout in seconds)? Should the model list come live from OpenRouter with no hardcoded default model ID, showing an empty choice until the user picks one?

## Handoff
Changes: none (I wrote, edited and committed nothing).
Verification evidence: I read GOAL.md (all 214 lines), `docs/TOOLKIT.md`, `app-creator.config.json`, `docs/research/sec-edgar.md` and `docs/research/openrouter.md` (one long output was cut short; I checked their section headings), the product-interview SKILL.md and `templates/decisions.md`. One `ls` matched nothing, which confirms `docs/PRODUCT-DECISIONS.md` doesn't exist yet. The other commands exited 0.
Remaining findings: These questions are likely to be "Not delegable" or need care:
- Q19: a fourth company means fetching more data.
- Q21: what to do if real fixtures can't be fetched.
- Q36: which browser storage is allowed for the key.
- Q37: the SEC contact email is personal data, and the owner must supply it.
- Q44: any paid live AI check depends on a test key the owner already has.

Several questions (Q23–Q30) need the formulas checked against SEC concept facts, not answered from memory.
Next action: Send Q1–Q44, GOAL.md and the path `docs/PRODUCT-DECISIONS.md` to `delegated-product-owner` (step 2), then record its answers and write the four documents (step 3).
<!-- VERBATIM:END -->
