# RESPONSE — B14-review-milestone-prompts

- From: project-orchestrator → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: 17a39a76-e59b-4d44-8964-b155fa2c07ee (local Claude Code transcript; not committed)
- Finished: 2026-11-03T18:10:59.865Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
**Verdict: M1 and M4 can be accepted. M2, M3 and M5 each need a small repair before `template-v1`. Several of B13's open items also need edits to the planning documents.**

All five prompts have every required section. The starting refs are right (`template-v1`, `m1`, `m2`, `m3`, `m4`), and each says the finished tag is for inspection only. I found no later-milestone features leaking into earlier ones beyond one stray name in M2. No prompt contains an email address, and none asks anyone to make up data, a contact or a key: fake contacts in tests use a reserved `.invalid` domain, tests use the obviously fake key `test-key-not-real-0000`, and if capture is blocked the prompts say to stop and report it.

## Per prompt

**M1 Foundation: accept.** It covers the note that search only reaches the three demo companies, both "not found" messages, demo-only mode, authentic fixtures with a manifest (or a recorded blocker), and a meaningful browser smoke test with screenshots. The scaffold facts it quotes match the repo (versions, `smoke.spec.ts`, `lib/health.ts`, the config keys). One optional hardening change:
- Quote: "no file under `fixtures/` contains the string `SYNTHETIC`"
- Replace with: "no file under `fixtures/` contains the marker `SYNTHETIC: invented for tests` or a `"_synthetic"` key"

**M2 Financial intelligence: repair.**
1. **A stray M3 name.** Line 172 lists `FilingMeta`, which belongs to M3.
   - Quote: "(shared shapes `SourceInfo`, `Provenance`, `MetricValue`, `FilingMeta` and the error envelope as in architecture.md)"
   - Replace with: "(shared shapes `SourceInfo`, `Provenance`, `MetricValue` and the error envelope as in architecture.md; `FilingMeta` arrives in M3)"
2. **A message points to a file that doesn't exist.** The "Live SEC data is not configured" message (M2-AC2, Q37) tells users to read `docs/SETUP.md`, and nothing creates that file before M2.
   - Add this row to the §5 file table after `examples/sec-analytics/README.md`: "| `docs/SETUP.md` | create it if missing, otherwise extend it: a section "SEC Analytics: live SEC mode" covering `npm run dev` → Live, what `SEC_USER_AGENT` must contain (a descriptive name plus your own contact email, set only by you in your shell or the ignored root `.env`; no example address), the cache and the 1 request/s throttle, the note that a class on one public IP should use demo data, and `be/scripts/live_sec_smoke.py`. The live-mode error message points here. |"
3. *(optional)* In the `test_sec_client_m2.py` bullet, add: "Any fake User-Agent is built from a reserved `.invalid` domain, never a real address."

Everything else GOAL asks of M2 is present: the duration/instant split with the 350–380-day annual window, never grouping by `fy`, the restatement and duplicate rule, the formulas matching Q26–Q30, missing values as null, provenance and formula tooltips, no valuation metrics, and live mode that never switches to demo data by itself.

**M3 Filing intelligence: repair.**
1. **Contradiction.** §11 forbids editing "the existing fixture files", but §6 tells the implementer to update `fixtures/README.md` and add manifest entries.
   - Quote: "or the existing fixture files (only add the new ones and their manifest entries)"
   - Replace with: "or the existing fixture data files (`company_tickers.json`, `submissions/CIK##########.json`, `companyfacts/`); only add the new files, their manifest entries and the `fixtures/README.md` update from section 6"
2. *(optional)* After "413 `document_too_large` (over 20 MB raw)", add: "enforced while the response is read (stop after 20 MB of decoded bytes)".

The other GOAL items are covered: the parser strips scripts and active content and renders text only, repeated table-of-contents headings are skipped, amendments are labelled, the no-sections fallback is labelled, archive URLs are validated, older submissions pages are fetched only when needed, and demo mode says "Latest in snapshot". The `beautifulsoup4==4.15.0` pin matches PROGRESS.md D6, so it isn't made up.

**M4 Comparative analysis: accept.** It keeps each company's own fiscal year-end and period end and shows "Fiscal years are not aligned". It never converts currencies and warns when they differ. Indexing is labelled and applies only to absolute amounts, never ratios. The CSV has the exact header, empty cells for missing values, a guard against spreadsheet formulas, the same row order as the table, and a URL-state round trip. No AI leaks in.

**M5 AI analyst: repair.**
1. **Origin check logic bug.** The word "and" means a request is refused only when both checks fail; it should be refused when either fails.
   - Quote: "`/api/ai/*` rejects a request whose `Origin` header is present and is not `http://127.0.0.1:<port>` or `http://localhost:<port>` (any port, so `npm run verify`'s spare ports work), and whose `Sec-Fetch-Site`, when present, is not `same-origin` or `none`, with 403 `forbidden_origin`."
   - Replace with: "`/api/ai/*` rejects a request with 403 `forbidden_origin` if **either** its `Origin` header is present and is not `http://127.0.0.1:<port>` or `http://localhost:<port>` (any port, so `npm run verify`'s spare ports work), **or** its `Sec-Fetch-Site` header is present and is not `same-origin` or `none`."
   - In the `test_ai_security.py` bullet, add: "`Sec-Fetch-Site: cross-site` with an allowed Origin → 403 `forbidden_origin`."
2. **GOAL §9 wants OpenRouter setup in `docs/SETUP.md`.** Add this file-table row: "| `docs/SETUP.md` | add a section "SEC Analytics: optional AI analyst": your own limited-credit key, memory-only vs this-tab storage and its risk, the possible small charge for the connection test, separate keys per student or group, and that this is separate from Claude Code's or Cline's model settings. No key values and no `OPENROUTER_*` names. |"

The rest of §7 is covered: key handling, the models list with pricing and no preselected model, the caps, cancel, error mapping without automatic retries, server-assigned citation ids that the app validates, prompt-injection tests, and reporting mocked and live checks separately with live AI blocked (N1).

## B13's open items: how to resolve each
Items 1–7 are fixes to the planning documents (`milestones/*.md`, `docs/PRODUCT-DECISIONS.md`), which can still change before `template-v1`.

1. **Screenshot widths.** Keep 1440, 1366 and 390 px in the prompts. In `acceptance.md`, change M1-AC6 "at 1440 and 390 px" to "at 1440, 1366 and 390 px" and the V2 row to match; change `architecture.md` line 255 the same way. Add a row to "Changes to earlier decisions" in PRODUCT-DECISIONS.md (Q14 detail extended).
2. **Filing documents moved from M1 to M3.** Accept the move: M1 doesn't need them, and capturing them at M3 keeps M3 data out of M1.
   - `plan.md` slice 1.2: remove "and 10-K/10-Q excerpts".
   - `plan.md` slice 3.2: add "`capture_fixtures.py --filings`".
   - `architecture.md` line 155: change the path to `fixtures/filings/<CIK10>/<accession>/<primaryDocument>.gz`, described as "the latest 10-K and 10-Q primary documents, gzip-compressed and unmodified (added in M3)".
   - Add a Q20 row to "Changes to earlier decisions".
3. **M2-AC5 stacked charts.** Accept. Change "a line chart shows both series" to "stacked line charts, one per metric, sharing the fiscal-year axis", and add a change row.
4. **M4-AC6 CSV rows.** Accept. Change "exactly the rows shown" to "exactly the data points shown (one line per company × metric × fiscal year), in table order".
5. **New API codes and fields.** Accept as written: each prompt tells its implementer to add them to `architecture.md`.
6. **Settings reader.** In `architecture.md` line 48, change "(pydantic `BaseSettings`)" to "(a plain pydantic model validating the environment; no `pydantic-settings` package)".
7. **Example agent under `.claude/`.** In the `plan.md` ground rules, change "Do not touch the toolkit: `.claude/`, …" to "Do not touch the toolkit (`.claude/`, …), except that slice 1.1 adds `.claude/agents/sec-data-specialist.md`".
8. **Stale file hashes in B13.** Leave B13's `PROMPT.md` alone, since step records are append-only. Record the prompt hashes after the repair in B14's `RESULT.json` and PROGRESS.md; the `template-v1` commit is the authoritative version. Current hashes, before the repair:
   - M1 `41cb350f…`
   - M2 `6cbed727…`
   - M3 `7f135930…`
   - M4 `47af2b50…`
   - M5 `38a7b36e…`
9. **`milestones/README.md` is stale.** Replace "The milestone folders, with each build brief (`PROMPT.md`), follow-ups and README, are added in the next bootstrap step." with "Each milestone folder holds its build brief (`PROMPT.md`), its follow-up prompts (`FOLLOWUPS.md`) and a README." Also, in `milestones/01-foundation/README.md`, change "On top of the earlier milestones, SEC Analytics adds" to "SEC Analytics starts with".
10. **N1 (no paid AI test key) and N2 (the SEC contact setting).** These are not prompt defects. The prompts already handle them: stop and report, never manufacture data.

Decision: repair. `product-architect` applies the M2, M3 and M5 prompt edits and items 1–7 and 9; then the owner re-runs `npm run check-toolkit` and the email grep, recomputes the five prompt hashes, and dispatches B14's re-check before creating `template-v1`.

## Handoff
Changes: none (orchestrator is read-only)
Verification evidence: read GOAL.md, PRODUCT-DECISIONS.md, the five `PROMPT.md` files, the milestone READMEs, `milestones/README.md`, the relevant parts of `plan.md`, `architecture.md` and `acceptance.md`, the research notes, the scaffold files and B13's RESPONSE. `npm run check-toolkit`: 34 ok, 3 warnings, 0 failures (exit code not captured). Email-address grep over `milestones/`: no matches (exit 1). Computed sha256 of the five prompts.
Remaining findings: M2 (stray `FilingMeta` name; missing `docs/SETUP.md`), M3 (fixture-edit contradiction), M5 (Origin "and"→"or" bug; SETUP section); planning-document updates for items 1–7 and 9; N1 and N2 stay open; how Next.js forwards a cancelled request at M5 can only be checked at build time.
Next action: dispatch the repair step (e.g. `B14b-repair-milestone-prompts`) to `product-architect`, then re-check before `template-v1`.
<!-- VERBATIM:END -->
