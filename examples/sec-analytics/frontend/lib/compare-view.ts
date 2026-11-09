// How the Compare screen lays out the comparison it receives. No calculations: values arrive computed (and
// indexed) from the backend; this only arranges and formats them.

import { MONEY_METRICS, PERCENT_METRICS } from "./compare-state";
import { formatMillions, formatPercent, formatTimes } from "./format";
import type { CompareCompany, CompareResponse, CompareRow } from "./types";

export interface TableLine {
  company: CompareCompany;
  metric: string;
  /** This line's rows by fiscal year label; a label the company does not have is absent. */
  cells: Record<string, CompareRow | undefined>;
}

export interface TableModel {
  /** Every fiscal year label in the comparison, ascending. Labels are the companies' own fiscal years. */
  labels: string[];
  lines: TableLine[];
  /** Number of data points: the same as the CSV's data lines. */
  points: number;
}

export function tableModel(response: CompareResponse): TableModel {
  const labels = [...new Set(response.rows.map((row) => row.fiscal_year_label))].sort();
  const lines: TableLine[] = [];
  for (const company of response.companies) {
    for (const metric of response.metrics) {
      const cells: Record<string, CompareRow | undefined> = {};
      for (const row of response.rows) {
        if (row.cik === company.cik && row.metric_id === metric) cells[row.fiscal_year_label] = row;
      }
      lines.push({ company, metric, cells });
    }
  }
  return { labels, lines, points: response.rows.length };
}

/** A value in its display form. A value that is not "ok" is a word, never 0. */
export function cellText(row: CompareRow): string {
  if (row.status !== "ok" || row.value === null) {
    if (row.status === "unavailable") return "unavailable";
    if (row.status === "not_meaningful") return "n/m";
    return "MISSING";
  }
  if (row.indexed) return row.value.toFixed(1);
  if (MONEY_METRICS.has(row.metric_id)) return formatMillions(row.value);
  if (PERCENT_METRICS.has(row.metric_id)) return formatPercent(row.value);
  return formatTimes(row.value);
}

/** The unit caption of a table line: "USD millions", "index", "%" or "×". */
export function rowUnitCaption(metric: string, unit: string, indexed: boolean): string {
  if (indexed) return "index";
  if (MONEY_METRICS.has(metric)) return unit ? `${unit} millions` : "";
  return PERCENT_METRICS.has(metric) ? "%" : "×";
}

/** "AAPL: FY ends 09-26 · MSFT: FY ends 06-30". */
export function fiscalYearEndLine(companies: readonly CompareCompany[]): string {
  return companies
    .map((company) => `${company.ticker || company.cik}: FY ends ${company.fiscal_year_end ?? "no data"}`)
    .join(" · ");
}

/** "Revenue, index = 100 at FY2017 (AAPL ends 2017-09-30; MSFT ends 2017-06-30)", or null without an index. */
export function indexLabel(response: CompareResponse, metricName: string): string | null {
  const base = response.index_base;
  if (!base) return null;
  const year = Object.values(base.fiscal_year_by_cik)[0];
  const ends = response.companies
    .map((company) => `${company.ticker || company.cik} ends ${base.period_end_by_cik[company.cik] ?? "no base"}`)
    .join("; ");
  return `${metricName}, index = 100 at ${year} (${ends})`;
}

export type ChartPoint = { label: string } & Record<string, number | null | string>;

/** One point per fiscal year label with each company's value under its CIK; missing is null (a gap). */
export function chartPoints(response: CompareResponse, metric: string): ChartPoint[] {
  const labels = [...new Set(response.rows.filter((row) => row.metric_id === metric).map((row) => row.fiscal_year_label))].sort();
  return labels.map((label) => {
    const point: ChartPoint = { label };
    for (const company of response.companies) {
      const found = response.rows.find((row) => row.cik === company.cik && row.metric_id === metric && row.fiscal_year_label === label);
      point[company.cik] = found && found.status === "ok" ? found.value : null;
    }
    return point;
  });
}

/** The row behind a chart point, for its tooltip. */
export function rowAt(response: CompareResponse, cik: string, metric: string, label: string): CompareRow | undefined {
  return response.rows.find((row) => row.cik === cik && row.metric_id === metric && row.fiscal_year_label === label);
}

/** The latest fiscal year label at which every company has a value for the metric, or null. */
export function barDefaultLabel(response: CompareResponse, metric: string): string | null {
  const points = chartPoints(response, metric);
  for (let index = points.length - 1; index >= 0; index -= 1) {
    if (response.companies.every((company) => typeof points[index][company.cik] === "number")) return points[index].label;
  }
  return null;
}

/** Money in different currencies never shares an axis; index points and ratios can. */
export function sharedAxisBlocked(response: CompareResponse, metric: string): boolean {
  if (!MONEY_METRICS.has(metric)) return false;
  if (!response.warnings.some((warning) => warning.code === "currencies_differ")) return false;
  return !response.rows.some((row) => row.metric_id === metric && row.indexed);
}

/** Series colours (theme tokens in globals.css), always paired with the ticker so colour is never the only cue. */
export const SERIES_COLOURS = ["var(--series-1)", "var(--series-2)", "var(--series-3)", "var(--series-4)"] as const;
