# Implementation plan: SEC Analytics (App Creator example)

Status: agreed on 2026-11-03 (delegated, see [docs/PRODUCT-DECISIONS.md](../docs/PRODUCT-DECISIONS.md))

Five milestones are five **student-facing releases**. Each one is built in several small, recorded steps
(`runs/m<n>/`), never in one agent call (GOAL.md §8). The slices below are the planned steps. The
`project-orchestrator` may split them further, add review or repair steps, and records each one.

**Ground rules for every slice:**

- Start from the previous milestone's tag.
- Do not touch the toolkit (`.claude/`, `scripts/`, `scaffold/`, `AGENTS.md`, `CLAUDE.md`, `docs/TOOLKIT.md`), except
  that slice 1.1 adds `.claude/agents/sec-data-specialist.md`.
- Do not touch the milestone `PROMPT.md` files, which are immutable once committed.
- End with `npm run verify` exiting 0, then update the slice status and progress log here and the statuses in
  [acceptance.md](acceptance.md).

Paths are relative to `examples/sec-analytics/` (written `fe/` for the frontend and `be/` for the backend).

## M1 — Foundation (from `template-v1` → tag `m1`)

| # | Slice | Criteria | Owner (agent) | May touch | Must not touch | Skills | Status |
|---|---|---|---|---|---|---|---|
| 1.1 | Example skeleton: copy `scaffold/` into `examples/sec-analytics/` (`npm run create-app -- --name "SEC Analytics" --dir examples/sec-analytics`), set `docsDir` to `milestones` and `demoEnv`/`devEnv` in `app-creator.config.json`, write `examples/sec-analytics/CLAUDE.md` (SEC rules from [architecture.md](architecture.md#financial-data-rules)) | M1-AC6 (skeleton passes) | backend-engineer | `examples/sec-analytics/**`, `app-creator.config.json` | `milestones/*.md` except status updates | build-feature | todo |
| 1.2 | Authentic fixtures: `be/scripts/capture_fixtures.py` (allowlisted, throttled, owner's `SEC_USER_AGENT`), trimmed submissions, Company Facts and ticker entries for AAPL, MSFT, GOOGL; `fixtures/manifest.json`. If blocked: record the blocker (N2), no manufactured data | M1-AC7 | backend-engineer | `be/scripts/`, `fixtures/`, `.env.example` (names only) | `fe/` | integrate-api, manage-data | todo |
| 1.3 | Backend M1 API: settings, `data/fixtures.py`, `logic/cik.py`, `logic/search.py`, `/api/meta`, `/api/companies/search`, `/api/companies/{cik}`, error envelope | M1-AC3, M1-AC4, M1-E2 | backend-engineer | `be/app/`, `be/tests/` | `fe/`, `fixtures/` | build-feature, test-and-check, plan-architecture | todo |
| 1.4 | Overview data: first version of `logic/periods.py` (annual selection, dedupe) for revenue and net income; `/api/companies/{cik}/overview` with provenance | M1-AC5 | backend-engineer | `be/app/logic/`, `be/app/api/`, `be/tests/` | `fe/` | test-and-check | todo |
| 1.5 | Dark terminal shell, keyboard search, profile and dashboard, `SourceBadge`, demo-universe note, loading/empty/error states | M1-AC1, M1-AC2, M1-AC5, M1-E1, V1–V3 | frontend-engineer (with design-lead) | `fe/app/`, `fe/components/`, `fe/lib/` | `be/` | design-interface, build-feature | todo |
| 1.6 | Playwright journey (1440 and 390 px), review (code, ux, test), milestone README, checkpoint | M1-AC1–M1-AC7 | test-engineer, then reviewers | `fe/e2e/`, `milestones/01-foundation/README.md` | app logic, except fixes found by the review | test-and-check, review-changes, orchestrate-steps | todo |

## M2 — Financial intelligence (from `m1` → `m2`)

| # | Slice | Criteria | Owner | May touch | Must not touch | Skills | Status |
|---|---|---|---|---|---|---|---|
| 2.1 | SEC client and cache: `clients/sec.py` (allowlist, redirects, User-Agent, 1 req/s, dedupe, Retry-After, 403 stop), `data/cache.py`, `data/source.py`, `source=demo\|live` | M2-AC2, M2-AC3, M2-AC9, M2-E12, M2-E13 | backend-engineer | `be/app/clients/`, `be/app/data/`, `be/tests/`, `.env.example` | `fe/` | integrate-api, manage-data, test-and-check | todo |
| 2.2 | Concept mapping verified against the fixtures, full `logic/periods.py` (350–380 days, instants, restatement policy) | M2-AC4, M2-E1–M2-E7, M2-E11 | backend-engineer | `be/app/logic/`, `be/tests/`, `examples/sec-analytics/CLAUDE.md` | `fe/` | test-and-check | todo |
| 2.3 | Ratios and derived metrics, `logic/metrics.py`; fixture-based known answers added to acceptance.md **before** their tests | M2-AC7, CALC1–CALC10, M2-E8–M2-E10 | backend-engineer (expected values: product-architect) | `be/app/logic/`, `be/tests/`, `milestones/acceptance.md` (calculation rows) | `fe/` | test-and-check | todo |
| 2.4 | `/api/metrics`, `/api/companies/{cik}/financials`, `/metrics`; live search via the ticker map | M2-AC1, M2-AC4, M2-AC6, M2-AC8 | backend-engineer | `be/app/api/`, `be/app/models/`, `be/tests/` | `fe/` | build-feature | todo |
| 2.5 | Mode selector, statement tables, key-figure strip, metric explorer chart, provenance tooltips, missing/unavailable display | M2-AC1–M2-AC6, M2-AC8, V1–V3 | frontend-engineer (with design-lead) | `fe/` | `be/` | design-interface, build-feature | todo |
| 2.6 | E2E, reviews (code, security for the SEC client, test), live SEC smoke (manual, reported separately), README, checkpoint | all M2 | test-engineer, reviewers | `fe/e2e/`, `milestones/02-financial-intelligence/README.md` | – | review-changes, orchestrate-steps | todo |

## M3 — Filing intelligence (from `m2` → `m3`)

| # | Slice | Criteria | Owner | May touch | Must not touch | Skills | Status |
|---|---|---|---|---|---|---|---|
| 3.1 | Filing list: submissions (+ older pages when needed), 10-K/10-Q/amendments, `/api/companies/{cik}/filings`, "Latest in snapshot" label | M3-AC1, M3-AC2, M3-E1, M3-E4 | backend-engineer | `be/app/`, `be/tests/` | `fe/` | integrate-api, test-and-check | todo |
| 3.2 | Document fetch, `capture_fixtures.py --filings`, `logic/sanitize.py`, `logic/sections.py` (TOC skip, fallback), `/api/companies/{cik}/filings/{accession}` | M3-AC3, M3-AC4, M3-AC7, M3-E2, M3-E3, M3-E5 | backend-engineer | `be/app/`, `be/tests/` | `fe/` | test-and-check | todo |
| 3.3 | Filings view and reader: section navigation, text search, source link | M3-AC1, M3-AC3–M3-AC6, V1–V3 | frontend-engineer | `fe/` | `be/` | design-interface, build-feature | todo |
| 3.4 | E2E, security review (sanitization), README, checkpoint | all M3 | test-engineer, reviewers | `fe/e2e/`, `milestones/03-filing-intelligence/README.md` | – | review-changes, orchestrate-steps | todo |

## M4 — Comparative analysis (from `m3` → `m4`)

| # | Slice | Criteria | Owner | May touch | Must not touch | Skills | Status |
|---|---|---|---|---|---|---|---|
| 4.1 | `logic/compare.py` (comparability warnings, indexing), `logic/csv_export.py`, `/api/compare`, `/api/compare.csv` | M4-AC2–M4-AC7, CALC11, M4-E1–M4-E3 | backend-engineer | `be/app/`, `be/tests/` | `fe/` | test-and-check, build-feature | todo |
| 4.2 | Compare screen: company chips (2–4), metric selector, table, grouped bars and lines, index toggle, Export CSV | M4-AC1–M4-AC5, V1–V3 | frontend-engineer (with design-lead) | `fe/` | `be/` | design-interface | todo |
| 4.3 | E2E, reviews, README, checkpoint | all M4 | test-engineer, reviewers | `fe/e2e/`, `milestones/04-comparative-analysis/README.md` | – | review-changes, orchestrate-steps | todo |

## M5 — AI analyst (from `m4` → `m5`)

| # | Slice | Criteria | Owner | May touch | Must not touch | Skills | Status |
|---|---|---|---|---|---|---|---|
| 5.1 | `clients/openrouter.py` (models, key info, chat; errors; timeout; no retries), log redaction, Origin check, limits; `/api/ai/models`, `/api/ai/test-connection` | M5-AC3, M5-AC7, M5-E5, M5-E6 | backend-engineer | `be/app/`, `be/tests/` | `fe/` | integrate-api, test-and-check | todo |
| 5.2 | `logic/retrieval.py`, `scope.py`, `prompting.py`, `citations.py`; `/api/ai/chat` with mocked upstream | M5-AC4, M5-AC5, M5-E1–M5-E4 | backend-engineer | `be/app/`, `be/tests/` | `fe/` | test-and-check | todo |
| 5.3 | AI settings (masked key, memory, sessionStorage opt-in, model list, test, clear) and the analyst panel on company, filing and comparison screens; cancel | M5-AC1–M5-AC4, M5-AC6, M5-AC8, V1–V3 | frontend-engineer (with design-lead) | `fe/` | `be/` | design-interface, build-feature | todo |
| 5.4 | E2E with a mocked backend, security review (key handling), README stating "live AI: not verified" unless N1 is lifted, checkpoint | all M5; M5-AC9 stays `blocked: N1` | test-engineer, reviewers | `fe/e2e/`, `milestones/05-ai-financial-analyst/README.md` | – | review-changes, orchestrate-steps | todo |

Status values: `todo`, `in progress`, `done (<date>, commit <short hash>)`, `blocked: <reason>`.

## Progress log

| Date | Slice | What changed | Checks run and results (command, exit code) | Open problems |
|---|---|---|---|---|
| 2026-11-03 | planning | product, architecture, acceptance and plan written from the delegated decisions (step B12) | `npm run check-toolkit` (see the B12 record) | N1, N2 |

## Known problems and open questions

- **N1** Paid live AI validation is blocked: there is no test key. Mocked integration only (owner decides).
- **N2** Fixture capture and live SEC checks need the owner's `SEC_USER_AGENT` in the build environment. If it is
  missing, slice 1.2 is blocked and reported, and nothing is manufactured.
- The concept mapping, fiscal-year labels and fiscal year-ends are proposals marked `[verify against fixtures]`
  (slices 1.4 and 2.2).
- With three demo companies, the four-company comparison is shown only in tests and live mode (Q19).
