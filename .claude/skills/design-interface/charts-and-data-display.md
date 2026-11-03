# Charts, cards and tables: choosing them, and keeping them honest

Charts are not required. Propose them only when the user must compare values, see a trend or spot an outlier
faster than a table allows. When a precise value matters more than a shape, a well-formatted table is better.

## Choosing a visual from the question the user asks

| The user wants to know | Propose | Avoid |
|---|---|---|
| "What is the latest value, and did it go up?" | summary cards: value, unit, period, change vs the previous comparable period | a chart for one number |
| "How did it change over periods?" (totals per period: sales, visits, distance) | bars per period, or a line with markers when there are many periods | a smooth line through 3 points |
| "How did it change over time?" (a level at a date: stock, balance, members) | line or bars on a **date axis**, so uneven gaps look uneven | evenly spaced category labels |
| "How do these items compare?" | horizontal bars sorted by value, same unit and period for all | pie charts; mixed periods |
| "What is it made of?" | stacked bars or a table with shares | pie with more than 4 slices |
| "Is a rate within a normal range?" | bars or a line with a visible zero line and a reference band if agreed | dual axes |
| "Which items need attention?" | a sortable table with the key column marked in text or a symbol, not colour alone | a dashboard of decorative gauges |

## Default dashboard layout (propose, do not impose)

1. A selector for the item or scenario (search, period), if there is more than one.
2. A row of 3 to 5 summary cards: label, value, unit, period, change vs the previous comparable period, or a
   written reason why no change is shown.
3. One to three charts that answer the questions in `<docs>/product.md`.
4. The detailed table, notes and sources below, or behind a "View underlying data" section.

One primary action per screen. Agree the cards and charts with the owner before building them, and record them
in "Screens and visuals" of `<docs>/product.md`.

## Where the numbers come from: one shared, tested layer

Cards, charts and tables show numbers computed **once**, in the backend logic layer (`<backend>/app/logic/`,
see `plan-architecture`). It returns display-ready data: values, units, period labels, and the reason for every
gap or caveat. The frontend only formats and draws what it receives; it never adds, divides or decides that a
value is missing. That way pytest checks every honesty rule below.

A display-ready series looks like this:

```json
{
  "metric": "distance", "unit": "km", "source": "fixture", "as_of": "2026-03-01",
  "points": [
    {"period": "2026-W10", "value": 21.5, "note": null},
    {"period": "2026-W11", "value": null, "note": "no runs recorded"},
    {"period": "2026-W12", "value": 0.0,  "note": null}
  ]
}
```

Formatting in the frontend is display only, in one helper so cards, tables and charts agree:

```ts
// <frontend>/lib/format.ts
const nf = new Intl.NumberFormat("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
export function formatValue(v: number | null, unit: string, note?: string | null): string {
  if (v === null) return note ? `n/a (${note})` : "n/a";
  return `${nf.format(v)} ${unit}`;            // a minus sign comes from Intl for negatives
}
```

Round once, with the app's documented rule (in `acceptance.md`), so the card, the chart and the table show the
same digits.

## Honesty checklist (each item a test on the logic layer, or a Playwright check)

- **Missing is not zero.** A missing value is `null` with a reason ("not reported", "no data for this period"). It
  is drawn as a gap with an "n/a" label, never as a bar or point at 0. Lines do not connect across gaps (Recharts:
  leave `connectNulls` off, which is the default; pass `null`, never `0` or `undefined` replaced by `0`).
- **Zero is not missing.** A real zero is drawn and labelled `0.0`. "Not meaningful" (a rate when the denominator
  is zero, a % change from a negative base) is a third case with its own label and reason. In the neutral finance
  example, a margin with revenue `0` is "not meaningful", with revenue not reported it is "n/a".
- **Negative values are obvious without colour:** a visible zero line (Recharts `<ReferenceLine y={0} />`), a
  minus sign in labels, bars below the axis.
- **Units and scale:** the unit (`km`, `%`, `x`, a currency) on every axis, card and tooltip; the same unit for every
  series on one axis. If one series is ten times larger than another, offer a series selector or separate small
  charts, never an unlabelled second axis.
- **Periods:** each label says which period (week, month, quarter, year, date). Partial or unusual periods are
  marked differently (outline or pattern, and in label and tooltip), and no change is computed across them.
- **Incomparable observations** (different units, definitions, period lengths, revised values) are not placed on
  one axis without a visible note; if they cannot be compared, do not compare.
- **Only real observations:** never fill gaps, extrapolate or add history to make a chart look fuller. With 2 or
  3 periods, use value labels and wider bars.
- **Axes:** bars start at zero; a line chart's value axis may start elsewhere only if the label says so.
- **Text alternative:** every chart has a title, an accessible name, and a visible text summary or table with
  every value. Tooltips are not reachable by keyboard and touch is unreliable, so they never hold information
  found nowhere else (see [responsive-and-accessibility.md](responsive-and-accessibility.md)).
- **Sample or recorded data:** if data is fictional, a sample or a recorded snapshot, the chart itself carries a
  visible label ("SAMPLE DATA", "Recorded 2026-03-01"), so a screenshot stays identified.
- **Source and date** are visible near the chart when the product depends on trusted data; live, cached and
  recorded data are labelled differently.

## Tables

- Right-align numbers; use **tabular numerals** so digits line up (Tailwind `tabular-nums`, i.e.
  `font-variant-numeric: tabular-nums`).
- Units in the column header (`Distance (km)`), not repeated in each cell.
- Sticky header for long tables (`sticky top-0` on `<th>` with a background).
- `<th scope="col">`, a `<caption>` (can be visually hidden) describing the table.
- Sorting: a `<button>` in the header with `aria-sort` on the `<th>`; the sort is stable.
- On a phone: the table scrolls inside its own box (`overflow-x-auto` on a wrapper), or secondary columns drop.

## Recharts in the standard stack

Add it when the first chart is agreed: `npm install --save-exact recharts` in `<frontend>`. Charts render in the
browser, so the chart component is a client component (`"use client"`).

```tsx
"use client";
import { Bar, BarChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type Point = { period: string; value: number | null; note: string | null };

export function PeriodBars({ title, unit, points }: { title: string; unit: string; points: Point[] }) {
  return (
    <figure aria-labelledby="chart-title">
      <figcaption id="chart-title" className="text-sm font-semibold">{title} ({unit})</figcaption>
      <div className="h-64" role="img" aria-label={`${title}, bar chart. The values are in the table below.`}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={points} margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
            <CartesianGrid stroke="var(--border)" vertical={false} />
            <XAxis dataKey="period" stroke="var(--muted)" tick={{ fontSize: 12 }} />
            <YAxis stroke="var(--muted)" tick={{ fontSize: 12 }} width={48} />
            <ReferenceLine y={0} stroke="var(--foreground)" />
            <Tooltip formatter={(v) => (v == null ? "n/a" : `${v} ${unit}`)} />
            <Bar dataKey="value" fill="var(--accent)" isAnimationActive={false} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      {/* the data table with every value, including "n/a (reason)" rows, follows here */}
    </figure>
  );
}
```

- Colours come from the theme's CSS variables ([design-system.md](design-system.md)), so dark and light both work.
- Turn off animation in tests and for users who prefer reduced motion.
- Read the Recharts documentation for the installed version; change single props rather than replacing whole
  default objects.
- Leave room for value labels: short, horizontal axis labels, margins so labels do not collide; check at 390 px.
