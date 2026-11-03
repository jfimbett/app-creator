# Showing SEC numbers honestly (SEC Analytics example)

Adapted from the toolkit's earlier financial-visuals guide for this example. The design tokens and exact strings are
in the milestone briefs (`milestones/*/PROMPT.md`) and [acceptance.md](../../../../../milestones/acceptance.md).

## One shared, tested layer

The backend logic (`backend/app/logic/`) computes every number once and returns display-ready values with unit,
period, kind (`reported` or `derived`), status, reason and provenance. The frontend only formats and draws what it
receives: it never adds, divides, rounds to a new value or decides that a value is missing.

## Honesty checklist

- **Missing is not zero.** `null` with a reason, shown as `—` plus `MISSING · <reason>`; a chart gap
  (`connectNulls={false}`), never a point at 0.
- **Zero is not missing.** A real zero is drawn and labelled. "Not meaningful" (for example a ratio with negative
  equity) is a third case with its own label.
- **Negative values** are obvious without colour: zero baseline always visible, a true minus sign (−).
- **Units on every axis, figure and tooltip** ("USD millions"); one unit per axis; no unlabelled second axis.
- **Periods:** every label says `FY<year> (ends YYYY-MM-DD)`; no change is computed across periods of different
  length.
- **Only real observations:** never fill gaps, extrapolate or add history to make a chart look fuller.
- **Accessible alternative:** each chart has a title and a table with the same values; tooltips also open on
  keyboard focus and never hold information found nowhere else.
- **Source on every panel** as text, never colour alone: `RECORDED SEC DEMO · snapshot <date>` (or
  `SYNTHETIC TEST DATA`), so a screenshot stays identified.
- **No market data:** no prices, market capitalisation or valuation multiples; no currency conversion.

## Choosing a visual

| The user wants to know | Use | Avoid |
|---|---|---|
| the latest value | a key figure: value, unit, fiscal year-end, provenance tooltip | a chart for one number |
| how a flow changed over years (revenue, net income) | a line with markers per fiscal year, plus the table | a smoothed line through few points |
| how balances changed (assets, debt) | a line on period end dates | evenly spaced labels hiding uneven gaps |
| how companies compare (M4) | bars sorted by value, same unit and comparable periods, or an index = 100 per company | pies; mixed currencies on one axis |
