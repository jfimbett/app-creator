---
name: test-and-check
description: Use when writing or changing logic, calculations, data access or permissions, when deciding what to test, when tests pass but results look wrong, or before saying that a feature works.
---

# Meaningful tests and calculation checks

Test what could actually go wrong and would hurt the user. A passing test suite or a successful start-up is not proof
that the app works: the main journey must be checked too.

## Inputs

- `docs/acceptance.md` (criteria, known-answer calculations, edge cases, permissions), `docs/architecture.md` (test
  command, parts of the app).
- The code that changed, and the existing tests (where `docs/architecture.md` says: `app/tests/` or the
  framework's convention).
- For screens: [browser-checks.md](browser-checks.md) and the template [browser_check.py](browser_check.py).

## Choose tests by risk

| What changed | Test it with |
|---|---|
| A financial calculation | known-answer tests whose expected values were established independently (below); units, signs, rounding |
| Values prepared for cards or charts | tests on the shared layer: missing → empty with a reason (never 0), zero, negative, not-comparable periods |
| Parsing external data | fixtures with real-shaped and malformed data; missing fields; units |
| Saving and reading data | temporary database; save, read back, required and unique fields |
| Permissions or payments | one test per rule: allowed user succeeds, others refused |
| A screen or flow | framework test client or app test runner; then the journey check, with a browser check for critical interactions |
| Pure layout or wording | the journey check only; no unit test needed |

Do not write tests that only restate the code, check that a library works, or assert on private details that will
change with every refactor.

## Actions

1. **Write the test first** for new logic or a bug: run it and show that it fails for the expected reason. While
   a slice is in progress, deliberately failing tests are normal; the slice is complete only when they pass.
2. **Write or fix the code**, then run the test until it passes, then the full test command.
3. **Financial calculations** also need:
   - **independently established expected values**, recorded in `docs/acceptance.md` *before* the
     implementation is trusted. For each example, write the hand working: every arithmetic step, with inputs
     chosen so a person can check each step (round numbers, one tricky case per rule: a loss, a zero, a
     rounding half, a partial period). Acceptable sources of an expected value: that written hand working, a
     published figure from the source document (with source and date), or a spreadsheet the student built. Then
     cross-check the hand working with a separate computation that does **not** import, copy or call the app's
     code. If the two disagree, find out why before writing the test. Never take an expected value from the
     app's own output, and never rely on the language model's mental arithmetic alone;
   - checks of units and currency (thousands vs millions, % vs decimal), sign conventions, and period alignment
     (same fiscal year, same date, same period length);
   - an identity or bound when one exists (assets = liabilities + equity; shares sum to 100%; a margin between -1
     and 1 for a normal company), as a test or a validation in the code;
   - for numbers derived from external sources, one value checked by hand against the source and written in
     `docs/acceptance.md` with the source, date and value.
4. **Edge cases** from `docs/acceptance.md`: empty input, missing values, zero denominators, very large numbers,
   duplicate records, the external service down.
5. **Checking the journey:** start the app and go through the main user journey (or the changed part) with normal
   data and one bad input, against test data rather than the student's own database. Use what the project
   itself has installed: the framework's test client, Streamlit's `AppTest`, `curl` against a local server, and
   for critical screens and interactions the project's browser check ([browser-checks.md](browser-checks.md)).
   Then look at the screenshots. Report tests, browser check and visual inspection separately. If nothing can
   show the screen, give the student a numbered click-through with the expected result per step, and report the
   journey as **not verified** until they confirm.
6. **Record results:** update statuses in `docs/acceptance.md` and the checks column of `docs/plan.md`.

## Outputs

Tests in the project's test folder, updated acceptance statuses, and in the change report: the commands run, the
number of tests passed or failed, what the journey check showed, and what remains unverified.

## Verification

- New tests were seen failing before the fix and passing after.
- The full test command passes; failures are reported, never hidden or skipped.
- Each calculation in scope has a known-answer test whose expected value has written hand working (or a cited
  source) in `docs/acceptance.md`, and a units check.

## Stop when

- The risk table's tests for this change exist and pass, and the journey was checked or the gap stated.
- **Stop and ask** if an expected value is unknown (ask the student for the business rule rather than guessing),
  or if making a test pass would require changing the expected value.

## Common mistakes

- Changing a test's expected value to make it pass.
- An "independent" check script that imports the function it is supposed to check.
- Reporting a browser check or the passing tests as "it looks right".
- Tests that call live services or depend on today's date.
- Saying "all tests pass" when only some were run.
