---
name: build-feature
description: Use when asked to add, change or continue a feature, or to build the next slice of the app's plan.md, once product.md and architecture.md are agreed; also when a dispatched step asks a builder agent to implement one slice and return a handoff.
---

# Plan and build one feature slice

One slice at a time: plan it, build it logic-first with tests, check it like a user would, then report and
checkpoint. A slice is small: one user-visible capability or one removed risk, one sitting, about five files.

**Paths.** `<docs>`, `<frontend>`, `<backend>` come from `app-creator.config.json` (`app.docsDir`,
`app.frontendDir`, `app.backendDir`). Root commands and working modes: [docs/TOOLKIT.md](../../../docs/TOOLKIT.md)
§3–4.

## Inputs

- `<docs>/product.md`, `architecture.md`, `acceptance.md`, `plan.md`. If `product.md` or `architecture.md` is
  missing or not agreed, use [product-interview](../product-interview/SKILL.md) first.
- The request: the owner's words, the next `todo` slice in `plan.md`, or, in delegated mode, the step prompt
  (its "done when" and the files it may touch).
- The actual code: read the files the slice touches before planning.
- The working mode: **interactive** (default: the owner approves the plan and each commit) or **delegated**
  (a recorded brief; `project-orchestrator` plans and gates steps, see
  [orchestrate-steps](../orchestrate-steps/SKILL.md)).

## Actions

1. **Plan the slice** in a short message:
   - what the user can do afterwards, and which acceptance criteria it makes pass (add new criteria to
     `acceptance.md` if the request is new; calculations get a known-answer row first);
   - the files to create or change, one line each, by layer (logic, data access, API, UI; see
     [plan-architecture](../plan-architecture/SKILL.md));
   - the checks you will run (which tests, which Playwright journey, at which widths);
   - risks or decisions only the owner can make.
   If the request changes scope (a new MVP feature, an item under "Explicitly not in the MVP", a new capability
   such as accounts, payments or a paid service), say so and stop for the owner. If the slice needs more than
   about five files or one sitting, split it and update `plan.md`.
2. **Get the go-ahead.**
   - Interactive: wait for the owner's yes. Routine edits inside the agreed plan need no separate approval.
   - Delegated: the orchestrator's step plan is the go-ahead for routine work. Do not widen the step; anything
     outside its "done when" or file list goes into the handoff as a finding.
3. **Build logic first, with tests** (`test-and-check`):
   1. write the failing test for the logic (pytest in `<backend>/tests/`, or Vitest for pure frontend logic),
      using the known answers in `acceptance.md`; run it and see it fail;
   2. implement the pure function in `<backend>/app/logic/`; run the test until it passes;
   3. data access (`integrate-api`, `manage-data` when the slice touches them), then the API endpoint with its
      pydantic models and error codes, with a pytest test through FastAPI's `TestClient`;
   4. the interface (`design-interface`): the typed API client call, the screen and all its states, then a
      Playwright spec in `<frontend>/e2e/` for the slice's journey.
   Keep calculations out of React and chart code: the logic layer prepares every value cards, charts and tables
   show. New settings go in `.env.example` (names only); tests and `npm run demo` work without `.env`.
4. **Run the checks** after each step: the single test you are working on, then the full suite with
   `npm run verify` from the repository root before calling the slice done. It must exit 0.
5. **Check the journey** for the slice: `npm run dev` (or `npm run demo` for offline data), open
   http://127.0.0.1:3000 and do what the user would. Open the Playwright screenshots in
   `<frontend>/test-results/` at both widths. If you cannot view the screen, give the owner the exact clicks and
   expected results and report the journey as **not verified**.
6. **Update the documents:** slice status and progress log in `plan.md` (checks run, exit codes); criteria status
   in `acceptance.md` (`passing (test: <file::name>)`); decisions in `architecture.md`; a line in `AI-USAGE.md`
   for meaningful AI help (design, code, a bug found).
7. **Report and checkpoint.**
   - Interactive: the change report from `AGENTS.md`, then propose a commit (`feat: ...`, `fix: ...`, `test: ...`).
   - Delegated (a dispatched step): end with the `## Handoff` block (TOOLKIT §7). The owner re-runs the checks,
     the orchestrator judges accept / repair / blocked, and the owner commits within the delegation. A repair is a
     new step with its own prompt; do not quietly keep changing files after the handoff.
   For larger slices and any change to calculations, accounts, payments or secrets, offer `review-changes` on the
   commit.

## Outputs

Working code for the slice in the right layers, tests (pytest, Vitest, Playwright as relevant), updated
`plan.md`, `acceptance.md` (and `architecture.md` if a decision was made), a change report or a handoff, and a
proposed (interactive) or owner-made (delegated) commit.

## Verification

- The new tests failed before the change and pass after it (show the failing run once).
- `npm run verify` exits 0 from the repository root.
- Each criterion the slice claims is marked passing with the test that proves it, or checked by hand with the
  date.
- The journey was exercised and the screenshots looked at, or the gap is stated with manual steps.
- `git status` shows only files in the slice's plan.

## Stop when

- The slice's criteria pass and the report or handoff is given. Do not start the next slice without the owner
  (interactive) or the orchestrator's next step (delegated).
- **Stop and ask** when: the plan needs a decision only the owner can make; a check fails twice after two
  different fix attempts (switch to `debug-issue`); the change needs a new paid service, personal data or a new
  secret; or the code contradicts `architecture.md`.
- Delegated mode: never treat the delegation as permission for new scope, money, publication, personal data or
  secrets; record those as blockers in the handoff.

## Common mistakes

- Building three features in one go, so nothing can be reviewed.
- Starting with the screen and testing the numbers by looking at them.
- Reporting "done" because the code was written or the app started: done means the criteria were checked and
  `npm run verify` passed.
- Running only the backend tests and skipping typecheck, build or the Playwright journey.
- Silently adding features listed under "Explicitly not in the MVP".
- In a dispatched step: editing files outside the step, or a handoff that says "all tests pass" with no command
  and exit code.

## Example

Slice 3 "Weekly totals table" (criteria AC2, CALC1, E2) in delegated mode:

1. Step prompt from the orchestrator: "done when AC2/CALC1/E2 pass and `npm run verify` exits 0; files:
   `backend/app/logic/totals.py`, `backend/tests/test_totals.py`, `backend/app/main.py`,
   `frontend/app/weekly/page.tsx`, `frontend/e2e/weekly.spec.ts`".
2. `test_totals.py::test_weekly_total_known_answer` (5 + 7 = 12.0 km; change +2.0) and
   `test_missing_previous_week` (change `None`, note "no runs last week") fail; implement `weekly_totals`; pass.
3. `GET /api/weekly-totals?week=2026-W12` with `TestClient`; `422 invalid_week` test.
4. Page with loading/empty/error states; Playwright at 1366 and 390 px; screenshots opened.
5. `npm run verify` → exit 0. Handoff:

```
## Handoff
Changes: backend/app/logic/totals.py, backend/app/main.py, backend/tests/test_totals.py, frontend/app/weekly/page.tsx, frontend/e2e/weekly.spec.ts, app/docs/plan.md, app/docs/acceptance.md
Verification evidence: npm run verify (exit 0: 9 pytest, 6 vitest, 4 playwright); screenshots weekly-1366, weekly-390 opened
Remaining findings: week picker has no keyboard shortcut (not in criteria)
Next action: orchestrator judges slice 3
```
