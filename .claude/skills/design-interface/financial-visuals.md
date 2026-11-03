# Visuals for financial data: choosing them, and keeping them honest

Charts are not required. Propose them only when the user must compare values, see a trend or spot an outlier
faster than a table allows. When a precise value matters more than a shape, a well-formatted table is better.

## Choosing a visual from the question the user asks

| The user wants to know | Propose | Avoid |
|---|---|---|
| "What is the latest value, and did it go up?" | summary cards: value, unit, period, change vs the previous comparable period | a chart for one number |
| "How did it change over the years?" (flows: revenue, profit) | bars per period, or a line with markers when there are many periods | a smooth line through 3 points |
| "How did it change over time?" (balances at a date: assets, debt, cash) | line or bars on a **date axis**, so uneven gaps look uneven | evenly spaced category labels |
| "How do these companies compare?" | horizontal bars sorted by value, same unit and period for all | pie charts; mixed periods |
| "What is it made of?" | stacked bars or a table with shares | pie with more than 4 slices |
| "Is it a ratio within a normal range?" (margin, leverage) | bars or a line with a visible zero line and a reference band if agreed | dual axes |
| "Which items need attention?" | a sortable table with the key column highlighted in text, not colour alone | a dashboard of decorative gauges |

## Default layout for a financial dashboard (propose, do not impose)

1. A selector for the entity or scenario (company, portfolio, period), if there is more than one.
2. A row of 3 to 5 summary cards: label, value, unit, period, change vs the previous comparable period, or a
   written reason why no change is shown.
3. One to three charts that answer the user's questions in `docs/product.md`.
4. The detailed table, notes and sources below, or behind a "View underlying data" section.

One primary action per screen still applies. Agree the cards and charts with the student before building them,
and record them in the "Screens and visuals" section of `docs/product.md`.

## Where the numbers come from: one shared, tested layer

Charts, cards and tables show numbers computed **once**, in the logic layer (for example `app/<module>/overview.py`
or `app/logic/charts.py`). That layer returns display-ready data: values, units, period labels, display texts,
and the reason for every gap or caveat. The chart code only draws what it receives; it never adds, divides,
rounds, or decides that a value is missing. This lets the normal test runner check every honesty rule below.

- Server-rendered pages: pass the prepared data to the page as embedded JSON (for example Django's `json_script`),
  not by building JavaScript strings.
- Python chart libraries (Plotly, Altair inside Streamlit or Dash): build the figure from the prepared data,
  in a small function that does no calculations.
- Round once, with the app's documented rule, in the shared layer, so the card, the chart and the table agree.

## Honesty checklist (each item a test on the shared layer, or a browser check)

- **Missing is not zero.** A missing value is `None`/`null` with a reason ("not reported", "not available"). It is
  drawn as a gap with an "n/a" label, never as a bar or point at 0. Lines do not connect across gaps.
- **Zero is not missing.** A real zero is drawn and labelled `0.0`. "Not meaningful" (for example a margin when
  revenue is zero, or a % change from a negative base) is a third case with its own label and reason.
- **Negative values are obvious without colour:** a visible zero line, a minus sign in labels, bars below the axis.
- **Units and scale:** the unit (`USD m`, `%`, `x`) on every axis, card and tooltip; the same unit for every series
  on one axis. If one series is ten times larger than another, do not let it flatten the other: offer a series
  selector or separate small charts, never an unlabelled second axis.
- **Periods:** each label says which period (fiscal year, quarter, date). Short, partial or transition periods are
  marked differently (pattern or outline, and in the label and tooltip), and no change is computed across them.
- **Incomparable observations** (different currency, different accounting basis, restated figures, different
  period length) are not placed on one axis without a visible note; if they cannot be compared, do not compare.
- **Only real observations:** never fill gaps, extrapolate or add history to make a chart look fuller. With 2 or 3
  periods, use value labels and wider bars.
- **Axes:** bars start at zero; a line chart's value axis may not start at zero only if the label says so.
- **Accessible alternative:** every chart has a title, a label for screen readers, and a visible text summary or
  table with every value. Tooltips are not reachable by keyboard, so they never hold information found nowhere else.
- **Synthetic data:** if the data is fictional or a sample, the chart itself carries a "SAMPLE DATA" mark, so a
  screenshot stays identified.
- **Source and date** of the data are visible near the chart when the product depends on trusted data.

## Chart libraries

- Prefer what the stack already has: Streamlit's charts or Plotly in path A; for server-rendered pages, one small
  charting library, chosen with the student.
- **Offline by default:** if a JavaScript library is used on server-rendered pages, keep one unchanged prebuilt
  file in the app's static folder (for example `static/vendor/<library>/`), with its licence file and a short
  README recording the version, where it came from and its published checksum. Loading it from a content
  delivery network (CDN) is a decision for the student to make, recorded in `docs/architecture.md`.
- Read the library's documentation for the installed version. Change single options rather than replacing whole
  default objects (replacing them can remove internal functions and crash interactions such as tooltips).
- Leave room for value labels: keep axis labels short, horizontal and on several lines if needed, and add padding
  so labels do not collide with axes. Check at the phone width.
