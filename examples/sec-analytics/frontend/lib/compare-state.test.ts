import { describe, expect, it } from "vitest";

import {
  addCompany,
  ALREADY_ADDED,
  COUNT_RULE,
  DEFAULT_STATE,
  parseCompareState,
  removeCompany,
  serializeCompareState,
  toggleMetric,
} from "./compare-state";

const AAPL = "0000320193";
const MSFT = "0000789019";
const GOOGL = "0001652044";
const NVDA = "0001045810";
const FIFTH = "0000000905";

describe("URL state (M4 §3.1)", () => {
  it("round-trips a full comparison", () => {
    const state = {
      ciks: [AAPL, MSFT],
      metrics: ["revenue", "net_margin"],
      years: 10,
      index: "none" as const,
      source: "demo" as const,
    };
    const text = serializeCompareState(state);
    expect(text).toBe(`ciks=${AAPL}%2C${MSFT}&metrics=revenue%2Cnet_margin&years=10&index=none&source=demo`);
    expect(parseCompareState(new URLSearchParams(text))).toEqual(state);
  });

  it("starts empty with the defaults and never adds companies by itself", () => {
    expect(parseCompareState(new URLSearchParams(""))).toEqual(DEFAULT_STATE);
    expect(DEFAULT_STATE.ciks).toEqual([]);
    expect(DEFAULT_STATE.metrics).toEqual(["revenue", "net_margin"]);
  });

  it("cleans a hand-edited URL: normalized CIKs, no repeats, known metrics, years 5-10", () => {
    const params = new URLSearchParams("ciks=320193,CIK0000320193,abc,789019&metrics=roe,fcf,fcf&years=42&index=x&source=live");
    expect(parseCompareState(params)).toEqual({
      ciks: [AAPL, MSFT],
      metrics: ["fcf"],
      years: 10,
      index: "none",
      source: "live",
    });
    expect(parseCompareState(new URLSearchParams("years=5&index=first_common_year")).years).toBe(5);
    expect(parseCompareState(new URLSearchParams("index=first_common_year")).index).toBe("first_common_year");
  });

  it("keeps at most four companies and six metrics from a URL", () => {
    const params = new URLSearchParams(
      `ciks=${[AAPL, MSFT, GOOGL, NVDA, FIFTH].join(",")}&metrics=revenue,revenue_growth,operating_margin,net_margin,operating_cash_flow,fcf,fcf_margin`,
    );
    const state = parseCompareState(params);
    expect(state.ciks).toHaveLength(4);
    expect(state.metrics).toHaveLength(6);
  });
});

describe("2–4 companies (M4-AC2, M4-E3)", () => {
  const three = { ...DEFAULT_STATE, ciks: [AAPL, MSFT, GOOGL] };

  it("adds a company at the end", () => {
    const { state, message } = addCompany(three, NVDA);
    expect(state.ciks).toEqual([AAPL, MSFT, GOOGL, NVDA]);
    expect(message).toBeNull();
  });

  it("refuses a fifth company with the rule", () => {
    const four = addCompany(three, NVDA).state;
    const { state, message } = addCompany(four, FIFTH);
    expect(state).toBe(four);
    expect(message).toBe(COUNT_RULE);
    expect(COUNT_RULE).toBe("Compare 2–4 companies");
  });

  it("ignores a company already present", () => {
    const { state, message } = addCompany(three, "320193");
    expect(state).toBe(three);
    expect(message).toBe(ALREADY_ADDED);
    expect(ALREADY_ADDED).toBe("Already in the comparison");
  });

  it("removing down to one leaves one chip and no comparison", () => {
    const one = removeCompany(removeCompany(three, GOOGL), MSFT);
    expect(one.ciks).toEqual([AAPL]);
  });
});

describe("metrics", () => {
  it("toggles within 1 to 6", () => {
    const one = { ...DEFAULT_STATE, metrics: ["revenue"] };
    expect(toggleMetric(one, "revenue").metrics).toEqual(["revenue"]);
    expect(toggleMetric(one, "fcf").metrics).toEqual(["revenue", "fcf"]);
    const six = { ...DEFAULT_STATE, metrics: ["revenue", "revenue_growth", "operating_margin", "net_margin", "operating_cash_flow", "fcf"] };
    expect(toggleMetric(six, "fcf_margin").metrics).toEqual(six.metrics);
    expect(toggleMetric(six, "fcf").metrics).toHaveLength(5);
  });
});
