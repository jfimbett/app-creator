import { describe, expect, it } from "vitest";

import {
  MINUS,
  NOT_REPORTED,
  formatDate,
  formatExact,
  formatExactMetric,
  formatMetric,
  formatPercent,
  formatSignedPercent,
  formatTimes,
  unitCaption,
  formatFiscalYear,
  formatFiscalYearEnd,
  formatMillions,
  formatMissing,
  formatPeriod,
} from "./format";

describe("formatMillions", () => {
  it("shows whole USD as millions with thousands separators", () => {
    expect(formatMillions(1_234_567_000_000)).toBe("1,234,567");
    expect(formatMillions(391_035_000_000)).toBe("391,035");
  });

  it("rounds to the nearest million", () => {
    expect(formatMillions(93_736_500_000)).toBe("93,737");
    expect(formatMillions(1_499_999)).toBe("1");
  });

  it("uses a true minus sign for negative values", () => {
    expect(formatMillions(-5_000_000)).toBe(`${MINUS}5`);
    expect(formatMillions(-1_234_000_000)).toBe("−1,234");
  });

  it("never shows a negative zero", () => {
    expect(formatMillions(-400_000)).toBe("0");
    expect(formatMillions(0)).toBe("0");
  });

  it("shows a dash for a missing value, never 0", () => {
    expect(formatMillions(null)).toBe("—");
    expect(formatMillions(Number.NaN)).toBe("—");
  });
});

describe("formatExact", () => {
  it("shows the exact value with its unit", () => {
    expect(formatExact(1_234_567_000_000, "USD")).toBe("1,234,567,000,000 USD");
  });

  it("uses the minus sign and the dash for missing", () => {
    expect(formatExact(-2_000, "USD")).toBe("−2,000 USD");
    expect(formatExact(null, "USD")).toBe("—");
  });
});

describe("dates", () => {
  it("keeps ISO dates and cuts timestamps to the date", () => {
    expect(formatDate("2024-09-28")).toBe("2024-09-28");
    expect(formatDate("2007-01-04T00:00:00.000Z")).toBe("2007-01-04");
  });

  it("shows a dash for missing or malformed dates", () => {
    expect(formatDate(null)).toBe("—");
    expect(formatDate("")).toBe("—");
    expect(formatDate("Sept 28")).toBe("—");
  });

  it("formats a period start–end", () => {
    expect(formatPeriod("2023-10-01", "2024-09-28")).toBe("2023-10-01 – 2024-09-28");
    expect(formatPeriod(null, "2024-09-28")).toBe("— – 2024-09-28");
  });

  it("formats the fiscal year-end MMDD as MM-DD", () => {
    expect(formatFiscalYearEnd("0928")).toBe("09-28");
    expect(formatFiscalYearEnd("0630")).toBe("06-30");
  });

  it("says not reported when the fiscal year-end is missing or malformed", () => {
    expect(formatFiscalYearEnd(null)).toBe(NOT_REPORTED);
    expect(formatFiscalYearEnd("928")).toBe(NOT_REPORTED);
    expect(NOT_REPORTED).toBe("Not reported by SEC");
  });

  it("always shows the fiscal year label with its end date", () => {
    expect(formatFiscalYear("FY2024", "2024-09-28")).toBe("FY2024 (ends 2024-09-28)");
  });
});

describe("formatMissing", () => {
  it("builds the text badge for a missing value", () => {
    expect(formatMissing("no mapped revenue concept")).toBe("MISSING · no mapped revenue concept");
    expect(formatMissing(null)).toBe("MISSING · not reported");
  });
});

describe("ratios and units (M2)", () => {
  it("shows percentages with one decimal and a true minus sign", () => {
    expect(formatPercent(0.25)).toBe("25.0%");
    expect(formatPercent(-0.126)).toBe(`${MINUS}12.6%`);
    expect(formatPercent(-0.0001)).toBe("0.0%");
    expect(formatPercent(null)).toBe("—");
  });

  it("shows multiples with two decimals", () => {
    expect(formatTimes(0.5)).toBe("0.50×");
    expect(formatTimes(1.234)).toBe("1.23×");
    expect(formatTimes(null)).toBe("—");
  });

  it("formats a value by its unit", () => {
    expect(formatMetric({ value: 0.15, unit: "percent" })).toBe("15.0%");
    expect(formatMetric({ value: 0.71, unit: "ratio" })).toBe("0.71×");
    expect(formatMetric({ value: 136_056_000_000, unit: "USD" })).toBe("136,056");
    expect(formatMetric({ value: 0, unit: "USD" })).toBe("0");
  });

  it("captions the unit", () => {
    expect(unitCaption("USD")).toBe("USD millions");
    expect(unitCaption("percent")).toBe("%");
    expect(unitCaption("ratio")).toBe("×");
    expect(unitCaption("")).toBe("");
  });

  it("gives exact values in tooltips", () => {
    expect(formatExactMetric({ value: 136_056_000_000, unit: "USD" })).toBe("136,056,000,000 USD");
    expect(formatExactMetric({ value: 0.25, unit: "percent" })).toBe("25.0%");
  });
});

describe("formatSignedPercent (year-on-year change on the key-figure cards)", () => {
  it("always shows the sign, so the direction never depends on colour", () => {
    expect(formatSignedPercent(0.151)).toBe("+15.1%");
    expect(formatSignedPercent(-0.02)).toBe(`${MINUS}2.0%`);
  });

  it("shows no sign when the rounded change is zero, and the dash when there is no value", () => {
    expect(formatSignedPercent(0)).toBe("0.0%");
    expect(formatSignedPercent(0.0004)).toBe("0.0%");
    expect(formatSignedPercent(-0.0004)).toBe("0.0%");
    expect(formatSignedPercent(null)).toBe("—");
  });
});
