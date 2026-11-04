import { describe, expect, it } from "vitest";

import { sourceFromParam, withSource } from "./sourceParam";

describe("sourceFromParam", () => {
  it("defaults to demo", () => {
    expect(sourceFromParam(null)).toBe("demo");
    expect(sourceFromParam(undefined)).toBe("demo");
    expect(sourceFromParam("")).toBe("demo");
    expect(sourceFromParam("LIVE")).toBe("demo");
  });

  it("reads live", () => {
    expect(sourceFromParam("live")).toBe("live");
  });
});

describe("withSource", () => {
  it("keeps live in the URL and adds nothing for demo", () => {
    expect(withSource("/companies/0000320193", "live")).toBe("/companies/0000320193?source=live");
    expect(withSource("/companies/0000320193", "demo")).toBe("/companies/0000320193");
  });
});
