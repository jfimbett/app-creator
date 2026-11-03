# RESPONSE — m1-01-plan

- From: project-orchestrator → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: 52b5656d-4ccc-4fc9-8c32-b14d7528b46f (local Claude Code transcript; not committed)
- Finished: 2026-11-03T18:27:23.038Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
# M1 Foundation: step plan

**Inputs read:** the brief at `template-v1` (all 487 lines), `FOLLOWUPS.md` (empty), `milestones/plan.md` slices 1.1–1.6, the M1 rows of `acceptance.md`, the API section of `architecture.md`, `orchestrate-steps`, the skills index and the agents. Since `template-v1`, `main` only adds step records, `PROGRESS.md` and `scripts/verify-ref.sh`. Config still has `"app": null`.

## Shared contracts (every parallel step follows these)

- **API shapes:** the brief §5 "API at M1" table, plus `SourceInfo`, `Provenance` and `MetricValue` from `architecture.md` "API". `architecture.md` leaves out two things the brief has: the overview's `notes` and its `years` parameter. The brief wins. m1-14 adds a decision row for this.
- **Error envelope:** `{"error":{"code","message","details","reference"}}`.
- **Fixture format:** the brief §6 rules for what each file keeps, plus the manifest schema (`schema_version: 1`, the per-file fields, `synthetic: false`). The synthetic tree goes in `be/tests/synthetic/` with a `"_synthetic"` key and `"synthetic": true`.
- **Who edits what:** each step touches only its listed paths. Only m1-05 and m1-14 edit `milestones/*.md`, and the owner integrates those edits one at a time. Parallel steps put proposed decision-log rows in their Handoff. Only m1-09 touches `fe/package*.json`.

## Steps

| id | agent | skills | scope (files) | done when | parallel? |
|---|---|---|---|---|---|
| m1-02-skeleton | backend-engineer | build-feature | Run `create-app` and set the exact `"app"` entry. Delete `examples/sec-analytics/docs/`. Run `npm run setup`. Add the three `.env.example` entries. Replace the scaffold README with a stub. Not in scope: any SEC code. | `check-toolkit` and `verify` both exit 0; the scaffold smoke still passes (M1-AC6 skeleton) | no (everything depends on it) |
| m1-03-assistant-files | docs-writer | write-docs | `examples/sec-analytics/CLAUDE.md`, the nested `sec-edgar-data` skill and `.claude/agents/sec-data-specialist.md`, all per §5. Include the notes on nested-skill loading and Cline. | `check-toolkit` exits 0; the frontmatter is exactly as in §5 | yes, alongside 04 and 08–09 |
| m1-04-sec-client | backend-engineer | integrate-api, test-and-check | `be/app/clients/sec.py`, `logic/cik.py`, `logic/concepts.py`; tests `test_sec_client.py` (respx, fake clock) and `test_cik.py`, written first (failing), then the code. No live calls. | `pytest -q` passes for both test files; `ruff check .` exits 0 (M1-E2 at unit level) | yes, alongside 03 and 08–09 |
| m1-05-capture-fixtures | backend-engineer (`SEC_USER_AGENT` in the environment) | integrate-api, manage-data | `be/scripts/capture_fixtures.py`, then one run (7 requests). Writes `fixtures/` (data, manifest, README, `.gitattributes`), `be/tests/synthetic/README.md` and `test_fixtures_manifest.py`. After capture, reads the fixture JSON by hand and adds FX1–FX4 to `acceptance.md`, plus the fiscal-year-end `[verify against fixtures]` row in `architecture.md`. If the capture is blocked: record N2 with the command, exit code and message, and create no partial fixtures. | Manifest test passes; the Handoff reports "live SEC: fixtures captured on <date>, 7 requests"; FX rows quote concept, unit, start, end, form, accession, filed date and `val` (M1-AC7) | no (needs 04) |
| m1-06-backend-api | backend-engineer | build-feature, plan-architecture, test-and-check | `settings.py`, `errors.py`, `models/`, `data/fixtures.py`, `logic/search.py`, `api/meta.py`, `api/companies.py` (search and profile), `main.py`. Tests: `test_search.py`, `test_api_m1.py` (all but overview), `test_no_network.py`. | `pytest -q` and `ruff` exit 0 (M1-AC3, M1-AC4, M1-E2) | yes, alongside 07 (different files) |
| m1-07-periods | backend-engineer | test-and-check | `logic/periods.py` and `test_periods.py`, which uses synthetic facts only. Write the tests first. | Every §9 periods case passes | yes, alongside 06 |
| m1-07b-overview | backend-engineer | test-and-check | `logic/statements.py`, the overview endpoint, `test_overview_fixtures.py` against FX1–FX4, and the overview cases in `test_api_m1.py`. | All pytest passes; at least 5 annual periods per company (M1-AC5 API) | no (needs 05, 06, 07) |
| m1-08-design-shell | design-lead | design-interface | `fe/app/globals.css` tokens, the `layout.tsx` shell, `AppHeader` (search slot only), `SourceBadge` and its test, `StatePanel`. | `lint`, `typecheck` and `test` pass; contrast of at least 4.5:1 noted | yes, alongside 04–07 and 09 |
| m1-09-frontend-lib | frontend-engineer | build-feature, test-and-check | `fe/lib/types.ts`, `api.ts`, `format.ts`, `combobox.ts`, `shortcuts.ts` and their Vitest files. Adds the exact `recharts` and `react-is` versions. | Vitest passes; the types mirror the contract | yes, alongside 04–08 |
| m1-10-screens | frontend-engineer | design-interface, build-feature | `CompanySearch`, `BackendStatus`, `CompanyProfile`, `KeyFigures`, `RevenueIncomeChart` and `ProvenanceTip`; pages `page.tsx`, `companies/[cik]`, `not-found` and `error`. Not in scope: `fe/app/api/` and any later-milestone navigation. | `verify` exits 0; the assistant has looked at its own screenshots (M1-AC1/2/5, M1-E1) | no (needs 07b, 08, 09) |
| m1-11-e2e | test-engineer | test-and-check | Write `fe/e2e/m1-foundation.spec.ts` (journeys 1–7, request host assertion, 3 widths, `scrollWidth` check) and delete `smoke.spec.ts`. | `verify` exits 0 and the 6 screenshots exist (M1-AC6) | no |
| m1-12-review | code-reviewer, test-reviewer, security-reviewer (SEC client, User-Agent handling, allowlist, no secret in fixtures or logs), ux-reviewer (screenshots, keyboard, ARIA) | review-changes | Read-only, against `git diff template-v1`. | Four reports with findings ranked by severity | yes, all four together |
| m1-13-repair | the owning builder for each finding | debug-issue | Fix the blocker and major findings. Each repair text goes into `FOLLOWUPS.md` first. | `verify` exits 0; each finding is fixed or recorded with a reason | per area |
| m1-14-docs-status | docs-writer | write-docs | The example README (demo universe, recapture, classroom-IP note), `acceptance.md` and `plan.md` statuses and progress log, the decision rows from Handoffs, and `AI-USAGE.md`. | Docs match the commands that were tested | no |
| m1-15-gate | project-orchestrator | orchestrate-steps | Brief §9 gate steps 1–5 and the record audit. The owner runs `npm run demo` by hand (journeys 1–3). | See below | no |

**Order:** 02, then {03, 04, 08, 09}, then 05, then {06, 07}, then 07b, then 10, 11, 12, 13, 14, 15.

## Gate

The milestone passes only when all of these hold:

- `npm run check-toolkit` exits 0.
- `npm run verify` exits 0 offline, with its summary line recorded.
- `npm run demo` works with no `.env`.
- All six screenshots have been opened and described.
- Every item in M1-AC1–AC7, M1-E1/E2 and V1–V3 is either passing with evidence or marked blocked.
- The fixtures are authentic (no N2 blocker; without them the gate fails).
- No review blocker is open.
- The `runs/m1` audit is clean.
- `git status` shows only the allowed paths, and the toolkit is untouched except the one new agent.

Decision: plan

## Handoff
Changes: none (orchestrator is read-only)
Verification evidence: read `git show template-v1:milestones/01-foundation/PROMPT.md` (all of it), FOLLOWUPS.md, plan.md, the M1 rows of acceptance.md, the API section of architecture.md, the skills index and the agents; `git diff template-v1 --stat` shows only step records, PROGRESS.md and scripts/verify-ref.sh. I ran no checks because no app exists yet.
Remaining findings: (1) architecture.md's overview lacks `notes` and `years`; the brief wins and m1-14 records a decision row. (2) plan.md slice 1.6 lists 1440 and 390 px but the brief requires 1440, 1366 and 390; the brief wins. (3) If `SEC_USER_AGENT` is missing at m1-05, the run is blocked (N2): steps 07b and 10–11 stall and the gate fails.
Next action: m1-02-skeleton, backend-engineer.
<!-- VERBATIM:END -->
