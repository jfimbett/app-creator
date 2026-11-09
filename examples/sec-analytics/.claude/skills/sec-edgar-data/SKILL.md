---
name: sec-edgar-data
description: "SEC Analytics example only: use when working in examples/sec-analytics/ on SEC EDGAR fetches (the SEC client, User-Agent, allowlist, throttle), recorded fixtures and their manifest, Company Facts concept mapping, annual period selection and duplicates, financial ratios, or filing text. Covers adding a concept, recapturing fixtures and adding a hand-worked known-answer test."
---

# Work with SEC EDGAR data in the SEC Analytics example

The rules are in [the example's CLAUDE.md](../../../CLAUDE.md); this skill says how to apply them. Paths are relative
to `examples/sec-analytics/` (`backend/`, `frontend/`, `fixtures/`).

**Loading.** This skill sits in a `.claude/skills/` folder *below* the repository root, so Claude Code does not load
it at startup. It loads the first time Claude reads or edits a file in `examples/sec-analytics/`, and is then
addressed as `examples/sec-analytics:sec-edgar-data`
([research](../../../../../docs/research/claude-code-and-cline.md) §1). **Cline does not load nested skills or nested
`CLAUDE.md` files automatically:** open this file and the example's `CLAUDE.md` yourself.

## Inputs

- [milestones/architecture.md](../../../../../milestones/architecture.md): "Financial data rules", the API contract
  (`MetricValue`, `Provenance`, `SourceInfo`) and the decision log.
- [milestones/acceptance.md](../../../../../milestones/acceptance.md): criteria and the known answers (`FX…` rows).
- [docs/research/sec-edgar.md](../../../../../docs/research/sec-edgar.md): hosts, endpoints, why `fy`/`fp` belong to
  the filing, fair access.
- `fixtures/manifest.json` and the fixture JSON; `backend/app/logic/concepts.py` (`CAPTURE_CONCEPTS`, the revenue
  priority list), `backend/app/logic/periods.py`, `backend/app/clients/sec.py`.
- For charts and number display: [numbers-and-charts.md](numbers-and-charts.md).

## Actions

### Add or change a concept mapping

1. Check that the concept is in `CAPTURE_CONCEPTS`. If not, it is not in the fixtures: adding it means a
   recapture (below), which is a planned step, not a side effect.
2. Open the fixture `companyfacts/CIK##########.json` yourself and look at the concept's `units` for each demo
   company: which unit, which `form`, which `start`/`end` durations, whether every annual period has a fact.
3. Write the priority order (alternates are never summed) in `logic/concepts.py` and a decision-log row in
   `milestones/architecture.md` with what you saw in the fixtures.
4. Write the failing test first: synthetic facts in `backend/tests/synthetic/` for the edge cases (alternate
   concept per year, a year with none → `null`, `missing`, a reason), plus a known-answer test on the fixtures.

### Recapture fixtures

1. Only with the plan's agreement: a recapture changes every number and every known answer.
2. The person sets `SEC_USER_AGENT` in their own environment or root `.env`. You never read, print or write it.
3. From `backend/`: `.venv/bin/python scripts/capture_fixtures.py` (Windows:
   `.venv\Scripts\python.exe scripts\capture_fixtures.py`). It makes exactly the 7 allowlisted requests, prints only
   `SEC_USER_AGENT: set (value hidden)` and rewrites `fixtures/` and `manifest.json`.
4. Never hand-edit the result. Re-work the `FX…` known answers by hand from the new JSON, update
   `milestones/acceptance.md` first, then the tests.

### Add a known-answer test

1. Open the fixture JSON (not the app's output). Apply the rules by hand: 350–380-day duration, `10-K`/`10-K/A`,
   latest `filed`, then higher accession.
2. Add a row to `milestones/acceptance.md` quoting concept, unit, start, end, form, accession, filed and `val`.
   For a derived value, write the formula and the inputs with their own provenance.
3. Then write the test in `backend/tests/` asserting the value, the period and the accession.

## Outputs

Code and tests in `backend/`, updated `milestones/architecture.md` (decision rows), `milestones/acceptance.md`
(known answers, statuses), and, after a recapture, a new `fixtures/` tree with its manifest.

## Verification

- `ruff check .` and `pytest -q` with the backend venv, then `npm run verify` from the repository root, offline.
- Tests mock HTTP with `respx` (no pass-through); no test needs `SEC_USER_AGENT` or the network.
- The manifest test passes (every file listed, sha256 matches, `synthetic: false`, no synthetic marker in
  `fixtures/`).
- Every value on screen and in the API has provenance and a source label; missing values show `MISSING · <reason>`.

## Stop when

- The mapping, recapture or test is done and verified as above.
- **Stop and report** (record a blocker in `milestones/plan.md`) when:
  - `SEC_USER_AGENT` is not set: ask the person to set it; never invent one or ask them to paste it;
  - SEC answers 403: do not retry or work around it; report "SEC refused the request (403)";
  - 429/503 persists after the allowed retries, or there is no network;
  - a mapping cannot be verified against the fixtures (concept absent, units or periods unclear).

## Live checks (from M2)

The verified concept lists, formulas, restatement policy, cache and throttle are in the example's `CLAUDE.md` ("Financial data
rules") and `backend/app/logic/`. Fixtures cannot show every filer's tagging, so check a mapping change on real companies too:
`backend/scripts/live_sec_smoke.py` by hand, and awkward filers (a bank, negative equity, a 20-F filer). Never in `npm run verify`.

## Common mistakes

- Grouping facts by `fy`/`fp`: a FY2025 10-K reports FY2023 comparatives with `fy: 2025`.
- Summing duplicates or alternative concepts instead of choosing one fact.
- Turning a missing value into 0, or dropping a year silently.
- Letting year-to-date or quarterly durations into an annual series (check `end − start`).
- Mixing units or currencies in one series; converting currencies.
- Labelling synthetic data as SEC data, or hand-editing a fixture "to make a test pass".
- Taking a URL from a caller, following a redirect off the allowlist, or retrying a 403.
- Aligning companies to calendar years, converting currencies, indexing a ratio, or indexing in the frontend (M4: one rule, in
  `logic/compare.py`; see the example's `CLAUDE.md` "Comparison, indexing and CSV").
- Writing 0 for a missing value in a CSV, or a text cell that starts with `=`, `+`, `-` or `@` without the leading `'`.
- Letting the AI analyst see numbers the app did not compute, putting filing text in the system message, or treating a
  valid source chip as proof that the sentence is true (M5: see the example's `CLAUDE.md` "AI analyst").
