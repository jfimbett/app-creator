# Working as a team of five

Part of [git-collaboration](SKILL.md). The student-facing summary is
[docs/GITHUB-COLLABORATION.md](../../../docs/GITHUB-COLLABORATION.md).

## Roles (everyone codes; each role owns decisions in one area)

| Role | Owns | Main folders | Matching agent |
|---|---|---|---|
| Product & integration lead | `plan.md`, acceptance criteria, Issue board, merges to `main`, releases | `<docs>/` | `project-orchestrator` (planning help) |
| Backend | API endpoints, data access, external services, backend tests | `<backend>/` | `backend-engineer` |
| Frontend | screens, components, client-side state | `<frontend>/src/` | `frontend-engineer` |
| Design & accessibility | design tokens, layout, charts' look, the 390 px and 1366 px views | styles, presentational components | `design-lead`, `ux-reviewer` |
| Quality & docs | fixtures, Playwright journeys, README/setup, reviews | tests, `<frontend>/e2e/`, docs | `test-engineer`, `docs-writer` |

`<docs>`, `<backend>`, `<frontend>` are the folders named in `app-creator.config.json`. Rotate roles between
milestones if the course wants everyone to learn every part. Identify people by role or GitHub username in
documents, never by email or other personal data.

## Shared contracts (agree them before parallel work)

A contract is a shape that two people's code depends on. Change it only through a small PR reviewed by everyone
it affects.

1. **API types.** The backend's response models (Pydantic) and the frontend's TypeScript types describe the same
   JSON. Write the shape in the architecture document first:
   ```ts
   // <frontend>/src/lib/api-types.ts  — mirrors the backend response model
   export type ResultRow = { id: string; label: string; value: number | null; unit: string };
   export type ResultsResponse = { rows: ResultRow[]; source: "live" | "fixture"; retrievedAt: string };
   ```
   `value: number | null` is part of the contract: missing is not zero, and both sides must handle `null`.
2. **Fixtures.** Shared example data in one folder (for example `<backend>/tests/fixtures/`), labelled recorded or
   synthetic, with no personal data. Frontend and tests use the same files, so everyone sees the same numbers.
3. **Route and file ownership.** Each endpoint and page has one owner in the plan; others propose changes by PR.
4. **Root commands.** Everyone uses `npm run setup`, `npm run dev`, `npm run verify`; nobody adds a private
   script the others must remember.
5. **Settings names** in `.env.example` (names and placeholders only). Each person creates their own `.env`.

## Daily rhythm

- **Start (5 min):** each person: done yesterday, doing today, blocked by. Update the board.
- **Integrate daily:** every in-progress branch merges `origin/main` into itself at least once a day and runs
  `npm run verify`. Small PRs merged daily cause small conflicts; week-old branches cause painful ones.
- **Review within a day:** each PR gets one reviewer who is not the author; rotate reviewers.
- **`main` is always green:** if `npm run verify` fails on `main`, fixing it is the team's first job
  (the integration lead coordinates; often `git revert <sha>` of the breaking merge, then a proper fix).
- **End of milestone:** the integration lead verifies `main` in a fresh clone, tags it (owner), and writes the
  changelog.

## Parallel work without collisions

- Contract PR first (types + fixture + stub endpoint returning fixture data). Then backend and frontend work in
  parallel against it.
- Two people editing the same file on the same day: talk first; split the file or sequence the work.
- Shared files that collide often (`package.json`, lockfiles, global styles, `plan.md`): keep edits tiny and merge
  them quickly.

## Example week (slice: "CSV export")

| Day | Backend | Frontend | Design | Quality & docs | Lead |
|---|---|---|---|---|---|
| Mon | contract PR: `GET /api/results.csv` stub + fixture | — | button placement sketch | test plan for A4.1–A4.3 | reviews contract PR, creates Issues |
| Tue | real CSV writer + pytest | button + download wiring | focus and narrow-width styles | Playwright journey | reviews |
| Wed | review frontend PR | review backend PR | review | README "Export" section | merges, `npm run verify` on `main` |
