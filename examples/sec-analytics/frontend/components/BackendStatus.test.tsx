import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { BackendStatus } from "./BackendStatus";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("BackendStatus", () => {
  it("shows OK in words when the backend answers", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ status: "ok", app: "SEC Analytics" }), { status: 200 })));
    render(<BackendStatus />);
    expect(await screen.findByText("Backend OK")).toBeTruthy();
    expect(screen.getByTestId("health-status").dataset.state).toBe("ok");
  });

  it("shows the start command in plain text, and re-checks on request", async () => {
    const fetchMock = vi.fn(async () => {
      throw new TypeError("fetch failed");
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<BackendStatus />);
    const status = await screen.findByText("Backend not reachable: start it with npm run demo");
    expect(status.textContent).toContain("start it with npm run demo");
    fireEvent.click(screen.getByRole("button", { name: "Check again" }));
    await screen.findByText("Backend not reachable: start it with npm run demo");
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
