import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { applyTheme, readTheme, THEME_INIT_SCRIPT, THEME_STORAGE_KEY, writeTheme } from "./theme";

describe("theme preference (M6-AC1)", () => {
  beforeEach(() => {
    window.localStorage.clear();
    delete document.documentElement.dataset.theme;
  });
  afterEach(() => vi.restoreAllMocks());

  it("uses the key sec-analytics.theme", () => {
    expect(THEME_STORAGE_KEY).toBe("sec-analytics.theme");
  });

  it("is dark when nothing is stored", () => {
    expect(readTheme()).toBe("dark");
  });

  it.each(["", "Light", "blue", "null", '"light"', "light "])("is dark for the invalid stored value %j", (value) => {
    window.localStorage.setItem(THEME_STORAGE_KEY, value);
    expect(readTheme()).toBe("dark");
  });

  it("reads a stored light or dark value", () => {
    window.localStorage.setItem(THEME_STORAGE_KEY, "light");
    expect(readTheme()).toBe("light");
    window.localStorage.setItem(THEME_STORAGE_KEY, "dark");
    expect(readTheme()).toBe("dark");
  });

  it("writeTheme stores exactly one key with the plain value", () => {
    writeTheme("light");
    expect(Object.keys(window.localStorage)).toEqual([THEME_STORAGE_KEY]);
    expect(window.localStorage.getItem(THEME_STORAGE_KEY)).toBe("light");
    writeTheme("dark");
    expect(window.localStorage.getItem(THEME_STORAGE_KEY)).toBe("dark");
  });

  it("applyTheme sets data-theme on <html>", () => {
    applyTheme("light");
    expect(document.documentElement.dataset.theme).toBe("light");
    applyTheme("dark");
    expect(document.documentElement.dataset.theme).toBe("dark");
  });

  it("falls back to dark and does not crash when storage throws", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    expect(readTheme()).toBe("dark");
    expect(() => writeTheme("light")).not.toThrow();
  });

  describe("the pre-paint script follows the same rule", () => {
    const run = () => new Function(THEME_INIT_SCRIPT)();

    it.each([
      [null, "dark"],
      ["light", "light"],
      ["dark", "dark"],
      ["Light", "dark"],
    ])("stored %j gives %s", (stored, expected) => {
      if (stored !== null) window.localStorage.setItem(THEME_STORAGE_KEY, stored);
      run();
      expect(document.documentElement.dataset.theme).toBe(expected);
    });

    it("leaves dark when storage throws", () => {
      vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
        throw new Error("blocked");
      });
      expect(run).not.toThrow();
      expect(document.documentElement.dataset.theme).toBe("dark");
    });
  });
});
