import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import type { MetricValue } from "@/lib/types";

import { ValueCell } from "./ValueCell";

afterEach(cleanup);

function metric(overrides: Partial<MetricValue>): MetricValue {
  return {
    metric_id: "net_margin",
    period_start: "2025-01-01",
    period_end: "2025-12-31",
    fiscal_year_label: "FY2025",
    value: null,
    unit: "percent",
    kind: "derived",
    status: "ok",
    reason: null,
    formula: "net income ÷ revenue",
    inputs: [],
    provenance: null,
    note: null,
    ...overrides,
  };
}

describe("ValueCell", () => {
  it("shows a percentage for an ok ratio", () => {
    render(<ValueCell metric={metric({ value: 0.25 })} />);
    expect(screen.getByRole("button").textContent).toBe("25.0%");
  });

  it("shows MISSING with the reason, never 0", () => {
    render(<ValueCell metric={metric({ kind: "reported", status: "missing", reason: "no mapped revenue concept", unit: "USD" })} />);
    expect(screen.getByRole("button").textContent).toBe("MISSING · no mapped revenue concept");
  });

  it("shows unavailable and gives the reason in the tooltip", () => {
    render(<ValueCell metric={metric({ status: "unavailable", reason: "denominator is zero" })} />);
    const button = screen.getByRole("button");
    expect(button.textContent).toBe("unavailable");
    fireEvent.focus(button);
    expect(screen.getByRole("tooltip").textContent).toContain("denominator is zero");
  });

  it("shows n/m with its reason for a number that would mislead", () => {
    render(<ValueCell metric={metric({ status: "not_meaningful", reason: "n/m (negative equity)", unit: "ratio" })} />);
    expect(screen.getByRole("button").textContent).toBe("n/m (negative equity)");
  });

  it("lists formula and inputs for a derived value", () => {
    const input = metric({ metric_id: "net_income", kind: "reported", value: 150, unit: "USD", formula: null });
    render(<ValueCell metric={metric({ value: 0.15, inputs: [input] })} />);
    fireEvent.focus(screen.getByRole("button"));
    const tip = screen.getByRole("tooltip").textContent ?? "";
    expect(tip).toContain("net income ÷ revenue");
    expect(tip).toContain("net_income");
    expect(tip).toContain("150 USD");
  });
});
