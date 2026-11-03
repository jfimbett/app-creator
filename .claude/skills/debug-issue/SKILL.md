---
name: debug-issue
description: Use when something is broken or wrong - an error message, a crash, a wrong number, a blank chart, a page that does not load, a failing test, or behaviour that differs from docs/acceptance.md.
---

# Debug: reproduce, locate, fix, verify

Find the cause before changing code. A fix that is not proven by a failing-then-passing check is a guess.

## Inputs

- The student's description: what they did, what they expected, what happened (the exact error text or a
  screenshot description). Ask for any of these that are missing, at most three questions.
- The code, logs and tests in `app/`; `docs/acceptance.md` for the expected behaviour.

## Actions

1. **Reproduce.** Run the exact steps, command or test and see the failure yourself. Write down the smallest set of
   steps that shows it. If you cannot reproduce it, say what you tried and ask for more detail; do not fix blind.
2. **Capture it in a test** that fails for the reason the student sees (`test-and-check`). If a test is not
   practical (pure layout), write the manual reproduction steps in the report instead.
3. **Locate the cause.** Read the error from the bottom up; follow the data from the input to where it goes wrong;
   check recent changes (`git diff`, `git log`); add temporary prints or logging if needed (remove them afterwards).
   State the cause in one sentence, with the file and line.
4. **Fix the cause, not the symptom.** The smallest change that makes the failing test pass. Do not change the
   expected value of a test to make it pass. Do not wrap errors in try/except to hide them.
5. **Verify:** the new test passes, the full test command passes, and the original reproduction steps now behave
   correctly in the running app.
6. **Look for siblings:** search for the same mistake elsewhere (same function, same pattern) and list them; fix them
   only if the student agrees.
7. **Record:** progress log in `docs/plan.md`; a line in `AI-USAGE.md` if the AI found or fixed it; change report;
   proposed commit (`fix: ...`).

## Outputs

Reproduction steps, the cause (file:line, one sentence), the fix, a regression test, check results, a change report.

## Verification

- The regression test failed before the fix and passes after.
- The original steps were re-run against the fixed app.

## Stop when

- The cause is identified, fixed and verified.
- **Stop and ask** after two different fix attempts fail, when the cause is outside the app (a service outage, a
  machine set-up problem, a data error at the source), or when the "bug" is really a missing or unclear business
  rule. Report what is known, what was ruled out and the options.

## Common mistakes

- Rewriting a whole file when one line was wrong.
- "Fixing" by catching the exception and returning an empty result.
- Declaring it fixed because the error message disappeared.
