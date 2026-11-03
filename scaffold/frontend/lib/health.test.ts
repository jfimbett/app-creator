import { describe, expect, it } from "vitest";

import { UNREACHABLE, interpretHealth } from "./health";

describe("interpretHealth", () => {
  it("reports ok with the app name for a healthy answer", () => {
    expect(interpretHealth(200, { status: "ok", app: "Demo" })).toEqual({ kind: "ok", app: "Demo" });
  });

  it("reports unreachable when the request failed without an answer", () => {
    expect(interpretHealth(null, undefined)).toEqual({ kind: "error", message: UNREACHABLE });
  });

  it("treats a proxy 500 as an unreachable backend", () => {
    const state = interpretHealth(500, "Internal Server Error");
    expect(state.kind).toBe("error");
    expect(state.kind === "error" && state.message).toContain("not reachable");
  });

  it("reports other HTTP statuses", () => {
    expect(interpretHealth(404, {})).toEqual({ kind: "error", message: "The backend answered with HTTP 404." });
  });

  it("does not trust a 200 answer with an unexpected body", () => {
    expect(interpretHealth(200, { status: "starting" }).kind).toBe("error");
    expect(interpretHealth(200, null).kind).toBe("error");
  });
});
