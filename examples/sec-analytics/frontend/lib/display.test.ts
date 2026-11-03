import { describe, expect, it } from "vitest";

import { chartPoints, companyLine, findFigure, reportingUnit, uniqueInOrder } from "./display";
import type { MetricValue, OverviewChartRow } from "./types";

function metric(metricId: string, value: number | null, status: MetricValue["status"] = "ok", reason: string | null = null): MetricValue {
  return {
    metric_id: metricId,
    period_start: "2023-10-01",
    period_end: "2024-09-28",
    fiscal_year_label: "FY2024",
    value,
    unit: "USD",
    kind: "reported",
    status,
    reason,
    formula: null,
    inputs: [],
    provenance: null,
    note: null,
  };
}

describe("uniqueInOrder", () => {
  it("merges repeated entries for display and keeps the first-seen order", () => {
    expect(uniqueInOrder(["Nasdaq", "Nasdaq", "NYSE", "Nasdaq"])).toEqual(["Nasdaq", "NYSE"]);
  });

  it("keeps an empty list empty", () => {
    expect(uniqueInOrder([])).toEqual([]);
  });
});

describe("companyLine", () => {
  it("joins name, first ticker and the 10-digit CIK", () => {
    expect(companyLine({ name: "Apple Inc.", ticker: "AAPL", cik: "0000320193" })).toBe("Apple Inc. · AAPL · CIK 0000320193");
  });

  it("leaves the ticker out when there is none", () => {
    expect(companyLine({ name: "Example Corp", ticker: null, cik: "0000000001" })).toBe("Example Corp · CIK 0000000001");
  });
});

describe("chartPoints", () => {
  const rows: OverviewChartRow[] = [
    { fiscal_year_label: "FY2023", period_end: "2023-09-30", revenue: metric("revenue", 100), net_income: metric("net_income", -5) },
    {
      fiscal_year_label: "FY2024",
      period_end: "2024-09-28",
      revenue: metric("revenue", null, "missing", "no mapped revenue concept"),
      net_income: metric("net_income", 0),
    },
  ];

  it("passes reported values through unchanged, including negatives and a real zero", () => {
    const points = chartPoints(rows);
    expect(points[0]).toMatchObject({ label: "FY2023", periodEnd: "2023-09-30", revenue: 100, netIncome: -5 });
    expect(points[1].netIncome).toBe(0);
  });

  it("turns a missing value into null (a gap), never 0", () => {
    expect(chartPoints(rows)[1].revenue).toBeNull();
  });

  it("treats a value whose status is not ok as missing even if a number is present", () => {
    const odd = [{ ...rows[0], revenue: metric("revenue", 7, "missing", "x") }];
    expect(chartPoints(odd)[0].revenue).toBeNull();
  });
});

describe("findFigure", () => {
  it("finds a key figure by metric id, or returns null", () => {
    const figures = [metric("revenue", 1), metric("net_income", 2)];
    expect(findFigure(figures, "net_income")?.value).toBe(2);
    expect(findFigure(figures, "operating_income")).toBeNull();
  });
});

describe("reportingUnit", () => {
  it("is the unit of the first reported value", () => {
    const row: OverviewChartRow = { fiscal_year_label: "FY2024", period_end: "2024-09-28", revenue: metric("revenue", 1), net_income: metric("net_income", 2) };
    expect(reportingUnit([row])).toBe("USD");
  });

  it("is null when nothing was reported (no revenue means no currency)", () => {
    const row: OverviewChartRow = {
      fiscal_year_label: "FY2024",
      period_end: "2024-09-28",
      revenue: metric("revenue", null, "missing", "no mapped revenue concept"),
      net_income: metric("net_income", null, "missing", "not reported"),
    };
    expect(reportingUnit([row])).toBeNull();
    expect(reportingUnit([])).toBeNull();
  });
});
