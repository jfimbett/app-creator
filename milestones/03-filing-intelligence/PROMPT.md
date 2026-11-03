# M3 Filing intelligence: build brief

This is the exact implementation brief for SEC Analytics milestone 03. Give it, unchanged, to the assistant or agent
that implements the milestone. It is immutable once the `template-v1` checkpoint exists. Corrections that change
the implementation go into [FOLLOWUPS.md](FOLLOWUPS.md) before they are dispatched.

Paths are relative to the repository root unless stated. `fe/` means `examples/sec-analytics/frontend/` and `be/`
means `examples/sec-analytics/backend/`.

---

## 1. Starting ref

- **Start from tag `m2`** (the verified M2 Financial intelligence checkpoint).
- A student rebuilding this milestone, in a **clean checkout** (`git status` clean; stop any running
  `npm run dev`/`demo` first):

  ```bash
  git fetch origin --tags
  git switch -c exercise/build-m3 m2
  npm ci
  npm run setup
  ```

- Check the start: `git merge-base --is-ancestor m2 HEAD` exits 0, `git log --oneline m2..HEAD` is empty, and
  `npm run verify` exits 0 before you change anything (otherwise record it as a finding first).
- The completed `m3` tag is **for inspection** (`git switch --detach m3`). Do not run this prompt on an `m3`
  checkout. Replaying the prompt will not produce identical code; the `m3` tag is the reference version.

## 2. Context: what exists at `m2`

Read the code before planning; where it differs from this summary, the code and the statuses in
`milestones/acceptance.md` win, and you record the difference.

- **Toolkit** as at `template-v1`, plus the example agent `.claude/agents/sec-data-specialist.md`.
- **Config:** app in `examples/sec-analytics/`, `docsDir` `milestones`, `devEnv` `{"DATA_MODE": "live"}`, `demoEnv`
  `{"DATA_MODE": "fixtures"}`.
- **Example rules:** `examples/sec-analytics/CLAUDE.md` and the nested skill
  `examples/sec-analytics/.claude/skills/sec-edgar-data/SKILL.md` (verified concept mapping, formulas, restatement
  policy, throttle). Read both now.
- **Fixtures:** authentic AAPL, MSFT, GOOGL snapshots (`company_tickers.json`, `submissions/` with 10-K, 10-K/A,
  10-Q, 10-Q/A rows of `filings.recent` and the unchanged `filings.files` list, `companyfacts/`), `manifest.json`,
  `.gitattributes`, built by `be/scripts/capture_fixtures.py`. No filing documents yet.
- **Backend:** settings (`DATA_MODE`, `FIXTURES_DIR`, `SEC_USER_AGENT`, `SEC_CACHE_DIR`,
  `SEC_MAX_REQUESTS_PER_SECOND`); `clients/sec.py` (allowlist incl. archive paths and older submissions pages,
  manual redirects, User-Agent, 1 req/s, single flight, 20 s timeout, Retry-After, no 403 retry, typed errors);
  `data/cache.py` (24 h TTL), `data/source.py` (`source=demo|live`, `409 live_disabled`); logic `cik`, `search`,
  `concepts`, `periods`, `statements`, `metrics`; endpoints `/api/health`, `/api/meta`, `/api/companies/search`,
  `/api/companies/{cik}`, `/overview`, `/api/metrics`, `/financials`, `/metrics`; error codes
  `sec_contact_not_configured`, `sec_unavailable`, `sec_rate_limited`, `sec_refused`, `upstream_not_allowed`;
  `be/scripts/live_sec_smoke.py`.
- **Frontend:** dark navy terminal shell, keyboard search, Demo/Live selector under `npm run dev`, source badges
  (`RECORDED SEC DEMO`, `LIVE`, `CACHED`, `MISSING`), company page with profile, key-figure strip, revenue/net income
  chart, income/balance/cash-flow summary tables, ratios, metric explorer, provenance tooltips, "Use recorded demo
  data" error panel; Playwright `m1-foundation.spec.ts` and `m2-financials.spec.ts` at 1440, 1366 and 390 px.
- **Planning:** [GOAL.md](../../GOAL.md) §4–§6, [docs/PRODUCT-DECISIONS.md](../../docs/PRODUCT-DECISIONS.md)
  (Q6, Q12, Q20, Q41, Q42), [milestones/architecture.md](../architecture.md),
  [milestones/acceptance.md](../acceptance.md) (M3 rows, M3-E1–M3-E5), [milestones/plan.md](../plan.md) (slices
  3.1–3.4), [docs/research/sec-edgar.md](../../docs/research/sec-edgar.md) §2–§4.

All M1 and M2 behaviour must keep working.

## 3. Goal and new work

GOAL.md §5, row 03: the latest available 10-K and 10-Q metadata and their actual filing text; a history with
amendment labels; a readable filing view with section navigation and text search; source links; a documented
fallback when section extraction is imperfect.

1. **Company sub-navigation.** The company page gets two tabs: **Overview** (everything from M1–M2) and
   **Filings** (`/companies/[cik]/filings`). Both keep `?source=`.
2. **Filings view** (Q6, Q42):
   - A "Latest" panel with the latest annual report (most recent original `10-K`) and the latest quarterly report
     (most recent original `10-Q`): form, filing date, period (`reportDate`), accession, and buttons "Read" and
     "Source". If a later amendment exists for it, the panel adds "amended by <accession> on <date>".
   - The heading wording depends on the source: demo → `Latest in snapshot (as of <date>)` (the retrieval date of the
     submissions fixture), live → `Latest on EDGAR (retrieved <time>)`, cached →
     `Latest on EDGAR (cached, retrieved <date>)`. **Never "Latest" alone.** An old snapshot must never look like
     the current latest filing.
   - A history table of `10-K`, `10-K/A`, `10-Q`, `10-Q/A` only, up to 10 years, newest first: form, an
     `AMENDMENT` text label on `/A` forms, filing date, period, accession, Read, Source. Filters: form type (annual /
     quarterly / both) and "include amendments" (on by default). A coverage line states the range shown and, in demo,
     "History limited to the recorded snapshot".
   - Live: older submissions pages (`filings.files`) are fetched only when the recent block does not reach back 10
     years or contains no 10-K or 10-Q, one page at a time, through the throttled client.
3. **Filing reader** (`/companies/[cik]/filings/[accession]`):
   - Fetches the filing's primary document (live: from the archive, cached until deleted because an accession never
     changes; demo: from the fixtures), converts it on the server to **sanitized plain-text blocks**, and renders
     text only. No raw HTML reaches the browser; `dangerouslySetInnerHTML` stays forbidden.
   - A section list (10-K: Items 1, 1A, 1B, 1C, 2, 3, 4, 5, 6, 7, 7A, 8, 9, 9A, 9B, 9C, 10–16 when found; 10-Q:
     Part I Items 1–4 and Part II Items 1, 1A, 2–6) labelled "Sections detected automatically; may be imperfect".
     Clicking a section scrolls to its **body** heading, not its table-of-contents entry, and moves focus there.
   - Fallback when fewer than 3 Item headings are found: the full sanitized text with search, and the note "Section
     boundaries not detected; showing full text". No unlabelled best guess.
   - Text search in the browser over the loaded blocks (no search endpoint): case-insensitive, from 2 characters,
     matches highlighted, a count ("3 of 41"), next/previous buttons, Enter / Shift+Enter, Esc clears.
   - A "Source" link to the exact sec.gov archive document (`https://www.sec.gov/Archives/edgar/data/<CIK without
     leading zeros>/<accession without dashes>/<primaryDocument>`) opening in a new tab with
     `rel="noopener noreferrer"`, plus the filing index link.
   - The reader header shows form, amendment label, company, period, filing date, accession and the source badge.
   - In demo, a history row whose document is not in the snapshot opens a reader state "This filing's document is
     not in the recorded demo snapshot" with the sec.gov Source link (a link only; nothing is fetched).

## 4. Design

Keep the M1–M2 look and extend it.

- **Dark navy terminal** tokens (background `#0A1020`, panels `#0F1A2E`/`#14223B`, border `#1F2E4A`, text
  `#DCE3EE`, muted `#8C9AB3`, amber accent `#F2B33D`, link `#6CB6FF`, warning `#E8A33A`; contrast ≥ 4.5:1). Dark is
  the done criterion; light mode stays out.
- **Tabs:** compact text tabs under the company header (Overview · Filings), the active one underlined in amber,
  `role="tablist"` semantics or plain links with `aria-current="page"`.
- **History table:** dense rows, tabular dates, accession in monospace, `AMENDMENT` as a text badge, Read and
  Source as text buttons; the table scrolls inside its container at 390 px.
- **Reader:** a readable column (max ~80 characters per line, 15 px text, 1.6 line height) on the dark panel; the
  section list as a sticky left rail on desktop and a "Sections" select at the top on 390 px; the search bar sticky
  at the top of the reader with count and next/previous; highlights in amber with dark text, the current match
  outlined; tables from the filing flattened to rows of text with cells separated by `" | "` and marked as "table"
  in a muted label.
- **Labels:** `Latest in snapshot (as of <date>)`, "Sections detected automatically; may be imperfect", "Section
  boundaries not detected; showing full text", source badges as text. Never colour alone.
- **States:** loading (skeleton lines), document too large, document not in snapshot, filing not found, invalid
  accession, SEC unavailable / rate limited / refused (with "Use recorded demo data" in live), no filings of the
  selected type.
- **Responsive** at 1440, 1366 and 390 px; no sideways page scroll.
- **Honesty:** no navigation to Compare or Analyst yet; no invented summaries of filings; no control that does
  nothing.

## 5. Architecture and files

Follow [milestones/architecture.md](../architecture.md): logic pure, API thin, data layer picks fixtures/cache/live
and labels, only `clients/sec.py` reaches SEC.

| Path | Change |
|---|---|
| `be/requirements.in`, `be/requirements.lock` | add `beautifulsoup4==4.15.0` (and its dependency); regenerate the lock exactly as its header describes, with a supported Python (3.10–3.13); use the `html.parser` from the standard library (no lxml) |
| `be/app/logic/filings.py` | parse submissions columns into `FilingMeta`; filter forms; amendment labels and "amended by" links; latest annual/quarterly; 10-year window; coverage; whether older pages are needed |
| `be/app/logic/archive.py` | build and validate archive URLs from CIK, accession and primary document |
| `be/app/logic/sanitize.py` | HTML → sanitized text blocks (rules in section 7) |
| `be/app/logic/sections.py` | Item heading detection, table-of-contents skip, fallback |
| `be/app/data/source.py` | `get_filing_document(cik, accession, source)`; older submissions pages in live |
| `be/app/data/fixtures.py` | read gzip filing documents and the extended manifest |
| `be/app/models/filings.py` | `FilingsResponse`, `FilingDocumentResponse` |
| `be/app/api/filings.py` | the two endpoints below |
| `be/scripts/capture_fixtures.py` | add `--filings` mode (section 6) |
| `be/tests/...`, `be/tests/synthetic/...` | section 9 |
| `fe/app/companies/[cik]/filings/page.tsx`, `fe/app/companies/[cik]/filings/[accession]/page.tsx` | Filings view and reader |
| `fe/components/` | `CompanyTabs`, `LatestFilings`, `FilingHistory`, `FilingReader`, `SectionNav`, `TextSearch` |
| `fe/lib/text-search.ts` | pure match finding and highlight segments (Vitest) |
| `fe/lib/types.ts`, `fe/lib/api.ts` | new types and calls |
| `fe/e2e/m3-filings.spec.ts` | section 9 |
| `examples/sec-analytics/CLAUDE.md`, nested skill, `examples/sec-analytics/README.md`, `fixtures/README.md` | sanitization and section rules, the fallback, filing fixtures, recapture with `--filings` |
| `milestones/acceptance.md`, `plan.md`, `architecture.md` | statuses, progress log, decision-log rows (new field and error code) |

**API added at M3** (shared shapes and the error envelope as in architecture.md):

| Method and path | Request | Response | Errors |
|---|---|---|---|
| `GET /api/companies/{cik}/filings` | `forms` (comma subset of `10-K,10-K/A,10-Q,10-Q/A`, default all four), `years` (1–10, default 10), `source` | `{cik, latest: {annual: FilingMeta\|null, quarterly: FilingMeta\|null, annual_amended_by: FilingMeta\|null, quarterly_amended_by: FilingMeta\|null, label: str}, history: [FilingMeta], coverage: {from: date, to: date, complete: bool, note: str\|null}, source}` | 422 `invalid_cik`, 422 `invalid_forms`, 404 `company_not_found`, 409 `live_disabled`, SEC errors as in M2 |
| `GET /api/companies/{cik}/filings/{accession}` | `accession` `^\d{10}-\d{2}-\d{6}$`, `source` | `{meta: FilingMeta, section_status: "detected"\|"not_detected", note: str, sections: [{id, item, title, block_start}], blocks: [{id: int, section_id: str\|null, kind: "text"\|"heading"\|"table_row", text: str}], source_link: str, source}` | 422 `invalid_accession`, 404 `filing_not_found` (not in this company's 10-K/10-Q list; no SEC request made), 404 `document_not_in_snapshot` (demo), 413 `document_too_large` (over 20 MB raw), SEC errors as in M2 |

`FilingMeta` is `{accession, form, is_amendment, filing_date, report_date, primary_document, document_url,
index_url}` plus one new field `document_in_snapshot: bool | null` (demo: whether the document is in the fixtures;
live: `null`). Add the field, `annual_amended_by`/`quarterly_amended_by`, `kind` on blocks, and the codes
`invalid_forms` and `document_not_in_snapshot` to the API table in architecture.md and the decision log.
`index_url` is `https://www.sec.gov/Archives/edgar/data/<cik>/<accession-no-dashes>/<accession>-index.html`
(a link only; the app never fetches it, so it needs no allowlist entry).

## 6. Fixtures and data

- **Extend, do not replace.** Add `--filings` to `be/scripts/capture_fixtures.py`. It reads the **existing**
  fixture submissions files (it does not refetch them) and, for each company, picks the latest original `10-K` and
  the latest original `10-Q` listed there, so the documents match what the snapshot says is latest. It downloads
  exactly those primary documents through the allowlisted, throttled client (6 requests) and stores each
  **gzip-compressed and otherwise unmodified** as
  `fixtures/filings/<CIK10>/<accession>/<primaryDocument>.gz`. It never touches the companyfacts files, so no M2
  number changes.
- **Amendment metadata:** if, within the 10-year window, the fixture `filings.recent` does not reach back 10 years,
  `--filings` may download the older submissions page(s) listed in `filings.files` (allowlisted
  `CIK##########-submissions-###.json`; the exact URL form is marked unverified in the research note, so check it
  and report), trim each to the four forms the same way as M1, and store it as
  `fixtures/submissions/CIK##########-submissions-###.json`. Record in the manifest how many `10-K/A` and `10-Q/A`
  rows the snapshot holds per company. If there are none, say so; M3-AC2 and M3-E1 then rely on synthetic tests.
- The manifest gets one entry per new file (`kind: "filing_document"` or `"submissions_page"`, `cik`,
  `source_url`, `retrieved_at`, `sha256` and `bytes` of the stored `.gz`, `accessions`, `periods` (report date),
  `scope`, `trimmed`: "none; stored gzip-compressed" for documents). `snapshot_date` stays the M1 date; the new
  entries carry their own retrieval dates, and the "Latest in snapshot" label uses the submissions file's
  `retrieved_at`.
- The capture needs `SEC_USER_AGENT` from the person's own environment or ignored root `.env` (read by the script,
  never printed); you never read `.env`. If retrieval is blocked: stop, record the blocker (N2) with command, exit
  code and message, keep the reader working on synthetic test documents in `be/tests/synthetic/`, and state that the
  demo reader cannot pass without authentic documents.
- **Synthetic documents** for tests (`be/tests/synthetic/filings/`, each starting with an HTML comment
  `SYNTHETIC: invented for tests, not SEC data`): one with `<script>`, `onclick`, `<iframe>`, `javascript:` links,
  `<style>`, `<form>`, inline XBRL `ix:header`; one with a table of contents and repeated Item headings; one with no
  Item headings; a submissions file with a `10-K` and a later `10-K/A` for the same period.
- Update `fixtures/README.md` and the manifest test from M1 so it covers `.gz` files (hash of the compressed file).

## 7. SEC and content rules that apply at M3

- **Fetching:** backend only; allowlisted archive path `^/Archives/edgar/data/\d+/\d{18}/[A-Za-z0-9._-]+$` on
  `www.sec.gov`; URL built from the normalized CIK (leading zeros removed for the archive path), the accession with
  dashes removed (18 digits) and the `primaryDocument` value from submissions, which must match
  `^[A-Za-z0-9._-]{1,200}$`; never a URL from the caller. The accession must appear in that company's 10-K/10-Q
  list before any request (`../../etc` → 422; unknown → 404, no SEC request). Manual redirects to allowlisted
  targets only. User-Agent, throttle (1 req/s, one in flight, single flight), 20 s timeout, Retry-After with at
  most 2 retries, no retry on 403, no bypass, exactly as in M2. Archive documents are cached until deleted.
- **Older submissions metadata:** handled when needed (above), one page at a time, never prefetched.
- **Untrusted content** (`logic/sanitize.py`): parse with BeautifulSoup `html.parser`; remove `script`, `style`,
  `noscript`, `template`, `iframe`, `frame`, `object`, `embed`, `form`, `input`, `button`, `select`, `textarea`,
  `svg`, `canvas`, `link`, `meta`, `base`, and the inline XBRL `ix:header` (hidden facts); drop every attribute,
  so `on*` handlers, `style` and `javascript:` URLs disappear; keep no links from the document (only the app's own
  Source link). Output plain text blocks: one per paragraph-like element (`p`, `div` with direct text, `li`,
  headings), one per table row (cells joined with `" | "`, empty cells dropped). Normalise whitespace and non-breaking
  spaces; drop empty blocks and page-number-only blocks. The browser renders `block.text` as React text nodes only.
- **Sections** (`logic/sections.py`, deterministic and documented in CLAUDE.md):
  - A heading candidate is a short block (≤ 200 characters) matching `^\s*item\s+(\d{1,2}[a-c]?)\s*[.:\-–—]?\s*`
    (case-insensitive); for 10-Q, track the current `Part I`/`Part II` so ids are `part1-item2`, `part2-item1a`.
  - Table-of-contents skip: drop candidates that are table rows, and candidates in a cluster where three or more
    candidates occur with fewer than 300 characters of text between consecutive ones.
  - For each item keep the first remaining candidate after the previously accepted section, in document order.
  - If fewer than 3 sections remain: `section_status: "not_detected"`, note "Section boundaries not detected;
    showing full text", no sections. Otherwise `"detected"` with the note "Sections detected automatically; may be
    imperfect". Never claim guaranteed semantic extraction.
- **Latest vs history:** the latest annual report is the most recent original `10-K` by filing date (a later
  `10-K/A` is shown as "amended by …", not as the latest report); likewise for `10-Q`. History holds only the four
  forms, up to 10 years, newest first, with `/A` forms labelled `AMENDMENT`.
- **Labels:** in demo, every "latest" wording is `Latest in snapshot (as of <date>)`.

## 8. No-interview defaults

Do not interview the owner; decisions are in [docs/PRODUCT-DECISIONS.md](../../docs/PRODUCT-DECISIONS.md) and
`milestones/*.md`. Never re-decide what is recorded. Defaults for unspecified reversible details (list them in the
Handoff; record important ones in the architecture decision log as "routine technical choice under delegation"):

- Block ids are consecutive integers from 0; section ids are lowercase (`item1a`, `part2-item1a`).
- Search: literal substring (no regex input), case-insensitive, at most 1,000 highlighted matches (the count says
  "1,000+" beyond that).
- Size limit 20 MB raw document; at most 30,000 blocks returned (beyond that the reader says the document was cut,
  with the Source link).
- History default: both annual and quarterly, amendments included, 10 years.
- Exact strings: as in this prompt and [acceptance.md](../acceptance.md).

If genuinely blocked (documents cannot be captured, section detection fails on the authentic documents after two
different fixes, or something needs money, a secret, personal data or new scope): record it with evidence in
`milestones/plan.md` "Known problems" and the Handoff, keep the labelled fallback working, and continue the
independent work.

## 9. Tests and verification

Failing test first; no test reaches the network (respx, no pass-through).

**pytest:**

- `test_filings.py`: parse fixture submissions; only the four forms; up to 10 years; newest first; M3-E1 (10-K and
  later 10-K/A for the same period → both in history, the `/A` labelled, latest annual stays the 10-K with
  "amended by"); M3-AC2 with the synthetic history; older pages needed or not; coverage note in demo; M3-E4 label
  `Latest in snapshot (as of <date>)` in demo and never "Latest" alone.
- `test_archive.py`: archive URL for Apple built exactly from CIK, accession and primary document (M3-AC6);
  `../../etc`, `0000320193-25-00007` (short), a primary document with `/` or `..` → rejected; a valid accession not
  in the list → `filing_not_found` with no request made (M3-E5).
- `test_sanitize.py` (M3-E2): the synthetic hostile document yields text with none of `<script`, `onclick`,
  `<iframe`, `javascript:`, `<style`, `<form`, hidden `ix:header` facts; the visible text survives; tables become
  `" | "` rows; whitespace normalised.
- `test_sections.py`: M3-E3 / M3-AC4 (Item 7 in the TOC and the body → the section starts at the body heading);
  10-Q Part I/Part II ids; M3-AC7 (no Item headings → `not_detected` and the exact note); fixture documents:
  Apple's and Microsoft's 10-K detect at least Items 1, 1A, 7 and 8 (if not, record it as a finding and keep the
  labelled fallback).
- `test_api_m3.py`: `/filings` and `/filings/{accession}` in demo for all three companies; 422 `invalid_accession`,
  422 `invalid_forms`, 404 `filing_not_found`, 404 `document_not_in_snapshot`, 413 `document_too_large` (synthetic
  oversize via a small injected limit); live with respx-mocked archive and submissions pages (allowlisted URL
  requested, cached on second call, `CACHED` label); `source=live` under fixtures → 409.
- Manifest test covers the `.gz` files; all M1–M2 tests still pass.

**Vitest:** `lib/text-search.test.ts` (case-insensitive matches, count, next/previous wrap, highlight segments with
special characters such as `(` `$` `.` treated literally, M3-AC5).

**Playwright** (`fe/e2e/m3-filings.spec.ts`, fixture mode):

1. Apple → Filings: `Latest in snapshot (as of <date>)` with the 10-K and 10-Q, form, filing date, period and
   accession (M3-AC1); history shows only the four forms.
2. Read the latest 10-K: readable text, section list with "Sections detected automatically; may be imperfect";
   `page.locator('[data-testid=filing-reader] script, [data-testid=filing-reader] iframe')` has count 0 (M3-AC3,
   M3-E2).
3. Click "Item 7": the target heading is in the viewport, has focus, and is the body heading (its block id equals
   the section's `block_start`, after the TOC) (M3-AC4).
4. Search "revenue": a count is shown, highlights exist, next/previous move the current match (M3-AC5).
5. "Source" has the exact archive URL, `target="_blank"` and `rel` containing `noopener` (M3-AC6); assert the href
   without opening sec.gov.
6. A history row without a document in the snapshot → the "not in the recorded demo snapshot" state with the Source
   link.
7. No request leaves `127.0.0.1`/`localhost`; screenshots of Filings and the reader (with a search active) at
   1440×900, 1366×900 and 390×844 (`fe/test-results/m3-<screen>-<width>.png`); at 390 px no sideways page scroll.
8. The M1 and M2 journeys still pass.

**Gate:**

1. `npm run check-toolkit` exits 0.
2. `npm run verify` exits 0 offline.
3. `npm run demo` works with no `.env`, no keys, no network: Apple → Filings → read the 10-K → Item 7 → search.
4. Open and inspect every new screenshot (readability of the reader at 390 px in particular); list what you checked.
5. **Live SEC (separate, optional):** only with `SEC_USER_AGENT` configured: `npm run dev` → Live → Apple → Filings
   → read the latest 10-K. Report "live SEC: passed/failed on <date>" or "not run (SEC_USER_AGENT not configured)".
   The `--filings` capture is reported the same way.

## 10. Acceptance criteria (from [acceptance.md](../acceptance.md))

- [ ] M3-AC1 Apple → Filings shows the latest 10-K and 10-Q under `Latest in snapshot (as of <date>)` with form,
  filing date, period and accession.
- [ ] M3-AC2 Amendments carry an "Amendment" label; only 10-K, 10-K/A, 10-Q, 10-Q/A appear, up to 10 years.
- [ ] M3-AC3 The reader shows readable text (no markup) and a section list labelled as detected automatically.
- [ ] M3-AC4 Clicking "Item 7" scrolls to the Item 7 body, not the TOC entry.
- [ ] M3-AC5 Searching "revenue" highlights matches with a count and next/previous controls.
- [ ] M3-AC6 "Source" opens the exact archive document URL in a new tab.
- [ ] M3-AC7 A document with no Item headings shows full sanitized text with search and "Section boundaries not
  detected; showing full text".
- [ ] M3-E1–M3-E5 as listed in acceptance.md.
- [ ] All M1 and M2 criteria still pass; V1–V3 screenshots inspected.

Update the statuses in `milestones/acceptance.md` and the slices and progress log in `milestones/plan.md`.

## 11. Out of scope

- Later milestones: multi-company comparison, indexing and CSV export (M4); the AI analyst, OpenRouter settings and
  any OpenRouter code (M5). No navigation or placeholders for them.
- Also out: 8-K and other forms in the history; exhibits and full submission `.txt` files; XBRL viewer features;
  generated filing summaries; a server-side search endpoint.
- Excluded everywhere (GOAL.md): accounts, payments, uploads, PostgreSQL or any database server, SQLite, a vector
  database, a Docker prerequisite, Streamlit, hosted deployment, SEC bulk archives and full/daily index downloads,
  prefetching, an arbitrary URL proxy, non-SEC companies, market prices and valuation metrics, currency conversion,
  calendar alignment, invented descriptions, light mode as a done criterion.
- Do not edit `milestones/*/PROMPT.md`, `FOLLOWUPS.md`, the toolkit (`.claude/`, `scripts/`, `scaffold/`,
  `AGENTS.md`, `CLAUDE.md`, `docs/TOOLKIT.md`), `GOAL.md`, `PROGRESS.md`, `runs/`, or the existing fixture files
  (only add the new ones and their manifest entries). The milestone README's "Results" section is filled in by the
  owner after the checkpoint.

## 12. Handoff

Do not commit, tag, push or change Git configuration: the owner integrates, commits and creates the `m3`
checkpoint. Never read, create, print or commit `.env` files, keys or contact data.

End your final message with exactly this block (docs/TOOLKIT.md §7):

```
## Handoff
Changes: <files created or changed, grouped by folder>
Verification evidence: <each command with its exit code and summary line; screenshots looked at; filing capture and live SEC reported separately>
Remaining findings: <blockers, section-detection results on the real documents, defaults chosen, deviations and why>
Next action: <one line>
```
