import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { HealthStatus } from "./HealthStatus";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("HealthStatus", () => {
  it("shows OK when the backend answers", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ status: "ok", app: "Demo" }), { status: 200 })));
    render(<HealthStatus />);
    expect(await screen.findByText(/the backend \(Demo\) is running/)).toBeTruthy();
    expect(screen.getByTestId("health-status").dataset.state).toBe("ok");
  });

  it("shows an error when the backend is unreachable", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => { throw new TypeError("fetch failed"); }));
    render(<HealthStatus />);
    expect(await screen.findByText(/not reachable/)).toBeTruthy();
    expect(screen.getByTestId("health-status").dataset.state).toBe("error");
  });
});
