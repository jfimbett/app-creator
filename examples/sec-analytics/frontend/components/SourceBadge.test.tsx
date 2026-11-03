import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { SourceBadge, sourceBadgeText } from "./SourceBadge";

afterEach(() => cleanup());

describe("SourceBadge", () => {
  it("shows the recorded-demo label with the snapshot date", () => {
    render(<SourceBadge kind="demo" snapshotDate="2026-11-03" />);
    const badge = screen.getByTestId("source-badge");
    expect(badge.textContent).toBe("RECORDED SEC DEMO · snapshot 2026-11-03");
    expect(badge.dataset.kind).toBe("demo");
  });

  it("shows the plain mode label when no snapshot date is given (header badge)", () => {
    render(<SourceBadge kind="demo" />);
    expect(screen.getByText("RECORDED SEC DEMO")).toBeTruthy();
  });

  it("prefers the label sent by the API", () => {
    render(<SourceBadge kind="demo" snapshotDate="2000-01-01" label="RECORDED SEC DEMO · snapshot 2026-11-03" />);
    expect(screen.getByText("RECORDED SEC DEMO · snapshot 2026-11-03")).toBeTruthy();
  });

  it("labels synthetic data as synthetic, never as SEC data", () => {
    render(<SourceBadge kind="synthetic" />);
    const badge = screen.getByTestId("source-badge");
    expect(badge.textContent).toBe("SYNTHETIC TEST DATA");
    expect(badge.textContent).not.toMatch(/RECORDED SEC/);
  });

  it("shows MISSING with its reason", () => {
    render(<SourceBadge kind="missing" reason="no mapped revenue concept" />);
    expect(screen.getByText("MISSING · no mapped revenue concept")).toBeTruthy();
  });

  it("explains a missing value even without a reason", () => {
    expect(sourceBadgeText({ kind: "missing" })).toBe("MISSING · not reported by SEC");
  });
});
