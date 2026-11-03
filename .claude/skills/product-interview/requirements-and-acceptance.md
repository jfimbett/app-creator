# Requirements, MVP and acceptance criteria

A requirement is useful only if two people would agree whether it is met. This guide turns answers from the
interview into MVP features, exclusions, acceptance criteria and known-answer calculations that a test or a
person can check.

## 1. MVP features

An MVP (minimum viable product) is the smallest version that solves the customer's main problem end to end.

- Three to five features. Each one has an id (`F1`), one sentence in the customer's words, and a reason
  ("without it the coach still needs the spreadsheet").
- A feature is a user capability, not a technical part. "F2 See weekly totals per member" is a feature;
  "set up the database" is a slice of work.
- Apply the removal test to each feature: *if we drop it, does the main journey still work?* If yes, it moves to
  "Explicitly not in the MVP".
- Every exclusion gets a short reason ("accounts: the coach is the only user"). Exclusions protect the team from
  scope creep; agents must not build them (AGENTS.md rule 7).

## 2. Acceptance criteria

Write each criterion as **Given** (starting state and data) / **When** (one user action) / **Then** (a visible or
testable result with concrete values).

| Weak | Checkable |
|---|---|
| "Search works well." | Given the demo data, when the user types `ana` in the search box, then the list shows "Ana Ruiz" within 1 second and no other member. |
| "Errors are handled." | Given the backend is stopped, when the user opens the weekly table, then the page shows "Could not load runs. Is the backend running? Try again." and a **Try again** button; no stack trace. |
| "Mobile friendly." | At 390 px wide, the weekly table scrolls inside its own box and the page has no sideways scrolling. |
| "Correct totals." | Given the runs in CALC1, the weekly total for Ana in week 12 is `12.0 km`. |

Checklist for every criterion:

- [ ] It names concrete input data (values, ids, or "the demo fixtures").
- [ ] It has exactly one action.
- [ ] Its result is observable: text on screen, a value, a status code, a downloaded file, a time limit.
- [ ] It says how it will be checked: automated test (pytest, Vitest, Playwright) or by hand, and by whom.
- [ ] It traces to a feature (`F1`) or an edge case (`E1`).

Cover, for each feature: the normal case, an empty case (no data yet), an invalid input, and a failure of
whatever it depends on (backend down, external API unavailable). Screens also get one criterion per agreed
width (390 px and 1366 px; see `design-interface`).

## 3. Calculations with known answers

Every number the app computes (totals, averages, rates, changes, scores) gets a row in the Calculations table of
`acceptance.md`:

1. **Formula** in words and symbols, with units: `weekly total (km) = sum of run distances (km) in ISO week`.
2. **An example with a known answer**, established **independently of the code**: written hand working (every
   step), a cited source value, or the owner's spreadsheet. Never the app's own output.
3. **Rounding rule**: where and how (`1 decimal, half away from zero, only for display`).
4. **Edge cases** with their expected display:
   - missing input → "n/a" with a reason, **never 0**;
   - a real zero → `0.0`;
   - negative values → minus sign;
   - not meaningful (division by zero, change from a negative base, periods of different length) → its own
     label, no number;
5. **Tolerance**: `exact` for counts and money in cents; a stated tolerance (e.g. `±0.0001`) for floating point.

Example (a neutral finance case, because it shows "missing is not zero" well):

| Id | Number | Inputs | Hand working | Expected | Tolerance |
|---|---|---|---|---|---|
| CALC1 | net margin | net income 75, revenue 1,200 (both USD m) | 75 ÷ 1,200: 1,200 × 0.06 = 72, remainder 3; 3 ÷ 1,200 = 0.0025; total 0.0625 | 0.0625 = 6.25 % | exact |
| CALC2 | net margin, revenue missing | net income 75, revenue not reported | no denominator | "n/a (revenue not reported)" | – |
| CALC3 | net margin, revenue zero | net income 75, revenue 0 | division by zero | "not meaningful (revenue is 0)" | – |

The test for CALC1 asserts `0.0625`; a separate check (a spreadsheet, or a short script that does not import the
app's code) confirms the same value. `test-and-check` describes how to write these tests.

## 4. From features to the plan

- Order slices by the main journey: what the user does first is built first.
- Each slice: one sitting, at most about five files, visible to a user or removes a real risk, ends with
  `npm run verify` passing and a commit.
- Each slice lists the criteria it makes pass. A slice with no criterion is either setup (the walking skeleton)
  or a sign that a criterion is missing.
- Put the riskiest unknown early (an external API whose format you have not seen, a calculation nobody has
  checked by hand).

## 5. Final check before asking for agreement

- [ ] Every feature `F*` has at least one `AC*`.
- [ ] Every calculation has a `CALC*` row with hand working and edge cases.
- [ ] Every main screen has its loading, empty and error states described.
- [ ] Every exclusion has a reason.
- [ ] Nothing is still `[to confirm]` that slice 2 depends on.
