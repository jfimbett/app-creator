---
name: test-and-check
description: Use when writing or changing logic, calculations, data access or permissions, when deciding what to test, when tests pass but results look wrong, when a page or endpoint is slow, or before saying that a feature works.
---

# Meaningful tests and calculation checks

Test what could actually go wrong and would hurt the user. A passing test suite or a successful start-up is not proof
that the app works: the main journey must be checked too.

Paths: `<backend>`, `<frontend>`, `<docs>` are `app.backendDir`, `app.frontendDir`, `app.docsDir` in
`app-creator.config.json`. The one command that runs everything is `npm run verify` at the repository root.

## Inputs

- `<docs>/acceptance.md` (criteria, known-answer calculations, edge cases, permissions), `<docs>/architecture.md`
  (parts of the app).
- The code that changed, and the existing tests: `<backend>/tests/` (pytest), `*.test.ts(x)` next to the code in
  `<frontend>` (Vitest), `<frontend>/e2e/` (Playwright).
- For screens: [playwright-journeys.md](playwright-journeys.md). For slowness: [performance.md](performance.md).

## Choose tests by risk

| What changed | Test it with |
|---|---|
| A calculation (financial, scientific, scoring) | known-answer tests whose expected values were established independently (below); units, signs, rounding |
| Values prepared for cards or charts | tests on the shared logic: missing → empty with a reason (never 0), zero, negative, not-comparable periods |
| Parsing external data | pytest with recorded and synthetic fixtures, HTTP mocked by `respx`; missing fields; units |
| Saving and reading data | pytest with a temporary database; save, read back, required and unique fields |
| An API endpoint | pytest with FastAPI's `TestClient`: status codes, response shape, validation errors (422), friendly errors |
| Permissions or payments | one test per rule: allowed user succeeds, others refused |
| Frontend logic (formatting, state rules) | Vitest on the pure function |
| A component's states | Vitest + Testing Library: loading, empty, error, normal |
| A screen or flow | a Playwright journey at 1366 px and 390 px, then visual inspection of the screenshots |
| Pure layout or wording | the journey check and a look; no unit test needed |

Do not write tests that only restate the code, check that a library works, or assert on private details that will
change with every refactor.

## The test tools on the standard stack

- **Backend (pytest).** Tests in `<backend>/tests/test_*.py`; `from fastapi.testclient import TestClient`. Use
  `tmp_path` for files and databases and `monkeypatch` for settings (`monkeypatch.setenv("DATA_MODE",
  "fixtures")`); no test needs `.env`. Mock outgoing HTTP with `respx` (pinned in the scaffold): unmocked
  requests fail, so a test cannot reach the internet. Example in
  [http-client-patterns.md](../integrate-api/http-client-patterns.md). Run alone: `<backend>/.venv/bin/python -m
  pytest -q` from `<backend>` (Windows: `.venv\Scripts\python`).
- **Frontend (Vitest).** `npm run test` in `<frontend>` (jsdom environment). Keep logic in plain functions in
  `lib/` so it can be tested without a browser; test components with `@testing-library/react` by role and text,
  as a user sees them:

  ```tsx
  import { render, screen } from "@testing-library/react";
  import { expect, test } from "vitest";
  import { formatAmount } from "@/lib/format";
  import { ValueCard } from "@/components/ValueCard";

  test("missing value is shown as a dash with a reason, not as 0", () => {
    expect(formatAmount(null)).toBe("—");
    render(<ValueCard label="Revenue" value={null} reason="Not reported" />);
    expect(screen.getByText("Not reported")).toBeTruthy();
    expect(screen.queryByText("0")).toBeNull();
  });
  ```

  (`formatAmount` and `ValueCard` are your own code; the scaffold's `lib/health.test.ts` and
  `components/HealthStatus.test.tsx` show the same pattern.)
- **Browser (Playwright).** Journeys in `<frontend>/e2e/`, run by `npm run verify` against the production build
  in demo (fixture) mode. Details, a full example and the visual-inspection checklist:
  [playwright-journeys.md](playwright-journeys.md).
- `npm run verify -- --quick` (per the launcher) skips the build and the browser test for a fast loop; the full
  `npm run verify` is what counts as evidence.

## Actions

1. **Write the test first** for new logic or a bug: run it and show that it fails for the expected reason. While
   a slice is in progress, deliberately failing tests are normal; the slice is complete only when they pass.
2. **Write or fix the code**, then run the test until it passes, then `npm run verify`.
3. **Calculations** (financial or any other numbers users rely on) also need:
   - **independently established expected values**, recorded in `<docs>/acceptance.md` *before* the
     implementation is trusted. For each example, write the hand working: every arithmetic step, with inputs
     chosen so a person can check each step (round numbers, one tricky case per rule: a loss, a zero, a
     rounding half, a partial period). Acceptable sources of an expected value: that written hand working, a
     published figure from the source document (with source and date), or a spreadsheet the owner built. Then
     cross-check the hand working with a separate computation that does **not** import, copy or call the app's
     code. If the two disagree, find out why before writing the test. Never take an expected value from the
     app's own output, and never rely on the language model's mental arithmetic alone;
   - checks of units and currency (thousands vs millions, % vs decimal), sign conventions, and period alignment
     (same year, same date, same period length);
   - **missing is not zero**: a value that is absent stays absent (`None`/`null`, shown as "—" with a reason),
     and a test proves it is never summed or charted as 0;
   - an identity or bound when one exists (parts sum to the total; shares sum to 100%; a ratio between -1 and 1
     where the definition guarantees it), as a test or a validation in the code;
   - for numbers derived from external sources, one value checked by hand against the source and written in
     `<docs>/acceptance.md` with the source, date and value.
4. **Edge cases** from `<docs>/acceptance.md`: empty input, missing values, zero denominators, very large numbers,
   duplicate records, the external service down (simulate it with `respx` or `page.route`).
5. **Checking the journey:** run `npm run verify` (it includes the Playwright journeys), or start the app (`npm
   run dev` / `npm run demo`) and run Playwright by hand. Go through the main journey with normal data and one bad
   input, against fixture or test data rather than the owner's own data. Then **look at the screenshots**. Report
   tests, browser check and visual inspection separately. If nothing can show the screen, give the owner a
   numbered click-through with the expected result per step, and report the journey as **not verified** until
   they confirm.
6. **Slow pages or endpoints:** measure before changing anything ([performance.md](performance.md)).
7. **Record results:** update statuses in `<docs>/acceptance.md` and the checks column of `<docs>/plan.md`.

## Outputs

Tests in the project's test folders, updated acceptance statuses, and in the change report: the commands run, the
number of tests passed or failed per tool, what the journey check showed, which screenshots were looked at, and
what remains unverified.

## Verification

- New tests were seen failing before the fix and passing after.
- `npm run verify` exits 0; failures are reported, never hidden, skipped or marked `xfail` to get green.
- Each calculation in scope has a known-answer test whose expected value has written hand working (or a cited
  source) in `<docs>/acceptance.md`, and a units check.
- Screenshots at 1366 px and 390 px exist for changed screens and were looked at.

## Stop when

- The risk table's tests for this change exist and pass, and the journey was checked or the gap stated.
- **Stop and ask** if an expected value is unknown (ask the owner for the business rule rather than guessing),
  if making a test pass would require changing the expected value, or if a check fails twice after two different
  fixes (`debug-issue`).

## Common mistakes

- Changing a test's expected value to make it pass.
- An "independent" check script that imports the function it is supposed to check.
- Reporting a passing browser check or passing tests as "it looks right".
- Tests that call live services, depend on today's date, or need the owner's `.env`.
- Saying "all tests pass" when only some were run (for example `--quick`, or only pytest).
- Optimizing without a before-and-after measurement.

## Example

Feature: "show the average order value per month". Hand working in `<docs>/acceptance.md`: January orders 100.00,
50.00, 0.00 (a free order) → 150.00 / 3 = 50.00; February has no orders → average **missing** (not 0, no division
by zero); March total 10.00 / 3 orders = 3.333… → shown as 3.33 (round half up). Cross-check in a spreadsheet.
pytest: `test_average_includes_free_orders`, `test_month_without_orders_is_missing`, `test_rounding_half_up`,
`TestClient` test that `/api/stats/aov` returns `null` with `"reason": "no orders"` for February. Vitest: the card
shows "—, no orders" for `null`. Playwright: the stats page at 1366 and 390 px, screenshots looked at (February
shows a gap in the chart, not a drop to zero).
