import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { OFFLINE_MESSAGE, StatePanel } from "./StatePanel";

afterEach(() => cleanup());

describe("StatePanel", () => {
  it("loading shows skeleton rows with an announced text, not a blank box", () => {
    render(<StatePanel kind="loading" title="Loading company…" rows={4} />);
    const panel = screen.getByRole("status");
    expect(panel.textContent).toContain("Loading company…");
    expect(panel.querySelectorAll(".skeleton")).toHaveLength(4);
  });

  it("offline uses the plain backend message and is an alert", () => {
    render(<StatePanel kind="offline" />);
    const alert = screen.getByRole("alert");
    expect(alert.textContent).toContain("OFFLINE");
    expect(alert.textContent).toContain(OFFLINE_MESSAGE);
  });

  it("error shows message, reference and a working retry", () => {
    const retry = vi.fn();
    render(<StatePanel kind="error" title="Could not load the overview" reference="ab12" action={{ label: "Try again", onClick: retry }} />);
    expect(screen.getByRole("alert").textContent).toContain("ERROR");
    expect(screen.getByText("ab12")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(retry).toHaveBeenCalledOnce();
  });

  it("empty and missing carry text tags", () => {
    render(<StatePanel kind="empty" title="No match in the demo universe (3 companies)" />);
    expect(screen.getByRole("status").textContent).toContain("NO DATA");
    cleanup();
    render(<StatePanel kind="missing" message="No mapped revenue concept." />);
    expect(screen.getByRole("status").textContent).toContain("MISSING");
  });
});
