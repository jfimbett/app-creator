# Acceptance criteria

Each criterion is checkable: a starting state, an action, an expected result. Status: `open`, `passing
(test: <test name>)`, `checked by hand on <date>`, or `failing`.

## Main user journey

| Id | Feature | Given | When | Then | Status |
|---|---|---|---|---|---|
| AC1 | F1 | <starting state> | <user action> | <visible result> | open |

## Screens (how each was checked)

| Id | Screen / state | Expected | Test | Browser check | Looked at by |
|---|---|---|---|---|---|
| V1 | <dashboard, normal data, phone width> | <cards wrap, no sideways scrolling, chart readable> | <test name or –> | <date or "not run"> | <Claude (screenshots) / student, date> |

## Calculations (known answers)

Expected values are established independently of the code: by written hand working (every step), a cited source
value, or the student's spreadsheet; then cross-checked by a separate computation that does not use the app's code.

| Id | Number | Inputs (example) | Hand working or source | Expected result | Tolerance | Status |
|---|---|---|---|---|---|---|
| CALC1 | <e.g. net margin> | <net income 75, revenue 1,200 (USD m)> | <75 ÷ 1,200: 1,200 × 0.06 = 72, remainder 3; 3 ÷ 1,200 = 0.0025; total 0.0625> | <0.0625 = 6.25 %> | <exact> | open |

## Edge cases and errors

| Id | Situation | Expected behaviour | Status |
|---|---|---|---|
| E1 | <missing value, empty upload, API down, wrong user> | <clear message, no crash, nothing leaked> | open |
| E2 | <a value is missing / zero / negative / from a period that is not comparable> | <shown as "n/a" with a reason / "0.0" / with a minus sign / no change computed, with a note> | open |

## Permissions (only if accounts exist)

| Id | User | Tries to | Expected | Status |
|---|---|---|---|---|
| P1 | signed-out visitor | open a customer's page | redirected to sign-in | open |
