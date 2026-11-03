# Refactoring safely

Companion to [SKILL.md](SKILL.md). **Refactoring** means changing how code is organized without changing what
it does: renaming, splitting a long function, moving code to the right layer, removing duplication. If behavior
changes, it is not a refactor; it is a feature or a fix and follows `build-feature` or `debug-issue`.

## When (and when not)

Refactor when it makes the next change easier or a real problem smaller: a function too long to understand,
the same logic copied in three places, SQL inside a route, calculation code inside a React component.

Do not refactor:

- while tests are failing (fix them first, or you cannot tell what broke what);
- in the same commit as a fix or a feature;
- code you are not otherwise touching, "while you are there", without the owner's agreement;
- to match personal taste, or to add abstractions "for later".

## The loop

1. **Green first.** Run `npm run verify` (or at least the tests covering the code). Everything passes. Note the
   numbers ("pytest 38 passed, Vitest 12 passed, Playwright 4 passed").
2. **Check the safety net.** Are there tests that would fail if the behavior changed? If not, write
   **characterization tests** first: tests that record what the code does now (inputs → current outputs), even
   if that output looks odd. Commit them separately (`test: characterize <module> before refactor`). If current
   behavior looks wrong, stop: that is a bug to report, not something to change silently.
3. **One small step.** One rename, one extraction, one move. Use the editor's rename where possible; search with
   `grep -rn "old_name" <backend> <frontend>` to catch strings, tests and docs.
4. **Run the tests after each step.** Still green: continue. Red: undo the step (`git restore <file>` for
   uncommitted changes you just made) and take a smaller step.
5. **Commit with no behavior change:** `refactor: move price formatting into lib/format.ts`. The message says it
   is a refactor; the diff contains no test expectation changes (except moved or renamed tests).
6. **Full check before you stop:** `npm run verify` exits 0, and a quick look at the main journey (screenshots)
   shows the same result as before.

## Common refactors on this stack

| Smell | Refactor | Where it goes |
|---|---|---|
| SQL or HTTP calls inside a FastAPI route | extract a function into the data-access or client module | `<backend>/app/db.py`, `app/clients/` |
| Calculation inside a route or React component | extract a pure function and test it | `<backend>/app/logic/` or `<frontend>/lib/` |
| The same formatting in several components | one helper with tests | `<frontend>/lib/format.ts` |
| A 300-line component | split into smaller components by section; keep state in the parent | `<frontend>/components/` |
| Magic numbers (timeouts, limits) | named constants or settings | top of the module or `config.py` |
| Copy-pasted Pydantic models | one shared model | `<backend>/app/models.py` |

Keep the layers from `<docs>/architecture.md`: routes call logic, logic calls data access and clients. A refactor
that changes this structure is an architecture decision: record it in the decision log first.

## Review and record

- A refactor diff should be easy to review: if a reviewer cannot confirm "no behavior change" in a few minutes,
  split it.
- Record it in the progress log of `<docs>/plan.md` (what and why), and in `AI-USAGE.md` when the AI proposed it.
- `code-reviewer` (`review-changes`) is the right reviewer for larger refactors.

## Example

Goal: the stats route contains a 40-line average calculation. Step 1: verify green (pytest 20 passed). Step 2:
existing endpoint tests cover normal, empty and missing months; add one characterization test for rounding.
Commit `test: pin rounding of monthly averages`. Step 3: extract `monthly_average(orders)` into
`app/logic/stats.py`, route calls it; tests green. Step 4: move its tests next to the new module. Commit
`refactor: extract monthly average into logic layer`. `npm run verify` exit 0; chart screenshot unchanged.
