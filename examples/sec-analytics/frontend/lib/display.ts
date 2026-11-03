// Small display helpers for the screens. They only pick and arrange values the backend has already computed.

import type { MetricValue, OverviewChartRow } from "./types";

/** Drops repeated entries, keeping the first-seen order (Alphabet lists "Nasdaq" once per ticker). Display only. */
export function uniqueInOrder(values: readonly string[]): string[] {
  return Array.from(new Set(values));
}

/** "Apple Inc. · AAPL · CIK 0000320193": how a company is named in search results and page headings. */
export function companyLine(company: { name: string; ticker: string | null; cik: string }): string {
  const parts = [company.name];
  if (company.ticker) parts.push(company.ticker);
  parts.push(`CIK ${company.cik}`);
  return parts.join(" · ");
}

/** One point of the revenue and net income chart. `null` draws a gap, never a zero. */
export interface ChartPoint {
  label: string;
  periodEnd: string;
  revenue: number | null;
  netIncome: number | null;
  row: OverviewChartRow;
}

function plotted(metric: MetricValue): number | null {
  return metric.status === "ok" ? metric.value : null;
}

/** The overview rows in the shape the chart draws; values are passed through unchanged. */
export function chartPoints(rows: readonly OverviewChartRow[]): ChartPoint[] {
  return rows.map((row) => ({
    label: row.fiscal_year_label,
    periodEnd: row.period_end,
    revenue: plotted(row.revenue),
    netIncome: plotted(row.net_income),
    row,
  }));
}

/** The key figure with this metric id, or null when the backend did not send it. */
export function findFigure(figures: readonly MetricValue[], metricId: string): MetricValue | null {
  return figures.find((figure) => figure.metric_id === metricId) ?? null;
}

/** The unit of the first reported value (the reporting currency), or null when nothing was reported. */
export function reportingUnit(rows: readonly OverviewChartRow[]): string | null {
  for (const row of rows) {
    for (const metric of [row.revenue, row.net_income]) {
      if (metric.status === "ok") return metric.unit;
    }
  }
  return null;
}
