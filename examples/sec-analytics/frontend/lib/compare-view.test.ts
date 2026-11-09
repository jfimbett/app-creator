import { describe, expect, it } from "vitest";

import {
  barDefaultLabel,
  cellText,
  chartPoints,
  fiscalYearEndLine,
  indexLabel,
  rowUnitCaption,
  sharedAxisBlocked,
  tableModel,
} from "./compare-view";
import type { CompareResponse, CompareRow } from "./types";

function row(cik: string, metric_id: string, label: string, end: string, value: number | null, extra: Partial<CompareRow> = {}): CompareRow {
  return {
    cik,
    metric_id,
    fiscal_year_label: label,
    period_start: null,
    period_end: end,
    value,
    unit: metric_id === "revenue" ? "USD" : "ratio",
    kind: metric_id === "revenue" ? "reported" : "derived",
    status: value === null ? "missing" : "ok",
    reason: value === null ? "no fact" : null,
    indexed: false,
    source_concept: null,
    accession: null,
    data_source: "RECORDED SEC DEMO · snapshot 2026-11-03",
    ...extra,
  };
}

const A = "0000320193";
const M = "0000789019";
const response: CompareResponse = {
  companies: [
    { cik: A, ticker: "AAPL", name: "Apple Inc.", fiscal_year_end: "09-26", currency: "USD" },
    { cik: M, ticker: "MSFT", name: "MICROSOFT CORP", fiscal_year_end: "06-30", currency: "USD" },
  ],
  metrics: ["revenue", "net_margin"],
  rows: [
    row(A, "revenue", "FY2025", "2025-09-27", 416161000000),
    row(A, "revenue", "FY2026", "2026-09-26", 478834000000),
    row(A, "net_margin", "FY2025", "2025-09-27", 0.24),
    row(A, "net_margin", "FY2026", "2026-09-26", 0.276035),
    row(M, "revenue", "FY2024", "2024-06-30", 245122000000),
    row(M, "revenue", "FY2025", "2025-06-30", null),
    row(M, "net_margin", "FY2024", "2024-06-30", 0.35),
    row(M, "net_margin", "FY2025", "2025-06-30", 0.36),
  ],
  index_base: null,
  warnings: [{ code: "fiscal_years_not_aligned", message: "Fiscal years are not aligned" }],
  index_available: true,
  source: { mode: "demo", label: "RECORDED SEC DEMO · snapshot 2026-11-03", retrieved_at: null, snapshot_date: "2026-11-03", source_urls: [] },
};

describe("tableModel", () => {
  it("has one column per fiscal year label and one line per company × metric, in response order", () => {
    const model = tableModel(response);
    expect(model.labels).toEqual(["FY2024", "FY2025", "FY2026"]);
    expect(model.lines.map((line) => [line.company.ticker, line.metric])).toEqual([
      ["AAPL", "revenue"],
      ["AAPL", "net_margin"],
      ["MSFT", "revenue"],
      ["MSFT", "net_margin"],
    ]);
    expect(model.lines[0].cells.FY2024).toBeUndefined();
    expect(model.lines[0].cells.FY2026?.period_end).toBe("2026-09-26");
    expect(model.points).toBe(8);
  });
});

describe("cellText and units", () => {
  it("formats money in millions, margins as %, debt-to-equity as ×, index points with one decimal", () => {
    expect(cellText(row(A, "revenue", "FY2026", "2026-09-26", 478834000000))).toBe("478,834");
    expect(cellText(row(A, "net_margin", "FY2026", "2026-09-26", 0.276035))).toBe("27.6%");
    expect(cellText(row(A, "debt_to_equity", "FY2026", "2026-09-26", 0.71))).toBe("0.71×");
    expect(cellText(row(A, "revenue", "FY2026", "2026-09-26", 208.8843, { indexed: true, unit: "index" }))).toBe("208.9");
  });

  it("never shows 0 for a missing or unavailable value", () => {
    expect(cellText(row(M, "revenue", "FY2025", "2025-06-30", null))).toBe("MISSING");
    expect(cellText(row(M, "revenue", "FY2025", "2025-06-30", null, { status: "unavailable" }))).toBe("unavailable");
    expect(cellText(row(M, "net_margin", "FY2025", "2025-06-30", null, { status: "not_meaningful" }))).toBe("n/m");
  });

  it("captions each row's unit", () => {
    expect(rowUnitCaption("revenue", "USD", false)).toBe("USD millions");
    expect(rowUnitCaption("revenue", "index", true)).toBe("index");
    expect(rowUnitCaption("net_margin", "ratio", false)).toBe("%");
    expect(rowUnitCaption("debt_to_equity", "ratio", false)).toBe("×");
  });
});

describe("labels", () => {
  it("names each company's fiscal year-end", () => {
    expect(fiscalYearEndLine(response.companies)).toBe("AAPL: FY ends 09-26 · MSFT: FY ends 06-30");
  });

  it("names the base year and each company's base period end when indexed", () => {
    const indexed = {
      ...response,
      index_base: { fiscal_year_by_cik: { [A]: "FY2017", [M]: "FY2017" }, period_end_by_cik: { [A]: "2017-09-30", [M]: "2017-06-30" } },
    };
    expect(indexLabel(indexed, "Revenue")).toBe("Revenue, index = 100 at FY2017 (AAPL ends 2017-09-30; MSFT ends 2017-06-30)");
    expect(indexLabel(response, "Revenue")).toBeNull();
  });
});

describe("chart data", () => {
  it("puts each company's value under its own fiscal year label; missing is null, never 0", () => {
    const points = chartPoints(response, "revenue");
    expect(points.map((p) => p.label)).toEqual(["FY2024", "FY2025", "FY2026"]);
    expect(points[1][M]).toBeNull();
    expect(points[2][A]).toBe(478834000000);
    expect(points[0][A]).toBeNull();
  });

  it("defaults the one-year bars to the latest label every company has a value for", () => {
    expect(barDefaultLabel(response, "net_margin")).toBe("FY2025");
    expect(barDefaultLabel(response, "revenue")).toBeNull();
  });

  it("blocks a shared axis for money in different currencies unless indexed", () => {
    const euro = { ...response, warnings: [{ code: "currencies_differ" as const, message: "Different reporting currencies (USD, EUR): not converted" }] };
    expect(sharedAxisBlocked(euro, "revenue")).toBe(true);
    expect(sharedAxisBlocked(euro, "net_margin")).toBe(false);
    expect(sharedAxisBlocked(response, "revenue")).toBe(false);
    const euroIndexed = { ...euro, rows: euro.rows.map((r) => (r.metric_id === "revenue" ? { ...r, indexed: true, unit: "index" } : r)) };
    expect(sharedAxisBlocked(euroIndexed, "revenue")).toBe(false);
  });
});
